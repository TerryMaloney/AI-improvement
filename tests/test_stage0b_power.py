"""Stage 0B power model: the properties the design decisions rest on."""
from __future__ import annotations

import json
import pathlib
from fractions import Fraction

import pytest

from lab.stage0b_power import (RECOMMENDED_N_PRIMARY, Scenario, analyse_scenario,
                               cost_for, exact_one_sided_p, n_for_power,
                               observed_cells, recommended_design, report, true_cells)

REPO = pathlib.Path(__file__).resolve().parent.parent
A05, A025 = Fraction(1, 20), Fraction(1, 40)


def test_cells_are_probability_distributions():
    for s in (Scenario("a", p=0.95, u=1.0, c_disp=0.5, delta=0.3),
              Scenario("b", p=0.5, u=0.5, c_disp=0.3, delta=0.4, h=0.2,
                       g_both=0.2, g_one=0.1)):
        assert sum(true_cells(s)) == pytest.approx(1.0)
        assert sum(observed_cells(s)) == pytest.approx(1.0)
        assert all(c >= -1e-12 for c in observed_cells(s))


def test_grader_false_negatives_are_one_directional():
    """The observed defect can only turn a correct answer into an incorrect
    grade. A model that let it work the other way would be modelling a different
    instrument."""
    clean = Scenario("clean", p=0.9, u=1.0, c_disp=0.5, delta=0.3)
    noisy = Scenario("noisy", p=0.9, u=1.0, c_disp=0.5, delta=0.3, g_both=0.3, g_one=0.2)
    assert observed_cells(noisy)[3] < observed_cells(clean)[3]      # fewer (1,1)
    assert observed_cells(noisy)[0] > observed_cells(clean)[0]      # more (0,0)


def test_symmetric_and_asymmetric_grader_error_fail_differently():
    """Symmetric false negatives delete at-risk items without leaving a trace in
    the discordant counts; asymmetric ones manufacture discordance. Collapsing
    them into one parameter would hide the distinction the design engineers
    against."""
    base = Scenario("base", p=0.95, u=1.0, c_disp=0.5, delta=0.3)
    sym = Scenario("sym", p=0.95, u=1.0, c_disp=0.5, delta=0.3, g_both=0.3)
    asym = Scenario("asym", p=0.95, u=1.0, c_disp=0.5, delta=0.3, g_one=0.3)
    b, s, a = (analyse_scenario(x, 40) for x in (base, sym, asym))
    assert s["expected_n01"] == pytest.approx(b["expected_n01"], abs=1e-9)  # no new n01
    assert s["expected_D"] < b["expected_D"]                                # fewer at risk
    assert a["expected_n01"] > b["expected_n01"]                            # manufactured
    assert a["expected_D"] > b["expected_D"]


def test_zero_effect_gives_zero_discordance_and_zero_power():
    s = Scenario("null", p=1.0, u=1.0, c_disp=0.5, delta=0.0)
    r = analyse_scenario(s, 40)
    assert r["expected_D"] == 0.0 and r["power"] == 0.0 and r["P_D_equals_zero"] == 1.0


def test_type_one_error_is_controlled_at_the_boundary():
    """Equal harm and repair rates put the true orientation probability at 1/2 --
    the least favourable point of the null. Rejection must stay under alpha."""
    s = Scenario("boundary", p=0.5, u=1.0, c_disp=0.5, delta=0.4, h=0.4)
    t = true_cells(s)
    assert t[2] == pytest.approx(t[1])          # t10 == t01
    for n in (25, 40, 50):
        assert analyse_scenario(s, n, A05)["power"] <= 0.05 + 1e-9


def test_uptake_not_n_is_what_makes_the_optional_arm_hopeless():
    """The finding that removes ARM B from the design."""
    low = Scenario("low", p=0.95, u=0.15, c_disp=0.5, delta=0.3)
    forced = Scenario("forced", p=0.95, u=1.0, c_disp=0.5, delta=0.3)
    assert n_for_power(low, 0.80, A025) is None
    assert n_for_power(forced, 0.80, A025) == 54


def test_a_stage0am_grade_of_grader_defect_cannot_be_bought_off_with_n():
    """Prefer fixing the instrument over increasing n -- asserted, not asserted-at."""
    like_0am = Scenario("like", p=0.95, u=1.0, c_disp=0.5, delta=0.3,
                        g_both=0.60, g_one=0.08)
    assert n_for_power(like_0am, 0.80, A025, n_max=120) is None


def test_high_baseline_is_better_than_a_middling_one():
    """Contradicts the instinct to make items harder: at low baseline, genuine
    repair (n01) cancels harm (n10) in a one-sided paired test."""
    hi = Scenario("hi", p=0.95, u=1.0, c_disp=0.5, delta=0.3)
    mid = Scenario("mid", p=0.65, u=1.0, c_disp=0.5, delta=0.3, h=0.2)
    assert analyse_scenario(hi, 40)["power"] > analyse_scenario(mid, 40)["power"]
    assert n_for_power(mid, 0.80, A025) is None


def test_the_query_contrast_separates_the_two_arms():
    harmful = Scenario("harmful", p=0.95, u=1.0, c_disp=0.70, delta=0.35)
    repaired = Scenario("repaired", p=0.95, u=1.0, c_disp=0.15, delta=0.35)
    assert analyse_scenario(harmful, 40)["power"] > 0.8
    assert analyse_scenario(repaired, 40)["power"] < 0.1


def test_recommended_design_is_powered_where_it_claims_to_be():
    d = recommended_design()
    assert d["n_primary_items"] == RECOMMENDED_N_PRIMARY == 50
    assert d["primary_family_size_K"] == 1 and d["alpha_primary"] == 0.05
    assert d["at_design_point"]["power"] >= 0.80
    assert d["at_design_point"]["expected_D"] >= 6, "must clear the D>=5 rejection floor"
    assert d["minimum_detectable_delta_at_80pct"] is not None
    assert "B_optional_retrieval_NOT_USED" not in d["arms"]


def test_cost_accounting_counts_the_extra_dispatches_the_forced_arms_need():
    a_only = cost_for(50, 15, ("A_closed",))
    full = cost_for(50, 15, ("A_closed", "C_required_model_query", "D_required_fixed_query"))
    assert a_only["dispatches"] == 65
    assert full["dispatches"] == 65 * (1 + 3 + 2)
    assert full["total_cost_usd"] > a_only["total_cost_usd"]


def test_persisted_power_artifact_is_current():
    path = REPO / "runs" / "exp004_stage0b_design" / "power_simulation.json"
    assert path.exists(), "run: python -m lab.stage0b_power"
    assert json.loads(path.read_text()) == json.loads(json.dumps(report()))


def test_exact_p_matches_the_frozen_procedure():
    from lab.stage0am import exact_one_sided_p as frozen
    for a in range(7):
        for b in range(7):
            assert float(exact_one_sided_p(a, b)) == pytest.approx(frozen(a, b))
