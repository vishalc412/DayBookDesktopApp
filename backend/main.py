"""
Main entry point for Daybook Backend Server v2.0
Enterprise-Grade Architecture with Double-Entry Accounting
"""

import os
import sys
import uvicorn

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.api_v2 import create_app
from app.core.config import settings

# Create FastAPI app
app = create_app()

if __name__ == "__main__":
    print("=" * 60)
    print(f"{settings.APP_NAME} v{settings.APP_VERSION}")
    print("Enterprise-Grade Double-Entry Accounting System")
    print("=" * 60)

    # Use configured port directly - NO dynamic allocation
    print(f"Database: {settings.DATABASE_URL}")
    print(f"Excel File: {settings.EXCEL_FILE_PATH}")
    print(f"Server: http://{settings.HOST}:{settings.PORT}")
    print(f"API Docs: http://{settings.HOST}:{settings.PORT}/api/docs")
    print("=" * 60)

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
