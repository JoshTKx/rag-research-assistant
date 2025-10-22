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

# Day 2: Document Processing & Chunking

## Morning Research: PDF Processing

### Why PDF extraction is tricky:
Could be a image of the page, instead of the actual content info. PDF stores layout instructions instead of the actual text. Its storing information to output the text, like drawing individual characters at a certain coordinate instead of containing the text info. Sometimes its also in a diff format, instead of something more standard like unicode. Hard to differentiate btw different sections like footnotes and headers or hyperlinks and metadata. So it becomes guesswork instead of actually knowing

### What pypdf can do:
Extract information aboutt fonts, encoding, character distances and similar topics. It wont confuse similar characters which OCR might, and can read rare characters.(Does this mean pypdf is only able to read texts from a pdf, not tables or images? If so how does it manage to, or even just overcome the challenges of text extraction from pdfs)

### What pypdf CANNOT do well:
Cant extract text from images, as its not OCR software

### Key pypdf methods I'll need:
- PdfReader: Object used to read the pdf, takes in the file object, a option to warn user of all problems and a password(I assume only for encrypted files). Can be used to convert the file to a list of PageObjects, which we can perform further actions on. Basically a collection of all the pages.
- extract_text():locates all text drawing commands to extract the text within the page(Whats the diff from get_contents())
- 

## Day 2 Morning: PDF Extraction Deep Dive

### How pypdf Overcomes PDF Challenges:

1. **Coordinate-based text → Readable text**
   - Reads character drawing commands
   - Orders by position (top→bottom, left→right)
   - Reconstructs sentences by detecting spacing

2. **Different encodings → Unicode**
   - Built-in encoding tables
   - Maps PDF character codes to standard Unicode
   - Handles most common formats automatically

3. **Limitations it CANNOT overcome:**
   - Multi-column layouts (might scramble order)
   - Tables (extracts as unstructured text)
   - Images with text (needs OCR)
   - Complex layouts (textbooks, magazines)

### Methods Clarified:

**PdfReader**
- Creates object to read PDF file
- Converts PDF into list of PageObjects
- Usage: `reader = PdfReader("file.pdf")`

**extract_text()** ✅ Use this!
- Returns human-readable text
- Handles encoding and spacing
- Perfect for RAG systems

**get_contents()** ❌ Avoid unless debugging
- Returns raw PDF commands
- Not human-readable
- For advanced PDF manipulation only

### For My RAG System:
- pypdf text extraction is sufficient
- Tables will be unstructured (but LLMs can still understand!)
- Multi-column papers might have weird ordering (test and see)
- If I need OCR later, I'd add Tesseract/pytesseract


## Chunking Strategy Analysis

### Simple Fixed-Size (500 chars, 50 overlap):
**Pros:**
- Predictable chunk sizes
- Good for consistent embedding dimensions
- Ensures coverage with overlap

**Cons:**
- Might split mid-thought
- Example: "ty reduction" at start of chunk 3
- Less semantic coherence

### Paragraph-Based:
**Pros:**
- Semantically complete thoughts
- Example: Each ML type is in its own chunk
- Better for question answering (complete context)

**Cons:**
- Varying sizes (32 to 230 chars)
- Small chunks might lack context
- Large paragraphs might exceed ideal size

### My Conclusion:
For RAG, paragraph chunking seems better because:
- It captures the semantic meaning of each chunk
- Paragraph is better, can gradually finetune size, from para to new line to sentence to words


## Day 2 Complete ✅

### What I Built:
- Complete document processing pipeline
- PDF extraction with pypdf (22 pages, 249 chunks)
- Metadata tracking (source, page, chunk_id)
- Full integration with ChromaDB
- Working retrieval with citations

### Key Discoveries:

1. **Paragraph chunking > Fixed chunking**
   - Preserves semantic meaning
   - Better for RAG responses

2. **Distance scores indicate relevance**
   - High distances (>1.2) = document doesn't contain relevant info
   - This is GOOD - system correctly identifies poor matches
   - With relevant queries, distances would be lower

