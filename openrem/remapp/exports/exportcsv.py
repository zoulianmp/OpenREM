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
..  module:: exportcsv.
    :synopsis: Module to export database data to single-sheet CSV files.

..  moduleauthor:: Ed McDonagh

"""

import csv
from celery import shared_task
from django.conf import settings


@shared_task
def exportFL2excel(filterdict):
    """Export filtered fluoro database data to a single-sheet CSV file.

    :param request: Query parameters from the fluoro filtered page URL.
    :type request: HTTP get
    
    """

    import os, sys, datetime
    from tempfile import TemporaryFile
    from django.conf import settings
    from django.core.files import File
    from django.shortcuts import redirect
    from remapp.models import General_study_module_attributes
    from remapp.models import Exports
    from remapp.interface.mod_filters import RFSummaryListFilter

    tsk = Exports.objects.create()

    tsk.task_id = exportFL2excel.request.id
    tsk.modality = "RF"
    tsk.export_type = "CSV export"
    datestamp = datetime.datetime.now()
    tsk.export_date = datestamp
    tsk.progress = 'Query filters imported, task started'
    tsk.status = 'CURRENT'
    tsk.save()

    try:
        tmpfile = TemporaryFile()
        writer = csv.writer(tmpfile)

        tsk.progress = 'CSV file created'
        tsk.save()
    except:
        messages.error(request, "Unexpected error creating temporary file - please contact an administrator: {0}".format(sys.exc_info()[0]))
        return redirect('/openrem/export/')
        
    # Get the data!
    
    e = General_study_module_attributes.objects.filter(modality_type__exact = 'RF')
    f = RFSummaryListFilter.base_filters

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
    tsk.save()
        
    numresults = e.count()

    tsk.num_records = numresults
    tsk.save()

    writer.writerow([
        'Manufacturer', 
        'Model name',
        'Institution name', 
        'Study date',
        'Accession number',
        'Patient age', 
        'Patient height', 
        'Patient mass (kg)', 
        'Study description',
        'Number of events',
        'DAP total (Gy.m2)',
        'RP dose total (Gy)',
        'Fluoro DAP total (Gy.m2)',
        'Fluoro RP dose total (Gy)',
        'Total fluoro time (ms)',
        'Acquisition DAP total (Gy.m2)',
        'Acquisition RP dose total (Gy)',
        'Total acquisition time (ms)',
        'RP definition',
        'Physician',
        'Operator'])
    for i, exams in enumerate(e):
        writer.writerow([
            exams.general_equipment_module_attributes_set.get().manufacturer, 
            exams.projection_xray_radiation_dose_set.get().observer_context_set.get().device_observer_name,
            exams.general_equipment_module_attributes_set.get().institution_name,
            exams.study_date,
            exams.accession_number, 
            exams.patient_study_module_attributes_set.get().patient_age_decimal,
            exams.patient_study_module_attributes_set.get().patient_size,
            exams.patient_study_module_attributes_set.get().patient_weight,
            exams.study_description,
            exams.projection_xray_radiation_dose_set.get().irradiation_event_xray_data_set.count(),
            exams.projection_xray_radiation_dose_set.get().accumulated_xray_dose_set.get().accumulated_projection_xray_dose_set.get().dose_area_product_total,
            exams.projection_xray_radiation_dose_set.get().accumulated_xray_dose_set.get().accumulated_projection_xray_dose_set.get().dose_rp_total,
            exams.projection_xray_radiation_dose_set.get().accumulated_xray_dose_set.get().accumulated_projection_xray_dose_set.get().fluoro_dose_area_product_total,
            exams.projection_xray_radiation_dose_set.get().accumulated_xray_dose_set.get().accumulated_projection_xray_dose_set.get().fluoro_dose_rp_total,
            exams.projection_xray_radiation_dose_set.get().accumulated_xray_dose_set.get().accumulated_projection_xray_dose_set.get().total_fluoro_time,
            exams.projection_xray_radiation_dose_set.get().accumulated_xray_dose_set.get().accumulated_projection_xray_dose_set.get().acquisition_dose_area_product_total,
            exams.projection_xray_radiation_dose_set.get().accumulated_xray_dose_set.get().accumulated_projection_xray_dose_set.get().acquisition_dose_rp_total,
            exams.projection_xray_radiation_dose_set.get().accumulated_xray_dose_set.get().accumulated_projection_xray_dose_set.get().total_acquisition_time,
            exams.projection_xray_radiation_dose_set.get().accumulated_xray_dose_set.get().accumulated_projection_xray_dose_set.get().reference_point_definition_code,
            exams.performing_physician_name,
            exams.operator_name,
            ])
        tsk.progress = "{0} of {1}".format(i+1, numresults)
        tsk.save()


    tsk.progress = 'All study data written.'
    tsk.save()

    csvfilename = "rfexport{0}.csv".format(datestamp.strftime("%Y%m%d-%H%M%S%f"))

    try:
        tsk.filename.save(csvfilename,File(tmpfile))
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


@shared_task
def exportCT2excel(filterdict):
    """Export filtered CT database data to a single-sheet CSV file.

    :param request: Query parameters from the CT filtered page URL.
    :type request: HTTP get
    
    """

    import os, sys, datetime
    from tempfile import TemporaryFile
    from django.conf import settings
    from django.core.files import File
    from django.shortcuts import redirect
    from remapp.models import General_study_module_attributes
    from remapp.models import Exports

    tsk = Exports.objects.create()

    tsk.task_id = exportCT2excel.request.id
    tsk.modality = "CT"
    tsk.export_type = "CSV export"
    datestamp = datetime.datetime.now()
    tsk.export_date = datestamp
    tsk.progress = 'Query filters imported, task started'
    tsk.status = 'CURRENT'
    tsk.save()

    try:
        tmpfile = TemporaryFile()
        writer = csv.writer(tmpfile)

        tsk.progress = 'CSV file created'
        tsk.save()
    except:
        messages.error(request, "Unexpected error creating temporary file - please contact an administrator: {0}".format(sys.exc_info()[0]))
        return redirect('/openrem/export/')
        
    # Get the data!
    from remapp.models import General_study_module_attributes
    from remapp.interface.mod_filters import CTSummaryListFilter
    
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
    tsk.save()
        
    numresults = e.count()

    tsk.progress = '{0} studies in query.'.format(numresults)
    tsk.num_records = numresults
    tsk.save()

    headers = [
        'Institution name', 
        'Manufacturer', 
        'Model name',
        'Station name',
        'Accession number',
        'Operator',
        'Study date',
        'Patient age', 
        'Patient height', 
        'Patient mass (kg)', 
        'Study description',
        'Requested procedure',
        'Number of events',
        'DLP total (mGy.cm)',
        ]

    from django.db.models import Max
    max_events = e.aggregate(Max('ct_radiation_dose__ct_accumulated_dose_data__total_number_of_irradiation_events'))

    for h in xrange(max_events['ct_radiation_dose__ct_accumulated_dose_data__total_number_of_irradiation_events__max']):
        headers += [
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
            ]
    writer.writerow(headers)

    tsk.progress = 'CSV header row written.'
    tsk.save()

    for i, exams in enumerate(e):
        examdata = [
			exams.general_equipment_module_attributes_set.get().institution_name,
			exams.general_equipment_module_attributes_set.get().manufacturer,
			exams.general_equipment_module_attributes_set.get().manufacturer_model_name,
			exams.general_equipment_module_attributes_set.get().station_name,
            exams.accession_number,
            exams.operator_name,
            exams.study_date,
            exams.patient_study_module_attributes_set.get().patient_age_decimal,
            exams.patient_study_module_attributes_set.get().patient_size,
            exams.patient_study_module_attributes_set.get().patient_weight,
            exams.study_description,
            exams.requested_procedure_code_meaning,
            exams.ct_radiation_dose_set.get().ct_accumulated_dose_data_set.get().total_number_of_irradiation_events,
            exams.ct_radiation_dose_set.get().ct_accumulated_dose_data_set.get().ct_dose_length_product_total,
			]
        for s in exams.ct_radiation_dose_set.get().ct_irradiation_event_data_set.all():
            examdata += [
                s.acquisition_protocol,
                s.ct_acquisition_type,
                s.exposure_time,
                s.scanning_length_set.get().scanning_length,
                s.nominal_single_collimation_width,
                s.nominal_total_collimation_width,
                s.pitch_factor,
                s.number_of_xray_sources,
                s.mean_ctdivol,
                s.dlp,
                ]
            if s.number_of_xray_sources > 1:
                for source in s.ct_xray_source_parameters_set.all():
                    examdata += [
                        source.identification_of_the_xray_source,
                        source.kvp,
                        source.maximum_xray_tube_current,
                        source.xray_tube_current,
                        source.exposure_time_per_rotation,
                        ]
            else:
                try:
                    examdata += [
                        s.ct_xray_source_parameters_set.get().identification_of_the_xray_source,
                        s.ct_xray_source_parameters_set.get().kvp,
                        s.ct_xray_source_parameters_set.get().maximum_xray_tube_current,
                        s.ct_xray_source_parameters_set.get().xray_tube_current,
                        s.ct_xray_source_parameters_set.get().exposure_time_per_rotation,
                        'n/a',
                        'n/a',
                        'n/a',
                        'n/a',
                        'n/a',
                        ]
                except:
                        examdata += ['n/a','n/a','n/a','n/a','n/a','n/a','n/a','n/a','n/a','n/a',]
            examdata += [s.xray_modulation_type,]

        writer.writerow(examdata)
        tsk.progress = "{0} of {1}".format(i+1, numresults)
        tsk.save()
    tsk.progress = 'All study data written.'
    tsk.save()

    csvfilename = "ctexport{0}.csv".format(datestamp.strftime("%Y%m%d-%H%M%S%f"))

    try:
        tsk.filename.save(csvfilename,File(tmpfile))
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

@shared_task
def exportMG2excel(filterdict):
    """Export filtered mammography database data to a single-sheet CSV file.

    :param request: Query parameters from the mammo filtered page URL.
    :type request: HTTP get
    
    """

    import os, sys, datetime
    from tempfile import TemporaryFile
    from django.conf import settings
    from django.core.files import File
    from django.shortcuts import redirect
    from remapp.models import General_study_module_attributes
    from remapp.models import Exports
    from remapp.interface.mod_filters import MGSummaryListFilter

    tsk = Exports.objects.create()

    tsk.task_id = exportMG2excel.request.id
    tsk.modality = "MG"
    tsk.export_type = "CSV export"
    datestamp = datetime.datetime.now()
    tsk.export_date = datestamp
    tsk.progress = 'Query filters imported, task started'
    tsk.status = 'CURRENT'
    tsk.save()

    try:
        tmpfile = TemporaryFile()
        writer = csv.writer(tmpfile)

        tsk.progress = 'CSV file created'
        tsk.save()
    except:
        messages.error(request, "Unexpected error creating temporary file - please contact an administrator: {0}".format(sys.exc_info()[0]))
        return redirect('/openrem/export/')
        
    # Get the data!
    
    s = General_study_module_attributes.objects.filter(modality_type__exact = 'MG')
    f = MGSummaryListFilter.base_filters

    for filt in f:
        if filt in filterdict and filterdict[filt]:
            # One Windows user found filterdict[filt] was a list. See https://bitbucket.org/openrem/openrem/issue/123/
            if isinstance(filterdict[filt], basestring):
                filterstring = filterdict[filt]
            else:
                filterstring = (filterdict[filt])[0]
            if filterstring != '':
                s = s.filter(**{f[filt].name + '__' + f[filt].lookup_type : filterstring})
    
    tsk.progress = 'Required study filter complete.'
    tsk.save()
        
    numresults = s.count()

    tsk.num_records = numresults
    tsk.save()
    
    writer.writerow([
        'Institution name', 
        'Manufacturer', 
        'Station name',
        'Accession number',
        'Study UID',
        'Study date',
        'Study time',
        'Patient age', 
        'Patient sex', 
        'Number of events',
        'View',
        'Aquisition',
        'Thickness',
        'Radiological Thickness',
        'Force',
        'Mag',
        'Area',
        'Mode',
        'Target',
        'Filter',
        'Focal spot size',
        'kVp',
        'mA',
        'ms',
        'uAs',
        'ESD',
        'AGD',
        '% Fibroglandular Tissue'
        'Exposure Mode Description'
        ])
    
    for i, study in enumerate(s):
        e = study.projection_xray_radiation_dose_set.get().irradiation_event_xray_data_set.all()
        for exp in e:
            writer.writerow([
                exp.projection_xray_radiation_dose.general_study_module_attributes.general_equipment_module_attributes_set.get().institution_name,
                exp.projection_xray_radiation_dose.general_study_module_attributes.general_equipment_module_attributes_set.get().manufacturer, 
                exp.projection_xray_radiation_dose.general_study_module_attributes.general_equipment_module_attributes_set.get().station_name,
                exp.projection_xray_radiation_dose.general_study_module_attributes.accession_number, 
                exp.projection_xray_radiation_dose.general_study_module_attributes.study_instance_uid,
                exp.projection_xray_radiation_dose.general_study_module_attributes.study_date,
                exp.date_time_started,
                exp.projection_xray_radiation_dose.general_study_module_attributes.patient_study_module_attributes_set.get().patient_age_decimal,
                exp.projection_xray_radiation_dose.general_study_module_attributes.patient_module_attributes_set.get().patient_sex,
                exp.projection_xray_radiation_dose.irradiation_event_xray_data_set.count(),
                exp.image_view,
                exp.acquisition_protocol,
                exp.irradiation_event_xray_mechanical_data_set.get().compression_thickness,
                exp.irradiation_event_xray_mechanical_data_set.get().dose_related_distance_measurements_set.get().radiological_thickness,
                exp.irradiation_event_xray_mechanical_data_set.get().compression_force,
                exp.irradiation_event_xray_mechanical_data_set.get().magnification_factor,
                exp.irradiation_event_xray_source_data_set.get().collimated_field_area,
                exp.irradiation_event_xray_source_data_set.get().exposure_control_mode,
                exp.irradiation_event_xray_source_data_set.get().anode_target_material,
                exp.irradiation_event_xray_source_data_set.get().xray_filters_set.get().xray_filter_material,
                exp.irradiation_event_xray_source_data_set.get().focal_spot_size,
                exp.irradiation_event_xray_source_data_set.get().kvp_set.get().kvp,
                exp.irradiation_event_xray_source_data_set.get().average_xray_tube_current,
                exp.irradiation_event_xray_source_data_set.get().exposure_time,
                exp.irradiation_event_xray_source_data_set.get().exposure_set.get().exposure,
                exp.entrance_exposure_at_rp,
                exp.irradiation_event_xray_source_data_set.get().average_glandular_dose,
                exp.percent_fibroglandular_tissue,
                exp.comment,
                ])
        tsk.progress = "{0} of {1}".format(i+1, numresults)
        tsk.save()

    tsk.progress = 'All study data written.'
    tsk.save()

    csvfilename = "mgexport{0}.csv".format(datestamp.strftime("%Y%m%d-%H%M%S%f"))

    try:
        tsk.filename.save(csvfilename,File(tmpfile))
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





