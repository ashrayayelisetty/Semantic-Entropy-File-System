"""System Coordinator
Orchestrates all SEFS components"""

from monitor import FileWatcher
from extractor import ContentExtractor
from semantic_engine import SemanticEngine
from os_manager import OSManager
from state_manager import StateManager
from ai_namer import get_ai_namer
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SEFSCoordinator:
    """Main system coordinator"""
    
    def __init__(self, root_path):
        """Initialize all components"""
        self.root = Path(root_path)
        
        # Initialize components
        self.watcher = FileWatcher(root_path)
        self.extractor = ContentExtractor()
        self.semantic_engine = SemanticEngine()
        self.os_manager = OSManager(root_path)
        self.state_manager = StateManager(root_path)
        self.ai_namer = get_ai_namer()
        self.cluster_names = {}
        
        logger.info("SEFS Coordinator initialized")
    
    def start(self):
        """Start the system"""
        self.watcher.start()
        
        # Process existing files
        self._process_existing_files()
        
        logger.info("SEFS system started")
    
    def stop(self):
        """Stop the system"""
        self.watcher.stop()
        logger.info("SEFS system stopped")
    
    def _process_existing_files(self):
        """Process all existing files in root"""
        files = self.watcher.get_all_files()
        logger.info(f"Processing {len(files)} existing files")
        
        for file_path in files:
            self._process_file(file_path)
        
        if files:
            self._reorganize()
    
    def _process_file(self, file_path):
        """Process a single file"""
        try:
            # Extract content
            content = self.extractor.extract_content(file_path)
            
            if content:
                # Add to semantic index
                self.semantic_engine.add_file(file_path, content)
                logger.info(f"Processed: {Path(file_path).name}")
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
    
    def _reorganize(self):
        """Reorganize files based on clustering"""
        # Cluster files
        cluster_assignments = self.semantic_engine.cluster_files()
        
        if not cluster_assignments:
            return
        
        # Generate cluster names (simplified for now)
        self._generate_cluster_names(cluster_assignments)
        
        # Sync with OS - returns dict of moved files
        moved_files = self.os_manager.sync_clusters(
            cluster_assignments,
            self.cluster_names
        )
        
        # Update state with new file locations
        for file_path, cluster_id in cluster_assignments.items():
            # Get the new path if file was moved
            current_path = moved_files.get(file_path, file_path)
            
            self.state_manager.update_file(
                file_path,
                cluster_id,
                self.semantic_engine.file_contents.get(file_path, ""),
                current_path=current_path
            )
        
        # Add to history
        self.state_manager.add_history_snapshot(
            cluster_assignments,
            self.cluster_names
        )
        
        logger.info("Reorganization complete")
    
    def _generate_cluster_names(self, cluster_assignments):
        """Generate names for clusters using AI or fallback"""
        try:
            # Use AI namer
            self.cluster_names = self.ai_namer.generate_names(
                cluster_assignments,
                self.semantic_engine.file_contents
            )
            logger.info(f"Generated names for {len(self.cluster_names)} clusters")
        except Exception as e:
            logger.error(f"Error generating cluster names: {e}")
            # Fallback to simple naming
            self.cluster_names = {
                cid: f"Cluster_{cid}" if cid != -1 else "Uncategorized"
                for cid in set(cluster_assignments.values())
            }
    
    def process_events(self):
        """Process pending file events"""
        events = self.watcher.get_events()
        
        if not events:
            return False
        
        for event_type, file_path in events:
            if event_type in ['created', 'modified']:
                self._process_file(file_path)
            elif event_type == 'deleted':
                self.semantic_engine.remove_file(file_path)
        
        # Reorganize after processing events
        self._reorganize()
        
        return True
    
    def get_current_state(self):
        """Get current system state - includes all files (root and organized)"""
        import glob
        
        # Get files from semantic engine (currently being processed)
        processing_files = list(self.semantic_engine.file_embeddings.keys())
        
        # Also get all files in organized folders
        all_files = []
        for pattern in ['**/*.txt', '**/*.pdf']:
            all_files.extend(glob.glob(str(self.root / pattern), recursive=True))
        
        # Combine and deduplicate
        all_file_paths = list(set(processing_files + all_files))
        
        return {
            'files': all_file_paths,
            'clusters': self.semantic_engine.get_cluster_stats(),
            'folders': self.os_manager.get_folder_structure(),
            'cluster_names': self.cluster_names
        }
