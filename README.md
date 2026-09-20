# IT Support RAG Chatbot

> A simple, educational **RAG (Retrieval-Augmented Generation)** chatbot for IT support.
> Built to teach anyone how RAG works — step by step, line by line.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?logo=streamlit&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-0.4+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## What is RAG?

**RAG = Retrieval-Augmented Generation**

Instead of just asking an AI model a question, RAG gives the model a "reference book" to look things up in before answering. This makes the AI's answers grounded in real documentation, not just its training data.

```
Normal AI:   Question → AI guesses the answer
RAG:          Question → Find relevant docs → AI reads docs → AI answers with sources
```

### Why RAG Matters

| Problem | RAG Solution |
|---|---|
| LLMs hallucinate (make things up) | Answers are grounded in real documents |
| LLMs have stale knowledge | Just add new docs to update knowledge |
| No way to verify sources | Every answer shows which documents it used |
| Generic answers | Answers are tailored to your specific IT policies |

---

## How RAG Works (The 6 Steps)

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE RAG PIPELINE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │  Step 1     │    │  Step 2     │    │  Step 3     │        │
│  │  LOAD       │ →  │  CHUNK      │ →  │  EMBED      │        │
│  │  Documents  │    │  Documents  │    │  Text       │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
│        │                  │                  │                  │
│        ▼                  ▼                  ▼                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │  Step 4     │    │  Step 5     │    │  Step 6     │        │
│  │  STORE      │ →  │  SEARCH     │ →  │  GENERATE   │        │
│  │  in DB      │    │  Similar    │    │  Answer     │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
│                                                                 │
│  BUILD PHASE (one-time)          QUERY PHASE (each question)   │
└─────────────────────────────────────────────────────────────────┘
```

### Step 1: Load Documents
**File:** `step1_load_documents.py`

Read markdown, PDF, and text files from the `knowledge_base/` folder into Python.

```python
# Example: Loading a file
content = open("knowledge_base/password_reset.md").read()
# Result: {"filename": "password_reset.md", "content": "# Password Reset..."}
```

**Supported formats:** `.md`, `.txt`, `.pdf`

### Step 2: Chunk Documents
**File:** `step2_chunk_documents.py`

LLMs can't read entire documents at once. We split them into small pieces (~500 characters each) with overlap to preserve context.

```
BEFORE CHUNKING:
┌──────────────────────────────────────────┐
│ Long document about password resets...   │
│ (5000 characters)                        │
└──────────────────────────────────────────┘

AFTER CHUNKING:
┌──────────┐ ┌──────────┐ ┌──────────┐
│ Chunk 1  │ │ Chunk 2  │ │ Chunk 3  │ ... (10 chunks)
│ 500 chars│ │ 500 chars│ │ 500 chars│
└──────────┘ └──────────┘ └──────────┘
```

### Step 3: Create Embeddings
**File:** `step3_create_embeddings.py`

Convert each text chunk into a list of numbers (a vector) that represents its meaning. Similar texts get similar numbers.

```
"How do I reset my password?"  →  [0.12, -0.45, 0.78, ...]  (384 numbers)
"I forgot my login"            →  [0.11, -0.43, 0.76, ...]  (very similar!)
"My printer is jammed"         →  [-0.34, 0.89, -0.12, ...] (very different!)
```

**Model:** `all-MiniLM-L6-v2` (384 dimensions, runs on CPU)

### Step 4: Store in Vector Database
**File:** `step4_store_in_vectordb.py`

Save all vectors in ChromaDB, a database optimized for finding similar vectors quickly.

```
ChromaDB (Vector Database)
┌─────────────────────────────────────────┐
│ ID              │ Vector      │ Text    │
├─────────────────────────────────────────┤
│ pass_reset.md::0│ [0.12, ...] │ "To..."│
│ pass_reset.md::1│ [0.15, ...] │ "Try..."│
│ vpn_troub.md::0 │ [-0.2, ...] │ "If..."│
│ ...              │ ...         │ ...    │
└─────────────────────────────────────────┘
```

### Step 5: Search Similar Chunks
**File:** `step5_search_similar.py`

When a user asks a question, convert it to a vector and find the most similar chunks in the database.

```
User: "How do I reset my password?"
         ↓ (convert to vector)
