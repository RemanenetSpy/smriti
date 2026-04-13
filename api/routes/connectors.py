"""
Chronos OS — Connectors Route
===============================
POST /connect  — Register a SaaS product's API schema
GET  /connectors — List all connected tools
Non-agentic SaaS instantly becomes agent-actionable.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from chronos_core.models import (
    ConnectorRegistration,
    ConnectorRecord,
    TIER_LIMITS,
    TierName,
)
from api.auth import verify_api_key
from api.deps import get_memory_store

logger = logging.getLogger("chronos.routes.connectors")

router = APIRouter(tags=["Connectors"])


@router.post("/connect", response_model=dict)
async def register_connector(
    registration: ConnectorRegistration,
    key_info: dict = Depends(verify_api_key),
):
    """
    Register a SaaS product with Chronos OS.
    The product's API endpoints become available as tools for agents.
    Non-agentic SaaS instantly becomes agent-actionable.
    """
    source_id = key_info["source_id"]
    tier = TierName(key_info["tier"])
    memory = get_memory_store()

    # Check connector quota
    current_count = await memory.count_connectors(source_id)
    limit = TIER_LIMITS[tier].connected_tools

    if limit != -1 and current_count >= limit:
        raise HTTPException(
            status_code=429,
            detail=(
                f"Connector limit reached ({current_count}/{limit}). "
                f"Upgrade your tier for more connected tools."
            ),
        )

    # Create connector record
    connector = ConnectorRecord(
        source_id=source_id,
        name=registration.name,
        description=registration.description,
        base_url=registration.base_url,
        auth_header=registration.auth_header,
        endpoints=registration.endpoints,
        metadata=registration.metadata,
    )

    connector_id = await memory.insert_connector(connector)

    logger.info(
        f"Registered connector '{registration.name}' "
        f"({len(registration.endpoints)} endpoints) for source={source_id}"
    )

    return {
        "connector_id": connector_id,
        "name": registration.name,
        "endpoints_count": len(registration.endpoints),
        "message": f"'{registration.name}' is now agent-actionable in Chronos OS.",
    }


@router.get("/connectors", response_model=list[dict])
async def list_connectors(
    source_id: Optional[str] = None,
    key_info: dict = Depends(verify_api_key),
):
    """
    List all registered connectors.
    If source_id is provided, filter by that source.
    """
    memory = get_memory_store()

    # If no source_id filter, show the caller's connectors
    filter_source = source_id or key_info["source_id"]
    connectors = await memory.get_connectors(filter_source)

    return [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "base_url": c.base_url,
            "endpoints_count": len(c.endpoints),
            "created_at": c.created_at.isoformat(),
        }
        for c in connectors
    ]
