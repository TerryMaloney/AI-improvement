"""Loading raw solver answers into the store, with an audit pass.

The audit is not paranoia about the model — it is the packet's own rule
applied to the lab's own instrument. A solver self-reports how many searches
it ran, and self-reports are the cheapest thing in the world to get wrong. So
every ingested answer is checked for the things that would silently corrupt a
result:

  * a closed-condition answer claiming it ran searches (the sandbox should make
    this impossible; if it appears, the sandbox is broken, not the model)
  * a search-condition answer over its stated budget
  * an answer containing a verbatim string from the answer key, which would
    mean ground truth reached a solver somehow

Flags are recorded, not silently dropped, and the report surfaces them. A run
with audit flags is a run whose numbers are suspect.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from lab.battery import leak_probe_strings, load_answers
from lab.store import Store

_BUDGET_RE = re.compile(r"SEARCH BUDGET: (\d+) search", re.I)

# The probe set is already restricted to long distinctive ground-truth prose
# (see lab.battery.leak_probe_strings for why matching accept-strings flagged
# every correct answer as a cheat). This is a second floor on top of that.
_MIN_LEAK_LEN = 40


def _parse_answer_file(path: Path) -> tuple[dict | None, str | None]:
    text = path.read_text().strip()
    try:
        return json.loads(text), None
    except json.JSONDecodeError:
        pass
    # Tolerate a fenced block or surrounding prose — solvers are told to return
    # bare JSON, but a run should not be lost to a stray markdown fence.
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if fence:
        try:
            return json.loads(fence.group(1)), "recovered from markdown fence"
        except json.JSONDecodeError:
            pass
    brace = re.search(r"\{.*\}", text, re.S)
    if brace:
        try:
            return json.loads(brace.group(0)), "recovered by brace extraction"
        except json.JSONDecodeError:
            pass
    return None, "could not parse any JSON object"


def audit(payload: dict, trial_row, leak_strings: list[str]) -> list[str]:
    flags: list[str] = []
    searches = payload.get("searches_used")
    prompt = trial_row["prompt"] or ""
    closed = "TOOLS: you have none" in prompt

    if closed and isinstance(searches, int) and searches > 0:
        flags.append(
            f"SANDBOX: closed-condition trial reports {searches} searches — the agent should "
            f"have had no search tool. Check the agent definition before trusting this run."
        )
    if not closed:
        m = _BUDGET_RE.search(prompt)
        if m and isinstance(searches, int) and searches > int(m.group(1)):
            flags.append(f"BUDGET: used {searches} searches against a stated budget of {m.group(1)}")

    answer = " ".join((payload.get("answer") or "").split()).lower()
    for s in leak_strings:
        if len(s) >= _MIN_LEAK_LEN and s.lower() in answer:
            flags.append(f"LEAK-SUSPECT: answer contains an answer-key string verbatim: {s[:60]!r}")
            break
    if not (payload.get("answer") or "").strip():
        flags.append("EMPTY: no answer text in payload")
    return flags


def ingest(run_dir: Path) -> dict:
    store = Store(run_dir / "results.db")
    leak_strings = leak_probe_strings(load_answers())
    answers_dir = run_dir / "answers"
    answers_dir.mkdir(parents=True, exist_ok=True)

    loaded, unparseable, flagged, unknown = 0, [], {}, []
    for path in sorted(answers_dir.glob("*.json")):
        trial_id = path.stem
        row = store.trial(trial_id)
        if row is None:
            unknown.append(trial_id)
            continue
        payload, note = _parse_answer_file(path)
        if payload is None:
            unparseable.append(f"{trial_id}: {note}")
            continue
        if note:
            payload.setdefault("_ingest_note", note)
        flags = audit(payload, row, leak_strings)
        if flags:
            payload["_audit_flags"] = flags
            flagged[trial_id] = flags
        store.save_answer(trial_id, payload, payload.get("duration_s"))
        loaded += 1

    total = len(store.trials())
    store.close()
    return {
        "loaded": loaded,
        "expected": total,
        "missing": total - loaded,
        "unparseable": unparseable,
        "unknown_trial_ids": unknown,
        "audit_flags": flagged,
    }
