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
        
    TODO:
    - Split text into chunks of approximately chunk_size
    - Each chunk should overlap with previous by 'overlap' characters
    - Don't split in the middle of words
    - Handle edge cases (text shorter than chunk_size)
    
    Strategy:
    1. Start at position 0
    2. Move forward by (chunk_size - overlap) each time
    3. Extract chunk from current position to current + chunk_size
    4. Make sure you don't split words (find space boundaries)
    """
    # YOUR CODE HERE
    # Hint: Use a while loop and track your position in the text

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
        if space_pos != 1 and space_pos < start + overlap:
            start = space_pos + 1
        

    return chunks
        


def chunk_by_paragraphs(text):
    """
    Split text by paragraphs (double newlines)
    
    Args:
        text: Text to split
        
    Returns:
        list: List of paragraphs
        
    TODO:
    - Split on double newlines (\n\n)
    - Remove empty paragraphs
    - Strip whitespace from each paragraph
    """
    # YOUR CODE HERE
    paragraphs = text.split("\n\n")
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    return paragraphs

# Test chunking
if __name__ == "__main__":
    # ... previous code to load file and show stats ...
    file_path = "test_document.txt"
    
    # Load the file
    text = load_text_file(file_path)
    
    # Get statistics
    stats = get_text_stats(text)
    
    # Print results
    print(f"\nDocument Statistics:")
    print(f"Characters: {stats['characters']}")
    print(f"Words: {stats['words']}")
    print(f"Lines: {stats['lines']}")
    
    # Print first 200 characters
    print(f"\nFirst 200 characters:")
    print(text[:200])
    # Test simple chunking
    print("\n" + "="*60)
    print("SIMPLE CHUNKING (500 chars, 50 overlap)")
    print("="*60)
    
    # TODO: Call chunk_text_simple with text, chunk_size=500, overlap=50
    # TODO: Print total number of chunks
    # TODO: For each chunk, print:
    #       - Chunk number
    #       - Chunk length
    #       - First 100 characters (or full chunk if shorter)
    chunks = chunk_text_simple(text)
    print(f"Total Chunks: {len(chunks)}")
    for i,chunk in enumerate(chunks):
        print(f"Chunk Number: {i}\n")
        print(f"Chunk Length: {len(chunk)}\n")
        print(f"Chunk Snippet: {chunk[:100]}\n")


    
    # Test paragraph chunking
    print("\n" + "="*60)
    print("PARAGRAPH CHUNKING")
    print("="*60)
    
    # TODO: Call chunk_by_paragraphs
    # TODO: Print total number of paragraphs
    # TODO: For each paragraph, print:
    #       - Paragraph number
    #       - Paragraph length
    #       - First 100 characters
    paragraphs = chunk_by_paragraphs(text)
    for i,paragraph in enumerate(paragraphs):
        print(f"Para Number: {i}\n")
        print(f"Para Length: {len(paragraph)}\n")
        print(f"Para Snippet: {paragraph[:100]}\n")