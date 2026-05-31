"""
KAAL — Agent Route
==========================
POST /agent/run — Execute an agent prompt with full Chronos temporal memory.
"""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends

from chronos_core.models import AgentRunRequest, AgentRunResponse
from api.auth import verify_api_key, check_orchestration_quota
from api.deps import get_memory_store

logger = logging.getLogger("chronos.routes.agent")

router = APIRouter(tags=["Agent"])


@router.post("/agent/run", response_model=AgentRunResponse)
async def run_agent(
    request: AgentRunRequest,
    key_info: dict = Depends(verify_api_key),
):
    """
    Execute an agent with Chronos temporal memory.

    The agent automatically:
    1. Retrieves relevant temporal context from memory
    2. Reasons over the prompt with memory-augmented context
    3. Can call connected SaaS tools
    4. Stores new events generated during execution
    """
    source_id = key_info["source_id"]

    # Check orchestration quota
    await check_orchestration_quota(source_id)

    thread_id = request.thread_id or uuid.uuid4().hex

    try:
        # Import agent runner (lazy to avoid import errors if deps missing)
        from agent.graph import run_agent_graph  # type: ignore

        result = await run_agent_graph(
            prompt=request.prompt,
            thread_id=thread_id,
            source_ids=[source_id],  # Filter by API key owner (tenant isolation)
            tool_ids=request.tools,
            max_steps=request.max_steps,
            owner_id=source_id,  # Privacy: only see own data
        )

        # Update usage
        memory = get_memory_store()
        await memory.increment_usage(source_id, orchestration=1)

        return AgentRunResponse(
            thread_id=thread_id,
            response=result.get("response", ""),
            steps=result.get("steps", []),
            events_retrieved=result.get("events_retrieved", 0),
            events_created=result.get("events_created", 0),
        )

    except ImportError:
        logger.warning("Agent runner not available — running simplified mode")

        # Simplified mode: just query memory and return context
        from api.deps import get_vector_store, get_svo_parser

        vector = get_vector_store()
        memory = get_memory_store()

        # Search memory for relevant context
        search_results = await vector.semantic_search(
            query=request.prompt,
            n_results=10,
            owner_id=source_id,  # Privacy: only see own data
        )

        # Build context from results
        context_parts = []
        event_ids = [r["id"] for r in search_results]
        if event_ids:
            events = await memory.get_events_by_ids(event_ids)
            for event in events:
                context_parts.append(
                    f"[{event.timestamp.isoformat()}] "
                    f"{event.subject} {event.verb} {event.object}"
                )

        context = "\n".join(context_parts) if context_parts else "No relevant memory found."

        await memory.increment_usage(source_id, orchestration=1)

        return AgentRunResponse(
            thread_id=thread_id,
            response=(
                f"[Simplified Mode — LangGraph not available]\n\n"
                f"Memory context for your query:\n{context}"
            ),
            steps=[{"type": "memory_retrieval", "results": len(search_results)}],
            events_retrieved=len(search_results),
            events_created=0,
        )

    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        return AgentRunResponse(
            thread_id=thread_id,
            response=f"Agent execution failed: {str(e)}",
            steps=[{"type": "error", "message": str(e)}],
        )
