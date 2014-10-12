#!/usr/local/bin/python
# scripts/openrem_mg

"""Script to launch the mam module to import information from mammography images 

    :param filename: relative or absolute path to mammography DICOM image file.
    :type filename: str.

    Tested with:
        * GE Senographe DS software versions ADS_43.10.1 and ADS_53.10.10 only.

"""

import sys
from openrem.remapp.extractors import mam

if len(sys.argv) < 2:
    sys.exit('Error: Supply at least one argument - the DICOM mammography image file')

for sr in sys.argv[1:]:
    mam(sr)
    
sys.exit()
