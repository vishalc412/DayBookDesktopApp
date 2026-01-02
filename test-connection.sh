#!/bin/bash

echo "=========================================="
echo "Testing DayBook Keeper Connection"
echo "=========================================="
echo ""

# Test backend on port 8765
echo "1. Testing backend on port 8765..."
if curl -s http://127.0.0.1:8765/api/health > /dev/null 2>&1; then
    echo "   ✅ Backend is running on port 8765"
    curl -s http://127.0.0.1:8765/api/health | head -3
else
    echo "   ❌ Backend NOT responding on port 8765"
    echo "   Checking if backend is running on any port..."

    for port in 8000 8001 8002 8765 8766 8767; do
        if curl -s http://127.0.0.1:$port/api/health > /dev/null 2>&1; then
            echo "   ✅ Found backend on port $port!"
            echo ""
            echo "   ⚠️  Port mismatch detected!"
            echo "   Backend is on: http://127.0.0.1:$port"
            echo "   Frontend expects: http://127.0.0.1:8765"
            echo ""
            echo "   To fix:"
            echo "   1. Stop backend (Ctrl+C)"
            echo "   2. cd backend"
            echo "   3. python main.py"
            echo "   (Should start on port 8765)"
            exit 1
        fi
    done

    echo "   ❌ Backend not found on any common port"
    echo ""
    echo "   To start backend:"
    echo "   cd backend"
    echo "   source venv/bin/activate"
    echo "   python main.py"
    exit 1
fi

echo ""

# Test frontend
echo "2. Testing frontend on port 3000..."
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "   ✅ Frontend is running on port 3000"
else
    echo "   ❌ Frontend NOT running on port 3000"
    echo ""
    echo "   To start frontend:"
    echo "   cd frontend"
    echo "   npm start"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ All services running correctly!"
echo "=========================================="
echo ""
echo "Backend:  http://127.0.0.1:8765"
echo "Frontend: http://localhost:3000"
echo ""
echo "Open http://localhost:3000 in your browser"
echo ""
