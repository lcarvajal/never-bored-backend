from fastapi import HTTPException, status
from azure.storage.blob import BlobServiceClient
import os


def upload_blob(file_name, file_content):
    try:
        connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        if not connect_str:
            raise ValueError("Azure Storage connection string not found.")

        blob_service_client = BlobServiceClient.from_connection_string(
            connect_str)
        blob_client = blob_service_client.get_blob_client(
            container="user-profile", blob=file_name)
        blob_client.upload_blob(file_content, overwrite=True)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail="Azure connection not made.",
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not able to upload file.",
        )


async def download_blob(file_name, container):
    try:
        connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        if not connect_str:
            raise ValueError("Azure Storage connection string not found.")

        blob_service_client = BlobServiceClient.from_connection_string(
            connect_str)
        blob_client = blob_service_client.get_blob_client(
            container, blob=file_name)
        blob_data = blob_client.download_blob().readall()
        return blob_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail="Azure connection not made.",
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Not able to find {file_name}',
        )
