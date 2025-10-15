# DocuMind - Multimodal RAG System

## Problem Statement

A semantic search and RAG system that indexes multiple data modalities (PDFs, DOCX, images, audio) into a unified semantic space, enabling users to query across all formats and receive grounded, citation-based answers from an LLM.

## Features (Text-Only Prototype)

- 📄 Multi-format document ingestion (PDF, DOCX, TXT)
- 🔍 Semantic search with sentence-transformers embeddings
- 🎯 Citation-based answers with source traceability
- 💾 Persistent vector storage with ChromaDB
- 🚀 Fast Streamlit UI for demo
- 📦 Modular, production-ready architecture

## Architecture

```
DocuMind/
├── src/
│   ├── core/
│   │   ├── config.py          # Configuration management
│   │   ├── logger.py          # Logging setup
│   │   └── exceptions.py      # Custom exceptions
│   ├── document_processing/
│   │   ├── extractors.py      # Text extraction from PDF/DOCX
│   │   ├── chunker.py         # Smart text chunking with overlap
│   │   └── preprocessor.py    # Text cleaning & normalization
│   ├── embeddings/
│   │   ├── generator.py       # Embedding generation
│   │   └── cache.py           # Embedding cache management
│   ├── vector_store/
│   │   ├── client.py          # ChromaDB client wrapper
│   │   └── indexer.py         # Document indexing logic
│   ├── retrieval/
│   │   ├── retriever.py       # Similarity search & ranking
│   │   └── reranker.py        # Optional reranking logic
│   ├── generation/
│   │   ├── llm_client.py      # LLM API client (OpenAI/local)
│   │   ├── prompt_templates.py # RAG prompt templates
│   │   └── citation_parser.py # Parse & validate citations
│   └── api/
│       ├── models.py          # Pydantic models
│       └── service.py         # Main RAG service orchestration
├── ui/
│   └── streamlit_app.py       # Streamlit frontend
├── tests/
│   ├── test_extractors.py
│   ├── test_chunker.py
│   └── test_retrieval.py
├── data/
│   ├── uploads/               # User uploaded documents
│   ├── vectordb/              # ChromaDB persistent storage
│   └── cache/                 # Embedding cache
├── requirements.txt
├── .env.example
└── README.md
```

## Installation

```bash
# Clone the repository
cd /home/dipak/DocuMind_cursor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt')"

# Setup environment
cp .env.example .env
# Edit .env with your OpenAI API key or local LLM endpoint
```

## Usage

```bash
# Run Streamlit app
streamlit run ui/streamlit_app.py

# Or use programmatically
python -c "from src.api.service import RAGService; service = RAGService()"
```

## Key Design Decisions

### Chunking Strategy

- **Chunk size**: 300 tokens (~200-400 words)
- **Overlap**: 50 tokens to preserve context
- **Method**: Sentence-aware splitting using NLTK
- **Why**: Balance between precision (small chunks) and context (overlap)

### Embedding Model

- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimension**: 384
- **Why**: Fast, lightweight, good semantic understanding

### Vector Store

- **Primary**: ChromaDB (local persistence)
- **Alternative**: FAISS (in-memory, faster)
- **Why**: ChromaDB offers metadata filtering + persistence out of the box

### Retrieval

- **Top-K**: 3-5 chunks
- **Similarity**: Cosine similarity
- **Metadata**: file_id, page, chunk_id, char offsets for precise citation

### LLM Integration

- **Default**: OpenAI GPT-3.5/4
- **Fallback**: Local models via Ollama
- **Prompt**: System prompt enforces citation format [1], [2]

## Roadmap

### Phase 1: Text-only RAG ✅

- PDF, DOCX, TXT extraction
- Semantic chunking & indexing
- Citation-based answers

### Phase 2: Image Support (Future)

- OCR with Tesseract/EasyOCR
- CLIP embeddings for images
- Unified text+image retrieval

### Phase 3: Audio Support (Future)

- Whisper STT for transcription
- Time-stamped chunk indexing
- Audio playback from citations

## Success Metrics

- ✅ End-to-end demo: Upload → Query → Cited Answer
- ✅ Clickable citations linking to source
- ✅ Retrieval precision validated manually
- ✅ Response time < 3s for typical query

## License

MIT
