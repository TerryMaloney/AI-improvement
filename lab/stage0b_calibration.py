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
`g_one` below 0.014 with zero observed defects needs 213 clean ITEMS, which is
four times the production run. **Calibration cannot certify that the grader is
good enough for n=50.** So the design does the only honest thing available: it
measures the bound it CAN reach and sizes production AT that bound.

THE SAMPLING UNIT IS THE ITEM. CORRECTED 2026-09-03 (second red team).
----------------------------------------------------------------------
An earlier version of this module pooled the two closed/exposed pairs of an item,
(A,C) and (A,D), and applied a Clopper-Pearson bound at n = 2 x items. That was
**invalid, and anti-conservative in the one direction that matters.**

1.  **The two indicators share a component, and share it completely.** Both pairs
    are built from the SAME closed-arm verdict on the SAME closed-arm answer. A
    single closed-arm grader defect produced TWO counted `g_one` events. One
    underlying event, two "observations": that is not a second draw, it is the
    same draw written down twice. Clopper-Pearson at n=2m assumes 2m independent
    Bernoulli trials, so the interval it returns is NARROWER than the evidence
    supports -- and an instrument-defect bound that is too narrow under-sizes the
    production run. Exchangeability is not independence, and the old note
    conflated them.

2.  **It bounded the wrong estimand.** `g_one` in lab/stage0b_power.py is a
    property of the A-vs-C item pair, because A-vs-C IS the primary comparison.
    An (A,D) defect describes arm D's answer form. Folding it in changes what is
    being bounded, and it does so on an assumption about MODEL BEHAVIOUR (that C
    and D answers take the same form) that no packet-level symmetry establishes:
    the two blocks differ, so the two answers may differ.

