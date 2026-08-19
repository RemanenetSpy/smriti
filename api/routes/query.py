"""
Smriti — Query Route
==========================
POST /query — Hybrid temporal + semantic retrieval.
The core value of Chronos: agents query structured temporal memory.

Retrieval algorithm (Bayesian Gap Cutoff):
  1. Broad vector search (distance < BROAD_CUTOFF=0.85) — wide candidate net
  2. Entity structural filter — drop zero-overlap candidates when query has entities
  3. Bayesian gap cutoff (Gap=0.08, Max=0.52) — dynamically isolate best match(es)

Best config found via 77-case benchmark sweep: 23 active passes, precision 0.299.

Supabase BYODB (optional):
  Add header  X-Supabase-Url: postgresql://...
  Query runs against your Supabase DB instead of the default Smriti DB.
  Omit the header → zero change in behaviour.
"""

from __future__ import annotations

import logging
import os
import re
import time
from typing import Optional

from fastapi import APIRouter, Depends, Header, Query

from smriti_core.models import (
    LiteEventRecord,
    QueryRequest,
    QueryResponse,
    QueryResult,
)
from api.auth import verify_api_key
from api.deps import get_memory_store, get_vector_store

logger = logging.getLogger("smriti.routes.query")

router = APIRouter(tags=["Query"])


# ---------------------------------------------------------------------------
# Bayesian Gap Cutoff — ported from benchmark/harness/run_precision_bench.py
# Best sweep result: Gap=0.08 / MaxCutoff=0.52 → precision 0.299 (+148% vs baseline)
# All parameters are env-var overridable.
# ---------------------------------------------------------------------------

_GAP_THRESHOLD = float(os.getenv("SMRITI_GAP_THRESHOLD", "0.08"))
_MAX_CUTOFF    = float(os.getenv("SMRITI_MAX_CUTOFF",    "0.52"))
_BROAD_CUTOFF  = float(os.getenv("SMRITI_BROAD_CUTOFF",  "0.85"))  # initial SQL net

_GAP_STOPWORDS = {
    "the", "a", "an", "is", "in", "of", "to", "it", "was", "has", "are",
    "and", "or", "for", "with", "on", "at", "by", "from", "this", "that",
    "not", "but", "its", "be", "as", "can", "all", "use", "also", "via",
    "per", "when", "than", "who", "what", "which", "how", "why", "where",
}

# Interrogative detection: matches wh-words at start or trailing '?'
_INTERROGATIVE_RE = re.compile(
    r"^\s*(what|who|where|when|why|how|which|is|are|was|were|can|could|does|do|did)\b|.*\?\s*$",
    re.IGNORECASE,
)


def _is_interrogative(text: str) -> bool:
    """Return True if the query is phrased as a question."""
    return bool(_INTERROGATIVE_RE.search(text))


def _extract_entities(text: str) -> set[str]:
    """Extract meaningful tokens from text, excluding stopwords."""
    words = re.findall(r'\b[a-zA-Z0-9_-]{3,}\b', text.lower())
    return set(words) - _GAP_STOPWORDS


def _adaptive_cutoff(distances: list[float], is_interrogative: bool = False) -> float:
    """
    Phase 4 — Adaptive threshold combining:
      1. Bayesian gap isolation (clear winner promotion)
      2. Relative margin baseline: max(0.85 * s_max, s_max - 0.12)
      3. Interrogative discount (δ=0.08): lowers the threshold for questions,
         forgiving the asymmetric penalty that symmetric bi-encoders impose on
         question-to-statement matching.

    No LLM, no external model. Pure math over the retrieved score distribution.
    """
    if not distances:
        return _MAX_CUTOFF

    sorted_d = sorted(distances)
    s_min = sorted_d[0]  # best (smallest) distance

    # --- 1. Bayesian gap: isolate rank-1 when it's a clear winner ---
    if len(sorted_d) > 1 and (sorted_d[1] - s_min) > _GAP_THRESHOLD:
        base = s_min + 0.04
    else:
        # --- 2. Relative margin: stay within 15% drop from best ---
        relative_margin = max(0.85 * s_min, s_min - 0.12)
        base = min(_MAX_CUTOFF, max(relative_margin, s_min + 0.10))

    # --- 3. Interrogative discount: expand acceptance boundary for questions ---
    delta = 0.08 if is_interrogative else 0.0
    return base + delta


