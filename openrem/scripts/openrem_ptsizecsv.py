#!/usr/local/bin/python
# scripts/openrem_ptsizecsv

"""Script to launch the rdsr to import information from DICOM Radiation SR objects 

    :param filename: relative or absolute path to Radiation Dose Structured Report.
    :type filename: str.

    Tested with:
        * CT: Siemens, Philips and GE RDSR, GE Enhanced SR.
        * Fluoro: Siemens Artis Zee RDSR
"""

import sys
from openrem.remapp.extractors import ptsizecsv2db

sys.exit(ptsizecsv2db.csv2db(sys.argv))
