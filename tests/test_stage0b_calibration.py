"""Stage 0B pre-calibration reconciliation — the derivations, pinned.

Every number this suite pins is one a later session could otherwise re-invent
after seeing calibration outcomes. That is the failure these tests exist to make
impossible: a threshold that moves once data exists is not a threshold.
"""
from __future__ import annotations

from fractions import Fraction

import pytest

from lab import stage0b_calibration as cal
from lab import stage0b_adjudication as adj
from lab.stage0b_cvd import CvDScenario, authorize
from lab.stage0b_power import RECOMMENDED_N_CONTROL, Scenario, analyse_scenario


# --------------------------------------------------------------------------- #
class TestTheBinomialBoundsAgreeWithTheFrozenImplementation:
    """The calibration module reuses Stage 0A-M's exact Clopper-Pearson limit
    rather than growing a second one that can drift from it."""

    def test_the_clean_upper_bound_reproduces_the_stage0am_published_numbers(self):
        # 0 of 15 -> 0.181 is the arithmetic_control bound in the independent review;
        # 0 of 25 -> 0.113 is Stage 0A-M's availability harm bound.
        assert round(cal.cp_upper(0, 15), 3) == 0.181
        assert round(cal.cp_upper(0, 25), 3) == 0.113

    def test_the_lower_bound_is_the_reflected_upper_bound(self):
        for k, n in ((0, 20), (1, 30), (5, 40), (29, 30)):
            assert cal.cp_lower(k, n) == pytest.approx(1.0 - cal.cp_upper(n - k, n))

    def test_the_closed_form_n_agrees_with_scanning_the_exact_bound(self):
        for target in (0.20, 0.15, 0.113, 0.10, 0.08, 0.05):
            n = cal.n_clean_for_upper_bound(target)
            assert cal.cp_upper(0, n) < target
            assert cal.cp_upper(0, n - 1) >= target


# --------------------------------------------------------------------------- #
class TestTheNegativeControlCountIsDerivedNotChosen:
    """15 and 20 were both in the repository; neither came from what the control
    has to establish."""

    def test_the_primary_cannot_reject_below_a_harm_rate_of_one_in_ten_at_n50(self):
        # one-sided exact floor at alpha=0.05 is D=5, and 5/50 = 0.10
        assert cal.minimum_rejectable_harm_rate(50) == pytest.approx(0.10)
        assert cal.minimum_rejectable_harm_rate(50, Fraction(1, 40)) == pytest.approx(0.12)

    def test_neither_superseded_value_clears_the_threshold_it_had_to_clear(self):
        thr = cal.minimum_rejectable_harm_rate(50)
        assert cal.cp_upper(0, 15) > thr        # the power module's carryover
        assert cal.cp_upper(0, 20) > thr        # the authoring protocol's 15+5

    def test_the_derived_minimum_is_29_and_the_recommendation_is_30(self):
        d = cal.negative_control_n(50)
        assert d["n_control_required"] == 29
        assert d["n_control_recommended"] == 30
        assert d["composition"] == {"reused_arithmetic_control": 15, "fresh": 15}
        assert d["bound_at_that_n_if_clean"] < cal.minimum_rejectable_harm_rate(50)

    def test_the_power_module_now_carries_the_derived_value(self):
        assert RECOMMENDED_N_CONTROL == cal.negative_control_n(50)["n_control_recommended"]

    def test_the_control_count_tracks_the_primary_count_rather_than_being_a_constant(self):
        # If power re-derivation raises the primary n, the rule raises the control n
        # too, because the rate it must beat is 5/n_primary.
        assert (cal.negative_control_n(90)["n_control_required"]
                > cal.negative_control_n(50)["n_control_required"])

    def test_the_brittleness_is_declared_rather_than_bought_off(self):
        d = cal.negative_control_n(50)
        assert d["bound_if_one_harm"] > cal.minimum_rejectable_harm_rate(50)
        assert "reported with the generic exposure tax explicitly not excluded" \
            in d["brittleness_declared"]


