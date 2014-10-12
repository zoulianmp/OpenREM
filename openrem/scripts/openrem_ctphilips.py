#!/usr/local/bin/python
# scripts/openrem_ctphilips

"""Script to launch the ct_philips module to import information from Philips CT 

    :param filename: relative or absolute path to Philips CT dose report DICOM image file.
    :type filename: str.

    Tested with:
        * Philips Gemini TF PET-CT v2.3.0
        * Brilliance BigBore v3.5.4.17001.
"""

import sys
from openrem.remapp.extractors import ct_philips

if len(sys.argv) < 2:
    sys.exit('Error: Supply at least one argument - the Philips dose report image')

for sr in sys.argv[1:]:
    ct_philips(sr)

sys.exit()
