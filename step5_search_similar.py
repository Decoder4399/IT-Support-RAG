"""
 =============================================================================
 STEP 5: SEARCH SIMILAR CHUNKS (ADVANCED RAG)
 =============================================================================

 WHAT IS THIS STEP?
     Find the most relevant chunks for a user's question using cosine
     similarity search with score thresholding and deduplication.

 ADVANCED IMPROVEMENTS:
     - Cosine similarity (proper distance metric)
     - Score threshold: discard results below 0.3 similarity
     - Deduplication: only keep best chunk per source document

 THE RAG PIPELINE (YOU ARE HERE: Step 5 of 6):
     Step 1-4: Build phase (done)
     Step 5: Search similar  <-- YOU ARE HERE
     Step 6: Generate answer
 =============================================================================
"""

from sentence_transformers import SentenceTransformer
from step4_store_in_vectordb import load_collection
from step3_create_embeddings import EMBEDDING_MODEL


def search_similar_chunks(
    query: str,
    top_k: int = 3,
    model: SentenceTransformer = None,
    score_threshold: float = 0.3,
) -> list[dict]:
    """
    Find the most relevant chunks with score filtering and deduplication.

    Args:
        query: The user's question
        top_k: How many chunks to return (default 3)
        model: The embedding model (loaded if not provided)
        score_threshold: Minimum similarity score to keep (default 0.3)

    Returns:
        Filtered, deduplicated list of relevant chunks
    """
    if model is None:
        model = SentenceTransformer(EMBEDDING_MODEL)

    query_embedding = model.encode([query]).tolist()
    collection = load_collection()

    # Retrieve more candidates for filtering
    n_candidates = min(top_k * 3, collection.count())
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_candidates,
        include=["documents", "metadatas", "distances"],
    )

    # Format results with cosine similarity scores
    candidates = []
    for i in range(len(results["ids"][0])):
        # With cosine metric, distance is 1 - cosine_similarity
        distance = results["distances"][0][i]
        similarity = 1 - distance

        if similarity < score_threshold:
            continue

        candidates.append({
            "chunk_id": results["ids"][0][i],
            "filename": results["metadatas"][0][i].get("filename", "unknown"),
            "content": results["documents"][0][i],
            "score": round(similarity, 4),
            "metadata": results["metadatas"][0][i],
            "section": results["metadatas"][0][i].get("section", ""),
        })

    # Deduplication: keep only the best chunk per source file
    deduplicated = _deduplicate_by_source(candidates)

    return deduplicated[:top_k]


def _deduplicate_by_source(chunks: list[dict]) -> list[dict]:
    """Keep only the highest-scoring chunk per source file."""
    best_per_file = {}
    for chunk in chunks:
        fname = chunk["filename"]
        if fname not in best_per_file or chunk["score"] > best_per_file[fname]["score"]:
            best_per_file[fname] = chunk
    return list(best_per_file.values())


# ---------------------------------------------------------------------------
# RUN THIS SCRIPT STANDALONE
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("STEP 5: Searching Similar Chunks (Advanced RAG)")
    print("=" * 60)
    print()
    print("Run the full pipeline with: python rag_engine.py")
    print("=" * 60)