# --------------------------------------------------------------------------- #
class TestTheGraderBoundIsTheThingThatSizesTheRun:
    """The load-bearing finding: calibration cannot certify the grader for n=50,
    so production is sized AT the achievable bound."""

    def test_asymmetric_grader_error_is_far_more_destructive_than_symmetric(self):
        base = dict(p=0.95, u=1.0, q_exposure=0.50, delta=0.30)
        a05 = Fraction(1, 20)
        one = analyse_scenario(Scenario("one", g_one=0.08, **base), 50, a05)["power"]
        both = analyse_scenario(Scenario("both", g_both=0.08, **base), 50, a05)["power"]
        assert one < 0.65 < both

    def test_holding_power_at_n50_needs_a_g_one_no_calibration_bank_can_certify(self):
        assert cal.required_production_n(0.95, 0.50, 0.014) == 50
        assert cal.required_production_n(0.95, 0.50, 0.020) > 50
        assert cal.n_clean_for_upper_bound(0.014) > 200

    def test_the_recorded_sensitivity_table_matches_a_live_recomputation(self):
        """Every entry cheap enough to re-derive is re-derived. The low-q_C rows
        need a scan to n=400 whose unreachable cases cost ~60s, so they are
        recorded with provenance rather than recomputed on every report."""
        for q, recorded in cal.Q_C_SENSITIVITY_AT_PERFECT_GRADER.items():
            if recorded is None or recorded > cal.N_PROD_VIABLE_CAP:
                continue
            assert cal.required_production_n(0.95, q, 0.0) == recorded, q

    def test_the_pass_bound_is_the_loosest_one_that_stays_inside_the_affordable_cap(self):
        n_at_bound = cal.required_production_n(0.95, 0.50, cal.G_ONE_BOUND_FOR_PASS)
        assert n_at_bound <= cal.N_PROD_AFFORDABLE_CAP
        assert cal.required_production_n(0.95, 0.50, 0.10) > n_at_bound

    def test_sizing_uses_the_upper_bound_for_the_instrument_and_the_point_for_the_environment(self):
        ns = [cal.required_production_n(0.95, 0.50, g) for g in (0.0, 0.02, 0.05, 0.08)]
        assert ns == sorted(ns)


