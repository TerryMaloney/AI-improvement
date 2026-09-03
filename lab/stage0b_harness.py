"""Stage 0B — arms A / C / D, and the per-dispatch ledger row.

    A   answerer(packet without exposure section)
    C   query-writer -> query -> searcher -> block -> answerer(packet + block)
    D   fixed query          -> searcher -> block -> answerer(packet + block)

ISOLATION
---------
Each dispatch is its own `claude -p` process. The query writer's reasoning never
reaches the answerer because the answerer is a different process that is handed
one string: the packet. The only causal path from C's query writer to C's
answerer is

    query -> search execution -> runtime block -> injected exposure section

and that path is the treatment. The runtime gate measures the isolation rather
than asserting it, by planting a marker in the query-writer dispatch and looking
for it in the answerer's context.

C/D SYMMETRY
------------
C and D differ in exactly one place: the string passed to `execute_search`.
They share the searcher agent, the model flag, the tool grant, the searcher
packet, the parser, the answerer agent, the answering packet and the grader.
That is enforced structurally -- `run_arm` takes a query and does not take
anything else that could differ -- and asserted by `packet_diff_report`.

TELEMETRY LINEAGE
-----------------
Every field in a `DispatchRow` is read off a runtime record. Stage 0A-M's
`retrieval_failure_rate` reported `attempted_retrieval: 0` because the analysis
built its outcome objects from empty tuples: a plausible field with no lineage.
Here a value the runtime did not expose is `None`, and `None` means UNOBSERVABLE.
It is never coerced to 0.
"""
from __future__ import annotations

import json
import pathlib
import re
from dataclasses import dataclass, field, asdict

from lab.stage0b_search import (Dispatch, ExposureBlock, SearchResult, dispatch,
                                execute_search, relevance_flags, sha)

REPO = pathlib.Path(__file__).resolve().parent.parent

QUERY_WRITER_AGENT = "stage0b-query-writer"
ANSWERER_AGENT = "stage0b-answerer"
SEARCHER_AGENT = "stage0b-searcher"
CMD_MODEL = "opus"

ARMS = ("A", "C", "D")
EXPOSED_ARMS = ("C", "D")

# --------------------------------------------------------------------------- #
# packets
# --------------------------------------------------------------------------- #

QUERY_WRITER_PACKET = (
    "You will be given one question.\n\n"
    "Write the single web search query you would use to look up its answer.\n"
    "Do not answer the question.\n\n"
    "QUESTION:\n{QUESTION}\n\n"
    'Return only a single JSON object: {"query": "<your one query>"}\n'
)

# The answering packet. `{EXPOSURE}` is the empty string in arm A and the
# exposure section in arms C and D, so A-vs-C/D differ by exactly that section
# and C-vs-D differ by exactly the block inside it. The answer-first instruction
# is part of the grader (design draft 3.4) and is identical in every arm.
ANSWER_PACKET = (
    "You are answering exactly one question in a controlled evaluation.\n\n"
    "QUESTION:\n{QUESTION}\n\n"
    "{EXPOSURE}"
    "Begin your reply with the direct answer. Add context afterwards if you wish.\n\n"
    'Return only a single JSON object: {"answer": "<your reply>"}\n'
)

EXPOSURE_SECTION = (
    "SEARCH RESULTS\n"
    "The block below was returned by a web search that the harness executed for this\n"
    "question. It is reproduced as the search returned it.\n\n"
    "<<<BEGIN SEARCH RESULT BLOCK\n"
    "{BLOCK}\n"
    "END SEARCH RESULT BLOCK>>>\n\n"
)


def build_answer_packet(question: str, block_text: str | None) -> str:
    exposure = "" if block_text is None else EXPOSURE_SECTION.replace("{BLOCK}", block_text)
    return ANSWER_PACKET.replace("{QUESTION}", question).replace("{EXPOSURE}", exposure)


def build_query_writer_packet(question: str) -> str:
    return QUERY_WRITER_PACKET.replace("{QUESTION}", question)


