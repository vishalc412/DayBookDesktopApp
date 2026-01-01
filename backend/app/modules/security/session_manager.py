"""
Session Manager with Auto-Lock Support
JWT-based session management with inactivity tracking
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.config import settings


class SessionSettings(BaseModel):
    """Session settings"""
    auto_lock_timeout: int = 900  # 15 minutes in seconds
    session_duration: int = 28800  # 8 hours in seconds
    show_timer: bool = True
    lock_on_minimize: bool = False


class SessionInfo(BaseModel):
    """Session information"""
    session_id: str
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    is_locked: bool
    settings: SessionSettings


class SessionManager:
    """
    Session Management with Auto-Lock

    Features:
    - JWT-based session tokens
    - Inactivity tracking
    - Auto-lock on timeout
    - Manual lock/unlock
    - Session expiration
    """

    def __init__(self):
        self.sessions: Dict[str, SessionInfo] = {}
        self.locked_sessions: Dict[str, SessionInfo] = {}

    def create_session(
        self,
        user_data: dict,
        settings_override: Optional[SessionSettings] = None
    ) -> str:
        """
        Create new session and return JWT token

        Args:
            user_data: User data to encode in token
            settings_override: Optional custom session settings

        Returns:
            JWT token string
        """
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()

        session_settings = settings_override or SessionSettings()

        # Create session info
        session_info = SessionInfo(
            session_id=session_id,
            created_at=now,
            expires_at=now + timedelta(seconds=session_settings.session_duration),
            last_activity=now,
            is_locked=False,
            settings=session_settings
        )

        # Store session
        self.sessions[session_id] = session_info

        # Create JWT token
        token_data = {
            "sub": user_data.get("username", "admin"),
            "session_id": session_id,
            "exp": session_info.expires_at,
            "iat": now,
            **user_data
        }

        token = jwt.encode(
            token_data,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        return token

    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify JWT token and return payload

        Args:
            token: JWT token string

        Returns:
            Token payload or None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError:
            return None

    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """
        Get session info by ID

        Args:
            session_id: Session ID

        Returns:
            SessionInfo or None
        """
        return self.sessions.get(session_id)

    def update_activity(self, session_id: str) -> bool:
        """
        Update last activity timestamp for session

        Args:
            session_id: Session ID

        Returns:
            True if updated, False if session not found
        """
        session = self.sessions.get(session_id)
        if not session:
            return False

        session.last_activity = datetime.utcnow()
        return True

    def check_inactivity(self, session_id: str) -> bool:
        """
        Check if session has exceeded inactivity timeout

        Args:
            session_id: Session ID

        Returns:
            True if inactive (should auto-lock), False otherwise
        """
        session = self.sessions.get(session_id)
        if not session:
            return True  # Non-existent session is considered inactive

        now = datetime.utcnow()
        inactive_duration = (now - session.last_activity).total_seconds()

        return inactive_duration > session.settings.auto_lock_timeout

    def is_session_expired(self, session_id: str) -> bool:
        """
        Check if session has expired

        Args:
            session_id: Session ID

        Returns:
            True if expired
        """
        session = self.sessions.get(session_id)
        if not session:
            return True

        return datetime.utcnow() > session.expires_at

    def lock_session(self, session_id: str) -> bool:
        """
        Lock a session (due to inactivity or manual lock)

        Args:
            session_id: Session ID

        Returns:
            True if locked, False if session not found
        """
        session = self.sessions.get(session_id)
        if not session:
            return False

        session.is_locked = True
        self.locked_sessions[session_id] = session
        return True

    def unlock_session(self, session_id: str, password_verified: bool) -> bool:
        """
        Unlock a locked session (requires password verification)

        Args:
            session_id: Session ID
            password_verified: Whether password was verified

        Returns:
            True if unlocked, False otherwise
        """
        if not password_verified:
            return False

        session = self.locked_sessions.get(session_id)
        if not session:
            return False

        # Check if session expired while locked
        if self.is_session_expired(session_id):
            self.destroy_session(session_id)
            return False

        # Unlock session
        session.is_locked = False
        session.last_activity = datetime.utcnow()
        self.locked_sessions.pop(session_id, None)

        return True

    def destroy_session(self, session_id: str):
        """
        Completely destroy a session (logout)

        Args:
            session_id: Session ID
        """
        self.sessions.pop(session_id, None)
        self.locked_sessions.pop(session_id, None)

    def get_session_status(self, session_id: str) -> Dict:
        """
        Get detailed session status

        Args:
            session_id: Session ID

        Returns:
            Dictionary with session status
        """
        session = self.sessions.get(session_id)
        if not session:
            return {
                "exists": False,
                "is_locked": True,
                "is_expired": True
            }

        now = datetime.utcnow()
        time_since_activity = (now - session.last_activity).total_seconds()
        time_until_lock = max(0, session.settings.auto_lock_timeout - time_since_activity)
        time_until_expiration = (session.expires_at - now).total_seconds()

        return {
            "exists": True,
            "session_id": session.session_id,
            "is_locked": session.is_locked,
            "is_expired": self.is_session_expired(session_id),
            "should_auto_lock": self.check_inactivity(session_id),
            "time_since_activity_seconds": int(time_since_activity),
            "time_until_lock_seconds": int(time_until_lock),
            "time_until_expiration_seconds": int(time_until_expiration),
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "expires_at": session.expires_at.isoformat(),
            "settings": session.settings.dict()
        }

    def cleanup_expired_sessions(self):
        """
        Remove expired sessions (should be called periodically)
        """
        now = datetime.utcnow()
        expired_ids = [
            sid for sid, session in self.sessions.items()
            if now > session.expires_at
        ]

        for sid in expired_ids:
            self.destroy_session(sid)

    def get_all_active_sessions(self) -> list[Dict]:
        """
        Get all active sessions (for admin purposes)

        Returns:
            List of session status dictionaries
        """
        return [
            self.get_session_status(sid)
            for sid in self.sessions.keys()
        ]


# Global session manager instance
session_manager = SessionManager()
