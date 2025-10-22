# day2_document_processing.py

"""
Document Processing Module
Handles text extraction and chunking for RAG system
"""

import logging
import pypdf

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_text_file(file_path):
    """
    Load text from a simple text file
    
    Args:
        file_path: Path to the text file
        
    Returns:
        str: Extracted text
        
    TODO: 
    - Open and read the file
    - Handle potential errors (file not found, encoding issues)
    - Log what you're doing
    - Return the text
    """
    try: 
        logger.info(f"Loading text from: {file_path}")
        # reader  = pypdf.PdfReader(file_path)
        # res = ""
        # for page in reader.pages:
        #     res += page.extract_text()
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        logger.info(f"Successfullly loaded file")
        return text
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return ""

    except Exception as e:
        logger.error(f"Failed to load text file: {e}")
        return ""


def get_text_stats(text):
    """
    Get basic statistics about the text
    
    Args:
        text: The text to analyze
        
    Returns:
        dict: Statistics including character count, word count, line count
        
    TODO:
    - Count characters (len)
    - Count words (split by spaces)
    - Count lines (split by newlines)
    - Return as a dictionary
    """
    # YOUR CODE HERE
    if not text:
        return {
            "characters" : 0,
        "words" : 0,
        "lines" : 0
        }

    return {
        "characters" : len(text),
        "words" : len(text.split(" ")),
        "lines" : len(text.split("\n"))
    }

# Test your functions
    


#### **Expected Output:**

# 2024-10-20 10:30:15 - INFO - Loading text from: test_document.txt
# 2024-10-20 10:30:15 - INFO - Successfully loaded 1234 characters

# Document Statistics:
# Characters: 1234
# Words: 189
# Lines: 15

# First 200 characters:
# Introduction to Machine Learning

# Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed...


def chunk_text_simple(text, chunk_size=500, overlap=50):
    """
    Split text into chunks with overlap
    
    Args:
        text: Text to chunk
        chunk_size: Target size for each chunk (in characters)
        overlap: Number of characters to overlap between chunks
        
    Returns:
        list: List of text chunks
        
    """

    chunks = []
    start  = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if end < len(text):
            last_space = chunk.rfind(" ")
            if last_space != -1:
                chunk = chunk[:last_space]
                end = start + last_space

        chunks.append(chunk)
        start = end - overlap

        space_pos = text.find(" ", start)
        if space_pos != -1 and space_pos < start + overlap:
            start = space_pos + 1
        

    return chunks
        


def chunk_by_paragraphs(text):
    """
    Split text by paragraphs (double newlines)
    
    Args:
        text: Text to split
        
    Returns:
        list: List of paragraphs
        
    """
    # YOUR CODE HERE
    paragraphs = text.split("\n\n")
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    return paragraphs



from pypdf import PdfReader
import os

