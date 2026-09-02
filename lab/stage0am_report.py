"""Stage 0A-M: freeze raw outcomes, grade deterministically, run the frozen analysis.

Order is deliberate and enforced: raw outcomes are hashed and frozen BEFORE any
grade is computed, so post-outcome manipulation is detectable. Grading uses the
committed frozen grader at its recorded fingerprint. Analysis uses the committed
`lab.stage0am` procedure with no options.
"""
from __future__ import annotations

import hashlib
import json
import pathlib

import yaml

from lab.anchored_grading import grade_boolean, grade_exact_entity, grade_numeric
from lab.stage0am import TrialOutcome, analyse, partition_pairs, retrieval_failure_rate

REPO = pathlib.Path(__file__).resolve().parent.parent
RUN = REPO / "runs" / "exp004_stage0am"
EXPECTED_GRADER = "10adaf1dac94ea70"


def _grader_sha() -> str:
    return hashlib.sha256((REPO / "lab" / "anchored_grading.py").read_bytes()).hexdigest()[:16]


def load_trials() -> list[dict]:
    return [json.loads(l) for l in (RUN / "trials.jsonl").read_text().splitlines() if l.strip()]


def freeze_raw(trials: list[dict]) -> dict:
    """Hash every raw response and the ledger, before grading."""
    files = sorted((RUN / "raw").glob("*.json"))
    per = {p.stem: hashlib.sha256(p.read_bytes()).hexdigest()[:16] for p in files}
    doc = {
        "n_raw_files": len(files),
        "n_ledger_rows": len(trials),
        "ledger_sha256_16": hashlib.sha256((RUN / "trials.jsonl").read_bytes()).hexdigest()[:16],
        "raw_response_sha256_16": per,
        "combined_sha256_16": hashlib.sha256(
            json.dumps(per, sort_keys=True).encode()).hexdigest()[:16],
        "frozen_before_grading": True,
    }
    (RUN / "raw_outcomes.frozen.json").write_text(json.dumps(doc, indent=1) + "\n")
    return doc


def grade_all(trials: list[dict]) -> list[dict]:
    sha = _grader_sha()
    assert sha == EXPECTED_GRADER, f"grader fingerprint {sha} != frozen {EXPECTED_GRADER}"
    keys = yaml.safe_load((REPO / "batteries" / "answers.anchored_v1.yaml").read_text())["answers"]
    out = []
    for t in trials:
        rec = dict(t)
        if t["dispatch_failure"] or t["answer"] is None:
            rec["graded"] = None
        else:
            k = keys[t["item_id"]]
            a = t["answer"]
            if k["route"] == "numeric":
                ok = grade_numeric(a, k["value"], k["tolerance"], k.get("rejects", []))
            elif k["route"] == "exact_entity":
                ok = grade_exact_entity(a, k["accept"], k.get("rejects", []))
            else:
                ok = grade_boolean(a, k["expected"])
            rec["graded"] = int(ok)
        out.append(rec)
    (RUN / "graded.jsonl").write_text("".join(json.dumps(r) + "\n" for r in out))
    return out


def build_pairs(graded: list[dict]):
    by = {}
    for g in graded:
        by.setdefault(g["item_id"], {})[g["arm"]] = g
    pairs, cls = [], {}
    for iid, arms in sorted(by.items()):
        c, r = arms["closed"], arms["retrieval_enabled"]
        cls[iid] = c["class"]
        pairs.append((
            TrialOutcome(iid, "closed", c["graded"], (), c["dispatch_failure"]),
            TrialOutcome(iid, "retrieval_enabled", r["graded"], (), r["dispatch_failure"]),
        ))
    return pairs, cls


def analyse_run(graded: list[dict]) -> dict:
    pairs, cls = build_pairs(graded)
    by_class: dict[str, list] = {}
    for p in pairs:
        by_class.setdefault(cls[p[0].item_id], []).append(p)

    retained, voided, cause = {}, {}, {}
    for name, ps in by_class.items():
        r, v, cz = partition_pairs(ps)
        retained[name], voided[name], cause[name] = r, v, cz

    primary = {k: retained[k] for k in ("date_anchored", "definition_anchored") if k in retained}
    control = {k: retained[k] for k in ("arithmetic_control",) if k in retained}
    res = analyse(primary, control)

    def cell(ps):
        n00 = sum(1 for c, r in ps if c == 0 and r == 0)
        n01 = sum(1 for c, r in ps if c == 0 and r == 1)
        n10 = sum(1 for c, r in ps if c == 1 and r == 0)
        n11 = sum(1 for c, r in ps if c == 1 and r == 1)
        return {"n00": n00, "n01": n01, "n10": n10, "n11": n11, "D": n01 + n10, "n": len(ps)}

    out = {"grader_sha256_16": _grader_sha(), "primary": {}, "negative_control": {}}
    for name, cr in res.primary.items():
        out["primary"][name] = {**cell(retained[name]), "raw_p": cr.p_value,
                                "holm_rejected": cr.rejected,
                                "paired_risk_difference": cr.risk_difference,
                                "harm_rate_upper_95": cr.harm_rate_upper_95,
                                "voided": voided[name], "void_cause": cause[name]}
    for name, cr in res.negative_control.items():
        out["negative_control"][name] = {**cell(retained[name]), "raw_p": cr.p_value,
                                         "harm_rate_upper_95": cr.harm_rate_upper_95,
                                         "paired_risk_difference": cr.risk_difference,
                                         "voided": voided[name], "void_cause": cause[name]}
    out["alpha"] = res.alpha
    out["any_primary_rejected"] = res.any_primary_rejected
    out["total_voided_items"] = sum(len(v) for v in voided.values())
    out["void_rate"] = out["total_voided_items"] / max(1, len(pairs))
    trials_t = [TrialOutcome(g["item_id"], g["arm"], g["graded"], (), g["dispatch_failure"])
                for g in graded]
    out["retrieval_failure_rate"] = retrieval_failure_rate(trials_t)
    return out
