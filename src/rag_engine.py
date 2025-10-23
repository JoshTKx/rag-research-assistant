"""
RAG Query Pipeline
Combines retrieval from ChromaDB with Gemini generation
"""

import os
import logging
from typing import Dict, List, Any
from dotenv import load_dotenv
from google import genai
from google.genai import types
import chromadb



# Load environment
load_dotenv()


# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)



def query_rag_system(
        question: str,
        collection: chromadb.Collection,
        n_results: int = 3) -> Dict[str, Any]:
    """
    Complete RAG pipeline: Question -> Retrieve -> Generate -> Answer

    Args:
        question: User's question
        collection: ChromaDB collection with documents
        n_results: Num of chunks to retrieve

    Returns:
        dict:{
            'answer': Generated answer from LLM,
            'sources': List of sources used (with page numbers),
            'context_chunks': Chunks retrieved
        }

    Raises:
        Exception: If query or generation fails
    """

    try:
        logger.info(f"Retrieving chunks for {question}")
        results = collection.query(
            query_texts = [question],
            n_results = n_results
        )
        logger.info(f"Retrieved {len(results['ids'][0])} chunks")

        # Filter chunks by distance threshold
        filtered_docs = []
        filtered_metadatas = []
        DISTANCE_THRESHOLD = 1.2


        for doc, meta, dist in zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ):
            if dist < DISTANCE_THRESHOLD:
                filtered_docs.append(doc)
                filtered_metadatas.append(meta)

        # Return early if no relevant chunks
        if not filtered_docs:
            logger.warning(f"No chunks met distance threshold ({DISTANCE_THRESHOLD})")
            return {
                'answer': "I don't have relevant information in my knowledge base.",
                'sources': [],
                'context_chunks': []
            }



        # Format context from filtered chunks
        context = format_context(filtered_docs, filtered_metadatas)    
    
        # Build prompt
        sys_instruct = "Only use provided context to answer the given question"
        prompt = f""" Using only the following context, answer the question.

        Context:
        {context}

        Question:
        {question}

        Answer based ONLY on the context above. If the answer is not in the context, reply with "I don't have enough information to answer this question."


        Answer:"""

        # Call Gemini
        client = genai.Client()
        model = "gemini-2.5-flash"

        logger.info(f"Calling Gemini for generation")
        response = client.models.generate_content(
            model= model,
            contents = prompt,
            config=types.GenerateContentConfig(
                system_instruction=sys_instruct,
            )
        )


        # Return complete response
        return {
            'answer' : response.text,
            'context_chunks' : filtered_docs,
            'sources' : extract_sources(filtered_metadatas)
        }
    
    except Exception as e:
        logger.error(f"Failed to query: {e}")
        return {
            'answer' : "An error occured while processing your question.",
            'sources' : [],
            'context_chunks' : []
        }


def format_context(documents:List[str], metadatas:List[dict]) -> str:
    """
    Format retrieved chunks into context string
    
    Args:
        documents: List of document texts from ChromaDB
        metadatas: List of metadata dicts
        
    Returns:
        str: Formatted context string with source citations
        
    """
    try:
        context = []

        for document, metadata in zip(documents, metadatas):
            source = metadata.get('source', 'Unknown')
            page = metadata.get('page_num', '?')
            context.append(
                f"Source: {source}, Page {page}\n{document}\n\n"
            )

        context_str = "".join(context)
        logger.info(f"Formatted context ({len(context_str)} chars)")
        return context_str
    
    except Exception as e:
        logger.error(f"Failed to format context: {e}")
        return ""

def extract_sources(metadatas: List[dict]) -> List[str]:
    """
    Extract unique sources for citation
    
    Args:
        metadatas: List of metadata dicts
        
    Returns:
        list: Unique source strings like "test.pdf (Page 5)"

    """

    # Sort by page number
    sorted_metas = sorted(metadatas, key= lambda x: x["page_num"])

    # Remove duplicates while preserving order
    seen = set()
    unique_sources =[]

    for meta in sorted_metas:
        source = meta.get('source', 'Unknown')
        page = meta.get('page_num', '?')
        formatted = f"{source} (Page {page})"

        if formatted not in seen:
            seen.add(formatted)
            unique_sources.append(formatted)
    
    return unique_sources




if __name__ == "__main__":
    """Test the RAG system with sample questions"""
    from src import document_processor

    print("\n" + "="*60)
    print("RAG SYSTEM TEST")
    print("="*60)

    # Setup test environment
    pdf_path = "test_document.pdf"
    client = chromadb.Client()
    collection = client.create_collection(name= "ml_documents")

    # Process PDF
    num_stored = document_processor.process_and_store_pdf(pdf_path, collection)

    # Test questions
    test_questions = [
        "What is Total Defence?",
        "What are Singapore's defence strategies?",
        "Tell me about 4th Industrial Revolution"
    ]
    
    for question in test_questions:
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print(f"{'='*60}")
        
        reply = query_rag_system(
            question= question,
            collection= collection
        )

        print(f"Source: {reply['sources']}")
        print(f"Answer: {reply['answer']}")

