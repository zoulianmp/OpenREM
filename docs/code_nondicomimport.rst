Non-DICOM import modules
========================

Patient height and weight csv import module
+++++++++++++++++++++++++++++++++++++++++++

This module enables a csv file to be parsed and the height and weight information
extracted and added to existing studies in the OpenREM database. An example may be
a csv extract from a RIS or EPR system.

There needs to be a common unique identifier for the exam - currently this
is limited to accession number or study instance UID.

.. automodule:: remapp.extractors.ptsizecsv2db
    :members:

.. autotask::   remapp.extractors.ptsizecsv2db.websizeimport
