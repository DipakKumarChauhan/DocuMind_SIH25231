"""
Document indexing logic for vector store.
Orchestrates extraction, chunking, embedding, and storage.
"""

from typing import List, Dict, Any
from pathlib import Path

from src.document_processing import TextExtractor, TextChunker
from src.embeddings import EmbeddingGenerator
from src.vector_store.client import ChromaDBClient
from src.core.logger import app_logger
from src.core.exceptions import VectorStoreError


class DocumentIndexer:
    """
    High-level API for indexing documents into vector store.
    """
    
    def __init__(
        self,
        vector_client: ChromaDBClient = None,
        embedding_generator: EmbeddingGenerator = None,
        text_chunker: TextChunker = None,
    ):
        """
        Initialize document indexer.
        
        Args:
            vector_client: ChromaDB client (created if not provided)
            embedding_generator: Embedding generator (created if not provided)
            text_chunker: Text chunker (created if not provided)
        """
        self.vector_client = vector_client or ChromaDBClient()
        self.embedding_generator = embedding_generator or EmbeddingGenerator()
        self.text_chunker = text_chunker or TextChunker()
        
        app_logger.info("DocumentIndexer initialized")
    
    def index_document(
        self,
        file_path: Path,
        batch_size: int = 32,
    ) -> Dict[str, Any]:
        """
        Index a single document: extract, chunk, embed, and store.
        
        Args:
            file_path: Path to document file
            batch_size: Batch size for embedding generation
            
        Returns:
            Dict with indexing statistics
        """
        file_path = Path(file_path)
        app_logger.info(f"Indexing document: {file_path}")
        
        try:
            # Step 1: Extract text
            extracted_doc = TextExtractor.extract(file_path)
            
            # Step 2: Chunk text
            chunks = self.text_chunker.chunk_document(extracted_doc)
            
            if not chunks:
                app_logger.warning(f"No chunks generated for {file_path}")
                return {
                    "file_name": file_path.name,
                    "status": "skipped",
                    "reason": "No text content",
                }
            
            # Step 3: Generate embeddings
            chunk_texts = [chunk["text"] for chunk in chunks]
            embeddings = self.embedding_generator.generate(
                chunk_texts,
                batch_size=batch_size,
                show_progress=True,
            )
            
            # Step 4: Prepare metadata
            metadatas = []
            for chunk in chunks:
                metadata = {
                    "file_name": chunk["file_name"],
                    "file_type": chunk["file_type"],
                    "file_path": chunk["file_path"],
                    "chunk_id": chunk["chunk_id"],
                    "page": chunk.get("page", 1),
                    "start_char": chunk["start_char"],
                    "end_char": chunk["end_char"],
                    "token_count": chunk["token_count"],
                }
                metadatas.append(metadata)
            
            # Step 5: Store in vector database
            doc_ids = self.vector_client.add_documents(
                texts=chunk_texts,
                embeddings=embeddings.tolist(),
                metadatas=metadatas,
            )
            
            app_logger.info(
                f"Successfully indexed {file_path.name}: "
                f"{len(chunks)} chunks, {len(doc_ids)} stored"
            )
            
            return {
                "file_name": file_path.name,
                "status": "success",
                "chunks_created": len(chunks),
                "chunks_stored": len(doc_ids),
                "total_pages": extracted_doc.get("total_pages", 1),
            }
            
        except Exception as e:
            app_logger.error(f"Failed to index {file_path}: {e}")
            return {
                "file_name": file_path.name,
                "status": "failed",
                "error": str(e),
            }
    
    def index_documents(
        self,
        file_paths: List[Path],
        batch_size: int = 32,
    ) -> List[Dict[str, Any]]:
        """
        Index multiple documents.
        
        Args:
            file_paths: List of document paths
            batch_size: Batch size for embedding generation
            
        Returns:
            List of indexing results
        """
        app_logger.info(f"Indexing {len(file_paths)} documents")
        
        results = []
        for file_path in file_paths:
            result = self.index_document(file_path, batch_size)
            results.append(result)
        
        # Summary stats
        successful = sum(1 for r in results if r["status"] == "success")
        failed = sum(1 for r in results if r["status"] == "failed")
        
        app_logger.info(
            f"Indexing complete: {successful} successful, {failed} failed"
        )
        
        return results
    
    def delete_document(self, file_name: str):
        """
        Delete all chunks for a specific document.
        
        Args:
            file_name: Name of file to delete
        """
        try:
            self.vector_client.delete_by_metadata({"file_name": file_name})
            app_logger.info(f"Deleted document: {file_name}")
        except Exception as e:
            app_logger.error(f"Failed to delete {file_name}: {e}")
            raise VectorStoreError(f"Document deletion failed: {e}") from e
    
    def get_stats(self) -> Dict[str, Any]:
        """Get indexing statistics."""
        return self.vector_client.get_stats()