**Corrected: the bound is computed on the (A,C) pair only, with the calibration
ITEM as the independent unit** -- which is exactly the unit the power model's own
generative assumption uses ("all probabilities per-item and independent across
items"). The (A,D) pair is retained and reported as a DIAGNOSTIC and as the only
exercise arm D's answer form gets before production; it enters no bound. An
item-level UNION bound (a defect in either pair) is reported alongside as a
conservative companion, and it too uses one unit per item.

Cost of the correction: a clean holdout of 24 items bounded `g_one` at 0.0605
under the invalid pooling and bounds it at 0.1173 under the valid unit. The
batch-1 holdout therefore rises from 24 items to 36, which is the smallest clean
holdout whose bound reaches the PASS threshold of 0.08 at all. Under the old
arithmetic batch 1 could not have passed even with a flawless holdout.

WHAT THE SELECTION RULE DOES TO THE PARAMETERS, AND WHAT IT DOES NOT
--------------------------------------------------------------------
Production items are selected by a divergence screen on the FIXED-QUERY block.
An earlier version concluded from this that `q_D = 1.0 BY CONSTRUCTION`.
**That was false, and the repository already contained its refutation.**

The same design records that the search artifact is NOT reproducible: two
dispatches of an identical query return a different synthesised paragraph. And
`lab/stage0b_harness.py:run_arm` executes the fixed query FRESHLY at answering
time. So the screened block is not the injected block, and divergence at screen
time does not transfer to the trial. `q_D = 1` was true of an artifact the
experiment never uses.

**Corrected: arm D re-executes its fixed query at answering time (design option
B), and the parameter is `r_D`** -- the probability that a RE-EXECUTION of the
frozen fixed query on a screened item is again divergent. It is measured, not
assumed. The screen is therefore a filter on item PROPENSITY, not a guarantee
about the dose: it selects items whose fixed query tends to return a displacing
claim, and `r_D` says how often that tendency shows up again on the day.

Option B was chosen over freezing the screened artifact because freezing it would
give arm D a stale block while arm C's is contemporaneous, breaking the single
structural guarantee the C/D contrast rests on -- `execute_search(query)` takes
one parameter, so C and D have nothing else to differ in. Trading that for a
literal `q_D = 1` would buy a true sentence about a treatment nobody runs.

Every calibration parameter is CONDITIONAL ON SCREEN-PASSING, because every
production item is. Calibration items that fail the screen contribute to exactly
one statistic: the screen pass rate `s`.

Nothing here dispatches, and nothing here reads a production outcome.
"""
from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from fractions import Fraction

from lab.stage0am import _cp_upper           # the frozen exact Clopper-Pearson limit
from lab.stage0b_adjudication import adjudication_plan
from lab.stage0b_power import Scenario, analyse_scenario

# --------------------------------------------------------------------------- #
# preregistered design commitments -- fixed BEFORE any calibration datum exists
# --------------------------------------------------------------------------- #

ALPHA_PRIMARY = Fraction(1, 20)      # A-vs-C, K=1 family
TARGET_POWER = 0.80
CONF = 0.95

# TERMINOLOGY, corrected 2026-09-03 (second red team).
# Stage 0B has NO FROZEN PREREGISTRATION YET. The design draft is explicitly
# "DRAFT. Not frozen", and the causal contract validates as `draft`. So no Stage
# 0B quantity is "preregistered" in the sense Stage 0A-M's were; they are
# PRE-CALIBRATION COMMITMENTS -- fixed before any calibration outcome exists,
# which is what makes them binding, and which is a real but weaker claim than
# preregistration. Names carry that distinction, and PARAMETER_LINEAGE records
# where each value came from.
PREREGISTRATION_STATUS = (
    "Stage 0B is NOT preregistered. Every threshold in this module is a "
    "PRE-CALIBRATION COMMITMENT: fixed and fingerprinted before the first "
    "calibration outcome exists. They become preregistration at design freeze, "
    "which has not happened and cannot happen until the bank has run."
)

# `delta` is the susceptibility the experiment exists to ESTIMATE. Calibration
# cannot measure it without dispatching exposed answerers on items whose closed
# outcome is already known, which is a treated outcome on a calibration item and
# buys nothing the sizing needs. It stays a preregistered MINIMUM INTERESTING
# EFFECT, exactly as it was in the design draft.
DELTA_PREREGISTERED = 0.30

# The target closed-book band (design draft 2.2). Below 0.90 the one-sided
# paired test loses power to repair/harm cancellation faster than n can buy it.
#
# CORRECTED 2026-09-03 (second red team). The previous PASS rule required the 95%
# one-sided LOWER bound on p to clear 0.90 -- a CERTIFICATION that p exceeds the
# band edge. Its operating characteristics make it unusable as a gate:
#
#     n=36  admits ZERO closed-book errors; P(pass | true p = 0.95) = 0.158
#     n=60  admits one;                     P(pass | true p = 0.95) = 0.192
#     n=84  admits three;                   P(pass | true p = 0.95) = 0.390
#     any n P(pass | true p = 0.90) <= 0.05, by construction of the bound
#
# A recipe sitting EXACTLY on the design point of 0.95 would fail that gate about
# five times in six at n=36, drive the bank to its cap, and there be declared a
# design failure. The rule tested a claim the design never made: design draft 2.2
# sets a BAND on the measured accuracy, not a certification that its edge is
# exceeded. It is withdrawn, and p now plays two separate honest roles:
#   * the BAND is checked on the POINT ESTIMATE, as written;
#   * SIZING uses the 95% LOWER bound -- the conservative direction, since a lower
#     p means fewer at-risk items and so a larger required n.
# Errors in the bank therefore cost production items instead of triggering a
# near-certain false stop, and the affordability cap stays the binding gate.
P_BAND_LOWER = 0.90
P_TARGET_LOWER = P_BAND_LOWER        # retained name; cited by committed artifacts

THE_P_RULE = {
    "band_check": "p_hat >= 0.90 (design draft 2.2, on the point estimate)",
    "sizing": "required_production_n reads the 95% one-sided LOWER bound on p",
    "certification_NOT_required":
        "a 95% lower bound clearing 0.90 is not a PASS condition. Requiring it would "
        "reject a recipe sitting on the design point 5 times in 6 at n=36.",
    "operating_characteristics_of_the_withdrawn_rule": {
        "36": {"max_errors_admitted": 0, "P_pass_at_p_0.90": 0.0225,
               "P_pass_at_p_0.95": 0.1578, "P_pass_at_p_1.00": 1.0},
        "60": {"max_errors_admitted": 1, "P_pass_at_p_0.90": 0.0138,
               "P_pass_at_p_0.95": 0.1916, "P_pass_at_p_1.00": 1.0},
        "84": {"max_errors_admitted": 3, "P_pass_at_p_0.90": 0.0264,
               "P_pass_at_p_0.95": 0.3897, "P_pass_at_p_1.00": 1.0},
    },
}

# PASS thresholds, all derived below in `thresholds_with_derivations()`.
G_ONE_BOUND_FOR_PASS = 0.08          # loosest bound that still keeps n_prod <= 90
N_PROD_AFFORDABLE_CAP = 90           # PASS ceiling on the re-derived production n
N_PROD_VIABLE_CAP = 120              # beyond this the estimand is unreachable
Q_C_MIN_VIABLE = 0.15                # below this n_prod > 156; the arm cannot be dosed
SCREEN_PASS_MIN_VIABLE = 0.40        # below this authoring costs more than the run
R_D_MIN_VIABLE = 0.30                # below this the screen has selected items whose
                                     # fixed query does not reliably re-deliver a dose,
                                     # and arm D stops doing its interpretive job
# The q_C sensitivity table, COMPUTED ONCE and recorded rather than recomputed.
# Provenance: required_production_n(p=0.95, q_C=q, g_one=0.0, delta=0.30,
# alpha=1/20, target=0.80, n_max=400), run 2026-09-03. It is recorded because the
# low-q_C entries need a scan to n=400 whose unreachable cases cost ~60s each, and
# an artifact nobody can regenerate in a test is worse than one nobody regenerates
# at all. `test_the_recorded_sensitivity_table_matches_a_live_recomputation`
# re-derives every entry cheap enough to re-derive.
Q_C_SENSITIVITY_AT_PERFECT_GRADER = {
    0.10: None,   # unreachable at n <= 400
    0.15: 156, 0.20: 117, 0.25: 93, 0.30: 78, 0.35: 66, 0.40: 58, 0.45: 52,
    0.50: 46, 0.55: 42, 0.60: 38, 0.65: 35, 0.70: 33, 0.75: 31, 0.80: 29,
    0.85: 27, 0.90: 25, 0.95: 24, 1.00: 23,
}

MIN_ITEMS_FOR_SIZING = 20            # below this a "required production n" is an
                                     # artefact of the confidence bound, not a size
MAX_RECIPE_ESCALATION_RATE = 0.15    # share of answers escalated for PREMISE_CONTEST or
                                     # NO_KEY_MATCH -- both are recipe defects, not
                                     # grader defects

# Batch sizes. AUTHORED counts include items the screen will reject.
# RESIZED 2026-09-03 (second red team). The holdout is what carries the grader
# bound, and with the ITEM as the valid unit a 24-item holdout bounds `g_one` at
# 0.1173 -- above the PASS threshold of 0.08. Batch 1 could not have passed with a
# flawless holdout. 36 is the smallest clean holdout that reaches the threshold at
# all, so it is the smallest batch 1 that can terminate the sequence.
BATCH1_AUTHORED = 64
BATCH1_TARGET_SCREENED = 48          # 12 development + 36 grader-validation holdout
BATCH1_DEV = 12
BATCH1_HOLDOUT = 36
BATCHN_AUTHORED = 22
BATCHN_TARGET_SCREENED = 16          # 4 development + 12 holdout
MAX_CALIBRATION_SCREENED = 80        # safety cap: at this size calibration costs
                                     # about what the production run costs
# The authored:screened ratio assumes the canary screen pass rate. It sizes the
# AUTHORING effort only; if the realized rate differs, more items are authored to
# the same recipe -- which is not outcome selection, because the screen dispatches
# no answerer.
ASSUMED_SCREEN_PASS_RATE = 0.75

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
# A screen-passing calibration item now costs SIX further dispatches, not five.
# The extra one is arm D's PRODUCTION search -- a second, fresh execution of the
# frozen fixed query, distinct from the screen. It is what measures `r_D`, and it
# exists because the screened block is not the injected block (see the module
# header). Without it the bank would report a divergence rate for an artifact the
# experiment never uses.
COST_FULL_CALIBRATION_ITEM = (COST_CLOSED_ANSWERER + COST_QUERY_WRITER
                              + COST_SEARCH          # C model-query search
                              + COST_SEARCH          # D production search (measures r_D)
                              + 2 * COST_EXPOSED_ANSWERER)
DISPATCHES_PER_SCREENED_CALIBRATION_ITEM = 6         # excludes the screen itself
COST_PRODUCTION_ITEM = (COST_CLOSED_ANSWERER                       # arm A
                        + COST_QUERY_WRITER + COST_SEARCH + COST_EXPOSED_ANSWERER   # arm C
                        + COST_SEARCH + COST_EXPOSED_ANSWERER)                      # arm D
DISPATCHES_PER_PRODUCTION_ITEM = 6
# Production does NOT re-run the screen: the screen happened at authoring time and
# is pre-treatment. Production arm D executes the fixed query once, exactly as
# calibration's D production search does.


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
    "r_D": {
        "definition": "P(a RE-EXECUTION of the item's frozen fixed query, at answering "
                      "time, returns a block whose runtime-synthesised summary contains "
                      "at least one predeclared reject alias | the item passed the screen)",
        "arm": "D -- fixed anchor-preserving query, executed fresh in the trial",
        "measured_by": "a second fixed-query search per screen-passing calibration item, "
                       "distinct from the screen dispatch",
        "replaces": "q_D, which was asserted to be 1.0 BY CONSTRUCTION because the "
                    "divergence screen admits on exactly that condition. THAT WAS FALSE, "
                    "and this repository already held the refutation: the search artifact "
                    "is not reproducible (two dispatches of one query return a different "
                    "synthesised paragraph), and lab/stage0b_harness.py:run_arm executes "
                    "arm D's fixed query FRESHLY at answering time. The screened block is "
                    "not the injected block, so screen-time divergence does not transfer "
                    "to the trial. q_D = 1 was true of an artifact the experiment never "
                    "uses.",
        "what_the_screen_actually_buys": "a filter on item PROPENSITY, not a guaranteed "
                                         "dose. It selects items whose fixed query tends "
                                         "to return a displacing claim; r_D says how often "
                                         "that tendency shows up again on the day.",
        "a_nondivergent_reexecution_is_not_a_failure": "it is the measurement. Voiding "
                                                       "such a trial would condition the "
                                                       "sample on a realized treatment "
                                                       "property of one arm.",
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
#     delta_C = q_C * delta          delta_D = r_D * delta
#
# CORRECTED 2026-09-03 (second red team): this used to read `delta_D = q_D * delta`
# with q_D pinned at 1, and concluded that D must displace at least as often as C.
# That conclusion is withdrawn along with its premise. Both arms now carry a
# MEASURED, sub-1 exposure rate from a contemporaneous search, and neither
# direction of the C-vs-D contrast is forced by the design. The test was already
# two-sided and stays two-sided -- now for the original reason rather than in spite
# of a structural asymmetry.

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
# RENAMED 2026-09-03 (second red team) from `Q_GAP_PREREGISTERED`. The 0.20
# displacement-scale gap was committed 2026-09-02, before the runtime was
# characterised; the 0.25 exposure-scale restatement was created at 120620c,
# after it. Neither is part of a frozen preregistration -- Stage 0B has none --
# and calling the newer one "preregistered" would have backdated a commitment by
# a day and a runtime discovery. It is a pre-calibration commitment, which is what
# the name now says.
PRECALIBRATION_COMMITTED_Q_GAP = 0.25   # |q_C - r_D|: a quarter of items change
                                        # exposure status depending on who wrote
                                        # the query
Q_GAP_IMPLIED_DISPLACEMENT_GAP = PRECALIBRATION_COMMITTED_Q_GAP * DELTA_PREREGISTERED

PARAMETER_LINEAGE = {
    "PRECALIBRATION_COMMITTED_Q_GAP": {
        "value": PRECALIBRATION_COMMITTED_Q_GAP,
        "scale": "exposure (|q_C - r_D|)",
        "committed": "2026-09-03, commit 120620c, before any calibration outcome",
        "derived_from": "DELTA_GAP_PREREGISTERED = 0.20 on the displacement scale, "
                        "committed 2026-09-02 in lab/stage0b_cvd.py. At delta=0.30 that "
                        "implies an exposure gap of 0.667, which is not a target anyone "
                        "would have written down in the units the bank observes.",
        "status": "PRE-CALIBRATION COMMITMENT, not preregistration",
    },
    "DELTA_PREREGISTERED": {
        "value": DELTA_PREREGISTERED,
        "committed": "2026-09-02, design draft 7.2 design point",
        "status": "PRE-CALIBRATION COMMITMENT. The name is retained because the "
                  "constant is cited by committed artifacts, but the status is the "
                  "same as everything else here: Stage 0B is not preregistered.",
    },
}


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
                "at which the primary could reject, which is D_min / n_primary",
        "STATUS": "PROVISIONAL. This is a FUNCTION of the final primary n, and the final "
                  "primary n does not exist yet -- it is re-derived from the calibration "
                  "bank. The value at n_primary=50 is quoted throughout the documents "
                  "because 50 is the design draft's superseded recommendation, NOT because "
                  "30 is a commitment. At the currently expected n_primary of 72 the rule "
                  "gives 42. No control item is authored until production n is fixed.",
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
        "P_BAND_LOWER": {
            "value": P_BAND_LOWER,
            "derivation": "design draft 2.2, unchanged: below 0.90 repairs cancel harms in "
                          "the one-sided paired test faster than n buys power back.",
            "applied_to": "the POINT ESTIMATE. Certification was withdrawn 2026-09-03; "
                          "see THE_P_RULE for its operating characteristics.",
            "clean_items_that_certification_would_have_needed":
                n_clean_for_upper_bound(1 - P_BAND_LOWER),
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
            {"dispatch": "D production search (a SECOND fixed-query execution)", "count": 1,
             "buys": "r_D -- the probability that a RE-EXECUTION of the frozen fixed query "
                     "is again divergent. Added 2026-09-03: the screened block is not the "
                     "injected block, because the artifact is not reproducible and arm D "
                     "executes its query freshly at answering time. Without this dispatch "
                     "the bank would report a divergence rate for an artifact the "
                     "experiment never uses.",
             "cost_usd": COST_SEARCH},
            {"dispatch": "C exposed answerer", "count": 1,
             "buys": "the (A,C) closed/exposed grader pair -- THE unit that carries the "
                     "grader bound",
             "cost_usd": COST_EXPOSED_ANSWERER},
            {"dispatch": "D exposed answerer", "count": 1,
             "buys": "the (A,D) pair as a DIAGNOSTIC (it enters no bound -- see the module "
                     "header on why pooling it was invalid), and the only exercise arm D's "
                     "answer form gets before production, which grades arm D too",
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
            "repeat dispatches beyond the two the design needs":
                "the artifact is not reproducible (design draft 12.3), so a THIRD execution "
                "would estimate runtime variance more finely. The two that exist are not "
                "repeats for variance: one is the SCREEN (selection) and one is the "
                "PRODUCTION dose (r_D). No sizing decision reads a third.",
        },
    }


def cost_plan(n_authored: int, n_screened: int) -> dict:
    screen = n_authored * COST_SCREEN_ONLY_ITEM
    full = n_screened * COST_FULL_CALIBRATION_ITEM
    return {
        "authored_items": n_authored,
        "screen_passing_items": n_screened,
        "dispatches": n_authored * 1 + n_screened * DISPATCHES_PER_SCREENED_CALIBRATION_ITEM,
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
                    "grader_observations_in_holdout": BATCH1_HOLDOUT,
                    "unit": "item -- one (A,C) pair per item, NOT two pooled pairs",
                    "g_one_bound_if_holdout_clean": round(cp_upper(0, BATCH1_HOLDOUT), 4),
                    "what_the_invalid_pooling_would_have_claimed":
                        round(cp_upper(0, 2 * BATCH1_HOLDOUT), 4)},
        "batch_2_and_3_each": {**cost_plan(BATCHN_AUTHORED, BATCHN_TARGET_SCREENED),
                               "development_subset": 4, "grader_validation_holdout": 12},
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

    # stage 2 -- arm D's PRODUCTION search: a SECOND, fresh execution of the frozen
    # fixed query, distinct from the screen. This is the block arm D's answerer
    # actually receives, and it is what measures r_D. The screen's block is kept
    # above for provenance and is NEVER injected.
    d_production_raw_artifact_sha: str | None = None
    d_production_injected_block: str | None = None
    d_production_injected_block_sha: str | None = None
    d_production_relevance: dict | None = None
    d_production_divergent: bool | None = None      # r_D's numerator
    d_production_query_faithful: bool | None = None
    screen_block_differs_from_production_block: bool | None = None

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
    # How each reference verdict was reached: the deterministic tier-1 rule that
    # decided it, or the escalation reason that sent it to a human. Recorded so a
    # third party can see WHICH verdicts rest on judgement.
    adjudication_route_closed: str | None = None    # rule name | escalation reason
    adjudication_route_c: str | None = None
    adjudication_route_d: str | None = None
    escalated_to_human: list[str] = field(default_factory=list)   # which of A/C/D

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
    "r_D":     ["screen_passed", "d_production_divergent"],
    "g_one":   ["subset", "hand_verdict_closed", "hand_verdict_c", "hand_verdict_d",
                "grader_verdict_closed", "grader_verdict_c", "grader_verdict_d"],
    "g_both":  ["subset", "hand_verdict_closed", "hand_verdict_c", "hand_verdict_d",
                "grader_verdict_closed", "grader_verdict_c", "grader_verdict_d"],
    "query_fidelity": ["c_query_faithful", "d_query_faithful",
                       "d_production_query_faithful"],
    "adjudication_independence": ["hand_verdict_recorded_first", "hand_adjudicator",
                                  "adjudication_route_closed", "adjudication_route_c",
                                  "adjudication_route_d", "escalated_to_human"],
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
    if graded and not row.hand_adjudicator:
        p.append(f"{row.item_id}: graded without recording WHO produced the reference "
                 f"verdict. A defect rate measured against an unattributed ground truth "
                 f"is not a measurement")
    if row.hand_adjudicator and "grading_v2" in str(row.hand_adjudicator):
        p.append(f"{row.item_id}: the candidate grader may never produce its own ground "
                 f"truth")
    if row.d_production_divergent is not None and not row.screen_passed:
        p.append(f"{row.item_id}: a production D block on an item that did not pass the "
                 f"screen -- r_D is defined only on screen-passing items")
    return p


# --------------------------------------------------------------------------- #
# the preregistered statistics, and the frozen decision rules
# --------------------------------------------------------------------------- #

def _defect(hand: str | None, grader: str | None) -> bool | None:
    """One answer: did the candidate grader disagree with the reference verdict?"""
    if hand is None or grader is None:
        return None
    return hand != grader


def ac_pair_defect(row: CalibrationRow) -> tuple[bool, bool] | None:
    """(g_one event, g_both event) for the A/C pair -- THE unit that feeds the bound.

    The A/C pair is used and the A/D pair is not, for two reasons set out in the
    module header: the two pairs share the closed-arm verdict completely, so
    counting both turns one underlying event into two "observations"; and `g_one`
    in the power model is a property of the A-vs-C pair, because A-vs-C is the
    primary comparison.

    Returns None when the item is not fully adjudicated, so a partial row
    contributes to no numerator and to no denominator.
    """
    c, e = _defect(row.hand_verdict_closed, row.grader_verdict_closed), \
        _defect(row.hand_verdict_c, row.grader_verdict_c)
    if c is None or e is None:
        return None
    return (c != e), (c and e)


def ad_pair_defect(row: CalibrationRow) -> tuple[bool, bool] | None:
    """The same for the A/D pair. DIAGNOSTIC ONLY -- it enters no bound.

    Its jobs: to say whether an exposed-answer grader defect is query-specific,
    and to be the only exercise arm D's answer form gets before production, since
    production grades arm D too.
    """
    c, e = _defect(row.hand_verdict_closed, row.grader_verdict_closed), \
        _defect(row.hand_verdict_d, row.grader_verdict_d)
    if c is None or e is None:
        return None
    return (c != e), (c and e)


def item_union_defect(row: CalibrationRow) -> bool | None:
    """Did EITHER pair reveal an asymmetric defect? One unit per item.

    Reported as a CONSERVATIVE COMPANION to the A/C bound. It bounds a larger
    quantity (a union is at least as likely as either part), so it can only make
    the required production n larger, never smaller. It is not the headline,
    because it does not bound the parameter the power model reads.
    """
    ac, ad = ac_pair_defect(row), ad_pair_defect(row)
    if ac is None and ad is None:
        return None
    return bool((ac and ac[0]) or (ad and ad[0]))


def calibration_statistics(rows: list[CalibrationRow]) -> dict:
    """ONLY the pre-calibration-committed quantities. Nothing else may be computed
    from a calibration bank before the stopping decision is taken, because a
    statistic invented after seeing the data is a stopping rule invented after
    seeing the data."""
    authored = len(rows)
    screened = [r for r in rows if r.screen_passed]
    n_s = len(screened)
    n_pass = n_s

    closed_graded = [r for r in screened if r.grader_verdict_closed is not None]
    k_p_err = sum(1 for r in closed_graded if r.grader_verdict_closed != "CORRECT")
    n_p = len(closed_graded)

    c_known = [r for r in screened if r.c_divergent is not None]
    k_qc = sum(1 for r in c_known if r.c_divergent)

    d_known = [r for r in screened if r.d_production_divergent is not None]
    k_rd = sum(1 for r in d_known if r.d_production_divergent)

    holdout = [r for r in screened if r.subset == "grader_validation_holdout"]
    adjudicated = [r for r in holdout if ac_pair_defect(r) is not None]
    m = len(adjudicated)                      # THE UNIT: one item, one observation
    ac = [ac_pair_defect(r) for r in adjudicated]
    k_one = sum(1 for x in ac if x[0])
    k_both = sum(1 for x in ac if x[1])
    ad = [x for x in (ad_pair_defect(r) for r in adjudicated) if x is not None]
    k_union = sum(1 for r in adjudicated if item_union_defect(r))

    p_hat = (n_p - k_p_err) / n_p if n_p else None
    p_lo = cp_lower(n_p - k_p_err, n_p) if n_p else None
    q_c_hat = k_qc / len(c_known) if c_known else None
    r_d_hat = k_rd / len(d_known) if d_known else None
    g_one_up = cp_upper(k_one, m) if m else None
    g_both_up = cp_upper(k_both, m) if m else None
    g_union_up = cp_upper(k_union, m) if m else None

    # SIZING enters p at its 95% LOWER bound: a lower p means fewer at-risk items,
    # so it is the conservative direction for the required n. It enters g_one at
    # its 95% UPPER bound, for the reason in `required_production_n`.
    # SIZING enters p at its 95% LOWER bound -- a lower p means fewer at-risk items,
    # so it is the conservative direction for the required n -- and g_one at its 95%
    # UPPER bound, for the reason in `required_production_n`.
    #
    # It is NOT computed below the floors. That is not an optimisation. On a handful
    # of items the lower bound on p collapses towards zero (one clean item gives
    # p_lo = 0.05) and the "required n" that falls out is a property of the
    # confidence bound rather than of the recipe; and for a q_C under the viability
    # floor the recipe is about to be sent back anyway. Publishing either number
    # invites someone to act on it.
    sizeable = (None not in (p_lo, q_c_hat, g_one_up)
                and n_p >= MIN_ITEMS_FOR_SIZING
                and q_c_hat >= Q_C_MIN_VIABLE)
    n_prod = required_production_n(p_lo, q_c_hat, g_one_up) if sizeable else None

    return {
        "authored_items": authored,
        "sampling_unit": "the calibration ITEM. One item contributes ONE observation to "
                         "the grader bound, via its (A,C) pair. Pooling (A,C) with (A,D) "
                         "would count one shared closed-arm verdict twice.",
        "screen": {
            "n_authored": authored, "n_passed": n_pass,
            "s_hat": round(n_pass / authored, 4) if authored else None,
        },
        "p": {"n": n_p, "errors": k_p_err,
              "p_hat": round(p_hat, 4) if p_hat is not None else None,
              "p_lower_95": round(p_lo, 4) if p_lo is not None else None,
              "band": [P_BAND_LOWER, 1.00],
              "in_band": (p_hat >= P_BAND_LOWER) if p_hat is not None else None,
              "role": "the BAND is a check on the point estimate, as the design draft "
                      "wrote it. The LOWER BOUND is what sizing uses. Certification that "
                      "p exceeds 0.90 is NOT required -- see THE_P_RULE."},
        "q_C": {"n": len(c_known), "divergent": k_qc,
                "q_C_hat": round(q_c_hat, 4) if q_c_hat is not None else None,
                "arm": "C -- model-written query, conditional on screen-passing"},
        "r_D": {"n": len(d_known), "divergent": k_rd,
                "r_D_hat": round(r_d_hat, 4) if r_d_hat is not None else None,
                "arm": "D -- frozen fixed query RE-EXECUTED at answering time",
                "note": "measured, not assumed. The old `q_D = 1.0 by construction` "
                        "described the screened block, which is not the injected block."},
        "grader": {
            "unit": "item", "holdout_items": m, "observations": m,
            "k_g_one": k_one, "k_g_both": k_both,
            "g_one_upper_95": round(g_one_up, 4) if g_one_up is not None else None,
            "g_both_upper_95": round(g_both_up, 4) if g_both_up is not None else None,
            "conservative_companion": {
                "k_item_union": k_union,
                "g_one_union_upper_95": round(g_union_up, 4) if g_union_up is not None else None,
                "note": "a defect in EITHER pair, one unit per item. Bounds a larger "
                        "quantity than the power model reads, so it can only raise the "
                        "required n. Reported, never substituted for the headline.",
            },
            "arm_D_diagnostic": {
                "k_g_one_on_AD_pairs": sum(1 for x in ad if x[0]),
                "k_g_both_on_AD_pairs": sum(1 for x in ad if x[1]),
                "note": "DIAGNOSTIC ONLY, enters no bound. A large split against the A/C "
                        "counts says an exposed-answer defect is query-specific. It is "
                        "also the only exercise arm D's answer form gets before "
                        "production, which grades arm D too.",
            },
        },
        "n_prod_required": n_prod,
        "n_prod_required_if_grader_were_perfect": (
            required_production_n(p_lo, q_c_hat, 0.0) if sizeable else None),
        "n_prod_not_computed_because": (
            None if sizeable else
            f"not sizeable: {n_p} closed-book graded items (floor {MIN_ITEMS_FOR_SIZING}), "
            f"q_C {q_c_hat} (floor {Q_C_MIN_VIABLE}). A required n derived from too few "
            f"items, or for a recipe under revision, is a number nobody may act on."),
        "negative_control_provisional": (
            negative_control_n(n_prod) if n_prod else None),
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
    # "not computed" is not "unreachable". A bank too small to size against must
    # CONTINUE, never be declared a design failure -- that distinction is the whole
    # reason `n_prod_not_computed_because` exists.
    sizeable = stats.get("n_prod_not_computed_because") is None
    if sizeable and q["q_C_hat"] is not None and q["q_C_hat"] >= Q_C_MIN_VIABLE:
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
    if p["p_hat"] is not None and p["n"] >= 30 and p["p_hat"] < P_BAND_LOWER:
        reasons.append(f"closed-book accuracy {p['p_hat']} < {P_BAND_LOWER} on {p['n']} items: "
                       f"the recipe is too hard, and harder items add cancellation not power")
    if q["q_C_hat"] is not None and q["q_C_hat"] < Q_C_MIN_VIABLE:
        reasons.append(f"q_C {q['q_C_hat']} < {Q_C_MIN_VIABLE}: the model-written query "
                       f"almost never returns a displacing claim, so the C arm is undosed")
    rd = stats["r_D"]["r_D_hat"]
    if rd is not None and rd < R_D_MIN_VIABLE:
        reasons.append(f"r_D {rd} < {R_D_MIN_VIABLE}: a screened item's fixed query rarely "
                       f"re-delivers a displacing claim on re-execution, so the screen is "
                       f"selecting on runtime noise rather than on item propensity")
    if reasons:
        return {"verdict": REVISE_RECIPE, "reasons": reasons}

    # ---- REVISE GRADER ------------------------------------------------------
    if g["k_g_one"] or g["k_g_both"]:
        return {"verdict": REVISE_GRADER, "reasons": [
            f"{g['k_g_one']} asymmetric and {g['k_g_both']} symmetric grader defects on "
            f"{g['observations']} held-out ITEMS. Repair from a GENERAL semantic rule on the "
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
    """Unmet PASS conditions, as strings. Empty list means PASS.

    p appears here only through the BAND on its point estimate and through the
    required n that its LOWER bound produces. There is no certification condition;
    THE_P_RULE records why that one was withdrawn.
    """
    p, g = stats["p"], stats["grader"]
    unmet = []
    if p["in_band"] is not True:
        unmet.append(f"closed-book accuracy {p['p_hat']} is outside the band "
                     f"[{P_BAND_LOWER}, 1.00]")
    if g["g_one_upper_95"] is None or g["g_one_upper_95"] > G_ONE_BOUND_FOR_PASS:
        unmet.append(f"grader asymmetry bound {g['g_one_upper_95']} has not reached "
                     f"{G_ONE_BOUND_FOR_PASS} (unit: item, n={g['observations']})")
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
    expected = required_production_n(0.95, 0.50, G_ONE_BOUND_FOR_PASS)
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
            "restated_exposure_gap": PRECALIBRATION_COMMITTED_Q_GAP,
            "implied_displacement_gap": round(Q_GAP_IMPLIED_DISPLACEMENT_GAP, 4),
        },
        "negative_control": {
            "STATUS": "PROVISIONAL -- a function of the final primary n, which does not "
                      "exist until the bank has run. No control item is authored yet.",
            "rule": "smallest clean sample whose 95% upper bound is strictly below "
                    "D_min / n_primary, the smallest realized harm rate at which the "
                    "primary could reject",
            "at_superseded_n_primary_50": nc,
            "at_currently_expected_n_primary": negative_control_n(expected),
            "table": {str(n): negative_control_n(n)["n_control_recommended"]
                      for n in (50, 60, 66, 72, 78, 90)},
            "provenance": provenance_of_the_two_control_numbers(),
        },
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
            "PASS_conditions": [
                f"closed-book point estimate inside the band [{P_BAND_LOWER}, 1.00]",
                f"grader asymmetry 95% upper bound <= {G_ONE_BOUND_FOR_PASS}, "
                f"UNIT = ITEM",
                f"re-derived production n <= {N_PROD_AFFORDABLE_CAP}",
            ],
            "the_p_rule": THE_P_RULE,
            "order": [REVISE_DESIGN, REVISE_RECIPE, REVISE_GRADER, PASS, CONTINUE],
            "max_calibration_screen_passing_items": MAX_CALIBRATION_SCREENED,
            "preregistration_status": PREREGISTRATION_STATUS,
        },
        "adjudication": adjudication_plan(BATCH1_TARGET_SCREENED),
        "parameter_lineage": PARAMETER_LINEAGE,
    }


def main() -> int:
    import pathlib
    out = pathlib.Path(__file__).resolve().parent.parent / "runs" / "exp004_stage0b_design"
    out.mkdir(parents=True, exist_ok=True)
    doc = report()
    (out / "calibration_plan.json").write_text(json.dumps(doc, indent=1) + "\n")
    nc = doc["negative_control"]
    print(f"negative control (PROVISIONAL): {nc['table']}")
    b = doc["plan"]["batch_1"]
    print(f"grader bound unit=ITEM: holdout {b['grader_validation_holdout']} items -> "
          f"{b['g_one_bound_if_holdout_clean']} "
          f"(invalid pooling would have claimed {b['what_the_invalid_pooling_would_have_claimed']})")
    a = doc["adjudication"]["manual_burden_forecast"]
    print(f"manual adjudication forecast: ~{a['forecast_human_adjudications']} of "
          f"{a['answers']} answers")
    b1, mx = doc["plan"]["batch_1"], doc["plan"]["maximum"]
    print(f"batch 1: {b1['authored_items']} authored -> {b1['screen_passing_items']} screened, "
          f"{b1['dispatches']} dispatches, ${b1['total_cost_usd']}")
    print(f"maximum: {mx['authored_items']} authored -> {mx['screen_passing_items']} screened, "
          f"{mx['dispatches']} dispatches, ${mx['total_cost_usd']}")
    print("n_prod at g_one:", json.dumps(doc["sizing_sensitivity"]["n_prod at g_one, q_C=0.50"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
