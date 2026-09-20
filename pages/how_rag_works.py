# How RAG Works - Animated step-by-step explanation
import time
import streamlit as st

st.set_page_config(page_title="How RAG Works", page_icon=":material/menu_book:", layout="wide")

# ── CSS ────────────────────────────────────────────────────────────
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

    .step-icon { font-size: 1.5rem; margin-right: 0.5rem; vertical-align: middle; }

    .progress-bar {
        background: #21262d; border-radius: 10px; height: 6px; margin: 1rem 0;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%; border-radius: 10px; transition: width 0.8s ease;
        background: linear-gradient(90deg, #58a6ff, #3fb950);
    }

    .arrow-down {
        text-align: center; color: #30363d; font-size: 1.2rem;
        margin: -0.2rem 0; animation: pulse 1.5s infinite;
    }

    @keyframes fadeSlideIn {
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulse {
        0%, 100% { opacity: 0.4; }
        50% { opacity: 1; }
    }

    .intro-box {
        background: linear-gradient(135deg, #1a1f36 0%, #0d1117 100%);
        border: 1px solid #30363d; border-radius: 12px;
        padding: 1.5rem; margin-bottom: 1.5rem; text-align: center;
    }
    .intro-box h2 { color: #e6edf3; font-size: 1.5rem; margin: 0; }
    .intro-box p { color: #8b949e; font-size: 0.9rem; margin: 0.5rem 0 0 0; }
</style>
""", unsafe_allow_html=True)

# ── Step definitions ───────────────────────────────────────────────
STEPS = [
    {
        "num": 1,
        "title": "Load Documents",
        "icon": ":open_file_folder:",
        "desc": "Read markdown, PDF, and text files from the knowledge base folder into Python.",
        "detail": "The loader scans knowledge_base/ for .md, .txt, and .pdf files. Each file becomes a document object with its text content and metadata (filename, path). This is raw material for the pipeline.",
    },
    {
        "num": 2,
        "title": "Chunk Documents",
        "icon": ":scissors:",
        "desc": "Split long documents into small overlapping pieces (~500 characters each).",
        "detail": "LLMs can only read limited text. We split at paragraph and sentence boundaries to preserve meaning. Each chunk overlaps slightly with the next so context is not lost at the edges.",
    },
    {
        "num": 3,
        "title": "Create Embeddings",
        "icon": ":bar_chart:",
        "desc": "Convert each text chunk into a numerical vector (384 numbers) that represents its meaning.",
        "detail": "The sentence-transformers model (all-MiniLM-L6-v2) converts text to vectors. Similar meanings produce similar numbers: 'forgot my password' and 'password reset' end up close in vector space.",
    },
    {
        "num": 4,
        "title": "Store in Vector DB",
        "icon": ":floppy_disk:",
        "desc": "Save all vectors in ChromaDB, a database optimized for fast similarity search.",
        "detail": "ChromaDB indexes the vectors so finding similar ones is instant. It persists to disk so we don't need to re-embed every time. Think of it as a search engine for meaning, not keywords.",
    },
    {
        "num": 5,
        "title": "Search Similar Chunks",
        "icon": ":mag:",
        "desc": "When a user asks a question, find the most relevant chunks using cosine similarity.",
        "detail": "The user's question is embedded with the same model, then compared against all stored vectors. The top-N most similar chunks are retrieved. These are the most relevant pieces of information.",
    },
    {
        "num": 6,
        "title": "Generate Answer",
        "icon": ":robot_face:",
        "desc": "Send the retrieved chunks + question to an LLM, which reads the context and generates a sourced answer.",
        "detail": "The LLM receives a system prompt, the relevant documentation chunks, and the user's question. It synthesizes information from multiple sources and generates a natural language answer with citations.",
    },
]

TOTAL_STEPS = len(STEPS)
DELAY_BETWEEN_STEPS = 1.5  # seconds


def init_anim_state():
    defaults = {
        "anim_step": -1,
        "animating": False,
        "anim_done": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def render_step(step, state):
    """Render a single step card."""
    if state == "done":
        cls = "done"
        badge = ":white_check_mark: Done"
    elif state == "active":
        cls = "active"
        badge = ":hourglass_flowing_sand: In progress..."
    else:
        cls = "waiting"
        badge = ""

    icon = step["icon"]
    html = f'''
    <div class="step-card {cls}">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <span class="step-num">Step {step["num"]}</span>
            <span style="font-size:0.75rem;color:#8b949e;">{badge}</span>
        </div>
        <h4>{icon} {step["title"]}</h4>
        <p>{step["desc"]}</p>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)

    # Show detail for active/done steps
    if state in ("active", "done"):
        with st.expander(f"Learn more about Step {step['num']}", expanded=(state == "active")):
            st.markdown(step["detail"])


def render_all_steps(current, animating_done=False):
    """Render all steps up to current, with appropriate states."""
    for i, step in enumerate(STEPS):
        if i < current:
            render_step(step, "done")
        elif i == current and not animating_done:
            render_step(step, "active")
        elif i == current and animating_done:
            render_step(step, "done")
        else:
            render_step(step, "waiting")

        # Arrow between steps (not after last)
        if i < TOTAL_STEPS - 1:
            if i < current:
                st.markdown('<div class="arrow-down">&#9660;</div>', unsafe_allow_html=True)
            elif i == current:
                st.markdown('<div class="arrow-down">&#9660;</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="arrow-down" style="opacity:0.2">&#9660;</div>', unsafe_allow_html=True)


def render_progress_bar(step_idx):
    """Render a progress bar."""
    pct = ((step_idx + 1) / TOTAL_STEPS) * 100
    st.markdown(f'''
    <div class="progress-bar">
        <div class="progress-fill" style="width:{pct}%"></div>
    </div>
    <p style="text-align:center;color:#8b949e;font-size:0.8rem;margin:0;">
        Step {step_idx + 1} of {TOTAL_STEPS} &mdash; {pct:.0f}% complete
    </p>
    ''', unsafe_allow_html=True)


# ── Main page ──────────────────────────────────────────────────────
init_anim_state()

st.markdown("""
<div class="intro-box">
    <h2>How RAG Works</h2>
    <p>Watch the Retrieval-Augmented Generation pipeline come to life, step by step.</p>
</div>
""", unsafe_allow_html=True)

# Controls
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    play = st.button("Play Animation", type="primary", use_container_width=True,
                      disabled=st.session_state.animating)
with col2:
    reset = st.button("Reset", use_container_width=True)
with col3:
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

# ── Animation loop ─────────────────────────────────────────────────
if st.session_state.animating:
    next_step = st.session_state.anim_step + 1

    if next_step < TOTAL_STEPS:
        # Show current step appearing
        st.session_state.anim_step = next_step

        # Render steps up to and including current
        render_all_steps(next_step)
        render_progress_bar(next_step)

        # Wait then advance
        time.sleep(DELAY_BETWEEN_STEPS)
        st.rerun()
    else:
        # Animation complete
        st.session_state.animating = False
        st.session_state.anim_done = True
        st.rerun()

elif st.session_state.anim_done:
    # Show all steps completed
    render_all_steps(TOTAL_STEPS - 1, animating_done=True)
    render_progress_bar(TOTAL_STEPS - 1)
    st.success("Animation complete! The RAG pipeline has all 6 steps.")
    st.balloons()

else:
    # Initial state / after reset - show placeholder
    if st.session_state.anim_step < 0:
        st.info("Click **Play Animation** to watch the RAG pipeline build step by step.")
        # Show all steps in waiting state
        for i, step in enumerate(STEPS):
            render_step(step, "waiting")
            if i < TOTAL_STEPS - 1:
                st.markdown('<div class="arrow-down" style="opacity:0.2">&#9660;</div>', unsafe_allow_html=True)
    else:
        render_all_steps(st.session_state.anim_step)
        render_progress_bar(st.session_state.anim_step)
