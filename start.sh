#!/bin/bash

# Daybook Desktop Application Startup Script
# This script starts both backend and frontend services

echo "=========================================="
echo "Daybook Desktop Application v1.1"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    exit 1
fi

# Setup Python virtual environment
echo "Setting up Python environment..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

# Copy environment file if not exists
if [ ! -f ".env" ]; then
    cp .env.example .env
fi

# Start backend server in background
echo "Starting backend server..."
python main.py &
BACKEND_PID=$!

cd ..

# Setup Node.js environment
echo "Setting up Node.js environment..."
cd frontend

# Copy environment file if not exists
if [ ! -f ".env" ]; then
    cp .env.example .env
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start Electron app
echo "Starting Electron application..."
npm run electron-dev

# Cleanup on exit
kill $BACKEND_PID
