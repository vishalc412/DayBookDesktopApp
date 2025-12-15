"""
Main entry point for Daybook Backend Server
FastAPI + Uvicorn Server
"""

import os
import sys
from dotenv import load_dotenv
import uvicorn

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.api import create_app

# Load environment variables
load_dotenv()

# Configuration
EXCEL_FILE_PATH = os.getenv('EXCEL_FILE_PATH', 'daybook.xlsx')
HOST = os.getenv('HOST', '127.0.0.1')
PORT = int(os.getenv('PORT', 5000))
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# Create FastAPI app
app = create_app(excel_file_path=EXCEL_FILE_PATH)

if __name__ == '__main__':
    print("=" * 60)
    print("Daybook Desktop Application - Backend Server v1.1")
    print("Powered by FastAPI + Uvicorn")
    print("=" * 60)
    print(f"Excel File: {EXCEL_FILE_PATH}")
    print(f"Server: http://{HOST}:{PORT}")
    print(f"API Docs: http://{HOST}:{PORT}/api/docs")
    print("=" * 60)

    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="info"
    )
