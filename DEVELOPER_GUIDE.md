# DocuMind Developer Quick Reference

## 🚀 Quick Commands

### Setup

```bash
./install.sh                          # One-command install
python setup.py                       # Manual setup
source venv/bin/activate              # Activate environment
```

### Run Application

```bash
streamlit run ui/streamlit_app.py     # Web UI
python cli.py --help                  # CLI help
python example.py                     # API example
```

### CLI Commands

```bash
python cli.py index file.pdf          # Index single file
python cli.py index -d docs/          # Index directory
python cli.py query "Question?"       # Query
python cli.py stats                   # View stats
python cli.py clear -y                # Clear all data
```

### Testing

```bash
pytest tests/ -v                      # Run tests
pytest tests/ --cov=src               # With coverage
python -m pytest tests/test_chunker.py::test_chunk_text_basic  # Single test
```

---

## 📦 Import Patterns

### Basic Usage

```python
from src.api import RAGService

service = RAGService()
results = service.index_documents(["doc.pdf"])
response = service.query("Question?")
```

### Advanced - Custom Components

```python
from src.vector_store import ChromaDBClient, DocumentIndexer
from src.embeddings import EmbeddingGenerator
from src.retrieval import Retriever
from src.generation import LLMClient

# Custom setup
vector_client = ChromaDBClient(collection_name="custom")
embedding_gen = EmbeddingGenerator(model_name="custom-model")
llm = LLMClient(model="gpt-4", temperature=0.0)

# Use in service
service = RAGService(
    vector_client=vector_client,
    embedding_generator=embedding_gen,
    llm_client=llm
)
```

### Individual Components

```python
# Document processing
from src.document_processing import TextExtractor, TextChunker

extractor = TextExtractor()
doc = extractor.extract("file.pdf")

chunker = TextChunker(chunk_size=200, chunk_overlap=30)
chunks = chunker.chunk_document(doc)

# Embeddings
from src.embeddings import EmbeddingGenerator

generator = EmbeddingGenerator()
embeddings = generator.generate(["text1", "text2"])

# Vector store
from src.vector_store import ChromaDBClient

client = ChromaDBClient()
client.add_documents(texts, embeddings, metadatas)
results = client.query(query_embedding, n_results=5)

# Retrieval
from src.retrieval import Retriever

retriever = Retriever(top_k=5, similarity_threshold=0.7)
chunks = retriever.retrieve("query")

# Generation
from src.generation import LLMClient, PromptTemplates

llm = LLMClient()
system, user = PromptTemplates.create_full_rag_prompt(query, chunks)
answer = llm.generate_with_system_prompt(system, user)
```

---

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# LLM
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.1

# Local LLM Alternative
USE_LOCAL_LLM=false
LOCAL_LLM_ENDPOINT=http://localhost:11434
LOCAL_LLM_MODEL=llama2

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Chunking
CHUNK_SIZE=300
CHUNK_OVERLAP=50

# Retrieval
TOP_K_RETRIEVAL=5
SIMILARITY_THRESHOLD=0.7
```

### Programmatic Configuration

```python
from src.core.config import settings

# Access settings
print(settings.chunk_size)
print(settings.embedding_model)

# Modify at runtime (for testing)
settings.top_k_retrieval = 10
```

---

## 🗂️ File Locations

```
data/
├── uploads/        # User uploaded documents
├── cache/          # Embedding cache
├── vectordb/       # ChromaDB storage
└── logs/           # Application logs

logs/
└── documind.log    # Rotating log file
```

---

## 🐛 Debugging

### Enable Debug Logging

```python
# In code
from src.core.logger import app_logger
import logging

app_logger.level("DEBUG")

# Or in .env
LOG_LEVEL=DEBUG
```

### Check Logs

```bash
tail -f logs/documind.log              # Live log
grep ERROR logs/documind.log           # Find errors
```

### Test Individual Components

```python
# Test extractor
from src.document_processing import TextExtractor
doc = TextExtractor.extract("test.pdf")
print(doc)

# Test chunker
from src.document_processing import TextChunker
chunker = TextChunker()
chunks = chunker.chunk_text("Your text here")
print(len(chunks))

