"""
KAAL — Pydantic Models
============================
Data models for the Chronos temporal memory system.
SVO event tuples, calendar records, API payloads, and query structures.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TierName(str, Enum):
    """Subscription tier names."""
    EXPLORER = "explorer"
    BUILDER = "builder"
    SCALE = "scale"


class TurnRole(str, Enum):
    """Role of a conversation participant."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


# ---------------------------------------------------------------------------
# Core Data Structures
# ---------------------------------------------------------------------------

class SVOTuple(BaseModel):
    """
    Subject-Verb-Object event tuple — the atomic unit of Chronos memory.
    Decomposed from raw text by the SVO parser (LiteLLM Mixture of Agents).
    """
    subject: str = Field(..., description="The entity performing the action")
    verb: str = Field(..., description="The action being performed")
    object: str = Field(..., description="The entity being acted upon")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this event occurred"
    )
    datetime_start: Optional[datetime] = Field(
        None, description="Start of the event's time range (if span)"
    )
    datetime_end: Optional[datetime] = Field(
        None, description="End of the event's time range (if span)"
    )
    entity_aliases: list[str] = Field(
        default_factory=list,
        description="Alternative names for entities (e.g., 'John', 'J. Doe')"
    )
    confidence: float = Field(
        default=1.0, ge=0.0, le=1.0,
        description="Parser confidence in this extraction"
    )


class EventRecord(BaseModel):
    """
    Structured event stored in the Event Calendar.
    One SVO tuple + metadata = one EventRecord.

    Bi-temporal validity (Zep-style):
      valid_from  — when this fact became true (ingest time by default)
      valid_to    — when this fact was superseded (NULL = currently active)
      superseded_by — ID of the newer event that replaced this one
    """
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    source_id: str = Field(..., description="ID of the connected SaaS/agent source")
    subject: str
    verb: str
    object: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    datetime_start: Optional[datetime] = None
    datetime_end: Optional[datetime] = None
    entity_aliases: list[str] = Field(default_factory=list)
    confidence: float = 1.0
    metadata_json: dict[str, Any] = Field(default_factory=dict)
    raw_text: str = Field(default="", description="Original text this event was parsed from")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # ── Scope & Bi-temporal validity ──────────────────────────────────────────
    scope: str = Field(default="default", description="Logical namespace (e.g. 'work', 'personal')")
    valid_from: datetime = Field(default_factory=datetime.utcnow, description="When this fact became active")
    valid_to: Optional[datetime] = Field(None, description="When this fact was superseded (NULL = active)")
    superseded_by: Optional[str] = Field(None, description="ID of the event that replaced this one")


class LiteEventRecord(BaseModel):
    """
    10x smaller event object for search results.
    Excludes massive text fields for lightning-fast UI rendering.
    """
    id: str
    source_id: str
    subject: str
    verb: str
    object: str
    timestamp: datetime
    confidence: float


