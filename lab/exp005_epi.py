"""EXP005-EPI persistent epistemic workspace.

The LLM is not the source of truth.  This module provides an external, inspectable
epistemic state with four hard separations:

* evidence is immutable observation history;
* beliefs are derived and revisable;
* derivations record dependencies so revisions propagate;
* objective/permission state is frozen and is never rewritten by evidence.

The first implementation is intentionally boolean and deterministic.  It is a
scientific instrument for testing longitudinal belief revision before adding an
LLM claim extractor or real-world retrieval.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import hashlib
import json
import math
from typing import Iterable


class BeliefStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    REJECTED = "REJECTED"
    DISPUTED = "DISPUTED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ObjectivePolicy:
    objective_id: str
    description: str
    permissions: tuple[str, ...] = ()


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    proposition: str
    asserted_value: bool
    source_id: str
    lineage_id: str
    reliability: float
    observed_at: int
    supersedes: tuple[str, ...] = ()
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.evidence_id:
            raise ValueError("evidence_id is required")
        if not self.proposition:
            raise ValueError("proposition is required")
        if not self.source_id or not self.lineage_id:
            raise ValueError("source_id and lineage_id are required")
        if not 0.5 < float(self.reliability) < 1.0:
            raise ValueError("reliability must be strictly between 0.5 and 1.0")
        if self.observed_at < 0:
            raise ValueError("observed_at must be non-negative")

    def canonical(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True)
class DerivedRule:
    """A deterministic boolean derivation.

    `op="all"` means the output is the conjunction of premise truth conditions.
    A premise is `(proposition, required_value)`.  This is sufficient for the
    first delayed-false-premise benchmark and keeps the ground truth executable.
    """
    rule_id: str
    output: str
    premises: tuple[tuple[str, bool], ...]
    op: str = "all"
    impact: float = 1.0

    def __post_init__(self) -> None:
        if not self.rule_id or not self.output or not self.premises:
            raise ValueError("rule_id, output and premises are required")
        if self.op != "all":
            raise ValueError("v1 supports only op='all'")
        if self.impact <= 0:
            raise ValueError("impact must be positive")


@dataclass(frozen=True)
class Belief:
    proposition: str
    status: BeliefStatus
    probability_true: float | None
    independent_support_lineages: int
    independent_reject_lineages: int
    active_evidence_ids: tuple[str, ...]
    derived_from: tuple[str, ...] = ()
    updated_at: int = 0

    @property
    def resolved_value(self) -> bool | None:
        if self.status == BeliefStatus.SUPPORTED:
            return True
        if self.status == BeliefStatus.REJECTED:
            return False
        return None


@dataclass(frozen=True)
class Revision:
    revision_id: str
    proposition: str
    observed_at: int
    old_status: BeliefStatus
    new_status: BeliefStatus
    old_probability_true: float | None
    new_probability_true: float | None
    reason: str
    evidence_ids: tuple[str, ...] = ()
    premise_ids: tuple[str, ...] = ()


def _logit_weight(reliability: float) -> float:
    return math.log(reliability / (1.0 - reliability))


def _logistic(score: float) -> float:
    if score >= 0:
        z = math.exp(-score)
        return 1.0 / (1.0 + z)
    z = math.exp(score)
    return z / (1.0 + z)


class EpistemicWorkspace:
    """External truth-maintenance layer with explicit evidence lineage."""

    SUPPORT_THRESHOLD = 0.80
    REJECT_THRESHOLD = 0.20

    def __init__(self, objective: ObjectivePolicy):
        self._objective = objective
        self._evidence: dict[str, Evidence] = {}
        self._rules: dict[str, DerivedRule] = {}
        self._beliefs: dict[str, Belief] = {}
        self._revisions: list[Revision] = []
        self._clock = 0

    @property
    def objective(self) -> ObjectivePolicy:
        return self._objective

    @property
    def evidence_log(self) -> tuple[Evidence, ...]:
        return tuple(sorted(self._evidence.values(), key=lambda e: (e.observed_at, e.evidence_id)))

    @property
    def revisions(self) -> tuple[Revision, ...]:
        return tuple(self._revisions)

    @property
    def rules(self) -> tuple[DerivedRule, ...]:
        return tuple(self._rules.values())

    def belief(self, proposition: str) -> Belief:
        return self._beliefs.get(
            proposition,
            Belief(proposition, BeliefStatus.UNKNOWN, None, 0, 0, (), (), self._clock),
        )

    def ingest(self, evidence: Evidence) -> None:
        """Append evidence.  Existing evidence is never mutated or deleted."""
        if evidence.evidence_id in self._evidence:
            if self._evidence[evidence.evidence_id] == evidence:
                return
            raise ValueError(f"evidence id collision: {evidence.evidence_id}")
        for sid in evidence.supersedes:
            if sid not in self._evidence:
                raise ValueError(f"cannot supersede unknown evidence {sid!r}")
        self._evidence[evidence.evidence_id] = evidence
        self._clock = max(self._clock, evidence.observed_at)
        self.recompute()

    def add_rule(self, rule: DerivedRule) -> None:
        if rule.rule_id in self._rules and self._rules[rule.rule_id] != rule:
            raise ValueError(f"rule id collision: {rule.rule_id}")
        if any(r.output == rule.output and r.rule_id != rule.rule_id for r in self._rules.values()):
            raise ValueError(f"v1 permits one derivation rule per output: {rule.output}")
        self._rules[rule.rule_id] = rule
        self._assert_acyclic()
        self.recompute()

    def _assert_acyclic(self) -> None:
        graph: dict[str, set[str]] = {}
        outputs = {r.output for r in self._rules.values()}
        for r in self._rules.values():
            graph.setdefault(r.output, set())
            for p, _ in r.premises:
                if p in outputs:
                    graph.setdefault(p, set()).add(r.output)
        indeg = {n: 0 for n in graph}
        for u in graph:
            for v in graph[u]:
                indeg[v] = indeg.get(v, 0) + 1
        queue = [n for n, d in indeg.items() if d == 0]
        seen = 0
        while queue:
            n = queue.pop()
            seen += 1
            for v in graph.get(n, ()):
                indeg[v] -= 1
                if indeg[v] == 0:
                    queue.append(v)
        if seen != len(indeg):
            raise ValueError("derived rules must form an acyclic dependency graph")

    def _superseded_ids(self) -> set[str]:
        out: set[str] = set()
        for e in self._evidence.values():
            out.update(e.supersedes)
        return out

    def _active_direct_evidence(self, proposition: str) -> list[Evidence]:
        superseded = self._superseded_ids()
        return [
            e for e in self._evidence.values()
            if e.proposition == proposition and e.evidence_id not in superseded
        ]

    @staticmethod
    def _lineage_representatives(evidence: Iterable[Evidence]) -> list[Evidence]:
        """Count copied evidence once per lineage.

        Within a lineage, the most reliable active item is the representative;
        recency breaks equal-reliability ties.  This is a declared v1 rule, not a
        learned source-trust model.
        """
        best: dict[str, Evidence] = {}
        for e in evidence:
            cur = best.get(e.lineage_id)
            key = (e.reliability, e.observed_at, e.evidence_id)
            if cur is None or key > (cur.reliability, cur.observed_at, cur.evidence_id):
                best[e.lineage_id] = e
        return list(best.values())

    def _direct_belief(self, proposition: str) -> Belief:
        reps = self._lineage_representatives(self._active_direct_evidence(proposition))
        if not reps:
            return Belief(proposition, BeliefStatus.UNKNOWN, None, 0, 0, (), (), self._clock)
        score = 0.0
        supports = rejects = 0
        for e in reps:
            w = _logit_weight(e.reliability)
            if e.asserted_value:
                score += w
                supports += 1
            else:
                score -= w
                rejects += 1
        p = _logistic(score)
        if p >= self.SUPPORT_THRESHOLD:
            status = BeliefStatus.SUPPORTED
        elif p <= self.REJECT_THRESHOLD:
            status = BeliefStatus.REJECTED
        elif supports and rejects:
            status = BeliefStatus.DISPUTED
        else:
            status = BeliefStatus.UNKNOWN
        return Belief(
            proposition=proposition,
            status=status,
            probability_true=p,
            independent_support_lineages=supports,
            independent_reject_lineages=rejects,
            active_evidence_ids=tuple(sorted(e.evidence_id for e in reps)),
            updated_at=self._clock,
        )

    def _rule_for_output(self, proposition: str) -> DerivedRule | None:
        for r in self._rules.values():
            if r.output == proposition:
                return r
        return None

    def _derived_belief(self, rule: DerivedRule, current: dict[str, Belief]) -> Belief:
        premise_beliefs = [current.get(p, self.belief(p)) for p, _ in rule.premises]
        values = [b.resolved_value for b in premise_beliefs]
        any_false = any(v is not None and v != required
                        for v, (_, required) in zip(values, rule.premises))
        all_true = all(v is not None and v == required
                       for v, (_, required) in zip(values, rule.premises))
        if all_true:
            status, p = BeliefStatus.SUPPORTED, 1.0
        elif any_false:
            status, p = BeliefStatus.REJECTED, 0.0
        else:
            status, p = BeliefStatus.UNKNOWN, None
        return Belief(
            proposition=rule.output,
            status=status,
            probability_true=p,
            independent_support_lineages=0,
            independent_reject_lineages=0,
            active_evidence_ids=(),
            derived_from=tuple(p for p, _ in rule.premises),
            updated_at=self._clock,
        )

    def recompute(self) -> None:
        old = dict(self._beliefs)
        direct_props = {e.proposition for e in self._evidence.values()}
        rule_outputs = {r.output for r in self._rules.values()}
        current: dict[str, Belief] = {
            p: self._direct_belief(p) for p in direct_props if p not in rule_outputs
        }
        unresolved = list(self._rules.values())
        for _ in range(len(unresolved) + 1):
            changed = False
            for rule in list(unresolved):
                premises_ready = all(
                    p in current or self._rule_for_output(p) is None for p, _ in rule.premises
                )
                if not premises_ready:
                    continue
                for p, _ in rule.premises:
                    current.setdefault(p, self._direct_belief(p))
                current[rule.output] = self._derived_belief(rule, current)
                unresolved.remove(rule)
                changed = True
            if not changed:
                break
        if unresolved:
            raise RuntimeError("could not resolve derived rules")

        all_props = set(old) | set(current)
        self._beliefs = current
        for prop in sorted(all_props):
            before = old.get(prop, Belief(prop, BeliefStatus.UNKNOWN, None, 0, 0, (), (), self._clock))
            after = current.get(prop, Belief(prop, BeliefStatus.UNKNOWN, None, 0, 0, (), (), self._clock))
            if (before.status, before.probability_true) != (after.status, after.probability_true):
                rid_payload = f"{prop}|{self._clock}|{before.status}|{after.status}|{len(self._revisions)}"
                rid = hashlib.sha256(rid_payload.encode()).hexdigest()[:16]
                reason = "derived_dependency_recompute" if after.derived_from else "evidence_recompute"
                self._revisions.append(Revision(
                    revision_id=rid,
                    proposition=prop,
                    observed_at=self._clock,
                    old_status=before.status,
                    new_status=after.status,
                    old_probability_true=before.probability_true,
                    new_probability_true=after.probability_true,
                    reason=reason,
                    evidence_ids=after.active_evidence_ids,
                    premise_ids=after.derived_from,
                ))

    def descendants(self, proposition: str) -> set[str]:
        graph: dict[str, set[str]] = {}
        for r in self._rules.values():
            for p, _ in r.premises:
                graph.setdefault(p, set()).add(r.output)
        seen: set[str] = set()
        stack = list(graph.get(proposition, ()))
        while stack:
            n = stack.pop()
            if n in seen:
                continue
            seen.add(n)
            stack.extend(graph.get(n, ()))
        return seen

    def provenance(self, proposition: str) -> dict:
        b = self.belief(proposition)
        evidence = [asdict(self._evidence[eid]) for eid in b.active_evidence_ids]
        premises = {p: self.provenance(p) for p in b.derived_from}
        return {
            "proposition": proposition,
            "status": b.status.value,
            "probability_true": b.probability_true,
            "evidence": evidence,
            "premises": premises,
        }

    def epistemic_debt(self, proposition: str, current_time: int | None = None,
                       decision_impact: float = 1.0) -> float:
        """Prioritise weak, stale, load-bearing beliefs for verification."""
        now = self._clock if current_time is None else current_time
        b = self.belief(proposition)
        if b.probability_true is None:
            uncertainty = 1.0
        else:
            uncertainty = 1.0 - abs(b.probability_true - 0.5) * 2.0
        active = [self._evidence[eid] for eid in b.active_evidence_ids if eid in self._evidence]
        if active:
            fragility = 1.0 / max(1, len({e.lineage_id for e in active}))
            last = max(e.observed_at for e in active)
            staleness = 1.0 + max(0, now - last) / 10.0
        else:
            fragility = 1.0
            staleness = 1.0
        load = 1.0 + len(self.descendants(proposition))
        return uncertainty * fragility * staleness * load * decision_impact

    def verification_queue(self, current_time: int | None = None,
                           impacts: dict[str, float] | None = None) -> list[tuple[str, float]]:
        impacts = impacts or {}
        propositions = set(self._beliefs)
        ranked = [
            (p, self.epistemic_debt(p, current_time, impacts.get(p, 1.0)))
            for p in propositions
        ]
        return sorted(ranked, key=lambda x: (-x[1], x[0]))

    def snapshot(self) -> dict:
        return {
            "objective": asdict(self._objective),
            "clock": self._clock,
            "evidence": [asdict(e) for e in self.evidence_log],
            "rules": [asdict(r) for r in self.rules],
            "beliefs": {p: {
                **asdict(b), "status": b.status.value
            } for p, b in sorted(self._beliefs.items())},
            "revisions": [{
                **asdict(r),
                "old_status": r.old_status.value,
                "new_status": r.new_status.value,
            } for r in self._revisions],
        }

    def fingerprint(self) -> str:
        payload = json.dumps(self.snapshot(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode()).hexdigest()[:16]


class NaiveRAG:
    """A deliberately simple flat-memory comparator.

    It stores all documents, treats every document as independent, and evaluates
    the latest requested proposition on demand.  It has no source-lineage
    deduplication, no belief history, no epistemic debt and no persistent revision
    propagation.  Derived rules are evaluated recursively only when queried.
    """

    SUPPORT_THRESHOLD = 0.80
    REJECT_THRESHOLD = 0.20

    def __init__(self):
        self.evidence: list[Evidence] = []
        self.rules: dict[str, DerivedRule] = {}

    def ingest(self, evidence: Evidence) -> None:
        self.evidence.append(evidence)

    def add_rule(self, rule: DerivedRule) -> None:
        self.rules[rule.output] = rule

    def _base(self, proposition: str) -> bool | None:
        superseded = {sid for e in self.evidence for sid in e.supersedes}
        rows = [e for e in self.evidence
                if e.proposition == proposition and e.evidence_id not in superseded]
        if not rows:
            return None
        score = sum((_logit_weight(e.reliability) if e.asserted_value else
                     -_logit_weight(e.reliability)) for e in rows)
        p = _logistic(score)
        if p >= self.SUPPORT_THRESHOLD:
            return True
        if p <= self.REJECT_THRESHOLD:
            return False
        return None

    def query(self, proposition: str, _stack: set[str] | None = None) -> bool | None:
        if proposition not in self.rules:
            return self._base(proposition)
        stack = set() if _stack is None else _stack
        if proposition in stack:
            return None
        stack.add(proposition)
        rule = self.rules[proposition]
        vals = [(self.query(p, stack), expected) for p, expected in rule.premises]
        stack.remove(proposition)
        if any(v is not None and v != expected for v, expected in vals):
            return False
        if all(v is not None and v == expected for v, expected in vals):
            return True
        return None


class RecentContext:
    """Comparator with only the most recent K evidence items."""
    def __init__(self, window: int = 8):
        if window <= 0:
            raise ValueError("window must be positive")
        self.window = window
        self.evidence: list[Evidence] = []
        self.rules: dict[str, DerivedRule] = {}

    def ingest(self, evidence: Evidence) -> None:
        self.evidence.append(evidence)

    def add_rule(self, rule: DerivedRule) -> None:
        self.rules[rule.output] = rule

    def query(self, proposition: str, _stack: set[str] | None = None) -> bool | None:
        rag = NaiveRAG()
        rag.evidence = self.evidence[-self.window:]
        rag.rules = self.rules
        return rag.query(proposition, _stack)
