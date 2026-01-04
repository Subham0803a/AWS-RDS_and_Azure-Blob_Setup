from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.models.model import User, Document
from app.schemas.schema import DocumentResponse
from app.database.connection import get_db
from app.database.azure_blob import get_azure_storage, AzureBlobStorage
from app.utils.dependencies import get_current_user
import uuid


router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    azure_storage: AzureBlobStorage = Depends(get_azure_storage)
):
    """Upload a document to Azure Blob Storage (Protected route)"""
    
    # Define allowed MIME types
    ALLOWED_TYPES = [
        "image/jpeg", 
        "image/png", 
        "image/gif", 
        "application/pdf",
        "application/msword", 
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file.content_type} is not supported."
        )
    
    try:
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File is too large (Max 10MB)")

        file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
        blob_name = f"{current_user.id}/{uuid.uuid4()}.{file_extension}"
        
        # Upload to Azure
        blob_url = azure_storage.upload_file(
            file_data=file_content,
            blob_name=blob_name,
            content_type=file.content_type or "application/octet-stream"
        )
        
        # Save to database
        new_document = Document(
            user_id=current_user.id,
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


@router.get("", response_model=List[DocumentResponse])
def get_my_documents(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all documents for the current user"""
    documents = db.query(Document).filter(
        Document.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific document"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document


@router.get("/{document_id}/download")
async def download_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    azure_storage: AzureBlobStorage = Depends(get_azure_storage)
):
    """Download a document"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
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
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    azure_storage: AzureBlobStorage = Depends(get_azure_storage)
):
    """Delete a document"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        azure_storage.delete_file(document.blob_name)
        db.delete(document)
        db.commit()
        
        return {"message": "Document deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
