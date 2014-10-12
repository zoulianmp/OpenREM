#!/usr/local/bin/python
# scripts/openrem_rdsr

"""Script to launch the rdsr to import information from DICOM Radiation SR objects 

    :param filename: relative or absolute path to Radiation Dose Structured Report.
    :type filename: str.

    Tested with:
        * CT: Siemens, Philips and GE RDSR, GE Enhanced SR.
        * Fluoro: Siemens Artis Zee RDSR
"""

import sys
from openrem.remapp.extractors import rdsr

if len(sys.argv) < 2:
    sys.exit('Error: Supply at least one argument - the radiation dose structured report')

for sr in sys.argv[1:]:
    rdsr(sr)
    
sys.exit()
