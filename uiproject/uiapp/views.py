from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import EmailaddressForm
from .models import Emailaddress
from azure.storage.blob import BlobServiceClient
from django import forms
import requests

# Create your views here.


class EmailaddressCreateView(CreateView):
    model = Emailaddress
    form_class = EmailaddressForm
    success_url = reverse_lazy('uiapp:emailaddress_create')

    def form_valid(self, form):
        try:
            print(form.cleaned_data["uploadfile"].content_type)
            # Test if the uploaded file is a zip file with all mime types

            if form.cleaned_data["uploadfile"].content_type != 'application/zip' and form.cleaned_data["uploadfile"].content_type != 'application/x-zip-compressed' and form.cleaned_data["uploadfile"].content_type != 'application/x-compressed' and form.cleaned_data["uploadfile"].content_type != 'multipart/x-zip' and form.cleaned_data["uploadfile"].content_type != 'application/octet-stream' and form.cleaned_data["uploadfile"].content_type != 'application/x-zip':
                raise forms.ValidationError(
                    'The uploaded file must be a zip file')
            blob_service_client = BlobServiceClient.from_connection_string(
                "")
            container_name = "uploadzip"
            container_client = blob_service_client.get_container_client(
                container_name)
            blob_client = container_client.upload_blob(
                data=form.cleaned_data["uploadfile"], name=form.cleaned_data["filename"])
            # make a request to the backend
            try:
                requests.get("http://127.0.0.1:5000/process_blob/"+form.cleaned_data["filename"],timeout=1)
            except requests.exceptions.Timeout: 
                pass
            if form.cleaned_data["email"] == '':
                return super().form_invalid(form)
            self.object = form.save()
            return super().form_valid(form) 
        except forms.ValidationError as e:
            form.add_error('uploadfile', e)
            return super().form_invalid(form)
