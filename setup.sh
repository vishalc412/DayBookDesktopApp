#!/bin/bash

# DayBook Keeper - Cross-Platform Setup Script
# This script installs all dependencies and prepares the project for first run

set -e

echo "=========================================="
echo "DayBook Keeper - Complete Setup"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if running on Linux or macOS
OS_TYPE="$(uname -s)"
echo -e "${BLUE}Detected OS: $OS_TYPE${NC}"
echo ""

# Step 1: Check Python
echo "=========================================="
echo "Step 1: Checking Python Installation"
echo "=========================================="

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo ""
    echo "Please install Python 3.11 or higher:"
    if [[ "$OS_TYPE" == "Darwin" ]]; then
        echo "  brew install python@3.11"
    else
        echo "  sudo apt-get install python3.11 python3.11-venv python3-pip"
    fi
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Step 2: Check Node.js
echo ""
echo "=========================================="
echo "Step 2: Checking Node.js Installation"
echo "=========================================="

if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    echo ""
    echo "Please install Node.js 18 or higher:"
    if [[ "$OS_TYPE" == "Darwin" ]]; then
        echo "  brew install node"
    else
        echo "  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -"
        echo "  sudo apt-get install -y nodejs"
    fi
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js $NODE_VERSION found${NC}"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm is not installed${NC}"
    exit 1
fi

NPM_VERSION=$(npm --version)
echo -e "${GREEN}✓ npm $NPM_VERSION found${NC}"

# Step 3: Setup Backend
echo ""
echo "=========================================="
echo "Step 3: Setting Up Backend"
echo "=========================================="

cd backend

# Create virtual environment
if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists${NC}"
    read -p "Do you want to recreate it? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing old virtual environment..."
        rm -rf venv
        echo "Creating new Python virtual environment..."
        python3 -m venv venv
    fi
else
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --quiet --upgrade pip

# Install dependencies
echo "Installing Python dependencies (this may take a few minutes)..."
pip install -r requirements.txt

# Mark as installed
touch venv/.installed

echo -e "${GREEN}✓ Backend dependencies installed${NC}"

# Create .env file
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "Creating backend .env from template..."
        cp .env.example .env
    else
        echo "Creating backend .env with defaults..."
        cat > .env << EOF
HOST=127.0.0.1
PORT=8765
DEBUG=True
EXCEL_FILE_PATH=daybook.xlsx
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin
EOF
    fi
    echo -e "${GREEN}✓ Backend .env created${NC}"
else
    echo -e "${GREEN}✓ Backend .env already exists${NC}"
fi

# Check if database exists
if [ ! -f "daybook.db" ]; then
    echo -e "${YELLOW}Note: Database will be created on first run${NC}"
fi

cd ..

# Step 4: Setup Frontend
echo ""
echo "=========================================="
echo "Step 4: Setting Up Frontend"
echo "=========================================="

cd frontend

# Install node modules
if [ -d "node_modules" ]; then
    echo -e "${YELLOW}Node modules already exist${NC}"
    read -p "Do you want to reinstall them? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing old node_modules..."
        rm -rf node_modules package-lock.json
        echo "Installing Node dependencies (this may take several minutes)..."
        npm install
    else
        echo -e "${GREEN}✓ Using existing node_modules${NC}"
    fi
else
    echo "Installing Node dependencies (this may take several minutes)..."
    npm install
fi

echo -e "${GREEN}✓ Frontend dependencies installed${NC}"

# Create .env file
if [ ! -f ".env" ]; then
    echo "Creating frontend .env..."
    cat > .env << EOF
REACT_APP_API_URL=http://127.0.0.1:8765/api
EOF
    echo -e "${GREEN}✓ Frontend .env created${NC}"
else
    echo -e "${GREEN}✓ Frontend .env already exists${NC}"
fi

cd ..

# Step 5: Verify installation
echo ""
echo "=========================================="
echo "Step 5: Verifying Installation"
echo "=========================================="

# Check backend dependencies
echo -n "Backend dependencies: "
if [ -f "backend/venv/.installed" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Check frontend dependencies
echo -n "Frontend dependencies: "
if [ -d "frontend/node_modules" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Check .env files
echo -n "Backend .env: "
if [ -f "backend/.env" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

echo -n "Frontend .env: "
if [ -f "frontend/.env" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Final summary
echo ""
echo "=========================================="
echo -e "${GREEN}✓✓✓ Setup Complete! ✓✓✓${NC}"
echo "=========================================="
echo ""
echo "You can now start the application using:"
echo "  ./start.sh    (Linux/Mac)"
echo ""
echo "The application will run on:"
echo "  Backend:  http://127.0.0.1:8765"
echo "  Frontend: http://localhost:3000"
echo "  API Docs: http://127.0.0.1:8765/api/docs"
echo ""
echo "Default credentials:"
echo "  Username: admin"
echo "  Password: admin"
echo ""
echo "=========================================="
