"""INDEPENDENT post-result review of Stage 0A-M. Read-only.

This module re-derives every load-bearing number in
``runs/exp004_stage0am/EXP004_STAGE0AM_REPORT.md`` from the persisted artifacts,
using its own statistics rather than ``lab.stage0am``'s, so that a shared bug in
the analysis path cannot make the reconstruction agree by construction.

It writes exactly one file, ``runs/exp004_stage0am/independent_review.json``.
It never writes ``trials.jsonl``, ``graded.jsonl``, ``analysis.json``,
``raw_outcomes.frozen.json`` or ``lab/anchored_grading.py``, and it never
dispatches.

Three things are kept strictly apart:

  OBSERVED     recomputed from a persisted artifact
  INFERRED     follows from OBSERVED facts plus a stated rule
  POST-HOC     a counterfactual re-grade, computed for diagnosis only. It has no
               standing over the frozen result and is labelled as such wherever
               it appears.
"""
from __future__ import annotations

import collections
import hashlib
import json
import pathlib
import re
from fractions import Fraction
from math import comb

import yaml

from lab.anchored_grading import grade_boolean, grade_exact_entity, grade_numeric, normalise

REPO = pathlib.Path(__file__).resolve().parent.parent
RUN = REPO / "runs" / "exp004_stage0am"
EXPERIMENT = REPO / "experiments" / "exp004_stage0am"
OUT = RUN / "independent_review.json"

FROZEN_GRADER_SHA = "10adaf1dac94ea70"
FROZEN_BATTERY_FP = "1ec90754f1de2696"
FREEZE_COMMIT = "a1f4efb482a6f20265a11ef45a3bd435df0dd660"
PRIMARY_CLASSES = ("date_anchored", "definition_anchored")
CONTROL_CLASSES = ("arithmetic_control",)


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------

def load_all() -> dict:
    graded = [json.loads(l) for l in (RUN / "graded.jsonl").read_text().splitlines() if l.strip()]
    trials = [json.loads(l) for l in (RUN / "trials.jsonl").read_text().splitlines() if l.strip()]
    return {
        "graded": graded,
        "trials": trials,
        "keys": yaml.safe_load((REPO / "batteries" / "answers.anchored_v1.yaml").read_text())["answers"],
        "battery": {q["id"]: q for q in
                    yaml.safe_load((REPO / "batteries" / "anchored_v1.yaml").read_text())["questions"]},
        "frozen": json.loads((RUN / "raw_outcomes.frozen.json").read_text()),
        "schedule": json.loads((EXPERIMENT / "schedule.json").read_text()),
        "official": json.loads((RUN / "analysis.json").read_text()),
    }


def raw_for(trial_id: str) -> dict:
    return json.loads((RUN / "raw" / f"{trial_id}.json").read_text())


# ---------------------------------------------------------------------------
# statistics -- deliberately re-implemented, and in exact rationals
# ---------------------------------------------------------------------------

def exact_one_sided_p(n10: int, n01: int) -> Fraction:
    """P(X >= n10) for X ~ Binomial(n10+n01, 1/2), exactly."""
    d = n10 + n01
    if d == 0:
        return Fraction(1)
    return Fraction(sum(comb(d, i) for i in range(n10, d + 1)), 2 ** d)


def holm(pvalues: dict[str, Fraction], alpha: Fraction = Fraction(1, 20)) -> dict[str, bool]:
    order = sorted(pvalues, key=lambda k: pvalues[k])
    out, live = {}, True
    for rank, key in enumerate(order):
        if live and pvalues[key] <= alpha / (len(order) - rank):
            out[key] = True
        else:
            live = False
            out[key] = False
    return out


def cp_upper(k: int, n: int, conf: float = 0.95) -> float:
    """Clopper-Pearson one-sided upper limit on a binomial rate."""
    if n <= 0:
        raise ValueError("n must be positive")
    if k >= n:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(300):
        mid = (lo + hi) / 2
        tail = sum(comb(n, i) * mid ** i * (1 - mid) ** (n - i) for i in range(0, k + 1))
        lo, hi = (mid, hi) if tail > 1 - conf else (lo, mid)
    return (lo + hi) / 2


