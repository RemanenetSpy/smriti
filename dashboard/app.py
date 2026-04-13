"""
Chronos OS — Streamlit Dashboard
===================================
Premium 'Letters to the Future' editorial dashboard for Chronos.
Design System: Parchment + Wax Seal Red with Cormorant Garamond typography.
"""

import json
import os
from datetime import datetime

import httpx
import streamlit as st

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_BASE = os.getenv("CHRONOS_API_URL", "http://localhost:8000")

import base64
from pathlib import Path

def get_base64_image(image_path: Path) -> str:
    if image_path.exists():
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

logo_path = Path(__file__).parent / "logo.png"
b64_logo = get_base64_image(logo_path)

if b64_logo:
    sidebar_logo_html = f'<img src="data:image/png;base64,{b64_logo}" style="width: 140px; filter: contrast(1.1); display: inline-block; padding-bottom: 0px; margin-bottom: 0px;" />'
    hero_logo_html = f'<img src="data:image/png;base64,{b64_logo}" style="width: 160px; filter: contrast(1.1); display: inline-block;" />'
else:
    sidebar_logo_html = '<div style="font-size:2.2rem; transform: translateY(10px);">🕰️</div>'
    hero_logo_html = '<div class="seal">🕰️</div>'
# ---------------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Chronos OS — Temporal AI Agent Ecosystem",
    page_icon="🕰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS — Chronos Editorial Design System
