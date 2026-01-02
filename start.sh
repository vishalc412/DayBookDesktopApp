#!/bin/bash

# DayBook Keeper - Simple Startup Script
# No dynamic ports, no complicated logic - just works!

set -e

echo "=========================================="
echo "DayBook Keeper v2.0"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Fixed port - no dynamic allocation
BACKEND_PORT=8765
FRONTEND_PORT=3000

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down...${NC}"

    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi

    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi

    # Kill any process on our ports
    lsof -ti:$BACKEND_PORT 2>/dev/null | xargs kill -9 2>/dev/null || true
    lsof -ti:$FRONTEND_PORT 2>/dev/null | xargs kill -9 2>/dev/null || true

    echo -e "${GREEN}Shutdown complete${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python found${NC}"

# Check Node
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js found${NC}"

echo ""
echo "=========================================="
echo "Step 1: Setup Backend on Port $BACKEND_PORT"
echo "=========================================="

cd backend

# Create venv if needed
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies
if [ ! -f "venv/.installed" ]; then
    echo "Installing Python dependencies..."
    pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt
    touch venv/.installed
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Dependencies up to date${NC}"
fi

# Create backend .env with fixed port
cat > .env << EOF
HOST=127.0.0.1
PORT=$BACKEND_PORT
DEBUG=True
EXCEL_FILE_PATH=daybook.xlsx
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin
EOF

echo -e "${GREEN}✓ Backend configured for port $BACKEND_PORT${NC}"

# Kill anything on backend port
lsof -ti:$BACKEND_PORT 2>/dev/null | xargs kill -9 2>/dev/null || true

# Start backend
echo "Starting backend..."
python main.py > ../backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to be ready
echo "Waiting for backend..."
for i in {1..30}; do
    if curl -s http://127.0.0.1:$BACKEND_PORT/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is running on http://127.0.0.1:$BACKEND_PORT${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}Error: Backend failed to start${NC}"
        cat ../backend.log
        exit 1
    fi
done

cd ..

echo ""
echo "=========================================="
echo "Step 2: Setup Frontend on Port $FRONTEND_PORT"
echo "=========================================="

cd frontend

# Install node modules if needed
if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    npm install
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Dependencies found${NC}"
fi

# Create frontend .env with backend URL
cat > .env << EOF
REACT_APP_API_URL=http://127.0.0.1:$BACKEND_PORT/api
EOF

echo -e "${GREEN}✓ Frontend configured to connect to http://127.0.0.1:$BACKEND_PORT/api${NC}"

# Kill anything on frontend port
lsof -ti:$FRONTEND_PORT 2>/dev/null | xargs kill -9 2>/dev/null || true

# Start frontend
echo "Starting React dev server..."
BROWSER=none npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend
echo "Waiting for frontend..."
for i in {1..60}; do
    if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Frontend is running on http://localhost:$FRONTEND_PORT${NC}"
        break
    fi
    sleep 1
done

cd ..

echo ""
echo "=========================================="
echo -e "${GREEN}✓✓✓ SUCCESS! ✓✓✓${NC}"
echo "=========================================="
echo ""
echo "  Backend:  http://127.0.0.1:$BACKEND_PORT"
echo "  Frontend: http://localhost:$FRONTEND_PORT"
echo "  API Docs: http://127.0.0.1:$BACKEND_PORT/api/docs"
echo ""
echo "  Backend Log:  backend.log"
echo "  Frontend Log: frontend.log"
echo ""
echo "Opening browser..."
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

# Open browser
sleep 2
if command -v open &> /dev/null; then
    open http://localhost:$FRONTEND_PORT
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:$FRONTEND_PORT
fi

# Wait forever
wait
