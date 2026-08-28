"""diagnostic_v1 is a frozen specification, and these tests are what makes it one.

A battery file full of good intentions is not a pre-registration. The properties
below are the ones that would otherwise quietly decay between authoring and
analysis: complete specifications, a tier wall that stops a diagnostic result
being promoted into a mechanism claim, ground truth that exists and is checked,
and no answer anywhere a prompt could reach.
"""

from __future__ import annotations

import re
from collections import Counter

import pytest
import yaml

from lab.battery import BATTERY_DIR, ground_truth_strings, load_answers, load_battery, scorable
from lab.labels import AXES, collinearity
from lab.spec import (
    CLAIM_KINDS,
    EXPLANATIONS,
    REQUIRED_FIELDS,
    VERDICTS,
    Tier,
    cite,
    gates,
    max_claim,
)
from lab.states import RetrievalState, load_egress

BATTERY = load_battery("diagnostic_v1")
ITEMS = [q.spec for q in BATTERY.questions]
BY_ID = {q.id: q for q in BATTERY.questions}
ANSWERS = load_answers()["answers"]

# Cell sizes fixed by the implementation plan §5. Changing one is a change to
# the power statement in §6, which is why the numbers are asserted and not
# merely observed.
PLANNED_CELLS = {"L": 6, "R": 4, "D": 5, "U": 4, "N": 4, "C": 2}


def test_battery_matches_the_planned_cell_structure():
    assert Counter(q.cell for q in BATTERY.questions) == PLANNED_CELLS
    assert len(BATTERY.questions) == sum(PLANNED_CELLS.values()) == 25


def test_the_battery_demands_labels_and_specifications():
    assert BATTERY.requires_task_labels
    assert BATTERY.requires_item_spec


@pytest.mark.parametrize("item", ITEMS, ids=[i["id"] for i in ITEMS])
class TestEveryItemIsFullySpecified:
    def test_all_required_fields_present_and_non_empty(self, item):
        for field in REQUIRED_FIELDS:
            assert item.get(field) not in (None, "", [], {}), f"{item['id']}: {field}"

    def test_declares_all_six_task_axes(self, item):
        assert set(item["task_labels"]) == set(AXES)

    def test_names_at_least_two_competing_explanations(self, item):
        codes = set(item["competing_explanations"])
        assert len(codes) >= 2
        assert codes <= set(EXPLANATIONS)

    def test_has_a_discriminator_that_says_something(self, item):
        assert len(item["discriminator"].split()) >= 20, (
            f"{item['id']}: a discriminator that cannot be stated in twenty words "
            f"probably does not separate anything"
        )

    def test_predicts_every_condition_it_runs(self, item):
        assert set(item["predictions"]) == set(item["conditions"])

    def test_declares_a_retrieval_expectation_per_condition(self, item):
        assert set(item["expected_retrieval_state"]) == set(item["conditions"])

    def test_verdict_rules_include_not_established(self, item):
        assert set(VERDICTS) <= set(item["verdict_rules"])
        assert str(item["verdict_rules"]["NOT_ESTABLISHED"]).strip()

    def test_failure_consequences_are_concrete(self, item):
        for name, consequence in item["failure_consequences"].items():
            assert len(str(consequence).split()) >= 5, (
                f"{item['id']}/{name}: a consequence needs to say what it forces"
            )

    def test_names_its_confounds(self, item):
        assert len(item["known_confounds"]) >= 1

    def test_says_why_it_is_here(self, item):
        assert len(item["why_in_battery"].split()) >= 15


