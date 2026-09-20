# IT Support RAG Chatbot

> An educational **Advanced RAG (Retrieval-Augmented Generation)** chatbot for IT support.
> Built to teach anyone how modern RAG works — from naive semantic search to hybrid search with reranking.

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

## How Advanced RAG Works (8 Steps)

This project implements a **production-grade** Advanced RAG pipeline — not just naive semantic search, but a multi-stage retrieval system with query rewriting, hybrid search, and cross-encoder reranking.

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     ADVANCED RAG PIPELINE                                │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│  │ Step 1   │  │ Step 2   │  │ Step 3   │  │ Step 4   │                │
│  │ LOAD     │→ │ CHUNK    │→ │ EMBED    │→ │ STORE    │                │
│  │ Docs     │  │ ~1000tok │  │ 384-dim  │  │ ChromaDB │                │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘                │
│                                                                          │
│  ════════════════ BUILD PHASE (one-time) ════════════════               │
│                                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│  │ Step 5a  │  │ Step 5b  │  │ Step 5c  │  │ Step 6   │                │
│  │ REWRITE  │→ │ SEARCH   │→ │ RERANK   │→ │ GENERATE │                │
│  │ Query    │  │ BM25+Sem │  │ Cross-Enc│  │ LLM      │                │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘                │
│                                                                          │
│  ════════════════ QUERY PHASE (each question) ═══════════════           │
└──────────────────────────────────────────────────────────────────────────┘
```

### Build Phase (One-Time)

#### Step 1: Load Documents
**File:** `step1_load_documents.py`

Scans the `knowledge_base/` folder for `.md`, `.txt`, and `.pdf` files. Each file becomes a document object with its text content and filename metadata.

```python
# Supported formats
files = ["password_reset.md", "SAP_troubleshooting.txt", "guide.pdf"]
# Result: [{"filename": "password_reset.md", "content": "# Password Reset..."}]
```

#### Step 2: Token-Aware Chunking
**File:** `step2_chunk_documents.py`

Splits documents into chunks using **tiktoken** for accurate token counting (not character-based). Uses Markdown header-aware splitting to preserve document structure.

```
Why ~1000 tokens per chunk?
├── Too small (< 200 tokens): Loses context, fragmented answers
├── Too large (> 2000 tokens): Dilutes relevant information
└── Sweet spot (~1000 tokens): Enough context, precise retrieval

Why 200-token overlap?
├── Prevents losing context at chunk boundaries
└── Ensures important information spans two chunks
```

```
BEFORE: One 5000-token document about password resets
AFTER:  ~5 chunks of ~1000 tokens each, overlapping by 200 tokens
        Markdown headers preserved: ## -> ### -> ####
```

**Tech:** `tiktoken` (OpenAI's tokenizer) for accurate token counting, regex for header splitting.

#### Step 3: Create Embeddings
**File:** `step3_create_embeddings.py`

Convert each text chunk into a **384-dimensional vector** using the `all-MiniLM-L6-v2` sentence transformer. Similar meanings produce similar vectors.

```
"How do I reset my password?"  →  [0.12, -0.45, 0.78, ...]  (384 numbers)
"I forgot my login"            →  [0.11, -0.43, 0.76, ...]  (very similar!)
"My printer is jammed"         →  [-0.34, 0.89, -0.12, ...] (very different!)
```

**Model:** `all-MiniLM-L6-v2` — 384 dimensions, ~80MB, runs on CPU.

#### Step 4: Store in Vector Database
**File:** `step4_store_in_vectordb.py`

Save all vectors in ChromaDB with **cosine distance** (not L2). Persisted to disk so the knowledge base survives restarts.

```
ChromaDB (Vector Database, cosine distance)
┌─────────────────────────────────────────────────────┐
│ ID               │ Vector       │ Text               │
├─────────────────────────────────────────────────────┤
│ pass_reset.md::0 │ [0.12, ...]  │ "To reset..."     │
│ pass_reset.md::1 │ [0.15, ...]  │ "Try the..."      │
│ vpn_troub.md::0  │ [-0.2, ...]  │ "If VPN fails..." │
│ ...              │ ...          │ ...                │
└─────────────────────────────────────────────────────┘
Score range: 0.0 (identical) → 1.0 (unrelated) — proper cosine semantics
```

### Query Phase (Every Question)

#### Step 5a: Query Rewriting
**File:** `step5a_query_rewriting.py`

Uses the LLM to rewrite vague user queries into clear search terms. Resolves pronouns using chat history. Extracts keywords for BM25 search.

```
User: "it won't work" (follow-up about VPN)
  ↓ LLM rewriting
