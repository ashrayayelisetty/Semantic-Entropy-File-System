"""SEFS FastAPI Backend
Main API server"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, UploadFile, File
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
    """Get cluster and file data for box visualization"""
    if not coordinator:
        return JSONResponse(
            status_code=503,
            content={"error": "System not initialized"}
        )
    
    state = coordinator.get_current_state()
    
    # Build clusters and files data
    clusters_dict = {}
    files = []
    cluster_assignments = coordinator.semantic_engine.cluster_assignments
    folder_to_cluster_id = {}  # Map folder names to unique cluster IDs
    next_cluster_id = 0
    
    for file_path in state['files']:
        file_path_obj = Path(file_path)
        parent_folder = file_path_obj.parent.name
        
        # Determine cluster based on folder
        if parent_folder == "sefs_root":
            # Files in root go to Uncategorized
            cluster_key = "uncategorized"
            cluster_name = "Uncategorized"
        else:
            # Each folder gets its own cluster
            if parent_folder not in folder_to_cluster_id:
                folder_to_cluster_id[parent_folder] = str(next_cluster_id)
                next_cluster_id += 1
            cluster_key = folder_to_cluster_id[parent_folder]
            cluster_name = parent_folder
        
        # Track cluster
        if cluster_key not in clusters_dict:
            clusters_dict[cluster_key] = {
                "id": cluster_key,
                "name": cluster_name,
                "fileCount": 0
            }
        clusters_dict[cluster_key]["fileCount"] += 1
        
        # Get file metadata
        try:
            file_stat = file_path_obj.stat()
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
        
        files.append({
            "id": file_path,
            "label": file_path_obj.name,
            "cluster": cluster_key,
            "clusterName": cluster_name,
            "size": size_str,
            "modified": date_str,
            "path": file_path
        })
    
    return {
        "clusters": list(clusters_dict.values()),
        "files": files
    }


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


@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file to sefs_root directory
    
    Args:
        file: Uploaded file from multipart/form-data
    
    Returns:
        JSON response with status, filename, and path
    """
    if not coordinator:
        return JSONResponse(
            status_code=503,
            content={"error": "System not initialized"}
        )
    
    try:
        # Validate file exists
        if not file or not file.filename:
            return JSONResponse(
                status_code=400,
                content={"error": "No file provided"}
            )
        
        # Generate safe filename
        original_filename = file.filename
        safe_filename = Path(original_filename).name  # Remove any path components
        
        # Handle duplicate filenames
        target_path = ROOT_DIR / safe_filename
        counter = 1
        while target_path.exists():
            stem = Path(safe_filename).stem
            suffix = Path(safe_filename).suffix
            safe_filename = f"{stem}_{counter}{suffix}"
            target_path = ROOT_DIR / safe_filename
            counter += 1
        
        # Save file
        content = await file.read()
        with open(target_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"File uploaded: {safe_filename}")
        
        return {
            "status": "success",
            "filename": original_filename,
            "path": str(target_path)
        }
    
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to upload file: {str(e)}"}
        )


@app.delete("/delete-file/{file_path:path}")
def delete_file(file_path: str):
    """Delete a file from the system"""
    if not coordinator:
        return JSONResponse(
            status_code=503,
            content={"error": "System not initialized"}
        )
    
    try:
        # Resolve current path
        current_path = coordinator.state_manager.resolve_current_path(file_path)
        
        if not current_path:
            return JSONResponse(
                status_code=404,
                content={"error": "File not found"}
            )
        
        file_obj = Path(current_path)
        
        # Security check - ensure file is within sefs_root
        root_path = Path(ROOT_DIR).resolve()
        try:
            file_resolved = file_obj.resolve()
            if not str(file_resolved).startswith(str(root_path)):
                return JSONResponse(
                    status_code=403,
                    content={"error": "Access denied"}
                )
        except Exception:
            return JSONResponse(
                status_code=404,
                content={"error": "File not found"}
            )
        
        # Get parent folder before deleting
        parent_folder = file_obj.parent
        
        # Delete the file
        if file_obj.exists():
            file_obj.unlink()
            logger.info(f"File deleted: {file_obj.name}")
            
            # Check if parent folder is now empty and delete it
            if parent_folder != root_path and parent_folder.exists():
                # Check if folder is empty (no files, only possibly .gitkeep or hidden files)
                remaining_files = [f for f in parent_folder.iterdir() if not f.name.startswith('.')]
                if len(remaining_files) == 0:
                    try:
                        parent_folder.rmdir()
                        logger.info(f"Deleted empty folder: {parent_folder.name}")
                    except Exception as e:
                        logger.warning(f"Could not delete folder {parent_folder.name}: {e}")
            
            return {"status": "success", "message": f"Deleted {file_obj.name}"}
        else:
            return JSONResponse(
                status_code=404,
                content={"error": "File not found"}
            )
    
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to delete file: {str(e)}"}
        )


@app.post("/rename-file")
async def rename_file(data: dict):
    """Rename a file"""
    if not coordinator:
        return JSONResponse(
            status_code=503,
            content={"error": "System not initialized"}
        )
    
    try:
        old_path = data.get("oldPath")
        new_name = data.get("newName")
        
        if not old_path or not new_name:
            return JSONResponse(
                status_code=400,
                content={"error": "Missing oldPath or newName"}
            )
        
        # Resolve current path
        current_path = coordinator.state_manager.resolve_current_path(old_path)
        
        if not current_path:
            return JSONResponse(
                status_code=404,
                content={"error": "File not found"}
            )
        
        old_file = Path(current_path)
        
        # Security check
        root_path = Path(ROOT_DIR).resolve()
        try:
            old_resolved = old_file.resolve()
            if not str(old_resolved).startswith(str(root_path)):
                return JSONResponse(
                    status_code=403,
                    content={"error": "Access denied"}
                )
        except Exception:
            return JSONResponse(
                status_code=404,
                content={"error": "File not found"}
            )
        
        # Create new path in same directory
        new_file = old_file.parent / new_name
        
        # Check if new name already exists
        if new_file.exists():
            return JSONResponse(
                status_code=400,
                content={"error": "A file with that name already exists"}
            )
        
        # Rename the file
        old_file.rename(new_file)
        logger.info(f"File renamed: {old_file.name} -> {new_name}")
        
        return {
            "status": "success",
            "message": f"Renamed to {new_name}",
            "newPath": str(new_file)
        }
    
    except Exception as e:
        logger.error(f"Error renaming file: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to rename file: {str(e)}"}
        )


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
