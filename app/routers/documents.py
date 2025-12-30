from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from app.database.connection import get_db
from app.database.azure_blob import get_azure_storage, AzureBlobStorage
import uuid

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload", response_model=schemas.DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db),
    azure_storage: AzureBlobStorage = Depends(get_azure_storage)
):
    """Upload a document to Azure Blob Storage"""
    
    # Define allowed MIME types (Images and PDFs only)
    ALLOWED_TYPES = [
        "image/jpeg", 
        "image/png", 
        "image/gif", 
        "application/pdf",
        "application/msword", 
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document" # .docx
    ]

    # Check if the uploaded file type is allowed
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file.content_type} is not supported. Only images and documents are allowed."
        )

    # Verify user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        file_content = await file.read()
        file_size = len(file_content)
        
        # Limit file size (e.g., max 10MB)
        if file_size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File is too large (Max 10MB)")

        file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
        blob_name = f"{user_id}/{uuid.uuid4()}.{file_extension}"
        
        # Upload to Azure Blob Storage
        blob_url = azure_storage.upload_file(
            file_data=file_content,
            blob_name=blob_name,
            content_type=file.content_type or "application/octet-stream"
        )
        
        # Save document metadata to database
        new_document = models.Document(
            user_id=user_id,
            original_filename=file.filename,
            blob_name=blob_name,
            blob_url=blob_url,
            file_size=file_size,
            content_type=file.content_type
        )
        
        db.add(new_document)
        db.commit()
        db.refresh(new_document)
        return new_document
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("", response_model=List[schemas.DocumentResponse])
def get_documents(
    user_id: int = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get all documents or filter by user_id"""
    query = db.query(models.Document)
    
    if user_id:
        query = query.filter(models.Document.user_id == user_id)
    
    documents = query.offset(skip).limit(limit).all()
    return documents


@router.get("/{document_id}", response_model=schemas.DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get a specific document by ID"""
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.get("/{document_id}/download")
async def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    azure_storage: AzureBlobStorage = Depends(get_azure_storage)
):
    """Download a document from Azure Blob Storage"""
    
    # Get document metadata from database
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        # Download from Azure Blob Storage
        file_content = azure_storage.download_file(document.blob_name)
        
        from fastapi.responses import Response
        return Response(
            content=file_content,
            media_type=document.content_type or "application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={document.original_filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    azure_storage: AzureBlobStorage = Depends(get_azure_storage)
):
    """Delete a document from both database and Azure Blob Storage"""
    
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        # Delete from Azure Blob Storage
        azure_storage.delete_file(document.blob_name)
        
        # Delete from database
        db.delete(document)
        db.commit()
        
        return {"message": "Document deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")


@router.get("/{user_id}/list", response_model=List[schemas.DocumentResponse])
def list_user_documents(user_id: int, db: Session = Depends(get_db)):
    """List all documents for a specific user"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    documents = db.query(models.Document).filter(models.Document.user_id == user_id).all()
    return documents