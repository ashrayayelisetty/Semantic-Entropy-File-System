#!/bin/bash
# SEFS Startup Script for Unix/Mac
# Starts both backend and frontend services

set -e

echo "========================================"
echo "  SEFS: Semantic Entropy File System"
echo "========================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.11+ and try again"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed or not in PATH"
    echo "Please install Node.js 18+ and try again"
    exit 1
fi

# Store PIDs for cleanup
BACKEND_PID=""
FRONTEND_PID=""

# Cleanup function
cleanup() {
    echo ""
    echo "Stopping services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        echo "Backend stopped (PID: $BACKEND_PID)"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo "Frontend stopped (PID: $FRONTEND_PID)"
    fi
    echo "Services stopped."
    exit 0
}

# Set up trap for cleanup on exit
trap cleanup SIGINT SIGTERM EXIT

echo "[1/4] Starting Backend Server..."
echo ""

# Start backend in background
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
cd ..

echo "Backend started (PID: $BACKEND_PID)"

# Wait for backend to initialize
echo "[2/4] Waiting for backend to initialize..."
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "Backend is ready!"
else
    echo "WARNING: Backend may not be ready yet. Continuing anyway..."
fi
echo ""

echo "[3/4] Starting Frontend Server..."
echo ""

# Start frontend in background
cd frontend/sefs-ui
npm start > frontend.log 2>&1 &
FRONTEND_PID=$!
cd ../..

echo "Frontend started (PID: $FRONTEND_PID)"

# Wait for frontend to initialize
echo "[4/4] Waiting for frontend to initialize..."
sleep 10

echo ""
echo "========================================"
echo "  SEFS is now running!"
echo "========================================"
echo ""
echo "Backend API:  http://localhost:8000"
echo "Frontend UI:  http://localhost:3000"
echo ""
echo "API Docs:     http://localhost:8000/docs"
echo "Health Check: http://localhost:8000/health"
echo ""
echo "Process IDs:"
echo "  Backend:  $BACKEND_PID"
echo "  Frontend: $FRONTEND_PID"
echo ""
echo "Logs:"
echo "  Backend:  backend/backend.log"
echo "  Frontend: frontend/sefs-ui/frontend.log"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Open browser (platform-specific)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open http://localhost:3000
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:3000
    fi
fi

# Wait for user interrupt
wait