class TestTheGraderBoundSamplingUnitIsTheItem:
    """ISSUE 1. Pooling (A,C) with (A,D) counted one shared closed-arm verdict
    twice and bounded the wrong estimand. Both defects are pinned here."""

    def test_the_two_pairs_share_the_closed_arm_verdict_completely(self):
        # A single closed-arm defect, with both exposed arms clean, is ONE event
        # about the A/C pair -- not two.
        r = _scored("cal001", "grader_validation_holdout",
                    closed=("CORRECT", "INCORRECT"))
        assert cal.ac_pair_defect(r) == (True, False)
        assert cal.ad_pair_defect(r) == (True, False)
        # ... and only the A/C one is counted.
        st = cal.calibration_statistics([r])
        assert st["grader"]["observations"] == 1
        assert st["grader"]["k_g_one"] == 1

    def test_one_item_contributes_exactly_one_observation(self):
        rows = [_scored(f"cal{i:03d}", "grader_validation_holdout") for i in range(24)]
        st = cal.calibration_statistics(rows)
        assert st["grader"]["observations"] == 24
        assert st["grader"]["g_one_upper_95"] == round(cal.cp_upper(0, 24), 4)

    def test_the_invalid_pooling_claimed_a_bound_the_evidence_does_not_support(self):
        valid, invalid = cal.cp_upper(0, 24), cal.cp_upper(0, 48)
        assert invalid < valid            # anti-conservative, the dangerous direction
        assert cal.required_production_n(0.95, 0.50, invalid) < \
            cal.required_production_n(0.95, 0.50, valid)

    def test_the_A_D_pair_is_a_diagnostic_and_enters_no_bound(self):
        clean_c = _scored("cal001", "grader_validation_holdout",
                          d=("CORRECT", "INCORRECT"))
        st = cal.calibration_statistics([clean_c])
        assert st["grader"]["k_g_one"] == 0                       # bound untouched
        assert st["grader"]["arm_D_diagnostic"]["k_g_one_on_AD_pairs"] == 1

    def test_the_union_companion_is_conservative_and_never_the_headline(self):
        rows = [_scored(f"cal{i:03d}", "grader_validation_holdout",
                        d=("CORRECT", "INCORRECT") if i < 3 else ("CORRECT", "CORRECT"))
                for i in range(24)]
        st = cal.calibration_statistics(rows)
        comp = st["grader"]["conservative_companion"]
        assert comp["k_item_union"] == 3 and st["grader"]["k_g_one"] == 0
        assert comp["g_one_union_upper_95"] > st["grader"]["g_one_upper_95"]

    def test_the_batch_1_holdout_can_actually_reach_the_pass_threshold(self):
        # The defect that mattered: at the old 24-item holdout a PERFECT result
        # bounded g_one at 0.117, above the 0.08 PASS threshold. Batch 1 could not
        # have passed.
        assert cal.cp_upper(0, 24) > cal.G_ONE_BOUND_FOR_PASS
        assert cal.cp_upper(0, cal.BATCH1_HOLDOUT) <= cal.G_ONE_BOUND_FOR_PASS
        # The aggregate bound needs 36. The holdout is larger because a SECOND
        # constraint now binds: the per-route floor, with the smallest route at
        # weight 0.25, forces 4 x 14 = 56. Both must hold; the floor is the tighter.
        assert cal.n_clean_for_upper_bound(cal.G_ONE_BOUND_FOR_PASS) == 36
        assert cal.BATCH1_HOLDOUT == round(
            cal.MIN_HOLDOUT_ITEMS_PER_ROUTE / min(cal.PRODUCTION_ROUTE_MIX.values()))
        assert cal.BATCH1_HOLDOUT > cal.n_clean_for_upper_bound(cal.G_ONE_BOUND_FOR_PASS)

    def test_the_statistics_declare_their_sampling_unit(self):
        st = cal.calibration_statistics([_scored("cal001", "grader_validation_holdout")])
        assert "ITEM" in st["sampling_unit"]
        assert st["grader"]["unit"] == "item"


class TestTheOldMultiplierIsReplacedRatherThanRestated:

    def test_the_derived_cap_costs_less_than_the_multiplier_would_have(self):
        plan = cal.calibration_plan()
        assert plan["batch_1"]["screen_passing_items"] == cal.BATCH1_TARGET_SCREENED
        assert plan["maximum"]["screen_passing_items"] == cal.MAX_CALIBRATION_SCREENED
        w = plan["why_not_the_old_multiplier"]["it_is_wrong_in_both_directions"]
        assert plan["maximum"]["total_cost_usd"] < w["too_large_under_the_realized_structure"][
            "total_cost_usd"]

    def test_the_multiplier_would_have_cost_more_than_the_run_it_protected(self):
        w = cal.calibration_plan()["why_not_the_old_multiplier"][
            "it_is_wrong_in_both_directions"]
        assert (w["too_large_under_the_realized_structure"]["total_cost_usd"]
                > w["production_run_for_comparison"]["total_cost_usd"])

    def test_the_multiplier_is_also_too_small_for_what_it_had_to_measure(self):
        w = cal.calibration_plan()["why_not_the_old_multiplier"][
            "it_is_wrong_in_both_directions"]["too_small_for_what_it_had_to_measure"]
        assert "CLOSED-BOOK ONLY" in w and "no q_C" in w

    def test_the_old_rule_is_recorded_as_underived_rather_than_deleted(self):
        assert "NONE" in cal.calibration_plan()["why_not_the_old_multiplier"][
            "old_rule_derivation"]

    def test_the_cap_is_where_calibration_costs_about_what_production_costs(self):
        mx = cal.calibration_plan()["maximum"]["total_cost_usd"]
        prod = (cal.required_production_n(0.95, 0.50, cal.G_ONE_BOUND_FOR_PASS)
                + cal.negative_control_n(72)["n_control_recommended"]) * cal.COST_PRODUCTION_ITEM
        assert 0.6 < mx / prod < 1.4


