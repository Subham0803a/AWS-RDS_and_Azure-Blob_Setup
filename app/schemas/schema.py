from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# Document Schemas
class DocumentBase(BaseModel):
    original_filename: str
    user_id: int  # Required for the relationship

class DocumentCreate(DocumentBase):
    blob_name: str
    blob_url: str
    file_size: Optional[int] = None
    content_type: Optional[str] = None

class DocumentResponse(DocumentBase):
    id: int
    blob_name: str
    blob_url: str
    file_size: Optional[int]
    content_type: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    documents: List[DocumentResponse] = [] 
    
    class Config:
        from_attributes = True