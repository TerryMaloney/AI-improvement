"""Fingerprints for the Stage 0B search-exposure instrument.

Every load-bearing component of the instrument gets a hash derived from the
committed file, so a contract binding can name a fingerprint that a third party
can recompute. These are NOT freeze records -- nothing about Stage 0B is frozen
yet -- they are the machinery a freeze will use, committed before it is needed
so the freeze/grade/analyse driver is not written after outcomes exist (the
window the independent review named at §1.1).

Run:  python -m lab.stage0b_fingerprint
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT = REPO / "experiments" / "exp004_stage0b" / "instrument_fingerprints.json"

# path -> what it is load-bearing FOR. A component with no stated causal role
# does not belong in a fingerprint set; it just makes the set look thorough.
COMPONENTS: dict[str, str] = {
    "lab/stage0b_search.py":
        "dispatch, the runtime block parser, and the deterministic relevance flags",
    "lab/stage0b_harness.py":
        "arm A/C/D packets, the fixed-query rule, and the per-dispatch ledger row",
    "lab/stage0b_failures.py":
        "failure semantics, defined before any Stage 0B outcome exists",
    "lab/stage0b_divergence_probe.py":
        "the pre-treatment divergence probe and its selection rule",
    "lab/stage0b_runtime_gate.py":
        "the live correspondence gate",
    "lab/stage0b_cvd.py":
        "the C-vs-D pre-freeze discriminability requirement",
    "lab/grading_v2.py":
        "the candidate grader (NOT frozen: it must first meet answers that are not "
        "Stage 0A-M's)",
    ".claude/agents/stage0b-searcher.md":
        "the one search mechanism, shared by arms C and D",
    ".claude/agents/stage0b-query-writer.md":
        "arm C's query writer",
    ".claude/agents/stage0b-answerer.md":
        "the answerer, identical in every arm",
    "experiments/exp004_stage0b/divergence_canaries.yaml":
        "canary items for the probe; permanently barred from production",
}


def file_sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def audit() -> dict:
    out, missing = {}, []
    for rel, role in COMPONENTS.items():
        p = REPO / rel
        if not p.exists():
            missing.append(rel)
            continue
        out[rel] = {"sha16": file_sha(p), "bytes": p.stat().st_size, "load_bearing_for": role}
    combined = hashlib.sha256(
        json.dumps({k: v["sha16"] for k, v in sorted(out.items())}, sort_keys=True).encode()
    ).hexdigest()[:16]
    return {
        "set": "stage0b_instrument",
        "frozen": False,
        "why_not_frozen": "The instrument passes its live correspondence gate, but the "
                          "calibration bank has not run, the grader has not met a "
                          "non-Stage-0A-M answer, and power has not been re-derived from "
                          "measured values. Freezing now would freeze assumptions.",
        "components": out,
        "missing": missing,
        "combined_sha16": combined,
    }


def main() -> int:
    doc = audit()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=1) + "\n")
    print(json.dumps({"combined_sha16": doc["combined_sha16"],
                      "components": len(doc["components"]),
                      "missing": doc["missing"]}, indent=1))
    return 1 if doc["missing"] else 0


if __name__ == "__main__":
    sys.exit(main())
