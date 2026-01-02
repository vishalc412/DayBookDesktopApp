# 🚀 DayBook Keeper v2.0 - Quick Start Guide

## ⚡ One-Command Startup

### macOS / Linux:
```bash
./start.sh
```

### Windows:
```cmd
start.bat
```

That's it! The script will:
- ✅ Check Python & Node.js installed
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Start backend on available port
- ✅ Start React frontend
- ✅ Open browser automatically

---

## 📋 Prerequisites

### Required Software:
- **Python 3.11, 3.12, or 3.13** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)

### Verify Installation:
```bash
python3 --version  # Should show 3.11.x, 3.12.x, or 3.13.x
node --version     # Should show v18.x or higher
```

---

## 🎯 Application URLs

After startup completes:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main web application |
| **Backend** | http://127.0.0.1:8001 | API server (port may vary) |
| **API Docs** | http://127.0.0.1:8001/api/docs | Interactive API documentation |

---

## 🛠️ Manual Startup (Alternative)

If you prefer to run services separately:

### Terminal 1 - Backend:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Terminal 2 - Frontend:
```bash
cd frontend
npm install
npm start
```

Then open http://localhost:3000 in your browser.

---

## 🔍 Troubleshooting

### Issue: "Port 8000 already in use"
✅ **Automatic Fix**: The backend automatically finds the next available port (8001, 8002, etc.)

### Issue: "Connection error. Please ensure the server is running"
**Solution:**
1. Check backend.log for errors
2. Ensure backend shows "Server: http://127.0.0.1:XXXX"
3. Restart with `./start.sh` or `start.bat`

### Issue: Python dependencies fail to install (Python 3.13)
**Solution:** This is already fixed in the latest version!
- ✅ pydantic 2.10.3 (full Python 3.13 support)
- ✅ All dependencies updated

### Issue: "electron-dev" script not found
**Solution:** This is expected - Electron has been removed. Use browser-based app instead.

---

## 📝 Logs

Check these files if something goes wrong:
- **backend.log** - Backend API server logs
- **frontend.log** - React development server logs

---

## ⌨️ Keyboard Shortcuts

- **Ctrl+C** in terminal → Stops both backend and frontend
- **Cmd/Ctrl + R** in browser → Refresh application

---

## 🎓 Module Overview

After startup, you'll have access to:

1. **📚 Daybook** - Journal entries and transactions
2. **💰 Savings** - Savings accounts and goals
3. **🥇 Precious Metals** - Gold, Silver, Platinum, Copper investments
4. **💳 Expenses** - Expense tracking and budgeting
5. **📊 Reports** - Financial reports and analytics

---

## 🆘 Getting Help

- **Documentation**: See README.md for detailed documentation
- **API Docs**: http://127.0.0.1:8001/api/docs
- **Issues**: Create an issue on GitHub

---

## ✅ Version Information

- **App Version**: 2.0.0
- **Python**: 3.11-3.13
- **FastAPI**: 0.115.0
- **React**: 18.2.0
- **Node.js**: 18+

---

**Happy Bookkeeping! 📚💰**
