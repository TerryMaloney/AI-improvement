"""Seeded synthetic worlds and active-verification experiments for EXP005-EPI.

The world generator is independent of the epistemic-debt formula.  It samples
hidden boolean truth, an acyclic dependency graph, source reliabilities and noisy
observations.  A verification action reveals one base proposition through a
near-certain independent source.  This lets us test verification policies without
an LLM judge or web noise.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import random
from typing import Callable

from lab.exp005_epi import (
    DerivedRule, EpistemicWorkspace, Evidence, ObjectivePolicy,
)


@dataclass(frozen=True)
class SyntheticWorld:
    seed: int
    base_truth: dict[str, bool]
    truth: dict[str, bool]
    rules: tuple[DerivedRule, ...]
    initial_evidence: tuple[Evidence, ...]
    impacts: dict[str, float]

    @property
    def base_props(self) -> tuple[str, ...]:
        return tuple(sorted(self.base_truth))


def _rng(seed: int) -> random.Random:
    digest = hashlib.sha256(f"exp005-epi-world:{seed}".encode()).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


def _eval_rule(rule: DerivedRule, truth: dict[str, bool]) -> bool:
    return all(truth[p] == required for p, required in rule.premises)


def generate_world(seed: int, n_base: int = 12, n_derived: int = 18) -> SyntheticWorld:
    if n_base < 4 or n_derived < 1:
        raise ValueError("world too small")
    r = _rng(seed)
    base = {f"B{i:02d}": bool(r.getrandbits(1)) for i in range(n_base)}
    truth = dict(base)
    rules: list[DerivedRule] = []
    available = list(base)
    for i in range(n_derived):
        out = f"D{i:02d}"
        k = r.randint(1, min(3, len(available)))
        premises = tuple((p, bool(r.getrandbits(1))) for p in r.sample(available, k))
        rule = DerivedRule(f"R{i:02d}", out, premises, impact=round(r.uniform(.5, 2.0), 3))
        truth[out] = _eval_rule(rule, truth)
        rules.append(rule)
        available.append(out)

    evidence: list[Evidence] = []
    t = 1
    for p in sorted(base):
        reliability = round(r.uniform(.62, .91), 3)
        observed = base[p] if r.random() < reliability else not base[p]
        lineage = f"origin-{p}"
        evidence.append(Evidence(
            f"E-{p}-0", p, observed, f"source-{p}", lineage, reliability, t
        ))
        t += 1
        # Copying is generated independently of truth/correctness.
        if r.random() < .35:
            copies = r.randint(2, 5)
            for j in range(copies):
                evidence.append(Evidence(
                    f"E-{p}-copy{j}", p, observed, f"copy-{p}-{j}", lineage,
                    max(.51, reliability - r.uniform(0, .05)), t
                ))
                t += 1
        # Occasionally add a genuinely independent second observation.
        if r.random() < .30:
            rel2 = round(r.uniform(.62, .90), 3)
            obs2 = base[p] if r.random() < rel2 else not base[p]
            evidence.append(Evidence(
                f"E-{p}-ind", p, obs2, f"ind-{p}", f"ind-lineage-{p}",
                rel2, t
            ))
            t += 1

    impacts = {p: round(r.uniform(.5, 2.5), 3) for p in truth}
    return SyntheticWorld(seed, base, truth, tuple(rules), tuple(evidence), impacts)


def build_workspace(world: SyntheticWorld) -> EpistemicWorkspace:
    ws = EpistemicWorkspace(ObjectivePolicy(
        "synthetic-truth",
        "Minimize epistemic error under a fixed verification budget.",
        ("ingest_synthetic_evidence", "request_verification"),
    ))
    for rule in world.rules:
        ws.add_rule(rule)
    for e in world.initial_evidence:
        ws.ingest(e)
    return ws


def prediction(ws: EpistemicWorkspace, proposition: str) -> bool | None:
    return ws.belief(proposition).resolved_value


def loss(ws: EpistemicWorkspace, world: SyntheticWorld,
         unresolved_penalty: float = 0.5, impact_weighted: bool = True) -> float:
    total = 0.0
    denom = 0.0
    for p, truth in world.truth.items():
        w = world.impacts[p] if impact_weighted else 1.0
        pred = prediction(ws, p)
        if pred is None:
            err = unresolved_penalty
        else:
            err = float(pred != truth)
        total += w * err
        denom += w
    return total / denom if denom else 0.0


def verification_evidence(world: SyntheticWorld, proposition: str, step: int) -> Evidence:
    if proposition not in world.base_truth:
        raise ValueError("verification acts only on base propositions")
    return Evidence(
        evidence_id=f"VERIFY-{world.seed}-{proposition}-{step}",
        proposition=proposition,
        asserted_value=world.base_truth[proposition],
        source_id=f"verification-tool-{proposition}",
        lineage_id=f"verification-lineage-{world.seed}-{proposition}-{step}",
        reliability=.995,
        observed_at=10_000 + step,
        metadata={"kind": "verification", "oracle_truth_in_synthetic_world": True},
    )


def _uncertainty(ws: EpistemicWorkspace, p: str) -> float:
    b = ws.belief(p)
    if b.probability_true is None:
        return 1.0
    return 1.0 - abs(b.probability_true - .5) * 2.0


def choose_debt(ws: EpistemicWorkspace, world: SyntheticWorld,
                candidates: set[str], rng: random.Random) -> str:
    ranked = ws.verification_queue(current_time=10_000, impacts=world.impacts)
    for p, _ in ranked:
        if p in candidates:
            return p
    raise ValueError("no candidate")


def choose_uncertainty(ws: EpistemicWorkspace, world: SyntheticWorld,
                       candidates: set[str], rng: random.Random) -> str:
    return max(sorted(candidates), key=lambda p: (_uncertainty(ws, p), p))


def choose_dependency(ws: EpistemicWorkspace, world: SyntheticWorld,
                      candidates: set[str], rng: random.Random) -> str:
    return max(sorted(candidates), key=lambda p: (len(ws.descendants(p)), world.impacts[p], p))


def choose_random(ws: EpistemicWorkspace, world: SyntheticWorld,
                  candidates: set[str], rng: random.Random) -> str:
    return rng.choice(sorted(candidates))


def choose_oracle(ws: EpistemicWorkspace, world: SyntheticWorld,
                  candidates: set[str], rng: random.Random) -> str:
    """Upper-bound policy: select the action with greatest immediate true loss reduction."""
    before = loss(ws, world)
    best: tuple[float, str] | None = None
    for p in sorted(candidates):
        clone = build_workspace(world)
        # Replay verifications already present in ws.
        for e in ws.evidence_log:
            if e.metadata.get("kind") == "verification":
                clone.ingest(e)
        clone.ingest(verification_evidence(world, p, 999))
        gain = before - loss(clone, world)
        cand = (gain, p)
        if best is None or cand > best:
            best = cand
    assert best is not None
    return best[1]


POLICIES: dict[str, Callable] = {
    "debt": choose_debt,
    "uncertainty": choose_uncertainty,
    "dependency": choose_dependency,
    "random": choose_random,
    "oracle": choose_oracle,
}


def run_policy(world: SyntheticWorld, policy: str, budget: int = 3) -> dict:
    if policy not in POLICIES:
        raise ValueError(f"unknown policy {policy!r}")
    if budget < 0 or budget > len(world.base_truth):
        raise ValueError("invalid budget")
    ws = build_workspace(world)
    r = _rng(world.seed + 9_999)
    candidates = set(world.base_truth)
    before = loss(ws, world)
    trajectory = [before]
    chosen = []
    for step in range(budget):
        p = POLICIES[policy](ws, world, candidates, r)
        candidates.remove(p)
        chosen.append(p)
        ws.ingest(verification_evidence(world, p, step))
        trajectory.append(loss(ws, world))
    return {
        "seed": world.seed,
        "policy": policy,
        "budget": budget,
        "before_loss": before,
        "after_loss": trajectory[-1],
        "gain": before - trajectory[-1],
        "chosen": chosen,
        "trajectory": trajectory,
    }


def policy_benchmark(n_worlds: int = 200, budget: int = 3,
                     root_seed: int = 50_000, include_oracle: bool = False) -> dict:
    if n_worlds <= 0:
        raise ValueError("n_worlds must be positive")
    names = ["debt", "uncertainty", "dependency", "random"]
    if include_oracle:
        names.append("oracle")
    rows = {name: [] for name in names}
    for i in range(n_worlds):
        world = generate_world(root_seed + i)
        for name in names:
            rows[name].append(run_policy(world, name, budget))
    summary = {}
    for name, runs in rows.items():
        summary[name] = {
            "n_worlds": n_worlds,
            "budget": budget,
            "mean_before_loss": sum(x["before_loss"] for x in runs) / n_worlds,
            "mean_after_loss": sum(x["after_loss"] for x in runs) / n_worlds,
            "mean_gain": sum(x["gain"] for x in runs) / n_worlds,
            "worlds_improved": sum(x["gain"] > 1e-12 for x in runs),
            "worlds_harmed": sum(x["gain"] < -1e-12 for x in runs),
        }
    return {
        "summary": summary,
        "license": (
            "Synthetic controller construct experiment. Hidden truth, source reliabilities "
            "and source lineage are generated by the benchmark. The generator and debt "
            "heuristic were designed in the same research pass, so a positive result is "
            "only a development signal. It is not a held-out, real-world, or LLM "
            "capability claim."
        ),
    }