3. **Real PDFs are messy**
   - Academic papers have headers, footers, formatting
   - pypdf does its best but text isn't perfect
   - Chunking strategy helps smooth this out

### Production Insights:
- Always check distances to validate retrieval quality
- Need query-document matching for good results
- Metadata is essential for citations
- Deterministic IDs prevent duplicates

### Challenges Faced:
- Understanding dict structure from extract_text_from_pdf()
- Looping over the right data structure
- Realized queries need to match document content

### Ready for Day 3: Building the Q&A System! ✅


## Day 3: RAG Architecture (Corrected Understanding)

### The RAG Flow (corrected):
1. User asks a question
2. **Vector DB (ChromaDB)** searches for relevant chunks
3. Retrieved chunks become "context"
4. Build prompt: "Use this context: [chunks] to answer: [question]"
5. **LLM (Gemini)** generates answer based on context
6. Return answer with source citations

**Key insight:** LLM and database are SEPARATE. LLM has no memory - we give it context in every prompt.

### Why we need RAG:
1. **Knowledge cutoff**: LLMs don't know about recent/private documents
2. **Hallucinations**: LLMs make things up; RAG provides real sources
3. **Verifiability**: Users can check sources (page numbers)
4. **Private data**: Company docs, research papers not in training data

Example: My Singapore defence PDF (2024) isn't in Gemini's training data!

### Key prompt engineering principles for RAG:
1. **Be explicit**: "Answer ONLY using the provided context"
2. **Handle unknowns**: "If context doesn't contain answer, say 'I don't know'"
3. **Request citations**: "Cite the source for your answer"
4. **Clear structure**: Separate context from question clearly

### Gemini vs ChatGPT APIs:

