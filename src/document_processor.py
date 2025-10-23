"""
Document Processing Module

Handles PDF text extraction, intelligent chunking, and storage 
in vector database for RAG systems.
"""

import logging
import os
import hashlib
from typing import List, Dict, Any

from pypdf import PdfReader
import chromadb


# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)



def chunk_text_simple(text: str, chunk_size: int=500, overlap: int=50) -> List[str]:
    """
    Split text into chunks with overlap
    
    Args:
        text: Text to chunk
        chunk_size: Target size for each chunk (in characters)
        overlap: Number of characters to overlap between chunks
        
    Returns:
        list: List of text chunks
        
    """
    if not text or not text.strip():
        return []
    
    chunks = []
    start  = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        # Don't split words - find last space
        if end < len(text):
            last_space = chunk.rfind(" ")
            if last_space != -1:
                chunk = chunk[:last_space]
                end = start + last_space

        chunks.append(chunk.strip())
        start = end - overlap

        # Adjust start to word boundary
        if start > 0 and start < len(text):
            space_pos = text.find(" ", start)
            if space_pos != -1 and space_pos < start + overlap:
                start = space_pos + 1
        
    return chunks
        


def chunk_by_paragraphs(text: str) -> List[str]:
    """
    Split text by paragraphs (double newlines)

    Preserves semantic meaning better than fixed-size chunking.
    
    Args:
        text: Text to split
        
    Returns:
        list: List of paragraphs
        
    """
    if not text or not text.strip():
        return []
    
    paragraphs = text.split("\n\n")
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    return paragraphs




def extract_text_from_pdf(pdf_path :str) -> Dict[str, Any]:
    """
    Extract text from PDF file
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        dict: {
            'text': full text from all pages combined,
            'pages': list of text from each page,
            'num_pages': number of pages,
            'metadata': PDF metadata (title, author, etc.)
        }

    Raises:
        FileNotFoundError: If PDF file doesn't exist
        Exception: If PDF extraction fails
    """
    try:
        logger.info(f"Reading text from {pdf_path}")
        reader = PdfReader(stream= pdf_path)

        pages = []
        for page in reader.pages:
            text = page.extract_text() 
            pages.append(text if text else "")

        info = {
            "num_pages": len(reader.pages),
            "metadata": reader.metadata,
            "pages": pages,
            "text": "\n\n".join(pages)
        }

        logger.info(f"Successfully extracted {len(pages)} pages")
        return info
        
    
    except FileNotFoundError:
        logger.error(f"File not Found: {pdf_path}")
        return {}
    except Exception as e:
        logger.error(f"Failed to extract text: {e}")
        return {}


def chunk_pdf_by_pages(pdf_path: str,
                    chunk_size: int=500,
                    overlap: int=50,
                    strategy: str = "paragraph"
) -> List[Dict[str, Any]]:
    """
    Extract and chunk PDF, tracking which page each chunk came from
    
    Args:
        pdf_path: Path to PDF file
        chunk_size: Size of chunks (only used if strategy='fixed')
        overlap: Overlap between chunks (only used if strategy='fixed')
        strategy: Chunking strategy - 'paragraph' or 'fixed'
        
    Returns:
        list: List of dicts with 'text', 'page_num', 'chunk_id', 'source'
    """

    source  = os.path.basename(pdf_path)
    pdf_data = extract_text_from_pdf(pdf_path)

    if not pdf_data:
        logger.error(f"PDF extraction failed")
        return []
    
    pdf_info = []
    for pg_num, page in enumerate(pdf_data["pages"], start= 1):

        # Choose chunking strategy
        if strategy == "paragraph":
            page_chunks = chunk_by_paragraphs(page)
        else:
            page_chunks = chunk_text_simple(page, chunk_size, overlap)

        # Add metadata to each chunk
        for chunk_id, chunk in enumerate(page_chunks):
            chunk_info = {
                "text" : chunk,
                "page_num": pg_num,
                "chunk_id" :  f"page{pg_num}_chunk{chunk_id}",
                "source" : source
            }
            pdf_info.append(chunk_info)

    logger.info(f"Created {len(pdf_info)} chunks from {pdf_data['num_pages']} pages")
    return pdf_info