def min_attainable_p(D: int) -> Fraction:
    """The smallest p-value reachable at a realized discordant count D -- i.e. if
    every discordant pair had pointed the harm way. If this exceeds the Holm
    threshold, no orientation of the observed data could have rejected."""
    return exact_one_sided_p(D, 0)


def smallest_rejecting_D(alpha: Fraction) -> int:
    D = 0
    while min_attainable_p(D) > alpha:
        D += 1
        if D > 200:
            raise RuntimeError("unreachable")
    return D


# ---------------------------------------------------------------------------
# PHASE 1 -- execution integrity
# ---------------------------------------------------------------------------

def integrity(data: dict) -> dict:
    graded, trials, frozen = data["graded"], data["trials"], data["frozen"]
    g_by, t_by = {g["trial_id"]: g for g in graded}, {t["trial_id"]: t for t in trials}

    raw_files = sorted((RUN / "raw").glob("*.json"))
    per = {p.stem: hashlib.sha256(p.read_bytes()).hexdigest()[:16] for p in raw_files}

    by_item: dict[str, dict[str, dict]] = {}
    for g in graded:
        by_item.setdefault(g["item_id"], {})[g["arm"]] = g

    sched = data["schedule"]["schedule"]
    by_order = {g["dispatch_order"]: g for g in graded}
    sched_errs = []
    for e in sched:
        pos = e["position"]
        first, second = by_order.get(2 * pos - 1), by_order.get(2 * pos)
        if not (first and second):
            sched_errs.append(f"position {pos}: missing dispatch")
            continue
        if {first["item_id"], second["item_id"]} != {e["item_id"]}:
            sched_errs.append(f"position {pos}: item mismatch")
        if (first["arm"], second["arm"]) != (e["arm_first"], e["arm_second"]):
            sched_errs.append(f"position {pos}: arm order mismatch")

    served = collections.Counter()
    denials = errors = 0
    for tid in sorted(g_by):
        raw = raw_for(tid)
        for m in raw["modelUsage"]:
            served[m] += 1
        denials += len(raw["permission_denials"])
        errors += bool(raw["is_error"])

    return {
        "n_raw_files": len(raw_files),
        "n_ledger_rows": len(trials),
        "n_graded_rows": len(graded),
        "n_items": len(by_item),
        "n_complete_pairs": sum(1 for a in by_item.values()
                                if set(a) == {"closed", "retrieval_enabled"}),
        "incomplete_pairs": sorted(i for i, a in by_item.items()
                                   if set(a) != {"closed", "retrieval_enabled"}),
        "per_file_hashes_match_freeze_record": per == frozen["raw_response_sha256_16"],
        "ledger_sha_recomputed": hashlib.sha256((RUN / "trials.jsonl").read_bytes()).hexdigest()[:16],
        "ledger_sha_in_freeze_record": frozen["ledger_sha256_16"],
        "combined_sha_recomputed": hashlib.sha256(
            json.dumps(per, sort_keys=True).encode()).hexdigest()[:16],
        "combined_sha_in_freeze_record": frozen["combined_sha256_16"],
        "frozen_before_grading_flag": frozen["frozen_before_grading"],
        "grading_added_no_other_field_change": all(
            all(t_by[tid].get(f) == g_by[tid].get(f) for f in t_by[tid]) for tid in t_by),
        "grader_sha_recomputed": hashlib.sha256(
            (REPO / "lab" / "anchored_grading.py").read_bytes()).hexdigest()[:16],
        "grader_sha_expected": FROZEN_GRADER_SHA,
        "single_freeze_commit": sorted({g["freeze_commit"] for g in graded}),
        "freeze_commit_expected": FREEZE_COMMIT,
        "dispatch_failures": sorted({str(g["dispatch_failure"]) for g in graded}),
        "ungradeable_rows": sum(1 for g in graded if g["graded"] is None),
        "schedule_compliance_errors": sched_errs,
        "dispatch_order_is_1_to_n": sorted(g["dispatch_order"] for g in graded) == list(
            range(1, len(graded) + 1)),
        "arm_agent_map": sorted({f"{g['arm']}->{g['agent']}" for g in graded}),
        "served_models_seen": dict(served),
        "permission_denials_total": denials,
        "harness_errors_total": errors,
        "arm_first_balance": dict(collections.Counter(e["arm_first"] for e in sched)),
    }


