"""Screens, scout, treatments and preflight — the hardening layer.

The property under test throughout is that these things FAIL CLOSED. A screen
that passes when it has not run, a scout that assumes a cooperative search space,
a treatment that is only a label, or a preflight that reports readiness it has
not established — each is worse than not having the check at all, because each
produces the reassurance without the check.
"""

from __future__ import annotations

from datetime import date

import pytest

from epistemic.registry import seed_registry
from epistemic.router import route
from lab.battery import load_battery
from lab.placebo import features, match_report
from lab.screens import (
    CEILING,
    EXCLUDE,
    FLOOR,
    KEEP,
    NOT_SCREENED,
    cell_power,
    consistency_threshold,
    knowledge_screen,
    power_statement,
    routing_screen,
)
from lab.scout import excluded_items, load_scout
from lab.states import RetrievalState, load_egress
from lab.treatments import (
    DISPATCH_COUNT,
    MULTI_DISPATCH,
    build_a_only,
    build_elaboration_only,
    describe,
    dispatch_count,
    framing_sentence,
    freeze_fingerprint,
    is_verification,
)

BATTERY = load_battery("diagnostic_v1")
AS_OF = date(2026, 8, 28)
EGRESS = load_egress()


def _route(q):
    return route(q.text, asked_on=AS_OF, registry=seed_registry())


class TestScreensFailClosed:
    def test_the_knowledge_screen_reports_not_screened_without_a_probe(self):
        """"Not yet checked" must never render as "fine"."""
        results = knowledge_screen(BATTERY, probe=None)
        assert {r.decision for r in results} == {NOT_SCREENED}
        assert len(results) == len(BATTERY.questions)

    def test_the_knowledge_screen_thresholds_are_fixed_before_any_result(self):
        assert (FLOOR, CEILING) == (0.10, 0.90)

    def test_ceiling_and_floor_both_exclude(self):
        probe = {q.id: 0.5 for q in BATTERY.questions}
        probe["L01"], probe["L02"] = 0.95, 0.05
        by_id = {r.item_id: r for r in knowledge_screen(BATTERY, probe)}
        assert by_id["L01"].decision == EXCLUDE and "ceiling" in by_id["L01"].reason
        assert by_id["L02"].decision == EXCLUDE and "floor" in by_id["L02"].reason
        assert by_id["L03"].decision == KEEP

    def test_an_item_missing_from_the_probe_is_not_screened_rather_than_kept(self):
        probe = {q.id: 0.5 for q in BATTERY.questions if q.id != "R01"}
        by_id = {r.item_id: r for r in knowledge_screen(BATTERY, probe)}
        assert by_id["R01"].decision == NOT_SCREENED


class TestRoutingScreen:
    def test_it_runs_without_any_solver(self):
        results = routing_screen(BATTERY)
        assert len(results) == len(BATTERY.questions)

    def test_it_detects_the_known_misroutes(self):
        """FD-12. Recorded as a test so a classifier change that silently fixes
        or worsens this is visible rather than absorbed."""
        bad = {r.item_id for r in routing_screen(BATTERY) if r.decision == EXCLUDE}
        assert {"R01", "R02", "R03", "R04"} <= bad, "cell R must still be flagged"
        assert {"L05", "D04", "C02"} <= bad, "the superlative misroutes must still be flagged"
        assert len(bad) == 10

    def test_a_misroute_reason_names_the_directive_that_would_be_delivered(self):
        r = next(x for x in routing_screen(BATTERY) if x.item_id == "R01")
        assert "DETERMINISTIC" in r.reason and "EMPIRICAL" in r.reason
        assert r.detail["confidence"] > 0


class TestPowerIsRecomputedNotInherited:
    def test_consistency_needs_at_least_two_items(self):
        assert consistency_threshold(1) is None, "one item moving is an item, not a direction"
        assert consistency_threshold(2) == 2
        assert consistency_threshold(6) == 3

    def test_a_reduced_cell_says_so_and_states_the_new_requirement(self):
        p = cell_power("D", surviving=3, conditions=4)
        assert p.verdict == "REDUCED"
        assert p.consistency_required == 2
        assert "rather than" in p.note

    def test_an_empty_cell_is_dead_not_a_null(self):
        p = cell_power("R", surviving=0, conditions=3)
        assert p.verdict == "DEAD"
        assert "untested, not refuted" in p.note

    def test_a_single_item_cell_cannot_claim_a_direction(self):
        p = cell_power("C", surviving=1, conditions=2)
        assert p.verdict == "SINGLE-ITEM" and p.consistency_required is None

    def test_exclusions_change_the_trial_count(self):
        conds = {c: len(BATTERY.by_cell(c)[0].spec["conditions"]) for c in "LRDUNC"}
        full = power_statement(BATTERY, set(), conds)
        cut = power_statement(BATTERY, {"D01", "D02"}, conds)
        assert cut["total_solver_trials"] < full["total_solver_trials"]
        assert "no longer exists" in cut["warning"]
        assert "stands as written" in full["warning"]


