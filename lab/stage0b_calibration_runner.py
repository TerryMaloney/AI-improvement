"""Stage 0B calibration runner — executes the frozen plan, and decides nothing.

WHY THIS MODULE EXISTS
----------------------
The authoring protocol 5 requires the freeze/grade/analyse driver to be committed
BEFORE the first dispatch, because Stage 0A-M's driver was first committed with 33
outcomes already on disk and that is the one real provenance window in the whole
run. The pre-dispatch check found no such driver for calibration: the schema, the
statistics and the decision rules existed, and nothing executed them.

WHAT IT DELIBERATELY DOES NOT DO
--------------------------------
It exercises NO scientific discretion. It does not author an item, repair one,
choose a key, retry a stochastic search to obtain a better screen result, or
decide a verdict. Every judgement it makes is a lookup in a committed rule. Where
a committed rule does not cover a case, it records a failure and stops rather than
improvising -- an improvising driver is an unlogged experimenter.

THE ORDERING IT MAKES IMPOSSIBLE TO SKIP
----------------------------------------
    authored bank -> screen -> answers -> reference adjudication
                  -> human queue -> HUMAN VERDICTS -> candidate grading

`authorize_grading()` is the only door to the last step, and it refuses while any
escalated answer lacks an attributed human verdict. That is a lock, not a
convention: the grader cannot be run early by forgetting a step.

RESUMABILITY, BECAUSE THIS IS HUNDREDS OF PAID DISPATCHES
---------------------------------------------------------
Every dispatch gets a deterministic id and is appended to a JSONL ledger the
moment it returns, before the next expensive call. A resumed run replays the
ledger, skips completed ids, and re-dispatches nothing. A dropped session, a
killed container or an exhausted quota costs the dispatch in flight and nothing
else. There is no automatic retry anywhere: retrying is forbidden wherever it
would condition the sample on a realized outcome, and the runner does not get to
decide which case it is looking at.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from dataclasses import dataclass, field

from lab.stage0b_adjudication import DETERMINATE, ESCALATE, reference_verdict
from lab.stage0b_calibration import (BATCH1_DEV, BATCH1_HOLDOUT, CalibrationRow,
                                     validate_bank, validate_row)
from lab.stage0b_keys import screen_summary

REPO = pathlib.Path(__file__).resolve().parent.parent
RUNDIR = REPO / "runs" / "exp004_stage0b_calibration"

LEDGER = "batch{b}_dispatch_ledger.jsonl"      # append-only, crash-safe
ROWS = "batch{b}_rows.json"                    # derived view, rewritten wholesale
QUEUE = "batch{b}_human_adjudication_queue.json"
VERDICTS = "batch{b}_human_verdicts.json"

STAGES = ("validate", "screen", "answer", "adjudicate", "export-queue",
          "import-verdicts", "status")

ARMS_STAGE2 = ("A_closed", "C_query", "C_search", "D_production_search",
               "C_answer", "D_answer")


def sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def fingerprint_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def dispatch_id(item_id: str, stage: str, slot: str) -> str:
    """Deterministic and content-free: the same slot always has the same id, so a
    resume can tell 'already done' from 'not started' without interpreting results."""
    return f"{item_id}|{stage}|{slot}"


# --------------------------------------------------------------------------- #
# the append-only ledger
# --------------------------------------------------------------------------- #

class DispatchLedger:
    """Append-only JSONL. Durable before the next expensive action, by construction:
    every append opens, writes, flushes and fsyncs."""

    def __init__(self, path: pathlib.Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._done: dict[str, dict] = {}
        if self.path.exists():
            for line in self.path.read_text().splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue                      # a torn final line is not fatal
                if rec.get("dispatch_id"):
                    self._done[rec["dispatch_id"]] = rec

    def has(self, did: str) -> bool:
        return did in self._done

    def get(self, did: str) -> dict | None:
        return self._done.get(did)

    def append(self, rec: dict) -> None:
        import os
        self._done[rec["dispatch_id"]] = rec
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    def by_stage(self, stage: str) -> list[dict]:
        return [r for r in self._done.values() if r.get("stage") == stage]

    def __len__(self) -> int:
        return len(self._done)


# --------------------------------------------------------------------------- #
# the dispatch backend -- real or synthetic, chosen by the caller not the runner
# --------------------------------------------------------------------------- #

class Backend:
    """What the runner is allowed to ask the world for.

    `SyntheticBackend` implements the same surface from fixtures, so the whole
    pipeline is testable end to end with zero paid calls. The runner cannot tell
    them apart, which is what makes the dry run evidence about the runner rather
    than about a mock of it.
    """

    def search(self, query: str) -> dict:
        raise NotImplementedError

    def write_query(self, question: str) -> dict:
        raise NotImplementedError

    def answer(self, question: str, block: str | None) -> dict:
        raise NotImplementedError


class LiveBackend(Backend):                              # pragma: no cover - paid
    """The committed instrument. Imported lazily so a dry run never touches it."""

    def search(self, query: str) -> dict:
        from lab.stage0b_search import execute_search
        sr = execute_search(query)
        b = sr.block
        return {"requested_query": query, "realized_query": sr.realized_query,
                "query_faithful": sr.query_faithful, "executed": sr.executed,
                "web_search_requests": sr.search_requests,
                "raw": b.raw if b else None, "raw_sha": b.raw_sha if b else None,
                "injected": b.injected if b else None,
                "injected_sha": b.injected_sha if b else None,
                "summary_text": b.summary_text if b else None,
                "links": b.links if b else [],
                "served_models": sr.dispatch.models_used,
                "realized_tool_surface": sr.dispatch.init_tools,
                "session_id": sr.dispatch.session_id,
                "cost_usd": sr.dispatch.cost_usd, "failure": sr.failure}

    def write_query(self, question: str) -> dict:
        from lab.stage0b_harness import write_query
        q, row = write_query({"id": "_", "question": question})
        return {"query": q, "cost_usd": row.cost_usd, "served_models": row.served_models,
                "session_id": row.session_id, "failure": row.failure,
                "realized_tool_surface": row.realized_tool_surface}

    def answer(self, question: str, block: str | None) -> dict:
        from lab.stage0b_harness import run_answer_stage
        a, row = run_answer_stage({"id": "_", "question": question},
                                  "A" if block is None else "C", block)
        return {"answer": a, "cost_usd": row.cost_usd, "served_models": row.served_models,
                "session_id": row.session_id, "failure": row.failure,
                "realized_tool_surface": row.realized_tool_surface}


# --------------------------------------------------------------------------- #
# stages
# --------------------------------------------------------------------------- #

@dataclass
class RunReport:
    stage: str
    batch: int
    dispatched: int = 0
    skipped_already_done: int = 0
    failures: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_json(self) -> dict:
        return {"stage": self.stage, "batch": self.batch, "dispatched": self.dispatched,
                "skipped_already_done": self.skipped_already_done,
                "failures": self.failures, "notes": self.notes}


def stage_validate(rows: list[CalibrationRow]) -> list[str]:
    """Authoring validation. The runner NEVER invents or repairs an item."""
    problems = []
    for r in rows:
        problems += validate_row(r)
    problems += validate_bank(rows)
    return problems


def stage_screen(rows: list[CalibrationRow], ledger: DispatchLedger,
                 backend: Backend) -> RunReport:
    """One fixed-query execution per authored item. No answerer anywhere.

    The raw artifact is persisted BEFORE any flag is derived from it, so a crash
    between the search and the derivation loses nothing and cannot silently change
    a screen result.
    """
    rep = RunReport("screen", rows[0].batch if rows else 0)
    for row in rows:
        did = dispatch_id(row.item_id, "screen", "D_screen")
        if ledger.has(did):
            rep.skipped_already_done += 1
            continue
        if not row.fixed_query:
            rep.failures.append(f"{row.item_id}: no fixed query")
            continue
        res = backend.search(row.fixed_query)
        rec = {"dispatch_id": did, "item_id": row.item_id, "stage": "screen",
               "slot": "D_screen", "query": row.fixed_query, "result": res}
        ledger.append(rec)                       # durable BEFORE deriving anything
        rep.dispatched += 1
        if res.get("failure"):
            rep.failures.append(f"{row.item_id}: {res['failure']}")
    return rep


def derive_screen(row: CalibrationRow, ledger: DispatchLedger) -> CalibrationRow:
    """Mechanically fold a persisted screen dispatch into the row."""
    rec = ledger.get(dispatch_id(row.item_id, "screen", "D_screen"))
    if rec is None:
        return row
    res = rec["result"]
    scr = screen_summary(row.screen_spec_typed(), res.get("summary_text"))
    row.fixed_query = rec["query"]
    row.d_raw_artifact_sha = res.get("raw_sha")
    row.d_injected_block = res.get("injected")
    row.d_injected_block_sha = res.get("injected_sha")
    row.d_relevance = scr
    row.d_divergent = scr["divergent"]
    row.d_query_faithful = res.get("query_faithful")
    row.screen_passed = bool(scr["divergent"]) and not res.get("failure")
    row.served_models["screen"] = res.get("served_models")
    row.realized_tool_surface["screen"] = res.get("realized_tool_surface")
    row.web_search_requests["screen"] = res.get("web_search_requests")
    row.cost_usd["screen"] = res.get("cost_usd")
    row.session_ids["screen"] = res.get("session_id")
    if res.get("failure"):
        row.failure, row.failure_stage = res["failure"], "screen"
    return row


def stage_answer(rows: list[CalibrationRow], ledger: DispatchLedger,
                 backend: Backend) -> RunReport:
    """Stage 2 on screen passers only, six dispatches per item, in a fixed order.

    Every dispatch is persisted the moment it returns. A resume picks up at the
    exact slot it stopped at -- not at the start of the item, and not at the start
    of the batch.
    """
    rep = RunReport("answer", rows[0].batch if rows else 0)
    for row in rows:
        if not row.screen_passed:
            continue

        def run(slot: str, fn) -> dict | None:
            did = dispatch_id(row.item_id, "answer", slot)
            if ledger.has(did):
                rep.skipped_already_done += 1
                return ledger.get(did)["result"]
            res = fn()
            ledger.append({"dispatch_id": did, "item_id": row.item_id, "stage": "answer",
                           "slot": slot, "result": res})
            rep.dispatched += 1
            if res.get("failure"):
                rep.failures.append(f"{row.item_id}/{slot}: {res['failure']}")
            return res

        run("A_closed", lambda: backend.answer(row.stem, None))
        qres = run("C_query", lambda: backend.write_query(row.stem))
        mq = (qres or {}).get("query")
        if mq:
            run("C_search", lambda: backend.search(mq))
        run("D_production_search", lambda: backend.search(row.fixed_query))
        csr = ledger.get(dispatch_id(row.item_id, "answer", "C_search"))
        cblock = (csr or {}).get("result", {}).get("injected")
        dsr = ledger.get(dispatch_id(row.item_id, "answer", "D_production_search"))
        dblock = (dsr or {}).get("result", {}).get("injected")
        if cblock:
            run("C_answer", lambda: backend.answer(row.stem, cblock))
        if dblock:
            run("D_answer", lambda: backend.answer(row.stem, dblock))
    return rep


def derive_answers(row: CalibrationRow, ledger: DispatchLedger) -> CalibrationRow:
    g = lambda slot: (ledger.get(dispatch_id(row.item_id, "answer", slot)) or {}).get("result")  # noqa: E731
    spec = row.screen_spec_typed()
    a, q, cs, ds = g("A_closed"), g("C_query"), g("C_search"), g("D_production_search")
    ca, da = g("C_answer"), g("D_answer")
    if a:
        row.closed_answer = a.get("answer")
        row.cost_usd["A_closed"] = a.get("cost_usd")
        row.served_models["A_closed"] = a.get("served_models")
    if q:
        row.model_written_query = q.get("query")
        row.cost_usd["C_query"] = q.get("cost_usd")
    if cs:
        scr = screen_summary(spec, cs.get("summary_text"))
        row.c_raw_artifact_sha = cs.get("raw_sha")
        row.c_injected_block = cs.get("injected")
        row.c_injected_block_sha = cs.get("injected_sha")
        row.c_relevance = scr
        row.c_divergent = scr["divergent"]
        row.c_query_faithful = cs.get("query_faithful")
        row.cost_usd["C_search"] = cs.get("cost_usd")
        row.web_search_requests["C_search"] = cs.get("web_search_requests")
    if ds:
        scr = screen_summary(spec, ds.get("summary_text"))
        row.d_production_raw_artifact_sha = ds.get("raw_sha")
        row.d_production_injected_block = ds.get("injected")
        row.d_production_injected_block_sha = ds.get("injected_sha")
        row.d_production_relevance = scr
        row.d_production_divergent = scr["divergent"]
        row.d_production_query_faithful = ds.get("query_faithful")
        row.cost_usd["D_production_search"] = ds.get("cost_usd")
        row.web_search_requests["D_production_search"] = ds.get("web_search_requests")
        row.screen_block_differs_from_production_block = (
            row.d_injected_block_sha != row.d_production_injected_block_sha
            if row.d_injected_block_sha and row.d_production_injected_block_sha else None)
    if ca:
        row.c_exposed_answer = ca.get("answer")
        row.cost_usd["C_answer"] = ca.get("cost_usd")
    if da:
        row.d_exposed_answer = da.get("answer")
        row.cost_usd["D_answer"] = da.get("cost_usd")
    return row


# --------------------------------------------------------------------------- #
# reference adjudication and the human queue
# --------------------------------------------------------------------------- #

ARM_FIELD = {"A": "closed_answer", "C": "c_exposed_answer", "D": "d_exposed_answer"}
ROUTE_FIELD = {"A": "adjudication_route_closed", "C": "adjudication_route_c",
               "D": "adjudication_route_d"}
HAND_FIELD = {"A": "hand_verdict_closed", "C": "hand_verdict_c", "D": "hand_verdict_d"}


def stage_adjudicate(rows: list[CalibrationRow]) -> list[dict]:
    """Deterministic tier-1 reference adjudication over every A/C/D answer.

    Where the committed rules license a verdict it is recorded. Where they return
    ESCALATE the case goes to the human queue and NOTHING else touches it -- not
    this model's judgement, not another model's, and not the candidate grader.
    """
    cases: list[dict] = []
    for row in rows:
        key = row.key_for_route()
        row.escalated_to_human = []
        for arm in ("A", "C", "D"):
            ans = getattr(row, ARM_FIELD[arm])
            if ans is None:
                continue
            adj = reference_verdict(row.route, ans, key)
            setattr(row, ROUTE_FIELD[arm], adj.reason)
            if adj.disposition == DETERMINATE:
                setattr(row, HAND_FIELD[arm], adj.verdict)
                if not row.hand_adjudicator:
                    row.hand_adjudicator = "tier1:lab.stage0b_adjudication"
                row.hand_verdict_recorded_first = True
            else:
                row.escalated_to_human.append(arm)
                cases.append({"item_id": row.item_id, "arm": arm, "route": row.route,
                              "subset": row.subset, "stem": row.stem,
                              "answer": ans, "reason": adj.reason,
                              "answer_key": row.answer_key})
    return cases


FORBIDDEN_IN_QUEUE = ("grader_verdict", "grading_v2", "candidate_grader", "expected_verdict",
                      "suggested", "recommendation", "favours", "favors", "hypothesis",
                      "treatment_effect", "helps", "hurts")


def build_queue(cases: list[dict], batch: int) -> dict:
    """The frozen human-adjudication queue. What it must NOT contain is as
    load-bearing as what it must: any grader output, any hint at a verdict, any
    statement about which way a case cuts for the hypothesis."""
    out = []
    for i, c in enumerate(sorted(cases, key=lambda x: (x["item_id"], x["arm"])), start=1):
        key = c["answer_key"]
        out.append({
            "case_id": f"b{batch}-{i:04d}",
            "case_number": i, "total_cases": len(cases),
            "item_id": c["item_id"], "route": c["route"], "arm": c["arm"],
            "subset": c["subset"], "question": c["stem"],
            "accept": key.get("accept") or None,
            "rejects": key.get("rejects") or None,
            "expected": key.get("expected"),
            "value": key.get("value"), "tolerance": key.get("tolerance"),
            "reject_values": key.get("reject_values") or None,
            "model_answer": c["answer"],
            "escalation_reason": c["reason"],
            "human_verdict": None, "human_adjudicator": None,
        })
    doc = {"artifact": "stage0b_calibration_human_adjudication_queue", "batch": batch,
           "total_cases": len(out),
           "verdict_codes": {"C": "CORRECT", "I": "INCORRECT",
                             "A": "ABSTAIN / genuinely ambiguous"},
           "contains_no_grader_output": True,
           "instructions": ("Judge only whether the MODEL ANSWER correctly answers the "
                            "QUESTION under the supplied key. Do not guess what the grader "
                            "would do. Do not judge whether search helped or hurt."),
           "cases": out}
    body = json.dumps(doc, sort_keys=True)
    for token in FORBIDDEN_IN_QUEUE:
        if token in body.lower():
            raise ValueError(f"queue contains forbidden token {token!r}: a queue that "
                             f"leaks the grader or a suggested verdict is not blind")
    doc["queue_fingerprint"] = sha16(body)
    return doc


def import_verdicts(queue: dict, verdicts: dict, adjudicator: str) -> tuple[dict, list[str]]:
    """Validated import of Terry's C/I/A. Refuses anything it cannot attribute."""
    problems, applied = [], {}
    codes = {"C": "CORRECT", "I": "INCORRECT", "A": "ABSTAIN"}
    known = {c["case_id"] for c in queue["cases"]}
    for cid, code in verdicts.items():
        if cid not in known:
            problems.append(f"verdict for unknown case {cid!r}")
            continue
        c = str(code).strip().upper()
        if c not in codes:
            problems.append(f"case {cid}: verdict {code!r} is not one of C / I / A")
            continue
        applied[cid] = codes[c]
    missing = sorted(known - set(applied))
    if not adjudicator:
        problems.append("no adjudicator recorded: an unattributed human verdict is not "
                        "a measurement")
    if "grading_v2" in str(adjudicator):
        problems.append("the candidate grader may never produce its own ground truth")
    return {"applied": applied, "missing": missing, "adjudicator": adjudicator}, problems


