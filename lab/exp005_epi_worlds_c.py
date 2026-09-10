"""Prospective adversarial synthetic world family for EXP005-EPI.

Generator C is intentionally hostile to simple structural verification heuristics.
It changes several assumptions that were oracle-clean in Generators A/B:

* structurally downstream paths can be blocked by other resolved premises;
* source reliability labels are noisy estimates of hidden source accuracy;
* reported lineage can falsely split copied evidence or merge independent evidence;
* temporal updates can be missed and false corrections can claim supersession;
* decision-impact labels are noisy estimates of evaluation importance;
* each base proposition has heterogeneous verification quality and cost;
* verifier reported accuracy can be miscalibrated relative to hidden accuracy.

This module contains no controller ranking function and no policy outcome code.
Hidden fields exist only for simulation/evaluation. A controller should receive a
ControllerView rather than the full AdversarialWorld.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import random

from lab.exp005_epi import DerivedRule, Evidence


@dataclass(frozen=True)
class VerifierOffer:
    tool_id: str
    proposition: str
    reported_accuracy: float
    cost: float


@dataclass(frozen=True)
class ControllerView:
    reported_impacts: dict[str, float]
    verifier_offers: tuple[VerifierOffer, ...]


@dataclass(frozen=True)
class AdversarialWorld:
    seed: int
    base_truth: dict[str, bool]
    truth: dict[str, bool]
    rules: tuple[DerivedRule, ...]
    initial_evidence: tuple[Evidence, ...]
    evaluation_impacts: dict[str, float]
    reported_impacts: dict[str, float]
    verifier_offers: tuple[VerifierOffer, ...]
    actual_verifier_accuracy: dict[str, float]
    actual_source_accuracy: dict[str, float]
    actual_lineage: dict[str, str]
    temporal_changed: tuple[str, ...]
    false_corrections: tuple[str, ...]
    gate_props: tuple[str, ...]

    @property
    def base_props(self) -> tuple[str, ...]:
        return tuple(sorted(self.base_truth))

    def controller_view(self) -> ControllerView:
        return ControllerView(dict(self.reported_impacts), self.verifier_offers)


def _rng(seed: int) -> random.Random:
    h = hashlib.sha256(f"exp005-epi-adversarial-c:{seed}".encode()).digest()
    return random.Random(int.from_bytes(h[:8], "big"))


def _clip(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _rule_truth(rule: DerivedRule, truth: dict[str, bool]) -> bool:
    return all(truth[p] == expected for p, expected in rule.premises)


def generate_adversarial_world(seed: int, n_base: int = 16) -> AdversarialWorld:
    if n_base != 16:
        raise ValueError("Generator C v1 is frozen at exactly 16 base propositions")
    r = _rng(seed)
    props = [f"C{i:02d}" for i in range(n_base)]
    gates = tuple(props[8:12])
    non_gates = [p for p in props if p not in gates]

    initial_truth = {p: bool(r.getrandbits(1)) for p in props}
    final_truth = dict(initial_truth)
    changed = set(r.sample(non_gates, k=3))
    for p in changed:
        final_truth[p] = not final_truth[p]

    domains = ("science", "operations", "policy", "maintenance")
    domain_accuracy = {
        "science": r.uniform(.72, .90),
        "operations": r.uniform(.64, .84),
        "policy": r.uniform(.60, .80),
        "maintenance": r.uniform(.68, .88),
    }

    evidence: list[Evidence] = []
    actual_source_accuracy: dict[str, float] = {}
    actual_lineage: dict[str, str] = {}
    ids_by_prop: dict[str, list[str]] = {p: [] for p in props}
    t = 1

    for i, p in enumerate(props):
        domain = domains[i % len(domains)]
        if p in gates:
            actual_q = .985
            reported_q = .965
            observed = initial_truth[p]
        else:
            actual_q = _clip(domain_accuracy[domain] + r.uniform(-.09, .09), .56, .95)
            reported_q = _clip(actual_q + r.uniform(-.12, .12), .55, .97)
            if i % 6 == seed % 6:
                reported_q = _clip(reported_q + .10, .55, .97)
            observed = initial_truth[p] if r.random() < actual_q else not initial_truth[p]

        source = f"C-{domain}-source-{p}"
        eid = f"C-{p}-old"
        true_lineage = f"actual-origin-{p}"
        reported_lineage = f"reported-origin-{p}"
        evidence.append(Evidence(eid, p, observed, source, reported_lineage,
                                 reported_q, t))
        actual_source_accuracy[eid] = actual_q
        actual_lineage[eid] = true_lineage
        ids_by_prop[p].append(eid)
        t += 1

        if p not in gates and r.random() < .50:
            for j in range(r.randint(2, 5)):
                ceid = f"C-{p}-copy{j}"
                # Copies are actually dependent, but some are falsely presented
                # as independent lineages to the workspace.
                if r.random() < .45:
                    shown_lineage = f"reported-split-{p}-{j}"
                else:
                    shown_lineage = reported_lineage
                q_copy = _clip(reported_q + r.uniform(-.04, .03), .51, .97)
                evidence.append(Evidence(
                    ceid, p, observed, f"republisher-{p}-{j}", shown_lineage,
                    q_copy, t
                ))
                actual_source_accuracy[ceid] = actual_q
                actual_lineage[ceid] = true_lineage
                ids_by_prop[p].append(ceid)
                t += 1

        if p not in gates and r.random() < .38:
            aeid = f"C-{p}-independent"
            actual_q2 = _clip(domain_accuracy[domain] + r.uniform(-.12, .10), .56, .94)
            reported_q2 = _clip(actual_q2 + r.uniform(-.12, .12), .52, .97)
            obs2 = initial_truth[p] if r.random() < actual_q2 else not initial_truth[p]
            # Some genuinely independent evidence is falsely merged with the
            # original reported lineage.
            shown_lineage = reported_lineage if r.random() < .28 else f"reported-independent-{p}"
            evidence.append(Evidence(
                aeid, p, obs2, f"independent-{domain}-{p}", shown_lineage,
                reported_q2, t
            ))
            actual_source_accuracy[aeid] = actual_q2
            actual_lineage[aeid] = f"actual-independent-{p}"
            ids_by_prop[p].append(aeid)
            t += 1

    # Genuine temporal changes. A recognized update supersedes the prior records;
    # a missed relationship leaves stale evidence active.
    for p in sorted(changed):
        q_actual = r.uniform(.72, .95)
        q_reported = _clip(q_actual + r.uniform(-.10, .10), .56, .97)
        value = final_truth[p] if r.random() < q_actual else not final_truth[p]
        supersedes = tuple(ids_by_prop[p]) if r.random() < .78 else ()
        eid = f"C-{p}-temporal-update"
        evidence.append(Evidence(
            eid, p, value, f"temporal-update-{p}", f"reported-update-{p}",
            q_reported, 500 + t, supersedes=supersedes
        ))
        actual_source_accuracy[eid] = q_actual
        actual_lineage[eid] = f"actual-update-{p}"
        t += 1

    stable_non_gates = [p for p in non_gates if p not in changed]
    false_corr = set(r.sample(stable_non_gates, k=2))
    for p in sorted(false_corr):
        q_actual = r.uniform(.54, .70)
        q_reported = _clip(q_actual + r.uniform(.08, .22), .62, .94)
        # The false-correction event is deliberately wrong in the generated world;
        # its reported confidence can nevertheless be high.
        value = not final_truth[p]
        supersedes = tuple(ids_by_prop[p]) if r.random() < .45 else ()
        eid = f"C-{p}-false-correction"
        evidence.append(Evidence(
            eid, p, value, f"late-correction-{p}", f"reported-correction-{p}",
            q_reported, 900 + t, supersedes=supersedes
        ))
        actual_source_accuracy[eid] = q_actual
        actual_lineage[eid] = f"actual-false-correction-{p}"
        t += 1

    truth = dict(final_truth)
    rules: list[DerivedRule] = []

    # Four deliberately blocked chains. The gate premise is guaranteed false in
    # hidden truth and has high-quality initial evidence, so raw descendant count
    # can exaggerate the current value of resolving the target proposition.
    for i in range(4):
        target = props[i]
        gate = gates[i]
        target_required = bool(r.getrandbits(1))
        gate_required = not final_truth[gate]
        a = DerivedRule(f"C-BLK-{i}-A", f"BLK{i}A",
                        ((target, target_required), (gate, gate_required)),
                        impact=round(r.uniform(.4, 2.8), 4))
        truth[a.output] = _rule_truth(a, truth)
        rules.append(a)
        b = DerivedRule(f"C-BLK-{i}-B", f"BLK{i}B", ((a.output, True),),
                        impact=round(r.uniform(.4, 2.8), 4))
        truth[b.output] = _rule_truth(b, truth)
        rules.append(b)
        c = DerivedRule(f"C-BLK-{i}-C", f"BLK{i}C", ((b.output, True),),
                        impact=round(r.uniform(.4, 2.8), 4))
        truth[c.output] = _rule_truth(c, truth)
        rules.append(c)

    # Four open chains where the target really can flip downstream conclusions.
    for i, target in enumerate(props[4:8]):
        req = bool(r.getrandbits(1))
        a = DerivedRule(f"C-OPEN-{i}-A", f"OPEN{i}A", ((target, req),),
                        impact=round(r.uniform(.4, 2.8), 4))
        truth[a.output] = _rule_truth(a, truth)
        rules.append(a)
        b = DerivedRule(f"C-OPEN-{i}-B", f"OPEN{i}B", ((a.output, True),),
                        impact=round(r.uniform(.4, 2.8), 4))
        truth[b.output] = _rule_truth(b, truth)
        rules.append(b)
        c = DerivedRule(f"C-OPEN-{i}-C", f"OPEN{i}C", ((b.output, True),),
                        impact=round(r.uniform(.4, 2.8), 4))
        truth[c.output] = _rule_truth(c, truth)
        rules.append(c)

    # Mixed hub and random structure prevents the benchmark from reducing to only
    # the handcrafted blocked/open motifs.
    hub = props[12]
    for i in range(5):
        other = props[(i + 1) % 8]
        rule = DerivedRule(
            f"C-HUB-{i}", f"HUB{i}",
            ((hub, bool(r.getrandbits(1))), (other, bool(r.getrandbits(1)))),
            impact=round(r.uniform(.3, 3.0), 4),
        )
        truth[rule.output] = _rule_truth(rule, truth)
        rules.append(rule)

    available = list(truth)
    for i in range(7):
        picks = r.sample(available, k=r.randint(2, 3))
        rule = DerivedRule(
            f"C-RND-{i}", f"RND-C-{i}",
            tuple((p, bool(r.getrandbits(1))) for p in picks),
            impact=round(r.uniform(.3, 3.0), 4),
        )
        truth[rule.output] = _rule_truth(rule, truth)
        rules.append(rule)
        available.append(rule.output)

    evaluation_impacts: dict[str, float] = {}
    for p in truth:
        evaluation_impacts[p] = round(r.uniform(.25, 3.5), 4)
    reported_impacts: dict[str, float] = {}
    for i, (p, actual) in enumerate(sorted(evaluation_impacts.items())):
        estimate = actual * r.uniform(.70, 1.30)
        if i % 9 == seed % 9:
            estimate *= r.choice((.55, 1.65))
        reported_impacts[p] = round(_clip(estimate, .10, 5.0), 4)

    offers: list[VerifierOffer] = []
    actual_verifier_accuracy: dict[str, float] = {}
    for i, p in enumerate(props):
        fast_reported = r.uniform(.63, .83)
        fast_actual = _clip(fast_reported + r.uniform(-.12, .08), .52, .94)
        if i % 4 == seed % 4:
            fast_actual = _clip(fast_actual - .10, .52, .94)
        fast_id = f"verify-fast-{p}"
        offers.append(VerifierOffer(
            fast_id, p, round(fast_reported, 4), round(r.uniform(.004, .015), 5)
        ))
        actual_verifier_accuracy[fast_id] = round(fast_actual, 4)

        deep_reported = r.uniform(.83, .97)
        deep_actual = _clip(deep_reported + r.uniform(-.08, .05), .56, .985)
        if i % 5 == seed % 5:
            deep_actual = _clip(deep_actual - .12, .56, .985)
        deep_id = f"verify-deep-{p}"
        offers.append(VerifierOffer(
            deep_id, p, round(deep_reported, 4), round(r.uniform(.016, .048), 5)
        ))
        actual_verifier_accuracy[deep_id] = round(deep_actual, 4)

    return AdversarialWorld(
        seed=seed,
        base_truth=final_truth,
        truth=truth,
        rules=tuple(rules),
        initial_evidence=tuple(sorted(evidence, key=lambda e: (e.observed_at, e.evidence_id))),
        evaluation_impacts=evaluation_impacts,
        reported_impacts=reported_impacts,
        verifier_offers=tuple(offers),
        actual_verifier_accuracy=actual_verifier_accuracy,
        actual_source_accuracy=actual_source_accuracy,
        actual_lineage=actual_lineage,
        temporal_changed=tuple(sorted(changed)),
        false_corrections=tuple(sorted(false_corr)),
        gate_props=gates,
    )
