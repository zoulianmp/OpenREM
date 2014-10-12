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
..  module:: get_values.
    :synopsis: Module to return values from DICOM elements using pydicom.

..  moduleauthor:: Ed McDonagh

"""

def get_value_kw(tag,dataset):
    """Get DICOM value by keyword reference.

    :param keyword:     DICOM keyword, no spaces or plural as per dictionary.
    :type keyword:      str.
    :param dataset:     The DICOM dataset containing the tag.
    :type dataset:      dataset
    :returns:           str. -- value
    """
    if (tag in dataset):
        value = getattr(dataset,tag)
        if value != '': 
            return value

def get_value_num(tag,dataset):
    """Get DICOM value by tag group and element number.
    
    Always use get_value_kw by preference for readability. This module can
    be required when reading private elements.

    :param tag:     DICOM group and element number as a single hexadecimal number (prefix 0x).
    :type tag:          hex
    :param dataset:     The DICOM dataset containing the tag.
    :type dataset:      dataset
    :returns:           str. -- value
    """
    if (tag in dataset):
        return dataset[tag].value

def get_seq_code_value(sequence,dataset):
    """From a DICOM sequence, get the code value.

    :param sequence:    DICOM sequence name.
    :type sequence:     DICOM keyword, no spaces or plural as per dictionary.
    :param dataset:     The DICOM dataset containing the sequence.
    :type dataset:      DICOM dataset
    :returns:           int. -- code value
    """
    if (sequence in dataset):
        seq = getattr(dataset,sequence)
        if hasattr(seq[0],'CodeValue'):  
            return seq[0].CodeValue
			
def get_seq_code_meaning(sequence,dataset):
    """From a DICOM sequence, get the code meaning.

    :param sequence:    DICOM sequence name.
    :type sequence:     DICOM keyword, no spaces or plural as per dictionary.
    :param dataset:     The DICOM dataset containing the sequence.
    :type dataset:      DICOM dataset
    :returns:           str. -- code meaning
    """
    if (sequence in dataset):
        seq = getattr(dataset,sequence)
        if hasattr(seq[0],'CodeMeaning'): 
            return seq[0].CodeMeaning

def get_or_create_cid(codevalue, codemeaning):
    """Create a code_value code_meaning pair entry in the Content_item_descriptions 
    table if it doesn't already exist. 

    :param codevalue:   Code value as defined in the DICOM standard part 16
    :type codevalue:    int.
    :param codemeaning: Code meaning as defined in the DICOM standard part 16
    :type codevalue:    int.
    :returns:           Content_item_descriptions entry for code value passed
    """
    from remapp.models import Content_item_descriptions
    if codevalue:
        if not Content_item_descriptions.objects.all().filter(code_value=codevalue).exists():
            cid = Content_item_descriptions(
                code_value = codevalue,
                code_meaning = codemeaning,
                )
            cid.save()
        return Content_item_descriptions.objects.get(code_value=codevalue)
