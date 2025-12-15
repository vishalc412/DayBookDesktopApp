"""
Authentication API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from .schemas import Token, LoginRequest, UserInfo
from .security import authenticate_user, create_access_token, get_current_user
from app.core.config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login endpoint to get access token

    Request body:
        username: admin
        password: admin

    Response:
        {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "token_type": "bearer",
            "username": "admin",
            "expires_in": 1800
        }
    """
    # Authenticate user
    if not authenticate_user(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": form_data.username,
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    }


@router.post("/login/json", response_model=Token)
async def login_json(login_data: LoginRequest):
    """
    Alternative login endpoint accepting JSON

    Request body:
        {
            "username": "admin",
            "password": "admin"
        }
    """
    if not authenticate_user(login_data.username, login_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": login_data.username},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": login_data.username,
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.get("/me", response_model=UserInfo)
async def get_current_user_info(current_user: str = Depends(get_current_user)):
    """
    Get current authenticated user information

    Headers:
        Authorization: Bearer <token>

    Response:
        {
            "username": "admin",
            "is_admin": true
        }
    """
    return {
        "username": current_user,
        "is_admin": True
    }


@router.post("/logout")
async def logout(current_user: str = Depends(get_current_user)):
    """
    Logout endpoint (client should delete token)

    Note: JWT tokens cannot be invalidated on server side.
    Client should delete the token to logout.
    """
    return {
        "success": True,
        "message": "Logged out successfully"
    }
