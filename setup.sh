#!/bin/bash
echo "============================================================"
echo "DayBookKeeper v2.0 - Setup Script (Linux/Mac)"
echo "by WarryWorks"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.9 or higher"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js is not installed"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo "[OK] Python and Node.js are installed"
echo ""

# Setup Backend
echo "============================================================"
echo "Setting up Backend..."
echo "============================================================"
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "[OK] Backend setup complete"
cd ..
echo ""

# Setup Frontend
echo "============================================================"
echo "Setting up Frontend..."
echo "============================================================"
cd frontend

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

echo "[OK] Frontend setup complete"
cd ..
echo ""

# Create .env files if they don't exist
if [ ! -f "backend/.env" ]; then
    echo "Creating backend .env file..."
    cat > backend/.env << EOF
HOST=127.0.0.1
PORT=8765
DEBUG=True
EOF
fi

if [ ! -f "frontend/.env" ]; then
    echo "Creating frontend .env file..."
    cat > frontend/.env << EOF
REACT_APP_API_URL=http://127.0.0.1:8765/api
EOF
fi

# Make start script executable
chmod +x start.sh

echo ""
echo "============================================================"
echo "Setup Complete!"
echo "============================================================"
echo ""
echo "To start the application, run: ./start.sh"
echo ""
