DICOM import modules
====================

RDSR module
+++++++++++

Ultimately this should be the only module required as it deals with all
Radiation Dose Structured Reports. Currently this has only been tested on
CT and fluoroscopy structured reports, but it also has the logic for
mammography structured reports if they start to appear.

.. automodule:: remapp.extractors.rdsr
    :members:

.. _mammo-module:

Mammography module
++++++++++++++++++

Mammography is interesting in that all the information required for dose
audit is contained in the image header, including patient 'size', ie thickness.
However the disadvantage over an RSDR is the requirement to process each
individual image rather than a single report for the study, which would 
also capture any rejected images.

.. automodule:: remapp.extractors.mam
    :members:

CT non-standard modules
+++++++++++++++++++++++

Initially only Philips CT dose report images are catered for. These have
all the information that could be derived from the images also held in
the DICOM header information, making harvesting relatively easy.

.. automodule:: remapp.extractors.ct_philips
    :members:

