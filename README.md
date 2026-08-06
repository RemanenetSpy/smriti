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

> **Give any AI persistent, temporal long-term memory in 5 minutes.**
> Smriti decomposes text into Subject-Verb-Object (SVO) causal events, stores them in PostgreSQL + pgvector, and lets agents query what happened, when, and why.

---

## 📖 What is Smriti?

**The Problem:** AI agents are stateless. Every session starts from zero. They have no memory of past decisions, conversations, or changes in state.
**The Solution:** Smriti is a **temporal memory layer**. It gives AI agents a hippocampus that persists across sessions and models.

| Feature | Smriti | Traditional RAG |
|---|---|---|
| **Structure** | **SVO Extraction:** Breaks text into `Subject → Verb → Object` | **Vector Sludge:** Dumps full paragraphs into a vector DB |
| **Time** | **Temporal Awareness:** Knows exact chronological order | **Timeless:** Cannot distinguish old facts from new |
| **Updates** | **Supersession:** Safely overrides facts without deleting history | **Overwrite:** Hard deletes or confusing duplicates |

---

## 🚀 Quick Start (5 Minutes)

**1. Get a Free API Key**
```bash
curl -X POST "https://spy9191-chronos-api-backend.hf.space/billing/keys?tier=explorer"
```

**2. Store a Memory**
```bash
curl -X POST https://spy9191-chronos-api-backend.hf.space/ingest \
  -H "X-API-Key: chrn_your_key" \
  -d '{"source_id": "demo", "events": [{"text": "Alice joined as Lead Engineer on July 15"}]}'
```

**3. Recall It**
```bash
curl -X POST https://spy9191-chronos-api-backend.hf.space/query \
  -H "X-API-Key: chrn_your_key" \
  -d '{"query": "Who joined the team recently?"}'
```

### What You Get Back
```json
{
  "results": [
    {
      "subject": "Alice",
      "verb": "joined",
      "object": "the team as Lead Engineer",
      "timestamp": "2026-07-15T00:00:00Z",
      "confidence_score": 0.94
    }
  ]
}
```

---

## 🔌 MCP Server (Claude, Cursor, VS Code)

Smriti ships with a built-in **Model Context Protocol (MCP)** server, giving your local AI tools instant memory without you writing a single API call.

### 1. Install & Configure
```bash
pip install -r mcp/requirements.txt
```

<details>
<summary><b>Setup for Claude Desktop</b></summary>

Add this to your `claude_desktop_config.json`:
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
</details>

<details>
<summary><b>Setup for Cursor</b></summary>

Add this to `.cursor/mcp.json` in your project root:
```json
{
  "mcpServers": {
    "smriti": {
      "command": "python",
      "args": ["-m", "smriti.mcp"],
      "cwd": "/path/to/smriti",
      "env": {
        "SMRITI_API_KEY": "chrn_your_key_here",
        "SMRITI_SOURCE_ID": "cursor-project"
      }
    }
  }
}
```
</details>

### 2. Available MCP Tools

| Tool | What It Does |
|------|-------------|
| `smriti_remember` | Store text; auto-extracts causal SVO events |
| `smriti_recall` | Hybrid search (semantic + temporal) across all memories |
| `smriti_timeline` | Generate a chronological timeline of events |
| `smriti_forget` | Supersede outdated memories cleanly |
| `smriti_health` | View service health status |

---

## 🏗️ The 4-Layer Architecture Pipeline

When you send text to Smriti, it passes through four discrete layers:

1. **Ingest Gate** — Accepts raw, chaotic text from chat logs, emails, or code.
2. **Decomposition** — The Groq LLM strips fluff and extracts structured `Subject → Verb → Object` tuples.
3. **Temporal Binding** — Assigns exact temporal boundaries to track state changes over time.
4. **Dual-Store Indexing** — Saves to PostgreSQL (for exact chronological queries) and pgvector (for fuzzy semantic search).

---

## 📖 REST API Reference

**Base URL:** `https://spy9191-chronos-api-backend.hf.space`  
**Auth:** Include header `X-API-Key: chrn_your_key`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/billing/keys` | POST | Generate a new API key |
| `/ingest` | POST | Send raw text to be converted into structured memories |
| `/query` | POST | Natural language memory retrieval |
| `/agent/run` | POST | Chat directly with our memory-aware LangGraph agent |
| `/health` | GET | System uptime and DB status |

---

## 💻 Integration Examples

### Node.js / JavaScript
```javascript
const headers = { "X-API-Key": "chrn_...", "Content-Type": "application/json" };

// Remember
await fetch("https://spy9191-chronos-api-backend.hf.space/ingest", {
  method: "POST", headers,
  body: JSON.stringify({ source_id: "app", events: [{ text: "Upgraded to Pro" }] })
});

// Recall
const res = await fetch("https://spy9191-chronos-api-backend.hf.space/query", {
  method: "POST", headers,
  body: JSON.stringify({ query: "Who upgraded?" })
});
console.log(await res.json());
```

### Python
```python
import httpx

API = "https://spy9191-chronos-api-backend.hf.space"
HEADERS = {"X-API-Key": "chrn_..."}

# Remember
httpx.post(f"{API}/ingest", headers=HEADERS, json={
    "source_id": "my-app",
    "events": [{"text": "User completed onboarding on July 15"}]
})

# Recall
result = httpx.post(f"{API}/query", headers=HEADERS, json={
    "query": "What did the user do?"
})
print(result.json()["results"])
```

---

## ⚙️ Environment Configuration

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | ✅ | Required for local hosting. Free from [console.groq.com](https://console.groq.com) |
| `SMRITI_API_KEY` | MCP only | Your Smriti API key (`chrn_...`) |
| `CHRONOS_DB_URL` | No | Override default PostgreSQL URL |
| `PGVECTOR_DB_URL` | No | Override default pgvector URL |

---

## 📊 Dashboard & Pricing

Manage your memories, keys, and view timelines via the Dashboard:  
**[smriti-kaal.vercel.app](https://smriti-kaal.vercel.app)**

| Tier | Price | Limits |
|---|---|---|
| **Explorer** | Free | 10,000 events/mo, 3 connected tools |
| **Builder** | $49/mo | 500,000 events/mo, 25 tools |
| **Scale** | $249/mo | 5,000,000 events/mo, unlimited tools |

---

<p align="center">
  <em>🕰️ Memory that persists. Context that continues.</em><br>
  <strong>© 2026 Smriti / Chronos Labs</strong>
</p>
