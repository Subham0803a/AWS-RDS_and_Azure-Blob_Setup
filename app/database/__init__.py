# app/database/__init__.py
from app.database.azure_blob import AzureBlobStorage, get_azure_storage
from app.database.connection import get_db, test_connection