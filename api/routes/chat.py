"""
Smriti — Chat Demo Route
==========================
POST /chat/demo — Public demo chat endpoint for the KaalChat widget.
No API key required. Rate-limited to 5 messages per session.

Bridges KaalChat.tsx to the Smriti memory + LLM pipeline:
  1. Retrieve relevant memory via pgvector semantic search
  2. Inject memory context into system prompt
  3. Call the Heavy LLM pipeline (Cerebras / Groq fallback)
  4. Return { response, messages_remaining }
"""

from __future__ import annotations

import logging
import os
from collections import defaultdict

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

logger = logging.getLogger("smriti.routes.chat")

router = APIRouter(tags=["Chat"])

# ── Per-session rate limiting (in-memory, resets on server restart) ───────────
_session_usage: dict[str, int] = defaultdict(int)
DEMO_MESSAGE_LIMIT = int(os.getenv("CHAT_DEMO_LIMIT", "5"))

# ── System prompt for the demo chat ──────────────────────────────────────────
_SYSTEM_PROMPT = """You are Smriti — a temporal memory AI built by Kaal.
You have access to structured long-term memory stored as Subject-Verb-Object events with timestamps.

When answering:
- Check the memory context below for relevant past events
- Cite specific events and timestamps when available
- If no relevant memory exists, say so honestly
- Be concise and helpful

You can explain how the /ingest, /query, /agent/run, and /connect endpoints work.
You can show users how to ingest events, query memory, run agents, and connect SaaS tools.

Special keywords you can use in your reply to show feature cards:
  [SHOW:ingest]  — shows the ingest code example card
  [SHOW:query]   — shows the query code example card
  [SHOW:agent]   — shows the agent code example card
  [SHOW:connect] — shows the connector code example card
  [SHOW:apikey]  — shows the API key creation card
"""


# ── Request / Response models ─────────────────────────────────────────────────

class ChatDemoRequest(BaseModel):
    message: str
    session_id: str = "anonymous"
    consent: bool = False


class ChatDemoResponse(BaseModel):
    response: str
    messages_remaining: int


# ── POST /chat/demo ───────────────────────────────────────────────────────────

@router.post("/chat/demo", response_model=ChatDemoResponse)
async def chat_demo(request: ChatDemoRequest):
    """
    Public demo chat endpoint. No API key required.
    Rate-limited to DEMO_MESSAGE_LIMIT messages per session_id.
    Retrieves Smriti memory context and generates a response via the LLM.
    """
    session_id = request.session_id or "anonymous"
    used = _session_usage[session_id]

    # Rate limit check
    if used >= DEMO_MESSAGE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail={
                "message": (
                    f"You have used all {DEMO_MESSAGE_LIMIT} demo messages. "
                    "Get a free API key to continue with unlimited access!"
                )
            },
        )

    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # ── 1. Call the LLM (no memory search — this is a public guide bot) ─────────
    try:
        from smriti_core.llm_router import get_heavy_pipeline
        from langchain_core.messages import HumanMessage, SystemMessage

        llm = get_heavy_pipeline()
        messages = [
            SystemMessage(content=system_content),
            HumanMessage(content=message),
        ]

        ai_response = await llm.ainvoke(messages)

        # Extract text content (handle list content blocks from some models)
        content = ai_response.content
        if isinstance(content, list):
            response_text = " ".join(
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in content
                if not (isinstance(block, dict) and block.get("type") == "thinking")
            )
        else:
            response_text = str(content)

    except Exception as e:
        logger.error(f"LLM call failed in /chat/demo: {e}")
        response_text = (
            "I'm having trouble connecting to my reasoning engine right now. "
            "Please try again in a moment, or check that CEREBRAS_API_KEY / "
            "GROQ_API_KEY are set correctly in the server environment."
        )

    # ── 4. Increment usage and return ─────────────────────────────────────────
    _session_usage[session_id] += 1
    remaining = max(0, DEMO_MESSAGE_LIMIT - _session_usage[session_id])

    logger.info(
        f"[chat/demo] session={session_id} | used={_session_usage[session_id]}/{DEMO_MESSAGE_LIMIT} "
        f"| memory_events={len(search_results) if memory_context else 0}"
    )

    return ChatDemoResponse(
        response=response_text,
        messages_remaining=remaining,
    )
