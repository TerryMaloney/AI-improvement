"""Claim-type classification — the cheap triage step.

Routes a question into one of five claim types *before* anything expensive
happens, because the right verification move is different for each:

    EMPIRICAL      a fact about the world       -> may need external evidence
    NORMATIVE      a should/ought judgement     -> never "verified"; audit the
                                                   assumptions and state the
                                                   weighting being applied
    PREDICTIVE     a claim about the future     -> calibrated forecast, not a
                                                   verdict
    DEFINITIONAL   which sense of a word is in  -> surface the definition in
                   use                            use; don't argue past it
    DETERMINISTIC  computable from the question -> compute it, don't search

No model call happens here. This is rules only, by design: the handoff packet
records that roughly a third of controller model calls in early rounds added
zero value, so the controller must not cost more than the investigation it is
supposed to be economising.

------------------------------------------------------------------------------
BUG HISTORY — deliberately preserved (handoff packet §1 says: leave this in).
------------------------------------------------------------------------------
Two bugs in the first version of this classifier both had the same shape: an
over-eager arithmetic detector claiming a question was DETERMINISTIC, which
made the pipeline compute an answer instead of verifying it. That is the
dangerous direction of error — it silently bypasses verification.

  Bug 1: the arithmetic detector matched a bare "-" character anywhere in the
         question. That fires on any hyphenated word: "US-Japan",
         "entity-hazard", "evidence-lineage". False-premise trap questions
         containing a hyphenated proper noun were therefore routed to
         "compute, don't search" and skipped verification entirely.

  Bug 2: a bare "how many" was treated as an arithmetic signal, so "how many
         people died in 1918" was read as arithmetic because "1918" looked
         like a digit operand.

Both are fixed the same way, and the fix is the load-bearing idea in this
module:

  1. An arithmetic signal requires a real operator sitting *between two
     numeric operands* — never a lone symbol, never a lone interrogative.
  2. When the classifier is unsure, it defaults to EMPIRICAL, never
     DETERMINISTIC. EMPIRICAL costs an extra search when it is wrong.
     DETERMINISTIC skips verification when it is wrong. Those errors are not
     symmetric, so the tie never goes to the cheap one.
  3. A question carrying real-world-entity signals (a proper noun, a
     who/when/where interrogative, a "current"/"as of now" framing) is demoted
     out of DETERMINISTIC even if an arithmetic pattern did match.

This bug and its fix are the best evidence in the whole project for "ship it,
then test it against real cases" over "reason about it until it seems right":
the detector looked obviously correct when read, and was wrong on the first
trap question it met.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class ClaimType(str, Enum):
    EMPIRICAL = "EMPIRICAL"
    NORMATIVE = "NORMATIVE"
    PREDICTIVE = "PREDICTIVE"
    DEFINITIONAL = "DEFINITIONAL"
    DETERMINISTIC = "DETERMINISTIC"


# Tie-break order when a question carries signals for more than one type.
# NORMATIVE outranks the rest because "should"/"ought" is the single most
# reliable marker in the set, and mislabelling a value judgement as a fact is
# the "false objectivity" failure from the packet's failure matrix.
# DETERMINISTIC sits second-to-last and EMPIRICAL last-as-default on purpose.
_PRIORITY: tuple[ClaimType, ...] = (
    ClaimType.NORMATIVE,
    ClaimType.DEFINITIONAL,
    ClaimType.PREDICTIVE,
    ClaimType.DETERMINISTIC,
    ClaimType.EMPIRICAL,
)


# --------------------------------------------------------------------------
# Arithmetic detection (the part that caused both historical bugs)
# --------------------------------------------------------------------------

# A numeric operand: 42, 3.5, 1,200. Deliberately does NOT match a bare year
# on its own — a year only matters here if a real operator sits next to it.
_NUM = r"\d+(?:[.,]\d+)*"

_ARITH_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(rf"{_NUM}\s*\+\s*{_NUM}"), "addition symbol between two numbers"),
    # NOTE (bug 1): "-" requires whitespace on BOTH sides. "12 - 5" is
    # subtraction; "1918-1920" is a date range and "US-Japan" is a name.
    # Requiring the spaces means we miss a genuine "12-5", which costs one
    # search. Not requiring them missed a trap question, which cost a wrong
    # answer. We take the search.
    (re.compile(rf"{_NUM}\s+-\s+{_NUM}"), "subtraction symbol between two numbers"),
    (re.compile(rf"{_NUM}\s*[×÷*/]\s*{_NUM}"), "multiplication/division symbol between two numbers"),
    (re.compile(rf"{_NUM}\s*\^\s*{_NUM}"), "exponent between two numbers"),
    (re.compile(rf"{_NUM}\s*%\s+of\s+{_NUM}"), "percent-of between two numbers"),
    (
        re.compile(rf"{_NUM}\s+(?:plus|minus|times|multiplied\s+by|divided\s+by)\s+{_NUM}"),
        "arithmetic word operator between two numbers",
    ),
)

# Compute verbs only count when at least two operands are actually present.
# "difference between" is NOT here: "the difference between the 2019 and 2021
# trade deficits" is a comparison question about the world, not a subtraction.
_COMPUTE_VERB = re.compile(
    r"\b(?:calculate|compute|what\s+is\s+the\s+(?:sum|product|quotient|average|mean)\s+of)\b",
    re.IGNORECASE,
)

_ANY_NUM = re.compile(_NUM)


# --------------------------------------------------------------------------
# Real-world-entity signals — these veto DETERMINISTIC
# --------------------------------------------------------------------------

_ENTITY_INTERROGATIVE = re.compile(r"\b(?:who|whom|whose|when|where|which)\b", re.IGNORECASE)
_CURRENCY_OF_STATE = re.compile(
    r"\b(?:current|currently|as\s+of\s+(?:now|today|\w+\s+\d{4})|right\s+now|today|latest|so\s+far|to\s+date)\b",
    re.IGNORECASE,
)
# A capitalized word that is not the first word of the question and is not a
# lone "I" — a rough proper-noun detector. Rough is fine: it only ever *adds*
# verification, never removes it.
_INTERIOR_PROPER_NOUN = re.compile(r"(?<!^)(?<![.!?]\s)\b[A-Z][a-z]{2,}")


# --------------------------------------------------------------------------
# Type signals
# --------------------------------------------------------------------------

_NORMATIVE_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\b(?:should|ought\s+to|must\s+we|do\s+we\s+need\s+to)\b", re.I), "deontic verb"),
    (re.compile(r"\b(?:is\s+it\s+worth|worth\s+it|worth\s+doing)\b", re.I), "worth-it framing"),
    (re.compile(r"\b(?:better|best|preferable|prioriti[sz]e|right\s+(?:approach|thing|call))\b", re.I), "evaluative comparative"),
    (re.compile(r"\b(?:vs\.?|versus)\b.*\b(?:which|now|first|better)\b", re.I), "choice framing"),
    (re.compile(r"\bwhich\b.*\b(?:first|now|instead)\b", re.I), "choice framing"),
)

_PREDICTIVE_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bwill\b(?!\s+(?:power|of\s+the\s+people))", re.I), "future-tense 'will'"),
    (re.compile(r"\b(?:going\s+to\s+\w+|likely\s+to|expected\s+to|forecast|predict(?:ion|ed)?)\b", re.I), "forecast verb"),
    (re.compile(r"\bby\s+(?:20[2-9]\d|next\s+(?:year|month|quarter|decade))\b", re.I), "future horizon"),
    (re.compile(r"\b(?:hold\s+(?:up\s+)?on|generali[sz]e\s+to)\b.*\b(?:more|other|untested|future)\b", re.I), "generalisation-to-unseen framing"),
)

_DEFINITIONAL_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bwhat\s+(?:counts\s+as|do(?:es)?\s+\w+\s+mean|is\s+meant\s+by)\b", re.I), "meaning question"),
    (re.compile(r"\b(?:the\s+same\s+(?:as|thing\s+as)|equivalent\s+to|synonymous\s+with)\b", re.I), "identity-of-terms question"),
    (re.compile(r"\b(?:define|definition\s+of|by\s+definition)\b", re.I), "explicit definition request"),
)

# "difference between X and Y" is definitional when X and Y are *terms*, and
# empirical when they are dated things in the world. "the difference between
# HTTP and HTTPS" is a definition question; "the difference between the 2019
# and 2021 trade deficits" is a lookup-and-subtract question about the world,
# and treating it as definitional would skip the premise check that a
# false-premise trap needs. Digits are the cheap discriminator.
_DIFFERENCE_BETWEEN = re.compile(r"\bdifference\s+between\b.*\band\b", re.I)


@dataclass(frozen=True)
class Classification:
    """The triage result. `signals` and `reasons` exist so a wrong call can be
    audited later without re-running anything — the packet's audit-trail rail."""

    claim_type: ClaimType
    confidence: float
    reasons: tuple[str, ...] = ()
    signals: dict[str, list[str]] = field(default_factory=dict)
    demoted_from: ClaimType | None = None

    @property
    def needs_external_evidence(self) -> bool:
        """Only EMPIRICAL claims are settled by going and looking."""
        return self.claim_type is ClaimType.EMPIRICAL

    def as_dict(self) -> dict:
        return {
            "claim_type": self.claim_type.value,
            "confidence": self.confidence,
            "reasons": list(self.reasons),
            "signals": {k: list(v) for k, v in self.signals.items()},
            "demoted_from": self.demoted_from.value if self.demoted_from else None,
        }


