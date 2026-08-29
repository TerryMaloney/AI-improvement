"""Stage 0A-M analysis: does retrieval displace an explicitly anchored answer?

The whole design rests on one inequality, so it is worth stating before any code.

For item i let Y_ib, Y_is be the closed-book and retrieval outcomes, and write
    a_i = P(Y_ib=1, Y_is=0)   (baseline-favouring discordance)
    b_i = P(Y_ib=0, Y_is=1)   (retrieval-favouring discordance)
Then a_i - b_i = p_bi - p_si = -delta_i, so under the class null "retrieval does
not hurt any item in this class" (delta_i >= 0 for all i) we have a_i <= b_i.

Conditional on WHICH items came out discordant, each contributes independently to
the baseline-favouring count with probability pi_i = a_i/(a_i+b_i) <= 1/2. A sum
of independent Bernoullis each with p <= 1/2 is stochastically dominated by
Binomial(D, 1/2). That holds for every discordant set, so it holds unconditionally,
and the one-sided binomial tail is therefore a valid p-value — conservative under
item heterogeneity, which is the direction we want.

This is the exact one-sided McNemar test, equivalently a conditional binomial sign
test on discordant pairs. It needs no dispersion parameter, which is why the design
uses R=1: with a single replicate per item x arm there is no within-arm replicate
correlation for an assumption to be wrong about.

What it does NOT do, and must never be reported as doing: detect within-class sign
heterogeneity. The statistic is driven by the class mean. A class that is 40%
badly harmed and 60% mildly helped returns a null.
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
    """Exact (Clopper-Pearson) upper bound on the share of discordant items that
    are baseline-favouring. Used for the NEGATIVE CONTROL class, where the point
    is to bound harm rather than to test for it: failing to reject is not evidence
    of no effect, but an upper bound is a statement with content."""
    d = n10 + n01
    if d == 0:
        return 1.0
    if n10 == d:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        tail = sum(comb(d, i) * mid ** i * (1 - mid) ** (d - i) for i in range(0, n10 + 1))
        if tail > 1 - conf:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


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
    harm_share_upper_95: float = field(default=1.0)


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
            harm_share_upper_95=harm_share_upper_bound(n10, n01),
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
            rejected=None,  # never tested; reported as a bound
            harm_share_upper_95=harm_share_upper_bound(n10, n01),
        )

    return Stage0AMResult(
        primary=prim, negative_control=ctrl, alpha=alpha,
        any_primary_rejected=any(v.rejected for v in prim.values()),
    )
