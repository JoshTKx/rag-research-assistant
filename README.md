# RAG Research Assistant

A production-ready Retrieval-Augmented Generation (RAG) system for document Q&A.

## 🎯 Current Status: Day 3 Complete

✅ Vector database with semantic search
✅ PDF document processing pipeline  
✅ LLM integration (Gemini 2.5 Flash)
✅ REST API with FastAPI
✅ Document upload functionality

## 🚀 Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Start the API
uvicorn day3_api:app --reload

# Upload a document
curl -X POST http://localhost:8000/upload -F "file=@document.pdf"

# Ask questions
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this about?"}'
```

## 📚 API Endpoints

- `POST /upload` - Upload PDF documents
- `POST /query` - Ask questions, get answers with sources
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI
- **Vector DB**: ChromaDB
- **LLM**: Google Gemini 2.5 Flash
- **Document Processing**: pypdf
- **Coming Soon**: Docker, Cloud Deployment

## 📈 Progress

- [x] Day 1: Vector database fundamentals
- [x] Day 2: Document processing pipeline
- [x] Day 3: RAG system + API
- [ ] Day 4: Docker + Deployment
- [ ] Day 5: Polish + Documentation

---

**Learning Project**: Building from first principles to deeply understand RAG systems for AI/ML engineering roles.
