"""
Smriti — Supabase Connector
============================
Manages a per-request asyncpg connection pool to a user's Supabase database.

Design principles:
  • Zero changes to smriti_core/ — this is a pure adapter layer.
  • Pools are cached by DSN so repeated requests reuse connections.
  • Clean connect() and eject() methods for easy lifecycle management.
  • Exposes exactly the same interface used by ingest/query routes
    (insert_events_batch, insert_turn, find_active_by_subject,
     invalidate_event, get_events_by_ids, semantic_search).
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

import asyncpg

# We reuse the exact same models — no copies, no drift.
from smriti_core.models import EventRecord, TurnRecord, TurnRole
from smriti_core.vector_store import VectorStore

logger = logging.getLogger("smriti.supabase.connector")

# ---------------------------------------------------------------------------
# Pool cache — one pool per unique Supabase URL, shared across requests.
# This avoids opening a new TCP connection on every API call.
# ---------------------------------------------------------------------------
_pool_cache: dict[str, asyncpg.Pool] = {}


def _safe_dsn(dsn: str) -> str:
    """Return the DSN with the password redacted for logging."""
    try:
        p = urlparse(dsn)
        return dsn.replace(p.password or "", "***") if p.password else dsn
    except Exception:
        return "<dsn>"


async def get_pool(supabase_url: str) -> asyncpg.Pool:
    """
    Return a cached asyncpg pool for the given Supabase direct connection URL.

    IMPORTANT: Supabase has two connection modes:
      • Port 5432 → Direct connection  ← USE THIS with asyncpg
      • Port 6543 → PgBouncer pooler   ← Breaks asyncpg prepared statements

    If the user accidentally passes port 6543, we silently correct it.
    """
    # Silently fix the common mistake of using the pooler port
    corrected_url = supabase_url.replace(":6543/", ":5432/")
    if corrected_url != supabase_url:
        logger.warning(
            "X-Supabase-Url used port 6543 (PgBouncer). "
            "Corrected to port 5432 (direct) for asyncpg compatibility."
        )

    if corrected_url not in _pool_cache:
        logger.info(f"Opening new Supabase pool → {_safe_dsn(corrected_url)}")
        pool = await asyncpg.create_pool(
            corrected_url,
            min_size=1,
            max_size=5,          # Conservative — one user DB, not our main DB
            command_timeout=30,
        )
        _pool_cache[corrected_url] = pool
        logger.info("Supabase pool ready")

    return _pool_cache[corrected_url]


async def eject_pool(supabase_url: str) -> None:
    """
    Gracefully close and remove the pool for a given Supabase URL.
    Call this to disconnect cleanly (e.g., when a user removes their DB config).
    """
    corrected_url = supabase_url.replace(":6543/", ":5432/")
    pool = _pool_cache.pop(corrected_url, None)
    if pool:
        await pool.close()
        logger.info(f"Ejected Supabase pool → {_safe_dsn(corrected_url)}")


async def eject_all_pools() -> None:
    """Close ALL cached Supabase pools. Used on server shutdown."""
    for url, pool in list(_pool_cache.items()):
        await pool.close()
        logger.info(f"Ejected Supabase pool → {_safe_dsn(url)}")
    _pool_cache.clear()


# ---------------------------------------------------------------------------
# SupabaseStore — drop-in adapter with the same interface as MemoryStore
# ---------------------------------------------------------------------------

class SupabaseStore:
    """
    Thin adapter that speaks the same interface as smriti_core.MemoryStore
    but writes to the user's Supabase database instead of our Neon DB.

    All SVO parsing, supersession logic, and embedding happens upstream
    in the route handlers — exactly as with the default store. This class
    only handles the final persistence step.
    """

    def __init__(self, pool: asyncpg.Pool, vector_store: "SupabaseVectorStore"):
        self._pool = pool
        self.vector = vector_store

    # ------------------------------------------------------------------
    # Event Calendar
    # ------------------------------------------------------------------

    async def insert_events_batch(self, events: list[EventRecord]) -> list[str]:
        """Batch-insert S-V-O events into the user's Supabase events table."""
        if not events:
            return []

        rows = [
            (
                e.id, e.source_id, e.subject, e.verb, e.object,
                e.timestamp, e.datetime_start, e.datetime_end,
                json.dumps(e.entity_aliases), e.confidence,
                json.dumps(e.metadata_json), e.raw_text, e.created_at,
                e.scope, e.valid_from, e.valid_to, e.superseded_by,
            )
            for e in events
        ]

        async with self._pool.acquire() as conn:
            await conn.executemany(
                """
                INSERT INTO events
                    (id, source_id, subject, verb, object, timestamp,
                     datetime_start, datetime_end, entity_aliases,
                     confidence, metadata_json, raw_text, created_at,
                     scope, valid_from, valid_to, superseded_by)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17)
                ON CONFLICT (id) DO NOTHING
                """,
                rows,
            )
        return [e.id for e in events]

    async def insert_turn(self, turn: TurnRecord) -> str:
        """Insert a raw conversation turn into the Turn Calendar."""
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO turns (id, source_id, role, content, timestamp, event_ids, created_at)
                VALUES ($1,$2,$3,$4,$5,$6,$7)
                ON CONFLICT (id) DO NOTHING
                """,
                turn.id, turn.source_id, turn.role.value,
                turn.content, turn.timestamp,
                json.dumps(turn.event_ids), turn.created_at,
            )
        return turn.id

    async def find_active_by_subject(
        self,
        owner_id: str,
        scope: str,
        subject: str,
        limit: int = 10,
    ) -> list[EventRecord]:
        """Fetch active facts with a matching subject — for supersession checks."""
        pattern = f"%{subject.lower()}%"
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM events
                WHERE valid_to IS NULL
                  AND scope = $1
                  AND metadata_json->>'owner_id' = $2
                  AND LOWER(subject) ILIKE $3
                ORDER BY valid_from DESC
                LIMIT $4
                """,
                scope, owner_id, pattern, limit,
            )
        return [_row_to_event(r) for r in rows]

    async def invalidate_event(self, event_id: str, superseded_by: Optional[str] = None) -> None:
        """Mark an event as superseded (bi-temporal invalidation)."""
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE events
                SET valid_to = NOW(), superseded_by = $2
                WHERE id = $1 AND valid_to IS NULL
                """,
                event_id, superseded_by,
            )

    async def get_events_by_ids(self, event_ids: list[str]) -> list[EventRecord]:
        """Fetch multiple events by their IDs."""
        if not event_ids:
            return []
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM events WHERE id = ANY($1)", event_ids
            )
        return [_row_to_event(r) for r in rows]


# ---------------------------------------------------------------------------
# SupabaseVectorStore — same interface as smriti_core.VectorStore
# ---------------------------------------------------------------------------

class SupabaseVectorStore:
    """
    pgvector adapter for the user's Supabase database.
    Reuses the same embedding model from the main VectorStore — no duplication.
    """

    def __init__(self, pool: asyncpg.Pool, main_vector_store: VectorStore):
        self._pool = pool
        # Borrow the embedding model from the main vector store — already loaded.
        self._main = main_vector_store

    def _embed(self, text: str) -> list[float]:
        """Delegate embedding to the already-loaded main model."""
        return self._main._embed(text)

    async def add_events_batch(self, events: list[EventRecord]) -> None:
        """Embed and store event vectors in the user's Supabase database."""
        if not events:
            return

        rows = []
        for e in events:
            embed_text = f"{e.subject} {e.verb} {e.object}"
            embedding = self._embed(embed_text)
            owner_id = e.metadata_json.get("owner_id", e.source_id)
            rows.append((
                e.id, e.source_id, owner_id, e.scope,
                str(embedding),   # pgvector expects '[x,y,z,...]' string format
                embed_text, e.timestamp,
            ))

        async with self._pool.acquire() as conn:
            await conn.executemany(
                """
                INSERT INTO event_vectors
                    (event_id, source_id, owner_id, scope, embedding, embed_text, timestamp)
                VALUES ($1,$2,$3,$4,$5::vector,$6,$7)
                ON CONFLICT (event_id) DO NOTHING
                """,
                rows,
            )

    async def semantic_search(
        self,
        query: str,
        n_results: int = 20,
        owner_id: Optional[str] = None,
        source_ids: Optional[list[str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        scope: Optional[str] = None,
        broad_cutoff: float = 0.85,
    ) -> list[dict]:
        """
        Cosine-distance semantic search against the user's Supabase vector table.
        Returns the same dict structure as smriti_core.VectorStore.semantic_search.
        """
        embedding = self._embed(query)
        embedding_str = str(embedding)

        conditions = ["ev.owner_id = $2"]
        params: list = [embedding_str, owner_id]
        i = 3

        if source_ids:
            conditions.append(f"ev.source_id = ANY(${i})"); params.append(source_ids); i += 1
        if start_time:
            conditions.append(f"ev.timestamp >= ${i}"); params.append(start_time); i += 1
        if end_time:
            conditions.append(f"ev.timestamp <= ${i}"); params.append(end_time); i += 1
        if scope:
            conditions.append(f"ev.scope = ${i}"); params.append(scope); i += 1

        params.extend([broad_cutoff, n_results])
        where = " AND ".join(conditions)

        sql = f"""
            SELECT
                ev.event_id   AS id,
                ev.embed_text AS document,
                (ev.embedding <=> $1::vector) AS distance
            FROM event_vectors ev
            WHERE {where}
              AND (ev.embedding <=> $1::vector) <= ${i}
            ORDER BY distance ASC
            LIMIT ${i + 1}
        """

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)

        return [{"id": r["id"], "document": r["document"], "distance": r["distance"]} for r in rows]


# ---------------------------------------------------------------------------
# Factory — get both stores from a single Supabase URL
# ---------------------------------------------------------------------------

async def get_supabase_stores(
    supabase_url: str,
    main_vector_store: VectorStore,
) -> tuple[SupabaseStore, SupabaseVectorStore]:
    """
    Connect to the user's Supabase DB and return ready-to-use store adapters.

    Args:
        supabase_url:       The direct Postgres connection string from Supabase dashboard.
        main_vector_store:  The main app's VectorStore (to borrow its loaded model).

    Returns:
        (SupabaseStore, SupabaseVectorStore) — same interface as the defaults.
    """
    pool = await get_pool(supabase_url)
    sv = SupabaseVectorStore(pool, main_vector_store)
    sm = SupabaseStore(pool, sv)
    return sm, sv


# ---------------------------------------------------------------------------
# Row converter (mirrors smriti_core.MemoryStore._row_to_event exactly)
# ---------------------------------------------------------------------------

def _row_to_event(row) -> EventRecord:
    return EventRecord(
        id=row["id"],
        source_id=row["source_id"],
        subject=row["subject"],
        verb=row["verb"],
        object=row["object"],
        timestamp=row["timestamp"],
        datetime_start=row["datetime_start"],
        datetime_end=row["datetime_end"],
        entity_aliases=json.loads(row["entity_aliases"]) if isinstance(row["entity_aliases"], str) else (row["entity_aliases"] or []),
        confidence=row["confidence"],
        metadata_json=json.loads(row["metadata_json"]) if isinstance(row["metadata_json"], str) else (row["metadata_json"] or {}),
        raw_text=row["raw_text"] or "",
        created_at=row["created_at"],
        scope=row["scope"] if "scope" in row.keys() else "default",
        valid_from=row["valid_from"] if "valid_from" in row.keys() else row["created_at"],
        valid_to=row["valid_to"] if "valid_to" in row.keys() else None,
        superseded_by=row["superseded_by"] if "superseded_by" in row.keys() else None,
    )
