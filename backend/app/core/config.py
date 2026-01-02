"""
Application Configuration
Manages environment variables and settings
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseModel):
    """Application settings"""

    # Application
    APP_NAME: str = "DayBookKeeper by WarryWorks"
    APP_VERSION: str = "1.1"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # Server
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", 8765))  # Using uncommon port to avoid conflicts

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
