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
    APP_NAME: str = "Daybook Desktop Application"
    APP_VERSION: str = "2.0"
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


settings = Settings()
