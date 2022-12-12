from .models import Email
from django import forms

class EmailForm(forms.ModelForm):
    file=forms.FileField()
    
    class Meta:
        model = Email
        fields = "__all__"