# Test embeddings
from src.embeddings import EmbeddingGenerator
gen = EmbeddingGenerator()
emb = gen.generate("test text")
print(emb.shape)
```

---

## 📊 Monitoring

### Get System Stats

```python
service = RAGService()
stats = service.get_stats()
print(stats)
```

### Vector Store Stats

```python
from src.vector_store import ChromaDBClient
client = ChromaDBClient()
print(client.get_stats())
```

### Cache Stats

```python
from src.embeddings import EmbeddingCache
cache = EmbeddingCache()
print(cache.get_stats())
```

---

## 🔧 Common Tasks

### Add New Document Format

```python
# In src/document_processing/extractors.py

@staticmethod
def extract_from_xlsx(file_path: Path) -> List[Dict[str, Any]]:
    # Your extraction logic
    return [{"page": 1, "text": "...", ...}]

# Register in extract() method
extractors = {
    '.pdf': TextExtractor.extract_from_pdf,
    '.docx': TextExtractor.extract_from_docx,
    '.xlsx': TextExtractor.extract_from_xlsx,  # Add this
}
```

### Change Embedding Model

```python
# In .env or code
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

# Or programmatically
generator = EmbeddingGenerator(
    model_name="your-model-name"
)
```

### Switch to Local LLM

```bash
# In .env
USE_LOCAL_LLM=true
LOCAL_LLM_ENDPOINT=http://localhost:11434
LOCAL_LLM_MODEL=llama2

# Or programmatically
llm = LLMClient(use_local=True, model="llama2")
```

### Custom Chunking Strategy

```python
chunker = TextChunker(
    chunk_size=500,      # Larger chunks
    chunk_overlap=100,   # More overlap
    max_chunk_size=1000  # Higher limit
)
```

---

## 🎨 Customization Examples

### Custom Prompt

```python
from src.generation import LLMClient

llm = LLMClient()

custom_system = """You are a legal expert.
Answer questions about contracts with citations."""

answer = llm.generate_with_system_prompt(
    system_prompt=custom_system,
    user_message="What are the terms?"
)
```

### Custom Reranking

```python
from src.retrieval import Reranker

# Use diversity reranking
reranker = Reranker(method="diversity")
reranked_chunks = reranker.rerank(chunks, query)
```

### Custom Filters

```python
# Query specific file
response = service.query(
    query="Question?",
    filters={"file_name": "contract.pdf"}
)

# Query specific page range
response = service.query(
    query="Question?",
    filters={"page": {"$gte": 10, "$lte": 20}}
)
```

---

## 🚨 Error Handling

```python
from src.core.exceptions import (
    DocumentProcessingError,
    EmbeddingGenerationError,
    VectorStoreError,
    RetrievalError,
    LLMError
)

try:
    service.index_documents(["file.pdf"])
except DocumentProcessingError as e:
    print(f"Failed to process document: {e}")
except EmbeddingGenerationError as e:
    print(f"Failed to generate embeddings: {e}")
```

---

## 📝 Response Structure

```python
response = service.query("Question?")

# Access answer
print(response.answer)

# Access sources
for source in response.sources:
    print(f"{source.file_name} - Page {source.page}")
    print(f"Score: {source.similarity_score}")

# Access citations
for num in response.citations:
    source = response.citation_map[num]
    print(f"[{num}] {source['file_name']}")
```

---

## 🎯 Performance Tips

1. **Batch index** multiple documents at once
2. **Use caching** for repeated embeddings
3. **Limit top_k** to 3-5 for faster retrieval
4. **Adjust chunk size** based on use case
5. **Use local LLM** for development (faster, free)

---

## 🔗 Useful Links

- [Sentence Transformers](https://www.sbert.net/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [OpenAI API](https://platform.openai.com/docs)
- [Streamlit Docs](https://docs.streamlit.io/)

---

## 🆘 Getting Help

1. Check logs: `logs/documind.log`
2. Run tests: `pytest tests/ -v`
3. Check example: `python example.py`
4. Review docs: `ARCHITECTURE.md`, `QUICKSTART.md`

---

**Quick Reference v1.0 - DocuMind RAG System**
