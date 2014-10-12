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
..  module:: openrem_settings.
    :synopsis: Helper module to add the project to the path.

..  moduleauthor:: Ed McDonagh

"""

def add_project_to_path():
    """Add project to path, assuming this file is within project
    """
    import os, sys
    # Add project to path, assuming openrem app has been installed within project
    basepath = os.path.dirname(__file__)
    projectpath = os.path.abspath(os.path.join(basepath, "..",".."))
    if projectpath not in sys.path:
        sys.path.insert(1,projectpath)
