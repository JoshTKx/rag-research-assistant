"""
RAG Query Pipeline
Combines retrieval from ChromaDB with Gemini generation
"""

import os
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types
import chromadb

import day2_document_processing

#Load environment
load_dotenv()


# Setup logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s -%(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def query_rag_system(question, collection, n_results =3):
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
    """

    try:
        logger.info(f"Retrieving chunks for {question}")
        results = collection.query(
            query_texts = [question],
            n_results = n_results
        )
        logger.info(f"Retrieved {len(results["ids"][0])} chunks")

        relevant_chunks = []

        for doc, meta, dist in zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ):
            if dist < 1.2:
                relevant_chunks.append((doc,meta))

        if not relevant_chunks:
            return {
                'answer': "I don't have relevant information in my knowledge base.",
                'sources': [],
                'context_chunks': []
            }




        context = format_context(results["documents"][0], results["metadatas"][0])    
        sys_instruct = "Only use provided context to answer the given question"

        prompt = f""" Using only the following context, answer the question.

        Context:
        {context}

        Question:
        {question}

        Answer based ONLY on the context above. If the answer is not in the context, reply with "I don't have enough information to answer this question."


        Answer:"""

        reply = {
            'context_chunks' : results["documents"][0],
            'sources' : extract_sources(results["metadatas"][0])
        }

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

        reply["answer"] = response.text
        return reply
    
    except Exception as e:
        logger.error(f"Failed to query: {e}")
        return {}


def format_context(documents, metadatas):
    """
    Helper function: Format retrieved chunks into context string
    
    Args:
        documents: List of document texts from ChromaDB
        metadatas: List of metadata dicts
        
    Returns:
        str: Formatted context string
        
    """
    try:
        context = []

        for document, metadata in zip(documents, metadatas):
            page_context = f"Source: {metadata["source"]}, Page {metadata["page_num"]} \n {document} \n\n"
            context.append(page_context)

        context_str = "".join(context)
        
        logger.info(f"Formatted context ({len(context_str)} chars)")
        return context_str
    
    except Exception as e:
        logger.error(f"Failed to format context: {e}")
        return ""

def extract_sources(metadatas):
    """
    Helper function: Extract unique sources for citation
    
    Args:
        metadatas: List of metadata dicts
        
    Returns:
        list: List of source strings like "test.pdf (Page 5)"

    """

    sources = sorted(metadatas, key= lambda x: x["page_num"])

    
    seen = set()
    unique =[]

    for s in sources:
        formatted = f"{s["source"]} (Page {s["page_num"]})"
        if formatted in seen:
            continue
        seen.add(formatted)
        unique.append(formatted)
    
    return unique




if __name__ == "__main__":
    print("\n" + "="*60)
    print("RAG SYSTEM TEST")
    print("="*60)

    pdf_path = "test_document.pdf"
    
    # Load your collection from Day 2
    # TODO: Create ChromaDB client
    # TODO: Get the collection you created yesterday
    client = chromadb.Client()
    collection = client.create_collection(name= "ml_documents")

    num_stored = day2_document_processing.process_and_store_pdf(pdf_path, collection)

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
        
        # TODO: Call query_rag_system()
        # TODO: Print the answer
        # TODO: Print the sources used

        reply = query_rag_system(
            question= question,
            collection= collection
        )

        print(f"Answer: {reply["answer"]}")
        print(f"Source: {reply["sources"]}")
        
        # YOUR CODE HERE
