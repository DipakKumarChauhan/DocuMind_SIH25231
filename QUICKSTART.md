# DocuMind Quick Start Guide

## Installation

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run setup
python setup.py
```

## Configuration

Edit `.env` file and add your OpenAI API key:

```bash
OPENAI_API_KEY=your_api_key_here
```

## Running the Application

### Option 1: Streamlit UI (Recommended for Demo)

```bash
streamlit run ui/streamlit_app.py
```

Then open http://localhost:8501 in your browser.

### Option 2: Command Line Interface

```bash
# Index documents
python cli.py index path/to/document.pdf

# Index all documents in a directory
python cli.py index -d path/to/documents/

# Query
python cli.py query "What is the project timeline?"

# View statistics
python cli.py stats

# Clear all data
python cli.py clear
```

### Option 3: Python API

```python
from src.api import RAGService

# Initialize service
service = RAGService()

# Index documents
results = service.index_documents(["document.pdf", "report.docx"])

# Query
response = service.query("What are the key findings?")
print(response.answer)

# View citations
for citation_num, source in response.citation_map.items():
    print(f"[{citation_num}] {source['file_name']} - Page {source['page']}")
```

## Features

✅ **Multi-format Support**: PDF, DOCX, TXT
✅ **Semantic Search**: Sentence-transformers embeddings
✅ **Citation-Based Answers**: Every claim is cited
✅ **Persistent Storage**: ChromaDB for vector storage
✅ **Interactive UI**: Streamlit dashboard
✅ **CLI Tool**: Command-line interface
✅ **Modular Architecture**: Production-ready code structure

## Architecture Overview

```
Upload → Extract → Chunk → Embed → Store
                                      ↓
Query → Embed → Retrieve → Rank → Generate (with citations)
```

## Extending to Multimodal

To add image/audio support later:

1. **Images**: Add CLIP embeddings in `src/embeddings/`
2. **Audio**: Add Whisper STT in `src/document_processing/`
3. **Unified indexing**: Modify `DocumentIndexer` to handle multiple modalities

## Troubleshooting

**Import errors**: Run `pip install -r requirements.txt` again

**NLTK errors**: Run `python -c "import nltk; nltk.download('punkt')"`

**ChromaDB errors**: Delete `data/vectordb/` and restart

**OpenAI errors**: Check your API key in `.env`

## Project Structure

```
DocuMind_cursor/
├── src/
│   ├── core/              # Configuration & logging
│   ├── document_processing/  # Text extraction & chunking
│   ├── embeddings/        # Embedding generation
│   ├── vector_store/      # ChromaDB integration
│   ├── retrieval/         # Semantic search
│   ├── generation/        # LLM integration
│   └── api/               # High-level service API
├── ui/                    # Streamlit interface
├── tests/                 # Unit tests
├── data/                  # Storage (uploads, cache, vectordb)
└── logs/                  # Application logs
```

## Performance Tips

- Use `batch_size=32` for faster embedding generation
- Cache embeddings with `cache_embeddings=True`
- Adjust `chunk_size` and `overlap` for your use case
- Use `top_k=3-5` for faster retrieval
- Consider using local LLM (Ollama) for cost savings

## License

MIT
