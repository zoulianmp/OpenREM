
def _irradiationeventxraydetectordata(dataset,event):
    from remapp.models import Irradiation_event_xray_detector_data
    detector = Irradiation_event_xray_detector_data.objects.create(irradiation_event_xray_data=event)
    # This table is just relating to exposure index, so nothing to report. 
    # We do know the 'sensitivity' though, and probably the detector dose...
    _deviceparticipant(dataset,'detector',detector)

def _xrayfilters(dataset,source):
    from remapp.models import Xray_filters
    from remapp.tools.get_values import get_or_create_cid
    filters = Xray_filters.objects.create(irradiation_event_xray_source_data=source)
    xray_filter_material = dataset[23]
    if xray_filter_material == 'MOLYBDENUM':
        filters.xray_filter_material = get_or_create_cid('C-150F9','Molybdenum or Molybdenum compound')
    if xray_filter_material == 'RHODIUM':
        filters.xray_filter_material = get_or_create_cid('C-167F9','Rhodium or Rhodium compound')
    filters.save()

def _xraygrid(gridcode,source):
    from remapp.models import Xray_grid
    from remapp.tools.get_values import get_or_create_cid
    grid = Xray_grid.objects.create(irradiation_event_xray_source_data=source)
    if gridcode == '111646':
        grid.xray_grid = get_or_create_cid('111646','No grid')
    if gridcode == '111642':
        grid.xray_grid = get_or_create_cid('111642','Focused grid')
    if gridcode == '111643':
        grid.xray_grid = get_or_create_cid('111643','Reciprocating grid')
    grid.save()

def _kvp(dataset,source):
    from remapp.models import Kvp
    kv = Kvp.objects.create(irradiation_event_xray_source_data=source)
    kv.kvp = dataset[26]
    kv.save()

def _exposure(dataset,source):
    from remapp.models import Exposure
    exp = Exposure.objects.create(irradiation_event_xray_source_data=source)
    exp.exposure = dataset[29] # uAs
    exp.save()

def _deviceparticipant(dataset,eventdatatype,foreignkey):
    from remapp.models import Device_participant
    if eventdatatype == 'detector':
        device = Device_participant.objects.create(irradiation_event_xray_detector_data=foreignkey)
    elif eventdatatype == 'source':
        device = Device_participant.objects.create(irradiation_event_xray_source_data=foreignkey)
    elif eventdatatype == 'accumulated':
        device = Device_participant.objects.create(accumulated_xray_dose=foreignkey)
    device.device_model_name = 'Senograph DS'
    device.device_manufacturer = 'GE'
    device.device_serial_number = dataset[2]
    device.save()


def _irradiationeventxraysourcedata(dataset,event):
    from remapp.models import Irradiation_event_xray_source_data
    from remapp.tools.get_values import get_or_create_cid
    source = Irradiation_event_xray_source_data.objects.create(irradiation_event_xray_data=event)
    # AGD/MGD is dGy in Mammo headers, and was dGy in Radiation Dose SR - CP1194 changes this to mGy!
    source.average_glandular_dose = 100.0 * float(dataset[32]) #MGD in dGy * 100 = mGy 
    source.average_xray_tube_current = dataset[28] # mA
    source.exposure_time = dataset[27]
    source.focal_spot_size = dataset[25]
    anode_target_material = dataset[22]
    if anode_target_material == 'MOLYBDENUM':
        source.anode_target_material = get_or_create_cid('C-150F9','Molybdenum or Molybdenum compound')
    if anode_target_material == 'RHODIUM':
        source.anode_target_material = get_or_create_cid('C-167F9','Rhodium or Rhodium compound')
    _xrayfilters(dataset,source)
    collimated_field_area = dataset[19]
    source.collimated_field_area = float(collimated_field_area.split('\\')[0]) * float(collimated_field_area.split('\\')[1]) / 1000000
    source.exposure_control_mode = dataset[35]
    source.save()
    _kvp(dataset,source)
    _exposure(dataset,source)
    xray_grid = dataset[24]
    if xray_grid == 'NONE':
        _xraygrid('111646',source)
    elif xray_grid == 'RECIPROCATING\\FOCUSED':
        _xraygrid('111642',source)
        _xraygrid('111643',source)

def _doserelateddistancemeasurements(dataset,mech):
    from remapp.models import Dose_related_distance_measurements
    dist = Dose_related_distance_measurements.objects.create(irradiation_event_xray_mechanical_data=mech)
    dist.distance_source_to_detector = dataset[14]
    dist.distance_source_to_entrance_surface = dataset[17]
    dist.save()

def _irradiationeventxraymechanicaldata(dataset,event):
    from remapp.models import Irradiation_event_xray_mechanical_data
    mech = Irradiation_event_xray_mechanical_data.objects.create(irradiation_event_xray_data=event)
    mech.compression_thickness = dataset[20]
    mech.compression_force = float(dataset[21])/10
    mech.magnification_factor = dataset[16]
    mech.save()
    _doserelateddistancemeasurements(dataset,mech)

