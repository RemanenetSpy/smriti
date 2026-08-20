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

    """
    # Use the URL exactly as provided. Port 6543 (PgBouncer) is required for IPv4 from HF Spaces.
    if supabase_url not in _pool_cache:
        logger.info(f"Opening new Supabase pool → {_safe_dsn(supabase_url)}")
        pool = await asyncpg.create_pool(
            supabase_url,
            min_size=1,
            max_size=5,          # Conservative — one user DB, not our main DB
            command_timeout=30,
            statement_cache_size=0, # REQUIRED for asyncpg to work with Supabase PgBouncer (port 6543)
        )
        _pool_cache[supabase_url] = pool
        logger.info("Supabase pool ready")

    return _pool_cache[supabase_url]


async def eject_pool(supabase_url: str) -> None:
    """
    Gracefully close and remove the pool for a given Supabase URL.
    Call this to disconnect cleanly (e.g., when a user removes their DB config).
    """
    pool = _pool_cache.pop(supabase_url, None)
    if pool:
        await pool.close()
        logger.info(f"Ejected Supabase pool → {_safe_dsn(supabase_url)}")


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
        import asyncio

        if self._main._model is None:
            self._main._load_model()
        
        embed_texts = [f"{e.subject} {e.verb} {e.object}" for e in events]
        # Batch-encode using the main model (runs in thread — sentence-transformers is sync)
        embeddings = await asyncio.to_thread(
            lambda: self._main._model.encode(
                embed_texts, normalize_embeddings=True, batch_size=32
            ).tolist()
        )

        rows = []
        for e, emb, txt in zip(events, embeddings, embed_texts):
            owner_id = e.metadata_json.get("owner_id", e.source_id)
            vec_str = f"[{','.join(str(x) for x in emb)}]"
            rows.append((e.id, e.source_id, owner_id, e.scope, vec_str, txt, e.timestamp))

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
        Phase 3 — Hybrid Retrieval via Reciprocal Rank Fusion (RRF).

        Combines two independent retrieval branches:
          1. Dense vector branch  — pgvector cosine distance (HNSW index)
          2. Sparse keyword branch — Postgres tsvector / ts_rank_cd (GIN index)

        RRF formula: score = w_vec/(60 + rank_vec) + w_fts/(60 + rank_fts)

        When cosine distance is artificially high due to symmetric-model asymmetry
        (the "alias gap"), the FTS branch rescues relevant results via keyword
        overlap. No LLM, no cross-encoder, no external API call.
        """
        import asyncio
        query_embedding = await asyncio.to_thread(self._main._embed, query)
        vec_str = f"[{','.join(str(x) for x in query_embedding)}]"

        # Build filter conditions (applied to both branches)
        conditions = ["ev.owner_id = $2"]
        params: list = [vec_str, owner_id]
        i = 3

        if source_ids:
            conditions.append(f"ev.source_id = ANY(${i})"); params.append(source_ids); i += 1
        if start_time:
            conditions.append(f"ev.timestamp >= ${i}"); params.append(start_time); i += 1
        if end_time:
            conditions.append(f"ev.timestamp <= ${i}"); params.append(end_time); i += 1
        if scope:
            conditions.append(f"ev.scope = ${i}"); params.append(scope); i += 1

        # Final params: broad_cutoff, keyword query string, n_results
        broad_cutoff_idx = i;      params.append(broad_cutoff); i += 1
        keyword_idx      = i;      params.append(query);        i += 1
        limit_idx        = i;      params.append(n_results * 2); i += 1  # over-fetch for RRF

        where = " AND ".join(conditions)

        sql = f"""
            WITH
            -- Branch 1: Dense vector search (pgvector HNSW)
            vec_ranked AS (
                SELECT
                    ev.event_id                                AS id,
                    ev.embed_text                              AS document,
                    (ev.embedding <=> $1::vector)              AS distance,
                    ROW_NUMBER() OVER (ORDER BY (ev.embedding <=> $1::vector) ASC) AS rnk
                FROM event_vectors ev
                WHERE {where}
                  AND (ev.embedding <=> $1::vector) <= ${broad_cutoff_idx}
                LIMIT ${limit_idx}
            ),
            -- Branch 2: Sparse full-text search (tsvector / BM25 cover density)
            fts_ranked AS (
                SELECT
                    ev.event_id                                AS id,
                    ev.embed_text                              AS document,
                    NULL::FLOAT                                AS distance,
                    ROW_NUMBER() OVER (
                        ORDER BY ts_rank_cd(
                            to_tsvector('english', ev.embed_text),
                            plainto_tsquery('english', ${keyword_idx})
                        ) DESC
                    )                                          AS rnk
                FROM event_vectors ev
                WHERE {where}
                  AND to_tsvector('english', ev.embed_text)
                      @@ plainto_tsquery('english', ${keyword_idx})
                LIMIT ${limit_idx}
            ),
            -- RRF fusion: score = w_vec/(60+rank) + w_fts/(60+rank)
            -- FTS Dynamic Override: when keyword search confirms a match,
            -- cap the distance at 0.35 regardless of vector distance.
            -- This neutralises the symmetric-model asymmetry penalty (Phase 3).
            fused AS (
                SELECT
                    COALESCE(v.id,  f.id)                     AS id,
                    COALESCE(v.document, f.document)          AS document,
                    CASE
                        WHEN f.id IS NOT NULL
                            THEN LEAST(COALESCE(v.distance, 0.35), 0.35)
                        ELSE v.distance
                    END                                       AS distance,
                    (
                        CASE WHEN v.id IS NOT NULL THEN 1.0 / (60.0 + v.rnk) ELSE 0 END
                      + CASE WHEN f.id IS NOT NULL THEN 1.0 / (60.0 + f.rnk) ELSE 0 END
                    )                                         AS rrf_score
                FROM vec_ranked  v
                FULL OUTER JOIN fts_ranked f ON v.id = f.id
            )
            SELECT id, document, distance
            FROM fused
            ORDER BY rrf_score DESC
            LIMIT ${limit_idx}
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
