def _scanninglength(dataset,event,col): # TID 10014
    from remapp.models import Scanning_length
    scanlen = Scanning_length.objects.create(ct_irradiation_event_data=event)
    scanlen.scanning_length = "" # declare it so export works, even if it is not populated.
    r_ge = dataset[col+3]
    r_arr = r_ge.split("-")
    if r_arr[0][0] == "S":
        r1 = -float(r_arr[0][1:])
    elif r_arr[0][0] == "I":
        r1 = float(r_arr[0][1:])
    if r_arr[1][0] == "S":
        r2 = -float(r_arr[1][1:])
    elif r_arr[1][0] == "I":
        r2 = float(r_arr[1][1:])
    if r1 and r2:
        # Doesn't take into account slice width - values are likely to represent centre of last slice.
        scanlen.top_z_location_of_reconstructable_volume = min(r1,r2)
        scanlen.bottom_z_location_of_reconstructable_volume = max(r1,r2)
        scanlen.length_of_reconstructable_volume = abs(r2-r1)
        scanlen.scanning_length = abs(r2-r1) # Wrong as it doesn't take into account helical overscan, but is a best approximation of it
    scanlen.save()


def _ctxraysourceparameters(dataset,event):
    from remapp.models import Ct_xray_source_parameters
    param = Ct_xray_source_parameters.objects.create(ct_irradiation_event_data=event)
    # Nothing in here from GE, will need to populate for Siemens
    param.save()


def _ctirradiationeventdata(dataset,ct,col):
    import dicom
    from remapp.models import Ct_irradiation_event_data
    from remapp.tools.get_values import get_or_create_cid
    irr = Ct_irradiation_event_data.objects.create(ct_radiation_dose=ct)
    irr.acquisition_protocol = dataset[8]
    if dataset[col+2] == "Helical":
        irr.ct_acquisition_type = get_or_create_cid("P5-08001","Spiral Acquisition")
    elif dataset[col+2] == "Axial":
        irr.ct_acquisition_type = get_or_create_cid("113804","Sequenced Acquisition")
    irr.irradiation_event_uid = dicom.UID.generate_uid()
    irr.mean_ctdivol = dataset[col+5]
    irr.dlp = dataset[col+6]
    if dataset[col+12] is "BODY32":
        irr.ctdiw_phantom_type = get_or_create_cid("113691","IEC Body Dosimetry Phantom")
    elif dataset[col+12] is "HEAD16":
        irr.ctdiw_phantom_type = get_or_create_cid("113690","IEC Head Dosimetry Phantom")
    irr.comment = dataset[col]
    irr.save()
    _ctxraysourceparameters(dataset,irr)
    _scanninglength(dataset,irr,col)


def _ctaccumulateddosedata(dataset,ct):
    from remapp.models import Ct_accumulated_dose_data
    acc = Ct_accumulated_dose_data.objects.create(ct_radiation_dose=ct)
    acc.total_number_of_irradiation_events = dataset[10]
    acc.ct_dose_length_product_total = dataset[11]
    acc.save()


def _ctradiationdose(dataset,g):
    from remapp.models import Ct_radiation_dose
    from remapp.tools.get_values import get_or_create_cid
    ct = Ct_radiation_dose.objects.create(general_study_module_attributes=g)
    ct.procedure_reported = get_or_create_cid('P5-08000','Computed Tomography X-Ray')
    ct.has_intent = get_or_create_cid('R-408C3','Diagnostic Intent')
    ct.scope_of_accumulation = get_or_create_cid('113014','Study')
    ct.source_of_dose_information = get_or_create_cid('113868','Derived From Human-Readable Reports')
    ct.save()
    _ctaccumulateddosedata(dataset,ct)
    
    for series in range(0,10):
        if dataset[(13*series) + 13]:
            _ctirradiationeventdata(dataset,ct,((13*series)+13))
        else:
            break



