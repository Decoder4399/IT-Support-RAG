"""
 =============================================================================
 STEP 2: CHUNK DOCUMENTS (ADVANCED RAG)
 =============================================================================

 WHAT IS THIS STEP?
     We split long documents into smaller pieces called "chunks".
     This makes it easier to find relevant information and ensures the
     LLM can process the context within its token limit.

 ADVANCED IMPROVEMENTS:
     - Token-aware chunking using tiktoken (not character counting)
     - Markdown header-aware splitting (respects document structure)
     - Larger chunks (1000 tokens) with 200-token overlap
     - Metadata includes section headers for context

 THE RAG PIPELINE (YOU ARE HERE: Step 2 of 6):
     Step 1: Load documents      (done - see step1_load_documents.py)
     Step 2: Chunk documents     <-- YOU ARE HERE
     Step 3: Create embeddings   (convert text to numbers)
     Step 4: Store in vector DB  (save embeddings for fast search)
     Step 5: Search similar      (find relevant chunks for a query)
     Step 6: Generate answer     (LLM creates answer from context)
 =============================================================================
"""

import re
import tiktoken
from step1_load_documents import load_documents


# Token-aware encoding for accurate chunk sizing
_encoder = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """Count tokens in text using tiktoken."""
    return len(_encoder.encode(text))


