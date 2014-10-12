#    OpenREM - Radiation Exposure Monitoring tools for the physicist
#    Copyright (C) 2014  The Royal Marsden NHS Foundation Trust and Jonathan Cole
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
..  module:: mg_csv_nhsbsp.
    :synopsis: Module to export mammography data to CSV files in the NHSBSP format.

..  moduleauthor:: Ed McDonagh and Jonathan Cole

"""

import csv
from celery import shared_task
from django.conf import settings



@shared_task
def mg_csv_nhsbsp(filterdict):
    """Export filtered mammography database data to a NHSBSP formatted single-sheet CSV file.

    :param filterdict: Dictionary of query parameters from the mammo filtered page URL.
    :type filterdict: dict
    :returns: None - file is saved to disk and location is stored in database
    
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

    tsk.task_id = mg_csv_nhsbsp.request.id
    tsk.modality = "MG"
    tsk.export_type = "NHSBSP CSV export"
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
        'Survey number',
        'Patient number',
        'View code',
        'kV',
        'Anode',
        'Filter',
        'Thickness',
        'mAs',
        'large cassette used',
        'auto/man',
        'Auto mode',
        'Density setting',
        'Age',
        'Comment',
        'AEC density mode',		
        ])

    for i, study in enumerate(s):
        e = study.projection_xray_radiation_dose_set.get().irradiation_event_xray_data_set.all()
        for exp in e:
            viewCode = str(exp.laterality)
            viewCode = viewCode[:1]
            if str(exp.image_view) == 'cranio-caudal':
			    viewCode = viewCode + 'CC'
            elif str(exp.image_view) == 'medio-lateral oblique':
                viewCode = viewCode + 'OB'
            else:
                viewCode = viewCode + str(exp.image_view)
            target = str(exp.irradiation_event_xray_source_data_set.get().anode_target_material)
            if "TUNGSTEN" in target.upper():
                target = 'W'
            elif "MOLY" in target.upper():
			    target = 'Mo'
            elif "RHOD" in target.upper():
                target = 'Rh'
            filterMat = str(exp.irradiation_event_xray_source_data_set.get().xray_filters_set.get().xray_filter_material)
            if "ALUM" in filterMat.upper():
                filterMat = 'Al'
            elif "MOLY" in filterMat.upper():
                filterMat = 'Mo'
            elif "RHOD" in filterMat.upper():
                filterMat = 'Rh'
            elif "SILV" in filterMat.upper():
                filterMat = 'Ag'
            automan = str(exp.irradiation_event_xray_source_data_set.get().exposure_control_mode)
            if "AUTO" in automan.upper():
                automan = 'AUTO'
            elif "MAN" in automan.upper():
                automan = "MANUAL"
			
            writer.writerow([
                '1',
                i+1,
                viewCode,
                exp.irradiation_event_xray_source_data_set.get().kvp_set.get().kvp,
                target,
                filterMat,
                exp.irradiation_event_xray_mechanical_data_set.get().compression_thickness,
                exp.irradiation_event_xray_source_data_set.get().exposure_set.get().exposure / 1000,
                '', # not applicable to FFDM
                automan,				
                exp.irradiation_event_xray_source_data_set.get().exposure_control_mode,
                '', # no consistent behaviour for recording density setting on FFDM units
                exp.projection_xray_radiation_dose.general_study_module_attributes.patient_study_module_attributes_set.get().patient_age_decimal,
                '', # not in DICOM headers
                '', # no consistent behaviour for recording density mode on FFDM units
                ])
        tsk.progress = "{0} of {1}".format(i+1, numresults)
        tsk.save()

    tsk.progress = 'All study data written.'
    tsk.save()

    csvfilename = "mg_nhsbsp_{0}.csv".format(datestamp.strftime("%Y%m%d-%H%M%S%f"))

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
    
