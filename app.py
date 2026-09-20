"""IT Support RAG Chatbot — navigation entry point."""
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

chat_page = st.Page("pages/chat.py", title="Chat", icon=":material/chat:", default=True)
settings_page = st.Page("pages/settings.py", title="Settings", icon=":material/settings:")
rag_page = st.Page("pages/how_rag_works.py", title="How RAG Works", icon=":material/menu_book:")

nav = st.navigation([chat_page, settings_page, rag_page])

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --bg-primary: #0d1117;
        --bg-secondary: #161b22;
        --bg-tertiary: #1c2333;
        --border-default: #30363d;
        --border-muted: #21262d;
        --text-primary: #e6edf3;
        --text-secondary: #8b949e;
        --text-muted: #484f58;
        --accent-blue: #58a6ff;
        --accent-green: #3fb950;
        --accent-red: #f85149;
        --accent-purple: #bc8cff;
        --accent-orange: #d29922;
        --accent-cyan: #39d2c0;
        --glow-blue: rgba(88,166,255,0.15);
        --glow-green: rgba(63,185,80,0.15);
        --shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
        --shadow-md: 0 4px 12px rgba(0,0,0,0.4);
        --shadow-lg: 0 8px 24px rgba(0,0,0,0.5);
        --radius-sm: 6px;
        --radius-md: 10px;
        --radius-lg: 16px;
    }

    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }

    .stApp {
        background-color: var(--bg-primary);
        color: var(--text-primary);
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }

    /* ── Sidebar ──────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background-color: var(--bg-secondary);
        border-right: 1px solid var(--border-default);
    }
    [data-testid="stSidebar"] [data-testid="stMarkdown"] h1,
    [data-testid="stSidebar"] [data-testid="stMarkdown"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdown"] h3 {
        color: var(--text-primary) !important;
    }

    /* ── Header Bar ───────────────────────────────────────── */
    .header-bar {
        background: linear-gradient(135deg, #161b22 0%, #1c2333 50%, #161b22 100%);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-lg);
        padding: 1.2rem 1.8rem;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: var(--shadow-md);
        animation: slideDown 0.4s ease;
    }
    .header-bar h1 {
        color: var(--text-primary);
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .header-bar p {
        color: var(--text-secondary);
        font-size: 0.82rem;
        margin: 0.3rem 0 0 0;
    }
    .header-right { text-align: right; }

    /* ── Status Badge ─────────────────────────────────────── */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }
    .status-badge::before {
        content: '';
        width: 7px;
        height: 7px;
        border-radius: 50%;
        display: inline-block;
    }
    .status-ok {
        background: var(--glow-green);
        color: var(--accent-green);
        border: 1px solid rgba(63,185,80,0.3);
    }
    .status-ok::before { background: var(--accent-green); animation: pulse-dot 2s infinite; }
    .status-err {
        background: rgba(248,81,73,0.1);
        color: var(--accent-red);
        border: 1px solid rgba(248,81,73,0.3);
    }
    .status-err::before { background: var(--accent-red); }
    .model-badge {
        display: inline-block;
        background: var(--bg-tertiary);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-sm);
        padding: 2px 10px;
        font-size: 0.7rem;
        color: var(--accent-blue);
        font-weight: 500;
        margin-top: 4px;
    }

    /* ── Cards ────────────────────────────────────────────── */
    .card {
        background: var(--bg-secondary);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
        padding: 1.2rem;
        margin-bottom: 0.8rem;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    .card:hover {
        border-color: var(--accent-blue);
        box-shadow: 0 0 16px var(--glow-blue);
    }
    .card h3, .card h4 {
        color: var(--text-primary);
        margin: 0 0 0.5rem 0;
        font-weight: 600;
    }
    .card p {
        color: var(--text-secondary);
        margin: 0;
        font-size: 0.85rem;
        line-height: 1.5;
    }

    /* ── Buttons ──────────────────────────────────────────── */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        border: none;
        border-radius: var(--radius-sm);
        font-weight: 600;
        transition: transform 0.15s, box-shadow 0.15s;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(46,160,67,0.3);
    }

    /* ── Quick Prompt Buttons ─────────────────────────────── */
    .quick-btn {
        background: var(--bg-secondary);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
        padding: 0.8rem 1rem;
        text-align: left;
        cursor: pointer;
        transition: all 0.2s;
        height: 100%;
    }
    .quick-btn:hover {
        border-color: var(--accent-blue);
        background: var(--bg-tertiary);
        box-shadow: 0 0 20px var(--glow-blue);
        transform: translateY(-2px);
    }
    .quick-btn .q-icon {
        font-size: 1.4rem;
        margin-bottom: 0.3rem;
    }
    .quick-btn .q-text {
        color: var(--text-primary);
        font-size: 0.82rem;
        font-weight: 500;
    }

    /* ── Source Cards ─────────────────────────────────────── */
    .source-card {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-default);
        border-left: 3px solid var(--accent-blue);
        border-radius: var(--radius-sm);
        padding: 0.8rem 1rem;
        margin-bottom: 0.5rem;
        font-size: 0.82rem;
    }
    .source-card.high { border-left-color: var(--accent-green); }
    .source-card.medium { border-left-color: var(--accent-orange); }
    .source-card.low { border-left-color: var(--accent-red); }
    .source-card .src-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.4rem;
    }
    .source-card .src-name {
        color: var(--text-primary);
        font-weight: 600;
        font-size: 0.8rem;
    }
    .source-card .src-score {
        background: var(--bg-primary);
        border: 1px solid var(--border-default);
        border-radius: 12px;
        padding: 2px 8px;
        font-size: 0.7rem;
        color: var(--accent-cyan);
        font-weight: 500;
    }
    .source-card .src-section {
        color: var(--accent-purple);
        font-size: 0.72rem;
        margin-bottom: 0.3rem;
    }
    .source-card .src-text {
        color: var(--text-secondary);
        font-size: 0.78rem;
        line-height: 1.4;
        max-height: 60px;
        overflow: hidden;
    }

    /* ── Welcome Screen ───────────────────────────────────── */
    .welcome-box {
        background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-lg);
        padding: 2.5rem;
        text-align: center;
        margin: 2rem 0;
        animation: fadeIn 0.6s ease;
    }
    .welcome-box h2 {
        color: var(--text-primary);
        font-size: 1.6rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
    }
    .welcome-box p {
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin: 0 0 1.5rem 0;
    }
    .welcome-features {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin-top: 1.5rem;
    }
    .welcome-feat {
        text-align: center;
        max-width: 160px;
    }
    .welcome-feat .feat-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    .welcome-feat .feat-title {
        color: var(--text-primary);
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.2rem;
    }
    .welcome-feat .feat-desc {
        color: var(--text-secondary);
        font-size: 0.75rem;
    }

    /* ── Animations ───────────────────────────────────────── */
    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-12px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.3); }
    }
    @keyframes glow-pulse {
        0%, 100% { box-shadow: 0 0 8px var(--glow-blue); }
        50% { box-shadow: 0 0 24px var(--glow-blue), 0 0 48px rgba(88,166,255,0.1); }
    }

    /* ── Streamlit Overrides ──────────────────────────────── */
    .stTabs [data-baseweb="tab"] {
        color: var(--text-secondary);
    }
    .stTabs [aria-selected="true"] {
        color: var(--text-primary);
        border-bottom-color: var(--accent-blue);
    }
    div[data-testid="stExpander"] {
        background: var(--bg-secondary);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
    }
</style>
""", unsafe_allow_html=True)

nav.run()
