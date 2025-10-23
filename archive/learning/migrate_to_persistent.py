import chromadb
import day2_document_processing
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_data():
    """Migrate data from in-memory to persistent storage"""

    logger.info("Creating persistent ChromaDB...")
    save_path = "./chroma_db"
    persistent_client = chromadb.PersistentClient(path= save_path)

    try:
        collection = persistent_client.create_collection(name="ml_documents")
        logger.info("Created persistent collection")
    
    except Exception as e:
        logger.warning(f"Collection might already exist: {e}")
        collection = persistent_client.get_collection(name= "ml_documents")

    pdf_path = "test_document.pdf"
    logger.info(f"Processing {pdf_path}...")

    num_chunks = day2_document_processing.process_and_store_pdf(
        pdf_path= pdf_path,
        collection= collection
    )

    logger.info(f"Migrated {num_chunks} chunks to persistent storage")
    logger.info(f"Data saved to {save_path}")

    return num_chunks

if __name__ == "__main__":
    migrate_data()    