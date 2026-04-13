"""
Chronos OS — Memory Store
==========================
Dual-calendar SQLite storage engine.
  • Event Calendar — structured SVO events with temporal indexing
  • Turn Calendar  — raw conversation turns for full context

Implements the Chronos research paper's dual-calendar architecture
for temporal-aware retrieval and multi-hop reasoning.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Optional

import aiosqlite

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
-- Event Calendar: structured SVO events
CREATE TABLE IF NOT EXISTS events (
    id              TEXT PRIMARY KEY,
    source_id       TEXT NOT NULL,
    subject         TEXT NOT NULL,
    verb            TEXT NOT NULL,
    object          TEXT NOT NULL,
    timestamp       TEXT NOT NULL,
    datetime_start  TEXT,
    datetime_end    TEXT,
    entity_aliases  TEXT DEFAULT '[]',
    confidence      REAL DEFAULT 1.0,
    metadata_json   TEXT DEFAULT '{}',
    raw_text        TEXT DEFAULT '',
    created_at      TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_events_source     ON events(source_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp  ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_subject    ON events(subject);
CREATE INDEX IF NOT EXISTS idx_events_verb       ON events(verb);

-- Turn Calendar: raw conversation turns
CREATE TABLE IF NOT EXISTS turns (
    id          TEXT PRIMARY KEY,
    source_id   TEXT NOT NULL,
    role        TEXT NOT NULL DEFAULT 'user',
    content     TEXT NOT NULL,
    timestamp   TEXT NOT NULL,
    event_ids   TEXT DEFAULT '[]',
    created_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_turns_source    ON turns(source_id);
CREATE INDEX IF NOT EXISTS idx_turns_timestamp ON turns(timestamp);

-- Connectors: registered SaaS tools
CREATE TABLE IF NOT EXISTS connectors (
    id          TEXT PRIMARY KEY,
    source_id   TEXT NOT NULL,
    name        TEXT NOT NULL,
    description TEXT DEFAULT '',
    base_url    TEXT NOT NULL,
    auth_header TEXT,
    endpoints   TEXT DEFAULT '[]',
    metadata    TEXT DEFAULT '{}',
    created_at  TEXT NOT NULL
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
    period_start        TEXT NOT NULL,
    created_at          TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_apikeys_source ON api_keys(source_id);
"""


