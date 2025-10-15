"""
ChromaDB client wrapper for vector storage and retrieval.
Provides persistent vector storage with metadata filtering.
"""

from typing import List, Dict, Any, Optional
import uuid

import chromadb
from chromadb.config import Settings as ChromaSettings

from src.core.config import settings
from src.core.logger import app_logger
from src.core.exceptions import VectorStoreError


class ChromaDBClient:
    """
    ChromaDB client for managing document embeddings.
    """
    
    def __init__(
        self,
        collection_name: str = None,
        persist_directory: str = None,
    ):
        """
        Initialize ChromaDB client.
        
        Args:
            collection_name: Name of collection (default from settings)
            persist_directory: Directory for persistent storage
        """
        self.collection_name = collection_name or settings.collection_name
        self.persist_directory = persist_directory or str(settings.chroma_persist_dir)
        
        app_logger.info(f"Initializing ChromaDB client at {self.persist_directory}")
        
        try:
            # Use PersistentClient for data persistence
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},  # Use cosine similarity
            )
            
            app_logger.info(
                f"Collection '{self.collection_name}' initialized with "
                f"{self.collection.count()} existing documents"
            )
            
        except Exception as e:
            app_logger.error(f"Failed to initialize ChromaDB: {e}")
            raise VectorStoreError(f"ChromaDB initialization failed: {e}") from e
    
    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]] = None,
        ids: List[str] = None,
    ) -> List[str]:
        """
        Add documents to the collection.
        
        Args:
            texts: List of text chunks
            embeddings: List of embedding vectors
            metadatas: List of metadata dicts
            ids: Optional document IDs (generated if not provided)
            
        Returns:
            List of document IDs
        """
        if not texts or not embeddings:
            app_logger.warning("No documents to add")
            return []
        
        if len(texts) != len(embeddings):
            raise VectorStoreError(
                f"Mismatch: {len(texts)} texts vs {len(embeddings)} embeddings"
            )
        
        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in texts]
        
        # Prepare metadatas
        if metadatas is None:
            metadatas = [{}] * len(texts)
        
        # Ensure all metadata values are strings, ints, or floats (ChromaDB requirement)
        metadatas = [self._sanitize_metadata(m) for m in metadatas]
        
        try:
            app_logger.info(f"Adding {len(texts)} documents to collection")
            
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
            )
            
            app_logger.info(f"Successfully added {len(texts)} documents")
            return ids
            
        except Exception as e:
            app_logger.error(f"Failed to add documents: {e}")
            raise VectorStoreError(f"Document addition failed: {e}") from e
    
    def query(
        self,
        query_embeddings: List[List[float]],
        n_results: int = 5,
        where: Dict[str, Any] = None,
        where_document: Dict[str, str] = None,
    ) -> Dict[str, Any]:
        """
        Query the collection for similar documents.
        
        Args:
            query_embeddings: Query embedding vectors
            n_results: Number of results to return
            where: Metadata filter conditions
            where_document: Document content filter
            
        Returns:
            Query results with ids, distances, metadatas, documents
        """
        try:
            app_logger.debug(
                f"Querying collection with {len(query_embeddings)} queries, "
                f"n_results={n_results}"
            )
            
            results = self.collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where,
                where_document=where_document,
            )
            
            app_logger.debug(f"Query returned {len(results['ids'][0])} results")
            return results
            
        except Exception as e:
            app_logger.error(f"Query failed: {e}")
            raise VectorStoreError(f"Query failed: {e}") from e
    
    def delete_by_metadata(self, where: Dict[str, Any]):
        """
        Delete documents matching metadata filter.
        
        Args:
            where: Metadata filter conditions
        """
        try:
            self.collection.delete(where=where)
            app_logger.info(f"Deleted documents matching filter: {where}")
        except Exception as e:
            app_logger.error(f"Delete operation failed: {e}")
            raise VectorStoreError(f"Delete failed: {e}") from e
    
    def delete_collection(self):
        """Delete the entire collection."""
        try:
            self.client.delete_collection(name=self.collection_name)
            app_logger.info(f"Deleted collection '{self.collection_name}'")
        except Exception as e:
            app_logger.error(f"Failed to delete collection: {e}")
            raise VectorStoreError(f"Collection deletion failed: {e}") from e
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        return {
            "collection_name": self.collection_name,
            "total_documents": self.collection.count(),
            "persist_directory": self.persist_directory,
        }
    
    @staticmethod
    def _sanitize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize metadata to ensure ChromaDB compatibility.
        ChromaDB only accepts str, int, float, or bool values.
        """
        sanitized = {}
        for key, value in metadata.items():
            if value is None:
                continue
            elif isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            else:
                # Convert other types to string
                sanitized[key] = str(value)
        return sanitized