def apply_verdicts(rows: list[CalibrationRow], queue: dict, imported: dict) -> list[str]:
    problems = []
    by_case = {c["case_id"]: c for c in queue["cases"]}
    by_item = {r.item_id: r for r in rows}
    for cid, verdict in imported["applied"].items():
        c = by_case[cid]
        row = by_item.get(c["item_id"])
        if row is None:
            problems.append(f"{cid}: no such item in bank")
            continue
        setattr(row, HAND_FIELD[c["arm"]], verdict)
        row.hand_adjudicator = imported["adjudicator"]
        row.hand_verdict_recorded_first = True
    return problems


# --------------------------------------------------------------------------- #
# THE LOCK
# --------------------------------------------------------------------------- #

def authorize_grading(rows: list[CalibrationRow], queue: dict | None) -> dict:
    """The only door to candidate grading. Refuses while a human case is open.

    This is a lock rather than a convention: a session that forgets the ordering
    cannot grade early, because there is no other entry point and this one counts
    the open cases itself.
    """
    reasons = []
    if queue is not None:
        by_item = {r.item_id: r for r in rows}
        for c in queue["cases"]:
            row = by_item.get(c["item_id"])
            if row is None:
                reasons.append(f"{c['case_id']}: item missing from bank")
                continue
            if getattr(row, HAND_FIELD[c["arm"]]) is None:
                reasons.append(f"{c['case_id']} ({c['item_id']}/{c['arm']}) has no human "
                               f"verdict")
    for row in rows:
        if not row.screen_passed:
            continue
        for arm in ("A", "C", "D"):
            if getattr(row, ARM_FIELD[arm]) is not None and \
                    getattr(row, HAND_FIELD[arm]) is None:
                reasons.append(f"{row.item_id}/{arm}: answered but not adjudicated")
        if any(getattr(row, HAND_FIELD[a]) is not None for a in ("A", "C", "D")):
            if not row.hand_adjudicator:
                reasons.append(f"{row.item_id}: adjudicated with no attributed adjudicator")
            if not row.hand_verdict_recorded_first:
                reasons.append(f"{row.item_id}: hand_verdict_recorded_first not set")
    return {
        "authorized": not reasons,
        "open_cases": len(reasons),
        "reasons": reasons[:40],
        "rule": "candidate grading is authorized only when every answered arm carries an "
                "attributed reference verdict recorded BEFORE grading. A defect rate "
                "measured against a ground truth the grader helped produce is not a "
                "measurement.",
    }


