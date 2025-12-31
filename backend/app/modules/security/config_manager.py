"""
Secure Configuration Manager
Manages .security_config file with encryption
"""

import os
import json
import base64
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from cryptography.fernet import Fernet
from pydantic import BaseModel


class SecurityConfig(BaseModel):
    """Security configuration model"""
    password_hash: str
    salt: str  # Hex-encoded salt for key derivation
    created_at: str
    last_password_change: str
    version: str = "2.0"
    security_questions: list[Dict[str, str]] = []
    settings: Dict[str, Any] = {
        "auto_lock_timeout": 900,  # 15 minutes
        "session_duration": 28800,  # 8 hours
        "failed_login_threshold": 5,
        "backup_enabled": True,
        "backup_frequency": "daily"
    }


class SecureConfigManager:
    """
    Manage secure configuration file

    The .security_config file stores:
    - Master password hash (bcrypt)
    - Salt for key derivation
    - Security questions (optional)
    - App settings
    - Audit timestamps

    Note: The file itself is encrypted with a machine-specific key
    for obfuscation (not user-password protection)
    """

    CONFIG_FILENAME = ".security_config"

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize config manager

        Args:
            config_dir: Directory to store config file (default: current directory)
        """
        self.config_dir = config_dir or Path.cwd()
        self.config_path = self.config_dir / self.CONFIG_FILENAME
        self._encryption_key = self._get_or_create_machine_key()

    def _get_or_create_machine_key(self) -> bytes:
        """
        Get or create machine-specific encryption key

        This key is used to obfuscate the config file (not for user data security).
        Real security comes from the master password.

        Returns:
            Fernet encryption key
        """
        key_file = self.config_dir / ".machine_key"

        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()

        # Generate new key
        key = Fernet.generate_key()

        # Save key
        with open(key_file, 'wb') as f:
            f.write(key)

        # Hide file on Unix-like systems
        if os.name != 'nt':
            os.chmod(key_file, 0o600)  # Read/write for owner only

        return key

    def config_exists(self) -> bool:
        """
        Check if security config file exists

        Returns:
            True if config exists (app has been set up)
        """
        return self.config_path.exists()

    def create_config(
        self,
        password_hash: str,
        salt: str,
        security_questions: Optional[list[Dict[str, str]]] = None
    ) -> SecurityConfig:
        """
        Create new security configuration (first-time setup)

        Args:
            password_hash: Bcrypt hash of master password
            salt: Hex-encoded salt for key derivation
            security_questions: Optional list of security questions

        Returns:
            Created SecurityConfig

        Raises:
            FileExistsError: If config already exists
        """
        if self.config_exists():
            raise FileExistsError(
                "Security configuration already exists. "
                "Use update_config to modify or delete .security_config first."
            )

        now = datetime.utcnow().isoformat()

        config = SecurityConfig(
            password_hash=password_hash,
            salt=salt,
            created_at=now,
            last_password_change=now,
            security_questions=security_questions or []
        )

        self._save_config(config)
        return config

    def load_config(self) -> SecurityConfig:
        """
        Load security configuration

        Returns:
            SecurityConfig

        Raises:
            FileNotFoundError: If config doesn't exist
        """
        if not self.config_exists():
            raise FileNotFoundError(
                "Security configuration not found. First-time setup required."
            )

        # Read encrypted config
        with open(self.config_path, 'rb') as f:
            encrypted_data = f.read()

        # Decrypt
        cipher = Fernet(self._encryption_key)
        decrypted_data = cipher.decrypt(encrypted_data)

        # Parse JSON
        config_dict = json.loads(decrypted_data.decode())

        return SecurityConfig(**config_dict)

    def update_config(self, updates: Dict[str, Any]) -> SecurityConfig:
        """
        Update security configuration

        Args:
            updates: Dictionary of fields to update

        Returns:
            Updated SecurityConfig
        """
        config = self.load_config()

        # Update fields
        for key, value in updates.items():
            if hasattr(config, key):
                setattr(config, key, value)

        self._save_config(config)
        return config

    def change_password(self, new_password_hash: str, new_salt: str) -> SecurityConfig:
        """
        Change master password

        Args:
            new_password_hash: New bcrypt hash
            new_salt: New hex-encoded salt

        Returns:
            Updated SecurityConfig
        """
        return self.update_config({
            "password_hash": new_password_hash,
            "salt": new_salt,
            "last_password_change": datetime.utcnow().isoformat()
        })

    def _save_config(self, config: SecurityConfig):
        """
        Save configuration to encrypted file

        Args:
            config: SecurityConfig to save
        """
        # Convert to JSON
        config_json = config.json()

        # Encrypt
        cipher = Fernet(self._encryption_key)
        encrypted_data = cipher.encrypt(config_json.encode())

        # Write to file
        with open(self.config_path, 'wb') as f:
            f.write(encrypted_data)

        # Set file permissions (read/write for owner only on Unix)
        if os.name != 'nt':
            os.chmod(self.config_path, 0o600)

    def backup_config(self, backup_path: Optional[Path] = None) -> Path:
        """
        Create backup of config file

        Args:
            backup_path: Optional custom backup path

        Returns:
            Path to backup file
        """
        if not self.config_exists():
            raise FileNotFoundError("No config to backup")

        if backup_path is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_path = self.config_dir / f".security_config.backup.{timestamp}"

        # Copy file
        with open(self.config_path, 'rb') as src:
            with open(backup_path, 'wb') as dst:
                dst.write(src.read())

        return backup_path

    def verify_integrity(self) -> bool:
        """
        Verify config file integrity

        Returns:
            True if config can be loaded and decrypted
        """
        try:
            self.load_config()
            return True
        except Exception:
            return False

    def reset_config(self):
        """
        Delete config file (USE WITH CAUTION - data will be lost!)

        This should only be used in development or if user explicitly
        requests a complete reset knowing they will lose all data.
        """
        if self.config_exists():
            self.config_path.unlink()

        # Also remove machine key
        key_file = self.config_dir / ".machine_key"
        if key_file.exists():
            key_file.unlink()


# Global config manager instance
secure_config_manager = SecureConfigManager()
