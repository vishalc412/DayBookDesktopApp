"""
Encryption Manager for Sensitive Financial Data
AES-256 encryption for savings, investments, and precious metals data
"""

import os
import base64
import json
from typing import Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend


class EncryptionManager:
    """
    Application-level encryption for sensitive financial data
    Uses AES-256 via Fernet (symmetric encryption)
    """

    def __init__(self):
        self._cipher: Optional[Fernet] = None
        self._key: Optional[bytes] = None

    def derive_key_from_password(
        self,
        password: str,
        salt: bytes,
        iterations: int = 100000
    ) -> bytes:
        """
        Derive encryption key from password using PBKDF2-HMAC-SHA256

        Args:
            password: Master password
            salt: Random salt (32 bytes)
            iterations: PBKDF2 iterations (default: 100,000)

        Returns:
            256-bit encryption key
        """
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            iterations=iterations,
            backend=default_backend()
        )

        key = kdf.derive(password.encode())
        return base64.urlsafe_b64encode(key)

    def initialize_cipher(self, encryption_key: bytes):
        """
        Initialize Fernet cipher with encryption key

        Args:
            encryption_key: 256-bit key (base64 encoded)
        """
        self._key = encryption_key
        self._cipher = Fernet(encryption_key)

    def encrypt_value(self, value: Any) -> str:
        """
        Encrypt a value (converts to JSON, then encrypts)

        Args:
            value: Any JSON-serializable value

        Returns:
            Base64-encoded encrypted string

        Raises:
            RuntimeError: If cipher not initialized
        """
        if self._cipher is None:
            raise RuntimeError("Encryption cipher not initialized. Call initialize_cipher first.")

        # Convert value to JSON string
        json_str = json.dumps(value)

        # Encrypt
        encrypted_bytes = self._cipher.encrypt(json_str.encode())

        # Return as base64 string
        return encrypted_bytes.decode()

    def decrypt_value(self, encrypted_str: str) -> Any:
        """
        Decrypt an encrypted string and parse JSON

        Args:
            encrypted_str: Base64-encoded encrypted string

        Returns:
            Decrypted and parsed value

        Raises:
            RuntimeError: If cipher not initialized
            cryptography.fernet.InvalidToken: If decryption fails (wrong key or corrupted data)
        """
        if self._cipher is None:
            raise RuntimeError("Encryption cipher not initialized. Call initialize_cipher first.")

        # Decrypt
        decrypted_bytes = self._cipher.decrypt(encrypted_str.encode())

        # Parse JSON
        return json.loads(decrypted_bytes.decode())

    def encrypt_dict(self, data: dict, keys_to_encrypt: list[str]) -> dict:
        """
        Encrypt specific keys in a dictionary

        Args:
            data: Dictionary with data
            keys_to_encrypt: List of keys to encrypt

        Returns:
            Dictionary with encrypted values
        """
        result = data.copy()

        for key in keys_to_encrypt:
            if key in result and result[key] is not None:
                result[key] = self.encrypt_value(result[key])

        return result

    def decrypt_dict(self, data: dict, keys_to_decrypt: list[str]) -> dict:
        """
        Decrypt specific keys in a dictionary

        Args:
            data: Dictionary with encrypted data
            keys_to_decrypt: List of keys to decrypt

        Returns:
            Dictionary with decrypted values
        """
        result = data.copy()

        for key in keys_to_decrypt:
            if key in result and result[key] is not None:
                try:
                    result[key] = self.decrypt_value(result[key])
                except Exception:
                    # If decryption fails, leave as is (might be unencrypted)
                    pass

        return result

    @staticmethod
    def generate_salt() -> bytes:
        """
        Generate random salt for key derivation

        Returns:
            32 bytes of random data
        """
        return os.urandom(32)

    @staticmethod
    def generate_key() -> bytes:
        """
        Generate random encryption key (for testing/development)

        Returns:
            Fernet-compatible encryption key
        """
        return Fernet.generate_key()

    def is_initialized(self) -> bool:
        """Check if cipher is initialized"""
        return self._cipher is not None


# Global encryption manager instance
encryption_manager = EncryptionManager()
