"""
=============================================================================
STEP 3: CREATE EMBEDDINGS
=============================================================================

WHAT IS THIS STEP?
    We convert each text chunk into a numerical vector (a list of numbers)
    using an "embedding model". These vectors capture the semantic meaning
    of the text - similar texts produce similar vectors.

WHY DO WE NEED THIS?
    - Computers can't directly compare text for similarity
    - Embeddings convert text into numbers that CAN be compared
    - Similar concepts end up "close together" in vector space
    - This allows us to find relevant chunks using math instead of keywords

WHAT IS AN EMBEDDING?
    Think of it like this:
    - "How do I reset my password?" might become [0.12, -0.45, 0.78, ...]
    - "I forgot my login credentials" might become [0.11, -0.43, 0.76, ...]
    - These vectors are CLOSE because the sentences mean similar things
    - "My printer is jammed" would be VERY DIFFERENT: [-0.34, 0.89, -0.12, ...]

WHICH EMBEDDING MODEL ARE WE USING?
    - Model: "all-MiniLM-L6-v2"
    - It's a small, fast model that runs on CPU
    - Produces 384-dimensional vectors (384 numbers per chunk)
    - Good balance of speed and accuracy for demo purposes

THE RAG PIPELINE (YOU ARE HERE: Step 3 of 6):
    Step 1: Load documents      (done)
    Step 2: Chunk documents     (done)
    Step 3: Create embeddings   <-- YOU ARE HERE
    Step 4: Store in vector DB  (save embeddings for fast search)
    Step 5: Search similar      (find relevant chunks for a query)
    Step 6: Generate answer     (LLM creates answer from context)
=============================================================================
"""

from sentence_transformers import SentenceTransformer
from step1_load_documents import load_documents
from step2_chunk_documents import chunk_documents


# Which embedding model to use
# This is a small, fast model that runs on CPU
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def create_embeddings(chunks: list[dict]) -> tuple[list[dict], SentenceTransformer]:
    """
    Convert text chunks into embedding vectors.

    Args:
        chunks: List of chunk dicts from Step 2.

    Returns:
        A tuple of:
        - List of chunk dicts, each now with an "embedding" field added
        - The loaded embedding model (needed for querying later)

    HOW IT WORKS:
        1. Load the sentence-transformers model
        2. Extract the text from each chunk
        3. Pass all texts to the model to get vectors
        4. Add each vector to its corresponding chunk dict
        5. Return the chunks with embeddings attached
    """
    # Step 1: Load the embedding model
    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)

    # Step 2: Extract texts from chunks
    texts = [chunk["content"] for chunk in chunks]
    print(f"Creating embeddings for {len(texts)} chunks...")

    # Step 3: Generate embeddings (this is the magic step!)
    # The model converts each text into a vector of 384 numbers
    embeddings = model.encode(texts, show_progress_bar=True)

    # Step 4: Add embeddings to chunks
    for chunk, embedding in zip(chunks, embeddings):
        chunk["embedding"] = embedding.tolist()  # Convert numpy array to list

    print(f"Embeddings created! Each is {len(embeddings[0])} dimensions.")
    return chunks, model


def get_query_embedding(query: str, model: SentenceTransformer) -> list[float]:
    """
    Create an embedding for a search query.

    This uses the same model that was used for the chunks.
    The query embedding can be compared to chunk embeddings
    to find the most relevant chunks.
    """
    embedding = model.encode([query])
    return embedding[0].tolist()


# ---------------------------------------------------------------------------
# RUN THIS SCRIPT STANDALONE TO SEE STEP 3 IN ACTION
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("STEP 3: Creating Embeddings")
    print("=" * 60)
    print()

    # Load documents (Step 1)
    print("Loading documents...")
    docs = load_documents()

    # Chunk them (Step 2)
    print("Chunking documents...")
    chunks = chunk_documents(docs)

    # Create embeddings (Step 3)
    print()
    chunks, model = create_embeddings(chunks)

    print()

    # Show what an embedding looks like
    sample = chunks[0]
    print(f"Sample chunk: {sample['chunk_id']}")
    print(f"Text: {sample['content'][:100]}...")
    print(f"Embedding (first 10 numbers): {sample['embedding'][:10]}")
    print(f"Embedding dimension: {len(sample['embedding'])}")
    print()

    # Demonstrate similarity: query vs chunks
    print("Demonstrating semantic similarity...")
    print("Query: 'How do I reset my password?'")
    print()

    query_embedding = get_query_embedding("How do I reset my password?", model)

    # Calculate similarity with each chunk
    import numpy as np

    similarities = []
    for chunk in chunks:
        chunk_embedding = np.array(chunk["embedding"])
        query_vec = np.array(query_embedding)
        # Cosine similarity = dot product / (magnitude of both)
        similarity = np.dot(query_vec, chunk_embedding) / (
            np.linalg.norm(query_vec) * np.linalg.norm(chunk_embedding)
        )
        similarities.append((chunk["chunk_id"], similarity, chunk["content"][:80]))

    # Sort by similarity (highest first)
    similarities.sort(key=lambda x: x[1], reverse=True)

    print("Top 3 most relevant chunks:")
    for i, (chunk_id, score, preview) in enumerate(similarities[:3], 1):
        print(f"  {i}. {chunk_id} (similarity: {score:.4f})")
        print(f"     {preview}...")
        print()

    print("Step 3 Complete!")
    print("Embeddings are ready to be stored in a vector database in Step 4.")
    print("=" * 60)
