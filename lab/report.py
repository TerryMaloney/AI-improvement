"""Markdown reports: the experimental record, and the thing you actually read.

Two audiences and both matter. The aggregate grid answers "did the treatment
work"; the per-question table answers "where, and did it work for the reason we
thought". A win that comes entirely from one question category is a different
finding from a broad one, and only the second table tells you which you have.

Reports always state their own denominators, including how many trials were
ungraded and why. An accuracy figure computed over a silently-shrunk sample is
the exact failure this project is about.
"""

from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path

from lab.battery import load_batteries
from lab.grading import FAIL, NEEDS_JUDGE, NO_ANSWER, PARTIAL, PASS, UNGRADED
from lab.store import Store

SCORED = {PASS, PARTIAL, FAIL}


def _fmt_pct(num: float | None) -> str:
    return "—" if num is None else f"{num * 100:.0f}%"


def _mean(xs: list[float]) -> float | None:
    return statistics.mean(xs) if xs else None


def _cell(rows: list[dict]) -> dict:
    scored = [r for r in rows if r["verdict"] in SCORED]
    scores = [r["score"] for r in scored if r["score"] is not None]
    searches = [r["searches"] for r in rows if isinstance(r["searches"], (int, float))]
    return {
        "n": len(rows),
        "scored": len(scored),
        "accuracy": _mean(scores),
        "passes": sum(1 for r in scored if r["verdict"] == PASS),
        "fails": sum(1 for r in scored if r["verdict"] == FAIL),
        "partials": sum(1 for r in scored if r["verdict"] == PARTIAL),
        "ungraded": sum(1 for r in rows if r["verdict"] == UNGRADED),
        "no_answer": sum(1 for r in rows if r["verdict"] == NO_ANSWER),
        "pending_judge": sum(1 for r in rows if r["verdict"] == NEEDS_JUDGE),
        "mean_searches": _mean([float(s) for s in searches]),
        "total_searches": sum(searches) if searches else 0,
        "hedge_rate": _mean([1.0 if r["hedged"] else 0.0 for r in rows if r["hedged"] is not None]),
        "abstain_rate": _mean([1.0 if r["abstained"] else 0.0 for r in rows]),
        "mean_chars": _mean([float(r["chars"]) for r in rows if r["chars"]]),
    }


def collect(run_dir: Path) -> dict:
    store = Store(run_dir / "results.db")
    config = store.config()
    rows = []
    for r in store.joined():
        detail = json.loads(r["detail_json"]) if r["detail_json"] else {}
        conduct = detail.get("conduct", {})
        rows.append(
            {
                "trial_id": r["trial_id"],
                "question_id": r["question_id"],
                "battery": r["battery_id"],
                "condition": r["condition"],
                "model": r["model"],
                "repeat": r["repeat"],
                "routed_claim_type": r["routed_claim_type"],
                "verdict": r["verdict"] or NO_ANSWER,
                "score": r["score"],
                "grade_method": r["grade_method"],
                "answer": r["answer_text"] or "",
                "searches": r["searches_used"] if r["searches_used"] is not None else conduct.get("searches_used"),
                "hedged": conduct.get("hedged"),
                "flagged_premise": conduct.get("flagged_premise"),
                "abstained": bool(r["abstained"]),
                "chars": conduct.get("answer_chars") or len(r["answer_text"] or ""),
                "detail": detail,
                "audit_flags": None,
            }
        )
    # audit flags live in the answers raw_json
    for row in rows:
        raw = store.conn.execute(
            "SELECT raw_json FROM answers WHERE trial_id=?", (row["trial_id"],)
        ).fetchone()
        if raw and raw["raw_json"]:
            row["audit_flags"] = json.loads(raw["raw_json"]).get("_audit_flags")
    store.close()
    return {"config": config, "rows": rows}


