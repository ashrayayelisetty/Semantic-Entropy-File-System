"""OS Manager for SEFS
Handles all operating system level file operations"""

import shutil
from pathlib import Path
import logging
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OSManager:
    """Manages OS-level file and folder operations"""
    
    def __init__(self, root_path):
        """Initialize OS Manager
        
        Args:
            root_path: Root directory to manage
        """
        self.root = Path(root_path)
        self.root.mkdir(exist_ok=True)
        self.semantic_folders = {}  # cluster_id -> folder_path
        self.folder_names = {}      # cluster_id -> folder_name
        logger.info(f"OS Manager initialized for: {self.root}")
    
    def create_semantic_folder(self, cluster_id, folder_name):
        """Create a semantic folder
        
        Args:
            cluster_id: Cluster identifier
            folder_name: Name for the folder
            
        Returns:
            Path object for created folder
        """
        # Sanitize folder name
        safe_name = self._sanitize_folder_name(folder_name)
        folder_path = self.root / safe_name
        
        # Create folder if it doesn't exist
        folder_path.mkdir(exist_ok=True)
        
        self.semantic_folders[cluster_id] = folder_path
        self.folder_names[cluster_id] = safe_name
        
        logger.info(f"Created folder: {safe_name} (Cluster {cluster_id})")
        return folder_path
    
    def delete_semantic_folder(self, cluster_id):
        """Delete a semantic folder if it's empty"""
        if cluster_id not in self.semantic_folders:
            return False
        
        folder_path = self.semantic_folders[cluster_id]
        
        try:
            # Only delete if empty
            if folder_path.exists() and not list(folder_path.iterdir()):
                folder_path.rmdir()
                logger.info(f"Deleted empty folder: {folder_path.name}")
                del self.semantic_folders[cluster_id]
                del self.folder_names[cluster_id]
                return True
        except Exception as e:
            logger.error(f"Error deleting folder {folder_path}: {e}")
        
        return False
    
    def move_file(self, file_path, cluster_id):
        """Move file to cluster folder
        
        Args:
            file_path: Path to file
            cluster_id: Target cluster
            
        Returns:
            New file path or None if failed
        """
        source = Path(file_path)
        
        if not source.exists():
            logger.warning(f"Source file not found: {file_path}")
            return None
        
        if cluster_id not in self.semantic_folders:
            logger.warning(f"Cluster folder not found: {cluster_id}")
            return None
        
        dest_folder = self.semantic_folders[cluster_id]
        dest = dest_folder / source.name
        
        # Handle name collision
        if dest.exists() and dest != source:
            base_name = source.stem
            extension = source.suffix
            counter = 1
            while dest.exists():
                new_name = f"{base_name}_{counter}{extension}"
                dest = dest_folder / new_name
                counter += 1
        
        # Skip if already in correct location
        if source == dest:
            return str(dest)
        
        try:
            shutil.move(str(source), str(dest))
            logger.info(f"Moved: {source.name} -> {dest_folder.name}/")
            return str(dest)
        except Exception as e:
            logger.error(f"Error moving file {source} to {dest}: {e}")
            return None
    
    def sync_clusters(self, cluster_assignments: Dict[str, int], cluster_names: Dict[int, str]):
        """Synchronize OS folders with cluster assignments
        
        Args:
            cluster_assignments: file_path -> cluster_id mapping
            cluster_names: cluster_id -> name mapping
            
        Returns:
            Dictionary of moved files
        """
        moved_files = {}
        
        # Group files by cluster
        clusters = {}
        for file_path, cluster_id in cluster_assignments.items():
            if cluster_id not in clusters:
                clusters[cluster_id] = []
            clusters[cluster_id].append(file_path)
        
        # Create folders and move files
        for cluster_id, files in clusters.items():
            # Get folder name
            if cluster_id == -1:
                folder_name = "Uncategorized"
            else:
                folder_name = cluster_names.get(cluster_id, f"Cluster_{cluster_id}")
            
            # Create folder
            self.create_semantic_folder(cluster_id, folder_name)
            
            # Move files
            for file_path in files:
                new_path = self.move_file(file_path, cluster_id)
                if new_path:
                    moved_files[file_path] = new_path
        
        # Clean up empty folders
        self._cleanup_empty_folders()
        
        return moved_files
    
    def get_folder_structure(self):
        """Get current folder structure"""
        structure = []
        
        for folder_path in self.root.iterdir():
            if folder_path.is_dir() and not folder_path.name.startswith('.'):
                files = [
                    f.name for f in folder_path.iterdir()
                    if f.is_file() and f.suffix.lower() in {'.pdf', '.txt'}
                ]
                structure.append({
                    'name': folder_path.name,
                    'path': str(folder_path),
                    'files': files,
                    'count': len(files)
                })
        
        return structure
    
    def _sanitize_folder_name(self, name):
        """Sanitize folder name for OS compatibility"""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        
        # Limit length
        if len(name) > 50:
            name = name[:50]
        
        # Remove leading/trailing spaces and dots
        name = name.strip(' .')
        
        # Ensure name is not empty
        if not name:
            name = "Unnamed_Folder"
        
        return name
    
    def _cleanup_empty_folders(self):
        """Remove empty semantic folders"""
        for folder_path in self.root.iterdir():
            if folder_path.is_dir() and not folder_path.name.startswith('.'):
                if not list(folder_path.iterdir()):
                    try:
                        folder_path.rmdir()
                        logger.info(f"Cleaned up empty folder: {folder_path.name}")
                    except Exception as e:
                        logger.error(f"Error cleaning folder {folder_path}: {e}")