def _accumulatedmammo_update(dataset,event): # TID 10005
#?    from remapp.tools.get_values import get_value_kw, get_or_create_cid
    accummam = event.projection_xray_radiation_dose.accumulated_xray_dose_set.get().accumulated_mammography_xray_dose_set.get()
    if event.irradiation_event_xray_source_data_set.get().average_glandular_dose:
        accummam.accumulated_average_glandular_dose += event.irradiation_event_xray_source_data_set.get().average_glandular_dose
    accummam.save()

def _irradiationeventxraydata(dataset,proj):
    from remapp.models import Irradiation_event_xray_data
    from remapp.tools.get_values import get_or_create_cid
    from remapp.tools.dcmdatetime import make_date_time
    import dicom
    event = Irradiation_event_xray_data.objects.create(projection_xray_radiation_dose=proj)
    event.irradiation_event_uid = dicom.UID.generate_uid()
    event.date_time_started = make_date_time(str(dataset[5]) + str(dataset[6]))
    event.irradiation_event_type = get_or_create_cid('113611', 'Stationary Acquisition')
    event.acquisition_protocol = dataset[11]
    event.anatomical_structure = get_or_create_cid('T-04000','Breast')
    image_view = dataset[12]
    if image_view == 'ML':
        event.image_view = get_or_create_cid('R-10224','medio-lateral')
    elif image_view == 'MLO':
        event.image_view = get_or_create_cid('R-10226','medio-lateral oblique')
    elif image_view == 'LM':
        event.image_view = get_or_create_cid('R-10228','latero-medial')
    elif image_view == 'LMO':
        event.image_view = get_or_create_cid('R-10230','latero-medial oblique')
    elif image_view == 'CC':
        event.image_view = get_or_create_cid('R-10242','cranio-caudal')
    elif image_view == 'FB':
        event.image_view = get_or_create_cid('R-10244','caudo-cranial (from below)')
    elif image_view == 'SIO':
        event.image_view = get_or_create_cid('R-102D0','superolateral to inferomedial oblique')
    elif image_view == 'ISO':
        event.image_view = get_or_create_cid('R-40AAA','inferomedial to superolateral oblique')
    elif image_view == 'XCCL':
        event.image_view = get_or_create_cid('R-1024A','cranio-caudal exaggerated laterally')
    elif image_view == 'XCCM':
        event.image_view = get_or_create_cid('R-1024B','cranio-caudal exaggerated medially')
    event.percent_fibroglandular_tissue = dataset[31][:len(dataset[31])-1]
    event.target_region = get_or_create_cid('T-04000','Breast')
    event.entrance_exposure_at_rp = float(dataset[30])/1000
    event.comment = dataset[36]
    procedure_this = dataset[11]
    procedure_general = event.projection_xray_radiation_dose.general_study_module_attributes.procedure_code_meaning
    if procedure_this not in procedure_general:
        event.projection_xray_radiation_dose.general_study_module_attributes.procedure_code_meaning = procedure_general + ',' + procedure_this
        event.projection_xray_radiation_dose.general_study_module_attributes.save()
    event.save()
    # personparticipant
    _irradiationeventxraydetectordata(dataset,event)
    _irradiationeventxraysourcedata(dataset,event)
    _irradiationeventxraymechanicaldata(dataset,event)
    _accumulatedmammo_update(dataset,event)
    
def _accumulatedxraydose(dataset,proj):
    from remapp.models import Accumulated_xray_dose, Accumulated_mammography_xray_dose
    from remapp.tools.get_values import get_value_kw, get_or_create_cid
    accum = Accumulated_xray_dose.objects.create(projection_xray_radiation_dose=proj)
    accum.acquisition_plane = get_or_create_cid('113622','Single Plane')
    accum.save()
    accummam = Accumulated_mammography_xray_dose.objects.create(accumulated_xray_dose=accum)
    accummam.accumulated_average_glandular_dose = 0.0
    accummam.save()
    
    
def _projectionxrayradiationdose(dataset,g):
    from remapp.models import Projection_xray_radiation_dose, Observer_context
    from remapp.tools.get_values import get_or_create_cid
    proj = Projection_xray_radiation_dose.objects.create(general_study_module_attributes=g)
    proj.procedure_reported = get_or_create_cid('P5-40010','Mammography')
    proj.has_intent = get_or_create_cid('R-408C3','Diagnostic Intent')
    proj.scope_of_accumulation = get_or_create_cid('113014','Study')
    proj.save()
    _accumulatedxraydose(dataset,proj)
    _irradiationeventxraydata(dataset,proj)


def _generalequipmentmoduleattributes(dataset,g):
    from remapp.models import General_equipment_module_attributes
    equip = General_equipment_module_attributes.objects.create(general_study_module_attributes=g)
    equip.manufacturer = 'GE'
    equip.station_name = dataset[3]
    if equip.station_name[3] == 'C':
        equip.institution_name = 'The Royal Marsden, Chelsea'
    elif equip.station_name[3] == 'S':
        equip.institution_name = 'The Royal Marsden, Sutton'
    equip.manufacturer_model_name = 'Senographe DS'
    equip.device_serial_number = dataset[1]
    equip.software_versions = dataset[4][13:]
    equip.save()

