"""Stage 0B ground truth — who decides what an answer actually said.

WHY THIS MODULE EXISTS, AND WHY IT DOES NOT IMPORT THE GRADER
-------------------------------------------------------------
The calibration bank measures the candidate grader's defect rate by comparing its
verdict against a hand-derived one. That comparison is worth nothing if the
hand-derived verdict is produced by the same rule, or by a rule that shares the
grader's failure mode. `lab/grading_v2.py` is deliberately NOT imported here, and
a test asserts it.

The honest difficulty, stated rather than designed around: **any deterministic
reference shares assumptions with a deterministic grader.** A rule that reads
first-occurrence order over the whole answer reproduces the span rule's verdict on
most inputs, including on the cases where the span rule is KNOWN to be wrong (a
leading contrastive negation, "Not Vandermeer -- Okonjo held the office", is
misread by both). Using such a rule as ground truth would certify the grader
against its own blind spot.

So this module does not try to be a better grader. It **partitions** answers:

    DETERMINATE   the key decides the verdict without judgement, and the rule
                  used to decide is not the rule under test
    ESCALATE      the classes where a deterministic rule is known to be
                  unreliable -- these go to a human, and only a human

The escalation classes are exactly the documented failure modes, so the human
adjudicates where independence actually buys something and nowhere else. That is
what keeps the manual burden bounded without weakening the validation.

THE ORDERING RULE THAT MAKES A DEFECT A MEASUREMENT
---------------------------------------------------
The reference verdict -- deterministic or human -- is recorded BEFORE the
candidate grader runs on that answer, and `CalibrationRow.hand_verdict_recorded_first`
asserts it. A human adjudicator who has seen the grader's verdict is not an
independent reference; they are a reviewer of the grader, which is a different and
much weaker thing.

WHAT IS FORBIDDEN
-----------------
* The candidate grader may never produce its own ground truth.
* The orchestrating model may never adjudicate an answer whose grader verdict it
  has already seen.
* An escalated case may never be resolved by re-running any grader.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

# --------------------------------------------------------------------------- #
# escalation taxonomy -- each entry names the failure mode it exists to dodge
# --------------------------------------------------------------------------- #

ESCALATION_REASONS = {
    "CONTRASTIVE_NEGATION":
        "a negation or contrast marker sits in the opening region, so first-occurrence "
        "order does not carry the semantics. This is the grader's own documented "
        "limitation ('Not Vandermeer -- Okonjo held the office'), and a deterministic "
        "reference would share it.",
    "PREMISE_CONTEST":
        "the answer disputes the question rather than answering it -- the `a08` class "
        "('Strictly speaking, none...'). No key can adjudicate a contested premise, and "
        "an item that provokes one is a recipe finding, not a grading finding.",
    "NO_KEY_MATCH":
        "neither an accept nor a reject alias appears anywhere. Either the answer is "
        "phrased outside the key's alias coverage, or it is off-topic. Both need a human, "
        "and both are recipe findings.",
    "REJECT_LEADS_ACCEPT":
        "a reject alias precedes an accept alias in the opening region. That is either a "
        "genuine wrong answer or a contrastive correction, and the difference is exactly "
        "what a positional rule cannot see.",
    "NO_POLARITY":
        "a boolean answer with no polarity token. Recorded as a known limitation rather "
        "than guessed.",
    "MULTIPLE_NUMERIC_CANDIDATES":
        "more than one in-tolerance-or-reject numeric value appears, so which one is the "
        "answer is a reading question, not an arithmetic one.",
}

# The opening region the reference rule reads. It is DELIBERATELY not the grader's
# span: no sentence segmentation, no abbreviation handling, no 240-character
# sentence cap. A fixed window cannot agree with the span rule for the span rule's
# reasons, which is the point of using one.
OPENING_CHARS = 240

_NEGATION_MARKERS = (
    "not ", "n't ", "never ", "no longer ", "rather than", "instead of",
    "as opposed to", "unlike ", "contrary to", "isn't", "wasn't", "aren't",
    "weren't", "did not", "was not", "is not", "were not",
)
_PREMISE_CONTEST_MARKERS = (
    "strictly speaking", "technically", "it depends", "depends on", "arguably",
    "there was no", "there is no", "no such", "undefined", "ill-defined",
    "the question assumes", "none -", "none,", "none.", "trick question",
    "ambiguous", "no formal definition",
)
_ABSTAIN_MARKERS = (
    "i don't know", "i do not know", "i cannot determine", "i can't determine",
    "unable to determine", "i'm not sure", "i am not sure", "cannot say",
)
_POLARITY = re.compile(r"(?<!\w)(yes|no|not|never)(?!\w)")
_NUMBER = re.compile(r"-?\d+(?:\.\d+)?")

DETERMINATE = "DETERMINATE"
ESCALATE = "ESCALATE"


def normalise(text: str) -> str:
    """Case-fold and strip accents. Independent of the grader's own normaliser --
    a test asserts the two modules share no import."""
    t = unicodedata.normalize("NFKD", text or "")
    t = "".join(c for c in t if not unicodedata.combining(c))
    return " ".join(t.casefold().split())


@dataclass(frozen=True)
class Adjudication:
    """One reference verdict, or one escalation.

    `verdict` is None exactly when `disposition` is ESCALATE. `rule` names the
    deterministic rule that decided, so a third party can re-derive it.
    """
    disposition: str                 # DETERMINATE | ESCALATE
    verdict: str | None              # CORRECT | INCORRECT | ABSTAIN | None
    reason: str                      # escalation key, or the rule that decided
    detail: str = ""

    @property
    def needs_human(self) -> bool:
        return self.disposition == ESCALATE


def _first(hay: str, needles) -> int | None:
    hits = [hay.find(normalise(n)) for n in (needles or []) if n]
    hits = [h for h in hits if h >= 0]
    return min(hits) if hits else None


def _opening_flags(answer: str) -> Adjudication | None:
    """Checks that escalate regardless of route, read on the opening region only."""
    head = normalise(answer)[:OPENING_CHARS]
    if any(m in head for m in _ABSTAIN_MARKERS):
        return Adjudication(DETERMINATE, "ABSTAIN", "explicit_abstention",
                            "an abstention marker leads the answer")
    if any(m in head for m in _PREMISE_CONTEST_MARKERS):
        return Adjudication(ESCALATE, None, "PREMISE_CONTEST", head[:120])
    if any(m in head for m in _NEGATION_MARKERS):
        return Adjudication(ESCALATE, None, "CONTRASTIVE_NEGATION", head[:120])
    return None


def reference_entity(answer: str, accept: list[str], rejects: list[str]) -> Adjudication:
    pre = _opening_flags(answer)
    if pre is not None:
        return pre
    whole = normalise(answer)
    a, r = _first(whole, accept), _first(whole, rejects)
    if a is None and r is None:
        return Adjudication(ESCALATE, None, "NO_KEY_MATCH", whole[:120])
    if a is None:
        return Adjudication(DETERMINATE, "INCORRECT", "reject_only",
                            "a reject alias appears and no accept alias does")
    if r is None:
        return Adjudication(DETERMINATE, "CORRECT", "accept_only",
                            "an accept alias appears and no reject alias does")
    if r < a:
        return Adjudication(ESCALATE, None, "REJECT_LEADS_ACCEPT", whole[:120])
    return Adjudication(DETERMINATE, "CORRECT", "accept_precedes_reject",
                        "an accept alias precedes every reject alias in the whole answer")


def reference_boolean(answer: str, expected: bool) -> Adjudication:
    pre = _opening_flags(answer)
    if pre is not None and pre.reason == "CONTRASTIVE_NEGATION":
        # A boolean answer's polarity token IS a negation marker, so the generic
        # check would escalate every "No." Fall through to the polarity rule and
        # escalate only when the opening carries MORE than one polarity token.
        head = normalise(answer)[:OPENING_CHARS]
        if len(_POLARITY.findall(head)) > 1:
            return Adjudication(ESCALATE, None, "CONTRASTIVE_NEGATION", head[:120])
    elif pre is not None:
        return pre
    head = normalise(answer)[:OPENING_CHARS]
    m = _POLARITY.search(head)
    if m is None:
        return Adjudication(ESCALATE, None, "NO_POLARITY", head[:120])
    said_yes = m.group(1) == "yes"
    ok = said_yes == bool(expected)
    return Adjudication(DETERMINATE, "CORRECT" if ok else "INCORRECT",
                        "first_polarity_token", m.group(1))


def reference_numeric(answer: str, value: float, tolerance: float,
                      reject_values: list[float] | None = None) -> Adjudication:
    pre = _opening_flags(answer)
    if pre is not None and pre.reason != "CONTRASTIVE_NEGATION":
        return pre
    head = normalise(answer)[:OPENING_CHARS]
    nums = [float(x) for x in _NUMBER.findall(head)]
    hits = [n for n in nums if abs(n - value) <= tolerance]
    rejects = [n for n in nums
               if any(abs(n - rv) <= tolerance for rv in (reject_values or []))]
    if not hits and not rejects:
        return Adjudication(ESCALATE, None, "NO_KEY_MATCH", head[:120])
    if hits and rejects:
        return Adjudication(ESCALATE, None, "MULTIPLE_NUMERIC_CANDIDATES", head[:120])
    if hits:
        return Adjudication(DETERMINATE, "CORRECT", "in_tolerance_value_only", str(hits[0]))
    return Adjudication(DETERMINATE, "INCORRECT", "reject_value_only", str(rejects[0]))


def reference_verdict(route: str, answer: str, key: dict) -> Adjudication:
    """Tier-1 reference adjudication. Never calls the candidate grader."""
    if not answer or not answer.strip():
        return Adjudication(DETERMINATE, "ABSTAIN", "empty_answer", "")
    if route == "exact_entity":
        return reference_entity(answer, key.get("accept", []), key.get("rejects", []))
    if route == "boolean":
        return reference_boolean(answer, bool(key["expected"]))
    if route == "numeric":
        return reference_numeric(answer, float(key["value"]), float(key.get("tolerance", 0)),
                                 key.get("reject_values"))
    raise ValueError(f"unknown route {route!r}")


# --------------------------------------------------------------------------- #
# the plan, and the manual prerequisite it implies
# --------------------------------------------------------------------------- #

# Escalation-rate assumption used ONLY to forecast the manual burden. It sizes
# nobody's sample and enters no bound. Anchored on Stage 0A-M: 2 of 130 answers
# were premise-contest or buried-answer cases (1.5%); the rest of the budget is
# alias-coverage and reject-leads-accept, which Stage 0A-M could not measure
# because it never logged an exposed answer.
FORECAST_ESCALATION_RATE = 0.20


def adjudication_plan(n_items: int, answers_per_item: int = 3) -> dict:
    n_answers = n_items * answers_per_item
    esc = round(n_answers * FORECAST_ESCALATION_RATE)
    return {
        "who_adjudicates": {
            "tier_1_deterministic": "lab/stage0b_adjudication.py:reference_verdict. Decides "
                                    "from the key alone, by a rule that is NOT the rule under "
                                    "test: first-occurrence order over the WHOLE answer, and a "
                                    "fixed 240-character opening window with no sentence "
                                    "segmentation and no abbreviation handling.",
            "tier_2_human": "Terry, on escalated cases only. The escalation classes are the "
                            "documented failure modes of any positional rule, so this is where "
                            "independence actually buys something.",
            "never": ["the candidate grader (it would be certifying itself)",
                      "the orchestrating model on any answer whose grader verdict it has "
                      "already seen",
                      "any re-run of any grader to resolve an escalation"],
        },
        "ordering": "the reference verdict is recorded BEFORE the candidate grader runs on "
                    "that answer. `CalibrationRow.hand_verdict_recorded_first` asserts it and "
                    "`validate_row` refuses a row graded without it.",
        "escalation_reasons": ESCALATION_REASONS,
        "manual_burden_forecast": {
            "items": n_items,
            "answers": n_answers,
            "forecast_escalation_rate": FORECAST_ESCALATION_RATE,
            "forecast_human_adjudications": esc,
            "note": "A FORECAST, not a parameter. It sizes no sample and enters no bound. "
                    "The realized escalation rate is itself a recipe-quality signal: "
                    "PREMISE_CONTEST and NO_KEY_MATCH are recipe defects (protocol 2 clauses "
                    "4 and 7), not grader defects.",
        },
        "MANUAL_PREREQUISITE": (
            f"Roughly {esc} answers from a {n_items}-item bank will need human adjudication, "
            f"and they must be adjudicated BEFORE the candidate grader is run on them. This is "
            f"a prerequisite of the calibration run, not a step discovered halfway through it. "
            f"If that burden is unacceptable, the bank is not dispatched -- the alternative is "
            f"not to skip adjudication, because a grader defect rate measured against the "
            f"grader's own rule is not a measurement."
        ),
    }