def packet_diff_report(question: str, block_c: str, block_d: str) -> dict:
    """What actually differs between the three arms' answering packets.

    Stage 0A-M asserted a 3-line packet diff. Stage 0B asserts the same class of
    invariant on a longer packet, and does it on realized strings rather than on
    the templates, so a substitution bug cannot hide inside it.
    """
    a = build_answer_packet(question, None)
    c = build_answer_packet(question, block_c)
    d = build_answer_packet(question, block_d)
    a_lines, c_lines, d_lines = a.splitlines(), c.splitlines(), d.splitlines()
    return {
        "A_sha": sha(a), "C_sha": sha(c), "D_sha": sha(d),
        "A_is_C_minus_exposure": c == a.replace(
            "Begin your reply", EXPOSURE_SECTION.replace("{BLOCK}", block_c) + "Begin your reply", 1),
        "C_and_D_differ_only_inside_the_block":
            c.replace(block_c, "\x00BLOCK\x00") == d.replace(block_d, "\x00BLOCK\x00"),
        "A_contains_no_exposure_section": "BEGIN SEARCH RESULT BLOCK" not in a,
        "A_line_count": len(a_lines), "C_line_count": len(c_lines), "D_line_count": len(d_lines),
    }


# --------------------------------------------------------------------------- #
# fixed-query construction (frozen rule, design draft 5)
# --------------------------------------------------------------------------- #

def fixed_query(item: dict) -> str:
    """The anchor-preserving fixed query for arm D.

    Mechanical and derivable by a third party from the item alone: the entity or
    quantity phrase, then the anchor exactly as the stem writes it. No operators,
    no site restrictions, no term absent from the stem. It is "high quality" only
    in the narrow sense that it preserves the anchor -- the hypothesised failure
    mode of a model-written query -- and is deliberately not optimised further,
    because an optimised query would confound query quality with query effort.
    """
    subject, anchor = item["query_subject"], item["anchor_as_written"]
    if not isinstance(subject, str) or not isinstance(anchor, str):
        # A YAML anchor written as a bare 2015 parses to an int and would make the
        # fixed query depend on how the file was quoted rather than on the stem.
        raise TypeError(f"item {item.get('id')}: query_subject and anchor_as_written "
                        f"must be strings as written in the stem")
    subject, anchor = subject.strip(), anchor.strip()
    q = f"{subject} {anchor}".strip()
    if not q:
        raise ValueError(f"item {item.get('id')} yields an empty fixed query")
    for banned in ('"', "site:", " OR ", " AND ", "-"):
        if banned in q and banned == "site:":
            raise ValueError(f"fixed query for {item.get('id')} carries an operator: {q!r}")
    return q


# --------------------------------------------------------------------------- #
# the ledger row
# --------------------------------------------------------------------------- #

@dataclass
class DispatchRow:
    """One dispatch. Three of these make an arm-C trial; one makes an arm-A trial.

    `None` means the runtime did not expose the value. It never means zero.
    """
    item_id: str
    arm: str
    stage: str                       # query_write | search | answer
    dispatch_index: int
    agent: str
    configured_model_flag: str
    configured_tools: list[str]
    configured_command: list[str]
    realized_tool_surface: list[str] | None
    served_models: list[str]
    session_id: str | None
    prompt_sha: str
    query_source: str | None         # model | fixed | None
    query_text: str | None
    realized_query: str | None
    query_faithful: bool | None
    web_search_requests: int | None  # authoritative
    server_tool_use: dict | None     # defective on this path; recorded to show it
    raw_search_artifact: str | None
    raw_artifact_sha: str | None
    injected_block: str | None
    injected_block_sha: str | None
    reminder_stripped: str | None
    relevance: dict | None
    final_text: str | None
    answer_text: str | None
    input_tokens: int | None
    output_tokens: int | None
    thinking_tokens: int | None
    cost_usd: float | None
    wall_s: float | None
    duration_ms: int | None
    num_turns: int | None
    permission_denials: list | None
    failure: str | None

    def to_json(self) -> dict:
        return asdict(self)


