# SEFS Startup Guide

This guide explains how to start the SEFS (Semantic Entropy File System) application using the provided startup scripts.

## Prerequisites

Before running the startup scripts, ensure you have:

1. **Python 3.11+** installed and in your PATH
2. **Node.js 18+** installed and in your PATH
3. **Backend dependencies** installed: `pip install -r backend/requirements.txt`
4. **Frontend dependencies** installed: `cd frontend/sefs-ui && npm install`

## Quick Start

### Windows

Simply double-click `START.bat` or run from command prompt:

```cmd
START.bat
```

### Unix/Mac

Make the script executable (first time only):

```bash
chmod +x START.sh
```

Then run:

```bash
./START.sh
```

## What the Scripts Do

The startup scripts perform the following steps:

1. **Verify Prerequisites**: Check that Python and Node.js are installed
2. **Start Backend**: Launch the FastAPI backend server on port 8000
3. **Wait for Backend**: Give the backend 5 seconds to initialize
4. **Start Frontend**: Launch the React frontend development server on port 3000
5. **Wait for Frontend**: Give the frontend 10 seconds to initialize
6. **Open Browser**: Automatically open http://localhost:3000 in your default browser
7. **Display Information**: Show URLs, PIDs/logs, and instructions

## Access Points

Once started, you can access:

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Logs

Application logs are saved to:

- **Backend**: `backend/backend.log`
- **Frontend**: `frontend/sefs-ui/frontend.log`

Check these files if you encounter issues.

## Stopping the Services

### Windows

- Press any key in the command window, or
- Close the command window, or
- Run: `taskkill /F /IM python.exe /IM node.exe`

### Unix/Mac

- Press `Ctrl+C` in the terminal

The scripts will automatically clean up background processes.

## Troubleshooting

### Backend won't start

- Check that port 8000 is not already in use
- Verify Python dependencies are installed: `pip install -r backend/requirements.txt`
- Check `backend/backend.log` for error messages

### Frontend won't start

- Check that port 3000 is not already in use
- Verify Node.js dependencies are installed: `cd frontend/sefs-ui && npm install`
- Check `frontend/sefs-ui/frontend.log` for error messages

### Browser doesn't open automatically

- Manually navigate to http://localhost:3000
- Check that the frontend server started successfully

### "Python/Node.js not found" error

- Ensure Python 3.11+ and Node.js 18+ are installed
- Verify they are in your system PATH
- Try running `python --version` and `node --version` manually

## Manual Startup (Alternative)

If the startup scripts don't work, you can start services manually:

### Terminal 1 - Backend

```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Terminal 2 - Frontend

```bash
cd frontend/sefs-ui
npm start
```

## Next Steps

After starting SEFS:

1. The system will monitor the `sefs_root/` directory for new files
2. Add PDF or text files to `sefs_root/` to see automatic organization
3. Use the demo file generator: `python create_demo_files.py`
4. Watch the visualization update in real-time
5. Explore the API at http://localhost:8000/docs

## Support

For issues or questions, refer to:

- Main README: `README.md`
- Demo Script: `DEMO_SCRIPT.md`
- API Documentation: http://localhost:8000/docs (when running)
