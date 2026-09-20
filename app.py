"""IT Support RAG Chatbot — navigation entry point."""
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

chat_page = st.Page("pages/chat.py", title="Chat", icon=":material/chat:", default=True)
settings_page = st.Page("pages/settings.py", title="Settings", icon=":material/settings:")
rag_page = st.Page("pages/how_rag_works.py", title="How RAG Works", icon=":material/menu_book:")

nav = st.navigation([chat_page, settings_page, rag_page])

st.markdown(
    "<style>"
    ".stApp { background-color: #0e1117; }"
    ".block-container { padding-top: 1rem; }"
    ".header-bar {"
    "  background: linear-gradient(135deg, #1a1f36 0%, #0d1117 100%);"
    "  border: 1px solid #30363d; border-radius: 12px;"
    "  padding: 1rem 1.5rem; margin-bottom: 1rem;"
    "  display: flex; align-items: center; justify-content: space-between;"
    "}"
    ".header-bar h1 { color: #e6edf3; font-size: 1.4rem; font-weight: 700; margin: 0; }"
    ".header-bar p { color: #8b949e; font-size: 0.8rem; margin: 0.2rem 0 0 0; }"
    ".status-badge {"
    "  display: inline-flex; align-items: center; padding: 4px 12px;"
    "  border-radius: 20px; font-size: 0.75rem; font-weight: 600;"
    "}"
    ".status-ok { background: #23863622; color: #3fb950; border: 1px solid #238636; }"
    ".status-err { background: #da363322; color: #f85149; border: 1px solid #da3633; }"
    "[data-testid=stSidebar] { background-color: #161b22; border-right: 1px solid #30363d; }"
    "</style>",
    unsafe_allow_html=True,
)

nav.run()