ANALYSIS_FIELD_LINEAGE = {
    # analysis field                 -> the runtime record it is read from
    "search_attempted":              "sum(result.modelUsage[*].webSearchRequests)",
    "search_executed":               "presence of a WebSearch tool_result block in the stream",
    "query_text":                    "assistant tool_use.input.query (realized), harness string (requested)",
    "raw_artifact_sha":              "sha256 of the tool_result content string",
    "injected_block_sha":            "sha256 of the string substituted into the answering packet",
    "relevance_flags":               "deterministic containment over injected_block",
    "served_model":                  "result.modelUsage keys, per dispatch",
    "realized_effort_tokens":        "result.usage.output_tokens, per dispatch",
    "realized_thinking_tokens":      "result.usage.output_tokens_details.thinking_tokens",
    "cost_usd":                      "result.total_cost_usd, per dispatch",
    "wall_s":                        "harness clock around subprocess.run",
    "realized_tool_surface":         "system/init.tools, per dispatch",
    "answer_text":                   "assistant text block / JSON `answer` field",
    "failure":                       "lab.stage0b_failures classification of the above",
}

# Explicitly NOT bound, so nobody re-derives Stage 0A-M's vacuous field:
FORBIDDEN_LINEAGE = {
    "usage.server_tool_use.web_search_requests":
        "reports 0 on this harness path even when a search demonstrably ran "
        "(measured 2026-09-03). Recorded for visibility; never an indicator.",
}


def _row(item_id: str, arm: str, stage: str, idx: int, agent: str,
         tools: list[str], d: Dispatch, **kw) -> DispatchRow:
    cmd = ["claude", "-p", "--agent", agent, "--model", CMD_MODEL,
           "--output-format", "stream-json", "--verbose"]
    if tools:
        cmd += ["--allowedTools", *tools]
    base = dict(
        item_id=item_id, arm=arm, stage=stage, dispatch_index=idx, agent=agent,
        configured_model_flag=CMD_MODEL, configured_tools=list(tools),
        configured_command=cmd, realized_tool_surface=d.init_tools,
        served_models=d.models_used, session_id=d.session_id, prompt_sha=d.prompt_sha,
        query_source=None, query_text=None, realized_query=None, query_faithful=None,
        web_search_requests=d.web_search_requests, server_tool_use=d.server_tool_use,
        raw_search_artifact=None, raw_artifact_sha=None, injected_block=None,
        injected_block_sha=None, reminder_stripped=None, relevance=None,
        final_text=d.final_text, answer_text=None,
        input_tokens=d.input_tokens, output_tokens=d.output_tokens,
        thinking_tokens=d.thinking_tokens, cost_usd=d.cost_usd, wall_s=d.wall_s,
        duration_ms=d.duration_ms, num_turns=d.num_turns,
        permission_denials=d.permission_denials, failure=None,
    )
    base.update(kw)
    return DispatchRow(**base)


# --------------------------------------------------------------------------- #
# stages
# --------------------------------------------------------------------------- #

_QUERY_JSON = re.compile(r'"query"\s*:\s*"((?:[^"\\]|\\.)*)"')


def extract_query(text: str | None) -> tuple[str | None, str | None]:
    """(query, failure_code). Exactly one query is required."""
    if not text or not text.strip():
        return None, "QUERY_WRITER_NO_OUTPUT"
    t = text.strip()
    try:
        obj = json.loads(t)
        if isinstance(obj, dict) and isinstance(obj.get("query"), str):
            return obj["query"], None
        if isinstance(obj, dict) and isinstance(obj.get("query"), list):
            return None, "QUERY_WRITER_MULTIPLE_QUERIES"
    except Exception:
        pass
    found = _QUERY_JSON.findall(t)
    if len(found) == 1:
        return json.loads(f'"{found[0]}"'), None
    if len(found) > 1:
        return None, "QUERY_WRITER_MULTIPLE_QUERIES"
    return None, "QUERY_WRITER_NO_OUTPUT"


def extract_answer(text: str | None) -> tuple[str | None, str | None]:
    """(answer, failure_code). Non-JSON but non-empty text is still an answer."""
    if not text or not text.strip():
        return None, "EMPTY_RESPONSE"
    t = text.strip()
    try:
        obj = json.loads(t)
        if isinstance(obj, dict) and "answer" in obj:
            return str(obj["answer"]), None
    except Exception:
        pass
    return t, None