# --------------------------------------------------------------------------- #
class TestTheDispatchStructureIsMinimalAndScreenedFirst:

    def test_the_screen_runs_on_every_authored_item_and_the_rest_only_on_passers(self):
        ds = cal.dispatch_structure()
        assert [d["dispatch"] for d in ds["stage_1_every_authored_item"]] \
            == ["D fixed-query search"]
        assert len(ds["stage_2_screen_passing_items_only"]) == 6

    def test_no_exposed_answerer_is_bought_by_the_exposure_estimate(self):
        assert "measured on the BLOCK, before any answerer" in cal.dispatch_structure()[
            "deliberately_absent"][
            "an exposed answerer run only to estimate exposure divergence"]

    def test_delta_is_not_measured_in_calibration(self):
        assert "PREREGISTERED" in cal.PARAMETER_GLOSSARY["delta"]["status"]
        assert cal.DELTA_PREREGISTERED == 0.30

    def test_every_cost_used_in_the_plan_is_a_measured_stage0b_dispatch(self):
        for c in (cal.COST_QUERY_WRITER, cal.COST_SEARCH, cal.COST_EXPOSED_ANSWERER):
            assert 0.005 < c < 0.20


# --------------------------------------------------------------------------- #
class TestTheParametersNameWhatCrossesTheBoundary:

    def test_q_C_is_defined_on_the_synthesised_summary_not_on_retrieved_content(self):
        g = cal.PARAMETER_GLOSSARY["q_C"]
        assert "RUNTIME-SYNTHESISED SUMMARY" in g["definition"]
        assert "c_disp" in g["replaces"]

    def test_the_fixed_query_rate_may_not_stand_in_for_the_model_query_rate(self):
        assert "different queries producing" in \
            cal.PARAMETER_GLOSSARY["q_C"]["why_it_cannot_be_taken_from_arm_D"]

    def test_the_screen_does_not_pin_arm_D_exposure_at_one(self):
        assert "q_D" not in cal.PARAMETER_GLOSSARY
        g = cal.PARAMETER_GLOSSARY["r_D"]
        assert "THAT WAS FALSE" in g["replaces"]
        assert "not the injected block" in g["replaces"]

    def test_the_cvd_scenario_refuses_to_default_arm_D_exposure(self):
        with pytest.raises(TypeError):
            CvDScenario.from_exposure(p=0.95, q_C=0.50)
        s = CvDScenario.from_exposure(p=0.95, q_C=0.50, r_D=0.80)
        assert s.delta_D == pytest.approx(0.80 * cal.DELTA_PREREGISTERED)

    def test_a_nondivergent_reexecution_is_the_measurement_not_a_failure(self):
        assert "not a failure" in \
            cal.PARAMETER_GLOSSARY["r_D"]["a_nondivergent_reexecution_is_not_a_failure"] \
            or "measurement" in \
            cal.PARAMETER_GLOSSARY["r_D"]["a_nondivergent_reexecution_is_not_a_failure"]

    def test_r_D_is_measured_by_a_second_search_distinct_from_the_screen(self):
        names = [d["dispatch"] for d in
                 cal.dispatch_structure()["stage_2_screen_passing_items_only"]]
        assert any("D production search" in n for n in names)
        assert cal.DISPATCHES_PER_SCREENED_CALIBRATION_ITEM == 6

    def test_the_q_gap_is_named_a_commitment_rather_than_a_preregistration(self):
        assert not hasattr(cal, "Q_GAP_PREREGISTERED")
        lin = cal.PARAMETER_LINEAGE["PRECALIBRATION_COMMITTED_Q_GAP"]
        assert lin["status"] == "PRE-CALIBRATION COMMITMENT, not preregistration"
        assert "0.20" in lin["derived_from"]
        assert "NOT preregistered" in cal.PREREGISTRATION_STATUS

    def test_the_legacy_displacement_gap_implies_an_exposure_gap_nobody_would_preregister(self):
        implied = cal.DELTA_GAP_ON_DISPLACEMENT_SCALE_LEGACY / cal.DELTA_PREREGISTERED
        assert implied > 0.66
        assert cal.PRECALIBRATION_COMMITTED_Q_GAP < implied

    def test_the_two_scales_cannot_be_mixed_silently(self):
        s = CvDScenario.from_exposure(p=0.95, q_C=0.40, r_D=1.0, delta=0.30)
        assert s.delta_C == pytest.approx(0.12)
        assert s.delta_D == pytest.approx(0.30)

    def test_an_out_of_range_exposure_rate_is_refused(self):
        with pytest.raises(ValueError):
            CvDScenario.from_exposure(p=0.95, q_C=1.4, r_D=0.8)

    def test_the_cvd_claim_is_narrowed_to_the_query_construction_procedure(self):
        v = authorize(CvDScenario.from_exposure(p=0.95, q_C=0.50, r_D=0.80), 50)
        assert "query-construction procedure" in v["claim"]
        assert "NOT a claim about retrieved page content" in v["claim"]


