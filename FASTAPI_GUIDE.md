# FastAPI + Gemini Integration Guide

## 🚀 Quick Start with FastAPI & Gemini

### 1. Get Your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your API key

### 2. Configure Environment

Edit `.env` file:

```bash
# Set Gemini as LLM provider
LLM_PROVIDER=gemini

# Add your Gemini API key
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-pro
GEMINI_TEMPERATURE=0.1
```

### 3. Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt
```

### 4. Start FastAPI Server

```bash
# Option 1: Using the startup script
./start_api.sh

# Option 2: Direct uvicorn command
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The server will start at: **http://localhost:8000**

---

## 📖 Accessing API Documentation

### Swagger UI (Interactive)

Open your browser: **http://localhost:8000/docs**

Features:

- Interactive API testing
- Try out all endpoints
- See request/response schemas
- Execute API calls directly from browser

### ReDoc (Documentation)

Open your browser: **http://localhost:8000/redoc**

Features:

- Clean, readable documentation
- Detailed endpoint descriptions
- Schema references
- Code examples

---

## 🧪 Testing with Swagger UI

### Step 1: Upload Documents

1. Go to **http://localhost:8000/docs**
2. Click on **POST /documents/upload**
3. Click **"Try it out"**
4. Click **"Choose File"** and select your documents (PDF, DOCX, or TXT)
5. Click **"Execute"**
6. View the response showing indexing results

### Step 2: Query Documents

1. Click on **POST /query**
2. Click **"Try it out"**
3. Enter your query in the `query` field (e.g., "What is the budget?")
4. Adjust `top_k` (number of sources, default: 5)
5. Toggle `rerank` if desired
6. Click **"Execute"**
7. View the response with:
   - Answer
   - Citations [1], [2], [3]
   - Source chunks with similarity scores

### Step 3: View Statistics

1. Click on **GET /stats**
2. Click **"Try it out"**
3. Click **"Execute"**
4. View system statistics

---

## 🔧 API Endpoints Reference

### 📄 **Documents**

#### Upload Documents

```
POST /documents/upload
```

Upload and index documents (PDF, DOCX, TXT)

**Request**: `multipart/form-data`

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "files=@document1.pdf" \
  -F "files=@document2.docx"
