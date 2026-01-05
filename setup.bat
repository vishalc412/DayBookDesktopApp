@echo off
REM DayBook Keeper - Cross-Platform Setup Script (Windows)
REM This script installs all dependencies and prepares the project for first run

setlocal enabledelayedexpansion

echo ==========================================
echo DayBook Keeper - Complete Setup
echo ==========================================
echo.

REM Step 1: Check Python
echo ==========================================
echo Step 1: Checking Python Installation
echo ==========================================

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python 3 is not installed or not in PATH
    echo.
    echo Please install Python 3.11 or higher from:
    echo   https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found

REM Step 2: Check Node.js
echo.
echo ==========================================
echo Step 2: Checking Node.js Installation
echo ==========================================

where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo.
    echo Please install Node.js 18 or higher from:
    echo   https://nodejs.org/
    pause
    exit /b 1
)

for /f "tokens=1" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
echo [OK] Node.js %NODE_VERSION% found

where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] npm is not installed
    pause
    exit /b 1
)

for /f "tokens=1" %%i in ('npm --version 2^>^&1') do set NPM_VERSION=%%i
echo [OK] npm %NPM_VERSION% found

REM Step 3: Setup Backend
echo.
echo ==========================================
echo Step 3: Setting Up Backend
echo ==========================================

cd backend

REM Create virtual environment
if exist "venv" (
    echo [WARNING] Virtual environment already exists
    set /p RECREATE="Do you want to recreate it? (y/N): "
    if /i "!RECREATE!"=="y" (
        echo Removing old virtual environment...
        rmdir /s /q venv
        echo Creating new Python virtual environment...
        python -m venv venv
    )
) else (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --quiet --upgrade pip

REM Install dependencies
echo Installing Python dependencies (this may take a few minutes)...
pip install -r requirements.txt

REM Mark as installed
type nul > venv\.installed

echo [OK] Backend dependencies installed

REM Create .env file
if not exist ".env" (
    if exist ".env.example" (
        echo Creating backend .env from template...
        copy .env.example .env >nul
    ) else (
        echo Creating backend .env with defaults...
        (
            echo HOST=127.0.0.1
            echo PORT=8765
            echo DEBUG=True
            echo EXCEL_FILE_PATH=daybook.xlsx
            echo ADMIN_USERNAME=admin
            echo ADMIN_PASSWORD=admin
        ) > .env
    )
    echo [OK] Backend .env created
) else (
    echo [OK] Backend .env already exists
)

REM Check if database exists
if not exist "daybook.db" (
    echo [NOTE] Database will be created on first run
)

cd ..

REM Step 4: Setup Frontend
echo.
echo ==========================================
echo Step 4: Setting Up Frontend
echo ==========================================

cd frontend

REM Install node modules
if exist "node_modules" (
    echo [WARNING] Node modules already exist
    set /p REINSTALL="Do you want to reinstall them? (y/N): "
    if /i "!REINSTALL!"=="y" (
        echo Removing old node_modules...
        rmdir /s /q node_modules
        if exist package-lock.json del package-lock.json
        echo Installing Node dependencies (this may take several minutes)...
        call npm install
    ) else (
        echo [OK] Using existing node_modules
    )
) else (
    echo Installing Node dependencies (this may take several minutes)...
    call npm install
)

echo [OK] Frontend dependencies installed

REM Create .env file
if not exist ".env" (
    echo Creating frontend .env...
    echo REACT_APP_API_URL=http://127.0.0.1:8765/api> .env
    echo [OK] Frontend .env created
) else (
    echo [OK] Frontend .env already exists
)

cd ..

REM Step 5: Verify installation
echo.
echo ==========================================
echo Step 5: Verifying Installation
echo ==========================================

REM Check backend dependencies
echo|set /p="Backend dependencies: "
if exist "backend\venv\.installed" (
    echo [OK]
) else (
    echo [FAILED]
)

REM Check frontend dependencies
echo|set /p="Frontend dependencies: "
if exist "frontend\node_modules" (
    echo [OK]
) else (
    echo [FAILED]
)

REM Check .env files
echo|set /p="Backend .env: "
if exist "backend\.env" (
    echo [OK]
) else (
    echo [FAILED]
)

echo|set /p="Frontend .env: "
if exist "frontend\.env" (
    echo [OK]
) else (
    echo [FAILED]
)

REM Final summary
echo.
echo ==========================================
echo [OK] Setup Complete!
echo ==========================================
echo.
echo You can now start the application using:
echo   start.bat    (Windows)
echo.
echo The application will run on:
echo   Backend:  http://127.0.0.1:8765
echo   Frontend: http://localhost:3000
echo   API Docs: http://127.0.0.1:8765/api/docs
echo.
echo Default credentials:
echo   Username: admin
echo   Password: admin
echo.
echo ==========================================
echo.
pause
