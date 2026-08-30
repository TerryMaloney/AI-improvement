"""Stage 0A-M candidate battery: structure, key quarantine, grading, schedule.

Nothing here dispatches. The grading tests exercise every authored key against
its own accepted phrasing and against the specific wrong answer the mechanism
predicts -- the current officeholder instead of the anchored one, the
alternative-definition quantity instead of the requested one. An item whose
displacing answer would grade as correct is a broken item, not a finding.
"""
from __future__ import annotations

import json
import pathlib

import pytest
import yaml

from lab.anchored_grading import grade, normalise

REPO = pathlib.Path(__file__).resolve().parent.parent
BATTERY = yaml.safe_load((REPO / "batteries" / "anchored_v1.yaml").read_text())
KEYS = yaml.safe_load((REPO / "batteries" / "answers.anchored_v1.yaml").read_text())["answers"]
MANIFEST = json.loads((REPO / "experiments" / "exp004_stage0am" / "manifest.json").read_text())
SCHEDULE = json.loads((REPO / "experiments" / "exp004_stage0am" / "schedule.json").read_text())
DIFF = json.loads((REPO / "experiments" / "exp004_stage0am" / "arm_packet_diff.json").read_text())
PROV = (REPO / "docs" / "EXP004_STAGE0A_M_KEY_PROVENANCE.md").read_text()
Q = BATTERY["questions"]


def by_class(c):
    return [q for q in Q if q["class"] == c]


class TestComposition:
    def test_exact_class_counts(self):
        assert len(by_class("date_anchored")) == 25
        assert len(by_class("definition_anchored")) == 25
        assert len(by_class("arithmetic_control")) == 15
        assert len(Q) == 65

    def test_manifest_counts_match_the_generated_battery(self):
        c = MANIFEST["counts"]
        assert c["date_anchored"] == len(by_class("date_anchored"))
        assert c["definition_anchored"] == len(by_class("definition_anchored"))
        assert c["arithmetic_control"] == len(by_class("arithmetic_control"))
        assert c["total_dispatches"] == len(Q) * 2 == 130

    def test_one_class_per_item_and_no_duplicate_ids_or_stems(self):
        assert len({q["id"] for q in Q}) == 65
        assert len({normalise(q["text"]) for q in Q}) == 65

    def test_control_is_outside_the_holm_family(self):
        assert MANIFEST["holm_family"] == ["date_anchored", "definition_anchored"]
        assert MANIFEST["outside_holm_family"] == ["arithmetic_control"]

    def test_every_item_declares_a_route_before_dispatch(self):
        assert all(q["grading_route"] in {"exact_entity", "numeric", "boolean"} for q in Q)


class TestKeyQuarantine:
    def test_no_item_stem_contains_its_own_answer(self):
        """Scoped per item, because a trial packet carries exactly one question.
        An answer appearing in a DIFFERENT item's stem is not a leak; an answer
        appearing in its own stem hands the solver the answer."""
        leaks = []
        for q in Q:
            stem = normalise(q["text"])
            for phrase in KEYS[q["id"]].get("accept", []):
                n = normalise(phrase)
                if len(n) >= 5 and n in stem:
                    leaks.append((q["id"], phrase))
        assert not leaks, f"stems containing their own answer: {leaks}"

    def test_no_stem_reveals_another_items_answer_within_the_same_class(self):
        """Weaker cross-item check, reported rather than fatal: two items in one
        class sharing an entity narrows the class's effective diversity."""
        overlaps = []
        for a in Q:
            for b in Q:
                if a["id"] >= b["id"] or a["class"] != b["class"]:
                    continue
                for phrase in KEYS[b["id"]].get("accept", []):
                    n = normalise(phrase)
                    if len(n) >= 5 and n in normalise(a["text"]):
                        overlaps.append((a["id"], b["id"], phrase))
        assert len(overlaps) <= 2, f"too many within-class entity overlaps: {overlaps}"

    def test_battery_file_carries_route_names_only(self):
        for q in Q:
            assert set(q) == {"id", "class", "subtype", "domain", "text", "grading_route"}

    def test_every_item_has_a_key(self):
        assert {q["id"] for q in Q} == set(KEYS)


