"""
Smriti PrecisionMemBench Wrapper — v2
======================================
Self-contained FastAPI service implementing the PrecisionMemBench provider API.

Changes from v1:
  - SMRITI_SIMILARITY_THRESHOLD default raised to 0.45 (was 0.25)
    → 0.25 was too strict: true positives weren't returned
  - Type-aware filtering: open_question and resolved beliefs excluded from /search
  - ChromaDB telemetry disabled (was causing 2-second latency per request)
  - Embedding cache: per-process LRU cache for repeated query strings

Environment variables:
  SMRITI_SIMILARITY_THRESHOLD   cosine distance cutoff     (default 0.45)
  SMRITI_EMBED_MODEL            sentence-transformer model (default all-MiniLM-L6-v2)
  SMRITI_PORT                   server port                (default 8080)
"""

from __future__ import annotations

# ── Force offline mode — model is cached, skip the HF network update check ──
import os
os.environ["HF_HUB_OFFLINE"]            = "1"
os.environ["TRANSFORMERS_OFFLINE"]      = "1"
os.environ["HF_DATASETS_OFFLINE"]       = "1"
os.environ["ANONYMIZED_TELEMETRY"]      = "False"   # ChromaDB telemetry off
os.environ["CHROMA_TELEMETRY_ENABLED"]  = "false"   # ChromaDB alt key
# ─────────────────────────────────────────────────────────────────────────────

import sys
import time
import logging
import functools
from dataclasses import dataclass, field
from typing import Optional

import chromadb
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("smriti.benchmark")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

EMBED_MODEL          = os.getenv("SMRITI_EMBED_MODEL", "all-MiniLM-L6-v2")
PORT                 = int(os.getenv("SMRITI_PORT", "8080"))
SIMILARITY_THRESHOLD = float(os.getenv("SMRITI_SIMILARITY_THRESHOLD", "0.45"))

# ---------------------------------------------------------------------------
# Embedding model (loaded once at startup)
# ---------------------------------------------------------------------------

print(f"[smriti] Loading {EMBED_MODEL}…", flush=True)
_model = SentenceTransformer(EMBED_MODEL)
print(f"[smriti] Model ready. threshold={SIMILARITY_THRESHOLD}", flush=True)

# LRU cache for query embeddings (avoids re-encoding the same query string)
@functools.lru_cache(maxsize=512)
def _embed_cached(text: str) -> tuple:
    return tuple(_model.encode(text, normalize_embeddings=True).tolist())

def _embed(text: str) -> list[float]:
    return list(_embed_cached(text))

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

_chroma: chromadb.ClientAPI = chromadb.Client(
    chromadb.Settings(anonymized_telemetry=False)
)

# (user_id, scope) → ChromaDB Collection
_collections: dict[tuple[str, str], chromadb.Collection] = {}

# (user_id, scope) → {beliefId: {text, type, resolved_at, superseded_by}}
_meta_store: dict[tuple[str, str], dict[str, dict]] = {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _scope_key(user_id: str, scope: str) -> tuple[str, str]:
    return (user_id, scope or "user:universal")


def _collection_name(user_id: str, scope: str) -> str:
    uid = user_id.replace(":", "_").replace("-", "_")[:20]
    sc  = (scope or "universal").replace(":", "_").replace("-", "_")[:30]
    return f"u_{uid}__s_{sc}"


def _get_or_create_collection(user_id: str, scope: str) -> chromadb.Collection:
    key = _scope_key(user_id, scope)
    if key not in _collections:
        name = _collection_name(user_id, scope)
        try:
            col = _chroma.get_collection(name)
        except Exception:
            col = _chroma.create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"},
            )
        _collections[key] = col
    return _collections[key]


def _is_excluded(meta: dict) -> bool:
    """Return True if this belief should NEVER appear in relevantBeliefs search."""
    belief_type   = meta.get("type", "fact")
    resolved_at   = meta.get("resolved_at")
    superseded_by = meta.get("superseded_by")
    pinned        = meta.get("pinned", False)

    # open_questions go to the openQuestions slot, not relevantBeliefs
    if belief_type == "open_question":
        return True

    # Resolved beliefs are historical, not active
    if resolved_at is not None:
        return True

    # Superseded beliefs are stale facts
    if superseded_by is not None:
        return True

    # Pinned facts are retrieved separately, exclude from vector search
    if str(pinned).lower() == "true":
        return True

    return False


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(title="Smriti Benchmark Service v2", version="2.0.0")


class AddRequest(BaseModel):
    text: str
    user_id: str
    metadata: dict = {}
    aliases: list[str] = []


class SearchRequest(BaseModel):
    query: str
    user_id: str
    limit: int = 20
    scope: Optional[str] = None


# ── /add ────────────────────────────────────────────────────────────────────

