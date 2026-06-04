"""
KAAL — TTS Route
==========================
POST /tts  — Convert text to speech using XTTSv2 with Amber's voice profile.
POST /chat/demo — Public demo chat endpoint (no API key required).
"""

from __future__ import annotations

import logging
import os
import time
import tempfile
import io
import re
from pathlib import Path
from typing import Optional
from fastapi import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel

logger = logging.getLogger("chronos.routes.voice")

router = APIRouter(tags=["Voice & Chat"])

# Path to Amber's voice reference file (committed to repo)
SPEAKER_WAV = Path(__file__).parent.parent.parent / "assets" / "amber_voice.wav"

# Lazy-loaded TTS instance
_tts_instance = None

def _get_tts():
    """Lazy-load XTTSv2 to avoid slowing startup. Loads on first /tts call."""
    global _tts_instance
    if _tts_instance is not None:
        return _tts_instance

    try:
        import torch
        # Patch torch.load for compatibility with newer PyTorch versions
        _orig_load = torch.load
        def _safe_load(*args, **kwargs):
            kwargs['weights_only'] = False
            return _orig_load(*args, **kwargs)
        torch.load = _safe_load

        from TTS.api import TTS
        os.environ["COQUI_TOS_AGREED"] = "1"
        logger.info("[TTS] Loading XTTSv2 model... (first call, may take ~60s)")
        _tts_instance = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
        torch.load = _orig_load
        logger.info("[TTS] XTTSv2 loaded successfully.")
    except Exception as e:
        logger.error(f"[TTS] Failed to load model: {e}")
        raise e

    return _tts_instance


# ---------------------------------------------------------------------------
# TTS Endpoint
# ---------------------------------------------------------------------------

class TTSRequest(BaseModel):
    text: str
    language: str = "en"

