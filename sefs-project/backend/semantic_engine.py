"""Semantic Engine for SEFS
Handles embeddings, clustering, and similarity computation"""

from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SemanticEngine:
    """Main semantic processing engine"""
    
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """Initialize semantic engine
        
        Args:
            model_name: SentenceTransformer model to use
        """
        logger.info(f"Loading model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.file_embeddings = {}  # file_path -> embedding
        self.file_contents = {}    # file_path -> content preview
        self.cluster_assignments = {}  # file_path -> cluster_id
        logger.info("Semantic engine initialized")
    
    def add_file(self, file_path, content):
        """Add a file to the semantic index
        
        Args:
            file_path: Path to the file
            content: Extracted text content
        """
        if not content or len(content.strip()) < 10:
            logger.warning(f"Content too short for {file_path}")
            return
        
        # Generate embedding (limit to first 5000 chars)
        embedding = self.model.encode(content[:5000])
        self.file_embeddings[file_path] = embedding
        self.file_contents[file_path] = content[:500]  # Store preview
        logger.info(f"Added file to index: {Path(file_path).name}")
    
    def remove_file(self, file_path):
        """Remove a file from the index"""
        self.file_embeddings.pop(file_path, None)
        self.file_contents.pop(file_path, None)
        self.cluster_assignments.pop(file_path, None)
        logger.info(f"Removed file from index: {Path(file_path).name}")

    def remove_directory(self, dir_path):
        """Remove all files under a directory from the index"""
        dir_str = str(dir_path).rstrip('\\/') + Path(dir_path).anchor[-1] # Ensure trailing slash for prefix match
        # Fallback to simple check if anchor trick fails
        if not dir_str.endswith(('\\', '/')):
            dir_str += '\\' if '\\' in dir_str else '/'
            
        all_paths = list(self.file_embeddings.keys())
        removed_count = 0
        for fp in all_paths:
            if fp.startswith(dir_str):
                self.remove_file(fp)
                removed_count += 1
        if removed_count > 0:
            logger.info(f"Removed {removed_count} files from index due to directory deletion: {dir_path}")
    
    def cluster_files(self, eps=0.5, min_samples=2):
        """Cluster files using DBSCAN
        
        Args:
            eps: DBSCAN epsilon parameter (similarity threshold)
            min_samples: Minimum samples per cluster
            
        Returns:
            Dictionary mapping file_path to cluster_id
        """
        if len(self.file_embeddings) < 2:
            # Handle single file or empty case
            if len(self.file_embeddings) == 1:
                file_path = list(self.file_embeddings.keys())[0]
                self.cluster_assignments = {file_path: 0}
                return self.cluster_assignments
            return {}
        
        # Prepare data for clustering
        file_paths = list(self.file_embeddings.keys())
        embeddings = np.array([self.file_embeddings[fp] for fp in file_paths])
        
        # Perform clustering
        clustering = DBSCAN(
            eps=eps,
            min_samples=min_samples,
            metric='cosine'
        )
        labels = clustering.fit_predict(embeddings)
        
        # Create cluster assignment dictionary
        self.cluster_assignments = {
            file_paths[i]: int(labels[i])
            for i in range(len(file_paths))
        }
        
        # Log cluster distribution
        unique_clusters = set(labels)
        logger.info(f"Created {len(unique_clusters)} clusters")
        for cluster_id in unique_clusters:
            count = sum(1 for label in labels if label == cluster_id)
            logger.info(f"  Cluster {cluster_id}: {count} files")
        
        return self.cluster_assignments
    
    def get_cluster_contents(self, cluster_id):
        """Get content previews for all files in a cluster"""
        files_in_cluster = [
            fp for fp, cid in self.cluster_assignments.items()
            if cid == cluster_id
        ]
        return {
            fp: self.file_contents.get(fp, "")
            for fp in files_in_cluster
        }
    
    def get_similarity(self, file_path1, file_path2):
        """Calculate cosine similarity between two files"""
        if file_path1 not in self.file_embeddings or \
           file_path2 not in self.file_embeddings:
            return 0.0
        
        emb1 = self.file_embeddings[file_path1].reshape(1, -1)
        emb2 = self.file_embeddings[file_path2].reshape(1, -1)
        return float(cosine_similarity(emb1, emb2)[0][0])
    
    def get_cluster_stats(self):
        """Get statistics about current clustering"""
        if not self.cluster_assignments:
            return {}
        
        stats = {}
        for file_path, cluster_id in self.cluster_assignments.items():
            if cluster_id not in stats:
                stats[cluster_id] = {
                    'count': 0,
                    'files': []
                }
            stats[cluster_id]['count'] += 1
            stats[cluster_id]['files'].append(Path(file_path).name)
        
        return stats
