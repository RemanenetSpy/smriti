---
title: Smriti — Temporal Memory API for AI Agents
emoji: 🕰️
colorFrom: red
colorTo: gray
sdk: docker
pinned: false
---

<p align="center">
  <img src="https://img.shields.io/badge/Status-Live-4ADE80?style=for-the-badge" alt="Live" />
  <img src="https://img.shields.io/badge/MCP-Claude%20%7C%20Cursor%20%7C%20VS%20Code-6B7194?style=for-the-badge" alt="MCP" />
  <img src="https://img.shields.io/badge/Free%20Tier-10K%20events%2Fmo-C7AB6B?style=for-the-badge" alt="Free" />
  <img src="https://img.shields.io/badge/Memory-SVO%20%2B%20pgvector-4ADE80?style=for-the-badge" alt="Memory" />
</p>

<h1 align="center">🕰️ Smriti — Temporal AI Memory</h1>
<p align="center"><em>Long-term memory for AI agents. Structured. Causal. Searchable.</em></p>
<p align="center">
  <strong>Give any AI agent persistent, temporal long-term memory in 5 minutes.</strong><br>
  Smriti decomposes text into Subject-Verb-Object (SVO) causal events, stores them in<br>
  PostgreSQL + pgvector, and lets agents query what happened, when, and why —<br>
  across any session, tool, or conversation.
</p>

> **Keywords:** `mcp-server` `ai-agent-memory` `long-term-memory` `persistent-memory` `claude-memory` `cursor-mcp` `llm-memory` `agent-memory` `memory-mcp` `temporal-memory` `svo-extraction` `pgvector` `langchain-memory` `mem0-alternative` `ai-memory-api` `claude-desktop-mcp` `cursor-ai-memory` `ai-agent-persistent-memory`

---

## Table of Contents

