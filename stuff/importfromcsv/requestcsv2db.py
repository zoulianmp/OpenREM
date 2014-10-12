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
..  module:: requestcsv2db.
    :synopsis: Use to import Requested Procedure Description data from csv file to existing studies in the database.

    To use, copy this file into openrem/remapp/extractors/ and run it using python.

..  moduleauthor:: Ed McDonagh

"""



def _requestinsert(accno,request,siuid, verbose):
    from django.db import models
    from remapp.models import General_study_module_attributes
    from django import db
    
    if request and accno:
        if not siuid:
            e = General_study_module_attributes.objects.filter(accession_number__exact = accno)
        else:
            e = General_study_module_attributes.objects.filter(study_instance_uid__exact = accno)
        if e:
            for exam in e:
                if verbose:
                    print accno + ":"
                exam.requested_procedure_code_meaning = request
                exam.save()
        elif verbose:
            print "Accession number " + accno + " not found in db"
    db.reset_queries()
       

    
def requestcsv2db(*args, **kwargs):
    """ Import Requested Procedure Description data from csv files. Must be placed with extractor routines in openrem/remapp/extractors/
        
    :param --si-uid: Use Study Instance UID instead of Accession Number. Short form -s.
    :type --si-uid: bool
    :param csvfile: relative or absolute path to csv file
    :type csvfile: str
    :param id: Accession number column header or header if -u or --si-uid is set. Quote if necessary.
    :type id: str
    :param height: Patient height column header. Create if necessary, quote if necessary.
    :type height: str
    :param weight: Patient weight column header. Create if necessary, quote if necessary.
    :type weight: str

    Example::
        
        pythoon requestcsv2db.py -s MyRequests.csv StudyInstanceUID RequestedProcedureDescription

    To create an appropriate csv file, you might use exiftool::
    
        exiftool -s -s -s -AccessionNumber -StudyInstanceUID -RequestedProcedureDescription -csv *.dcm > requests.csv

    See https://bitbucket.org/edmcdonagh/openrem/issue/75/ for history

    """

    import os, sys, csv
    import argparse
    import openrem_settings

    
    # Required and optional arguments
    parser = argparse.ArgumentParser(description="Import height and weight data into an OpenREM database. If either is missing just add a blank column with appropriate title.")
    parser.add_argument("-u", "--si-uid", action="store_true", help="Use Study Instance UID instead of Accession Number")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("csvfile", help="csv file containing the height and/or weight information and study identifier")
    parser.add_argument("id", help="Column title for the accession number or study instance UID")
    parser.add_argument("request", help="Column title for the requested procedure description")
    args=parser.parse_args()
    
    openrem_settings.add_project_to_path()
    os.environ['DJANGO_SETTINGS_MODULE'] = '{0}.settings'.format(openrem_settings.name_of_project())
    
    f = open(args.csvfile, 'rb')
    try:
        dataset = csv.DictReader(f)        
        for line in dataset:
            _requestinsert(line[args.id], line[args.request], args.si_uid, args.verbose)
    finally:
        f.close()

if __name__ == "__main__":
    import sys
    sys.exit(requestcsv2db())