**Gemini (what I'm using):**
```python
model = genai.GenerativeModel(
    'gemini-1.5-flash',
    system_instruction="Instructions here"
)
response = model.generate_content("User question")
```

**ChatGPT (for later):**
```python
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "Instructions"},
        {"role": "user", "content": "Question"}
    ]
)
```

### Questions resolved:
- ✅ Understood: LLM and DB are separate components
- ✅ Understood: Basic RAG is one-pass, not a loop
- ✅ Understood: We control what LLM sees via the prompt


## Day 3: RAG Query Pipeline Complete ✅

### What I Built:
- Complete RAG pipeline: Retrieve → Format → Generate
- Integrated Gemini 2.5 Flash for answer generation
- Source citation with page numbers
- Proper error handling and logging

### Test Results Analysis:

**Question 1: "What is Total Defence?"**
- Retrieved 3 chunks (Pages 17, 18, 3)
- Generated comprehensive answer ✅
- Used multiple sources correctly ✅

**Question 2: "What are Singapore's defence strategies?"**
- Retrieved 1 primary source (Page 3)
- Direct, accurate answer ✅

**Question 3: "Tell me about 4th Industrial Revolution"**
- Retrieved chunks with high distances (>1.4)
- LLM correctly said "not enough information" ✅
- **This proves the system doesn't hallucinate!**

### Key Insights:

1. **Distance matters**: High distances (>1.2) = weak matches
2. **Prompt engineering works**: Explicit instructions prevent hallucinations
3. **Source attribution**: Users can verify answers by checking pages
4. **Graceful degradation**: System admits when it doesn't know

### Code Quality:
- Clean separation of concerns (retrieve, format, generate)
- Good error handling with try/except
- Comprehensive logging for debugging
- Helper functions for formatting

### What Could Be Improved:
- Add distance threshold filtering
- Sort sources by page number
- Could add chunk selection logic (pick best chunks, not just top 3)


## Day 3 Afternoon: FastAPI Wrapper

### What is FastAPI?
A way to build frameworks to allow different software applications to interact with one another

### Key Concepts:
- Route/Endpoint: It is a location on your system that the api can monitor, where data can be stored and retrievd
- Path Operation: 
    GET: retrieves info from the endpoint
    POST: Stores information at that endpoint
    DELETE: Remove information from the endpoint
- Request Body: A Json which is structured like a python dictionary
- Response Model: not too sure

### Why FastAPI for this project?
- Not too sure


## Day 3 Afternoon: FastAPI Wrapper

### What is FastAPI?
A modern Python web framework for building APIs. It allows me to create HTTP 
endpoints that other applications can call to use my RAG system. Like building 
a restaurant menu - I define what requests I accept (endpoints) and what I 
serve back (responses).

### Key Concepts:

**Endpoint/Route:**
- A URL path where the API listens (e.g., /query, /upload)
- NOT where data is stored - just an address for operations
- Example: POST /query means "send questions to this address"

**HTTP Methods (Path Operations):**
- GET: Retrieve/read data (list documents, health check)
- POST: Create/process data (upload file, ask question)
- DELETE: Remove data (delete document)
- PUT/PATCH: Update data (less common in our RAG system)

**Request Body:**
- JSON data sent by the client
- FastAPI auto-converts to Python objects
- Example: {"question": "What is AI?", "n_results": 3}

**Response Model:**
- Pydantic model defining structure of what API returns
- Provides automatic validation and documentation
- Example: QueryResponse(answer="...", sources=["..."])

### Why FastAPI for RAG project?
1. **Fast development**: Auto-docs, less boilerplate
2. **Production-ready**: Built-in validation, async support
3. **Perfect for AI**: Easy file uploads, JSON handling
4. **Industry standard**: Used by major tech companies
5. **Makes me employable**: Shows modern Python skills

### API Architecture:
```
Client (Browser/App)
    ↓ HTTP Request
FastAPI Server (my code)
    ↓ Calls
RAG System (my functions)
    ↓ Queries
ChromaDB (vector database)
    ↓ Returns chunks
Back through chain → JSON response
```

### My API Endpoints:
- GET /health → Check if API is running
- POST /query → Ask questions (main feature!)
- POST /upload → Upload PDF documents
- GET /documents → List all documents
- DELETE /document/{name} → Remove document


# Day 4: Docker Containerization & Deployment

## Day 4: Docker Fundamentals (Corrected)

### What is Docker?
Docker is a containerization platform that packages applications with ALL 
their dependencies (code, libraries, system tools) into isolated containers. 
Unlike virtual environments (which only isolate Python packages), containers 
isolate the entire application stack including OS libraries.

### Why containerization matters:
1. **Consistency**: Eliminates "works on my machine" - same environment everywhere
2. **Portability**: Runs identically on any system with Docker (dev → cloud)
3. **Isolation**: Multiple apps can run on same server without conflicts
4. **Reproducibility**: Anyone can replicate exact environment with one command
5. **Deployment simplicity**: Package once, deploy anywhere

### Key concepts:
- **Image**: Snapshot/template containing app + dependencies (like a recipe)
- **Container**: Running instance of an image (like a dish made from recipe)
- **Dockerfile**: Text file with instructions to build an image
- **Docker Compose**: Tool to run multiple containers together (e.g., API + database)

### Container vs Virtual Machine:
**VM**: Simulates entire computer (OS, kernel, everything) - Heavy, slow to start
**Container**: Shares host OS kernel, only packages app + libraries - Light, fast

Containers are isolated sandboxes that:
- Share the host OS kernel (efficient!)
- Only include necessary libraries
- Expose only specific ports for networking
- Start in seconds vs minutes for VMs

### Container vs Virtual Environment:
**venv**: Only isolates Python packages, still uses host OS/libraries
**Container**: Isolates entire stack - Python version, system libs, everything

### For my RAG project:
Docker will package into one portable image:
- Specific Python version (3.11)
- FastAPI + all dependencies
- ChromaDB with data persistence
- My application code
- System libraries pypdf needs

Then I can deploy this exact environment anywhere:
- My teammate's laptop
- Google Cloud Run
- AWS
- Anywhere with Docker!