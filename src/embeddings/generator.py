"""
Embedding generation using sentence-transformers.
Provides caching and batch processing for efficiency.
"""

from typing import List, Union
import hashlib
import pickle
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from src.core.config import settings
from src.core.logger import app_logger
from src.core.exceptions import EmbeddingGenerationError


class EmbeddingGenerator:
    """
    Generate embeddings using sentence-transformers with caching.
    """
    
    def __init__(
        self,
        model_name: str = None,
        device: str = "cpu",
        cache_embeddings: bool = True,
    ):
        """
        Initialize embedding generator.
        
        Args:
            model_name: Sentence transformer model name
            device: Device to run model on ('cpu' or 'cuda')
            cache_embeddings: Whether to cache embeddings
        """
        self.model_name = model_name or settings.embedding_model
        self.device = device
        self.cache_embeddings = cache_embeddings
        self.cache_dir = settings.cache_dir / "embeddings"
        
        if self.cache_embeddings:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        app_logger.info(f"Loading embedding model: {self.model_name}")
        try:
            self.model = SentenceTransformer(self.model_name, device=self.device)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            app_logger.info(
                f"Model loaded successfully. Embedding dimension: {self.embedding_dim}"
            )
        except Exception as e:
            app_logger.error(f"Failed to load embedding model: {e}")
            raise EmbeddingGenerationError(f"Model loading failed: {e}") from e
    
    def generate(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        show_progress: bool = False,
    ) -> np.ndarray:
        """
        Generate embeddings for text(s).
        
        Args:
            texts: Single text or list of texts
            batch_size: Batch size for processing
            show_progress: Show progress bar
            
        Returns:
            Numpy array of embeddings (shape: [n_texts, embedding_dim])
        """
        # Handle single text
        if isinstance(texts, str):
            texts = [texts]
            single_input = True
        else:
            single_input = False
        
        if not texts:
            return np.array([])
        
        try:
            app_logger.debug(f"Generating embeddings for {len(texts)} texts")
            
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True,
                normalize_embeddings=True,  # L2 normalization for cosine similarity
            )
            
            # Return single embedding if single input
            if single_input:
                return embeddings[0]
            
            return embeddings
            
        except Exception as e:
            app_logger.error(f"Embedding generation failed: {e}")
            raise EmbeddingGenerationError(f"Failed to generate embeddings: {e}") from e
    
    def generate_with_cache(
        self,
        texts: Union[str, List[str]],
        cache_key: str = None,
    ) -> np.ndarray:
        """
        Generate embeddings with caching support.
        
        Args:
            texts: Text(s) to embed
            cache_key: Optional cache key (otherwise computed from texts)
            
        Returns:
            Embeddings array
        """
        if not self.cache_embeddings:
            return self.generate(texts)
        
        # Compute cache key if not provided
        if cache_key is None:
            if isinstance(texts, str):
                cache_key = self._compute_hash(texts)
            else:
                cache_key = self._compute_hash("".join(texts))
        
        cache_path = self.cache_dir / f"{cache_key}.pkl"
        
        # Try to load from cache
        if cache_path.exists():
            try:
                with open(cache_path, 'rb') as f:
                    embeddings = pickle.load(f)
                app_logger.debug(f"Loaded embeddings from cache: {cache_key}")
                return embeddings
            except Exception as e:
                app_logger.warning(f"Failed to load cache {cache_key}: {e}")
        
        # Generate embeddings
        embeddings = self.generate(texts)
        
        # Save to cache
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(embeddings, f)
            app_logger.debug(f"Saved embeddings to cache: {cache_key}")
        except Exception as e:
            app_logger.warning(f"Failed to save cache {cache_key}: {e}")
        
        return embeddings
    
    @staticmethod
    def _compute_hash(text: str) -> str:
        """Compute SHA256 hash of text for cache key."""
        return hashlib.sha256(text.encode()).hexdigest()[:16]
    
    def clear_cache(self):
        """Clear all cached embeddings."""
        if self.cache_dir.exists():
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()
            app_logger.info("Embedding cache cleared")
