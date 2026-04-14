"""
Chronos OS — Multi-Model Mixture of Agents Router
===================================================
Intelligently routes tasks to different LLMs to aggregate free-tier API limits.
Falls back safely if rate limits (429) or downtimes occur.
"""

import os
import logging
from typing import Any

from langchain_community.chat_models import ChatLiteLLM
from langchain_core.language_models.chat_models import BaseChatModel

logger = logging.getLogger("chronos.llm_router")

def get_fast_pipeline_kwargs() -> dict[str, Any]:
    """
    Routing configuration for the Fast Pipeline (Memory Extraction).
    Primary: Cerebras Llama 3.1 8B (Massive limit, extreme speed)
    Fallback: Groq Llama 3.1 8B Instant
    """
    has_cerebras = bool(os.getenv("CEREBRAS_API_KEY"))
    has_groq = bool(os.getenv("GROQ_API_KEY"))
    
    if has_cerebras and has_groq:
        return {
            "model": "cerebras/llama3.1-8b",
            "fallbacks": [{"model": "groq/llama-3.1-8b-instant"}]
        }
    elif has_cerebras:
        return {"model": "cerebras/llama3.1-8b"}
    else:
        # Default to Groq if no Cerebras key is found
        return {"model": "groq/llama-3.1-8b-instant"}


def get_heavy_pipeline() -> BaseChatModel:
    """
    Routing configuration for the Heavy Pipeline (Agentic Reasoning).
    Primary: Cerebras Qwen 3 235B (Elite logic and deep reasoning)
    Fallback: Groq Llama 3.3 70B
    """
    has_cerebras = bool(os.getenv("CEREBRAS_API_KEY"))
    has_groq = bool(os.getenv("GROQ_API_KEY"))
    
    # Initialize the robust Groq fallback (always available if .env set)
    # Using litellm via langchain
    groq_llm = ChatLiteLLM(
        model="groq/llama-3.3-70b-versatile",
        temperature=0.4
    )
    
    if has_cerebras:
        cerebras_llm = ChatLiteLLM(
            model="cerebras/qwen3-235b",
            temperature=0.4
        )
        if has_groq:
            # Langchain native fallback mechanism
            return cerebras_llm.with_fallbacks([groq_llm])
        return cerebras_llm
        
    return groq_llm
