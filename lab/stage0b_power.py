"""Stage 0B power, sized on EXPECTED DISCORDANCE rather than on n.

WHY THIS MODULE EXISTS
----------------------
Stage 0A-M was sized on a class-level effect parameter `d` at an assumed
baseline accuracy of 0.85. It produced D = 2 discordant pairs in total. At D = 2
the smallest attainable exact p-value is 1/4, so no orientation of the observed
data could have rejected at any Holm threshold -- the run was incapable of
rejecting before a single grade was read.

That is the failure this module is built to prevent. The quantity a paired exact
test actually spends is the DISCORDANT COUNT, so Stage 0B is sized on E[D],
E[n10] and E[n01], and n is whatever delivers them.

THE GENERATIVE MODEL
--------------------
Per item, with all probabilities per-item and independent across items:

    p          P(closed-book answer is correct)                   -- baseline
    u          P(the treated arm actually consumes retrieval)     -- UPTAKE
    q_exposure P(the injected block's RUNTIME-SYNTHESISED SUMMARY carries a
               predeclared reject alias | exposed). RENAMED 2026-09-03 from
               `c_disp`, which said "retrieved content carries displacing
               information". Measured, no retrieved page content crosses the
               boundary at all -- the block is a query echo, a titles+URLs link
               array and a prose answer synthesised INSIDE the search runtime.
               The parameter is ARM-SPECIFIC: q_C for the model-written query,
               q_D for the fixed one, and q_D is 1.0 by construction on the
               production pool because the divergence screen admits on it. See
               lab/stage0b_calibration.py:PARAMETER_GLOSSARY.
    delta      P(the answer is displaced | a divergent block injected, closed correct)
               -- the susceptibility the experiment is trying to measure
    h        P(a wrong closed answer is repaired | anchored content consumed)
    g        P(the grader misreads a trial), applied symmetrically to both arms

True paired cells, conditioning on the closed outcome:

    P(treated correct | closed correct)   = 1 - u * q_exposure * delta
    P(treated correct | closed incorrect) = u * (1 - q_exposure) * h

Grader noise is then convolved in independently per arm, because a grader defect
that fires on both arms of an item still produces a CONCORDANT pair, whereas one
that fires on a single arm manufactures discordance out of nothing. Stage 0A-M's
two discordant pairs were exactly that.

Everything is computed EXACTLY. (n10, n01) is a marginal of a 4-cell multinomial
and the exact p-value depends on nothing else, so power is a finite sum with no
Monte Carlo error.

Nothing here dispatches, and nothing here reads a production outcome.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from functools import lru_cache
from math import comb

# Measured per-dispatch costs, Stage 0A-M (runs/exp004_stage0am, 130 dispatches,
# $2.5126 total). Used to price Stage 0B; extrapolated, not measured, for the
# injected-context answerer.
COST_CLOSED_DISPATCH = 1.0629 / 65          # $0.01635  [MEASURED]
COST_DECLINED_RETRIEVAL = 0.8546 / 57       # $0.01499  [MEASURED]
COST_SEARCHING_DISPATCH = 0.5951 / 8        # $0.07439  [MEASURED, Stage 0A-M]
# Superseded 2026-09-03 by MEASURED Stage 0B-path costs. The searcher figure is the
# mean of the six real `stage0b-searcher` dispatches (2 runtime-gate + 4 divergence
# probe); the injected answerer is no longer an extrapolation.
COST_STAGE0B_SEARCH = 0.06400               # [MEASURED, n=6]
COST_STAGE0B_QUERY_WRITER = 0.01359         # [MEASURED, n=1]
COST_INJECTED_ANSWERER = 0.02755            # [MEASURED, n=1]; was 0.025 [ESTIMATE]


@dataclass(frozen=True)
class Scenario:
    """`g_both` and `g_one` are separated because Stage 0A-M proved they are
    different failures with different consequences.

    The frozen grader's false negatives were overwhelmingly ARM-SYMMETRIC: of the
    16 exact_entity items, 13 were misgraded in BOTH arms and 2 in exactly one
    (plus the boolean item a09, misgraded in both). A symmetric false negative
    moves a (1,1) pair to (0,0) and so silently DELETES an at-risk item -- it
    costs power without leaving a trace in the discordant counts. An asymmetric
    one MANUFACTURES a discordant pair out of elaboration style, and Stage 0A-M's
    only two discordant pairs were exactly that.

    Modelling both with one symmetric-noise parameter would hide the distinction
    the design has to engineer against, so they are separate.
    """
    name: str
    p: float           # closed-book baseline accuracy
    u: float           # retrieval uptake
    q_exposure: float  # P(the injected summary carries a reject alias | exposed)
    delta: float       # displacement susceptibility
    h: float = 0.0     # repair probability
    g_both: float = 0.0  # P(grader false-negatives BOTH arms of an item)
    g_one: float = 0.0   # P(grader false-negatives exactly ONE arm, side 50/50)


def true_cells(s: Scenario) -> tuple[float, float, float, float]:
    """(t00, t01, t10, t11) before grader noise."""
    harm = s.u * s.q_exposure * s.delta
    repair = s.u * (1 - s.q_exposure) * s.h
    t11 = s.p * (1 - harm)
    t10 = s.p * harm
    t01 = (1 - s.p) * repair
    t00 = (1 - s.p) * (1 - repair)
    return t00, t01, t10, t11


def observed_cells(s: Scenario) -> tuple[float, float, float, float]:
    """Apply the grader's FALSE-NEGATIVE noise. It is one-directional: the
    observed defect can only turn a correct answer into an incorrect grade, never
    the reverse -- reject-precedence and negation-precedence cannot rescue a
    wrong answer."""
    t00, t01, t10, t11 = true_cells(s)
    truth = {(0, 0): t00, (0, 1): t01, (1, 0): t10, (1, 1): t11}
    obs = {(0, 0): 0.0, (0, 1): 0.0, (1, 0): 0.0, (1, 1): 0.0}
    p_clean = 1.0 - s.g_both - s.g_one
    if p_clean < 0:
        raise ValueError("g_both + g_one exceeds 1")
    for (b, t), pr in truth.items():
        obs[(b, t)] += pr * p_clean                       # grader behaved
        obs[(0, 0)] += pr * s.g_both                      # both arms false-negative
        obs[(0, t)] += pr * s.g_one / 2                   # closed arm only
        obs[(b, 0)] += pr * s.g_one / 2                   # treated arm only
    return obs[(0, 0)], obs[(0, 1)], obs[(1, 0)], obs[(1, 1)]


def exact_one_sided_p(n10: int, n01: int) -> Fraction:
    d = n10 + n01
    if d == 0:
        return Fraction(1)
    return Fraction(sum(comb(d, i) for i in range(n10, d + 1)), 2 ** d)


@lru_cache(maxsize=None)
def _rejects(n10: int, n01: int, alpha_num: int, alpha_den: int) -> bool:
    return exact_one_sided_p(n10, n01) <= Fraction(alpha_num, alpha_den)


def joint_n10_n01(n: int, o10: float, o01: float):
    """Exact P(n10=i, n01=j) -- a marginal of the 4-cell multinomial.

    Computed by a stable forward recurrence rather than by evaluating powers and
    binomials term by term, so it stays exact-in-spirit and fast enough for the
    n-sweep that sizes the design.
    """
    rest = 1.0 - o10 - o01
    if rest < 0:
        raise ValueError("cell probabilities exceed 1")
    for i in range(n + 1):
        ci = comb(n, i) * (o10 ** i)
        for j in range(n - i + 1):
            yield i, j, ci * comb(n - i, j) * (o01 ** j) * (rest ** (n - i - j))


def analyse_scenario(s: Scenario, n: int, alpha: Fraction = Fraction(1, 40)) -> dict:
    """alpha defaults to the Holm K=2 first step (1/40 = 0.025), which is what a
    primary class must clear to reject when it is the smaller of two p-values."""
    _, o01, o10, _ = observed_cells(s)
    an, ad = alpha.numerator, alpha.denominator
    power = e_n10 = e_n01 = p_zero = p_below_floor = 0.0
    for i, j, pr in joint_n10_n01(n, o10, o01):
        e_n10 += i * pr
        e_n01 += j * pr
        if i + j == 0:
            p_zero += pr
        if _rejects(i, j, an, ad):
            power += pr
        if not _rejects(i + j, 0, an, ad):
            p_below_floor += pr
    return {
        "scenario": s.name, "n": n, "alpha": float(alpha),
        "params": {k: v for k, v in asdict(s).items() if k != "name"},
        "expected_n10": round(e_n10, 3),
        "expected_n01": round(e_n01, 3),
        "expected_D": round(e_n10 + e_n01, 3),
        "P_D_equals_zero": round(p_zero, 4),
        "P_D_below_rejection_floor": round(p_below_floor, 4),
        "power": round(power, 4),
    }


def n_for_power(s: Scenario, target: float = 0.80, alpha: Fraction = Fraction(1, 40),
                n_max: int = 120) -> int | None:
    """Smallest n reaching `target` power, or None if unreachable within n_max.

    Power is not guaranteed monotone in n for a discrete exact test, so this
    scans rather than bisects.
    """
    for n in range(4, n_max + 1):
        if analyse_scenario(s, n, alpha)["power"] >= target:
            return n
    return None


# ---------------------------------------------------------------------------
# The preregistration-candidate scenario grid
# ---------------------------------------------------------------------------
# `q_exposure` is the query-quality channel and is the parameter Stage 0B's arm
# structure is designed to move: a model-written query is assumed likelier to
# return present-tense content for a past-anchored question than a fixed query
# that pins the anchor date. On the production pool that assumption is partly
# FORCED rather than free -- the divergence screen admits an item only if its
# FIXED-query block is divergent, so q_D = 1.0 there and only q_C is estimated.
# These scenario values are ASSUMED and are superseded by the calibration bank.

SCENARIOS: tuple[Scenario, ...] = (
    # --- Stage 0A-M priced as a scenario, with its own measured pathologies ---
    # g_both/g_one are calibrated from the run: on the date class, 15 of 25 items
    # were false-negatived in both arms and 2 in exactly one.
    Scenario("stage0am_as_run_clean_grader", p=1.00, u=0.12, q_exposure=0.50, delta=0.30),
    Scenario("stage0am_as_run_with_its_grader", p=1.00, u=0.12, q_exposure=0.50, delta=0.30,
             g_both=0.60, g_one=0.08),
    # --- baseline sweep, retrieval REQUIRED (u=1), model-written query --------
    Scenario("baseline_0.95_required_retrieval", p=0.95, u=1.0, q_exposure=0.50, delta=0.30),
    Scenario("baseline_0.80_required_retrieval", p=0.80, u=1.0, q_exposure=0.50, delta=0.30),
    Scenario("baseline_0.65_required_retrieval", p=0.65, u=1.0, q_exposure=0.50, delta=0.30, h=0.20),
    Scenario("baseline_0.50_required_retrieval", p=0.50, u=1.0, q_exposure=0.50, delta=0.30, h=0.20),
    # --- uptake, at a fixed good baseline ------------------------------------
    Scenario("low_uptake_optional_arm", p=0.95, u=0.15, q_exposure=0.50, delta=0.30),
    Scenario("high_uptake_optional_arm", p=0.95, u=0.90, q_exposure=0.50, delta=0.30),
    # --- the query-construction contrast -------------------------------------
    Scenario("model_query_harmful", p=0.95, u=1.0, q_exposure=0.70, delta=0.35),
    Scenario("fixed_query_repairs", p=0.95, u=1.0, q_exposure=0.15, delta=0.35),
    # --- instrument pathologies ----------------------------------------------
    Scenario("grader_symmetric_fn_20pct", p=0.95, u=1.0, q_exposure=0.50, delta=0.30, g_both=0.20),
    Scenario("grader_asymmetric_fn_8pct", p=0.95, u=1.0, q_exposure=0.50, delta=0.30, g_one=0.08),
    Scenario("grader_stage0am_like", p=0.95, u=1.0, q_exposure=0.50, delta=0.30,
             g_both=0.60, g_one=0.08),
    Scenario("ceiling_no_effect", p=1.00, u=1.0, q_exposure=0.50, delta=0.0),
    Scenario("floor", p=0.20, u=1.0, q_exposure=0.50, delta=0.30, h=0.20),
)

ARM_COSTS = {
    "A_closed": COST_CLOSED_DISPATCH,
    "C_required_model_query": COST_STAGE0B_QUERY_WRITER + COST_STAGE0B_SEARCH
                              + COST_INJECTED_ANSWERER,
    "D_required_fixed_query": COST_STAGE0B_SEARCH + COST_INJECTED_ANSWERER,
    "B_optional_retrieval_NOT_USED": COST_DECLINED_RETRIEVAL,
}


def cost_for(n_primary_items: int, n_control_items: int, arms: tuple[str, ...]) -> dict:
    per_item = sum(ARM_COSTS[a] for a in arms)
    n = n_primary_items + n_control_items
    return {
        "arms": list(arms),
        "items": n,
        "dispatches": n * sum(3 if a == "C_required_model_query"
                              else 2 if a == "D_required_fixed_query" else 1 for a in arms),
        "cost_per_item_usd": round(per_item, 4),
        "total_cost_usd": round(n * per_item, 2),
    }


RECOMMENDED_N_PRIMARY = 50
# 15 was Stage 0A-M's REALIZED arithmetic_control size, carried here unchanged and
# never derived; the authoring protocol independently said 20 (15 reused + 5 fresh,
# design draft 8). Neither was computed from what the control must ESTABLISH.
# Superseded 2026-09-03 by lab.stage0b_calibration.negative_control_n, which derives
# it from the bound the control has to beat. At n_primary=50 that is 30.
RECOMMENDED_N_CONTROL = 30
SUPERSEDED_N_CONTROL_VALUES = {"power_module_carryover": 15, "authoring_protocol": 20}
RECOMMENDED_ARMS = ("A_closed", "C_required_model_query", "D_required_fixed_query")


def recommended_design() -> dict:
    """One primary comparison (A vs C) in a K=1 family, so the primary class
    tests at alpha=0.05 rather than the 0.025 a K=2 family would force. The
    query-quality contrast (C vs D) is a preregistered SECONDARY in its own
    family and does not spend the primary's alpha."""
    design = Scenario("design_point", p=0.95, u=1.0, q_exposure=0.50, delta=0.30)
    a05, a025 = Fraction(1, 20), Fraction(1, 40)
    return {
        "primary_comparison": "A_closed vs C_required_model_query, paired by item",
        "primary_family_size_K": 1,
        "alpha_primary": 0.05,
        "n_primary_items": RECOMMENDED_N_PRIMARY,
        "n_control_items": RECOMMENDED_N_CONTROL,
        "arms": list(RECOMMENDED_ARMS),
        "design_point": asdict(design),
        "at_design_point": analyse_scenario(design, RECOMMENDED_N_PRIMARY, a05),
        "minimum_detectable_delta_at_80pct": next(
            (round(d, 2) for d in [i / 100 for i in range(5, 101, 5)]
             if analyse_scenario(Scenario("mde", p=0.95, u=1.0, q_exposure=0.50, delta=d),
                                 RECOMMENDED_N_PRIMARY, a05)["power"] >= 0.80), None),
        "if_forced_back_to_K2_alpha_0.025": analyse_scenario(
            design, RECOMMENDED_N_PRIMARY, a025),
        "secondary_C_vs_D": "same paired exact test, own family, reported with its own "
                            "discordant counts; a null there is a null about query "
                            "quality, not about displacement",
        "cost": cost_for(RECOMMENDED_N_PRIMARY, RECOMMENDED_N_CONTROL, RECOMMENDED_ARMS),
        "why_not_more_n": "Grader defects of the size Stage 0A-M actually had "
                          "(g_both=0.60, g_one=0.08) leave the design unpowered at EVERY "
                          "n up to 120. Instrument repair buys power that n cannot.",
    }


