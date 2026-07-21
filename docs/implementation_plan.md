# Chronos OS — Temporal AI Agent Ecosystem

Transform Chronos from a personal time-capsule app into **Chronos OS**: the infrastructure layer that gives every AI agent and SaaS product structured temporal long-term memory.

## Background

| | Current (MVP) | Target (Chronos OS) |
|---|---|---|
| **Product** | Personal journaling SPA (React/TS/Vite) | Temporal AI Agent Ecosystem |
| **Users** | Individuals writing letters to their future self | AI startups, SaaS builders, agent developers |
| **Stack** | React 19 + localStorage + crypto-js | Python (FastAPI + LangGraph + SQLite + ChromaDB) + **Gemini 2.5 Flash (free)** |
| **Memory** | Base64 encrypted blobs in localStorage | Structured SVO event tuples + dual calendars |
| **Monetization** | Premium waitlist / Stripe demo | Usage-based (events + orchestration calls + marketplace cut) |

The existing React app stays as-is on the Play Store / web — it becomes the **consumer on-ramp**. Chronos OS is a **new, separate Python project** built alongside it.

---

## Decisions (Finalized)

| Decision | Choice | Rationale |
|---|---|---|
| **LLM Provider** | **Google Gemini 2.5 Flash** (free via Google AI Studio) | No cost, 1M token context, generous rate limits, no credit card needed |
| **Deployment** | **Railway** (free tier → ~$5/mo) | One-click deploy, easy scaling |
| **Pricing Model** | Premium 3-tier (see below) | Positioned against Mem0 ($19–$249), Zep (credits), LangSmith ($39/seat) |

> [!WARNING]
> **This is a brand-new Python project** — it does NOT modify your existing React/TS Chronos Vault app. The React app remains untouched.

---

## Proposed Changes

The entire project lives under `c:\Users\reman\OneDrive\Desktop\Chronos OS\chronos-hub\`. Here is the complete file tree we will build:

```
chronos-hub/
├── .env.example              # Environment variable template
├── requirements.txt          # Python dependencies
├── README.md                 # Chronos OS documentation
│
├── chronos_core/             # 🧠 Memory Core (the secret sauce)
│   ├── __init__.py
│   ├── models.py             # Pydantic models for events, SVO tuples, calendars
│   ├── svo_parser.py         # LLM-powered SVO extraction from raw text
│   ├── memory_store.py       # SQLite event calendar + turn calendar
│   └── vector_store.py       # ChromaDB semantic search layer
│
├── api/                      # 🌐 FastAPI Gateway
│   ├── __init__.py
│   ├── main.py               # FastAPI app entry point + CORS + middleware
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── ingest.py         # POST /ingest — universal event ingestion
│   │   ├── query.py          # POST /query — temporal + semantic retrieval
│   │   ├── connectors.py     # POST /connect — register SaaS/agent tools
│   │   ├── agent.py          # POST /agent/run — execute agent with memory
│   │   └── billing.py        # Stripe checkout + usage tracking
│   ├── auth.py               # API key authentication middleware
│   └── deps.py               # Dependency injection (DB sessions, stores)
│
├── agent/                    # 🤖 LangGraph Agent Runner
│   ├── __init__.py
│   ├── graph.py              # LangGraph state graph definition
│   ├── nodes.py              # Agent nodes (call_model, use_tools, retrieve_memory)
│   └── tools.py              # Built-in tools (query_memory, search_connectors)
│
├── dashboard/                # 📊 Streamlit Dashboard
│   └── app.py                # Single-file Streamlit UI
│
└── tests/                    # ✅ Basic tests
    ├── test_svo_parser.py
    ├── test_memory_store.py
    └── test_api.py
