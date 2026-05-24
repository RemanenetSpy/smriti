"""
Chronos OS — Multi-Model Mixture of Agents Router
===================================================
Intelligently routes tasks to different LLMs to aggregate free-tier API limits.
Falls back safely if rate limits (429) or downtimes occur.

Pipelines:
  Fast  → Groq Llama 3.1 8B      (SVO extraction, high volume)
  Heavy → Cerebras Qwen 3 235B   (Agent reasoning, deep logic)
  Fallback → Automated redundancy where applicable
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
    Primary: Cerebras Llama 3.1 8B (Ultra-fast, 1M limits)
    Fallback: Groq Llama 3.1 8B Instant
    """
    has_cerebras = bool(os.getenv("CEREBRAS_API_KEY"))
    has_groq = bool(os.getenv("GROQ_API_KEY"))

    if has_cerebras and has_groq:
        return {
            "model": "cerebras/llama3.1-8b",
            "fallbacks": [{"model": "groq/llama-3.1-8b-instant"}],
            "num_retries": 3,
        }
    elif has_cerebras:
        return {"model": "cerebras/llama3.1-8b", "num_retries": 3}
    else:
        return {"model": "groq/llama-3.1-8b-instant", "num_retries": 3}


# ---------------------------------------------------------------------------
# Heavy Pipeline (Agentic Reasoning — low volume, high complexity)
# ---------------------------------------------------------------------------

# Singleton cache: avoids re-creating LLM objects on every request.
_heavy_pipeline: BaseChatModel | None = None


def get_heavy_pipeline() -> BaseChatModel:
    """
    Return a LangChain ChatModel for the Heavy Pipeline.
    Primary: Cerebras GPT-OSS 20B (Compact, highly efficient logic)
    Fallback: Groq Llama 3.3 70B
    """
    global _heavy_pipeline
    if _heavy_pipeline is not None:
        return _heavy_pipeline

    from langchain_litellm import ChatLiteLLM

    has_cerebras = bool(os.getenv("CEREBRAS_API_KEY"))
    has_groq = bool(os.getenv("GROQ_API_KEY"))

    if has_cerebras:
        primary = ChatLiteLLM(model="cerebras/gpt-oss-20b", temperature=0.4, max_retries=3)
        if has_groq:
            fallback = ChatLiteLLM(model="groq/llama-3.3-70b-versatile", temperature=0.4, max_retries=3)
            _heavy_pipeline = primary.with_fallbacks([fallback])
        else:
            _heavy_pipeline = primary
    else:
        _heavy_pipeline = ChatLiteLLM(model="groq/llama-3.3-70b-versatile", temperature=0.4, max_retries=3)

    logger.info(f"Heavy pipeline initialized: {_heavy_pipeline}")
    return _heavy_pipeline
