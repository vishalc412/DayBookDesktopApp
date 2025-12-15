@echo off
REM Daybook Desktop Application Startup Script for Windows
REM This script starts both backend and frontend services

echo ==========================================
echo Daybook Desktop Application v1.1
echo ==========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is not installed
    pause
    exit /b 1
)

REM Setup Python virtual environment
echo Setting up Python environment...
cd backend
if not exist "venv" (
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -q -r requirements.txt

REM Copy environment file if not exists
if not exist ".env" (
    copy .env.example .env
)

REM Start backend server in background
echo Starting backend server...
start /B python main.py

cd ..

REM Setup Node.js environment
echo Setting up Node.js environment...
cd frontend

REM Copy environment file if not exists
if not exist ".env" (
    copy .env.example .env
)

REM Install dependencies if needed
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)

REM Start Electron app
echo Starting Electron application...
call npm run electron-dev

pause
