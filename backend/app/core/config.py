"""
Application Configuration
Manages environment variables and settings
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel


class Settings(BaseModel):
    """Application settings"""

    # Application
    APP_NAME: str = "BookKeep by WarryWorks"
    APP_VERSION: str = "1.1"
    DEBUG: bool = True

    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 5000

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./daybook.db"
    DATABASE_ECHO: bool = False

    # Excel
    EXCEL_FILE_PATH: str = "daybook.xlsx"
    EXCEL_AUTO_SYNC: bool = True

    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent

    # Authentication
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Default Admin Credentials (Change these!)
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin"


settings = Settings()
