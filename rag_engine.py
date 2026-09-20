"""
RAG ENGINE: ADVANCED RAG PIPELINE
Combines all steps into a complete Advanced RAG pipeline:
  Build:  Load → Chunk (token-aware) → Embed → Store (cosine)
  Query:  Rewrite → Hybrid Search → Rerank → Generate (with memory)

Supports dynamic document loading, custom portal/helpline settings,
conversation memory, and runtime API key / model configuration.
"""

from pathlib import Path
from step1_load_documents import load_documents
from step2_chunk_documents import chunk_documents
from step3_create_embeddings import create_embeddings, EMBEDDING_MODEL
from step4_store_in_vectordb import store_in_vectordb, load_collection
from step5_search_similar import search_similar_chunks
from step5a_query_rewriting import rewrite_query
from step5b_hybrid_search import hybrid_search
from step5c_rerank import rerank_chunks
from step6_generate_answer import generate_answer
from sentence_transformers import SentenceTransformer


DEFAULT_SYSTEM_PROMPT = """You are a helpful IT Support Assistant. You answer questions about
IT issues like password resets, VPN problems, email issues, printer setup,
software installation, and WiFi connectivity.

IMPORTANT RULES:
1. ONLY answer based on the provided context documents.
2. If the context does not contain the answer, say you do not have enough information.
3. Be concise and actionable - users want step-by-step solutions.
4. When referencing a source, mention which document it came from.
5. Use conversation history to understand follow-up questions.
{custom_section}
"""


