"""
 =============================================================================
 STEP 5b: HYBRID SEARCH (ADVANCED RAG)
 =============================================================================

 WHAT IS THIS STEP?
     Combine keyword search (BM25) with semantic search (embeddings)
     using Reciprocal Rank Fusion (RRF) to get the best of both worlds.

 WHY DO WE NEED THIS?
     - Semantic search misses exact keyword matches
     - BM25 misses synonym/paraphrase matches
     - Hybrid search covers both blind spots
     - RRF combines rankings without needing score normalization

 TECHNIQUE: Reciprocal Rank Fusion (RRF)
     score(d) = sum(1 / (k + rank_i(d))) for each ranking system
     k = 60 (standard constant)

 THE RAG PIPELINE (YOU ARE HERE: Step 5b of 6):
     Step 1-4: Build phase (done)
     Step 5a: Query rewriting (done)
     Step 5b: Hybrid search   <-- YOU ARE HERE
     Step 5c: Rerank
     Step 6: Generate answer
 =============================================================================
"""

import re
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from step4_store_in_vectordb import load_collection
from step3_create_embeddings import EMBEDDING_MODEL


def hybrid_search(
    query: str,
    keywords: list[str] = None,
    top_k: int = 10,
    model: SentenceTransformer = None,
) -> list[dict]:
    """
    Search using both BM25 (keyword) and semantic (embedding) search.

    Args:
        query: The search query (rewritten from step5a)
        keywords: Keywords for BM25 search (extracted in step5a)
        top_k: Number of results to return
        model: Embedding model (loaded if not provided)

    Returns:
        Fused and ranked list of chunks
    """
    if model is None:
        model = SentenceTransformer(EMBEDDING_MODEL)

    collection = load_collection()

    # Fetch all chunks from ChromaDB
    all_data = collection.get(
        include=["documents", "metadatas", "embeddings"],
    )

    if not all_data["ids"]:
        return []

    documents = all_data["documents"]
    metadatas = all_data["metadatas"]
    ids = all_data["ids"]
    embeddings = all_data["embeddings"]

    # --- BM25 Keyword Search ---
    tokenized_corpus = [_tokenize(doc) for doc in documents]
    bm25 = BM25Okapi(tokenized_corpus)

    search_terms = keywords if keywords else query.split()
    bm25_scores = bm25.get_scores(search_terms)

    # Get BM25 rankings (higher score = more relevant)
    bm25_ranked = sorted(
        range(len(bm25_scores)),
        key=lambda i: bm25_scores[i],
        reverse=True,
    )

    # --- Semantic Search ---
    query_embedding = model.encode([query]).tolist()
    import numpy as np
    query_vec = np.array(query_embedding[0])

    cosine_scores = []
    for emb in embeddings:
        emb_vec = np.array(emb)
        # Cosine similarity
        score = np.dot(query_vec, emb_vec) / (
            np.linalg.norm(query_vec) * np.linalg.norm(emb_vec) + 1e-10
        )
        cosine_scores.append(score)

    semantic_ranked = sorted(
        range(len(cosine_scores)),
        key=lambda i: cosine_scores[i],
        reverse=True,
    )

    # --- Reciprocal Rank Fusion ---
    k = 60  # Standard RRF constant
    fused_scores = {}

    for rank, idx in enumerate(bm25_ranked[:top_k * 2]):
        doc_id = ids[idx]
        fused_scores[doc_id] = fused_scores.get(doc_id, 0) + 1.0 / (k + rank + 1)

    for rank, idx in enumerate(semantic_ranked[:top_k * 2]):
        doc_id = ids[idx]
        fused_scores[doc_id] = fused_scores.get(doc_id, 0) + 1.0 / (k + rank + 1)

    # Sort by fused score
    ranked_ids = sorted(fused_scores.keys(), key=lambda x: fused_scores[x], reverse=True)

    # Build results
    id_to_idx = {doc_id: i for i, doc_id in enumerate(ids)}
    results = []

    for doc_id in ranked_ids[:top_k]:
        idx = id_to_idx[doc_id]
        meta = metadatas[idx]
        results.append({
            "chunk_id": doc_id,
            "filename": meta.get("filename", "unknown"),
            "content": documents[idx],
            "score": round(fused_scores[doc_id], 4),
            "metadata": meta,
            "section": meta.get("section", ""),
        })

    return results


def _tokenize(text: str) -> list[str]:
    """Simple tokenization for BM25."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return text.split()


if __name__ == "__main__":
    print("=" * 60)
    print("STEP 5b: Hybrid Search (Advanced RAG)")
    print("=" * 60)
    print()
    print("Run the full pipeline with: python rag_engine.py")
    print("=" * 60)
