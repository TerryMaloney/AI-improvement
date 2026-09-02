"""Stage 0A-M production runner — dispatch, persist, never grade.

Dispatch path (frozen 2026-09-02 after the TodoWrite blocker):

    printf '<packet>' | claude -p --agent <agent> --model opus \
        --output-format json --allowedTools WebSearch WebFetch

Both arms use the IDENTICAL command line. The only difference between arms is
which agent definition is named, and therefore which tools that agent is allowed
to have. Measured realized surfaces: closed = [], retrieval = [WebSearch,
WebFetch]. The `--allowedTools` grant is passed to both arms precisely so that it
cannot be an arm difference; the closed agent's own allowlist is empty, so the
grant is inert for it (verified at runtime).

This module dispatches and persists. It does not grade and does not aggregate.
Raw responses are written to disk before anything reads them.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import time

REPO = pathlib.Path(__file__).resolve().parent.parent
RUN = REPO / "runs" / "exp004_stage0am"
AGENTS = {"closed": "stage0am-solver-closed", "retrieval_enabled": "stage0am-solver-web"}
TEMPLATES = {
    "closed": REPO / "experiments" / "exp004_stage0am" / "packet_closed.template.md",
    "retrieval_enabled": REPO / "experiments" / "exp004_stage0am" / "packet_retrieval_enabled.template.md",
}
CMD_MODEL = "opus"


def build_packet(arm: str, question: str) -> str:
    t = TEMPLATES[arm].read_text()
    assert t.count("{QUESTION}") == 1, "packet template must carry exactly one {QUESTION}"
    return t.replace("{QUESTION}", question)


def dispatch(arm: str, packet: str, timeout: int = 600) -> dict:
    """One trial. Fresh process, fresh context. Returns the harness JSON plus wall time."""
    cmd = ["claude", "-p", "--agent", AGENTS[arm], "--model", CMD_MODEL,
           "--output-format", "json", "--allowedTools", "WebSearch", "WebFetch"]
    t0 = time.time()
    proc = subprocess.run(cmd, input=packet, capture_output=True, text=True, timeout=timeout)
    wall = time.time() - t0
    out = {"_wall_s": round(wall, 2), "_returncode": proc.returncode, "_cmd": cmd}
    try:
        out.update(json.loads(proc.stdout))
    except Exception as exc:                      # dispatch-level failure, case B candidate
        out["_parse_error"] = str(exc)
        out["_stdout"] = proc.stdout[:4000]
        out["_stderr"] = proc.stderr[:4000]
    return out


def extract_answer(raw: dict) -> tuple[str | None, str | None]:
    """Return (answer_text, dispatch_failure). answer_text is None iff case B.

    The solver is asked for a JSON object; we take its `answer` field. A response
    that is not parseable JSON but is non-empty text is still a final answer and
    is passed through verbatim -- the grader, not this function, decides whether
    it is correct. Only the absence of any final answer is a dispatch failure.
    """
    if raw.get("_returncode") != 0:
        return None, "DISPATCH_ERROR"
    if raw.get("is_error"):
        return None, "DISPATCH_ERROR"
    result = raw.get("result")
    if result is None:
        return None, "EMPTY_RESPONSE"
    text = result.strip()
    if not text:
        return None, "EMPTY_RESPONSE"
    try:
        obj = json.loads(text)
        if isinstance(obj, dict) and "answer" in obj:
            return str(obj["answer"]), None
    except Exception:
        pass
    return text, None            # unparsed but non-empty: still a final answer


def telemetry(raw: dict) -> dict:
    u = raw.get("usage") or {}
    return {
        "models_used": sorted((raw.get("modelUsage") or {}).keys()),
        "num_turns": raw.get("num_turns"),
        "stop_reason": raw.get("stop_reason"),
        "permission_denials": raw.get("permission_denials"),
        "duration_ms": raw.get("duration_ms"),
        "duration_api_ms": raw.get("duration_api_ms"),
        "wall_s": raw.get("_wall_s"),
        "cost_usd": raw.get("total_cost_usd"),
        "input_tokens": u.get("input_tokens"),
        "output_tokens": u.get("output_tokens"),
        "thinking_tokens": (u.get("output_tokens_details") or {}).get("thinking_tokens"),
        "cache_read_input_tokens": u.get("cache_read_input_tokens"),
        "server_tool_use": u.get("server_tool_use"),
    }
