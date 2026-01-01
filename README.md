# 📚 Daybook Desktop Application

> **Version 1.1** - A desktop application for offline bookkeeping with real-time Excel synchronization

![Python](https://img.shields.io/badge/Python-3.11--3.13-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)
![React](https://img.shields.io/badge/React-18.2-blue.svg)
![Electron](https://img.shields.io/badge/Electron-28.0-purple.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🎯 Overview

Daybook Desktop Application is a **cross-platform desktop application** designed for small businesses and individuals to maintain their daybook entries with **real-time Excel synchronization**. The application runs completely offline and automatically syncs all entries to an Excel file for easy sharing and backup.

### ✨ Key Features

- 📊 **Real-Time Excel Sync** - All entries automatically saved to Excel format
- 💻 **Cross-Platform** - Works on Windows, macOS, and Linux
- 🔄 **Bidirectional Sync** - Import existing Excel data
- 📈 **Automatic Balance Calculation** - Running balances updated in real-time
- 🎨 **Clean UI** - Modern, intuitive interface built with React
- 🚀 **Fast & Responsive** - FastAPI backend with Uvicorn server
- 📱 **Desktop Native** - Built with Electron for native OS integration

---

## 🏗️ Architecture

### Technology Stack

**Backend:**
- Python 3.11-3.13
- FastAPI 0.115 (REST API)
- Uvicorn (ASGI server)
- openpyxl (Excel operations)
- Pydantic 2.10 (data validation)

**Frontend:**
- React 18.2
- Axios (HTTP client)
- date-fns (date formatting)
- Modern CSS with Flexbox/Grid

**Desktop:**
- Electron 28.0
- Native OS integration
- IPC communication

### Project Structure

```
DayBookDesktopApp/
├── backend/                    # Python backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api.py             # FastAPI routes & endpoints
│   │   ├── models.py          # Data models
│   │   └── excel_sync.py      # Excel synchronization logic
│   ├── main.py                # Application entry point
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Environment variables template
│
├── frontend/                   # React + Electron frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── services/          # API services
│   │   ├── styles/            # CSS styles
│   │   ├── App.js             # Main React app
│   │   └── index.js           # React entry point
│   ├── electron/
│   │   ├── main.js            # Electron main process
│   │   └── preload.js         # Electron preload script
│   ├── public/
│   │   └── index.html         # HTML template
│   ├── package.json           # Node dependencies
│   └── .env.example           # Frontend environment variables
│
├── start.sh                    # Linux/macOS startup script
├── start.bat                   # Windows startup script
├── .gitignore
├── LICENSE
└── README.md
```

---

## 📋 Prerequisites

Before installing, ensure you have:

- **Python 3.11, 3.12, or 3.13** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18 or higher** - [Download Node.js](https://nodejs.org/)
- **Git** (optional) - [Download Git](https://git-scm.com/)

### Verify Installation

```bash
python3 --version  # Should be 3.11, 3.12, or 3.13
node --version     # Should be 18+
npm --version      # Should be 9+
```

> **Note for Python 3.13 users**: All dependencies are now fully compatible with Python 3.13.

---

## 🚀 Installation

### Option 1: Quick Start (Automated)

#### On Linux/macOS:
```bash
chmod +x start.sh
./start.sh
```

#### On Windows:
```cmd
start.bat
```

### Option 2: Manual Installation

#### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/DayBookDesktopApp.git
cd DayBookDesktopApp
```

#### Step 2: Setup Backend
```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

#### Step 3: Setup Frontend
```bash
cd ../frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env
```

---

## 🎮 Running the Application

### Development Mode

#### Start Backend Server:
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main.py
```

The backend will start at: `http://127.0.0.1:5000`
API Documentation: `http://127.0.0.1:5000/api/docs`

#### Start Frontend (in a new terminal):
```bash
cd frontend
npm run electron-dev
```

### Production Build

```bash
cd frontend
npm run build
npm run package
```

This will create installers in the `frontend/dist` directory for your platform.

---

## 📖 Usage Guide

### Creating a New Entry

1. **Launch the application**
2. **Fill in the entry form:**
   - Date: Select the transaction date
   - Description: Enter transaction description
   - Category: Choose from predefined categories
   - Reference: Add invoice/receipt number (optional)
   - Debit Amount: Enter if money is received
   - Credit Amount: Enter if money is paid
3. **Click "Add Entry"**

### Editing an Entry

1. Click the **"Edit"** button on any entry in the table
2. Modify the fields in the form
3. Click **"Update Entry"**

### Deleting an Entry

1. Click the **"Delete"** button on any entry
2. Confirm the deletion
3. The entry will be removed and balances recalculated

### Viewing Summary

The dashboard displays:
- **Total Entries**: Total number of transactions
- **Total Debit**: Sum of all debit amounts
- **Total Credit**: Sum of all credit amounts
- **Current Balance**: Running balance

### Excel File

- Excel file is automatically created as `daybook.xlsx` in the backend directory
- All entries are synced in real-time
- File can be opened with Microsoft Excel, LibreOffice, or Google Sheets
- File includes formatted headers and automatic column widths

---

## 🔧 Configuration

### Backend Configuration (`backend/.env`)

```bash
EXCEL_FILE_PATH=daybook.xlsx  # Path to Excel file
HOST=127.0.0.1                # Server host
PORT=5000                     # Server port
DEBUG=True                    # Debug mode
```

### Frontend Configuration (`frontend/.env`)

```bash
REACT_APP_API_URL=http://127.0.0.1:5000/api  # Backend API URL
ELECTRON_START_URL=http://localhost:3000      # Dev server URL
NODE_ENV=development                          # Environment
```

---

## 📡 API Endpoints

### Health Check
```
GET /api/health
```

### Entries
```
GET    /api/entries          # Get all entries
POST   /api/entries          # Create new entry
PUT    /api/entries/{id}     # Update entry
DELETE /api/entries/{id}     # Delete entry
```

### Summary
```
GET    /api/summary          # Get summary statistics
```

### Export
```
GET    /api/export           # Get Excel file path
```

### API Documentation

FastAPI provides interactive API documentation:
- **Swagger UI**: http://127.0.0.1:5000/api/docs
- **ReDoc**: http://127.0.0.1:5000/api/redoc

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
source venv/bin/activate
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

---

## 🐛 Troubleshooting

### Issue: Backend won't start

**Solution:**
```bash
# Check if port 5000 is already in use
lsof -i :5000  # On Linux/macOS
netstat -ano | findstr :5000  # On Windows

# Change PORT in backend/.env if needed
```

### Issue: Excel file locked

**Solution:**
- Close any Excel applications that might have the file open
- The app uses file locking to prevent conflicts

### Issue: Frontend can't connect to backend

**Solution:**
- Ensure backend is running on http://127.0.0.1:5000
- Check `REACT_APP_API_URL` in `frontend/.env`
- Check CORS settings in `backend/app/api.py`

### Issue: Electron window doesn't open

**Solution:**
```bash
cd frontend
rm -rf node_modules
npm install
npm run electron-dev
```

### Issue: Python 3.13 installation fails with pydantic-core build error

**Solution:**
This issue has been resolved in the latest version. If you're using an older clone:
```bash
cd backend
git pull  # Get latest requirements.txt
rm -rf venv
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

The updated `requirements.txt` now includes:
- pydantic 2.10.3 (full Python 3.13 support)
- email-validator 2.2.0 (stable version)
- Updated FastAPI, SQLAlchemy, and other dependencies

---

## 🗂️ Data Model

### DaybookEntry

| Field | Type | Description |
|-------|------|-------------|
| entry_id | Integer | Unique identifier (auto-generated) |
| date | DateTime | Transaction date |
| description | String | Transaction description |
| debit | Float | Debit amount (money received) |
| credit | Float | Credit amount (money paid) |
| balance | Float | Running balance (auto-calculated) |
| category | String | Transaction category |
| reference | String | Invoice/receipt reference |

### Categories

- Sales
- Purchase
- Expense
- Income
- Asset
- Liability
- Other

---

## ⚡ Quick Reference

### Common Commands

```bash
# Start backend
cd backend && python main.py

# Start frontend (development)
cd frontend && npm run electron-dev

# Install backend dependencies
cd backend && pip install -r requirements.txt

# Install frontend dependencies
cd frontend && npm install

# Run tests
cd backend && pytest
cd frontend && npm test

# Build production
cd frontend && npm run build && npm run package
```

---

<div align="center">

**Made with ❤️ for small businesses and freelancers**

[Documentation](README.md) • [API Docs](http://127.0.0.1:5000/api/docs) • [Issues](https://github.com/vishalc412/DayBookDesktopApp/issues)

</div>