# ---------------------------------------------------------------------------
# PHASE 2 -- independent reconstruction of the primary result
# ---------------------------------------------------------------------------

def regrade_with_frozen_grader(data: dict) -> dict[str, int]:
    """Re-run the FROZEN grader on the FROZEN answers. Not a re-grade of record:
    a check that graded.jsonl is the deterministic image of trials.jsonl."""
    out = {}
    for t in data["trials"]:
        k = data["keys"][t["item_id"]]
        a = t["answer"]
        if k["route"] == "numeric":
            ok = grade_numeric(a, k["value"], k["tolerance"], k.get("rejects", []))
        elif k["route"] == "exact_entity":
            ok = grade_exact_entity(a, k["accept"], k.get("rejects", []))
        else:
            ok = grade_boolean(a, k["expected"])
        out[t["trial_id"]] = int(ok)
    return out


def tables(data: dict, grades: dict[tuple[str, str], int] | None = None) -> dict[str, dict]:
    """2x2 tables per class. `grades` defaults to the frozen graded ledger."""
    if grades is None:
        grades = {(g["item_id"], g["arm"]): g["graded"] for g in data["graded"]}
    cls = {g["item_id"]: g["class"] for g in data["graded"]}
    out: dict[str, dict] = {}
    for item, c in cls.items():
        t = out.setdefault(c, {"n00": 0, "n01": 0, "n10": 0, "n11": 0, "items": []})
        b, s = grades[(item, "closed")], grades[(item, "retrieval_enabled")]
        t[f"n{b}{s}"] += 1
        t["items"].append([item, b, s])
    for c, t in out.items():
        t["n"] = t["n00"] + t["n01"] + t["n10"] + t["n11"]
        t["D"] = t["n01"] + t["n10"]
        t["discordant"] = sorted(i for i, b, s in t["items"] if b != s)
    return out


def reconstruct(data: dict) -> dict:
    regraded = regrade_with_frozen_grader(data)
    official_grades = {g["trial_id"]: g["graded"] for g in data["graded"]}
    tab = tables(data)

    classes = {}
    for name, t in tab.items():
        p = exact_one_sided_p(t["n10"], t["n01"])
        classes[name] = {
            "n": t["n"], "n00": t["n00"], "n01": t["n01"], "n10": t["n10"], "n11": t["n11"],
            "D": t["D"],
            "p_exact_fraction": str(p), "p_exact_float": float(p),
            "paired_risk_difference": (t["n10"] - t["n01"]) / t["n"],
            "harm_rate_upper_95": cp_upper(t["n10"], t["n"]),
            "discordant_items": t["discordant"],
            "min_attainable_p_at_realized_D": float(min_attainable_p(t["D"])),
        }
    pv = {c: exact_one_sided_p(tab[c]["n10"], tab[c]["n01"]) for c in PRIMARY_CLASSES}
    decisions = holm(pv)
    for c, r in decisions.items():
        classes[c]["holm_rejected"] = r

    off = data["official"]
    agreement = {}
    for c in PRIMARY_CLASSES:
        o = off["primary"][c]
        agreement[c] = all([
            o["n00"] == classes[c]["n00"], o["n01"] == classes[c]["n01"],
            o["n10"] == classes[c]["n10"], o["n11"] == classes[c]["n11"],
            o["D"] == classes[c]["D"], o["n"] == classes[c]["n"],
            abs(o["raw_p"] - classes[c]["p_exact_float"]) < 1e-12,
            o["holm_rejected"] == classes[c]["holm_rejected"],
            abs(o["harm_rate_upper_95"] - classes[c]["harm_rate_upper_95"]) < 1e-9,
        ])
    for c in CONTROL_CLASSES:
        o = off["negative_control"][c]
        agreement[c] = all([
            o["n11"] == classes[c]["n11"], o["D"] == classes[c]["D"], o["n"] == classes[c]["n"],
            abs(o["raw_p"] - classes[c]["p_exact_float"]) < 1e-12,
        ])

    return {
        "regrade_matches_frozen_ledger": regraded == official_grades,
        "regrade_mismatches": sorted(k for k in regraded if regraded[k] != official_grades[k]),
        "classes": classes,
        "any_primary_rejected": any(decisions.values()),
        "holm_alpha": 0.05,
        "holm_thresholds": {"step_1_smallest_p": 0.025, "step_2": 0.05},
        "smallest_D_that_could_reject_at_0.025": smallest_rejecting_D(Fraction(1, 40)),
        "smallest_D_that_could_reject_at_0.05": smallest_rejecting_D(Fraction(1, 20)),
        "agrees_with_official_analysis_json": agreement,
        "materially_disagrees": not all(agreement.values()),
    }


