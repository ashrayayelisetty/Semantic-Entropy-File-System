@echo off
REM SEFS Startup Script for Windows
REM Starts both backend and frontend services

echo ========================================
echo   SEFS: Semantic Entropy File System
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ and try again
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 18+ and try again
    pause
    exit /b 1
)

echo [1/5] Checking Python dependencies...
echo.

REM Check if required packages are installed
cd backend
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo Installing minimal Python dependencies...
    pip install -r requirements-minimal.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)
cd ..

echo [2/5] Starting Backend Server...
echo.

REM Start backend in background
cd backend
start /B cmd /c "python -m uvicorn main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1"
cd ..

REM Wait for backend to initialize
echo [3/5] Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Check if backend is running
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo WARNING: Backend may not be ready yet. Continuing anyway...
) else (
    echo Backend is ready!
)
echo.

echo [4/5] Starting Frontend Server...
echo.

REM Start frontend in background
cd frontend\sefs-ui
start /B cmd /c "npm start > frontend.log 2>&1"
cd ..\..

REM Wait for frontend to initialize
echo [5/5] Waiting for frontend to initialize...
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo   SEFS is now running!
echo ========================================
echo.
echo Backend API:  http://localhost:8000
echo Frontend UI:  http://localhost:3000
echo.
echo API Docs:     http://localhost:8000/docs
echo Health Check: http://localhost:8000/health
echo.
echo Logs:
echo   Backend:  backend\backend.log
echo   Frontend: frontend\sefs-ui\frontend.log
echo.
echo NOTE: AI naming is disabled without API keys.
echo      To enable, see GEMINI_SETUP.md
echo.
echo To stop services:
echo   1. Close this window
echo   2. Or press Ctrl+C and run: taskkill /F /IM python.exe /IM node.exe
echo.
echo Opening browser in 3 seconds...
timeout /t 3 /nobreak >nul

REM Open browser
start http://localhost:3000

echo.
echo Press any key to stop all services...
pause >nul

REM Cleanup - kill background processes
echo.
echo Stopping services...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
echo Services stopped.
