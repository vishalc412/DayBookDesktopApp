#!/bin/bash
# DayBook Keeper v2.0 - Stop Script (Linux/Mac)

echo "=========================================="
echo "Stopping DayBook Keeper..."
echo "=========================================="

# Kill processes using ports 8765 and 3000
echo "Stopping backend (port 8765)..."
lsof -ti:8765 2>/dev/null | xargs kill -9 2>/dev/null || echo "No backend process found"

echo "Stopping frontend (port 3000)..."
lsof -ti:3000 2>/dev/null | xargs kill -9 2>/dev/null || echo "No frontend process found"

# Kill processes by PID files if they exist
if [ -f ".backend.pid" ]; then
    kill $(cat .backend.pid) 2>/dev/null || true
    rm .backend.pid
fi

if [ -f ".frontend.pid" ]; then
    kill $(cat .frontend.pid) 2>/dev/null || true
    rm .frontend.pid
fi

# Kill any Python main.py processes
pkill -f "python main.py" 2>/dev/null || true

# Kill any npm start processes
pkill -f "react-scripts start" 2>/dev/null || true

echo "[OK] All services stopped"
echo ""
