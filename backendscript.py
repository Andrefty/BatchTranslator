from flask import Flask
from flask import Response
import os
import zipfile
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import argostranslate.package
import argostranslate.translate
from langdetect import detect
import shutil

app = Flask(__name__)


def zip_translated_files(zip_path, unzip_dir):
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        for file in os.listdir(unzip_dir):
            file_path = os.path.join(unzip_dir, file)
            zip_file.write(file_path,os.path.basename(file_path))


@app.route('/process_blob/<blname>')
def process_blob(blname):
    workpath = os.path.join(os.getcwd(), "unzipfolder")
    # Create the BlobServiceClient object
    service_client = BlobServiceClient.from_connection_string(
        "***REMOVED***")

    # Create the container client
    container_name = "uploadzip"
    container_client = service_client.get_container_client(container_name)

    if container_client.get_blob_client(blname).exists():
        zip_path = os.path.join(workpath, blname)
        with open(zip_path, "wb") as f:
            blob_client = container_client.get_blob_client(blname)
            f.write(blob_client.download_blob().readall())
    else:
        # return http error message
        return Response(status=501)
    # Unzip the file
    unzip_dir = os.path.join(workpath, "dir"+blname)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(path=unzip_dir)

    # Delete the zip file
    os.remove(zip_path)

    # Translate each file in the zip to English using Argos, if the file is not in English
    for file in os.listdir(unzip_dir):
        file_path = os.path.join(unzip_dir, file)
        # Use buffered reading to read the file in chunks
        with open(file_path, 'r', encoding='utf-8') as input_file:
            text = input_file.read()
        os.remove(file_path)
        language = detect(text)
        if language != 'en':
            from_code = language
            to_code = "en"

            # Download and install Argos Translate package
            argostranslate.package.update_package_index()
            available_packages = argostranslate.package.get_available_packages()
            package_to_install = next(
                filter(
                    lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
                )
            )
            argostranslate.package.install_from_path(
                package_to_install.download())

            # Translate
            translated_text = argostranslate.translate.translate(
                text, from_code, to_code)

            # Use buffered writing to write the translated text in chunks
            with open(file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(translated_text)

    # Zip the translated files
    zip_path = os.path.join(workpath, "translated_"+blname)
    zip_translated_files(zip_path, unzip_dir)

    # Create the destination container client
    destination_service_client = BlobServiceClient.from_connection_string(
        "***REMOVED***")
    destination_container_name = "translatedzip"
    destination_container_client = destination_service_client.get_container_client(
        destination_container_name)

    # Upload the zip file to the destination container
    with open(zip_path, "rb") as data:
        destination_container_client.upload_blob(name=blname, data=data)

    # Delete the zip file
    os.remove(zip_path)

    # Delete the unzip directory
    shutil.rmtree(unzip_dir)

    # Delete the blob from storage
    blob_client.delete_blob()

    return Response(status=200)


if __name__ == '__main__':
    app.run()
