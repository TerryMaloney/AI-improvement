"""Stage 0A-M analysis: does retrieval displace an explicitly anchored answer?

TWO NULLS, AND THEY ARE NOT THE SAME HYPOTHESIS
-----------------------------------------------
For item i let Y_ib, Y_is be the closed-book and retrieval-enabled outcomes, and
    a_i = P(Y_ib=1, Y_is=0)   (baseline-favouring discordance)
    b_i = P(Y_ib=0, Y_is=1)   (retrieval-favouring discordance)
so that a_i - b_i = p_bi - p_si = -delta_i.

    H0_pointwise:  delta_i >= 0 for every item i
    H0_mean:       (1/n) sum_i delta_i >= 0

H0_pointwise is a strict subset of H0_mean: the mean null also permits some
genuinely harmed items provided helped items offset them. A test valid against
the LARGER null licenses the stronger conclusion, so which one we can defend
decides what a rejection is allowed to say.

PROVEN: validity against H0_pointwise
-------------------------------------
Under H0_pointwise, a_i <= b_i for every i, so conditional on which items came
out discordant, each contributes independently to the baseline-favouring count
with probability pi_i = a_i/(a_i+b_i) <= 1/2. A sum of independent Bernoullis
each with p <= 1/2 is stochastically dominated by Binomial(D, 1/2). That holds
for every discordant set, hence unconditionally, so the one-sided binomial tail
is a valid p-value -- conservative under item heterogeneity.

PROVEN UNDER POISSONIZATION: validity against H0_mean
-----------------------------------------------------
If each item generated Poisson(a_i) and Poisson(b_i) discordances rather than at
most one, then n10 ~ Poisson(sum a) and n01 ~ Poisson(sum b) independently, and
conditional on D = n10+n01 we get n10 ~ Binomial(D, sum_a/(sum_a+sum_b))
exactly. H0_mean gives sum_a <= sum_b, hence that binomial parameter is <= 1/2
and the same domination applies. This is the right idealisation when per-item
discordance probabilities are small.

NOT PROVEN: validity against H0_mean in the exact Bernoulli model
-----------------------------------------------------------------
The real model is Bernoulli -- each item contributes at most one discordance --
which is under-dispersed relative to Poisson. Under-dispersion is the
conservative direction, but that is an argument, not a proof.

[MEASURED] What was actually done instead: an exhaustive-in-practice search of
the configuration space at the planned n=25, computing Type-I EXACTLY by 2-D
convolution (no Monte Carlo) over a structured grid, 4000 random configurations,
hill-climbing, and simulated annealing with 8 restarts. Worst case found:

    alpha = 0.05   ->  Type-I = 0.030
    alpha = 0.025  ->  Type-I = 0.0105   (the Holm K=2 first step)

The worst configurations sit exactly on the boundary sum_a = sum_b. No
configuration exceeding alpha was found. [OPEN] This is a searched bound, not a
theorem; a general Bernoulli proof is not in hand.

WHAT A REJECTION LICENSES
-------------------------
Primary, fully proven: **at least one item in the class is harmed by retrieval**
(H0_pointwise is rejected, i.e. NOT all delta_i >= 0). That is the existence
claim a mechanism assay is for.

Secondary, numerically supported at the planned design but not proven: the
class-average effect is negative.

Non-rejection licenses neither the negation of the other. The statistic responds
to net directional imbalance, so a class that is 40% badly harmed and 60% mildly
helped returns a null -- asserted by test, so nobody later claims otherwise.

THE CROSS-ITEM DEPENDENCE ASSUMPTION
------------------------------------
The domination argument needs the orientations of DIFFERENT items not to conspire.
Separate API requests are not by themselves statistically independent
observations, so the assumption has to be stated rather than assumed.

What is NOT required: independence between the two arms WITHIN an item. That is
an algebraic fact, not an assumption --
    a_i - b_i = P(1,0) - P(0,1) = p_closed_i - p_search_i
holds for an arbitrary joint distribution of the two arm outcomes, because
p_closed = P(1,1)+P(1,0) and p_search = P(1,1)+P(0,1) and the P(1,1) terms
cancel. Within-item arm correlation is therefore irrelevant to the test.

What IS required, in its weakest sufficient form:

    [SEQUENTIAL CONDITIONAL INEQUALITY]
    Fix a preregistered ordering of items. Condition on which items came out
    discordant. Let X_1..X_D be their orientations in that order, X_j = 1 for
    baseline-favouring. Assume
        P(X_j = 1 | X_1..X_{j-1}, the discordance pattern) <= 1/2   for every j.

[PROVEN] Under that condition, sum_j X_j is stochastically dominated by
Binomial(D, 1/2), so the one-sided binomial tail remains a valid p-value.
Proof by sequential coupling: draw U_1..U_D iid Uniform(0,1) and realise
X_j = 1{U_j <= p_j} where p_j is the conditional probability above. Since
p_j <= 1/2 we have X_j <= 1{U_j <= 1/2} =: Z_j pointwise, the Z_j are iid
Bernoulli(1/2), hence sum X_j <= sum Z_j ~ Binomial(D, 1/2) pointwise. D is
fixed by the conditioning, and averaging over discordance patterns preserves the
domination.

This is strictly weaker than independence: it permits arbitrary dependence, so
long as no history ever makes a baseline-favouring orientation more likely than
even.

WHEN THE CONDITION HOLDS, AND WHEN IT DOES NOT
-----------------------------------------------
It holds automatically if H0_pointwise holds CONDITIONAL ON every realisation of
any shared latent state (server load, index freshness, time of day): if
pi_i(Theta) <= 1/2 for every Theta, then any mixture over Theta given history is
also <= 1/2.

It FAILS when the null holds only MARGINALLY -- when a shared state pushes
pi above 1/2 for some realisations and below for others. [MEASURED] Type-I at
n=25, alpha=0.05:

    one shared orientation coin (pi=0 or 1)          0.498
    exchangeable beta mixture, c=0.5                 0.324
    exchangeable beta mixture, c=2                   0.172
    exchangeable beta mixture, c=10 (mild!)          0.063
    5 blocks of 5, orientation shared in block       0.144
    shared pi ~ U(0.2,0.8), mean exactly 1/2         0.121

versus the conditionally-safe cases, which are conservative:

    shared pi ~ U(0,0.5), always <= 1/2              0.003
    adaptive adversary held at the bound             0.028
    history-adaptive hostile adversary               0.000

So arbitrary cross-item dependence breaks this test badly, and even mild
exchangeable orientation correlation exceeds nominal. The design's defence is
therefore procedural, not statistical: the dispatch schedule (randomised arm
order within item, randomised item order, interleaved classes, arms paired in
time, fresh context per trial) exists to make the sequential conditional
inequality credible. See the specification's dispatch-schedule section.

WHY R=1
-------
With a single replicate per item x arm there is no within-arm replicate
correlation for an assumption to be wrong about. The design's robustness comes
from that, not from a dispersion estimate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import comb

BASELINE_FAVOURING = "n10"
RETRIEVAL_FAVOURING = "n01"


def discordance(pairs: list[tuple[int, int]]) -> tuple[int, int]:
    """Count discordant pairs. `pairs` is [(closed_outcome, retrieval_outcome), ...]."""
    n10 = sum(1 for b, s in pairs if b == 1 and s == 0)
    n01 = sum(1 for b, s in pairs if b == 0 and s == 1)
    return n10, n01


def exact_one_sided_p(n10: int, n01: int) -> float:
    """P(X >= n10) for X ~ Binomial(n10+n01, 1/2). Valid under the class null."""
    d = n10 + n01
    if d == 0:
        return 1.0
    return sum(comb(d, i) for i in range(n10, d + 1)) / 2 ** d


def harm_share_upper_bound(n10: int, n01: int, conf: float = 0.95) -> float:
    """Exact upper bound on the share of DISCORDANT items that are
    baseline-favouring. Retained as a descriptive companion only.

    Do not use this as the negative control's headline number: when a control
    class is perfectly clean (n10 = n01 = 0) the discordant denominator is empty
    and this correctly but uselessly returns 1.0. A clean negative control must
    not read as maximally uninformative. Use `harm_rate_upper_bound`.
    """
    d = n10 + n01
    if d == 0:
        return 1.0
    if n10 == d:
        return 1.0
    return _cp_upper(n10, d, conf)


def harm_rate_upper_bound(n10: int, n_items: int, conf: float = 0.95) -> float:
    """Exact Clopper-Pearson upper bound on the RATE of baseline-favouring
    discordance among ALL items in the class, n10 / n_items.

    This is the negative control's headline quantity, because it is what the
    control exists to bound: how often does merely enabling retrieval flip a
    correct closed-book answer to an incorrect one, on tasks where retrieval
    should be irrelevant. Unlike the conditional share it stays informative when
    the control is clean -- 0 of 15 gives an upper bound near 0.18 rather than 1.0.
    """
    if n_items <= 0:
        raise ValueError("n_items must be positive")
    if n10 >= n_items:
        return 1.0
    return _cp_upper(n10, n_items, conf)


def _cp_upper(k: int, n: int, conf: float) -> float:
    """Clopper-Pearson upper limit: the largest p with P(X <= k) > 1 - conf."""
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        tail = sum(comb(n, i) * mid ** i * (1 - mid) ** (n - i) for i in range(0, k + 1))
        if tail > 1 - conf:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def paired_risk_difference(n10: int, n01: int, n_items: int) -> float:
    """(closed correct rate) - (retrieval correct rate) = (n10 - n01)/n.

    Descriptive only. Concordant items cancel, so this is exactly the paired
    risk difference. No exact interval is claimed for it here.
    """
    if n_items <= 0:
        raise ValueError("n_items must be positive")
    return (n10 - n01) / n_items


def holm(pvalues: dict[str, float], alpha: float = 0.05) -> dict[str, bool]:
    """Holm step-down. Controls FWER over the preregistered class family without
    assuming independence between classes."""
    order = sorted(pvalues, key=lambda k: pvalues[k])
    m = len(order)
    out: dict[str, bool] = {}
    still_rejecting = True
    for rank, key in enumerate(order):
        if still_rejecting and pvalues[key] <= alpha / (m - rank):
            out[key] = True
        else:
            still_rejecting = False
            out[key] = False
    return out


@dataclass
class ClassResult:
    name: str
    n_items: int
    n10: int
    n01: int
    p_value: float
    rejected: bool | None = None
    harm_rate_upper_95: float = field(default=1.0)      # n10/n, the control headline
    harm_share_upper_95: float = field(default=1.0)     # n10/(n10+n01), descriptive
    risk_difference: float = field(default=0.0)         # (n10-n01)/n, descriptive


@dataclass
class Stage0AMResult:
    primary: dict[str, ClassResult]
    negative_control: dict[str, ClassResult]
    alpha: float
    any_primary_rejected: bool


def analyse(
    primary: dict[str, list[tuple[int, int]]],
    negative_control: dict[str, list[tuple[int, int]]] | None = None,
    alpha: float = 0.05,
) -> Stage0AMResult:
    """Primary classes enter the Holm family. Negative-control classes do NOT —
    they are reported as exact upper bounds on harm share. Mixing them would
    spend alpha on a hypothesis the design does not make."""
    negative_control = negative_control or {}
    overlap = set(primary) & set(negative_control)
    if overlap:
        raise ValueError(f"a class cannot be both primary and negative control: {sorted(overlap)}")

    prim: dict[str, ClassResult] = {}
    for name, pairs in primary.items():
        n10, n01 = discordance(pairs)
        prim[name] = ClassResult(
            name=name, n_items=len(pairs), n10=n10, n01=n01,
            p_value=exact_one_sided_p(n10, n01),
            harm_rate_upper_95=harm_rate_upper_bound(n10, len(pairs)),
            harm_share_upper_95=harm_share_upper_bound(n10, n01),
            risk_difference=paired_risk_difference(n10, n01, len(pairs)),
        )
    decisions = holm({k: v.p_value for k, v in prim.items()}, alpha)
    for name, rejected in decisions.items():
        prim[name].rejected = rejected

    ctrl: dict[str, ClassResult] = {}
    for name, pairs in negative_control.items():
        n10, n01 = discordance(pairs)
        ctrl[name] = ClassResult(
            name=name, n_items=len(pairs), n10=n10, n01=n01,
            p_value=exact_one_sided_p(n10, n01),
            rejected=None,  # never tested; reported as bounds
            harm_rate_upper_95=harm_rate_upper_bound(n10, len(pairs)),
            harm_share_upper_95=harm_share_upper_bound(n10, n01),
            risk_difference=paired_risk_difference(n10, n01, len(pairs)),
        )

    return Stage0AMResult(
        primary=prim, negative_control=ctrl, alpha=alpha,
        any_primary_rejected=any(v.rejected for v in prim.values()),
    )


# ---------------------------------------------------------------------------
# Failure semantics: retrieval-tool outcome vs missing trial outcome
# ---------------------------------------------------------------------------
#
# The specification originally defined "technical failure" as "the tool call did
# not complete (error, timeout, empty transport response, egress refusal)" and
# voided the item across both arms. Read literally that covers a solver whose
# WebFetch was refused but which still returned a gradeable answer -- and that
# reading contradicts the intent-to-treat rule in section 6, which keeps such a
# trial in the retrieval-enabled arm.
#
# The contradiction is resolved in favour of section 6, and not merely to break a
# tie. Voiding on retrieval-tool failure is post-treatment selection on a
# variable only the treatment arm can exhibit: the closed arm has no tools, so it
# can never register a retrieval failure, and the exclusion is therefore
# structurally arm-asymmetric. It would also remove part of the phenomenon under
# study -- a model that searched, got nothing, and confabulated anyway is one of
# the mechanisms by which retrieval can cause harm.
#
# The discriminating question is NOT which tool failed. It is:
#
#     did the dispatch yield a gradeable final answer?
#
# If yes, the trial is data, whatever happened to its tools. If no, there is no
# outcome to grade, and a pair missing one half cannot enter a paired test at
# all -- so the item is void. That is mechanically forced by pairing, not a
# policy choice; the policy choice is only that voiding is symmetric across arms,
# which is retained because dispatch deaths plausibly correlate with arm.

RETRIEVAL_TOOL_OUTCOMES = frozenset({
    "OK",                    # retrieval ran and returned results
    "REFUSED_BY_PROXY",      # egress refusal -- the measured state of this environment
    "TOOL_ERROR",            # the tool raised
    "TOOL_TIMEOUT",          # the tool did not return in time
    "EMPTY_RESULTS",         # completed, returned nothing useful
    "UNHELPFUL_RESULTS",     # completed, returned results that did not resolve the question
    "NOT_ATTEMPTED",         # the model declined to retrieve; still treated, still ITT
})
"""Observed outcomes of the treatment. None of these voids anything."""

DISPATCH_FAILURES = frozenset({
    "DISPATCH_ERROR",        # the API call for the trial itself failed
    "AGENT_TERMINATED",      # the solver stopped before producing a final answer
    "TRANSPORT_TIMEOUT",     # the dispatch did not return
    "EMPTY_RESPONSE",        # the dispatch returned nothing to grade
    "UNPARSEABLE_RESPONSE",  # the response carried no extractable final answer
})
"""Missing outcome data. These void the item across both arms."""


@dataclass
class TrialOutcome:
    """One dispatch. `graded` is None exactly when there is no answer to grade."""
    item_id: str
    arm: str                                  # "closed" | "retrieval_enabled"
    graded: int | None                        # 1 correct, 0 incorrect, None ungradeable
    retrieval_outcomes: tuple[str, ...] = ()  # every retrieval tool call's outcome
    dispatch_failure: str | None = None       # a DISPATCH_FAILURES member, or None


def trial_is_gradeable(trial: TrialOutcome) -> bool:
    """A trial is data iff it produced a final answer that could be graded.

    Explicitly independent of `retrieval_outcomes`: a trial whose every retrieval
    call was REFUSED_BY_PROXY is still gradeable if the solver answered.
    """
    if trial.dispatch_failure is not None:
        if trial.dispatch_failure not in DISPATCH_FAILURES:
            raise ValueError(f"unknown dispatch failure: {trial.dispatch_failure!r}")
        return False
    return trial.graded is not None


def pair_disposition(closed: TrialOutcome, retrieval: TrialOutcome) -> str:
    """RETAIN iff both halves are gradeable, else VOID_PAIR."""
    if closed.item_id != retrieval.item_id:
        raise ValueError(f"pair spans two items: {closed.item_id} vs {retrieval.item_id}")
    if {closed.arm, retrieval.arm} != {"closed", "retrieval_enabled"}:
        raise ValueError(f"a pair needs one arm of each: {closed.arm}, {retrieval.arm}")
    return "RETAIN" if trial_is_gradeable(closed) and trial_is_gradeable(retrieval) else "VOID_PAIR"


def partition_pairs(
    pairs: list[tuple[TrialOutcome, TrialOutcome]],
) -> tuple[list[tuple[int, int]], list[str], dict[str, int]]:
    """Split dispatched pairs into analysable (closed, retrieval) grades and voids.

    Returns the retained grade pairs in `analyse`'s input shape, the void item ids,
    and a per-arm count of which arm's failure caused each void -- reported because
    arm-correlated dispatch mortality is itself a treatment outcome, and a void
    rate that leans on one arm is a finding rather than a nuisance.
    """
    retained: list[tuple[int, int]] = []
    voided: list[str] = []
    void_cause = {"closed": 0, "retrieval_enabled": 0, "both": 0}
    for closed, retrieval in pairs:
        if pair_disposition(closed, retrieval) == "RETAIN":
            retained.append((closed.graded, retrieval.graded))
            continue
        voided.append(closed.item_id)
        c_bad, r_bad = not trial_is_gradeable(closed), not trial_is_gradeable(retrieval)
        void_cause["both" if c_bad and r_bad else "closed" if c_bad else "retrieval_enabled"] += 1
    return retained, voided, void_cause


def retrieval_failure_rate(trials: list[TrialOutcome]) -> dict[str, float]:
    """Reported as a treatment outcome. Never an inclusion rule."""
    treated = [t for t in trials if t.arm == "retrieval_enabled"]
    if not treated:
        return {"n_treated": 0}
    attempted = [t for t in treated if any(o != "NOT_ATTEMPTED" for o in t.retrieval_outcomes)]
    failed = [t for t in attempted
              if all(o in {"REFUSED_BY_PROXY", "TOOL_ERROR", "TOOL_TIMEOUT"}
                     for o in t.retrieval_outcomes if o != "NOT_ATTEMPTED")]
    return {
        "n_treated": len(treated),
        "declined_retrieval": len(treated) - len(attempted),
        "attempted_retrieval": len(attempted),
        "all_retrieval_calls_failed": len(failed),
        "rate_all_failed_given_attempted": len(failed) / len(attempted) if attempted else 0.0,
    }
