# RAG Research Assistant

> An intelligent document Q&A system using Retrieval-Augmented Generation (RAG)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.119-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This is a "Chat with your PDF" API that transforms dense documents into a conversational research partner. You upload a PDF, and it uses Retrieval-Augmented Generation (RAG) to find the most relevant information and generate accurate, context-aware answers. The best part is that every answer comes with source citations, showing you exactly where in the document the information was found.
## Features

-  **PDF Document Processing** - Intelligent chunking with semantic preservation
-  **Semantic Search** - Vector embeddings for accurate retrieval
-  **AI-Powered Answers** - Context-aware responses using Gemini 2.5 Flash
-  **Source Citations** - Answers include page references for verification
-  **REST API** - Clean FastAPI interface with auto-generated docs
-  **Containerized** - Production-ready Docker deployment
-  **Cloud-Ready** - Deployed and tested on Render

## Use Cases

- **Academic Research**: A student uploads a 50-page scientific paper and asks, "What was the main conclusion of this study?" The API reads the paper, synthesizes the conclusion, and provides the page number where it's stated.

- **Legal & Compliance**: A paralegal uploads a complex, 100-page contract and asks, "What are the penalty clauses for a breach of contract?" The system retrieves the exact clauses and their page numbers, saving hours of manual review.

- **Business Analysis**: An analyst uploads a lengthy annual financial report. They can immediately query, "What was the company's Q4 revenue and what factors did they cite for its growth?" and get a direct answer with sources.

## Architecture

```
┌─────────────┐
│   Upload    │
│     PDF     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Extract &  │
│    Chunk    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   ChromaDB  │
│   (Vectors) │
└──────┬──────┘
       │
Query  │
  ┌────┴────┐
  │         │
  ▼         ▼
Retrieve   LLM
Context  Generate
  │         │
  └────┬────┘
       ▼
   Answer +
   Sources
```

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (optional)
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/rag-research-assistant.git
cd rag-research-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Running Locally

**Option 1: With Docker (Recommended)**
```bash
docker-compose up
```

**Option 2: Directly**
```bash
uvicorn src.api:app --reload
```

Visit: http://localhost:8000/docs for interactive API documentation

## API Usage

### Upload a Document
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@document.pdf"
```

### Query Documents
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is this document about?",
    "n_results": 3
  }'
```

**Response:**
```json
{
  "question": "What is this document about?",
  "answer": "Based on the document...",
  "sources": ["document.pdf (Page 3)", "document.pdf (Page 7)"],
  "num_chunks_used": 3
}
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/upload` | POST | Upload PDF document |
| `/query` | POST | Ask questions about documents |
| `/docs` | GET | Interactive API documentation |

## Tech Stack

**Backend:**
- [FastAPI](https://fastapi.tiangolo.com/) - Modern async web framework
- Python 3.11 - Core language

**AI/ML:**
- [Google Gemini 2.5 Flash](https://ai.google.dev/) - Large language model
- [ChromaDB](https://www.trychroma.com/) - Vector database
- Sentence Transformers - Text embeddings

**Infrastructure:**
- Docker & Docker Compose - Containerization
- Render - Cloud deployment

## Project Structure
```
rag-research-assistant/
├── src/
│   ├── __init__.py
│   ├── api.py                  # FastAPI application
│   ├── rag_engine.py           # RAG query pipeline
│   └── document_processor.py   # PDF processing & chunking
├── tests/
│   ├── __init__.py
│   └── test_api.py             # API tests
├── docs/
│   ├── ARCHITECTURE.md         # System design
│   └── DEPLOYMENT.md           # Deployment guide
├── archive/
│   └── learning/               # Learning exercises
├── Dockerfile                  # Container definition
├── docker-compose.yml          # Multi-container setup
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
└── README.md                   # This file
```

## Testing
```bash
# Run tests
pytest tests/

# Test specific file
pytest tests/test_api.py -v

# With coverage
pytest --cov=src tests/
```

## Deployment

### Deploy to Render (Free)

1. Push to GitHub
2. Create new Web Service on [Render](https://render.com)
3. Connect your repository
4. Configure:
   - **Runtime:** Docker
   - **Instance Type:** Free
5. Add environment variable: `GEMINI_API_KEY`
6. Deploy!

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions.

### Deploy to Google Cloud Run

[Coming soon]

## Configuration

Environment variables (in `.env`):
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional
CHROMA_DB_PATH=./chroma_db
COLLECTION_NAME=ml_documents
LOG_LEVEL=INFO
```

## Future Enhancements

- [ ] User authentication & authorization
- [ ] Conversation memory for follow-up questions
- [ ] Support for multiple LLM providers
- [ ] Web-based frontend interface
- [ ] Batch document processing
- [ ] Document versioning
- [ ] Advanced search filters
- [ ] Export conversations

## Development Notes

This project was built as a comprehensive learning exercise to understand:
- RAG (Retrieval-Augmented Generation) architecture
- Vector databases and semantic search
- FastAPI and production Python patterns
- Docker containerization
- Cloud deployment strategies

**Key Learnings:**
- Paragraph-based chunking preserves semantic meaning better than fixed-size
- Distance thresholds prevent irrelevant results
- Proper error handling is critical for production APIs
- Docker simplifies deployment significantly

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details

## Author

**Joshua Teo**
- GitHub: [@JoshTKx](https://github.com/JoshTKx)
- LinkedIn: [josh-teo](https://linkedin.com/in/josh-teo/)


## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [Google Gemini](https://ai.google.dev/)
- Vector search by [ChromaDB](https://www.trychroma.com/)

---

**Live Demo:** Coming soon after deployment!

**Status:** Complete MVP - Demonstrates RAG fundamentals and production deployment

Star this repo if you found it helpful!