class TestTheFrozenScout:
    def test_a_missing_scout_refuses_rather_than_assuming(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="cannot be planned"):
            load_scout(tmp_path / "absent.json")

    def test_the_committed_scout_covers_every_cell_d_item(self):
        scout = load_scout()
        assert {r["item_id"] for r in scout["results"]} == {q.id for q in BATTERY.by_cell("D")}

    def test_each_result_quotes_the_criterion_it_was_judged_against(self):
        for r in load_scout()["results"]:
            assert r["criterion"], f"{r['item_id']}: no pre-registered criterion recorded"
            assert len(r["observation"].split()) >= 20

    def test_the_scout_used_the_frozen_loaded_query(self):
        by_id = {r["item_id"]: r for r in load_scout()["results"]}
        for q in BATTERY.by_cell("D"):
            assert by_id[q.id]["query"] == q.spec["scout_queries"]["loaded"]

    def test_items_whose_search_space_corrects_are_excluded(self):
        assert excluded_items(load_scout()) == {"D01", "D02"}

    def test_every_cell_d_item_has_a_frozen_neutral_topic(self):
        """`search_independent`'s blindness is only real if the gatherer gets a
        neutral string instead of the question — every cell-D question contains
        its own false premise."""
        for q in BATTERY.by_cell("D"):
            neutral = q.spec["scout_queries"]["neutral"]
            assert neutral and neutral != q.text
            assert neutral.lower() != q.spec["scout_queries"]["loaded"].lower()


class TestTreatmentsAreDefinedNotLabelled:
    def test_every_condition_the_battery_names_has_a_dispatch_cost(self):
        named = {c for q in BATTERY.questions for c in q.spec["conditions"]}
        assert named <= set(DISPATCH_COUNT)

    def test_an_undeclared_condition_raises_rather_than_defaulting_to_one(self):
        with pytest.raises(KeyError, match="dispatch cost is not declared"):
            dispatch_count("some_new_arm")

    def test_multi_dispatch_arms_cost_more_than_one(self):
        assert dispatch_count("search_selfcheck") == 2
        assert dispatch_count("search_independent") == 3
        assert all(dispatch_count(c) >= 2 for c in MULTI_DISPATCH)

    def test_no_arm_is_called_verification_in_this_environment(self):
        for cond in ("search_only", "search_selfcheck", "search_independent"):
            assert is_verification(cond, EGRESS) is False
            assert "NOT verification" in describe(cond, EGRESS).licensed_wording

    def test_verification_is_judged_by_the_formal_definition_not_by_intent(self):
        """If egress opened, `search_independent` could satisfy it; the answer
        is computed from the environment, not from the arm's name."""
        from lab.states import EgressStatus

        full = EgressStatus(web_search=True, web_fetch=True)
        assert is_verification("search_independent", full) is True
        assert is_verification("search_selfcheck", full) is False

    def test_multi_dispatch_arms_never_claim_source_access(self):
        for cond in MULTI_DISPATCH:
            assert describe(cond, EGRESS).reaches != RetrievalState.SOURCE_ACCESS