class TurnRecord(BaseModel):
    """
    Raw conversation turn stored in the Turn Calendar (SQLite).
    Preserves full context alongside structured events.
    """
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    source_id: str = Field(..., description="ID of the connected SaaS/agent source")
    role: TurnRole = TurnRole.USER
    content: str = Field(..., description="Raw text content of this turn")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_ids: list[str] = Field(
        default_factory=list,
        description="IDs of EventRecords extracted from this turn"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Connector (SaaS Tool Registration)
# ---------------------------------------------------------------------------

class ConnectorEndpoint(BaseModel):
    """A single API endpoint exposed by a connected SaaS tool."""
    method: str = Field("GET", description="HTTP method")
    path: str = Field(..., description="Endpoint path (e.g., /api/invoices)")
    description: str = Field("", description="What this endpoint does")
    parameters: dict[str, Any] = Field(default_factory=dict)


class ConnectorRegistration(BaseModel):
    """Schema for registering a SaaS product with KAAL."""
    name: str = Field(..., description="Display name (e.g., 'Stripe', 'Notion')")
    description: str = Field("", description="What this tool does")
    base_url: str = Field(..., description="Base API URL")
    auth_header: Optional[str] = Field(None, description="Auth header name")
    endpoints: list[ConnectorEndpoint] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ConnectorRecord(ConnectorRegistration):
    """Stored connector with ID and timestamps."""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    source_id: str = Field(..., description="Owner's source ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# API Request / Response Payloads
# ---------------------------------------------------------------------------

class IngestEvent(BaseModel):
    """A single event in an ingest payload."""
    text: str = Field(..., description="Raw text to parse into SVO events")
    timestamp: Optional[datetime] = Field(
        None, description="When this event happened (defaults to now)"
    )
    metadata: dict[str, Any] = Field(default_factory=dict)
    scope: Optional[str] = Field(
        None,
        description="Scope override for this specific event (overrides payload-level scope)"
    )


class IngestPayload(BaseModel):
    """
    POST /ingest request body.
    Any SaaS or agent sends events here.
    """
    source_id: str = Field(..., description="Your registered source ID")
    events: list[IngestEvent] = Field(
        ..., min_length=1,
        description="List of events to ingest"
    )
    parse_svo: bool = Field(
        True, description="Whether to extract SVO tuples (uses LLM)"
    )
    scope: str = Field(
        default="default",
        description="Logical namespace for all events in this payload (e.g. 'work', 'personal')"
    )


class IngestResponse(BaseModel):
    """POST /ingest response."""
    ingested_count: int
    event_ids: list[str]
    svo_tuples: list[SVOTuple] = Field(default_factory=list)
    turn_ids: list[str] = Field(default_factory=list)


class TimeRange(BaseModel):
    """A time window for temporal queries."""
    start: Optional[datetime] = None
    end: Optional[datetime] = None


class QueryRequest(BaseModel):
    """
    POST /query request body.
    Supports hybrid temporal + semantic retrieval.
    """
    query: str = Field(..., description="Natural language query")
    time_range: Optional[TimeRange] = None
    source_ids: list[str] = Field(
        default_factory=list,
        description="Filter by specific sources (empty = all)"
    )
    max_results: int = Field(default=20, ge=1, le=100)
    semantic_weight: float = Field(
        default=0.5, ge=0.0, le=1.0,
        description="Balance between semantic (1.0) and temporal (0.0) ranking"
    )
    scope: Optional[str] = Field(
        None,
        description="Restrict results to this scope only (None = all scopes for this owner)"
    )
    similarity_threshold: float = Field(
        default=None,  # None → resolved from config at request time
        ge=0.0, le=1.0,
        description="Max cosine distance to include (cosine distance, not similarity). "
                    "None = use SMRITI_SIMILARITY_THRESHOLD env var (default 0.15). "
                    "Lower = stricter: 0.10 ≈ ≥90%%, 0.15 ≈ ≥85%%, 0.30 ≈ ≥70%%.",
    )

    def resolved_threshold(self) -> float:
        """Return the effective threshold, falling back to config if not set."""
        from chronos_core.config import SIMILARITY_THRESHOLD
        if self.similarity_threshold is None:
            return SIMILARITY_THRESHOLD
        return self.similarity_threshold


class QueryResult(BaseModel):
    """A single result from a /query response."""
    event: LiteEventRecord
    relevance_score: float = Field(0.0, description="Combined ranking score")
    provenance: str = Field("", description="How this result was found")


class QueryResponse(BaseModel):
    """POST /query response."""
    results: list[QueryResult]
    total_found: int
    query_time_ms: float


# ---------------------------------------------------------------------------
# Agent Runner Payloads
# ---------------------------------------------------------------------------

class AgentRunRequest(BaseModel):
    """POST /agent/run request body."""
    prompt: str = Field(..., description="Agent task/question")
    thread_id: Optional[str] = Field(
        None, description="Resume a previous thread (None = new)"
    )
    source_ids: list[str] = Field(
        default_factory=list,
        description="Memory scopes to search"
    )
    tools: list[str] = Field(
        default_factory=list,
        description="Additional connector tool IDs to enable"
    )
    max_steps: int = Field(default=10, ge=1, le=50)


class AgentRunResponse(BaseModel):
    """POST /agent/run response."""
    thread_id: str
    response: str
    steps: list[dict[str, Any]] = Field(default_factory=list)
    events_retrieved: int = 0
    events_created: int = 0


# ---------------------------------------------------------------------------
# Billing / Usage
# ---------------------------------------------------------------------------

class TierLimits(BaseModel):
    """Limits for a subscription tier."""
    events_per_month: int
    orchestration_per_month: int
    connected_tools: int
    retention_days: int  # -1 = unlimited
    agent_threads: int
    event_overage_per_1k: float  # $ per 1k events over limit
    orchestration_overage: float  # $ per call over limit


# Tier configurations matching the pricing table
TIER_LIMITS: dict[TierName, TierLimits] = {
    TierName.EXPLORER: TierLimits(
        events_per_month=10_000,
        orchestration_per_month=1_000,
        connected_tools=3,
        retention_days=30,
        agent_threads=5,
        event_overage_per_1k=0.0,  # No overage — hard cap
        orchestration_overage=0.0,
    ),
    TierName.BUILDER: TierLimits(
        events_per_month=500_000,
        orchestration_per_month=10_000,
        connected_tools=25,
        retention_days=365,
        agent_threads=100,
        event_overage_per_1k=0.05,
        orchestration_overage=0.10,
    ),
    TierName.SCALE: TierLimits(
        events_per_month=5_000_000,
        orchestration_per_month=-1,  # Unlimited
        connected_tools=-1,  # Unlimited
        retention_days=-1,   # Unlimited
        agent_threads=-1,    # Unlimited
        event_overage_per_1k=0.03,
        orchestration_overage=0.07,
    ),
}


class UsageStats(BaseModel):
    """Current usage for a source/API key."""
    source_id: str
    tier: TierName = TierName.EXPLORER
    events_used: int = 0
    orchestration_used: int = 0
    connectors_used: int = 0
    period_start: datetime = Field(default_factory=datetime.utcnow)
    period_end: Optional[datetime] = None


class BillingCheckoutRequest(BaseModel):
    """POST /billing/checkout request."""
    tier: TierName
    success_url: str = "https://chronos-hub.app/success"
    cancel_url: str = "https://chronos-hub.app/cancel"


class BillingCheckoutResponse(BaseModel):
    """POST /billing/checkout response."""
    checkout_url: str
    session_id: str
