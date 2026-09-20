"""
=============================================================================
STEP 1: LOAD DOCUMENTS
=============================================================================

WHAT IS THIS STEP?
    This is the first step in the RAG (Retrieval-Augmented Generation) pipeline.
    We load raw documents from the knowledge_base folder and read their content
    into Python so we can process them in later steps.

WHY DO WE NEED THIS?
    RAG needs a knowledge base to search through. Documents on disk are just
    files - we need to read them into memory as text so we can chunk them,
    embed them, and search through them.

SUPPORTED FILE TYPES:
    - .md   (Markdown)
    - .txt  (Plain text)
    - .pdf  (PDF documents)

THE RAG PIPELINE (YOU ARE HERE: Step 1 of 6):
    Step 1: Load documents      <-- YOU ARE HERE
    Step 2: Chunk documents     (split into smaller pieces)
    Step 3: Create embeddings   (convert text to numbers)
    Step 4: Store in vector DB  (save embeddings for fast search)
    Step 5: Search similar      (find relevant chunks for a query)
    Step 6: Generate answer     (LLM creates answer from context)
=============================================================================
"""

import os
from pathlib import Path


def load_pdf(file_path: Path) -> str:
    """
    Extract text from a PDF file using PyMuPDF (fitz).

    Args:
        file_path: Path to the PDF file.

    Returns:
        Extracted text as a single string.
    """
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(str(file_path))
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text("text"))
        doc.close()
        return "\n\n".join(text_parts)
    except ImportError:
        print(f"  Warning: pymupdf not installed, skipping {file_path.name}")
        return ""
    except Exception as e:
        print(f"  Error reading PDF {file_path.name}: {e}")
        return ""


def load_text_file(file_path: Path) -> str:
    """
    Read a plain text file.

    Args:
        file_path: Path to the text file.

    Returns:
        File content as a string.
    """
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Try latin-1 if utf-8 fails
        return file_path.read_text(encoding="latin-1")


def load_documents(data_dir: str = "knowledge_base") -> list[dict]:
    """
    Load all supported documents from the knowledge base directory.

    Supports: .md, .txt, .pdf files.

    Args:
        data_dir: Path to the folder containing knowledge base files.

    Returns:
        A list of document dictionaries:
        {
            "filename": "password_reset.md",
            "filepath": "knowledge_base/password_reset.md",
            "content": "# Password Reset Guide\n\n..."
        }

    HOW IT WORKS:
        1. We scan the data_dir for all supported files
        2. For each file, we read its text content (PDF uses PyMuPDF)
        3. We store the filename, path, and content in a dictionary
        4. We return a list of all these dictionaries
    """
    documents = []
    data_path = Path(data_dir)

    if not data_path.exists():
        print(f"Error: Directory '{data_dir}' not found!")
        return documents

    # Supported extensions and their loaders
    loaders = {
        ".md": lambda p: p.read_text(encoding="utf-8"),
        ".txt": load_text_file,
        ".pdf": load_pdf,
    }

    for file_path in sorted(data_path.rglob("*")):
        if file_path.suffix.lower() in loaders and file_path.is_file():
            try:
                content = loaders[file_path.suffix.lower()](file_path)
                if content.strip():
                    documents.append({
                        "filename": file_path.name,
                        "filepath": str(file_path),
                        "content": content,
                    })
                    print(f"  Loaded: {file_path.name} ({len(content)} characters)")
                else:
                    print(f"  Skipped empty file: {file_path.name}")
            except Exception as e:
                print(f"  Error loading {file_path.name}: {e}")

    return documents


# ---------------------------------------------------------------------------
# RUN THIS SCRIPT STANDALONE TO SEE STEP 1 IN ACTION
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("STEP 1: Loading Documents")
    print("=" * 60)
    print()

    docs = load_documents()

    print()
    print(f"Loaded {len(docs)} documents total.")
    print()

    for doc in docs:
        preview = doc["content"][:200].replace("\n", " ")
        print(f"  {doc['filename']}:")
        print(f"    Preview: {preview}...")
        print()

    print("=" * 60)
    print("Step 1 Complete!")
    print("=" * 60)
