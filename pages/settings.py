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
    .block-container { padding-top: 2rem; max-width: 860px; margin: 0 auto; }
    .settings-header {
        text-align: center; margin-bottom: 2rem;
    }
    .settings-header h2 { color: #e6edf3; font-size: 1.6rem; font-weight: 700; margin: 0; }
    .settings-header p { color: #8b949e; font-size: 0.88rem; margin: 0.3rem 0 0 0; }
    .s-card {
        background: linear-gradient(135deg, #161b22 0%, #1c2333 100%);
        border: 1px solid #30363d; border-radius: 14px;
        padding: 1.5rem; margin-bottom: 1rem;
        transition: border-color 0.2s;
    }
    .s-card:hover { border-color: #484f58; }
    .s-card-title {
        display: flex; align-items: center; gap: 0.5rem;
        color: #e6edf3; font-size: 1rem; font-weight: 600;
        margin: 0 0 1rem 0; padding-bottom: 0.6rem;
        border-bottom: 1px solid #21262d;
    }
    .s-card-title .s-icon { font-size: 1.2rem; }
    .s-desc { color: #8b949e; font-size: 0.78rem; margin-top: 0.3rem; }
    .status-grid {
        display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;
        margin-top: 1rem;
    }
    .status-item {
        background: #0d1117; border: 1px solid #30363d; border-radius: 10px;
        padding: 0.8rem 1rem; text-align: center;
    }
    .status-item .s-label { color: #8b949e; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; }
    .status-item .s-value { color: #e6edf3; font-size: 0.9rem; font-weight: 600; margin-top: 0.2rem; }
    .status-item .s-value.ok { color: #3fb950; }
    .status-item .s-value.err { color: #f85149; }
    .status-item .s-value.neutral { color: #8b949e; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
for k, v in [("api_key", ""), ("llm_model", OPENROUTER_MODELS[0]),
              ("portal_link", ""), ("helpline", "")]:
    if k not in st.session_state:
        st.session_state[k] = v

st.markdown('''
<div class="settings-header">
<h2>\u2699\ufe0f Settings</h2>
<p>Configure your IT Support Chatbot. API key is required to start chatting.</p>
</div>
''', unsafe_allow_html=True)

# API Configuration
st.markdown('''
<div class="s-card">
<div class="s-card-title"><span class="s-icon">\U0001f511</span> API Configuration</div>
</div>
''', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    api_key = st.text_input(
        "OpenRouter API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="sk-or-v1-...",
        help="Get a free key at https://openrouter.ai/keys",
    )
    st.markdown('<p class="s-desc">\u2714\ufe0f Required. Stored in memory only for this session.</p>', unsafe_allow_html=True)
with col2:
    model = st.selectbox(
        "LLM Model",
        OPENROUTER_MODELS,
        index=OPENROUTER_MODELS.index(st.session_state.llm_model)
        if st.session_state.llm_model in OPENROUTER_MODELS else 0,
        help="Select which language model to use for generating answers",
    )
    st.markdown('<p class="s-desc">\U0001f9e0 Larger models are smarter but slower. Start with 8b for testing.</p>', unsafe_allow_html=True)

st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)

# Customization
st.markdown('''
<div class="s-card">
<div class="s-card-title"><span class="s-icon">\U0001f3a8</span> Customization</div>
</div>
''', unsafe_allow_html=True)

col3, col4 = st.columns(2)
with col3:
    portal = st.text_input(
        "Self-Service Portal URL",
        value=st.session_state.portal_link,
        placeholder="https://support.company.com",
        help="The chatbot will direct users to this link for self-service",
    )
    st.markdown('<p class="s-desc">\U0001f310 Included in answers about self-service options.</p>', unsafe_allow_html=True)
with col4:
    helpline = st.text_input(
        "IT Helpline Number",
        value=st.session_state.helpline,
        placeholder="ext. 5555 or 1-800-XXX-XXXX",
        help="The chatbot will mention this number when it cannot answer from context",
    )
    st.markdown('<p class="s-desc">\U0001f4de Shown when the knowledge base doesn\'t have the answer.</p>', unsafe_allow_html=True)

st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)

# Save button
if st.button("\U0001f4be  Save All Settings", type="primary", use_container_width=True):
    st.session_state.api_key = api_key
    st.session_state.llm_model = model
    st.session_state.portal_link = portal
    st.session_state.helpline = helpline

    if "rag_engine" in st.session_state and st.session_state.rag_engine:
        st.session_state.rag_engine.set_customization(portal, helpline)

    st.success("\u2705 Settings saved! Go to Chat to start asking questions.")

st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)

# Current Status
st.markdown('''
<div class="s-card">
<div class="s-card-title"><span class="s-icon">\U0001f4ca</span> Current Status</div>
</div>
''', unsafe_allow_html=True)

key_ok = st.session_state.api_key != ""
model_short = st.session_state.llm_model.split("/")[-1] if st.session_state.llm_model else "---"
has_portal = st.session_state.portal_link != ""

st.markdown(f'''
<div class="status-grid">
    <div class="status-item">
        <div class="s-label">API Key</div>
        <div class="s-value {"ok" if key_ok else "err"}">{"Configured" if key_ok else "Not Set"}</div>
    </div>
    <div class="status-item">
        <div class="s-label">Model</div>
        <div class="s-value neutral">{model_short}</div>
    </div>
    <div class="status-item">
        <div class="s-label">Portal Link</div>
        <div class="s-value {"ok" if has_portal else "neutral"}">{"Yes" if has_portal else "No"}</div>
    </div>
</div>
''', unsafe_allow_html=True)