```

---

### Component 1: Chronos Memory Core (`chronos_core/`)

> [!NOTE]
> This is the core differentiator — the structured temporal memory layer based on the Chronos research paper's SVO event decomposition + dual calendar architecture.

#### [NEW] [models.py](file:///c:/Users/reman/OneDrive/Desktop/Chronos%20OS/chronos-hub/chronos_core/models.py)
- Pydantic models: `SVOTuple` (subject, verb, object, timestamp, datetime_range, entity_aliases, confidence)
- `EventRecord` — structured event for the Event Calendar (SQLite)
- `TurnRecord` — raw conversation turn for the Turn Calendar (SQLite)
- `IngestPayload` — incoming JSON from any SaaS/agent
- `QueryRequest` — temporal + semantic query spec
- `QueryResult` — ranked results with provenance

#### [NEW] [svo_parser.py](file:///c:/Users/reman/OneDrive/Desktop/Chronos%20OS/chronos-hub/chronos_core/svo_parser.py)
- Uses **Google Gemini 2.5 Flash** (free tier via `google-genai` SDK) for SVO extraction
- Fallback: LiteLLM gateway for swapping to other providers later
- Prompt template: "Extract all Subject-Verb-Object events with timestamps from this text. Return JSON array."
- Regex fallback for simple patterns when LLM quota is exhausted
- Batch processing support for bulk ingestion

#### [NEW] [memory_store.py](file:///c:/Users/reman/OneDrive/Desktop/Chronos%20OS/chronos-hub/chronos_core/memory_store.py)
- **Event Calendar** — SQLite table: `events(id, source_id, subject, verb, object, timestamp, datetime_start, datetime_end, entity_aliases, confidence, metadata_json, created_at)`
- **Turn Calendar** — SQLite table: `turns(id, source_id, role, content, timestamp, event_ids, created_at)`
- Methods: `insert_event()`, `insert_turn()`, `query_temporal()` (SQL WHERE on timestamp ranges), `query_by_entity()`, `multi_hop_query()` (join events across time)
- Connection pooling with `aiosqlite` for async FastAPI

#### [NEW] [vector_store.py](file:///c:/Users/reman/OneDrive/Desktop/Chronos%20OS/chronos-hub/chronos_core/vector_store.py)
- ChromaDB collection `chronos_events` 
- On each event insert: embed the raw text + store with SQLite event_id as metadata
- `semantic_search(query, n_results)` — returns event IDs ranked by relevance
- Hybrid retrieval: vector search → join with SQLite for full context + temporal filtering

---

### Component 2: FastAPI Gateway (`api/`)

#### [NEW] [main.py](file:///c:/Users/reman/OneDrive/Desktop/Chronos%20OS/chronos-hub/api/main.py)
- FastAPI app with CORS middleware (allow all origins for dev)
- Lifespan handler to initialize SQLite + ChromaDB on startup
- Include all route routers
- Health check endpoint at `GET /`

#### [NEW] [routes/ingest.py](file:///c:/Users/reman/OneDrive/Desktop/Chronos%20OS/chronos-hub/api/routes/ingest.py)
- `POST /ingest` — the universal endpoint
- Accepts JSON: `{ "source_id": "stripe-saas-123", "events": [{"text": "...", "timestamp": "..."}] }` or raw conversation turns
- Pipeline: validate → SVO parse → insert into Event Calendar + Turn Calendar + ChromaDB
- Returns: event IDs + extracted SVO tuples
- Usage metering: increment event count for billing

#### [NEW] [routes/query.py](file:///c:/Users/reman/OneDrive/Desktop/Chronos%20OS/chronos-hub/api/routes/query.py)
- `POST /query` — temporal + semantic retrieval
- Accepts: `{ "query": "What contracts changed in Q1?", "time_range": {"start": "...", "end": "..."}, "source_ids": [...] }`
- Hybrid retrieval: ChromaDB semantic → SQLite temporal filter → multi-hop reasoning
- Returns ranked events with provenance chain

#### [NEW] [routes/connectors.py](file:///c:/Users/reman/OneDrive/Desktop/Chronos%20OS/chronos-hub/api/routes/connectors.py)
- `POST /connect` — register a SaaS product's API schema
- Stores tool definitions so agents can discover and call connected products
- `GET /connectors` — list all connected tools
- Non-agentic SaaS instantly becomes agent-actionable

#### [NEW] [routes/agent.py](file:///c:/Users/reman/OneDrive/Desktop/Chronos%20OS/chronos-hub/api/routes/agent.py)
- `POST /agent/run` — execute an agent prompt with full Chronos memory
- Accepts: `{ "prompt": "...", "thread_id": "...", "tools": [...] }`
- Invokes LangGraph agent runner with memory context
- Streams response via SSE or returns final result
- Usage metering: increment orchestration call count

#### [NEW] [routes/billing.py](file:///c:/Users/reman/OneDrive/Desktop/Chronos%20OS/chronos-hub/api/routes/billing.py)
- `POST /billing/checkout` — create Stripe checkout session
- `GET /billing/usage` — current usage stats (events, orchestration calls)
- Premium 3-tier pricing (see Pricing section below)

#### [NEW] [auth.py](file:///c:/Users/reman/OneDrive/Desktop/Chronos%20OS/chronos-hub/api/auth.py)
- API key middleware: validate `X-API-Key` header
- SQLite `api_keys` table: `(key_hash, source_id, tier, events_used, orchestration_used, created_at)`
- Rate limiting per tier

#### [NEW] [deps.py](file:///c:/Users/reman/OneDrive/Desktop/Chronos%20OS/chronos-hub/api/deps.py)
- Dependency injection for FastAPI routes
- Provides: `get_memory_store()`, `get_vector_store()`, `get_svo_parser()`

---

### Component 3: LangGraph Agent Runner (`agent/`)

#### [NEW] [graph.py](file:///c:/Users/reman/OneDrive/Desktop/Chronos%20OS/chronos-hub/agent/graph.py)
- LangGraph `StateGraph` with state: `{ messages, memory_context, tool_results }`
- Nodes: `retrieve_memory` → `call_model` → `tools` (loop) → `END`
- Conditional edges: if tool calls exist → execute tools → loop back to model
- SQLite checkpointer for session persistence

#### [NEW] [nodes.py](file:///c:/Users/reman/OneDrive/Desktop/Chronos%20OS/chronos-hub/agent/nodes.py)
- `retrieve_memory_node()` — queries Chronos memory before each agent turn
- `call_model_node()` — invokes LLM with memory-augmented context
- `execute_tools_node()` — runs tools (including connected SaaS tools)

#### [NEW] [tools.py](file:///c:/Users/reman/OneDrive/Desktop/Chronos%20OS/chronos-hub/agent/tools.py)
- `@tool query_chronos_memory` — agents can query the temporal memory
- `@tool ingest_event` — agents can store new events during execution
- `@tool list_connectors` — discover available SaaS tools
- `@tool call_connector` — invoke a connected SaaS API

---

### Component 4: Streamlit Dashboard (`dashboard/`)

#### [NEW] [app.py](file:///c:/Users/reman/OneDrive/Desktop/Chronos%20OS/chronos-hub/dashboard/app.py)
- **Connect Your Product** — form to paste API key + register tool schema
- **Event Timeline** — visualize all ingested events on a temporal axis (extends "Letters to the Future" UI to B2B)
- **Test Agent** — text input to run agent prompts with live streaming
- **Usage & Billing** — event counts, orchestration calls, tier status
- Premium dark theme matching Chronos branding (deep navy + gold accents)

---

### Component 5: Configuration & Deployment

#### [NEW] [requirements.txt](file:///c:/Users/reman/OneDrive/Desktop/Chronos%20OS/chronos-hub/requirements.txt)
```
fastapi>=0.115.0
uvicorn[standard]>=0.34.0
pydantic>=2.10.0
aiosqlite>=0.21.0
chromadb>=0.6.0
google-genai>=1.0.0
litellm>=1.60.0
langgraph>=0.4.0
langchain-google-genai>=2.0.0
langchain-core>=0.3.0
streamlit>=1.42.0
stripe>=11.0.0
python-dotenv>=1.0.0
httpx>=0.28.0
```

#### [NEW] [.env.example](file:///c:/Users/reman/OneDrive/Desktop/Chronos%20OS/chronos-hub/.env.example)
```
GOOGLE_API_KEY=AIza...                 # Free from Google AI Studio
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
CHRONOS_DB_PATH=./data/chronos.db
CHROMA_PERSIST_DIR=./data/chroma
API_SECRET_KEY=your-secret-for-signing-api-keys
```

#### [NEW] [README.md](file:///c:/Users/reman/OneDrive/Desktop/Chronos%20OS/chronos-hub/README.md)
- Project overview, quickstart, API docs, architecture diagram

---

## Build Schedule

| Day | Focus | Deliverable |
|-----|-------|-------------|
| **Day 1** | Memory Core | `chronos_core/` — SVO parser + dual calendars + vector store, all working with tests |
| **Day 2** | API Gateway | `api/` — `/ingest`, `/query` endpoints live, auth middleware, usage metering |
| **Day 3** | Agent Runner + Connectors | `agent/` — LangGraph graph + `/agent/run` + `/connect` endpoints |
| **Day 4** | Dashboard + Billing | `dashboard/app.py` + Stripe integration + deploy to Railway |
| **Day 5** | Polish + Launch | README, tests, Reddit posts ("Free temporal memory for your AI/SaaS") |

---

## Pricing — Premium 3-Tier Model

Positioned competitively against Mem0 ($19–$249/mo), Zep (credit-based), and LangSmith ($39/seat):

| | **Explorer** (Free) | **Builder** ($49/mo) | **Scale** ($249/mo) |
|---|---|---|---|
| **Events/month** | 10,000 | 500,000 | 5,000,000 |
| **Orchestration calls** | 100 | 10,000 | Unlimited |
| **Connected tools** | 3 | 25 | Unlimited |
| **Retention** | 30 days | 1 year | Unlimited |
| **Agent threads** | 5 | 100 | Unlimited |
| **Support** | Community | Priority email | Dedicated Slack |
| **Event overage** | — | $0.05 / 1k events | $0.03 / 1k events |
| **Orchestration overage** | — | $0.10 / call | $0.07 / call |

> [!TIP]
> **Why these numbers?** Mem0 Pro is $249/mo. LangSmith Plus is $39/seat (but per-seat adds up fast for teams). Zep credits are opaque. Our $49 Builder tier undercuts Mem0 Starter ($19) on raw value (50x more events) while the $249 Scale tier matches Mem0 Pro but adds orchestration + agent runner + marketplace — features they don't have. The "Explorer" free tier is generous enough to hook startups from Reddit.

---

## Verification Plan

### Automated Tests
1. **Unit tests** for SVO parser (mock LLM responses, verify tuple extraction)
2. **Unit tests** for memory_store (insert events, query by time range, multi-hop)
3. **Integration tests** for `/ingest` → `/query` round-trip via `httpx.AsyncClient`
4. **Agent test** — run a sample prompt through LangGraph, verify memory retrieval

### Manual Verification
1. **cURL the API** — ingest sample events, query them back, run an agent prompt
2. **Streamlit dashboard** — connect a mock tool, visualize timeline, test agent chat
3. **Stripe test mode** — create checkout session, verify usage tracking

### Commands
```bash
# Run the API server
cd chronos-hub && uvicorn api.main:app --reload --port 8000

# Run the dashboard
cd chronos-hub && streamlit run dashboard/app.py --server.port 8501

# Run tests
cd chronos-hub && python -m pytest tests/ -v
```
