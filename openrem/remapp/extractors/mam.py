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
..  module:: mam.
    :synopsis: Module to extract radiation dose related data from mammography image objects.

..  moduleauthor:: Ed McDonagh

"""
def _xrayfilters(dataset,source):
    from remapp.models import Xray_filters
    from remapp.tools.get_values import get_value_kw, get_or_create_cid
    filters = Xray_filters.objects.create(irradiation_event_xray_source_data=source)
    xray_filter_material = get_value_kw('FilterMaterial',dataset)
    if xray_filter_material:
        if xray_filter_material.strip().lower() == 'molybdenum':
            filters.xray_filter_material = get_or_create_cid('C-150F9','Molybdenum or Molybdenum compound')
        if xray_filter_material.strip().lower() == 'rhodium':
            filters.xray_filter_material = get_or_create_cid('C-167F9','Rhodium or Rhodium compound')
        if xray_filter_material.strip().lower() == 'silver':
            filters.xray_filter_material = get_or_create_cid('C-137F9','Silver or Silver compound')
        if xray_filter_material.strip().lower() == 'aluminum' or xray_filter_material.strip().lower() == 'aluminium':
            filters.xray_filter_material = get_or_create_cid('C-120F9','Aluminum or Aluminum compound')

        filters.save()
    

def _kvp(dataset,source):
    from remapp.models import Kvp
    from remapp.tools.get_values import get_value_kw
    kv = Kvp.objects.create(irradiation_event_xray_source_data=source)
    kv.kvp = get_value_kw('KVP',dataset)
    kv.save()


def _exposure(dataset,source):
    from remapp.models import Exposure
    exp = Exposure.objects.create(irradiation_event_xray_source_data=source)
    from remapp.tools.get_values import get_value_kw
    exp.exposure = get_value_kw('ExposureInuAs',dataset) # uAs
    exp.save()


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


def _irradiationeventxraysourcedata(dataset,event):
    from remapp.models import Irradiation_event_xray_source_data
    from remapp.tools.get_values import get_value_kw, get_or_create_cid
    source = Irradiation_event_xray_source_data.objects.create(irradiation_event_xray_data=event)
    # AGD/MGD is dGy in Mammo headers, and was dGy in Radiation Dose SR - CP1194 changes this to mGy!
    agd_dgy = get_value_kw('OrganDose',dataset) #AGD in dGy 
    if agd_dgy:
        source.average_glandular_dose = float(agd_dgy) * 100.0 #AGD in mGy
    source.average_xray_tube_current = get_value_kw('XRayTubeCurrent',dataset)
    source.exposure_time = get_value_kw('ExposureTime',dataset)
    source.focal_spot_size = get_value_kw('FocalSpots',dataset)
    anode_target_material = get_value_kw('AnodeTargetMaterial',dataset)
    if anode_target_material.strip().lower() == 'molybdenum':
        source.anode_target_material = get_or_create_cid('C-150F9','Molybdenum or Molybdenum compound')
    if anode_target_material.strip().lower() == 'rhodium':
        source.anode_target_material = get_or_create_cid('C-167F9','Rhodium or Rhodium compound')
    if anode_target_material.strip().lower() == 'tungsten':
        source.anode_target_material = get_or_create_cid('C-164F9','Tungsten or Tungsten compound')
    collimated_field_area = get_value_kw('FieldOfViewDimensions',dataset)
    if collimated_field_area:
        source.collimated_field_area = float(collimated_field_area[0]) * float(collimated_field_area[1]) / 1000000
    source.exposure_control_mode = get_value_kw('ExposureControlMode',dataset)
    source.save()
    _xrayfilters(dataset,source)
    _kvp(dataset,source)
    _exposure(dataset,source)
    xray_grid = get_value_kw('Grid',dataset)
    if xray_grid:
        if xray_grid == 'NONE':
            _xraygrid('111646',source)
        elif xray_grid == ['RECIPROCATING', 'FOCUSED']:
            _xraygrid('111642',source)
            _xraygrid('111643',source)


def _doserelateddistancemeasurements(dataset,mech):
    from remapp.models import Dose_related_distance_measurements
    from remapp.tools.get_values import get_value_kw, get_value_num
    dist = Dose_related_distance_measurements.objects.create(irradiation_event_xray_mechanical_data=mech)
    dist.distance_source_to_detector = get_value_kw('DistanceSourceToDetector',dataset)
    dist.distance_source_to_entrance_surface = get_value_kw('DistanceSourceToEntrance',dataset)
    dist.radiological_thickness = get_value_num(0x00451049,dataset)
    dist.save()        


def _irradiationeventxraymechanicaldata(dataset,event):
    from remapp.models import Irradiation_event_xray_mechanical_data
    from remapp.tools.get_values import get_value_kw
    mech = Irradiation_event_xray_mechanical_data.objects.create(irradiation_event_xray_data=event)
    mech.compression_thickness = get_value_kw('BodyPartThickness',dataset)
    mech.compression_force = float(get_value_kw('CompressionForce',dataset))/10 # GE Conformance statement says in N, treating as dN
    mech.magnification_factor = get_value_kw('EstimatedRadiographicMagnificationFactor',dataset)
    mech.column_angulation = get_value_kw('PositionerPrimaryAngle',dataset)
    mech.save()
    _doserelateddistancemeasurements(dataset,mech)


def _accumulatedmammo_update(dataset,event): # TID 10005
    from remapp.tools.get_values import get_value_kw, get_or_create_cid
    accummam = event.projection_xray_radiation_dose.accumulated_xray_dose_set.get().accumulated_mammography_xray_dose_set.get()
    if event.irradiation_event_xray_source_data_set.get().average_glandular_dose:
        accummam.accumulated_average_glandular_dose += event.irradiation_event_xray_source_data_set.get().average_glandular_dose
    if event.laterality:
        if accummam.laterality:
            if accummam.laterality.code_meaning == 'Left breast':
                if event.laterality.code_meaning == 'Right':
                    accummam.laterality = get_or_create_cid('T-04080','Both breasts')
            if accummam.laterality.code_meaning == 'Right breast':
                if event.laterality.code_meaning == 'Left':
                    accummam.laterality = get_or_create_cid('T-04080','Both breasts')
        else:
            if event.laterality.code_meaning == 'Right':
                accummam.laterality = get_or_create_cid('T-04020','Right breast')
            if event.laterality.code_meaning == 'Left':
                accummam.laterality = get_or_create_cid('T-04030','Left breast')
    accummam.save()


def _irradiationeventxraydata(dataset,proj): # TID 10003
    from remapp.models import Irradiation_event_xray_data
    from remapp.tools.get_values import get_value_kw, get_or_create_cid, get_seq_code_value, get_seq_code_meaning
    from remapp.tools.dcmdatetime import make_date_time
    event = Irradiation_event_xray_data.objects.create(projection_xray_radiation_dose=proj)
    event.acquisition_plane = get_or_create_cid('113622', 'Single Plane')
    event.irradiation_event_uid = get_value_kw('SOPInstanceUID',dataset)
    event_time = get_value_kw('AcquisitionTime',dataset)
    event_date = get_value_kw('AcquisitionDate',dataset)
    event.date_time_started = make_date_time('{0}{1}'.format(event_date,event_time))
    event.irradiation_event_type = get_or_create_cid('113611','Stationary Acquisition')
    event.acquisition_protocol = get_value_kw('ProtocolName',dataset)
    event.anatomical_structure = get_or_create_cid(get_seq_code_value('AnatomicRegionSequence',dataset),get_seq_code_meaning('AnatomicRegionSequence',dataset))
    laterality = get_value_kw('ImageLaterality',dataset)
    if laterality:
        if laterality.strip() == 'R':
            event.laterality = get_or_create_cid('G-A100','Right')
        if laterality.strip() == 'L':
            event.laterality = get_or_create_cid('G-A101','Left')
    event.image_view = get_or_create_cid(get_seq_code_value('ViewCodeSequence',dataset),get_seq_code_meaning('ViewCodeSequence',dataset))
    # image view modifier?
    if event.anatomical_structure:
        event.target_region = event.anatomical_structure
    event.entrance_exposure_at_rp = get_value_kw('EntranceDoseInmGy',dataset)
    # reference point definition?
    pc_fibroglandular = get_value_kw('CommentsOnRadiationDose',dataset)
    if pc_fibroglandular:
        if '%' in pc_fibroglandular:
            event.percent_fibroglandular_tissue = pc_fibroglandular.replace('%','').strip()
    event.comment = get_value_kw('ExposureControlModeDescription',dataset)
    event.save()

#    irradiationeventxraydetectordata(dataset,event)
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
    from remapp.models import Projection_xray_radiation_dose
    from remapp.tools.get_values import get_or_create_cid
    proj = Projection_xray_radiation_dose.objects.create(general_study_module_attributes=g)
    proj.procedure_reported = get_or_create_cid('P5-40010','Mammography')
    proj.has_intent = get_or_create_cid('R-408C3','Diagnostic Intent')
    proj.scope_of_accumulation = get_or_create_cid('113014','Study')
    proj.source_of_dose_information = get_or_create_cid('113866','Copied From Image Attributes')
    proj.xray_detector_data_available = get_or_create_cid('R-00339','No')
    proj.xray_source_data_available = get_or_create_cid('R-0038D','Yes')
    proj.xray_mechanical_data_available = get_or_create_cid('R-0038D','Yes')
    proj.save()
    _accumulatedxraydose(dataset,proj)
    _irradiationeventxraydata(dataset,proj)


def _generalequipmentmoduleattributes(dataset,study):
    from remapp.models import General_equipment_module_attributes
    from remapp.tools.get_values import get_value_kw
    from remapp.tools.dcmdatetime import get_date, get_time
    equip = General_equipment_module_attributes.objects.create(general_study_module_attributes=study)
    equip.manufacturer = get_value_kw("Manufacturer",dataset)
    equip.institution_name = get_value_kw("InstitutionName",dataset)
    equip.institution_address = get_value_kw("InstitutionAddress",dataset)
    equip.station_name = get_value_kw("StationName",dataset)
    equip.institutional_department_name = get_value_kw("InstitutionalDepartmentName",dataset)
    equip.manufacturer_model_name = get_value_kw("ManufacturerModelName",dataset)
    equip.device_serial_number = get_value_kw("DeviceSerialNumber",dataset)
    equip.software_versions = get_value_kw("SoftwareVersions",dataset)
    equip.gantry_id = get_value_kw("GantryID",dataset)
    equip.spatial_resolution = get_value_kw("SpatialResolution",dataset)
    equip.date_of_last_calibration = get_date("DateOfLastCalibration",dataset)
    equip.time_of_last_calibration = get_time("TimeOfLastCalibration",dataset)
    equip.save()


def _patientstudymoduleattributes(dataset,g): # C.7.2.2
    from remapp.models import Patient_study_module_attributes
    from remapp.tools.get_values import get_value_kw
    patientatt = Patient_study_module_attributes.objects.create(general_study_module_attributes=g)
    patientatt.patient_age = get_value_kw('PatientAge',dataset)
    patientatt.save()


def _patientmoduleattributes(dataset,g): # C.7.1.1
    from remapp.models import Patient_module_attributes, Patient_study_module_attributes
    from remapp.tools.get_values import get_value_kw
    from remapp.tools.dcmdatetime import get_date
    from remapp.tools.not_patient_indicators import get_not_pt
    from datetime import timedelta
    from decimal import Decimal
    pat = Patient_module_attributes.objects.create(general_study_module_attributes=g)
    pat.patient_sex = get_value_kw('PatientSex',dataset)
    patient_birth_date = get_date('PatientBirthDate',dataset) # Not saved to database
    pat.not_patient_indicator = get_not_pt(dataset)
    patientatt = Patient_study_module_attributes.objects.get(general_study_module_attributes=g)
    if patient_birth_date:
        patientatt.patient_age_decimal = Decimal((g.study_date.date() - patient_birth_date.date()).days)/Decimal('365.25')
    elif patientatt.patient_age:
        if patientatt.patient_age[-1:]=='Y':
            patientatt.patient_age_decimal = Decimal(patientatt.patient_age[:-1])
        elif patientatt.patient_age[-1:]=='M':
            patientatt.patient_age_decimal = Decimal(patientatt.patient_age[:-1])/Decimal('12')
        elif patientatt.patient_age[-1:]=='D':
            patientatt.patient_age_decimal = Decimal(patientatt.patient_age[:-1])/Decimal('365.25') 
    if patientatt.patient_age_decimal:
        patientatt.patient_age_decimal = patientatt.patient_age_decimal.quantize(Decimal('.1'))
    patientatt.save()
    pat.save()



def _generalstudymoduleattributes(dataset,g):
    from remapp.tools.get_values import get_value_kw, get_seq_code_meaning, get_seq_code_value
    from remapp.tools.dcmdatetime import get_date, get_time
    g.study_instance_uid = get_value_kw('StudyInstanceUID',dataset)
    g.study_date = get_date('StudyDate',dataset)
    g.study_time = get_time('StudyTime',dataset)
    g.referring_physician_name = get_value_kw('ReferringPhysicianName',dataset)
    g.referring_physician_identification = get_value_kw('ReferringPhysicianIdentification',dataset)
    g.study_id = get_value_kw('StudyID',dataset)
    g.accession_number = get_value_kw('AccessionNumber',dataset)
    g.study_description = get_value_kw('StudyDescription',dataset)
    g.modality_type = get_value_kw('Modality',dataset)
    g.physician_of_record = get_value_kw('PhysicianOfRecord',dataset)
    g.name_of_physician_reading_study = get_value_kw('NameOfPhysicianReadingStudy',dataset)
    g.performing_physician_name = get_value_kw('PerformingPhysicianName',dataset)
    g.operator_name = get_value_kw('OperatorName',dataset)
    g.procedure_code_meaning = get_value_kw('ProtocolName',dataset) # Being used to summarise protocol for study
    g.requested_procedure_code_value = get_seq_code_value('RequestedProcedureCodeSequence',dataset)
    g.requested_procedure_code_meaning = get_seq_code_meaning('RequestedProcedureCodeSequence',dataset)
    g.save()

    _generalequipmentmoduleattributes(dataset,g)
    _projectionxrayradiationdose(dataset,g)
    _patientstudymoduleattributes(dataset,g)
    _patientmoduleattributes(dataset,g)


def _test_if_mammo(dataset):
    """ Test if dicom object passed is a mammo file by looking at SOP Class UID"""
    if dataset.SOPClassUID == '1.2.840.10008.5.1.4.1.1.1.2.1' or dataset.SOPClassUID == '1.2.840.10008.5.1.4.1.1.1.2':
        return 1
    elif dataset.SOPClassUID == '1.2.840.10008.5.1.4.1.1.7' and dataset.Modality == 'MG' and 'ORIGINAL' in dataset.ImageType:
        return 1
    return 0


def _mammo2db(dataset):
    import os, sys
    import openrem_settings

    os.environ['DJANGO_SETTINGS_MODULE'] = 'openrem.openremproject.settings'
    from django.db import models

    openrem_settings.add_project_to_path()
    from remapp.models import General_study_module_attributes
    from remapp.tools import check_uid
    from remapp.tools.get_values import get_value_kw
    from remapp.tools.dcmdatetime import make_date_time

    study_uid = get_value_kw('StudyInstanceUID',dataset)
    if not study_uid:
        sys.exit('No UID returned')  
    study_in_db = check_uid.check_uid(study_uid)
    if study_in_db:
        event_uid = get_value_kw('SOPInstanceUID',dataset)
        inst_in_db = check_uid.check_uid(event_uid,'Event')
        if inst_in_db:
            return 0
        # further check required to ensure 'for processing' and 'for presentation' 
        # versions of the same irradiation event don't get imported twice
        same_study_uid = General_study_module_attributes.objects.filter(study_instance_uid__exact = study_uid)
        event_time = get_value_kw('AcquisitionTime',dataset)
        event_date = get_value_kw('AcquisitionDate',dataset)
        event_date_time = make_date_time('{0}{1}'.format(event_date,event_time))
        for events in same_study_uid.get().projection_xray_radiation_dose_set.get().irradiation_event_xray_data_set.all():
            if event_date_time == events.date_time_started:
                return 0
        # study exists, but event doesn't
        _irradiationeventxraydata(dataset,same_study_uid.get().projection_xray_radiation_dose_set.get())
        # update the accumulated tables
        return 0

    # study doesn't exist, start from scratch
    g = General_study_module_attributes.objects.create()
    _generalstudymoduleattributes(dataset,g)
    
    
    


def mam(mg_file):
    """Extract radiation dose structured report related data from mammography images
    
    :param filename: relative or absolute path to mammography DICOM image file.
    :type filename: str.

    Tested with:
        * GE Senographe DS software versions ADS_43.10.1 and ADS_53.10.10 only.
        * Limited testing: GE Senographe Essential
        * Limited testing: Hologic Selenia
        * Limited testing: Siemens Inspiration
    
    """

    import sys
    import dicom

    dataset = dicom.read_file(mg_file)
    ismammo = _test_if_mammo(dataset)
    if not ismammo:
        return '{0} is not a mammography DICOM image'.format(mg_file)

    _mammo2db(dataset)

    return 0

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        sys.exit('Error: Supply exactly one argument - the DICOM mammography image file')

    sys.exit(mam(sys.argv[1]))