def _generalequipmentmoduleattributes(dataset,g, sitecode):
    from remapp.models import General_equipment_module_attributes
    equip = General_equipment_module_attributes.objects.create(general_study_module_attributes=g)
    if sitecode is "C":
        equip.manufacturer = "GE"
        equip.institution_name = "Royal Marsden Hospital"
        equip.institution_address = "Fulham Road, London"
        equip.station_name = "rpycls32ct03" # Check this!
        equip.institutional_department_name = "Radiology"
        equip.manufacturer_model_name = "LightSpeed Pro 32"
        equip.device_serial_number = "" # Find this out! - blank in GE RDSR
        equip.software_versions = "" # Leave blank? Will have changed over the course of the data recording.
        equip.gantry_id = "" # Find this out - Missing GE RDSR
        # Leave spatial resolution and calibration
    elif sitecode is "S":
        equip.manufacturer = "GE"
        equip.institution_name = "The Royal Marsden, Sutton"
        equip.institution_address = "Downs Road, Surrey"
        equip.station_name = "RPYS_LS16CT01" # Check this!
        equip.institutional_department_name = "Radiology"
        equip.manufacturer_model_name = "LightSpeed 16"
        equip.device_serial_number = "" # Find this out!
        equip.software_versions = "" # Leave blank? Will have changed over the course of the data recording.
        equip.gantry_id = "" # Find this out
        # Leave spatial resolution and calibration
    elif sitecode is "F":
        equip.manufacturer = "Siemens"
        equip.institution_name = "The Royal Brompton"
        equip.institution_address = "Fuham Road, London"
        equip.station_name = "SENS64" # Check this!
        equip.institutional_department_name = "Radiology"
        equip.manufacturer_model_name = "Sensation 64"
        equip.device_serial_number = "" # Find this out!
        equip.software_versions = "" # Leave blank? Will have changed over the course of the data recording.
        equip.gantry_id = "" # Find this out
        # Leave spatial resolution and calibration
    equip.save()    


def _generalstudymoduleattributes(dataset,g):
    import dicom
    from remapp.tools.dcmdatetime import make_date, make_time
    g.study_instance_uid = dicom.UID.generate_uid()
    g.study_date = make_date(dataset[4])
    g.study_time = make_time(dataset[7])
    g.accession_number = dataset[3]
    g.modality_type = 'CT'
    if dataset[8] != "#N/A" and not dataset[8]:
        g.study_description = dataset[8]
    else:
        g.study_description = dataset[9]
    g.save()


def _patientstudymoduleattributes(dataset,g): # C.7.2.2
    from remapp.models import Patient_study_module_attributes
    patientatt = Patient_study_module_attributes.objects.create(general_study_module_attributes=g)
    patientatt.patient_age = dataset[1]
    if dataset[2] != "#N/A" and not dataset[2]:
        patientatt.patient_age_decimal = dataset[2]
    else:
        if 'Y' in patientatt.patient_age:
            patientatt.patient_age_decimal = patientatt.patient_age[:patientatt.patient_age.find('Y')]
        elif 'M' in patientatt.patient_age:
            months = patientatt.patient_age[:patientatt.patient_age.find('M')]
            patientatt.patient_age_decimal = float(months)/12
        elif 'D' in patientatt.patient_age:
            days = patientatt.patient_age[:patientatt.patient_age.find('D')]
            patientatt.patient_age_decimal = float(days)/365
    if dataset[6] != "#N/A":
        patientatt.patient_weight = dataset[6]
    if dataset[5] != "#N/A":
        patientatt.patient_size = dataset[5]
    patientatt.save()


def _patientmoduleattributes(dataset,g):
    from remapp.models import Patient_module_attributes
    pat = Patient_module_attributes.objects.create(general_study_module_attributes=g)
    pat.patient_sex = dataset[0]
    pat.save()


def _ctcsv2db(dataset, sitecode):
    from django.db import models
    from remapp.models import General_study_module_attributes
    from django import db
    
    # If there isn't an accession number, ignore. If there is, check to see if it has been entered into the database already.
    if dataset[3] != '':
        e = General_study_module_attributes.objects.filter(accession_number__exact = dataset[3])
        if not e:
            g = General_study_module_attributes.objects.create()
            _generalstudymoduleattributes(dataset,g)
            _generalequipmentmoduleattributes(dataset, g, sitecode)
            _patientstudymoduleattributes(dataset,g)
            _patientmoduleattributes(dataset,g)
            _ctradiationdose(dataset,g)
    db.reset_queries()
    
    
def _add_project_to_path():
    import os, sys
    # Add project to path, assuming openrem app has been installed within project
    basepath = os.path.dirname(__file__)
    projectpath = os.path.abspath(os.path.join(basepath, "..","openrem"))
    if projectpath not in sys.path:
        sys.path.append(projectpath)


def _ctcsv(csv_file, sitecode):
    """Extract radiation dose related data from legacy csv files
    
    Arguments:
    filename : relative or absolute path to csv file.
    
    Limitations:
    Only suitable for csv versions of the excel master sheet from older versions of the RMH CT dose recording tools.
    """

    import os, csv
    _add_project_to_path()
    os.environ['DJANGO_SETTINGS_MODULE'] = 'openrem.settings'
    
    dataset = csv.reader(open(csv_file, 'rb'))        
    ctlist = []
    ctlist.extend(dataset)
    for line in ctlist:
        dummy = _ctcsv2db(line, sitecode)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        sys.exit('Error: Supply exactly two arguments separated by a space - the csv file, and the site code - C, S or F')
    sys.exit(_ctcsv(sys.argv[1], sys.argv[2]))
