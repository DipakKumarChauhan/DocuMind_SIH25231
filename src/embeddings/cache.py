"""
Embedding cache management utilities.
"""

from pathlib import Path
from typing import Optional, Dict, Any
import json
import pickle
from datetime import datetime

from src.core.config import settings
from src.core.logger import app_logger


class EmbeddingCache:
    """Manage embedding cache with metadata tracking."""
    
    def __init__(self, cache_dir: Path = None):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Cache directory (default from settings)
        """
        self.cache_dir = cache_dir or settings.cache_dir / "embeddings"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.cache_dir / "metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load cache metadata."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                app_logger.warning(f"Failed to load cache metadata: {e}")
        return {}
    
    def _save_metadata(self):
        """Save cache metadata."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            app_logger.error(f"Failed to save cache metadata: {e}")
    
    def save(
        self,
        key: str,
        embeddings,
        metadata: Dict[str, Any] = None,
    ):
        """
        Save embeddings with metadata.
        
        Args:
            key: Cache key
            embeddings: Embedding array
            metadata: Additional metadata
        """
        cache_path = self.cache_dir / f"{key}.pkl"
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(embeddings, f)
            
            # Update metadata
            self.metadata[key] = {
                "created_at": datetime.now().isoformat(),
                "size": cache_path.stat().st_size,
                **(metadata or {}),
            }
            self._save_metadata()
            
            app_logger.debug(f"Saved embeddings to cache: {key}")
        except Exception as e:
            app_logger.error(f"Failed to save cache {key}: {e}")
    
    def load(self, key: str) -> Optional:
        """
        Load embeddings from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Embeddings or None if not found
        """
        cache_path = self.cache_dir / f"{key}.pkl"
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                embeddings = pickle.load(f)
            app_logger.debug(f"Loaded embeddings from cache: {key}")
            return embeddings
        except Exception as e:
            app_logger.warning(f"Failed to load cache {key}: {e}")
            return None
    
    def exists(self, key: str) -> bool:
        """Check if cache key exists."""
        return (self.cache_dir / f"{key}.pkl").exists()
    
    def clear(self):
        """Clear all cached embeddings."""
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()
        self.metadata = {}
        self._save_metadata()
        app_logger.info("Embedding cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        cache_files = list(self.cache_dir.glob("*.pkl"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            "total_entries": len(cache_files),
            "total_size_mb": total_size / (1024 * 1024),
            "cache_dir": str(self.cache_dir),
        }