def process_and_store_pdf(
        pdf_path: str,
        collection: chromadb.Collection, 
        chunk_size: int=500, 
        overlap: int=100,
        strategy: str = "paragraph"
) -> int:
    """
    Complete pipeline: PDF → Chunks → ChromaDB
    
    Args:
        pdf_path: Path to PDF file
        collection: ChromaDB collection to store chunks
        chunk_size: Chunk size (only for fixed strategy)
        overlap: Overlap size (only for fixed strategy)
        strategy: 'paragraph' (semantic) or 'fixed' (size-based)
        
    Returns:
        int: Number of chunks stored
        
    Raises:
        Exception: If storage fails
    """
    logger.info(f"Processing PDF: {pdf_path}")

    # Extract and chunk
    chunks = chunk_pdf_by_pages(pdf_path, chunk_size, overlap, strategy)

    if not chunks:
        logging.warning("No chunks to store")
        return 0

    # Prepare data for ChromaDB
    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:
        #Generate deterministic ID
        unique_string = f"{chunk['source']}-{chunk['page_num']}-{chunk['text'][:50]}"
        doc_id = hashlib.sha256(unique_string.encode()).hexdigest()

        ids.append(doc_id)
        documents.append(chunk["text"])

        # Store metadata
        meta = {
            "page_num": chunk["page_num"],
            "chunk_id" : chunk["chunk_id"],
            "source" : chunk["source"]
        }
        metadatas.append(meta)
        
    # Store in ChromaDB
    try:
        collection.upsert(
            ids = ids,
            documents = documents,
            metadatas = metadatas
        )
        logger.info(f"Successfully stored {len(chunks)} chunks")
        return len(chunks)

    except Exception as e:
        logger.error(f"Failed to store chunks: {e}")
        return 0



# Test PDF functions

if __name__ == "__main__":
    """Test document processing pipeline"""
    
    pdf_path = "test_document.pdf"
    
    print("\n" + "="*60)
    print("PDF EXTRACTION TEST")
    print("="*60)
    
    pdf_data = extract_text_from_pdf(pdf_path)
    
    if pdf_data:
        print(f"\nPDF Statistics:")
        print(f"  Pages: {pdf_data['num_pages']}")
        print(f"  Total characters: {len(pdf_data['text'])}")
        print(f"  Metadata: {pdf_data['metadata']}")
        print(f"\n  First page preview (200 chars):")
        print(f"  {pdf_data['pages'][0][:200]}...")
    else:
        print("Failed to extract PDF")
    
    print("\n" + "="*60)
    print("CHUNKING COMPARISON")
    print("="*60)
    
    # Test both strategies
    para_chunks = chunk_pdf_by_pages(pdf_path, strategy="paragraph")
    fixed_chunks = chunk_pdf_by_pages(pdf_path, strategy="fixed", chunk_size=500)
    
    print(f"\nParagraph chunking: {len(para_chunks)} chunks")
    print(f"Fixed-size chunking: {len(fixed_chunks)} chunks")
    
    print("\n" + "="*60)
    print("STORAGE & RETRIEVAL TEST")
    print("="*60)
    
    # Create ChromaDB
    client = chromadb.Client()
    collection = client.create_collection(name="ml_documents")
    
    # Store with paragraph chunking (recommended)
    num_stored = process_and_store_pdf(
        pdf_path, 
        collection, 
        strategy="paragraph"
    )
    print(f"\nStored {num_stored} chunks in database")
    
    # Test retrieval
    test_queries = [
        "What is Total Defence?",
        "Singapore's defence strategy"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = collection.query(
            query_texts=[query],
            n_results=1
        )
        
        dist = results['distances'][0][0]
        meta = results['metadatas'][0][0]
        
        status = "Good" if dist < 1.0 else "Weak"
        print(f"  {status} match (distance: {dist:.3f})")
        print(f"  Source: {meta['source']} | Page {meta['page_num']}")