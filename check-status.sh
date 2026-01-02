#!/bin/bash

# DayBook Keeper - Status Check Script
# Run this to diagnose connection issues

echo "=========================================="
echo "DayBook Keeper - Status Check"
echo "=========================================="
echo ""

# Check if backend is running
echo "1. Checking backend..."
BACKEND_RUNNING=$(ps aux | grep "[p]ython.*main.py" | wc -l)
if [ $BACKEND_RUNNING -gt 0 ]; then
    BACKEND_PORT=$(ps aux | grep "[p]ython.*main.py" | head -1 | grep -oE ":[0-9]{4}" | cut -d':' -f2)
    echo "   ✓ Backend is running"
    echo "   Port: Checking backend.log..."

    if [ -f "backend.log" ]; then
        LOGGED_PORT=$(grep -o "http://127.0.0.1:[0-9]*" backend.log | grep -o "[0-9]*" | head -1)
        echo "   Port from log: $LOGGED_PORT"

        # Test backend endpoint
        if curl -s "http://127.0.0.1:$LOGGED_PORT/api/health" > /dev/null 2>&1; then
            echo "   ✓ Backend is responding on port $LOGGED_PORT"
        else
            echo "   ✗ Backend not responding on port $LOGGED_PORT"
        fi
    fi
else
    echo "   ✗ Backend is NOT running"
    echo "   Run: cd backend && python main.py"
fi

echo ""

# Check if frontend is running
echo "2. Checking frontend..."
FRONTEND_RUNNING=$(ps aux | grep "[n]ode.*react-scripts" | wc -l)
if [ $FRONTEND_RUNNING -gt 0 ]; then
    echo "   ✓ Frontend is running"

    # Test frontend endpoint
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "   ✓ Frontend is responding on port 3000"
    else
        echo "   ⚠ Frontend process running but not responding yet"
    fi
else
    echo "   ✗ Frontend is NOT running"
    echo "   Run: cd frontend && npm start"
fi

echo ""

# Check .env file
echo "3. Checking configuration..."
if [ -f "frontend/.env" ]; then
    echo "   ✓ frontend/.env exists"
    ENV_URL=$(cat frontend/.env | grep REACT_APP_API_URL | cut -d'=' -f2)
    echo "   API URL: $ENV_URL"

    if [ -f "backend.log" ]; then
        BACKEND_URL=$(grep -o "http://127.0.0.1:[0-9]*/api" backend.log | head -1)
        echo "   Backend URL: ${BACKEND_URL}"

        if [ "$ENV_URL" != "${BACKEND_URL}" ]; then
            echo "   ⚠ WARNING: URLs don't match!"
            echo "   Frontend expects: $ENV_URL"
            echo "   Backend running on: $BACKEND_URL"
            echo "   → Restart frontend with: cd frontend && npm start"
        else
            echo "   ✓ URLs match correctly"
        fi
    fi
else
    echo "   ✗ frontend/.env is missing"
    echo "   Run ./start.sh to create it"
fi

echo ""

# Check logs for errors
echo "4. Checking logs..."
if [ -f "backend.log" ]; then
    ERROR_COUNT=$(grep -i "error" backend.log | wc -l)
    if [ $ERROR_COUNT -gt 0 ]; then
        echo "   ⚠ Backend log has $ERROR_COUNT errors"
        echo "   Last error:"
        grep -i "error" backend.log | tail -1
    else
        echo "   ✓ No errors in backend.log"
    fi
else
    echo "   - backend.log not found"
fi

if [ -f "frontend.log" ]; then
    FRONTEND_ERROR_COUNT=$(grep -i "error" frontend.log | wc -l)
    if [ $FRONTEND_ERROR_COUNT -gt 0 ]; then
        echo "   ⚠ Frontend log has $FRONTEND_ERROR_COUNT errors"
    else
        echo "   ✓ No errors in frontend.log"
    fi
else
    echo "   - frontend.log not found"
fi

echo ""
echo "=========================================="
echo "Summary:"
echo "=========================================="

ALL_GOOD=true

if [ $BACKEND_RUNNING -eq 0 ]; then
    echo "❌ Backend is not running"
    ALL_GOOD=false
fi

if [ $FRONTEND_RUNNING -eq 0 ]; then
    echo "❌ Frontend is not running"
    ALL_GOOD=false
fi

if [ ! -f "frontend/.env" ]; then
    echo "❌ Frontend .env is missing"
    ALL_GOOD=false
fi

if [ "$ALL_GOOD" = true ]; then
    echo "✅ Everything looks good!"
    echo ""
    echo "If you still see connection errors:"
    echo "1. Open browser console (F12)"
    echo "2. Look for '🔧 API Configuration' message"
    echo "3. Verify the API_URL matches backend port"
    echo "4. If not, restart frontend: cd frontend && npm start"
else
    echo ""
    echo "📝 To fix issues, run:"
    echo "   ./start.sh"
fi

echo ""
