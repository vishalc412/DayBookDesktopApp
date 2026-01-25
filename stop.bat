@echo off
REM DayBook Keeper v2.0 - Stop Script (Windows)

echo ==========================================
echo Stopping DayBook Keeper...
echo ==========================================

REM Kill processes on port 8765 (backend)
echo Stopping backend (port 8765)...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8765" ^| find "LISTENING"') do taskkill /F /PID %%a 2>nul

REM Kill processes on port 3000 (frontend)
echo Stopping frontend (port 3000)...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":3000" ^| find "LISTENING"') do taskkill /F /PID %%a 2>nul

REM Kill any Python processes running main.py
echo Stopping Python processes...
taskkill /F /FI "WINDOWTITLE eq DayBook Backend*" 2>nul

REM Kill any Node processes running npm
echo Stopping Node processes...
taskkill /F /FI "WINDOWTITLE eq DayBook Frontend*" 2>nul

echo [OK] All services stopped
echo.
pause
