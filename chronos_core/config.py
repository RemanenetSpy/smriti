"""
KAAL — Central Runtime Configuration
======================================
Single source of truth for all tunable parameters.
Every value can be overridden by an environment variable — nothing is hardcoded.

Environment variables reference:
  SMRITI_SUPERSESSION_THRESHOLD     float  [0.0-1.0]  default 0.65
  SMRITI_SUPERSESSION_W_SUBJECT      float  [0.0-1.0]  default 0.40
  SMRITI_SUPERSESSION_W_DOMAIN       float  [0.0-1.0]  default 0.40
  SMRITI_SUPERSESSION_W_VERB         float  [0.0-1.0]  default 0.20
  SMRITI_DOMAIN_SCORE_UPDATE         float  [0.0-1.0]  default 0.90  (anchor match, value changed)
  SMRITI_DOMAIN_SCORE_DUPLICATE      float  [0.0-1.0]  default 0.50  (anchor + second token same)
  SMRITI_DOMAIN_SCORE_FALLBACK_SCALE float  [0.0-1.0]  default 0.30  (no anchor, Jaccard fallback)
  SMRITI_VERB_SCORE_BOTH_STATE       float  [0.0-1.0]  default 1.00  (both state verbs)
  SMRITI_VERB_SCORE_ONE_STATE        float  [0.0-1.0]  default 0.75  (one state verb)
  SMRITI_VERB_SCORE_NO_STATE         float  [0.0-1.0]  default 0.25  (both action verbs)
  SMRITI_SIMILARITY_THRESHOLD        float  [0.0-1.0]  default 0.15  (cosine distance cutoff)
  SMRITI_STATE_VERBS_EXTRA           str    comma-separated verbs to add to the default set
  SMRITI_STATE_VERBS_REMOVE          str    comma-separated verbs to remove from the default set
  SMRITI_STOP_WORDS_EXTRA            str    comma-separated stop words to add
  SMRITI_DOMAIN_ANCHORS_EXTRA        str    comma-separated anchor tokens to add
"""

from __future__ import annotations

import os


def _float(key: str, default: float) -> float:
    raw = os.getenv(key, "").strip()
    return float(raw) if raw else default


def _str_set(key: str, base: frozenset[str]) -> frozenset[str]:
    """Apply EXTRA and REMOVE env vars to a base frozenset."""
    result = set(base)
    extra = os.getenv(f"{key}_EXTRA", "")
    remove = os.getenv(f"{key}_REMOVE", "")
    if extra:
        result.update(t.strip().lower() for t in extra.split(",") if t.strip())
    if remove:
        result.difference_update(t.strip().lower() for t in remove.split(",") if t.strip())
    return frozenset(result)


# ---------------------------------------------------------------------------
# Supersession engine parameters
# ---------------------------------------------------------------------------

SUPERSESSION_THRESHOLD: float = _float("SMRITI_SUPERSESSION_THRESHOLD", 0.65)

# Signal weights (should sum to ~1.0; engine normalises anyway)
SUPERSESSION_W_SUBJECT: float = _float("SMRITI_SUPERSESSION_W_SUBJECT", 0.40)
SUPERSESSION_W_DOMAIN:  float = _float("SMRITI_SUPERSESSION_W_DOMAIN",  0.40)
SUPERSESSION_W_VERB:    float = _float("SMRITI_SUPERSESSION_W_VERB",     0.20)

# Domain-score branch values (configurable without redeploying)
DOMAIN_SCORE_UPDATE:         float = _float("SMRITI_DOMAIN_SCORE_UPDATE",         0.90)
DOMAIN_SCORE_DUPLICATE:      float = _float("SMRITI_DOMAIN_SCORE_DUPLICATE",      0.50)
DOMAIN_SCORE_FALLBACK_SCALE: float = _float("SMRITI_DOMAIN_SCORE_FALLBACK_SCALE", 0.30)

# Verb-score branch values
VERB_SCORE_BOTH_STATE: float = _float("SMRITI_VERB_SCORE_BOTH_STATE", 1.00)
VERB_SCORE_ONE_STATE:  float = _float("SMRITI_VERB_SCORE_ONE_STATE",  0.75)
VERB_SCORE_NO_STATE:   float = _float("SMRITI_VERB_SCORE_NO_STATE",   0.25)

# ---------------------------------------------------------------------------
# Vector similarity threshold
# ---------------------------------------------------------------------------

# Cosine distance (not similarity). Lower = stricter.
# 0.15 ≈ ≥85% cosine similarity.  0.30 ≈ ≥70%.
SIMILARITY_THRESHOLD: float = _float("SMRITI_SIMILARITY_THRESHOLD", 0.15)

# ---------------------------------------------------------------------------
# Vocabulary sets (all extensible via env vars)
# ---------------------------------------------------------------------------

_BASE_STATE_VERBS: frozenset[str] = frozenset({
    # Copular / existential
    "is", "are", "was", "were", "am", "be", "been", "being",
    "has", "have", "had",
    # Location / state transitions
    "moved", "relocated", "transferred", "went", "arrived", "left",
    # Update verbs
    "changed", "updated", "revised", "modified", "corrected", "adjusted",
    "set", "reset", "configured", "assigned",
    # Temporal rescheduling
    "delayed", "rescheduled", "postponed", "cancelled",
    "starts", "ends", "opens", "closes", "begins",
    # Attribute declarations
    "became", "turned", "weighs", "costs", "lives", "works", "resides",
    "located", "based", "scheduled",
})

_BASE_STOP_WORDS: frozenset[str] = frozenset({
    "my", "your", "our", "their", "its", "this", "that", "these",
    "the", "a", "an", "some", "any",
})

_BASE_DOMAIN_ANCHORS: frozenset[str] = frozenset({
    "at", "in", "on", "for", "to", "from", "by", "until", "since",
    "after", "before", "between", "during", "around",
})

# Apply env-var extensions/removals at import time
STATE_VERBS:    frozenset[str] = _str_set("SMRITI_STATE_VERBS",    _BASE_STATE_VERBS)
STOP_WORDS:     frozenset[str] = _str_set("SMRITI_STOP_WORDS",     _BASE_STOP_WORDS)
DOMAIN_ANCHORS: frozenset[str] = _str_set("SMRITI_DOMAIN_ANCHORS", _BASE_DOMAIN_ANCHORS)
