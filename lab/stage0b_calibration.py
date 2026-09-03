"""Stage 0B calibration — sized on the decisions it must resolve, not on a multiplier.

WHY THIS MODULE EXISTS
----------------------
The battery-authoring protocol required a calibration bank ">= 3x production
size". That number has no derivation anywhere in the repository: it appears as a
bare assertion in the protocol, in the design draft 2.4, in NEXT.md and in the
decision log, and in none of those places is it computed from anything. At the
recommended production size it demanded >= 150 items and, under the realized
six-dispatch trial structure, ~900 dispatches -- more than twice the entire
production run it was meant to protect.

A calibration bank exists to RESOLVE DECISIONS. Each decision has a statistic,
each statistic has a precision requirement, and the bank is whatever delivers
them. That is what this module computes, and the multiplier is replaced by it.

THE FOUR DECISIONS, AND WHAT EACH NEEDS
---------------------------------------
1.  Does the item recipe meet the target closed-book band?  ->  `p`, and a 95%
    one-sided LOWER bound on it that clears 0.90.
2.  How large must production be?                           ->  `q_C`, measured
    ON THE C ARM, plus the grader-defect bound (below).
3.  Can the grader be frozen?                               ->  `g_one`/`g_both`
    measured on FRESH answers, including EXPOSED ones, with an upper bound.
4.  Is the C-vs-D claim authorized?                         ->  `q_C`, `q_D`, `p`.

THE FINDING THAT SIZES THE BANK
-------------------------------
Grader asymmetry dominates. At the recommended n=50, alpha=0.05, p=0.95,
q_C=0.50, delta=0.30, power stays >= 0.80 only while `g_one` <= 0.014. Bounding
`g_one` below 0.014 with zero observed defects needs 213 clean pairs, which is
four times the production run. **Calibration cannot certify that the grader is
good enough for n=50.** So the design does the only honest thing available: it
measures the bound it CAN reach and sizes production AT that bound. That is why
the recommended production n rises from 50 to a measured value, and it is a
consequence of Stage 0A-M's own lesson (design draft 7.1) rather than a new
assumption.

The pooling that makes the bound affordable: a calibration item yields TWO
closed/exposed pairs, (A,C) and (A,D), not one. They are exchangeable for this
parameter because the answering packet, the block format and the answerer agent
are byte-identical between C and D -- only the query differs -- so an
arm-correlated grader defect that fires on one must be able to fire on the other.
That exchangeability is CHECKABLE (compare the two pair-wise defect counts) and
is recorded as an assumption rather than assumed silently.

WHAT THE SELECTION RULE DOES TO THE PARAMETERS
----------------------------------------------
Production items are selected by the divergence screen, which requires the
FIXED-QUERY block's synthesised summary to carry a reject alias. So on the
production pool `q_D = 1.0 BY CONSTRUCTION`. It is not an estimate and it must
never be estimated from unscreened items. Every other calibration parameter is
therefore CONDITIONAL ON SCREEN-PASSING, and calibration items that fail the
screen contribute to exactly one statistic: the screen pass rate `s`.

Nothing here dispatches, and nothing here reads a production outcome.
"""
from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from fractions import Fraction

from lab.stage0am import _cp_upper           # the frozen exact Clopper-Pearson limit
from lab.stage0b_power import Scenario, analyse_scenario

# --------------------------------------------------------------------------- #
# preregistered design commitments -- fixed BEFORE any calibration datum exists
# --------------------------------------------------------------------------- #

ALPHA_PRIMARY = Fraction(1, 20)      # A-vs-C, K=1 family
TARGET_POWER = 0.80
CONF = 0.95

# `delta` is the susceptibility the experiment exists to ESTIMATE. Calibration
# cannot measure it without dispatching exposed answerers on items whose closed
# outcome is already known, which is a treated outcome on a calibration item and
# buys nothing the sizing needs. It stays a preregistered MINIMUM INTERESTING
# EFFECT, exactly as it was in the design draft.
DELTA_PREREGISTERED = 0.30

# The target closed-book band (design draft 2.2). Below 0.90 the one-sided
# paired test loses power to repair/harm cancellation faster than n can buy it.
P_TARGET_LOWER = 0.90

# PASS thresholds, all derived below in `thresholds_with_derivations()`.
G_ONE_BOUND_FOR_PASS = 0.08          # loosest bound that still keeps n_prod <= 90
N_PROD_AFFORDABLE_CAP = 90           # PASS ceiling on the re-derived production n
N_PROD_VIABLE_CAP = 120              # beyond this the estimand is unreachable
Q_C_MIN_VIABLE = 0.15                # below this n_prod > 156; the arm cannot be dosed
SCREEN_PASS_MIN_VIABLE = 0.40        # below this authoring costs more than the run

# Batch sizes. AUTHORED counts include items the screen will reject.
BATCH1_AUTHORED = 48
BATCH1_TARGET_SCREENED = 36          # 12 development + 24 grader-validation holdout
BATCH1_DEV = 12
BATCH1_HOLDOUT = 24
BATCHN_AUTHORED = 32
BATCHN_TARGET_SCREENED = 24          # 8 development + 16 holdout
MAX_CALIBRATION_SCREENED = 84        # safety cap: at this size calibration costs
                                     # about as much as the production run itself

# MEASURED per-dispatch costs on the Stage 0B path (2026-09-03), from
# experiments/exp004_stage0b/runtime_correspondence.json and
# runs/exp004_stage0b_instrument/divergence_probe.json. The searcher figure is
# the mean of the six real searcher dispatches (2 gate + 4 probe).
COST_CLOSED_ANSWERER = 0.01635       # [MEASURED, Stage 0A-M closed dispatch]
COST_QUERY_WRITER = 0.01359          # [MEASURED, n=1, Stage 0B gate]
COST_SEARCH = 0.06400                # [MEASURED, n=6, Stage 0B gate + probe]
COST_EXPOSED_ANSWERER = 0.02755      # [MEASURED, n=1, Stage 0B gate]

