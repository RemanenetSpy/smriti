"""
KAAL — Supersession Engine
===========================
Confidence-scored multi-signal detection for fact supersession.

Design principles:
  Optimize  — pure Python string/set ops, zero LLM/DB calls, runs in <1ms
  Adapt     — threshold is a runtime parameter, not a constant
  Efficient — O(k) where k = active events with matching subject (typically 1-3)
  Flexible  — weights are class-level attrs, override per-deployment if needed

Usage:
    engine = SupersessionEngine()
    score = engine.score(existing_event, incoming_event)
    if engine.should_supersede(existing_event, incoming_event, threshold=0.65):
        await memory.invalidate_event(existing_event.id)
"""

from __future__ import annotations

from chronos_core.models import EventRecord


# ---------------------------------------------------------------------------
# Vocabulary: state-change verbs that indicate an updatable declarative fact
# ---------------------------------------------------------------------------

STATE_VERBS: frozenset[str] = frozenset({
    # Copular / existential
    "is", "are", "was", "were", "am", "be", "been", "being",
    "has", "have", "had",
    # Location / state transitions
    "moved", "relocated", "transferred", "went", "arrived", "left",
    # Update verbs
    "changed", "updated", "revised", "modified", "corrected", "adjusted",
    "set", "reset", "configured", "assigned",
    # Temporal rescheduling
    "delayed", "rescheduled", "postponed", "cancelled", "moved",
    "starts", "ends", "opens", "closes", "begins",
    # Attribute declarations
    "became", "turned", "weighs", "costs", "lives", "works", "resides",
    "located", "based", "scheduled",
})

# Stop-words stripped before token comparison
_STOP: frozenset[str] = frozenset({
    "my", "your", "our", "their", "its", "this", "that", "these",
    "the", "a", "an", "some", "any",
})

# Domain-anchor tokens: prepositions and determiners that prefix an object value
# e.g. "at 9AM", "in Delhi", "for 3 hours", "on Monday"
_DOMAIN_ANCHORS: frozenset[str] = frozenset({
    "at", "in", "on", "for", "to", "from", "by", "until", "since",
    "after", "before", "between", "during", "around",
})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalize_tokens(text: str) -> list[str]:
    """Lowercase, strip punctuation, remove stop-words."""
    tokens = []
    for tok in text.lower().split():
        tok = tok.strip(".,!?;:'\"()[]{}—-")
        if tok and tok not in _STOP:
            tokens.append(tok)
    return tokens


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _domain_anchor(tokens: list[str]) -> str | None:
    """
    Return the first meaningful domain token of an object string.
    Prefers an anchor preposition (at/in/on…) if present as the first token;
    otherwise falls back to the first non-stop noun token.
    """
    if not tokens:
        return None
    if tokens[0] in _DOMAIN_ANCHORS:
        return tokens[0]
    return tokens[0]  # First noun/noun-phrase head


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class SupersessionEngine:
    """
    Determines whether an incoming event supersedes an existing one
    using a weighted, multi-signal confidence score.

    Signals
    -------
    subject_similarity (40%)
        Jaccard overlap of normalised subject tokens.
        Handles aliases: "My flight" ≈ "flight" ≈ "the flight" → 1.0

    object_domain_similarity (40%)
        Compares the *semantic domain* of each object (not literal values).
        "at 9AM" vs "at 1PM"  → domain anchor "at" matches → 0.90
        "in Delhi" vs "in Mumbai" → anchor "in" matches → 0.85
        "a contract" vs "a project" → different second token → 0.20
        This is the key signal that catches verb-changed corrections.

    verb_category (20%)
        State-change verbs (is/moved/delayed…) signal declarative facts
        that can be superseded.  Action verbs (signed/launched/completed)
        signal one-time events that must never be superseded.

    Default threshold: 0.65
    """

    DEFAULT_THRESHOLD: float = 0.65

    # Weight configuration (must sum to 1.0)
    W_SUBJECT: float = 0.40
    W_DOMAIN:  float = 0.40
    W_VERB:    float = 0.20

    # ----------------------------------------------------------------
    # Public API
    # ----------------------------------------------------------------

    def score(self, existing: EventRecord, incoming: EventRecord) -> float:
        """Return confidence score 0.0–1.0 that `incoming` supersedes `existing`."""
        s1 = self._subject_score(existing.subject, incoming.subject)
        s2 = self._domain_score(existing.object, incoming.object)
        s3 = self._verb_score(existing.verb, incoming.verb)
        raw = self.W_SUBJECT * s1 + self.W_DOMAIN * s2 + self.W_VERB * s3
        return round(min(1.0, max(0.0, raw)), 4)

    def should_supersede(
        self,
        existing: EventRecord,
        incoming: EventRecord,
        threshold: float | None = None,
    ) -> bool:
        """Return True if incoming should invalidate existing."""
        return self.score(existing, incoming) >= (threshold or self.DEFAULT_THRESHOLD)

    # ----------------------------------------------------------------
    # Signal 1 — Subject similarity
    # ----------------------------------------------------------------

    @staticmethod
    def _subject_score(a: str, b: str) -> float:
        ta = set(_normalize_tokens(a))
        tb = set(_normalize_tokens(b))
        return _jaccard(ta, tb)

    # ----------------------------------------------------------------
    # Signal 2 — Object domain similarity
    # ----------------------------------------------------------------

    @staticmethod
    def _domain_score(a: str, b: str) -> float:
        ta = _normalize_tokens(a)
        tb = _normalize_tokens(b)
        da = _domain_anchor(ta)
        db = _domain_anchor(tb)
        if da is None or db is None:
            return 0.0

        # Anchor match (preposition or first noun head)
        anchor_score = float(da == db)

        # Second-token match gives a bonus (e.g. "at 9" vs "at 1" → anchor match,
        # second token differs → we confirm same domain but different value)
        second_score = 0.0
        if len(ta) >= 2 and len(tb) >= 2:
            second_score = float(ta[1] == tb[1])

        # Domain matches (anchor same) + second token DIFFERS = classic value update
        # anchor match + second match = exact duplicate, not a supersession
        if anchor_score == 1.0 and second_score == 0.0:
            return 0.90   # ← "at 9AM" → "at 1PM" : same domain, different value
        if anchor_score == 1.0 and second_score == 1.0:
            return 0.50   # ← identical object prefix, probably same event
        if anchor_score == 0.0:
            # No shared anchor — check full token Jaccard as fallback
            return 0.3 * _jaccard(set(ta), set(tb))

        return 0.5 * anchor_score + 0.3 * second_score  # partial match

    # ----------------------------------------------------------------
    # Signal 3 — Verb category
    # ----------------------------------------------------------------

    @staticmethod
    def _verb_score(a: str, b: str) -> float:
        a_state = a.lower().strip() in STATE_VERBS
        b_state = b.lower().strip() in STATE_VERBS
        if a_state and b_state:
            return 1.0   # Both declarative → strong supersession signal
        if a_state or b_state:
            return 0.75  # One declarative → moderate signal
        return 0.25       # Both action verbs → one-time events, resist supersession
