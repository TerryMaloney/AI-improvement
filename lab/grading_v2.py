"""CANDIDATE grading semantics for Stage 0B. NOT the Stage 0A-M grader.

`lab/anchored_grading.py` is frozen and must not change: Stage 0A-M is scored
under it. This module is a separate, unfrozen candidate that exists so the
Stage 0B rule can be specified, tested and fingerprinted BEFORE any Stage 0B
outcome is observed.

THE DEFECT IT REPAIRS
---------------------
Stage 0A-M's independent review established, deterministically, that:

  * 32 / 32 exact_entity trials contained the accepted entity;
  * in all 28 that were graded incorrect, the accepted entity appeared strictly
    BEFORE any reject alias;
  * 14 / 14 boolean trials opened with the correct polarity token, and 2 were
    graded incorrect because a negation token appeared later, inside a
    contextual clause ("...it was no longer a member state...").

Both are the same failure: a rule that asks "does a wrong-looking string appear
ANYWHERE" cannot distinguish

    "Bolsonaro was president, and was later succeeded by Lula"   (correct)
from
    "Lula was president"                                          (incorrect)
or
    "Lula, who succeeded Bolsonaro, was president"                (incorrect)

Whole-answer containment is the wrong scope. The distinguishing information is
POSITION and SCOPE, and it is present in every one of these strings.

THE RULE
--------
Grade the ANSWER SPAN -- the leading direct answer -- and treat everything after
it as unscored elaboration.

  answer_span(text)  ->  the first sentence, capped at SPAN_CHAR_CAP characters

  entity   the span must contain an accepted alias, and no reject alias may
           appear in the span before it. Rejects outside the span are ignored.
  boolean  the FIRST polarity token in the span decides. Later negations are
           elaboration.
  numeric  a number within tolerance of the value must appear in the span.
           Rejects still do not override (the Stage 0A-M numeric rule was
           already correct and is preserved).

WHY DIRECT-ANSWER-FIRST RATHER THAN A STRUCTURED FIELD
------------------------------------------------------
Three candidates were compared (see docs/EXP004_STAGE0B_DESIGN_DRAFT.md §5):

  (1) natural answer + whole-answer deterministic parser -- the Stage 0A-M rule.
      Rejected: demonstrably cannot separate the two sentences above.
  (2) natural answer + direct-answer-first span parser -- THIS MODULE.
      Costs nothing behaviourally: 32/32 entity and 14/14 boolean Stage 0A-M
      answers already led with the direct answer, unprompted.
  (3) structured primary-answer field (JSON). Most parseable, but demanding a
      structured field changes the task the model is performing, and format
      compliance can interact with the arm -- a solver that has just read search
      results is in a different generation state from one that has not. That is
      a treatment-correlated instrument risk, which is exactly the class of
      defect Stage 0A-M was destroyed by.

(2) is the primary. (3) is retained only as a pre-registered robustness arm-free
replication, never as the primary route.

ABSTENTION
----------
`ABSTAIN` is a third verdict, distinct from incorrect. Stage 0A-M had no way to
say "the solver declined", which conflates refusal with error. An abstention is
reported, and its handling is preregistered by the analysis, not by this module.
"""
from __future__ import annotations

import re
from enum import Enum

from lab.anchored_grading import NUMBER_WORDS, extract_numbers, normalise

SPAN_CHAR_CAP = 240
"""Hard cap on the answer span, in raw characters, before sentence splitting.

A cap is required, not cosmetic: without one a solver that writes its whole
answer as a single unpunctuated sentence would be graded on everything, which is
the Stage 0A-M rule again. The cap is generous enough for every Stage 0A-M
leading sentence (longest observed: 231 characters) and is frozen here.
"""

_SENTENCE_END = re.compile(r"(?<=[.!?])[\s ]")

# Abbreviations whose trailing period must not end the span.
_ABBREV = ("inc.", "ltd.", "co.", "corp.", "u.s.", "u.k.", "e.g.", "i.e.", "no.",
           "mr.", "mrs.", "ms.", "dr.", "st.", "vs.", "approx.", "est.", "d.c.")


def _starts_new_sentence(text: str, i: int) -> bool:
    """A real sentence opens with a capital or a digit.

    This disambiguates the two readings of a trailing abbreviation period:
    "Apple Inc. reported ..." continues one sentence, while
    "Google Inc. As of 1 June 2015 ..." is two -- and in the second case the
    direct answer is the abbreviation itself, so the span must stop there.
    """
    while i < len(text) and text[i].isspace():
        i += 1
    return i < len(text) and (text[i].isupper() or text[i].isdigit())


