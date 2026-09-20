# How RAG Works - Animated step-by-step explanation (Advanced RAG)
import time
import streamlit as st

st.set_page_config(page_title="How RAG Works", page_icon=":material/menu_book:", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .block-container { padding-top: 2rem; max-width: 900px; margin: 0 auto; }
    .step-card {
        background: #161b22; border: 1px solid #30363d; border-radius: 12px;
        padding: 1.2rem 1.5rem; margin-bottom: 0.8rem;
        opacity: 0; transform: translateY(20px);
        animation: fadeSlideIn 0.5s ease forwards;
    }
    .step-card.done { border-left: 4px solid #3fb950; }
    .step-card.active { border-left: 4px solid #58a6ff; box-shadow: 0 0 20px #58a6ff22; }
    .step-card.waiting { border-left: 4px solid #30363d; opacity: 0.4; }
    .step-card .step-num {
        display: inline-block; background: #21262d; border: 1px solid #444;
        border-radius: 8px; padding: 2px 10px; font-size: 0.75rem;
        color: #8b949e; font-weight: 600; margin-bottom: 0.4rem;
    }
    .step-card.active .step-num { background: #0d419d; color: #58a6ff; border-color: #58a6ff; }
    .step-card.done .step-num { background: #238636; color: #3fb950; border-color: #3fb950; }
    .step-card h4 { color: #e6edf3; font-size: 1rem; margin: 0.3rem 0; font-weight: 600; }
    .step-card p { color: #8b949e; font-size: 0.85rem; margin: 0; line-height: 1.5; }
    .progress-bar { background: #21262d; border-radius: 10px; height: 6px; margin: 1rem 0; overflow: hidden; }
    .progress-fill { height: 100%; border-radius: 10px; transition: width 0.8s ease; background: linear-gradient(90deg, #58a6ff, #3fb950); }
    .arrow-down { text-align: center; color: #30363d; font-size: 1.2rem; margin: -0.2rem 0; animation: pulse 1.5s infinite; }
    @keyframes fadeSlideIn { to { opacity: 1; transform: translateY(0); } }
    @keyframes pulse { 0%, 100% { opacity: 0.4; } 50% { opacity: 1; } }
    .intro-box {
        background: linear-gradient(135deg, #1a1f36 0%, #0d1117 100%);
        border: 1px solid #30363d; border-radius: 12px;
        padding: 1.5rem; margin-bottom: 1.5rem; text-align: center;
    }
    .intro-box h2 { color: #e6edf3; font-size: 1.5rem; margin: 0; }
    .intro-box p { color: #8b949e; font-size: 0.9rem; margin: 0.5rem 0 0 0; }
</style>
""", unsafe_allow_html=True)

STEPS = [
    {"num": 1, "title": "Load Documents", "icon": ":open_file_folder:",
     "desc": "Read markdown, PDF, and text files from the knowledge base folder.",
     "detail": "The loader scans knowledge_base/ for .md, .txt, and .pdf files."},
    {"num": 2, "title": "Chunk (Token-Aware)", "icon": ":scissors:",
     "desc": "Split into token-aware chunks (~1000 tokens) respecting Markdown headers.",
     "detail": "Uses tiktoken for accurate token counting. Splits on Markdown headers to preserve structure. 200-token overlap preserves context."},
    {"num": 3, "title": "Create Embeddings", "icon": ":bar_chart:",
     "desc": "Convert each chunk into a 384-dimensional vector using all-MiniLM-L6-v2.",
     "detail": "Similar meanings produce similar numbers, enabling semantic search."},
    {"num": 4, "title": "Store in Vector DB", "icon": ":floppy_disk:",
     "desc": "Save vectors in ChromaDB with cosine distance for proper similarity scoring.",
     "detail": "Cosine similarity gives proper 0-1 scores instead of raw L2 distance."},
    {"num": 5, "title": "Rewrite Query", "icon": ":pencil2:",
     "desc": "Use LLM to rewrite ambiguous queries, resolve pronouns, and extract keywords.",
     "detail": "Transforms vague queries into clear search terms. Resolves 'it', 'that' using chat history."},
    {"num": 6, "title": "Hybrid Search", "icon": ":mag:",
     "desc": "Combine BM25 keyword search with semantic search using Reciprocal Rank Fusion.",
     "detail": "BM25 catches exact keyword matches. Semantic search catches meaning. RRF (k=60) fuses both."},
    {"num": 7, "title": "Rerank (Cross-Encoder)", "icon": ":trophy:",
     "desc": "Rerank top-10 candidates using a cross-encoder that reads query + document together.",
     "detail": "Cross-encoders are more accurate than bi-encoders. Retrieve 10, keep top 3."},
    {"num": 8, "title": "Generate Answer", "icon": ":robot_face:",
     "desc": "Send reranked chunks + chat history to LLM for a sourced, conversational answer.",
     "detail": "The LLM receives system prompt, last 5 conversation turns, and reranked context."},
]

TOTAL_STEPS = len(STEPS)
DELAY = 1.2

if "anim_step" not in st.session_state:
    st.session_state.anim_step = -1
if "animating" not in st.session_state:
    st.session_state.animating = False
if "anim_done" not in st.session_state:
    st.session_state.anim_done = False

def render_step(step, state):
    cls = {"done": "done", "active": "active"}.get(state, "waiting")
    badge = {"done": ":white_check_mark: Done", "active": ":hourglass_flowing_sand: In progress..."}.get(state, "")
    html = f'''<div class="step-card {cls}">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <span class="step-num">Step {step["num"]}</span>
            <span style="font-size:0.75rem;color:#8b949e;">{badge}</span>
        </div>
        <h4>{step["icon"]} {step["title"]}</h4>
        <p>{step["desc"]}</p>
    </div>'''
    st.markdown(html, unsafe_allow_html=True)
    if state in ("active", "done"):
        with st.expander(f"Learn more about Step {step['num']}", expanded=(state == "active")):
            st.markdown(step["detail"])

def render_all(current, done=False):
    for i, step in enumerate(STEPS):
        state = "done" if i < current or (i == current and done) else ("active" if i == current else "waiting")
        render_step(step, state)
        if i < TOTAL_STEPS - 1:
            op = "1" if i < current or i == current else "0.2"
            st.markdown(f'''<div class="arrow-down" style="opacity:{op}">&#9660;</div>''', unsafe_allow_html=True)

def render_progress(idx):
    pct = ((idx + 1) / TOTAL_STEPS) * 100
    st.markdown(f'''<div class="progress-bar"><div class="progress-fill" style="width:{pct}%"></div></div>
    <p style="text-align:center;color:#8b949e;font-size:0.8rem;margin:0;">Step {idx+1} of {TOTAL_STEPS} -- {pct:.0f}%</p>''', unsafe_allow_html=True)

st.markdown('''<div class="intro-box"><h2>How Advanced RAG Works</h2>
<p>Query Rewriting + Hybrid Search + Cross-Encoder Reranking -- 8 steps.</p></div>''', unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    play = st.button("Play Animation", type="primary", use_container_width=True, disabled=st.session_state.animating)
with c2:
    reset = st.button("Reset", use_container_width=True)
with c3:
    show_all = st.button("Show All Steps", use_container_width=True)

if reset:
    st.session_state.anim_step = -1
    st.session_state.animating = False
    st.session_state.anim_done = False
    st.rerun()
if show_all:
    st.session_state.anim_step = TOTAL_STEPS - 1
    st.session_state.animating = False
    st.session_state.anim_done = True
    st.rerun()
if play and not st.session_state.animating:
    st.session_state.anim_step = -1
    st.session_state.animating = True
    st.session_state.anim_done = False
    st.rerun()

if st.session_state.animating:
    nxt = st.session_state.anim_step + 1
    if nxt < TOTAL_STEPS:
        st.session_state.anim_step = nxt
        render_all(nxt)
        render_progress(nxt)
        time.sleep(DELAY)
        st.rerun()
    else:
        st.session_state.animating = False
        st.session_state.anim_done = True
        st.rerun()
elif st.session_state.anim_done:
    render_all(TOTAL_STEPS - 1, done=True)
    render_progress(TOTAL_STEPS - 1)
    st.success("Animation complete! The Advanced RAG pipeline has all 8 steps.")
    st.balloons()
else:
    if st.session_state.anim_step < 0:
        st.info("Click **Play Animation** to watch the Advanced RAG pipeline.")
        for i, step in enumerate(STEPS):
            render_step(step, "waiting")
            if i < TOTAL_STEPS - 1:
                st.markdown('''<div class="arrow-down" style="opacity:0.2">&#9660;</div>''', unsafe_allow_html=True)
    else:
        render_all(st.session_state.anim_step)
        render_progress(st.session_state.anim_step)
