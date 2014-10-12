from remapp.models import (General_study_module_attributes, 
    Projection_xray_radiation_dose, Observer_context, 
    Accumulated_xray_dose, Calibration, Irradiation_event_xray_data, 
    Image_view_modifier, Person_participant, 
    Irradiation_event_xray_detector_data, Irradiation_event_xray_source_data, 
    Pulse_width, Kvp, Xray_tube_current, Exposure, Xray_filters, Xray_grid,
    Device_participant, Irradiation_event_xray_mechanical_data, 
    Dose_related_distance_measurements, Accumulated_projection_xray_dose, 
    Accumulated_mammography_xray_dose, 
    Accumulated_cassette_based_projection_radiography_dose, 
    Accumulated_integrated_projection_radiography_dose, 
    Patient_module_attributes, General_equipment_module_attributes, 
    Patient_study_module_attributes, Content_item_descriptions,
    Ct_radiation_dose, Ct_accumulated_dose_data,
    Ct_irradiation_event_data, Scanning_length,
    Ct_dose_check_details, Ct_xray_source_parameters,
    Exports, Size_upload)

from django.contrib import admin

admin.site.register(General_study_module_attributes) 
admin.site.register(Projection_xray_radiation_dose)
admin.site.register(Observer_context)
admin.site.register(Accumulated_xray_dose)
admin.site.register(Calibration)
admin.site.register(Irradiation_event_xray_data)
admin.site.register(Image_view_modifier)
admin.site.register(Person_participant)
admin.site.register(Irradiation_event_xray_detector_data)
admin.site.register(Irradiation_event_xray_source_data)
admin.site.register(Pulse_width)
admin.site.register(Kvp)
admin.site.register(Xray_tube_current)
admin.site.register(Exposure)
admin.site.register(Xray_filters)
admin.site.register(Xray_grid)
admin.site.register(Device_participant)
admin.site.register(Irradiation_event_xray_mechanical_data)
admin.site.register(Dose_related_distance_measurements)
admin.site.register(Accumulated_projection_xray_dose)
admin.site.register(Accumulated_mammography_xray_dose)
admin.site.register(Accumulated_cassette_based_projection_radiography_dose)
admin.site.register(Accumulated_integrated_projection_radiography_dose)
admin.site.register(Patient_module_attributes)
admin.site.register(General_equipment_module_attributes)
admin.site.register(Patient_study_module_attributes)
admin.site.register(Content_item_descriptions)
admin.site.register(Ct_radiation_dose)
admin.site.register(Ct_accumulated_dose_data)
admin.site.register(Ct_irradiation_event_data)
admin.site.register(Scanning_length)
admin.site.register(Ct_dose_check_details)
admin.site.register(Ct_xray_source_parameters)
admin.site.register(Exports)
admin.site.register(Size_upload)