def extract_text_from_pdf(pdf_path):
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
    """
    try:
        logger.info(f"Reading text from {pdf_path}")
        reader = PdfReader(stream= pdf_path)

        pages = []

        for page in reader.pages:
            pages.append(page.extract_text())

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


def chunk_pdf_by_pages(pdf_path, chunk_size=500, overlap=50):
    """
    Extract and chunk PDF, tracking which page each chunk came from
    
    Args:
        pdf_path: Path to PDF
        chunk_size: Size of chunks
        overlap: Overlap between chunks
        
    Returns:
        list: List of dicts with 'text', 'page_num', 'chunk_id', 'source'
    """
    # YOUR CODE HERE
    source  = os.path.basename(pdf_path)
    pdf_data = extract_text_from_pdf(pdf_path)

    if not pdf_data:
        logger.error(f"PDF extraction failed")
        return []
    
    pdf_info = []
    for pg_num, page in enumerate(pdf_data["pages"], start= 1):
        paragraphs = chunk_text_simple(page, chunk_size, overlap)

        for chunk_id, chunk in enumerate(paragraphs):
            chunk_info = {
                "text" : chunk,
                "page_num": pg_num,
                "chunk_id" :  f"page{pg_num}_chunk{chunk_id}",
                "source" : source
            }
            pdf_info.append(chunk_info)

    logger.info(f"Created {len(pdf_info)} chunks from {pdf_data['num_pages']} pages")
    return pdf_info

import chromadb
import hashlib

def process_and_store_pdf(pdf_path, collection, chunk_size=500, overlap=100):
    """
    Complete pipeline: PDF → Chunks → ChromaDB
    
    Args:
        pdf_path: Path to PDF
        collection: ChromaDB collection
        chunk_size: Not used if using paragraph chunking
        overlap: Not used if using paragraph chunking
        
    Returns:
        int: Number of chunks stored
        
    TODO:
    - Get chunks using chunk_pdf_by_pages()
    - For each chunk:
        - Generate deterministic ID (hash of source + page + text)
        - Prepare for ChromaDB (lists of ids, documents, metadatas)
    - Store in ChromaDB using collection.upsert()
    - Return count
    
    Hints:
    - Create lists: ids = [], documents = [], metadatas = []
    - For each chunk, append to these lists
    - ID generation: hashlib.sha256(f"{source}-{page}-{text}".encode()).hexdigest()
    - Metadata should be dict without 'text' key
    - collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    """
    # YOUR CODE HERE
    chunks = chunk_pdf_by_pages(pdf_path, chunk_size, overlap)

    if not chunks:
        logging.warning("No chunks to store")
        return 0

    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:

        unique_string = f"{chunk['source']}-{chunk['page_num']}-{chunk['text'][:50]}"
        doc_id = hashlib.sha256(unique_string.encode()).hexdigest()

        ids.append(doc_id)
        meta = {
            "page_num": chunk["page_num"],
            "chunk_id" : chunk["chunk_id"],
            "source" : chunk["source"]
        }
        metadatas.append(meta)
        documents.append(chunk["text"])

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



# Test your PDF functions
if __name__ == "__main__":
    # ... previous tests ...
    
    pdf_path = "test_document.pdf"
    
    print("\n" + "="*60)
    print("PDF EXTRACTION TEST")
    print("="*60)
    
    pdf_data = extract_text_from_pdf(pdf_path)
    
    if pdf_data:
        print(f"\n✅ PDF Statistics:")
        print(f"  Pages: {pdf_data['num_pages']}")
        print(f"  Total characters: {len(pdf_data['text'])}")
        print(f"  Metadata: {pdf_data['metadata']}")
        print(f"\n  First page preview (200 chars):")
        print(f"  {pdf_data['pages'][0][:200]}...")
    else:
        print("❌ Failed to extract PDF")
    
    print("\n" + "="*60)
    print("PDF CHUNKING TEST")
    print("="*60)
    
    chunks = chunk_pdf_by_pages(pdf_path)
    
    print(f"\n✅ Total chunks: {len(chunks)}")
    print(f"\nFirst 3 chunks:")
    
    for chunk in chunks[:3]:
        print(f"\n  📄 {chunk['source']} | Page {chunk['page_num']} | {chunk['chunk_id']}")
        print(f"     Text ({len(chunk['text'])} chars): {chunk['text'][:100]}...")

    print("\n" + "="*60)
    print("COMPLETE PIPELINE: PDF → ChromaDB")
    print("="*60)
    
    # Create ChromaDB
    client = chromadb.Client()
    collection = client.create_collection(name="ml_documents")
    
    # Process and store
    num_stored = process_and_store_pdf(pdf_path, collection)
    print(f"\n✅ Stored {num_stored} chunks in database")
    
    # Test retrieval
    print("\n" + "="*60)
    print("RETRIEVAL TEST")
    print("="*60)
    
    queries = [
        "What is Total Defence?",
        "What is Singapore's defence strategy?",
        "Tell me about 4th Industrial Revolution in Singapore"
    ]
    
    for query in queries:
        print(f"\n🔍 Query: '{query}'")
        results = collection.query(
            query_texts=[query],
            n_results=2
        )
        
        for i, (doc, dist, meta) in enumerate(zip(
            results['documents'][0],
            results['distances'][0],
            results['metadatas'][0]
        ), 1):
            print(f"\n  Result {i} (distance: {dist:.3f}):")
            print(f"  📄 {meta['source']} | Page {meta['page_num']} | {meta['chunk_id']}")
            print(f"  📝 {doc[:150]}...")


    # Add this to your test section:
    print("\n" + "="*60)
    print("TESTING WITH RELEVANT QUERIES")
    print("="*60)

    relevant_queries = [
        "What is Total Defence?",
        "Singapore's defence strategy",
        "4th Industrial Revolution technologies"
    ]

    for query in relevant_queries:
        print(f"\n🔍 Query: '{query}'")
        results = collection.query(
            query_texts=[query],
            n_results=1
        )
        
        dist = results['distances'][0][0]
        doc = results['documents'][0][0]
        meta = results['metadatas'][0][0]
        
        print(f"  Distance: {dist:.3f} {'✅ Good match!' if dist < 1.0 else '⚠️ Loose match'}")
        print(f"  📄 {meta['source']} | Page {meta['page_num']}")
        print(f"  📝 {doc[:200]}...")