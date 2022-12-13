from .models import Emailaddress
from django import forms
import uuid
# import zipfile

class EmailaddressForm(forms.ModelForm):
    uploadfile=forms.FileField()
    def clean_filename(filename):
            return str(uuid.uuid4())
    class Meta:
        model = Emailaddress
        fields ="__all__"
        widgets = {
            'filename': forms.HiddenInput(),
        }