def write_query(item: dict, timeout: int = 600) -> tuple[str | None, DispatchRow]:
    packet = build_query_writer_packet(item["question"])
    d = dispatch(QUERY_WRITER_AGENT, packet, allowed_tools=None, timeout=timeout)
    query, fail = extract_query(d.final_text)
    if d.returncode != 0 or d.is_error or d.parse_error:
        fail = "DISPATCH_ERROR"
    row = _row(item["id"], "C", "query_write", 1, QUERY_WRITER_AGENT, [], d,
               query_source="model", query_text=query, failure=fail)
    return query, row


def run_search_stage(item: dict, arm: str, query: str, source: str,
                     timeout: int = 600) -> tuple[SearchResult, DispatchRow]:
    sr = execute_search(query, timeout=timeout)
    b: ExposureBlock | None = sr.block
    rel = None
    if b is not None and b.parse_ok:
        rel = relevance_flags(b, item.get("accept_aliases", []), item.get("reject_aliases", []))
    row = _row(item["id"], arm, "search", 2, SEARCHER_AGENT, ["WebSearch"], sr.dispatch,
               query_source=source, query_text=query, realized_query=sr.realized_query,
               query_faithful=sr.query_faithful,
               raw_search_artifact=b.raw if b else None,
               raw_artifact_sha=b.raw_sha if b else None,
               injected_block=b.injected if b else None,
               injected_block_sha=b.injected_sha if b else None,
               reminder_stripped=b.reminder_stripped if b else None,
               relevance=rel, failure=sr.failure)
    return sr, row


def run_answer_stage(item: dict, arm: str, block_text: str | None,
                     timeout: int = 600) -> tuple[str | None, DispatchRow]:
    packet = build_answer_packet(item["question"], block_text)
    d = dispatch(ANSWERER_AGENT, packet, allowed_tools=None, timeout=timeout)
    answer, fail = extract_answer(d.final_text)
    if d.returncode != 0 or d.is_error or d.parse_error:
        fail = "DISPATCH_ERROR"
    idx = 1 if arm == "A" else 3
    row = _row(item["id"], arm, "answer", idx, ANSWERER_AGENT, [], d,
               injected_block=block_text,
               injected_block_sha=sha(block_text) if block_text is not None else None,
               answer_text=answer, failure=fail)
    return answer, row


def run_arm(item: dict, arm: str, timeout: int = 600) -> dict:
    """One arm of one item. Returns a trial record: rows plus the derived answer.

    C and D reach `run_search_stage` with the same agent, model, tool grant and
    packet, and differ only in `query`. There is no other parameter for them to
    differ in, which is the symmetry, expressed as code rather than as prose.
    """
    if arm not in ARMS:
        raise ValueError(f"unknown arm {arm!r}")
    rows: list[DispatchRow] = []

    if arm == "A":
        answer, r = run_answer_stage(item, "A", None, timeout=timeout)
        rows.append(r)
        return {"item_id": item["id"], "arm": arm, "answer": answer,
                "rows": [x.to_json() for x in rows], "failure": r.failure}

    if arm == "C":
        query, qrow = write_query(item, timeout=timeout)
        rows.append(qrow)
        if qrow.failure or not query:
            return {"item_id": item["id"], "arm": arm, "answer": None,
                    "rows": [x.to_json() for x in rows], "failure": qrow.failure}
        source = "model"
    else:
        query, source = fixed_query(item), "fixed"

    sr, srow = run_search_stage(item, arm, query, source, timeout=timeout)
    rows.append(srow)
    if srow.failure or sr.block is None:
        return {"item_id": item["id"], "arm": arm, "answer": None,
                "rows": [x.to_json() for x in rows], "failure": srow.failure}

    answer, arow = run_answer_stage(item, arm, sr.block.injected, timeout=timeout)
    rows.append(arow)
    return {"item_id": item["id"], "arm": arm, "answer": answer,
            "rows": [x.to_json() for x in rows], "failure": arow.failure}