Query: [0.12, -0.44, 0.77, ...]
         ↓ (search ChromaDB)
Top 3 results:
  1. password_reset.md::2 (score: 0.85)
  2. password_reset.md::0 (score: 0.82)
  3. email_issues.md::1   (score: 0.45)
```

### Step 6: Generate Answer
**File:** `step6_generate_answer.py`

Send the retrieved chunks + the user's question to an LLM, which reads the context and generates a helpful answer.

```
┌─────────────────────────────────────────────────────┐
│ LLM Prompt:                                         │
│                                                     │
│ System: You are an IT support assistant...          │
│                                                     │
│ Context: [Retrieved chunks from Step 5]             │
│ - "To reset password, go to accounts.company..."   │
│ - "If self-service fails, call IT at ext. 5555..." │
│                                                     │
│ Question: "How do I reset my password?"             │
└─────────────────────────────────────────────────────┘
         ↓
LLM Answer: "To reset your password, follow these steps:
1. Go to https://accounts.company.com/reset
2. Enter your employee ID
3. Check your email for the reset link
4. Create a new password (min 12 characters)

If self-service fails, call IT Help Desk at ext. 5555."
```

---

## Live Demo — Web UI

The Streamlit app has **3 pages** accessible from the hamburger menu (☰):

### Chat Page
- Dark-themed chat interface with source citations
- Quick prompt buttons for common IT questions
- Upload new documents directly from the sidebar
- Rebuild knowledge base on demand

### Settings Page
- Enter your OpenRouter API key (stored in session only, never saved to disk)
- Choose from 6 LLM models (Llama, Claude, Gemini, Mistral, GPT-4o)
- Customize portal URL and helpline number injected into answers

### How RAG Works Page
- Animated step-by-step visualization of the RAG pipeline
- Play/Reset/Show All controls
- Progress bar and expandable detail cards

---

## Project Structure

```
it-support-rag/
├── app.py                         # Streamlit entry point (navigation)
├── pages/
│   ├── __init__.py
│   ├── chat.py                    # Chat page UI
│   ├── settings.py                # Settings page (API key, model, customization)
│   └── how_rag_works.py           # Animated RAG explanation page
├── rag_engine.py                  # Full RAG pipeline (combines all 6 steps)
├── step1_load_documents.py        # Step 1: Load .md/.txt/.pdf files
├── step2_chunk_documents.py       # Step 2: Split into overlapping chunks
├── step3_create_embeddings.py     # Step 3: Convert text to vectors
├── step4_store_in_vectordb.py     # Step 4: Store in ChromaDB
├── step5_search_similar.py        # Step 5: Semantic similarity search
├── step6_generate_answer.py       # Step 6: LLM answer generation
├── knowledge_base/                # IT support documents
│   ├── password_reset.md
│   ├── vpn_troubleshooting.md
│   ├── email_issues.md
│   ├── printer_setup.md
│   ├── software_installation.md
│   ├── wifi_connectivity.md
│   └── SAP_troubleshooting.txt
├── chroma_db/                     # Persisted vector database (auto-generated)
├── requirements.txt               # Python dependencies
├── .env                           # API key configuration
└── README.md                      # This file
```

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/it-support-rag.git
cd it-support-rag
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Requirements:**
| Package | Version | Purpose |
|---|---|---|
| `chromadb` | >=0.4.0 | Vector database |
| `sentence-transformers` | >=2.2.0 | Text embeddings |
| `openai` | >=1.0.0 | OpenRouter LLM API |
| `streamlit` | >=1.28.0 | Web UI |
| `python-dotenv` | >=1.0.0 | Environment variables |

### 3. Run the Web UI

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

### 4. Configure Your API Key

1. Click the **☰ menu** (top-left) → **Settings**
2. Enter your **OpenRouter API key** (get one free at [openrouter.ai/keys](https://openrouter.ai/keys))
3. Select an LLM model (start with `llama-3.1-8b-instruct` for testing)
4. Click **Save All Settings**
5. Go back to **Chat** and start asking questions!

### 5. Run Individual Steps (Educational)

Each step is a standalone script you can run to see the pipeline in action:

```bash
python step1_load_documents.py      # See documents load
python step2_chunk_documents.py     # Watch chunking happen
python step3_create_embeddings.py   # Observe embeddings being created
python step4_store_in_vectordb.py   # Store vectors in ChromaDB
python step5_search_similar.py      # Search for relevant chunks
python step6_generate_answer.py     # Generate answers with LLM
```

### 6. Run the Full Pipeline (Terminal)

```bash
python rag_engine.py
```

This starts an interactive chat session in your terminal.

---

## Adding Your Own Documents

1. Add `.md`, `.txt`, or `.pdf` files to the `knowledge_base/` folder
2. Either:
   - **Via UI:** Use the sidebar file uploader on the Chat page
   - **Via code:** Delete the `chroma_db/` folder and run `python rag_engine.py`
3. The knowledge base rebuilds automatically

### Document Format Tips

- Use **Markdown headers** (`#`, `##`, `###`) to structure content
- Keep each section focused on **one topic**
- Include **step-by-step instructions** for IT procedures
- Add **contact information** and **links** where relevant

