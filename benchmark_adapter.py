"""
Smriti ↔ PrecisionMemBench Adapter
=====================================
Bridges the tenurehq/precisionmembench harness to the Smriti API.

Design principles:
  Optimize  — batched ingest (single POST per test case), not one per event
  Adapt     — threshold overridable per-test via payload field
  Efficient — async httpx, reused session, zero blocking I/O
  Flexible  — all config via env vars, sensible defaults

Configuration (environment variables):
  SMRITI_API_URL    = https://spy9191-chronos-api-backend.hf.space
  SMRITI_API_KEY    = chrn_...
  SMRITI_THRESHOLD  = 0.15       (default cosine distance threshold)
  SMRITI_SCOPE_MODE = test_id    (use test case ID as scope → hard isolation)
  ADAPTER_PORT      = 8765

Endpoints served (benchmark harness protocol):
  POST /ingest   — receive benchmark events, forward to Smriti, map IDs
  POST /recall   — query Smriti, return matching benchmark event IDs
  GET  /reset    — flush per-test ID map (called between test cases)
  GET  /health   — liveness check with stats

Usage:
  pip install fastapi uvicorn httpx
  SMRITI_API_KEY=chrn_xxx python benchmark_adapter.py

Benchmark harness call order per test case:
  1. GET /reset
  2. POST /ingest  (one or many times)
  3. POST /recall  (one or many times)
  4. Score computed by harness from /recall response
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import Any

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_URL       = os.getenv("SMRITI_API_URL", "https://spy9191-chronos-api-backend.hf.space")
API_KEY       = os.getenv("SMRITI_API_KEY", "")
SCOPE_MODE    = os.getenv("SMRITI_SCOPE_MODE", "test_id")   # "test_id" | "fixed"
ADAPTER_PORT  = int(os.getenv("ADAPTER_PORT", "8765"))

# Numeric defaults — all overridable by env var (no hardcoded numbers in logic)
# SMRITI_THRESHOLD and SMRITI_SEMANTIC_WEIGHT are read lazily so that the adapter
# picks up any value set BEFORE it starts, without importing the full chronos stack.
def _get_threshold() -> float:
    return float(os.getenv("SMRITI_THRESHOLD") or os.getenv("SMRITI_SIMILARITY_THRESHOLD", "0.15"))

def _get_semantic_weight() -> float:
    return float(os.getenv("SMRITI_SEMANTIC_WEIGHT", "0.7"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("smriti_adapter")

# ---------------------------------------------------------------------------
# State (in-memory, per-test-case)
# ---------------------------------------------------------------------------

# Mapping: benchmark event ID → Smriti event ID
_bench_to_smriti: dict[str, str] = {}
# Reverse mapping (populated lazily)
_smriti_to_bench: dict[str, str] = {}
# Async HTTP client (reused across requests)
_client: httpx.AsyncClient | None = None


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _client
    if not API_KEY:
        logger.warning("SMRITI_API_KEY is not set — API calls will be rejected")
    _client = httpx.AsyncClient(
        base_url=API_URL,
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        timeout=httpx.Timeout(30.0, connect=10.0),
    )
    logger.info(
        f"Adapter started → {API_URL} | "
        f"threshold={_get_threshold()} | "
        f"semantic_weight={_get_semantic_weight()} | "
        f"scope_mode={SCOPE_MODE}"
    )
    yield
    await _client.aclose()


app = FastAPI(
    title="Smriti Benchmark Adapter",
    description="Bridges tenurehq/precisionmembench to the Smriti memory API",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_scope(payload: dict) -> str:
    """
    Derive scope for this test case.
    SCOPE_MODE=test_id  → use test_id field (or 'bench-default') as scope
    SCOPE_MODE=fixed    → always use 'benchmark'
    """
    if SCOPE_MODE == "fixed":
        return "benchmark"
    return str(payload.get("test_id") or payload.get("scope") or "bench-default")


async def _smriti_post(path: str, body: dict) -> dict:
    """POST to Smriti API with error surfacing."""
    r = await _client.post(path, json=body)
    if r.status_code >= 400:
        logger.error(f"Smriti API error {r.status_code} on {path}: {r.text[:300]}")
        raise HTTPException(status_code=502, detail=f"Smriti API: {r.status_code} {r.text[:200]}")
    return r.json()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
async def health() -> dict[str, Any]:
    """Liveness check."""
    return {
        "status": "ok",
        "api_url": API_URL,
        "threshold": THRESHOLD,
        "scope_mode": SCOPE_MODE,
        "mapped_events": len(_bench_to_smriti),
    }


@app.get("/reset")
async def reset() -> dict[str, str]:
    """
    Flush all state between test cases.
    Called by the benchmark harness before each new test.
    """
    _bench_to_smriti.clear()
    _smriti_to_bench.clear()
    logger.info("State reset ✓")
    return {"status": "reset"}


@app.post("/ingest")
async def ingest(payload: dict) -> dict[str, Any]:
    """
    Receive events from the benchmark harness and forward them to Smriti.

    Expected payload:
      {
        "test_id": "test_42",
        "scope":   "work",          # optional, overrides test_id as scope
        "events": [
          {"id": "bench-evt-001", "text": "Alice moved to Seattle"},
          {"id": "bench-evt-002", "text": "Alice's role is VP of Engineering"}
        ]
      }
    """
    scope = _resolve_scope(payload)
    bench_events: list[dict] = payload.get("events", [])

    if not bench_events:
        return {"status": "ok", "ingested": 0}

    # Batch all events into a single Smriti ingest request (EFFICIENT)
    smriti_payload = {
        "source_id": f"bench-{scope}",
        "scope": scope,
        "parse_svo": True,
        "events": [
            {
                "text": ev.get("text", ""),
                "timestamp": ev.get("timestamp"),
                "metadata": ev.get("metadata", {}),
                # Per-event scope override if provided
                "scope": ev.get("scope"),
            }
            for ev in bench_events
        ],
    }

    data = await _smriti_post("/ingest", smriti_payload)
    smriti_ids: list[str] = data.get("event_ids", [])

    # Map benchmark IDs → Smriti IDs
    for bench_ev, smriti_id in zip(bench_events, smriti_ids):
        bench_id = bench_ev.get("id")
        if bench_id and smriti_id:
            _bench_to_smriti[bench_id] = smriti_id
            _smriti_to_bench[smriti_id] = bench_id

    logger.info(
        f"Ingested {len(smriti_ids)} events | scope={scope!r} | "
        f"bench_ids={[e.get('id') for e in bench_events]}"
    )
    return {
        "status": "ok",
        "ingested": len(smriti_ids),
        "scope": scope,
    }


@app.post("/recall")
async def recall(payload: dict) -> dict[str, Any]:
    """
    Query Smriti and return matched benchmark event IDs.

    Expected payload:
      {
        "test_id":   "test_42",
        "query":     "Where did Alice move?",
        "scope":     "work",          # optional
        "threshold": 0.20,            # optional, overrides default
        "max_results": 5
      }

    Response:
      {
        "matched_ids": ["bench-evt-001"],
        "debug": [...]    # full Smriti results for debugging
      }
    """
    scope = _resolve_scope(payload)
    query = payload.get("query", "")
    threshold = float(payload.get("threshold") or _get_threshold())  # per-test override or env default
    max_results = int(payload.get("max_results", 10))

    if not query:
        raise HTTPException(status_code=400, detail="'query' field is required")

    smriti_payload = {
        "query": query,
        "scope": scope,
        "similarity_threshold": threshold,
        "max_results": max_results,
        "semantic_weight": _get_semantic_weight(),  # from SMRITI_SEMANTIC_WEIGHT env var
    }

    data = await _smriti_post("/query", smriti_payload)
    results: list[dict] = data.get("results", [])

    # Map Smriti event IDs back to benchmark IDs
    matched_bench_ids: list[str] = []
    debug_rows: list[dict] = []

    for r in results:
        smriti_id = r.get("event", {}).get("id", "")
        bench_id = _smriti_to_bench.get(smriti_id)
        score = r.get("relevance_score", 0.0)

        debug_rows.append({
            "smriti_id": smriti_id,
            "bench_id": bench_id,
            "score": score,
            "subject": r.get("event", {}).get("subject"),
            "verb":    r.get("event", {}).get("verb"),
            "object":  r.get("event", {}).get("object"),
        })

        if bench_id:
            matched_bench_ids.append(bench_id)

    logger.info(
        f"Recall: '{query[:60]}' → {len(matched_bench_ids)} matched | "
        f"scope={scope!r} | threshold={threshold}"
    )
    return {
        "matched_ids": matched_bench_ids,
        "debug": debug_rows,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(
        "benchmark_adapter:app",
        host="0.0.0.0",
        port=ADAPTER_PORT,
        reload=False,
        log_level="info",
    )
