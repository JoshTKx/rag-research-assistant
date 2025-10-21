"""
FastAPI wrapper for RAG system
"""

from fastapi import FastAPI, HTTPException,UploadFile, File
from pydantic import BaseModel
from typing import Optional
import chromadb
import day3_rag_query
import day2_document_processing
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
db_path = "./chroma_db"

try:
    chroma_client = chromadb.PersistentClient(path=db_path)
    collection = chroma_client.get_collection(name= "ml_documents")
    logger.info("Connected to ChromaDB collection")
    logger.info(f"Collection has {collection.count()} chunks")
except Exception as e:
    logger.error(f"Failed to connect to ChromaDB: {e}")
    collection = None

app = FastAPI(
    title="RAG Research Assistant API",
    description= "API for document Q&A using RAG",
    version= "1.0.0"
)

@app.get("/")
def read_root():
    """
    Root endpoint - health check
    
    """
    return {
        "message": "RAG API is running",
        "status" : "healthy"
    }

@app.get("/health")
def health_check():
    """
    Health check endpoint
    """
    return {
        "status" : "healthy",
        "version" : app.version
    }



# Request/Response models
class QueryRequest(BaseModel):
    """
    Request model for /query endpoint
    
    """
    # YOUR CODE HERE
    question : str
    n_results: Optional[int] = 3


class QueryResponse(BaseModel):
    """
    Response model for /query endpoint
    
    TODO: Define what we return:
    - question: str (echo back the question)
    - answer: str (the generated answer)
    - sources: list[str] (list of source citations)
    - num_chunks_used: int (how many chunks were retrieved)
    
    Example:
    {
        "question": "What is Total Defence?",
        "answer": "Total Defence is...",
        "sources": ["doc.pdf (Page 3)", "doc.pdf (Page 5)"],
        "num_chunks_used": 3
    }
    """
    # YOUR CODE HERE
    question: str
    answer: str
    sources : list[str]
    num_chunks_used : int


@app.post("/query", response_model=QueryResponse)
def query_documents(request: QueryRequest):
    """
    Query the RAG system
    
    Args:
        request: QueryRequest with question and n_results
        
    Returns:
        QueryResponse with answer and sources
        
    """


    logger.info(f"Received question: {request.question}")

    if not collection:
        raise HTTPException(status_code=500, detail="Database not initialised")
    
    if not request.question or request.question.strip() == "":
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    if request.n_results < 1 or request.n_results > 10:
        raise HTTPException(status_code=400, detail="n_results must be between 1 and 10")
    
    try:
        logger.info(f"Querying RAG system")
        reply = day3_rag_query.query_rag_system(
            question= request.question, 
            collection= collection, 
            n_results= request.n_results)
        
        return QueryResponse(
            question= request.question,
            answer = reply["answer"],
            sources= reply["sources"],
            num_chunks_used = len(reply["context_chunks"])
        )

    except Exception as e:
        logger.error(f"Query Failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


