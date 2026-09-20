"""Chat page — IT Support RAG chatbot."""
import uuid
import streamlit as st
from rag_engine import RAGEngine

OPENROUTER_MODELS = [
    "meta-llama/llama-3.1-8b-instruct",
    "meta-llama/llama-3.1-70b-instruct",
    "anthropic/claude-3.5-sonnet",
    "google/gemini-2.0-flash-001",
    "mistralai/mistral-7b-instruct",
    "openai/gpt-4o-mini",
]

QUICK_PROMPTS = [
    {"text": "How do I reset my password?", "icon": "\U0001f511"},
    {"text": "My VPN won't connect", "icon": "\U0001f310"},
    {"text": "Printer is showing offline", "icon": "\U0001f5a8\ufe0f"},
    {"text": "WiFi is very slow", "icon": "\U0001f4f6"},
    {"text": "How to install new software?", "icon": "\U0001f4e6"},
    {"text": "Email not sending or receiving", "icon": "\U0001f4e7"},
]


def init_session():
    for k, v in [("messages", []), ("rag_engine", None), ("kb_ready", False),
                  ("pending_question", None), ("api_key", ""), ("llm_model", OPENROUTER_MODELS[0]),
                  ("portal_link", ""), ("helpline", "")]:
        if k not in st.session_state:
            st.session_state[k] = v


def ensure_engine():
    if st.session_state.rag_engine is None:
        st.session_state.rag_engine = RAGEngine()
    if not st.session_state.kb_ready:
        with st.spinner("Building knowledge base..."):
            try:
                st.session_state.rag_engine.build_knowledge_base()
                st.session_state.kb_ready = True
            except Exception as e:
                st.error(f"KB build error: {e}")
                return False
    st.session_state.rag_engine.set_customization(
        st.session_state.portal_link, st.session_state.helpline
    )
    return True


def render_sources(sources, msg_idx):
    if not sources:
        return
    with st.expander(f"\U0001f4da Sources ({len(sources)} documents)", expanded=False):
        for i, src in enumerate(sources, 1):
            fname = src.get("filename", "?")
            rerank = src.get("rerank_score")
            score = src.get("score", 0)
            score_val = rerank if rerank else score
            score_label = "rerank" if rerank else "similarity"
            # Color coding based on score
            if score_val >= 0.7:
                card_cls = "high"
            elif score_val >= 0.4:
                card_cls = "medium"
            else:
                card_cls = "low"
            text = src.get("content", "")
            section = src.get("section", "")
            section_html = f'<div class="src-section">{section}</div>' if section else ""
            preview = text[:300].replace("\n", " ") + ("..." if len(text) > 300 else "")
            st.markdown(
                f'<div class="source-card {card_cls}">'
                f'<div class="src-header">'
                f'<span class="src-name">{i}. {fname}</span>'
                f'<span class="src-score">{score_label}: {score_val:.3f}</span>'
                f'</div>'
                f'{section_html}'
                f'<div class="src-text">{preview}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


def render_welcome():
    """Render the welcome screen when no messages."""
    st.markdown('''
    <div class="welcome-box">
        <h2>\U0001f916 IT Support Chatbot</h2>
        <p>Ask IT questions, get sourced answers powered by Advanced RAG</p>
        <div class="welcome-features">
            <div class="welcome-feat">
                <div class="feat-icon">\U0001f50d</div>
                <div class="feat-title">Hybrid Search</div>
                <div class="feat-desc">BM25 + semantic search with reranking</div>
            </div>
            <div class="welcome-feat">
                <div class="feat-icon">\U0001f4da</div>
                <div class="feat-title">Sourced Answers</div>
                <div class="feat-desc">Every answer cites its documents</div>
            </div>
            <div class="welcome-feat">
                <div class="feat-icon">\U0001f4ac</div>
                <div class="feat-title">Multi-turn Chat</div>
                <div class="feat-desc">Follow-up questions with memory</div>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('<p style="color:#8b949e;font-size:0.85rem;text-align:center;margin-bottom:0.8rem">Try asking:</p>', unsafe_allow_html=True)

    cols = st.columns(3)
    for i, qp in enumerate(QUICK_PROMPTS):
        with cols[i % 3]:
            if st.button(
                f"{qp['icon']}  {qp['text']}",
                key=f"q{i}",
                use_container_width=True,
            ):
                st.session_state.pending_question = qp["text"]
                st.rerun()


def render():
    init_session()

    api_ok = bool(st.session_state.api_key)
    status_cls = "status-ok" if api_ok else "status-err"
    status_txt = "API Ready" if api_ok else "No API Key"
    model_txt = st.session_state.llm_model.split("/")[-1] if st.session_state.llm_model else "---"

    st.markdown(
        '<div class="header-bar">'
        '<div>'
        '<h1>\U0001f916 IT Support Chatbot</h1>'
        '<p>Advanced RAG \u2014 Query Rewriting + Hybrid Search + Reranking</p>'
        '</div>'
        '<div class="header-right">'
        f'<span class="status-badge {status_cls}">{status_txt}</span>'
        f'<div class="model-badge">{model_txt}</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown('<h3 style="color:#e6edf3;margin:0 0 0.5rem 0">\U0001f4da Knowledge Base</h3>', unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "Upload documents",
            type=["pdf", "txt", "md"],
            accept_multiple_files=True,
            help="Add PDF, TXT, or MD files to the knowledge base",
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("\U0001f4e4 Upload", use_container_width=True):
                if uploaded and st.session_state.rag_engine:
                    with st.spinner("Uploading & rebuilding..."):
                        try:
                            n = st.session_state.rag_engine.add_documents_to_knowledge_base(uploaded)
                            st.session_state.kb_ready = True
                            st.success(f"+{n} files")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
        with c2:
            if st.button("\U0001f504 Rebuild", use_container_width=True):
                if st.session_state.rag_engine:
                    with st.spinner("Rebuilding..."):
                        try:
                            st.session_state.rag_engine.build_knowledge_base()
                            st.session_state.kb_ready = True
                            st.success("Done!")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

        st.markdown('<hr style="border-color:#30363d;margin:1rem 0">', unsafe_allow_html=True)
        if st.button("\U0001f5d1\ufe0f Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.markdown(
            '<p style="color:#484f58;font-size:0.72rem;margin-top:1rem;text-align:center">'
            'Use Settings (top-right menu) to configure API key and model.</p>',
            unsafe_allow_html=True,
        )

    if not ensure_engine():
        return

    if not api_ok:
        st.warning("\u26a0\ufe0f Open the **Settings** page (click \u2630 menu at top-right) to add your OpenRouter API key.")

    if not st.session_state.messages:
        render_welcome()
    else:
        for idx, msg in enumerate(st.session_state.messages):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if "sources" in msg:
                    render_sources(msg["sources"], idx)

    prompt = st.session_state.pop("pending_question", None)
    if not prompt:
        prompt = st.chat_input("Ask about IT support...")

    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("\U0001f50d Rewriting query, searching, reranking..."):
                try:
                    result = st.session_state.rag_engine.ask(
                        prompt,
                        api_key=st.session_state.api_key,
                        model=st.session_state.llm_model,
                        chat_history=st.session_state.messages,
                        stream=True,
                    )
                    sources = result["sources"]

                    # Stream the answer token by token
                    answer = st.write_stream(result["answer"])

                    render_sources(sources, len(st.session_state.messages))

                    st.session_state.messages.append({
                        "role": "assistant", "content": answer, "sources": sources,
                    })
                except Exception as e:
                    err = f"Error: {e}"
                    st.error(err)
                    st.session_state.messages.append({"role": "assistant", "content": err})


render()
