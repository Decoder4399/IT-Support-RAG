"""
 =============================================================================
 STEP 6: GENERATE ANSWER WITH LLM (ADVANCED RAG)
 =============================================================================

 WHAT IS THIS STEP?
     We take the reranked chunks and send them along with the user's
     question (and chat history) to an LLM for answer generation.

 ADVANCED IMPROVEMENTS:
     - Conversation memory: last 5 turns included in prompt
     - Context-aware answers that reference previous questions
     - Better prompt engineering for step-by-step IT answers

 THE RAG PIPELINE (YOU ARE HERE: Step 6 of 6):
     Step 1-4: Build phase (done)
     Step 5a-5c: Advanced retrieval (done)
     Step 6: Generate answer  <-- YOU ARE HERE
 =============================================================================
"""

from openai import OpenAI


DEFAULT_SYSTEM_PROMPT = """You are a helpful IT Support Assistant. You answer questions about
IT issues like password resets, VPN problems, email issues, printer setup,
software installation, and WiFi connectivity.

IMPORTANT RULES:
1. ONLY answer based on the provided context documents.
2. If the context does not contain the answer, say you do not have enough information.
3. Be concise and actionable - users want step-by-step solutions.
4. When referencing a source, mention which document it came from.
5. If the user asks a follow-up question, use conversation history for context.
{custom_section}
"""


def generate_answer(
    query: str,
    context_chunks: list[dict],
    system_prompt: str = None,
    api_key: str = "",
    model: str = "meta-llama/llama-3.1-8b-instruct",
    chat_history: list[dict] = None,
    stream: bool = False,
) -> str:
    """
    Generate an answer using the LLM with retrieved context and conversation history.

    Args:
        query: The user's question
        context_chunks: Reranked relevant chunks from Step 5c
        system_prompt: Optional custom system prompt
        api_key: OpenRouter API key
        model: LLM model name
        chat_history: Previous conversation turns
        stream: If True, return a generator that yields chunks

    Returns:
        The LLM's generated answer as a string, or a generator if stream=True
    """
    if not api_key:
        return ("Error: No API key configured. "
                "Please add your OpenRouter API key in the Settings panel.")

    context = format_context(context_chunks)

    # Build messages with conversation history
    messages = [
        {"role": "system", "content": system_prompt or DEFAULT_SYSTEM_PROMPT},
    ]

    # Add last 3 turns of history for context
    if chat_history:
        for msg in chat_history[-3:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"][:300],
            })

    # Add current query with context
    user_prompt = f"""Answer the following question based on the provided context.

## Question
{query}

## Context
{context}

## Instructions
- Answer using ONLY the information in the context above.
- Cite your sources when possible.
- If the context doesn't contain the answer, say so clearly.
- Be specific and provide step-by-step guidance where possible.
- If this is a follow-up question, use the conversation history for context.
"""
    messages.append({"role": "user", "content": user_prompt})

    client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
        max_tokens=500,
        stream=stream,
    )

    if stream:
        def _generate():
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        return _generate()

    return response.choices[0].message.content


def format_context(chunks: list[dict]) -> str:
    """Format reranked chunks into a context string for the LLM."""
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        filename = chunk.get("filename", "unknown")
        score = chunk.get("rerank_score") or chunk.get("score", 0)
        content = chunk.get("content", "")[:500]
        section = chunk.get("section", "")
        header = f" [Section: {section}]" if section else ""
        context_parts.append(
            f"[Document {i}: {filename}{header} (relevance: {score:.2f})]\n{content}\n"
        )
    return "\n---\n\n".join(context_parts)


if __name__ == "__main__":
    print("Step 6: Generate Answer with LLM (Advanced RAG)")
    print("Run the full pipeline with: python rag_engine.py")