class TestTheTierWall:
    def test_primary_items_are_deterministic(self):
        """D5: a judge may not determine a primary outcome. exp003c then
        measured a real judge length effect at rubric boundaries."""
        for item in ITEMS:
            if item["evidence_tier"] == "PRIMARY":
                assert item["outcome_type"] == "deterministic", item["id"]

    def test_judged_items_never_reach_primary(self):
        for item in ITEMS:
            if item["outcome_type"] in ("judged", "deterministic_with_judge_fallback"):
                assert item["evidence_tier"] != "PRIMARY", item["id"]

    def test_measurement_validity_items_cannot_support_a_mechanism_claim(self):
        validity = [i for i in ITEMS if i["evidence_tier"] == "MEASUREMENT_VALIDITY"]
        assert validity, "a battery with no instrument check cannot tell a null from a broken tool"
        for item in validity:
            cite(item, "instrument_validity")
            for claim in ("explanation_elimination", "mechanism_effect"):
                with pytest.raises(ValueError, match="may support"):
                    cite(item, claim)

    def test_diagnostic_items_cannot_support_a_mechanism_claim(self):
        """The failure this wall exists for: a cell built to detect a property
        of the instrument, whose result gets written up as evidence for the
        hypothesis because it landed in the same table."""
        for item in ITEMS:
            if item["evidence_tier"] == "DIAGNOSTIC":
                cite(item, "explanation_elimination")
                with pytest.raises(ValueError, match="mechanism_effect"):
                    cite(item, "mechanism_effect")

    def test_primary_items_may_support_everything(self):
        for item in ITEMS:
            if item["evidence_tier"] == "PRIMARY":
                for claim in CLAIM_KINDS:
                    cite(item, claim)

    def test_the_gate_is_declared_only_on_measurement_validity_items(self):
        gated = [i for i in ITEMS if gates(i)]
        assert {i["id"] for i in gated} == {"C01", "C02"}
        for item in gated:
            assert item["evidence_tier"] == "MEASUREMENT_VALIDITY"
            assert max_claim(item) == "instrument_validity"

    def test_the_gate_says_what_it_halts(self):
        for item in ITEMS:
            if gates(item):
                text = " ".join(str(v) for v in item["failure_consequences"].values())
                assert "HALT" in text, f"{item['id']}: a gate must say what it stops"

    def test_at_least_one_cell_can_carry_a_primary_result(self):
        primary = {i["cell"] for i in ITEMS if i["evidence_tier"] == "PRIMARY"}
        assert primary == {"L", "R"}


class TestLengthSensitivityIsDeclaredHonestly:
    def test_judge_free_items_declare_none(self):
        for item in ITEMS:
            if item["outcome_type"] in ("deterministic", "diagnostic_only"):
                assert item["length_sensitivity"] == "NONE", item["id"]

    def test_items_with_a_judge_never_declare_none(self):
        """exp003c measured Delta_length = -0.125 at rubric boundaries. An item
        whose verdict can pass through a judge cannot claim immunity to it."""
        for item in ITEMS:
            if item["outcome_type"] in ("judged", "deterministic_with_judge_fallback"):
                assert item["length_sensitivity"] in ("POSSIBLE", "LIKELY"), item["id"]


class TestRetrievalExpectations:
    def test_closed_conditions_expect_no_retrieval(self):
        closed = {"baseline", "directive_placebo", "A_only", "directive_only", "closed_book"}
        for item in ITEMS:
            for cond, state in item["expected_retrieval_state"].items():
                if cond in closed:
                    assert state == "NONE", f"{item['id']}/{cond}"

    def test_no_item_expects_an_unreachable_state(self):
        """FD-4. WebFetch is egress-blocked, so SOURCE_ACCESS and VERIFICATION
        cannot occur and no item may be specified to reach them."""
        reachable = load_egress().reachable
        for item in ITEMS:
            for cond, state in item["expected_retrieval_state"].items():
                assert RetrievalState(state) in reachable, f"{item['id']}/{cond}: {state}"

    def test_cell_d_never_claims_source_access_or_verification(self):
        for item in ITEMS:
            if item["cell"] == "D":
                states = set(item["expected_retrieval_state"].values())
                assert "SOURCE_ACCESS" not in states
                assert "VERIFICATION" not in states

    def test_cell_d_names_its_checking_as_snippet_level(self):
        raw = (BATTERY_DIR / "diagnostic_v1.yaml").read_text().lower()
        assert "snippet-level checking" in raw, (
            "the cell-D header must name what the search arms actually do, or a "
            "reader will take `search_independent` for verification"
        )


