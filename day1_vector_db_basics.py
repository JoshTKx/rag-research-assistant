
import chromadb
import uuid

# TODO: Your task is to:
# 1. Create a ChromaDB client
# 2. Create a collection called "test_sentences"
# 3. Add these 5 sentences:
sentences = [
    "The cat sat on the mat",
    "Python is a programming language",
    "Machine learning uses neural networks",
    "The dog played in the park",
    "JavaScript runs in web browsers"
]

# 4. Query: "Tell me about animals" 
# 5. Query: "Tell me about programming"
# 6. Print the results and see if it returns relevant sentences

# START CODING HERE (use ChromaDB docs only):

chroma_client = chromadb.Client()

collection = chroma_client.create_collection(name = 'test_sentences')

collection.add(
    ids = ['id1','id2','id3','id4','id5'],
    documents = sentences
)

result = collection.query(
    query_texts = ["Tell me about animals", "Tell me about programming"],
    n_results = 1
)
print(result)

result_all = collection.query(
    query_texts=["Tell me about animals"],
    n_results=5  # Get all 5 sentences
)

weird_result = collection.query(
    query_texts=["Tell me about pizza"],
    n_results=1
)


def add_documents(collection, docs):
    """Add multiple documents with auto-generated IDs"""
    collection.add(
        ids = str(uuid.uuid4() for _ in docs),
        documents = docs
    )

def search_with_threshold(collection, query, threshold=1.0):
    """Return only results below distance threshold"""
    result = collection.query(
        query_texts = query,
        n_results = 2
    )
    return [
        doc 
        for doc, dist in zip(result['documents'], result['distances'])
        if dist <= threshold
    ]
    
    

# print(f"\n'Pizza' query returned: {weird_result['documents'][0]}")
# print(f"Distance: {weird_result['distances'][0]}")
# multi_result = collection.query(
#     query_texts=["Tell me about animals"],
#     n_results=3
# )

# print("\nTop 3 results for animals:")
# for doc, dist in zip(multi_result['documents'][0], multi_result['distances'][0]):
#     print(f"  {dist:.3f}: {doc}")

# Recreate collection with metadata
# collection = chroma_client.create_collection(name="test_with_metadata")
# collection.add(
#     ids=['id1','id2','id3','id4','id5'],
#     documents=sentences,
#     metadatas=[
#         {"category": "animals"},
#         {"category": "programming"},
#         {"category": "tech"},
#         {"category": "animals"},
#         {"category": "programming"}
#     ]
# )

# # Query and filter by metadata
# filtered_result = collection.query(
#     query_texts=["coding languages"],
#     n_results=2,
#     where={"category": "programming"}  # Only search programming docs
# )
# print(f"\nFiltered results: {filtered_result['documents']}")

# print("\nAll results for 'Tell me about animals':")
# for i, (doc, dist) in enumerate(zip(result_all['documents'][0], result_all['distances'][0])):
#     print(f"{i+1}. Distance: {dist:.3f} - '{doc}'")

# Test different query phrasings
# queries = [
#     "Tell me about animals",           # Information request
#     "animals",                          # Just the topic
#     "The cat",                          # Specific animal
#     "describe an animal",               # Descriptive request
# ]

# print("\n" + "="*60)
# print("Testing Different Query Phrasings")
# print("="*60)

# for query in queries:
#     result = collection.query(
#         query_texts=[query],
#         n_results=2
#     )
#     print(f"\nQuery: '{query}'")
#     print(f"  Top match: '{result['documents'][0][0]}' (dist: {result['distances'][0][0]:.3f})")
#     print(f"  2nd match: '{result['documents'][0][1]}' (dist: {result['distances'][0][1]:.3f})")

# more_sentences = [
#     "The cat sat on the mat",                    # Static
#     "Cats are small furry animals",              # Informative
#     "I saw a cat yesterday",                     # Narrative
#     "Tell me about cats",                        # Question
# ]

# collection2 = chroma_client.create_collection(name="test_styles")
# collection2.add(
#     ids=[f'id{i}' for i in range(len(more_sentences))],
#     documents=more_sentences
# )

# result = collection2.query(
#     query_texts=["Tell me about animals"],
#     n_results=4
# )

# print("\n" + "="*60)
# print("Testing Sentence Styles")
# print("="*60)
# for doc, dist in zip(result['documents'][0], result['distances'][0]):
#     print(f"{dist:.3f}: {doc}")