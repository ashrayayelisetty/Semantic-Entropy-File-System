"""SEFS FastAPI Backend
Main API server"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
import logging
from pathlib import Path
import os

# Try to load environment variables from .env file (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logging.warning("python-dotenv not installed. Environment variables from .env file will not be loaded.")

from coordinator import SEFSCoordinator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
ROOT_DIR = Path(__file__).parent.parent / "sefs_root"
ROOT_DIR.mkdir(exist_ok=True)

# Global coordinator
coordinator = None
active_websockets = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global coordinator
    
    # Startup
    logger.info("Starting SEFS system")
    coordinator = SEFSCoordinator(str(ROOT_DIR))
    coordinator.start()
    
    # Start background processing
    asyncio.create_task(process_file_events())
    
    yield
    
    # Shutdown
    logger.info("Stopping SEFS system")
    coordinator.stop()


app = FastAPI(
    title="SEFS API",
    description="Semantic Entropy File System API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Background task for processing file events
async def process_file_events():
    """Process file events in background"""
    while True:
        try:
            if coordinator and coordinator.process_events():
                # Notify websocket clients
                state = coordinator.get_current_state()
                await broadcast_update(state)
            
            await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"Error in event processing: {e}")
            await asyncio.sleep(5)


async def broadcast_update(data):
    """Broadcast update to all connected websockets"""
    disconnected = []
    
    for ws in active_websockets:
        try:
            await ws.send_json(data)
        except:
            disconnected.append(ws)
    
    # Remove disconnected clients
    for ws in disconnected:
        active_websockets.remove(ws)


# REST API Endpoints

@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "service": "SEFS API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "coordinator": "running" if coordinator else "not initialized"
    }


@app.get("/files")
def get_files():
    """Get all indexed files"""
    if not coordinator:
        return JSONResponse(
            status_code=503,
            content={"error": "System not initialized"}
        )
    
    state = coordinator.get_current_state()
    return {
        "files": state['files'],
        "count": len(state['files'])
    }


@app.get("/clusters")
def get_clusters():
    """Get cluster information"""
    if not coordinator:
        return JSONResponse(
            status_code=503,
            content={"error": "System not initialized"}
        )
    
    state = coordinator.get_current_state()
    return {
        "clusters": state['clusters'],
        "names": state['cluster_names']
    }


@app.get("/folders")
def get_folders():
    """Get OS folder structure"""
    if not coordinator:
        return JSONResponse(
            status_code=503,
            content={"error": "System not initialized"}
        )
    
    state = coordinator.get_current_state()
    return {"folders": state['folders']}


@app.get("/graph")
def get_graph_data():
    """Get data for graph visualization with metadata"""
    if not coordinator:
        return JSONResponse(
            status_code=503,
            content={"error": "System not initialized"}
        )
    
    state = coordinator.get_current_state()
    
    # Build nodes with metadata
    nodes = []
    cluster_assignments = coordinator.semantic_engine.cluster_assignments
    
    for file_path in state['files']:
        # Determine cluster - either from assignments or from folder name
        cluster_id = cluster_assignments.get(file_path, -1)
        
        # If not in assignments, try to determine from folder
        if cluster_id == -1:
            file_path_obj = Path(file_path)
            parent_folder = file_path_obj.parent.name
            
            # Try to match folder name to cluster names
            cluster_name = parent_folder if parent_folder != "sefs_root" else "Uncategorized"
            
            # Find cluster ID by name
            for cid, cname in state['cluster_names'].items():
                if cname == parent_folder:
                    cluster_id = cid
                    break
        else:
            cluster_name = state['cluster_names'].get(cluster_id, "Uncategorized")
        
        # If still no cluster name, use folder name
        if cluster_id == -1:
            file_path_obj = Path(file_path)
            parent_folder = file_path_obj.parent.name
            cluster_name = parent_folder if parent_folder != "sefs_root" else "Uncategorized"
        
        # Get file metadata
        try:
            file_stat = Path(file_path).stat()
            file_size = file_stat.st_size
            modified_time = file_stat.st_mtime
            
            # Format size
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            
            # Format date
            from datetime import datetime
            date_str = datetime.fromtimestamp(modified_time).strftime("%Y-%m-%d %H:%M:%S")
            
        except Exception as e:
            size_str = "Unknown"
            date_str = "Unknown"
        
        nodes.append({
            "id": file_path,
            "label": Path(file_path).name,
            "cluster": cluster_id,
            "clusterName": cluster_name,
            "size": size_str,
            "modified": date_str,
            "path": file_path,
            "x": 0,
            "y": 0
        })
    
    return {"nodes": nodes}


@app.get("/state")
def get_state():
    """Get complete system state"""
    if not coordinator:
        return JSONResponse(
            status_code=503,
            content={"error": "System not initialized"}
        )
    
    return coordinator.get_current_state()


@app.get("/history")
def get_history():
    """Get clustering history"""
    if not coordinator:
        return JSONResponse(
            status_code=503,
            content={"error": "System not initialized"}
        )
    
    return {"history": coordinator.state_manager.get_history()}


@app.post("/reorganize")
async def trigger_reorganization(background_tasks: BackgroundTasks):
    """Manually trigger reorganization"""
    if not coordinator:
        return JSONResponse(
            status_code=503,
            content={"error": "System not initialized"}
        )
    
    background_tasks.add_task(coordinator._reorganize)
    return {"status": "reorganization triggered"}


@app.post("/generate-names")
async def generate_names(background_tasks: BackgroundTasks):
    """Generate AI-powered cluster names"""
    if not coordinator:
        return JSONResponse(
            status_code=503,
            content={"error": "System not initialized"}
        )
    
    # Check if we have cluster names to regenerate
    if not coordinator.cluster_names:
        return JSONResponse(
            status_code=400,
            content={"error": "No clusters available. Please add files and reorganize first."}
        )
    
    # Note: After files are moved, cluster_assignments may be empty
    # The AI naming feature would need to be called during reorganization
    # or we'd need to maintain cluster assignments after file moves
    # For now, return success as the names were already generated during reorganization
    return {
        "status": "cluster names already generated",
        "message": "Names are generated automatically during reorganization",
        "cluster_names": coordinator.cluster_names
    }


@app.get("/open-file/{file_path:path}")
def open_file(file_path: str):
    """Open a file in the default system application"""
    import os
    import subprocess
    import platform
    
    try:
        if not coordinator:
            return JSONResponse(
                status_code=503,
                content={"error": "System not initialized"}
            )
        
        # Resolve current path from state
        current_path = coordinator.state_manager.resolve_current_path(file_path)
        
        if not current_path:
            return JSONResponse(
                status_code=404,
                content={"error": f"File not found: {Path(file_path).name}"}
            )
        
        full_path = Path(current_path)
        
        # Security check - ensure file is within sefs_root
        root_path = Path(ROOT_DIR).resolve()
        try:
            full_path_resolved = full_path.resolve()
            if not str(full_path_resolved).startswith(str(root_path)):
                return JSONResponse(
                    status_code=403,
                    content={"error": "Access denied: file outside root directory"}
                )
        except Exception:
            return JSONResponse(
                status_code=404,
                content={"error": "File not found"}
            )
        
        # Verify file exists
        if not full_path.exists():
            return JSONResponse(
                status_code=404,
                content={"error": f"File not found: {full_path.name}"}
            )
        
        # Open file with default application
        system = platform.system()
        if system == "Windows":
            os.startfile(str(full_path))
        elif system == "Darwin":  # macOS
            subprocess.run(["open", str(full_path)])
        else:  # Linux
            subprocess.run(["xdg-open", str(full_path)])
        
        return {"status": "success", "message": f"Opened {full_path.name}"}
    
    except Exception as e:
        logger.error(f"Error opening file: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to open file: {str(e)}"}
        )


@app.get("/logs")
def get_logs():
    """Get recent system logs"""
    try:
        log_file = Path(__file__).parent / "backend.log"
        if log_file.exists():
            # Read last 100 lines
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                recent_logs = lines[-100:] if len(lines) > 100 else lines
                return {"logs": "".join(recent_logs)}
        return {"logs": "No logs available"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to read logs: {str(e)}"}
        )


# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket connection for live updates"""
    await websocket.accept()
    active_websockets.append(websocket)
    logger.info("WebSocket client connected")
    
    try:
        # Send initial state
        if coordinator:
            state = coordinator.get_current_state()
            await websocket.send_json(state)
        
        # Keep connection alive
        while True:
            # Wait for client messages (ping/pong)
            await websocket.receive_text()
    
    except WebSocketDisconnect:
        active_websockets.remove(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in active_websockets:
            active_websockets.remove(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