class TestGroundTruth:
    def test_every_item_has_an_answer_key_entry(self):
        missing = [q.id for q in BATTERY.questions if q.id not in ANSWERS]
        assert not missing, f"no ground truth for {missing}"

    def test_uncertainty_items_have_no_ground_truth_and_say_so(self):
        """Cell U has nothing to be correct about. A value here would be an
        invented answer, which is the failure the whole project is about."""
        for q in BATTERY.questions:
            if q.cell == "U":
                entry = ANSWERS[q.id]
                assert entry["status"] == "rubric_only"
                assert entry.get("ground_truth") is None
                assert entry.get("judge_rubric")

    def test_every_other_item_is_verified_and_therefore_scorable(self):
        for q in BATTERY.questions:
            if q.cell == "U":
                continue
            entry = ANSWERS[q.id]
            assert entry["status"] == "verified", f"{q.id}: {entry['status']}"
            assert scorable(entry)

    def test_every_entry_records_the_basis_of_its_check(self):
        """`verified` means CHECKED, and the check has to be written down.

        The first version of this test measured the source field's word count,
        which is a bad proxy: "Computed. 17 x 23 = 391." is six words and is a
        complete, re-runnable check, while eight words of vague provenance is
        not. What the rule actually wants is a NAMED BASIS — either a derivation
        or an identifiable source — so that is what is asserted.
        """
        derivation = re.compile(r"\b(?:computed|definitional|derivation|enumeration)\b", re.I)
        for q in BATTERY.questions:
            source = str(ANSWERS[q.id].get("source", ""))
            has_derivation = bool(derivation.search(source)) and len(source.split()) >= 5
            has_provenance = len(source.split()) >= 12
            assert has_derivation or has_provenance, (
                f"{q.id}: source records neither a derivation nor an identifiable "
                f"provenance: {source!r}"
            )

    def test_numeric_tolerances_cannot_swallow_a_distractor(self):
        """The f10 defect: a tolerance wide enough to reach a distractor
        silently disables the distractor check and passes the trap answer."""
        for q in BATTERY.questions:
            if q.grading_method != "numeric":
                continue
            entry = ANSWERS[q.id]
            truth = entry["ground_truth"]
            tol = float(q.grading.get("tolerance", 0))
            for bad in entry.get("reject_values") or []:
                assert abs(float(bad) - float(truth)) > tol, f"{q.id}: {bad} within {tol} of {truth}"

    def test_distractors_are_not_values_quoted_from_the_question(self):
        """A distractor that appears in the question fires on correct answers
        that restate the problem."""
        for q in BATTERY.questions:
            if q.grading_method != "numeric":
                continue
            in_question = {
                float(n.replace(",", ""))
                for n in re.findall(r"\d[\d,]*(?:\.\d+)?", q.text)
            }
            for bad in ANSWERS[q.id].get("reject_values") or []:
                assert float(bad) not in in_question, (
                    f"{q.id}: distractor {bad} appears in the question text"
                )


class TestQuarantine:
    def test_the_battery_file_contains_no_answer_value(self):
        """`gold_criterion` and the mode anchors state HOW correctness is
        decided and what SHAPE a correct response takes — which is what the
        specification is for. What they may not contain is the answer itself.

        Two operational choices, both found by this test failing:

        * Word-boundary matching, not substring. The first run flagged L04's
          accept string "nato" because "discriminator" and "combinatorics"
          contain it — a false positive that would have trained a reader to
          ignore the alarm.
        * Bare numbers excluded. It also flagged "1968", which is L05's
          DISTRACTOR value and simultaneously a cue inside L04's question text.
          A number cannot tell a leak from a coincidence, which is the same
          reason lab.battery.leak_probe_strings excludes short accept strings.

        Trap markers are checked separately below, because a `reject_premise`
        anchor cannot be written without describing a rejection.
        """
        raw = " ".join((BATTERY_DIR / "diagnostic_v1.yaml").read_text().split()).lower()
        leaks = []
        for qid in BY_ID:
            entry = ANSWERS.get(qid) or {}
            values = [entry.get("ground_truth")] + list(entry.get("accept") or []) \
                + list(entry.get("also_expect") or [])
            for value in values:
                if not isinstance(value, str):
                    continue
                token = " ".join(value.split()).lower()
                if len(token) < 4 or re.fullmatch(r"[\d\s,.-]+", token):
                    continue
                if re.search(rf"(?<![a-z]){re.escape(token)}(?![a-z])", raw):
                    leaks.append(f"{qid}: {value!r}")
        assert not leaks, "answer VALUES present in the battery file:\n  " + "\n  ".join(leaks)

    def test_no_specification_field_reaches_a_generated_packet(self):
        """The check that actually protects the experiment.

        The file-content test above is a discipline check. This is the
        structural one: build the real prompt for every item under every
        condition it runs, and assert no answer-key string survives into it.
        `build_prompt` reads `question.text` and nothing else, so no
        specification field can reach a solver — this proves it rather than
        asserting it.
        """
        from datetime import date

        from epistemic.registry import seed_registry
        from epistemic.router import route
        from lab.trials import Condition, build_prompt

        registry = seed_registry()
        probes = [s for s in ground_truth_strings({"answers": {k: ANSWERS[k] for k in BY_ID}})
                  if isinstance(s, str) and len(s) >= 12]
        leaks = []
        for q in BATTERY.questions:
            rt = route(q.text, asked_on=date(2026, 8, 28), registry=registry)
            for allow_search in (False, True):
                for inject in (False, True):
                    cond = Condition(
                        name="probe", agent="solver-closed",
                        inject_directive=inject, allow_search=allow_search,
                    )
                    prompt = " ".join(build_prompt(q, cond, rt, 3).split()).lower()
                    for s in probes:
                        if " ".join(s.split()).lower() in prompt:
                            leaks.append(f"{q.id}: {s[:60]!r}")
        assert not leaks, "answer-key text reached a packet:\n  " + "\n  ".join(sorted(set(leaks)))

    def test_the_answer_key_is_not_imported_by_prompt_building_code(self):
        """Checked on the import graph, not on the file text.

        The first version grepped trials.py for "load_answers" and failed on its
        own module docstring, which says the function is called by the grading
        path only. Prose about a rule is not a violation of it.
        """
        import ast

        tree = ast.parse((BATTERY_DIR.parent / "lab" / "trials.py").read_text())
        imported = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        }
        assert "load_answers" not in imported
        assert not any(
            isinstance(n, ast.Attribute) and n.attr == "load_answers" for n in ast.walk(tree)
        )


