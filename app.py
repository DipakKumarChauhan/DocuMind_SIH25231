"""
FastAPI application for DocuMind RAG system.
Provides REST API with Swagger/OpenAPI documentation.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from pathlib import Path
import shutil

from src.api import RAGService, QueryRequest, RAGResponse, IndexingResult
from src.core.config import settings
from src.core.logger import app_logger
from src.core.exceptions import DocuMindException

# Initialize FastAPI app
app = FastAPI(
    title="DocuMind RAG API",
    description="""
    🚀 **DocuMind - Multimodal RAG System**
    
    A production-ready Retrieval-Augmented Generation system with citation-based answers.
    
    ## Features
    - 📄 Multi-format document support (PDF, DOCX, TXT)
    - 🔍 Semantic search with sentence-transformers
    - 🎯 Citation-based answers (no hallucinations)
    - 💾 Persistent vector storage with ChromaDB
    - 🤖 Multiple LLM providers (OpenAI, Gemini, Local)
    
    ## Quick Start
    1. Upload documents using `/documents/upload`
    2. Query using `/query`
    3. View sources and citations in response
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG service (cached)
rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Get or initialize RAG service."""
    global rag_service
    if rag_service is None:
        app_logger.info("Initializing RAG service...")
        rag_service = RAGService()
    return rag_service


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    app_logger.info("Starting DocuMind API...")
    get_rag_service()
    app_logger.info("DocuMind API ready!")


@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to DocuMind RAG API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


@app.get("/health", tags=["General"])
async def health_check():
    """Health check endpoint."""
    try:
        service = get_rag_service()
        stats = service.get_stats()
        return {
            "status": "healthy",
            "service": "DocuMind RAG",
            "stats": stats
        }
    except Exception as e:
        app_logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.post("/documents/upload", response_model=List[IndexingResult], tags=["Documents"])
async def upload_documents(
    files: List[UploadFile] = File(..., description="Documents to upload (PDF, DOCX, TXT)")
):
    """
    Upload and index documents.
    
    - **files**: List of files to upload
    - Returns indexing results with status and chunk counts
    
    Example:
    ```bash
    curl -X POST "http://localhost:8000/documents/upload" \
         -H "accept: application/json" \
         -F "files=@document1.pdf" \
         -F "files=@document2.docx"
    ```
    """
    try:
        service = get_rag_service()
        
        # Save uploaded files
        file_paths = []
        for file in files:
            # Check if filename is valid
            if not file.filename or file.filename == "":
                raise HTTPException(
                    status_code=400,
                    detail="Empty filename provided. Please select a valid file."
                )
            
            # Validate file type
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in ['.pdf', '.docx', '.txt']:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file_ext}. Supported: .pdf, .docx, .txt"
                )
            
            # Save file
            file_path = settings.upload_dir / file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            file_paths.append(str(file_path))
            app_logger.info(f"Saved uploaded file: {file.filename}")
        
        # Index documents
        results = service.index_documents(file_paths)
        
        app_logger.info(f"Indexed {len(file_paths)} documents")
        return results
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 400 errors)
        raise
    except DocuMindException as e:
        app_logger.error(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        app_logger.error(f"Unexpected error in upload: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/query", response_model=RAGResponse, tags=["Query"])
async def query_documents(
    query: str = Query(..., description="Search query", min_length=1),
    top_k: int = Query(5, ge=1, le=20, description="Number of sources to retrieve"),
    rerank: bool = Query(True, description="Enable diversity reranking"),
    file_filter: Optional[str] = Query(None, description="Filter by specific filename")
):
    """
    Query indexed documents with RAG.
    
    - **query**: Your question
    - **top_k**: Number of source chunks to retrieve (1-20)
    - **rerank**: Whether to apply diversity reranking
    - **file_filter**: Optional filename to search within
    
    Returns answer with citations and source chunks.
    
    Example:
    ```bash
    curl -X POST "http://localhost:8000/query?query=What%20is%20the%20budget?&top_k=5"
    ```
    """
    try:
        service = get_rag_service()
        
        # Build filters
        filters = {}
        if file_filter:
            filters["file_name"] = file_filter
        
        # Execute query
        response = service.query(
            query=query,
            top_k=top_k,
            filters=filters if filters else None,
            rerank=rerank,
        )
        
        app_logger.info(f"Query processed: '{query[:50]}...'")
        return response
        
    except DocuMindException as e:
        app_logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        app_logger.error(f"Unexpected error in query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/stats", tags=["Statistics"])
async def get_statistics():
    """
    Get system statistics.
    
    Returns:
    - Total documents indexed
    - Total chunks stored
    - Model information
    - Database configuration
    """
    try:
        service = get_rag_service()
        stats = service.get_stats()
        return stats
    except Exception as e:
        app_logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents/{filename}", tags=["Documents"])
async def delete_document(filename: str):
    """
    Delete a specific document and its chunks.
    
    - **filename**: Name of the file to delete
    
    Example:
    ```bash
    curl -X DELETE "http://localhost:8000/documents/report.pdf"
    ```
    """
    try:
        service = get_rag_service()
        service.delete_document(filename)
        
        app_logger.info(f"Deleted document: {filename}")
        return {"message": f"Document '{filename}' deleted successfully"}
        
    except DocuMindException as e:
        app_logger.error(f"Delete failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        app_logger.error(f"Unexpected error in delete: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/documents", tags=["Documents"])
async def clear_all_documents(
    confirm: bool = Query(False, description="Confirmation flag (must be true)")
):
    """
    Clear all indexed documents.
    
    ⚠️ **Warning**: This will delete all documents and cannot be undone!
    
    - **confirm**: Must be set to `true` to confirm deletion
    
    Example:
    ```bash
    curl -X DELETE "http://localhost:8000/documents?confirm=true"
    ```
    """
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Confirmation required. Set confirm=true to clear all documents."
        )
    
    try:
        service = get_rag_service()
        service.clear_all()
        
        app_logger.info("Cleared all documents")
        return {"message": "All documents cleared successfully"}
        
    except Exception as e:
        app_logger.error(f"Clear all failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models/info", tags=["Models"])
async def get_model_info():
    """
    Get information about configured models.
    
    Returns:
    - LLM provider and model
    - Embedding model
    - Configuration details
    """
    return {
        "llm": {
            "provider": settings.llm_provider,
            "model": (
                settings.gemini_model if settings.llm_provider == "gemini"
                else settings.openai_model if settings.llm_provider == "openai"
                else settings.local_llm_model
            ),
            "temperature": (
                settings.gemini_temperature if settings.llm_provider == "gemini"
                else settings.openai_temperature
            ),
        },
        "embedding": {
            "model": settings.embedding_model,
            "dimension": settings.embedding_dimension,
        },
        "vector_store": {
            "type": settings.vector_db_type,
            "collection": settings.collection_name,
        },
        "chunking": {
            "chunk_size": settings.chunk_size,
            "chunk_overlap": settings.chunk_overlap,
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
