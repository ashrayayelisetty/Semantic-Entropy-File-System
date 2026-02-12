# SEFS: Semantic Entropy File System

**A revolutionary self-organizing file manager that uses AI and semantic understanding to automatically cluster and organize your documents.**

SEFS combines machine learning, real-time file monitoring, and beautiful visualization to create a file management system that understands what your files are about—not just their names or types. Files automatically cluster into "semantic gravity wells" based on content similarity, and the system creates real OS folders to keep everything organized.

---

## 🌟 What Makes SEFS Special?

- **Semantic Gravity Wells**: Files automatically cluster based on content meaning, visualized as gravity wells that pull related documents together
- **OS-Level Integration**: Creates real folders on your filesystem and moves files automatically—not just a virtual view
- **Real-Time Intelligence**: Monitors your directory and reorganizes instantly when new files are added
- **AI-Powered Naming**: Uses CrewAI agents to generate meaningful, descriptive folder names
- **Beautiful Visualization**: Interactive D3.js gravity well interface showing semantic relationships in real-time
- **Zero Configuration**: Works out of the box with sensible defaults

---

## 🎯 Key Features

### Automatic Organization
- Monitors designated directory for PDF and text files
- Extracts content and generates semantic embeddings using SentenceTransformers
- Clusters files using DBSCAN algorithm based on cosine similarity
- Creates folders and moves files automatically

### Intelligent Naming
- AI agents analyze cluster content to generate meaningful names
- Fallback to keyword-based naming if AI is unavailable
- OS-compatible folder names (sanitized special characters)

### Real-Time Visualization
- Interactive 2D gravity well metaphor
- Files pulled toward cluster centers by semantic similarity
- Color-coded clusters with pulsing animations
- Drag-and-drop exploration
- Live activity feed showing system operations

### Robust Architecture
- FastAPI backend with WebSocket support for real-time updates
- State persistence across restarts
- Bidirectional OS synchronization
- Comprehensive error handling and logging

---

## 📋 Prerequisites

Before installing SEFS, ensure you have:

