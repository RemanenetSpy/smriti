"""
KAAL — Memory Store
==========================
Dual-calendar PostgreSQL storage engine backed by Neon.
  • Event Calendar — structured SVO events with temporal indexing
  • Turn Calendar  — raw conversation turns for full context

Implements the Chronos research paper's dual-calendar architecture
for temporal-aware retrieval and multi-hop reasoning.
Uses asyncpg connection pooling for high concurrency on Render.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Optional

import asyncpg

from .models import (
    ConnectorRecord,
    EventRecord,
    TurnRecord,
    TurnRole,
    UsageStats,
    TierName,
)

logger = logging.getLogger("chronos.memory_store")

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_SCHEMA_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;

-- Event Calendar: structured SVO events
CREATE TABLE IF NOT EXISTS events (
    id              TEXT PRIMARY KEY,
    source_id       TEXT NOT NULL,
    subject         TEXT NOT NULL,
    verb            TEXT NOT NULL,
    object          TEXT NOT NULL,
    timestamp       TIMESTAMPTZ NOT NULL,
    datetime_start  TIMESTAMPTZ,
    datetime_end    TIMESTAMPTZ,
    entity_aliases  JSONB DEFAULT '[]',
    confidence      REAL DEFAULT 1.0,
    metadata_json   JSONB DEFAULT '{}',
    raw_text        TEXT DEFAULT '',
    created_at      TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_events_source    ON events(source_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_subject   ON events(subject);
CREATE INDEX IF NOT EXISTS idx_events_verb      ON events(verb);

-- Turn Calendar: raw conversation turns
CREATE TABLE IF NOT EXISTS turns (
    id          TEXT PRIMARY KEY,
    source_id   TEXT NOT NULL,
    role        TEXT NOT NULL DEFAULT 'user',
    content     TEXT NOT NULL,
    timestamp   TIMESTAMPTZ NOT NULL,
    event_ids   JSONB DEFAULT '[]',
    created_at  TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_turns_source    ON turns(source_id);
CREATE INDEX IF NOT EXISTS idx_turns_timestamp ON turns(timestamp DESC);

-- Connectors: registered SaaS tools
CREATE TABLE IF NOT EXISTS connectors (
    id          TEXT PRIMARY KEY,
    source_id   TEXT NOT NULL,
    name        TEXT NOT NULL,
    description TEXT DEFAULT '',
    base_url    TEXT NOT NULL,
    auth_header TEXT,
    endpoints   JSONB DEFAULT '[]',
    metadata    JSONB DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_connectors_source ON connectors(source_id);

-- API Keys & Usage
CREATE TABLE IF NOT EXISTS api_keys (
    key_hash            TEXT PRIMARY KEY,
    source_id           TEXT NOT NULL UNIQUE,
    tier                TEXT NOT NULL DEFAULT 'explorer',
    events_used         INTEGER DEFAULT 0,
    orchestration_used  INTEGER DEFAULT 0,
    connectors_used     INTEGER DEFAULT 0,
    period_start        TIMESTAMPTZ NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_apikeys_source ON api_keys(source_id);
"""