class RAGEngine:
    """Advanced RAG pipeline with query rewriting, hybrid search, and reranking."""

    def __init__(self):
        self.embedding_model = None
        self.collection = None
        self.portal_link = ""
        self.helpline = ""

    def set_customization(self, portal_link="", helpline=""):
        """Set custom portal link and helpline number for the system prompt."""
        self.portal_link = portal_link.strip()
        self.helpline = helpline.strip()

    def _get_system_prompt(self):
        """Build the system prompt with optional custom sections."""
        extras = []
        if self.portal_link:
            extras.append(f"- The self-service portal is available at: {self.portal_link}")
        if self.helpline:
            extras.append(f"- The IT helpdesk helpline number is: {self.helpline}")
            extras.append("- If you cannot answer from context, direct the user to call the helpline.")
        custom_section = ""
        if extras:
            custom_section = "\nADDITIONAL INFORMATION:\n" + "\n".join(extras)
        return DEFAULT_SYSTEM_PROMPT.format(custom_section=custom_section)

    def build_knowledge_base(self, data_dir="knowledge_base"):
        """Build the knowledge base (Steps 1-4)."""
        print("=" * 60)
        print("Building Knowledge Base (Advanced RAG)")
        print("=" * 60)

        print(f"\n[Step 1] Loading documents from {data_dir}...")
        docs = load_documents(data_dir)
        if not docs:
            raise ValueError(f"No documents found in '{data_dir}/' folder.")
        print(f"  Loaded {len(docs)} documents")

        print("\n[Step 2] Chunking documents (token-aware, markdown-aware)...")
        chunks = chunk_documents(docs)
        print(f"  Created {len(chunks)} chunks")

        print("\n[Step 3] Creating embeddings...")
        chunks, self.embedding_model = create_embeddings(chunks)
        print(f"  Created {len(chunks)} embeddings")

        print("\n[Step 4] Storing in ChromaDB (cosine distance)...")
        self.collection = store_in_vectordb(chunks)
        print(f"  Stored {self.collection.count()} chunks")

        print("\n" + "=" * 60)
        print("Knowledge base built successfully!")
        print("=" * 60)

    def add_documents_to_knowledge_base(self, uploaded_files, data_dir="knowledge_base"):
        """Save uploaded files and rebuild the knowledge base."""
        data_path = Path(data_dir)
        data_path.mkdir(parents=True, exist_ok=True)

        saved_count = 0
        for uploaded_file in uploaded_files:
            if hasattr(uploaded_file, "name") and hasattr(uploaded_file, "getvalue"):
                file_name = uploaded_file.name
                file_content = uploaded_file.getvalue()
            elif isinstance(uploaded_file, dict):
                file_name = uploaded_file["name"]
                file_content = uploaded_file["content"]
            else:
                continue
            file_path = data_path / file_name
            file_path.write_bytes(file_content)
            saved_count += 1
            print(f"  Saved: {file_name}")

        if saved_count == 0:
            return 0

        print(f"\nRebuilding knowledge base with {saved_count} new file(s)...")
        self.build_knowledge_base(data_dir)
        return saved_count

    def load_existing_knowledge_base(self):
        """Load an existing knowledge base from ChromaDB."""
        if self.embedding_model is None:
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        try:
            self.collection = load_collection()
            print(f"Loaded existing knowledge base ({self.collection.count()} chunks)")
        except Exception:
            print("No existing knowledge base found. Building new one...")
            self.build_knowledge_base()

    def ask(
        self,
        question,
        top_k=3,
        api_key="",
        model="meta-llama/llama-3.1-8b-instruct",
        chat_history=None,
    ):
        """
        Ask a question using the Advanced RAG pipeline.

        Pipeline: Rewrite → Hybrid Search → Rerank → Generate

        Args:
            question: The user's question
            top_k: Number of chunks to return after reranking
            api_key: OpenRouter API key
            model: LLM model name
            chat_history: Previous conversation turns

        Returns:
            dict with answer, sources, query, and pipeline metadata
        """
        if self.collection is None:
            self.load_existing_knowledge_base()

        pipeline_info = {}

        # Step 5a: Query Rewriting
        print(f"\n[Step 5a] Rewriting query...")
        rewritten = rewrite_query(
            question, chat_history=chat_history,
            api_key=api_key, model=model,
        )
        print(f"  Original: {rewritten['original']}")
        print(f"  Rewritten: {rewritten['rewritten']}")
        print(f"  Keywords: {rewritten['keywords']}")
        pipeline_info["rewritten_query"] = rewritten["rewritten"]
        pipeline_info["keywords"] = rewritten["keywords"]

        # Step 5b: Hybrid Search (semantic + BM25)
        print(f"\n[Step 5b] Hybrid search (semantic + keyword)...")
        candidates = hybrid_search(
            rewritten["rewritten"],
            keywords=rewritten["keywords"],
            top_k=top_k * 3,
            model=self.embedding_model,
        )
        print(f"  Found {len(candidates)} candidates")

        # Step 5c: Rerank with cross-encoder
        print(f"\n[Step 5c] Reranking with cross-encoder...")
        final_chunks = rerank_chunks(
            rewritten["rewritten"],
            candidates,
            top_k=top_k,
        )
        print(f"  Reranked to {len(final_chunks)} chunks")
        for i, chunk in enumerate(final_chunks, 1):
            print(f"    {i}. {chunk['filename']} (rerank_score: {chunk.get('rerank_score', 'N/A')})")

        # Step 6: Generate Answer (with conversation history)
        print(f"\n[Step 6] Generating answer...")
        system_prompt = self._get_system_prompt()
        answer = generate_answer(
            question, final_chunks,
            system_prompt=system_prompt,
            api_key=api_key,
            model=model,
            chat_history=chat_history,
        )
        print(f"  Generated answer ({len(answer)} characters)")

        return {
            "answer": answer,
            "sources": final_chunks,
            "query": question,
            "pipeline": pipeline_info,
        }


if __name__ == "__main__":
    engine = RAGEngine()
    engine.build_knowledge_base()
    while True:
        try:
            question = input("\nYour question: ").strip()
            if question.lower() in ("quit", "exit", "q"):
                break
            if not question:
                continue
            result = engine.ask(question)
            print("\n" + "=" * 60)
            print(result["answer"])
            print("=" * 60)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