# --------------------------------------------------------------------------- #
_SRC = [{"identifier": "https://example.invalid/reg", "title": "Register",
         "establishes": "the anchored value", "accessed": "2026-09-03",
         "tier": "authoritative_primary", "verifier": "test"}]


def _row(item_id="cal001", subset="grader_validation_holdout", route="exact_entity", **kw):
    """A row on the TYPED schema: the answer key and the screen spec are two
    separate objects, and neither stands in for the other."""
    keys = {"exact_entity": {"route": "exact_entity", "accept": ["Right"],
                             "rejects": ["Wrong"]},
            "boolean": {"route": "boolean", "expected": False},
            "numeric": {"route": "numeric", "value": 9, "tolerance": 0,
                        "reject_values": [8]}}
    specs = {"exact_entity": {"route": "exact_entity", "displacing_aliases": ["Wrong"],
                              "affirming_aliases": ["Right"]},
             "boolean": {"route": "boolean",
                         "displacing_propositions": ["the state was a member"],
                         "affirming_propositions": ["the state was a partner"]},
             "numeric": {"route": "numeric", "subject_terms": ["planet"],
                         "displacing_value_forms": ["8", "eight"],
                         "affirming_value_forms": ["9", "nine"]}}
    base = dict(item_id=item_id, pool="calibration", subset=subset, batch=1,
                production_barred=True, stem="stem?", route=route,
                answer_key=keys[route], screen_spec=specs[route], key_sources=_SRC,
                key_provenance="docs/ANSWER_KEY_CORRECTION_PROCESS.md#x",
                query_subject="subject", anchor_as_written="in 2015")
    base.update(kw)
    return cal.CalibrationRow(**base)


def _scored(item_id, subset, closed=("CORRECT", "CORRECT"),
            c=("CORRECT", "CORRECT"), d=("CORRECT", "CORRECT"), divergent_c=True,
            divergent_d_production=True):
    return _row(item_id, subset, screen_passed=True, d_divergent=True,
                c_divergent=divergent_c,
                d_production_divergent=divergent_d_production,
                hand_verdict_closed=closed[0], grader_verdict_closed=closed[1],
                hand_verdict_c=c[0], grader_verdict_c=c[1],
                hand_verdict_d=d[0], grader_verdict_d=d[1],
                hand_verdict_recorded_first=True, grader_fingerprint="deadbeefdeadbeef",
                hand_adjudicator="tier1:lab.stage0b_adjudication")


