---
title: Chronos API Backend
emoji: 🕰️
colorFrom: red
colorTo: gray
sdk: docker
pinned: false
---

<p align="center">
  <img src="https://img.shields.io/badge/Status-Live-4ADE80?style=for-the-badge" alt="Live" />
  <img src="https://img.shields.io/badge/AI-Llama%203.3%2070B-C7AB6B?style=for-the-badge" alt="AI" />
  <img src="https://img.shields.io/badge/Free%20Tier-10K%20events%2Fmo-6B7194?style=for-the-badge" alt="Free" />
</p>

<h1 align="center">🕰️ CHRONOS OS</h1>
<p align="center"><em>Temporal AI Agent Ecosystem — Letters to the Future, for agents.</em></p>
<p align="center">
  <strong>Give any AI agent structured, temporal long-term memory.</strong><br>
  Chronos decomposes text into Subject-Verb-Object events, stores them across dual calendars,<br>
  and lets agents query what happened, when, and why — across any connected SaaS tool.
</p>

---

## Table of Contents

- [What is Chronos OS?](#what-is-chronos-os)
- [Architecture](#architecture)
- [Quick Start (5 Minutes)](#quick-start-5-minutes)
- [API Reference](#api-reference)
- [Dashboard Guide](#dashboard-guide)
- [Agent System](#agent-system)
- [Pricing Tiers](#pricing-tiers)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## What is Chronos OS?

**The problem:** AI agents are goldfish. They process a request, forget everything, and start from zero next time. No memory of what happened yesterday, last week, or across your other tools.

**The solution:** Chronos OS is a **temporal memory API** that any AI agent or SaaS product can plug into. It:

1. **Ingests** text from any source (CRM, chat, email, code commits...)
2. **Decomposes** it into structured Subject-Verb-Object events using AI (Llama 3.3 70B via Groq)
3. **Stores** events in dual calendars — SQLite for temporal queries, ChromaDB for semantic search
4. **Retrieves** relevant memories via natural language — "What happened with Acme Corp last quarter?"
5. **Powers** agents that actually remember — an AI that knows *your* history

### Real Example

```
INPUT:  "Acme Corp signed a $50,000 contract for Q2 2026"

CHRONOS EXTRACTS:
  Subject: Acme Corp
  Verb:    signed
  Object:  a $50,000 contract for Q2 2026
  When:    Q2 2026

LATER, ANY AGENT CAN ASK:
  "What happened with contracts?"
  → [2026-04-12] Acme Corp signed a $50,000 contract for Q2 2026
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    CHRONOS OS v0.1.0                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │ POST /ingest│  │ POST /query  │  │ POST /agent/run    │  │
│  │  Raw text → │  │  NL search → │  │  Prompt → Memory   │  │
│  │  SVO events │  │  Hybrid rank │  │  → LLM → Response  │  │
│  └──────┬──────┘  └──────┬───────┘  └─────────┬──────────┘  │
│         │                │                     │             │
│  ┌──────▼────────────────▼─────────────────────▼──────────┐  │
│  │              🧠 Memory Core                            │  │
│  │  ┌──────────────────┐  ┌──────────────────────────┐    │  │
│  │  │  Event Calendar  │  │    Embedding Index       │    │  │
│  │  │  (SQLite)        │  │    (ChromaDB)            │    │  │
│  │  │  • SVO tuples    │  │    • Semantic vectors    │    │  │
│  │  │  • Timestamps    │  │    • Cosine similarity   │    │  │
│  │  │  • Turn history  │  │    • Fast nearest-neighbor│   │  │
│  │  └──────────────────┘  └──────────────────────────┘    │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │ SVO Parser   │  │ Auth + Tiers │  │ Razorpay Billing   │  │
│  │ Llama 3.3 70B│  │ API keys     │  │ Explorer/Builder/  │  │
│  │ via Groq API │  │ SHA-256 hash │  │ Scale              │  │
│  └──────────────┘  └──────────────┘  └────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### File Structure

```
chronos-hub/
├── chronos_core/           🧠 Memory Core
│   ├── models.py           Pydantic models, tier config, pricing
│   ├── svo_parser.py       AI event extraction (Groq / Llama 3.3)
│   ├── memory_store.py     SQLite dual calendars (events + turns)
│   └── vector_store.py     ChromaDB semantic search (sentence-transformers)
│
├── api/                    🌐 FastAPI Gateway
│   ├── main.py             App entry, CORS, lifespan
│   ├── auth.py             API key auth, tier quota enforcement
│   ├── deps.py             Dependency injection (singletons)
│   └── routes/
│       ├── ingest.py       POST /ingest — feed events
│       ├── query.py        POST /query — search memory
│       ├── connectors.py   POST /connect — register SaaS tools
│       ├── agent.py        POST /agent/run — chat with memory
│       └── billing.py      Razorpay checkout, usage, key generation
│
├── agent/                  🤖 LangGraph Agent Runner
│   ├── graph.py            State graph: memory → model → response
│   ├── nodes.py            Processing nodes (retrieve, call LLM)
│   └── tools.py            Built-in tools for agents
│
├── dashboard/              📊 Streamlit Dashboard
│   └── app.py              7-page UI (navy+gold Chronos design)
│
├── .env                    Environment variables (your keys)
├── .env.example            Template
├── requirements.txt        Python dependencies
└── test_quick.py           Integration test script
```

---

## Quick Start (5 Minutes)

### Prerequisites

- Python 3.11+
- A free Groq API key from [console.groq.com](https://console.groq.com)

### Step 1 — Install

```bash
cd chronos-hub
pip install -r requirements.txt
```

### Step 2 — Configure

```bash
# Copy the template
cp .env.example .env

# Edit .env and add your Groq key:
# GROQ_API_KEY=gsk_your_key_here
```

### Step 3 — Start the API

```bash
python -m uvicorn api.main:app --port 8000
```

You should see:
```
✅ Chronos OS ready — all systems online
Uvicorn running on http://127.0.0.1:8000
```

### Step 4 — Start the Dashboard

```bash
# In a second terminal:
python -m streamlit run dashboard/app.py --server.port 8501
```

Open **http://localhost:8501** in your browser.

### Step 5 — Test It

```bash
python test_quick.py
```

Expected output:
```
=== GENERATING API KEY ===
Key: chrn_abc123...

=== INGESTING EVENTS ===
Ingested: 4 events
SVO tuples found: 4

=== QUERYING MEMORY ===
Found: 4 results in ~80ms

=== ALL TESTS PASSED ===
```

---

## API Reference

**Base URL:** `http://localhost:8000`
**Auth:** Include your API key in the `X-API-Key` header.
**Docs:** Open `http://localhost:8000/docs` for interactive Swagger UI.

---

### `POST /billing/keys` — Generate API Key

No auth required. Creates a new API key.

```bash
curl -X POST "http://localhost:8000/billing/keys?tier=explorer"
```

**Response:**
```json
{
  "api_key": "chrn_abc123...",
  "source_id": "src_7277b1709a854375",
  "tier": "explorer",
  "message": "⚠️ Save this API key now — it cannot be retrieved later."
}
```

---

### `POST /ingest` — Feed Events

Send raw text; the AI extracts structured SVO events automatically.

```bash
curl -X POST http://localhost:8000/ingest \
  -H "X-API-Key: chrn_your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "source_id": "my-crm",
    "events": [
      {"text": "Acme Corp signed a $50,000 contract for Q2 2026"},
      {"text": "Jane was promoted to VP of Engineering on March 15"},
      {"text": "Server migration completed from AWS to Railway on April 1"}
    ],
    "parse_svo": true
  }'
```

**Response:**
```json
{
  "ingested_count": 3,
  "event_ids": ["abc123", "def456", "ghi789"],
  "svo_tuples": [
    {
      "subject": "Acme Corp",
      "verb": "signed",
      "object": "a $50,000 contract for Q2 2026",
      "confidence": 0.95
    }
  ],
  "turn_ids": ["turn_1", "turn_2", "turn_3"]
}
```

**Parameters:**

| Field | Type | Required | Description |
|---|---|---|---|
| `source_id` | string | ✅ | Identifies the data source |
| `events` | array | ✅ | List of `{text, timestamp?, metadata?}` objects |
| `parse_svo` | bool | No | Enable AI extraction (default: `true`) |

---

### `POST /query` — Search Memory

Natural language search with optional time filtering.

```bash
curl -X POST http://localhost:8000/query \
  -H "X-API-Key: chrn_your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What happened with contracts?",
    "max_results": 10
  }'
```

**Response:**
```json
{
  "results": [
    {
      "event": {
        "subject": "Acme Corp",
        "verb": "signed",
        "object": "a $50,000 contract for Q2 2026",
        "timestamp": "2026-04-12T18:28:17Z"
      },
      "relevance_score": 0.92,
      "provenance": "semantic"
    }
  ],
  "total_found": 1,
  "query_time_ms": 80.0
}
```

**Parameters:**

| Field | Type | Required | Description |
|---|---|---|---|
| `query` | string | ✅ | Natural language question |
| `time_range` | object | No | `{start, end}` ISO datetimes |
| `source_ids` | array | No | Filter by specific sources |
| `max_results` | int | No | 1–100 (default: 20) |
| `semantic_weight` | float | No | 0.0–1.0 (default: 0.5) |

---

### `POST /agent/run` — Chat with Agent

Conversational AI with full temporal memory access.

```bash
curl -X POST http://localhost:8000/agent/run \
  -H "X-API-Key: chrn_your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Summarize everything that happened recently",
    "thread_id": null
  }'
```

**Response:**
```json
{
  "thread_id": "thread_abc123",
  "response": "Based on your temporal memory, here's what happened recently...",
  "events_retrieved": 4,
  "events_created": 0
}
```

---

### `POST /connect` — Register a SaaS Tool

```bash
curl -X POST http://localhost:8000/connect \
  -H "X-API-Key: chrn_your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Stripe",
    "description": "Payment processing",
    "base_url": "https://api.stripe.com",
    "auth_header": "Authorization",
    "endpoints": [
      {"method": "GET", "path": "/v1/invoices", "description": "List invoices"}
    ]
  }'
```

---

### `GET /billing/usage` — Check Usage

```bash
curl http://localhost:8000/billing/usage \
  -H "X-API-Key: chrn_your_key"
```

---

### `GET /health` — Health Check

```bash
curl http://localhost:8000/health
```

```json
{
  "status": "healthy",
  "stores": {"sqlite_events": 4, "chroma_embeddings": 4}
}
```

---

## Dashboard Guide

The dashboard runs at **http://localhost:8501** and provides a visual interface for all Chronos features.

| Page | What It Does |
|---|---|
| 🏠 **Overview** | System health, event count, embedding count, AI status |
| 📥 **Ingest Events** | Write events in plain English → AI extracts SVO tuples |
| 🔍 **Query Memory** | Natural language search with date filters and relevance |
| 🤖 **Agent Chat** | Conversational AI that reasons with your temporal memory |
| 🔗 **Connect Tool** | Register any SaaS API for agent discovery |
| 📊 **Usage & Billing** | Tier badge, usage meters, pricing table |
| 🔑 **API Keys** | Generate new keys with one click |

### How to Use the Dashboard

1. Open **http://localhost:8501**
2. Click **🔑 API Keys** → Click **Generate Key** → Copy the key
3. Paste the key into the **🔑 API Key** field in the sidebar
4. Go to **📥 Ingest Events** → Type events → Click **Ingest Into Memory**
5. Go to **🔍 Query Memory** → Ask a question → See results
6. Go to **🤖 Agent Chat** → Have a conversation with memory-aware AI

---

## Agent System

Chronos includes a **LangGraph-based agent** that automatically:

1. **Retrieves** relevant memories from ChromaDB before responding
2. **Injects** temporal context into the LLM's system prompt
3. **Responds** with awareness of past events, dates, and relationships

### How It Works

```
User: "What's our biggest contract?"
         │
         ▼
┌─────────────────────┐
│ retrieve_memory_node │  ← Searches ChromaDB + SQLite
│ ("contract" → Acme) │     for relevant past events
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  call_model_node    │  ← Llama 3.3 70B (Groq)
│  System prompt +    │     with memory context injected
│  memory context +   │
│  user question      │
└────────┬────────────┘
         │
         ▼
"Based on your records, Acme Corp signed a $50K contract for Q2 2026."
```

### AI Model

| Property | Value |
|---|---|
| **Model** | Llama 3.3 70B Versatile |
| **Provider** | Groq (free tier) |
| **Speed** | 300+ tokens/second |
| **Daily Limit** | 14,400 requests/day |
| **Cost** | Free (no credit card) |

---

## Pricing Tiers

Chronos OS uses a three-tier model with metered overage:

| Feature | Explorer | Builder | Scale |
|---|---|---|---|
| **Price** | Free | $49/month | $249/month |
| **Events/month** | 10,000 | 500,000 | 5,000,000 |
| **Orchestration calls** | 100 | 10,000 | Unlimited |
| **Connected tools** | 3 | 25 | Unlimited |
| **Data retention** | 30 days | 1 year | Unlimited |
| **Agent threads** | 5 | 100 | Unlimited |
| **Event overage (per 1K)** | Hard cap | $0.05 | $0.03 |
| **Orchestration overage** | Hard cap | $0.10 | $0.07 |
| **Support** | Community | Priority email | Dedicated Slack |

---

## Configuration

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | ✅ | Free API key from [console.groq.com](https://console.groq.com) |
| `CHRONOS_DB_PATH` | No | SQLite path (default: `./data/chronos.db`) |
| `CHROMA_PERSIST_DIR` | No | ChromaDB path (default: `./data/chroma`) |
| `API_SECRET_KEY` | No | Secret for signing API keys |
| `RAZORPAY_KEY_ID` | No | Razorpay key ID for billing |
| `RAZORPAY_KEY_SECRET` | No | Razorpay secret key |
| `RAZORPAY_PLAN_BUILDER` | No | Razorpay plan ID for Builder tier |
| `RAZORPAY_PLAN_SCALE` | No | Razorpay plan ID for Scale tier |
| `CHRONOS_API_URL` | No | API URL for dashboard (default: `http://localhost:8000`) |

### Tech Stack

| Component | Technology |
|---|---|
| **API Framework** | FastAPI + Uvicorn |
| **Structured Storage** | SQLite (via aiosqlite) |
| **Vector Search** | ChromaDB + sentence-transformers |
| **Embedding Model** | all-MiniLM-L6-v2 (HuggingFace) |
| **LLM** | Llama 3.3 70B (Groq, free) |
| **Agent Framework** | LangGraph + LangChain |
| **Dashboard** | Streamlit |
| **Billing** | Razorpay |
| **Auth** | SHA-256 hashed API keys |

---

## Troubleshooting

| Problem | Solution |
|---|---|
| **"Cannot connect to API"** | Make sure the API is running: `python -m uvicorn api.main:app --port 8000` |
| **Dashboard won't load** | Start it: `python -m streamlit run dashboard/app.py --server.port 8501` |
| **"No GROQ_API_KEY set"** | Create `.env` file with `GROQ_API_KEY=gsk_your_key` |
| **"Missing API key" on requests** | Add `X-API-Key: chrn_...` header to all API calls |
| **Query returns 0 results** | Ingest some events first via `POST /ingest` |
| **Slow first startup** | The embedding model (~80MB) downloads once from HuggingFace on first run |
| **Agent gives generic response** | Make sure there are ingested events for the agent to recall |

### Running Both Servers

You need **two terminals** running simultaneously:

**Terminal 1 — API Server:**
```bash
cd chronos-hub
python -m uvicorn api.main:app --port 8000
```

**Terminal 2 — Dashboard:**
```bash
cd chronos-hub
python -m streamlit run dashboard/app.py --server.port 8501
```

---

## Integration Examples

### Python SDK Usage

```python
import httpx

API = "http://localhost:8000"
KEY = "chrn_your_key_here"
HEADERS = {"X-API-Key": KEY}

# Ingest an event
httpx.post(f"{API}/ingest", headers=HEADERS, json={
    "source_id": "my-app",
    "events": [{"text": "User completed onboarding on April 12"}]
})

# Query memory
result = httpx.post(f"{API}/query", headers=HEADERS, json={
    "query": "What did the user do?"
})
print(result.json()["results"])  # → onboarding event

# Chat with agent
response = httpx.post(f"{API}/agent/run", headers=HEADERS, json={
    "prompt": "Summarize user activity"
})
print(response.json()["response"])
```

### JavaScript / Node.js

```javascript
const API = "http://localhost:8000";
const headers = { "X-API-Key": "chrn_your_key", "Content-Type": "application/json" };

// Ingest
await fetch(`${API}/ingest`, {
  method: "POST", headers,
  body: JSON.stringify({
    source_id: "my-web-app",
    events: [{ text: "Customer upgraded to Pro plan" }]
  })
});

// Query
const res = await fetch(`${API}/query`, {
  method: "POST", headers,
  body: JSON.stringify({ query: "Who upgraded recently?" })
});
console.log(await res.json());
```

---

<p align="center">
  <em>🕰️ Curated with continuity in mind.</em><br>
  <strong>© 2026 Chronos Labs</strong>
</p>
