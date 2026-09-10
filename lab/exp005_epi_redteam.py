"""Post-hoc mechanism red-team utilities for EXP005-EPI.

This module does NOT define a confirmatory experiment. It exists to attack the
interpretation of already-visible EXP005-EPI synthetic outcomes with stronger
baselines, ablations and imperfect-verifier stress tests.

Nothing returned by this module may be promoted as prospective evidence. A new
candidate controller must be frozen and tested on a new generator before promotion.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import statistics
from typing import Callable

from lab.exp005_epi import EpistemicWorkspace, Evidence
from lab.exp005_epi_worlds import (
    _rng, build_workspace, generate_world, loss, verification_evidence,
)
from lab.exp005_epi_worlds_b import generate_transfer_world


Chooser = Callable[[EpistemicWorkspace, object, set[str]], str]


def uncertainty(ws: EpistemicWorkspace, proposition: str) -> float:
    b = ws.belief(proposition)
    if b.probability_true is None:
        return 1.0
    return 1.0 - abs(b.probability_true - 0.5) * 2.0


@dataclass(frozen=True)
class Features:
    uncertainty: float
    fragility: float
    staleness: float
    load: int
    own_impact: float
    descendant_impact: float

    @property
    def total_impact(self) -> float:
        return self.own_impact + self.descendant_impact


def features(ws: EpistemicWorkspace, world: object, proposition: str,
             current_time: int = 10_000) -> Features:
    b = ws.belief(proposition)
    by_id = {e.evidence_id: e for e in ws.evidence_log}
    active = [by_id[eid] for eid in b.active_evidence_ids if eid in by_id]
    if active:
        fragility = 1.0 / max(1, len({e.lineage_id for e in active}))
        last = max(e.observed_at for e in active)
        staleness = 1.0 + max(0, current_time - last) / 10.0
    else:
        fragility = 1.0
        staleness = 1.0
    descendants = ws.descendants(proposition)
    own = world.impacts[proposition]
    downstream = sum(world.impacts.get(p, 1.0) for p in descendants)
    return Features(
        uncertainty(ws, proposition), fragility, staleness,
        1 + len(descendants), own, downstream,
    )


def _argmax(candidates: set[str], score: Callable[[str], float]) -> str:
    return max(sorted(candidates), key=lambda p: (score(p), p))


def choose_uncertainty_load(ws, world, candidates):
    return _argmax(candidates, lambda p: features(ws, world, p).uncertainty *
                                      features(ws, world, p).load)


def choose_uncertainty_total_utility(ws, world, candidates):
    return _argmax(candidates, lambda p: features(ws, world, p).uncertainty *
                                      features(ws, world, p).total_impact)


def choose_load_only(ws, world, candidates):
    return _argmax(candidates, lambda p: float(features(ws, world, p).load))


def choose_debt_no_staleness(ws, world, candidates):
    return _argmax(
        candidates,
        lambda p: (
            features(ws, world, p).uncertainty
            * features(ws, world, p).fragility
            * features(ws, world, p).load
            * features(ws, world, p).own_impact
        ),
    )


def choose_debt_no_impact(ws, world, candidates):
    return _argmax(
        candidates,
        lambda p: (
            features(ws, world, p).uncertainty
            * features(ws, world, p).fragility
            * features(ws, world, p).staleness
            * features(ws, world, p).load
        ),
    )


def choose_frozen_debt(ws, world, candidates):
    ranked = ws.verification_queue(current_time=10_000, impacts=world.impacts)
    for p, _ in ranked:
        if p in candidates:
            return p
    raise ValueError("no candidate")


def choose_uncertainty(ws, world, candidates):
    return _argmax(candidates, lambda p: uncertainty(ws, p))


def choose_dependency(ws, world, candidates):
    return max(
        sorted(candidates),
        key=lambda p: (len(ws.descendants(p)), world.impacts[p], p),
    )


POLICIES: dict[str, Chooser] = {
    "debt": choose_frozen_debt,
    "uncertainty": choose_uncertainty,
    "dependency": choose_dependency,
    "load_only": choose_load_only,
    "uncertainty_load": choose_uncertainty_load,
    "uncertainty_total_utility": choose_uncertainty_total_utility,
    "debt_no_staleness": choose_debt_no_staleness,
    "debt_no_impact": choose_debt_no_impact,
}


def run_custom(world: object, policy: str, budget: int = 3,
               impact_weighted: bool = True) -> dict:
    """Run a deterministic post-hoc policy with the original perfect verifier."""
    if policy not in POLICIES:
        raise ValueError(f"unknown policy {policy!r}")
    ws = build_workspace(world)
    candidates = set(world.base_truth)
    before = loss(ws, world, impact_weighted=impact_weighted)
    trajectory = [before]
    chosen: list[str] = []
    for step in range(budget):
        p = POLICIES[policy](ws, world, candidates)
        candidates.remove(p)
        chosen.append(p)
        ws.ingest(verification_evidence(world, p, step))
        trajectory.append(loss(ws, world, impact_weighted=impact_weighted))
    return {
        "seed": world.seed,
        "policy": policy,
        "before_loss": before,
        "after_loss": trajectory[-1],
        "gain": before - trajectory[-1],
        "chosen": chosen,
        "trajectory": trajectory,
    }


def noisy_verification_evidence(world: object, proposition: str, step: int,
                                *, actual_accuracy: float,
                                reported_reliability: float,
                                draw: float) -> Evidence:
    """Synthetic stress-only verifier; result can be wrong.

    ``actual_accuracy`` controls generated correctness. The epistemic system sees
    only ``reported_reliability``. This separates real tool accuracy from the
    confidence metadata the system trusts.
    """
    if not 0.5 < actual_accuracy < 1.0:
        raise ValueError("actual_accuracy must be in (0.5,1)")
    if not 0.5 < reported_reliability < 1.0:
        raise ValueError("reported_reliability must be in (0.5,1)")
    value = world.base_truth[proposition]
    if draw > actual_accuracy:
        value = not value
    return Evidence(
        evidence_id=f"REDTEAM-VERIFY-{world.seed}-{proposition}-{step}",
        proposition=proposition,
        asserted_value=value,
        source_id=f"redteam-verifier-{proposition}",
        lineage_id=f"redteam-verifier-lineage-{world.seed}-{proposition}-{step}",
        reliability=reported_reliability,
        observed_at=10_000 + step,
        metadata={
            "kind": "posthoc_noisy_verification_stress",
            "actual_accuracy_hidden_from_workspace": actual_accuracy,
        },
    )


def run_noisy_verifier(world: object, policy: str, *, budget: int = 3,
                       actual_accuracy: float = 0.9,
                       reported_reliability: float = 0.9) -> dict:
    if policy not in POLICIES:
        raise ValueError(f"unknown policy {policy!r}")
    ws = build_workspace(world)
    rng = _rng(world.seed + 9_999)
    candidates = set(world.base_truth)
    before = loss(ws, world)
    chosen = []
    for step in range(budget):
        p = POLICIES[policy](ws, world, candidates)
        candidates.remove(p)
        chosen.append(p)
        ws.ingest(noisy_verification_evidence(
            world, p, step,
            actual_accuracy=actual_accuracy,
            reported_reliability=reported_reliability,
            draw=rng.random(),
        ))
    gain = before - loss(ws, world)
    return {"seed": world.seed, "policy": policy, "gain": gain, "chosen": chosen}


def paired_summary(a: list[float], b: list[float]) -> dict:
    if len(a) != len(b) or not a:
        raise ValueError("paired vectors must have equal positive length")
    d = [x - y for x, y in zip(a, b)]
    mean = statistics.mean(d)
    se = 0.0 if len(d) == 1 else statistics.stdev(d) / math.sqrt(len(d))
    return {
        "n": len(d),
        "mean_difference": mean,
        "normal_approx_95_ci": [mean - 1.96 * se, mean + 1.96 * se],
        "wins": sum(x > 1e-12 for x in d),
        "ties": sum(abs(x) <= 1e-12 for x in d),
        "losses": sum(x < -1e-12 for x in d),
    }


def audit_generator(generator: Callable[[int], object], root_seed: int,
                    n_worlds: int = 500, impact_weighted: bool = True) -> dict:
    rows = {name: [] for name in POLICIES}
    for i in range(n_worlds):
        world = generator(root_seed + i)
        for name in rows:
            rows[name].append(run_custom(
                world, name, impact_weighted=impact_weighted
            )["gain"])
    return {
        "n_worlds": n_worlds,
        "root_seed": root_seed,
        "impact_weighted": impact_weighted,
        "mean_gain": {name: statistics.mean(v) for name, v in rows.items()},
        "paired_vs_debt": {
            name: paired_summary(v, rows["debt"])
            for name, v in rows.items() if name != "debt"
        },
        "license": (
            "POST-HOC MECHANISM AUDIT on already-visible confirmation worlds. "
            "These comparisons can falsify or narrow mechanism stories but cannot "
            "confirm a replacement controller."
        ),
    }


def audit_existing_confirmations() -> dict:
    return {
        "generator_A": audit_generator(generate_world, 900_000),
        "generator_B": audit_generator(generate_transfer_world, 1_500_000),
    }
