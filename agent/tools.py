"""
Smriti — Agent Tools
==========================
Built-in tools that agents can use during execution.
These connect the LangGraph agent to the Chronos memory system.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

from langchain_core.tools import tool


@tool
def query_smriti_memory(
    query: str,
    time_start: Optional[str] = None,
    time_end: Optional[str] = None,
    max_results: str = "10",
) -> str:
    """
    Search Chronos temporal memory for relevant events.
    Use this to recall past events, conversations, and interactions.
    Supports natural language queries with optional time filtering.

    Args:
        query: Natural language search query
        time_start: ISO datetime string for time range start (optional)
        time_end: ISO datetime string for time range end (optional)
        max_results: Maximum number of results to return (as string)
    """
    return json.dumps({
        "tool": "query_smriti_memory",
        "query": query,
        "time_start": time_start,
        "time_end": time_end,
        "max_results": int(max_results) if max_results else 10,
        "note": "Results injected by graph runtime",
    })


@tool
def ingest_smriti_event(
    subject: str,
    verb: str,
    obj: str,
    raw_text: str = "",
) -> str:
    """
    Store a new event in Chronos temporal memory.
    Use this to record important findings, decisions, or observations
    during your work so they can be recalled later.

    Args:
        subject: Who or what is performing the action
        verb: The action being performed
        obj: Who or what is being acted upon
        raw_text: Optional full text description of the event
    """
    return json.dumps({
        "tool": "ingest_smriti_event",
        "subject": subject,
        "verb": verb,
        "object": obj,
        "raw_text": raw_text,
        "timestamp": datetime.utcnow().isoformat(),
    })


@tool
def list_connected_tools() -> str:
    """
    List all SaaS tools connected to Smriti.
    Use this to discover what external services and APIs are available.
    """
    return json.dumps({
        "tool": "list_connected_tools",
        "note": "Results injected by graph runtime",
    })


@tool
def call_connected_tool(
    connector_id: str,
    endpoint_path: str,
    method: str = "GET",
    body: Optional[str] = None,
) -> str:
    """
    Call a connected SaaS tool's API endpoint.
    Use list_connected_tools first to discover available tools.

    Args:
        connector_id: The ID of the connector to call
        endpoint_path: The API endpoint path (e.g., /api/invoices)
        method: HTTP method (GET, POST, PUT, DELETE)
        body: Optional JSON request body
    """
    return json.dumps({
        "tool": "call_connected_tool",
        "connector_id": connector_id,
        "endpoint_path": endpoint_path,
        "method": method,
        "body": body,
    })


# All available tools for the agent
CHRONOS_TOOLS = [
    query_smriti_memory,
    ingest_smriti_event,
    list_connected_tools,
    call_connected_tool,
]
