#!/bin/bash

# DayBook Keeper v2.0 - Web Application Startup Script
# This script starts both backend and frontend services

set -e  # Exit on error

echo "=========================================="
echo "DayBook Keeper v2.0"
echo "Web Application Startup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track process IDs for cleanup
BACKEND_PID=""
FRONTEND_PID=""

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down...${NC}"

    if [ ! -z "$FRONTEND_PID" ]; then
        echo "Stopping frontend..."
        kill $FRONTEND_PID 2>/dev/null || true
    fi

    if [ ! -z "$BACKEND_PID" ]; then
        echo "Stopping backend..."
        kill $BACKEND_PID 2>/dev/null || true
    fi

    echo -e "${GREEN}✓ Shutdown complete${NC}"
    exit 0
}

# Set up trap for cleanup on Ctrl+C or exit
trap cleanup SIGINT SIGTERM EXIT

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "Please install Python 3.11, 3.12, or 3.13"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}' | cut -d'.' -f1,2)
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Check Node.js installation
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    echo "Please install Node.js 18 or higher"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js $NODE_VERSION found${NC}"

echo ""
echo "=========================================="
echo "Setting up Backend..."
echo "=========================================="

cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade pip
pip install --quiet --upgrade pip

# Check if dependencies need installation
NEED_INSTALL=false
if [ ! -f "venv/.installed" ]; then
    NEED_INSTALL=true
else
    # Check if requirements.txt is newer than .installed marker
    if [ "requirements.txt" -nt "venv/.installed" ]; then
        NEED_INSTALL=true
    fi
fi

if [ "$NEED_INSTALL" = true ]; then
    echo "Installing Python dependencies..."
    pip install --quiet -r requirements.txt
    touch venv/.installed
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Python dependencies up to date${NC}"
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env from template${NC}"
    fi
fi

# Start backend server in background
echo ""
echo "Starting backend server..."
python main.py > ../backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to be ready (check for port in log)
echo "Waiting for backend to start..."
COUNTER=0
BACKEND_PORT=""
while [ $COUNTER -lt 30 ]; do
    if [ -f "../backend.log" ]; then
        BACKEND_PORT=$(grep -o "http://127.0.0.1:[0-9]*" ../backend.log | grep -o "[0-9]*" | head -1)
        if [ ! -z "$BACKEND_PORT" ]; then
            echo -e "${GREEN}✓ Backend started on port $BACKEND_PORT${NC}"
            break
        fi
    fi
    sleep 0.5
    COUNTER=$((COUNTER + 1))
done

if [ -z "$BACKEND_PORT" ]; then
    echo -e "${RED}Error: Backend failed to start${NC}"
    echo "Check backend.log for details"
    cat ../backend.log
    exit 1
fi

cd ..

echo ""
echo "=========================================="
echo "Setting up Frontend..."
echo "=========================================="

cd frontend

# Create .env with backend URL
echo "REACT_APP_API_URL=http://127.0.0.1:$BACKEND_PORT/api" > .env
echo -e "${GREEN}✓ Frontend .env configured (API: http://127.0.0.1:$BACKEND_PORT/api)${NC}"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies (this may take a few minutes)..."
    npm install
    echo -e "${GREEN}✓ Node dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Node dependencies found${NC}"
fi

# Start frontend server in background
echo ""
echo "Starting React development server..."
npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to be ready
echo "Waiting for frontend to start..."
COUNTER=0
while [ $COUNTER -lt 60 ]; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Frontend ready${NC}"
        break
    fi
    sleep 0.5
    COUNTER=$((COUNTER + 1))
done

if [ $COUNTER -eq 60 ]; then
    echo -e "${YELLOW}Warning: Frontend taking longer than expected${NC}"
    echo "Check frontend.log if issues persist"
fi

cd ..

echo ""
echo "=========================================="
echo -e "${GREEN}✓ DayBook Keeper Started Successfully!${NC}"
echo "=========================================="
echo ""
echo "  Backend:  http://127.0.0.1:$BACKEND_PORT"
echo "  Frontend: http://localhost:3000"
echo "  API Docs: http://127.0.0.1:$BACKEND_PORT/api/docs"
echo ""
echo "  Logs:"
echo "    Backend:  backend.log"
echo "    Frontend: frontend.log"
echo ""
echo "Press Ctrl+C to stop all services"
echo "=========================================="

# Auto-open browser (macOS, Linux, or WSL)
if command -v open &> /dev/null; then
    # macOS
    sleep 2
    open http://localhost:3000
elif command -v xdg-open &> /dev/null; then
    # Linux
    sleep 2
    xdg-open http://localhost:3000
fi

# Wait for processes
wait
