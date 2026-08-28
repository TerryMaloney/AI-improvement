"""Answer-key integrity: correction rule C1, made executable.

See docs/ANSWER_KEY_CORRECTION_PROCESS.md. The rule exists because two grading
defects in exp001 pointed in OPPOSITE directions:

  * f08's `reject` held bare entity fragments ("Poland and"), which matched
    inside a correct denial and produced false FAILs.
  * f07's `accept_trap_markers` held a bare topic word ("deficit"), which
    matched any answer discussing trade balances at all and produced false
    PASSes — including for an answer that abstained and never addressed the
    premise.

Both are the same underlying error: a matching string that cannot tell an
assertion from a mention. This test refuses that class of string outright,
so the rule cannot quietly regress the next time someone adds a trap question.
"""

import re

import pytest

from lab.battery import load_answers

# Words that name the subject matter without taking a position on the premise.
# A trap marker made only of these matches any on-topic answer.
BARE_TOPIC_WORDS = {
    "deficit", "surplus", "balance", "trade", "nobel", "prize", "ceo",
    "population", "moons", "deaths", "member", "state", "states",
}

NEGATION_OR_PREMISE = re.compile(
    r"\b(?:not|never|no|none|did\s+not|does\s+not|was\s+not|were\s+not|"
    r"false|incorrect|mistaken|wrong|assumes|presupposes|only|premise)\b",
    re.I,
)

# A directional assertion is allowed as a `reject` string: it states the false
# premise outright. grade_trap_detected gives an explicit rejection precedence
# over an incidental mention, so these are safe.
ASSERTION_SHAPED = re.compile(r"\b(?:won|left|withdrew|awarded|is|has|had)\b", re.I)

# OPERATIONALISATION NOTE, found by this test failing on its first run.
# C1 as written permits "a directional assertion that cannot be produced by a
# correct answer". The first version of this test only recognised negations and
# premise words, and so rejected "runs a deficit" — which is a perfectly good
# discriminating marker: it states a RELATION contradicting the premise, and an
# answer that accepts the false premise (that the US runs a surplus) will not
# contain it. "deficit" alone names a topic and discriminates nothing.
# The distinction that matters is therefore relation-vs-topic, not the presence
# of a negation word. A marker qualifies if it is a multi-word phrase carrying a
# verb. The key was not changed to satisfy the test; the test was corrected to
# match the rule already committed.
RELATIONAL = re.compile(r"\b(?:runs|run|has|have|is|are|was|were|does|do|left|won|leave)\b", re.I)


def _is_relational_phrase(s: str) -> bool:
    return len(re.findall(r"[a-z]+", s.lower())) >= 3 and bool(RELATIONAL.search(s))


def _entries_with_traps():
    answers = load_answers().get("answers", {})
    return {
        qid: e
        for qid, e in answers.items()
        if isinstance(e, dict) and (e.get("accept_trap_markers") or e.get("reject"))
    }


def _violations(s: str, field: str) -> list[str]:
    out = []
    tokens = [w for w in re.findall(r"[a-z]+", s.lower())]
    if not tokens:
        return ["empty or non-alphabetic string"]
    # (a) bare topic word: every token is a topic word, and there is no negation
    if all(t in BARE_TOPIC_WORDS for t in tokens) and not NEGATION_OR_PREMISE.search(s):
        out.append(f"(a) bare topic word: {s!r} matches any on-topic answer")
    # (c) bare year or number
    if re.fullmatch(r"[\d\s,.-]+", s.strip()):
        out.append(f"(c) bare number/year: {s!r}")
    # (b) bare entity fragment: capitalised name plus a dangling connective
    if re.fullmatch(r"[A-Z][A-Za-z.\-]*(?:\s+[A-Z][A-Za-z.\-]*)*\s+(?:and|or|,)\s*", s + " "):
        out.append(f"(b) bare entity fragment: {s!r} appears in denials too")
    # a marker must carry a negation or premise construction; a reject string
    # must instead be assertion-shaped
    if (
        field == "accept_trap_markers"
        and not NEGATION_OR_PREMISE.search(s)
        and not _is_relational_phrase(s)
    ):
        out.append(
            f"marker {s!r} names a topic without stating a relation: it carries no "
            f"negation, no premise construction, and is not a multi-word relational phrase"
        )
    if field == "reject" and not ASSERTION_SHAPED.search(s):
        out.append(f"reject {s!r} is not assertion-shaped")
    return out


@pytest.mark.parametrize("field", ["accept_trap_markers", "reject"])
def test_c1_trap_strings_are_premise_bearing(field):
    problems = []
    for qid, entry in _entries_with_traps().items():
        for s in entry.get(field, []) or []:
            for v in _violations(s, field):
                problems.append(f"{qid}.{field}: {v}")
    assert not problems, "correction rule C1 violated:\n  " + "\n  ".join(problems)


def test_c1_removed_the_two_known_defective_strings():
    """The specific strings that caused the exp001 artifacts must stay gone."""
    answers = load_answers()["answers"]
    assert "deficit" not in (answers["f07"].get("accept_trap_markers") or []), \
        "f07 bare topic word 'deficit' is back; it auto-passes any answer mentioning trade"
    assert not any(
        s in (answers["f08"].get("reject") or [])
        for s in ["Poland and", "Hungary and", "Italy and"]
    ), "f08 bare entity fragments are back; they match inside correct denials"


def test_v1_frozen_key_still_contains_the_defects():
    """The frozen key must NOT be corrected — it is the historical record of
    what exp001 was actually graded against. If this test starts failing,
    someone has rewritten history."""
    from pathlib import Path

    import yaml

    v1 = yaml.safe_load(Path("batteries/answers.v1.frozen.yaml").read_text())["answers"]
    assert "deficit" in v1["f07"]["accept_trap_markers"], \
        "the frozen v1 key has been edited; exp001's grading provenance is destroyed"
    assert "Poland and" in v1["f08"]["reject"], \
        "the frozen v1 key has been edited; exp001's grading provenance is destroyed"
