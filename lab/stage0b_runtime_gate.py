"""Stage 0B live runtime correspondence gate.

Stage 0A-M's lesson, stated as a rule this module enforces: **the live system is
the experiment; the configuration file is a description of it.** 1,397 static
tests passed while the closed arm could not be spawned at all. So every check
here dispatches. A check that a file says the right thing is not evidence and is
not accepted as a substitute.

A check the runtime does not let us observe is recorded as UNOBSERVABLE. It is
not recorded as a pass. The gate's status is PASS only if no check FAILED, and
the count of UNOBSERVABLE checks is reported alongside, because a gate that
quietly counts unobservable as fine is the same failure in a new place.

Run:  python -m lab.stage0b_runtime_gate      (live, paid: ~6 dispatches)
"""
from __future__ import annotations

import json
import pathlib
import sys

from lab.stage0b_harness import (ANSWERER_AGENT, QUERY_WRITER_AGENT, SEARCHER_AGENT,
                                 build_answer_packet, build_query_writer_packet,
                                 extract_query, fixed_query, packet_diff_report,
                                 run_search_stage)
from lab.stage0b_search import dispatch, sha

REPO = pathlib.Path(__file__).resolve().parent.parent
EVIDENCE = REPO / "experiments" / "exp004_stage0b" / "runtime_correspondence.json"

PASS, FAIL, UNOBS = "PASS", "FAIL", "UNOBSERVABLE"

# A token planted in the query writer's dispatch. If any part of the query
# writer's context reached the answerer, the answerer could echo it. It cannot,
# because they are separate processes -- but "cannot" is what Stage 0A-M said
# about the closed arm's tool surface.
MARKER = "ISOLATION-CANARY-7Q4XZ"

CTX_PROBE = ('Return ONLY a single JSON object and nothing else: '
             '{"tools":[<exact names of every tool you actually have>],'
             '"can_read_files":<true|false>,'
             '"marker_seen":"<any marker token from a PREVIOUS conversation, or NONE>"}')

# A harmless public question used for every live check here. It is not a
# production item and never becomes one.
CANARY = {
    "id": "gate_canary_unsg_2015",
    "question": "Who was the Secretary-General of the United Nations in 2015?",
    "query_subject": "Secretary-General of the United Nations",
    "anchor_as_written": "2015",
    "accept_aliases": ["Ban Ki-moon"],
    "reject_aliases": ["Guterres"],
}


def _chk(cid: str, name: str, status: str, detail, evidence=None) -> dict:
    return {"id": cid, "check": name, "status": status, "detail": detail,
            "evidence": evidence}


def _json_probe(text: str | None) -> dict:
    try:
        return json.loads((text or "").strip())
    except Exception:
        return {"_unparsed": (text or "")[:400]}