class MemoryStore:
    """
    Async SQLite-backed dual-calendar memory store.
    Thread-safe via aiosqlite's connection pooling.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.getenv(
            "CHRONOS_DB_PATH", "./data/chronos.db"
        )
        self._db: Optional[aiosqlite.Connection] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def initialize(self) -> None:
        """Create database and tables if they don't exist."""
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        self._db = await aiosqlite.connect(self.db_path)
        self._db.row_factory = aiosqlite.Row
        await self._db.executescript(_SCHEMA_SQL)
        await self._db.commit()
        logger.info(f"Memory store initialized at {self.db_path}")

    async def close(self) -> None:
        """Close the database connection."""
        if self._db:
            await self._db.close()
            self._db = None

    @property
    def db(self) -> aiosqlite.Connection:
        if not self._db:
            raise RuntimeError("MemoryStore not initialized. Call initialize() first.")
        return self._db

    # ------------------------------------------------------------------
    # Event Calendar
    # ------------------------------------------------------------------

    async def insert_event(self, event: EventRecord) -> str:
        """Insert a structured SVO event into the Event Calendar."""
        await self.db.execute(
            """INSERT INTO events
               (id, source_id, subject, verb, object, timestamp,
                datetime_start, datetime_end, entity_aliases,
                confidence, metadata_json, raw_text, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                event.id,
                event.source_id,
                event.subject,
                event.verb,
                event.object,
                event.timestamp.isoformat(),
                event.datetime_start.isoformat() if event.datetime_start else None,
                event.datetime_end.isoformat() if event.datetime_end else None,
                json.dumps(event.entity_aliases),
                event.confidence,
                json.dumps(event.metadata_json),
                event.raw_text,
                event.created_at.isoformat(),
            ),
        )
        await self.db.commit()
        return event.id

    async def insert_events_batch(self, events: list[EventRecord]) -> list[str]:
        """Batch insert multiple events."""
        ids = []
        for event in events:
            await self.db.execute(
                """INSERT INTO events
                   (id, source_id, subject, verb, object, timestamp,
                    datetime_start, datetime_end, entity_aliases,
                    confidence, metadata_json, raw_text, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    event.id,
                    event.source_id,
                    event.subject,
                    event.verb,
                    event.object,
                    event.timestamp.isoformat(),
                    event.datetime_start.isoformat() if event.datetime_start else None,
                    event.datetime_end.isoformat() if event.datetime_end else None,
                    json.dumps(event.entity_aliases),
                    event.confidence,
                    json.dumps(event.metadata_json),
                    event.raw_text,
                    event.created_at.isoformat(),
                ),
            )
            ids.append(event.id)
        await self.db.commit()
        return ids

    async def query_temporal(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        source_ids: Optional[list[str]] = None,
        limit: int = 50,
    ) -> list[EventRecord]:
        """Query events by time range."""
        conditions = []
        params: list = []

        if start:
            conditions.append("timestamp >= ?")
            params.append(start.isoformat())
        if end:
            conditions.append("timestamp <= ?")
            params.append(end.isoformat())
        if source_ids:
            placeholders = ",".join("?" * len(source_ids))
            conditions.append(f"source_id IN ({placeholders})")
            params.extend(source_ids)

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"SELECT * FROM events {where} ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        async with self.db.execute(query, params) as cursor:
            rows = await cursor.fetchall()

        return [self._row_to_event(row) for row in rows]

    async def query_by_entity(
        self,
        entity: str,
        source_ids: Optional[list[str]] = None,
        limit: int = 50,
    ) -> list[EventRecord]:
        """Find events involving a specific entity (subject or object)."""
        conditions = [
            "(subject LIKE ? OR object LIKE ? OR entity_aliases LIKE ?)"
        ]
        pattern = f"%{entity}%"
        params: list = [pattern, pattern, pattern]

        if source_ids:
            placeholders = ",".join("?" * len(source_ids))
            conditions.append(f"source_id IN ({placeholders})")
            params.extend(source_ids)

        where = f"WHERE {' AND '.join(conditions)}"
        query = f"SELECT * FROM events {where} ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        async with self.db.execute(query, params) as cursor:
            rows = await cursor.fetchall()

        return [self._row_to_event(row) for row in rows]

    async def multi_hop_query(
        self,
        entities: list[str],
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        source_ids: Optional[list[str]] = None,
        limit: int = 50,
    ) -> list[EventRecord]:
        """
        Multi-hop temporal query: find events that connect multiple entities
        across time. The key Chronos differentiator.
        """
        entity_conditions = []
        params: list = []

        for entity in entities:
            pattern = f"%{entity}%"
            entity_conditions.append(
                "(subject LIKE ? OR object LIKE ? OR entity_aliases LIKE ?)"
            )
            params.extend([pattern, pattern, pattern])

        conditions = [f"({' OR '.join(entity_conditions)})"]

        if start:
            conditions.append("timestamp >= ?")
            params.append(start.isoformat())
        if end:
            conditions.append("timestamp <= ?")
            params.append(end.isoformat())
        if source_ids:
            placeholders = ",".join("?" * len(source_ids))
            conditions.append(f"source_id IN ({placeholders})")
            params.extend(source_ids)

        where = f"WHERE {' AND '.join(conditions)}"
        query = f"SELECT * FROM events {where} ORDER BY timestamp ASC LIMIT ?"
        params.append(limit)

        async with self.db.execute(query, params) as cursor:
            rows = await cursor.fetchall()

        return [self._row_to_event(row) for row in rows]

    async def get_event(self, event_id: str) -> Optional[EventRecord]:
        """Fetch a single event by ID."""
        async with self.db.execute(
            "SELECT * FROM events WHERE id = ?", (event_id,)
        ) as cursor:
            row = await cursor.fetchone()
        return self._row_to_event(row) if row else None

    async def get_events_by_ids(self, event_ids: list[str]) -> list[EventRecord]:
        """Fetch multiple events by their IDs."""
        if not event_ids:
            return []
        placeholders = ",".join("?" * len(event_ids))
        async with self.db.execute(
            f"SELECT * FROM events WHERE id IN ({placeholders})", event_ids
        ) as cursor:
            rows = await cursor.fetchall()
        return [self._row_to_event(row) for row in rows]

    async def count_events(self, source_id: Optional[str] = None) -> int:
        """Count total events, optionally filtered by source."""
        if source_id:
            async with self.db.execute(
                "SELECT COUNT(*) FROM events WHERE source_id = ?", (source_id,)
            ) as cursor:
                row = await cursor.fetchone()
        else:
            async with self.db.execute("SELECT COUNT(*) FROM events") as cursor:
                row = await cursor.fetchone()
        return row[0] if row else 0

    # ------------------------------------------------------------------
    # Turn Calendar
    # ------------------------------------------------------------------

    async def insert_turn(self, turn: TurnRecord) -> str:
        """Insert a raw conversation turn into the Turn Calendar."""
        await self.db.execute(
            """INSERT INTO turns
               (id, source_id, role, content, timestamp, event_ids, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                turn.id,
                turn.source_id,
                turn.role.value,
                turn.content,
                turn.timestamp.isoformat(),
                json.dumps(turn.event_ids),
                turn.created_at.isoformat(),
            ),
        )
        await self.db.commit()
        return turn.id

    async def get_turns(
        self,
        source_id: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 50,
    ) -> list[TurnRecord]:
        """Query conversation turns."""
        conditions = []
        params: list = []

        if source_id:
            conditions.append("source_id = ?")
            params.append(source_id)
        if start:
            conditions.append("timestamp >= ?")
            params.append(start.isoformat())
        if end:
            conditions.append("timestamp <= ?")
            params.append(end.isoformat())

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"SELECT * FROM turns {where} ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        async with self.db.execute(query, params) as cursor:
            rows = await cursor.fetchall()

        return [self._row_to_turn(row) for row in rows]

    # ------------------------------------------------------------------
    # Connectors
    # ------------------------------------------------------------------

    async def insert_connector(self, connector: ConnectorRecord) -> str:
        """Register a SaaS tool connector."""
        await self.db.execute(
            """INSERT OR REPLACE INTO connectors
               (id, source_id, name, description, base_url,
                auth_header, endpoints, metadata, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                connector.id,
                connector.source_id,
                connector.name,
                connector.description,
                connector.base_url,
                connector.auth_header,
                json.dumps([ep.model_dump() for ep in connector.endpoints]),
                json.dumps(connector.metadata),
                connector.created_at.isoformat(),
            ),
        )
        await self.db.commit()
        return connector.id

    async def get_connectors(
        self, source_id: Optional[str] = None
    ) -> list[ConnectorRecord]:
        """List registered connectors."""
        if source_id:
            async with self.db.execute(
                "SELECT * FROM connectors WHERE source_id = ?", (source_id,)
            ) as cursor:
                rows = await cursor.fetchall()
        else:
            async with self.db.execute("SELECT * FROM connectors") as cursor:
                rows = await cursor.fetchall()
        return [self._row_to_connector(row) for row in rows]

    async def get_connector(self, connector_id: str) -> Optional[ConnectorRecord]:
        """Fetch a single connector by ID."""
        async with self.db.execute(
            "SELECT * FROM connectors WHERE id = ?", (connector_id,)
        ) as cursor:
            row = await cursor.fetchone()
        return self._row_to_connector(row) if row else None

    async def count_connectors(self, source_id: str) -> int:
        """Count connectors for a source."""
        async with self.db.execute(
            "SELECT COUNT(*) FROM connectors WHERE source_id = ?", (source_id,)
        ) as cursor:
            row = await cursor.fetchone()
        return row[0] if row else 0

    # ------------------------------------------------------------------
    # API Keys & Usage
    # ------------------------------------------------------------------

    async def register_api_key(
        self,
        key_hash: str,
        source_id: str,
        tier: TierName = TierName.EXPLORER,
    ) -> None:
        """Register a new API key."""
        now = datetime.utcnow().isoformat()
        await self.db.execute(
            """INSERT OR REPLACE INTO api_keys
               (key_hash, source_id, tier, events_used,
                orchestration_used, connectors_used, period_start, created_at)
               VALUES (?, ?, ?, 0, 0, 0, ?, ?)""",
            (key_hash, source_id, tier.value, now, now),
        )
        await self.db.commit()

    async def get_usage(self, source_id: str) -> Optional[UsageStats]:
        """Get usage stats for a source."""
        async with self.db.execute(
            "SELECT * FROM api_keys WHERE source_id = ?", (source_id,)
        ) as cursor:
            row = await cursor.fetchone()

        if not row:
            return None

        return UsageStats(
            source_id=row["source_id"],
            tier=TierName(row["tier"]),
            events_used=row["events_used"],
            orchestration_used=row["orchestration_used"],
            connectors_used=row["connectors_used"],
            period_start=datetime.fromisoformat(row["period_start"]),
        )

    async def increment_usage(
        self,
        source_id: str,
        events: int = 0,
        orchestration: int = 0,
    ) -> None:
        """Increment usage counters for a source."""
        if events > 0:
            await self.db.execute(
                "UPDATE api_keys SET events_used = events_used + ? WHERE source_id = ?",
                (events, source_id),
            )
        if orchestration > 0:
            await self.db.execute(
                "UPDATE api_keys SET orchestration_used = orchestration_used + ? WHERE source_id = ?",
                (orchestration, source_id),
            )
        await self.db.commit()

    async def validate_api_key(self, key_hash: str) -> Optional[dict]:
        """Validate an API key and return source info."""
        async with self.db.execute(
            "SELECT * FROM api_keys WHERE key_hash = ?", (key_hash,)
        ) as cursor:
            row = await cursor.fetchone()
        if row:
            return dict(row)
        return None

    # ------------------------------------------------------------------
    # Row Converters
    # ------------------------------------------------------------------

    @staticmethod
    def _row_to_event(row) -> EventRecord:
        """Convert a database row to an EventRecord."""
        return EventRecord(
            id=row["id"],
            source_id=row["source_id"],
            subject=row["subject"],
            verb=row["verb"],
            object=row["object"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            datetime_start=(
                datetime.fromisoformat(row["datetime_start"])
                if row["datetime_start"] else None
            ),
            datetime_end=(
                datetime.fromisoformat(row["datetime_end"])
                if row["datetime_end"] else None
            ),
            entity_aliases=json.loads(row["entity_aliases"] or "[]"),
            confidence=row["confidence"],
            metadata_json=json.loads(row["metadata_json"] or "{}"),
            raw_text=row["raw_text"] or "",
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    @staticmethod
    def _row_to_turn(row) -> TurnRecord:
        """Convert a database row to a TurnRecord."""
        return TurnRecord(
            id=row["id"],
            source_id=row["source_id"],
            role=TurnRole(row["role"]),
            content=row["content"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            event_ids=json.loads(row["event_ids"] or "[]"),
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    @staticmethod
    def _row_to_connector(row) -> ConnectorRecord:
        """Convert a database row to a ConnectorRecord."""
        from .models import ConnectorEndpoint
        endpoints_raw = json.loads(row["endpoints"] or "[]")
        endpoints = [ConnectorEndpoint(**ep) for ep in endpoints_raw]

        return ConnectorRecord(
            id=row["id"],
            source_id=row["source_id"],
            name=row["name"],
            description=row["description"] or "",
            base_url=row["base_url"],
            auth_header=row["auth_header"],
            endpoints=endpoints,
            metadata=json.loads(row["metadata"] or "{}"),
            created_at=datetime.fromisoformat(row["created_at"]),
        )
