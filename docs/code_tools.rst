
Tools and helper modules
========================

OpenREM settings
++++++++++++++++
Administrative module to define the name of the project and to add it to
the Python path

.. automodule:: remapp.extractors.openrem_settings
    :members:


Get values
++++++++++
Tiny modules to reduce repetition in the main code when extracting
information from DICOM headers using pydicom.

.. automodule:: remapp.tools.get_values
    :members:

Check if UID exists
+++++++++++++++++++
Small module to check if UID already exists in the database.

.. automodule:: remapp.tools.check_uid
    :members:

DICOM time and date values
++++++++++++++++++++++++++
Module to convert betweeen DICOM and Python dates and times.

.. automodule:: remapp.tools.dcmdatetime
    :members:

Test for QA or other non-patient related studies
++++++++++++++++++++++++++++++++++++++++++++++++

.. automodule:: remapp.tools.not_patient_indicators
    :members:
