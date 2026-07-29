import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Optional, Any

from smriti_core.models import EventRecord, TurnRecord, LiteEventRecord, QueryResult, TierName

class InMemoryMemoryStore:
    def __init__(self):
        self.events: dict[str, EventRecord] = {}
        self.api_keys: dict[str, dict] = {}
        self.usage: dict[str, UsageRecord] = {}

    async def initialize(self):
        pass

    async def close(self):
        pass

    async def register_api_key(self, key_hash: str, source_id: str, tier: TierName = TierName.EXPLORER):
        now = datetime.now(timezone.utc)
        self.api_keys[key_hash] = {
            "key_hash": key_hash,
            "source_id": source_id,
            "tier": tier,
            "events_used": 0,
            "orchestration_used": 0,
            "connectors_used": 0,
            "period_start": now,
            "created_at": now,
        }

    async def validate_api_key(self, key_hash: str) -> Optional[dict]:
        return self.api_keys.get(key_hash, {"source_id": "bench_owner", "tier": TierName.SCALE})

    async def increment_usage(self, owner_id: str, events: int = 0) -> None:
        pass

    async def get_usage(self, source_id: str) -> Optional[Any]:
        return None

    async def find_active_by_subject(self, owner_id: str, scope: str, subject: str) -> list[EventRecord]:
        out = []
        for e in self.events.values():
            if e.scope == scope and e.subject.lower() == subject.lower():
                if not e.metadata_json.get("superseded_by"):
                    out.append(e)
        return out

    async def invalidate_event(self, event_id: str, superseded_by: str) -> None:
        if event_id in self.events:
            self.events[event_id].metadata_json["superseded_by"] = superseded_by

    async def insert_events_batch(self, events: list[EventRecord]) -> list[str]:
        return await self.store_events(events)

    async def store_events(self, events: list[EventRecord]) -> list[str]:
        ids = []
        for e in events:
            if not e.id:
                e.id = f"evt_{uuid.uuid4().hex[:12]}"
            self.events[e.id] = e
            ids.append(e.id)
        return ids

    async def insert_turn(self, turn: TurnRecord) -> str:
        return await self.store_turn(turn)

    async def store_turn(self, turn: TurnRecord) -> str:
        return f"turn_{uuid.uuid4().hex[:8]}"

    async def get_events_by_ids(self, event_ids: list[str]) -> list[EventRecord]:
        return [self.events[eid] for eid in event_ids if eid in self.events]

    async def query_temporal(self, start=None, end=None, source_ids=None, scope=None, limit=20) -> list[EventRecord]:
        res = list(self.events.values())
        if scope:
            res = [e for e in res if e.scope == scope]
        return res[:limit]

    async def multi_hop_query(self, entities: list[str], start=None, end=None, source_ids=None, scope=None, limit=20) -> list[EventRecord]:
        res = []
        for e in self.events.values():
            if scope and e.scope != scope:
                continue
            text = f"{e.subject} {e.verb} {e.object} {' '.join(e.entity_aliases or [])}"
            if any(ent.lower() in text.lower() for ent in entities):
                res.append(e)
        return res[:limit]

class InMemoryVectorStore:
    def __init__(self):
        import chromadb
        self._chroma = chromadb.Client(chromadb.Settings(anonymized_telemetry=False))
        self._col = self._chroma.get_or_create_collection("smriti_bench", metadata={"hnsw:space": "cosine"})

    async def initialize(self, pool=None):
        pass

    async def add_events_batch(self, events: list[EventRecord]) -> None:
        await self.store_embeddings(events)

    async def store_embeddings(self, events: list[EventRecord]) -> None:
        if not events:
            return
        from sentence_transformers import SentenceTransformer
        if not hasattr(self, '_model'):
            self._model = SentenceTransformer('all-MiniLM-L6-v2')

        ids = [e.id for e in events]
        docs = [f"{e.subject} {e.verb} {e.object} {' '.join(e.entity_aliases or [])} {e.raw_text}" for e in events]
        embeddings = self._model.encode(docs, normalize_embeddings=True).tolist()
        metas = [{"owner_id": e.metadata_json.get("owner_id", "bench_owner"), "scope": e.scope, "event_id": e.id} for e in events]
        self._col.upsert(ids=ids, embeddings=embeddings, documents=docs, metadatas=metas)

    async def semantic_search(self, query: str, n_results: int = 20, owner_id: str = None, source_ids=None, start_time=None, end_time=None, scope: str = None, similarity_threshold: float = 0.45) -> list[dict]:
        from sentence_transformers import SentenceTransformer
        if not hasattr(self, '_model'):
            self._model = SentenceTransformer('all-MiniLM-L6-v2')
        emb = self._model.encode(query, normalize_embeddings=True).tolist()
        
        count = self._col.count()
        if count == 0:
            return []

        res = self._col.query(query_embeddings=[emb], n_results=min(n_results*3, count), include=["metadatas", "distances"])
        out = []
        cutoff = similarity_threshold
        for meta, dist in zip(res["metadatas"][0], res["distances"][0]):
            if dist > cutoff:
                continue
            if scope and meta.get("scope") != scope:
                continue
            out.append({"id": meta["event_id"], "distance": dist})
        return out[:n_results]