Rewritten: "VPN connection failing on Windows client"
Keywords: ["vpn", "connection", "failing", "windows", "client"]
```

**Optimization:** Skipped entirely when there's no chat history (first query is usually clear enough), saving 1-3 seconds.

#### Step 5b: Hybrid Search (BM25 + Semantic)
**File:** `step5b_hybrid_search.py`

Combines two complementary search methods using **Reciprocal Rank Fusion (RRF)**:

| Method | Finds | Misses |
|---|---|---|
| **BM25** (keyword) | Exact terms, technical codes, error messages | Synonyms, paraphrases |
| **Semantic** (embeddings) | Meaning, paraphrases, synonyms | Exact keyword matches |
| **Hybrid (RRF)** | Both! | Nothing. |

```
Query: "cannot login to email"
  BM25 finds:     "Email Login Issues" (exact keyword match)
  Semantic finds: "Unable to Access Mailbox" (meaning match)
  RRF fuses:      Both ranked by reciprocal rank score
```

**RRF formula:** `score(d) = sum(1 / (60 + rank_i(d)))` for each ranking system.

**Optimizations:**
- BM25 index cached in memory, rebuilt only when collection changes
- Cosine similarity computed via vectorized numpy matrix operations
- No redundant ChromaDB fetches per query

#### Step 5c: Cross-Encoder Reranking
**File:** `step5c_rerank.py`

Takes the top candidates from hybrid search and reranks them using a **cross-encoder** model. Cross-encoders read the query and document *together* for more accurate relevance scoring.

```
Why cross-encoders are better than embeddings for ranking:
├── Embeddings: Encode query and doc SEPARATELY, then compare
├── Cross-encoder: Reads query + doc TOGETHER in one pass
└── Result: More accurate relevance scores, catches false positives

Model: cross-encoder/ms-marco-MiniLM-L-6-v2
Input: [query, document] pair
Output: relevance score
Retrieval: top-10 candidates → reranked → top-3
```

**Optimization:** Skipped entirely when hybrid search already returns <= 3 candidates.

#### Step 6: Generate Answer
**File:** `step6_generate_answer.py`

Sends the reranked chunks + the user's question (with conversation history) to an LLM for answer generation. Uses streaming so tokens appear in the UI as they're generated.

```
┌─────────────────────────────────────────────────────┐
│ LLM Prompt:                                         │
│                                                     │
│ System: You are an IT support assistant...          │
│                                                     │
│ History: (last 3 conversation turns)                │
│                                                     │
│ Context: [Reranked chunks from Step 5c]             │
│ - "To reset password, go to accounts.company..."   │
│ - "If self-service fails, call IT at ext. 5555..." │
│                                                     │
│ Question: "How do I reset my password?"             │
└─────────────────────────────────────────────────────┘
         ↓ streaming
LLM Answer: "To reset your password, follow these steps:
1. Go to https://accounts.company.com/reset
2. Enter your employee ID
3. Check your email for the reset link
4. Create a new password (min 12 characters)

