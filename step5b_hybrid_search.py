"""
 =============================================================================
 STEP 5b: HYBRID SEARCH (ADVANCED RAG)
 =============================================================================

 WHAT IS THIS STEP?
     Combine keyword search (BM25) with semantic search (embeddings)
     using Reciprocal Rank Fusion (RRF) to get the best of both worlds.

 OPTIMIZED:
     - BM25 index cached in memory, rebuilt only when collection changes
     - Cosine similarity computed via vectorized numpy operations
     - No redundant ChromaDB fetches per query
"""

import re
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from step4_store_in_vectordb import load_collection
from step3_create_embeddings import EMBEDDING_MODEL


# --- Cache ---
_bm25_index = None
_bm25_ids = None
_bm25_documents = None
_bm25_metadatas = None
_bm25_embeddings_matrix = None
_bm25_count = 0


def _rebuild_bm25_cache(model):
    """Rebuild the BM25 + embedding cache from ChromaDB."""
    global _bm25_index, _bm25_ids, _bm25_documents, _bm25_metadatas
    global _bm25_embeddings_matrix, _bm25_count

    collection = load_collection()
    all_data = collection.get(include=["documents", "metadatas", "embeddings"])

    if not all_data["ids"]:
        _bm25_index = None
        _bm25_count = 0
        return

    _bm25_ids = all_data["ids"]
    _bm25_documents = all_data["documents"]
    _bm25_metadatas = all_data["metadatas"]

    # Build BM25 index
    tokenized_corpus = [_tokenize(doc) for doc in _bm25_documents]
    _bm25_index = BM25Okapi(tokenized_corpus)

    # Build embeddings matrix for vectorized cosine
    _bm25_embeddings_matrix = np.array(all_data["embeddings"])
    _bm25_count = len(_bm25_ids)

    # Pre-compute norms for cosine similarity
    norms = np.linalg.norm(_bm25_embeddings_matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1
    _bm25_embeddings_matrix = _bm25_embeddings_matrix / norms


def hybrid_search(
    query: str,
    keywords: list[str] = None,
    top_k: int = 10,
    model: SentenceTransformer = None,
) -> list[dict]:
    """
    Search using both BM25 (keyword) and semantic (embedding) search.
    Uses cached BM25 index and vectorized cosine for speed.
    """
    if model is None:
        model = SentenceTransformer(EMBEDDING_MODEL)

    # Rebuild cache if empty or collection changed
    collection = load_collection()
    current_count = collection.count()
    if _bm25_index is None or _bm25_count != current_count:
        _rebuild_bm25_cache(model)

    if _bm25_index is None or _bm25_count == 0:
        return []

    # --- BM25 Keyword Search ---
    search_terms = keywords if keywords else query.split()
    bm25_scores = _bm25_index.get_scores(search_terms)
    bm25_ranked = np.argsort(bm25_scores)[::-1]

    # --- Semantic Search (vectorized) ---
    query_embedding = model.encode([query])[0]
    query_norm = np.linalg.norm(query_embedding)
    if query_norm > 0:
        query_embedding = query_embedding / query_norm
    cosine_scores = _bm25_embeddings_matrix @ query_embedding
    semantic_ranked = np.argsort(cosine_scores)[::-1]

    # --- Reciprocal Rank Fusion ---
    k = 60
    fused_scores = {}

    for rank in range(min(top_k * 2, _bm25_count)):
        idx = bm25_ranked[rank]
        doc_id = _bm25_ids[idx]
        fused_scores[doc_id] = fused_scores.get(doc_id, 0) + 1.0 / (k + rank + 1)

    for rank in range(min(top_k * 2, _bm25_count)):
        idx = semantic_ranked[rank]
        doc_id = _bm25_ids[idx]
        fused_scores[doc_id] = fused_scores.get(doc_id, 0) + 1.0 / (k + rank + 1)

    ranked_ids = sorted(fused_scores.keys(), key=lambda x: fused_scores[x], reverse=True)

    id_to_idx = {_bm25_ids[i]: i for i in range(_bm25_count)}
    results = []

    for doc_id in ranked_ids[:top_k]:
        idx = id_to_idx[doc_id]
        meta = _bm25_metadatas[idx]
        results.append({
            "chunk_id": doc_id,
            "filename": meta.get("filename", "unknown"),
            "content": _bm25_documents[idx],
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
    print("Step 5b: Hybrid Search (Advanced RAG)")
    print("Run the full pipeline with: python rag_engine.py")
