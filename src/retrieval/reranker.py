"""
Optional reranking logic for improved retrieval quality.
Can be used to rerank retrieved chunks using cross-encoders or other methods.
"""

from typing import List, Dict, Any

from src.core.logger import app_logger


class Reranker:
    """
    Rerank retrieved chunks for improved relevance.
    """
    
    def __init__(self, method: str = "simple"):
        """
        Initialize reranker.
        
        Args:
            method: Reranking method ('simple', 'diversity', etc.)
        """
        self.method = method
        app_logger.info(f"Reranker initialized with method: {method}")
    
    def rerank(
        self,
        chunks: List[Dict[str, Any]],
        query: str = None,
    ) -> List[Dict[str, Any]]:
        """
        Rerank chunks.
        
        Args:
            chunks: List of retrieved chunks
            query: Original query (optional, used by some methods)
            
        Returns:
            Reranked chunks
        """
        if self.method == "simple":
            # Already sorted by similarity
            return chunks
        elif self.method == "diversity":
            # Maximize diversity across sources
            return self._diversity_rerank(chunks)
        else:
            app_logger.warning(f"Unknown reranking method: {self.method}")
            return chunks
    
    def _diversity_rerank(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rerank to maximize source diversity while preserving relevance.
        
        Args:
            chunks: Input chunks
            
        Returns:
            Reranked chunks
        """
        if not chunks:
            return chunks
        
        # Group by source
        by_source = {}
        for chunk in chunks:
            source = chunk.get("file_name", "unknown")
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(chunk)
        
        # Interleave chunks from different sources
        reranked = []
        max_len = max(len(v) for v in by_source.values())
        
        for i in range(max_len):
            for source_chunks in by_source.values():
                if i < len(source_chunks):
                    reranked.append(source_chunks[i])
        
        app_logger.debug(f"Diversity reranking: {len(chunks)} chunks from {len(by_source)} sources")
        return reranked
