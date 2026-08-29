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