def render(run_dir: Path) -> str:
    data = collect(run_dir)
    config, rows = data["config"], data["rows"]
    exp_id = config.get("id", run_dir.name)

    conditions = list(dict.fromkeys(r["condition"] for r in rows))
    models = list(dict.fromkeys(r["model"] for r in rows))

    by_cm: dict[tuple[str, str], list[dict]] = defaultdict(list)
    by_c: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_cm[(r["condition"], r["model"])].append(r)
        by_c[r["condition"]].append(r)

    out: list[str] = []
    A = out.append

    A(f"# {config.get('title', exp_id)}")
    A("")
    A(f"**Experiment:** `{exp_id}`  ")
    A(f"**Hypothesis under test:** {config.get('hypothesis', '—')}  ")
    A(f"**Batteries:** {', '.join(config.get('batteries', []))}  ")
    A(f"**Trials:** {len(rows)} ({len(conditions)} conditions × {len(models)} models)")
    A("")
    if config.get("notes"):
        A("> " + config["notes"].replace("\n", "\n> "))
        A("")

    # ------------------------------------------------------------ integrity
    flagged = [r for r in rows if r.get("audit_flags")]
    unanswered = [r for r in rows if r["verdict"] == NO_ANSWER]
    pending = [r for r in rows if r["verdict"] == NEEDS_JUDGE]
    ungraded = [r for r in rows if r["verdict"] == UNGRADED]

    A("## Result integrity")
    A("")
    A("Read this before the numbers. Every figure below is computed over "
      "*scored* trials only, and these are the trials that aren't in it.")
    A("")
    A(f"- **Unanswered trials:** {len(unanswered)}")
    A(f"- **Awaiting judge:** {len(pending)}")
    A(f"- **Ungraded (unverified ground truth):** {len(ungraded)}")
    A(f"- **Audit flags:** {len(flagged)}")
    if ungraded:
        qs = sorted({r["question_id"] for r in ungraded})
        A(f"  - questions with unverified ground truth: {', '.join(qs)} — "
          f"run `python -m lab refresh` and re-grade before treating this experiment as complete.")
    for r in flagged:
        for f in r["audit_flags"]:
            A(f"  - `{r['trial_id']}`: {f}")
    A("")

    # ------------------------------------------------------------- headline
    A("## Headline: condition × model")
    A("")
    A("| Condition | Model | Accuracy | Scored/n | Pass | Partial | Fail | Searches (total) | Hedge rate | Abstain rate |")
    A("|---|---|---|---|---|---|---|---|---|---|")
    for c in conditions:
        for m in models:
            cell = _cell(by_cm[(c, m)])
            if not cell["n"]:
                continue
            A(
                f"| {c} | {m} | **{_fmt_pct(cell['accuracy'])}** | {cell['scored']}/{cell['n']} | "
                f"{cell['passes']} | {cell['partials']} | {cell['fails']} | {cell['total_searches']} | "
                f"{_fmt_pct(cell['hedge_rate'])} | {_fmt_pct(cell['abstain_rate'])} |"
            )
    A("")

    A("### Pooled across models")
    A("")
    A("| Condition | Accuracy | Scored/n | Searches (total) | Mean answer chars | Hedge rate |")
    A("|---|---|---|---|---|---|")
    for c in conditions:
        cell = _cell(by_c[c])
        A(
            f"| {c} | **{_fmt_pct(cell['accuracy'])}** | {cell['scored']}/{cell['n']} | "
            f"{cell['total_searches']} | {cell['mean_chars']:.0f} | {_fmt_pct(cell['hedge_rate'])} |"
            if cell["mean_chars"]
            else f"| {c} | **{_fmt_pct(cell['accuracy'])}** | {cell['scored']}/{cell['n']} | "
                 f"{cell['total_searches']} | — | {_fmt_pct(cell['hedge_rate'])} |"
        )
    A("")

    # -------------------------------------------------------- cost per point
    A("### Cost of a correct answer")
    A("")
    A("Searches per additional correct answer, versus the cheapest condition. "
      "This is the number that decides whether a procedure is worth running — "
      "an accuracy gain bought with unbounded retrieval is not a win.")
    A("")
    base_c = min(conditions, key=lambda c: _cell(by_c[c])["total_searches"])
    base = _cell(by_c[base_c])
    A(f"Reference condition (fewest searches): **{base_c}**")
    A("")
    A("| Condition | Δ accuracy vs reference | Extra searches | Searches per extra correct answer |")
    A("|---|---|---|---|")
    for c in conditions:
        cell = _cell(by_c[c])
        if cell["accuracy"] is None or base["accuracy"] is None:
            continue
        d_acc = cell["accuracy"] - base["accuracy"]
        d_search = cell["total_searches"] - base["total_searches"]
        extra_correct = d_acc * cell["scored"]
        ratio = f"{d_search / extra_correct:.1f}" if extra_correct > 0.01 else ("—" if d_search == 0 else "∞ (no accuracy gain)")
        A(f"| {c} | {d_acc * 100:+.0f} pts | {d_search:+d} | {ratio} |")
    A("")

    # ---------------------------------------------------------- by category
    batteries = config.get("batteries", [])
    cats: dict[str, str] = {}
    traps: set[str] = set()
    try:
        for b in load_batteries(batteries):
            for q in b.questions:
                cats[q.id] = q.category
                if q.trap:
                    traps.add(q.id)
    except Exception:
        pass

    if cats:
        A("## By question category")
        A("")
        A("Where the effect actually lives. A gain concentrated in one category "
          "is a narrower finding than the headline number suggests.")
        A("")
        by_cat: dict[tuple[str, str], list[dict]] = defaultdict(list)
        for r in rows:
            by_cat[(cats.get(r["question_id"], "?"), r["condition"])].append(r)
        cat_names = sorted({c for c, _ in by_cat})
        A("| Category | " + " | ".join(conditions) + " |")
        A("|---" * (len(conditions) + 1) + "|")
        for cat in cat_names:
            cells = [_cell(by_cat[(cat, c)]) for c in conditions]
            A(f"| {cat} | " + " | ".join(
                f"{_fmt_pct(x['accuracy'])} ({x['scored']}/{x['n']})" for x in cells
            ) + " |")
        A("")

        if traps:
            A("### Trap questions specifically")
            A("")
            A("False-premise and stale-entity traps — the questions where a "
              "confident wrong answer is the failure being measured.")
            A("")
            A("| Condition | Trap accuracy | Premise flagged |")
            A("|---|---|---|")
            for c in conditions:
                trap_rows = [r for r in rows if r["question_id"] in traps and r["condition"] == c]
                cell = _cell(trap_rows)
                flagged_rate = _mean([1.0 if r["flagged_premise"] else 0.0 for r in trap_rows])
                A(f"| {c} | {_fmt_pct(cell['accuracy'])} ({cell['scored']}/{cell['n']}) | {_fmt_pct(flagged_rate)} |")
            A("")

    # -------------------------------------------------------- per question
    A("## Per question")
    A("")
    A("| Question | Routed as | " + " | ".join(f"{c}" for c in conditions) + " |")
    A("|---" * (len(conditions) + 2) + "|")
    qids = list(dict.fromkeys(r["question_id"] for r in rows))
    marks = {PASS: "✅", FAIL: "❌", PARTIAL: "🟡", UNGRADED: "⚪", NEEDS_JUDGE: "⏳", NO_ANSWER: "·"}
    for qid in qids:
        qrows = [r for r in rows if r["question_id"] == qid]
        routed = qrows[0]["routed_claim_type"] if qrows else "?"
        cells = []
        for c in conditions:
            vs = [marks.get(r["verdict"], "?") for r in qrows if r["condition"] == c]
            cells.append("".join(vs) if vs else "—")
        trap_mark = " 🪤" if qid in traps else ""
        A(f"| `{qid}`{trap_mark} | {routed} | " + " | ".join(cells) + " |")
    A("")
    A("✅ pass · 🟡 partial · ❌ fail · ⚪ ungraded (unverified ground truth) · "
      "⏳ awaiting judge · · no answer · 🪤 trap question")
    A("")

    # -------------------------------------------------- disagreement detail
    A("## Where the conditions disagreed")
    A("")
    A("The rows worth reading by hand. A condition winning on a question is only "
      "evidence if you can see *why* it won.")
    A("")
    any_diff = False
    for qid in qids:
        per_cond = {}
        for c in conditions:
            vs = [r["verdict"] for r in rows if r["question_id"] == qid and r["condition"] == c]
            per_cond[c] = vs
        distinct = {tuple(v) for v in per_cond.values()}
        if len(distinct) <= 1:
            continue
        any_diff = True
        A(f"### `{qid}`")
        A("")
        for c in conditions:
            crows = [r for r in rows if r["question_id"] == qid and r["condition"] == c]
            for r in crows:
                snippet = " ".join(r["answer"].split())[:280]
                A(f"- **{c}** / {r['model']} → **{r['verdict']}** "
                  f"({r['searches'] if r['searches'] is not None else '?'} searches)")
                if snippet:
                    A(f"  > {snippet}{'…' if len(r['answer']) > 280 else ''}")
        A("")
    if not any_diff:
        A("_No question produced different verdicts across conditions._")
        A("")

    return "\n".join(out)


