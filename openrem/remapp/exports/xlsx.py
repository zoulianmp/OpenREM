#    OpenREM - Radiation Exposure Monitoring tools for the physicist
#    Copyright (C) 2012,2013  The Royal Marsden NHS Foundation Trust
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    Additional permission under section 7 of GPLv3:
#    You shall not make any use of the name of The Royal Marsden NHS
#    Foundation trust in connection with this Program in any press or 
#    other public announcement without the prior written consent of 
#    The Royal Marsden NHS Foundation Trust.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
..  module:: xlsx.
    :synopsis: Module to export database data to multi-sheet Microsoft XLSX files.

..  moduleauthor:: Ed McDonagh

"""


from xlsxwriter.workbook import Workbook
from celery import shared_task
from django.conf import settings




@shared_task
def ctxlsx(filterdict):
    """Export filtered CT database data to multi-sheet Microsoft XSLX files.

    :param filterdict: Query parameters from the CT filtered page URL.
    :type filterdict: HTTP get
    
    """

    import os, sys, datetime
    from tempfile import TemporaryFile
    from django.conf import settings
    from django.core.files import File
    from django.shortcuts import redirect
    from remapp.models import General_study_module_attributes
    from remapp.models import Exports
    from remapp.interface.mod_filters import CTSummaryListFilter

    tsk = Exports.objects.create()

    tsk.task_id = ctxlsx.request.id
    tsk.modality = "CT"
    tsk.export_type = "XLSX export"
    datestamp = datetime.datetime.now()
    tsk.export_date = datestamp
    tsk.progress = 'Query filters imported, task started'
    tsk.status = 'CURRENT'
    tsk.save()

    try:
        tmpxlsx = TemporaryFile()
        book = Workbook(tmpxlsx, {'default_date_format': 'dd/mm/yyyy',
                                 'strings_to_numbers':  True})
        tsk.progress = 'Workbook created'
        tsk.save()
    except:
        messages.error(request, "Unexpected error creating temporary file - please contact an administrator: {0}".format(sys.exc_info()[0]))
        return redirect('/openrem/export/')

    # Get the data
    e = General_study_module_attributes.objects.filter(modality_type__exact = 'CT')
    f = CTSummaryListFilter.base_filters

    for filt in f:
        if filt in filterdict and filterdict[filt]:
            # One Windows user found filterdict[filt] was a list. See https://bitbucket.org/openrem/openrem/issue/123/
            if isinstance(filterdict[filt], basestring):
                filterstring = filterdict[filt]
            else:
                filterstring = (filterdict[filt])[0]
            if filterstring != '':
                e = e.filter(**{f[filt].name + '__' + f[filt].lookup_type : filterstring})

    tsk.progress = 'Required study filter complete.'
    tsk.num_records = e.count()
    tsk.save()

    # Add summary sheet and all data sheet
    summarysheet = book.add_worksheet("Summary")
    wsalldata = book.add_worksheet('All data')       
    wsalldata.set_column('G:G', 10) # allow date to be displayed.

    # Some prep
    commonheaders = [
        'Institution', 
        'Manufacturer', 
        'Model',
        'Station name',
        'Accession number',
        'Operator',
        'Date',
        'Age', 
        'Height', 
        'Mass (kg)', 
        'Test patient?',
        'Study description',
        'Requested procedure',
        'No. events',
        'DLP total (mGy.cm)',
        ]
    protocolheaders = commonheaders + [
        'Protocol',
        'Type',
        'Exposure time',
        'Scanning length',
        'Slice thickness',
        'Total collimation',
        'Pitch',
        'No. sources',
        'CTDIvol',
        'DLP',
        'S1 name',
        'S1 kVp',
        'S1 max mA',
        'S1 mA',
        'S1 Exposure time/rotation',
        'S2 name',
        'S2 kVp',
        'S2 max mA',
        'S2 mA',
        'S2 Exposure time/rotation',
        'mA Modulation type',
        'Comments',
        ]
        
    # Generate list of protocols in queryset and create worksheets for each
    tsk.progress = 'Generating list of protocols in the dataset...'
    tsk.save()

    sheetlist = {}
    protocolslist = []
    for exams in e:
        for s in exams.ct_radiation_dose_set.get().ct_irradiation_event_data_set.all():
            if s.acquisition_protocol:
                safeprotocol = s.acquisition_protocol
            else:
                safeprotocol = u'Unknown'
            if safeprotocol not in protocolslist:
                protocolslist.append(safeprotocol)
    protocolslist.sort()

    tsk.progress = 'Creating an Excel safe version of protocol names and creating a worksheet for each...'
    tsk.save()

    for protocol in protocolslist:
        tabtext = protocol.lower().replace(" ","_")
        translation_table = {ord('['):ord('('), ord(']'):ord(')'), ord(':'):ord(';'), ord('*'):ord('#'), ord('?'):ord(';'), ord('/'):ord('|'), ord('\\'):ord('|')}
        tabtext = tabtext.translate(translation_table) # remove illegal characters
        tabtext = tabtext[:31]
        if tabtext not in sheetlist:
            sheetlist[tabtext] = {
                'sheet': book.add_worksheet(tabtext),
                'count':0,
                'protocolname':[protocol]}
            sheetlist[tabtext]['sheet'].write_row(0,0,protocolheaders)
            sheetlist[tabtext]['sheet'].set_column('G:G', 10) # Date column
        else:
            if protocol not in sheetlist[tabtext]['protocolname']:
                sheetlist[tabtext]['protocolname'].append(protocol)



    ##################
    # All data sheet

    from django.db.models import Max
    max_events = e.aggregate(Max('ct_radiation_dose__ct_accumulated_dose_data__total_number_of_irradiation_events'))

    alldataheaders = commonheaders

    tsk.progress = 'Generating headers for the all data sheet...'
    tsk.save()

    for h in xrange(max_events['ct_radiation_dose__ct_accumulated_dose_data__total_number_of_irradiation_events__max']):
        alldataheaders += [
            'E' + str(h+1) + ' Protocol',
            'E' + str(h+1) + ' Type',
            'E' + str(h+1) + ' Exposure time',
            'E' + str(h+1) + ' Scanning length',
            'E' + str(h+1) + ' Slice thickness',
            'E' + str(h+1) + ' Total collimation',
            'E' + str(h+1) + ' Pitch',
            'E' + str(h+1) + ' No. sources',
            'E' + str(h+1) + ' CTDIvol',
            'E' + str(h+1) + ' DLP',
            'E' + str(h+1) + ' S1 name',
            'E' + str(h+1) + ' S1 kVp',
            'E' + str(h+1) + ' S1 max mA',
            'E' + str(h+1) + ' S1 mA',
            'E' + str(h+1) + ' S1 Exposure time/rotation',
            'E' + str(h+1) + ' S2 name',
            'E' + str(h+1) + ' S2 kVp',
            'E' + str(h+1) + ' S2 max mA',
            'E' + str(h+1) + ' S2 mA',
            'E' + str(h+1) + ' S2 Exposure time/rotation',
            'E' + str(h+1) + ' mA Modulation type',
            'E' + str(h+1) + ' Comments',
            ]
    wsalldata.write_row('A1', alldataheaders)
    numcolumns = (22 * max_events['ct_radiation_dose__ct_accumulated_dose_data__total_number_of_irradiation_events__max']) + 14 - 1
    numrows = e.count()
    wsalldata.autofilter(0,0,numrows,numcolumns)

    for row,exams in enumerate(e):

        tsk.progress = 'Writing study {0} of {1} to All data sheet and individual protocol sheets'.format(row + 1, numrows)
        tsk.save()

        examdata = [
			exams.general_equipment_module_attributes_set.get().institution_name,
			exams.general_equipment_module_attributes_set.get().manufacturer,
			exams.general_equipment_module_attributes_set.get().manufacturer_model_name,
			exams.general_equipment_module_attributes_set.get().station_name,
            exams.accession_number,
            exams.operator_name,
            exams.study_date,  # Is a date - cell needs formatting
            str(exams.patient_study_module_attributes_set.get().patient_age_decimal),
            str(exams.patient_study_module_attributes_set.get().patient_size),
            str(exams.patient_study_module_attributes_set.get().patient_weight),
            exams.patient_module_attributes_set.get().not_patient_indicator,
            exams.study_description,
            exams.requested_procedure_code_meaning,
            str(exams.ct_radiation_dose_set.get().ct_accumulated_dose_data_set.get().total_number_of_irradiation_events),
            str(exams.ct_radiation_dose_set.get().ct_accumulated_dose_data_set.get().ct_dose_length_product_total),
			]
        for s in exams.ct_radiation_dose_set.get().ct_irradiation_event_data_set.all():
            examdata += [
                s.acquisition_protocol,
                str(s.ct_acquisition_type),
                str(s.exposure_time),
                str(s.scanning_length_set.get().scanning_length),
                str(s.nominal_single_collimation_width),
                str(s.nominal_total_collimation_width),
                str(s.pitch_factor),
                str(s.number_of_xray_sources),
                str(s.mean_ctdivol),
                str(s.dlp),
                ]
            if s.number_of_xray_sources > 1:
                for source in s.ct_xray_source_parameters_set.all():
                    examdata += [
                        str(source.identification_of_the_xray_source),
                        str(source.kvp),
                        str(source.maximum_xray_tube_current),
                        str(source.xray_tube_current),
                        str(source.exposure_time_per_rotation),
                        ]
            else:
                try:
                    examdata += [
                        str(s.ct_xray_source_parameters_set.get().identification_of_the_xray_source),
                        str(s.ct_xray_source_parameters_set.get().kvp),
                        str(s.ct_xray_source_parameters_set.get().maximum_xray_tube_current),
                        str(s.ct_xray_source_parameters_set.get().xray_tube_current),
                        str(s.ct_xray_source_parameters_set.get().exposure_time_per_rotation),
                        'n/a',
                        'n/a',
                        'n/a',
                        'n/a',
                        'n/a',
                        ]
                except:
                        examdata += ['n/a','n/a','n/a','n/a','n/a','n/a','n/a','n/a','n/a','n/a',]
            examdata += [
                s.xray_modulation_type,
                str(s.comment),
                ]

        wsalldata.write_row(row+1,0, examdata)
        
        # Now we need to write a sheet per series protocol for each 'exams'.
        
        for s in exams.ct_radiation_dose_set.get().ct_irradiation_event_data_set.all():
            protocol = s.acquisition_protocol
            if not protocol:
                protocol = u'Unknown'
            tabtext = protocol.lower().replace(" ","_")
            translation_table = {ord('['):ord('('), ord(']'):ord(')'), ord(':'):ord(';'), ord('*'):ord('#'), ord('?'):ord(';'), ord('/'):ord('|'), ord('\\'):ord('|')}
            tabtext = tabtext.translate(translation_table) # remove illegal characters
            tabtext = tabtext[:31]
            sheetlist[tabtext]['count'] += 1
            
            examdata = [
                exams.general_equipment_module_attributes_set.get().institution_name,
                exams.general_equipment_module_attributes_set.get().manufacturer,
                exams.general_equipment_module_attributes_set.get().manufacturer_model_name,
                exams.general_equipment_module_attributes_set.get().station_name,
                exams.accession_number,
                exams.operator_name,
                exams.study_date,  # Is a date - cell needs formatting
                str(exams.patient_study_module_attributes_set.get().patient_age_decimal),
                str(exams.patient_study_module_attributes_set.get().patient_size),
                str(exams.patient_study_module_attributes_set.get().patient_weight),
                exams.patient_module_attributes_set.get().not_patient_indicator,
                exams.study_description,
                exams.requested_procedure_code_meaning,
                str(exams.ct_radiation_dose_set.get().ct_accumulated_dose_data_set.get().total_number_of_irradiation_events),
                str(exams.ct_radiation_dose_set.get().ct_accumulated_dose_data_set.get().ct_dose_length_product_total),
                ]
            examdata += [
                s.acquisition_protocol,
                str(s.ct_acquisition_type),
                str(s.exposure_time),
                str(s.scanning_length_set.get().scanning_length),
                str(s.nominal_single_collimation_width),
                str(s.nominal_total_collimation_width),
                str(s.pitch_factor),
                str(s.number_of_xray_sources),
                str(s.mean_ctdivol),
                str(s.dlp),
                ]
            if s.number_of_xray_sources > 1:
                for source in s.ct_xray_source_parameters_set.all():
                    examdata += [
                        str(source.identification_of_the_xray_source),
                        str(source.kvp),
                        str(source.maximum_xray_tube_current),
                        str(source.xray_tube_current),
                        str(source.exposure_time_per_rotation),
                        ]
            else:
                try:
                    examdata += [
                        str(s.ct_xray_source_parameters_set.get().identification_of_the_xray_source),
                        str(s.ct_xray_source_parameters_set.get().kvp),
                        str(s.ct_xray_source_parameters_set.get().maximum_xray_tube_current),
                        str(s.ct_xray_source_parameters_set.get().xray_tube_current),
                        str(s.ct_xray_source_parameters_set.get().exposure_time_per_rotation),
                        'n/a',
                        'n/a',
                        'n/a',
                        'n/a',
                        'n/a',
                        ]
                except:
                        examdata += ['n/a','n/a','n/a','n/a','n/a','n/a','n/a','n/a','n/a','n/a',]
            examdata += [
                s.xray_modulation_type,
                s.comment,
                ]

            sheetlist[tabtext]['sheet'].write_row(sheetlist[tabtext]['count'],0,examdata)

    # Could at this point go through each sheet adding on the auto filter as we now know how many of each there are...
    
    # Populate summary sheet
    tsk.progress = 'Now populating the summary sheet...'
    tsk.save()

    import pkg_resources  # part of setuptools
    import datetime

    try:
        vers = pkg_resources.require("openrem")[0].version
    except:
        vers = ''

    version = vers
    titleformat = book.add_format()
    titleformat.set_font_size=(22)
    titleformat.set_font_color=('#FF0000')
    titleformat.set_bold()
    toplinestring = 'XLSX Export from OpenREM version {0} on {1}'.format(version, str(datetime.datetime.now()))
    linetwostring = 'OpenREM is copyright 2014 The Royal Marsden NHS Foundation Trust, and available under the GPL. See http://openrem.org'
    summarysheet.write(0,0, toplinestring, titleformat)
    summarysheet.write(1,0, linetwostring)

    # Number of exams
    summarysheet.write(3,0,"Total number of exams")
    summarysheet.write(3,1,e.count())

    # Generate list of Study Descriptions
    summarysheet.write(5,0,"Study Description")
    summarysheet.write(5,1,"Frequency")
    from django.db.models import Count
    study_descriptions = e.values("study_description").annotate(n=Count("pk"))
    for row, item in enumerate(study_descriptions.order_by('n').reverse()):
        summarysheet.write(row+6,0,item['study_description'])
        summarysheet.write(row+6,1,item['n'])
    summarysheet.set_column('A:A', 25)

    # Generate list of Requested Procedures
    summarysheet.write(5,3,"Requested Procedure")
    summarysheet.write(5,4,"Frequency")
    from django.db.models import Count
    requested_procedure = e.values("requested_procedure_code_meaning").annotate(n=Count("pk"))
    for row, item in enumerate(requested_procedure.order_by('n').reverse()):
        summarysheet.write(row+6,3,item['requested_procedure_code_meaning'])
        summarysheet.write(row+6,4,item['n'])
    summarysheet.set_column('D:D', 25)

    # Generate list of Series Protocols
    summarysheet.write(5,6,"Series Protocol")
    summarysheet.write(5,7,"Frequency")
    sortedprotocols = sorted(sheetlist.iteritems(), key=lambda (k,v): v['count'], reverse=True)
    for row, item in enumerate(sortedprotocols):
        summarysheet.write(row+6,6,', '.join(item[1]['protocolname'])) # Join as can't write a list to a single cell.
        summarysheet.write(row+6,7,item[1]['count'])
    summarysheet.set_column('G:G', 15)


    book.close()
    tsk.progress = 'XLSX book written.'
    tsk.save()

    xlsxfilename = "ctexport{0}.xlsx".format(datestamp.strftime("%Y%m%d-%H%M%S%f"))

    try:
        tsk.filename.save(xlsxfilename,File(tmpxlsx))
    except OSError as e:
        tsk.progress = "Errot saving export file - please contact an administrator. Error({0}): {1}".format(e.errno, e.strerror)
        tsk.status = 'ERROR'
        tsk.save()
        return
    except:
        tsk.progress = "Unexpected error saving export file - please contact an administrator: {0}".format(sys.exc_info()[0])
        tsk.status = 'ERROR'
        tsk.save()
        return

    tsk.status = 'COMPLETE'
    tsk.processtime = (datetime.datetime.now() - datestamp).total_seconds()
    tsk.save()