class TestTaskLabelsCarryInformation:
    def test_no_axis_is_just_claim_type_relabelled(self):
        """If an axis is one-to-one with claim type, grouping results by it is
        grouping by the treatment, and the mechanism gets confirmed by its own
        bookkeeping."""
        report = collinearity(
            [(q.id, q.task_labels, q.expected_claim_type) for q in BATTERY.questions]
        )
        determined = [a for a, r in report.items() if r["determined_by_claim_type"]]
        assert not determined, f"axes determined by claim_type: {determined}"

    def test_every_axis_actually_varies(self):
        for axis in AXES:
            values = {q.task_labels[axis] for q in BATTERY.questions}
            assert len(values) >= 2, f"{axis} takes one value across the battery; it explains nothing"

    def test_the_battery_exercises_every_response_mode(self):
        modes = {q.task_labels["correct_response_mode"] for q in BATTERY.questions}
        assert {"assert", "reject_premise", "estimate", "abstain"} <= modes


class TestTheSpecificationIsFrozen:
    def test_item_ids_are_unique_and_cell_prefixed(self):
        ids = [q.id for q in BATTERY.questions]
        assert len(ids) == len(set(ids))
        for q in BATTERY.questions:
            assert q.id.startswith(q.cell), f"{q.id} does not carry its cell"

    def test_the_declared_condition_set_is_closed(self):
        raw = yaml.safe_load((BATTERY_DIR / "diagnostic_v1.yaml").read_text())
        header = raw["description"] + (raw.get("notes") or "")
        assert header
        by_cell: dict[str, set[frozenset]] = {}
        for item in ITEMS:
            by_cell.setdefault(item["cell"], set()).add(frozenset(item["conditions"]))
        for cell, sets in by_cell.items():
            assert len(sets) == 1, (
                f"cell {cell} runs items under different condition sets, so its items "
                f"are not comparable within the cell"
            )


class TestTheRenderedSpecificationDocument:
    """`docs/DIAGNOSTIC_V1_SPECIFICATION.md` is generated, not written.

    A specification document maintained by hand alongside a battery file drifts
    from it, and the drift is invisible precisely when it matters — after the
    data exists and someone is reading the document to recall what was
    predicted.
    """

    DOC = BATTERY_DIR.parent / "docs" / "DIAGNOSTIC_V1_SPECIFICATION.md"

    def test_the_committed_document_is_not_stale(self):
        from lab.spec import render_specification

        expected = render_specification(BATTERY, ANSWERS) + "\n"
        assert self.DOC.exists(), "run `python -m lab spec diagnostic_v1 --write`"
        assert self.DOC.read_text() == expected, (
            "the committed specification does not match the battery. Regenerate it with "
            "`python -m lab spec diagnostic_v1 --write` — and if the battery changed after "
            "dispatch, that is a protocol amendment, not a rebuild."
        )

    def test_the_document_records_a_fingerprint(self):
        from lab.spec import battery_fingerprint

        assert f"`{battery_fingerprint(ITEMS)}`" in self.DOC.read_text()

    def test_the_document_carries_no_answer_value(self):
        raw = " ".join(self.DOC.read_text().split()).lower()
        leaks = []
        for qid in BY_ID:
            entry = ANSWERS.get(qid) or {}
            for value in [entry.get("ground_truth")] + list(entry.get("accept") or []):
                if not isinstance(value, str):
                    continue
                token = " ".join(value.split()).lower()
                if len(token) < 4 or re.fullmatch(r"[\d\s,.-]+", token):
                    continue
                if re.search(rf"(?<![a-z]){re.escape(token)}(?![a-z])", raw):
                    leaks.append(f"{qid}: {value!r}")
        assert not leaks, "answer values in the specification document:\n  " + "\n  ".join(leaks)

    def test_the_document_states_that_nothing_has_run_yet(self):
        assert "No solver dispatch has occurred" in self.DOC.read_text()

    def test_every_item_appears_with_its_tier(self):
        text = self.DOC.read_text()
        for q in BATTERY.questions:
            assert f"### {q.id} — " in text
        for tier in ("MEASUREMENT_VALIDITY", "DIAGNOSTIC", "PRIMARY"):
            assert tier in text