# --------------------------------------------------------------------------- #
# persistence and CLI
# --------------------------------------------------------------------------- #

def load_bank(path: pathlib.Path) -> list[CalibrationRow]:
    data = json.loads(path.read_text())
    return [CalibrationRow(**r) for r in data["items"]]


def save_rows(rows: list[CalibrationRow], path: pathlib.Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps({"rows": [r.to_json() for r in rows]}, indent=1, sort_keys=True)
    path.write_text(body + "\n")
    return sha16(body)


def status(batch: int, bank: pathlib.Path | None) -> dict:
    led = RUNDIR / LEDGER.format(b=batch)
    ledger = DispatchLedger(led)
    out = {"batch": batch, "ledger": str(led), "dispatches_recorded": len(ledger),
           "by_stage": {s: len(ledger.by_stage(s)) for s in ("screen", "answer")}}
    if bank and bank.exists():
        rows = load_bank(bank)
        rows = [derive_answers(derive_screen(r, ledger), ledger) for r in rows]
        out["items"] = len(rows)
        out["screen_passed"] = sum(1 for r in rows if r.screen_passed)
        q = RUNDIR / QUEUE.format(b=batch)
        queue = json.loads(q.read_text()) if q.exists() else None
        out["queue"] = {"exists": queue is not None,
                        "cases": queue["total_cases"] if queue else 0,
                        "fingerprint": queue.get("queue_fingerprint") if queue else None}
        out["grading_authorization"] = authorize_grading(rows, queue)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Stage 0B calibration runner")
    ap.add_argument("--stage", required=True, choices=STAGES)
    ap.add_argument("--batch", type=int, default=1)
    ap.add_argument("--bank", type=pathlib.Path, default=None)
    ap.add_argument("--verdicts", type=pathlib.Path, default=None)
    ap.add_argument("--adjudicator", default="")
    ap.add_argument("--dry-run", action="store_true",
                    help="use the synthetic backend; makes no paid call")
    a = ap.parse_args(argv)

    if a.stage == "status":
        print(json.dumps(status(a.batch, a.bank), indent=1))
        return 0
    if a.bank is None:
        print("--bank is required for every stage except status", file=sys.stderr)
        return 2

    rows = load_bank(a.bank)
    problems = stage_validate(rows)
    if problems:
        print(json.dumps({"stage": "validate", "problems": problems[:60]}, indent=1))
        if a.stage != "validate":
            print("REFUSING to dispatch against an invalid bank", file=sys.stderr)
            return 1
        return 1
    if a.stage == "validate":
        print(json.dumps({"stage": "validate", "items": len(rows), "problems": []}, indent=1))
        return 0

    if a.dry_run:
        from tests.fixtures.stage0b_synthetic import SyntheticBackend
        backend: Backend = SyntheticBackend()
    else:                                                 # pragma: no cover - paid
        backend = LiveBackend()

    ledger = DispatchLedger(RUNDIR / LEDGER.format(b=a.batch))
    if a.stage == "screen":
        rep = stage_screen(rows, ledger, backend)
    elif a.stage == "answer":
        rows = [derive_screen(r, ledger) for r in rows]
        rep = stage_answer(rows, ledger, backend)
    elif a.stage in ("adjudicate", "export-queue"):
        rows = [derive_answers(derive_screen(r, ledger), ledger) for r in rows]
        cases = stage_adjudicate(rows)
        queue = build_queue(cases, a.batch)
        qp = RUNDIR / QUEUE.format(b=a.batch)
        qp.parent.mkdir(parents=True, exist_ok=True)
        qp.write_text(json.dumps(queue, indent=1, sort_keys=True) + "\n")
        rep = RunReport(a.stage, a.batch)
        rep.notes = [f"escalations {len(cases)}", f"queue {qp}",
                     f"fingerprint {queue['queue_fingerprint']}"]
    elif a.stage == "import-verdicts":
        rows = [derive_answers(derive_screen(r, ledger), ledger) for r in rows]
        stage_adjudicate(rows)
        queue = json.loads((RUNDIR / QUEUE.format(b=a.batch)).read_text())
        verdicts = json.loads(a.verdicts.read_text())
        imported, problems = import_verdicts(queue, verdicts, a.adjudicator)
        problems += apply_verdicts(rows, queue, imported)
        rep = RunReport(a.stage, a.batch)
        rep.failures = problems
        rep.notes = [f"applied {len(imported['applied'])}",
                     f"still missing {len(imported['missing'])}"]
    else:                                                  # pragma: no cover
        raise AssertionError(a.stage)

    rows_sha = save_rows(rows, RUNDIR / ROWS.format(b=a.batch))
    rep.notes.append(f"rows fingerprint {rows_sha}")
    print(json.dumps(rep.to_json(), indent=1))
    return 1 if rep.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