@router.post("/query", response_model=QueryResponse)
async def query_memory(
    request: QueryRequest,
    key_info: dict = Depends(verify_api_key),
    header_supabase_url: Optional[str] = Header(default=None, alias="X-Supabase-Url"),
    query_supabase_url: Optional[str] = Query(default=None, alias="supabase_url"),
):
    """
    Hybrid temporal + semantic retrieval from Chronos memory.
    
    TENANT ISOLATION: All queries are scoped to the API key owner.
    User A can never see User B's data.

    Pipeline:
    1. pgvector semantic search (fuzzy recall) — filtered by owner_id
    2. PostgreSQL temporal filtering (deterministic) — filtered by owner_id
    3. Merge + rank results by combined score

    Optional header X-Supabase-Url runs the query against the user's
    own Supabase DB instead of the default Smriti DB.
    """
    start_time = time.time()
    owner_id = key_info["source_id"]  # Tenant isolation key

    # ── Storage target: Supabase BYODB or default Smriti DB ──────────
    active_supabase_url = query_supabase_url or header_supabase_url
    if active_supabase_url:
        from supabase.connector import get_supabase_stores
        memory, vector = await get_supabase_stores(active_supabase_url, get_vector_store())
        logger.info(f"Supabase BYODB query active for owner={owner_id!r}")
    else:
        memory = get_memory_store()
        vector = get_vector_store()
    # ─────────────────────────────────────────────────────────────────

    results: list[QueryResult] = []
    seen_ids: set[str] = set()

    # ----------------------------------------------------------------
    # Phase 1: Semantic search via pgvector (Bayesian Gap Cutoff)
    # ----------------------------------------------------------------
    # If the caller supplied an explicit similarity_threshold, use it as
    # a static cutoff (backwards-compatible). Otherwise, run the full
    # gap algorithm: broad net → entity filter → dynamic gap cutoff.
    explicit_threshold = (
        request.similarity_threshold  # None when not set by caller
        if request.similarity_threshold is not None
        else None
    )
    use_gap_algorithm = explicit_threshold is None

    # Always search with broad net; for static-threshold callers, use their value directly.
    sql_cutoff = _BROAD_CUTOFF if use_gap_algorithm else explicit_threshold

    semantic_results = await vector.semantic_search(
        query=request.query,
        n_results=request.max_results * 4 if use_gap_algorithm else request.max_results,
        owner_id=owner_id,
        source_ids=request.source_ids or None,
        start_time=request.time_range.start if request.time_range else None,
        end_time=request.time_range.end if request.time_range else None,
        scope=request.scope,
        broad_cutoff=sql_cutoff,
    )

    if use_gap_algorithm and semantic_results:
        # Stage 2 — Entity structural filter
        q_ents = _extract_entities(request.query)
        if len(q_ents) >= 2:
            filtered = []
            for r in semantic_results:
                doc_text = r.get("document", "")
                doc_ents = _extract_entities(doc_text)
                if q_ents & doc_ents:  # at least one shared entity
                    filtered.append(r)
            if filtered:  # only apply filter if it keeps at least one result
                semantic_results = filtered

        # Stage 3 — Adaptive cutoff (Phase 4: interrogative-aware)
        is_q = _is_interrogative(request.query)
        dists  = [r["distance"] for r in semantic_results]
        cutoff = _adaptive_cutoff(dists, is_interrogative=is_q)
        semantic_results = [r for r in semantic_results if r["distance"] <= cutoff]
        logger.debug(
            f"Adaptive cutoff={cutoff:.3f} is_interrogative={is_q} "
            f"→ {len(semantic_results)} candidates (from {len(dists)} raw)"
        )

    # Fetch full event records from PostgreSQL
    semantic_ids = [r["id"] for r in semantic_results]
    if semantic_ids:
        events = await memory.get_events_by_ids(semantic_ids)
        event_map = {e.id: e for e in events}

        for sr in semantic_results:
            event = event_map.get(sr["id"])
            if event and event.id not in seen_ids:
                similarity = max(0, 1 - sr["distance"])
                lite_event = LiteEventRecord(
                    id=event.id,
                    source_id=event.source_id,
                    subject=event.subject,
                    verb=event.verb,
                    object=event.object,
                    timestamp=event.timestamp,
                    confidence=event.confidence,
                )
                results.append(QueryResult(
                    event=lite_event,
                    relevance_score=similarity * request.semantic_weight,
                    provenance="semantic_search",
                ))
                seen_ids.add(event.id)

    # ----------------------------------------------------------------
    # Phase 2: Temporal search via PostgreSQL (scoped to owner)
    # ----------------------------------------------------------------
    temporal_weight = 1.0 - request.semantic_weight

    if request.time_range and (request.time_range.start or request.time_range.end):
        # Force owner_id into source_ids filter for temporal queries
        owner_source_ids = [owner_id]
        if request.source_ids:
            owner_source_ids.extend(request.source_ids)

        temporal_events = await memory.query_temporal(
            start=request.time_range.start,
            end=request.time_range.end,
            source_ids=owner_source_ids,
            scope=request.scope,  # NEW
            limit=request.max_results,
        )

        for event in temporal_events:
            if event.id not in seen_ids:
                # Double-check ownership via metadata
                meta = event.metadata_json or {}
                if meta.get("owner_id") and meta["owner_id"] != owner_id:
                    continue  # Skip events that don't belong to this user

                lite_event = LiteEventRecord(
                    id=event.id,
                    source_id=event.source_id,
                    subject=event.subject,
                    verb=event.verb,
                    object=event.object,
                    timestamp=event.timestamp,
                    confidence=event.confidence,
                )
                results.append(QueryResult(
                    event=lite_event,
                    relevance_score=temporal_weight * 0.8,
                    provenance="temporal_filter",
                ))
                seen_ids.add(event.id)

    # ----------------------------------------------------------------
    # Phase 3: Entity-based search (scoped to owner)
    # ----------------------------------------------------------------
    words = request.query.split()
    entities = [w for w in words if w[0].isupper() and len(w) > 2] if words else []

    if entities:
        # Force owner_id into source_ids filter for entity queries
        owner_source_ids = [owner_id]
        if request.source_ids:
            owner_source_ids.extend(request.source_ids)

        entity_events = await memory.multi_hop_query(
            entities=entities,
            start=request.time_range.start if request.time_range else None,
            end=request.time_range.end if request.time_range else None,
            source_ids=owner_source_ids,
            scope=request.scope,  # NEW
            limit=request.max_results,
        )

        for event in entity_events:
            if event.id not in seen_ids:
                # Double-check ownership via metadata
                meta = event.metadata_json or {}
                if meta.get("owner_id") and meta["owner_id"] != owner_id:
                    continue

                lite_event = LiteEventRecord(
                    id=event.id,
                    source_id=event.source_id,
                    subject=event.subject,
                    verb=event.verb,
                    object=event.object,
                    timestamp=event.timestamp,
                    confidence=event.confidence,
                )
                results.append(QueryResult(
                    event=lite_event,
                    relevance_score=temporal_weight * 0.6,
                    provenance="entity_multi_hop",
                ))
                seen_ids.add(event.id)

    # ----------------------------------------------------------------
    # Sort by relevance and cap at max_results
    # ----------------------------------------------------------------
    results.sort(key=lambda r: r.relevance_score, reverse=True)
    results = results[:request.max_results]

    elapsed = (time.time() - start_time) * 1000
    logger.info(
        f"Query returned {len(results)} results in {elapsed:.1f}ms for "
        f"owner={owner_id}: '{request.query[:60]}...'"
    )

    return QueryResponse(
        results=results,
        total_found=len(results),
        query_time_ms=round(elapsed, 2),
    )
