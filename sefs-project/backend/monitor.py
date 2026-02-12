"""File System Monitor for SEFS
Watches a root directory for PDF and text file changes"""

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import queue
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SEFSEventHandler(FileSystemEventHandler):
    """Handles file system events for SEFS"""
    
    def __init__(self, event_queue):
        self.queue = event_queue
        self.supported_extensions = {'.pdf', '.txt'}
    
    def _is_supported_file(self, path):
        """Check if file should be processed"""
        return Path(path).suffix.lower() in self.supported_extensions
    
    def on_created(self, event):
        if not event.is_directory and self._is_supported_file(event.src_path):
            self.queue.put(('created', event.src_path))
            logger.info(f"[MONITOR] File created: {event.src_path}")
    
    def on_modified(self, event):
        if not event.is_directory and self._is_supported_file(event.src_path):
            self.queue.put(('modified', event.src_path))
            logger.info(f"[MONITOR] File modified: {event.src_path}")
    
    def on_deleted(self, event):
        if event.is_directory:
            self.queue.put(('directory_deleted', event.src_path))
            logger.info(f"[MONITOR] Directory deleted: {event.src_path}")
        elif self._is_supported_file(event.src_path):
            self.queue.put(('deleted', event.src_path))
            logger.info(f"[MONITOR] File deleted: {event.src_path}")


class FileWatcher:
    """Main file watching service"""
    
    def __init__(self, root_path):
        self.root = Path(root_path)
        self.root.mkdir(exist_ok=True)
        self.queue = queue.Queue()
        self.observer = Observer()
        self.running = False
    
    def start(self):
        """Start monitoring the directory"""
        handler = SEFSEventHandler(self.queue)
        self.observer.schedule(handler, str(self.root), recursive=True)
        self.observer.start()
        self.running = True
        logger.info(f"[MONITOR] Watching directory: {self.root}")
    
    def stop(self):
        """Stop monitoring"""
        self.observer.stop()
        self.observer.join()
        self.running = False
        logger.info("[MONITOR] Stopped watching")
    
    def get_events(self):
        """Retrieve all pending events"""
        events = []
        while not self.queue.empty():
            try:
                events.append(self.queue.get_nowait())
            except queue.Empty:
                break
        return events
    
    def get_all_files(self):
        """Get all supported files in the root directory"""
        files = []
        for file_path in self.root.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in {'.pdf', '.txt'}:
                files.append(str(file_path))
        return files
