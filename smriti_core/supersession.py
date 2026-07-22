"""
Smriti — Supersession Engine
===========================
Confidence-scored multi-signal detection for fact supersession.

All numeric parameters are read from smriti_core.config, which in turn
reads from environment variables.  Nothing is hardcoded in this file.

Algorithm overview:
    combined_score = W_SUBJECT * subject_jaccard
                   + W_DOMAIN  * object_domain_score
                   + W_VERB    * verb_category_score

If combined_score >= SUPERSESSION_THRESHOLD → invalidate the older event.

Design properties:
  • Zero LLM / DB calls — pure in-process string/set operations
  • O(k) where k = active events with matching subject (typically 1–3)
  • All coefficients, thresholds, and vocabularies are env-var configurable
  • Stateless — safe to reuse as a module-level singleton
"""

from __future__ import annotations

from smriti_core import config
from smriti_core.models import EventRecord


# ---------------------------------------------------------------------------
# Token normalisation helpers (use config vocabularies)
# ---------------------------------------------------------------------------

def _normalize_tokens(text: str) -> list[str]:
    """Lowercase, strip punctuation, remove config stop-words."""
    tokens = []
    for tok in text.lower().split():
        tok = tok.strip(".,!?;:'\"()[]{}—-")
        if tok and tok not in config.STOP_WORDS:
            tokens.append(tok)
    return tokens


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _domain_anchor(tokens: list[str]) -> str | None:
    """
    Return the first meaningful domain token.
    Prefers a preposition/anchor if the first token is in config.DOMAIN_ANCHORS;
    otherwise returns the first noun token.
    """
    if not tokens:
        return None
    return tokens[0]  # first non-stop token is always the domain head


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class SupersessionEngine:
    """
    Determines whether an incoming event supersedes an existing one.

    All parameters are sourced from smriti_core.config (env-var driven).
    Instance-level overrides can be passed to __init__ for testing.
    """

    def __init__(
        self,
        threshold:  float | None = None,
        w_subject:  float | None = None,
        w_domain:   float | None = None,
        w_verb:     float | None = None,
    ):
        # Instance overrides for testing; fall back to global config
        self.threshold = threshold if threshold is not None else config.SUPERSESSION_THRESHOLD
        self.w_subject = w_subject if w_subject is not None else config.SUPERSESSION_W_SUBJECT
        self.w_domain  = w_domain  if w_domain  is not None else config.SUPERSESSION_W_DOMAIN
        self.w_verb    = w_verb    if w_verb    is not None else config.SUPERSESSION_W_VERB

    # ----------------------------------------------------------------
    # Public API
    # ----------------------------------------------------------------

    def score(self, existing: EventRecord, incoming: EventRecord) -> float:
        """Return confidence score 0.0–1.0 that `incoming` supersedes `existing`."""
        s1 = self._subject_score(existing.subject, incoming.subject)
        s2 = self._domain_score(existing.object, incoming.object)
        s3 = self._verb_score(existing.verb, incoming.verb)

        # Normalise weights so the score is robust even if weights don't sum to 1.0
        total_w = self.w_subject + self.w_domain + self.w_verb
        if total_w == 0:
            return 0.0
        raw = (self.w_subject * s1 + self.w_domain * s2 + self.w_verb * s3) / total_w
        return round(min(1.0, max(0.0, raw)), 4)

    def should_supersede(
        self,
        existing: EventRecord,
        incoming: EventRecord,
        threshold: float | None = None,
    ) -> bool:
        """Return True if incoming should invalidate existing."""
        t = threshold if threshold is not None else self.threshold
        return self.score(existing, incoming) >= t

    # ----------------------------------------------------------------
    # Signal 1 — Subject similarity (Jaccard token overlap)
    # ----------------------------------------------------------------

    @staticmethod
    def _subject_score(a: str, b: str) -> float:
        ta = set(_normalize_tokens(a))
        tb = set(_normalize_tokens(b))
        return _jaccard(ta, tb)

    # ----------------------------------------------------------------
    # Signal 2 — Object domain similarity
    #
    # Compares the *semantic domain* of objects, not literal values.
    # "at 9AM" vs "at 1PM"  → same anchor "at" → value-update pattern
    # "in Delhi" vs "in Paris" → same anchor "in" → location update
    # "a contract" vs "a merger" → anchor "a" is non-informative, second
    #   token differs → low score (different things)
    # ----------------------------------------------------------------

    @staticmethod
    def _domain_score(a: str, b: str) -> float:
        ta = _normalize_tokens(a)
        tb = _normalize_tokens(b)
        da = _domain_anchor(ta)
        db = _domain_anchor(tb)
        if da is None or db is None:
            return 0.0

        anchor_match = da == db

        # Second token comparison: confirms whether values differ or are identical
        second_match = (
            len(ta) >= 2 and len(tb) >= 2 and ta[1] == tb[1]
        )

        if anchor_match and not second_match:
            # Classic value-update: same domain, different value
            # e.g. "at 9AM" → "at 1PM"
            return config.DOMAIN_SCORE_UPDATE

        if anchor_match and second_match:
            # Possible duplicate or very similar — moderate signal
            return config.DOMAIN_SCORE_DUPLICATE

        # No anchor match — use full Jaccard as a weak fallback
        return config.DOMAIN_SCORE_FALLBACK_SCALE * _jaccard(set(ta), set(tb))

    # ----------------------------------------------------------------
    # Signal 3 — Verb category (state vs action)
    # ----------------------------------------------------------------

    @staticmethod
    def _verb_score(a: str, b: str) -> float:
        a_state = a.lower().strip() in config.STATE_VERBS
        b_state = b.lower().strip() in config.STATE_VERBS
        if a_state and b_state:
            return config.VERB_SCORE_BOTH_STATE
        if a_state or b_state:
            return config.VERB_SCORE_ONE_STATE
        return config.VERB_SCORE_NO_STATE
