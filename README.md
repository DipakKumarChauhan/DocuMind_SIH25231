# DocuMind - Citation-Based RAG System with React Frontend

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![React](https://img.shields.io/badge/React-18.2-61DAFB.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A production-ready Retrieval-Augmented Generation (RAG) system with citation-based answers, featuring a modern React frontend and FastAPI backend.

[Features](#features) • [Quick Start](#quick-start) • [Architecture](#architecture) • [API](#api-documentation) • [Contributing](#contributing)

</div>

---

## 🌟 Features

### Backend

- 📄 **Multi-format Support** - PDF, DOCX, TXT document processing
- 🔍 **Semantic Search** - Sentence-transformers embeddings (384-dim)
- 🎯 **Citation-Based Answers** - No hallucinations, fully traceable sources
- 💾 **Persistent Storage** - ChromaDB vector database
- 🤖 **LLM Integration** - Google Gemini (configurable for OpenAI/local models)
- 🚀 **FastAPI Backend** - RESTful API with Swagger docs
- 📊 **Smart Chunking** - Sentence-aware with overlap for context preservation

### Frontend

- ⚛️ **React + Vite** - Fast, modern development experience
- 🎨 **Tailwind CSS** - Beautiful, responsive UI
- 📤 **File Upload** - Drag & drop document upload
- 💬 **Real-time Chat** - Interactive query interface
- 📚 **Source Display** - Detailed source citations with similarity scores
- ⚡ **Live Status** - Backend connection monitoring
- 🌓 **Clean UI** - Professional, user-friendly interface

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Node.js 16+** and npm
- **Git**
- **Google Gemini API Key** (or OpenAI API key)

### 1. Clone the Repository

```bash
git clone git@github.com:DipakKumarChauhan/DocuMind_SIH25231.git
cd DocuMind_SIH25231
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API key
nano .env  # or use any text editor
```

Add your API key to `.env`:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Go back to project root
cd ..
```

### 4. Run the Application

#### Terminal 1: Start Backend

```bash
# Make sure virtual environment is activated
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Start FastAPI server
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at:

- **API:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

#### Terminal 2: Start Frontend

```bash
# Navigate to frontend
cd frontend

# Start Vite dev server
npm run dev
```

Frontend will be available at:

- **App:** http://localhost:3000

### 5. Use the Application

1. **Open** http://localhost:3000 in your browser
2. **Click** the Upload icon (↑) in the sidebar
3. **Upload** PDF, DOCX, or TXT files
4. **Wait** for indexing to complete
5. **Click** the Chat icon (💬)
6. **Ask** questions about your documents
7. **Get** citation-based answers with source references!

---

---

## 📁 Project Structure

```
DocuMind/
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── App.jsx            # Main React component
│   │   ├── api.js             # Backend API client
│   │   ├── main.jsx           # React entry point
│   │   └── index.css          # Tailwind styles
│   ├── package.json           # Frontend dependencies
│   └── vite.config.js         # Vite configuration
├── src/                       # Backend Python Code
│   ├── api/
│   │   ├── models.py          # Pydantic models
│   │   └── service.py         # RAG service orchestration
│   ├── core/
│   │   ├── config.py          # Configuration management
│   │   ├── logger.py          # Logging setup
│   │   └── exceptions.py      # Custom exceptions
│   ├── document_processing/
│   │   ├── extractors.py      # PDF/DOCX text extraction
│   │   ├── chunker.py         # Smart text chunking
│   │   └── preprocessor.py    # Text cleaning
│   ├── embeddings/
│   │   ├── generator.py       # Embedding generation
│   │   └── cache.py           # Embedding cache
│   ├── vector_store/
│   │   ├── client.py          # ChromaDB client
│   │   └── indexer.py         # Document indexing
│   ├── retrieval/
│   │   ├── retriever.py       # Similarity search
│   │   └── reranker.py        # Result reranking
│   └── generation/
│       ├── llm_client.py      # LLM integration
│       ├── prompt_templates.py # RAG prompts
│       └── citation_parser.py # Citation parsing
├── data/
│   ├── uploads/               # User uploaded files
│   ├── vectordb/              # ChromaDB storage
│   └── cache/                 # Embedding cache
├── tests/                     # Unit tests
├── app.py                     # FastAPI application
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
└── README.md                 # This file
```

---

## 🏗️ Architecture

### System Flow

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   React     │─────▶│   FastAPI    │─────▶│  ChromaDB   │
│  Frontend   │◀─────│   Backend    │◀─────│  VectorDB   │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │ Gemini LLM   │
                     └──────────────┘
```

### Key Components

1. **Document Processing** - Extracts text from PDFs, DOCX, TXT
2. **Chunking** - Splits text into 300-token chunks with 50-token overlap
3. **Embedding** - Generates 384-dim vectors using sentence-transformers
4. **Vector Store** - Stores embeddings in ChromaDB with metadata
5. **Retrieval** - Finds top-K similar chunks using cosine similarity
6. **Generation** - LLM generates citation-based answers
7. **Frontend** - React UI for document upload and queries

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# LLM Configuration
GOOGLE_API_KEY=your_gemini_api_key_here
LLM_PROVIDER=gemini  # Options: gemini, openai, local
LLM_MODEL=gemini-2.5-flash

# Optional: OpenAI
# OPENAI_API_KEY=your_openai_key

# Vector Store
VECTOR_DB_TYPE=chromadb
CHROMA_PERSIST_DIR=data/vectordb

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Chunking
CHUNK_SIZE=300
CHUNK_OVERLAP=50

# Retrieval
TOP_K=5
SIMILARITY_THRESHOLD=0.3
```

### Get API Keys

- **Google Gemini:** https://makersuite.google.com/app/apikey
- **OpenAI:** https://platform.openai.com/api-keys

---

## 📚 API Documentation

### Upload Documents

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "files=@document.pdf" \
  -F "files=@report.docx"
```

### Query Documents

```bash
curl -X POST "http://localhost:8000/query?query=What%20is%20the%20summary&top_k=5"
```

### Get Statistics

```bash
curl "http://localhost:8000/stats"
```

### Health Check

```bash
curl "http://localhost:8000/health"
```

**Interactive API Docs:** http://localhost:8000/docs

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_chunker.py

# Run with coverage
pytest --cov=src tests/
```

---

---

## 💡 Key Design Decisions

### Chunking Strategy

- **Chunk size:** 300 tokens (~200-400 words)
- **Overlap:** 50 tokens to preserve context
- **Method:** Sentence-aware splitting
- **Why:** Balance between precision (small chunks) and context (overlap)

### Embedding Model

- **Model:** `sentence-transformers/all-MiniLM-L6-v2`
- **Dimension:** 384
- **Why:** Fast, lightweight, excellent semantic understanding

### Vector Store

- **Primary:** ChromaDB with persistence
- **Why:** Metadata filtering + persistence out of the box
- **Location:** `data/vectordb/`

### Retrieval

- **Top-K:** 5 chunks (configurable)
- **Similarity:** Cosine similarity
- **Threshold:** 0.3 minimum score
- **Metadata:** file_name, page, chunk_id for precise citation

### LLM Integration

- **Default:** Google Gemini 2.5 Flash
- **Alternatives:** OpenAI GPT-3.5/4, Local models (Ollama)
- **Prompt:** System prompt enforces citation format [1], [2]

---

## 🚧 Roadmap

### ✅ Phase 1: Text-based RAG (Complete)

- [x] PDF, DOCX, TXT extraction
- [x] Semantic chunking & indexing
- [x] Citation-based answers
- [x] React frontend
- [x] FastAPI backend
- [x] Real-time query interface

### 🔄 Phase 2: Enhanced Features (In Progress)

- [ ] Multi-user support
- [ ] Authentication & authorization
- [ ] Chat history persistence
- [ ] Document management (delete, update)
- [ ] Advanced filtering options
- [ ] Export results (PDF/TXT)

### 🔮 Phase 3: Multimodal Support (Future)

- [ ] Image support with OCR
- [ ] CLIP embeddings for images
- [ ] Audio transcription (Whisper)
- [ ] Video processing
- [ ] Unified multimodal retrieval

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m "Add your feature"`
4. Push to branch: `git push origin feature/your-feature`
5. Submit a pull request

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint/Prettier for JavaScript
- Write tests for new features
- Update documentation
- Keep commits atomic and descriptive

---

## 🐛 Troubleshooting

### Backend Issues

**Issue:** Module not found errors

```bash
# Solution: Reinstall dependencies
pip install -r requirements.txt
```

**Issue:** ChromaDB telemetry errors (safe to ignore)

```
Failed to send telemetry event...
```

These are warnings and don't affect functionality.

**Issue:** Port 8000 already in use

```bash
# Solution: Kill process or use different port
python -m uvicorn app:app --port 8001 --reload
```

### Frontend Issues

**Issue:** Cannot connect to backend

- Ensure backend is running on port 8000
- Check `.env` file has correct `VITE_API_URL`
- Verify CORS is enabled in backend

**Issue:** npm install fails

```bash
# Solution: Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Issue:** Port 3000 already in use

```bash
# Solution: Vite will auto-select next available port
# Or specify port in vite.config.js
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Dipak Kumar Chauhan** - [@DipakKumarChauhan](https://github.com/DipakKumarChauhan)

---

## 🙏 Acknowledgments

- **Sentence Transformers** - For embedding models
- **ChromaDB** - For vector database
- **Google Gemini** - For LLM capabilities
- **FastAPI** - For backend framework
- **React** - For frontend framework
- **Vite** - For blazing fast development

---

## 📞 Support

For issues, questions, or suggestions:

- Open an issue on [GitHub](https://github.com/DipakKumarChauhan/DocuMind_SIH25231/issues)
- Email: dipak@documind.ai

---

<div align="center">

**⭐ Star this repo if you find it useful!**

Made with ❤️ for SIH 2025

</div>