# ---------------------------------------------------------------------------
# PHASE 3/4 -- ceiling and the grading artifact
# ---------------------------------------------------------------------------

def first_pos(haystack: str, needle: str) -> int | None:
    """Position of the first word-boundary match, on normalised text. This is the
    same normalisation the frozen grader uses, so positions are comparable to its
    verdicts; the grader itself only asks whether a match exists."""
    h, n = normalise(haystack), normalise(needle)
    if not n:
        return None
    m = re.search(rf"(?<!\w){re.escape(n)}(?!\w)", h)
    return m.start() if m else None


LEAD_CHARS = 40
"""A mention within this many normalised characters counts as 'led with'."""


def entity_forensics(data: dict) -> dict:
    """Every exact_entity trial, by deterministic string position only."""
    rows = []
    for g in data["graded"]:
        item = data["battery"][g["item_id"]]
        if item["grading_route"] != "exact_entity":
            continue
        key = data["keys"][g["item_id"]]
        a = g["answer"]
        acc = [p for p in (first_pos(a, x) for x in key["accept"]) if p is not None]
        rej = [(x, p) for x, p in ((x, first_pos(a, x)) for x in key.get("rejects", []))
               if p is not None]
        amin = min(acc) if acc else None
        rmin = min((p for _, p in rej), default=None)
        rows.append({
            "item": g["item_id"], "arm": g["arm"], "class": g["class"], "graded": g["graded"],
            "accept_present": amin is not None, "reject_present": rmin is not None,
            "accept_pos": amin, "reject_pos": rmin,
            "reject_aliases_hit": [x for x, _ in rej],
            "accept_before_reject": (amin is not None and (rmin is None or amin < rmin)),
            "led_with_accept": amin is not None and amin <= LEAD_CHARS,
        })
    both = [r for r in rows if r["accept_present"] and r["reject_present"]]
    return {
        "n_entity_trials": len(rows),
        "accept_present": sum(r["accept_present"] for r in rows),
        "accept_absent": sum(not r["accept_present"] for r in rows),
        "accept_absent_trials": [f"{r['item']}-{r['arm']}" for r in rows if not r["accept_present"]],
        "graded_correct": sum(r["graded"] for r in rows),
        "accept_present_but_graded_incorrect": sum(
            1 for r in rows if r["accept_present"] and r["graded"] == 0),
        "accept_and_reject_both_present": len(both),
        "of_those_accept_strictly_first": sum(r["accept_before_reject"] for r in both),
        "of_those_led_with_accept": sum(r["led_with_accept"] for r in both),
        "of_those_graded_incorrect": sum(1 for r in both if r["graded"] == 0),
        "rows": rows,
    }


_FIRST_POLARITY = re.compile(r"^\W*(yes|no)\b", re.IGNORECASE)


def boolean_forensics(data: dict) -> dict:
    rows = []
    for g in data["graded"]:
        item = data["battery"][g["item_id"]]
        if item["grading_route"] != "boolean":
            continue
        expected = bool(data["keys"][g["item_id"]]["expected"])
        m = _FIRST_POLARITY.match(g["answer"].strip())
        lead = m.group(1).lower() if m else None
        rows.append({
            "item": g["item_id"], "arm": g["arm"], "graded": g["graded"], "expected": expected,
            "leading_polarity_token": lead,
            "leading_token_is_correct": (lead is not None) and ((lead == "yes") == expected),
        })
    return {
        "n_boolean_trials": len(rows),
        "all_answers_lead_with_a_polarity_token": all(r["leading_polarity_token"] for r in rows),
        "leading_token_correct": sum(r["leading_token_is_correct"] for r in rows),
        "graded_correct": sum(r["graded"] for r in rows),
        "leading_token_correct_but_graded_incorrect": sum(
            1 for r in rows if r["leading_token_is_correct"] and r["graded"] == 0),
        "affected_trials": [f"{r['item']}-{r['arm']}" for r in rows
                            if r["leading_token_is_correct"] and r["graded"] == 0],
        "expected_true_items": sorted({r["item"] for r in rows if r["expected"]}),
        "rows": rows,
    }


