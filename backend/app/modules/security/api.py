"""
Enhanced Authentication API with Master Password Support
Endpoints for setup, login, session management, and auto-lock
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

from .master_password import master_password_manager
from .encryption import encryption_manager
from .session_manager import session_manager, SessionSettings
from .config_manager import secure_config_manager


router = APIRouter(prefix="/security", tags=["Security"])


# Request/Response Models

class SetupRequest(BaseModel):
    """First-time setup request"""
    username: Optional[str] = "admin"
    password: str
    confirm_password: str
    security_questions: Optional[list[dict]] = None

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class LoginRequest(BaseModel):
    """Login request"""
    password: str


class UnlockRequest(BaseModel):
    """Unlock session request"""
    session_id: str
    password: str


class ChangePasswordRequest(BaseModel):
    """Change password request"""
    old_password: str
    new_password: str
    confirm_new_password: str

    @validator('confirm_new_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class PasswordStrengthRequest(BaseModel):
    """Password strength check request"""
    password: str


class AuthResponse(BaseModel):
    """Authentication response"""
    success: bool
    token: Optional[str] = None
    session_id: Optional[str] = None
    message: str
    expires_at: Optional[str] = None


class SessionStatusResponse(BaseModel):
    """Session status response"""
    active: bool
    is_locked: bool
    is_expired: bool
    should_warn: bool
    time_remaining_seconds: Optional[int] = None


class PasswordStrengthResponse(BaseModel):
    """Password strength response"""
    is_valid: bool
    score: int
    feedback: list[str]


# Endpoints

@router.get("/status")
async def get_setup_status():
    """
    Check if app has been set up (master password configured)

    Returns:
        dict with setup status
    """
    is_setup = secure_config_manager.config_exists()

    return {
        "is_setup": is_setup,
        "requires_setup": not is_setup,
        "version": "2.0"
    }


@router.post("/setup", response_model=AuthResponse)
async def setup_master_password(request: SetupRequest):
    """
    First-time setup: Create master password

    This endpoint should only work if no config exists.

    Args:
        request: SetupRequest with password and optional security questions

    Returns:
        AuthResponse with success status

    Raises:
        HTTPException 400: If setup already completed or password validation fails
    """
    # Check if already set up
    if secure_config_manager.config_exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Master password already configured. Use change-password to update."
        )

    # Validate password strength
    strength = master_password_manager.validate_password_strength(request.password)
    if not strength.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password does not meet requirements: {', '.join(strength.feedback)}"
        )

    try:
        # Hash password and get salt
        password_hash, salt = master_password_manager.hash_password(request.password)

        # Process security questions if provided
        security_questions = []
        if request.security_questions:
            for sq in request.security_questions:
                security_questions.append({
                    "question": sq["question"],
                    "answer_hash": master_password_manager.hash_security_answer(sq["answer"])
                })

        # Create config
        config = secure_config_manager.create_config(
            password_hash=password_hash,
            salt=salt,
            security_questions=security_questions
        )

        # Initialize encryption with derived key
        salt_bytes = bytes.fromhex(salt)
        encryption_key = encryption_manager.derive_key_from_password(
            request.password,
            salt_bytes
        )
        encryption_manager.initialize_cipher(encryption_key)

        # Create initial session
        token = session_manager.create_session({"username": request.username or "admin"})

        # Extract session ID from token
        payload = session_manager.verify_token(token)
        session_id = payload.get("session_id") if payload else None

        return AuthResponse(
            success=True,
            token=token,
            session_id=session_id,
            message="Master password configured successfully. Your data is now secure.",
            expires_at=datetime.fromtimestamp(payload["exp"]).isoformat() if payload else None
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Setup failed: {str(e)}"
        )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Login with master password

    Args:
        request: LoginRequest with password

    Returns:
        AuthResponse with JWT token

    Raises:
        HTTPException 401: If password incorrect
        HTTPException 423: If locked out due to failed attempts
    """
    # Check if setup completed
    if not secure_config_manager.config_exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Setup not completed. Please complete first-time setup."
        )

    # Check if locked out
    is_locked, seconds_remaining = master_password_manager.is_locked_out()
    if is_locked:
        minutes_remaining = seconds_remaining // 60
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Too many failed attempts. Try again in {minutes_remaining} minute(s)."
        )

    try:
        # Load config
        config = secure_config_manager.load_config()

        # Verify password
        if not master_password_manager.verify_password(request.password, config.password_hash):
            # Record failed attempt
            master_password_manager.record_failed_attempt()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password"
            )

        # Reset failed attempts
        master_password_manager.reset_failed_attempts()

        # Initialize encryption
        salt_bytes = bytes.fromhex(config.salt)
        encryption_key = encryption_manager.derive_key_from_password(
            request.password,
            salt_bytes
        )
        encryption_manager.initialize_cipher(encryption_key)

        # Create session
        token = session_manager.create_session(
            {"username": "admin"},
            SessionSettings(**config.settings)
        )

        # Extract session info
        payload = session_manager.verify_token(token)
        session_id = payload.get("session_id") if payload else None

        return AuthResponse(
            success=True,
            token=token,
            session_id=session_id,
            message="Login successful",
            expires_at=datetime.fromtimestamp(payload["exp"]).isoformat() if payload else None
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/verify-token")
async def verify_token(token: str):
    """
    Verify JWT token and return session status

    Args:
        token: JWT token string

    Returns:
        Session information
    """
    payload = session_manager.verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    session_id = payload.get("session_id")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )

    session_status = session_manager.get_session_status(session_id)

    return {
        "valid": True,
        "username": payload.get("sub"),
        "session_status": session_status
    }


