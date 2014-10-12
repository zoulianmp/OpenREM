# test_get_values.py

from django.test import TestCase
from dicom.sequence import Sequence
from dicom.dataset import Dataset
from remapp.tools.get_values import get_seq_code_value, get_seq_code_meaning

class GetCodeValueTests(TestCase):
    def test_get_code_value_value_exists(self):
        """
        get_seq_code_value should return the CodeValue when it is present
        """
        dummySeq = Dataset()
        ds = Dataset()
        dummySeq.CodeValue = '1234'
        ds.ViewCodeSequence = Sequence([dummySeq])
        val = get_seq_code_value('ViewCodeSequence',ds)
        
        self.assertEqual(val, '1234')

    def test_get_code_value_attr_not_present(self):
        """
        get_seq_code_value should not return and not error when CodeValue is not present
        """
        dummySeq = Dataset()
        ds = Dataset()
        ds.ViewCodeSequence = Sequence([dummySeq])
        val = get_seq_code_value('ViewCodeSequence',ds)
        
        self.assertEqual(val, None)

class GetCodeMeaningTests(TestCase):
    def test_get_code_meaning_meaning_exists(self):
        """
        get_seq_code_meaning should return the CodeMeaning when it is present
        """
        dummySeq = Dataset()
        ds = Dataset()
        dummySeq.CodeMeaning = 'A code meaning'
        ds.ViewCodeSequence = Sequence([dummySeq])
        val = get_seq_code_meaning('ViewCodeSequence',ds)
        
        self.assertEqual(val, 'A code meaning')

    def test_get_code_value_attr_not_present(self):
        """
        get_seq_code_value should not return and not error when CodeMeaning is not present
        """
        dummySeq = Dataset()
        ds = Dataset()
        ds.ViewCodeSequence = Sequence([dummySeq])
        val = get_seq_code_meaning('ViewCodeSequence',ds)
        
        self.assertEqual(val, None)
