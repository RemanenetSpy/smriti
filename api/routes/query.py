"""
Chronos OS — Query Route
==========================
POST /query — Hybrid temporal + semantic retrieval.
The core value of Chronos: agents query structured temporal memory.
"""

from __future__ import annotations

import logging
import time

from fastapi import APIRouter, Depends

from chronos_core.models import (
    LiteEventRecord,
    QueryRequest,
    QueryResponse,
    QueryResult,
)
from api.auth import verify_api_key
from api.deps import get_memory_store, get_vector_store

logger = logging.getLogger("chronos.routes.query")

router = APIRouter(tags=["Query"])


@router.post("/query", response_model=QueryResponse)
async def query_memory(
    request: QueryRequest,
    key_info: dict = Depends(verify_api_key),
):
    """
    Hybrid temporal + semantic retrieval from Chronos memory.

    Pipeline:
    1. ChromaDB semantic search (fuzzy recall)
    2. SQLite temporal filtering (deterministic precision)
    3. Merge + rank results by combined score
    """
    start_time = time.time()

    memory = get_memory_store()
    vector = get_vector_store()

    results: list[QueryResult] = []
    seen_ids: set[str] = set()

    # ----------------------------------------------------------------
    # Phase 1: Semantic search via ChromaDB
    # ----------------------------------------------------------------
    semantic_results = await vector.semantic_search(
        query=request.query,
        n_results=request.max_results,
        source_ids=request.source_ids or None,
        start_time=request.time_range.start if request.time_range else None,
        end_time=request.time_range.end if request.time_range else None,
    )

    # Fetch full event records from SQLite
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
    # Phase 2: Temporal search via SQLite
    # ----------------------------------------------------------------
    temporal_weight = 1.0 - request.semantic_weight

    if request.time_range and (request.time_range.start or request.time_range.end):
        temporal_events = await memory.query_temporal(
            start=request.time_range.start,
            end=request.time_range.end,
            source_ids=request.source_ids or None,
            limit=request.max_results,
        )

        for event in temporal_events:
            if event.id not in seen_ids:
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
                    relevance_score=temporal_weight * 0.8,  # Base temporal relevance
                    provenance="temporal_filter",
                ))
                seen_ids.add(event.id)

    # ----------------------------------------------------------------
    # Phase 3: Entity-based search (extract entities from query)
    # ----------------------------------------------------------------
    # Simple heuristic: treat capitalized words as potential entities
    words = request.query.split()
    entities = [w for w in words if w[0].isupper() and len(w) > 2] if words else []

    if entities:
        entity_events = await memory.multi_hop_query(
            entities=entities,
            start=request.time_range.start if request.time_range else None,
            end=request.time_range.end if request.time_range else None,
            source_ids=request.source_ids or None,
            limit=request.max_results,
        )

        for event in entity_events:
            if event.id not in seen_ids:
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
        f"Query returned {len(results)} results in {elapsed:.1f}ms: "
        f"'{request.query[:60]}...'"
    )

    return QueryResponse(
        results=results,
        total_found=len(results),
        query_time_ms=round(elapsed, 2),
    )