```

**Response**: `List[IndexingResult]`

```json
[
  {
    "file_name": "document1.pdf",
    "status": "success",
    "chunks_created": 45,
    "chunks_stored": 45,
    "total_pages": 10
  }
]
```

#### Delete Document

```
DELETE /documents/{filename}
```

Delete specific document by filename

**Example**:

```bash
curl -X DELETE "http://localhost:8000/documents/report.pdf"
```

#### Clear All Documents

```
DELETE /documents?confirm=true
```

Clear all indexed documents (requires confirmation)

**Example**:

```bash
curl -X DELETE "http://localhost:8000/documents?confirm=true"
```

---

### 🔍 **Query**

#### Query Documents

```
POST /query
```

Query indexed documents with RAG

**Parameters**:

- `query` (required): Your question
- `top_k` (optional): Number of sources (1-20, default: 5)
- `rerank` (optional): Enable reranking (default: true)
- `file_filter` (optional): Filter by filename

**Example**:

```bash
curl -X POST "http://localhost:8000/query?query=What%20is%20the%20budget?&top_k=5"
```

**Response**: `RAGResponse`

```json
{
  "query": "What is the budget?",
  "answer": "The budget is $50,000 according to the project timeline document [1].",
  "sources": [
    {
      "id": "abc123",
      "text": "Budget: $50,000",
      "file_name": "timeline.txt",
      "page": 1,
      "similarity_score": 0.89,
      "chunk_id": 5
    }
  ],
  "citations": [1],
  "citation_map": {
    "1": {
      "file_name": "timeline.txt",
      "page": 1,
      "text": "Budget: $50,000",
      "similarity_score": 0.89
    }
  },
  "num_sources": 1,
  "avg_similarity": 0.89
}
```

---

### 📊 **Statistics & Info**

#### Get Statistics

```
GET /stats
```

Get system statistics

**Example**:

```bash
curl http://localhost:8000/stats
```

**Response**:

```json
{
  "total_documents": 10,
  "total_chunks": 450,
  "collection_name": "documind_docs",
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "vector_db_type": "chromadb",
  "llm_model": "gemini-pro"
}
```

#### Get Model Info

```
GET /models/info
```

Get configured model information

**Example**:

```bash
curl http://localhost:8000/models/info
```

**Response**:

```json
{
  "llm": {
    "provider": "gemini",
    "model": "gemini-pro",
    "temperature": 0.1
  },
  "embedding": {
    "model": "sentence-transformers/all-MiniLM-L6-v2",
    "dimension": 384
  },
  "vector_store": {
    "type": "chromadb",
    "collection": "documind_docs"
  },
  "chunking": {
    "chunk_size": 300,
    "chunk_overlap": 50
  }
}
```

#### Health Check

```
GET /health
```

Check API health status

---

## 🐍 Python Client Example

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Upload documents
files = [
    ("files", open("document1.pdf", "rb")),
    ("files", open("document2.docx", "rb"))
]
response = requests.post(f"{BASE_URL}/documents/upload", files=files)
print("Upload:", response.json())

# Query
params = {
    "query": "What are the key findings?",
    "top_k": 5,
    "rerank": True
}
response = requests.post(f"{BASE_URL}/query", params=params)
result = response.json()

print("\nAnswer:", result["answer"])
print("\nCitations:")
for num, source in result["citation_map"].items():
    print(f"  [{num}] {source['file_name']} - Page {source['page']}")

# Get stats
response = requests.get(f"{BASE_URL}/stats")
print("\nStats:", response.json())
```

---

## 🧪 Testing Different LLM Providers

### Gemini (Default)

```bash
# .env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
```

### OpenAI

```bash
# .env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
```

### Local (Ollama)

```bash
# .env
LLM_PROVIDER=local
LOCAL_LLM_ENDPOINT=http://localhost:11434
LOCAL_LLM_MODEL=llama2
```

---

## 🔍 Advanced Usage

### Filter by Specific File

```bash
curl -X POST "http://localhost:8000/query?query=budget&file_filter=report.pdf"
```

### Adjust Retrieval Parameters

```bash
curl -X POST "http://localhost:8000/query?query=timeline&top_k=10&rerank=false"
```

---

## 🐛 Troubleshooting

### "Gemini API key not found"

- Check `.env` file exists
- Verify `GEMINI_API_KEY` is set correctly
- Restart the server after changing `.env`

### "Import errors"

```bash
pip install -r requirements.txt --force-reinstall
```

### "Port 8000 already in use"

```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app:app --port 8001
```

### View Logs

```bash
# Check application logs
tail -f logs/documind.log
```

---

## 📝 Example Workflow

```bash
# 1. Start server
./start_api.sh

# 2. Upload documents (in another terminal)
curl -X POST "http://localhost:8000/documents/upload" \
  -F "files=@sample.pdf"

# 3. Query
curl -X POST "http://localhost:8000/query?query=summary&top_k=3"

# 4. Check stats
curl http://localhost:8000/stats

# 5. Open browser for interactive testing
# http://localhost:8000/docs
```

---

## 🎯 Benefits of FastAPI + Swagger

✅ **Interactive Testing** - No need for Postman or curl  
✅ **Auto-Generated Docs** - Always up-to-date  
✅ **Type Safety** - Pydantic validation  
✅ **Performance** - Async support  
✅ **Easy Integration** - RESTful API  
✅ **CORS Support** - Frontend-ready

---

## 🚀 Next Steps

1. Open **http://localhost:8000/docs** in your browser
2. Try uploading a document
3. Test queries with different parameters
4. Explore the auto-generated documentation
5. Build your frontend integration!

Happy testing! 🎉
