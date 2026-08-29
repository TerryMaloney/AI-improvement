"""D′ as built, and the consistency audit across the nine §J changes.

Two jobs. First, assert that the design on disk is the design that was decided —
counts from the generated manifest, not from arithmetic, because the arithmetic
was wrong once already (500 trials instead of 388, from a global `repeats` that
could not express per-cell k). Second, check that the nine pre-registration
changes do not contradict one another or the constraints they were adopted under.
"""

from __future__ import annotations

import json
import pathlib
from datetime import date

import pytest
import yaml

from epistemic.registry import seed_registry
from lab.battery import load_battery
from lab.routing import agrees, intended_route, routed_route
from lab.trials import ExperimentConfig

REPO = pathlib.Path(__file__).resolve().parent.parent
BATTERY = load_battery("diagnostic_v1")
MANIFEST = json.loads((REPO / "runs" / "exp003a" / "manifest.json").read_text())
CONFIG = ExperimentConfig.load("exp003a_mechanism")
FROZEN = (REPO / "docs" / "EXP003A_FROZEN_DECISIONS.md").read_text()
PLAN = (REPO / "docs" / "EXP003_IMPLEMENTATION_PLAN.md").read_text()
AS_OF = date(2026, 8, 28)
_REG = seed_registry()

PLANNED_TRIALS = {"L": 120, "R": 100, "D": 60, "U": 60, "N": 36, "C": 12}


class TestTheManifestIsTheAuthority:
    def test_total_is_388_from_the_generated_manifest(self):
        assert MANIFEST["trial_count"] == 388 == sum(PLANNED_TRIALS.values())

    def test_per_cell_counts_match_the_plan(self):
        assert MANIFEST["by_cell"] == PLANNED_TRIALS

    def test_per_cell_replicates_are_expressible(self):
        """The bug this pins: a single global `repeats` silently produced 500
        trials, because plan §6 sets k=5 for L/R/D and k=3 for U/N/C."""
        assert CONFIG.repeats_by_cell == {"L": 5, "R": 5, "D": 5, "U": 3, "N": 3, "C": 3}

    def test_the_scout_exclusions_are_applied_and_reasoned(self):
        assert set(MANIFEST["excluded_items"]) == {"D01", "D02"}
        for reason in MANIFEST["excluded_items"].values():
            assert len(reason.split()) >= 10, "an exclusion must carry its reason"
        assert not [t for t in MANIFEST["trials"] if t["question_id"] in {"D01", "D02"}]

    def test_dispatch_count_exceeds_trial_count_because_of_the_multi_dispatch_arms(self):
        assert MANIFEST["dispatch_count"] > MANIFEST["trial_count"]
        multi = [t for t in MANIFEST["trials"] if t["dispatches"] > 1]
        assert {t["condition"] for t in multi} == {"search_selfcheck", "search_independent"}


class TestCellRIsCrossed:
    def test_cell_r_runs_five_arms(self):
        for q in BATTERY.by_cell("R"):
            assert q.spec["conditions"] == [
                "baseline", "placebo_routed", "placebo_intended",
                "directive_routed", "directive_intended",
            ]

    def test_routed_and_intended_prompts_actually_differ(self):
        by_item: dict[str, dict[str, str]] = {}
        for t in MANIFEST["trials"]:
            by_item.setdefault(t["question_id"], {})[t["condition"]] = t["prompt"]
        for q in BATTERY.by_cell("R"):
            arms = by_item[q.id]
            assert arms["directive_routed"] != arms["directive_intended"], q.id
            assert arms["placebo_routed"] != arms["placebo_intended"], q.id

    def test_each_placebo_is_matched_to_its_own_block(self):
        """Not to the other arm's block. The intended directive is 68 words
        shorter, so one placebo would leave one arm uncontrolled."""
        from lab.placebo import features

        for q in BATTERY.by_cell("R"):
            routed = routed_route(q.text, AS_OF, _REG).prompt_block()
            intended = intended_route(q.text, q.expected_claim_type, AS_OF, _REG).prompt_block()
            assert abs(len(routed.split()) - len(intended.split())) > 30, (
                f"{q.id}: the two blocks should differ substantially in length, or the "
                f"second placebo is unnecessary"
            )
            packets = {t["condition"]: t["prompt"] for t in MANIFEST["trials"]
                       if t["question_id"] == q.id}
            for arm, block in (("placebo_routed", routed), ("placebo_intended", intended)):
                pb = packets[arm].split("HANDLING GUIDANCE FOR THIS QUESTION")[1]
                pb = pb.split("THE QUESTION")[0]
                d, p = features(block), features(pb)
                assert abs(d["words"] - p["words"]) <= max(1, round(d["words"] * 0.10)), \
                    f"{q.id}/{arm}: word count not matched to its own block"
                assert d["bullets"] == p["bullets"], f"{q.id}/{arm}: bullets"

    def test_only_cell_r_is_crossed(self):
        crossed = {q.id for q in BATTERY.questions if q.spec["routing_disposition"] == "crossed"}
        assert crossed == {q.id for q in BATTERY.by_cell("R")}


