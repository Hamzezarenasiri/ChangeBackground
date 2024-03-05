from azure.storage.blob import BlobServiceClient, ContentSettings

from background_changer.settings import settings

# Define your Azure Storage account credentials
account_name = settings.AZURE_STORAGE_ACCOUNT_NAME
account_key = settings.AZURE_STORAGE_ACCOUNT_ACCESS_KEY

# Create a BlobServiceClient using account key


# Upload image to Azure Blob Storage
def upload_image_to_blob_storage(image_path, image_name, container_name, content_type):
    blob_service_client = BlobServiceClient(
        account_url=f"https://{account_name}.blob.core.windows.net",
        credential=account_key,
    )
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(image_name)
    if content_type:
        blob_client.set_http_headers(
            content_settings=ContentSettings(content_type=content_type),
        )
    with open(image_path, "rb") as data:
        blob_client.upload_blob(
            data,
        )

    blob_client = container_client.get_blob_client(image_name)
    return blob_client.url
