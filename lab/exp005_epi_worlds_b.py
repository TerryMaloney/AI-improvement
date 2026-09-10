"""Structurally different synthetic world family for EXP005-EPI transfer.

Generator B is committed before any controller is evaluated on it.  It deliberately
changes topology and evidence processes relative to Generator A: explicit
temporal changes, false corrections, domain-conditioned source quality, chain/hub
dependencies, copied-source clusters, and impact/dependency decorrelation.

This module contains no verification-policy ranking function.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import random

from lab.exp005_epi import DerivedRule, Evidence


@dataclass(frozen=True)
class TransferWorld:
    seed: int
    base_truth: dict[str, bool]
    truth: dict[str, bool]
    rules: tuple[DerivedRule, ...]
    initial_evidence: tuple[Evidence, ...]
    impacts: dict[str, float]
    domains: dict[str, str]
    temporal_changed: tuple[str, ...]
    false_corrections: tuple[str, ...]

    @property
    def base_props(self) -> tuple[str, ...]:
        return tuple(sorted(self.base_truth))


def _rng(seed: int) -> random.Random:
    h = hashlib.sha256(f"exp005-epi-transfer-b:{seed}".encode()).digest()
    return random.Random(int.from_bytes(h[:8], "big"))


def _rule_truth(rule: DerivedRule, truth: dict[str, bool]) -> bool:
    return all(truth[p] == expected for p, expected in rule.premises)


def generate_transfer_world(seed: int, n_base: int = 14) -> TransferWorld:
    if n_base < 10:
        raise ValueError("Generator B requires at least 10 base propositions")
    r = _rng(seed)
    props = [f"T{i:02d}" for i in range(n_base)]
    domains_list = ("science", "operations", "policy")
    domains = {p: domains_list[i % len(domains_list)] for i, p in enumerate(props)}
    domain_quality = {
        "science": r.uniform(.70, .90),
        "operations": r.uniform(.64, .86),
        "policy": r.uniform(.60, .82),
    }

    initial_truth = {p: bool(r.getrandbits(1)) for p in props}
    final_truth = dict(initial_truth)
    changed = set(r.sample(props, k=max(2, n_base // 5)))
    for p in changed:
        final_truth[p] = not final_truth[p]

    evidence: list[Evidence] = []
    t = 1
    for p in props:
        q = domain_quality[domains[p]]
        rel = min(.94, max(.55, q + r.uniform(-.08, .08)))
        observed_old = initial_truth[p] if r.random() < rel else not initial_truth[p]
        old_id = f"B-{p}-old"
        lineage = f"B-origin-{p}"
        evidence.append(Evidence(old_id, p, observed_old, f"{domains[p]}-source-{p}",
                                 lineage, rel, t))
        t += 1

        copy_prob = {"science": .20, "operations": .40, "policy": .55}[domains[p]]
        if r.random() < copy_prob:
            for j in range(r.randint(2, 6)):
                evidence.append(Evidence(
                    f"B-{p}-copy{j}", p, observed_old, f"republisher-{p}-{j}",
                    lineage, max(.51, rel - r.uniform(0, .06)), t
                ))
                t += 1

        if p in changed:
            update_rel = min(.96, max(.58, domain_quality[domains[p]] + r.uniform(-.02, .10)))
            update_value = final_truth[p] if r.random() < update_rel else not final_truth[p]
            supersedes = (old_id,) if update_value == final_truth[p] else ()
            evidence.append(Evidence(
                f"B-{p}-change", p, update_value, f"update-{p}", f"update-lineage-{p}",
                update_rel, 500 + t, supersedes=supersedes
            ))
            t += 1

    stable = [p for p in props if p not in changed]
    false_corr = set(r.sample(stable, k=max(1, len(stable) // 4)))
    for p in sorted(false_corr):
        rel = r.uniform(.58, .76)
        evidence.append(Evidence(
            f"B-{p}-false-correction", p, not final_truth[p],
            f"late-rumor-{p}", f"late-rumor-lineage-{p}", rel, 900 + t
        ))
        t += 1

    truth = dict(final_truth)
    rules: list[DerivedRule] = []

    prev = props[0]
    for i in range(5):
        out = f"C{i:02d}"
        required = bool(r.getrandbits(1))
        rule = DerivedRule(f"BC{i:02d}", out, ((prev, required),),
                           impact=round(r.uniform(.5, 1.3), 3))
        truth[out] = _rule_truth(rule, truth)
        rules.append(rule)
        prev = out

    hub = props[1]
    for i in range(7):
        out = f"H{i:02d}"
        other = props[2 + (i % (len(props) - 2))]
        rule = DerivedRule(
            f"BH{i:02d}", out,
            ((hub, bool(r.getrandbits(1))), (other, bool(r.getrandbits(1)))),
            impact=round(r.uniform(.2, .8), 3),
        )
        truth[out] = _rule_truth(rule, truth)
        rules.append(rule)

    for i, p in enumerate(props[-3:]):
        out = f"I{i:02d}"
        rule = DerivedRule(f"BI{i:02d}", out, ((p, bool(r.getrandbits(1))),),
                           impact=round(r.uniform(2.5, 4.0), 3))
        truth[out] = _rule_truth(rule, truth)
        rules.append(rule)

    available = list(truth)
    for i in range(6):
        out = f"RND{i:02d}"
        picks = r.sample(available, k=r.randint(2, 3))
        rule = DerivedRule(
            f"BR{i:02d}", out,
            tuple((p, bool(r.getrandbits(1))) for p in picks),
            impact=round(r.uniform(.4, 2.2), 3),
        )
        truth[out] = _rule_truth(rule, truth)
        rules.append(rule)
        available.append(out)

    impacts = {p: round(r.uniform(.3, 3.5), 3) for p in final_truth}
    impacts.update({r_.output: r_.impact for r_ in rules})

    return TransferWorld(
        seed=seed,
        base_truth=final_truth,
        truth=truth,
        rules=tuple(rules),
        initial_evidence=tuple(sorted(evidence, key=lambda e: (e.observed_at, e.evidence_id))),
        impacts=impacts,
        domains=domains,
        temporal_changed=tuple(sorted(changed)),
        false_corrections=tuple(sorted(false_corr)),
    )
