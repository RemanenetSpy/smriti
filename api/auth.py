"""
Smriti — API Key Authentication
=====================================
Middleware to validate X-API-Key headers against the SQLite api_keys table.
Supports tier-based rate limiting and usage tracking.
"""

from __future__ import annotations

import hashlib
import secrets
import logging
from typing import Optional

from fastapi import HTTPException, Security, Request
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials

from smriti_core.models import TierName, TIER_LIMITS
from .deps import get_memory_store

logger = logging.getLogger("smriti.auth")

# ---------------------------------------------------------------------------
# API Key header scheme
# ---------------------------------------------------------------------------

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)


def hash_api_key(key: str) -> str:
    """Hash an API key for storage (SHA-256)."""
    return hashlib.sha256(key.encode()).hexdigest()


def generate_api_key() -> str:
    """Generate a new secure API key."""
    return f"chrn_{secrets.token_urlsafe(32)}"


async def verify_api_key(
    request: Request,
    api_key_header: Optional[str] = Security(api_key_header),
    bearer_token: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
) -> dict:
    """
    FastAPI dependency: validate the API key from either X-API-Key or Bearer token.
    Raises 401 if missing, 403 if invalid.
    """
    api_key = api_key_header
    if not api_key and bearer_token:
        api_key = bearer_token.credentials

    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Include X-API-Key header or Authorization: Bearer token.",
        )

    key_hash = hash_api_key(api_key)
    store = get_memory_store()
    key_info = await store.validate_api_key(key_hash)

    if not key_info:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key.",
        )

    return key_info


async def check_event_quota(source_id: str, event_count: int = 1) -> None:
    """
    Check if the source has enough event quota remaining.
    Raises 429 if quota exceeded on Explorer tier (hard cap).
    """
    store = get_memory_store()
    usage = await store.get_usage(source_id)

    if not usage:
        return  # No usage record = no limits enforced yet

    tier = usage.tier
    limits = TIER_LIMITS[tier]

    if tier == TierName.EXPLORER and usage.events_used + event_count > limits.events_per_month:
        raise HTTPException(
            status_code=429,
            detail=(
                f"Event quota exceeded ({usage.events_used}/{limits.events_per_month}). "
                f"Upgrade to Builder ($49/mo) for 500k events/month."
            ),
        )


async def check_orchestration_quota(source_id: str) -> None:
    """
    Check if the source has enough orchestration quota remaining.
    Raises 429 if quota exceeded on Explorer tier (hard cap).
    """
    store = get_memory_store()
    usage = await store.get_usage(source_id)

    if not usage:
        return

    tier = usage.tier
    limits = TIER_LIMITS[tier]

    if tier == TierName.EXPLORER and usage.orchestration_used >= limits.orchestration_per_month:
        raise HTTPException(
            status_code=429,
            detail=(
                f"Orchestration quota exceeded ({usage.orchestration_used}/{limits.orchestration_per_month}). "
                f"Upgrade to Builder ($49/mo) for 10k calls/month."
            ),
        )