class TestTheLedgerSchemaCarriesLineageForEveryStatistic:

    def test_every_statistic_names_the_fields_it_is_computed_from(self):
        fields = set(cal.CalibrationRow.__dataclass_fields__)
        for stat, needed in cal.REQUIRED_FOR_EACH_STATISTIC.items():
            assert set(needed) <= fields, f"{stat} reads a field the row does not have"

    def test_a_calibration_row_asserts_its_own_production_bar(self):
        assert validate_has(_row(production_barred=False), "production_barred must be True")
        assert validate_has(_row(pool="production"), "pool must be 'calibration'")

    def test_grading_without_recording_the_hand_verdict_first_is_a_schema_error(self):
        r = _row(grader_verdict_closed="CORRECT", grader_fingerprint="abc",
                 hand_verdict_recorded_first=False)
        assert validate_has(r, "hand_verdict_recorded_first")

    def test_grading_without_a_grader_fingerprint_is_a_schema_error(self):
        r = _row(grader_verdict_closed="CORRECT", hand_verdict_recorded_first=True)
        assert validate_has(r, "grader fingerprint")

    def test_screen_passed_without_divergence_is_a_schema_error(self):
        assert validate_has(_row(screen_passed=True, d_divergent=False), "screen_passed with")

    def test_a_well_formed_row_has_no_problems(self):
        assert cal.validate_row(_scored("cal001", "development")) == []


def validate_has(row, fragment):
    return any(fragment in p for p in cal.validate_row(row))