If self-service fails, call IT Help Desk at ext. 5555."
```

---

## Performance Optimizations

| Optimization | Before | After | Impact |
|---|---|---|---|
| Query rewriting | Always called LLM | Skipped when no chat history | -1 to 3s on first message |
| BM25 index | Rebuilt every query | Cached in memory | -0.3s per query |
| Cosine similarity | Python loop over embeddings | Vectorized numpy matrix ops | -0.2s per query |
| Reranking | Always runs cross-encoder | Skipped when <= 3 candidates | -1s when not needed |
| LLM max_tokens | 1000 | 500 | -1s on generation |
| Chat history in prompt | 5 turns | 3 turns | Shorter prompt, faster |
| Context chunk length | Full text | Truncated to 500 chars | Shorter prompt, faster |
| Answer streaming | Wait for full response | Tokens appear incrementally | Perceived speed: 3x faster |

---

## Live Demo — Web UI

The Streamlit app has **3 pages** accessible from the hamburger menu:

### Chat Page
- Dark-themed chat interface with source citations
- **Quick prompt buttons** for common IT questions (password reset, VPN, printer, WiFi, software, email)
- **Streaming answers** — tokens appear as the LLM generates them
- **Animated pipeline indicator** showing which RAG step is executing
- **Rerank scores** displayed on source cards with color-coded borders (green = high, yellow = medium, red = low)
- Upload new documents directly from the sidebar
- Rebuild knowledge base on demand

### Settings Page
- Enter your OpenRouter API key (stored in session only, never saved to disk)
- Choose from 6 LLM models (Llama, Claude, Gemini, Mistral, GPT-4o)
- Customize portal URL and helpline number injected into answers
- Status dashboard showing API key, model, and portal configuration

### How RAG Works Page
- **Fully animated** step-by-step visualization of the 8-step Advanced RAG pipeline
- Play / Pause / Reset / Speed controls
- Animated data flow packets between pipeline nodes
- Glow effects, progress bars, and expanding info cards
- Step-by-step reference guide with tech badges

---

## Project Structure

```
it-support-rag/
├── app.py                         # Streamlit nav entry + global CSS
├── pages/
│   ├── __init__.py
│   ├── chat.py                    # Chat UI with streaming + source cards
│   ├── settings.py                # Settings page (API key, model, customization)
│   └── how_rag_works.py           # Fully animated RAG pipeline visualization
├── rag_engine.py                  # Advanced RAG pipeline orchestrator
├── step1_load_documents.py        # Step 1: Load .md/.txt/.pdf files
├── step2_chunk_documents.py       # Step 2: Token-aware chunking (~1000 tokens)
├── step3_create_embeddings.py     # Step 3: Sentence-transformers (384-dim)
├── step4_store_in_vectordb.py     # Step 4: ChromaDB storage (cosine distance)
├── step5a_query_rewriting.py      # Step 5a: LLM query expansion/rewriting
├── step5b_hybrid_search.py        # Step 5b: BM25 + semantic with RRF fusion
├── step5c_rerank.py               # Step 5c: Cross-encoder reranking
├── step5_search_similar.py        # Step 5: Basic similarity search (fallback)
├── step6_generate_answer.py       # Step 6: LLM generation with streaming
├── knowledge_base/                # IT support documents (9 files)
│   ├── password_reset.md
│   ├── vpn_troubleshooting.md
│   ├── email_issues.md
│   ├── printer_setup.md
│   ├── software_installation.md
│   ├── wifi_connectivity.md
│   ├── SAP_troubleshooting.txt
│   ├── BYOD_process.txt
│   └── copilot.txt
├── chroma_db/                     # Persisted vector database (auto-generated)
├── requirements.txt               # Python dependencies
├── .env                           # API key configuration (empty by default)
├── .gitignore                     # Excludes .env, chroma_db, __pycache__
└── README.md                      # This file
```

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Decoder4399/IT-Support-RAG.git
cd IT-Support-RAG/it-support-rag
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

| Package | Version | Purpose |
|---|---|---|
| `chromadb` | >=0.4.0 | Vector database |
| `sentence-transformers` | >=2.2.0 | Text embeddings + cross-encoder reranker |
| `openai` | >=1.0.0 | OpenRouter LLM API |
| `streamlit` | >=1.28.0 | Web UI |
| `python-dotenv` | >=1.0.0 | Environment variables |
| `tiktoken` | >=0.5.0 | Token-aware chunking |
| `rank-bm25` | >=0.2.0 | BM25 keyword search |

### 3. Run the Web UI

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

### 4. Configure Your API Key

1. Click the menu (top-right) → **Settings**
2. Enter your **OpenRouter API key** (get one free at [openrouter.ai/keys](https://openrouter.ai/keys))
3. Select an LLM model (start with `llama-3.1-8b-instruct` for testing)
4. Click **Save All Settings**
5. Go back to **Chat** and start asking questions!

### 5. Run Individual Steps (Educational)

Each step is a standalone script you can run to see the pipeline in action:

```bash
python step1_load_documents.py       # See documents load
python step2_chunk_documents.py      # Watch token-aware chunking
python step3_create_embeddings.py    # Observe 384-dim embeddings being created
python step4_store_in_vectordb.py    # Store vectors in ChromaDB with cosine distance
python step5a_query_rewriting.py     # See LLM query rewriting
python step5b_hybrid_search.py       # Watch BM25 + semantic hybrid search
python step5c_rerank.py              # Cross-encoder reranking demo
python step6_generate_answer.py      # Generate answers with LLM
```

### 6. Run the Full Pipeline (Terminal)

```bash
python rag_engine.py
```

This starts an interactive chat session in your terminal with full Advanced RAG pipeline logging.

---

## Adding Your Own Documents

1. Add `.md`, `.txt`, or `.pdf` files to the `knowledge_base/` folder
2. Either:
   - **Via UI:** Use the sidebar file uploader on the Chat page
   - **Via code:** Delete the `chroma_db/` folder and run `python rag_engine.py`
3. The knowledge base rebuilds automatically

### Document Format Tips

- Use **Markdown headers** (`#`, `##`, `###`) to structure content — the chunker splits on these
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

