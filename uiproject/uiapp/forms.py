from .models import Emailaddress
from django import forms
# import zipfile

class EmailaddressForm(forms.ModelForm):
    uploadfile=forms.FileField()
    # def clean_file(self):
    #     # Get the uploaded file
    #     file = self.cleaned_data['file']

    #     # Check if the uploaded file is a zip file
    #     if file.content_type != 'application/zip':
    #         raise forms.ValidationError('The uploaded file must be a zip file')

    #     # Return the cleaned file data
    #     return file
    # def clean_file(self):
    #     file = self.cleaned_data['uploadfile']
    #     try:
    #         with zipfile.ZipFile(file) as zip:
    #             zip.testzip()
    #     except zipfile.BadZipFile:
    #         raise forms.ValidationError('The file is not a valid zip file')
    #     return file
    class Meta:
        model = Emailaddress
        fields = "__all__"
