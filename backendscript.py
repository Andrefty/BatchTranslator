import io
import zipfile

from argos_translate import ArgosTranslate
from azure.storage.blob import BlockBlobService


# create a BlockBlobService instance
blob_service = BlockBlobService(
    account_name="your_storage_account_name",
    account_key="your_storage_account_key"
)

# create an ArgosTranslate instance
argos_translate = ArgosTranslate(
    api_key="your_argos_translate_api_key"
)

# download the zip file from Azure Blob Storage
zip_file_contents = blob_service.get_blob_to_bytes(
    container_name="your_container_name",
    blob_name="your_blob_name"
)

# open the zip file
zip_file = zipfile.ZipFile(io.BytesIO(zip_file_contents))

# extract the files from the zip file
zip_file.extractall()

# translate the contents of each file to English
for file_name in zip_file.namelist():
    # read the contents of the file
    file_contents = zip_file.read(file_name)

    # translate the contents of the file to English
    translated_contents = argos_translate.translate(
        text=file_contents,
        source_language="auto",
        target_language="en"
    )

    # write the translated contents to a new file
    with open(file_name, "w") as file:
        file.write(translated_contents)
