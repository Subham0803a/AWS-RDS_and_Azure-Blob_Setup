from azure.storage.blob import BlobServiceClient, ContainerClient, ContentSettings
from dotenv import load_dotenv
import os
from typing import Optional
import io

load_dotenv()

class AzureBlobStorage:
    def __init__(self):
        self.connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        self.container_name = os.getenv('AZURE_CONTAINER_NAME')
        
        if not self.connection_string:
            raise ValueError("Azure Storage connection string not found in environment variables")
        
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self._get_or_create_container()
    
    def _get_or_create_container(self) -> ContainerClient:
        """Get container or create if it doesn't exist"""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            # Check if container exists
            container_client.get_container_properties()
            print(f"✅ Container '{self.container_name}' already exists")
        except Exception:
            # Create container if it doesn't exist
            container_client = self.blob_service_client.create_container(self.container_name)
            print(f"✅ Container '{self.container_name}' created successfully")
        
        return container_client
    
    def upload_file(self, file_data: bytes, blob_name: str, content_type: str = "application/octet-stream") -> str:
        """
        Upload file to Azure Blob Storage
        
        Args:
            file_data: File content as bytes
            blob_name: Name for the blob (file name in storage)
            content_type: MIME type of the file
            
        Returns:
            URL of the uploaded blob
        """
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            
            # Convert the string/dict into a ContentSettings object
            settings = ContentSettings(content_type=content_type)
            
            blob_client.upload_blob(
                file_data, 
                overwrite=True,
                content_settings=settings # Pass the object, not a dict
            )
            
            # Return the blob URL
            blob_url = blob_client.url
            print(f"✅ File uploaded successfully: {blob_name}")
            return blob_url
        except Exception as e:
            print(f"❌ Error uploading file: {e}")
            raise
    
    def download_file(self, blob_name: str) -> bytes:
        """
        Download file from Azure Blob Storage
        
        Args:
            blob_name: Name of the blob to download
            
        Returns:
            File content as bytes
        """
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_data = blob_client.download_blob()
            return blob_data.readall()
        except Exception as e:
            print(f"❌ Error downloading file: {e}")
            raise
    
    def delete_file(self, blob_name: str) -> bool:
        """
        Delete file from Azure Blob Storage
        
        Args:
            blob_name: Name of the blob to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_client.delete_blob()
            print(f"✅ File deleted successfully: {blob_name}")
            return True
        except Exception as e:
            print(f"❌ Error deleting file: {e}")
            return False
    
    def list_files(self, prefix: Optional[str] = None) -> list:
        """
        List all files in the container
        
        Args:
            prefix: Optional prefix to filter blobs
            
        Returns:
            List of blob names
        """
        try:
            blobs = self.container_client.list_blobs(name_starts_with=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            print(f"❌ Error listing files: {e}")
            raise
    
    def get_file_url(self, blob_name: str) -> str:
        """
        Get the URL of a blob
        
        Args:
            blob_name: Name of the blob
            
        Returns:
            URL of the blob
        """
        blob_client = self.container_client.get_blob_client(blob_name)
        return blob_client.url
    
    def file_exists(self, blob_name: str) -> bool:
        """
        Check if a file exists in the container
        
        Args:
            blob_name: Name of the blob to check
            
        Returns:
            True if exists, False otherwise
        """
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_client.get_blob_properties()
            return True
        except Exception:
            return False

# Create a singleton instance
azure_storage = AzureBlobStorage()

def get_azure_storage() -> AzureBlobStorage:
    """Dependency to get Azure Storage instance"""
    return azure_storage