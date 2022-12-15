import io
import os
import zipfile

from azure.cognitiveservices.language.translator import TranslatorClient
from azure.storage.blob import BlockBlobService


# create a BlockBlobService instance
blob_service = BlockBlobService(
    account_name="your_storage_account_name",
    account_key="your_storage_account_key"
)

# create a TranslatorClient instance
translator_client = TranslatorClient(
    endpoint="your_azure_translator_endpoint",
    credential="your_azure_translator_key"
)

# download the zip file from Azure Blob Storage
zip_file_contents = blob_service.get_blob_to_bytes(
    container_name="your_container_name",
    blob_name="your_blob_name"
)

# open the zip file
zip_file = zipfile.ZipFile(io.BytesIO(zip_file_contents))

# create a new zip file to store the translated files
translated_zip_file = zipfile.ZipFile("translated_files.zip", "w")

# translate the contents of each file to English
for file_name in zip_file.namelist():
    # read the contents of the file
    file_contents = zip_file.read(file_name)

    # translate the contents of the file to English
    translated_contents = translator_client.translate(
        text=file_contents,
        to_language="en"
    ).text

    # write the translated contents to a new file
    translated_file_name = f"{file_name}.en"
    with open(translated_file_name, "w") as file:
        file.write(translated_contents)

    # add the translated file to the translated zip file
    translated_zip_file.write(translated_file_name)

    # delete the translated file
    os.remove(translated_file_name)

# close the translated zip file
translated_zip_file.close()

# upload the translated zip file to Azure Blob Storage
blob_service.create_blob_from_path(
    container_name="your_translated_container_name",
    blob_name="your_translated_blob_name",
    file_path="translated_files.zip"
)

# delete the original zip file
blob_service.delete_blob(
    container_name="your_container_name",
    blob_name="your_blob_name"
)

