from django import forms

class SizeUploadForm(forms.Form):
    """Form for patient size csv file upload
    """
    sizefile = forms.FileField(
        label='Select a file'
    )

class SizeHeadersForm(forms.Form):
    """Form for csv column header patient size imports through the web interface
    """

    height_field = forms.ChoiceField(choices='')
    weight_field = forms.ChoiceField(choices='')
    id_field = forms.ChoiceField(choices='')
    id_type = forms.ChoiceField(choices='')

    def __init__(self, my_choice=None, **kwargs):
        super(SizeHeadersForm, self).__init__(**kwargs)
        if my_choice:

            self.fields['height_field'] = forms.ChoiceField(choices=my_choice, widget=forms.Select(attrs={"class":"form-control"}))
            self.fields['weight_field'] = forms.ChoiceField(choices=my_choice, widget=forms.Select(attrs={"class":"form-control"}))
            self.fields['id_field'] = forms.ChoiceField(choices=my_choice, widget=forms.Select(attrs={"class":"form-control"}))
            ID_TYPES = (("acc-no", "Accession Number"),("si-uid", "Study instance UID"))
            self.fields['id_type'] = forms.ChoiceField(choices=ID_TYPES, widget=forms.Select(attrs={"class":"form-control"}))

