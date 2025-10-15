"""
Main RAG service orchestration.
High-level API combining all components.
"""

from typing import List, Dict, Any
from pathlib import Path

from src.vector_store import DocumentIndexer, ChromaDBClient
from src.retrieval import Retriever, Reranker
from src.generation import LLMClient, PromptTemplates, CitationParser
from src.embeddings import EmbeddingGenerator
from src.core.config import settings
from src.core.logger import app_logger
from src.api.models import QueryRequest, RAGResponse, IndexingResult, SourceChunk


class RAGService:
    """
    Main RAG service orchestrating all components.
    """
    
    def __init__(
        self,
        vector_client: ChromaDBClient = None,
        embedding_generator: EmbeddingGenerator = None,
        llm_client: LLMClient = None,
    ):
        """
        Initialize RAG service.
        
        Args:
            vector_client: Vector store client
            embedding_generator: Embedding generator
            llm_client: LLM client
        """
        app_logger.info("Initializing RAG service...")
        
        # Initialize components
        self.embedding_generator = embedding_generator or EmbeddingGenerator()
        self.vector_client = vector_client or ChromaDBClient()
        self.llm_client = llm_client or LLMClient()
        
        # Initialize higher-level components
        self.indexer = DocumentIndexer(
            vector_client=self.vector_client,
            embedding_generator=self.embedding_generator,
        )
        
        self.retriever = Retriever(
            vector_client=self.vector_client,
            embedding_generator=self.embedding_generator,
        )
        
        self.reranker = Reranker(method="diversity")
        
        app_logger.info("RAG service initialized successfully")
    
    def index_documents(self, file_paths: List[str]) -> List[IndexingResult]:
        """
        Index multiple documents.
        
        Args:
            file_paths: List of document file paths
            
        Returns:
            List of indexing results
        """
        app_logger.info(f"Indexing {len(file_paths)} documents")
        
        paths = [Path(fp) for fp in file_paths]
        results = self.indexer.index_documents(paths)
        
        return [IndexingResult(**r) for r in results]
    
    def query(
        self,
        query: str,
        top_k: int = None,
        filters: Dict[str, Any] = None,
        rerank: bool = True,
    ) -> RAGResponse:
        """
        Execute RAG query: retrieve + generate with citations.
        
        Args:
            query: User question
            top_k: Number of chunks to retrieve
            filters: Metadata filters
            rerank: Whether to rerank results
            
        Returns:
            RAG response with answer and citations
        """
        app_logger.info(f"Processing query: '{query[:100]}...'")
        
        # Step 1: Retrieve relevant chunks
        retrieval_result = self.retriever.retrieve_with_context(
            query=query,
            top_k=top_k,
            filters=filters,
        )
        
        chunks = retrieval_result["chunks"]
        
        if not chunks:
            app_logger.warning("No relevant chunks found")
            return RAGResponse(
                query=query,
                answer="I couldn't find any relevant information in the indexed documents to answer your question.",
                sources=[],
                citations=[],
                citation_map={},
                num_sources=0,
                avg_similarity=0.0,
            )
        
        # Step 2: Optional reranking
        if rerank:
            chunks = self.reranker.rerank(chunks, query)
        
        # Step 3: Generate answer with LLM
        system_prompt, user_prompt = PromptTemplates.create_full_rag_prompt(
            query=query,
            chunks=chunks,
        )
        
        answer = self.llm_client.generate_with_system_prompt(
            system_prompt=system_prompt,
            user_message=user_prompt,
        )
        
        # Step 4: Parse and validate citations
        citations = CitationParser.extract_citations(answer)
        citation_map = CitationParser.map_citations_to_sources(answer, chunks)
        
        # Validate citations
        is_valid, errors = CitationParser.validate_citations(answer, len(chunks))
        if not is_valid:
            app_logger.warning(f"Citation validation errors: {errors}")
        
        # Step 5: Convert chunks to SourceChunk models
        source_chunks = []
        for chunk in chunks:
            try:
                source_chunks.append(SourceChunk(
                    id=chunk["id"],
                    text=chunk["text"],
                    file_name=chunk.get("file_name", "unknown"),
                    page=chunk.get("page", 1),
                    similarity_score=chunk["similarity_score"],
                    chunk_id=chunk.get("chunk_id", 0),
                ))
            except Exception as e:
                app_logger.warning(f"Failed to convert chunk to model: {e}")
        
        app_logger.info(
            f"Query complete: {len(citations)} citations, "
            f"{len(source_chunks)} sources"
        )
        
        return RAGResponse(
            query=query,
            answer=answer,
            sources=source_chunks,
            citations=citations,
            citation_map=citation_map,
            num_sources=len(chunks),
            avg_similarity=retrieval_result["avg_similarity"],
        )
    
    def delete_document(self, file_name: str):
        """
        Delete all chunks for a document.
        
        Args:
            file_name: Name of file to delete
        """
        self.indexer.delete_document(file_name)
        app_logger.info(f"Deleted document: {file_name}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        vector_stats = self.vector_client.get_stats()
        
        return {
            "total_documents": vector_stats["total_documents"],
            "total_chunks": vector_stats["total_documents"],
            "collection_name": vector_stats["collection_name"],
            "embedding_model": settings.embedding_model,
            "vector_db_type": settings.vector_db_type,
            "llm_model": self.llm_client.model,
        }
    
    def clear_all(self):
        """Clear all indexed documents."""
        self.vector_client.delete_collection()
        # Recreate collection
        self.vector_client = ChromaDBClient()
        self.indexer.vector_client = self.vector_client
        self.retriever.vector_client = self.vector_client
        app_logger.info("All documents cleared")
