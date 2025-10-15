# DocuMind System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│  ┌──────────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Streamlit UI    │  │  CLI Tool    │  │  Python API      │  │
│  └──────────────────┘  └──────────────┘  └──────────────────┘  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       RAG SERVICE (Orchestrator)                 │
│                    src/api/service.py                            │
└────────────────────────────┬─────────────────────────────────────┘
                             │
            ┌────────────────┼────────────────┐
            ▼                ▼                ▼
┌──────────────────┐ ┌──────────────┐ ┌─────────────────┐
│   INDEXING       │ │  RETRIEVAL   │ │   GENERATION    │
│   PIPELINE       │ │   PIPELINE   │ │   PIPELINE      │
└──────────────────┘ └──────────────┘ └─────────────────┘
```

## Detailed Component Architecture

### 1. Document Processing Layer

```
src/document_processing/
├── extractors.py       → Extract text from PDF/DOCX/TXT
├── chunker.py          → Smart chunking with overlap
└── preprocessor.py     → Text cleaning & normalization

Flow:
File → Extract → Clean → Chunk → Metadata
```

**Key Features:**

- Multi-format support (PDF, DOCX, TXT)
- Page-aware extraction
- Sentence-aware chunking
- Configurable chunk size & overlap
- Metadata preservation

### 2. Embedding Layer

```
src/embeddings/
├── generator.py        → Sentence-transformers integration
└── cache.py           → Embedding cache management

Flow:
Text → Tokenize → Encode → L2 Normalize → 384-dim vector
```

**Key Features:**

- sentence-transformers/all-MiniLM-L6-v2
- Batch processing for efficiency
- Persistent caching
- Normalized embeddings for cosine similarity

### 3. Vector Store Layer

```
src/vector_store/
├── client.py          → ChromaDB wrapper
└── indexer.py         → Document indexing orchestration

Flow:
Chunks + Embeddings + Metadata → ChromaDB → Persistent Storage
```

**Key Features:**

- ChromaDB for vector storage
- Metadata filtering support
- Cosine similarity search
- Persistent on-disk storage
- Atomic operations

### 4. Retrieval Layer

```
src/retrieval/
├── retriever.py       → Semantic search engine
└── reranker.py        → Result reranking (optional)

Flow:
Query → Embed → Similarity Search → Filter → Rerank → Top-K Results
```

**Key Features:**

- Semantic similarity search
- Configurable top-K
- Similarity threshold filtering
- Diversity-based reranking
- Source aggregation

### 5. Generation Layer

```
src/generation/
├── llm_client.py         → OpenAI/Local LLM client
├── prompt_templates.py   → RAG prompt engineering
└── citation_parser.py    → Citation extraction & validation

Flow:
Query + Sources → Format Prompt → LLM API → Parse Citations → Response
```

**Key Features:**

- OpenAI GPT-3.5/4 support
- Local LLM via Ollama
- Retry logic with exponential backoff
- Citation-enforcing prompts
- Citation validation

### 6. Service Layer (Orchestrator)

```
src/api/
├── service.py         → RAGService (main orchestrator)
└── models.py          → Pydantic data models

Flow:
User Request → RAGService → [Index/Query Pipeline] → Response
```

**Key Features:**

- High-level API abstraction
- Component initialization & management
- Error handling & logging
- Statistics & monitoring

## Data Flow Diagrams

### Indexing Pipeline

```
┌──────────┐
│   File   │
└────┬─────┘
     │
     ▼
┌──────────────────┐
│ Text Extraction  │ (extractors.py)
└────┬─────────────┘
     │  [text, page, metadata]
     ▼
┌──────────────────┐
│  Text Chunking   │ (chunker.py)
└────┬─────────────┘
     │  [chunks with overlap]
     ▼
┌──────────────────┐
│ Embedding Gen.   │ (generator.py)
└────┬─────────────┘
     │  [384-dim vectors]
     ▼
┌──────────────────┐
│  Vector Store    │ (ChromaDB)
└──────────────────┘
   [Persisted to disk]
```

### Query Pipeline (RAG)

```
┌──────────────┐
│ User Query   │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ Query Embedding  │ (generator.py)
└──────┬───────────┘
       │  [384-dim vector]
       ▼
┌──────────────────┐
│ Similarity Search│ (retriever.py)
└──────┬───────────┘
       │  [top-K chunks]
       ▼
┌──────────────────┐
│   Reranking      │ (reranker.py, optional)
└──────┬───────────┘
       │  [reordered chunks]
       ▼
