"""
Smriti — Multi-Model Mixture of Agents Router
===================================================
Intelligently routes tasks to different LLMs to aggregate free-tier API limits.
Falls back safely if rate limits (429) or downtimes occur.

Pipelines:
  Fast  → Cerebras Llama 3.1 8B  (SVO extraction, high volume)
  Fallback → Groq Llama 3.1 8B Instant
  Heavy → Cerebras GPT-OSS 120B  (Agent reasoning, deep logic)
  Fallback → Groq Llama 3.3 70B
"""

import os
import re
import logging
from functools import lru_cache
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel

logger = logging.getLogger("smriti.llm_router")


def _sanitize_key(env_var: str) -> str:
    """
    Read an API key from the environment and strip any control characters
    (newlines, carriage returns, tabs, etc.) that would corrupt HTTP headers.
    This guards against keys pasted with trailing newlines in the HF Spaces
    secrets UI, which causes a 'Forbidden control character' aiohttp crash.
    """
    raw = os.getenv(env_var, "")
    # Remove all ASCII control characters (0x00-0x1F) and DEL (0x7F)
    sanitized = re.sub(r"[\x00-\x1f\x7f]", "", raw)
    if sanitized != raw:
        logger.warning(
            f"Environment variable '{env_var}' contained control characters "
            f"(e.g. newlines) — they have been stripped. "
            f"Please fix the secret value in your HF Space / .env file."
        )
    return sanitized


# ---------------------------------------------------------------------------
# Fast Pipeline (SVO Extraction — high volume, low complexity)
# ---------------------------------------------------------------------------

def get_fast_pipeline_kwargs() -> dict[str, Any]:
    """
    Return litellm.acompletion kwargs for the Fast Pipeline.
    Primary: Cerebras Llama 3.1 8B (Ultra-fast, free tier)
    Fallback: Groq Llama 3.1 8B Instant

    NOTE: Cerebras model slugs use hyphens — "llama-3.1-8b" not "llama3.1-8b".
    Keys are sanitized to strip control chars that can cause header injection errors.
    """
    cerebras_key = _sanitize_key("CEREBRAS_API_KEY")
    groq_key = _sanitize_key("GROQ_API_KEY")

    has_cerebras = bool(cerebras_key)
    has_groq = bool(groq_key)

    if has_cerebras and has_groq:
        return {
            "model": "cerebras/llama-3.1-8b",
            "api_key": cerebras_key,
            "fallbacks": [{"model": "groq/llama-3.1-8b-instant", "api_key": groq_key}],
            "num_retries": 3,
        }
    elif has_cerebras:
        return {"model": "cerebras/llama-3.1-8b", "api_key": cerebras_key, "num_retries": 3}
    else:
        return {"model": "groq/llama-3.1-8b-instant", "api_key": groq_key, "num_retries": 3}


# ---------------------------------------------------------------------------
# Heavy Pipeline (Agentic Reasoning — low volume, high complexity)
# ---------------------------------------------------------------------------

# Singleton cache: avoids re-creating LLM objects on every request.
_heavy_pipeline: BaseChatModel | None = None


def get_heavy_pipeline() -> BaseChatModel:
    """
    Return a LangChain ChatModel for the Heavy Pipeline.
    Primary: Cerebras ZAI GLM 4.7 (Long-horizon tasks)
    Fallback: Groq Llama 3.3 70B
    """
    global _heavy_pipeline
    if _heavy_pipeline is not None:
        return _heavy_pipeline

    from langchain_litellm import ChatLiteLLM

    has_cerebras = bool(os.getenv("CEREBRAS_API_KEY"))
    has_groq = bool(os.getenv("GROQ_API_KEY"))

    if has_cerebras:
        primary = ChatLiteLLM(model="cerebras/gpt-oss-120b", temperature=0.4, max_retries=0)
        if has_groq:
            fallback = ChatLiteLLM(model="groq/llama-3.3-70b-versatile", temperature=0.4, max_retries=0)
            _heavy_pipeline = primary.with_fallbacks([fallback])
        else:
            _heavy_pipeline = primary
    else:
        _heavy_pipeline = ChatLiteLLM(model="groq/llama-3.3-70b-versatile", temperature=0.4, max_retries=0)

    logger.info(f"Heavy pipeline initialized: {_heavy_pipeline}")
    return _heavy_pipeline
