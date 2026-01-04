import random
import string
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

load_dotenv()

OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", 10))


def generate_otp() -> str:
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))


def get_otp_expiry() -> datetime:
    """Get OTP expiry time (timezone-aware)"""
    return datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES)


def is_otp_valid(otp_expiry: datetime) -> bool:
    """Check if OTP is still valid"""
    # Make current time timezone-aware
    current_time = datetime.now(timezone.utc)
    
    # If otp_expiry is naive, make it aware
    if otp_expiry.tzinfo is None:
        otp_expiry = otp_expiry.replace(tzinfo=timezone.utc)
    
    return current_time < otp_expiry
