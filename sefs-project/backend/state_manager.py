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
        self._migrate_legacy_state()
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
    
    def update_file(self, file_path, cluster_id, content_preview, current_path=None):
        """Update file information"""
        self.state['files'][file_path] = {
            'cluster': cluster_id,
            'preview': content_preview,
            'updated': datetime.now().isoformat(),
            'current_path': current_path or file_path
        }
        self.save_state()
    
    def update_file_location(self, original_path, new_path):
        """Update the physical location of a file"""
        if original_path in self.state['files']:
            self.state['files'][original_path]['current_path'] = new_path
            self.save_state()
            logger.info(f"Updated file location: {Path(original_path).name} -> {new_path}")
    
    def resolve_current_path(self, file_identifier):
        """Resolve the current physical path for a file"""
        if file_identifier in self.state['files']:
            file_data = self.state['files'][file_identifier]
            current_path = file_data.get('current_path', file_identifier)
            
            # Verify file exists at current path
            if Path(current_path).exists():
                return current_path
            
            # Fallback: check if file exists at original identifier
            if Path(file_identifier).exists():
                return file_identifier
        
        # Try to find file by name in semantic folders
        file_name = Path(file_identifier).name
        for root_file in Path(self.root).rglob(file_name):
            if root_file.is_file():
                logger.info(f"Found file by search: {root_file}")
                return str(root_file)
        
        return None
    
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
    
    def _migrate_legacy_state(self):
        """Migrate old state format to include current_path field"""
        migrated = False
        
        for file_path, file_data in self.state['files'].items():
            if 'current_path' not in file_data:
                # Try to find the file's current location
                original_path = Path(file_path)
                file_name = original_path.name
                
                # Check if file exists at original location
                if original_path.exists():
                    file_data['current_path'] = file_path
                    migrated = True
                else:
                    # Search for file in semantic folders
                    found = False
                    for found_file in self.root.rglob(file_name):
                        if found_file.is_file():
                            file_data['current_path'] = str(found_file)
                            migrated = True
                            found = True
                            logger.info(f"Migrated path for {file_name}: {found_file}")
                            break
                    
                    if not found:
                        # File not found, use original path as fallback
                        file_data['current_path'] = file_path
                        migrated = True
        
        if migrated:
            self.save_state()
            logger.info("State migration completed")
