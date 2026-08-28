"""Task labels: vocabulary, coherence, and separation from claim type.

The point of these axes is that they are NOT the router's vocabulary. If an axis
turned out to be a one-to-one relabelling of `claim_type`, grouping results by it
would be grouping by the treatment, and the mechanism would be confirmed by its
own bookkeeping.
"""

from __future__ import annotations

import pytest

from lab.battery import load_battery
from lab.labels import AXES, VOCAB, allowed, collinearity, validate

GOOD = {
    "knowledge_source": "parametric",
    "reasoning_depth": "lookup",
    "premise": "sound",
    "referent": "unique",
    "ground_truth_state": "stable",
    "correct_response_mode": "assert",
}


def test_six_axes_exactly():
    assert len(AXES) == 6
    assert set(AXES) == set(VOCAB)


def test_every_axis_carries_its_operational_test():
    """A vocabulary without a stated test is a category the author can apply
    however it suits the result they want."""
    for axis in AXES:
        test = VOCAB[axis]["_test"]
        assert len(test) > 80, f"{axis}: operational test is too thin to apply"
        assert "->" in test, f"{axis}: operational test states no decision rule"


def test_valid_labels_round_trip():
    assert validate(GOOD) == GOOD


def test_missing_labels_are_refused_not_defaulted():
    """An item silently defaulted into parametric/lookup/sound/unique/stable/
    assert would be assigned to the wrong diagnostic cell while looking
    deliberate."""
    with pytest.raises(ValueError, match="task_labels missing"):
        validate(None, where="x")
    with pytest.raises(ValueError, match="missing axes"):
        validate({"knowledge_source": "parametric"}, where="x")


def test_unknown_axis_and_unknown_value_are_refused():
    with pytest.raises(ValueError, match="unknown task-label axes"):
        validate({**GOOD, "vibes": "good"})
    with pytest.raises(ValueError, match="not in the vocabulary"):
        validate({**GOOD, "premise": "sort of true"})


@pytest.mark.parametrize(
    "override,fragment",
    [
        ({"premise": "false"}, "reject_premise"),
        ({"referent": "nonexistent"}, "reject_premise"),
        ({"referent": "ambiguous"}, "incompatible with correct_response_mode=assert"),
        ({"ground_truth_state": "unknown"}, "abstain or estimate"),
        ({"knowledge_source": "derivable"}, "at least one inferential move"),
        ({"knowledge_source": "derivable", "reasoning_depth": "single_step",
          "ground_truth_state": "volatile"}, "cannot drift with the calendar"),
    ],
)
def test_incoherent_combinations_are_refused(override, fragment):
    """Each rule is a definitional consequence of the labels involved, so a
    violation means a label is wrong — not that the item is unusual."""
    with pytest.raises(ValueError, match="incoherent"):
        validate({**GOOD, **override})
    try:
        validate({**GOOD, **override})
    except ValueError as e:
        assert fragment in str(e)


def test_collinearity_detects_an_axis_that_is_just_claim_type():
    items = [
        ("q1", {**GOOD}, "EMPIRICAL"),
        ("q2", {**GOOD}, "EMPIRICAL"),
        ("q3", {**GOOD, "knowledge_source": "derivable", "reasoning_depth": "single_step"},
         "DETERMINISTIC"),
    ]
    rep = collinearity(items)
    # knowledge_source is perfectly predicted by claim type in this set
    assert rep["knowledge_source"]["determined_by_claim_type"] is True
    # ...and so, trivially, are the axes that never vary
    assert rep["premise"]["distinct_values"] == 1


def test_collinearity_clears_an_axis_that_varies_within_a_claim_type():
    items = [
        ("q1", {**GOOD}, "EMPIRICAL"),
        ("q2", {**GOOD, "reasoning_depth": "multi_step"}, "EMPIRICAL"),
    ]
    assert collinearity(items)["reasoning_depth"]["determined_by_claim_type"] is False


def test_frozen_batteries_stay_loadable_and_unlabelled():
    """`factual` and `abstract` predate the axes and are frozen as regression
    batteries. Requiring labels globally would mean editing frozen material to
    satisfy new instrumentation."""
    for name in ("factual", "abstract"):
        battery = load_battery(name)
        assert battery.requires_task_labels is False
        assert all(q.task_labels is None and not q.labelled for q in battery.questions)


def test_a_battery_can_demand_labels(tmp_path):
    import yaml

    doc = {
        "id": "demo_v1",
        "requires_task_labels": True,
        "questions": [{"id": "d1", "text": "How many minutes are in 3 hours and 20 minutes?"}],
    }
    path = tmp_path / "demo.yaml"
    path.write_text(yaml.safe_dump(doc))
    with pytest.raises(ValueError, match="task_labels missing"):
        load_battery(path)

    doc["questions"][0]["task_labels"] = {
        **GOOD, "knowledge_source": "derivable", "reasoning_depth": "single_step",
    }
    path.write_text(yaml.safe_dump(doc))
    battery = load_battery(path)
    assert battery.questions[0].labelled
    assert battery.questions[0].task_labels["knowledge_source"] == "derivable"


def test_allowed_excludes_the_operational_test_key():
    for axis in AXES:
        assert "_test" not in allowed(axis)
        assert len(allowed(axis)) >= 3
