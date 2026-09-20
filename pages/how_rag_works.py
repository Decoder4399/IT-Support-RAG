# How RAG Works - Fully Animated Pipeline
import time
import streamlit as st

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; max-width: 1100px; margin: 0 auto; }
    .pipeline-wrap {
        background: linear-gradient(135deg, #161b22 0%, #1c2333 100%);
        border: 1px solid #30363d; border-radius: 16px;
        padding: 2rem 1.5rem; margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .pipeline-label { text-align: center; margin-bottom: 1.5rem; }
    .pipeline-label h3 { color: #e6edf3; font-size: 1rem; font-weight: 600; margin: 0; letter-spacing: 0.05em; text-transform: uppercase; }
    .pipeline-label p { color: #8b949e; font-size: 0.78rem; margin: 0.3rem 0 0 0; }
    .pipeline-row { display: flex; align-items: center; justify-content: center; gap: 0; margin-bottom: 0.8rem; }
    .p-node {
        width: 120px; min-height: 90px; background: #0d1117; border: 2px solid #30363d;
        border-radius: 12px; display: flex; flex-direction: column; align-items: center;
        justify-content: center; text-align: center; padding: 0.6rem;
        position: relative; transition: all 0.4s cubic-bezier(0.4,0,0.2,1); flex-shrink: 0;
    }
    .p-node .node-icon { font-size: 1.5rem; margin-bottom: 0.3rem; transition: transform 0.3s; }
    .p-node .node-title { color: #8b949e; font-size: 0.68rem; font-weight: 600; line-height: 1.2; transition: color 0.3s; }
    .p-node .node-num {
        position: absolute; top: -8px; right: -8px; background: #21262d;
        border: 1px solid #30363d; border-radius: 50%; width: 20px; height: 20px;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.6rem; color: #484f58; font-weight: 700; transition: all 0.3s;
    }
    .p-node.done { border-color: #3fb950; background: linear-gradient(135deg, #0d1117 0%, #0f1a12 100%); box-shadow: 0 0 20px rgba(63,185,80,0.15); }
    .p-node.done .node-icon { transform: scale(1.1); }
    .p-node.done .node-title { color: #3fb950; }
    .p-node.done .node-num { background: #238636; border-color: #3fb950; color: #fff; }
    .p-node.active { border-color: #58a6ff; background: linear-gradient(135deg, #0d1117 0%, #0d1a2e 100%); box-shadow: 0 0 30px rgba(88,166,255,0.2), 0 0 60px rgba(88,166,255,0.05); animation: nodeGlow 1.5s ease-in-out infinite; }
    .p-node.active .node-icon { transform: scale(1.15); }
    .p-node.active .node-title { color: #58a6ff; }
    .p-node.active .node-num { background: #0d419d; border-color: #58a6ff; color: #fff; animation: numPulse 1s ease-in-out infinite; }
    .p-node.waiting { opacity: 0.35; }
    .p-conn { width: 40px; height: 3px; background: #21262d; position: relative; flex-shrink: 0; border-radius: 2px; overflow: visible; }
    .p-conn.done { background: #3fb950; }
    .p-conn.active { background: linear-gradient(90deg, #3fb950, #58a6ff); animation: connPulse 1s ease-in-out infinite; }
    .p-conn.active::after {
        content: ''; position: absolute; top: -3px; left: 0; width: 9px; height: 9px;
        background: #58a6ff; border-radius: 50%; box-shadow: 0 0 8px #58a6ff;
        animation: flowDot 0.8s linear infinite;
    }
    .p-arrow { width: 0; height: 0; border-top: 6px solid transparent; border-bottom: 6px solid transparent; border-left: 8px solid #21262d; flex-shrink: 0; transition: border-color 0.3s; }
    .p-arrow.done { border-left-color: #3fb950; }
    .p-arrow.active { border-left-color: #58a6ff; }
    .info-card {
        background: linear-gradient(135deg, #161b22 0%, #1c2333 100%);
        border: 1px solid #30363d; border-radius: 12px; padding: 1.5rem; margin-top: 1rem; animation: fadeSlideUp 0.4s ease;
    }
    .info-card .info-header { display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.8rem; }
    .info-card .info-icon { font-size: 2rem; width: 50px; height: 50px; background: #0d1117; border: 1px solid #30363d; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
    .info-card .info-title { color: #e6edf3; font-size: 1.1rem; font-weight: 700; margin: 0; }
    .info-card .info-subtitle { color: #8b949e; font-size: 0.8rem; margin: 0.1rem 0 0 0; }
    .info-card .info-body { color: #8b949e; font-size: 0.88rem; line-height: 1.6; }
    .info-card .info-body strong { color: #e6edf3; }
    .info-card .info-tech { display: inline-block; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; padding: 2px 8px; font-size: 0.72rem; color: #58a6ff; font-family: monospace; margin: 0.2rem 0.2rem 0 0; }
    .data-flow { text-align: center; margin: 0.8rem 0; }
    .data-packet { display: inline-block; background: linear-gradient(135deg, #58a6ff, #bc8cff); color: #fff; font-size: 0.72rem; font-weight: 600; padding: 4px 14px; border-radius: 20px; animation: packetFloat 2s ease-in-out infinite; box-shadow: 0 0 12px rgba(88,166,255,0.3); }
    .prog-wrap { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 1rem 1.5rem; margin-top: 1rem; }
    .prog-bar { background: #21262d; border-radius: 10px; height: 8px; overflow: hidden; margin-bottom: 0.5rem; }
    .prog-fill { height: 100%; border-radius: 10px; background: linear-gradient(90deg, #58a6ff, #3fb950); transition: width 0.6s cubic-bezier(0.4,0,0.2,1); }
    .prog-text { display: flex; justify-content: space-between; font-size: 0.75rem; color: #8b949e; }
    .prog-text .step-label { color: #58a6ff; font-weight: 600; }
    @keyframes nodeGlow { 0%,100%{box-shadow:0 0 20px rgba(88,166,255,0.2)} 50%{box-shadow:0 0 35px rgba(88,166,255,0.35),0 0 70px rgba(88,166,255,0.1)} }
    @keyframes numPulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.15)} }
    @keyframes connPulse { 0%,100%{opacity:1} 50%{opacity:0.6} }
    @keyframes flowDot { 0%{left:-4px} 100%{left:calc(100% - 5px)} }
    @keyframes fadeSlideUp { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }
    @keyframes packetFloat { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-4px)} }
</style>
""", unsafe_allow_html=True)

STEPS = [
    {"num": 1, "title": "Load", "icon": "\U0001f4c1",
     "desc": "Read .md, .txt, .pdf files",
     "detail": "Scans knowledge_base/ for supported formats. Each file becomes a document object with text content and metadata.",
     "techs": ["PyMuPDF", "pathlib", "glob"]},
    {"num": 2, "title": "Chunk", "icon": "\u2702\ufe0f",
     "desc": "~1000 tokens, 200 overlap",
     "detail": "Uses <strong>tiktoken</strong> for accurate token counting. Splits on Markdown headers to preserve structure. 200-token overlap maintains context.",
     "techs": ["tiktoken", "regex", "1000 tok"]},
    {"num": 3, "title": "Embed", "icon": "\U0001f4ca",
     "desc": "384-dim vectors (MiniLM)",
     "detail": "Each chunk becomes a <strong>384-dimensional vector</strong>. Similar meanings produce similar vectors. ~80MB model, runs on CPU.",
     "techs": ["sentence-transformers", "MiniLM-L6", "384d"]},
    {"num": 4, "title": "Store", "icon": "\U0001f4be",
     "desc": "ChromaDB cosine distance",
     "detail": "Vectors indexed in <strong>ChromaDB</strong> with cosine similarity. Proper 0\u20131 scores. Persisted to disk.",
     "techs": ["ChromaDB", "cosine", "persistent"]},
    {"num": 5, "title": "Rewrite", "icon": "\u270f\ufe0f",
     "desc": "LLM expands query + keywords",
     "detail": "LLM transforms vague queries into clear search terms. Resolves pronouns using chat history. Extracts keywords for BM25.",
     "techs": ["LLM call", "pronouns", "keywords"]},
    {"num": 6, "title": "Search", "icon": "\U0001f50d",
     "desc": "BM25 + semantic via RRF",
     "detail": "<strong>BM25</strong> catches exact matches. <strong>Semantic</strong> catches meaning. <strong>RRF</strong> (k=60) fuses both rankings.",
     "techs": ["rank_bm25", "cosine", "RRF"]},
    {"num": 7, "title": "Rerank", "icon": "\U0001f3c6",
     "desc": "Cross-encoder: top-10 \u2192 top-3",
     "detail": "Retrieves 10 candidates, reranks with <strong>ms-marco-MiniLM-L-6-v2</strong>. Cross-encoder reads query+doc together.",
     "techs": ["cross-encoder", "ms-marco", "MiniLM"]},
    {"num": 8, "title": "Generate", "icon": "\U0001f916",
     "desc": "LLM answer + sources + history",
     "detail": "LLM receives system prompt, <strong>last 5 turns</strong>, and reranked context. Synthesizes sourced answers.",
     "techs": ["OpenRouter", "temp=0.3", "1000 tok"]},
]

TOTAL = len(STEPS)

if "ar_step" not in st.session_state:
    st.session_state.ar_step = -1
if "ar_playing" not in st.session_state:
    st.session_state.ar_playing = False
if "ar_done" not in st.session_state:
    st.session_state.ar_done = False
if "ar_speed" not in st.session_state:
    st.session_state.ar_speed = 1.0

DELAYS = {0.5: 1.8, 1.0: 1.2, 2.0: 0.6}


def node_state(step_idx, node_idx):
    if step_idx < 0:
        return "waiting"
    if node_idx < step_idx:
        return "done"
    if node_idx == step_idx:
        return "active"
    return "waiting"


def conn_state(step_idx, conn_idx):
    if step_idx < 0:
        return ""
    if conn_idx < step_idx:
        return "done"
    if conn_idx == step_idx:
        return "active"
    return ""


def build_pipeline_html(step_idx):
    nodes_html = []
    for i in range(TOTAL):
        s = node_state(step_idx, i)
        step = STEPS[i]
        nodes_html.append(
            '<div class="p-node ' + s + '">'
            '<span class="node-icon">' + step["icon"] + '</span>'
            '<span class="node-title">' + step["title"] + '</span>'
            '<span class="node-num">' + str(step["num"]) + '</span>'
            '</div>'
        )
        if i < TOTAL - 1:
            cs = conn_state(step_idx, i)
            nodes_html.append('<div class="p-conn ' + cs + '"></div>')
            nodes_html.append('<div class="p-arrow ' + cs + '"></div>')

    data_html = ""
    if 0 <= step_idx < TOTAL:
        step = STEPS[step_idx]
        data_html = '<div class="data-flow"><span class="data-packet">' + step["icon"] + " " + step["title"] + ' Step \u2192 processing...</span></div>'

    return (
        '<div class="pipeline-wrap">'
        '<div class="pipeline-label">'
        '<h3>\U0001f9e0 Advanced RAG Pipeline</h3>'
        '<p>8-step retrieval-augmented generation with hybrid search and reranking</p>'
        '</div>'
        '<div class="pipeline-row">' + "".join(nodes_html) + '</div>'
        + data_html +
        '</div>'
    )


def build_info_html(step_idx):
    if step_idx < 0 or step_idx >= TOTAL:
        return ""
    step = STEPS[step_idx]
    techs = "".join('<span class="info-tech">' + t + '</span>' for t in step["techs"])
    return (
        '<div class="info-card">'
        '<div class="info-header">'
        '<div class="info-icon">' + step["icon"] + '</div>'
        '<div><div class="info-title">Step ' + str(step["num"]) + ': ' + step["title"] + '</div>'
        '<div class="info-subtitle">' + step["desc"] + '</div></div>'
        '</div>'
        '<div class="info-body">' + step["detail"] + '</div>'
        '<div style="margin-top:0.8rem">' + techs + '</div>'
        '</div>'
    )


def build_progress_html(step_idx):
    pct = ((step_idx + 1) / TOTAL * 100) if step_idx >= 0 else 0
    label = ("Step " + str(step_idx + 1) + " of " + str(TOTAL)) if step_idx >= 0 else "Ready"
    return (
        '<div class="prog-wrap">'
        '<div class="prog-bar"><div class="prog-fill" style="width:' + str(pct) + '%"></div></div>'
        '<div class="prog-text"><span class="step-label">' + label + '</span><span>' + str(int(pct)) + '%</span></div>'
        '</div>'
    )

st.markdown('<div style="text-align:center;margin-bottom:1.5rem">'
'<h2 style="color:#e6edf3;font-size:1.6rem;font-weight:700;margin:0">How Advanced RAG Works</h2>'
'<p style="color:#8b949e;font-size:0.9rem;margin:0.3rem 0 0 0">Query Rewriting + Hybrid Search + Cross-Encoder Reranking</p>'
'</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
with c1:
    speed = st.select_slider("Speed", options=[0.5, 1.0, 2.0], value=st.session_state.ar_speed,
                             format_func=lambda x: {0.5: "\U0001f6a2 Slow", 1.0: "\u25b6\ufe0f Normal", 2.0: "\u26a1 Fast"}[x])
    st.session_state.ar_speed = speed
with c2:
    play = st.button("\u25b6\ufe0f Play", type="primary", use_container_width=True, disabled=st.session_state.ar_playing)
with c3:
    pause = st.button("\u23f8\ufe0f Pause", use_container_width=True, disabled=not st.session_state.ar_playing)
with c4:
    reset = st.button("\U0001f504 Reset", use_container_width=True)

if reset:
    st.session_state.ar_step = -1
    st.session_state.ar_playing = False
    st.session_state.ar_done = False
    st.rerun()

if pause:
    st.session_state.ar_playing = False
    st.rerun()

if play and not st.session_state.ar_playing:
    if st.session_state.ar_done:
        st.session_state.ar_step = -1
        st.session_state.ar_done = False
    st.session_state.ar_playing = True
    st.rerun()

st.markdown(build_pipeline_html(st.session_state.ar_step), unsafe_allow_html=True)

info = build_info_html(st.session_state.ar_step)
if info:
    st.markdown(info, unsafe_allow_html=True)

st.markdown(build_progress_html(st.session_state.ar_step), unsafe_allow_html=True)

if st.session_state.ar_playing:
    if st.session_state.ar_step < TOTAL - 1:
        st.session_state.ar_step += 1
        time.sleep(DELAYS.get(st.session_state.ar_speed, 1.2))
        st.rerun()
    else:
        st.session_state.ar_playing = False
        st.session_state.ar_done = True
        st.rerun()

if st.session_state.ar_done:
    st.success("\u2705 Animation complete! The Advanced RAG pipeline has all 8 steps.")
    st.balloons()

if st.session_state.ar_step < 0 and not st.session_state.ar_playing:
    st.info("\U0001f4a1 Click **Play** to watch the Advanced RAG pipeline animate through all 8 steps.")

with st.expander("\U0001f4d6 Step-by-Step Reference", expanded=False):
    for step in STEPS:
        techs = " | ".join(step["techs"])
        st.markdown("**Step " + str(step["num"]) + ": " + step["icon"] + " " + step["title"] + "**")
        st.markdown(step["detail"])
        st.caption(techs)
        st.divider()