class MemoryStore:
    """
    Async PostgreSQL dual-calendar memory store using asyncpg connection pool.
    Backed by Neon — data persists across all redeploys.
    """

    def __init__(self, dsn: Optional[str] = None):
        self.dsn = dsn or os.getenv("DATABASE_URL")
        if not self.dsn:
            raise RuntimeError("DATABASE_URL environment variable is not set.")
        self._pool: Optional[asyncpg.Pool] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def initialize(self) -> None:
        """Create connection pool and apply schema migrations."""
        self._pool = await asyncpg.create_pool(
            self.dsn,
            min_size=2,
            max_size=10,
            command_timeout=60,
        )
        async with self._pool.acquire() as conn:
            await conn.execute(_SCHEMA_SQL)
        logger.info("Memory store initialized (Neon PostgreSQL)")

    async def close(self) -> None:
        """Close the connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None

    @property
    def pool(self) -> asyncpg.Pool:
        if not self._pool:
            raise RuntimeError("MemoryStore not initialized. Call initialize() first.")
        return self._pool

    # ------------------------------------------------------------------
    # Event Calendar
    # ------------------------------------------------------------------

    async def insert_event(self, event: EventRecord) -> str:
        """Insert a structured SVO event into the Event Calendar."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO events
                    (id, source_id, subject, verb, object, timestamp,
                     datetime_start, datetime_end, entity_aliases,
                     confidence, metadata_json, raw_text, created_at)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)
                ON CONFLICT (id) DO NOTHING
                """,
                event.id,
                event.source_id,
                event.subject,
                event.verb,
                event.object,
                event.timestamp,
                event.datetime_start,
                event.datetime_end,
                json.dumps(event.entity_aliases),
                event.confidence,
                json.dumps(event.metadata_json),
                event.raw_text,
                event.created_at,
            )
        return event.id

    async def insert_events_batch(self, events: list[EventRecord]) -> list[str]:
        """Batch insert multiple events using COPY protocol — fastest possible."""
        if not events:
            return []

        rows = [
            (
                e.id, e.source_id, e.subject, e.verb, e.object,
                e.timestamp, e.datetime_start, e.datetime_end,
                json.dumps(e.entity_aliases), e.confidence,
                json.dumps(e.metadata_json), e.raw_text, e.created_at,
            )
            for e in events
        ]

        async with self.pool.acquire() as conn:
            await conn.executemany(
                """
                INSERT INTO events
                    (id, source_id, subject, verb, object, timestamp,
                     datetime_start, datetime_end, entity_aliases,
                     confidence, metadata_json, raw_text, created_at)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)
                ON CONFLICT (id) DO NOTHING
                """,
                rows,
            )
        return [e.id for e in events]

    async def query_temporal(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        source_ids: Optional[list[str]] = None,
        limit: int = 50,
    ) -> list[EventRecord]:
        """Query events by time range."""
        conditions, params = [], []
        i = 1

        if start:
            conditions.append(f"timestamp >= ${i}"); params.append(start); i += 1
        if end:
            conditions.append(f"timestamp <= ${i}"); params.append(end); i += 1
        if source_ids:
            conditions.append(f"source_id = ANY(${i})"); params.append(source_ids); i += 1

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        params.append(limit)
        query = f"SELECT * FROM events {where} ORDER BY timestamp DESC LIMIT ${i}"

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
        return [self._row_to_event(r) for r in rows]

    async def query_by_entity(
        self,
        entity: str,
        source_ids: Optional[list[str]] = None,
        limit: int = 50,
    ) -> list[EventRecord]:
        """Find events involving a specific entity (subject or object)."""
        pattern = f"%{entity}%"
        conditions = ["(subject ILIKE $1 OR object ILIKE $1 OR entity_aliases::text ILIKE $1)"]
        params: list = [pattern]
        i = 2

        if source_ids:
            conditions.append(f"source_id = ANY(${i})"); params.append(source_ids); i += 1

        params.append(limit)
        where = f"WHERE {' AND '.join(conditions)}"
        query = f"SELECT * FROM events {where} ORDER BY timestamp DESC LIMIT ${i}"

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
        return [self._row_to_event(r) for r in rows]

    async def multi_hop_query(
        self,
        entities: list[str],
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        source_ids: Optional[list[str]] = None,
        limit: int = 50,
    ) -> list[EventRecord]:
        """
        Multi-hop temporal query: find events connecting multiple entities.
        The key Chronos differentiator.
        """
        entity_parts, params = [], []
        i = 1
        for entity in entities:
            pattern = f"%{entity}%"
            entity_parts.append(
                f"(subject ILIKE ${i} OR object ILIKE ${i} OR entity_aliases::text ILIKE ${i})"
            )
            params.append(pattern); i += 1

        conditions = [f"({' OR '.join(entity_parts)})"]

        if start:
            conditions.append(f"timestamp >= ${i}"); params.append(start); i += 1
        if end:
            conditions.append(f"timestamp <= ${i}"); params.append(end); i += 1
        if source_ids:
            conditions.append(f"source_id = ANY(${i})"); params.append(source_ids); i += 1

        params.append(limit)
        where = f"WHERE {' AND '.join(conditions)}"
        query = f"SELECT * FROM events {where} ORDER BY timestamp ASC LIMIT ${i}"

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
        return [self._row_to_event(r) for r in rows]

    async def get_event(self, event_id: str) -> Optional[EventRecord]:
        """Fetch a single event by ID."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM events WHERE id = $1", event_id)
        return self._row_to_event(row) if row else None

    async def get_events_by_ids(self, event_ids: list[str]) -> list[EventRecord]:
        """Fetch multiple events by their IDs."""
        if not event_ids:
            return []
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM events WHERE id = ANY($1)", event_ids
            )
        return [self._row_to_event(r) for r in rows]

    async def count_events(self, source_id: Optional[str] = None) -> int:
        """Count total events, optionally filtered by source."""
        async with self.pool.acquire() as conn:
            if source_id:
                return await conn.fetchval(
                    "SELECT COUNT(*) FROM events WHERE source_id = $1", source_id
                )
            return await conn.fetchval("SELECT COUNT(*) FROM events")

    # ------------------------------------------------------------------
    # Turn Calendar
    # ------------------------------------------------------------------

    async def insert_turn(self, turn: TurnRecord) -> str:
        """Insert a raw conversation turn into the Turn Calendar."""
        async with self.pool.acquire() as conn:
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

    async def get_turns(
        self,
        source_id: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 50,
    ) -> list[TurnRecord]:
        """Query conversation turns."""
        conditions, params = [], []
        i = 1

        if source_id:
            conditions.append(f"source_id = ${i}"); params.append(source_id); i += 1
        if start:
            conditions.append(f"timestamp >= ${i}"); params.append(start); i += 1
        if end:
            conditions.append(f"timestamp <= ${i}"); params.append(end); i += 1

        params.append(limit)
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"SELECT * FROM turns {where} ORDER BY timestamp DESC LIMIT ${i}"

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
        return [self._row_to_turn(r) for r in rows]

    # ------------------------------------------------------------------
    # Connectors
    # ------------------------------------------------------------------

    async def insert_connector(self, connector: ConnectorRecord) -> str:
        """Register a SaaS tool connector."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO connectors
                    (id, source_id, name, description, base_url,
                     auth_header, endpoints, metadata, created_at)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
                ON CONFLICT (id) DO UPDATE SET
                    name=EXCLUDED.name, description=EXCLUDED.description,
                    base_url=EXCLUDED.base_url, auth_header=EXCLUDED.auth_header,
                    endpoints=EXCLUDED.endpoints, metadata=EXCLUDED.metadata
                """,
                connector.id, connector.source_id, connector.name,
                connector.description, connector.base_url, connector.auth_header,
                json.dumps([ep.model_dump() for ep in connector.endpoints]),
                json.dumps(connector.metadata), connector.created_at,
            )
        return connector.id

    async def get_connectors(self, source_id: Optional[str] = None) -> list[ConnectorRecord]:
        """List registered connectors."""
        async with self.pool.acquire() as conn:
            if source_id:
                rows = await conn.fetch(
                    "SELECT * FROM connectors WHERE source_id = $1", source_id
                )
            else:
                rows = await conn.fetch("SELECT * FROM connectors")
        return [self._row_to_connector(r) for r in rows]

    async def get_connector(self, connector_id: str) -> Optional[ConnectorRecord]:
        """Fetch a single connector by ID."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM connectors WHERE id = $1", connector_id
            )
        return self._row_to_connector(row) if row else None

    async def count_connectors(self, source_id: str) -> int:
        """Count connectors for a source."""
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT COUNT(*) FROM connectors WHERE source_id = $1", source_id
            )

    # ------------------------------------------------------------------
    # API Keys & Usage
    # ------------------------------------------------------------------

    async def register_api_key(
        self, key_hash: str, source_id: str, tier: TierName = TierName.EXPLORER,
    ) -> None:
        """Register a new API key."""
        now = datetime.utcnow()
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO api_keys
                    (key_hash, source_id, tier, events_used, orchestration_used,
                     connectors_used, period_start, created_at)
                VALUES ($1,$2,$3,0,0,0,$4,$4)
                ON CONFLICT (key_hash) DO NOTHING
                """,
                key_hash, source_id, tier.value, now,
            )

    async def get_usage(self, source_id: str) -> Optional[UsageStats]:
        """Get usage stats for a source."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM api_keys WHERE source_id = $1", source_id
            )
        if not row:
            return None
        return UsageStats(
            source_id=row["source_id"],
            tier=TierName(row["tier"]),
            events_used=row["events_used"],
            orchestration_used=row["orchestration_used"],
            connectors_used=row["connectors_used"],
            period_start=row["period_start"],
        )

    async def increment_usage(
        self, source_id: str, events: int = 0, orchestration: int = 0,
    ) -> None:
        """Increment usage counters for a source."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE api_keys SET
                    events_used = events_used + $1,
                    orchestration_used = orchestration_used + $2
                WHERE source_id = $3
                """,
                events, orchestration, source_id,
            )

    async def validate_api_key(self, key_hash: str) -> Optional[dict]:
        """Validate an API key and return source info."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM api_keys WHERE key_hash = $1", key_hash
            )
        return dict(row) if row else None

    # ------------------------------------------------------------------
    # Row Converters
    # ------------------------------------------------------------------

    @staticmethod
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
        )

    @staticmethod
    def _row_to_turn(row) -> TurnRecord:
        return TurnRecord(
            id=row["id"],
            source_id=row["source_id"],
            role=TurnRole(row["role"]),
            content=row["content"],
            timestamp=row["timestamp"],
            event_ids=json.loads(row["event_ids"]) if isinstance(row["event_ids"], str) else (row["event_ids"] or []),
            created_at=row["created_at"],
        )

    @staticmethod
    def _row_to_connector(row) -> ConnectorRecord:
        from .models import ConnectorEndpoint
        endpoints_raw = json.loads(row["endpoints"]) if isinstance(row["endpoints"], str) else (row["endpoints"] or [])
        return ConnectorRecord(
            id=row["id"],
            source_id=row["source_id"],
            name=row["name"],
            description=row["description"] or "",
            base_url=row["base_url"],
            auth_header=row["auth_header"],
            endpoints=[ConnectorEndpoint(**ep) for ep in endpoints_raw],
            metadata=json.loads(row["metadata"]) if isinstance(row["metadata"], str) else (row["metadata"] or {}),
            created_at=row["created_at"],
        )