def accuracy_by_class_arm(data: dict) -> dict:
    acc: dict[str, dict[str, list[int]]] = {}
    for g in data["graded"]:
        acc.setdefault(g["class"], {}).setdefault(g["arm"], []).append(g["graded"])
    return {c: {a: {"correct": sum(v), "n": len(v), "accuracy": sum(v) / len(v)}
                for a, v in arms.items()} for c, arms in acc.items()}


def accuracy_by_route(data: dict) -> dict:
    acc: dict[str, dict[str, list[int]]] = {}
    for g in data["graded"]:
        r = data["battery"][g["item_id"]]["grading_route"]
        acc.setdefault(f"{g['class']}/{r}", {}).setdefault(g["arm"], []).append(g["graded"])
    return {c: {a: f"{sum(v)}/{len(v)}" for a, v in arms.items()} for c, arms in acc.items()}


# ---------------------------------------------------------------------------
# POST-HOC counterfactual grader -- diagnosis only, never the result of record
# ---------------------------------------------------------------------------

def posthoc_regrade(data: dict) -> dict:
    """What the run would have scored under a first-mention / first-polarity rule.

    LABELLED POST-HOC. It is computed after outcomes were visible and has no
    inferential standing. Its only purpose is to answer one diagnostic question:
    is the date class's realized difficulty knowledge or instrument?
    """
    grades: dict[tuple[str, str], int] = {}
    for g in data["graded"]:
        item, key, a = data["battery"][g["item_id"]], data["keys"][g["item_id"]], g["answer"]
        if item["grading_route"] == "exact_entity":
            acc = [p for p in (first_pos(a, x) for x in key["accept"]) if p is not None]
            rej = [p for p in (first_pos(a, x) for x in key.get("rejects", [])) if p is not None]
            v = bool(acc) and (not rej or min(acc) < min(rej))
        elif item["grading_route"] == "boolean":
            m = _FIRST_POLARITY.match(a.strip())
            v = bool(m) and ((m.group(1).lower() == "yes") == bool(key["expected"]))
        else:
            v = grade_numeric(a, key["value"], key["tolerance"], key.get("rejects", []))
        grades[(g["item_id"], g["arm"])] = int(v)
    tab = tables(data, grades)
    return {
        "LABEL": "POST-HOC COUNTERFACTUAL -- diagnostic only, no inferential standing",
        "rule": "entity: first mention wins; boolean: first polarity token wins; numeric: unchanged",
        "total_correct": sum(grades.values()),
        "total_trials": len(grades),
        "accuracy_by_class_arm": {
            c: {a: {"correct": sum(v for (i, aa), v in grades.items()
                                   if aa == a and data["battery"][i]["class"] == c),
                    "n": sum(1 for (i, aa) in grades
                             if aa == a and data["battery"][i]["class"] == c)}
                for a in ("closed", "retrieval_enabled")} for c in tab},
        "tables": {c: {k: t[k] for k in ("n", "n00", "n01", "n10", "n11", "D")}
                   for c, t in tab.items()},
        "every_class_has_zero_discordance": all(t["D"] == 0 for t in tab.values()),
    }


# ---------------------------------------------------------------------------
# PHASE 5 -- the discordant pairs
# ---------------------------------------------------------------------------

