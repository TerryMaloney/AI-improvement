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


# Spelled-out small integers are extracted alongside digits.
#
# Not a convenience. Six items have integer keys in 0-20 (a08, b05, b08, b09,
# b11, b25), and a solver writing "four" rather than "4" was graded incorrect.
# That is not merely a power loss: answer FORMAT plausibly correlates with arm --
# a retrieval-enabled solver quoting a source tends to emit digits, a closed-book
# solver reasoning in prose is likelier to spell a small number out -- so the gap
# could manufacture discordant pairs out of formatting rather than correctness,
# in a direction set by an artifact of the instrument.
#
# The mapping is applied uniformly to the accepted value and to the rejects, so a
# solver writing "five" is rejected exactly as one writing "5" is. No item in the
# battery has 0, 1 or 2 as its value or as a reject, so the frequent prose senses
# of "one" and "two" cannot collide with any key: they contribute a number that
# matches nothing.
NUMBER_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
    "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
}
WORD_NUM = re.compile(r"\b(" + "|".join(NUMBER_WORDS) + r")\b", re.IGNORECASE)


def extract_numbers(text: str) -> list[float]:
    out = []
    for m in NUM.finditer(text or ""):
        try:
            out.append(float(m.group(0).replace(",", "")))
        except ValueError:
            continue
    for m in WORD_NUM.finditer(text or ""):
        out.append(float(NUMBER_WORDS[m.group(1).lower()]))
    return out


def grade_exact_entity(answer: str, accept: list[str], rejects: list[str]) -> bool:
    if any(_contains_phrase(answer, r) for r in rejects):
        return False
    return any(_contains_phrase(answer, a) for a in accept)


def grade_numeric(answer: str, value: float, tolerance: float, rejects: list[float]) -> bool:
    """Correct iff the requested value appears. Rejects do NOT override it.

    This differs deliberately from `grade_exact_entity`, where a reject does take
    precedence. The asymmetry is not an oversight, and the reasoning matters
    enough to keep next to the code.

    Every reject in this battery lies outside its accept band -- the separation
    invariant in the test suite enforces it. So on the numeric route, a reject can
    only ever change the verdict in one situation: when the CORRECT value is
    present too. Reject-precedence therefore performs no protective work here. An
    answer containing only a reject already fails, because no found number lands
    within tolerance of the value. All reject-precedence could do was convert
    correct answers into incorrect ones.

    And it did. Every one of these was graded incorrect under the old rule:

        "193 member states, excluding the 2 permanent observers"   (b15)
        "13 individual golds, out of 23 total"                     (b08)
        "381 m to the architectural top; 443 m with the antenna"   (b17)
        "8 planets; there were 9 before 2006"                      (b05)
        "20 of the 27 EU member states"                            (b09)

    Each answers the question asked, correctly, and names the contrasting figure
    to show the distinction was understood -- the behaviour the anchored-stem
    design is trying to elicit. Marking them wrong is a false negative, and a
    dangerous one: a solver that has just retrieved a source is MORE likely to
    state both figures, so the false negatives concentrate in the
    retrieval-enabled arm and manufacture n10 -- a false HARM signal, pointing
    the way the hypothesis predicts. Fixed before any outcome was observed.

    `rejects` remains in the keys: it documents the displacing answer, drives the
    separation invariant, and is asserted by the tests that a bare reject fails.
    """
    found = extract_numbers(answer)
    if not found:
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
