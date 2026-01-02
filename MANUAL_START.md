# 🔧 Manual Start Guide - Troubleshooting

If `./start.sh` isn't working, follow these manual steps:

## Step 1: Start Backend

Open **Terminal 1**:

```bash
cd backend

# Create venv if it doesn't exist
python3 -m venv venv

# Activate venv
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << 'EOF'
HOST=127.0.0.1
PORT=8765
DEBUG=True
EOF

# Start backend
python main.py
```

**Expected output:**
```
============================================================
DayBookKeeper by WarryWorks v1.1
============================================================
✓ Port 8765 is available
Server: http://127.0.0.1:8765
API Docs: http://127.0.0.1:8765/api/docs
============================================================
```

✅ **IMPORTANT**: Note the port number! It should be **8765**.

**Keep this terminal open!** Leave it running.

---

## Step 2: Start Frontend

Open **Terminal 2** (new terminal):

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Create .env file
cat > .env << 'EOF'
REACT_APP_API_URL=http://127.0.0.1:8765/api
EOF

# Start frontend
npm start
```

**Expected output:**
```
Compiled successfully!

You can now view daybook-web-app in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://10.0.0.x:3000
```

✅ Browser should open automatically to http://localhost:3000

**Keep this terminal open!** Leave it running.

---

## Step 3: Verify Connection

Open **Terminal 3**:

```bash
./test-connection.sh
```

Should show:
```
✅ Backend is running on port 8765
✅ Frontend is running on port 3000
✅ All services running correctly!
```

---

## Step 4: Check Browser Console

1. Open browser to http://localhost:3000
2. Press **F12** (or Cmd+Option+I on Mac)
3. Go to **Console** tab
4. Look for:
   ```
   🔧 API Configuration: {
     REACT_APP_API_URL: "http://127.0.0.1:8765/api",
     API_URL: "http://127.0.0.1:8765/api"
   }
   ```

✅ **Both URLs should say 127.0.0.1:8765**

---

## Common Issues

### Issue: Backend shows different port (e.g., 8766)

**Cause:** Port 8765 is occupied

**Solution:** Either:
- **Option A:** Kill whatever is using port 8765
  ```bash
  lsof -ti:8765 | xargs kill -9  # macOS/Linux
  ```

- **Option B:** Update frontend .env to match
  ```bash
  echo "REACT_APP_API_URL=http://127.0.0.1:8766/api" > frontend/.env
  ```
  Then restart frontend (Ctrl+C, then `npm start`)

### Issue: "Connection error" in browser

**Check these:**
1. Backend terminal still running? ✓
2. Backend shows port 8765? ✓
3. Frontend .env has port 8765? ✓
4. Restarted frontend after .env change? ✓
5. Browser console shows correct port? ✓

**If all ✓ but still failing:**
```bash
# Hard refresh browser
Cmd+Shift+R  # macOS
Ctrl+Shift+R # Windows/Linux
```

### Issue: Backend won't start

**Error: "No module named 'fastapi'"**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Error: "Address already in use"**
```bash
# Check what's using port 8765
lsof -i:8765  # macOS/Linux
netstat -ano | findstr :8765  # Windows

# Kill it
lsof -ti:8765 | xargs kill -9  # macOS/Linux
```

---

## To Stop Services

1. **Backend**: Press Ctrl+C in Terminal 1
2. **Frontend**: Press Ctrl+C in Terminal 2

---

## Quick Reference

| Service | URL | Terminal |
|---------|-----|----------|
| Backend API | http://127.0.0.1:8765 | Terminal 1 |
| API Docs | http://127.0.0.1:8765/api/docs | Browser |
| Frontend | http://localhost:3000 | Terminal 2 |

---

**Still not working?** Run this diagnostic:
```bash
./check-status.sh
```
