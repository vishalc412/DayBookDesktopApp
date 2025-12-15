"""
Authentication Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional


class LoginRequest(BaseModel):
    """Login request schema"""
    username: str = Field(..., min_length=1, description="Username")
    password: str = Field(..., min_length=1, description="Password")


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"
    username: str
    expires_in: int  # Seconds


class TokenData(BaseModel):
    """Token payload data"""
    username: Optional[str] = None


class UserInfo(BaseModel):
    """User information"""
    username: str
    is_admin: bool = True