- **Python 3.11 or higher** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18 or higher** - [Download Node.js](https://nodejs.org/)
- **pip** (Python package manager, included with Python)
- **npm** (Node package manager, included with Node.js)
- **Git** (optional, for cloning the repository)

### System Requirements
- **OS**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 2GB for dependencies and models
- **Internet**: Required for initial model download and optional AI naming

---

## 🚀 Installation

### Step 1: Clone or Download the Project

```bash
# If using Git
git clone <repository-url>
cd sefs-project

# Or download and extract the ZIP file, then navigate to the directory
```

### Step 2: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate

# On Unix/Mac:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

**Note**: The first time you run the system, SentenceTransformers will download the `all-MiniLM-L6-v2` model (~80MB). This is a one-time download.

### Step 3: Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend/sefs-ui

# Install Node.js dependencies
npm install
```

### Step 4: Optional - AI Naming Setup

If you want to use AI-powered folder naming with CrewAI:

#### Option A: Using Gemini (Free - Recommended)

1. Get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a `.env` file in the `backend` directory:

```bash
# backend/.env
GEMINI_API_KEY=your_gemini_api_key_here
MODEL_NAME=gemini/gemini-1.5-flash
```

**For detailed Gemini setup instructions, see [GEMINI_SETUP.md](GEMINI_SETUP.md)**

#### Option B: Using OpenAI

1. Get an OpenAI API key from [OpenAI Platform](https://platform.openai.com/)
2. Create a `.env` file in the `backend` directory:

```bash
# backend/.env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL_NAME=gpt-4o-mini
```

**Note**: AI naming is optional. The system works perfectly with keyword-based naming if you skip this step.

---

## 💻 Usage

### Quick Start with Startup Scripts

The easiest way to run SEFS is using the provided startup scripts:

**Windows:**
```cmd
START.bat
```

**Unix/Mac:**
```bash
chmod +x START.sh  # First time only
./START.sh
```

The scripts will:
1. Start the backend server on port 8000
2. Start the frontend development server on port 3000
3. Automatically open your browser to http://localhost:3000

For detailed startup instructions, see [STARTUP_GUIDE.md](STARTUP_GUIDE.md).

### Manual Startup

If you prefer to start services manually:

**Terminal 1 - Backend:**
```bash
cd backend
# Activate virtual environment first (see Installation)
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend/sefs-ui
npm start
```

### Using SEFS

1. **Access the Interface**
   - Open your browser to http://localhost:3000
   - You'll see the gravity well visualization

2. **Add Files**
   - Drop PDF or text files into the `sefs_root/` directory
   - The system automatically detects and processes them
   - Watch the visualization update in real-time

3. **View Organization**
   - Files cluster into semantic groups (gravity wells)
   - Check the activity feed for system events
   - Open `sefs_root/` in your file explorer to see real folders

4. **Explore the Visualization**
   - Hover over files to see details
   - Drag files to explore relationships
   - Click cluster centers to see folder names

### API Access

The backend provides a REST API and WebSocket interface:

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (interactive Swagger UI)
- **Health Check**: http://localhost:8000/health

---

## 🎪 Demo Instructions

SEFS includes a demo file generator to showcase the system's capabilities.

### Running the Demo

1. **Clean the Directory** (optional, for a fresh demo):
```bash
# Remove any existing files in sefs_root
rm -rf sefs_root/*  # Unix/Mac
# or
del /Q sefs_root\*  # Windows
```

2. **Generate Demo Files**:
```bash
# From the project root directory
python create_demo_files.py
```

This creates 9 sample files:
- 3 AI/Machine Learning research papers
- 3 cooking recipes
- 3 travel guides

3. **Watch the Magic**:
   - The system automatically detects the files
   - Extracts content and generates embeddings
   - Clusters files into 3 distinct semantic groups
   - Creates folders and moves files
   - Updates the visualization in real-time

4. **Explore the Results**:
   - View the 3 gravity wells in the UI (AI, Recipes, Travel)
   - Check `sefs_root/` to see the created folders
   - Open folders to verify files are organized correctly

5. **Test Real-Time Updates**:
   - Create a new text file about neural networks
   - Save it to `sefs_root/`
   - Watch it automatically join the AI cluster

### Demo Tips

- Position your browser and file explorer side-by-side for maximum impact
- Use the activity feed to narrate what the system is doing
- Show the OS folders to demonstrate real integration
- Add a new file live to show real-time capabilities

For a complete demo script with timing and talking points, see [DEMO_SCRIPT.md](DEMO_SCRIPT.md).

---

## 📁 Project Structure

```
sefs-project/
├── backend/                    # Python backend
│   ├── main.py                # FastAPI server & WebSocket
│   ├── coordinator.py         # System orchestrator
│   ├── monitor.py             # File system watcher
│   ├── extractor.py           # Content extraction (PDF/text)
│   ├── semantic_engine.py     # ML clustering & embeddings
│   ├── os_manager.py          # OS folder operations
│   ├── state_manager.py       # State persistence
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # React frontend
│   └── sefs-ui/
│       ├── src/
│       │   ├── App.js         # Main application
│       │   ├── GravityView.js # D3.js visualization
│       │   └── ActivityFeed.js # Activity log component
│       ├── public/
│       └── package.json       # Node dependencies
│
├── sefs_root/                  # Monitored directory (created automatically)
│   ├── .sefs_state.json       # System state (auto-generated)
│   └── .sefs_history.json     # Clustering history (auto-generated)
│
├── create_demo_files.py        # Demo data generator
├── test_system.py              # Integration tests
├── test_e2e_workflow.py        # End-to-end tests
├── START.sh                    # Unix/Mac startup script
├── START.bat                   # Windows startup script
├── STARTUP_GUIDE.md            # Detailed startup instructions
├── DEMO_SCRIPT.md              # Complete demo guide
└── README.md                   # This file
```

---

## 🔧 Configuration

SEFS works with sensible defaults, but you can customize behavior by editing the backend files:

### Clustering Parameters
Edit `backend/semantic_engine.py`:
```python
# DBSCAN clustering parameters
eps=0.5              # Maximum distance between samples
min_samples=2        # Minimum cluster size
metric='cosine'      # Distance metric
```

### File Monitoring
Edit `backend/coordinator.py`:
```python
# Supported file extensions
SUPPORTED_EXTENSIONS = ['.pdf', '.txt']

# Content extraction limit
MAX_CONTENT_LENGTH = 5000  # characters
```

### Server Configuration
Edit `backend/main.py`:
```python
# Server settings
HOST = "0.0.0.0"
PORT = 8000
```

### Frontend Configuration
Edit `frontend/sefs-ui/src/GravityView.js`:
```javascript
// Polling interval for updates
const POLL_INTERVAL = 3000;  // milliseconds

// Visualization parameters
const GRAVITY_STRENGTH = 0.5;
const CHARGE_STRENGTH = -100;
```

---

## 🧪 Testing

SEFS includes comprehensive tests to verify functionality.

### Run Integration Tests
```bash
# From project root
python test_system.py
```

Tests include:
- Health check endpoint
- File indexing
- Clustering functionality
- Folder creation
- Graph data generation
- AI name generation

### Run End-to-End Tests
```bash
python test_e2e_workflow.py
```

Tests the complete workflow:
- File addition and detection
- Content extraction
- Semantic clustering
- OS folder synchronization
- State persistence

### Manual Testing Checklist
- [ ] Add a PDF file - verify it's processed
- [ ] Add a text file - verify it's processed
- [ ] Add multiple related files - verify they cluster together
- [ ] Check OS folders are created
- [ ] Verify files are moved to correct folders
- [ ] Restart system - verify state is restored
- [ ] Add file while running - verify real-time update
- [ ] Check activity feed shows events

---

## 🛠️ Troubleshooting

### Backend Issues

**Problem**: Backend won't start
- **Solution**: Check that port 8000 is not in use
- **Solution**: Verify Python dependencies: `pip install -r backend/requirements.txt`
- **Solution**: Check `backend/backend.log` for error messages

**Problem**: Files not being detected
- **Solution**: Verify files are in `sefs_root/` directory
- **Solution**: Ensure files are `.pdf` or `.txt` format
- **Solution**: Check file permissions (must be readable)
- **Solution**: Look for errors in backend logs

**Problem**: Clustering not working
- **Solution**: Ensure files have sufficient text content (>100 characters)
- **Solution**: Try adjusting DBSCAN parameters in `semantic_engine.py`
- **Solution**: Check that SentenceTransformers model downloaded correctly

**Problem**: AI naming fails
- **Solution**: Verify `OPENAI_API_KEY` is set in `.env` file
- **Solution**: Check API key is valid and has credits
- **Solution**: System will fall back to keyword-based naming automatically

### Frontend Issues

**Problem**: Frontend won't start
- **Solution**: Check that port 3000 is not in use
- **Solution**: Verify Node dependencies: `cd frontend/sefs-ui && npm install`
- **Solution**: Check `frontend/sefs-ui/frontend.log` for errors

**Problem**: Visualization not loading
- **Solution**: Verify backend is running at http://localhost:8000
- **Solution**: Check browser console for errors (F12)
- **Solution**: Try refreshing the page (F5)

**Problem**: Real-time updates not working
- **Solution**: Check WebSocket connection in browser console
- **Solution**: Verify backend WebSocket endpoint is accessible
- **Solution**: Try reconnecting by refreshing the page

### OS Integration Issues

**Problem**: Folders not created
- **Solution**: Check `sefs_root/` directory permissions (must be writable)
- **Solution**: Verify OS manager logs in backend
- **Solution**: Ensure folder names are OS-compatible

**Problem**: Files not moved
- **Solution**: Check file permissions (must be movable)
- **Solution**: Verify no other process is using the files
- **Solution**: Check for filename collisions

### Performance Issues

**Problem**: Slow processing
- **Solution**: Reduce file size or content length limit
- **Solution**: Ensure sufficient RAM available (4GB minimum)
- **Solution**: Check CPU usage - clustering is compute-intensive

**Problem**: High memory usage
- **Solution**: Limit number of files (system optimized for <100 files)
- **Solution**: Restart system to clear cached embeddings
- **Solution**: Reduce embedding model size (edit `semantic_engine.py`)

### Getting Help

If you encounter issues not covered here:
1. Check the logs: `backend/backend.log` and `frontend/sefs-ui/frontend.log`
2. Review the [STARTUP_GUIDE.md](STARTUP_GUIDE.md) for detailed setup instructions
3. Verify all prerequisites are installed correctly
4. Try the manual startup method to isolate issues
5. Check the API documentation at http://localhost:8000/docs

---

## 🔌 API Reference

### REST Endpoints

**GET /**
- Returns service information and version

**GET /health**
- Health check endpoint
- Returns: `{"status": "healthy"}`

**GET /files**
- List all indexed files
- Returns: `{"files": [...], "count": n}`

**GET /clusters**
- Get cluster information
- Returns: `{"clusters": {...}, "names": {...}}`

**GET /folders**
- Get OS folder structure
- Returns: `{"folders": [...]}`

**GET /graph**
- Get visualization data
- Returns: `{"nodes": [...], "clusters": [...]}`

**GET /state**
- Get complete system state
- Returns: `{"files": {...}, "clusters": {...}, "names": {...}}`

**GET /history**
- Get clustering history
- Returns: `{"history": [...]}`

**POST /reorganize**
- Manually trigger reorganization
- Returns: `{"status": "reorganized", "clusters": n}`

**POST /generate-names**
- Generate AI-powered folder names
- Returns: `{"status": "success", "names": {...}}`

### WebSocket

**WS /ws**
- Real-time updates endpoint
- Sends JSON messages on system events:
  - File additions
  - Clustering updates
  - Folder changes
  - Name generation

Example message:
```json
{
  "type": "update",
  "data": {
    "files": {...},
    "clusters": {...}
  }
}
```

---

## 🏗️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework with async support
- **Uvicorn** - ASGI server for FastAPI
- **Watchdog** - File system monitoring
- **SentenceTransformers** - Semantic embeddings (all-MiniLM-L6-v2 model)
- **scikit-learn** - DBSCAN clustering algorithm
- **PyPDF2** - PDF text extraction
- **CrewAI** - AI agent framework for intelligent naming (optional)
- **WebSockets** - Real-time communication

### Frontend
- **React** - UI framework
- **D3.js** - Data visualization and force simulation
- **Axios** - HTTP client for API calls

### Machine Learning
- **Semantic Embeddings** - 384-dimensional vectors from SentenceTransformers
- **DBSCAN Clustering** - Density-based spatial clustering with cosine similarity
- **Force Simulation** - Physics-based layout for visualization

### Storage
- **Local Filesystem** - OS-level folder management
- **JSON** - State persistence (`.sefs_state.json`, `.sefs_history.json`)

---

## 📄 License

MIT License

Copyright (c) 2024 SEFS Project

Built for AI-Week Hackathon at VNR VJIET

---

## 🙏 Acknowledgments

- **SentenceTransformers** for semantic embedding models
- **FastAPI** for the excellent web framework
- **D3.js** for powerful visualization capabilities
- **CrewAI** for AI agent orchestration
- **VNR VJIET** for hosting the AI-Week Hackathon

---

## 🚀 Future Enhancements

Potential improvements for future versions:

- **File Type Support**: DOCX, PPTX, images with OCR, code files
- **Multi-Level Hierarchies**: Nested folder structures for complex organization
- **Manual Override**: Drag-and-drop to manually adjust clusters
- **Search Functionality**: Full-text search across all indexed files
- **Cloud Integration**: Sync with Google Drive, Dropbox, OneDrive
- **Mobile App**: iOS/Android companion apps
- **Browser Extension**: Organize downloads automatically
- **Collaborative Features**: Shared organization spaces
- **Custom Models**: Fine-tune embeddings for specific domains
- **Timeline View**: Visualize organization history over time
- **Export/Import**: Share organization schemes
- **Advanced Analytics**: Insights into file relationships and patterns

---

## 📚 Additional Documentation

- **[GEMINI_SETUP.md](GEMINI_SETUP.md)** - Complete guide for setting up free Gemini AI naming
- **[STARTUP_GUIDE.md](STARTUP_GUIDE.md)** - Detailed startup instructions and troubleshooting
- **[DEMO_SCRIPT.md](DEMO_SCRIPT.md)** - Complete demo guide with timing and talking points
- **API Documentation** - Interactive docs at http://localhost:8000/docs (when running)

---

**Ready to experience the future of file organization? Get started now!** 🎉
