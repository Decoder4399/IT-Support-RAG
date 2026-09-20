"""
 =============================================================================
 STEP 5a: QUERY REWRITING (ADVANCED RAG)
 =============================================================================

 WHAT IS THIS STEP?
     Before searching, we use the LLM to rewrite and expand the user's query.
     This improves retrieval quality by generating better search terms.

 WHY DO WE NEED THIS?
     - User queries are often short and ambiguous
     - "it won't work" needs to be expanded to be searchable
     - Follow-up questions use pronouns ("it", "that", "this")
     - Multiple paraphrases improve retrieval recall

 TECHNIQUES USED:
     1. Query Expansion: Generate 3 paraphrases, search with all
     2. Pronoun Resolution: Use chat history to resolve "it", "that"
     3. Keyword Extraction: Extract key terms for BM25 search

 THE RAG PIPELINE (YOU ARE HERE: Step 5a of 6):
     Step 1-4: Build phase (done)
     Step 5a: Query rewriting  <-- YOU ARE HERE
     Step 5b: Hybrid search
     Step 5c: Rerank
     Step 6: Generate answer
 =============================================================================
"""

from openai import OpenAI


def rewrite_query(
    query: str,
    chat_history: list[dict] = None,
    api_key: str = "",
    model: str = "meta-llama/llama-3.1-8b-instruct",
) -> dict:
    """
    Rewrite the user's query for better retrieval.

    Args:
        query: The original user question
        chat_history: Previous conversation turns for context
        api_key: OpenRouter API key
        model: LLM model to use for rewriting

    Returns:
        {
            "rewritten": "The improved query for semantic search",
            "keywords": ["keyword1", "keyword2", ...],
            "original": "The original query"
        }
    """
    if not api_key:
        return {
            "rewritten": query,
            "keywords": query.split(),
            "original": query,
        }

    history_context = ""
    if chat_history:
        recent = chat_history[-6:]  # last 3 turns
        history_context = "\n".join(
            f"{m['role']}: {m['content'][:200]}" for m in recent
        )

    client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

    # Get rewritten query + keywords in one call
    rewriting_prompt = f"""You are a search query optimizer for an IT support system.

Given the user's question (and conversation history if provided), produce:

1. REWRITTEN: A clear, self-contained search query that captures the user's intent.
   - Resolve pronouns (it, that, this) using conversation context
   - Add relevant technical terms
   - Make it specific enough for semantic search

2. KEYWORDS: 3-5 important technical keywords from the query, separated by commas.

Respond in this exact format:
REWRITTEN: <the rewritten query>
KEYWORDS: <keyword1>, <keyword2>, <keyword3>

User question: {query}

{f'Conversation history:{chr(10)}{history_context}' if history_context else ''}"""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": rewriting_prompt}],
        temperature=0.1,
        max_tokens=200,
    )

    result_text = response.choices[0].message.content.strip()

    # Parse the response
    rewritten = query
    keywords = query.split()

    for line in result_text.split("\n"):
        if line.upper().startswith("REWRITTEN:"):
            rewritten = line.split(":", 1)[1].strip()
        elif line.upper().startswith("KEYWORDS:"):
            kw_text = line.split(":", 1)[1].strip()
            keywords = [k.strip() for k in kw_text.split(",") if k.strip()]

    return {
        "rewritten": rewritten,
        "keywords": keywords,
        "original": query,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("STEP 5a: Query Rewriting (Advanced RAG)")
    print("=" * 60)
    print()
    print("Run the full pipeline with: python rag_engine.py")
    print("=" * 60)
