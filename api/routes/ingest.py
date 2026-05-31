"""
KAAL — Ingest Route
===========================
POST /ingest — Universal event ingestion endpoint.
Any SaaS or agent sends events here to get temporal memory.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime

from fastapi import APIRouter, Depends

from chronos_core.models import (
    EventRecord,
    IngestPayload,
    IngestResponse,
    TurnRecord,
    TurnRole,
)
from api.auth import verify_api_key, check_event_quota
from api.deps import get_memory_store, get_vector_store, get_svo_parser

logger = logging.getLogger("chronos.routes.ingest")

router = APIRouter(tags=["Ingest"])


@router.post("/ingest", response_model=IngestResponse)
async def ingest_events(
    payload: IngestPayload,
    key_info: dict = Depends(verify_api_key),
):
    """
    Ingest raw events into the Chronos temporal memory.

    Pipeline: validate → SVO parse → store in Event Calendar +
    Turn Calendar + ChromaDB vector store.
    """
    start_time = time.time()
    source_id = payload.source_id  # User's label (e.g., "my-crm")
    owner_id = key_info["source_id"]  # API key owner (tenant isolation)

    # Check quota against the OWNER, not the source label
    await check_event_quota(owner_id, len(payload.events))

    memory = get_memory_store()
    vector = get_vector_store()
    parser = get_svo_parser()

    all_event_ids: list[str] = []
    all_svo_tuples = []
    all_turn_ids: list[str] = []

    for ingest_event in payload.events:
        ts = ingest_event.timestamp or datetime.utcnow()

        # Merge owner_id into event metadata for tenant isolation
        event_meta = {**ingest_event.metadata, "owner_id": owner_id}

        # 1. Store raw turn in Turn Calendar
        turn = TurnRecord(
            source_id=owner_id,  # Track by owner for privacy
            role=TurnRole.USER,
            content=ingest_event.text,
            timestamp=ts,
        )

        # 2. Parse SVO tuples (if enabled)
        event_records: list[EventRecord] = []

        if payload.parse_svo:
            svo_tuples = await parser.parse(ingest_event.text, ts)
            all_svo_tuples.extend(svo_tuples)

            for svo in svo_tuples:
                event = EventRecord(
                    source_id=source_id,
                    subject=svo.subject,
                    verb=svo.verb,
                    object=svo.object,
                    timestamp=svo.timestamp,
                    datetime_start=svo.datetime_start,
                    datetime_end=svo.datetime_end,
                    entity_aliases=svo.entity_aliases,
                    confidence=svo.confidence,
                    metadata_json=event_meta,
                    raw_text=ingest_event.text,
                )
                event_records.append(event)
        else:
            # No SVO parsing — store as a single raw event
            event = EventRecord(
                source_id=source_id,
                subject="unknown",
                verb="recorded",
                object=ingest_event.text[:200],
                timestamp=ts,
                raw_text=ingest_event.text,
                metadata_json=event_meta,
                confidence=0.0,
            )
            event_records.append(event)

        # 3. Persist to SQLite Event Calendar
        if event_records:
            ids = await memory.insert_events_batch(event_records)
            all_event_ids.extend(ids)
            turn.event_ids = ids

            # 4. Persist to ChromaDB vector store
            await vector.add_events_batch(event_records)

        # 5. Persist turn to Turn Calendar
        turn_id = await memory.insert_turn(turn)
        all_turn_ids.append(turn_id)

    # 6. Update usage metering
    await memory.increment_usage(owner_id, events=len(all_event_ids))

    elapsed = (time.time() - start_time) * 1000
    logger.info(
        f"Ingested {len(all_event_ids)} events + {len(all_turn_ids)} turns "
        f"for source={source_id} in {elapsed:.1f}ms"
    )

    return IngestResponse(
        ingested_count=len(all_event_ids),
        event_ids=all_event_ids,
        svo_tuples=all_svo_tuples,
        turn_ids=all_turn_ids,
    )