class TestTheRouterIsExplicit:
    def test_every_trial_carries_both_claim_types_and_its_route_mode(self):
        for t in MANIFEST["trials"]:
            assert t["route_mode"] in ("routed", "intended")
            assert t["routed_claim_type"]
            assert t["intended_claim_type"]

    def test_an_agreeing_item_is_byte_identical_across_modes(self):
        """So a contrast on an agreeing item is exactly zero by construction,
        not by luck."""
        q = BATTERY.by_id("L01")
        assert agrees(q.text, q.expected_claim_type, AS_OF, _REG)
        assert routed_route(q.text, AS_OF, _REG).prompt_block() == \
               intended_route(q.text, q.expected_claim_type, AS_OF, _REG).prompt_block()

    def test_cell_n_is_labelled_theta_system_and_cannot_claim_theta_directive(self):
        for q in BATTERY.by_cell("N"):
            assert q.spec["estimand"] == ["theta_system"]
            assert "theta_directive" not in q.spec["estimand"]

    def test_inert_items_declare_no_route_dependent_arm(self):
        dependent = {"directive_only", "search_directive", "A_only",
                     "directive_routed", "directive_intended"}
        for q in BATTERY.questions:
            if q.spec["routing_disposition"] == "inert_no_directive_arm":
                assert not set(q.spec["conditions"]) & dependent, q.id


class TestRandomisation:
    def test_the_seed_is_recorded_in_the_experiment_identity(self):
        assert CONFIG.dispatch_seed == MANIFEST["dispatch_seed"] == 20260829

    def test_order_is_reproducible_from_the_frozen_configuration(self):
        import random

        ids = sorted(t["trial_id"] for t in MANIFEST["trials"])
        random.Random(MANIFEST["dispatch_seed"]).shuffle(ids)
        actual = [t["trial_id"] for t in
                  sorted(MANIFEST["trials"], key=lambda t: t["dispatch_position"])]
        assert ids == actual

    def test_order_is_not_the_same_as_preparation_order(self):
        """A shuffle that changed nothing would provide no protection."""
        actual = [t["trial_id"] for t in
                  sorted(MANIFEST["trials"], key=lambda t: t["dispatch_position"])]
        assert actual != sorted(actual)

    def test_the_manifest_says_what_is_randomised_and_what_is_not(self):
        text = MANIFEST["randomisation"]
        assert "order" in text.lower()
        assert "not randomised" in text.lower() or "NOT randomised" in text
        assert "no protection against confounding" in text


class TestKnowledgeProbeSeparation:
    def test_the_probe_has_its_own_config_and_is_screen_classed(self):
        probe = ExperimentConfig.load("exp003a_knowledge_probe")
        assert probe.id != CONFIG.id
        assert all(c.dispatch_class == "screen" for c in probe.conditions)
        assert [c.name for c in probe.conditions] == ["baseline"], \
            "a probe with a treatment arm could select items where the mechanism helps"

    def test_the_experiment_dispatches_its_own_baseline(self):
        """The probe's baseline may not be reused: it selects on baseline
        performance, so reusing it as the control biases every contrast."""
        baselines = [t for t in MANIFEST["trials"] if t["condition"] == "baseline"]
        assert baselines, "the experiment must dispatch its own baseline arm"

    def test_the_primary_manifest_contains_no_screening_trials(self):
        assert MANIFEST["dispatch_classes"] == ["solver_experiment"]

    def test_probe_artifact_if_present_is_screen_classed_and_uncontaminating(self):
        """Infrastructure invariant, not an experimental assertion.

        The original form of this test asserted the probe had not yet run. That
        was a workflow precondition, and it expired the moment the probe was
        dispatched and committed. What actually has to hold — before the probe,
        after the probe, and forever — is that screening observations never leak
        into a solver experiment. That is what is checked here. The probe
        artifact and every frozen grade are read only.
        """
        artifact = REPO / "runs" / "screens" / "knowledge_probe.json"
        if artifact.exists():
            probe = json.loads(artifact.read_text())
            assert probe["dispatch_class"] == "screen", \
                "a probe artifact that is not screen-classed could be mistaken for experimental data"
        assert not [t for t in MANIFEST["trials"] if t["dispatch_class"] == "screen"], \
            "no screening trial may appear in the production manifest"


