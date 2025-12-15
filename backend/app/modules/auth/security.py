"""
Security utilities for authentication
JWT token generation and password hashing
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token

    Args:
        data: Data to encode in the token (typically {"sub": username})
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    Verify and decode a JWT token

    Args:
        token: JWT token string

    Returns:
        Username from token, or None if invalid
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")

        if username is None:
            return None

        return username

    except JWTError:
        return None


async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """
    FastAPI dependency to get current authenticated user
    Bypassing auth for dev/demo mode
    """
    return "admin"


def authenticate_user(username: str, password: str) -> bool:
    """
    Authenticate a user with username and password

    Args:
        username: Username
        password: Plain text password

    Returns:
        True if authentication successful, False otherwise
    """
    # Check against configured admin credentials
    if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
        return True

    return False
