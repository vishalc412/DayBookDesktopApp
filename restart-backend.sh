#!/bin/bash

# Comprehensive Backend Restart Script
# Stops any running instances and starts fresh

echo "=========================================="
echo "Restarting DayBook Backend"
echo "=========================================="
echo ""

# Kill any existing Python processes running main.py
echo "Stopping existing backend processes..."
pkill -f "python.*main.py" 2>/dev/null || true
sleep 2

# Kill any processes on port 8765
echo "Freeing port 8765..."
lsof -ti:8765 2>/dev/null | xargs kill -9 2>/dev/null || true
sleep 1

echo "✓ Old processes stopped"
echo ""

# Navigate to backend
cd backend

# Activate virtual environment
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "ERROR: Virtual environment not found!"
    echo "Please run setup.sh first"
    exit 1
fi

# Start backend with verbose error logging
echo "Starting backend with error logging..."
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

python main.py 2>&1 | tee ../backend_errors.log
