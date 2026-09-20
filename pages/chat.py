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
    "How do I reset my password?",
    "My VPN won\'t connect",
    "Printer is showing offline",
    "WiFi is very slow",
    "How to install new software?",
    "Email not sending or receiving",
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
    with st.expander(f"Sources ({len(sources)} documents)", expanded=False):
        for i, src in enumerate(sources, 1):
            fname = src.get("filename", "?")
            rerank = src.get("rerank_score")
            score = src.get("score", 0)
            score_display = f"rerank: `{rerank:.3f}`" if rerank else f"similarity: `{score:.3f}`"
            text = src.get("content", "")
            section = src.get("section", "")
            section_display = f" | Section: {section}" if section else ""
            st.markdown(f"**{i}. {fname}**{section_display} -- {score_display}", unsafe_allow_html=True)
            st.text_area(
                "preview", value=text[:400] + ("..." if len(text) > 400 else ""),
                height=80, disabled=True,
                key=f"m{msg_idx}_s{i}_{uuid.uuid4().hex[:5]}",
            )


def render():
    init_session()

    api_ok = bool(st.session_state.api_key)
    status_cls = "status-ok" if api_ok else "status-err"
    status_txt = "API Ready" if api_ok else "No API Key"
    model_txt = st.session_state.llm_model.split("/")[-1] if st.session_state.llm_model else "---"

    st.markdown(
        f'<div class="header-bar">'
        f'<div><h1>IT Support Chatbot</h1>'
        f'<p>Advanced RAG -- Query Rewriting + Hybrid Search + Reranking</p></div>'
        f'<div style="text-align:right;">'
        f'<span class="status-badge {status_cls}">{status_txt}</span>'
        f'<div style="color:#8b949e;font-size:0.72rem;margin-top:3px;">{model_txt}</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Knowledge Base")
        uploaded = st.file_uploader(
            "Upload documents",
            type=["pdf", "txt", "md"],
            accept_multiple_files=True,
            help="Add PDF, TXT, or MD files to the knowledge base",
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Upload", use_container_width=True):
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
            if st.button("Rebuild", use_container_width=True):
                if st.session_state.rag_engine:
                    with st.spinner("Rebuilding..."):
                        try:
                            st.session_state.rag_engine.build_knowledge_base()
                            st.session_state.kb_ready = True
                            st.success("Done!")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

        st.divider()
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.divider()
        st.caption("Use the Settings page (top-right menu) to configure API key and model.")

    if not ensure_engine():
        return

    if not api_ok:
        st.info("Open the **Settings** page (click the menu at top-right) to add your OpenRouter API key.")

    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "sources" in msg:
                render_sources(msg["sources"], idx)

    if not st.session_state.messages:
        st.markdown("**Try asking:**")
        cols = st.columns(3)
        for i, qp in enumerate(QUICK_PROMPTS):
            with cols[i % 3]:
                if st.button(qp, key=f"q{i}", use_container_width=True):
                    st.session_state.pending_question = qp
                    st.rerun()

    prompt = st.session_state.pop("pending_question", None)
    if not prompt:
        prompt = st.chat_input("Ask about IT support...")

    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Rewriting query, searching, reranking, generating..."):
                try:
                    result = st.session_state.rag_engine.ask(
                        prompt,
                        api_key=st.session_state.api_key,
                        model=st.session_state.llm_model,
                        chat_history=st.session_state.messages,
                    )
                    answer = result["answer"]
                    sources = result["sources"]

                    st.markdown(answer)
                    render_sources(sources, len(st.session_state.messages))

                    st.session_state.messages.append({
                        "role": "assistant", "content": answer, "sources": sources,
                    })
                except Exception as e:
                    err = f"Error: {e}"
                    st.error(err)
                    st.session_state.messages.append({"role": "assistant", "content": err})


render()