def chunk_documents(
    documents: list[dict],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[dict]:
    """
    Split documents into token-aware chunks with markdown structure awareness.

    Args:
        documents: List of document dicts from Step 1.
        chunk_size: Maximum tokens per chunk (default 1000).
        chunk_overlap: Tokens to overlap between chunks (default 200).

    Returns:
        A list of chunk dictionaries with section context.
    """
    all_chunks = []

    for doc in documents:
        content = doc["content"]
        filename = doc["filename"]

        if filename.endswith(".md"):
            chunks = _split_markdown(content, filename, chunk_size, chunk_overlap)
        else:
            chunks = _split_plain_text(content, filename, chunk_size, chunk_overlap)

        all_chunks.extend(chunks)

    return all_chunks


def _split_markdown(
    text: str, filename: str, chunk_size: int, overlap: int
) -> list[dict]:
    """
    Split markdown respecting header structure.

    Strategy:
    1. Split on markdown headers (# ## ### etc.)
    2. Each section becomes a chunk (or multiple if too large)
    3. Section headers are prepended to each chunk for context
    """
    # Split on markdown headers, keeping the header with its content
    sections = re.split(r'(?=^#{1,3}\s)', text, flags=re.MULTILINE)

    chunks = []
    current_section_header = ""

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Extract header if present
        header_match = re.match(r'^(#{1,3}\s+.+)$', section, re.MULTILINE)
        if header_match:
            current_section_header = header_match.group(1).strip()

        # If section fits in one chunk, keep it together
        if count_tokens(section) <= chunk_size:
            chunks.append({
                "chunk_id": f"{filename}::{len(chunks)}",
                "filename": filename,
                "content": section,
                "section": current_section_header,
                "chunk_index": len(chunks),
                "total_chunks": 0,  # updated below
            })
        else:
            # Section is too long, split by paragraphs
            para_chunks = _split_by_paragraphs(
                section, filename, len(chunks), chunk_size, overlap,
                section_header=current_section_header,
            )
            chunks.extend(para_chunks)

    # Update total_chunks
    for chunk in chunks:
        chunk["total_chunks"] = len(chunks)

    return chunks


def _split_plain_text(
    text: str, filename: str, chunk_size: int, overlap: int
) -> list[dict]:
    """Split plain text (non-markdown) by paragraphs and sentences."""
    chunks = _split_by_paragraphs(text, filename, 0, chunk_size, overlap)

    # Update total_chunks
    for chunk in chunks:
        chunk["total_chunks"] = len(chunks)

    return chunks


def _split_by_paragraphs(
    text: str, filename: str, start_index: int,
    chunk_size: int, overlap: int, section_header: str = "",
) -> list[dict]:
    """Split text into chunks by paragraphs, then sentences if needed."""
    paragraphs = re.split(r'\n\n+', text)

    chunks = []
    current_chunk = ""
    current_tokens = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        para_tokens = count_tokens(para)

        # If adding this paragraph exceeds chunk_size
        if current_tokens + para_tokens + 2 > chunk_size:
            # Save current chunk if it's not empty
            if current_chunk.strip():
                chunks.append(_make_chunk(
                    current_chunk.strip(), filename, start_index + len(chunks),
                    section_header,
                ))

            # If paragraph itself is too long, split by sentences
            if para_tokens > chunk_size:
                sentence_chunks = _split_by_sentences(
                    para, filename, start_index + len(chunks),
                    chunk_size, overlap, section_header,
                )
                chunks.extend(sentence_chunks)
                current_chunk = ""
                current_tokens = 0
            else:
                # Start new chunk with overlap
                if overlap > 0 and current_chunk:
                    overlap_text = _get_token_overlap(current_chunk, overlap)
                    current_chunk = overlap_text + "\n\n" + para
                    current_tokens = count_tokens(current_chunk)
                else:
                    current_chunk = para
                    current_tokens = para_tokens
        else:
            # Add paragraph to current chunk
            if current_chunk:
                current_chunk += "\n\n" + para
                current_tokens += para_tokens + 2
            else:
                current_chunk = para
                current_tokens = para_tokens

    # Don't forget the last chunk
    if current_chunk.strip():
        chunks.append(_make_chunk(
            current_chunk.strip(), filename, start_index + len(chunks),
            section_header,
        ))

    return chunks


def _split_by_sentences(
    text: str, filename: str, start_index: int,
    chunk_size: int, overlap: int, section_header: str = "",
) -> list[dict]:
    """Split long text by sentence boundaries."""
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = ""
    current_tokens = 0

    for sentence in sentences:
        sent_tokens = count_tokens(sentence)

        if current_tokens + sent_tokens + 1 > chunk_size:
            if current_chunk.strip():
                chunks.append(_make_chunk(
                    current_chunk.strip(), filename, start_index + len(chunks),
                    section_header,
                ))
            current_chunk = sentence
            current_tokens = sent_tokens
        else:
            if current_chunk:
                current_chunk += " " + sentence
                current_tokens += sent_tokens + 1
            else:
                current_chunk = sentence
                current_tokens = sent_tokens

    if current_chunk.strip():
        chunks.append(_make_chunk(
            current_chunk.strip(), filename, start_index + len(chunks),
            section_header,
        ))

    return chunks


def _get_token_overlap(text: str, overlap_tokens: int) -> str:
    """Get the last N tokens of text as a string."""
    tokens = _encoder.encode(text)
    if len(tokens) <= overlap_tokens:
        return text
    overlap_tokens = tokens[-overlap_tokens:]
    return _encoder.decode(overlap_tokens)


def _make_chunk(content: str, filename: str, index: int, section: str = "") -> dict:
    """Create a chunk dictionary with metadata."""
    return {
        "chunk_id": f"{filename}::{index}",
        "filename": filename,
        "content": content,
        "section": section,
        "chunk_index": index,
        "total_chunks": 0,  # caller updates this
    }


# ---------------------------------------------------------------------------
# RUN THIS SCRIPT STANDALONE TO SEE STEP 2 IN ACTION
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("STEP 2: Chunking Documents (Advanced - Token Aware)")
    print("=" * 60)
    print()

    print("Loading documents from Step 1...")
    docs = load_documents()
    print(f"Loaded {len(docs)} documents.")
    print()

    print("Chunking documents (token-aware, markdown-aware)...")
    chunks = chunk_documents(docs, chunk_size=1000, chunk_overlap=200)
    print(f"Created {len(chunks)} chunks.")
    print()

    # Token statistics
    total_tokens = sum(count_tokens(c["content"]) for c in chunks)
    avg_tokens = total_tokens / len(chunks) if chunks else 0
    print(f"Total tokens: {total_tokens}")
    print(f"Average chunk size: {avg_tokens:.0f} tokens")
    print()

    # Show a preview
    print("First 3 chunks:")
    print("-" * 40)
    for chunk in chunks[:3]:
        print(f"ID: {chunk['chunk_id']}")
        print(f"Source: {chunk['filename']} (chunk {chunk['chunk_index'] + 1}/{chunk['total_chunks']})")
        print(f"Section: {chunk.get('section', 'N/A')}")
        print(f"Tokens: {count_tokens(chunk['content'])}")
        print(f"Content: {chunk['content'][:150]}...")
        print("-" * 40)

    print()
    print("Step 2 Complete!")
    print("=" * 60)