- [What is Smriti?](#what-is-smriti)
- [Quick Start (5 Minutes)](#quick-start-5-minutes)
- [MCP Server — Claude, Cursor, VS Code](#-mcp-server--claude-cursor-vs-code)
- [REST API Reference](#rest-api-reference)
- [Architecture](#architecture)
- [Dashboard Guide](#dashboard-guide)
- [Pricing Tiers](#pricing-tiers)
- [Configuration](#configuration)
- [Integration Examples](#integration-examples)
- [Troubleshooting](#troubleshooting)

---

## What is Smriti?

**The problem:** AI agents are stateless. Every session starts from zero. No memory of decisions made last week, no recall of past conversations, no awareness of what changed. Every agent you build is a goldfish.

**The solution:** Smriti is a **temporal memory API** — a plug-in long-term memory layer for any AI agent, MCP host, or SaaS product. It:

1. **Ingests** text from any source — chat, CRM, email, code commits, documents
2. **Decomposes** it into structured `Subject → Verb → Object` causal events using AI
3. **Stores** events in dual stores — PostgreSQL (temporal queries) + pgvector (semantic search)
4. **Retrieves** relevant memories via natural language — *"What happened with Acme Corp last quarter?"*
5. **Powers** agents that actually remember — memory persists across sessions, tools, and models

### What Makes Smriti Different

| Feature | Smriti | Typical RAG | Mem0 | Zep |
|---|---|---|---|---|
| SVO causal extraction | ✅ | ❌ | ❌ | ❌ |
| Temporal bi-calendar | ✅ | ❌ | ❌ | Partial |
| MCP server built-in | ✅ | ❌ | ❌ | ❌ |
| Never deletes (supersession) | ✅ | ❌ | ❌ | ❌ |
| Free tier | ✅ 10K events | ❌ | ✅ limited | Paid |
| Self-hostable | ✅ | ✅ | ❌ | ✅ |

### Real Example

```
INPUT:  "Acme Corp signed a $50,000 contract for Q2 2026"

SMRITI EXTRACTS:
  Subject: Acme Corp
  Verb:    signed
  Object:  a $50,000 contract for Q2 2026
  When:    Q2 2026

MONTHS LATER, ANY AGENT CAN ASK:
  "What are our biggest contracts?"
  → [2026-04-12] Acme Corp signed a $50,000 contract for Q2 2026  (score: 0.92)
```

---

## Quick Start (5 Minutes)

**Live API:** `https://spy9191-chronos-api-backend.hf.space`
**Dashboard:** `https://smriti-kaal.vercel.app`

### Step 1 — Get a Free API Key

```bash
curl -X POST "https://spy9191-chronos-api-backend.hf.space/billing/keys?tier=explorer"
# Returns: {"api_key": "chrn_...", "tier": "explorer"}
```

Or visit [smriti-kaal.vercel.app](https://smriti-kaal.vercel.app) and click **Generate Key**.

### Step 2 — Store a Memory

```bash
curl -X POST https://spy9191-chronos-api-backend.hf.space/ingest \
  -H "X-API-Key: chrn_your_key" \
  -H "Content-Type: application/json" \
  -d '{"source_id": "quickstart", "events": [{"text": "Alice joined the team as lead engineer on July 15"}]}'
```

### Step 3 — Recall It

```bash
curl -X POST https://spy9191-chronos-api-backend.hf.space/query \
  -H "X-API-Key: chrn_your_key" \
  -H "Content-Type: application/json" \
  -d '{"query": "Who joined the team recently?"}'
# Returns: Alice joined the team as lead engineer on July 15 (score: 0.94)
```

### Local Setup

```bash
git clone https://github.com/RemanenetSpy/smriti
cd smriti
pip install -r requirements.txt
cp .env.example .env   # Add your GROQ_API_KEY
python -m uvicorn api.main:app --port 8000
```

---

## 🔌 MCP Server — Claude, Cursor, VS Code

Smriti ships a **Model Context Protocol (MCP)** server that gives any MCP-compatible AI host instant persistent long-term memory — zero custom integration needed.

> Works with: **Claude Desktop**, **Cursor**, **VS Code + Copilot**, **Windsurf**, **Claude Code**, **Continue**, any MCP-compatible client

### 3-Step Setup

```bash
# 1. Install MCP dependencies
pip install -r mcp/requirements.txt

# 2. Set your API key
export SMRITI_API_KEY="chrn_your_api_key_here"

# 3. Test with MCP Inspector
npx @modelcontextprotocol/inspector python -m smriti.mcp
```

### Claude Desktop Config

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "smriti": {
      "command": "python",
      "args": ["-m", "smriti.mcp"],
      "cwd": "/path/to/smriti",
      "env": {
        "SMRITI_API_KEY": "chrn_your_key_here",
        "SMRITI_SOURCE_ID": "claude-desktop"
      }
    }
  }
}
```

### Cursor Config

Edit `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "smriti": {
      "command": "python",
      "args": ["-m", "smriti.mcp"],
      "cwd": "/path/to/smriti",
      "env": {
        "SMRITI_API_KEY": "chrn_your_key_here",
        "SMRITI_SOURCE_ID": "my-project"
      }
    }
  }
}
```

### MCP Tools

| Tool | What It Does | Key Arguments |
|------|-------------|---------------|
| `smriti_remember` | Store a memory — text auto-decomposes into SVO causal events | `text`, `source_id`, `scope`, `timestamp` |
| `smriti_recall` | Hybrid search: semantic + temporal + entity across all memories | `query`, `max_results`, `time_range_start`, `time_range_end` |
| `smriti_timeline` | Chronological event timeline for a time window | `time_range_start`, `time_range_end`, `scope` |
| `smriti_forget` | Find memories to supersede — history is preserved, never deleted | `query`, `scope` |
| `smriti_health` | Service health check | — |
| `smriti_usage` | API usage stats and tier limits | — |

### MCP Resources

| URI | Description |
|-----|-------------|
| `smriti://status` | Live service health and memory counts |
| `smriti://usage` | Current API usage stats and tier limits |
| `smriti://config` | MCP server configuration (non-sensitive) |

### MCP Prompts

| Name | Purpose |
|------|---------|
| `memory-chat` | System prompt for memory-augmented conversations |
| `daily-recap` | Timeline-based daily/weekly recap template |
| `knowledge-extraction` | Bulk knowledge ingestion from documents |

### SSE Transport (Remote / Multi-Client)

```bash
python -m smriti.mcp --transport sse --port 8080
```

> 📖 Full MCP docs: [`mcp/README.md`](mcp/README.md)

---

## REST API Reference

**Base URL:** `https://spy9191-chronos-api-backend.hf.space`
**Auth:** `X-API-Key: chrn_your_key` header on all requests.
**Interactive docs:** [/docs](https://spy9191-chronos-api-backend.hf.space/docs)

---

### `POST /billing/keys` — Generate API Key

No auth required.

```bash
curl -X POST "https://spy9191-chronos-api-backend.hf.space/billing/keys?tier=explorer"
```

```json
{
  "api_key": "chrn_abc123...",
  "tier": "explorer",
  "message": "Save this API key now — it cannot be retrieved later."
}
```

---

### `POST /ingest` — Store Memories

| Field | Type | Required | Description |
|---|---|---|---|
| `source_id` | string | ✅ | Data source identifier |
| `events` | array | ✅ | List of `{text, timestamp?, metadata?}` objects |
| `parse_svo` | bool | No | Enable AI SVO extraction (default: `true`) |
| `scope` | string | No | Memory scope / namespace |

---

### `POST /query` — Search Memory

| Field | Type | Required | Description |
|---|---|---|---|
| `query` | string | ✅ | Natural language question |
| `time_range` | object | No | `{start, end}` ISO datetimes |
| `source_ids` | array | No | Filter by specific sources |
| `max_results` | int | No | 1–100 (default: 20) |
| `semantic_weight` | float | No | 0.0–1.0 (default: 0.5) |

---

### `POST /agent/run` — Chat with Memory-Aware AI

```bash
curl -X POST https://spy9191-chronos-api-backend.hf.space/agent/run \
  -H "X-API-Key: chrn_your_key" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Summarize everything that happened recently", "thread_id": null}'
```

---

### `GET /health` — Health Check

```bash
curl https://spy9191-chronos-api-backend.hf.space/health
# {"status": "healthy", "stores": {"postgres_events": 4, "pgvector_embeddings": 4}}
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Smriti v0.1.0                             │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │ MCP Server   │  │ REST API     │  │  Agent (LangGraph) │  │
│  │ 6 tools      │  │ FastAPI      │  │  POST /agent/run   │  │
│  │ Claude/Cursor│  │ /ingest      │  │  Memory → LLM      │  │
│  └──────┬───────┘  │ /query       │  └─────────┬──────────┘  │
│         │          └──────┬───────┘            │             │
│  ┌──────▼──────────────────▼────────────────────▼──────────┐  │
│  │                  🧠 Memory Core                         │  │
│  │  ┌──────────────────────┐  ┌──────────────────────────┐  │  │
│  │  │  Event Calendar      │  │  Embedding Index         │  │  │
│  │  │  (PostgreSQL/Neon)   │  │  (pgvector)              │  │  │
│  │  │  • SVO tuples        │  │  • Semantic vectors      │  │  │
│  │  │  • Timestamps        │  │  • Cosine similarity     │  │  │
│  │  │  • Supersession log  │  │  • all-MiniLM-L6-v2      │  │  │
│  │  └──────────────────────┘  └──────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │ SVO Parser   │  │ Auth + Tiers │  │ Next.js Dashboard  │  │
│  │ Groq LLM     │  │ API keys     │  │ smriti-kaal.vercel │  │
│  └──────────────┘  └──────────────┘  └────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### Deployments

| Component | Platform | URL |
|---|---|---|
| **Frontend Dashboard** | Vercel (Next.js) | [smriti-kaal.vercel.app](https://smriti-kaal.vercel.app) |
| **Backend API** | Hugging Face Spaces (Docker) | [spy9191-chronos-api-backend.hf.space](https://spy9191-chronos-api-backend.hf.space) |

### File Structure

```
smriti/
├── api/                        REST API (FastAPI)
├── mcp/                        MCP Server (Claude / Cursor / VS Code)
│   ├── server.py               FastMCP — 6 tools, 3 resources, 3 prompts
│   ├── client.py               HTTP client for Smriti REST API
│   ├── config.py               Environment variable configuration
│   ├── __main__.py             CLI entry (python -m smriti.mcp)
│   ├── claude_desktop_config.json
│   ├── cursor_config.json
│   └── README.md
├── chronos_core/               Memory Core (SVO parser, stores)
├── agent/                      LangGraph Agent
├── chronos-ui/                 Next.js Dashboard (Vercel)
├── benchmark/                  PrecisionMemBench eval harness
├── docs/                       Technical docs
├── Dockerfile
└── requirements.txt
```

---

## Dashboard Guide

Dashboard at **https://smriti-kaal.vercel.app** (or `http://localhost:3000` locally).

| Page | What It Does |
|---|---|
| 🏠 **Overview** | System health, event count, embedding count, AI status |
| 📥 **Ingest Events** | Write events in plain English → AI extracts SVO tuples |
| 🔍 **Query Memory** | Natural language search with date filters and relevance scores |
| 🤖 **Agent Chat** | Conversational AI that reasons with temporal memory |
| 🔗 **Connect Tool** | Register any SaaS API for agent discovery |
| 📊 **Usage & Billing** | Tier badge, usage meters, pricing table |
| 🔑 **API Keys** | Generate and manage keys |

---

## Pricing Tiers

| Feature | Explorer | Builder | Scale |
|---|---|---|---|
| **Price** | Free | $49/month | $249/month |
| **Events/month** | 10,000 | 500,000 | 5,000,000 |
| **MCP sessions** | Unlimited | Unlimited | Unlimited |
| **Orchestration calls** | 100 | 10,000 | Unlimited |
| **Connected tools** | 3 | 25 | Unlimited |
| **Data retention** | 30 days | 1 year | Unlimited |
| **Support** | Community | Priority email | Dedicated Slack |

---

## Configuration

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | ✅ | Free from [console.groq.com](https://console.groq.com) |
| `SMRITI_API_KEY` | MCP only | Your Smriti API key (`chrn_...`) |
| `CHRONOS_DB_URL` | No | Postgres DB URL |
| `PGVECTOR_DB_URL` | No | pgvector DB URL |
| `API_SECRET_KEY` | No | Secret for signing API keys |

### MCP Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SMRITI_API_KEY` | *(required)* | API key (`chrn_...`) |
| `SMRITI_BASE_URL` | `https://spy9191-chronos-api-backend.hf.space` | API base URL |
| `SMRITI_SOURCE_ID` | `mcp-client` | Default source namespace |
| `SMRITI_SCOPE` | `default` | Default memory scope |
| `SMRITI_MAX_RESULTS` | `20` | Default max results |
| `SMRITI_PARSE_SVO` | `true` | Enable SVO extraction |
| `SMRITI_TIMEOUT` | `30.0` | HTTP timeout (seconds) |

### Tech Stack

| Component | Technology |
|---|---|
| **API Framework** | FastAPI + Uvicorn |
| **MCP Framework** | FastMCP (Model Context Protocol) |
| **Structured Storage** | Neon PostgreSQL |
| **Vector Search** | pgvector + sentence-transformers |
| **Embedding Model** | all-MiniLM-L6-v2 (HuggingFace) |
| **SVO Parser / LLM** | Llama 3.x via Groq |
| **Agent Framework** | LangGraph + LangChain |
| **Dashboard** | Next.js + React (Vercel) |
| **Auth** | SHA-256 hashed API keys |

---

## Integration Examples

### Python

```python
import httpx

API = "https://spy9191-chronos-api-backend.hf.space"
KEY = "chrn_your_key_here"
HEADERS = {"X-API-Key": KEY}

# Store a memory
httpx.post(f"{API}/ingest", headers=HEADERS, json={
    "source_id": "my-app",
    "events": [{"text": "User completed onboarding on July 15"}]
})

# Recall it
result = httpx.post(f"{API}/query", headers=HEADERS, json={
    "query": "What did the user do?"
})
print(result.json()["results"])
```

### JavaScript / Node.js

```javascript
const API = "https://spy9191-chronos-api-backend.hf.space";
const headers = { "X-API-Key": "chrn_your_key", "Content-Type": "application/json" };

await fetch(`${API}/ingest`, {
  method: "POST", headers,
  body: JSON.stringify({
    source_id: "my-web-app",
    events: [{ text: "Customer upgraded to Pro plan" }]
  })
});

const res = await fetch(`${API}/query`, {
  method: "POST", headers,
  body: JSON.stringify({ query: "Who upgraded recently?" })
});
console.log(await res.json());
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| **"Cannot connect to API"** | Check `python -m uvicorn api.main:app --port 8000` is running |
| **"No GROQ_API_KEY set"** | Add `GROQ_API_KEY=gsk_...` to `.env` |
| **"Missing API key"** | Add `X-API-Key: chrn_...` header to all requests |
| **Query returns 0 results** | Ingest some events first via `POST /ingest` |
| **Slow first startup** | Embedding model (~80MB) downloads once on first run |
| **MCP not connecting** | Run `npx @modelcontextprotocol/inspector python -m smriti.mcp` to test |
| **MCP tools not appearing** | Check `SMRITI_API_KEY` is set in the env block of your host config |

---

<p align="center">
  <em>🕰️ Memory that persists. Context that continues.</em><br>
  <strong>© 2026 Smriti / Chronos Labs</strong>
</p>
