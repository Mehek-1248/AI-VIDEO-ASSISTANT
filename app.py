import streamlit as st
import time
from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Video Assistant",
    page_icon="🎞️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

/* ── Root Variables — "session log" palette ── */
:root {
    --paper: #f1f4ea;
    --paper-line: #dfe6d2;
    --surface: #ffffff;
    --surface-tint: #eaeee0;
    --line: #d7dec9;
    --ink: #20241b;
    --ink-soft: #5c6350;
    --brick: #b33a2e;
    --brick-deep: #8c2c22;
    --brick-pale: #f5e1dc;
    --amber: #c98a2c;
    --amber-pale: #f6e9d0;
    --moss: #4b6b4e;
    --moss-pale: #e1ead9;
}

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: var(--paper) !important;
    color: var(--ink) !important;
}

.stApp { background: var(--paper) !important; }

/* faint ruled-paper texture */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image: repeating-linear-gradient(
        to bottom,
        rgba(75, 107, 78, 0.05) 0px,
        rgba(75, 107, 78, 0.05) 1px,
        transparent 1px,
        transparent 34px
    );
    pointer-events: none;
    z-index: 0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface-tint) !important;
    border-right: 1px solid var(--line) !important;
}
[data-testid="stSidebar"] * { color: var(--ink) !important; }

.brand {
    font-family: 'Fraunces', serif;
    font-size: 1.5rem;
    font-weight: 600;
    line-height: 1.15;
    color: var(--brick-deep);
}
.brand-sub {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: var(--ink-soft);
    margin-top: 0.3rem;
}

/* ── Headings ── */
h1, h2, h3, h4, h5, h6 { font-family: 'Fraunces', serif !important; color: var(--ink) !important; }

/* ── Hero ── */
.hero-row { display:flex; align-items:flex-end; gap:1.5rem; margin-bottom: 0.25rem; }
.hero-title {
    font-family: 'Fraunces', serif;
    font-size: clamp(2rem, 4.2vw, 3rem);
    font-weight: 600;
    line-height: 1.05;
    margin: 0;
    color: var(--ink);
}
.hero-sub {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.95rem;
    color: var(--ink-soft);
    margin-top: 0.5rem;
}

/* small hand-built waveform, the one deliberate flourish */
.waveform { display:flex; align-items:flex-end; gap:3px; height:34px; }
.waveform span { display:block; width:4px; border-radius:2px; }

/* ── Section heading (plain, not an eyebrow) ── */
.section-heading {
    font-family: 'Fraunces', serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--ink);
    margin-bottom: 0.6rem;
}

/* ── Cassette-style session label ── */
.cassette {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.4rem;
    position: relative;
    transform: rotate(-0.3deg);
    box-shadow: 3px 4px 0 var(--brick-pale);
}
.cassette-meta {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    color: var(--brick-deep);
    margin-bottom: 0.4rem;
}
.cassette-title {
    font-family: 'Fraunces', serif;
    font-size: 1.55rem;
    font-weight: 600;
    color: var(--ink);
}

/* ── Plain content panel (no card-kit sameness) ── */
.panel {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 1.3rem 1.4rem;
}
.panel-content {
    font-size: 0.9rem;
    line-height: 1.75;
    color: var(--ink);
}

/* ── Folder-tab cards for extraction row ── */
.tab-wrap { margin-top: 0.3rem; }
.tab {
    display: inline-block;
    padding: 0.32rem 0.85rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    font-weight: 500;
    color: #fff;
    border-radius: 6px 6px 0 0;
    position: relative;
    top: 1px;
}
.tab-brick { background: var(--brick); }
.tab-amber { background: var(--amber); }
.tab-moss  { background: var(--moss); }
.tab-card {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 0 10px 10px 10px;
    padding: 1.1rem 1.2rem;
    min-height: 170px;
    font-size: 0.87rem;
    line-height: 1.7;
}

/* ── Inputs & Buttons ── */
.stTextInput > div > div > input {
    background: var(--surface) !important;
    border: 1px solid var(--line) !important;
    border-radius: 7px !important;
    color: var(--ink) !important;
    font-family: 'IBM Plex Mono', monospace !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--brick) !important;
    box-shadow: 0 0 0 2px rgba(179,58,46,0.15) !important;
}

.stButton > button {
    background: var(--brick) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 7px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.6rem 1.4rem !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 16px rgba(179,58,46,0.25) !important;
}
.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: var(--ink) !important;
    border: 1px solid var(--line) !important;
}

/* language pills (st.radio, horizontal) */
[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 0.4rem;
}
[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 20px;
    padding: 0.25rem 0.85rem !important;
}

/* ── Pipeline timeline ── */
.timeline { border-left: 2px solid var(--line); margin-left: 0.5rem; padding-left: 1.1rem; }
.timeline-item { position: relative; padding-bottom: 1rem; }
.timeline-item:last-child { padding-bottom: 0; }
.timeline-item .dot {
    position: absolute; left: -1.42rem; top: 0.2rem;
    width: 10px; height: 10px; border-radius: 50%;
    border: 2px solid var(--surface-tint);
}
.dot-active  { background: var(--amber); animation: pulse 1.4s infinite; }
.dot-done    { background: var(--moss); }
.dot-pending { background: var(--line); }
.timeline-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    color: var(--ink);
}
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.35; } }