def report(ns: tuple[int, ...] = (25, 40, 60)) -> dict:
    grid = [analyse_scenario(s, n) for s in SCENARIOS for n in ns]
    sizing = {s.name: n_for_power(s) for s in SCENARIOS}
    return {
        "recommended_design": recommended_design(),
        "what_this_is": "Stage 0B power, sized on expected discordance. Exact, no Monte Carlo.",
        "alpha_note": "alpha=0.025 is the Holm K=2 first step; a class that is the "
                      "larger of two p-values needs only 0.05.",
        "rejection_floor": {
            "smallest_D_that_can_reject_at_0.025": 6,
            "smallest_D_that_can_reject_at_0.05": 5,
            "stage0am_realized_D_primary_family": 2,
            "consequence": "Stage 0A-M could not have rejected at any orientation of "
                           "its observed discordances.",
        },
        "grid": grid,
        "n_for_80pct_power_at_alpha_0.025": sizing,
        "cost": {
            "measured_unit_costs_usd": {
                "closed_dispatch": round(COST_CLOSED_DISPATCH, 5),
                "retrieval_dispatch_that_declined": round(COST_DECLINED_RETRIEVAL, 5),
                "retrieval_dispatch_that_searched": round(COST_SEARCHING_DISPATCH, 5),
                "stage0b_search_dispatch_MEASURED": COST_STAGE0B_SEARCH,
                "stage0b_query_writer_MEASURED": COST_STAGE0B_QUERY_WRITER,
                "injected_context_answerer_MEASURED": COST_INJECTED_ANSWERER,
            },
            "candidate_designs": {
                "A_C_only_n40_plus_15_control": cost_for(
                    40, 15, ("A_closed", "C_required_model_query")),
                "A_C_D_n40_plus_15_control": cost_for(
                    40, 15, ("A_closed", "C_required_model_query", "D_required_fixed_query")),
                "A_C_D_n60_plus_15_control": cost_for(
                    60, 15, ("A_closed", "C_required_model_query", "D_required_fixed_query")),
                "four_arm_n40_plus_15_control": cost_for(
                    40, 15, ("A_closed", "B_optional_retrieval_NOT_USED",
                             "C_required_model_query", "D_required_fixed_query")),
            },
        },
    }


