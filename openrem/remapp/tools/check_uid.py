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
..  module:: check_uid.
    :synopsis: Simple module to check if uid already exists in database.

..  moduleauthor:: Ed McDonagh

"""


def check_uid(uid, level='Study'):
    """Check if UID already exists in database.

    :param uid:         Study UID.
    :type uid:          str.
    :returns:           1 if it does exist, 0 otherwise
    """
    import sys
    from remapp.models import General_study_module_attributes
    
    if level == 'Study':
        existing = General_study_module_attributes.objects.filter(study_instance_uid__exact = uid)
    elif level == 'Event':
        existing = General_study_module_attributes.objects.filter(projection_xray_radiation_dose__irradiation_event_xray_data__irradiation_event_uid__exact = uid)
    if existing:
        return 1

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(check_uid())