# --------------------------------------------------------------------------- #
class TestTheDecisionRulesAreFixedBeforeAnyDatumExists:

    def _bank(self, n_hold, n_dev=4, closed_errors=0, c_divergent=None, defects=0):
        rows = []
        c_divergent = n_hold + n_dev if c_divergent is None else c_divergent
        for i in range(n_dev + n_hold):
            subset = "development" if i < n_dev else "grader_validation_holdout"
            closed = ("CORRECT", "INCORRECT") if i < closed_errors else ("CORRECT", "CORRECT")
            c = ("CORRECT", "INCORRECT") if (i >= n_dev and i - n_dev < defects) \
                else ("CORRECT", "CORRECT")
            rows.append(_scored(f"cal{i:03d}", subset, closed=closed, c=c,
                                divergent_c=i < c_divergent))
        return rows

    def test_a_clean_large_bank_passes_and_says_what_it_authorizes(self):
        rows = self._bank(n_hold=cal.BATCH1_HOLDOUT, n_dev=cal.BATCH1_DEV)
        st = cal.calibration_statistics(rows)
        assert st["p"]["in_band"] is True
        assert st["grader"]["g_one_upper_95"] <= cal.G_ONE_BOUND_FOR_PASS
        d = cal.decide(st, n_screened_total=cal.BATCH1_TARGET_SCREENED)
        assert d["verdict"] == cal.PASS
        assert any("freeze" in a for a in d["authorizes"])

    def test_a_small_clean_bank_continues_rather_than_passing(self):
        rows = self._bank(n_hold=6, n_dev=2)
        st = cal.calibration_statistics(rows)
        assert st["n_prod_required"] is None, "too small to size against"
        d = cal.decide(st, n_screened_total=8)
        assert d["verdict"] == cal.CONTINUE
        assert d["next_batch_screen_passing_items"] == cal.BATCHN_TARGET_SCREENED

    def test_a_single_held_out_grader_defect_forces_a_repair_and_burns_the_holdout(self):
        rows = self._bank(n_hold=cal.BATCH1_HOLDOUT, n_dev=cal.BATCH1_DEV, defects=1)
        d = cal.decide(cal.calibration_statistics(rows), n_screened_total=48)
        assert d["verdict"] == cal.REVISE_GRADER
        assert "spent" in d["reasons"][0]

    def test_a_grader_change_after_the_holdout_was_scored_forces_a_fresh_holdout(self):
        rows = self._bank(n_hold=cal.BATCH1_HOLDOUT, n_dev=cal.BATCH1_DEV)
        d = cal.decide(cal.calibration_statistics(rows), n_screened_total=48,
                       grader_repaired_since_holdout=True)
        assert d["verdict"] == cal.CONTINUE
        assert "fresh holdout" in d["reasons"][0]

    def test_a_recipe_below_the_band_revises_the_recipe_and_never_the_pool(self):
        rows = self._bank(n_hold=24, n_dev=12, closed_errors=8)
        d = cal.decide(cal.calibration_statistics(rows), n_screened_total=48)
        assert d["verdict"] == cal.REVISE_RECIPE
        assert any("too hard" in r for r in d["reasons"])

    def test_an_undosed_C_arm_revises_the_recipe(self):
        rows = self._bank(n_hold=24, n_dev=12, c_divergent=2)   # q_C ~ 0.056
        d = cal.decide(cal.calibration_statistics(rows), n_screened_total=48)
        assert d["verdict"] == cal.REVISE_RECIPE
        assert any("undosed" in r for r in d["reasons"])

    def test_reaching_the_cap_without_passing_revises_the_design(self):
        rows = self._bank(n_hold=6, n_dev=2)
        d = cal.decide(cal.calibration_statistics(rows),
                       n_screened_total=cal.MAX_CALIBRATION_SCREENED)
        assert d["verdict"] == cal.REVISE_DESIGN

    def test_the_evaluation_order_is_part_of_the_rule(self):
        # a bank that fails BOTH the recipe and the grader is a recipe problem:
        # a grader repair cannot rescue items the model cannot answer closed-book.
        rows = self._bank(n_hold=24, n_dev=12, closed_errors=8, defects=1)
        assert cal.decide(cal.calibration_statistics(rows),
                          n_screened_total=48)["verdict"] == cal.REVISE_RECIPE

    def test_the_screen_pass_rate_is_computed_over_authored_items_not_screened_ones(self):
        rows = self._bank(n_hold=6, n_dev=2)
        rows.append(_row("cal999", "development", screen_passed=False, d_divergent=False))
        st = cal.calibration_statistics(rows)
        assert st["screen"]["n_authored"] == 9
        assert st["screen"]["n_passed"] == 8

    def test_screened_out_items_feed_the_pass_rate_and_nothing_else(self):
        rows = self._bank(n_hold=24, n_dev=12)
        base = cal.calibration_statistics(rows)
        rows.append(_row("cal999", "development", screen_passed=False, d_divergent=False))
        with_reject = cal.calibration_statistics(rows)
        assert with_reject["p"] == base["p"]
        assert with_reject["q_C"] == base["q_C"]
        assert with_reject["screen"]["s_hat"] < 1.0

    def test_the_arm_D_diagnostic_is_reported_separately_and_enters_no_bound(self):
        st = cal.calibration_statistics(self._bank(n_hold=24, n_dev=12, defects=3))
        assert st["grader"]["k_g_one"] == 3           # the A/C pairs carry the bound
        assert st["grader"]["arm_D_diagnostic"]["k_g_one_on_AD_pairs"] == 0

    def test_a_bank_too_small_to_size_against_is_not_a_design_failure(self):
        st = cal.calibration_statistics(self._bank(n_hold=6, n_dev=2))
        assert cal.decide(st, n_screened_total=8)["verdict"] == cal.CONTINUE

    def test_the_reported_n_prod_is_the_one_sized_at_the_grader_bound(self):
        st = cal.calibration_statistics(self._bank(n_hold=24, n_dev=12))
        assert st["n_prod_required"] > st["n_prod_required_if_grader_were_perfect"]


# --------------------------------------------------------------------------- #
class TestTheReportIsSelfDescribingAndAssertsNoOutcome:

    def test_the_report_states_that_no_calibration_datum_exists(self):
        assert "No calibration datum exists" in cal.report()["what_this_is"]

    def test_the_report_records_the_provenance_of_both_superseded_control_counts(self):
        prov = cal.report()["negative_control"]["provenance"]
        assert set(prov) == {"15", "20", "resolution"}
        assert "REALIZED arithmetic_control class size" in prov["15"]["provenance"]
        assert "15 + 5 = 20" in prov["20"]["provenance"]
