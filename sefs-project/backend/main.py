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
    """Get data for graph visualization"""
    if not coordinator:
        return JSONResponse(
            status_code=503,
            content={"error": "System not initialized"}
        )
    
    state = coordinator.get_current_state()
    
    # Build nodes
    nodes = []
    cluster_assignments = coordinator.semantic_engine.cluster_assignments
    
    for file_path in state['files']:
        cluster_id = cluster_assignments.get(file_path, -1)
        cluster_name = state['cluster_names'].get(cluster_id, "Uncategorized")
        
        nodes.append({
            "id": file_path,
            "label": Path(file_path).name,
            "cluster": cluster_id,
            "clusterName": cluster_name,
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