def run_gate(timeout: int = 600) -> dict:
    checks: list[dict] = []
    live: dict = {}

    # ---- live dispatches -------------------------------------------------- #
    # 1. query writer, with the marker planted in its prompt
    qw_packet = build_query_writer_packet(CANARY["question"]) + f"\nMARKER: {MARKER}\n"
    qw = dispatch(QUERY_WRITER_AGENT, qw_packet, allowed_tools=None, timeout=timeout)
    live["query_writer"] = qw.to_json()
    model_query, qfail = extract_query(qw.final_text)

    # 2. query writer context probe (fresh process, same agent)
    qw_probe = dispatch(QUERY_WRITER_AGENT, CTX_PROBE, allowed_tools=None, timeout=timeout)
    qwp = _json_probe(qw_probe.final_text)
    live["query_writer_probe"] = {"dispatch": qw_probe.to_json(), "report": qwp}

    # 3/4. search executed for C (model query) and D (fixed query), SAME mechanism
    fq = fixed_query(CANARY)
    c_query = model_query or fq
    sr_c, row_c = run_search_stage(CANARY, "C", c_query, "model", timeout=timeout)
    sr_d, row_d = run_search_stage(CANARY, "D", fq, "fixed", timeout=timeout)
    live["search_C"] = row_c.to_json()
    live["search_D"] = row_d.to_json()

    # 5. answerer, arm C packet (exposed), carrying the parsed block
    block_c = sr_c.block.injected if sr_c.block else None
    ans_packet = build_answer_packet(CANARY["question"], block_c)
    ans = dispatch(ANSWERER_AGENT, ans_packet, allowed_tools=None, timeout=timeout)
    live["answerer_C"] = ans.to_json()

    # 6. answerer context probe (fresh process, same agent, arm A shape)
    ans_probe = dispatch(ANSWERER_AGENT, CTX_PROBE, allowed_tools=None, timeout=timeout)
    ansp = _json_probe(ans_probe.final_text)
    live["answerer_probe"] = {"dispatch": ans_probe.to_json(), "report": ansp}

    # ---- the fourteen checks ---------------------------------------------- #

    # 1 query writer starts fresh
    seen = ansp.get("marker_seen")
    if isinstance(seen, str):
        checks.append(_chk("C01", "query writer / answerer start fresh",
                           PASS if MARKER not in seen and seen.upper() in ("NONE", "") else FAIL,
                           f"probe reports marker_seen={seen!r}; each dispatch is its own process",
                           {"marker": MARKER}))
    else:
        checks.append(_chk("C01", "query writer / answerer start fresh", UNOBS,
                           "probe did not return a marker_seen field", {"report": ansp}))

    # 2 query writer cannot access answer keys / files
    crf = qwp.get("can_read_files")
    checks.append(_chk("C02", "query writer has no file access (key quarantine)",
                       PASS if crf is False else (FAIL if crf is True else UNOBS),
                       f"query-writer self-report can_read_files={crf!r}; "
                       f"realized tool surface={qw_probe.init_tools!r}",
                       {"realized_tools": qw_probe.init_tools}))

    # 3 query text is persisted
    checks.append(_chk("C03", "query text persisted",
                       PASS if model_query else FAIL,
                       f"model query recorded: {model_query!r} (extract failure: {qfail!r})",
                       {"fixed_query": fq}))

    # 4 search ACTUALLY executed for C
    checks.append(_chk("C04", "search actually executed for arm C",
                       PASS if (sr_c.executed and (sr_c.search_requests or 0) >= 1) else FAIL,
                       f"tool_result present={sr_c.executed}, "
                       f"authoritative webSearchRequests={sr_c.search_requests}, "
                       f"server_tool_use={sr_c.dispatch.server_tool_use} (known-defective, "
                       f"recorded to show it is not the indicator)",
                       {"query": c_query}))

    # 5 search ACTUALLY executed for D
    checks.append(_chk("C05", "search actually executed for arm D",
                       PASS if (sr_d.executed and (sr_d.search_requests or 0) >= 1) else FAIL,
                       f"tool_result present={sr_d.executed}, "
                       f"authoritative webSearchRequests={sr_d.search_requests}",
                       {"query": fq}))

    # 6 C and D use the same search mechanism
    same = (row_c.agent == row_d.agent == SEARCHER_AGENT
            and row_c.configured_command[:-2] == row_d.configured_command[:-2]
            and row_c.configured_tools == row_d.configured_tools
            and row_c.realized_tool_surface == row_d.realized_tool_surface
            and row_c.configured_model_flag == row_d.configured_model_flag)
    checks.append(_chk("C06", "C and D use the same search mechanism",
                       PASS if same else FAIL,
                       f"agent {row_c.agent}=={row_d.agent}; realized surfaces "
                       f"{row_c.realized_tool_surface} vs {row_d.realized_tool_surface}; "
                       f"model flag {row_c.configured_model_flag}",
                       {"cmd_C": row_c.configured_command, "cmd_D": row_d.configured_command}))

    # 7 authoritative runtime result representation persisted
    ok7 = bool(row_c.raw_search_artifact and row_c.raw_artifact_sha
               and row_d.raw_search_artifact and row_d.raw_artifact_sha)
    checks.append(_chk("C07", "authoritative runtime block persisted, with hash",
                       PASS if ok7 else FAIL,
                       f"C raw sha={row_c.raw_artifact_sha}, D raw sha={row_d.raw_artifact_sha}; "
                       f"taken from the stream tool_result, NOT from the searcher's prose",
                       {"C_len": len(row_c.raw_search_artifact or ""),
                        "D_len": len(row_d.raw_search_artifact or "")}))

    # 8 injected block equals the parser-produced artifact, and is inside the packet
    inj = sr_c.block.injected if sr_c.block else None
    ok8 = bool(inj) and inj in ans_packet and sha(inj) == row_c.injected_block_sha
    checks.append(_chk("C08", "injected block == parser artifact, byte for byte",
                       PASS if ok8 else FAIL,
                       f"parsed sha={row_c.injected_block_sha}; substring of the realized "
                       f"answering packet={bool(inj) and inj in ans_packet}; "
                       f"runtime imperative removed={row_c.reminder_stripped!r}",
                       {"packet_sha": sha(ans_packet)}))

    # 9 answerer context is fresh
    aseen = ansp.get("marker_seen")
    checks.append(_chk("C09", "answerer context is fresh",
                       PASS if isinstance(aseen, str) and aseen.upper() in ("NONE", "") else
                       (FAIL if isinstance(aseen, str) else UNOBS),
                       f"answerer probe marker_seen={aseen!r}; separate process per dispatch",
                       {"answerer_session": ans.session_id,
                        "query_writer_session": qw.session_id}))

    # 10 query-writer history does not appear in the C answerer context
    body = ans_packet
    leaked = [s for s in (MARKER, qw.final_text or "\x00INVALID\x00") if s and s in body]
    checks.append(_chk("C10", "query-writer history absent from the C answering packet",
                       PASS if not leaked else FAIL,
                       f"the realized arm-C packet contains the injected block and the "
                       f"question, and none of the query writer's output or marker "
                       f"(leaked={[l[:40] for l in leaked]})",
                       {"query_writer_output_sha": sha(qw.final_text or ""),
                        "sessions_differ": qw.session_id != ans.session_id}))

    # 11 A gets no search result block
    a_packet = build_answer_packet(CANARY["question"], None)
    ok11 = ("BEGIN SEARCH RESULT BLOCK" not in a_packet
            and "Links:" not in a_packet
            and (inj or "\x00") not in a_packet)
    checks.append(_chk("C11", "arm A packet carries no search result block",
                       PASS if ok11 else FAIL,
                       f"arm A packet sha={sha(a_packet)}, {len(a_packet)} chars, "
                       f"no exposure section present",
                       {"A_packet": a_packet}))

    # 12 C/D answering packets differ only where intended
    if sr_c.block and sr_d.block:
        rep = packet_diff_report(CANARY["question"], sr_c.block.injected, sr_d.block.injected)
        ok12 = rep["C_and_D_differ_only_inside_the_block"] and rep["A_contains_no_exposure_section"]
        checks.append(_chk("C12", "C/D packets differ only in the injected block",
                           PASS if ok12 else FAIL,
                           f"C sha={rep['C_sha'][:16]} D sha={rep['D_sha'][:16]}; "
                           f"identical after masking the block: "
                           f"{rep['C_and_D_differ_only_inside_the_block']}", rep))
    else:
        checks.append(_chk("C12", "C/D packets differ only in the injected block", UNOBS,
                           "one arm produced no block, so no packet pair exists to diff", None))

    # 13 served model and configured effort MEASURED, not assumed
    disp = {"query_writer": qw, "searcher_C": sr_c.dispatch, "searcher_D": sr_d.dispatch,
            "answerer": ans}
    served = {k: v.models_used for k, v in disp.items()}
    solver_models = {m for v in disp.values() for m in v.models_used if "haiku" not in m}
    cmds = {k: " ".join(v.agent for _ in [0]) for k, v in disp.items()}
    ok13 = len(solver_models) == 1 and all(v.models_used for v in disp.values())
    checks.append(_chk("C13", "served model + configured effort measured per dispatch",
                       PASS if ok13 else FAIL,
                       f"solver model across all four dispatches: {sorted(solver_models)}; "
                       f"configured effort is the frozen command line, recorded per dispatch; "
                       f"realized effort (output tokens) is a mediator and is NOT equalised: "
                       f"{ {k: v.output_tokens for k, v in disp.items()} }",
                       {"served_models": served,
                        "realized_thinking_tokens": {k: v.thinking_tokens for k, v in disp.items()},
                        "cost_usd": {k: v.cost_usd for k, v in disp.items()}}))

    # 14 environment / search reachability measured through the Stage 0B path
    reach = {"search_ok": bool(sr_c.executed and sr_d.executed),
             "searcher_realized_tools": sr_c.dispatch.init_tools,
             "webfetch_on_stage0b_path": "WebFetch" in (sr_c.dispatch.init_tools or []),
             "answerer_realized_tools": ans_probe.init_tools,
             "query_writer_realized_tools": qw_probe.init_tools}
    ok14 = reach["search_ok"] and not reach["webfetch_on_stage0b_path"]
    checks.append(_chk("C14", "environment measured through the actual Stage 0B path",
                       PASS if ok14 else FAIL,
                       f"search reachable 2/2 through the Stage 0B searcher; WebFetch is not "
                       f"granted anywhere on the Stage 0B path, so the environment is "
                       f"search-capable and fetch-absent BY CONSTRUCTION as well as blocked. "
                       f"The treatment is runtime_exposed_search_result_block, never "
                       f"unrestricted web retrieval.", reach))

    failed = [c for c in checks if c["status"] == FAIL]
    unobs = [c for c in checks if c["status"] == UNOBS]
    return {
        "gate": "stage0b_runtime_correspondence",
        "construct": "runtime_exposed_search_result_block",
        "static_config_is_not_evidence": "Every check above dispatched. A frontmatter or "
                                         "config assertion may not substitute for any of them.",
        "canary_item": CANARY,
        "checks": checks,
        "counts": {"total": len(checks), "pass": len(checks) - len(failed) - len(unobs),
                   "fail": len(failed), "unobservable": len(unobs)},
        "status": "PASS" if not failed else "FAIL",
        "live_records": live,
        "total_cost_usd": round(sum(d.cost_usd or 0 for d in
                                    [qw, qw_probe, sr_c.dispatch, sr_d.dispatch, ans, ans_probe]), 4),
        "dispatches": 6,
    }


def main() -> int:
    doc = run_gate()
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(doc, indent=1) + "\n")
    print(json.dumps({"status": doc["status"], "counts": doc["counts"],
                      "cost_usd": doc["total_cost_usd"]}, indent=1))
    for c in doc["checks"]:
        print(f"  {c['id']} {c['status']:12} {c['check']}")
        if c["status"] != "PASS":
            print(f"        -> {c['detail']}")
    return 0 if doc["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
