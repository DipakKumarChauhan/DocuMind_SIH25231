"""
Pydantic models for API request/response validation.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class DocumentUploadRequest(BaseModel):
    """Request model for document upload."""
    file_path: str = Field(..., description="Path to document file")
    
    @field_validator("file_path")
    @classmethod
    def validate_file_exists(cls, v):
        """Validate that file exists."""
        path = Path(v)
        if not path.exists():
            raise ValueError(f"File not found: {v}")
        return str(path)


class QueryRequest(BaseModel):
    """Request model for RAG query."""
    query: str = Field(..., min_length=1, description="Search query")
    top_k: Optional[int] = Field(5, ge=1, le=20, description="Number of chunks to retrieve")
    filters: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")


class SourceChunk(BaseModel):
    """Model for a retrieved source chunk."""
    id: str
    text: str
    file_name: str
    page: int
    similarity_score: float
    chunk_id: int
    
    class Config:
        extra = "allow"  # Allow additional metadata fields


class RAGResponse(BaseModel):
    """Response model for RAG query."""
    query: str
    answer: str
    sources: List[SourceChunk]
    citations: List[int]
    citation_map: Dict[int, Dict[str, Any]]
    num_sources: int
    avg_similarity: float
    
    class Config:
        extra = "allow"


class IndexingResult(BaseModel):
    """Result of document indexing operation."""
    file_name: str
    status: str  # 'success', 'failed', 'skipped'
    chunks_created: Optional[int] = None
    chunks_stored: Optional[int] = None
    total_pages: Optional[int] = None
    error: Optional[str] = None


class SystemStats(BaseModel):
    """System statistics."""
    total_documents: int
    total_chunks: int
    collection_name: str
    embedding_model: str
    vector_db_type: str