| Model | Size | Speed | Quality | Best For |
|---|---|---|---|---|
| `meta-llama/llama-3.1-8b-instruct` | 8B | Fast | Good | Testing, quick answers |
| `meta-llama/llama-3.1-70b-instruct` | 70B | Slow | Excellent | Complex troubleshooting |
| `anthropic/claude-3.5-sonnet` | - | Medium | Excellent | Detailed explanations |
| `google/gemini-2.0-flash-001` | - | Fast | Good | Fast responses |
| `mistralai/mistral-7b-instruct` | 7B | Fast | Good | Lightweight tasks |
| `openai/gpt-4o-mini` | - | Fast | Good | General purpose |

---

## Key Concepts

### Why Token-Aware Chunking?
- Character-based splitting creates inconsistent chunks (some too small, some too large)
- Token counting with tiktoken matches how LLMs actually read text
- 1000 tokens ≈ 750 words — enough context for meaningful answers

### Why Hybrid Search?
- Semantic search alone misses exact keywords (error codes, part numbers)
- BM25 alone misses synonyms and paraphrases
- RRF (Reciprocal Rank Fusion) combines both rankings without score normalization

### Why Cross-Encoder Reranking?
- Embeddings compare query and document independently (fast but less accurate)
- Cross-encoders read query + document together (slow but more accurate)
- The hybrid approach: retrieve many with embeddings, rerank the best with cross-encoder

### Why Cosine Distance?
- L2 (Euclidean) distance is biased by document length
- Cosine distance measures angle between vectors (direction, not magnitude)
- Score range 0-1 is intuitive: 0 = identical meaning, 1 = unrelated

---

## Troubleshooting

| Issue | Solution |
|---|---|
| "No documents found" | Ensure `knowledge_base/` folder exists and contains `.md`/`.txt`/`.pdf` files |
| "Error generating answer" | Check your API key in the Settings page |
| "ChromaDB not found" | The app builds the KB automatically on first run; or run `python step4_store_in_vectordb.py` |
| Slow first run | The embedding model (~80MB) downloads on first use; subsequent runs are faster |
| Streamlit won't start | Ensure port 8501 is free, or run `streamlit run app.py --server.port 8502` |
| Streaming not working | Ensure your model supports streaming via OpenRouter |
| Reranker slow on first query | Cross-encoder model loads lazily on first rerank call (~3-5s); cached after |

---

## Architecture Decisions

| Decision | Rationale |
|---|---|
| **ChromaDB** over FAISS | Simpler API, persistent storage out of the box, no compilation needed |
| **all-MiniLM-L6-v2** | Fast, lightweight (80MB), 384-dim embeddings, works on CPU |
| **OpenRouter** over direct API | Access to 100+ models with one API key, free tier available |
| **Streamlit** over Flask/Gradio | Built-in session state, rapid prototyping, multi-page support |
| **Token-aware chunking** | Accurate chunk sizes matching LLM tokenizers, not naive character splits |
| **BM25 + Semantic hybrid** | Catches both exact keyword matches and semantic similarity |
| **Cross-encoder reranking** | Higher accuracy ranking after fast initial retrieval |
| **Streaming generation** | Tokens appear incrementally in UI, perceived 3x speed improvement |
| **Cached BM25 index** | Avoids rebuilding index on every query |
| **Runtime API key** | No hardcoded secrets; key stored in session memory only |

---

## Contributing

Contributions are welcome! Ideas:
- Add support for more file types (DOCX, HTML)
- Implement conversation memory with a database backend
- Create a Docker deployment option
- Add evaluation metrics (answer relevance, source accuracy)
- Implement A/B testing between naive and advanced RAG
- Add multilingual support

---

## License

MIT — Feel free to use this for learning and projects.

---

## Acknowledgments

- [ChromaDB](https://www.trychroma.com/) — Vector database
- [Sentence Transformers](https://www.sbert.net/) — Embedding models + cross-encoder rerankers
- [OpenRouter](https://openrouter.ai/) — LLM API gateway
- [Streamlit](https://streamlit.io/) — Web app framework
- [tiktoken](https://github.com/openai/tiktoken) — Fast tokenizer
- [rank-bm25](https://github.com/dorianbrown/rank_bm25) — BM25 keyword search
