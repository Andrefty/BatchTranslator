from flask import Flask
from flask import Response
import os, gc
import zipfile
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import argostranslate.package
import argostranslate.translate
from langdetect import detect
import shutil
import mysql.connector
from azure.communication.email import EmailClient, EmailContent, EmailAddress, EmailMessage, EmailRecipients

def send_email(recipient_email,zipurl):
    # Create an EmailClient using your Azure Communication Services connection string
    email_client = EmailClient.from_connection_string("endpoint=https://csforemail.communication.azure.com/;accesskey=***REMOVED***")

    # Set the recipient's email address, subject, and body of the email
    to_email_address = EmailAddress(email=recipient_email)
    recipi=EmailRecipients(to=[to_email_address])
    subject = "Translated zip file"
    body = "Here is the link to your translated zip file: "+zipurl
    content=EmailContent(subject=subject,plain_text=body)
    mess=EmailMessage(sender="***REMOVED***",content=content,recipients=recipi)

    # Send the email
    email_client.send(mess)

app = Flask(__name__)

# Connect to the database
cnx = mysql.connector.connect(
    user='user',
    password='***REMOVED***',
    host='***REMOVED***',
    database='emaildb'
)
cnx.autocommit=True
# Create a cursor to execute queries
cursor = cnx.cursor()

# Check if the blname exists in the database
query = "SELECT email FROM uiapp_emailaddress WHERE filename = %s"
delquery = "DELETE FROM uiapp_emailaddress WHERE filename = %s"
def zip_translated_files(zip_path, unzip_dir):
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        for file in os.listdir(unzip_dir):
            file_path = os.path.join(unzip_dir, file)
            zip_file.write(file_path,os.path.basename(file_path))


@app.route('/process_blob/<blname>')
def process_blob(blname):
    workpath = os.path.join(os.path.abspath(__file__), "unzipfolder")
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
        gc.collect()
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

            if (from_code not in [i.code for i in argostranslate.translate.get_installed_languages()]) or (to_code not in [i.code for i in argostranslate.translate.get_installed_languages()]):
                print("Language not installed, installing...")
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
        bl_cl=destination_container_client.upload_blob(name=blname+".zip", data=data)

    # Delete the zip file
    os.remove(zip_path)

    # Delete the unzip directory
    shutil.rmtree(unzip_dir)

    # Delete the blob from storage
    blob_client.delete_blob()

    cursor.execute(query, (blname,))
    rec=cursor.fetchone()
    if rec:
        send_email(rec[0],bl_cl.url)
        cursor.execute(delquery,(blname,))
        print(cursor.rowcount, "record(s) deleted")
    gc.collect()
    return Response(status=200)

if __name__ == '__main__':
    app.run()
