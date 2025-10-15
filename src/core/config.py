"""
Core configuration management for DocuMind RAG system.
Loads settings from environment variables with validation.
"""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # LLM Configuration
    llm_provider: str = Field(default="gemini", description="LLM provider: openai, gemini, or local")
    
    # OpenAI Configuration
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = Field(default="gpt-3.5-turbo", description="OpenAI model name")
    openai_temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    
    # Google Gemini Configuration
    gemini_api_key: str = Field(default="", description="Google Gemini API key")
    gemini_model: str = Field(default="gemini-pro", description="Gemini model name")
    gemini_temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    
    # Local LLM Alternative
    use_local_llm: bool = Field(default=False, description="Use local LLM instead of cloud")
    local_llm_endpoint: str = Field(default="http://localhost:11434", description="Ollama endpoint")
    local_llm_model: str = Field(default="llama2", description="Local LLM model name")
    
    # Embedding Configuration
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Sentence transformer model"
    )
    embedding_dimension: int = Field(default=384, description="Embedding vector dimension")
    
    # Vector Store Configuration
    vector_db_type: Literal["chromadb", "faiss"] = Field(default="chromadb")
    chroma_persist_dir: Path = Field(default=Path("./data/vectordb"))
    collection_name: str = Field(default="documind_docs")
    
    # Chunking Configuration
    chunk_size: int = Field(default=300, ge=50, le=1000, description="Chunk size in tokens")
    chunk_overlap: int = Field(default=50, ge=0, le=200, description="Overlap in tokens")
    max_chunk_size: int = Field(default=500, ge=100, description="Maximum chunk size")
    
    # Retrieval Configuration
    top_k_retrieval: int = Field(default=5, ge=1, le=20, description="Number of chunks to retrieve")
    similarity_threshold: float = Field(default=0.3, ge=0.0, le=1.0, description="Minimum similarity score")
    
    # Storage Paths
    upload_dir: Path = Field(default=Path("./data/uploads"))
    cache_dir: Path = Field(default=Path("./data/cache"))
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Path = Field(default=Path("./logs/documind.log"))
    
    def model_post_init(self, __context) -> None:
        """Create necessary directories after initialization."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.chroma_persist_dir.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        Path("./data").mkdir(exist_ok=True)


# Global settings instance
settings = Settings()
