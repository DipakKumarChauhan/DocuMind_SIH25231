"""
Custom exceptions for DocuMind RAG system.
Provides clear error hierarchy for different failure modes.
"""


class DocuMindException(Exception):
    """Base exception for all DocuMind errors."""
    pass


class DocumentProcessingError(DocuMindException):
    """Raised when document extraction or processing fails."""
    pass


class EmbeddingGenerationError(DocuMindException):
    """Raised when embedding generation fails."""
    pass


class VectorStoreError(DocuMindException):
    """Raised when vector store operations fail."""
    pass


class RetrievalError(DocuMindException):
    """Raised when retrieval operations fail."""
    pass


class LLMError(DocuMindException):
    """Raised when LLM API calls fail."""
    pass


class ChunkingError(DocuMindException):
    """Raised when text chunking fails."""
    pass


class ValidationError(DocuMindException):
    """Raised when input validation fails."""
    pass