# The per-item dispatch structure, derived in `dispatch_structure()`.
COST_SCREEN_ONLY_ITEM = COST_SEARCH
COST_FULL_CALIBRATION_ITEM = (COST_CLOSED_ANSWERER + COST_QUERY_WRITER + COST_SEARCH
                              + 2 * COST_EXPOSED_ANSWERER)   # D search already paid at screen
COST_PRODUCTION_ITEM = (COST_CLOSED_ANSWERER                       # arm A
                        + COST_QUERY_WRITER + COST_SEARCH + COST_EXPOSED_ANSWERER   # arm C
                        + COST_SEARCH + COST_EXPOSED_ANSWERER)                      # arm D


# --------------------------------------------------------------------------- #
# exact binomial bounds
# --------------------------------------------------------------------------- #

def cp_upper(k: int, n: int, conf: float = CONF) -> float:
    """Exact one-sided Clopper-Pearson UPPER limit on a rate, k of n."""
    if n <= 0:
        raise ValueError("n must be positive")
    if k >= n:
        return 1.0
    return _cp_upper(k, n, conf)


def cp_lower(k: int, n: int, conf: float = CONF) -> float:
    """Exact one-sided Clopper-Pearson LOWER limit on a SUCCESS rate, k of n.

    Obtained by reflecting the upper limit on the failure rate, so there is one
    exact implementation in the repository rather than two that can drift.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    return 1.0 - cp_upper(n - k, n, conf)


def n_clean_for_upper_bound(target: float, conf: float = CONF) -> int:
    """Smallest n whose ZERO-event upper bound is strictly below `target`.

    Closed form: 1 - (1-conf)^(1/n) < target. Returned as the integer ceiling of
    the exact solution, and cross-checked against `cp_upper` by test.
    """
    if not 0 < target < 1:
        raise ValueError("target must be in (0,1)")
    n = math.ceil(math.log(1 - conf) / math.log(1 - target))
    while cp_upper(0, n, conf) >= target:
        n += 1
    return n


# --------------------------------------------------------------------------- #
# the parameters, renamed to the representation that actually crosses the boundary
# --------------------------------------------------------------------------- #

PARAMETER_GLOSSARY = {
    "q_C": {
        "definition": "P(the C-arm injected block's RUNTIME-SYNTHESISED SUMMARY contains "
                      "at least one predeclared reject alias | the item passed the "
                      "fixed-query divergence screen)",
        "arm": "C -- model-written query",
        "measured_by": "one query-writer dispatch + one search execution per calibration "
                       "item, then lab.stage0b_search.relevance_flags(...)['divergent']",
        "replaces": "c_disp, which named 'retrieved content carrying displacing "
                    "information'. Measured 2026-09-03, no retrieved page content crosses "
                    "the boundary at all: the block is a query echo, a titles+URLs link "
                    "array, and a prose answer synthesised INSIDE the search runtime. The "
                    "displacing claim, when there is one, lives in that synthesised "
                    "paragraph, so that is where the parameter is defined.",
        "why_it_cannot_be_taken_from_arm_D": "D executes the frozen anchor-preserving "
                                             "fixed query. C executes a query a model "
                                             "wrote. They are different queries producing "
                                             "different blocks; substituting one rate for "
                                             "the other is the whole hypothesis assumed "
                                             "rather than measured.",
    },
    "q_D": {
        "definition": "the same probability for the D arm's frozen fixed query",
        "arm": "D -- fixed anchor-preserving query",
        "value_on_the_production_pool": 1.0,
        "why": "the divergence screen ADMITS an item to production iff its fixed-query "
               "block is divergent, so q_D is 1.0 BY CONSTRUCTION on every production "
               "item. It is not estimated. Its measured value on UNSCREENED authored "
               "items is the screen pass rate `s`, which is a different quantity with a "
               "different job.",
    },
    "delta": {
        "definition": "P(the answer is displaced | closed-book answer correct AND a "
                      "divergent block injected)",
        "status": "PREREGISTERED MINIMUM INTERESTING EFFECT, 0.30. Not measured in "
                  "calibration: it is the quantity the experiment exists to estimate, and "
                  "estimating it on calibration items would size the run on a first look "
                  "at its own effect.",
    },
    "s": {
        "definition": "P(an authored item passes the fixed-query divergence screen)",
        "job": "converts a production item count into an AUTHORING count; also a recipe "
               "viability signal in its own right",
    },
    "g_one": {
        "definition": "P(the grader false-negatives exactly ONE arm of a closed/exposed "
                      "pair of the same item)",
        "why_it_dominates": "it MANUFACTURES discordance out of formatting difference. At "
                            "n=50 the design holds 80% power only while g_one <= 0.014.",
    },
    "g_both": {
        "definition": "P(the grader false-negatives BOTH arms)",
        "why_it_is_milder": "it moves a (1,1) pair to (0,0) and silently DELETES an "
                            "at-risk item. At n=50 the design tolerates g_both up to 0.082.",
    },
}

# The parameters `authorize()` in lab.stage0b_cvd consumes are DISPLACEMENT
# probabilities, not exposure probabilities. Under the corrected decomposition
# with a single susceptibility `delta`, they are:
#
#     delta_C = q_C * delta      delta_D = q_D * delta = delta   (q_D == 1)
#
# which has a consequence the design had not written down: with q_D pinned at 1
# by the selection rule and q_C <= 1, the model query can only be LESS exposing
# than the fixed query on the selected items. The C-vs-D test is kept two-sided
# anyway -- a C query can return a DIFFERENT and more potent displacing claim, so
# the direction is not logically forced -- but the asymmetry is declared here
# rather than discovered later.


def displacement_from_exposure(q: float, delta: float = DELTA_PREREGISTERED) -> float:
    """Map an EXPOSURE rate onto the DISPLACEMENT scale lab.stage0b_cvd works in."""
    return q * delta


# The old `DELTA_GAP_PREREGISTERED = 0.20` lives on the displacement scale. Under
# the decomposition above it implies (q_C - q_D) * delta >= 0.20, i.e. a
# 0.667 difference in exposure rate at delta=0.30 -- which is not a target anyone
# would have preregistered had it been written in the units it is measured in.
# The gap is therefore restated on the EXPOSURE scale, where the calibration bank
# actually observes it.
DELTA_GAP_ON_DISPLACEMENT_SCALE_LEGACY = 0.20
Q_GAP_PREREGISTERED = 0.25           # |q_C - q_D|: a quarter of items change exposure
                                     # status depending on who wrote the query
Q_GAP_IMPLIED_DISPLACEMENT_GAP = Q_GAP_PREREGISTERED * DELTA_PREREGISTERED   # 0.075


# --------------------------------------------------------------------------- #
# sizing
# --------------------------------------------------------------------------- #

def required_production_n(p: float, q_C: float, g_one: float,
                          delta: float = DELTA_PREREGISTERED,
                          alpha: Fraction = ALPHA_PRIMARY,
                          target: float = TARGET_POWER, n_max: int = 400) -> int | None:
    """Smallest primary n reaching `target` power for A-vs-C.

    THE PREREGISTERED SIZING RULE, and the asymmetry in it is deliberate:

      * `q_C` enters at its POINT ESTIMATE. It is an unbiased measurement of a
        property of the search environment and an error in it moves power in
        either direction.
      * `g_one` enters at its 95% UPPER BOUND. It is an INSTRUMENT DEFECT, and
        the one lesson Stage 0A-M paid 130 dispatches for is that a grader defect
        must never be assumed small (design draft 7.1). Sizing at the bound is
        what converts "we saw no defects" into a run that survives the defects we
        could not have seen.
    """
    s = Scenario("sizing", p=p, u=1.0, q_exposure=q_C, delta=delta, g_one=g_one)
    for n in range(4, n_max + 1):
        if analyse_scenario(s, n, alpha)["power"] >= target:
            return n
    return None


def minimum_rejectable_harm_rate(n_primary: int, alpha: Fraction = ALPHA_PRIMARY) -> float:
    """The smallest REALIZED per-item harm rate at which the primary can reject.

    The one-sided exact floor is the smallest D with 1/2^D <= alpha; at
    alpha=0.05 that is D=5. Expressed as a rate it is D_min / n_primary, and it is
    the number the negative control has to beat -- see `negative_control_n`.
    """
    d = 1
    while Fraction(1, 2 ** d) > alpha:
        d += 1
    return d / n_primary


def negative_control_n(n_primary: int, alpha: Fraction = ALPHA_PRIMARY,
                       conf: float = CONF) -> dict:
    """How many negative-control items, DERIVED from what the control must establish.

    The control's job -- and `lab.stage0am.harm_rate_upper_bound` says so in the
    frozen code -- is to bound the rate at which merely being exposed flips a
    correct closed-book answer, ON TASKS WHERE THE EXPOSURE CANNOT BE RELEVANT.
    Call that rate the GENERIC EXPOSURE TAX.

    It is the only handle Stage 0B has on that tax, because the divergence screen
    admits only divergent items to production: there is no within-primary
    contrast between dosed and undosed items to fall back on.

    So the requirement is: a CLEAN control must exclude a generic tax large enough
    to have produced the whole primary signal. The primary cannot reject at all
    below `minimum_rejectable_harm_rate(n_primary)`, so that is the level to
    exclude, and n is the smallest clean sample whose 95% upper bound clears it.
    """
    thr = minimum_rejectable_harm_rate(n_primary, alpha)
    n = n_clean_for_upper_bound(thr, conf)
    # The derived minimum is taken up to the next even number so that the
    # composition stays half reused / half fresh: design draft 8 keeps Stage
    # 0A-M's 15 arithmetic_control items and adds fresh ones, and an odd total
    # would make the split an arbitrary choice rather than a stated one.
    rec = n + (n % 2)
    return {
        "n_primary": n_primary,
        "minimum_rejectable_harm_rate": round(thr, 4),
        "n_control_required": n,
        "n_control_recommended": rec,
        "composition": {"reused_arithmetic_control": 15, "fresh": rec - 15},
        "margin_over_minimum": rec - n,
        "bound_at_that_n_if_clean": round(cp_upper(0, rec, conf), 4),
        "bound_if_one_harm": round(cp_upper(1, rec, conf), 4),
        "rule": "the control's 95% upper bound on the generic exposure tax, when the "
                "control is clean, must be strictly below the smallest realized harm rate "
                "at which the primary could reject",
        "brittleness_declared": "a single harm in the control lifts the bound above the "
                                "threshold. That is not bought off with more items -- it "
                                "is a preregistered REPORTING rule: if the control shows "
                                "any harm, the primary is reported with the generic "
                                "exposure tax explicitly not excluded.",
    }


def provenance_of_the_two_control_numbers() -> dict:
    """Where 15 and 20 came from. Neither was derived; both are superseded."""
    return {
        "15": {
            "appears_in": "lab/stage0b_power.py:RECOMMENDED_N_CONTROL, and the sizing "
                          "paragraph of the 2026-09-02 decision-log entry",
            "provenance": "Stage 0A-M's REALIZED arithmetic_control class size. It scored "
                          "15/15 in both arms with D=0 and a 95% harm bound of 0.181. The "
                          "number was carried into the Stage 0B cost model unchanged.",
            "why_it_is_wrong": "it is a description of a past run, not a requirement. Its "
                               "clean bound, 0.181, does not exclude a generic exposure "
                               "tax of 0.10 -- the entire minimum rejectable primary "
                               "signal at n=50.",
        },
        "20": {
            "appears_in": "docs/EXP004_STAGE0B_BATTERY_AUTHORING_PROTOCOL.md 1",
            "provenance": "design draft 8: REUSE the 15 arithmetic_control items and ADD 5 "
                          "FRESH ones, so that an exposure effect would be visible rather "
                          "than assumed away. 15 + 5 = 20.",
            "why_it_is_wrong": "the 5 fresh items answer a different objection "
                               "(production-exposed items cannot show a fresh effect). "
                               "Nobody checked what bound 20 items attain: 0.139, which "
                               "still does not clear 0.10.",
        },
        "resolution": "both are superseded by the derivation in `negative_control_n`. The "
                      "composition survives -- 15 reused arithmetic_control items plus "
                      "fresh ones to the required total -- because the reuse argument was "
                      "sound and only the count was unexamined.",
    }


def thresholds_with_derivations(n_prod_reference: int = 50) -> dict:
    """Every PASS/REVISE threshold, with the computation that produced it."""
    return {
        "G_ONE_BOUND_FOR_PASS": {
            "value": G_ONE_BOUND_FOR_PASS,
            "derivation": "the loosest grader-asymmetry bound at which the re-derived "
                          "production n stays within the affordable cap: at g_one=0.0798 "
                          f"the required n is {required_production_n(0.95, 0.50, 0.0798)}, "
                          f"inside {N_PROD_AFFORDABLE_CAP}; at g_one=0.10 it is "
                          f"{required_production_n(0.95, 0.50, 0.10)}.",
            "pairs_needed_clean": n_clean_for_upper_bound(G_ONE_BOUND_FOR_PASS),
            "what_cannot_be_reached": {
                "g_one_keeping_power_at_n50": 0.014,
                "clean_pairs_that_would_need": n_clean_for_upper_bound(0.014),
                "consequence": "calibration cannot certify the grader for n=50, so "
                               "production is sized AT the achievable bound instead.",
            },
        },
        "N_PROD_AFFORDABLE_CAP": {
            "value": N_PROD_AFFORDABLE_CAP,
            "derivation": f"{N_PROD_AFFORDABLE_CAP} primary + "
                          f"{negative_control_n(N_PROD_AFFORDABLE_CAP)['n_control_recommended']} "
                          "control items at six dispatches each, which is the largest run "
                          "the measured unit costs keep under ~$30.",
        },
        "Q_C_MIN_VIABLE": {
            "value": Q_C_MIN_VIABLE,
            "derivation": f"at q_C=0.15 the required n is "
                          f"{required_production_n(0.95, 0.15, 0.0)} even with a perfect "
                          f"grader; at q_C=0.10 no n <= 400 reaches 80% power "
                          f"({required_production_n(0.95, 0.10, 0.0)}). Below 0.15 the C "
                          "arm cannot be dosed at any affordable size.",
        },
        "SCREEN_PASS_MIN_VIABLE": {
            "value": SCREEN_PASS_MIN_VIABLE,
            "derivation": "at s=0.40, obtaining the screened items the run needs costs "
                          "more in screen dispatches than the production run costs in "
                          "total. Below that the recipe, not the budget, is the problem.",
        },
        "P_TARGET_LOWER": {
            "value": P_TARGET_LOWER,
            "derivation": "design draft 2.2, unchanged: below 0.90 repairs cancel harms in "
                          "the one-sided paired test faster than n buys power back.",
            "clean_items_to_certify": n_clean_for_upper_bound(1 - P_TARGET_LOWER),
        },
    }


# --------------------------------------------------------------------------- #
# the dispatch structure, and what it costs
# --------------------------------------------------------------------------- #

def dispatch_structure() -> dict:
    """The MINIMUM dispatches per calibration item, and why each one is required.

    Screening first is not an optimisation detail: every calibration estimand is
    conditional on screen-passing, because every production item is. An item the
    screen rejects is not a cheaper calibration item, it is a different
    population, and it contributes to `s` and to nothing else.
    """
    return {
        "stage_1_every_authored_item": [
            {"dispatch": "D fixed-query search", "count": 1,
             "buys": "the divergence screen, and the screen pass rate `s`",
             "cost_usd": COST_SEARCH},
        ],
        "stage_2_screen_passing_items_only": [
            {"dispatch": "closed-book answerer (arm-A packet)", "count": 1,
             "buys": "p, and the grader's behaviour on fresh CLOSED answers",
             "cost_usd": COST_CLOSED_ANSWERER},
            {"dispatch": "query-writer", "count": 1,
             "buys": "the C-arm query -- without it q_C does not exist",
             "cost_usd": COST_QUERY_WRITER},
            {"dispatch": "C model-query search", "count": 1,
             "buys": "q_C, the parameter the A-vs-C power calculation needs from the "
                     "CORRECT ARM",
             "cost_usd": COST_SEARCH},
            {"dispatch": "C exposed answerer", "count": 1,
             "buys": "one closed/exposed grader pair, (A,C)",
             "cost_usd": COST_EXPOSED_ANSWERER},
            {"dispatch": "D exposed answerer", "count": 1,
             "buys": "the second closed/exposed grader pair, (A,D). This is the cheapest "
                     "pair in the design: one dispatch instead of a whole extra item.",
             "cost_usd": COST_EXPOSED_ANSWERER},
        ],
        "deliberately_absent": {
            "an exposed answerer run only to estimate exposure divergence":
                "exposure divergence is measured on the BLOCK, before any answerer. The "
                "exposed answerers here are bought by the grader objective and by nothing "
                "else, which is why there are exactly two of them.",
            "a delta estimate":
                "delta is the estimand. Measuring it on calibration items would size the "
                "run on a first look at its own effect.",
            "repeat dispatches of one query":
                "the artifact is not reproducible by measurement (design draft 12.3); "
                "repeats would estimate runtime variance, which no sizing decision reads.",
        },
    }


def cost_plan(n_authored: int, n_screened: int) -> dict:
    screen = n_authored * COST_SCREEN_ONLY_ITEM
    full = n_screened * COST_FULL_CALIBRATION_ITEM
    return {
        "authored_items": n_authored,
        "screen_passing_items": n_screened,
        "dispatches": n_authored * 1 + n_screened * 5,
        "screen_cost_usd": round(screen, 2),
        "full_item_cost_usd": round(full, 2),
        "total_cost_usd": round(screen + full, 2),
    }


def calibration_plan() -> dict:
    """The frozen sequential plan. Batch sizes and the cap are fixed here, before
    any calibration datum exists, which is the only thing that makes a sequential
    scheme legitimate."""
    b1 = cost_plan(BATCH1_AUTHORED, BATCH1_TARGET_SCREENED)
    maxa = BATCH1_AUTHORED + 2 * BATCHN_AUTHORED
    mx = cost_plan(maxa, MAX_CALIBRATION_SCREENED)
    return {
        "batch_1": {**b1, "development_subset": BATCH1_DEV,
                    "grader_validation_holdout": BATCH1_HOLDOUT,
                    "grader_pairs_in_holdout": 2 * BATCH1_HOLDOUT,
                    "g_one_bound_if_holdout_clean": round(cp_upper(0, 2 * BATCH1_HOLDOUT), 4)},
        "batch_2_and_3_each": {**cost_plan(BATCHN_AUTHORED, BATCHN_TARGET_SCREENED),
                               "development_subset": 8, "grader_validation_holdout": 16},
        "maximum": {**mx, "cap_rule": "at the cap the calibration bank costs about what "
                                      "the production run costs. Spending more on "
                                      "calibration than on the experiment is not caution, "
                                      "it is a different experiment."},
        "why_not_the_old_multiplier": {
            "old_rule": ">= 3x production size",
            "old_rule_derivation": "NONE. Asserted in the authoring protocol 1, design "
                                   "draft 2.4, NEXT.md and the 2026-09-02 decision-log "
                                   "entry; computed in none of them.",
            "it_is_wrong_in_both_directions": {
                "too_small_for_what_it_had_to_measure":
                    "design draft 2.4 dispatches calibration items CLOSED-BOOK ONLY. At "
                    "any multiple of production that measures `p` and nothing else: no "
                    "q_C (needs a query-writer and a C search), no q_D (needs the fixed "
                    "search), and no grader behaviour on EXPOSED answers -- which is the "
                    "one grader parameter the power model says is design-breaking. A bank "
                    "three times the size of the run would still have left the sizing "
                    "resting on assumed values.",
                "too_large_under_the_realized_structure":
                    cost_plan(200, 150),
                "production_run_for_comparison": {
                    "items": 102,
                    "total_cost_usd": round(102 * COST_PRODUCTION_ITEM, 2)},
            },
            "replaced_by": "the four decisions above, each with its own precision "
                           "requirement and its own stopping rule",
        },
    }


# --------------------------------------------------------------------------- #
# the ledger row
# --------------------------------------------------------------------------- #

@dataclass
class CalibrationRow:
    """One calibration item, and every quantity the sizing decisions read.

    `None` means NOT OBSERVED, exactly as in `lab.stage0b_harness.DispatchRow`. It
    never means zero and it never means False.

    THE ANTI-OUTCOME-SHOPPING FIELD ORDER. `hand_verdict_*` is recorded BEFORE
    `grader_verdict_*` is computed, and `hand_verdict_recorded_first` asserts it.
    A grader defect is then a disagreement between two things written down in a
    fixed order, rather than a judgement made after seeing which way it went.
    """
    # identity and the wall
    item_id: str
    pool: str                                  # always "calibration"
    subset: str                                # "development" | "grader_validation_holdout"
    batch: int
    production_barred: bool                    # always True, asserted per row

    # the item
    stem: str
    route: str                                 # exact_entity | numeric | boolean
    accept_aliases: list[str]
    reject_aliases: list[str]
    key_provenance: str
    query_subject: str
    anchor_as_written: str

    # stage 1 -- the screen
    fixed_query: str | None = None
    d_raw_artifact_sha: str | None = None
    d_injected_block: str | None = None
    d_injected_block_sha: str | None = None
    d_relevance: dict | None = None
    d_divergent: bool | None = None            # THE SCREEN
    d_reject_in_links_only: bool | None = None
    d_query_faithful: bool | None = None
    screen_passed: bool | None = None

    # stage 2 -- the C arm
    model_written_query: str | None = None
    c_raw_artifact_sha: str | None = None
    c_injected_block: str | None = None
    c_injected_block_sha: str | None = None
    c_relevance: dict | None = None
    c_divergent: bool | None = None            # q_C's numerator
    c_reject_in_links_only: bool | None = None
    c_query_faithful: bool | None = None

    # stage 2 -- the three answers
    closed_answer: str | None = None
    c_exposed_answer: str | None = None
    d_exposed_answer: str | None = None

    # adjudication, recorded BEFORE grading
    hand_verdict_closed: str | None = None     # CORRECT | INCORRECT | ABSTAIN
    hand_verdict_c: str | None = None
    hand_verdict_d: str | None = None
    hand_verdict_recorded_first: bool | None = None
    hand_adjudicator: str | None = None

    # the candidate grader, at a recorded fingerprint
    grader_fingerprint: str | None = None
    grader_verdict_closed: str | None = None
    grader_verdict_c: str | None = None
    grader_verdict_d: str | None = None

    # derived defect flags -- computed, never entered by hand
    defect_closed: bool | None = None
    defect_c: bool | None = None
    defect_d: bool | None = None

    # provenance for every dispatch that made this row
    served_models: dict = field(default_factory=dict)      # stage -> [model, ...]
    configured_effort: dict = field(default_factory=dict)  # stage -> command line
    realized_tool_surface: dict = field(default_factory=dict)
    web_search_requests: dict = field(default_factory=dict)  # stage -> authoritative count
    cost_usd: dict = field(default_factory=dict)
    session_ids: dict = field(default_factory=dict)
    failure: str | None = None
    failure_stage: str | None = None

    def to_json(self) -> dict:
        return asdict(self)


REQUIRED_FOR_EACH_STATISTIC = {
    # statistic -> the CalibrationRow fields it is computed from. Nothing may feed
    # the power model without an entry here.
    "s":       ["screen_passed"],
    "p":       ["screen_passed", "grader_verdict_closed"],
    "q_C":     ["screen_passed", "c_divergent"],
    "q_D":     ["screen_passed", "d_divergent"],
    "g_one":   ["subset", "hand_verdict_closed", "hand_verdict_c", "hand_verdict_d",
                "grader_verdict_closed", "grader_verdict_c", "grader_verdict_d"],
    "g_both":  ["subset", "hand_verdict_closed", "hand_verdict_c", "hand_verdict_d",
                "grader_verdict_closed", "grader_verdict_c", "grader_verdict_d"],
    "query_fidelity": ["c_query_faithful", "d_query_faithful"],
}


def validate_row(row: CalibrationRow) -> list[str]:
    """Structural problems that must be fixed before the row can feed a statistic."""
    p: list[str] = []
    if row.pool != "calibration":
        p.append(f"{row.item_id}: pool must be 'calibration', got {row.pool!r}")
    if not row.production_barred:
        p.append(f"{row.item_id}: production_barred must be True for every calibration item")
    if row.subset not in ("development", "grader_validation_holdout"):
        p.append(f"{row.item_id}: subset must be development or grader_validation_holdout")
    if row.route not in ("exact_entity", "numeric", "boolean"):
        p.append(f"{row.item_id}: unknown route {row.route!r}")
    if not row.key_provenance:
        p.append(f"{row.item_id}: key provenance is required before any dispatch")
    if row.screen_passed and row.d_divergent is not True:
        p.append(f"{row.item_id}: screen_passed with d_divergent={row.d_divergent!r}")
    graded = any(v is not None for v in (row.grader_verdict_closed, row.grader_verdict_c,
                                         row.grader_verdict_d))
    if graded and not row.hand_verdict_recorded_first:
        p.append(f"{row.item_id}: graded without hand_verdict_recorded_first -- the "
                 f"adjudication order is what makes a defect a measurement")
    if graded and not row.grader_fingerprint:
        p.append(f"{row.item_id}: graded without recording the grader fingerprint")
    return p


# --------------------------------------------------------------------------- #
# the preregistered statistics, and the frozen decision rules
# --------------------------------------------------------------------------- #

def _pair_defects(row: CalibrationRow) -> tuple[int, int]:
    """(g_one events, g_both events) over this row's TWO closed/exposed pairs.

    The pairs are (closed, C) and (closed, D). Pooling them is licensed by the
    packets being byte-identical between C and D; `exchangeability_check` reports
    the two counts separately so the licence is inspectable.
    """
    hv = (row.hand_verdict_closed, row.hand_verdict_c, row.hand_verdict_d)
    gv = (row.grader_verdict_closed, row.grader_verdict_c, row.grader_verdict_d)
    if any(x is None for x in hv + gv):
        return 0, 0
    d_closed = hv[0] != gv[0]
    one = both = 0
    for i in (1, 2):
        d_exposed = hv[i] != gv[i]
        if d_closed and d_exposed:
            both += 1
        elif d_closed or d_exposed:
            one += 1
    return one, both


def calibration_statistics(rows: list[CalibrationRow]) -> dict:
    """ONLY the preregistered quantities. Nothing else may be computed from a
    calibration bank before the stopping decision is taken, because a statistic
    invented after seeing the data is a stopping rule invented after seeing the
    data."""
    authored = len(rows)
    screened = [r for r in rows if r.screen_passed]
    n_s = len(screened)
    n_pass = sum(1 for r in rows if r.screen_passed)

    closed_graded = [r for r in screened if r.grader_verdict_closed is not None]
    k_p_err = sum(1 for r in closed_graded if r.grader_verdict_closed != "CORRECT")
    n_p = len(closed_graded)

    c_known = [r for r in screened if r.c_divergent is not None]
    k_qc = sum(1 for r in c_known if r.c_divergent)

    holdout = [r for r in screened if r.subset == "grader_validation_holdout"]
    adjudicated = [r for r in holdout
                   if r.hand_verdict_closed is not None and r.grader_verdict_closed is not None]
    pairs = 2 * len(adjudicated)
    k_one = sum(_pair_defects(r)[0] for r in adjudicated)
    k_both = sum(_pair_defects(r)[1] for r in adjudicated)

    p_hat = (n_p - k_p_err) / n_p if n_p else None
    q_c_hat = k_qc / len(c_known) if c_known else None
    g_one_up = cp_upper(k_one, pairs) if pairs else None
    g_both_up = cp_upper(k_both, pairs) if pairs else None

    n_prod = (required_production_n(p_hat, q_c_hat, g_one_up)
              if None not in (p_hat, q_c_hat, g_one_up) and q_c_hat > 0 else None)

    return {
        "authored_items": authored,
        "screen": {
            "n_authored": authored, "n_passed": n_pass,
            "s_hat": round(n_pass / authored, 4) if authored else None,
        },
        "p": {"n": n_p, "errors": k_p_err,
              "p_hat": round(p_hat, 4) if p_hat is not None else None,
              "p_lower_95": round(cp_lower(n_p - k_p_err, n_p), 4) if n_p else None,
              "target_lower": P_TARGET_LOWER},
        "q_C": {"n": len(c_known), "divergent": k_qc,
                "q_C_hat": round(q_c_hat, 4) if q_c_hat is not None else None,
                "arm": "C -- model-written query, conditional on screen-passing"},
        "q_D": {"value_by_construction": 1.0, "n_screened": n_s,
                "note": "the screen ADMITS on d_divergent, so this is not an estimate"},
        "grader": {
            "holdout_items": len(adjudicated), "pairs": pairs,
            "k_g_one": k_one, "k_g_both": k_both,
            "g_one_upper_95": round(g_one_up, 4) if g_one_up is not None else None,
            "g_both_upper_95": round(g_both_up, 4) if g_both_up is not None else None,
            "exchangeability_check": {
                "defects_on_C_pairs": sum(
                    1 for r in adjudicated
                    if (r.hand_verdict_c != r.grader_verdict_c)),
                "defects_on_D_pairs": sum(
                    1 for r in adjudicated
                    if (r.hand_verdict_d != r.grader_verdict_d)),
                "note": "pooling (A,C) with (A,D) assumes the two are exchangeable for a "
                        "grader defect. A large split between these counts falsifies that "
                        "and forces the bound to be recomputed on C pairs alone.",
            },
        },
        "n_prod_required": n_prod,
        "n_prod_required_if_grader_were_perfect": (
            required_production_n(p_hat, q_c_hat, 0.0)
            if None not in (p_hat, q_c_hat) and q_c_hat and q_c_hat > 0 else None),
    }


PASS = "PASS"
CONTINUE = "CONTINUE"
REVISE_RECIPE = "REVISE_ITEM_RECIPE"
REVISE_GRADER = "REVISE_GRADER"
REVISE_DESIGN = "REVISE_STAGE0B_DESIGN"


def decide(stats: dict, n_screened_total: int, grader_repaired_since_holdout: bool = False,
           holdout_burned: bool = False) -> dict:
    """The frozen decision rule. Fixed BEFORE calibration data exists; a later
    session may read it, never rewrite it.

    Evaluated in this order, and the order is part of the rule: a recipe that
    fails cannot be rescued by a grader repair, and a grader that was repaired on
    its own validation set has no bound to report at all.
    """
    p, q, g = stats["p"], stats["q_C"], stats["grader"]
    reasons: list[str] = []

    # ---- REVISE STAGE 0B DESIGN -- the estimand itself is unreachable --------
    if q["q_C_hat"] is not None and q["q_C_hat"] >= Q_C_MIN_VIABLE:
        perfect = stats["n_prod_required_if_grader_were_perfect"]
        if perfect is None or perfect > N_PROD_VIABLE_CAP:
            return {"verdict": REVISE_DESIGN, "reasons": [
                f"even with a PERFECT grader the required production n is {perfect}, "
                f"beyond the viability cap {N_PROD_VIABLE_CAP}. No instrument repair and "
                f"no affordable n reaches the estimand."]}
    if n_screened_total >= MAX_CALIBRATION_SCREENED:
        pass_now = _pass_conditions(stats)
        if pass_now:
            return {"verdict": REVISE_DESIGN, "reasons": [
                f"the calibration cap of {MAX_CALIBRATION_SCREENED} screen-passing items is "
                f"reached and PASS is still unmet: " + "; ".join(pass_now)]}

    # ---- REVISE ITEM RECIPE -- more items cannot fix a point estimate --------
    if stats["screen"]["s_hat"] is not None and stats["screen"]["s_hat"] < SCREEN_PASS_MIN_VIABLE:
        reasons.append(f"screen pass rate {stats['screen']['s_hat']} < {SCREEN_PASS_MIN_VIABLE}: "
                       f"the recipe does not produce items this search environment can dose")
    if p["p_hat"] is not None and p["n"] >= 30 and p["p_hat"] < P_TARGET_LOWER:
        reasons.append(f"closed-book accuracy {p['p_hat']} < {P_TARGET_LOWER} on {p['n']} items: "
                       f"the recipe is too hard, and harder items add cancellation not power")
    if q["q_C_hat"] is not None and q["q_C_hat"] < Q_C_MIN_VIABLE:
        reasons.append(f"q_C {q['q_C_hat']} < {Q_C_MIN_VIABLE}: the model-written query "
                       f"almost never returns a displacing claim, so the C arm is undosed")
    if reasons:
        return {"verdict": REVISE_RECIPE, "reasons": reasons}

    # ---- REVISE GRADER ------------------------------------------------------
    if g["k_g_one"] or g["k_g_both"]:
        return {"verdict": REVISE_GRADER, "reasons": [
            f"{g['k_g_one']} asymmetric and {g['k_g_both']} symmetric grader defects on "
            f"{g['pairs']} held-out pairs. Repair from a GENERAL semantic rule on the "
            f"development subset, re-run the Stage 0A-M regression corpus and the semantic "
            f"corpus with zero regressions, then validate on a FRESH holdout -- the current "
            f"holdout has now informed the repair and is spent."]}
    if grader_repaired_since_holdout or holdout_burned:
        return {"verdict": CONTINUE, "reasons": [
            "the grader changed after the holdout was scored, so the holdout's bound no "
            "longer describes the grader that will be frozen. A fresh holdout is required."]}

    # ---- PASS / CONTINUE ----------------------------------------------------
    unmet = _pass_conditions(stats)
    if not unmet:
        return {"verdict": PASS, "reasons": [],
                "authorizes": ["freeze lab/grading_v2.py at its recorded fingerprint",
                               "re-derive power from the measured p, q_C and the g_one bound",
                               "run lab.stage0b_cvd.authorize on the measured values",
                               f"author {stats['n_prod_required']} primary production items "
                               f"plus "
                               f"{negative_control_n(stats['n_prod_required'])['n_control_recommended']}"
                               f" negative controls"]}
    return {"verdict": CONTINUE, "reasons": unmet,
            "next_batch_screen_passing_items": BATCHN_TARGET_SCREENED,
            "next_batch_authored_items": BATCHN_AUTHORED}


def _pass_conditions(stats: dict) -> list[str]:
    """Unmet PASS conditions, as strings. Empty list means PASS."""
    p, g = stats["p"], stats["grader"]
    unmet = []
    if p["p_lower_95"] is None or p["p_lower_95"] < P_TARGET_LOWER:
        unmet.append(f"p lower bound {p['p_lower_95']} has not cleared {P_TARGET_LOWER}")
    if g["g_one_upper_95"] is None or g["g_one_upper_95"] > G_ONE_BOUND_FOR_PASS:
        unmet.append(f"grader asymmetry bound {g['g_one_upper_95']} has not reached "
                     f"{G_ONE_BOUND_FOR_PASS}")
    n = stats["n_prod_required"]
    if n is None or n > N_PROD_AFFORDABLE_CAP:
        unmet.append(f"required production n {n} exceeds the affordable cap "
                     f"{N_PROD_AFFORDABLE_CAP}")
    return unmet


# --------------------------------------------------------------------------- #
# report
# --------------------------------------------------------------------------- #

def report() -> dict:
    ref = 50
    nc = negative_control_n(ref)
    return {
        "what_this_is": "Stage 0B pre-calibration design reconciliation. No calibration "
                        "datum exists. Every threshold here is fixed BEFORE the first "
                        "calibration dispatch.",
        "parameters": PARAMETER_GLOSSARY,
        "delta_gap_restated": {
            "legacy_on_displacement_scale": DELTA_GAP_ON_DISPLACEMENT_SCALE_LEGACY,
            "implied_exposure_gap_at_delta_0.30":
                round(DELTA_GAP_ON_DISPLACEMENT_SCALE_LEGACY / DELTA_PREREGISTERED, 4),
            "why_that_is_not_a_target": "a 0.667 difference in exposure rate between the "
                                        "two queries is not something anyone would have "
                                        "preregistered had the number been written in the "
                                        "units it is measured in",
            "restated_exposure_gap": Q_GAP_PREREGISTERED,
            "implied_displacement_gap": round(Q_GAP_IMPLIED_DISPLACEMENT_GAP, 4),
        },
        "negative_control": {**nc, "provenance": provenance_of_the_two_control_numbers()},
        "thresholds": thresholds_with_derivations(ref),
        "dispatch_structure": dispatch_structure(),
        "plan": calibration_plan(),
        "sizing_sensitivity": {
            "n_prod at q_C, g_one=0": {str(q): required_production_n(0.95, q, 0.0)
                                       for q in (0.15, 0.25, 0.35, 0.50, 0.70, 0.90)},
            "n_prod at g_one, q_C=0.50": {str(g): required_production_n(0.95, 0.50, g)
                                          for g in (0.0, 0.014, 0.04, 0.0798, 0.10)},
        },
        "decision_rules": {
            "PASS": _pass_conditions({
                "p": {"p_lower_95": None}, "grader": {"g_one_upper_95": None},
                "n_prod_required": None}),
            "order": [REVISE_DESIGN, REVISE_RECIPE, REVISE_GRADER, PASS, CONTINUE],
            "max_calibration_screen_passing_items": MAX_CALIBRATION_SCREENED,
        },
    }


def main() -> int:
    import pathlib
    out = pathlib.Path(__file__).resolve().parent.parent / "runs" / "exp004_stage0b_design"
    out.mkdir(parents=True, exist_ok=True)
    doc = report()
    (out / "calibration_plan.json").write_text(json.dumps(doc, indent=1) + "\n")
    nc = doc["negative_control"]
    print(f"negative control: n={nc['n_control_required']} "
          f"(threshold {nc['minimum_rejectable_harm_rate']}, "
          f"clean bound {nc['bound_at_that_n_if_clean']})")
    b1, mx = doc["plan"]["batch_1"], doc["plan"]["maximum"]
    print(f"batch 1: {b1['authored_items']} authored -> {b1['screen_passing_items']} screened, "
          f"{b1['dispatches']} dispatches, ${b1['total_cost_usd']}")
    print(f"maximum: {mx['authored_items']} authored -> {mx['screen_passing_items']} screened, "
          f"{mx['dispatches']} dispatches, ${mx['total_cost_usd']}")
    print("n_prod at g_one:", json.dumps(doc["sizing_sensitivity"]["n_prod at g_one, q_C=0.50"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