def discordant_pairs(data: dict) -> list[dict]:
    by_item: dict[str, dict[str, dict]] = {}
    for g in data["graded"]:
        by_item.setdefault(g["item_id"], {})[g["arm"]] = g
    out = []
    for item, arms in sorted(by_item.items()):
        c, r = arms["closed"], arms["retrieval_enabled"]
        if c["graded"] == r["graded"]:
            continue
        key = data["keys"][item]
        rec: dict = {
            "item": item, "class": c["class"], "question": data["battery"][item]["text"],
            "route": data["battery"][item]["grading_route"],
            "orientation": "n10 (baseline-favouring / harm)" if c["graded"] == 1
                           else "n01 (retrieval-favouring / help)",
        }
        for arm, g in (("closed", c), ("retrieval_enabled", r)):
            raw = raw_for(g["trial_id"])
            acc = [p for p in (first_pos(g["answer"], x) for x in key.get("accept", []))
                   if p is not None]
            rej = [(x, first_pos(g["answer"], x)) for x in key.get("rejects", [])]
            rec[arm] = {
                "answer": g["answer"],
                "frozen_grade": g["graded"],
                "accept_hit_pos": min(acc) if acc else None,
                "reject_hits": [x for x, p in rej if p is not None],
                "web_search_requests": sum(v.get("webSearchRequests", 0)
                                           for v in raw["modelUsage"].values()),
                "num_turns": raw["num_turns"],
            }
        both_named = (rec["closed"]["accept_hit_pos"] is not None
                      and rec["retrieval_enabled"]["accept_hit_pos"] is not None)
        no_retrieval = rec["retrieval_enabled"]["web_search_requests"] == 0
        rec["both_arms_named_the_accepted_entity"] = both_named
        rec["retrieval_arm_performed_no_retrieval"] = no_retrieval
        rec["classification"] = (
            "GRADING / ELABORATION ARTIFACT" if both_named and no_retrieval
            else "POSSIBLE RETRIEVAL DISPLACEMENT" if not both_named and not no_retrieval
            else "AMBIGUOUS")
        rec["why"] = (
            "both arms named the accepted entity, and the retrieval arm issued zero searches, "
            "so the flip cannot be caused by retrieved content; it is produced by whether the "
            "answer also mentioned a reject alias, under entity-route reject-precedence."
            if rec["classification"] == "GRADING / ELABORATION ARTIFACT" else "see fields")
        out.append(rec)
    return out


# ---------------------------------------------------------------------------
# PHASE 6 -- retrieval uptake
# ---------------------------------------------------------------------------

def retrieval_uptake(data: dict) -> dict:
    """Uptake is measured from the RAW harness records, not from
    `analysis.json`'s `retrieval_failure_rate`, which was fed empty
    retrieval-outcome tuples and is therefore vacuous."""
    rows = []
    for g in data["graded"]:
        if g["arm"] != "retrieval_enabled":
            continue
        raw = raw_for(g["trial_id"])
        per = {m: v.get("webSearchRequests", 0) for m, v in raw["modelUsage"].items()}
        rows.append({
            "item": g["item_id"], "class": g["class"], "graded": g["graded"],
            "num_turns": raw["num_turns"],
            "server_tool_use": raw["usage"]["server_tool_use"],
            "model_usage_web_search_requests": per,
            "total_web_search_requests": sum(per.values()),
            "web_fetch_requests": raw["usage"]["server_tool_use"]["web_fetch_requests"],
            "permission_denials": len(raw["permission_denials"]),
            "outcome": "ATTEMPTED" if sum(per.values()) > 0 else "NOT_ATTEMPTED",
        })
    closed_grade = {g["item_id"]: g["graded"] for g in data["graded"] if g["arm"] == "closed"}
    att = [r for r in rows if r["outcome"] == "ATTEMPTED"]
    by_class = collections.Counter(r["class"] for r in att)
    n_by_class = collections.Counter(r["class"] for r in rows)
    return {
        "n_treated": len(rows),
        "attempted_retrieval": len(att),
        "not_attempted": len(rows) - len(att),
        "attempted_items": sorted(r["item"] for r in att),
        "web_fetch_attempted": sum(1 for r in rows if r["web_fetch_requests"] > 0),
        "total_search_requests": sum(r["total_web_search_requests"] for r in rows),
        "search_count_distribution": dict(
            collections.Counter(r["total_web_search_requests"] for r in rows)),
        "attempts_by_class": {c: f"{by_class.get(c, 0)}/{n_by_class[c]}" for c in n_by_class},
        "num_turns_distribution": dict(collections.Counter(r["num_turns"] for r in rows)),
        "num_turns_gt_1_iff_search_recorded": all(
            (r["num_turns"] > 1) == (r["total_web_search_requests"] > 0) for r in rows),
        "top_level_server_tool_use_web_search_total": sum(
            r["server_tool_use"]["web_search_requests"] for r in rows),
        "search_requests_billed_to_solver_model": sum(
            v for r in rows for m, v in r["model_usage_web_search_requests"].items() if "opus" in m),
        "among_attempted": {
            "retrieval_arm_correct": sum(r["graded"] for r in att),
            "closed_partner_correct": sum(closed_grade[r["item"]] for r in att),
            "discordant": sum(1 for r in att if r["graded"] != closed_grade[r["item"]]),
            "harm_rate_upper_95_given_actual_use": cp_upper(0, len(att)) if att else None,
        },
        "official_analysis_json_claim": data["official"]["retrieval_failure_rate"],
        "official_claim_is_vacuous": (
            data["official"]["retrieval_failure_rate"]["attempted_retrieval"] == 0
            and len(att) > 0),
        "rows": rows,
    }


