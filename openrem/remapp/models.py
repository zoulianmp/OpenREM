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
..  module:: models.
    :synopsis: Models to create the database tables and relationships.

..  moduleauthor:: Ed McDonagh

"""

# Following two lines added so that sphinx autodocumentation works. 
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'openremproject.settings'
from django.db import models

class Size_upload(models.Model):
    sizefile = models.FileField(upload_to='sizeupload')
    height_field = models.TextField(blank=True, null=True)
    weight_field = models.TextField(blank=True, null=True)
    id_field = models.TextField(blank=True, null=True)
    id_type = models.TextField(blank=True, null=True)
    task_id = models.TextField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    progress = models.TextField(blank=True, null=True)
    num_records = models.IntegerField(blank=True, null=True)
    logfile = models.FileField(upload_to='sizelogs/%Y/%m/%d', null=True)
    import_date = models.DateTimeField(blank=True, null=True)
    processtime = models.FloatField(blank=True,null=True)

class Exports(models.Model):
    """Table to hold the export status and filenames
    """
    task_id = models.TextField()
    filename = models.FileField(upload_to='exports/%Y/%m/%d', null=True)
    status = models.TextField(blank=True, null=True)
    progress = models.TextField(blank=True, null=True)
    modality = models.CharField(max_length=8, blank=True, null=True)
    num_records = models.IntegerField(blank=True, null=True)
    export_type = models.TextField(blank=True, null=True)
    export_date = models.DateTimeField(blank=True, null=True)
    processtime = models.DecimalField(max_digits=30,decimal_places=10,blank=True,null=True)

class Content_item_descriptions(models.Model):
    """Table to hold all the context ID code values and code meanings.
    
    + Should be renamed Context_identifiers. If it does, I think it would only need to be edited in tools.get_values.get_or_set_cid and admin, then a South migration.
    + Could be prefilled from the tables in DICOM 3.16, but is actually populated as the codes occur. This assumes they are used correctly.
    
    """    
    code_value = models.CharField(max_length=16)
    code_meaning = models.TextField(blank=True, null=True)
    cid_table = models.CharField(max_length=16,blank=True)
    def __unicode__(self):
        return self.code_meaning
    class Meta:
        ordering = ['code_value']

class General_study_module_attributes(models.Model): # C.7.2.1
    """General Study Module C.7.2.1
    
    Specifies the Attributes that describe and identify the Study 
    performed upon the Patient.
    
    From DICOM Part 3: Information Object Definitions Table C.7-3

    Additional to the module definition:
        * performing_physician_name
        * operator_name
        * modality_type
        * procedure_code_value_and_meaning
        * requested_procedure_code_value_and_meaning
    """
    study_instance_uid = models.TextField(blank=True, null=True)
    study_date = models.DateField(blank=True, null=True)
    study_time = models.TimeField(blank=True, null=True)
    referring_physician_name = models.TextField(blank=True, null=True)
    referring_physician_identification = models.TextField(blank=True, null=True)
    study_id = models.CharField(max_length=16,blank=True,null=True)
    accession_number = models.CharField(max_length=16,blank=True,null=True)
    study_description = models.TextField(blank=True,null=True)
    physician_of_record = models.TextField(blank=True,null=True)
    name_of_physician_reading_study = models.TextField(blank=True,null=True)
    # Possibly need a few sequences linked to this table...
    # Next three don't belong in this table, but they don't belong anywhere in a RDSR!
    performing_physician_name = models.TextField(blank=True,null=True)
    operator_name = models.TextField(blank=True,null=True)
    modality_type = models.CharField(max_length=8,blank=True,null=True)
    procedure_code_value = models.CharField(max_length=16,blank=True,null=True)
    procedure_code_meaning = models.TextField(blank=True,null=True)
    requested_procedure_code_value = models.CharField(max_length=16,blank=True,null=True)
    requested_procedure_code_meaning = models.TextField(blank=True,null=True)
    def __unicode__(self):
        return self.study_instance_uid

class Projection_xray_radiation_dose(models.Model): # TID 10001
    """Projection X-Ray Radiation Dose template TID 10001
    
    From DICOM Part 16:
        This template defines a container (the root) with subsidiary content items, each of which represents a
        single projection X-Ray irradiation event entry or plane-specific dose accumulations. There is a defined
        recording observer (the system or person responsible for recording the log, generally the system). A
        Biplane irradiation event will be recorded as two individual events, one for each plane. Accumulated
        values will be kept separate for each plane.
    
    """
    general_study_module_attributes = models.ForeignKey(General_study_module_attributes)
    procedure_reported = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='tid10001_procedure')
    has_intent = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='tid10001_intent')
    acquisition_device_type = models.CharField(max_length=16,blank=True)
    scope_of_accumulation = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='tid10001_scope')
    xray_detector_data_available = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='tid10001_detector')
    xray_source_data_available = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='tid10001_source')
    xray_mechanical_data_available = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='tid10001_mech')
    comment = models.TextField(blank=True, null=True)
    source_of_dose_information = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='tid10001_infosource') # might need to be a table on its own as is 1-n, even though it should only list the primary source...

class Accumulated_xray_dose(models.Model): # TID 10002
    """Accumulated X-Ray Dose TID 10002
    
    From DICOM Part 16:
        This general template provides detailed information on projection X-Ray dose value accumulations over
        several irradiation events from the same equipment (typically a study or a performed procedure step).
    
    """
    projection_xray_radiation_dose = models.ForeignKey(Projection_xray_radiation_dose)
    acquisition_plane = models.ForeignKey(Content_item_descriptions,blank=True,null=True)

class Calibration(models.Model):
    """Table to hold the calibration information
    
    + Container in TID 10002 Accumulated X-ray dose
    
    """
    accumulated_xray_dose = models.ForeignKey(Accumulated_xray_dose)
    dose_measurement_device = models.ForeignKey(Content_item_descriptions,blank=True,null=True)
    calibration_date = models.DateTimeField(blank=True, null=True)
    calibration_factor = models.DecimalField(max_digits=8,decimal_places=5,blank=True,null=True)
    calibration_uncertainty = models.DecimalField(max_digits=8,decimal_places=5,blank=True,null=True)
    calibration_responsible_party = models.TextField(blank=True, null=True)

class Irradiation_event_xray_data(models.Model): # TID 10003
    """Irradiation Event X-Ray Data TID 10003
    
    From DICOM part 16:
        This template conveys the dose and equipment parameters of a single irradiation event.
    
    """
    projection_xray_radiation_dose = models.ForeignKey(Projection_xray_radiation_dose)
    acquisition_plane = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='tid10003_plane')
    irradiation_event_uid = models.TextField(blank=True, null=True)
    irradiation_event_label = models.TextField(blank=True, null=True)
    label_type = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='tid10003_labeltype')
    date_time_started = models.DateTimeField(blank=True, null=True)
    irradiation_event_type = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='tid10003_eventtype')
    acquisition_protocol = models.TextField(blank=True, null=True)
    anatomical_structure = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='tid10003_anatomy')
    laterality = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='tid10003_laterality')
    image_view = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='tid10003_view')
    projection_eponymous_name = models.CharField(max_length=16,blank=True)
    patient_table_relationship = models.CharField(max_length=16,blank=True)
    patient_orientation = models.CharField(max_length=16,blank=True)
    patient_orientation_modifier = models.CharField(max_length=16,blank=True)
    target_region = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='tid10003_region')
    dose_area_product = models.DecimalField(max_digits=16,decimal_places=12,blank=True,null=True)
    half_value_layer = models.DecimalField(max_digits=8,decimal_places=5,blank=True,null=True)
    entrance_exposure_at_rp = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    reference_point_definition = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='tid10003_rpdefinition')
    breast_composition = models.CharField(max_length=16,blank=True) # TID 4007, CID 6000
    percent_fibroglandular_tissue = models.DecimalField(max_digits=6,decimal_places=3,blank=True,null=True) # TID 4007
    comment = models.TextField(blank=True, null=True)
    def __unicode__(self):
        return self.irradiation_event_uid
    def convert_gym2_to_cgycm2(self): # not used anywhere?
        return 1000000*self.dose_area_product

    
class Image_view_modifier(models.Model): # EV 111032
    """Table to hold image view modifiers for the irradiation event xray data table
    
    From DICOM Part 16 Annex D DICOM controlled Terminology Definitions
        + Code Value 111032
        + Code Meaning Image View Modifier 
        + Code Definition Modifier for image view
    """
    irradiation_event_xray_data = models.ForeignKey(Irradiation_event_xray_data)
    image_view_modifier = models.ForeignKey(Content_item_descriptions,blank=True,null=True)

class Irradiation_event_xray_detector_data(models.Model): # TID 10003a
    """Irradiation Event X-Ray Detector Data TID 10003a
    
    From DICOM Part 16 Correction Proposal CP-1077:
        This template contains data which is expected to be available to the X-ray detector or plate reader component of the equipment.
    """
    irradiation_event_xray_data = models.ForeignKey(Irradiation_event_xray_data)
    exposure_index = models.DecimalField(max_digits=7,decimal_places=2,blank=True,null=True)
    target_exposure_index = models.DecimalField(max_digits=7,decimal_places=2,blank=True,null=True)
    deviation_index = models.DecimalField(max_digits=7,decimal_places=2,blank=True,null=True)

class Irradiation_event_xray_source_data(models.Model): # TID 10003b
    """Irradiation Event X-Ray Source Data TID 10003b
    
    From DICOM Part 16 Correction Proposal CP-1077:
        This template contains data which is expected to be available to the X-ray source component of the equipment.
    
    Additional to the template:
        * ii_field_size
        * exposure_control_mode
    """
    irradiation_event_xray_data = models.ForeignKey(Irradiation_event_xray_data)
    dose_rp = models.DecimalField(max_digits=16,decimal_places=12,blank=True,null=True)
    reference_point_definition = models.TextField(blank=True, null=True)
    reference_point_definition_code = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='tid10003b_rpdefinition')
    average_glandular_dose = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    fluoro_mode = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='tid10003b_fluoromode')
    pulse_rate = models.DecimalField(max_digits=6,decimal_places=3,blank=True,null=True)
    number_of_pulses = models.DecimalField(max_digits=6,decimal_places=0,blank=True,null=True)
    derivation = models.CharField(max_length=16,blank=True)
    irradiation_duration = models.DecimalField(max_digits=7,decimal_places=2,blank=True,null=True)
    average_xray_tube_current = models.DecimalField(max_digits=6,decimal_places=2,blank=True,null=True)
    exposure_time = models.DecimalField(max_digits=16,decimal_places=2,blank=True,null=True)
    focal_spot_size = models.DecimalField(max_digits=4,decimal_places=2,blank=True,null=True)
    anode_target_material = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='tid10003b_anodetarget')
    collimated_field_area = models.DecimalField(max_digits=8,decimal_places=6,blank=True,null=True)
    # not in DICOM standard - 'image intensifier' field size and exposure control mode
    ii_field_size = models.IntegerField(blank=True,null=True)
    exposure_control_mode = models.CharField(max_length=16,blank=True,null=True)

class Xray_grid(models.Model):
    """Content ID 10017 X-Ray Grid
    
    From DICOM Part 16
    """
    irradiation_event_xray_source_data = models.ForeignKey(Irradiation_event_xray_source_data)
    xray_grid = models.ForeignKey(Content_item_descriptions,blank=True,null=True)

class Pulse_width(models.Model): # EV 113793
    """In TID 10003b. Code value 113793 (ms)
    """
    irradiation_event_xray_source_data = models.ForeignKey(Irradiation_event_xray_source_data)
    pulse_width = models.DecimalField(max_digits=7,decimal_places=3,blank=True,null=True)

class Kvp(models.Model): # EV 113733
    """In TID 10003b. Code value 113733 (kV)
    """
    irradiation_event_xray_source_data = models.ForeignKey(Irradiation_event_xray_source_data)
    kvp = models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True)

class Xray_tube_current(models.Model): # EV 113734
    """In TID 10003b. Code value 113734 (mA)
    """
    irradiation_event_xray_source_data = models.ForeignKey(Irradiation_event_xray_source_data)
    xray_tube_current = models.DecimalField(max_digits=6,decimal_places=2,blank=True,null=True)

class Exposure(models.Model): # EV 113736
    """In TID 10003b. Code value 113736 (uAs)
    """
    irradiation_event_xray_source_data = models.ForeignKey(Irradiation_event_xray_source_data)
    exposure = models.DecimalField(max_digits=16,decimal_places=2,blank=True,null=True)

class Xray_filters(models.Model): # EV 113771
    """Container in TID 10003b. Code value 113771
    """
    irradiation_event_xray_source_data = models.ForeignKey(Irradiation_event_xray_source_data)
    xray_filter_type = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='xrayfilters_type')
    xray_filter_material = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='xrayfilters_material')
    xray_filter_thickness_minimum = models.DecimalField(max_digits=4,decimal_places=2,blank=True,null=True)
    xray_filter_thickness_maximum = models.DecimalField(max_digits=4,decimal_places=2,blank=True,null=True)
        
class Irradiation_event_xray_mechanical_data(models.Model): # TID 10003c
    """Irradiation Event X-Ray Mechanical Data TID 10003c

    From DICOM Part 16 Correction Proposal CP-1077:
        This template contains data which is expected to be available to the gantry or mechanical component of the equipment.
    
    Additional to the template:
        * compression_force
        * magnification_factor
    """
    irradiation_event_xray_data = models.ForeignKey(Irradiation_event_xray_data)
    crdr_mechanical_configuration = models.ForeignKey(Content_item_descriptions,blank=True,null=True)
    positioner_primary_angle = models.DecimalField(max_digits=4,decimal_places=2,blank=True,null=True)
    positioner_secondary_angle = models.DecimalField(max_digits=4,decimal_places=2,blank=True,null=True)
    positioner_primary_end_angle = models.DecimalField(max_digits=4,decimal_places=2,blank=True,null=True)
    positioner_secondary_end_angle = models.DecimalField(max_digits=4,decimal_places=2,blank=True,null=True)
    column_angulation = models.DecimalField(max_digits=4,decimal_places=2,blank=True,null=True)
    table_head_tilt_angle = models.DecimalField(max_digits=4,decimal_places=2,blank=True,null=True)
    table_horizontal_rotation_angle = models.DecimalField(max_digits=4,decimal_places=2,blank=True,null=True)
    table_cradle_tilt_angle = models.DecimalField(max_digits=4,decimal_places=2,blank=True,null=True)
    compression_thickness = models.DecimalField(max_digits=6,decimal_places=2,blank=True,null=True)
    # not in DICOM standard - compression force in N
    compression_force = models.DecimalField(max_digits=6,decimal_places=3,blank=True,null=True)
    magnification_factor = models.DecimalField(max_digits=4,decimal_places=2,blank=True,null=True)
    
class Dose_related_distance_measurements(models.Model): # CID 10008
    """Dose Related Distance Measurements Context ID 10008
    
    Called from TID 10003c
    """
    irradiation_event_xray_mechanical_data = models.ForeignKey(Irradiation_event_xray_mechanical_data)
    distance_source_to_isocenter = models.DecimalField(max_digits=6,decimal_places=2,blank=True,null=True)
    distance_source_to_reference_point = models.DecimalField(max_digits=6,decimal_places=2,blank=True,null=True)
    distance_source_to_detector = models.DecimalField(max_digits=6,decimal_places=2,blank=True,null=True)
    table_longitudinal_position = models.DecimalField(max_digits=6,decimal_places=2,blank=True,null=True)
    table_lateral_position = models.DecimalField(max_digits=6,decimal_places=2,blank=True,null=True)
    table_height_position = models.DecimalField(max_digits=6,decimal_places=2,blank=True,null=True)
    distance_source_to_table_plane = models.DecimalField(max_digits=6,decimal_places=2,blank=True,null=True)
    # not in DICOM standard - distance source to entrance surface distance in mm
    distance_source_to_entrance_surface = models.DecimalField(max_digits=6,decimal_places=2,blank=True,null=True)
    radiological_thickness = models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True)
    
class Accumulated_projection_xray_dose(models.Model): # TID 10004
    """Accumulated Projection X-Ray Dose TID 10004
    
    From DICOM Part 16:
        This general template provides detailed information on projection X-Ray dose value accumulations over
        several irradiation events from the same equipment (typically a study or a performed procedure step).
    
    """
    accumulated_xray_dose = models.ForeignKey(Accumulated_xray_dose)
    dose_area_product_total = models.DecimalField(max_digits=16,decimal_places=12,blank=True,null=True)
    dose_rp_total = models.DecimalField(max_digits=16,decimal_places=12,blank=True,null=True)
    fluoro_dose_area_product_total = models.DecimalField(max_digits=16,decimal_places=12,blank=True,null=True)
    fluoro_dose_rp_total = models.DecimalField(max_digits=16,decimal_places=12,blank=True,null=True)
    total_fluoro_time  = models.DecimalField(max_digits=7,decimal_places=2,blank=True,null=True)
    acquisition_dose_area_product_total = models.DecimalField(max_digits=16,decimal_places=12,blank=True,null=True)
    acquisition_dose_rp_total = models.DecimalField(max_digits=16,decimal_places=12,blank=True,null=True)
    total_acquisition_time  = models.DecimalField(max_digits=7,decimal_places=2,blank=True,null=True)
    total_number_of_radiographic_frames  = models.DecimalField(max_digits=6,decimal_places=0,blank=True,null=True)
    reference_point_definition = models.TextField(blank=True, null=True)
    reference_point_definition_code = models.ForeignKey(Content_item_descriptions,blank=True,null=True)
#    dap_total_cgycm2 = models.DecimalField(max_digits=16,decimal_places=10,blank=True,null=True)
    
    def convert_gym2_to_cgycm2(self):
        """Converts Gy.m2 to cGy.cm2 for display in web interface    
        """
        return 1000000*self.dose_area_product_total
    
#    def _convert_to_cgycm2(self,dap):
#        dap = dap*1000000 # Gym2 to uGym2 = cGycm2
#        return dap

class Accumulated_mammography_xray_dose(models.Model): # TID 10005
    """Accumulated Mammography X-Ray Dose TID 10005
    
    From DICOM Part 16:
        This modality specific template provides detailed information on mammography X-Ray dose value
        accumulations over several irradiation events from the same equipment (typically a study or a performed
        procedure step).
    """
    accumulated_xray_dose = models.ForeignKey(Accumulated_xray_dose)
    accumulated_average_glandular_dose = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    laterality = models.ForeignKey(Content_item_descriptions,blank=True,null=True)

class Accumulated_cassette_based_projection_radiography_dose(models.Model): # TID 10006
    """Accumulated Cassette-based Projection Radiography Dose TID 10006
    
    From DICOM Part 16 Correction Proposal CP-1077:
        This template provides information on Projection Radiography dose values accumulated on Cassette-
        based systems over one or more irradiation events (typically a study or a performed procedure step) from
        the same equipment.
    """
    accumulated_xray_dose = models.ForeignKey(Accumulated_xray_dose)
    detector_type = models.ForeignKey(Content_item_descriptions,blank=True,null=True)
    total_number_of_radiographic_frames  = models.DecimalField(max_digits=6,decimal_places=0,blank=True,null=True)
    
class Accumulated_integrated_projection_radiography_dose(models.Model): # TID 10007
    """Accumulated Integrated Projection Radiography Dose TID 10007
    
    From DICOM Part 16 Correction Proposal CP-1077:
        This template provides information on Projection Radiography dose values accumulated on Integrated
        systems over one or more irradiation events (typically a study or a performed procedure step) from the
        same equipment.
    """
    accumulated_xray_dose = models.ForeignKey(Accumulated_xray_dose)
    dose_area_product_total = models.DecimalField(max_digits=16,decimal_places=12,blank=True,null=True)
    dose_rp_total = models.DecimalField(max_digits=16,decimal_places=12,blank=True,null=True)
    total_number_of_radiographic_frames  = models.DecimalField(max_digits=6,decimal_places=0,blank=True,null=True)
    reference_point_definition_code = models.ForeignKey(Content_item_descriptions,blank=True,null=True)
    reference_point_definition = models.TextField(blank=True, null=True)
    
class Patient_module_attributes(models.Model): # C.7.1.1
    """Patient Module C.7.1.1
    
    From DICOM Part 3: Information Object Definitions Table C.7-1:
        Specifies the Attributes of the Patient that describe and identify the Patient who is
        the subject of a diagnostic Study. This Module contains Attributes of the patient that are needed
        for diagnostic interpretation of the Image and are common for all studies performed on the
        patient. It contains Attributes that are also included in the Patient Modules in Section C.2.
    """
    general_study_module_attributes = models.ForeignKey(General_study_module_attributes)
    patient_name = models.TextField(blank=True,null=True)
    patient_id = models.TextField(blank=True,null=True)
    patient_birth_date = models.DateField(blank=True, null=True)
    patient_sex = models.CharField(max_length=2,blank=True,null=True)
    other_patient_ids = models.TextField(blank=True,null=True)
    not_patient_indicator = models.TextField(blank=True,null=True)

class Patient_study_module_attributes(models.Model): # C.7.2.2
    """Patient Study Module C.7.2.2
    
    From DICOM Part 3: Information Object Definitions Table C.7-4a:
        Defines Attributes that provide information about the Patient at the time the Study
        started.        
    """
    general_study_module_attributes = models.ForeignKey(General_study_module_attributes)
    admitting_diagnosis_description = models.TextField(blank=True,null=True)
    admitting_diagnosis_code_sequence = models.TextField(blank=True,null=True)
    patient_age = models.CharField(max_length=4,blank=True,null=True)
    patient_age_decimal = models.DecimalField(max_digits=7,decimal_places=3,blank=True,null=True)
    patient_size = models.DecimalField(max_digits=16,decimal_places=8,blank=True,null=True)
    patient_weight = models.DecimalField(max_digits=16,decimal_places=8,blank=True,null=True)
    # TODO: Add patient size code sequence
    
class General_equipment_module_attributes(models.Model): # C.7.5.1
    """General Equipment Module C.7.5.1
    
    From DICOM Part 3: Information Object Definitions Table C.7-8:
        Specifies the Attributes that identify and describe the piece of equipment that
        produced a Series of Composite Instances.
    """
    general_study_module_attributes = models.ForeignKey(General_study_module_attributes)
    manufacturer = models.TextField(blank=True,null=True)
    institution_name = models.TextField(blank=True,null=True)
    institution_address = models.TextField(blank=True,null=True)
    station_name = models.CharField(max_length=32,blank=True,null=True)
    institutional_department_name = models.TextField(blank=True,null=True)
    manufacturer_model_name = models.TextField(blank=True,null=True)
    device_serial_number = models.TextField(blank=True,null=True)
    software_versions = models.TextField(blank=True,null=True)
    gantry_id = models.TextField(blank=True,null=True)
    spatial_resolution = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    date_of_last_calibration = models.DateTimeField(blank=True, null=True)
    time_of_last_calibration = models.DateTimeField(blank=True, null=True)
    def __unicode__(self):
        return self.station_name


############# CT

class Ct_radiation_dose(models.Model): # TID 10011
    """CT Radiation Dose TID 10011
    
    From DICOM Part 16:
        This template defines a container (the root) with subsidiary content items, each of which corresponds to a
        single CT X-Ray irradiation event entry. There is a defined recording observer (the system or person
        responsible for recording the log, generally the system). Accumulated values shall be kept for a whole
        Study or at least a part of a Study, if the Study is divided in the workflow of the examination, or a
        performed procedure step. Multiple CT Radiation Dose objects may be created for one Study.
    """
    general_study_module_attributes = models.ForeignKey(General_study_module_attributes)
    procedure_reported = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='tid10011_procedure')
    has_intent = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='tid10011_intent')
    start_of_xray_irradiation = models.DateTimeField(blank=True, null=True)
    end_of_xray_irradiation = models.DateTimeField(blank=True, null=True)
    scope_of_accumulation = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='tid10011_scope')
    comment = models.TextField(blank=True, null=True)
    source_of_dose_information = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='tid10011_source') # might need to be a table on its own as is 1-n

class Ct_accumulated_dose_data(models.Model): # TID 10012
    """CT Accumulated Dose Data
    
    From DICOM Part 16:
        This general template provides detailed information on CT X-Ray dose value accumulations over several
        irradiation events from the same equipment and over the scope of accumulation specified for the report
        (typically a Study or a Performed Procedure Step).
    """
    ct_radiation_dose = models.ForeignKey(Ct_radiation_dose)
    total_number_of_irradiation_events = models.DecimalField(max_digits=6,decimal_places=0,blank=True,null=True)
    ct_dose_length_product_total = models.DecimalField(max_digits=16,decimal_places=8,blank=True,null=True)
    ct_effective_dose_total = models.DecimalField(max_digits=16,decimal_places=8,blank=True,null=True)
    reference_authority_code = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='tid10012_authority')
    reference_authority_text = models.CharField(max_length=256,blank=True)
    measurement_method = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='tid10012_method')
    patient_model = models.CharField(max_length=256,blank=True)
    effective_dose_phantom_type = models.CharField(max_length=256,blank=True)
    dosimeter_type = models.CharField(max_length=256,blank=True)
    comment = models.TextField(blank=True, null=True)


class Ct_irradiation_event_data(models.Model): # TID 10013
    """CT Irradiation Event Data TID 10013
    
    From DICOM Part 16:
        This template conveys the dose and equipment parameters of a single irradiation event.
    
    Additional to the template:
        + date_time_started
        + series_description
    """
    ct_radiation_dose = models.ForeignKey(Ct_radiation_dose)
    acquisition_protocol = models.TextField(blank=True,null=True)
    target_region = models.ForeignKey(Content_item_descriptions,blank=True,null=True,related_name='tid10013_region')
    ct_acquisition_type = models.ForeignKey(Content_item_descriptions,blank=True,null=True,related_name='tid10013_type')
    procedure_context = models.ForeignKey(Content_item_descriptions,blank=True,null=True,related_name='tid10013_context')
    irradiation_event_uid = models.TextField(blank=True, null=True)
    exposure_time = models.DecimalField(max_digits=16,decimal_places=4,blank=True,null=True)
    nominal_single_collimation_width = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    nominal_total_collimation_width = models.DecimalField(max_digits=10,decimal_places=4,blank=True,null=True)
    pitch_factor = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    number_of_xray_sources = models.DecimalField(max_digits=2,decimal_places=0,blank=True,null=True)
    mean_ctdivol = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    ctdiw_phantom_type = models.ForeignKey(Content_item_descriptions,blank=True,null=True,related_name='tid10013_phantom')
    ctdifreeair_calculation_factor = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    mean_ctdifreeair = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    dlp = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    effective_dose = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    measurement_method = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='tid10013_method')
    effective_dose_conversion_factor = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    xray_modulation_type = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    # Not in DICOM standard:
    date_time_started = models.DateTimeField(blank=True, null=True)
    series_description = models.TextField(blank=True, null=True)


class Ct_xray_source_parameters(models.Model):
    """Container in TID 10013 to hold CT x-ray source parameters
    """
    ct_irradiation_event_data = models.ForeignKey(Ct_irradiation_event_data)
    identification_of_the_xray_source = models.TextField(blank=True, null=True)
    kvp = models.DecimalField(max_digits=6,decimal_places=2,blank=True,null=True)
    maximum_xray_tube_current = models.DecimalField(max_digits=6,decimal_places=2,blank=True,null=True)
    xray_tube_current = models.DecimalField(max_digits=6,decimal_places=2,blank=True,null=True)
    exposure_time_per_rotation = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    xray_filter_aluminum_equivalent = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)

class Scanning_length(models.Model): # TID 10014
    """Scanning Length TID 10014
    
    From DICOM Part 16:
        No description
    """
    ct_irradiation_event_data = models.ForeignKey(Ct_irradiation_event_data)
    scanning_length = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    length_of_reconstructable_volume = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    exposed_range = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    top_z_location_of_reconstructable_volume = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    bottom_z_location_of_reconstructable_volume = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    top_z_location_of_scanning_length = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    bottom_z_location_of_scanning_length = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    frame_of_reference_uid = models.TextField(blank=True, null=True)

class Ct_dose_check_details(models.Model): # TID 10015
    """CT Dose Check Details TID 10015
    
    From DICOM Part 16:
        This template records details related to the use of the NEMA Dose Check Standard (NEMA XR-25-2010).
    """
    ct_irradiation_event_data = models.ForeignKey(Ct_irradiation_event_data)
    dlp_alert_value_configured = models.NullBooleanField()
    ctdivol_alert_value_configured = models.NullBooleanField()
    dlp_alert_value = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    ctdivol_alert_value = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    accumulated_dlp_forward_estimate = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    accumulated_ctdivol_forward_estimate = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    alert_reason_for_proceeding = models.CharField(max_length=512,blank=True) # alert_ added to allow two fields that are in different containers in std
    dlp_notification_value_configured = models.NullBooleanField()
    ctdivol_notification_value_configured = models.NullBooleanField()
    dlp_notification_value = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    ctdivol_notification_value = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    dlp_forward_estimate = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    ctdivol_forward_estimate = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    notification_reason_for_proceeding = models.CharField(max_length=512,blank=True) # notification_ added to allow two fields that are in different containers in std


# Models common to both
    
class Observer_context(models.Model): # TID 1002
    """Observer Context TID 1002
    
    From DICOM Part 16:
        The observer (person or device) that created the Content Items to which this context applies.
    """
    projection_xray_radiation_dose = models.ForeignKey(Projection_xray_radiation_dose,blank=True,null=True)
    ct_radiation_dose = models.ForeignKey(Ct_radiation_dose,blank=True,null=True)
    observer_type = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='tid1002_observertype')
    device_observer_uid = models.TextField(blank=True, null=True)
    device_observer_name = models.TextField(blank=True, null=True)
    device_observer_manufacturer = models.TextField(blank=True, null=True)
    device_observer_model_name = models.TextField(blank=True, null=True)
    device_observer_serial_number = models.TextField(blank=True, null=True)
    device_observer_physical_location_during_observation = models.TextField(blank=True, null=True)
    device_role_in_procedure = models.ForeignKey(Content_item_descriptions,blank=True,null=True, related_name='tid1002_role')
    def __unicode__(self):
        return self.device_observer_name

class Device_participant(models.Model): # TID 1021
    """Device Participant TID 1021
    
    From DICOM Part 16:
        This template describes a device participating in an activity as other than an observer or subject. E.g. for
        a dose report documenting an irradiating procedure, participants include the irradiating device.
    """
    accumulated_xray_dose = models.ForeignKey(Accumulated_xray_dose,blank=True,null=True)
    irradiation_event_xray_detector_data = models.ForeignKey(Irradiation_event_xray_detector_data,blank=True,null=True)
    irradiation_event_xray_source_data = models.ForeignKey(Irradiation_event_xray_source_data,blank=True,null=True)
    ct_accumulated_dose_data = models.ForeignKey(Ct_accumulated_dose_data,blank=True,null=True)
    ct_irradiation_event_data = models.ForeignKey(Ct_irradiation_event_data,blank=True,null=True)
    device_role_in_procedure = models.ForeignKey(Content_item_descriptions,blank=True,null=True)
    device_name = models.TextField(blank=True, null=True)
    device_manufacturer = models.TextField(blank=True, null=True)
    device_model_name = models.TextField(blank=True, null=True)
    device_serial_number = models.TextField(blank=True, null=True)
    device_observer_uid = models.TextField(blank=True, null=True)

class Person_participant(models.Model): # TID 1020
    """Person Participant TID 1020
    
    From DICOM Part 16:
        This template describes a person participating in an activity as other than an observer or subject. E.g. for
        a dose report documenting an irradiating procedure, participants include the person administering the
        irradiation and the person authorizing the irradiation.
    """
    projection_xray_radiation_dose = models.ForeignKey(Projection_xray_radiation_dose,blank=True,null=True)
    ct_radiation_dose = models.ForeignKey(Ct_radiation_dose,blank=True,null=True)
    irradiation_event_xray_data = models.ForeignKey(Irradiation_event_xray_data,blank=True,null=True)
    ct_accumulated_dose_data = models.ForeignKey(Ct_accumulated_dose_data,blank=True,null=True)
    ct_irradiation_event_data = models.ForeignKey(Ct_irradiation_event_data,blank=True,null=True)
    ct_dose_check_details_alert = models.ForeignKey(Ct_dose_check_details,blank=True,null=True, related_name='tid1020_alert')
    ct_dose_check_details_notification = models.ForeignKey(Ct_dose_check_details,blank=True,null=True, related_name='tid1020_notification')
    person_name = models.TextField(blank=True, null=True)
    person_role_in_procedure = models.CharField(max_length=16,blank=True)
    person_id = models.TextField(blank=True, null=True)
    person_id_issuer = models.TextField(blank=True, null=True)
    organization_name = models.TextField(blank=True, null=True)
    person_role_in_organization = models.TextField(blank=True, null=True)
    def __unicode__(self):
        return self.person_name