def _match_all(question: str, patterns) -> list[str]:
    return [label for pattern, label in patterns if pattern.search(question)]


def _definitional_signals(question: str) -> list[str]:
    found = _match_all(question, _DEFINITIONAL_PATTERNS)
    if _DIFFERENCE_BETWEEN.search(question) and not _ANY_NUM.search(question):
        found.append("distinction-between-terms question")
    return found


def _arithmetic_signals(question: str) -> list[str]:
    """Detect genuine arithmetic. See the BUG HISTORY block above before
    loosening anything in here."""
    found = _match_all(question, _ARITH_PATTERNS)
    if _COMPUTE_VERB.search(question) and len(_ANY_NUM.findall(question)) >= 2:
        found.append("compute verb with two or more operands")
    return found


def _entity_veto_signals(question: str) -> list[str]:
    """Signals that this question is about the world, not about a calculation.
    Any one of these blocks a DETERMINISTIC routing."""
    found: list[str] = []
    if _ENTITY_INTERROGATIVE.search(question):
        found.append("who/when/where/which interrogative")
    if _CURRENCY_OF_STATE.search(question):
        found.append("current-state framing")
    if _INTERIOR_PROPER_NOUN.search(question):
        found.append("proper noun present")
    return found


def classify_claim(question: str) -> Classification:
    """Classify a question into a claim type.

    Safety rule, non-negotiable: when in doubt, return EMPIRICAL. A wrong
    EMPIRICAL costs one search. A wrong DETERMINISTIC costs a wrong answer
    delivered confidently.
    """
    q = question.strip()

    signals: dict[str, list[str]] = {
        ClaimType.NORMATIVE.value: _match_all(q, _NORMATIVE_PATTERNS),
        ClaimType.DEFINITIONAL.value: _definitional_signals(q),
        ClaimType.PREDICTIVE.value: _match_all(q, _PREDICTIVE_PATTERNS),
        ClaimType.DETERMINISTIC.value: _arithmetic_signals(q),
    }
    entity_vetoes = _entity_veto_signals(q)
    signals["ENTITY_VETO"] = entity_vetoes

    fired = [t for t in _PRIORITY if t is not ClaimType.EMPIRICAL and signals[t.value]]

    if not fired:
        return Classification(
            claim_type=ClaimType.EMPIRICAL,
            confidence=0.6,
            reasons=("no non-empirical signal matched; defaulting to EMPIRICAL (safe default)",),
            signals=signals,
        )

    chosen = fired[0]
    reasons = [f"{chosen.value}: {s}" for s in signals[chosen.value]]

    # The demotion rail. A question that mentions a real entity or asks
    # who/when/where is not a calculator problem, whatever the digits look like.
    if chosen is ClaimType.DETERMINISTIC and entity_vetoes:
        return Classification(
            claim_type=ClaimType.EMPIRICAL,
            confidence=0.55,
            reasons=tuple(
                reasons
                + [f"demoted to EMPIRICAL — entity signal present: {v}" for v in entity_vetoes]
            ),
            signals=signals,
            demoted_from=ClaimType.DETERMINISTIC,
        )

    # Multiple types fired: still answer, but say the confidence is lower so a
    # downstream step can choose to spend a call resolving the ambiguity.
    confidence = 0.9 if len(fired) == 1 else 0.6
    if len(fired) > 1:
        reasons.append(
            "multiple claim types matched (" + ", ".join(t.value for t in fired) + "); "
            "took highest-priority type at reduced confidence"
        )

    return Classification(
        claim_type=chosen,
        confidence=confidence,
        reasons=tuple(reasons),
        signals=signals,
    )
