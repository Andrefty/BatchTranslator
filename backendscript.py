import os
import zipfile
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

# Replace with your Azure Storage account name and key
account_name = "storagetexte"
account_key = "2x2yhYM0XmQ+nE25iuU02lDZ7yaHPZ3rL0nFbEJtdnf0kL/4LRgvookhRXgwq8ZivOzHVMBIcmy9+ASt3uO4Mg=="

# Create the BlobServiceClient object
service_client = BlobServiceClient(
    f"https://{account_name}.blob.core.windows.net",
    credential=account_key,
)

# Create the container client
container_name = "uploadzip"
container_client = ContainerClient(service_client, container_name)

# List the blobs in the container
blobs = container_client.list_blobs()

# Keep running while there are blobs left in the container
while blobs:
    # Iterate over the list of blobs
    for blob in blobs:
        # Do something with the blob, such as download it
        # Replace "local_path" with the desired local file path
        with open(blob.name, "wb") as f:
            blob_client = BlobClient(service_client, container_name, blob.name)
            f.write(blob_client.download_blob().readall())

        # Unzip the file
        with zipfile.ZipFile(blob.name, 'r') as zip_ref:
            zip_ref.extractall()

        # Delete the zip file
        os.remove(blob.name)

        # Delete the blob from storage
        blob_client.delete_blob()

    # List the blobs again to check if there are any left
    blobs = container_client.list_blobs()

print("All blobs have been processed and deleted.")