@app.post("/add")
async def add(req: AddRequest):
    belief_id = req.metadata.get("beliefId") or req.metadata.get("belief_id")
    if not belief_id:
        return JSONResponse({"ok": False, "error": "missing beliefId"}, status_code=400)

    scope   = req.metadata.get("scope", "user:universal")
    user_id = req.user_id

    # Rich text: canonical_name + aliases + content + why_it_matters (harness already built this)
    rich_text = req.text
    if req.aliases:
        rich_text = f"{req.text} {' '.join(req.aliases)}".strip()

    embedding = _embed(rich_text)
    col       = _get_or_create_collection(user_id, scope)

    # Store extended metadata (type, resolved_at, superseded_by)
    chroma_meta = {
        "beliefId":      belief_id,
        "user_id":       user_id,
        "scope":         scope,
        "type":          str(req.metadata.get("type", "fact") or "fact"),
        "resolved_at":   str(req.metadata.get("resolved_at") or ""),
        "superseded_by": str(req.metadata.get("superseded_by") or ""),
        "pinned":        str(req.metadata.get("pinned", False)),
    }

    col.upsert(
        ids=[belief_id],
        embeddings=[embedding],
        documents=[rich_text],
        metadatas=[chroma_meta],
    )

    key = _scope_key(user_id, scope)
    if key not in _meta_store:
        _meta_store[key] = {}
    _meta_store[key][belief_id] = {
        "text":          rich_text,
        "type":          req.metadata.get("type", "fact"),
        "resolved_at":   req.metadata.get("resolved_at"),
        "superseded_by": req.metadata.get("superseded_by"),
        "pinned":        req.metadata.get("pinned", False),
    }

    return {"ok": True, "db_overhead_ms": 0}


# ── /search ─────────────────────────────────────────────────────────────────

@app.post("/search")
async def search(req: SearchRequest):
    if not req.query.strip():
        return {"results": []}

    t0 = time.perf_counter()
    query_embedding = _embed(req.query)

    scopes_to_search = (
        [req.scope]
        if req.scope
        else [sc for (uid, sc) in _collections.keys() if uid == req.user_id]
    )

    results: list[dict] = []

    for scope in scopes_to_search:
        key = _scope_key(req.user_id, scope)
        if key not in _collections:
            continue

        col   = _collections[key]
        count = col.count()
        if count == 0:
            continue

        n = min(req.limit * 3, count)  # fetch 3× more, then filter
        try:
            res = col.query(
                query_embeddings=[query_embedding],
                n_results=n,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as e:
            logger.warning(f"Query error: {e}")
            continue

        for doc, meta, dist in zip(
            res["documents"][0],
            res["metadatas"][0],
            res["distances"][0],
        ):
            # Hard distance threshold
            if dist > SIMILARITY_THRESHOLD:
                continue

            # Type / state filter — exclude open_questions, resolved, superseded
            local_meta = _meta_store.get(key, {}).get(meta["beliefId"], {})
            if not local_meta:
                # Fallback: read from chroma meta (strings)
                local_meta = {
                    "type":          meta.get("type", "fact"),
                    "resolved_at":   meta.get("resolved_at") or None,
                    "superseded_by": meta.get("superseded_by") or None,
                    "pinned":        meta.get("pinned", "False"),
                }
                # Chroma stores strings; convert empties back to None
                if local_meta["resolved_at"] == "None" or local_meta["resolved_at"] == "":
                    local_meta["resolved_at"] = None
                if local_meta["superseded_by"] == "None" or local_meta["superseded_by"] == "":
                    local_meta["superseded_by"] = None

            if _is_excluded(local_meta):
                continue

            results.append({
                "id":    meta["beliefId"],
                "memory": doc,
                "score": round(1.0 - dist, 6),
                "_dist": dist,
            })

    # Deduplicate + sort + trim
    seen: set[str] = set()
    deduped: list[dict] = []
    for r in sorted(results, key=lambda x: x["score"], reverse=True):
        if r["id"] not in seen:
            seen.add(r["id"])
            deduped.append(r)
        if len(deduped) >= req.limit:
            break

    elapsed = round((time.perf_counter() - t0) * 1000, 2)
    logger.debug(
        f"search '{req.query[:40]}' scope={req.scope} "
        f"→ {len(deduped)} results ({elapsed}ms)"
    )

    return {"results": deduped}


# ── /reset ───────────────────────────────────────────────────────────────────

@app.delete("/reset")
async def reset():
    global _chroma, _collections, _meta_store
    try:
        for col in _chroma.list_collections():
            _chroma.delete_collection(col.name)
    except Exception:
        pass
    _chroma = chromadb.Client(chromadb.Settings(anonymized_telemetry=False))
    _collections.clear()
    _meta_store.clear()
    _embed_cached.cache_clear()
    return {"ok": True}


# ── /health ──────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status":    "ok",
        "model":     EMBED_MODEL,
        "threshold": SIMILARITY_THRESHOLD,
        "collections": len(_collections),
        "beliefs":   sum(len(v) for v in _meta_store.values()),
        "embed_cache": _embed_cached.cache_info()._asdict(),
    }


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"[smriti] Starting on port {PORT}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="warning")