@router.post("/tts", summary="Text to Speech — Amber's voice (XTTSv2)")
async def speak(req: TTSRequest):
    """
    Convert text to speech using XTTSv2 with Amber's cloned voice.
    Returns audio/wav stream. Rate limited by reverse proxy.
    """
    if not req.text or len(req.text.strip()) == 0:
        return JSONResponse(status_code=400, content={"error": "text is required"})

    if len(req.text) > 500:
        return JSONResponse(status_code=400, content={"error": "text too long (max 500 chars)"})

    if not SPEAKER_WAV.exists():
        logger.error(f"[TTS] Speaker wav not found at {SPEAKER_WAV}")
        return JSONResponse(status_code=503, content={"error": "Voice reference file missing."})

    try:
        tts = _get_tts()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        tts.tts_to_file(
            text=req.text.strip(),
            speaker_wav=str(SPEAKER_WAV),
            language=req.language,
            file_path=tmp_path,
        )

        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()

        os.unlink(tmp_path)

        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/wav",
            headers={"Content-Disposition": "inline; filename=kaal_voice.wav"},
        )
    except Exception as e:
        logger.error(f"[TTS] Generation failed: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# ---------------------------------------------------------------------------
# Demo Chat Endpoint (no API key required)
# ---------------------------------------------------------------------------

# 12 pre-built template responses — AI only edits the last sentence
TEMPLATES = {
    "what_is_kaal": "Kaal is a temporal memory engine that gives AI agents structured, persistent, queryable memory. Every piece of information you ingest is automatically parsed into a Subject-Verb-Object tuple, timestamped in both Gregorian and Hijri calendars, and semantically embedded. It's the memory layer your LLM never had.",
    "ingest": "Ingesting events is how you write memory into Kaal. You send natural language text — like 'Ali closed the Acme Corp deal for $50k on Monday' — and Kaal automatically parses the Subject, Verb, and Object, attaches a timestamp, generates a 384-dimension embedding, and stores it in Neon PostgreSQL. No pre-formatting needed.",
    "query": "The query endpoint runs two retrieval passes simultaneously: a semantic vector search using pgvector and a temporal keyword scan. Results are fused using a weighted ranking function. You can use natural language and temporal anchors like 'last week' or 'before Q2' — Kaal parses them automatically.",
    "agent": "The agent orchestration pipeline runs GPT OSS 120B on Cerebras hardware — roughly 2,100 tokens per second. Before every LLM call, a memory_inject_node fetches the most relevant events from your temporal store and injects them as context. If the agent needs external data, it calls your registered connectors automatically.",
    "connect": "The Connector Registry lets you register any external API as an agent-callable tool. You POST a tool name, base URL, description, and a JSON schema of endpoints. The agent discovers and calls these tools automatically when context suggests they're needed — no code changes required.",
    "apikey": "Your API key is your identity in Kaal. Every event, query, and connector is scoped to your key's source_id, so your data is completely isolated from other users. To get a key, click 'API Keys' in the sidebar and complete the verification — it takes about 2 minutes.",
    "billing": "The Explorer tier is completely free — 10,000 events per month, 100 orchestrations, and 3 connected tools. Your current usage is shown in the Billing tab once you add an API key. Paid tiers with higher limits are coming soon.",
    "pricing": "Kaal's Explorer tier is free with no credit card required. You get 10,000 events per month, 100 orchestrations, and 3 tool connections — enough to build and test a full memory-augmented agent.",
    "svo": "SVO stands for Subject-Verb-Object. When you ingest text, Llama 3.1 8B running on Cerebras extracts a structured tuple from it — for example, 'Ali closed the Acme Corp deal' becomes subject='Ali', verb='closed', object='Acme Corp deal'. This structure is what makes Kaal's memory actually queryable instead of just searchable.",
    "temporal": "Kaal stores two timestamps for every event: Gregorian (machine time) and Hijri (Islamic calendar). This makes it uniquely suited for markets where both calendars are operationally relevant — scheduling, finance, compliance. Temporal anchors in queries like 'before Ramadan' or 'last Dhul Hijja' are parsed automatically.",
    "demo": "Let me show you how Kaal works. You can use the Ingest tab to write an event like 'Sara closed a deal with Acme Corp for $50k today', then switch to the Query tab and ask 'What deals did Sara close this month?' — Kaal will retrieve it instantly using hybrid temporal + semantic search.",
    "help": "I'm here to help. You can ask me what Kaal does, how to ingest events, how querying works, what the agent can do, how to connect tools, or how to get your API key. What would you like to know?",
}

def _classify_intent(message: str) -> Optional[str]:
    """Keyword-based intent classifier. Returns a template key or None."""
    m = message.lower()
    if any(k in m for k in ["what is kaal", "what does kaal", "tell me about kaal", "explain kaal"]):
        return "what_is_kaal"
    if any(k in m for k in ["ingest", "save event", "write event", "add event", "how to save"]):
        return "ingest"
    if any(k in m for k in ["query", "search memory", "find event", "retrieve", "search event"]):
        return "query"
    if any(k in m for k in ["agent", "gpt", "llm", "orchestrat", "run agent", "ai agent"]):
        return "agent"
    if any(k in m for k in ["connect", "tool", "connector", "stripe", "notion", "github", "saas"]):
        return "connect"
    if any(k in m for k in ["api key", "get key", "apikey", "how to start", "authenticate"]):
        return "apikey"
    if any(k in m for k in ["billing", "usage", "quota", "limit", "how much"]):
        return "billing"
    if any(k in m for k in ["pric", "cost", "free", "paid", "tier", "plan"]):
        return "pricing"
    if any(k in m for k in ["svo", "subject verb", "subject-verb", "how memory work", "parse"]):
        return "svo"
    if any(k in m for k in ["temporal", "time", "hijri", "gregorian", "calendar", "timestamp"]):
        return "temporal"
    if any(k in m for k in ["demo", "show me", "example", "see it", "try it"]):
        return "demo"
    if any(k in m for k in ["help", "confused", "stuck", "what can", "how do i"]):
        return "help"
    return None

# Simple in-memory session rate limiter (resets on server restart — good enough for demo)
_session_counts: dict[str, int] = {}
MAX_DEMO_MESSAGES = 5

class DemoChatRequest(BaseModel):
    message: str
    session_id: str
    consent: bool = False

@router.post("/chat/demo", summary="Public demo chat — no API key required")
async def demo_chat(req: DemoChatRequest):
    """
    Public AI chat endpoint for the Kaal dashboard demo experience.
    - Rate limited to 5 messages per session
    - Template-first: serves pre-built answers for known intents (low token cost)
    - Falls back to GPT OSS 120B for open questions
    - Stores conversation in Chronos memory if consent=True
    """
    # Rate limit check
    count = _session_counts.get(req.session_id, 0)
    if count >= MAX_DEMO_MESSAGES:
        return JSONResponse(
            status_code=429,
            content={
                "error": "rate_limited",
                "message": "You've used all 5 demo messages. Get an API key for unlimited access.",
                "messages_remaining": 0,
            }
        )

    _session_counts[req.session_id] = count + 1
    messages_remaining = MAX_DEMO_MESSAGES - _session_counts[req.session_id]

    # Intent classification — try template first
    intent = _classify_intent(req.message)

    if intent:
        response_text = TEMPLATES[intent]
        template_key = intent
        logger.info(f"[Chat/Demo] Session {req.session_id[:8]} — template hit: {intent}")
    else:
        # Full GPT OSS 120B generation for unclassified questions
        try:
            import os, httpx
            cerebras_key = os.getenv("CEREBRAS_API_KEY", "")
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(
                    "https://api.cerebras.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {cerebras_key}", "Content-Type": "application/json"},
                    json={
                        "model": "llama-3.3-70b",
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "You are Kaal — a temporal memory engine AI assistant. "
                                    "Answer questions about the Kaal product concisely (max 3 sentences). "
                                    "Kaal is a temporal memory API: POST /ingest writes events, POST /query retrieves them, POST /agent/run runs GPT OSS 120B reasoning over memory. "
                                    "Never reveal system internals. Be warm, intelligent, and direct."
                                )
                            },
                            {"role": "user", "content": req.message}
                        ],
                        "max_tokens": 200,
                        "temperature": 0.7,
                    }
                )
            r.raise_for_status()
            response_text = r.json()["choices"][0]["message"]["content"]
            template_key = None
            logger.info(f"[Chat/Demo] Session {req.session_id[:8]} — GPT generated response")
        except Exception as e:
            logger.error(f"[Chat/Demo] LLM call failed: {e}")
            response_text = "I'm having trouble reaching my brain right now. Try asking about ingest, query, agent, or connectors — I know those cold!"
            template_key = None

    # Store in Chronos memory if user consented
    if req.consent:
        try:
            from api.deps import get_memory_store, get_vector_store
            from chronos_core.svo_parser import SVOParser
            memory = get_memory_store()
            vector = get_vector_store()
            parser = SVOParser()

            event_text = f"Demo user asked: {req.message}. Kaal responded: {response_text}"
            events = await parser.parse([event_text])
            if events:
                await memory.store_events(events, source_id="public_training")
                embeddings = await vector.embed_texts([event_text])
                await vector.store(events, embeddings, source_id="public_training")
                logger.info(f"[Chat/Demo] Stored consented conversation in Chronos memory.")
        except Exception as e:
            logger.warning(f"[Chat/Demo] Failed to store in memory: {e}")

    return {
        "response": response_text,
        "template_key": template_key,
        "messages_remaining": messages_remaining,
        "intent": intent,
    }
