"""
=============================================================================
STEP 6: GENERATE ANSWER WITH LLM
=============================================================================

WHAT IS THIS STEP?
    We take the relevant chunks found in Step 5 and send them along with
    the user's question to a Large Language Model (LLM). The LLM reads
    the context and generates a helpful answer.

WHY DO WE NEED THIS?
    - Retrieved chunks alone are just raw text
    - The LLM synthesizes information from multiple chunks
    - It generates a natural language answer
    - It can cite which source documents it used

THE RAG PIPELINE (YOU ARE HERE: Step 6 of 6):
    Step 1: Load documents      (done)
    Step 2: Chunk documents     (done)
    Step 3: Create embeddings   (done)
    Step 4: Store in vector DB  (done)
    Step 5: Search similar      (done)
    Step 6: Generate answer     <-- YOU ARE HERE
=============================================================================
"""

from openai import OpenAI


# Default system prompt (can be overridden with custom portal/helpline info)
DEFAULT_SYSTEM_PROMPT = """You are a helpful IT Support Assistant. You answer questions about
IT issues like password resets, VPN problems, email issues, printer setup,
software installation, and WiFi connectivity.

IMPORTANT RULES:
1. ONLY answer based on the provided context documents.
2. If the context does not contain the answer, say you do not have enough information.
3. Be concise and actionable - users want step-by-step solutions.
4. When referencing a source, mention which document it came from.
"""


def generate_answer(
    query: str,
    context_chunks: list[dict],
    system_prompt: str = None,
    api_key: str = "",
    model: str = "meta-llama/llama-3.1-8b-instruct",
) -> str:
    """
    Generate an answer using the LLM with retrieved context.

    Args:
        query: The user's question
        context_chunks: List of relevant chunks from Step 5
        system_prompt: Optional custom system prompt
        api_key: OpenRouter API key (passed from UI)
        model: LLM model name (passed from UI)

    Returns:
        The LLM's generated answer as a string
    """
    if not api_key:
        return ("Error: No API key configured. "
                "Please add your OpenRouter API key in the Settings panel.")

    context = format_context(context_chunks)

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
"""

    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt or DEFAULT_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=1000,
    )

    return response.choices[0].message.content


def format_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a context string for the LLM."""
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        filename = chunk.get("filename", "unknown")
        score = chunk.get("score", 0)
        content = chunk.get("content", "")
        context_parts.append(
            f"[Document {i}: {filename} (relevance: {score:.2f})]\n{content}\n"
        )
    return "\n---\n\n".join(context_parts)


if __name__ == "__main__":
    print("Step 6: Generate Answer with LLM (standalone test)")
    print("Run the full pipeline with: python rag_engine.py")