def main() -> int:
    import pathlib
    out = pathlib.Path(__file__).resolve().parent.parent / "runs" / "exp004_stage0b_design"
    out.mkdir(parents=True, exist_ok=True)
    doc = report()
    (out / "power_simulation.json").write_text(json.dumps(doc, indent=1) + "\n")
    print(json.dumps(doc["rejection_floor"], indent=1))
    print()
    print(f"{'scenario':40s} {'n':>3s} {'E[n10]':>7s} {'E[n01]':>7s} {'E[D]':>6s} "
          f"{'P(D=0)':>7s} {'power':>6s}")
    for r in doc["grid"]:
        if r["n"] != 40:
            continue
        print(f"{r['scenario']:40s} {r['n']:3d} {r['expected_n10']:7.2f} {r['expected_n01']:7.2f} "
              f"{r['expected_D']:6.2f} {r['P_D_equals_zero']:7.3f} {r['power']:6.3f}")
    print()
    print("n for 80% power @ alpha=0.025:", json.dumps(doc["n_for_80pct_power_at_alpha_0.025"]))
    print()
    print("RECOMMENDED:", json.dumps({
        k: doc["recommended_design"][k] for k in
        ("n_primary_items", "alpha_primary", "minimum_detectable_delta_at_80pct")}))
    print("  at design point:", json.dumps({
        k: doc["recommended_design"]["at_design_point"][k]
        for k in ("expected_n10", "expected_D", "power")}))
    print("  cost:", json.dumps(doc["recommended_design"]["cost"]))
    print()
    for k, v in doc["cost"]["candidate_designs"].items():
        print(f"  {k:38s} {v['dispatches']:4d} dispatches  ${v['total_cost_usd']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
