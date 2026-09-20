"""
=============================================================================
STEP 5: SEARCH SIMILAR CHUNKS
=============================================================================

WHAT IS THIS STEP?
    When a user asks a question, we convert it to an embedding and search
    the vector database for the most similar chunks. These are the most
    relevant pieces of information for answering the question.

WHY DO WE NEED THIS?
    - The user's question needs to be matched against our knowledge base
    - Vector similarity finds chunks that are semantically related
    - This is much better than keyword search because it understands meaning
    - For example: "forgot my password" matches "password reset procedure"

HOW DOES SIMILARITY SEARCH WORK?
    1. Convert the user's question to an embedding vector
    2. Compare this vector to ALL stored chunk vectors
    3. Calculate similarity score (cosine similarity)
    4. Return the top-N most similar chunks
    5. Higher score = more relevant

THE RAG PIPELINE (YOU ARE HERE: Step 5 of 6):
    Step 1: Load documents      (done)
    Step 2: Chunk documents     (done)
    Step 3: Create embeddings   (done)
    Step 4: Store in vector DB  (done)
    Step 5: Search similar      <-- YOU ARE HERE
    Step 6: Generate answer     (LLM creates answer from context)
=============================================================================
"""

from sentence_transformers import SentenceTransformer
from step4_store_in_vectordb import load_collection, CHROMA_PERSIST_DIR, COLLECTION_NAME
from step3_create_embeddings import EMBEDDING_MODEL


def search_similar_chunks(
    query: str,
    top_k: int = 3,
    model: SentenceTransformer = None,
) -> list[dict]:
    """
    Find the most relevant chunks for a user's question.

    Args:
        query: The user's question (e.g., "How do I reset my password?")
        top_k: How many chunks to return (default 3)
        model: The embedding model (loaded if not provided)

    Returns:
        List of relevant chunks with similarity scores:
        [
            {
                "chunk_id": "password_reset.md::2",
                "filename": "password_reset.md",
                "content": "To reset your password, go to...",
                "score": 0.85,           <- similarity score (higher = more relevant)
                "metadata": {...}        <- extra info about the chunk
            },
            ...
        ]

    HOW IT WORKS:
        1. Load the embedding model (or reuse the provided one)
        2. Convert the query text to an embedding vector
        3. Load the ChromaDB collection
        4. Query the collection with the query embedding
        5. Return the results with similarity scores
    """
    # Step 1: Load the embedding model
    if model is None:
        print(f"Loading embedding model: {EMBEDDING_MODEL}")
        model = SentenceTransformer(EMBEDDING_MODEL)

    # Step 2: Convert query to embedding
    print(f"Searching for: '{query}'")
    query_embedding = model.encode([query]).tolist()

    # Step 3: Load the vector database
    print("Loading vector database...")
    collection = load_collection()

    # Step 4: Search for similar chunks
    # query_embeddings: the vector to search for
    # n_results: how many results to return
    # include: what data to return (documents, metadata, distances)
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    # Step 5: Format the results
    formatted_results = []
    for i in range(len(results["ids"][0])):
        # ChromaDB returns distances (lower = more similar)
        # Convert to a similarity score (higher = more similar)
        distance = results["distances"][0][i]
        similarity = 1 - distance  # Convert distance to similarity

        formatted_results.append({
            "chunk_id": results["ids"][0][i],
            "filename": results["metadatas"][0][i]["filename"],
            "content": results["documents"][0][i],
            "score": round(similarity, 4),
            "metadata": results["metadatas"][0][i],
        })

    return formatted_results


# ---------------------------------------------------------------------------
# RUN THIS SCRIPT STANDALONE TO SEE STEP 5 IN ACTION
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("STEP 5: Searching Similar Chunks")
    print("=" * 60)
    print()

    # Test queries to demonstrate the search
    test_queries = [
        "How do I reset my password?",
        "My VPN won't connect, what should I do?",
        "Printer is showing offline",
        "How to install new software?",
        "WiFi is very slow",
    ]

    for query in test_queries:
        print("-" * 60)
        results = search_similar_chunks(query, top_k=2)

        print(f"\nQuery: {query}")
        print(f"Found {len(results)} relevant chunks:\n")

        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['filename']} (score: {result['score']:.4f})")
            preview = result["content"][:150].replace("\n", " ")
            print(f"     {preview}...")
            print()

    print("=" * 60)
    print("Step 5 Complete!")
    print("These chunks will be sent to the LLM as context in Step 6.")
    print("=" * 60)
