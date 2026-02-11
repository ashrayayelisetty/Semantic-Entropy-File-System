"""State Manager for SEFS
Handles persistence of system state"""

import json
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StateManager:
    """Manages system state persistence"""
    
    def __init__(self, root_path):
        """Initialize state manager
        
        Args:
            root_path: Root directory containing SEFS data
        """
        self.root = Path(root_path)
        self.state_file = self.root / '.sefs_state.json'
        self.history_file = self.root / '.sefs_history.json'
        self.state = self._load_state()
        self.history = self._load_history()
        logger.info("State manager initialized")
    
    def _load_state(self):
        """Load state from disk"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading state: {e}")
        
        return {
            'files': {},
            'clusters': {},
            'last_updated': None
        }
    
    def _load_history(self):
        """Load clustering history"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading history: {e}")
        
        return []
    
    def save_state(self):
        """Save current state to disk"""
        self.state['last_updated'] = datetime.now().isoformat()
        
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
            logger.info("State saved")
        except Exception as e:
            logger.error(f"Error saving state: {e}")
    
    def save_history(self):
        """Save history to disk"""
        try:
            # Keep only last 50 history entries
            if len(self.history) > 50:
                self.history = self.history[-50:]
            
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving history: {e}")
    
    def update_file(self, file_path, cluster_id, content_preview):
        """Update file information"""
        self.state['files'][file_path] = {
            'cluster': cluster_id,
            'preview': content_preview,
            'updated': datetime.now().isoformat()
        }
        self.save_state()
    
    def update_cluster(self, cluster_id, folder_name, file_count):
        """Update cluster information"""
        self.state['clusters'][str(cluster_id)] = {
            'name': folder_name,
            'file_count': file_count,
            'updated': datetime.now().isoformat()
        }
        self.save_state()
    
    def add_history_snapshot(self, cluster_assignments, cluster_names):
        """Add a clustering snapshot to history"""
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'assignments': cluster_assignments,
            'names': cluster_names
        }
        self.history.append(snapshot)
        self.save_history()
    
    def get_state(self):
        """Get current state"""
        return self.state
    
    def get_history(self):
        """Get clustering history"""
        return self.history
