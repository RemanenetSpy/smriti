"""
Chronos OS — SVO Parser
========================
Extracts Subject-Verb-Object event tuples from raw text using
the Mixture of Agents LiteLLM Router (Cerebras + Groq fallback).
Falls back to regex extraction when all LLM quotas are exhausted.
"""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime
from typing import Optional

from .models import SVOTuple

logger = logging.getLogger("chronos.svo_parser")

# ---------------------------------------------------------------------------
# SVO extraction prompt
# ---------------------------------------------------------------------------

SVO_EXTRACTION_PROMPT = """You are a structured event extractor for the Chronos temporal memory system.

Given the following text, extract ALL Subject-Verb-Object (SVO) events with timestamps.

Rules:
1. Each event must have: subject (who/what), verb (action), object (target/recipient).
2. If a timestamp is mentioned or implied, include it. Otherwise use "now".
3. If an event spans a time range, include datetime_start and datetime_end.
4. Include entity aliases when the same entity is referred to differently.
5. Rate your confidence in each extraction from 0.0 to 1.0.
6. Return ONLY a valid JSON array — no markdown, no explanation.

Output format (JSON array):
[
  {
    "subject": "string",
    "verb": "string",
    "object": "string",
    "timestamp": "ISO 8601 datetime string",
    "datetime_start": "ISO 8601 or null",
    "datetime_end": "ISO 8601 or null",
    "entity_aliases": ["alias1", "alias2"],
    "confidence": 0.95
  }
]

Text to analyze:
---
{text}
---

Current datetime for reference: {current_time}

Extract all SVO events as JSON:"""


# ---------------------------------------------------------------------------
# Regex fallback patterns
# ---------------------------------------------------------------------------

# Simple patterns: "X did Y", "X verb-ed Y", etc.
_SVO_PATTERNS = [
    # "Subject verbed Object" (past tense -ed)
    re.compile(
        r"(?P<subject>[A-Z][a-zA-Z\s]+?)\s+"
        r"(?P<verb>[a-z]+ed)\s+"
        r"(?P<object>.+?)(?:\.|,|;|$)",
        re.MULTILINE
    ),
    # "Subject verbs Object" (present tense -s)
    re.compile(
        r"(?P<subject>[A-Z][a-zA-Z\s]+?)\s+"
        r"(?P<verb>[a-z]+s)\s+"
        r"(?P<object>.+?)(?:\.|,|;|$)",
        re.MULTILINE
    ),
    # "Subject will verb Object" (future)
    re.compile(
        r"(?P<subject>[A-Z][a-zA-Z\s]+?)\s+will\s+"
        r"(?P<verb>[a-z]+)\s+"
        r"(?P<object>.+?)(?:\.|,|;|$)",
        re.MULTILINE
    ),
]


def _regex_fallback(text: str, timestamp: Optional[datetime] = None) -> list[SVOTuple]:
    """
    Extract SVO tuples using regex when LLM is unavailable.
    Lower confidence (0.4) since regex is imprecise.
    """
    ts = timestamp or datetime.utcnow()
    results: list[SVOTuple] = []
    seen = set()

    for pattern in _SVO_PATTERNS:
        for match in pattern.finditer(text):
            subject = match.group("subject").strip()
            verb = match.group("verb").strip()
            obj = match.group("object").strip()[:200]  # Cap length

            key = (subject.lower(), verb.lower(), obj.lower())
            if key in seen:
                continue
            seen.add(key)

            results.append(SVOTuple(
                subject=subject,
                verb=verb,
                object=obj,
                timestamp=ts,
                confidence=0.4,
            ))

    return results


# ---------------------------------------------------------------------------
# Main Parser Class
# ---------------------------------------------------------------------------

