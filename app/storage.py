from fastapi import HTTPException
from azure.storage.blob import BlobServiceClient
import os, requests

def upload_blob(file_name, file_content):
    try:
        connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        if not connect_str:
            raise ValueError("Azure Storage connection string not found.")
        
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        blob_client = blob_service_client.get_blob_client(container="user-profile", blob=file_name)
        blob_client.upload_blob(file_content, overwrite=True)

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=404, detail="Roadmap not found")

async def download_blob(file_name, container):
    try:
        connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        if not connect_str:
            raise ValueError("Azure Storage connection string not found.")
        
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        blob_client = blob_service_client.get_blob_client(container, blob=file_name)
        blob_data = blob_client.download_blob().readall()
        return blob_data
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=404, detail="Roadmap not found")