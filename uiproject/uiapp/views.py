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
                "***REMOVED***")
            container_name = "uploadzip"
            container_client = blob_service_client.get_container_client(
                container_name)
            print("fromcleaneddata", form.cleaned_data["filename"])
            blob_client = container_client.upload_blob(
                data=form.cleaned_data["uploadfile"], name=form.cleaned_data["filename"])
            # make a request to the backend
            try:
                requests.get("http://127.0.0.1:5000/process_blob/"+form.cleaned_data["filename"],timeout=0.000001)
            except requests.exceptions.ReadTimeout: 
                pass
            if form.cleaned_data["email"] == '':
                return super().form_invalid(form)
            self.object = form.save()
            return super().form_valid(form) 
        except forms.ValidationError as e:
            form.add_error('uploadfile', e)
            return super().form_invalid(form)


"""
from django.views.generic import View
from django.http import HttpResponse

from azure.storage.blob import BlobServiceClient


class FileUploadView(View):
    def post(self, request):
        # Get the uploaded file from the request
        uploaded_file = request.FILES['file']

        # Connect to Azure Blob Storage
        blob_service_client = BlobServiceClient.from_connection_string("<your_connection_string>")

        # Get the container where the file will be uploaded
        container_name = "<your_container_name>"
        container_client = blob_service_client.get_container_client(container_name)

        # Upload the file
        blob_client = container_client.upload_blob(uploaded_file, blob_name=uploaded_file.name)

        # Return a successful response
        return HttpResponse("File uploaded successfully.")

"""
