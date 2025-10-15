"""
Retrieval system for finding relevant document chunks.
Implements semantic search with ranking and filtering.
"""

from typing import List, Dict, Any, Optional

from src.embeddings import EmbeddingGenerator
from src.vector_store.client import ChromaDBClient
from src.core.config import settings
from src.core.logger import app_logger
from src.core.exceptions import RetrievalError


class Retriever:
    """
    Semantic retrieval system for RAG.
    """
    
    def __init__(
        self,
        vector_client: ChromaDBClient = None,
        embedding_generator: EmbeddingGenerator = None,
        top_k: int = None,
        similarity_threshold: float = None,
    ):
        """
        Initialize retriever.
        
        Args:
            vector_client: ChromaDB client
            embedding_generator: Embedding generator
            top_k: Number of results to retrieve
            similarity_threshold: Minimum similarity score
        """
        self.vector_client = vector_client or ChromaDBClient()
        self.embedding_generator = embedding_generator or EmbeddingGenerator()
        self.top_k = top_k or settings.top_k_retrieval
        self.similarity_threshold = similarity_threshold or settings.similarity_threshold
        
        app_logger.info(
            f"Retriever initialized: top_k={self.top_k}, "
            f"threshold={self.similarity_threshold}"
        )
    
    def retrieve(
        self,
        query: str,
        top_k: int = None,
        filters: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: Search query
            top_k: Number of results (overrides default)
            filters: Metadata filters (e.g., {"file_name": "report.pdf"})
            
        Returns:
            List of retrieved chunks with metadata and scores
        """
        if not query or not query.strip():
            raise RetrievalError("Query cannot be empty")
        
        top_k = top_k or self.top_k
        
        try:
            app_logger.info(f"Retrieving documents for query: '{query[:100]}...'")
            
            # Generate query embedding
            query_embedding = self.embedding_generator.generate(query)
            
            # Query vector store
            results = self.vector_client.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k,
                where=filters,
            )
            
            # Process results
            chunks = self._process_results(results)
            
            # Log similarity scores for debugging
            if chunks:
                scores = [chunk["similarity_score"] for chunk in chunks]
                app_logger.info(f"Similarity scores: {scores}")
            
            # Filter by similarity threshold
            filtered_chunks = [
                chunk for chunk in chunks
                if chunk["similarity_score"] >= self.similarity_threshold
            ]
            
            app_logger.info(
                f"Retrieved {len(chunks)} chunks, "
                f"{len(filtered_chunks)} above threshold ({self.similarity_threshold})"
            )
            
            return filtered_chunks
            
        except Exception as e:
            app_logger.error(f"Retrieval failed: {e}")
            raise RetrievalError(f"Failed to retrieve documents: {e}") from e
    
    def _process_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process ChromaDB results into structured chunks.
        
        Args:
            results: Raw ChromaDB query results
            
        Returns:
            List of processed chunks
        """
        chunks = []
        
        # ChromaDB returns lists of lists (one per query)
        ids = results["ids"][0]
        distances = results["distances"][0]
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        
        for i in range(len(ids)):
            # Convert distance to similarity (cosine distance -> similarity)
            # ChromaDB with cosine space returns cosine distance (0-2 range)
            # Convert to similarity: 1 - (distance/2) to get 0-1 range
            # where 0 = opposite, 1 = identical
            similarity = 1.0 - (distances[i] / 2.0)
            
            chunk = {
                "id": ids[i],
                "text": documents[i],
                "similarity_score": similarity,
                "distance": distances[i],
                **metadatas[i],
            }
            chunks.append(chunk)
        
        return chunks
    
    def retrieve_with_context(
        self,
        query: str,
        top_k: int = None,
        filters: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve chunks with additional context for RAG.
        
        Args:
            query: Search query
            top_k: Number of results
            filters: Metadata filters
            
        Returns:
            Dict with chunks and summary statistics
        """
        chunks = self.retrieve(query, top_k, filters)
        
        # Compute statistics
        avg_similarity = (
            sum(c["similarity_score"] for c in chunks) / len(chunks)
            if chunks else 0.0
        )
        
        # Group by source file
        sources = {}
        for chunk in chunks:
            file_name = chunk.get("file_name", "unknown")
            if file_name not in sources:
                sources[file_name] = []
            sources[file_name].append(chunk)
        
        return {
            "query": query,
            "chunks": chunks,
            "total_chunks": len(chunks),
            "avg_similarity": avg_similarity,
            "num_sources": len(sources),
            "sources": list(sources.keys()),
        }
