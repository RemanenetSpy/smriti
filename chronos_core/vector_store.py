"""
Chronos OS — Vector Store
==========================
ChromaDB semantic search layer.
Works alongside the SQLite Memory Store for hybrid retrieval:
  • ChromaDB → broad semantic recall (fuzzy)
  • SQLite   → precise temporal / entity filtering (deterministic)

Together they deliver the Chronos dual-retrieval pipeline.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Optional

from .models import EventRecord

logger = logging.getLogger("chronos.vector_store")


class VectorStore:
    """
    ChromaDB-backed semantic search over Chronos events.
    Stores embeddings of raw event text with SQLite event IDs
    as metadata for cross-store joins.
    """

    def __init__(self, persist_dir: Optional[str] = None):
        self.persist_dir = persist_dir or os.getenv(
            "CHROMA_PERSIST_DIR", "./data/chroma"
        )
        self._client = None
        self._collection = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def initialize(self) -> None:
        """Initialize ChromaDB client and collection."""
        import asyncio
        await asyncio.to_thread(self._sync_initialize)

    def _sync_initialize(self) -> None:
        """Synchronous ChromaDB initialization (called via to_thread)."""
        import chromadb
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

        os.makedirs(self.persist_dir, exist_ok=True)

        self._client = chromadb.PersistentClient(path=self.persist_dir)

        # Use sentence-transformers (downloads from HuggingFace Hub — fast)
        # instead of ChromaDB's default ONNX model (very slow CDN)
        embedding_fn = SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        self._collection = self._client.get_or_create_collection(
            name="chronos_events",
            embedding_function=embedding_fn,
            metadata={
                "description": "Chronos temporal event embeddings",
                "hnsw:space": "cosine",
            },
        )
        count = self._collection.count()
        logger.info(
            f"Vector store initialized at {self.persist_dir} "
            f"({count} existing embeddings)"
        )

    @property
    def collection(self):
        if not self._collection:
            raise RuntimeError(
                "VectorStore not initialized. Call initialize() first."
            )
        return self._collection

    # ------------------------------------------------------------------
    # Insert
    # ------------------------------------------------------------------

    async def add_event(self, event: EventRecord) -> None:
        """
        Embed and store an event.
        Uses ChromaDB's built-in embedding function (all-MiniLM-L6-v2 by default).
        """
        import asyncio

        # Build the text to embed: combine SVO + raw for richer semantics
        embed_text = self._build_embed_text(event)

        await asyncio.to_thread(
            self.collection.add,
            ids=[event.id],
            documents=[embed_text],
            metadatas=[{
                "source_id": event.source_id,
                "owner_id": event.metadata_json.get("owner_id", event.source_id),
                "subject": event.subject,
                "verb": event.verb,
                "object": event.object,
                "timestamp": event.timestamp.isoformat(),
                "confidence": event.confidence,
            }],
        )

    async def add_events_batch(self, events: list[EventRecord]) -> None:
        """Batch embed and store multiple events."""
        if not events:
            return

        import asyncio

        ids = [e.id for e in events]
        documents = [self._build_embed_text(e) for e in events]
        metadatas = [
            {
                "source_id": e.source_id,
                "owner_id": e.metadata_json.get("owner_id", e.source_id),
                "subject": e.subject,
                "verb": e.verb,
                "object": e.object,
                "timestamp": e.timestamp.isoformat(),
                "confidence": e.confidence,
            }
            for e in events
        ]

        await asyncio.to_thread(
            self.collection.add,
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )
        logger.info(f"Batch added {len(events)} events to vector store")

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
    ) -> list[dict]:
        """
        Semantic search over embedded events.
        Returns list of {id, distance, metadata} dicts.
        
        Privacy: when owner_id is set, only events belonging to that
        owner are returned (tenant isolation).
        """
        import asyncio

        # Build WHERE filter
        where_filter = self._build_where_filter(
            source_ids, start_time, end_time, owner_id
        )

        kwargs = {
            "query_texts": [query],
            "n_results": min(n_results, self.collection.count() or 1),
        }
        if where_filter:
            kwargs["where"] = where_filter

        results = await asyncio.to_thread(
            self.collection.query,
            **kwargs,
        )

        # Flatten results
        output = []
        if results and results["ids"] and results["ids"][0]:
            for i, event_id in enumerate(results["ids"][0]):
                output.append({
                    "id": event_id,
                    "distance": results["distances"][0][i] if results.get("distances") else 0,
                    "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                    "document": results["documents"][0][i] if results.get("documents") else "",
                })

        return output

    async def count(self) -> int:
        """Get total number of embeddings."""
        import asyncio
        return await asyncio.to_thread(self.collection.count)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_embed_text(event: EventRecord) -> str:
        """Build the text to embed for an event."""
        parts = [
            f"{event.subject} {event.verb} {event.object}",
        ]
        if event.raw_text:
            parts.append(event.raw_text)
        return " | ".join(parts)

    @staticmethod
    def _build_where_filter(
        source_ids: Optional[list[str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        owner_id: Optional[str] = None,
    ) -> Optional[dict]:
        """Build a ChromaDB WHERE filter with tenant isolation."""
        conditions = []

        # Tenant isolation: owner_id takes priority
        if owner_id:
            conditions.append({"owner_id": {"$eq": owner_id}})
        elif source_ids and len(source_ids) == 1:
            conditions.append({"source_id": {"$eq": source_ids[0]}})
        elif source_ids and len(source_ids) > 1:
            conditions.append({"source_id": {"$in": source_ids}})

        if start_time:
            conditions.append({"timestamp": {"$gte": start_time.isoformat()}})
        if end_time:
            conditions.append({"timestamp": {"$lte": end_time.isoformat()}})

        if not conditions:
            return None
        if len(conditions) == 1:
            return conditions[0]
        return {"$and": conditions}
