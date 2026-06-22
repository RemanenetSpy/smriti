"""
KAAL — Vector Store
==========================
pgvector semantic search layer backed by Neon PostgreSQL.
Replaces ChromaDB while keeping the same API surface.

Dual-retrieval pipeline:
  • pgvector  → broad semantic recall  (cosine similarity, fuzzy)
  • PostgreSQL → precise temporal / entity filtering (deterministic)

Embeddings: all-MiniLM-L6-v2 (384 dims) via sentence-transformers.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Optional

from .models import EventRecord

logger = logging.getLogger("chronos.vector_store")


class VectorStore:
    """
    pgvector-backed semantic search over Chronos events.
    Shares the same asyncpg pool as the MemoryStore for efficiency.
    """

    EMBEDDING_DIM = 384  # all-MiniLM-L6-v2

    def __init__(self, pool=None):
        # Pool is injected by api/main.py after MemoryStore initializes
        self._pool = pool
        self._model = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def initialize(self, pool=None) -> None:
        """Create the vectors table and HNSW index if not present."""
        if pool:
            self._pool = pool

        if not self._pool:
            raise RuntimeError("VectorStore requires an asyncpg pool.")

        async with self._pool.acquire() as conn:
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS event_vectors (
                    event_id    TEXT PRIMARY KEY REFERENCES events(id) ON DELETE CASCADE,
                    source_id   TEXT NOT NULL,
                    owner_id    TEXT NOT NULL,
                    scope       TEXT NOT NULL DEFAULT 'default',
                    embedding   vector({self.EMBEDDING_DIM}) NOT NULL,
                    embed_text  TEXT NOT NULL,
                    timestamp   TIMESTAMPTZ NOT NULL
                );
            """)
            # Migration: add scope column if upgrading from an older schema
            await conn.execute("""
                DO $$ BEGIN
                    ALTER TABLE event_vectors ADD COLUMN IF NOT EXISTS scope TEXT NOT NULL DEFAULT 'default';
                EXCEPTION WHEN others THEN NULL;
                END $$;
                
                CREATE INDEX IF NOT EXISTS idx_vectors_source
                    ON event_vectors(source_id);
                CREATE INDEX IF NOT EXISTS idx_vectors_owner
                    ON event_vectors(owner_id);
                CREATE INDEX IF NOT EXISTS idx_vectors_scope
                    ON event_vectors(scope);
            """)

        # Load embedding model in background thread without blocking port binding
        import asyncio
        asyncio.create_task(asyncio.to_thread(self._load_model))
        logger.info(f"Vector store initialized (pgvector {self.EMBEDDING_DIM}d)")

    def _load_model(self) -> None:
        """Load the sentence-transformer model (cached after first call)."""
        if self._model is not None:
            return
        from sentence_transformers import SentenceTransformer
        self._model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Embedding model loaded: all-MiniLM-L6-v2")

    def _embed(self, text: str) -> list[float]:
        """Embed text using sentence-transformers."""
        if self._model is None:
            self._load_model()
        return self._model.encode(text, normalize_embeddings=True).tolist()

    # ------------------------------------------------------------------
    # Insert
    # ------------------------------------------------------------------

    async def add_event(self, event: EventRecord) -> None:
        """Embed and store a single event vector."""
        import asyncio
        embed_text = self._build_embed_text(event)
        embedding = await asyncio.to_thread(self._embed, embed_text)
        owner_id = event.metadata_json.get("owner_id", event.source_id)

        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO event_vectors
                    (event_id, source_id, owner_id, scope, embedding, embed_text, timestamp)
                VALUES ($1, $2, $3, $4, $5::vector, $6, $7)
                ON CONFLICT (event_id) DO UPDATE SET
                    embedding = EXCLUDED.embedding,
                    embed_text = EXCLUDED.embed_text,
                    scope = EXCLUDED.scope
                """,
                event.id, event.source_id, owner_id, event.scope,
                f"[{','.join(str(x) for x in embedding)}]",
                embed_text, event.timestamp,
            )

    async def add_events_batch(self, events: list[EventRecord]) -> None:
        """Embed and store multiple events — embeddings computed in parallel."""
        if not events:
            return
        import asyncio

        embed_texts = [self._build_embed_text(e) for e in events]
        # Encode all at once (sentence-transformers batches efficiently)
        embeddings = await asyncio.to_thread(
            lambda: self._model.encode(embed_texts, normalize_embeddings=True, batch_size=32).tolist()
        )

        rows = [
            (
                e.id, e.source_id,
                e.metadata_json.get("owner_id", e.source_id),
                e.scope,
                f"[{','.join(str(x) for x in emb)}]",
                txt, e.timestamp,
            )
            for e, emb, txt in zip(events, embeddings, embed_texts)
        ]

        async with self._pool.acquire() as conn:
            await conn.executemany(
                """
                INSERT INTO event_vectors
                    (event_id, source_id, owner_id, scope, embedding, embed_text, timestamp)
                VALUES ($1, $2, $3, $4, $5::vector, $6, $7)
                ON CONFLICT (event_id) DO UPDATE SET
                    embedding = EXCLUDED.embedding,
                    embed_text = EXCLUDED.embed_text,
                    scope = EXCLUDED.scope
                """,
                rows,
            )
        logger.info(f"Batch added {len(events)} event vectors to pgvector")

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    async def semantic_search(
        self,
        query: str,
        n_results: int = 20,
        source_ids: Optional[list[str]] = None,
        owner_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        scope: Optional[str] = None,
        similarity_threshold: Optional[float] = None,
    ) -> list[dict]:
        """
        Cosine similarity search over embedded events.

        similarity_threshold: cosine distance cutoff (lower = stricter).
          None  → read from SMRITI_SIMILARITY_THRESHOLD env var (default 0.15).
          0.10  → ≥90% cosine similarity (very strict)
          0.15  → ≥85% cosine similarity (default)
          0.30  → ≥70% cosine similarity (lenient)
        """
        from chronos_core.config import SIMILARITY_THRESHOLD
        threshold = similarity_threshold if similarity_threshold is not None else SIMILARITY_THRESHOLD
        import asyncio

        query_embedding = await asyncio.to_thread(self._embed, query)
        vec_str = f"[{','.join(str(x) for x in query_embedding)}]"

        conditions, params = [], [vec_str]
        i = 2

        # Tenant isolation (highest priority)
        if owner_id:
            conditions.append(f"ev.owner_id = ${i}"); params.append(owner_id); i += 1
        elif source_ids:
            conditions.append(f"ev.source_id = ANY(${i})"); params.append(source_ids); i += 1

        # Hard scope isolation
        if scope:
            conditions.append(f"ev.scope = ${i}"); params.append(scope); i += 1

        # Time range filters
        if start_time:
            conditions.append(f"ev.timestamp >= ${i}"); params.append(start_time); i += 1
        if end_time:
            conditions.append(f"ev.timestamp <= ${i}"); params.append(end_time); i += 1

        # Configurable similarity threshold (cosine distance, not similarity)
        params.append(threshold)  # resolved: never None
        threshold_param = i; i += 1

        params.append(n_results)
        limit_param = i

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        query_sql = f"""
            SELECT ev.event_id,
                   (ev.embedding <=> $1::vector) AS distance,
                   ev.source_id, ev.owner_id, ev.scope, ev.embed_text, ev.timestamp
            FROM event_vectors ev
            JOIN events e ON ev.event_id = e.id AND e.valid_to IS NULL
            {where}
              AND (ev.embedding <=> $1::vector) <= ${threshold_param}
            ORDER BY ev.embedding <=> $1::vector
            LIMIT ${limit_param}
        """

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query_sql, *params)

        return [
            {
                "id": r["event_id"],
                "distance": float(r["distance"]),
                "metadata": {
                    "source_id": r["source_id"],
                    "owner_id": r["owner_id"],
                    "scope": r["scope"],
                    "timestamp": r["timestamp"].isoformat(),
                },
                "document": r["embed_text"],
            }
            for r in rows
        ]

    async def count(self) -> int:
        """Get total number of stored embeddings."""
        async with self._pool.acquire() as conn:
            return await conn.fetchval("SELECT COUNT(*) FROM event_vectors")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_embed_text(event: EventRecord) -> str:
        """Build rich text for embedding: SVO + raw text."""
        parts = [f"{event.subject} {event.verb} {event.object}"]
        if event.raw_text:
            parts.append(event.raw_text)
        return " | ".join(parts)
