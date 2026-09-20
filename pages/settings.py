# Settings page - accessible from hamburger menu
import streamlit as st

st.set_page_config(page_title="Settings", page_icon=":material/settings:", layout="wide")

OPENROUTER_MODELS = [
    "meta-llama/llama-3.1-8b-instruct",
    "meta-llama/llama-3.1-70b-instruct",
    "anthropic/claude-3.5-sonnet",
    "google/gemini-2.0-flash-001",
    "mistralai/mistral-7b-instruct",
    "openai/gpt-4o-mini",
]

st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .block-container { padding-top: 2rem; max-width: 800px; margin: 0 auto; }
    .setting-card {
        background: #161b22; border: 1px solid #30363d; border-radius: 12px;
        padding: 1.5rem; margin-bottom: 1rem;
    }
    .setting-card h3 {
        color: #e6edf3; font-size: 1.1rem; font-weight: 600; margin: 0 0 1rem 0;
        padding-bottom: 0.5rem; border-bottom: 1px solid #21262d;
    }
    .setting-desc { color: #8b949e; font-size: 0.82rem; margin-top: 0.3rem; }
</style>
""", unsafe_allow_html=True)

# ── Initialize session state ───────────────────────────────────────
for k, v in [("api_key", ""), ("llm_model", OPENROUTER_MODELS[0]),
              ("portal_link", ""), ("helpline", "")]:
    if k not in st.session_state:
        st.session_state[k] = v


st.markdown("# :gear: Settings")
st.markdown("Configure your IT Support Chatbot. API key is required to start chatting.")

st.divider()

# ── API Configuration ──────────────────────────────────────────────
st.markdown('<div class="setting-card"><h3>API Configuration</h3></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    api_key = st.text_input(
        "OpenRouter API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="sk-or-v1-...",
        help="Get a free key at https://openrouter.ai/keys",
    )
    st.markdown('<p class="setting-desc">Required. Your key is stored in memory only for this session.</p>', unsafe_allow_html=True)

with col2:
    model = st.selectbox(
        "LLM Model",
        OPENROUTER_MODELS,
        index=OPENROUTER_MODELS.index(st.session_state.llm_model)
        if st.session_state.llm_model in OPENROUTER_MODELS else 0,
        help="Select which language model to use for generating answers",
    )
    st.markdown('<p class="setting-desc">Larger models are smarter but slower. Start with 8b for testing.</p>', unsafe_allow_html=True)

st.divider()

# ── Customization ──────────────────────────────────────────────────
st.markdown('<div class="setting-card"><h3>Customization</h3></div>', unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    portal = st.text_input(
        "Self-Service Portal URL",
        value=st.session_state.portal_link,
        placeholder="https://support.company.com",
        help="The chatbot will direct users to this link for self-service",
    )
    st.markdown('<p class="setting-desc">Included in answers when users ask about self-service options.</p>', unsafe_allow_html=True)

with col4:
    helpline = st.text_input(
        "IT Helpline Number",
        value=st.session_state.helpline,
        placeholder="ext. 5555 or 1-800-XXX-XXXX",
        help="The chatbot will mention this number when it cannot answer from context",
    )
    st.markdown('<p class="setting-desc">Shown to users when the knowledge base does not have the answer.</p>', unsafe_allow_html=True)

st.divider()

# ── Save button ────────────────────────────────────────────────────
if st.button("Save All Settings", type="primary", use_container_width=True):
    st.session_state.api_key = api_key
    st.session_state.llm_model = model
    st.session_state.portal_link = portal
    st.session_state.helpline = helpline

    # Update the RAG engine if it exists
    if "rag_engine" in st.session_state and st.session_state.rag_engine:
        st.session_state.rag_engine.set_customization(portal, helpline)

    st.success("Settings saved! Go to Chat to start asking questions.")

# ── Current status ─────────────────────────────────────────────────
st.divider()
st.markdown("### Current Status")

status_cols = st.columns(3)
with status_cols[0]:
    key_status = ":green[Configured]" if st.session_state.api_key else ":red[Not set]"
    st.markdown(f"**API Key:** {key_status}")
with status_cols[1]:
    st.markdown(f"**Model:** `{st.session_state.llm_model.split('/')[-1]}`")
with status_cols[2]:
    has_portal = ":green[Yes]" if st.session_state.portal_link else ":gray[No]"
    st.markdown(f"**Portal Link:** {has_portal}")