def _patientstudymoduleattributes(dataset,g): # C.7.2.2
    from remapp.models import Patient_study_module_attributes
    patientatt = Patient_study_module_attributes.objects.create(general_study_module_attributes=g)
    patientatt.patient_age = dataset[9]
    if 'Y' in patientatt.patient_age:
        patientatt.patient_age_decimal = patientatt.patient_age[:patientatt.patient_age.find('Y')]
    elif 'M' in patientatt.patient_age:
        months = patientatt.patient_age[:patientatt.patient_age.find('M')]
        patientatt.patient_age_decimal = float(months)/12
    elif 'D' in patientatt.patient_age:
        days = patientatt.patient_age[:patientatt.patient_age.find('D')]
        patientatt.patient_age_decimal = float(days)/365
    patientatt.save()

def _patientmoduleattributes(dataset,g):
    from remapp.models import Patient_module_attributes
    pat = Patient_module_attributes.objects.create(general_study_module_attributes=g)
    pat.patient_sex = dataset[8]
    pat.save()

def _generalstudymoduleattributes(dataset,g):
    from remapp.tools.dcmdatetime import make_date, make_time
    import dicom
    g.study_instance_uid = dicom.UID.generate_uid()
    g.study_date = make_date(dataset[5])
    g.study_time = make_time(dataset[6])
    g.accession_number = dataset[7]
    g.modality_type = 'MG'
    g.procedure_code_meaning = dataset[11]
    g.save()
    _generalequipmentmoduleattributes(dataset,g)
    _patientstudymoduleattributes(dataset,g)
    _patientmoduleattributes(dataset,g)
    _projectionxrayradiationdose(dataset,g)



def _mgcsv2db(line):
    from django.db import models
    from remapp.models import General_study_module_attributes
    from remapp.tools.dcmdatetime import make_date_time, make_date, make_time
    from django import db
    from datetime import timedelta

    # First off, some logic to see if exposure is part of an exam already registered
    if line[7] != '': # Is there an accession number?
        e = General_study_module_attributes.objects.filter(accession_number__exact = line[7])
        if e: # ie the acccession number has been found, so only an irradiation event needs to be created
            itime = e.get().projection_xray_radiation_dose_set.get().irradiation_event_xray_data_set.filter(
                date_time_started__exact = make_date_time(str(line[5]) + str(line[6])))
            if not itime: # ie there aren't any existing events with the same date/time stamp
                _irradiationeventxraydata(line,e.get().projection_xray_radiation_dose_set.get())
        else:
            g = General_study_module_attributes.objects.create()
            _generalstudymoduleattributes(line,g)
    else:
        if not (line[8] == 'O' and line[9] == '001D'):
            window = timedelta(seconds=(30*60)) # half an hour either side of any previous exposures 
            e = General_study_module_attributes.objects.filter(
                    accession_number__exact = ''
                ).filter(
                    study_date__exact = make_date(line[5])
                ).filter(
                    general_equipment_module_attributes__device_serial_number__exact = line[1]
                ).filter(
                    patient_study_module_attributes__patient_age__exact = line[9]
                ).filter(
                    study_time__gt = make_time(line[6]) - window
                ).filter(
                    study_time__lt = make_time(line[6]) + window
                )
            if e:
                if e.count() > 1:
                    print 'More than one study matched the no accession number matching filter :-( ' + e[0].general_equipment_module_attributes_set.get().device_serial_number + ' ' + e.study_date + ' ' + e.study_time
                else:
                    itime = e.get().projection_xray_radiation_dose_set.get().irradiation_event_xray_data_set.filter(
                        date_time_started__exact = make_date_time(str(line[5]) + str(line[6])))
                    if not itime:
                        _irradiationeventxraydata(line,e.get().projection_xray_radiation_dose_set.get())
            else:
                g = General_study_module_attributes.objects.create()
                _generalstudymoduleattributes(line,g)
    db.reset_queries()

def _add_project_to_path():
    import os, sys
    # Add project to path, assuming openrem app has been installed within project
    basepath = os.path.dirname(__file__)
    projectpath = os.path.abspath(os.path.join(basepath, "..","openrem"))
    if projectpath not in sys.path:
        sys.path.append(projectpath)

def _mgcsv(csv_file):
    """Extract radiation dose related data from legacy csv files
    
    Arguments:
    filename : relative or absolute path to csv file.
    
    Limitations:
    Only suitable for csv mammography files from older versions of the RMH dose recording tools.
    """

    import os, csv
    _add_project_to_path()
    os.environ['DJANGO_SETTINGS_MODULE'] = 'openrem.settings'
    
    dataset = csv.reader(open(csv_file, 'rb'))        
    mglist = []
    mglist.extend(dataset)
    for line in mglist:
        dummy = _mgcsv2db(line)


if __name__ == "__main__":
    import sys, csv
    if len(sys.argv) != 2:
        sys.ext('Error: Supply exactly one argument - the CSV file')
    sys.exit(_mgcsv(sys.argv[1]))

