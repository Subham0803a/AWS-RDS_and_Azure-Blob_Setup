from fastapi import APIRouter, Depends, HTTPException, status, Header
from typing import Optional
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.model import User
from app.schemas.schema import (
    SignupRequest, VerifyOTPRequest, LoginRequest, TokenResponse,
    ForgetPasswordRequest, ResetPasswordRequest, UserResponse
)
from app.utils.auth_utils import hash_password, verify_password, create_access_token
from app.utils.dependencies import get_current_user
from app.services.otp_service import generate_otp, get_otp_expiry, is_otp_valid
from app.services.email_service import get_email_service, EmailService
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    db: Session = Depends(get_db),
    email_service: EmailService = Depends(get_email_service)
):
    """Register a new user and send OTP for verification"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == request.email) | (User.username == request.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Generate OTP
    otp = generate_otp()
    otp_expiry = get_otp_expiry()
    
    # Create new user
    new_user = User(
        username=request.username,
        email=request.email,
        full_name=request.full_name,
        hashed_password=hash_password(request.password),
        otp_code=otp,
        otp_expiry=otp_expiry,
        is_active=False,
        is_verified=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Send OTP email
    await email_service.send_otp_email(request.email, otp, request.full_name)
    
    return {
        "message": "User registered successfully. Please check your email for OTP verification.",
        "email": request.email
    }


@router.post("/verify-otp")
async def verify_otp(
    request: VerifyOTPRequest,
    db: Session = Depends(get_db),
    email_service: EmailService = Depends(get_email_service)
):
    """Verify OTP and activate user account"""
    
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already verified"
        )
    
    # Check OTP validity
    if not user.otp_code or not user.otp_expiry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No OTP found for this user"
        )
    
    if not is_otp_valid(user.otp_expiry):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired. Please request a new one."
        )
    
    if user.otp_code != request.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )
    
    # Activate user
    user.is_verified = True
    user.is_active = True
    user.otp_code = None
    user.otp_expiry = None
    db.commit()
    
    # Send welcome email
    await email_service.send_welcome_email(user.email, user.full_name)
    
    return {
        "message": "Account verified successfully! Welcome email sent.",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name
        }
    }


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account not verified. Please verify your email first."
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    # Create JWT token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/forget-password")
async def forget_password(
    request: ForgetPasswordRequest,
    db: Session = Depends(get_db),
    email_service: EmailService = Depends(get_email_service)
):
    """Send OTP for password reset"""
    
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email"
        )
    
    # Generate OTP
    otp = generate_otp()
    otp_expiry = get_otp_expiry()
    
    user.otp_code = otp
    user.otp_expiry = otp_expiry
    db.commit()
    
    # Send OTP email
    await email_service.send_otp_email(request.email, otp, user.full_name)
    
    return {
        "message": "OTP sent to your email for password reset",
        "email": request.email
    }


@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password using OTP"""
    
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check OTP validity
    if not user.otp_code or not user.otp_expiry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No OTP found. Please request password reset first."
        )
    
    if not is_otp_valid(user.otp_expiry):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired. Please request a new one."
        )
    
    if user.otp_code != request.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )
    
    # Update password
    user.hashed_password = hash_password(request.new_password)
    user.otp_code = None
    user.otp_expiry = None
    db.commit()
    
    return {"message": "Password reset successfully. You can now login with your new password."}


@router.post("/resend-otp")
async def resend_otp(
    request: ForgetPasswordRequest,
    db: Session = Depends(get_db),
    email_service: EmailService = Depends(get_email_service)
):
    """Resend OTP for verification or password reset"""
    
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Generate new OTP
    otp = generate_otp()
    otp_expiry = get_otp_expiry()
    
    user.otp_code = otp
    user.otp_expiry = otp_expiry
    db.commit()
    
    # Send OTP email
    await email_service.send_otp_email(request.email, otp, user.full_name)
    
    return {
        "message": "New OTP sent to your email",
        "email": request.email
    }
    
@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """Logout user (client-side token deletion)"""
    return {
        "message": "Logged out successfully. Please delete the token from client side.",
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email
        }
    }
    
@router.get("/debug-auth-header")
def debug_auth_header(authorization: Optional[str] = Header(None)):
    """Debug endpoint to see what authorization header is received"""
    if not authorization:
        return {"error": "No Authorization header received"}
    
    parts = authorization.split()
    
    return {
        "full_header": authorization,
        "header_length": len(authorization),
        "parts_count": len(parts),
        "scheme": parts[0] if len(parts) > 0 else None,
        "token_preview": parts[1][:50] + "..." if len(parts) > 1 else None,
        "token_segment_count": len(parts[1].split('.')) if len(parts) > 1 else 0,
        "expected_segments": 3
    }