"""C-vs-D: what the secondary comparison must be capable of, decided before outcomes.

THE QUESTION THIS MODULE ANSWERS
--------------------------------
Stage 0B's objective sentence contains two claims, not one:

    (i)  content returned by an executed search can displace an anchored answer;
    (ii) whether it does depends on the query that produced the content.

Claim (i) rests on A-vs-C. Claim (ii) rests entirely on C-vs-D. Stage 0A-M's
whole failure was a comparison that could not have rejected at any orientation of
its own data being reported as a null, so a design that intends to state (ii)
must establish beforehand that C-vs-D can distinguish the possibilities. That is
not the same as promoting it to primary, and it is not achieved by symmetry with
the primary.

WHAT IS AND IS NOT DECIDED HERE
-------------------------------
NOT promoted to primary. A-vs-C stays the primary family with K=1 and alpha=0.05.
Promoting C-vs-D would cost the primary the alpha it was sized on, to buy
sensitivity for a claim that is genuinely secondary.

D is retained REGARDLESS of whether C-vs-D is discriminating, because D's first
job is interpretive: without it, a null in C cannot be told apart from "the
model's query happened to return anchored content". That job needs D to exist,
not C-vs-D to reject.

THE PRE-FREEZE RULE
-------------------
1.  C-vs-D is two-sided. Neither direction is predicted -- a model-written query
    could plausibly be worse (it drops the anchor) or better (it is specific).
    The exact two-sided floor is therefore 2/2^D, so:

        D_cd = 5  ->  smallest attainable p = 0.0625   CANNOT reject at 0.05
        D_cd = 6  ->  smallest attainable p = 0.03125  can reject at 0.05

2.  **The reporting rule, fixed before outcomes.** If the realized C-vs-D
    discordant count is below `MIN_DISCORDANT_FOR_A_CLAIM`, the comparison is
    reported as UNINFORMATIVE -- INCAPABLE OF REJECTING. It may not be reported
    as "no evidence that query construction matters", and claim (ii) is not made
    in either direction. This is the rule Stage 0A-M did not have.

3.  **The authorization rule, applied before freeze against MEASURED values.**
    Once the calibration bank supplies p, and the divergence probe supplies the
    realized displacing-content rates for the model query and the fixed query,
    `authorize` is run. If the design cannot expect `MIN_DISCORDANT_FOR_A_CLAIM`
    discordant pairs and 80% power against the preregistered `delta_gap`, then
    claim (ii) is WITHDRAWN FROM THE DESIGN BEFORE THE RUN and C-vs-D is
    declared descriptive. The alternative -- running it and reporting whatever
    comes out -- is how an uninformative null gets published as a finding.

`delta_gap` is preregistered rather than fitted: it is the smallest difference in
displacement probability between a model query and an anchor-preserving fixed
query that would matter to anyone. It is set at 0.20 and is a design commitment,
not an estimate.

WHAT THIS COMPARISON ESTIMATES -- NARROWED 2026-09-03, AND THE NARROWING IS THE POINT
------------------------------------------------------------------------------------
The realized runtime block ECHOES THE QUERY in its header line (design draft
12.2). So C and D differ in at least three ways at once: the query text itself
reaches the answerer, the runtime-synthesised paragraph differs, and the link
list differs. C-vs-D therefore does NOT isolate "retrieved information caused the
effect", and it never could have on this runtime.

Three options were weighed before any outcome exists:

  (A) keep the echo and NARROW the claim;
  (B) strip the echo symmetrically from C and D before injection;
  (C) keep Stage 0B simple and defer the decomposition to a later experiment.

**Chosen: (A), with (C)'s deferral.** (B) is rejected because stripping the header
would make the injected block differ from what the runtime actually exposes, which
is the exact mistake the "verbatim" claim already cost this design once; it would
also hand the answerer a block whose first line has been removed by the harness, a
new artifact traded for an old one. No arm is added: the smallest identifiable
claim is preferred to a decomposition Stage 0B was not sized for.

So the estimand C-vs-D supports is, in full:

    the TOTAL DOWNSTREAM EFFECT OF THE QUERY-CONSTRUCTION PROCEDURE under this
    realized search runtime -- bundling the echoed query text, the
    runtime-synthesised answer and the link list, and attributing to none of them
    separately.

It is NOT an estimate of the effect of retrieved page content. Decomposing the
three channels is a NAMED FOLLOW-ON, not a Stage 0B result.

WHAT THE SELECTION RULE DOES TO delta_D
---------------------------------------
The divergence screen admits an item to production iff its FIXED-query block is
divergent, so on the production pool `q_D = 1.0 BY CONSTRUCTION` while `q_C` is
estimated. Under the common-susceptibility decomposition
`delta_C = q_C * delta`, `delta_D = q_D * delta`, that means D is expected to
displace AT LEAST as often as C. The test is nonetheless kept TWO-SIDED: a
model-written query can return a different and more potent displacing claim, so
the direction is not logically forced. The asymmetry is declared here rather than
discovered in a later review.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb

from lab.stage0b_power import joint_n10_n01

# Two-sided exact floor: with D discordant pairs the smallest attainable
# two-sided p is 2/2^D. D=5 gives 0.0625 and cannot reject at 0.05; D=6 gives
# 0.03125 and can.
MIN_DISCORDANT_FOR_A_CLAIM = 6
ALPHA_SECONDARY = Fraction(1, 20)          # 0.05, its own family, no primary alpha spent
DELTA_GAP_PREREGISTERED = 0.20
TARGET_POWER = 0.80


def exact_two_sided_p(n10: int, n01: int) -> Fraction:
    """Exact two-sided sign-test p on the discordant pairs."""
    d = n10 + n01
    if d == 0:
        return Fraction(1)
    k = min(n10, n01)
    tail = Fraction(sum(comb(d, i) for i in range(0, k + 1)), 2 ** d)
    return min(Fraction(1), 2 * tail)


def smallest_attainable_p(d: int) -> Fraction:
    """The best p any orientation of `d` discordant pairs could produce.

    The number Stage 0A-M needed and did not compute: at D=2 it is 1/2 two-sided,
    and no arrangement of the data could have rejected."""
    return exact_two_sided_p(d, 0)


def can_reject_at(d: int, alpha: Fraction = ALPHA_SECONDARY) -> bool:
    return smallest_attainable_p(d) <= alpha


@dataclass(frozen=True)
class CvDScenario:
    """Displacement probabilities for the two exposed arms, on the SAME items.

    p        P(the closed-book answer is correct) -- measured on the calibration bank
    delta_C  P(displaced | model-written query) = q_C * delta
    delta_D  P(displaced | fixed anchor-preserving query) = q_D * delta, and q_D is
             1.0 by construction on the production pool, so delta_D == delta
    g        symmetric per-arm grader error rate

    delta_C and delta_D are DISPLACEMENT probabilities. Calibration measures the
    EXPOSURE rates q_C and q_D; `delta` stays a preregistered minimum interesting
    effect. Build these from a calibration result with `from_exposure`, so the
    two scales cannot be silently mixed.
    """
    p: float
    delta_C: float
    delta_D: float
    g: float = 0.0

    def cells(self) -> tuple[float, float]:
        """(P(C wrong & D right), P(C right & D wrong)) per item.

        Both arms are exposed, so an item contributes a discordant pair only when
        the two queries lead to different verdicts. Displacement is only defined
        where the closed-book answer is correct; the remaining mass is treated as
        concordant, which is conservative for discordance and therefore for power.
        """
        pc_wrong = self.p * self.delta_C
        pd_wrong = self.p * self.delta_D
        # independent per arm, then symmetric grader noise on each arm
        def noisy(q):
            return q * (1 - self.g) + (1 - q) * self.g
        qc, qd = noisy(pc_wrong), noisy(pd_wrong)
        return qc * (1 - qd), qd * (1 - qc)


    @classmethod
    def from_exposure(cls, p: float, q_C: float, q_D: float = 1.0,
                      delta: float = 0.30, g: float = 0.0) -> "CvDScenario":
        """Build the scenario from MEASURED exposure rates and a preregistered delta.

        `q_D` defaults to 1.0 because the divergence screen pins it there on the
        production pool. Passing anything else means the items were not screened,
        and the scenario is then not describing the run that will happen.
        """
        return cls(p=p, delta_C=q_C * delta, delta_D=q_D * delta, g=g)


# The preregistered gap, restated on the scale it is measured on. On the
# DISPLACEMENT scale the commitment is 0.20; at delta=0.30 that implies an
# exposure-rate difference of 0.667 between the two queries, which is not a target
# anyone would have written down had the number been expressed in the units the
# calibration bank observes. lab.stage0b_calibration.Q_GAP_PREREGISTERED restates
# it as |q_C - q_D| >= 0.25, implying a displacement gap of 0.075.
DELTA_GAP_IMPLIED_EXPOSURE_GAP_AT_DELTA_030 = 0.20 / 0.30


def analyse(s: CvDScenario, n: int, alpha: Fraction = ALPHA_SECONDARY) -> dict:
    o10, o01 = s.cells()
    e_d = n * (o10 + o01)
    power = 0.0
    p_reject_cache: dict[tuple[int, int], bool] = {}
    for i, j, prob in joint_n10_n01(n, o10, o01):
        key = (i, j)
        if key not in p_reject_cache:
            p_reject_cache[key] = exact_two_sided_p(i, j) <= alpha
        if p_reject_cache[key]:
            power += prob
    return {
        "n": n,
        "p": s.p, "delta_C": s.delta_C, "delta_D": s.delta_D, "grader_error": s.g,
        "E_n10_C_worse": round(n * o10, 3),
        "E_n01_D_worse": round(n * o01, 3),
        "E_discordant": round(e_d, 3),
        "meets_discordance_floor": e_d >= MIN_DISCORDANT_FOR_A_CLAIM,
        "power": round(power, 4),
        "alpha": str(alpha),
        "min_discordant_for_a_claim": MIN_DISCORDANT_FOR_A_CLAIM,
    }


def authorize(s: CvDScenario, n: int, delta_gap: float = DELTA_GAP_PREREGISTERED,
              target_power: float = TARGET_POWER) -> dict:
    """Run before freeze, on MEASURED p / delta_C / delta_D. Never after outcomes."""
    res = analyse(s, n)
    gap = abs(s.delta_C - s.delta_D)
    reasons = []
    if not res["meets_discordance_floor"]:
        reasons.append(
            f"expected discordance {res['E_discordant']} < {MIN_DISCORDANT_FOR_A_CLAIM}: "
            f"at that count the smallest attainable two-sided p is "
            f"{float(smallest_attainable_p(int(res['E_discordant'] or 0))):.4f}, so the "
            f"comparison cannot reject at any orientation of its own data")
    if res["power"] < target_power:
        reasons.append(f"power {res['power']} < {target_power} at the measured rates")
    # 0.30 - 0.10 is 0.19999999999999998 in binary floating point, so a bare `<`
    # would withdraw a claim that sits exactly on the preregistered gap.
    if gap < delta_gap - 1e-9:
        reasons.append(
            f"the measured gap between the two queries is {gap:.3f}, below the "
            f"preregistered {delta_gap} that the claim is about; a comparison sized on a "
            f"smaller gap would be detecting a difference nobody preregistered as mattering")
    return {
        "verdict": "CLAIM_AUTHORIZED" if not reasons else "CLAIM_WITHDRAWN_BEFORE_RUN",
        "claim": "the query-construction procedure changes the TOTAL downstream effect "
                 "of exposure to this search runtime's result block -- bundling the "
                 "echoed query text, the runtime-synthesised answer and the link list, "
                 "and attributing to none of them separately. NOT a claim about "
                 "retrieved page content.",
        "reasons": reasons,
        "if_withdrawn": "Arm D is still run. Its interpretive job -- without it a null in "
                        "C cannot be told apart from 'the model's query happened to return "
                        "anchored content' -- does not require C-vs-D to reject. C-vs-D is "
                        "then reported descriptively, with its realized discordant count "
                        "and its smallest attainable p stated in the same sentence.",
        "analysis": res,
    }


def report_realized(n10: int, n01: int, alpha: Fraction = ALPHA_SECONDARY) -> dict:
    """How a realized C-vs-D result must be described. Fixed before outcomes."""
    d = n10 + n01
    floor = smallest_attainable_p(d)
    p = exact_two_sided_p(n10, n01)
    if d < MIN_DISCORDANT_FOR_A_CLAIM:
        status = "UNINFORMATIVE — INCAPABLE OF REJECTING"
        wording = (f"C-vs-D produced {d} discordant pairs. At {d} the smallest attainable "
                   f"two-sided p is {float(floor):.4f}, so this comparison could not have "
                   f"rejected at alpha={float(alpha):.3f} whatever the data had looked like. "
                   f"No claim is made about query construction in either direction.")
    elif p <= alpha:
        status = "REJECTED"
        wording = (f"C-vs-D: {n10}/{n01} discordant, exact two-sided p={float(p):.4f}. "
                   f"Query construction changes displacement on these items.")
    else:
        status = "NULL, AND POWERED ENOUGH TO SAY SO"
        wording = (f"C-vs-D: {n10}/{n01} discordant, exact two-sided p={float(p):.4f}. "
                   f"The comparison could have rejected ({d} discordant pairs, floor "
                   f"{float(floor):.4f}) and did not.")
    return {"n10": n10, "n01": n01, "discordant": d, "p": str(p),
            "smallest_attainable_p": str(floor), "status": status, "required_wording": wording}


# The scenarios that decide whether the claim is worth designing for. Run on the
# ASSUMED design point today; re-run on measured values before freeze.
DESIGN_POINT_SCENARIOS = {
    "query construction matters a lot (model query drops the anchor)":
        CvDScenario(p=0.95, delta_C=0.30, delta_D=0.05),
    "query construction matters by exactly the preregistered gap":
        CvDScenario(p=0.95, delta_C=0.30, delta_D=0.10),
    "query construction does not matter":
        CvDScenario(p=0.95, delta_C=0.30, delta_D=0.30),
    "nothing displaces anything (the A-vs-C null world)":
        CvDScenario(p=0.95, delta_C=0.02, delta_D=0.02),
    "Stage 0A-M's grader error rate, symmetric 20%":
        CvDScenario(p=0.95, delta_C=0.30, delta_D=0.10, g=0.20),
}


def n_for_power(s: CvDScenario, target: float = TARGET_POWER,
                n_max: int = 240) -> int | None:
    for n in range(10, n_max + 1, 2):
        if analyse(s, n)["power"] >= target:
            return n
    return None


OUT = None  # set in main()


def main() -> int:
    import json
    import pathlib as _pl
    n = 50
    doc = {
        "comparison": "C vs D",
        "inferential_status": "SECONDARY, own family, alpha=0.05, no primary alpha spent",
        "not_promoted_to_primary": "Promoting it would cost A-vs-C the alpha it was sized "
                                   "on, to buy sensitivity for a genuinely secondary claim.",
        "two_sided": "Neither direction is predicted; a model query could be worse (drops "
                     "the anchor) or better (more specific).",
        "min_discordant_for_a_claim": MIN_DISCORDANT_FOR_A_CLAIM,
        "floor_table": {d: str(smallest_attainable_p(d)) for d in range(0, 9)},
        "delta_gap_preregistered": DELTA_GAP_PREREGISTERED,
        "scenarios_at_n50": {k: analyse(v, n) for k, v in DESIGN_POINT_SCENARIOS.items()},
        "authorization_on_assumed_values": {
            k: authorize(v, n) for k, v in DESIGN_POINT_SCENARIOS.items()},
        "n_for_80_percent_power": {
            k: n_for_power(v) for k, v in DESIGN_POINT_SCENARIOS.items()},
        "note": "These use the ASSUMED design point. The binding run of `authorize` "
                "happens before freeze, on p from the calibration bank and delta_C/delta_D "
                "from the divergence probe.",
        "finding_on_assumed_values":
            "At the recommended n=50, C-vs-D has power 0.599 against the preregistered "
            "gap of 0.20 -- it does NOT clear 0.80, and would need n=76. Under a "
            "Stage 0A-M-like symmetric 20% grader error rate it is unpowered at every n "
            "up to 200. Symmetric grader noise is WORSE for C-vs-D than for the primary: "
            "in a one-sided paired test it deletes at-risk items silently, but here it "
            "manufactures BALANCED discordance that directly swamps the sign test. "
            "The design is therefore on notice: unless the measured values are kinder "
            "than the assumed ones, claim (ii) is withdrawn before the run or the C/D "
            "family is resized. It is not resized on assumed values today, because "
            "sizing on assumptions is what produced Stage 0A-M.",
    }
    out = _pl.Path(__file__).resolve().parent.parent / "runs" / "exp004_stage0b_design" / "cvd_inferential_status.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1) + "\n")
    print(json.dumps({k: doc[k] for k in
                      ("min_discordant_for_a_claim", "floor_table",
                       "n_for_80_percent_power", "finding_on_assumed_values")},
                     indent=1))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
