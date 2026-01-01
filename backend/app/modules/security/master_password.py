"""
Master Password Manager
Enhanced password system with strength validation and security questions
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Tuple
from passlib.context import CryptContext
from pydantic import BaseModel, validator


# Password hashing context (bcrypt with cost factor 12)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


class PasswordStrength(BaseModel):
    """Password strength validation result"""
    is_valid: bool
    score: int  # 0-100
    feedback: list[str]


class SecurityQuestion(BaseModel):
    """Security question for password recovery"""
    question: str
    answer_hash: str


class MasterPasswordManager:
    """
    Master Password Management System
    """

    # Password requirements
    MIN_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True
    SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    # Failed login tracking
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 5

    def __init__(self):
        self.failed_attempts: dict[str, list[datetime]] = {}

    def validate_password_strength(self, password: str) -> PasswordStrength:
        """
        Validate password strength according to security requirements

        Requirements:
        - Minimum 12 characters
        - At least 1 uppercase letter
        - At least 1 lowercase letter
        - At least 1 digit
        - At least 1 special character

        Args:
            password: Password to validate

        Returns:
            PasswordStrength with validation results
        """
        feedback = []
        score = 0

        # Length check
        if len(password) < self.MIN_LENGTH:
            feedback.append(f"Password must be at least {self.MIN_LENGTH} characters")
        else:
            score += 20

        # Uppercase check
        if self.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            feedback.append("Password must include at least one uppercase letter")
        elif re.search(r'[A-Z]', password):
            score += 20

        # Lowercase check
        if self.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            feedback.append("Password must include at least one lowercase letter")
        elif re.search(r'[a-z]', password):
            score += 20

        # Digit check
        if self.REQUIRE_DIGIT and not re.search(r'\d', password):
            feedback.append("Password must include at least one digit")
        elif re.search(r'\d', password):
            score += 20

        # Special character check
        if self.REQUIRE_SPECIAL:
            special_char_pattern = f"[{re.escape(self.SPECIAL_CHARS)}]"
            if not re.search(special_char_pattern, password):
                feedback.append(f"Password must include at least one special character ({self.SPECIAL_CHARS})")
            elif re.search(special_char_pattern, password):
                score += 20

        # Bonus for longer passwords
        if len(password) >= 16:
            score += 10
        if len(password) >= 20:
            score += 10

        # Check for common patterns
        if re.search(r'(.)\1{2,}', password):  # Repeated characters
            score -= 10
            feedback.append("Avoid repeated characters")

        if re.search(r'(123|234|345|456|567|678|789)', password):
            score -= 10
            feedback.append("Avoid sequential numbers")

        if re.search(r'(abc|bcd|cde|def|efg)', password, re.IGNORECASE):
            score -= 10
            feedback.append("Avoid sequential letters")

        # Ensure score is in valid range
        score = max(0, min(100, score))

        is_valid = len(feedback) == 0 or all(
            "must" not in fb for fb in feedback
        )

        return PasswordStrength(
            is_valid=is_valid,
            score=score,
            feedback=feedback
        )

    def hash_password(self, password: str) -> Tuple[str, str]:
        """
        Hash password with bcrypt

        Args:
            password: Plain text password

        Returns:
            Tuple of (password_hash, salt) - Note: bcrypt includes salt in hash
        """
        # Validate password strength first
        strength = self.validate_password_strength(password)
        if not strength.is_valid:
            raise ValueError(f"Password does not meet requirements: {', '.join(strength.feedback)}")

        # Hash password (bcrypt automatically handles salt)
        password_hash = pwd_context.hash(password)

        # For compatibility, we still return a separate salt
        # In bcrypt, the salt is embedded in the hash, but we generate
        # a separate salt for key derivation
        from .encryption import EncryptionManager
        salt = EncryptionManager.generate_salt()

        return password_hash, salt.hex()

    def verify_password(
        self,
        plain_password: str,
        hashed_password: str
    ) -> bool:
        """
        Verify password against hash

        Args:
            plain_password: Plain text password
            hashed_password: Bcrypt hash

        Returns:
            True if password matches, False otherwise
        """
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            return False

    def record_failed_attempt(self, identifier: str = "default"):
        """
        Record a failed login attempt

        Args:
            identifier: User identifier (default: "default" for single-user system)
        """
        now = datetime.utcnow()

        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = []

        # Add current attempt
        self.failed_attempts[identifier].append(now)

        # Clean up old attempts (older than lockout duration)
        cutoff = now - timedelta(minutes=self.LOCKOUT_DURATION_MINUTES * 2)
        self.failed_attempts[identifier] = [
            attempt for attempt in self.failed_attempts[identifier]
            if attempt > cutoff
        ]

    def is_locked_out(self, identifier: str = "default") -> Tuple[bool, Optional[int]]:
        """
        Check if user is locked out due to failed attempts

        Args:
            identifier: User identifier

        Returns:
            Tuple of (is_locked, seconds_remaining)
        """
        if identifier not in self.failed_attempts:
            return False, None

        now = datetime.utcnow()
        recent_attempts = [
            attempt for attempt in self.failed_attempts[identifier]
            if attempt > now - timedelta(minutes=self.LOCKOUT_DURATION_MINUTES)
        ]

        if len(recent_attempts) >= self.MAX_FAILED_ATTEMPTS:
            # Calculate time until lockout expires
            oldest_recent = min(recent_attempts)
            lockout_expires = oldest_recent + timedelta(minutes=self.LOCKOUT_DURATION_MINUTES)
            seconds_remaining = int((lockout_expires - now).total_seconds())

            return True, max(0, seconds_remaining)

        return False, None

    def reset_failed_attempts(self, identifier: str = "default"):
        """
        Reset failed attempts (call on successful login)

        Args:
            identifier: User identifier
        """
        if identifier in self.failed_attempts:
            self.failed_attempts[identifier] = []

    def hash_security_answer(self, answer: str) -> str:
        """
        Hash security question answer

        Args:
            answer: Plain text answer (normalized to lowercase, stripped)

        Returns:
            Bcrypt hash of answer
        """
        normalized = answer.strip().lower()
        return pwd_context.hash(normalized)

    def verify_security_answer(self, answer: str, answer_hash: str) -> bool:
        """
        Verify security question answer

        Args:
            answer: Plain text answer
            answer_hash: Bcrypt hash

        Returns:
            True if answer matches
        """
        normalized = answer.strip().lower()
        try:
            return pwd_context.verify(normalized, answer_hash)
        except Exception:
            return False


# Global master password manager instance
master_password_manager = MasterPasswordManager()
