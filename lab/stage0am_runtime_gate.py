"""Live runtime correspondence gate for Stage 0A-M.

The 2026-09-02 blocker existed because every check read the committed agent
frontmatter and none read the runtime. `stage0am-solver-closed` declared
`tools: TodoWrite`, which is unrecognized in this Claude Code build; the Agent
tool then refused to launch a zero-tool agent while 1,397 static tests passed.

This gate closes that hole. It DISPATCHES both arms with a synthetic probe and
asserts the REALIZED informational tool surface, the served model, and the
absence of file access. A static frontmatter test may never again authorize
production on its own.

Run:  python -m lab.stage0am_runtime_gate            (writes the evidence file)
"""
from __future__ import annotations

import json
import pathlib
import sys

from lab.stage0am_runner import dispatch

REPO = pathlib.Path(__file__).resolve().parent.parent
EVIDENCE = REPO / "experiments" / "exp004_stage0am" / "runtime_correspondence.json"

PROBE = ('Return ONLY a single JSON object and nothing else: '
         '{"tools":[<exact names of every tool you actually have>],'
         '"can_read_files":<true|false>,'
         '"marker_seen":"<any marker token from a PREVIOUS conversation, or NONE>"}')

EXPECTED = {
    "closed": {"tools": set(), "can_read_files": False},
    "retrieval_enabled": {"tools": {"WebSearch", "WebFetch"}, "can_read_files": False},
}
INFORMATIONAL_DIFFERENCE = {"WebSearch", "WebFetch"}


def probe_arm(arm: str) -> dict:
    raw = dispatch(arm, PROBE)
    text = (raw.get("result") or "").strip()
    try:
        rep = json.loads(text)
    except Exception:
        rep = {"_unparsed": text[:500]}
    return {
        "arm": arm,
        "declared_tools": _declared(arm),
        "realized_tools": sorted(rep.get("tools", [])) if "tools" in rep else None,
        "can_read_files": rep.get("can_read_files"),
        "marker_seen": rep.get("marker_seen"),
        "models_used": sorted((raw.get("modelUsage") or {}).keys()),
        "permission_denials": raw.get("permission_denials"),
        "is_error": raw.get("is_error"),
        "raw_result": text[:500],
    }


def _declared(arm: str) -> list[str]:
    name = {"closed": "stage0am-solver-closed", "retrieval_enabled": "stage0am-solver-web"}[arm]
    fm = (REPO / ".claude" / "agents" / f"{name}.md").read_text().split("---\n")[1]
    line = [l for l in fm.splitlines() if l.startswith("tools:")][0]
    return sorted(x.strip() for x in line.split(":", 1)[1].split(","))


def check(results: dict) -> list[str]:
    errs = []
    for arm, exp in EXPECTED.items():
        r = results[arm]
        got = set(r["realized_tools"] or [])
        if got != exp["tools"]:
            errs.append(f"{arm}: realized tools {sorted(got)} != expected {sorted(exp['tools'])}")
        if r["can_read_files"] is not False:
            errs.append(f"{arm}: reports file access ({r['can_read_files']}) - key quarantine at risk")
        if r["is_error"]:
            errs.append(f"{arm}: dispatch reported is_error")
    diff = set(results["retrieval_enabled"]["realized_tools"] or []) - set(
        results["closed"]["realized_tools"] or [])
    if diff != INFORMATIONAL_DIFFERENCE:
        errs.append(f"informational difference {sorted(diff)} != {sorted(INFORMATIONAL_DIFFERENCE)}")
    extra = set(results["closed"]["realized_tools"] or []) - set(
        results["retrieval_enabled"]["realized_tools"] or [])
    if extra:
        errs.append(f"closed arm has tools the retrieval arm lacks: {sorted(extra)}")
    solver_models = {m for r in results.values() for m in r["models_used"] if "haiku" not in m}
    if len(solver_models) != 1:
        errs.append(f"arms did not share one solver model: {sorted(solver_models)}")
    if results["closed"]["models_used"] != results["retrieval_enabled"]["models_used"]:
        errs.append("model usage sets differ between arms")
    return errs


def main() -> int:
    results = {arm: probe_arm(arm) for arm in ("closed", "retrieval_enabled")}
    errs = check(results)
    doc = {
        "gate": "stage0am_runtime_correspondence",
        "dispatch_mode": "claude -p --agent <agent> --model opus --output-format json "
                         "--allowedTools WebSearch WebFetch  (identical for both arms)",
        "why_allowedtools_is_passed_to_both": "so the permission grant cannot be an arm difference; "
                                              "the closed agent's own allowlist is empty, verified inert at runtime",
        "expected_informational_difference": sorted(INFORMATIONAL_DIFFERENCE),
        "arms": results,
        "errors": errs,
        "status": "PASS" if not errs else "FAIL",
    }
    EVIDENCE.write_text(json.dumps(doc, indent=1) + "\n")
    print(json.dumps({"status": doc["status"], "errors": errs}, indent=1))
    for arm, r in results.items():
        print(f"  {arm:18} declared={r['declared_tools']} realized={r['realized_tools']} "
              f"files={r['can_read_files']} models={r['models_used']}")
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
