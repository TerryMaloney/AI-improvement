"""Deterministic longitudinal benchmark for EXP005-EPI.

This is not a model benchmark.  It validates the external epistemic machinery on
worlds where the evidence stream and ground truth are generated/declared by us.
Later phases replace claim ingestion with LLM/tool outputs while preserving these
tests as regression cases.
"""
from __future__ import annotations

from dataclasses import dataclass
import json

from lab.exp005_epi import (
    DerivedRule, EpistemicWorkspace, Evidence, MatchedRAG, NaiveRAG,
    ObjectivePolicy, RecentContext,
)


@dataclass(frozen=True)
class Scenario:
    name: str
    evidence: tuple[Evidence, ...]
    rules: tuple[DerivedRule, ...]
    expected_epistemic: dict[str, bool | None]
    ground_truth: dict[str, bool]
    description: str


def ev(i: str, p: str, value: bool, source: str, lineage: str,
       reliability: float, t: int, supersedes: tuple[str, ...] = ()) -> Evidence:
    return Evidence(i, p, value, source, lineage, reliability, t, supersedes)


def delayed_false_premise() -> Scenario:
    rules = (
        DerivedRule("rY", "Y", (("X", True),)),
        DerivedRule("rZ", "Z", (("X", True), ("A", True))),
    )
    rows = [
        ev("a1", "A", True, "registry", "registry", .98, 1),
        ev("x_bad", "X", True, "wire", "rumor-origin", .82, 2),
    ]
    for n in range(3, 18):
        rows.append(ev(f"d{n}", f"D{n}", n % 2 == 0, f"src{n}", f"lin{n}", .90, n))
    rows.append(ev("x_fix", "X", False, "primary-record", "primary-record", .98, 20))
    for n in range(21, 36):
        rows.append(ev(f"late{n}", f"L{n}", True, f"late-src{n}", f"late-lin{n}", .90, n))
    return Scenario(
        "delayed_false_premise", tuple(rows), rules,
        {"A": True, "X": False, "Y": False, "Z": False},
        {"A": True, "X": False, "Y": False, "Z": False},
        "A credible false premise is corrected much later; dependent beliefs must repair.",
    )


def copied_consensus() -> Scenario:
    rows = [
        ev(f"copy{i}", "X", True, f"copy-site-{i}", "single-origin", .82, i)
        for i in range(1, 6)
    ]
    rows.append(ev("independent", "X", False, "primary", "independent-primary", .97, 10))
    return Scenario(
        "copied_consensus", tuple(rows), (),
        {"X": False}, {"X": False},
        "Five apparent sources copy one origin; one stronger independent source contradicts them.",
    )


def false_correction_resistance() -> Scenario:
    rows = (
        ev("orig", "X", True, "primary", "primary", .98, 1),
        ev("weak-correction", "X", False, "blog", "blog", .65, 20),
    )
    return Scenario(
        "false_correction_resistance", rows, (),
        {"X": True}, {"X": True},
        "Weak newer evidence should not automatically overwrite strong established evidence.",
    )


def genuine_temporal_change() -> Scenario:
    rows = (
        ev("old", "X", True, "registry", "registry-v1", .98, 1),
        ev("new", "X", False, "registry", "registry-v2", .98, 20, supersedes=("old",)),
    )
    return Scenario(
        "genuine_temporal_change", rows, (),
        {"X": False}, {"X": False},
        "A later authoritative record explicitly supersedes an old state.",
    )


def unresolved_conflict() -> Scenario:
    rows = (
        ev("s1", "X", True, "study-a", "study-a", .82, 1),
        ev("s2", "X", False, "study-b", "study-b", .82, 2),
    )
    return Scenario(
        "unresolved_conflict", rows, (),
        {"X": None}, {"X": True},
        "Balanced independent evidence should remain disputed instead of being forced to a side.",
    )


SCENARIOS = (
    delayed_false_premise,
    copied_consensus,
    false_correction_resistance,
    genuine_temporal_change,
    unresolved_conflict,
)