┌──────────────────┐
│ Prompt Creation  │ (prompt_templates.py)
└──────┬───────────┘
       │  [system + user prompt]
       ▼
┌──────────────────┐
│  LLM Generation  │ (llm_client.py)
└──────┬───────────┘
       │  [answer with citations]
       ▼
┌──────────────────┐
│ Citation Parse   │ (citation_parser.py)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  RAG Response    │
└──────────────────┘
```

## Key Design Patterns

### 1. Dependency Injection

- Components accept dependencies via constructor
- Allows easy mocking for tests
- Supports multiple implementations (e.g., FAISS vs ChromaDB)

### 2. Factory Pattern

- Configuration-based instantiation
- Settings loaded from `.env`
- Centralized in `src/core/config.py`

### 3. Strategy Pattern

- Different extractors for different formats
- Pluggable reranking strategies
- Configurable LLM backends

### 4. Repository Pattern

- `ChromaDBClient` abstracts vector store operations
- Easy to swap implementations
- Consistent interface

### 5. Pipeline Pattern

- Indexing: Extract → Chunk → Embed → Store
- Retrieval: Query → Retrieve → Rerank → Generate

## Configuration Management

```python
# src/core/config.py
class Settings(BaseSettings):
    # LLM
    openai_api_key: str
    openai_model: str = "gpt-3.5-turbo"

    # Embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Chunking
    chunk_size: int = 300
    chunk_overlap: int = 50

    # Retrieval
    top_k_retrieval: int = 5
    similarity_threshold: float = 0.7

    # Storage
    chroma_persist_dir: Path = "./data/vectordb"
```

All settings loaded from `.env` with validation via Pydantic.

## Error Handling Hierarchy

```
DocuMindException (base)
├── DocumentProcessingError
├── EmbeddingGenerationError
├── VectorStoreError
├── RetrievalError
├── LLMError
├── ChunkingError
└── ValidationError
```

Each layer raises specific exceptions for clear error tracking.

## Logging Strategy

- **Library:** loguru
- **Levels:** DEBUG, INFO, WARNING, ERROR
- **Outputs:**
  - Console (colored, human-readable)
  - File (rotating, 10MB max, 7-day retention)
- **Format:** Timestamp | Level | Module:Function:Line | Message

## Performance Optimizations

1. **Embedding Caching:** Cache generated embeddings on disk
2. **Batch Processing:** Encode multiple texts in one forward pass
3. **Lazy Loading:** Models loaded only when needed
4. **Normalized Embeddings:** Pre-normalized for faster cosine similarity
5. **Top-K Limiting:** Retrieve only needed chunks
6. **Connection Pooling:** Reuse LLM client connections

## Scalability Considerations

**Current (MVP):**

- Local ChromaDB storage
- Single-machine deployment
- File-based caching

**Future (Production):**

- Managed vector DB (Pinecone/Weaviate)
- Redis for caching
- FastAPI service with load balancing
- Async operations
- Distributed embeddings generation

## Testing Strategy

```
tests/
├── test_extractors.py     → Unit tests for extraction
├── test_chunker.py        → Unit tests for chunking
├── test_retrieval.py      → Integration tests for retrieval
└── test_e2e.py (future)   → End-to-end RAG tests
```

Uses pytest with fixtures for isolated testing.

## Future Extensions

### Multimodal Support

**Images:**

```
Image → OCR (Tesseract) → Text chunks
Image → CLIP encoding → Image embeddings
Unified index: [text chunks + image chunks]
```

**Audio:**

```
Audio → Whisper STT → Transcript with timestamps
Transcript → Chunk (10-30s windows) → Embed → Index
Citation: "At 2:35 in meeting_recording.mp3"
```

**Unified Retrieval:**

- Single query retrieves text + image + audio chunks
- Cross-modal embeddings (CLIP for text+image alignment)
- Metadata indicates chunk type for proper rendering

## Security Considerations

1. **API Keys:** Never commit to version control, use `.env`
2. **Input Validation:** Pydantic models validate all inputs
3. **File Upload:** Validate file types and size limits
4. **SQL Injection:** ChromaDB uses parameterized queries
5. **Rate Limiting:** Add for production API deployment

## Monitoring & Observability

**Current:**

- Structured logging with loguru
- Console + file outputs
- Error tracking in logs

**Future:**

- Prometheus metrics
- Grafana dashboards
- APM tools (DataDog, New Relic)
- Usage analytics

---

This architecture provides a solid foundation for a production RAG system while remaining hackathon-friendly with quick setup and clear separation of concerns.