@router.post("/logout")
async def logout(session_id: str):
    """
    Logout and destroy session

    Args:
        session_id: Session ID to destroy

    Returns:
        Success message
    """
    session_manager.destroy_session(session_id)

    return {
        "success": True,
        "message": "Logged out successfully"
    }


@router.post("/lock")
async def lock_session(session_id: str):
    """
    Manually lock current session

    Args:
        session_id: Session ID to lock

    Returns:
        Success message
    """
    success = session_manager.lock_session(session_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    return {
        "success": True,
        "locked": True,
        "message": "Session locked successfully"
    }


@router.post("/unlock", response_model=AuthResponse)
async def unlock_session(request: UnlockRequest):
    """
    Unlock locked session with password

    Args:
        request: UnlockRequest with session_id and password

    Returns:
        AuthResponse with new token
    """
    # Load config and verify password
    config = secure_config_manager.load_config()

    password_verified = master_password_manager.verify_password(
        request.password,
        config.password_hash
    )

    if not password_verified:
        master_password_manager.record_failed_attempt()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    # Reset failed attempts
    master_password_manager.reset_failed_attempts()

    # Unlock session
    success = session_manager.unlock_session(request.session_id, password_verified)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to unlock session. It may have expired."
        )

    # Re-initialize encryption
    salt_bytes = bytes.fromhex(config.salt)
    encryption_key = encryption_manager.derive_key_from_password(
        request.password,
        salt_bytes
    )
    encryption_manager.initialize_cipher(encryption_key)

    # Create new token
    token = session_manager.create_session({"username": "admin"})
    payload = session_manager.verify_token(token)

    return AuthResponse(
        success=True,
        token=token,
        session_id=request.session_id,
        message="Session unlocked successfully",
        expires_at=datetime.fromtimestamp(payload["exp"]).isoformat() if payload else None
    )


@router.put("/change-password", response_model=AuthResponse)
async def change_password(request: ChangePasswordRequest):
    """
    Change master password

    Args:
        request: ChangePasswordRequest with old and new passwords

    Returns:
        AuthResponse with new token

    Raises:
        HTTPException 401: If old password incorrect
        HTTPException 400: If new password invalid
    """
    # Load config
    config = secure_config_manager.load_config()

    # Verify old password
    if not master_password_manager.verify_password(request.old_password, config.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )

    # Validate new password strength
    strength = master_password_manager.validate_password_strength(request.new_password)
    if not strength.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"New password does not meet requirements: {', '.join(strength.feedback)}"
        )

    try:
        # Hash new password
        new_hash, new_salt = master_password_manager.hash_password(request.new_password)

        # Update config
        secure_config_manager.change_password(new_hash, new_salt)

        # Re-initialize encryption with new password
        salt_bytes = bytes.fromhex(new_salt)
        encryption_key = encryption_manager.derive_key_from_password(
            request.new_password,
            salt_bytes
        )
        encryption_manager.initialize_cipher(encryption_key)

        # Create new session
        token = session_manager.create_session({"username": "admin"})
        payload = session_manager.verify_token(token)

        return AuthResponse(
            success=True,
            token=token,
            session_id=payload.get("session_id") if payload else None,
            message="Password changed successfully",
            expires_at=datetime.fromtimestamp(payload["exp"]).isoformat() if payload else None
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password change failed: {str(e)}"
        )


@router.post("/check-password-strength", response_model=PasswordStrengthResponse)
async def check_password_strength(request: PasswordStrengthRequest):
    """
    Check password strength without storing it

    Args:
        request: PasswordStrengthRequest with password to check

    Returns:
        PasswordStrengthResponse with validation results
    """
    strength = master_password_manager.validate_password_strength(request.password)

    return PasswordStrengthResponse(
        is_valid=strength.is_valid,
        score=strength.score,
        feedback=strength.feedback
    )


@router.get("/session/{session_id}/status", response_model=SessionStatusResponse)
async def get_session_status(session_id: str):
    """
    Get detailed session status (for auto-lock monitoring)

    Args:
        session_id: Session ID

    Returns:
        SessionStatusResponse
    """
    status_dict = session_manager.get_session_status(session_id)

    if not status_dict.get("exists"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Determine if should show warning (< 5 minutes remaining)
    time_until_lock = status_dict.get("time_until_lock_seconds", 0)
    should_warn = 0 < time_until_lock < 300  # 5 minutes

    return SessionStatusResponse(
        active=not status_dict["is_expired"],
        is_locked=status_dict["is_locked"],
        is_expired=status_dict["is_expired"],
        should_warn=should_warn,
        time_remaining_seconds=time_until_lock
    )


@router.post("/session/{session_id}/activity")
async def update_session_activity(session_id: str):
    """
    Update last activity timestamp (called by frontend on user interaction)

    Args:
        session_id: Session ID

    Returns:
        Success message
    """
    success = session_manager.update_activity(session_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    return {
        "success": True,
        "message": "Activity updated"
    }
