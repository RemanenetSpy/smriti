"""
Chronos OS — Agent Nodes
==========================
Individual processing nodes for the LangGraph state graph.
Each node performs a single responsibility in the agent pipeline.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

logger = logging.getLogger("chronos.agent.nodes")

# System prompt for the Chronos agent
CHRONOS_SYSTEM_PROMPT = """You are a Chronos OS Agent — an AI assistant with structured temporal long-term memory.

You have access to the Chronos temporal memory system, which stores events as Subject-Verb-Object (SVO) tuples with timestamps. This gives you the ability to:

1. **Recall past events** across any connected SaaS tool or data source
2. **Reason temporally** — understand what happened when, in what order, and how events relate across time
3. **Multi-hop reasoning** — connect events across different time periods and sources
4. **Record new observations** to build your memory over time

When answering questions:
- Always check your temporal memory for relevant context
- Cite specific events and timestamps when available
- If you store a new event, confirm what you recorded
- Be precise about temporal relationships (before, after, during, caused by)

You are the persistent spine that makes AI agents actually useful over time."""


async def retrieve_memory_node(state: dict) -> dict:
    """
    Node: Retrieve relevant temporal memory before the agent responds.
    Queries ChromaDB (semantic) filtered by owner_id for tenant isolation.
    """
    from api.deps import get_memory_store, get_vector_store

    messages = state.get("messages", [])
    owner_id = state.get("owner_id", "")

    # Get the last user message as the query
    last_user_msg = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_user_msg = msg.content
            break

    if not last_user_msg:
        return state

    try:
        vector = get_vector_store()
        memory = get_memory_store()

        # Semantic search — filtered by owner for privacy
        search_results = await vector.semantic_search(
            query=last_user_msg,
            n_results=10,
            owner_id=owner_id or None,  # Tenant isolation
        )

        # Fetch full events
        event_ids = [r["id"] for r in search_results]
        events = await memory.get_events_by_ids(event_ids) if event_ids else []

        # Build memory context
        if events:
            memory_lines = ["[Chronos Temporal Memory Context]"]
            for event in events:
                memory_lines.append(
                    f"  [{event.timestamp.strftime('%Y-%m-%d %H:%M')}] "
                    f"{event.subject} {event.verb} {event.object}"
                    + (f" | {event.raw_text[:100]}" if event.raw_text else "")
                )
            memory_context = "\n".join(memory_lines)
        else:
            memory_context = "[Chronos Memory: No relevant past events found]"

        state["memory_context"] = memory_context
        state["events_retrieved"] = len(events)

    except Exception as e:
        logger.warning(f"Memory retrieval failed: {e}")
        state["memory_context"] = "[Chronos Memory: Retrieval unavailable]"
        state["events_retrieved"] = 0

    return state


async def call_model_node(state: dict) -> dict:
    """
    Node: Call the LLM with memory-augmented context.
    Uses the Heavy Pipeline from the Mixture of Agents Router.
    Memory context is injected into the system prompt by retrieve_memory_node,
    so the model can reason about temporal events without tool calling.
    """
    messages = state.get("messages", [])
    memory_context = state.get("memory_context", "")

    # Build augmented system message
    system_content = CHRONOS_SYSTEM_PROMPT
    if memory_context:
        system_content += f"\n\n{memory_context}"

    # Ensure system message is first
    augmented = [SystemMessage(content=system_content)]
    for msg in messages:
        if not isinstance(msg, SystemMessage):
            if isinstance(msg, AIMessage):
                # Strip reasoning_content from prior assistant messages to prevent 
                # "property reasoning_content is unsupported" errors in multi-turn
                clean_kwargs = dict(msg.additional_kwargs)
                clean_kwargs.pop("reasoning_content", None)
                
                clean_msg = AIMessage(
                    content=msg.content,
                    additional_kwargs=clean_kwargs,
                    id=msg.id,
                    tool_calls=msg.tool_calls,
                    invalid_tool_calls=msg.invalid_tool_calls,
                )
                augmented.append(clean_msg)
            else:
                augmented.append(msg)

    # Get the LLM from the Mixture of Agents Router (Heavy Pipeline)
    try:
        from chronos_core.llm_router import get_heavy_pipeline
        
        llm = get_heavy_pipeline()

        # Bind tools so the agent can interact with SaaS connectors
        from agent.tools import CHRONOS_TOOLS
        
        # Tools to bind (we can exclude memory since it's injected, but let's give it all)
        llm_with_tools = llm.bind_tools(CHRONOS_TOOLS)

        response = await llm_with_tools.ainvoke(augmented)
        state["messages"] = messages + [response]

    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        error_msg = AIMessage(
            content=f"I apologize, but I encountered an error: {str(e)}. "
            f"Please check your API key configuration (CEREBRAS_API_KEY / GROQ_API_KEY)."
        )
        state["messages"] = messages + [error_msg]

    return state


async def execute_tools_node(state: dict) -> dict:
    """
    Node: Execute tool calls from the LLM response.
    Handles Chronos-specific tools (memory query, event ingest, connectors).
    """
    from langchain_core.messages import ToolMessage

    messages = state.get("messages", [])
    if not messages:
        return state

    last_msg = messages[-1]
    if not isinstance(last_msg, AIMessage) or not last_msg.tool_calls:
        return state

    tool_messages = []

    for tool_call in last_msg.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_id = tool_call.get("id", "")

        try:
            result = await _execute_tool(tool_name, tool_args, state)
            tool_messages.append(
                ToolMessage(content=result, tool_call_id=tool_id)
            )
        except Exception as e:
            logger.error(f"Tool execution failed: {tool_name} — {e}")
            tool_messages.append(
                ToolMessage(
                    content=f"Tool error: {str(e)}",
                    tool_call_id=tool_id,
                )
            )

    state["messages"] = messages + tool_messages
    return state


async def _execute_tool(name: str, args: dict, state: dict) -> str:
    """Execute a specific Chronos tool and return the result."""
    from api.deps import get_memory_store, get_vector_store

    if name == "query_chronos_memory":
        vector = get_vector_store()
        memory = get_memory_store()

        results = await vector.semantic_search(
            query=args.get("query", ""),
            n_results=int(args.get("max_results", 10)),
            source_ids=state.get("source_ids"),
        )

        event_ids = [r["id"] for r in results]
        events = await memory.get_events_by_ids(event_ids) if event_ids else []

        return json.dumps([
            {
                "timestamp": e.timestamp.isoformat(),
                "subject": e.subject,
                "verb": e.verb,
                "object": e.object,
                "raw_text": e.raw_text[:200] if e.raw_text else "",
                "confidence": e.confidence,
            }
            for e in events
        ], indent=2)

    elif name == "ingest_chronos_event":
        from chronos_core.models import EventRecord

        memory = get_memory_store()
        vector = get_vector_store()

        source_ids = state.get("source_ids", ["agent"])
        event = EventRecord(
            source_id=source_ids[0] if source_ids else "agent",
            subject=args.get("subject", "agent"),
            verb=args.get("verb", "recorded"),
            object=args.get("obj", args.get("object", "")),
            raw_text=args.get("raw_text", ""),
            timestamp=datetime.utcnow(),
        )

        await memory.insert_event(event)
        await vector.add_event(event)

        state["events_created"] = state.get("events_created", 0) + 1
        return f"Event stored: {event.subject} {event.verb} {event.object} at {event.timestamp.isoformat()}"

    elif name == "list_connected_tools":
        memory = get_memory_store()
        source_ids = state.get("source_ids", [])
        connectors = await memory.get_connectors(
            source_ids[0] if source_ids else None
        )
        return json.dumps([
            {
                "id": c.id,
                "name": c.name,
                "description": c.description,
                "endpoints": len(c.endpoints),
            }
            for c in connectors
        ], indent=2)

    elif name == "call_connected_tool":
        # Execute HTTP call to connected SaaS
        import httpx

        memory = get_memory_store()
        connector = await memory.get_connector(args.get("connector_id", ""))

        if not connector:
            return "Error: Connector not found"

        url = connector.base_url.rstrip("/") + args.get("endpoint_path", "/")
        method = args.get("method", "GET").upper()

        headers = {}
        if connector.auth_header:
            headers[connector.auth_header] = "CONFIGURED"  # Would need actual auth

        async with httpx.AsyncClient(timeout=30) as client:
            if method == "GET":
                resp = await client.get(url, headers=headers)
            elif method == "POST":
                body = json.loads(args.get("body", "{}")) if args.get("body") else {}
                resp = await client.post(url, headers=headers, json=body)
            else:
                return f"Unsupported method: {method}"

        return f"Status: {resp.status_code}\n{resp.text[:500]}"

    else:
        return f"Unknown tool: {name}"
