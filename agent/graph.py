"""
Chronos OS — Agent State Graph
================================
LangGraph state graph that orchestrates the Chronos agent.
Architecture: retrieve_memory → call_model → (tools loop) → END
"""

from __future__ import annotations

import logging
import uuid
from typing import Annotated, Any

from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from .nodes import (
    retrieve_memory_node,
    call_model_node,
    execute_tools_node,
)

logger = logging.getLogger("chronos.agent.graph")


# ---------------------------------------------------------------------------
# Agent State
# ---------------------------------------------------------------------------

class ChronosAgentState(TypedDict):
    """State shared across all nodes in the agent graph."""
    messages: Annotated[list[BaseMessage], add_messages]
    memory_context: str
    source_ids: list[str]
    owner_id: str  # Tenant isolation: only see own data
    tool_ids: list[str]
    events_retrieved: int
    events_created: int
    step_count: int
    max_steps: int


# ---------------------------------------------------------------------------
# Routing Logic
# ---------------------------------------------------------------------------

def should_continue(state: ChronosAgentState) -> str:
    """
    Conditional edge: decide whether to execute tools or finish.
    Returns 'tools' if the last message has tool calls, else 'end'.
    """
    messages = state.get("messages", [])
    step_count = state.get("step_count", 0)
    max_steps = state.get("max_steps", 10)

    # Safety: stop if we've exceeded max steps
    if step_count >= max_steps:
        logger.warning(f"Agent hit max steps ({max_steps}), stopping")
        return "end"

    if not messages:
        return "end"

    last_msg = messages[-1]
    if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
        return "tools"

    return "end"


async def increment_step(state: ChronosAgentState) -> ChronosAgentState:
    """Increment the step counter after tool execution."""
    state["step_count"] = state.get("step_count", 0) + 1
    return state


# ---------------------------------------------------------------------------
# Graph Construction
# ---------------------------------------------------------------------------

def build_agent_graph() -> StateGraph:
    """
    Build the Chronos agent state graph.

    Flow:
      START → retrieve_memory → call_model → [tools → call_model]* → END
    """
    workflow = StateGraph(ChronosAgentState)

    # Add nodes
    workflow.add_node("retrieve_memory", retrieve_memory_node)
    workflow.add_node("call_model", call_model_node)
    workflow.add_node("tools", execute_tools_node)
    workflow.add_node("increment", increment_step)

    # Add edges
    workflow.add_edge(START, "retrieve_memory")
    workflow.add_edge("retrieve_memory", "call_model")

    # Conditional: after model, either use tools or finish
    workflow.add_conditional_edges(
        "call_model",
        should_continue,
        {
            "tools": "tools",
            "end": END,
        },
    )

    # After tools, increment step count then go back to model
    workflow.add_edge("tools", "increment")
    workflow.add_edge("increment", "call_model")

    return workflow


# Compiled graph (singleton)
_graph = None


def get_agent_graph():
    """Get or create the compiled agent graph."""
    global _graph
    if _graph is None:
        workflow = build_agent_graph()
        _graph = workflow.compile()
        logger.info("Chronos agent graph compiled successfully")
    return _graph


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def run_agent_graph(
    prompt: str,
    thread_id: str | None = None,
    source_ids: list[str] | None = None,
    tool_ids: list[str] | None = None,
    max_steps: int = 10,
    owner_id: str = "",
) -> dict[str, Any]:
    """
    Run the Chronos agent with temporal memory.

    Args:
        prompt: The user's task/question
        thread_id: Session ID for continuity (None = new session)
        source_ids: Memory scopes to search
        tool_ids: Additional connector tool IDs to enable
        max_steps: Maximum tool-use iterations
        owner_id: API key owner for tenant-isolated memory access

    Returns:
        dict with: response, steps, events_retrieved, events_created
    """
    graph = get_agent_graph()
    tid = thread_id or uuid.uuid4().hex

    initial_state: ChronosAgentState = {
        "messages": [HumanMessage(content=prompt)],
        "memory_context": "",
        "source_ids": source_ids or [],
        "owner_id": owner_id,
        "tool_ids": tool_ids or [],
        "events_retrieved": 0,
        "events_created": 0,
        "step_count": 0,
        "max_steps": max_steps,
    }

    config = {"configurable": {"thread_id": tid}}

    try:
        result = await graph.ainvoke(initial_state, config=config)

        # Extract final response
        messages = result.get("messages", [])
        final_response = ""
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and msg.content and not msg.tool_calls:
                if isinstance(msg.content, list):
                    text_parts = []
                    for block in msg.content:
                        if isinstance(block, dict):
                            # Handle GLM/DeepSeek reasoning block formats
                            if block.get("type") == "text" and "text" in block:
                                text_parts.append(block["text"])
                            # Some models put text directly in 'text' without type
                            elif "text" in block and not block.get("type") == "thinking":
                                text_parts.append(block["text"])
                        elif isinstance(block, str):
                            text_parts.append(block)
                    final_response = "\n".join(text_parts)
                else:
                    final_response = str(msg.content)
                break

        # Build step log
        steps = []
        for i, msg in enumerate(messages):
            if isinstance(msg, AIMessage):
                content_str = str(msg.content) if msg.content else ""
                step = {"type": "ai", "content": content_str[:200]}
                if msg.tool_calls:
                    step["tool_calls"] = [
                        {"name": tc["name"], "args": tc["args"]}
                        for tc in msg.tool_calls
                    ]
                steps.append(step)

        return {
            "response": final_response,
            "thread_id": tid,
            "steps": steps,
            "events_retrieved": result.get("events_retrieved", 0),
            "events_created": result.get("events_created", 0),
        }

    except Exception as e:
        logger.error(f"Agent graph execution failed: {e}")
        return {
            "response": f"Agent error: {str(e)}",
            "thread_id": tid,
            "steps": [{"type": "error", "message": str(e)}],
            "events_retrieved": 0,
            "events_created": 0,
        }
