"""
=============================================================================
STEP 4: STORE IN VECTOR DATABASE
=============================================================================

WHAT IS THIS STEP?
    We save all the chunk embeddings into a vector database (ChromaDB).
    This allows fast similarity search when we need to find relevant chunks.

WHY DO WE NEED THIS?
    - We could search through all chunks in memory, but it's slow
    - Vector databases are optimized for similarity search
    - ChromaDB stores vectors and supports fast nearest-neighbor queries
    - It persists to disk so we don't have to re-embed every time

WHAT IS CHROMADB?
    ChromaDB is a lightweight, embedded vector database:
    - No server needed - runs inside your Python process
    - Stores vectors on disk for persistence
    - Supports fast cosine similarity search
    - Perfect for small to medium knowledge bases

THE RAG PIPELINE (YOU ARE HERE: Step 4 of 6):
    Step 1: Load documents      (done)
    Step 2: Chunk documents     (done)
    Step 3: Create embeddings   (done)
    Step 4: Store in vector DB  <-- YOU ARE HERE
    Step 5: Search similar      (find relevant chunks for a query)
    Step 6: Generate answer     (LLM creates answer from context)
=============================================================================
"""

import chromadb
from step1_load_documents import load_documents
from step2_chunk_documents import chunk_documents
from step3_create_embeddings import create_embeddings


# Where to store the vector database on disk
CHROMA_PERSIST_DIR = "./chroma_db"

# Collection name (like a table in a traditional database)
COLLECTION_NAME = "it_support_docs"


def store_in_vectordb(chunks: list[dict]) -> chromadb.Collection:
    """
    Store chunk embeddings in ChromaDB for fast similarity search.

    Args:
        chunks: List of chunk dicts with embeddings from Step 3.

    Returns:
        A ChromaDB collection object (like a table of vectors).

    HOW IT WORKS:
        1. Create a persistent ChromaDB client (stores data on disk)
        2. Create or get a collection (like a table)
        3. Add all chunks with their embeddings, text, and metadata
        4. ChromaDB indexes the vectors for fast search
    """
    # Step 1: Create a persistent ChromaDB client
    # This stores data in the CHROMA_PERSIST_DIR folder
    print(f"Creating ChromaDB client (persist dir: {CHROMA_PERSIST_DIR})")
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

    # Step 2: Delete existing collection to ensure clean rebuild
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"Deleted old collection: {COLLECTION_NAME}")
    except Exception:
        pass

    # Step 3: Create fresh collection
    print(f"Creating collection: {COLLECTION_NAME}")
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hf:space": "cosine"},
    )

    # Step 3: Prepare the data for ChromaDB
    # ChromaDB needs: ids, embeddings, documents (text), and metadata
    ids = [chunk["chunk_id"] for chunk in chunks]
    embeddings = [chunk["embedding"] for chunk in chunks]
    documents = [chunk["content"] for chunk in chunks]
    metadatas = [
        {
            "filename": chunk["filename"],
            "chunk_index": chunk["chunk_index"],
            "total_chunks": chunk["total_chunks"],
        }
        for chunk in chunks
    ]

    # Step 4: Add everything to the collection
    # This is where ChromaDB indexes the vectors
    print(f"Adding {len(chunks)} chunks to ChromaDB...")
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )

    print(f"Stored {collection.count()} chunks in ChromaDB.")
    return collection


def load_collection() -> chromadb.Collection:
    """
    Load an existing ChromaDB collection.

    This is useful when you've already stored the vectors and just
    want to search through them without re-embedding everything.
    """
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    return client.get_collection(name=COLLECTION_NAME)


# ---------------------------------------------------------------------------
# RUN THIS SCRIPT STANDALONE TO SEE STEP 4 IN ACTION
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("STEP 4: Storing in Vector Database")
    print("=" * 60)
    print()

    # Load documents (Step 1)
    print("Loading documents...")
    docs = load_documents()

    # Chunk them (Step 2)
    print("Chunking documents...")
    chunks = chunk_documents(docs)

    # Create embeddings (Step 3)
    print("Creating embeddings...")
    chunks, model = create_embeddings(chunks)
    print()

    # Store in ChromaDB (Step 4)
    print("Storing in ChromaDB...")
    collection = store_in_vectordb(chunks)

    print()

    # Verify the storage
    print("Verifying storage...")
    print(f"  Collection name: {collection.name}")
    print(f"  Total chunks stored: {collection.count()}")

    # Show all stored IDs
    all_ids = collection.get()["ids"]
    print(f"  Chunk IDs: {all_ids[:5]}... (showing first 5)")
    print()

    print("Step 4 Complete!")
    print("Vectors are now stored and ready for search in Step 5.")
    print("=" * 60)