class TestConsistencyAuditAcrossTheNineChanges:
    """The nine §J changes, checked against each other and against the
    constraints they were adopted under."""

    def test_j2_l05_reworded_and_now_routes_as_declared(self):
        q = BATTERY.by_id("L05")
        assert q.text.startswith("In what year")
        assert agrees(q.text, q.expected_claim_type, AS_OF, _REG)

    def test_j2_did_not_change_l05s_construct(self):
        q = BATTERY.by_id("L05")
        assert q.spec["task_labels"]["reasoning_depth"] == "lookup"
        assert q.grading_method == "numeric"
        assert q.spec["evidence_tier"] == "PRIMARY"

    def test_j3_no_cell_r_item_was_reworded(self):
        """The rewrites were rejected; the items must be unchanged."""
        assert "Calculate" not in BATTERY.by_id("R01").text
        assert "Compute" not in BATTERY.by_id("R04").text
        for q in BATTERY.by_cell("R"):
            assert q.spec["task_labels"]["reasoning_depth"] == "multi_step"

    def test_j4_the_covariate_is_withdrawn_not_merely_qualified(self):
        assert "The covariate is WITHDRAWN" in FROZEN
        assert "biased one" in FROZEN
        assert "longer responses caused the treatment effect" in FROZEN

    def test_j5_elaboration_only_is_defined_but_not_in_the_experiment(self):
        from lab.treatments import build_elaboration_only  # noqa: F401

        named = {c for q in BATTERY.questions for c in q.spec["conditions"]}
        assert "elaboration_only" not in named
        assert "elaboration_only" not in {c.name for c in CONFIG.conditions}
        assert "deferred to a follow-up experiment" in FROZEN

    def test_j6_the_old_power_claim_survives_only_as_a_quotation(self):
        """The superseded sentence is deliberately quoted so the amendment is
        auditable. What must not survive is the sentence asserted as live."""
        phrase = "powered to detect a mechanism that changes an"
        assert PLAN.count(phrase) == 1, "the old claim appears more than once"
        before = PLAN.split(phrase)[0]
        assert "SUPERSEDED (J6)" in before, "the surviving instance is not marked superseded"
        assert "That is false as a statistical claim" in PLAN

    def test_j6_the_replacement_separates_the_four_concepts(self):
        for required in (
            "Effect-size resolution", "Statistical significance", "Uncertainty",
            "Direction consistency", "Confirmatory versus descriptive",
        ):
            assert required in PLAN, required
        assert "p < 0.05** requires a shift of 0.8" in PLAN or \
               "p < 0.05 requires a shift of 0.8" in PLAN.replace("**", "")
        assert "cannot reach p < 0.05" in PLAN

    def test_j7_routing_accuracy_is_recorded_as_unmeasured(self):
        assert "not** an\nestimate of routing accuracy" in FROZEN or \
               "not an estimate of routing accuracy" in FROZEN.replace("**", "")

    def test_j8_c3_counts_are_recorded_and_independence_is_not_claimed(self):
        assert "25 (100%)" in FROZEN
        assert "establish **nothing** about independence" in FROZEN

    def test_j1_and_d_prime_agree_on_the_trial_count(self):
        assert "388 trials, verified from the\ngenerated manifest" in FROZEN

    def test_no_change_reintroduces_a_length_confound(self):
        """J1's two placebos exist precisely to stop this; J4's withdrawal must
        not be read as licence to ignore length entirely."""
        assert "68 words shorter" in FROZEN
        for q in BATTERY.by_cell("R"):
            assert {"placebo_routed", "placebo_intended"} <= set(q.spec["conditions"])

    def test_the_tier_wall_survived_every_change(self):
        for q in BATTERY.questions:
            if q.spec["evidence_tier"] == "PRIMARY":
                assert q.spec["outcome_type"] == "deterministic", q.id
                assert q.spec["length_sensitivity"] == "NONE", q.id

    def test_fd1_is_still_frozen_not_fixed(self):
        """D-prime added arms; it must not have quietly repaired the closed-book
        budget contradiction, which is part of the treatment as measured."""
        from epistemic.router import Route  # noqa: F401

        packets = [t["prompt"] for t in MANIFEST["trials"]
                   if t["condition"] == "directive_only"]
        assert packets
        assert any("SEARCH BUDGET" in p and "TOOLS: you have none" in p for p in packets)

    def test_fd13_discloses_the_confidence_asymmetry(self):
        assert "FD-13" in FROZEN
        assert "constructed" in FROZEN


def test_the_yaml_config_and_the_loaded_config_agree():
    raw = yaml.safe_load((REPO / "experiments" / "exp003a_mechanism.yaml").read_text())
    assert raw["dispatch_seed"] == CONFIG.dispatch_seed
    assert raw["use_item_conditions"] is True
    assert set(raw["exclude_items"]) == set(CONFIG.exclude_items)
    assert raw["runs_against"]["battery"] == BATTERY.id
