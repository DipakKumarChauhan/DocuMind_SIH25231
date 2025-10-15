# DocuMind Frontend-Backend Integration Guide

## ✅ What Was Done

### 1. Frontend Setup

- **Created React + Vite application** in `/frontend` directory
- **Installed dependencies:**
  - React 18.2.0 (UI framework)
  - Lucide React (icons)
  - Tailwind CSS (styling)
  - Vite (build tool)

### 2. Backend Integration

- **Created API service** (`/frontend/src/api.js`) to communicate with FastAPI backend
- **Configured CORS** - Backend allows requests from frontend
- **Connected endpoints:**
  - `/health` - Health check
  - `/documents/upload` - Upload PDFs, DOCX, TXT files
  - `/query` - Query documents with RAG
  - `/stats` - Get system statistics

### 3. Features Implemented

#### Document Upload

- Drag & drop file upload in Uploads tab
- Supports: PDF, DOCX, TXT
- Shows upload progress and success/error messages
- Displays uploaded files with chunk count

#### Query Interface

- Real-time question answering
- Citation-based responses
- Source highlighting with similarity scores
- Loading states and error handling

#### UI Components

- **Icon Sidebar** - Quick navigation
- **Expandable Sidebar** - Chat history, uploads management
- **Main Chat Area** - Conversation interface
- **Backend Status Banner** - Shows connection status

### 4. Backend Improvements

- **Enhanced prompt template** for more detailed answers
- **Increased context window** (300 → 800 chars) for better responses
- Modified system prompt to encourage comprehensive answers

## 🚀 How to Run

### Terminal 1: Start Backend

```bash
cd /home/dipak/DocuMind_cursor
source .venv/bin/activate
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**Backend will be available at:** http://localhost:8000

- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Terminal 2: Start Frontend

```bash
cd /home/dipak/DocuMind_cursor/frontend
npm run dev
```

**Frontend will be available at:** http://localhost:3000

## 📋 How to Use

### Step 1: Upload Documents

1. Click the **Upload** icon (↑) in the left sidebar
2. Click "Upload Files" button
3. Select PDF, DOCX, or TXT files
4. Wait for indexing to complete
5. Files appear in the uploads list with chunk count

### Step 2: Ask Questions

1. Click the **Chat** icon (💬) in the left sidebar
2. Type your question in the input box
3. Press Enter or click Send
4. Get answer with citations and sources

### Example Questions:

- "What is Word2Vec?"
- "Summarize the main methodology"
- "What technology stack was used?"

## 🔧 API Response Format

### Backend Returns:

```json
{
  "query": "Your question",
  "answer": "Answer with citations [1], [2]...",
  "sources": [
    {
      "text": "Source content",
      "file_name": "document.pdf",
      "page": 1,
      "similarity_score": 0.85,
      "chunk_id": 0
    }
  ],
  "citations": [1, 2],
  "metadata": { ... }
}
```

### Frontend Displays:

- **Answer** with embedded citations
- **Detailed sources** with:
  - Source number [1], [2], etc.
  - Filename and page
  - Similarity score (match percentage)
  - Full source text
  - Query processing time

## 🎨 UI Features

### Backend Status Indicator

- 🟢 **Connected** - Green indicator (hidden)
- 🔵 **Checking** - Blue banner at top
- 🔴 **Disconnected** - Red banner with retry button

### Upload States

- ⏳ **Uploading** - Gray button, disabled
- ✅ **Success** - Green notification with file count
- ❌ **Error** - Red notification with error message

### Query States

- 💬 **Ready** - Input enabled, blue send button
- ⏳ **Loading** - Animated dots while processing
- ✅ **Response** - Answer with sources displayed
- ❌ **Error** - Red error message

## 🐛 Troubleshooting

### Backend Not Starting

```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies if needed
pip install -r requirements.txt
```

### Frontend Issues

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check port 3000 is free
lsof -ti:3000 | xargs kill -9  # Kill process on port 3000
```

### CORS Errors

- Backend has `allow_origins=["*"]` in `app.py`
- Check backend is running on port 8000
- Verify frontend uses http://localhost:8000 in API calls

### NaN Scores / Unknown Sources

- **Fixed** - Frontend now properly maps backend response fields
- `text` → `content`
- `similarity_score` → `score`
- `file_name` → `metadata.file_name`

## 📊 Current Status

✅ **Backend Running** - Port 8000  
✅ **Frontend Running** - Port 3000  
✅ **API Connected** - CORS enabled  
✅ **File Upload** - Working  
✅ **Query System** - Working  
✅ **Citations** - Displaying correctly  
✅ **Sources** - Showing with scores  
✅ **Answer Quality** - Enhanced prompts

## 🔄 Recent Fixes

1. **NaN Scores Fixed** - Properly mapped `similarity_score` field
2. **Unknown Sources Fixed** - Correctly extracting `file_name` from metadata
3. **Short Answers Fixed** - Updated prompt template for detailed responses
4. **Context Window** - Increased from 300 to 800 characters
5. **UI Polish** - Better source display with gradients and badges

## 📁 File Structure

```
/home/dipak/DocuMind_cursor/
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component
│   │   ├── api.js           # Backend API client
│   │   ├── main.jsx         # React entry point
│   │   └── index.css        # Tailwind styles
│   ├── package.json         # Dependencies
│   ├── vite.config.js       # Vite config
│   └── .env                 # API URL config
├── src/
│   ├── api/service.py       # RAG service
│   └── generation/
│       └── prompt_templates.py  # LLM prompts
└── app.py                   # FastAPI backend
```

## 🎯 Next Steps (Optional Enhancements)

1. **Add chat history** - Save conversations to backend
2. **File management** - Delete uploaded documents
3. **Advanced filters** - Filter by file, date, relevance
4. **Export results** - Download answers as PDF/TXT
5. **Multi-language** - Support for Bengali interface
6. **Voice input** - Speech-to-text for queries
7. **Dark mode** - Theme toggle

---

**Created:** October 15, 2025  
**Status:** ✅ Fully Functional  
**Tech Stack:** React + Vite + Tailwind CSS + FastAPI + ChromaDB + Gemini