class Verdict(str, Enum):
    CORRECT = "CORRECT"
    INCORRECT = "INCORRECT"
    ABSTAIN = "ABSTAIN"


_ABSTAIN_PHRASES = (
    "i do not know", "i don't know", "i cannot determine", "i can not determine",
    "cannot be determined", "unable to determine", "i am not sure", "no information",
    "i have no way to know", "insufficient information",
)


def is_abstention(text: str) -> bool:
    n = normalise(text or "")
    return any(p in n for p in (normalise(p) for p in _ABSTAIN_PHRASES))


def answer_span(text: str) -> str:
    """The leading direct-answer span: the first sentence, capped.

    Sentence splitting is deliberately crude and deterministic. A period that
    ends a known abbreviation does not end the span; nothing else is special.
    """
    t = (text or "").strip()
    if not t:
        return ""
    head = t[:SPAN_CHAR_CAP]
    pos = 0
    while True:
        m = _SENTENCE_END.search(head, pos)
        if m is None:
            return head.strip()
        end = m.start()                       # index just past the '.', '!' or '?'
        if head[:end].lower().endswith(_ABBREV) and not _starts_new_sentence(head, m.end()):
            pos = m.end()                     # "Apple Inc. reported ..." -- same sentence
            continue
        return head[:end].strip()             # "Google Inc. As of ..." -- sentence ended


def _first_pos(haystack: str, needle: str) -> int | None:
    h, n = normalise(haystack), normalise(needle)
    if not n:
        return None
    m = re.search(rf"(?<!\w){re.escape(n)}(?!\w)", h)
    return m.start() if m else None


def grade_entity_v2(answer: str, accept: list[str], rejects: list[str]) -> Verdict:
    """Correct iff an accepted alias appears in the span before any reject alias."""
    if is_abstention(answer):
        return Verdict.ABSTAIN
    span = answer_span(answer)
    acc = [p for p in (_first_pos(span, a) for a in accept) if p is not None]
    rej = [p for p in (_first_pos(span, r) for r in rejects or []) if p is not None]
    if not acc:
        return Verdict.INCORRECT
    if rej and min(rej) < min(acc):
        return Verdict.INCORRECT
    return Verdict.CORRECT


_POLARITY = re.compile(r"(?<!\w)(yes|no|not|never)(?!\w)", re.IGNORECASE)
_AFFIRMATIVE = {"yes"}


def grade_boolean_v2(answer: str, expected: bool) -> Verdict:
    """The FIRST polarity token in the span decides. Later negations are context."""
    if is_abstention(answer):
        return Verdict.ABSTAIN
    m = _POLARITY.search(normalise(answer_span(answer)))
    if m is None:
        return Verdict.INCORRECT
    said_yes = m.group(1).lower() in _AFFIRMATIVE
    return Verdict.CORRECT if said_yes == bool(expected) else Verdict.INCORRECT


def grade_numeric_v2(answer: str, value: float, tolerance: float,
                     rejects: list[float] | None = None) -> Verdict:
    """A number within tolerance must appear in the SPAN. Rejects never override.

    The Stage 0A-M numeric rule was already correct on the rejects question and
    is preserved verbatim; the only change is that it now reads the span rather
    than the whole answer, so a contrast figure quoted three sentences later
    cannot be mistaken for the answer -- and, symmetrically, cannot rescue one.
    """
    if is_abstention(answer):
        return Verdict.ABSTAIN
    found = extract_numbers(answer_span(answer))
    if not found:
        return Verdict.INCORRECT
    return Verdict.CORRECT if any(abs(f - value) <= tolerance for f in found) \
        else Verdict.INCORRECT


ROUTES = {"exact_entity", "numeric", "boolean"}


def grade_v2(route: str, answer: str, key: dict) -> Verdict:
    if route == "exact_entity":
        return grade_entity_v2(answer, key["accept"], key.get("rejects", []))
    if route == "numeric":
        return grade_numeric_v2(answer, key["value"], key["tolerance"], key.get("rejects", []))
    if route == "boolean":
        return grade_boolean_v2(answer, key["expected"])
    raise ValueError(f"unknown grading route: {route!r}")


__all__ = ["Verdict", "answer_span", "is_abstention", "grade_v2", "grade_entity_v2",
           "grade_boolean_v2", "grade_numeric_v2", "SPAN_CHAR_CAP", "ROUTES", "NUMBER_WORDS"]
