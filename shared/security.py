"""
Security utilities for authentication and authorization.
"""
import os
from datetime import datetime, timedelta
from typing import Union, Any
import jwt
from passlib.context import CryptContext
import structlog

logger = structlog.get_logger()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing - fix bcrypt compatibility
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except Exception as e:
    logger.warning("Bcrypt configuration warning", error=str(e))
    # Fallback configuration
    pwd_context = CryptContext(schemes=["bcrypt"])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error("Password verification failed", error=str(e))
        return False

def get_password_hash(password: str) -> str:
    """Hash a password."""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error("Password hashing failed", error=str(e))
        raise

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error("Token creation failed", error=str(e))
        raise

def verify_token(token: str) -> Union[dict, None]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError as e:
        logger.error("Token verification failed", error=str(e))
        return None
    except Exception as e:
        logger.error("Token verification error", error=str(e))
        return None