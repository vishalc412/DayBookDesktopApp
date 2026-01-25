# DayBookKeeper v2.0 - Cross-Platform Setup Guide

## Quick Start (Any Platform)

### Windows
```batch
# First time setup
setup.bat

# Start application
start.bat

# Stop application
stop.bat
```

### Linux/Mac
```bash
# First time setup
chmod +x setup.sh start.sh stop.sh
./setup.sh

# Start application
./start.sh

# Stop application
./stop.sh
```

---

## Prerequisites

Before running the setup, ensure you have:

1. **Python 3.9 or higher**
   - Windows: Download from https://www.python.org/
   - Mac: `brew install python3` or download from python.org
   - Linux: `sudo apt install python3 python3-pip python3-venv`

2. **Node.js 18 or higher**
   - Download from https://nodejs.org/
   - Or use nvm: `nvm install 18`

3. **Git** (optional, for cloning)
   - Download from https://git-scm.com/

---

## What Each Script Does

### `setup.bat` / `setup.sh`
- Checks if Python and Node.js are installed
- Creates Python virtual environment in `backend/venv`
- Installs all Python dependencies from `backend/requirements.txt`
- Installs all Node.js dependencies with `npm install`
- Creates `.env` configuration files
- Makes scripts executable (Linux/Mac only)

### `start.bat` / `start.sh`
- Activates Python virtual environment
- Starts backend server on `http://127.0.0.1:8765`
- Starts frontend server on `http://localhost:3000`
- Opens browser automatically
- Shows logs in separate windows (Windows) or files (Linux/Mac)

### `stop.bat` / `stop.sh`
- Stops all backend processes
- Stops all frontend processes
- Cleans up running services

---

## Manual Setup (If Scripts Don't Work)

### Backend Setup
```bash
cd backend

# Windows
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend
npm install
```

### Manual Start

**Terminal 1 (Backend):**
```bash
cd backend

# Windows
venv\Scripts\activate.bat
python main.py

# Linux/Mac
source venv/bin/activate
python main.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm start
```

---

## Accessing the Application

Once started:
- **Frontend UI:** http://localhost:3000
- **Backend API:** http://127.0.0.1:8765
- **API Documentation:** http://127.0.0.1:8765/api/docs

---

## Troubleshooting

### Port Already in Use

**Windows:**
```batch
# Find what's using port 8765
netstat -ano | findstr :8765
# Kill process (replace PID with actual number)
taskkill /F /PID <PID>
```

**Linux/Mac:**
```bash
# Find what's using port 8765
lsof -ti:8765
# Kill process
kill -9 $(lsof -ti:8765)
```

### Python/Node Not Found

1. Make sure Python and Node.js are installed
2. Add them to your PATH environment variable
3. Restart your terminal/command prompt

### Dependencies Installation Fails

**Windows:**
```batch
# Run as Administrator
# Or use PowerShell and run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Linux:**
```bash
# Install build tools
sudo apt-get install build-essential python3-dev
```

### Backend Crashes

Check `backend.log` for errors:
```bash
tail -f backend.log  # Linux/Mac
type backend.log     # Windows
```

### Frontend Won't Start

Check `frontend.log` for errors and ensure:
1. `backend/.env` has correct port
2. `frontend/.env` points to correct API URL
3. Node modules installed: `cd frontend && npm install`

---

## Environment Variables

### Backend (`.env` in `backend/` folder)
```env
HOST=127.0.0.1
PORT=8765
DEBUG=True
```

### Frontend (`.env` in `frontend/` folder)
```env
REACT_APP_API_URL=http://127.0.0.1:8765/api
```

---

## Project Structure

```
DayBookDesktopApp/
├── backend/               # Python FastAPI backend
│   ├── venv/             # Python virtual environment
│   ├── main.py           # Backend entry point
│   ├── requirements.txt  # Python dependencies
│   └── .env             # Backend config
├── frontend/             # React frontend
│   ├── node_modules/    # Node dependencies
│   ├── src/             # React source code
│   ├── package.json     # Node dependencies
│   └── .env             # Frontend config
├── setup.bat/.sh        # Setup scripts
├── start.bat/.sh        # Start scripts
└── stop.bat/.sh         # Stop scripts
```

---

## Features

### Modules Implemented:
- ✅ **Daybook** - Transaction management
- ✅ **Savings & Investments** - Track savings accounts
- ✅ **Precious Metals** - Gold/Silver portfolio tracking
- ✅ **Expenses** - Expense tracking and budgeting
- ✅ **Reports** - Generate financial reports

---

## Support

For issues or questions:
1. Check `backend.log` and `frontend.log`
2. Ensure all prerequisites are installed
3. Try manual setup if scripts fail
4. Make sure ports 8765 and 3000 are available

---

## License

DayBookKeeper v2.0 by WarryWorks
