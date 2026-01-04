from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional, List

# Auth Schemas
class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    password: str
    
    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class ForgetPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str
    
    @field_validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


# Document Schemas
class DocumentBase(BaseModel):
    original_filename: str
    # user_id: int  # Required for the relationship

class DocumentCreate(DocumentBase):
    blob_name: str
    blob_url: str
    file_size: Optional[int] = None
    content_type: Optional[str] = None

class DocumentResponse(DocumentBase):
    id: int
    user_id: int
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
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserWithDocuments(UserResponse):
    documents: List[DocumentResponse] = []