class TestGradingEveryAuthoredKey:
    """Each key must accept its own answer and reject the displacing one."""

    @pytest.mark.parametrize("qid", [q["id"] for q in Q])
    def test_route_is_implementable_and_deterministic(self, qid):
        g = KEYS[qid]
        item = {"grading": g}
        if g["route"] == "exact_entity":
            assert grade(item, g["accept"][0])
        elif g["route"] == "numeric":
            assert grade(item, f"The answer is {g['value']}.")
        else:
            assert grade(item, "Yes." if g["expected"] else "No.")

    @pytest.mark.parametrize("qid", [q["id"] for q in Q])
    def test_the_predicted_wrong_answer_fails(self, qid):
        g = KEYS[qid]
        item = {"grading": g}
        if g["route"] == "exact_entity":
            for r in g.get("rejects", []):
                assert not grade(item, f"The answer is {r}."), f"{qid}: reject {r!r} graded correct"
        elif g["route"] == "numeric":
            for r in g.get("rejects", []):
                assert not grade(item, f"The answer is {r}."), f"{qid}: reject {r} graded correct"
        else:
            assert not grade(item, "No." if g["expected"] else "Yes.")

    @pytest.mark.parametrize("qid", [q["id"] for q in Q if KEYS[q["id"]]["route"] == "exact_entity"])
    def test_capitalisation_and_punctuation_are_harmless(self, qid):
        g = KEYS[qid]
        a = g["accept"][0]
        assert grade({"grading": g}, f"  {a.upper()}!  ")
        assert grade({"grading": g}, f"It was {a.lower()}, I believe.")

    def test_lexical_exactness_does_not_masquerade_as_correctness(self):
        """A response naming the displacing state must fail even when it also
        mentions the accepted one -- 'X, not Y' and 'Y, not X' must differ."""
        g = KEYS["a01"]
        assert grade({"grading": g}, "Angela Merkel.")
        assert not grade({"grading": g}, "Olaf Scholz, who succeeded Angela Merkel.")

    def test_numeric_tolerance_separates_accept_from_reject(self):
        for qid, g in KEYS.items():
            if g["route"] != "numeric":
                continue
            for r in g.get("rejects", []):
                assert abs(g["value"] - r) > g["tolerance"], \
                    f"{qid}: tolerance {g['tolerance']} overlaps reject {r}"


class TestProvenance:
    @pytest.mark.parametrize("qid", [q["id"] for q in Q if q["class"] != "arithmetic_control"])
    def test_every_primary_item_has_a_provenance_record(self, qid):
        assert f"### {qid} —" in PROV

    def test_verification_status_is_recorded_per_item(self):
        allowed = {"VERIFIED_WEB_2026-08-30", "PENDING_INDEPENDENT_VERIFICATION", "COMPUTED_IN_SESSION"}
        assert {i["verification"] for i in MANIFEST["items"]} <= allowed

    def test_pending_items_are_not_production_eligible(self):
        for i in MANIFEST["items"]:
            if i["verification"] == "PENDING_INDEPENDENT_VERIFICATION":
                assert i["production_eligible"] is False


class TestDispatchSchedule:
    def test_every_item_appears_exactly_once(self):
        assert sorted(s["item_id"] for s in SCHEDULE["schedule"]) == sorted(q["id"] for q in Q)

    def test_no_class_is_dispatched_as_a_contiguous_block(self):
        cls = {q["id"]: q["class"] for q in Q}
        seq = [cls[s["item_id"]] for s in SCHEDULE["schedule"]]
        longest, run = 1, 1
        for a, b in zip(seq, seq[1:]):
            run = run + 1 if a == b else 1
            longest = max(longest, run)
        assert longest <= 4, f"a class ran {longest} positions contiguously"

    def test_the_control_is_spread_across_the_run_not_dumped_at_one_end(self):
        cls = {q["id"]: q["class"] for q in Q}
        pos = [s["position"] for s in SCHEDULE["schedule"] if cls[s["item_id"]] == "arithmetic_control"]
        assert min(pos) < 15 and max(pos) > 50

    def test_arm_order_is_randomised_not_fixed(self):
        firsts = [s["arm_first"] for s in SCHEDULE["schedule"]]
        assert 0.25 < firsts.count("closed") / len(firsts) < 0.75
        assert len(set(firsts)) == 2

    def test_both_arms_are_present_and_adjacent_for_every_item(self):
        for s in SCHEDULE["schedule"]:
            assert {s["arm_first"], s["arm_second"]} == {"closed", "retrieval_enabled"}

    def test_seeds_are_recorded_so_the_schedule_is_reproducible(self):
        assert isinstance(SCHEDULE["item_order_seed"], int)
        assert isinstance(SCHEDULE["arm_order_seed"], int)
        assert SCHEDULE["generated_before_any_outcome"] is True


class TestArmPackets:
    def test_arms_differ_only_by_the_retrieval_permission(self):
        assert DIFF["identical_apart_from_treatment"] is True
        assert DIFF["differing_line_count"] <= 4

    def test_closed_arm_has_no_phantom_search_budget(self):
        assert DIFF["closed_arm_phantom_budget_terms_found"] == []

    def test_no_arm_label_cues_the_solver(self):
        assert DIFF["no_arm_label_visible_to_solver"] is True

    def test_stem_placeholder_is_identical_in_both_arms(self):
        assert DIFF["stem_placeholder_identical"] is True


class TestNoTreatmentExposure:
    def test_manifest_asserts_zero_exposure(self):
        assert "NONE" in MANIFEST["treatment_exposure"]
        assert "NOT FROZEN" in MANIFEST["status"]

    def test_no_run_directory_exists_for_this_experiment(self):
        assert not (REPO / "runs" / "exp004_stage0am").exists(), \
            "a run directory implies dispatch; none may exist before execution authorisation"
