"""Prospective counterfactual revision-value controllers for Generator C.

This module freezes the candidate and baselines before any Generator-C controller
outcome is inspected. Controller functions receive only ``ControllerView`` plus
the observable workspace. They never receive hidden truth, evaluation impacts,
actual source accuracy, actual lineage, or actual verifier accuracy.

Primary comparison:

    CRV-net vs uncertainty x structural downstream utility (UDU-net)

Both use the same tool-quality transform and acquisition cost. They differ only
in how they estimate consequence: CRV asks which current beliefs would actually
change under opposite tool reports; UDU counts all structural descendants.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
import random
import statistics
from typing import Callable

from lab.exp005_epi import BeliefStatus, EpistemicWorkspace, Evidence, ObjectivePolicy
from lab.exp005_epi_worlds_c import (
    AdversarialWorld, ControllerView, VerifierOffer,
)


@dataclass(frozen=True)
class VerificationAction:
    proposition: str
    tool_id: str
    estimated_net_value: float


Policy = Callable[[EpistemicWorkspace, ControllerView, set[str]], VerificationAction | None]


def build_workspace_c(world: AdversarialWorld) -> EpistemicWorkspace:
    ws = EpistemicWorkspace(ObjectivePolicy(
        "synthetic-generator-c",
        "Minimize decision-relevant epistemic error net of verification cost.",
        ("ingest_synthetic_evidence", "request_verification", "decline_verification"),
    ))
    for rule in world.rules:
        ws.add_rule(rule)
    for e in world.initial_evidence:
        ws.ingest(e)
    return ws


def clone_workspace(ws: EpistemicWorkspace) -> EpistemicWorkspace:
    clone = EpistemicWorkspace(ws.objective)
    for rule in ws.rules:
        clone.add_rule(rule)
    for e in ws.evidence_log:
        clone.ingest(e)
    return clone


def uncertainty(ws: EpistemicWorkspace, proposition: str) -> float:
    p = ws.belief(proposition).probability_true
    if p is None:
        return 1.0
    return 1.0 - abs(p - .5) * 2.0


def information_quality(reported_accuracy: float) -> float:
    """Symmetric binary-channel advantage over chance, in [0,1]."""
    return max(0.0, min(1.0, 2.0 * reported_accuracy - 1.0))


def _all_reported_utility(view: ControllerView) -> float:
    return max(1e-12, sum(view.reported_impacts.values()))


def structural_utility_fraction(ws: EpistemicWorkspace, view: ControllerView,
                                proposition: str) -> float:
    affected = {proposition} | ws.descendants(proposition)
    utility = sum(view.reported_impacts.get(p, 0.0) for p in affected)
    return utility / _all_reported_utility(view)


def _hypothetical_evidence(ws: EpistemicWorkspace, offer: VerifierOffer,
                           value: bool, suffix: str) -> Evidence:
    now = max((e.observed_at for e in ws.evidence_log), default=0) + 1
    return Evidence(
        evidence_id=f"HYP-{offer.tool_id}-{suffix}",
        proposition=offer.proposition,
        asserted_value=value,
        source_id=f"hypothetical-{offer.tool_id}",
        lineage_id=f"hypothetical-lineage-{offer.tool_id}-{suffix}",
        reliability=offer.reported_accuracy,
        observed_at=now,
        metadata={"kind": "counterfactual_only"},
    )


def counterfactual_affected_utility_fraction(
    ws: EpistemicWorkspace,
    view: ControllerView,
    offer: VerifierOffer,
) -> float:
    """Fraction of reported utility whose resolved state depends on tool report.

    This is a *revision* counterfactual, not an oracle-truth counterfactual. The
    hypothetical evidence uses the tool's reported reliability, so a weak tool
    that cannot move the current updater may have zero affected utility even when
    the proposition has many structural descendants.
    """
    yes = clone_workspace(ws)
    no = clone_workspace(ws)
    yes.ingest(_hypothetical_evidence(yes, offer, True, "TRUE"))
    no.ingest(_hypothetical_evidence(no, offer, False, "FALSE"))

    affected = 0.0
    for p, weight in view.reported_impacts.items():
        if yes.belief(p).resolved_value != no.belief(p).resolved_value:
            affected += weight
    return affected / _all_reported_utility(view)


def _offers(view: ControllerView, candidates: set[str]):
    return [o for o in view.verifier_offers if o.proposition in candidates]


def _best_positive(scored: list[tuple[float, VerifierOffer]]) -> VerificationAction | None:
    if not scored:
        return None
    score, offer = max(scored, key=lambda x: (x[0], x[1].tool_id))
    if score <= 0.0:
        return None
    return VerificationAction(offer.proposition, offer.tool_id, score)


def choose_crv_net(ws: EpistemicWorkspace, view: ControllerView,
                   candidates: set[str]) -> VerificationAction | None:
    scored: list[tuple[float, VerifierOffer]] = []
    for offer in _offers(view, candidates):
        u = uncertainty(ws, offer.proposition)
        consequence = counterfactual_affected_utility_fraction(ws, view, offer)
        score = u * consequence * information_quality(offer.reported_accuracy) - offer.cost
        scored.append((score, offer))
    return _best_positive(scored)


def choose_udu_net(ws: EpistemicWorkspace, view: ControllerView,
                   candidates: set[str]) -> VerificationAction | None:
    """Strong simple baseline: uncertainty x all structural downstream utility."""
    scored: list[tuple[float, VerifierOffer]] = []
    for offer in _offers(view, candidates):
        u = uncertainty(ws, offer.proposition)
        consequence = structural_utility_fraction(ws, view, offer.proposition)
        score = u * consequence * information_quality(offer.reported_accuracy) - offer.cost
        scored.append((score, offer))
    return _best_positive(scored)


def choose_structural_net(ws: EpistemicWorkspace, view: ControllerView,
                          candidates: set[str]) -> VerificationAction | None:
    """Structural-utility baseline without uncertainty weighting."""
    scored: list[tuple[float, VerifierOffer]] = []
    for offer in _offers(view, candidates):
        consequence = structural_utility_fraction(ws, view, offer.proposition)
        score = consequence * information_quality(offer.reported_accuracy) - offer.cost
        scored.append((score, offer))
    return _best_positive(scored)


def choose_uncertainty_own_net(ws: EpistemicWorkspace, view: ControllerView,
                               candidates: set[str]) -> VerificationAction | None:
    """Cost-aware uncertainty baseline that values only the queried belief itself."""
    total = _all_reported_utility(view)
    scored: list[tuple[float, VerifierOffer]] = []
    for offer in _offers(view, candidates):
        own = view.reported_impacts.get(offer.proposition, 0.0) / total
        score = (uncertainty(ws, offer.proposition) * own
                 * information_quality(offer.reported_accuracy) - offer.cost)
        scored.append((score, offer))
    return _best_positive(scored)


def choose_legacy_debt(ws: EpistemicWorkspace, view: ControllerView,
                       candidates: set[str]) -> VerificationAction | None:
    """Frozen old debt ranking, retained as a reference rather than primary baseline.

    The old controller had no tool-cost semantics. We preserve its proposition
    ranking and, once a proposition is selected, choose the offered tool with the
    greatest reported information-quality-per-cost. It always acts while budget
    and candidates remain; its net score is therefore intentionally not used as a
    primary fairness comparison against the cost-aware policies.
    """
    ranked = ws.verification_queue(current_time=10_000, impacts=view.reported_impacts)
    proposition = next((p for p, _ in ranked if p in candidates), None)
    if proposition is None:
        return None
    offers = [o for o in view.verifier_offers if o.proposition == proposition]
    if not offers:
        return None
    offer = max(
        offers,
        key=lambda o: (information_quality(o.reported_accuracy) / max(o.cost, 1e-12), o.tool_id),
    )
    return VerificationAction(proposition, offer.tool_id, float("nan"))


POLICIES: dict[str, Policy] = {
    "crv_net": choose_crv_net,
    "udu_net": choose_udu_net,
    "structural_net": choose_structural_net,
    "uncertainty_own_net": choose_uncertainty_own_net,
    "legacy_debt": choose_legacy_debt,
}


def evaluation_loss(ws: EpistemicWorkspace, world: AdversarialWorld,
                    *, impact_weighted: bool, unresolved_penalty: float = .5) -> float:
    total = 0.0
    denom = 0.0
    for p, truth in world.truth.items():
        weight = world.evaluation_impacts[p] if impact_weighted else 1.0
        pred = ws.belief(p).resolved_value
        if pred is None:
            err = unresolved_penalty
        else:
            err = float(pred != truth)
        total += weight * err
        denom += weight
    return total / denom if denom else 0.0


def _outcome_draw(world: AdversarialWorld, offer: VerifierOffer) -> float:
    payload = f"exp005-c-tool-outcome:{world.seed}:{offer.tool_id}:{offer.proposition}"
    h = hashlib.sha256(payload.encode()).digest()
    return random.Random(int.from_bytes(h[:8], "big")).random()


def realized_verification_evidence(world: AdversarialWorld, offer: VerifierOffer,
                                   step: int) -> Evidence:
    """Generate the hidden-realization of one verification action.

    The outcome is keyed only by world and action, not by policy or step, so two
    policies choosing the same action receive the same potential outcome.
    """
    actual = world.actual_verifier_accuracy[offer.tool_id]
    value = world.base_truth[offer.proposition]
    if _outcome_draw(world, offer) >= actual:
        value = not value
    return Evidence(
        evidence_id=f"VERIFY-C-{offer.tool_id}",
        proposition=offer.proposition,
        asserted_value=value,
        source_id=offer.tool_id,
        lineage_id=f"verification-lineage-{offer.tool_id}",
        reliability=offer.reported_accuracy,
        observed_at=20_000 + step,
        metadata={"kind": "generator_c_verification"},
    )


def run_policy_c(world: AdversarialWorld, policy: str, max_budget: int = 4) -> dict:
    if policy not in POLICIES:
        raise ValueError(f"unknown policy {policy!r}")
    if max_budget < 0 or max_budget > len(world.base_truth):
        raise ValueError("invalid max_budget")

    ws = build_workspace_c(world)
    view = world.controller_view()
    # A policy gets only the view. Hidden simulation fields remain in this runner.
    candidates = set(world.base_truth)
    offer_by_id = {o.tool_id: o for o in view.verifier_offers}

    before_w = evaluation_loss(ws, world, impact_weighted=True)
    before_u = evaluation_loss(ws, world, impact_weighted=False)
    chosen: list[dict] = []
    total_cost = 0.0
    stopped_early = False

    for step in range(max_budget):
        action = POLICIES[policy](ws, view, candidates)
        if action is None:
            stopped_early = True
            break
        if action.proposition not in candidates:
            raise RuntimeError("policy selected an unavailable proposition")
        offer = offer_by_id[action.tool_id]
        if offer.proposition != action.proposition:
            raise RuntimeError("policy selected mismatched proposition/tool")
        candidates.remove(action.proposition)
        ws.ingest(realized_verification_evidence(world, offer, step))
        total_cost += offer.cost
        chosen.append({
            "proposition": action.proposition,
            "tool_id": action.tool_id,
            "estimated_net_value": action.estimated_net_value,
            "reported_accuracy": offer.reported_accuracy,
            "actual_accuracy": world.actual_verifier_accuracy[offer.tool_id],
            "cost": offer.cost,
        })

    after_w = evaluation_loss(ws, world, impact_weighted=True)
    after_u = evaluation_loss(ws, world, impact_weighted=False)
    epistemic_gain_w = before_w - after_w
    epistemic_gain_u = before_u - after_u
    net_gain_w = epistemic_gain_w - total_cost

    return {
        "seed": world.seed,
        "policy": policy,
        "max_budget": max_budget,
        "actions_taken": len(chosen),
        "stopped_early": stopped_early,
        "before_weighted_loss": before_w,
        "after_weighted_loss": after_w,
        "weighted_epistemic_gain": epistemic_gain_w,
        "unweighted_epistemic_gain": epistemic_gain_u,
        "total_cost": total_cost,
        "weighted_net_gain": net_gain_w,
        "chosen": chosen,
    }


def _paired_summary(a: list[float], b: list[float]) -> dict:
    d = [x - y for x, y in zip(a, b)]
    if not d:
        raise ValueError("paired vectors must be non-empty")
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


def benchmark_c(generator, *, n_worlds: int = 1000, root_seed: int = 2_500_000,
                max_budget: int = 4) -> dict:
    rows: dict[str, list[dict]] = {p: [] for p in POLICIES}
    for i in range(n_worlds):
        world = generator(root_seed + i)
        for policy in POLICIES:
            rows[policy].append(run_policy_c(world, policy, max_budget=max_budget))

    summary = {}
    for policy, runs in rows.items():
        summary[policy] = {
            "n_worlds": n_worlds,
            "mean_weighted_epistemic_gain": statistics.mean(r["weighted_epistemic_gain"] for r in runs),
            "mean_unweighted_epistemic_gain": statistics.mean(r["unweighted_epistemic_gain"] for r in runs),
            "mean_total_cost": statistics.mean(r["total_cost"] for r in runs),
            "mean_weighted_net_gain": statistics.mean(r["weighted_net_gain"] for r in runs),
            "net_harm_rate": sum(r["weighted_net_gain"] < -1e-12 for r in runs) / n_worlds,
            "epistemic_harm_rate": sum(r["weighted_epistemic_gain"] < -1e-12 for r in runs) / n_worlds,
            "mean_actions": statistics.mean(r["actions_taken"] for r in runs),
            "early_stop_rate": sum(r["stopped_early"] for r in runs) / n_worlds,
        }

    def vector(policy: str, field: str) -> list[float]:
        return [r[field] for r in rows[policy]]

    paired = {
        "crv_minus_udu_net_gain": _paired_summary(
            vector("crv_net", "weighted_net_gain"),
            vector("udu_net", "weighted_net_gain"),
        ),
        "crv_minus_udu_weighted_epistemic_gain": _paired_summary(
            vector("crv_net", "weighted_epistemic_gain"),
            vector("udu_net", "weighted_epistemic_gain"),
        ),
        "crv_minus_udu_unweighted_epistemic_gain": _paired_summary(
            vector("crv_net", "unweighted_epistemic_gain"),
            vector("udu_net", "unweighted_epistemic_gain"),
        ),
        "crv_minus_legacy_net_gain": _paired_summary(
            vector("crv_net", "weighted_net_gain"),
            vector("legacy_debt", "weighted_net_gain"),
        ),
    }
    return {
        "root_seed": root_seed,
        "n_worlds": n_worlds,
        "max_budget": max_budget,
        "summary": summary,
        "paired": paired,
        "license": (
            "Prospective synthetic Generator-C controller test only. Policies see "
            "reported metadata and workspace state, not hidden simulation truth. "
            "A pass does not license natural-language extraction, real-world source "
            "inference, real-tool reliability, or LLM capability claims."
        ),
    }
