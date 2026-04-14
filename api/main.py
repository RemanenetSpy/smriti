"""
Chronos OS — FastAPI Application
==================================
The API gateway for the Chronos Temporal AI Agent Ecosystem.
Backend: Neon PostgreSQL + pgvector (persistent cloud storage).

Endpoints:
  POST /ingest        — Universal event ingestion
  POST /query         — Hybrid temporal + semantic retrieval
  POST /connect       — Register SaaS tools
  GET  /connectors    — List connected tools
  POST /agent/run     — Execute agent with temporal memory
  POST /billing/*     — Razorpay checkout + usage
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from chronos_core.memory_store import MemoryStore
from chronos_core.vector_store import VectorStore
from chronos_core.svo_parser import SVOParser
from api.deps import set_stores

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("chronos.api")


# ---------------------------------------------------------------------------
# Application Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and tear down core services."""
    logger.info("🕰️  Chronos OS starting up...")

    # Initialize Memory Store (Neon PostgreSQL via asyncpg pool)
    memory_store = MemoryStore()
    await memory_store.initialize()

    # Initialize Vector Store (pgvector — shares the same pool)
    vector_store = VectorStore()
    await vector_store.initialize(pool=memory_store.pool)

    # Initialize SVO Parser (LiteLLM Mixture of Agents Router)
    svo_parser = SVOParser()

    # Register singletons for dependency injection
    set_stores(memory_store, vector_store, svo_parser)

    logger.info("✅ Chronos OS ready — Neon PostgreSQL + pgvector online")

    yield  # App is running

    # Shutdown
    logger.info("🔒 Chronos OS shutting down...")
    await memory_store.close()
    logger.info("👋 Goodbye from Chronos OS")


# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Chronos OS",
    description=(
        "The Temporal AI Agent Ecosystem. "
        "Structured long-term memory for every agent and SaaS product. "
        "Powered by SVO event tuples + dual calendar architecture."
    ),
    version="0.2.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow all origins for development / Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

from api.routes.ingest import router as ingest_router
from api.routes.query import router as query_router
from api.routes.connectors import router as connectors_router
from api.routes.agent import router as agent_router
from api.routes.billing import router as billing_router

app.include_router(ingest_router)
app.include_router(query_router)
app.include_router(connectors_router)
app.include_router(agent_router)
app.include_router(billing_router)


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------

@app.get("/", tags=["Health"])
async def health_check():
    """Health check — verify Chronos OS is alive."""
    return {
        "service": "Chronos OS",
        "version": "0.2.0",
        "status": "operational",
        "storage": "Neon PostgreSQL + pgvector",
        "tagline": "Letters to the Future — for agents.",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def detailed_health():
    """Detailed health check with system stats."""
    from api.deps import get_memory_store, get_vector_store

    try:
        memory = get_memory_store()
        vector = get_vector_store()

        event_count = await memory.count_events()
        vector_count = await vector.count()

        return {
            "status": "healthy",
            "stores": {
                "postgres_events": event_count,
                "pgvector_embeddings": vector_count,
            },
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
        }
