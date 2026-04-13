"""
Chronos OS — Dependency Injection
==================================
Provides shared instances of core services to FastAPI routes.
"""

from __future__ import annotations

from chronos_core.memory_store import MemoryStore
from chronos_core.vector_store import VectorStore
from chronos_core.svo_parser import SVOParser

# ---------------------------------------------------------------------------
# Singleton instances (initialized in main.py lifespan)
# ---------------------------------------------------------------------------

_memory_store: MemoryStore | None = None
_vector_store: VectorStore | None = None
_svo_parser: SVOParser | None = None


def set_stores(
    memory: MemoryStore,
    vector: VectorStore,
    parser: SVOParser,
) -> None:
    """Called once during app lifespan startup."""
    global _memory_store, _vector_store, _svo_parser
    _memory_store = memory
    _vector_store = vector
    _svo_parser = parser


def get_memory_store() -> MemoryStore:
    """FastAPI dependency: get the SQLite memory store."""
    if not _memory_store:
        raise RuntimeError("MemoryStore not initialized")
    return _memory_store


def get_vector_store() -> VectorStore:
    """FastAPI dependency: get the ChromaDB vector store."""
    if not _vector_store:
        raise RuntimeError("VectorStore not initialized")
    return _vector_store


def get_svo_parser() -> SVOParser:
    """FastAPI dependency: get the SVO parser."""
    if not _svo_parser:
        raise RuntimeError("SVOParser not initialized")
    return _svo_parser
