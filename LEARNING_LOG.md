# RAG Research Assistant - Learning Log

## Day 1: Embeddings & Vector Databases

### What are embeddings?
embeddings are a way to represent data, whether text or images or eventually video and audio. I believe these embeddings are stored in the form of vectors, where vectors located nearer to ear other, are more similar

### What is a vector database?
Its a database to store all my embeddings are compare similarity btw text and images

### Why do I need ChromaDB for RAG?
the database serves as the memory for your agent, where your agent can refer to to retrieve certain information, such as policy details for example or in our case, the selected pdf documents

### Key vocabulary:
- Embedding: Converting text or images to vectors
- Vector: A representation of the saved information
- Similarity search: Find embedding similar or with alm the same traits and return them
- Semantic search: A form of similarity but based on meaning and intent rather than actual word

---

## Notes & Questions
whats the difference btw, smt like vectordb vs chromadb, isit just implementation?