def effort_by_arm(data: dict) -> dict:
    import statistics as st
    out: dict[str, dict] = {}
    per_arm: dict[str, list[dict]] = {}
    for g in data["graded"]:
        per_arm.setdefault(g["arm"], []).append(g)
    for arm, gs in per_arm.items():
        tel = [g["telemetry"] for g in gs]
        out[arm] = {
            "median_output_tokens": st.median(t["output_tokens"] for t in tel),
            "mean_output_tokens": round(st.mean(t["output_tokens"] for t in tel), 1),
            "thinking_tokens_total": sum(t["thinking_tokens"] for t in tel),
            "median_wall_s": st.median(t["wall_s"] for t in tel),
            "cost_usd": round(sum(t["cost_usd"] for t in tel), 4),
            "median_answer_chars": st.median(len(g["answer"]) for g in gs),
        }
    up = {r["item"]: r for r in retrieval_uptake(data)["rows"]}
    searched = [g for g in per_arm["retrieval_enabled"] if up[g["item_id"]]["outcome"] == "ATTEMPTED"]
    declined = [g for g in per_arm["retrieval_enabled"] if up[g["item_id"]]["outcome"] != "ATTEMPTED"]
    for label, gs in (("retrieval_enabled_that_searched", searched),
                      ("retrieval_enabled_that_declined", declined)):
        if not gs:
            continue
        out[label] = {
            "n": len(gs),
            "median_output_tokens": st.median(g["telemetry"]["output_tokens"] for g in gs),
            "median_wall_s": st.median(g["telemetry"]["wall_s"] for g in gs),
            "cost_usd": round(sum(g["telemetry"]["cost_usd"] for g in gs), 4),
        }
    return out


# ---------------------------------------------------------------------------

def review() -> dict:
    data = load_all()
    rec = reconstruct(data)
    ent, boo = entity_forensics(data), boolean_forensics(data)
    up = retrieval_uptake(data)
    tab = tables(data)
    return {
        "what_this_is": "INDEPENDENT post-result review of Stage 0A-M. Read-only. "
                        "Does not alter the frozen result.",
        "generated_by": "lab/stage0am_review.py",
        "phase_1_integrity": integrity(data),
        "phase_2_reconstruction": rec,
        "phase_3_ceiling": {
            "accuracy_by_class_and_arm": accuracy_by_class_arm(data),
            "accuracy_by_class_and_route": accuracy_by_route(data),
            "discordant_pairs_by_class": {c: t["D"] for c, t in tab.items()},
            "harm_rate_upper_95_by_class": {
                c: cp_upper(t["n10"], t["n"]) for c, t in tab.items()},
            "date_anchored_harm_bound_conditional_on_closed_correct": cp_upper(
                tab["date_anchored"]["n10"],
                tab["date_anchored"]["n10"] + tab["date_anchored"]["n11"]),
            "planned_baseline_accuracy": 0.85,
            "realized_closed_accuracy_primary": sum(
                g["graded"] for g in data["graded"]
                if g["arm"] == "closed" and g["class"] in PRIMARY_CLASSES) / 50,
        },
        "phase_4_grading_artifact": {"entity_route": ent, "boolean_route": boo,
                                     "posthoc_counterfactual": posthoc_regrade(data)},
        "phase_5_discordant_pairs": discordant_pairs(data),
        "phase_6_retrieval_uptake": up,
        "phase_6_effort": effort_by_arm(data),
    }


def main() -> int:
    doc = review()
    OUT.write_text(json.dumps(doc, indent=1, default=str) + "\n")
    print(f"wrote {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