class TestAOnlyIsLengthMatched:
    @pytest.mark.parametrize("qid", [q.id for q in BATTERY.questions])
    def test_a_only_matches_the_directive_on_every_measurable_axis(self, qid):
        q = BATTERY.by_id(qid)
        rt = _route(q)
        block, a = rt.prompt_block(), build_a_only(rt, q.text)
        d, p = features(block), features(a)
        assert abs(d["words"] - p["words"]) <= max(1, round(d["words"] * 0.10))
        assert d["bullets"] == p["bullets"]
        assert d["section_headers"] == p["section_headers"]
        assert (d["em_dashes"], d["paragraph_blocks"]) == (p["em_dashes"], p["paragraph_blocks"])

    def test_a_only_carries_the_real_framing_sentence(self):
        q = BATTERY.by_id("L01")
        rt = _route(q)
        assert framing_sentence(rt.claim_type) in build_a_only(rt, q.text)

    @pytest.mark.parametrize("qid", [q.id for q in BATTERY.questions])
    def test_a_only_reuses_the_placebo_carrier_almost_verbatim(self, qid):
        """The contrast `A_only` − `directive_placebo` should be the epistemic
        framing, not the framing plus a reshuffle of inert prose.

        The first version of this test asserted two differing lines and found
        EIGHT: pinning the lead changed the length budget, so the solver picked
        different variants for every carrier bullet. The generator was fixed
        rather than the assertion. Four slots stay free — header, lead, last
        bullet, closing — because the length and em-dash budgets have to land
        somewhere, and a framing sentence with no em dash where the placebo's
        lead had one leaves a deficit the closing alone cannot always cover.
        """
        from lab.placebo import build as build_placebo

        q = BATTERY.by_id(qid)
        rt = _route(q)
        placebo = build_placebo(rt.prompt_block(), q.text).split("\n")
        a = build_a_only(rt, q.text).split("\n")
        differing = [i for i, (x, y) in enumerate(zip(placebo, a)) if x != y]
        assert len(differing) <= 4, f"{qid}: {len(differing)} lines differ"
        bullets = [i for i, line in enumerate(placebo) if line.startswith("- ")]
        shared = [i for i in bullets[:-1] if i in differing]
        assert not shared, f"{qid}: bullets other than the last differ: {shared}"

    def test_a_only_is_not_inert_and_the_placebo_still_is(self):
        q = BATTERY.by_id("L01")
        rt = _route(q)
        from lab.placebo import build as build_placebo

        assert match_report(rt.prompt_block(), build_placebo(rt.prompt_block(), q.text))["ok"]
        # A_only deliberately carries mechanism vocabulary; the placebo checker
        # is the wrong tool for it and would fail, which is the point.
        assert match_report(rt.prompt_block(), build_a_only(rt, q.text))["forbidden_terms_present"]

    def test_the_compute_control_is_defined_and_matched_but_not_adopted(self):
        """FD-11: the text exists so adopting it is a config change, and it is
        deliberately absent from the battery so the decision stays open."""
        q = BATTERY.by_id("R01")
        rt = _route(q)
        e = build_elaboration_only(rt, q.text)
        assert abs(len(rt.prompt_block().split()) - len(e.split())) <= 5
        named = {c for qq in BATTERY.questions for c in qq.spec["conditions"]}
        assert "elaboration_only" not in named


class TestFreezeFingerprints:
    def test_the_treatment_fingerprint_is_recorded(self):
        import pathlib

        doc = pathlib.Path("docs/EXP003A_FROZEN_DECISIONS.md").read_text()
        assert f"TREATMENT_FREEZE: {freeze_fingerprint()}" in doc

    def test_changing_a_treatment_changes_the_fingerprint(self, monkeypatch):
        import lab.treatments as t

        before = t.freeze_fingerprint()
        monkeypatch.setitem(t.FROZEN_TEXTS, "SELFCHECK_REVIEW_PROMPT", "different")
        assert t.freeze_fingerprint() != before


class TestPreflightFailsClosed:
    def test_it_answers_the_binary_question(self):
        from lab.preflight import run

        r = run()
        assert r["question"].startswith("CAN THE EXPERIMENT RUN")
        assert r["answer"] in ("YES", "NO")
        assert r["runnable"] is (r["answer"] == "YES")

    def test_runnable_is_the_conjunction_of_every_check(self):
        from lab.preflight import run

        r = run()
        assert r["runnable"] == all(c["status"] == "PASS" for c in r["checks"])

    def test_it_covers_every_required_area(self):
        from lab.preflight import run

        ids = {c["id"] for c in run()["checks"]}
        required = {
            "battery_schema", "required_fields", "tier_compliance", "outcome_types",
            "length_sensitivity", "expected_retrieval_states", "retrieval_reproducibility",
            "ground_truth", "answer_leak", "treatment_definitions", "treatment_freeze",
            "scoring_freeze", "judge_config", "telemetry", "cost_accounting",
            "dispatch_accounting", "determinism", "experiment_identity",
            "prep_dispatch_separation", "no_solver_contamination", "git_identity",
            "screens_complete", "routing_consistency", "power_recomputed",
            "mechanism_confounds",
        }
        assert required <= ids, f"preflight missing: {sorted(required - ids)}"

    def test_every_failing_check_says_what_must_change(self):
        from lab.preflight import run

        for c in run()["blockers"]:
            assert c["fix"], f"{c['id']}: a blocker without a fix is a complaint"
            assert len(c["fix"].split()) >= 5

    def test_it_currently_says_no(self):
        """Recorded deliberately. The experiment is NOT runnable, and a test
        that would start failing the moment it becomes runnable is the honest
        way to notice that the blockers were cleared."""
        from lab.preflight import run

        r = run()
        assert r["answer"] == "NO"
        ids = {c["id"] for c in r["blockers"]}
        assert "screens_complete" in ids
        assert "routing_consistency" in ids

    def test_a_check_that_errors_counts_against_the_verdict(self):
        from lab.preflight import Check, ERROR

        assert Check("x", "q", ERROR, "boom").ok is False

    def test_no_solver_results_exist(self):
        from lab.preflight import run

        c = next(c for c in run()["checks"] if c["id"] == "no_solver_contamination")
        assert c["status"] == "PASS"
