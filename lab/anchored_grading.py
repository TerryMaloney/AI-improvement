"""Deterministic grading for the Stage 0A-M anchored battery.

Every route here is mechanical. There is no judge and no runtime escalation: an
item's route is declared at authoring time, and if a correct answer can be
phrased in a way the route does not accept, that is an authoring defect to be
caught by the paraphrase tests before dispatch -- not something to be rescued by
a judge afterwards, which would make the primary analysis subset depend on
outcomes.

Three routes:

  exact_entity  normalised string match against an enumerated alias set
  numeric       value extracted from prose, compared within a frozen tolerance
  boolean       yes/no extracted from prose

Each item also carries `rejects`: the principal plausible wrong answer implied by
the mechanism (the current officeholder instead of the anchored one, the
alternative-definition quantity instead of the requested one). A response
matching a reject is graded incorrect even if it happens to contain an accepted
alias somewhere -- otherwise "X, not Y" and "Y, not X" would grade the same.
"""

from __future__ import annotations

import re
import unicodedata

_PUNCT = re.compile(r"[^\w\s.%-]", re.UNICODE)
_WS = re.compile(r"\s+")


def normalise(text: str) -> str:
    """Casefold, strip accents and most punctuation, collapse whitespace."""
    t = unicodedata.normalize("NFKD", text or "")
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.casefold()
    t = _PUNCT.sub(" ", t)
    return _WS.sub(" ", t).strip()


def _contains_phrase(haystack: str, needle: str) -> bool:
    """Word-boundary containment on normalised text, so 'nato' does not match
    'discriminator' and '8' does not match '18'."""
    h, n = normalise(haystack), normalise(needle)
    if not n:
        return False
    return re.search(rf"(?<!\w){re.escape(n)}(?!\w)", h) is not None


NUM = re.compile(r"-?\d[\d,]*\.?\d*")


def extract_numbers(text: str) -> list[float]:
    out = []
    for m in NUM.finditer(text or ""):
        try:
            out.append(float(m.group(0).replace(",", "")))
        except ValueError:
            continue
    return out


def grade_exact_entity(answer: str, accept: list[str], rejects: list[str]) -> bool:
    if any(_contains_phrase(answer, r) for r in rejects):
        return False
    return any(_contains_phrase(answer, a) for a in accept)


def grade_numeric(answer: str, value: float, tolerance: float, rejects: list[float]) -> bool:
    found = extract_numbers(answer)
    if not found:
        return False
    if any(abs(f - r) <= tolerance for f in found for r in rejects):
        return False
    return any(abs(f - value) <= tolerance for f in found)


_YES = ("yes", "it was", "was a member", "was still", "had", "did")
_NO = ("no", "it was not", "was not", "were not", "had not", "did not", "was never")


def grade_boolean(answer: str, expected: bool) -> bool:
    n = normalise(answer)
    neg = any(_contains_phrase(n, p) for p in _NO)
    pos = any(_contains_phrase(n, p) for p in _YES)
    if neg and not expected:
        return True
    if pos and not neg and expected:
        return True
    return False


def grade(item: dict, answer: str) -> bool:
    route = item["grading"]["route"]
    g = item["grading"]
    if route == "exact_entity":
        return grade_exact_entity(answer, g["accept"], g.get("rejects", []))
    if route == "numeric":
        return grade_numeric(answer, g["value"], g["tolerance"], g.get("rejects", []))
    if route == "boolean":
        return grade_boolean(answer, g["expected"])
    raise ValueError(f"unknown grading route: {route!r}")