def write_report(run_dir: Path) -> Path:
    path = run_dir / "report.md"
    path.write_text(render(run_dir))
    return path


def compare(run_dirs: list[Path]) -> str:
    """Cross-experiment comparison — the 'has our thinking moved' view."""
    out: list[str] = []
    A = out.append
    A("# Cross-experiment comparison")
    A("")
    A("| Experiment | Hypothesis | Condition | Model | Accuracy | Scored/n | Searches |")
    A("|---|---|---|---|---|---|---|")
    for rd in run_dirs:
        data = collect(rd)
        cfg, rows = data["config"], data["rows"]
        by_cm: dict[tuple[str, str], list[dict]] = defaultdict(list)
        for r in rows:
            by_cm[(r["condition"], r["model"])].append(r)
        for (c, m), rs in sorted(by_cm.items()):
            cell = _cell(rs)
            A(f"| `{cfg.get('id', rd.name)}` | {cfg.get('hypothesis', '—')} | {c} | {m} | "
              f"**{_fmt_pct(cell['accuracy'])}** | {cell['scored']}/{cell['n']} | {cell['total_searches']} |")
    A("")
    A("Comparing across experiments is only valid where the batteries and "
      "grading match. Check the battery ids before reading a difference as an effect.")
    return "\n".join(out)