# Navy + Gold | Cormorant Garamond + Inter | Luxury Minimalist
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    /* ═══════════════════════════════════════════════════════════════
       FONTS — Chronos Identity
       Cormorant Garamond (editorial headings)
       Spectral (body serif)
       Inter (UI text)
       JetBrains Mono (code/data)
    ═══════════════════════════════════════════════════════════════ */
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=Spectral:ital,wght@0,300;0,400;0,500;0,600;1,400&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ═══════════════════════════════════════════════════════════════
       ROOT PALETTE (Parchment & Wax Seal)
    ═══════════════════════════════════════════════════════════════ */
    :root {
        --chronos-bg: #F7F5F0;  /* Parchment */
        --chronos-surface: #FFFFFF;
        --chronos-surface-alt: #FCFAF5;
        --chronos-accent: #A93322; /* Wax Seal Red */
        --chronos-accent-dim: #D15A47;
        --chronos-accent-glow: rgba(169, 51, 34, 0.15);
        --chronos-text: #2B2C30;
        --chronos-text-dim: #6E7079;
        --chronos-border: #E8E3D8;
        --chronos-border-hover: #D6CBB8;
        --chronos-success: #2C7A4B;
        --chronos-danger: #A93322;
    }

    /* ═══════════════════════════════════════════════════════════════
       GLOBAL OVERRIDES
    ═══════════════════════════════════════════════════════════════ */
    .stApp {
        background: var(--chronos-bg) !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
        color: var(--chronos-text) !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--chronos-surface-alt) !important;
        border-right: 1px solid var(--chronos-border) !important;
    }

    [data-testid="stSidebar"] * {
        color: var(--chronos-text) !important;
    }

    /* All headers → Cormorant Garamond */
    h1, h2, h3 {
        font-family: 'Cormorant Garamond', 'Georgia', serif !important;
        color: var(--chronos-accent) !important;
        letter-spacing: -0.5px !important;
    }
    h1 { font-weight: 300 !important; font-size: 2.8rem !important; }
    h2 { font-weight: 400 !important; font-size: 1.8rem !important; }
    h3 { font-weight: 500 !important; font-size: 1.3rem !important; }

    /* Paragraphs → Spectral */
    p, .stMarkdown p {
        font-family: 'Spectral', 'Georgia', serif !important;
        color: var(--chronos-text) !important;
        line-height: 1.7 !important;
    }

    /* Code blocks → JetBrains Mono */
    code, pre, .stCodeBlock {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* ═══════════════════════════════════════════════════════════════
       HERO HEADER — Wax Seal Aesthetic
    ═══════════════════════════════════════════════════════════════ */
    .chronos-hero {
        background: var(--chronos-surface);
        border: 1px solid var(--chronos-border);
        border-radius: 2px;
        padding: 3rem 3.5rem;
        margin-bottom: 2.5rem;
        position: relative;
        overflow: hidden;
        text-align: center;
    }
    .chronos-hero::before {
        content: '';
        position: absolute;
        top: 0; left: 50%;
        transform: translateX(-50%);
        width: 150px; height: 1px;
        background: linear-gradient(90deg, transparent, var(--chronos-accent-dim), transparent);
    }
    .chronos-hero .seal {
        font-size: 3.5rem;
        margin-bottom: 0.5rem;
    }
    .chronos-hero h1 {
        font-family: 'Cormorant Garamond', serif !important;
        color: var(--chronos-accent) !important;
        font-weight: 300 !important;
        font-size: 2.6rem !important;
        margin: 0 !important;
        letter-spacing: 2px !important;
    }
    .chronos-hero .tagline {
        font-family: 'Spectral', serif;
        color: var(--chronos-text-dim);
        font-size: 1.05rem;
        font-style: italic;
        margin-top: 0.8rem;
        letter-spacing: 0.5px;
    }
    .chronos-hero .subtitle {
        font-family: 'Inter', sans-serif;
        color: var(--chronos-text-dim);
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin-top: 1.2rem;
    }

    /* ═══════════════════════════════════════════════════════════════
       METRIC CARDS — Editorial Numbers
    ═══════════════════════════════════════════════════════════════ */
    .metric-card {
        background: var(--chronos-surface);
        border: 1px solid var(--chronos-border);
        border-radius: 2px;
        padding: 2rem 1.5rem;
        text-align: center;
        transition: border-color 0.4s ease;
    }
    .metric-card:hover {
        border-color: var(--chronos-border-hover);
    }
    .metric-value {
        font-family: 'Cormorant Garamond', serif;
        color: var(--chronos-text);
        font-size: 3rem;
        font-weight: 300;
        line-height: 1;
    }
    .metric-label {
        font-family: 'Inter', sans-serif;
        color: var(--chronos-text-dim);
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 2.5px;
        margin-top: 0.8rem;
    }

    /* ═══════════════════════════════════════════════════════════════
       STATUS BADGES
    ═══════════════════════════════════════════════════════════════ */
    .badge-online {
        display: inline-block;
        background: rgba(74, 222, 128, 0.08);
        color: var(--chronos-success);
        padding: 0.35rem 1rem;
        border: 1px solid rgba(74, 222, 128, 0.2);
        border-radius: 1px;
        font-family: 'Inter', sans-serif;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .badge-offline {
        display: inline-block;
        background: rgba(248, 113, 113, 0.08);
        color: var(--chronos-danger);
        padding: 0.35rem 1rem;
        border: 1px solid rgba(248, 113, 113, 0.2);
        border-radius: 1px;
        font-family: 'Inter', sans-serif;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* ═══════════════════════════════════════════════════════════════
       TIMELINE EVENTS — Temporal Memory Results
    ═══════════════════════════════════════════════════════════════ */
    .timeline-event {
        background: var(--chronos-surface);
        border-left: 2px solid var(--chronos-accent-dim);
        padding: 1rem 1.5rem;
        margin: 0.8rem 0;
        border-radius: 0 2px 2px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.02);
        transition: border-color 0.3s ease, transform 0.3s ease;
    }
    .timeline-event:hover {
        border-left-color: var(--chronos-accent);
        transform: translateX(4px);
    }
    .timeline-event .ts {
        font-family: 'JetBrains Mono', monospace;
        color: var(--chronos-accent);
        font-size: 0.75rem;
        font-weight: 500;
    }
    .timeline-event .svo {
        font-family: 'Spectral', serif;
        color: var(--chronos-text);
        font-size: 0.95rem;
        margin-top: 0.3rem;
    }
    .timeline-event .meta {
        font-family: 'Inter', sans-serif;
        color: var(--chronos-text-dim);
        font-size: 0.7rem;
        margin-top: 0.4rem;
    }

    /* ═══════════════════════════════════════════════════════════════
       TIER BADGES
    ═══════════════════════════════════════════════════════════════ */
    .tier-badge {
        display: inline-block;
        padding: 0.6rem 2rem;
        border-radius: 1px;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.8rem;
        letter-spacing: 3px;
        text-transform: uppercase;
    }
    .tier-explorer {
        background: rgba(74, 222, 128, 0.08);
        color: var(--chronos-success);
        border: 1px solid rgba(74, 222, 128, 0.15);
    }
    .tier-builder {
        background: rgba(169, 51, 34, 0.08);
        color: var(--chronos-accent);
        border: 1px solid rgba(169, 51, 34, 0.2);
    }
    .tier-scale {
        background: rgba(139, 92, 246, 0.08);
        color: #A78BFA;
        border: 1px solid rgba(139, 92, 246, 0.15);
    }

    /* ═══════════════════════════════════════════════════════════════
       DIVIDERS — Editorial Rule
    ═══════════════════════════════════════════════════════════════ */
    .editorial-rule {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--chronos-border-hover), transparent);
        margin: 2.5rem 0;
    }

    /* ═══════════════════════════════════════════════════════════════
       SECTION LABEL
    ═══════════════════════════════════════════════════════════════ */
    .section-label {
        font-family: 'Inter', sans-serif;
        color: var(--chronos-text-dim);
        font-size: 0.6rem;
        text-transform: uppercase;
        letter-spacing: 4px;
        margin-bottom: 0.5rem;
    }

    /* ═══════════════════════════════════════════════════════════════
       BUTTONS & INPUTS — Chronos Style
    ═══════════════════════════════════════════════════════════════ */
    .stButton > button {
        background: var(--chronos-surface) !important;
        color: var(--chronos-accent) !important;
        border: 1px solid var(--chronos-accent-dim) !important;
        border-radius: 2px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.75rem !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        padding: 0.6rem 1.5rem !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background: var(--chronos-accent) !important;
        color: white !important;
        box-shadow: 0 4px 15px var(--chronos-accent-glow) !important;
    }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: var(--chronos-surface) !important;
        border: 1px solid var(--chronos-border) !important;
        border-radius: 2px !important;
        color: var(--chronos-text) !important;
        font-family: 'Spectral', serif !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--chronos-accent-dim) !important;
        box-shadow: 0 0 0 1px var(--chronos-accent-glow) !important;
    }

    .stSelectbox > div > div {
        background: var(--chronos-surface) !important;
        border: 1px solid var(--chronos-border) !important;
        border-radius: 2px !important;
    }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        background: var(--chronos-surface) !important;
        border: 1px solid var(--chronos-border) !important;
        border-radius: 2px !important;
    }

    /* Metrics override */
    [data-testid="stMetric"] {
        background: var(--chronos-surface);
        border: 1px solid var(--chronos-border);
        border-radius: 2px;
        padding: 1rem;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Cormorant Garamond', serif !important;
        color: var(--chronos-text) !important;
    }
    [data-testid="stMetricLabel"] {
        font-family: 'Inter', sans-serif !important;
        color: var(--chronos-text-dim) !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        font-size: 0.65rem !important;
    }

    /* Tables */
    .stTable, .stDataFrame {
        font-family: 'Inter', sans-serif !important;
    }

    /* Footer */
    .chronos-footer {
        text-align: center;
        font-family: 'Spectral', serif;
        color: var(--chronos-text-dim);
        font-size: 0.8rem;
        font-style: italic;
        margin-top: 3rem;
        padding: 1.5rem 0;
        border-top: 1px solid var(--chronos-border);
    }
    .chronos-footer .seal-small {
        font-size: 1.2rem;
        display: block;
        margin-bottom: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def api_call(method: str, path: str, api_key: str = "", **kwargs) -> dict:
    """Make an API call to the Chronos backend."""
    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key

    try:
        with httpx.Client(timeout=30) as client:
            url = f"{API_BASE}{path}"
            if method == "GET":
                resp = client.get(url, headers=headers, params=kwargs.get("params"))
            elif method == "POST":
                resp = client.post(url, headers=headers, json=kwargs.get("json"))
            else:
                return {"error": f"Unsupported method: {method}"}

            if resp.status_code == 200:
                return resp.json()
            else:
                return {"error": f"HTTP {resp.status_code}: {resp.text}"}

    except httpx.ConnectError:
        return {"error": "Cannot connect to Chronos API. Is the server running?"}
    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# Sidebar — Chronos Identity
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center;padding:0.5rem 0 0.5rem">
        {sidebar_logo_html}
        <div style="font-family:'Inter',sans-serif;font-size:0.5rem;
                    color:var(--chronos-text-dim);text-transform:uppercase;letter-spacing:4px;margin-top:0.2rem">
            Temporal AI Agent Ecosystem
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # API Key input
    api_key = st.text_input(
        "🔑 API Key",
        type="password",
        placeholder="chrn_...",
        help="Your Chronos API key for authenticated requests",
    )

    if api_key:
        st.session_state["api_key"] = api_key

    stored_key = st.session_state.get("api_key", "")

    st.markdown("---")

    # Navigation
    page = st.radio(
        "Navigate",
        ["⟡ Overview", "⭳ Ingest Events", "⚲ Query Memory",
         "✦ Agent Chat", "⚙ Connect Tool",
         "▤ Usage & Billing", "⚷ API Keys"],
        label_visibility="collapsed",
    )

    # Sidebar footer
    st.markdown("""
    <div style="position:fixed;bottom:1rem;font-family:'Spectral',serif;
                font-size:0.7rem;color:#6B7194;font-style:italic">
        Letters to the Future, for agents.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGES
# ═══════════════════════════════════════════════════════════════════════════

if page == "⟡ Overview":
    # Hero
    st.markdown(f"""
    <div class="chronos-hero">
        {hero_logo_html}
        <div class="tagline" style="margin-top: 10px;">Capturing the fragments of today for the clarity of tomorrow.</div>
        <div class="subtitle">Temporal AI Agent Ecosystem · v0.1.0</div>
    </div>
    """, unsafe_allow_html=True)

    # Health check
    health = api_call("GET", "/health")

    if "error" not in health:
        stores = health.get("stores", {})
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{stores.get('sqlite_events', 0):,}</div>
                <div class="metric-label">Events Stored</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{stores.get('chroma_embeddings', 0):,}</div>
                <div class="metric-label">Embeddings</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="metric-card">
                <div class="badge-online">● Operational</div>
                <div class="metric-label" style="margin-top:1.2rem">System Status</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value" style="font-size:1.8rem">DeepSeek R1</div>
                <div class="metric-label">AI Engine</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error(f"⚠️ {health['error']}")
        st.info("Start the API server: `python -m uvicorn api.main:app --port 8000`")

    # Architecture
    st.markdown("<hr class='editorial-rule'>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'>Architecture</div>", unsafe_allow_html=True)
    st.markdown("### The Dual Calendar System")
    st.markdown("""
    Chronos decomposes every piece of text into **Subject-Verb-Object** event tuples,
    stores them in a dual calendar (structured events + raw conversation turns),
    and indexes them for both **semantic** and **temporal** retrieval.
    """)

    st.code("""
# Feed any text → AI extracts structured events
POST /ingest
{
  "source_id": "your-saas-app",
  "events": [{"text": "Acme Corp signed a $50k contract for Q2 2026"}]
}

# Ask any question → hybrid search finds answers
POST /query
{
  "query": "What happened with Acme Corp?"
}

# Response: [{subject: "Acme Corp", verb: "signed", object: "$50k contract", when: "Q2 2026"}]
    """, language="python")


elif page == "⭳ Ingest Events":
    st.markdown("<div class='section-label'>Memory Ingestion</div>", unsafe_allow_html=True)
    st.markdown("## Feed the Temporal Memory")
    st.markdown("*Enter events as natural language. The AI extracts the who, what, and when.*")

    source_id = st.text_input("Source ID", value="my-app", help="Identifies where these events come from")

    st.markdown("#### Events")
    st.markdown("*One event per line — write in plain English:*")

    events_text = st.text_area(
        "Events (one per line)",
        value="Acme Corp signed a $50,000 contract for Q2 2026\nJane was promoted to VP of Engineering on March 15\nThe team completed the product demo for TechStart on April 1",
        height=150,
        label_visibility="collapsed",
    )

    parse_svo = st.checkbox("✨ Enable AI SVO Parsing (DeepSeek R1)", value=True)

    if st.button("📥 Ingest Into Memory") and stored_key and events_text.strip():
        lines = [l.strip() for l in events_text.strip().split("\n") if l.strip()]
        payload = {
            "source_id": source_id,
            "events": [{"text": line} for line in lines],
            "parse_svo": parse_svo,
        }

        with st.spinner("DeepSeek R1 is extracting temporal events..."):
            result = api_call("POST", "/ingest", stored_key, json=payload)

        if "error" not in result:
            st.success(f"✅ Ingested **{result.get('ingested_count', 0)} events** into temporal memory")

            svo_tuples = result.get("svo_tuples", [])
            if svo_tuples:
                st.markdown("<div class='section-label'>Extracted SVO Tuples</div>", unsafe_allow_html=True)
                for svo in svo_tuples:
                    st.markdown(f"""
                    <div class="timeline-event">
                        <div class="svo">
                            <strong>{svo.get('subject', '?')}</strong>
                            <span style="color:#6B7194"> → </span>
                            <em>{svo.get('verb', '?')}</em>
                            <span style="color:#6B7194"> → </span>
                            {svo.get('object', '?')}
                        </div>
                        <div class="meta">
                            confidence: {svo.get('confidence', 0):.0%}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.error(result["error"])
    elif not stored_key:
        st.warning("Paste your API key in the sidebar first.")


elif page == "⚲ Query Memory":
    st.markdown("<div class='section-label'>Temporal Retrieval</div>", unsafe_allow_html=True)
    st.markdown("## Query the Memory")
    st.markdown("*Ask in natural language. Chronos searches across time and meaning.*")

    query = st.text_input("", placeholder="What happened with contracts this quarter?", label_visibility="collapsed")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        start_date = st.date_input("From", value=None)
    with col2:
        end_date = st.date_input("To", value=None)
    with col3:
        max_results = st.slider("Results", 1, 50, 20)

    if st.button("🔍 Search Temporal Memory") and query and stored_key:
        payload = {"query": query, "max_results": max_results}
        if start_date:
            payload["time_range"] = payload.get("time_range", {})
            payload["time_range"]["start"] = datetime.combine(start_date, datetime.min.time()).isoformat()
        if end_date:
            payload["time_range"] = payload.get("time_range", {})
            payload["time_range"]["end"] = datetime.combine(end_date, datetime.max.time()).isoformat()

        with st.spinner("Searching across time..."):
            result = api_call("POST", "/query", stored_key, json=payload)

        if "error" not in result:
            total = result.get("total_found", 0)
            ms = result.get("query_time_ms", 0)

            st.markdown(f"""
            <div style="font-family:'Inter',sans-serif;color:#6B7194;font-size:0.75rem;
                        text-transform:uppercase;letter-spacing:2px;margin:1rem 0">
                {total} events found · {ms:.0f}ms
            </div>
            """, unsafe_allow_html=True)

            for r in result.get("results", []):
                event = r.get("event", {})
                score = r.get("relevance_score", 0)
                source = r.get("provenance", "unknown")
                timestamp = event.get("timestamp", "?")[:16]

                st.markdown(f"""
                <div class="timeline-event">
                    <div class="ts">{timestamp}</div>
                    <div class="svo">
                        <strong>{event.get('subject', '')}</strong> {event.get('verb', '')} {event.get('object', '')}
                    </div>
                    <div class="meta">relevance: {score:.0%} · via {source}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error(result["error"])


elif page == "✦ Agent Chat":
    st.markdown("<div class='section-label'>Temporal Agent</div>", unsafe_allow_html=True)
    st.markdown("## Converse with Memory")
    st.markdown("*An agent that remembers. Ask anything — it searches your temporal memory first.*")

    # Chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask your temporally-aware agent...")

    if prompt and stored_key:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Reasoning with temporal memory..."):
                result = api_call("POST", "/agent/run", stored_key, json={
                    "prompt": prompt,
                    "thread_id": st.session_state.get("thread_id"),
                })

            if "error" not in result:
                response = result.get("response", "No response")
                st.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.session_state["thread_id"] = result.get("thread_id")

                ev_ret = result.get("events_retrieved", 0)
                ev_cre = result.get("events_created", 0)
                if ev_ret or ev_cre:
                    st.caption(f"🕰️ {ev_ret} memories recalled · {ev_cre} new memories formed")
            else:
                st.error(result["error"])
    elif prompt:
        st.warning("Paste your API key in the sidebar first.")


elif page == "⚙ Connect Tool":
    st.markdown("<div class='section-label'>SaaS Integration</div>", unsafe_allow_html=True)
    st.markdown("## Connect a Tool")
    st.markdown("*Register any SaaS API — agents will discover and use it automatically.*")

    with st.form("connect_form"):
        name = st.text_input("Tool Name", placeholder="Stripe, Notion, Slack...")
        description = st.text_area("Description", placeholder="What does this tool do?", height=80)
        base_url = st.text_input("Base API URL", placeholder="https://api.myproduct.com")
        auth_header = st.text_input("Auth Header", value="Authorization")

        st.markdown("**Endpoints** *(JSON)*")
        endpoints_json = st.text_area(
            "Endpoints",
            value='[{"method": "GET", "path": "/api/data", "description": "Fetch data"}]',
            height=80,
            label_visibility="collapsed",
        )

        submitted = st.form_submit_button("🔗 Connect Tool")

        if submitted and stored_key:
            try:
                endpoints = json.loads(endpoints_json)
                result = api_call("POST", "/connect", stored_key, json={
                    "name": name, "description": description,
                    "base_url": base_url, "auth_header": auth_header,
                    "endpoints": endpoints,
                })
                if "error" not in result:
                    st.success(f"✅ {result.get('message', 'Connected!')}")
                else:
                    st.error(result["error"])
            except json.JSONDecodeError:
                st.error("Invalid JSON in endpoints field")
        elif submitted:
            st.warning("Paste your API key in the sidebar first.")


elif page == "▤ Usage & Billing":
    st.markdown("<div class='section-label'>Account</div>", unsafe_allow_html=True)
    st.markdown("## Usage & Billing")

    if stored_key:
        result = api_call("GET", "/billing/usage", stored_key)

        if "error" not in result:
            tier = result.get("tier", "explorer")
            usage = result.get("usage", {})

            # Tier badge
            tier_class = f"tier-{tier}"
            st.markdown(f"""
            <div style="text-align:center;margin:1.5rem 0 2.5rem">
                <span class="tier-badge {tier_class}">{tier}</span>
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)

            events = usage.get("events", {})
            with c1:
                st.metric("Events Used", f"{events.get('used', 0):,}",
                          f"{events.get('remaining', 0):,} remaining")

            orch = usage.get("orchestration", {})
            with c2:
                remaining = orch.get("remaining", 0)
                st.metric("Orchestration", f"{orch.get('used', 0):,}",
                          f"{remaining if isinstance(remaining, str) else f'{remaining:,}'} remaining")

            conn = usage.get("connectors", {})
            with c3:
                st.metric("Connected Tools", f"{conn.get('used', 0)}",
                          f"of {conn.get('limit', 0)} slots")

            # Pricing table
            st.markdown("<hr class='editorial-rule'>", unsafe_allow_html=True)
            st.markdown("<div class='section-label'>Pricing</div>", unsafe_allow_html=True)
            st.markdown("### Temporal Memory Tiers")

            pricing = {
                "": ["**Explorer**", "**Builder**", "**Scale**"],
                "Price": ["Free", "$49/month", "$249/month"],
                "Events/mo": ["10,000", "500,000", "5,000,000"],
                "Orchestration": ["100", "10,000", "Unlimited"],
                "Connected Tools": ["3", "25", "Unlimited"],
                "Retention": ["30 days", "1 year", "Unlimited"],
                "Support": ["Community", "Priority email", "Dedicated Slack"],
            }
            st.table(pricing)
        else:
            st.error(result["error"])
    else:
        st.info("Paste your API key in the sidebar to view usage.")


elif page == "⚷ API Keys":
    st.markdown("<div class='section-label'>Authentication</div>", unsafe_allow_html=True)
    st.markdown("## Generate API Key")
    st.markdown("*Create a new key to authenticate with Chronos OS. Store it safely — it's shown only once.*")

    tier = st.selectbox("Tier", ["explorer", "builder", "scale"])

    if st.button("🔑 Generate Key"):
        result = api_call("POST", f"/billing/keys?tier={tier}")

        if "error" not in result:
            st.success("Key generated. Store it in a safe place — it cannot be retrieved again.")
            st.code(result.get("api_key", ""), language=None)

            st.markdown(f"""
            <div class="timeline-event">
                <div class="ts">Source ID</div>
                <div class="svo">{result.get('source_id', '?')}</div>
                <div class="meta">tier: {result.get('tier', '?')}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error(result["error"])


# ---------------------------------------------------------------------------
# Footer — Chronos Seal
# ---------------------------------------------------------------------------

st.markdown("""
<div class="chronos-footer">
    <span class="seal-small">🕰️</span>
    Chronos OS v0.1.0 — Curated with continuity in mind.
    <br>© 2026 Chronos Labs
</div>
""", unsafe_allow_html=True)