def _workspace_prediction(ws: EpistemicWorkspace, p: str) -> bool | None:
    return ws.belief(p).resolved_value


def run_workspace(s: Scenario) -> tuple[EpistemicWorkspace, dict[str, bool | None]]:
    ws = EpistemicWorkspace(ObjectivePolicy(
        "truthful-assistance",
        "Maintain the best-supported epistemic state without modifying permissions.",
        ("read_evidence", "propose_verification"),
    ))
    for r in s.rules:
        ws.add_rule(r)
    for e in s.evidence:
        ws.ingest(e)
    return ws, {p: _workspace_prediction(ws, p) for p in s.expected_epistemic}


def run_naive_rag(s: Scenario) -> dict[str, bool | None]:
    rag = NaiveRAG()
    for r in s.rules:
        rag.add_rule(r)
    for e in s.evidence:
        rag.ingest(e)
    return {p: rag.query(p) for p in s.expected_epistemic}


def run_matched_rag(s: Scenario) -> dict[str, bool | None]:
    rag = MatchedRAG()
    for r in s.rules:
        rag.add_rule(r)
    for e in s.evidence:
        rag.ingest(e)
    return {p: rag.query(p) for p in s.expected_epistemic}


def run_recent(s: Scenario, window: int = 8) -> dict[str, bool | None]:
    m = RecentContext(window=window)
    for r in s.rules:
        m.add_rule(r)
    for e in s.evidence:
        m.ingest(e)
    return {p: m.query(p) for p in s.expected_epistemic}


def score(pred: dict[str, bool | None], expected: dict[str, bool | None]) -> dict:
    keys = sorted(expected)
    correct = sum(pred.get(k) == expected[k] for k in keys)
    resolved_expected = [k for k in keys if expected[k] is not None]
    resolved_correct = sum(pred.get(k) == expected[k] for k in resolved_expected)
    return {
        "n": len(keys),
        "correct": correct,
        "accuracy": correct / len(keys) if keys else 1.0,
        "resolved_n": len(resolved_expected),
        "resolved_correct": resolved_correct,
    }


def benchmark() -> dict:
    results = {}
    totals = {"workspace": [0, 0], "matched_rag": [0, 0], "naive_rag": [0, 0], "recent_context": [0, 0]}
    for factory in SCENARIOS:
        s = factory()
        ws, wp = run_workspace(s)
        mp = run_matched_rag(s)
        np = run_naive_rag(s)
        rp = run_recent(s)
        row = {
            "description": s.description,
            "expected": s.expected_epistemic,
            "workspace": {"predictions": wp, **score(wp, s.expected_epistemic)},
            "matched_rag": {"predictions": mp, **score(mp, s.expected_epistemic)},
            "naive_rag": {"predictions": np, **score(np, s.expected_epistemic)},
            "recent_context": {"predictions": rp, **score(rp, s.expected_epistemic)},
            "workspace_revision_count": len(ws.revisions),
            "workspace_fingerprint": ws.fingerprint(),
        }
        results[s.name] = row
        for name, pred in (("workspace", wp), ("matched_rag", mp), ("naive_rag", np), ("recent_context", rp)):
            sc = score(pred, s.expected_epistemic)
            totals[name][0] += sc["correct"]
            totals[name][1] += sc["n"]
    return {
        "scenarios": results,
        "aggregate": {
            name: {"correct": c, "n": n, "accuracy": c / n if n else 1.0}
            for name, (c, n) in totals.items()
        },
        "license": (
            "Construct-validation only. These deterministic scenarios demonstrate that the "
            "implemented mechanisms behave as specified; they are not evidence that an LLM "
            "system is more accurate in the real world. The matched-RAG control receives the "
            "same reliability, lineage and supersession metadata and therefore blocks a weak "
            "claim that metadata access alone is an epistemic-workspace capability gain."
        ),
    }


def main() -> int:
    print(json.dumps(benchmark(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