---

## Customization

### Portal Link & Helpline

In the **Settings page**, you can configure:
- **Self-Service Portal URL** — included in answers about self-service
- **IT Helpline Number** — shown when the knowledge base doesn't have the answer

These are injected into the LLM system prompt dynamically.

### LLM Models

Supported models via OpenRouter:

| Model | Size | Speed | Quality |
|---|---|---|---|
| `meta-llama/llama-3.1-8b-instruct` | 8B | Fast | Good |
| `meta-llama/llama-3.1-70b-instruct` | 70B | Slow | Excellent |
| `anthropic/claude-3.5-sonnet` | - | Medium | Excellent |
| `google/gemini-2.0-flash-001` | - | Fast | Good |
| `mistralai/mistral-7b-instruct` | 7B | Fast | Good |
| `openai/gpt-4o-mini` | - | Fast | Good |

---

## Key Concepts

### Why Chunking Matters
- LLMs have limited context windows (can only read so much text)
- Smaller chunks = more precise retrieval
- Overlap preserves context across chunk boundaries

### Why Embeddings Matter
- Computers can't compare text directly
- Embeddings convert meaning to numbers
- Similar meanings = similar numbers
- This enables fast, semantic search

### Why Vector Databases Matter
- Searching through thousands of vectors is slow without indexing
- ChromaDB optimizes similarity search
- Persistent storage means we don't rebuild every time

---

## Troubleshooting

| Issue | Solution |
|---|---|
| "No documents found" | Ensure `knowledge_base/` folder exists and contains `.md`/`.txt`/`.pdf` files |
| "Error generating answer" | Check your `OPENROUTER_API_KEY` in the Settings page |
| "ChromaDB not found" | Run `python step4_store_in_vectordb.py` first, or let the UI build it |
| Slow first run | The embedding model (~80MB) downloads on first use; subsequent runs are faster |
| Streamlit won't start | Ensure port 8501 is free, or run `streamlit run app.py --server.port 8502` |
| Duplicate key errors | Already fixed — the app uses unique random keys per session |

---

## Architecture Decisions

| Decision | Rationale |
|---|---|
| **ChromaDB** over FAISS | Simpler API, persistent storage out of the box, no compilation needed |
| **all-MiniLM-L6-v2** | Fast, lightweight (80MB), 384-dim embeddings, works on CPU |
| **OpenRouter** over direct API | Access to 100+ models with one API key, free tier available |
| **Streamlit** over Flask/Gradio | Built-in session state, rapid prototyping, multi-page support |
| **6 standalone scripts** | Each step is independently runnable for educational purposes |
| **Runtime API key** | No hardcoded secrets; key stored in session memory only |

---

## Contributing

Contributions are welcome! Ideas:
- Add support for more file types (DOCX, HTML)
- Implement hybrid search (keyword + semantic)
- Add conversation memory for multi-turn chats
- Create a Docker deployment option
- Add evaluation metrics (answer relevance, source accuracy)

---

## License

MIT — Feel free to use this for learning and projects.

---

## Acknowledgments

- [ChromaDB](https://www.trychroma.com/) — Vector database
- [Sentence Transformers](https://www.sbert.net/) — Embedding models
- [OpenRouter](https://openrouter.ai/) — LLM API gateway
- [Streamlit](https://streamlit.io/) — Web app framework
