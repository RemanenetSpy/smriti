"""
Chronos OS — Multi-Model Mixture of Agents Router
===================================================
Intelligently routes tasks to different LLMs to aggregate free-tier API limits.
Falls back safely if rate limits (429) or downtimes occur.

Pipelines:
  Fast  → Cerebras Llama 3.1 8B  (SVO extraction, high volume)
  Heavy → Cerebras Qwen 3 235B   (Agent reasoning, deep logic)
  Fallback → Groq equivalents    (automatic on failure)
"""

import os
import logging
from functools import lru_cache
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel

logger = logging.getLogger("chronos.llm_router")


# ---------------------------------------------------------------------------
# Fast Pipeline (SVO Extraction — high volume, low complexity)
# ---------------------------------------------------------------------------

def get_fast_pipeline_kwargs() -> dict[str, Any]:
    """
    Return litellm.acompletion kwargs for the Fast Pipeline.
    Primary: Cerebras Llama 3.1 8B  (1M tokens/day, extreme speed)
    Fallback: Groq Llama 3.1 8B Instant (14,400 req/day)
    """
    has_cerebras = bool(os.getenv("CEREBRAS_API_KEY"))
    has_groq = bool(os.getenv("GROQ_API_KEY"))

    if has_cerebras and has_groq:
        return {
            "model": "cerebras/llama3.1-8b",
            "fallbacks": [{"model": "groq/llama-3.1-8b-instant"}],
        }
    elif has_cerebras:
        return {"model": "cerebras/llama3.1-8b"}
    else:
        return {"model": "groq/llama-3.1-8b-instant"}


# ---------------------------------------------------------------------------
# Heavy Pipeline (Agentic Reasoning — low volume, high complexity)
# ---------------------------------------------------------------------------

# Singleton cache: avoids re-creating LLM objects on every request.
_heavy_pipeline: BaseChatModel | None = None


def get_heavy_pipeline() -> BaseChatModel:
    """
    Return a LangChain ChatModel for the Heavy Pipeline.
    Primary: Cerebras Qwen 3 235B  (rivals Claude 4 logic)
    Fallback: Groq Llama 3.3 70B   (strong general reasoning)

    Cached as a module-level singleton so connections are reused.
    """
    global _heavy_pipeline
    if _heavy_pipeline is not None:
        return _heavy_pipeline

    from langchain_litellm import ChatLiteLLM

    has_cerebras = bool(os.getenv("CEREBRAS_API_KEY"))
    has_groq = bool(os.getenv("GROQ_API_KEY"))

    # For Heavy Reasoning, prioritize Groq because it has better RPM (Requests Per Minute)
    # limits than Cerebras free tier, preventing "RateLimit" hangs during chat.
    if has_groq:
        primary = ChatLiteLLM(model="groq/llama-3.3-70b-versatile", temperature=0.4)
        if has_cerebras:
            fallback = ChatLiteLLM(model="cerebras/qwen-3-235b-a22b-instruct-2507", temperature=0.4)
            _heavy_pipeline = primary.with_fallbacks([fallback])
        else:
            _heavy_pipeline = primary
    elif has_cerebras:
        _heavy_pipeline = ChatLiteLLM(model="cerebras/qwen-3-235b-a22b-instruct-2507", temperature=0.4)
    else:
        raise ValueError("Neither GROQ_API_KEY nor CEREBRAS_API_KEY is set.")

    logger.info(f"Heavy pipeline initialized: {_heavy_pipeline}")
    return _heavy_pipeline
