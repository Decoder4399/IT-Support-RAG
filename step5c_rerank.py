"""
 =============================================================================
 STEP 5c: CROSS-ENCODER RERANKING (ADVANCED RAG)
 =============================================================================

 WHAT IS THIS STEP?
     After retrieving initial candidates (top-10), we rerank them using
     a cross-encoder model that reads the query and document together
     for more accurate relevance scoring.

 WHY DO WE NEED THIS?
     - Bi-encoders (embeddings) compare query and doc independently
     - Cross-encoders read both together, giving better accuracy
     - Reranking catches false positives from the initial retrieval
     - We retrieve more candidates (10) then keep only the best (3)

 MODEL: cross-encoder/ms-marco-MiniLM-L-6-v2
     - Trained on Microsoft MS MARCO passage ranking
     - 6-layer MiniLM, fast inference
     - Input: [query, document] pair
     - Output: relevance score

 THE RAG PIPELINE (YOU ARE HERE: Step 5c of 6):
     Step 1-4: Build phase (done)
     Step 5a: Query rewriting (done)
     Step 5b: Hybrid search (done)
     Step 5c: Rerank         <-- YOU ARE HERE
     Step 6: Generate answer
 =============================================================================
"""

from sentence_transformers import CrossEncoder


# Lazy-loaded reranker model
_reranker = None


def _get_reranker():
    """Load the cross-encoder reranker model (lazy loading)."""
    global _reranker
    if _reranker is None:
        print("  Loading cross-encoder reranker...")
        _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _reranker


def rerank_chunks(
    query: str,
    chunks: list[dict],
    top_k: int = 3,
) -> list[dict]:
    """
    Rerank retrieved chunks using a cross-encoder model.

    Args:
        query: The search query
        chunks: List of candidate chunks from hybrid search
        top_k: Number of chunks to keep after reranking

    Returns:
        Reranked list of chunks with new scores
    """
    if not chunks:
        return []

    if len(chunks) <= top_k:
        # Already have fewer results than needed
        return chunks

    reranker = _get_reranker()

    # Create query-document pairs
    pairs = [(query, chunk["content"]) for chunk in chunks]

    # Get cross-encoder scores
    scores = reranker.predict(pairs)

    # Assign scores and sort
    for chunk, score in zip(chunks, scores):
        chunk["rerank_score"] = round(float(score), 4)

    # Sort by rerank score (higher = more relevant)
    reranked = sorted(chunks, key=lambda x: x["rerank_score"], reverse=True)

    return reranked[:top_k]


if __name__ == "__main__":
    print("=" * 60)
    print("STEP 5c: Cross-Encoder Reranking (Advanced RAG)")
    print("=" * 60)
    print()
    print("Run the full pipeline with: python rag_engine.py")
    print("=" * 60)
