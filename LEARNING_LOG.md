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


## Evening Deep Dive: How Embeddings Actually Work

### Default Embedding Model:
It uses all-MiniLM-L6-v2, a MiniLm from the sentence-transformers library(Is this connected to huggingface), used for semantic search tasks

### How Text Becomes Vectors:
First we break apart the text into small sections known as tokens, these tokens are fed to the embedding model to use, from there the embedding model will first generate a generic vector for each token based on its standard meaning, then the transformer, uses attention to generate a more context specific vector by looking at the surrounding tokens. From all the context specific vectors, the model generates a overall representation, normally via a mean of all the vectors, in a process called pooling, and this vector then represents the text

### Vector Dimensions:
The vectors that the embedding model uses has 384 dimensions, and the vectors basically represents the level of complexity that can be represented. So a vector that has higher dimensions can represent the text in greater detail and differentiate between different text more clearly, capturing more varience, however this can lead to a larger space to search, increasing the time taken to search for semantic pairs

### Why Similar = Close:
Similar text would have tokens with similar contextual meaning, so their vectors would be more similar , resulting in a similar vector

### New vocabulary I learned:
- Pooling
- Transformers
- attention mechanism


## Understanding Distance Metrics

### Distance metric used:
It uses Cosine distance, which is a conversion of the cosine similarity to a distance format, where a lower value indicates 2 vectors are closer and the text or tokens are more similar

### How it's calculated:
Its calculated from 1 - Cosine similarity, which is calculated by the cosine of the angle between the document and query vectors

### Why my distances are in the 0-2 range:
Cosine similarity ranges from 1 to -1, so 1 - cosine similarity would range from 0 to 2

### Production thresholds:
You would have to adjust it like a hyper parameter, and the right value would vary based on the database u have.
But a good baseline would be:
0-0.3 Good Match
0.3-0.6 Relevant Match
0.6-1.0 Loose Match
/>1.0 dissimilar 


## Code Improvements from AI Review

### What I changed:
1. Added error handling and logging - Why: More robust and better for debugging
2. Changed to using a hashfuntion to get a deterministic value instead of uuid- Why: Prevents overlaps in hash values
3. Added metadata recording and filtering - Why: More functionality

### What I learned about production code:
-Logging and proper error handling is important
-Good descriptors and comments are crucial

### Things I'll consider for Week 2:
- Add for descriptions and comments
-

## Week 2 Preparation: RAG Design Decisions

### Chunking Strategy:
Splitting the tokens into chunks that are complete but small. Use recursive chunking to split progressively, eg. paragraph -> new line -> sentence -> spaces. Also Good to do chunk overlap, so each subsequent chunk consists of about 20% of the previous chunk as well, so information is complete

### Metadata to Track:
source, page number, chunk id

### Citation Approach:
this can be taken from the metadata

### Pitfalls to Avoid:
1. Using fixed sized chunking
2. Retrieving too many chunks at once, middle usually gets lost, start small, eg 5
3. Query, statement mismatch, convert query to statement before performing semantic search

### Questions I still have:
- 
-