
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
..  module:: rdsr.
    :synopsis: Module to extract radiation dose related data from DICOM Radiation SR objects.

..  moduleauthor:: Ed McDonagh

"""

def _observercontext(dataset,obs): # TID 1002
    from remapp.tools.get_values import get_or_create_cid
    for cont in dataset.ContentSequence:
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Observer Type':
            obs.observer_type = get_or_create_cid(cont.ConceptCodeSequence[0].CodeValue, cont.ConceptCodeSequence[0].CodeMeaning)
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Device Observer UID':
            obs.device_observer_uid = cont.UID
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Device Observer Name':
            obs.device_observer_name = cont.TextValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Device Observer Manufacturer':
            obs.device_observer_manufacturer = cont.TextValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Device Observer Model Name':
            obs.device_observer_model_name = cont.TextValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Device Observer Serial Number':
            obs.device_observer_serial_number = cont.TextValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Device Observer Physical Location during observation':
            obs.device_observer_physical_location_during_observation = cont.TextValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Device Role in Procedure':
            obs.device_role_in_procedure = get_or_create_cid(cont.ConceptCodeSequence[0].CodeValue, cont.ConceptCodeSequence[0].CodeMeaning)
    obs.save()
    
def _deviceparticipant(dataset,eventdatatype,foreignkey):
    from remapp.models import Device_participant
    from remapp.tools.get_values import get_or_create_cid
    if eventdatatype == 'detector':
        device = Device_participant.objects.create(irradiation_event_xray_detector_data=foreignkey)
    elif eventdatatype == 'source':
        device = Device_participant.objects.create(irradiation_event_xray_source_data=foreignkey)
    elif eventdatatype == 'accumulated':
        device = Device_participant.objects.create(accumulated_xray_dose=foreignkey)
    elif eventdatatype == 'ct_accumulated':
        device = Device_participant.objects.create(ct_accumulated_dose_data=foreignkey)
    elif eventdatatype == 'ct_event':
        device = Device_participant.objects.create(ct_irradiation_event_data=foreignkey)
    else:
        print "Doh"
    for cont in dataset.ContentSequence:
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Device Role in Procedure':
            device.device_role_in_procedure = get_or_create_cid(cont.ConceptCodeSequence[0].CodeValue, cont.ConceptCodeSequence[0].CodeMeaning)
            for cont2 in cont.ContentSequence:
                if cont2.ConceptNameCodeSequence[0].CodeMeaning == 'Device Name':
                    device.device_name = cont2.TextValue
                if cont2.ConceptNameCodeSequence[0].CodeMeaning == 'Device Manufacturer':
                    device.device_manufacturer = cont2.TextValue
                if cont2.ConceptNameCodeSequence[0].CodeMeaning == 'Device Model Name':
                    device.device_model_name = cont2.TextValue
                if cont2.ConceptNameCodeSequence[0].CodeMeaning == 'Device Serial Number':
                    device.device_serial_number = cont2.TextValue
                if cont2.ConceptNameCodeSequence[0].CodeMeaning == 'Device Observer UID':
                    device.device_observer_uid = cont2.UID
    device.save()

def _pulsewidth(dataset,source):
    from remapp.models import Pulse_width
    pulse = Pulse_width.objects.create(irradiation_event_xray_source_data=source)
    for cont in dataset.ContentSequence:
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Pulse Width':
            pulse.pulse_width = cont.MeasuredValueSequence[0].NumericValue
    pulse.save()

def _kvptable(dataset,source):
    from remapp.models import Kvp
    kvpdata = Kvp.objects.create(irradiation_event_xray_source_data=source)
    for cont in dataset.ContentSequence:
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'KVP':
            kvpdata.kvp = cont.MeasuredValueSequence[0].NumericValue
    kvpdata.save()

def _xraytubecurrent(dataset,source):
    from remapp.models import Xray_tube_current
    tubecurrent = Xray_tube_current.objects.create(irradiation_event_xray_source_data=source)
    for cont in dataset.ContentSequence:
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'X-Ray Tube Current':
            tubecurrent.xray_tube_current = cont.MeasuredValueSequence[0].NumericValue
    tubecurrent.save()

def _exposure(dataset,source):
    from remapp.models import Exposure
    exposure = Exposure.objects.create(irradiation_event_xray_source_data=source)
    for cont in dataset.ContentSequence:
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Exposure':
            exposure.exposure = cont.MeasuredValueSequence[0].NumericValue
    exposure.save()

def _xrayfilters(dataset,source):
    from remapp.models import Xray_filters
    from remapp.tools.get_values import get_or_create_cid
    filters = Xray_filters.objects.create(irradiation_event_xray_source_data=source)
    for cont in dataset.ContentSequence:
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'X-Ray Filters':
            for cont2 in cont.ContentSequence:
                if cont2.ConceptNameCodeSequence[0].CodeMeaning == 'X-Ray Filter Type':
                    filters.xray_filter_type = get_or_create_cid(cont2.ConceptCodeSequence[0].CodeValue, cont2.ConceptCodeSequence[0].CodeMeaning)
                if cont2.ConceptNameCodeSequence[0].CodeMeaning == 'X-Ray Filter Material':
                    filters.xray_filter_material = get_or_create_cid(cont2.ConceptCodeSequence[0].CodeValue, cont2.ConceptCodeSequence[0].CodeMeaning)
                if cont2.ConceptNameCodeSequence[0].CodeMeaning == 'X-Ray Filter Thickness Minimum':
                    filters.xray_filter_thickness_minimum = cont2.MeasuredValueSequence[0].NumericValue
                if cont2.ConceptNameCodeSequence[0].CodeMeaning == 'X-Ray Filter Thickness Maximum':
                    filters.xray_filter_thickness_maximum = cont2.MeasuredValueSequence[0].NumericValue
    filters.save()


def _doserelateddistancemeasurements(dataset,mech): #CID 10008
    from remapp.models import Dose_related_distance_measurements
    distance = Dose_related_distance_measurements.objects.create(irradiation_event_xray_mechanical_data=mech)
    codes = {   'Distance Source to Isocenter'      :'distance_source_to_isocenter',
                'Distance Source to Reference Point':'distance_source_to_reference_point',
                'Distance Source to Detector'       :'distance_source_to_detector',
                'Table Longitudinal Position'       :'table_longitudinal_position',
                'Table Lateral Position'            :'table_lateral_position',
                'Table Height Position'             :'table_height_position',
                'Distance Source to Table Plane'    :'distance_source_to_table_plane'}
    for cont in dataset.ContentSequence:
        try:
            setattr(distance,codes[cont.ConceptNameCodeSequence[0].CodeMeaning],cont.MeasuredValueSequence[0].NumericValue)
        except KeyError:
            pass
    distance.save()

def _irradiationeventxraymechanicaldata(dataset,event): #TID 10003c
    from remapp.models import Irradiation_event_xray_mechanical_data
    from remapp.tools.get_values import get_or_create_cid
    mech = Irradiation_event_xray_mechanical_data.objects.create(irradiation_event_xray_data=event)
    for cont in dataset.ContentSequence:
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'CR/DR Mechanical Configuration':
            mech.crdr_mechanical_configuration = get_or_create_cid(cont.ConceptCodeSequence[0].CodeValue, cont.ConceptCodeSequence[0].CodeMeaning)
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Positioner Primary Angle':
            mech.positioner_primary_angle = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Positioner Secondary Angle':
            mech.positioner_secondary_angle = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Positioner Primary End Angle':
            mech.positioner_primary_end_angle = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Positioner Secondary End Angle':
            mech.positioner_secondary_end_angle = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Column Angulation':
            mech.column_angulation = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Table Head Tilt Angle':
            mech.table_head_tilt_angle = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Table Horizontal Rotation Angle':
            mech.table_horizontal_rotation_angle = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Table Cradle Tilt Angle':
            mech.table_cradle_tilt_angle = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Compression Thickness':
            mech.compression_thickness = cont.MeasuredValueSequence[0].NumericValue
    _doserelateddistancemeasurements(dataset,mech)
    mech.save()

def _irradiationeventxraysourcedata(dataset,event): #TID 10003b
    from remapp.models import Irradiation_event_xray_source_data
    from remapp.tools.get_values import get_or_create_cid
    from xml.etree import ElementTree as ET
    source = Irradiation_event_xray_source_data.objects.create(irradiation_event_xray_data=event)
    for cont in dataset.ContentSequence:
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Dose (RP)':
            source.dose_rp = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Reference Point Definition':
            # this will fail if the text value is present instead of the code
            source.reference_point_definition_code = get_or_create_cid(cont.ConceptCodeSequence[0].CodeValue, cont.ConceptCodeSequence[0].CodeMeaning)
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Average Glandular Dose':
            source.average_glandular_dose = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Fluoro Mode':
            source.fluoro_mode = get_or_create_cid(cont.ConceptCodeSequence[0].CodeValue, cont.ConceptCodeSequence[0].CodeMeaning)
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Pulse Rate':
            source.pulse_rate = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Number of Pulses':
            source.number_of_pulses = cont.MeasuredValueSequence[0].NumericValue
            # should be a derivation thing in here for when the no. pulses is estimated
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Irradiation Duration':
            source.irradiation_duration = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Average X-Ray Tube Current':
            source.average_xray_tube_current = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Exposure Time':
            source.exposure_time = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Focal Spot Size':
            source.focal_spot_size = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Anode Target Material':
            source.anode_target_material = get_or_create_cid(cont.ConceptCodeSequence[0].CodeValue, cont.ConceptCodeSequence[0].CodeMeaning)
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Collimated Field Area':
            source.collimated_field_area = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'X-Ray Grid':
            source.xray_grid = get_or_create_cid(cont.ConceptCodeSequence[0].CodeValue, cont.ConceptCodeSequence[0].CodeMeaning)
    _pulsewidth(dataset,source)
    _kvptable(dataset,source)
    _xraytubecurrent(dataset,source)
    _exposure(dataset,source)
    _xrayfilters(dataset,source)
    _deviceparticipant(dataset,'source',source)
    try:
        source.ii_field_size = ET.fromstring(source.irradiation_event_xray_data.comment).find('iiDiameter').get('SRData')
    except:
        pass
    source.save()

def _irradiationeventxraydetectordata(dataset,event): #TID 10003a
    from remapp.models import Irradiation_event_xray_detector_data
    detector = Irradiation_event_xray_detector_data.objects.create(irradiation_event_xray_data=event)
    for cont in dataset.ContentSequence:
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Exposure Index':
            detector.exposure_index = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Target Exposure Index':
            detector.target_exposure_index = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Deviation Index':
            detector.deviation_index = cont.MeasuredValueSequence[0].NumericValue
    _deviceparticipant(dataset,'detector',detector)
    detector.save()
        
def _imageviewmodifier(dataset,event):
    from remapp.models import Image_view_modifier
    from remapp.tools.get_values import get_or_create_cid
    modifier = Image_view_modifier.objects.create(irradiation_event_xray_data=event)
    for cont in dataset.ContentSequence:
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Image View Modifier':
            modifier.image_view_modifier = get_or_create_cid(cont.ConceptCodeSequence[0].CodeValue, cont.ConceptCodeSequence[0].CodeMeaning)
    modifier.save()


def _irradiationeventxraydata(dataset,proj): # TID 10003
    from remapp.models import Irradiation_event_xray_data
    from remapp.tools.get_values import get_or_create_cid
    from remapp.tools.dcmdatetime import make_date_time
    event = Irradiation_event_xray_data.objects.create(projection_xray_radiation_dose=proj)
    for cont in dataset.ContentSequence:
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Acquisition Plane':
            event.acquisition_plane = get_or_create_cid(cont.ConceptCodeSequence[0].CodeValue, cont.ConceptCodeSequence[0].CodeMeaning)
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Irradiation Event UID':
            event.irradiation_event_uid = cont.UID
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Irradiation Event Label':
            event.irradiation_event_label = cont.TextValue
            for cont2 in cont.ContentSequence:
                if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Label Type':
                    event.label_type = get_or_create_cid(cont2.ConceptCodeSequence[0].CodeValue, cont2.ConceptCodeSequence[0].CodeMeaning)
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'DateTime Started':
            event.date_time_started = make_date_time(cont.DateTime)
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Irradiation Event Type':
            event.irradiation_event_type = get_or_create_cid(cont.ConceptCodeSequence[0].CodeValue, cont.ConceptCodeSequence[0].CodeMeaning)
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Acquisition Protocol':
            event.acquisition_protocol = cont.TextValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Anatomical structure':
            event.anatomical_structure = cont.CodeValue
            for cont2 in cont.ContentSequence:
                if cont2.ConceptNameCodeSequence[0].CodeMeaning == 'Laterality':
                    event.laterality = cont2.ConceptCodeSequence[0].CodeValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Image View':
            event.image_view = cont.CodeValue
            _imageviewmodifier(cont,event)
            # need something here for the projection eponymous name
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Patient Table Relationship':
            event.patient_table_relationship = cont.CodeValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Patient Orientation':
            event.patient_orientation = cont.CodeValue
            for cont2 in cont.ContentSequence:
                if cont2.ConceptNameCodeSequence[0].CodeMeaning == 'Patient Orientation Modifier':
                    event.patient_orientation_modifier = cont2.ConceptCodeSequence[0].CodeValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Target Region':
            event.target_region = get_or_create_cid(cont.ConceptCodeSequence[0].CodeValue, cont.ConceptCodeSequence[0].CodeMeaning)
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Dose Area Product':
            event.dose_area_product = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Half Value Layer':
            event.half_value_layer = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Entrance Exposure at RP':
            event.entrance_exposure_at_rp = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Reference Point Definition':
            event.reference_point_definition = get_or_create_cid(cont.ConceptCodeSequence[0].CodeValue, cont.ConceptCodeSequence[0].CodeMeaning)
        if cont.ValueType == 'CONTAINER':
            if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Mammography CAD Breast Composition':
                for cont2 in cont.ContentSequence:
                    if cont2.ConceptNamesCodes[0].CodeMeaning == 'Breast Composition':
                        event.breast_composition = cont2.CodeValue
                    if cont2.ConceptNamesCodes[0].CodeMeaning == 'Percent Fibroglandular Tissue':
                        event.percent_fibroglandular_tissue = cont2.NumericValue 
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Comment':
            event.comment = cont.TextValue
    
    # needs include for optional multiple person participant
    _irradiationeventxraydetectordata(dataset,event)
    _irradiationeventxraysourcedata(dataset,event)
    _irradiationeventxraymechanicaldata(dataset,event)

    event.save()

def _calibration(dataset,accum): 
    from remapp.models import Calibration
    from remapp.tools.get_values import get_or_create_cid
    from remapp.tools.dcmdatetime import make_date_time
    cal = Calibration.objects.create(accumulated_xray_dose=accum)
    for cont in dataset.ContentSequence:
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Dose Measurement Device':
            cal.dose_measurement_device = get_or_create_cid(cont.ConceptCodeSequence[0].CodeValue, cont.ConceptCodeSequence[0].CodeMeaning)
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Calibration Date':
            cal.calibration_date = make_date_time(cont.DateTime)
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Calibration Factor':
            cal.calibration_factor = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Calibration Uncertainty':
            cal.calibration_uncertainty = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Calibration Responsible Party':
            cal.calibration_responsible_party = cont.TextValue
    cal.save()

def _accumulatedmammoxraydose(dataset,accum): # TID 10005
    from remapp.models import Accumulated_mammography_xray_dose
    from remapp.tools.get_values import get_or_create_cid
    accummammo = Accumulated_mammography_xray_dose.objects.create(accumulated_xray_dose=accum)
    for cont in dataset.ContentSequence:
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Accumulated Average Glandular Dose':
            accummammo.accumulated_average_glandular_dose = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Laterality':
            accummammo.laterality = get_or_create_cid(cont.ConceptCodeSequence[0].CodeValue, cont.ConceptCodeSequence[0].CodeMeaning)
    accummammo.save()

def _accumulatedprojectionxraydose(dataset,accum): # TID 10004
    from remapp.tools.get_values import get_or_create_cid
    from remapp.models import Accumulated_projection_xray_dose, Content_item_descriptions
    
    accumproj = Accumulated_projection_xray_dose.objects.create(accumulated_xray_dose=accum)
    for cont in dataset.ContentSequence:
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Dose Area Product Total':
            accumproj.dose_area_product_total = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Dose (RP) Total':
            accumproj.dose_rp_total = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Fluoro Dose Area Product Total':
            accumproj.fluoro_dose_area_product_total = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Fluoro Dose (RP) Total':
            accumproj.fluoro_dose_rp_total = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Total Fluoro Time':
            accumproj.total_fluoro_time = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Acquisition Dose Area Product Total':
            accumproj.acquisition_dose_area_product_total = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Acquisition Dose (RP) Total':
            accumproj.acquisition_dose_rp_total = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Total Acquisition Time':
            accumproj.total_acquisition_time = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Total Number of Radiographic Frames':
            accumproj.total_number_of_radiographic_frames = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Reference Point Definition':
            # will break if text instead of code?
            accumproj.reference_point_definition_code = get_or_create_cid(cont.ConceptCodeSequence[0].CodeValue, cont.ConceptCodeSequence[0].CodeMeaning)
    if (accumproj.fluoro_dose_area_product_total != "" or
        accumproj.total_fluoro_time != "" or
        accumproj.acquisition_dose_area_product_total != "" or
        accumproj.total_acquisition_time != ""):
            accumproj.accumulated_xray_dose.projection_xray_radiation_dose.general_study_module_attributes.modality_type = 'RF'
    elif accumproj.total_number_of_radiographic_frames != "":
        accumproj.accumulated_xray_dose.projection_xray_radiation_dose.general_study_module_attributes.modality_type = "DX"
    accumproj.save()


def _accumulatedcassettebasedprojectionradiographydose(dataset,accum): # TID 10006
    from remapp.models import Accumulated_cassette_based_projection_radiography_dose
    from remapp.tools.get_values import get_or_create_cid
    accumcass = Accumulated_cassette_based_projection_radiography_dose.objects.create(accumulated_xray_dose=accum)
    for cont in dataset.ContentSequence:
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Detector Type':
            accumcass.detector_type = get_or_create_cid(cont.ConceptCodeSequence[0].CodeValue, cont.ConceptCodeSequence[0].CodeMeaning)
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Total Number of Radiographic Frames':
            accumcass.total_number_of_radiographic_frames = cont.MeasuredValueSequence[0].NumericValue
    accumcass.save()

def _accumulatedintegratedprojectionradiographydose(dataset,accum): # TID 10007
    from remapp.models import Accumulated_integrated_projection_radiography_dose
    from remapp.tools.get_values import get_or_create_cid
    accumint = Accumulated_integrated_projection_radiography_dose.objects.create(accumulated_xray_dose=accum)
    for cont in dataset.ContentSequence:
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Dose Area Product Total':
            accumint.dose_area_product_total = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Dose (RP) Total':
            accumint.dose_rp_total = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Total Number of Radiographic Frames':
            accumint.total_number_of_radiographic_frames = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Reference Point Definition':
            accumint.reference_point_definition_code = get_or_create_cid(cont.ConceptCodeSequence[0].CodeValue, cont.ConceptCodeSequence[0].CodeMeaning) # will fail if text
    accumint.save()

def _accumulatedxraydose(dataset,proj): # TID 10002
    from remapp.models import Accumulated_xray_dose, Content_item_descriptions
    from remapp.tools.get_values import get_or_create_cid
    accum = Accumulated_xray_dose.objects.create(projection_xray_radiation_dose=proj)
    for cont in dataset.ContentSequence:
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Acquisition Plane':
            accum.acquisition_plane = get_or_create_cid(cont.ConceptCodeSequence[0].CodeValue, cont.ConceptCodeSequence[0].CodeMeaning)
        if cont.ValueType == 'CONTAINER':
            if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Calibration':
                _calibration(cont,accum)
    _accumulatedprojectionxraydose(dataset,accum)
    if accum.projection_xray_radiation_dose.procedure_reported == 'P5-40010':
        _accumulatedmammoxraydose(dataset,accum)
    _accumulatedcassettebasedprojectionradiographydose(dataset,accum)
    _accumulatedintegratedprojectionradiographydose(dataset,accum)
    accum.save()

def _scanninglength(dataset,event): # TID 10014
    from remapp.models import Scanning_length
    scanlen = Scanning_length.objects.create(ct_irradiation_event_data=event)
    for cont in dataset.ContentSequence:
        if cont.ConceptNameCodeSequence[0].CodeMeaning.lower() == 'scanning length':
            scanlen.scanning_length = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning.lower() == 'length of reconstructable volume':
            scanlen.length_of_reconstructable_volume = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning.lower() == 'exposed range':
            scanlen.exposed_range = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning.lower() == 'top z location of reconstructable volume':
            scanlen.top_z_location_of_reconstructable_volume = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning.lower() == 'bottom z location of reconstructable volume':
            scanlen.bottom_z_location_of_reconstructable_volume = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning.lower() == 'top z location of scanning length':
            scanlen.top_z_location_of_scanning_length = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning.lower() == 'bottom z location of scanning length':
            scanlen.bottom_z_location_of_scanning_length = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning.lower() == 'irradiation event uid':
            scanlen.irradiation_event_uid = cont.UID
    scanlen.save()

def _ctxraysourceparameters(dataset,event):
    from remapp.models import Ct_xray_source_parameters
    param = Ct_xray_source_parameters.objects.create(ct_irradiation_event_data=event)
    for cont in dataset.ContentSequence:
        if cont.ConceptNameCodeSequence[0].CodeMeaning.lower() == 'identification of the x-ray source' or cont.ConceptNameCodeSequence[0].CodeMeaning.lower() == 'identification number of the x-ray source':
            param.identification_of_the_xray_source = cont.TextValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'KVP':
            param.kvp = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning.lower() == 'maximum x-ray tube current':
            param.maximum_xray_tube_current = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning.lower() == 'x-ray tube current':
            param.xray_tube_current = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Exposure Time per Rotation':
            param.exposure_time_per_rotation = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning.lower() == 'x-ray filter aluminum equivalent':
            param.xray_filter_aluminum_equivalent = cont.MeasuredValueSequence[0].NumericValue
    param.save()


def _ctirradiationeventdata(dataset,ct): # TID 10013
    from remapp.models import Ct_irradiation_event_data
    from remapp.tools.get_values import get_or_create_cid
    event = Ct_irradiation_event_data.objects.create(ct_radiation_dose=ct)
    for cont in dataset.ContentSequence:
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Acquisition Protocol':
            event.acquisition_protocol = cont.TextValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'TargetRegion':
            event.target_region = get_or_create_cid(cont.ConceptCodeSequence[0].CodeValue, cont.ConceptCodeSequence[0].CodeMeaning)
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'CT Acquisition Type':
            event.ct_acquisition_type = get_or_create_cid(cont.ConceptCodeSequence[0].CodeValue, cont.ConceptCodeSequence[0].CodeMeaning)
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'ProcedureContext':
            event.procedure_context = get_or_create_cid(cont.ConceptCodeSequence[0].CodeValue, cont.ConceptCodeSequence[0].CodeMeaning)
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Irradiation Event UID':
            event.irradiation_event_uid = cont.UID
        if cont.ValueType == 'CONTAINER':
            if cont.ConceptNameCodeSequence[0].CodeMeaning == 'CT Acquisition Parameters':
                _scanninglength(cont,event)
                for cont2 in cont.ContentSequence:
                    if cont2.ConceptNameCodeSequence[0].CodeMeaning == 'Exposure Time':
                        event.exposure_time = cont2.MeasuredValueSequence[0].NumericValue
                    if cont2.ConceptNameCodeSequence[0].CodeMeaning == 'Nominal Single Collimation Width':
                        event.nominal_single_collimation_width = cont2.MeasuredValueSequence[0].NumericValue
                    if cont2.ConceptNameCodeSequence[0].CodeMeaning == 'Nominal Total Collimation Width':
                        event.nominal_total_collimation_width = cont2.MeasuredValueSequence[0].NumericValue
                    if cont2.ConceptNameCodeSequence[0].CodeMeaning == 'Pitch Factor':
                        event.pitch_factor = cont2.MeasuredValueSequence[0].NumericValue
                    if cont2.ConceptNameCodeSequence[0].CodeMeaning.lower() == 'number of x-ray sources':
                        event.number_of_xray_sources = cont2.MeasuredValueSequence[0].NumericValue
                    if cont2.ValueType == 'CONTAINER':
                        if cont2.ConceptNameCodeSequence[0].CodeMeaning.lower() == 'ct x-ray source parameters':
                            _ctxraysourceparameters(cont2,event)
            if cont.ConceptNameCodeSequence[0].CodeMeaning == 'CT Dose':
                for cont2 in cont.ContentSequence:
                    if cont2.ConceptNameCodeSequence[0].CodeMeaning == 'Mean CTDIvol':
                        event.mean_ctdivol = cont2.MeasuredValueSequence[0].NumericValue
                    if cont2.ConceptNameCodeSequence[0].CodeMeaning == 'CTDIw Phantom Type':
                        event.ctdiw_phantom_type = get_or_create_cid(cont2.ConceptCodeSequence[0].CodeValue, cont2.ConceptCodeSequence[0].CodeMeaning)
                    if cont2.ConceptNameCodeSequence[0].CodeMeaning == 'CTDIfreeair Calculation Factor':
                        event.ctdifreeair_calculation_factor = cont2.MeasuredValueSequence[0].NumericValue
                    if cont2.ConceptNameCodeSequence[0].CodeMeaning == 'Mean CTDIfreeair':
                        event.mean_ctdifreeair = cont2.MeasuredValueSequence[0].NumericValue
                    if cont2.ConceptNameCodeSequence[0].CodeMeaning == 'DLP':
                        event.dlp = cont2.MeasuredValueSequence[0].NumericValue
                    if cont2.ConceptNameCodeSequence[0].CodeMeaning == 'Effective Dose':
                        event.effective_dose = cont2.MeasuredValueSequence[0].NumericValue
                    ## Effective dose measurement method and conversion factor
                    ## CT Dose Check details here
        if cont.ConceptNameCodeSequence[0].CodeMeaning.lower() == 'x-ray modulation type':
            event.xray_modulation_type = cont.TextValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Comment':
            event.comment = cont.TextValue
    if not event.xray_modulation_type and event.comment:
        comments = event.comment.split(",")
        for comm in comments:
            if comm.lstrip().startswith("X-ray Modulation Type"):
                modulationtype = comm[(comm.find('=')+2):]
                event.xray_modulation_type = modulationtype
        
    ## personparticipant here
    _deviceparticipant(dataset,'ct_event',event)
    event.save()
                        

def _ctaccumulateddosedata(dataset,ct): # TID 10012
    from remapp.models import Ct_accumulated_dose_data, Content_item_descriptions
    ctacc = Ct_accumulated_dose_data.objects.create(ct_radiation_dose=ct)
    for cont in dataset.ContentSequence:
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Total Number of Irradiation Events':
            ctacc.total_number_of_irradiation_events = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'CT Dose Length Product Total':
            ctacc.ct_dose_length_product_total = cont.MeasuredValueSequence[0].NumericValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'CT Effective Dose Total':
            ctacc.ct_effective_dose_total = cont.MeasuredValueSequence[0].NumericValue
        #
        # Reference authority code or name belongs here, followed by the effective dose details
        #
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Comment':
            ctacc.comment = cont.TextValue
    _deviceparticipant(dataset,'ct_accumulated',ctacc)

    ctacc.save()


def _projectionxrayradiationdose(dataset,g,reporttype):
    from remapp.models import Projection_xray_radiation_dose, Ct_radiation_dose, Observer_context
    from remapp.tools.get_values import get_or_create_cid
    from remapp.tools.dcmdatetime import make_date_time
    if reporttype == 'projection':
        proj = Projection_xray_radiation_dose.objects.create(general_study_module_attributes=g)
    elif reporttype == 'ct':
        proj = Ct_radiation_dose.objects.create(general_study_module_attributes=g)
    else: pass
    for cont in dataset.ContentSequence:
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Procedure reported':
            proj.procedure_reported = get_or_create_cid(cont.ConceptCodeSequence[0].CodeValue, cont.ConceptCodeSequence[0].CodeMeaning)
            if ('ContentSequence' in cont): # Extra if statement to allow for non-conformant GE RDSR that don't have this mandatory field.
                for cont2 in cont.ContentSequence:
                    if cont2.ConceptNameCodeSequence[0].CodeMeaning == 'Has Intent':
                        proj.has_intent = get_or_create_cid(cont2.ConceptCodeSequence[0].CodeValue, cont2.ConceptCodeSequence[0].CodeMeaning)
        if cont.ConceptNameCodeSequence[0].CodeMeaning.lower() == 'start of x-ray irradiation':
            proj.start_of_xray_irradiation = make_date_time(cont.DateTime)
        if cont.ConceptNameCodeSequence[0].CodeMeaning.lower() == 'end of x-ray irradiation':
            proj.end_of_xray_irradiation = make_date_time(cont.DateTime) 
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Scope of Accumulation':
            proj.scope_of_accumulation = get_or_create_cid(cont.ConceptCodeSequence[0].CodeValue, cont.ConceptCodeSequence[0].CodeMeaning)
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Comment':
            proj.comment = cont.TextValue
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Source of Dose Information':
            proj.source_of_dose_information = get_or_create_cid(cont.ConceptCodeSequence[0].CodeValue, cont.ConceptCodeSequence[0].CodeMeaning)
        proj.save()
        
        if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Observer Type':
            if reporttype == 'projection':
                obs = Observer_context.objects.create(projection_xray_radiation_dose=proj)
            elif reporttype == 'ct':
                obs = Observer_context.objects.create(ct_radiation_dose=proj)
            _observercontext(dataset,obs)

        if cont.ValueType == 'CONTAINER':
            if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Accumulated X-Ray Dose Data':
                proj.general_study_module_attributes.modality_type = 'RF,DX'
                _accumulatedxraydose(cont,proj)
            if cont.ConceptNameCodeSequence[0].CodeMeaning == 'Irradiation Event X-Ray Data':
                _irradiationeventxraydata(cont,proj)
            if cont.ConceptNameCodeSequence[0].CodeMeaning == 'CT Accumulated Dose Data':
                proj.general_study_module_attributes.modality_type = 'CT'
                _ctaccumulateddosedata(cont,proj)
            if cont.ConceptNameCodeSequence[0].CodeMeaning == 'CT Acquisition':
                _ctirradiationeventdata(cont,proj)

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
    patientatt.patient_age = get_value_kw("PatientAge",dataset)
    patientatt.patient_weight = get_value_kw("PatientWeight",dataset)
    patientatt.save()

def _patientmoduleattributes(dataset,g): # C.7.1.1
    from remapp.models import Patient_module_attributes, Patient_study_module_attributes
    from remapp.tools.get_values import get_value_kw
    from remapp.tools.dcmdatetime import get_date
    from remapp.tools.not_patient_indicators import get_not_pt
    from datetime import timedelta
    from decimal import Decimal
    pat = Patient_module_attributes.objects.create(general_study_module_attributes=g)
    patient_birth_date = get_date("PatientBirthDate",dataset) # Not saved to database
    pat.patient_sex = get_value_kw("PatientSex",dataset)
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
    from remapp.tools.get_values import get_value_kw, get_seq_code_value, get_seq_code_meaning
    from remapp.tools.dcmdatetime import get_date, get_time
    g.study_instance_uid = get_value_kw('StudyInstanceUID',dataset)
    g.study_date = get_date('StudyDate',dataset)
    g.study_time = get_time('StudyTime',dataset)
    g.referring_physician_name = get_value_kw('ReferringPhysicianName',dataset)
    g.referring_physician_identification = get_value_kw('ReferringPhysicianIdentification',dataset)
    g.study_id = get_value_kw('StudyID',dataset)
    g.accession_number = get_value_kw('AccessionNumber',dataset)
    g.study_description = get_value_kw('StudyDescription',dataset)
    g.physician_of_record = get_value_kw('PhysicianOfRecord',dataset)
    g.name_of_physician_reading_study = get_value_kw('NameOfPhysicianReadingStudy',dataset)
    g.performing_physician_name = get_value_kw('PerformingPhysicianName',dataset)
    g.operator_name = get_value_kw('OperatorName',dataset)
    g.procedure_code_value = get_seq_code_value('ProcedureCodeSequence',dataset)
    g.procedure_code_meaning = get_seq_code_meaning('ProcedureCodeSequence',dataset)
    g.requested_procedure_code_value = get_seq_code_value('RequestedProcedureCodeSequence',dataset)
    g.requested_procedure_code_meaning = get_seq_code_meaning('RequestedProcedureCodeSequence',dataset)
    if dataset.ContentTemplateSequence[0].TemplateIdentifier == '10001':
        _projectionxrayradiationdose(dataset,g,'projection')
    elif dataset.ContentTemplateSequence[0].TemplateIdentifier == '10011':
        _projectionxrayradiationdose(dataset,g,'ct')
    g.save()
    if not g.requested_procedure_code_meaning:
        if (('RequestAttributesSequence' in dataset) and dataset[0x40,0x275].VM): # Ulgy hack to prevent issues with zero length LS16 sequence
            req = dataset.RequestAttributesSequence
            g.requested_procedure_code_meaning = get_value_kw('RequestedProcedureDescription',req[0])
            if not g.requested_procedure_code_meaning: # Sometimes the above is true, but there is no RequestedProcedureDescription in that sequence, but there is a basic field as below.
                g.requested_procedure_code_meaning = get_value_kw('RequestedProcedureDescription',dataset)
            g.save()
        else:
            g.requested_procedure_code_meaning = get_value_kw('RequestedProcedureDescription',dataset)
            g.save()
        

def _rsdr2db(dataset):
    import os, sys
    import openrem_settings

    os.environ['DJANGO_SETTINGS_MODULE'] = 'openrem.openremproject.settings'
    from django.db import models

    openrem_settings.add_project_to_path()
    from remapp.models import General_study_module_attributes

    if 'StudyInstanceUID' in dataset:
        uid = dataset.StudyInstanceUID
        existing = General_study_module_attributes.objects.filter(study_instance_uid__exact = uid)
        if existing:
            sys.exit()

    g = General_study_module_attributes.objects.create()
    _generalstudymoduleattributes(dataset,g)
    _generalequipmentmoduleattributes(dataset,g)
    _patientstudymoduleattributes(dataset,g)
    _patientmoduleattributes(dataset,g)


def rdsr(rdsr_file):
    """Extract radiation dose related data from DICOM Radiation SR objects.

    :param filename: relative or absolute path to Radiation Dose Structured Report.
    :type filename: str.
    
    Tested with:
        * CT: Siemens, Philips and GE RDSR, GE Enhanced SR.
        * Fluoro: Siemens Artis Zee RDSR
    """

    import sys, dicom
    dataset = dicom.read_file(rdsr_file)

    if dataset.SOPClassUID == '1.2.840.10008.5.1.4.1.1.88.22':
        print '{0}{1}'.format(rdsr_file," is not an RDSR, but it is an enhanced structured report, so we'll attempt to use it")
    elif dataset.SOPClassUID != '1.2.840.10008.5.1.4.1.1.88.67':
        return ('{0}{1}'.format(rdsr_file," is not a Radiation Dose Structured Report"))
    elif dataset.ConceptNameCodeSequence[0].CodeValue != '113701':
        return ('{0}{1}'.format(rdsr_file," doesn't seem to have a report in it :-("))

    _rsdr2db(dataset)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        sys.exit('Error: Supply exactly one argument - the DICOM RDSR file')

    sys.exit(rdsr(sys.argv[1]))
