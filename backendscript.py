import os
import zipfile
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

# workpath=

# Create the BlobServiceClient object
service_client = BlobServiceClient.from_connection_string(
                "***REMOVED***")

# Create the container client
container_name = "uploadzip"
container_client = service_client.get_container_client(container_name)
# List the blobs in the container
blobs = container_client.list_blobs()

# Keep running while there are blobs left in the container
while blobs:
    # Iterate over the list of blobs
    for blob in blobs:
        # Do something with the blob, such as download it
        # Replace "local_path" with the desired local file path
        with open(blob.name, "wb") as f:
            blob_client = container_client.get_blob_client(blob.name)
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