/* ── Transcript log ── */
.transcript-box {
    background: var(--surface-tint);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 1.1rem 1.3rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
    line-height: 1.85;
    max-height: 320px;
    overflow-y: auto;
    color: var(--ink-soft);
    white-space: pre-wrap;
    word-break: break-word;
}

/* ── Chat rendered as a transcript, not chat bubbles ── */
.transcript-turn {
    display: flex;
    gap: 1rem;
    padding: 0.65rem 0;
    border-bottom: 1px solid var(--line);
}
.transcript-turn:last-child { border-bottom: none; }
.turn-speaker {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    font-weight: 600;
    min-width: 84px;
    padding-top: 0.15rem;
}
.speaker-you { color: var(--brick-deep); }
.speaker-bot { color: var(--moss); }
.turn-text { font-size: 0.88rem; line-height: 1.65; color: var(--ink); }

/* ── Divider ── */
hr { border: none !important; border-top: 1px solid var(--line) !important; margin: 1.5rem 0 !important; }

/* Streamlit misc */
.stProgress > div > div > div { background: var(--brick) !important; }
.stSpinner > div { border-top-color: var(--brick) !important; }
[data-testid="stMarkdownContainer"] p { color: var(--ink) !important; }
label { color: var(--ink-soft) !important; font-size: 0.8rem !important; }

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--surface-tint); }
::-webkit-scrollbar-thumb { background: var(--line); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--brick); }
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ──────────────────────────────────────────────────────────
for key, default in {
    "result": None,
    "chat_history": [],
    "processing": False,
    "pipeline_done": False,
    "pipeline_steps": {},
    "session_count": 0,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Helpers ────────────────────────────────────────────────────────────────────
def step_status(steps: dict, key: str) -> str:
    s = steps.get(key, "pending")
    if s == "active": return "dot-active"
    if s == "done":   return "dot-done"
    return "dot-pending"

def render_timeline_item(label: str, key: str):
    css = step_status(st.session_state.pipeline_steps, key)
    st.markdown(f"""
    <div class="timeline-item">
        <div class="dot {css}"></div>
        <div class="timeline-label">{label}</div>
    </div>""", unsafe_allow_html=True)

def waveform(bars=18, color1="var(--brick)", color2="var(--amber)"):
    import random
    random.seed(7)
    heights = [random.randint(6, 32) for _ in range(bars)]
    spans = "".join(
        f'<span style="height:{h}px;background:{color1 if i % 2 == 0 else color2}"></span>'
        for i, h in enumerate(heights)
    )
    return f'<div class="waveform">{spans}</div>'

# ─── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="brand">Session Log</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">AI Video Assistant</div>', unsafe_allow_html=True)
    st.markdown("---")

    source = st.text_input(
        "YouTube URL or file path",
        placeholder="https://youtube.com/watch?v=... or /path/to/file.mp4",
    )
    language = st.radio("Language", ["english", "hinglish"], horizontal=True)
    run_btn = st.button(
        "Analyse recording" if not st.session_state.processing else "Analysis in progress...",
        use_container_width=True,
        disabled=st.session_state.processing,
    )

    if st.session_state.pipeline_done or st.session_state.processing:
        st.markdown("---")
        st.markdown('<div class="section-heading" style="font-size:0.95rem">Pipeline status</div>', unsafe_allow_html=True)
        st.markdown('<div class="timeline">', unsafe_allow_html=True)
        for step, label in [
            ("audio",      "Audio processing"),
            ("transcript", "Transcription"),
            ("title",      "Title generation"),
            ("summary",    "Summarisation"),
            ("extract",    "Extraction"),
            ("rag",        "RAG engine"),
        ]:
            render_timeline_item(label, step)
        st.markdown('</div>', unsafe_allow_html=True)

# ─── Main Area — Hero ─────────────────────────────────────────────────────────────
hero_l, hero_r = st.columns([3, 1])
with hero_l:
    st.markdown('<div class="hero-title">AI Video Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Turn a recording into a transcript, a summary, and a running conversation you can question.</div>', unsafe_allow_html=True)
with hero_r:
    st.markdown(waveform(), unsafe_allow_html=True)

st.markdown("---")

# ── Run Pipeline ────────────────────────────────────────────────────────────────
if run_btn:
    if not source.strip():
        st.error("Add a YouTube URL or file path before analysing.")
    else:
        st.session_state.processing = True
        st.session_state.pipeline_done = False
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.pipeline_steps = {}

        progress_placeholder = st.empty()
        step_labels = {
            "audio": "Audio processing",
            "transcript": "Transcription",
            "title": "Title generation",
            "summary": "Summarisation",
            "extract": "Extraction",
            "rag": "RAG engine",
        }

        def update_step(key, state):
            st.session_state.pipeline_steps[key] = state
            if state == "active":
                progress_placeholder.info(f"Running: {step_labels[key]}...")
            elif state == "done":
                progress_placeholder.success(f"Completed: {step_labels[key]}")

        try:
            progress_placeholder.info("Starting the pipeline...")

            update_step("audio", "active")
            chunks = process_input(source)
            update_step("audio", "done")

            update_step("transcript", "active")
            transcript = transcribe_all(chunks, language)
            update_step("transcript", "done")

            update_step("title", "active")
            title = generate_title(transcript)
            update_step("title", "done")

            update_step("summary", "active")
            summary = summarize(transcript)
            update_step("summary", "done")

            update_step("extract", "active")
            action_items = extract_action_items(transcript)
            decisions    = extract_key_decisions(transcript)
            questions    = extract_questions(transcript)
            update_step("extract", "done")

            update_step("rag", "active")
            rag_chain = build_rag_chain(transcript)
            update_step("rag", "done")

            st.session_state.session_count += 1
            st.session_state.result = {
                "title": title,
                "transcript": transcript,
                "summary": summary,
                "action_items": action_items,
                "key_decisions": decisions,
                "open_questions": questions,
                "rag_chain": rag_chain,
                "language": language,
            }
            st.session_state.pipeline_done = True
            progress_placeholder.success("Analysis complete.")
            time.sleep(0.5)
            progress_placeholder.empty()
            st.rerun()

        except Exception as e:
            for k in ["audio", "transcript", "title", "summary", "extract", "rag"]:
                if st.session_state.pipeline_steps.get(k) == "active":
                    st.session_state.pipeline_steps[k] = "pending"
            error_text = str(e)
            if "429" in error_text or "rate_limited" in error_text:
                progress_placeholder.error(
                    "LLM API rate limit reached. Wait for the limit to reset, "
                    "check your provider quota, then try again."
                )
            else:
                progress_placeholder.error(f"Something went wrong: {e}")
        finally:
            st.session_state.processing = False

# ── Results ──────────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    st.markdown(f"""
    <div class="cassette">
        <div class="cassette-meta">Session {st.session_state.session_count:03d}, analysed in {r['language'].capitalize()}</div>
        <div class="cassette-title">{r['title']}</div>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2], gap="medium")

    with col1:
        st.markdown('<div class="section-heading">Summary</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="panel"><div class="panel-content">{r["summary"]}</div></div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-heading">Full transcript</div>', unsafe_allow_html=True)
        with st.expander("Open transcript", expanded=False):
            st.markdown(f'<div class="transcript-box">{r["transcript"]}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        st.markdown(f"""
        <div class="tab-wrap">
            <div class="tab tab-brick">Action items</div>
            <div class="tab-card">{r['action_items']}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="tab-wrap">
            <div class="tab tab-amber">Key decisions</div>
            <div class="tab-card">{r['key_decisions']}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="tab-wrap">
            <div class="tab tab-moss">Open questions</div>
            <div class="tab-card">{r['open_questions']}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── RAG Chat, styled as a transcript rather than chat bubbles ──────────────
    st.markdown('<div class="section-heading" style="font-size:1.2rem">Ask the meeting</div>', unsafe_allow_html=True)

    if st.session_state.chat_history:
        turns_html = '<div class="panel">'
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                turns_html += f"""
                <div class="transcript-turn">
                    <div class="turn-speaker speaker-you">You</div>
                    <div class="turn-text">{msg['content']}</div>
                </div>"""
            else:
                turns_html += f"""
                <div class="transcript-turn">
                    <div class="turn-speaker speaker-bot">Assistant</div>
                    <div class="turn-text">{msg['content']}</div>
                </div>"""
        turns_html += '</div>'
        st.markdown(turns_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="panel" style="text-align:center;padding:2.2rem">
            <div class="panel-content" style="color:var(--ink-soft)">
                Nothing asked yet — questions about the recording will appear here, turn by turn.
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

    chat_col1, chat_col2 = st.columns([5, 1], gap="small")
    with chat_col1:
        user_input = st.text_input(
            "Your question", placeholder="What were the main decisions made?",
            label_visibility="collapsed",
        )
    with chat_col2:
        send_btn = st.button("Send", use_container_width=True)

    if send_btn and user_input.strip():
        with st.spinner("Thinking…"):
            answer = ask_question(r["rag_chain"], user_input.strip())
        st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("Clear chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

else:
    # Empty state — a blank ruled page waiting for a session
    st.markdown(f"""
    <div class="panel" style="padding:3rem 2rem;text-align:center">
        {waveform(bars=24)}
        <div style="font-family:'Fraunces',serif;font-size:1.4rem;font-weight:600;color:var(--ink);margin-top:1.4rem">
            No session yet
        </div>
        <div style="color:var(--ink-soft);font-size:0.88rem;max-width:420px;margin:0.6rem auto 0;line-height:1.7">
            Paste a YouTube URL or a local file path in the sidebar, pick a language, and analyse it to get
            a transcript, summary, and a conversation you can question.
        </div>
    </div>""", unsafe_allow_html=True)