"""
=============================================================================
STEP 2: CHUNK DOCUMENTS
=============================================================================

WHAT IS THIS STEP?
    We split long documents into smaller pieces called "chunks".
    This makes it easier to find relevant information and ensures the
    LLM can process the context within its token limit.

WHY DO WE NEED THIS?
    - LLMs have a limited "context window" (they can only read so much text)
    - Large documents would exceed this limit if sent as-is
    - Smaller chunks allow more precise retrieval
    - Each chunk can be independently embedded and searched

CHUNKING STRATEGY:
    - We split by paragraphs first (natural breaks in content)
    - If a chunk is still too long, we split by sentences
    - We use "overlap" to preserve context across chunk boundaries
    - Overlap means the last few words of one chunk appear in the next

THE RAG PIPELINE (YOU ARE HERE: Step 2 of 6):
    Step 1: Load documents      (done - see step1_load_documents.py)
    Step 2: Chunk documents     <-- YOU ARE HERE
    Step 3: Create embeddings   (convert text to numbers)
    Step 4: Store in vector DB  (save embeddings for fast search)
    Step 5: Search similar      (find relevant chunks for a query)
    Step 6: Generate answer     (LLM creates answer from context)
=============================================================================
"""

from step1_load_documents import load_documents


def chunk_documents(
    documents: list[dict],
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[dict]:
    """
    Split documents into smaller chunks for embedding and retrieval.

    Args:
        documents: List of document dicts from Step 1.
        chunk_size: Maximum characters per chunk (default 500).
        chunk_overlap: Characters to overlap between chunks (default 50).

    Returns:
        A list of chunk dictionaries:
        {
            "chunk_id": "password_reset.md::0",  <- unique ID for this chunk
            "filename": "password_reset.md",      <- source file
            "content": "This guide covers the standard procedure...",  <- the text
            "chunk_index": 0,                     <- which chunk in this document
            "total_chunks": 5                     <- total chunks from this file
        }

    HOW IT WORKS:
        1. For each document, we split the text into chunks
        2. We try to split at paragraph boundaries (\n\n)
        3. If a paragraph is too long, we split at sentence boundaries
        4. Each chunk overlaps slightly with the next one
        5. This ensures context is preserved across chunk boundaries
    """
    all_chunks = []

    for doc in documents:
        content = doc["content"]
        filename = doc["filename"]

        # Split the document into chunks
        chunks = _split_text(content, chunk_size, chunk_overlap)

        # Create chunk dictionaries
        for i, chunk_text in enumerate(chunks):
            if chunk_text.strip():  # Skip empty chunks
                all_chunks.append({
                    "chunk_id": f"{filename}::{i}",
                    "filename": filename,
                    "content": chunk_text.strip(),
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                })

    return all_chunks


def _split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """
    Split text into chunks with overlap.

    This is the core chunking logic:
        1. First, try to split by double newlines (paragraphs)
        2. If any chunk is still too long, split by sentences
        3. Combine small chunks until we reach chunk_size
        4. Each chunk overlaps with the next by 'overlap' characters
    """
    chunks = []

    # Step A: Split by paragraphs first
    paragraphs = text.split("\n\n")

    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If adding this paragraph exceeds chunk_size
        if len(current_chunk) + len(para) + 2 > chunk_size:
            # Save current chunk if it's not empty
            if current_chunk.strip():
                chunks.append(current_chunk.strip())

            # If the paragraph itself is too long, split by sentences
            if len(para) > chunk_size:
                sentence_chunks = _split_by_sentences(para, chunk_size, overlap)
                chunks.extend(sentence_chunks)
                current_chunk = ""
            else:
                # Start a new chunk with overlap from the previous one
                if overlap > 0 and current_chunk:
                    # Take the last 'overlap' characters as the start of the new chunk
                    current_chunk = current_chunk[-overlap:] + "\n\n" + para
                else:
                    current_chunk = para
        else:
            # Add paragraph to current chunk
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para

    # Don't forget the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def _split_by_sentences(text: str, chunk_size: int, overlap: int) -> list[str]:
    """
    Split long text by sentence boundaries.

    Sentences are natural units of meaning, so splitting at sentence
    boundaries preserves the semantic meaning of each chunk better
    than splitting in the middle of a sentence.
    """
    # Simple sentence splitting (handles . ! ? followed by space or newline)
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 > chunk_size:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


# ---------------------------------------------------------------------------
# RUN THIS SCRIPT STANDALONE TO SEE STEP 2 IN ACTION
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("STEP 2: Chunking Documents")
    print("=" * 60)
    print()

    # First load the documents (Step 1)
    print("Loading documents from Step 1...")
    docs = load_documents()
    print(f"Loaded {len(docs)} documents.")
    print()

    # Now chunk them
    print("Chunking documents...")
    chunks = chunk_documents(docs, chunk_size=500, chunk_overlap=50)
    print(f"Created {len(chunks)} chunks.")
    print()

    # Show some statistics
    total_chars = sum(len(c["content"]) for c in chunks)
    avg_chars = total_chars / len(chunks) if chunks else 0
    print(f"Total characters: {total_chars}")
    print(f"Average chunk size: {avg_chars:.0f} characters")
    print()

    # Show a preview of the first few chunks
    print("First 3 chunks:")
    print("-" * 40)
    for chunk in chunks[:3]:
        print(f"ID: {chunk['chunk_id']}")
        print(f"Source: {chunk['filename']} (chunk {chunk['chunk_index'] + 1}/{chunk['total_chunks']})")
        print(f"Content: {chunk['content'][:150]}...")
        print("-" * 40)

    print()
    print("Step 2 Complete!")
    print("These chunks are ready to be converted to embeddings in Step 3.")
    print("=" * 60)
