"""
RAG Research Assistant API

A FastAPI application providing document Q&A capabilities using
Retrieval-Augmented Generation (RAG) with vector search and LLMs.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional
import chromadb
import logging
import tempfile
import os

from src import rag_engine
from src import document_processor

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger(__name__)

# ChromaDB configuration
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "ml_documents")

# Initialise ChromaDB
try:
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    try :
        collection = chroma_client.get_collection(name=COLLECTION_NAME)
        logger.info(f"Connected to ChromaDB collection: {COLLECTION_NAME}")
        logger.info(f"Collection has {collection.count()} chunks")
    except Exception:
        # Create collection if it doesn't exist
        collection = chroma_client.create_collection(name=COLLECTION_NAME)
        logger.info(f"Created new ChromaDB collection: {COLLECTION_NAME}")
        logger.info(f"Collection is empty - upload documents via /upload endpoint")
        
except Exception as e:
    logger.error(f"Failed to connect to ChromaDB: {e}")
    collection = None


# Initialise FastAPI
app = FastAPI(
    title="RAG Research Assistant API",
    description= "API for document Q&A using Retrieval-Augmented Generation",
    version= "1.0.0",
    docs_url='/docs',
    redoc_url='/redoc'
)



class InfoResponse(BaseModel):
    """
    API information response
    """

    message: str
    status: str
    version: str
    docs: str

@app.get(
        "/",
        response_model=InfoResponse,
        summary="Root endpoint",
        description="Returns basic API information and health status"
)
def read_root():
    """
    Root endpoint providing API information.
    
    Returns:
        dict: API status and basic information
    """
    return {
        "message": "RAG Research Assistant API",
        "status" : "healthy",
        "version": app.version,
        "docs": "/docs"
    }

@app.get(
        "/health",
        summary="Health check endpoint",
        description="Returns API health status and version"
)
def health_check():
    """
    Health check endpoint

    Returns:
        dict: API status and version
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
    question : str
    n_results: Optional[int] = 3


class QueryResponse(BaseModel):
    """
    Response model for /query endpoint
    """
    question: str
    answer: str
    sources : list[str]
    num_chunks_used : int

class UploadResponse(BaseModel):
    """
    Response model for /upload endpoint
    """
    filename : str
    num_chunks : int
    status : str

@app.post(
        "/query",
        response_model=QueryResponse,
        summary="Query endpoint",
        description="Accepts a QueryRequest with question and n_results and Returns Query Response with answer and sources"
)
def query_documents(request: QueryRequest):
    """
    Query the RAG system
    
    Args:
        request: QueryRequest with question and n_results
        
    Returns:
        QueryResponse with question, answer, sources and num_chunks
        
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
        reply = rag_engine.query_rag_system(
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

@app.post("/upload",
        response_model=UploadResponse,
        summary="Upload PDF endpoint",
        description="Accepts a PDF file, Returns an Upload response"
)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a PDF document
    
    Args:
        file: PDF file upload
        
    Returns:
        UploadResponse with filename, num_chunks and status
        
    """

    logger.info(f"Received file: {file.filename}")

    if not collection:
        raise HTTPException(status_code=500, detail="Database not initialised")
    
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    content = await file.read()

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="File is empty")
    
    logger.info(f"Processing {file.filename} ({len(content)} bytes)")
    
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete= False, suffix=".pdf") as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name

        logger.info(f"Saved to temp file: {temp_path}")

        num_chunks = document_processor.process_and_store_pdf(
            pdf_path= temp_path,
            collection= collection,
            )
        
        logger.info(f"Processed {file.filename} : {num_chunks} chunks")

        return UploadResponse(
            filename = file.filename,
            num_chunks= num_chunks,
            status= "success"
        )
        
    except Exception as e:
        logger.error(f"Upload Failed: {e}")
        raise HTTPException(status_code=500, detail= f"Processing failed: {e}")

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
            logger.info("Cleaned up temp file")    





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


