@echo off
REM DayBook Keeper v2.0 - Web Application Startup Script (Windows)
REM This script starts both backend and frontend services

setlocal enabledelayedexpansion

echo ==========================================
echo DayBook Keeper v2.0
echo Web Application Startup
echo ==========================================
echo.

REM Check Python installation
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.11, 3.12, or 3.13
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found

REM Check Node.js installation
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Node.js is not installed or not in PATH
    echo Please install Node.js 18 or higher
    pause
    exit /b 1
)

for /f "tokens=1" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
echo [OK] Node.js %NODE_VERSION% found
echo.

echo ==========================================
echo Setting up Backend...
echo ==========================================

cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install/upgrade pip
python -m pip install --quiet --upgrade pip

REM Check if dependencies need installation
set NEED_INSTALL=0
if not exist "venv\.installed" set NEED_INSTALL=1

if %NEED_INSTALL%==1 (
    echo Installing Python dependencies...
    pip install --quiet -r requirements.txt
    type nul > venv\.installed
    echo [OK] Python dependencies installed
) else (
    echo [OK] Python dependencies up to date
)

REM Create .env if it doesn't exist
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [OK] Created .env from template
    )
)

REM Start backend server
echo.
echo Starting backend server...
start /B python main.py > ..\backend.log 2>&1

REM Wait for backend to be ready
echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Extract port from log
set BACKEND_PORT=
for /f "tokens=3 delims=:" %%a in ('findstr /C:"Server: http://127.0.0.1:" ..\backend.log 2^>nul') do (
    set BACKEND_PORT=%%a
    goto :port_found
)

:port_found
if "%BACKEND_PORT%"=="" (
    echo Error: Backend failed to start
    echo Check backend.log for details
    type ..\backend.log
    pause
    exit /b 1
)

echo [OK] Backend started on port %BACKEND_PORT%

cd ..

echo.
echo ==========================================
echo Setting up Frontend...
echo ==========================================

cd frontend

REM Create .env with backend URL
echo REACT_APP_API_URL=http://127.0.0.1:%BACKEND_PORT%/api> .env
echo [OK] Frontend .env configured (API: http://127.0.0.1:%BACKEND_PORT%/api)

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing Node dependencies (this may take a few minutes)...
    call npm install
    echo [OK] Node dependencies installed
) else (
    echo [OK] Node dependencies found
)

REM Start frontend server
echo.
echo Starting React development server...
start /B npm start > ..\frontend.log 2>&1

REM Wait for frontend
echo Waiting for frontend to start (this may take 30-60 seconds)...
timeout /t 30 /nobreak >nul

echo [OK] Frontend should be ready

cd ..

echo.
echo ==========================================
echo [OK] DayBook Keeper Started Successfully!
echo ==========================================
echo.
echo   Backend:  http://127.0.0.1:%BACKEND_PORT%
echo   Frontend: http://localhost:3000
echo   API Docs: http://127.0.0.1:%BACKEND_PORT%/api/docs
echo.
echo   Logs:
echo     Backend:  backend.log
echo     Frontend: frontend.log
echo.
echo Opening browser...
echo Press Ctrl+C to stop all services
echo ==========================================
echo.

REM Auto-open browser
timeout /t 2 /nobreak >nul
start http://localhost:3000

REM Keep window open
pause
