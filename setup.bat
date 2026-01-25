@echo off
echo ============================================================
echo DayBookKeeper v2.0 - Setup Script (Windows)
echo by WarryWorks
echo ============================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.9 or higher from https://www.python.org/
    pause
    exit /b 1
)

:: Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo [OK] Python and Node.js are installed
echo.

:: Setup Backend
echo ============================================================
echo Setting up Backend...
echo ============================================================
cd backend

:: Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
)

:: Activate virtual environment and install dependencies
echo Installing Python dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

echo [OK] Backend setup complete
cd ..
echo.

:: Setup Frontend
echo ============================================================
echo Setting up Frontend...
echo ============================================================
cd frontend

:: Install Node.js dependencies
echo Installing Node.js dependencies...
call npm install

echo [OK] Frontend setup complete
cd ..
echo.

:: Create .env files if they don't exist
if not exist backend\.env (
    echo Creating backend .env file...
    echo HOST=127.0.0.1> backend\.env
    echo PORT=8765>> backend\.env
    echo DEBUG=True>> backend\.env
)

if not exist frontend\.env (
    echo Creating frontend .env file...
    echo REACT_APP_API_URL=http://127.0.0.1:8765/api> frontend\.env
)

echo.
echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo To start the application, run: start.bat
echo.
pause