class SVOParser:
    """
    Extracts Subject-Verb-Object tuples from raw text.
    
    Primary: High Speed Model via LiteLLM Router.
    Fallback: Regex patterns (when LLM fails or limits exhausted)
    """

    def __init__(self):
        from .llm_router import get_fast_pipeline_kwargs
        self._llm_kwargs = get_fast_pipeline_kwargs()
        logger.info(f"SVO parser initialized with fast pipeline: {self._llm_kwargs.get('model')}")

    async def parse(
        self,
        text: str,
        timestamp: Optional[datetime] = None,
    ) -> list[SVOTuple]:
        """
        Extract SVO tuples from text.
        Tries Litellm Fast Pipeline first, falls back to regex.
        """
        if not text or not text.strip():
            return []

        ts = timestamp or datetime.utcnow()

        # Try LLM extraction via LiteLLM
        try:
            return await self._parse_with_litellm(text, ts)
        except Exception as e:
            logger.warning(f"Fast Pipeline SVO extraction failed: {e}. Falling back to regex.")

        # Regex fallback
        return _regex_fallback(text, ts)

    async def _parse_with_litellm(
        self,
        text: str,
        timestamp: datetime,
    ) -> list[SVOTuple]:
        """Call LiteLLM unified completion to extract SVO tuples."""
        import litellm
        from .llm_router import get_fast_pipeline_kwargs

        prompt = SVO_EXTRACTION_PROMPT.format(
            text=text,
            current_time=timestamp.isoformat(),
        )

        kwargs = get_fast_pipeline_kwargs()
        kwargs["messages"] = [
            {
                "role": "system",
                "content": "You are a precise JSON event extractor. Output ONLY valid JSON arrays.",
            },
            {"role": "user", "content": prompt},
        ]
        kwargs["temperature"] = 0.1
        kwargs["max_tokens"] = 2000
        # Not all fallback models gracefully support strict json format enforcement in litellm uniformly if the provider doesn't support it.
        # But we will use it for safety.
        kwargs["response_format"] = {"type": "json_object"}

        # LiteLLM acompletion directly leverages the fallback arrays natively!
        response = await litellm.acompletion(**kwargs)

        raw = response.choices[0].message.content.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)

        parsed = json.loads(raw)

        # Handle both array and {"events": [...]} formats
        if isinstance(parsed, dict):
            parsed = parsed.get("events", parsed.get("svo_events", [parsed]))
        if not isinstance(parsed, list):
            parsed = [parsed]

        tuples: list[SVOTuple] = []
        for item in parsed:
            try:
                # Parse timestamps
                ts = item.get("timestamp")
                if ts and ts != "now":
                    try:
                        item["timestamp"] = datetime.fromisoformat(
                            ts.replace("Z", "+00:00")
                        )
                    except (ValueError, TypeError):
                        item["timestamp"] = timestamp
                else:
                    item["timestamp"] = timestamp

                for field in ("datetime_start", "datetime_end"):
                    val = item.get(field)
                    if val and val != "null" and val is not None:
                        try:
                            item[field] = datetime.fromisoformat(
                                val.replace("Z", "+00:00")
                            )
                        except (ValueError, TypeError):
                            item[field] = None
                    else:
                        item[field] = None

                tuples.append(SVOTuple(**item))
            except Exception as e:
                logger.warning(f"Failed to parse SVO tuple: {item} — {e}")
                continue

        model_name = self._llm_kwargs.get('model', 'unknown')
        logger.info(
            f"Fast Pipeline ({model_name}) extracted {len(tuples)} SVO tuples "
            f"from text ({len(text)} chars)"
        )
        return tuples

    async def parse_batch(
        self,
        texts: list[str],
        timestamps: Optional[list[datetime]] = None,
    ) -> list[list[SVOTuple]]:
        """Parse multiple texts, returning SVO tuples per text."""
        import asyncio

        ts_list = timestamps or [datetime.utcnow()] * len(texts)
        tasks = [self.parse(text, ts) for text, ts in zip(texts, ts_list)]
        return await asyncio.gather(*tasks)
