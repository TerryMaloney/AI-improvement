"""Stage 0B — the search-exposure instrument.

WHAT THIS MODULE EXISTS TO GET RIGHT
------------------------------------
The Stage 0B design draft said the searcher would "return the search result block
verbatim". Measured against the live runtime on 2026-09-03, that sentence is
false in three separate ways, and every one of them matters:

1.  **A model rewrites the block.** The searcher agent's prose output is a
    *retelling*: it reformats the links as markdown, drops the header line, drops
    the trailing runtime instruction, and duplicates the source list because the
    runtime instruction told it to. Nothing byte-identical survives that path.

2.  **The provider's results are not what crosses the boundary.** What the
    runtime hands the searcher is a composed block: a header echoing the query, a
    `Links:` JSON array of **titles and URLs only — no snippets**, a
    **model-synthesised prose answer to the query**, and a trailing imperative
    addressed to the reader. There are no search snippets anywhere in it.

3.  **It is not reproducible.** Two dispatches of the identical query returned
    byte-identical `Links:` arrays and a *different* synthesised paragraph. A
    hash of this artifact is per-trial provenance. It is not a reproducibility
    guarantee and must never be described as one.

So the recorded artifact is taken from the runtime, not from the searcher model.
`--output-format stream-json` exposes the `tool_result` content block the runtime
gave the agent; that string is the authoritative representation and it is what
this module persists. The searcher's own prose is captured for audit and is
never used as data. The searcher model is reduced to the one thing the harness
cannot do itself — issue the tool call — and whether it issued the *requested*
query is then checked by byte equality against `tool_use.input.query`.

The construct is therefore named `runtime_exposed_search_result_block`.
Not "web retrieval", and not "search snippet exposure" either: there are no
snippets in it.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import subprocess
import time
from dataclasses import dataclass, field, asdict

REPO = pathlib.Path(__file__).resolve().parent.parent

SEARCHER_AGENT = "stage0b-searcher"
CMD_MODEL = "opus"

# The trailing imperative the runtime appends to a WebSearch tool result. It is
# an instruction addressed to the agent that ran the search, not retrieved
# content, and injecting it into an answerer would (a) tell that answerer to emit
# markdown source lists, a format change arm A never receives, which interacts
# directly with the grader's leading-sentence span rule, and (b) put an
# instruction inside a block the contract calls retrieved content. It is removed,
# and the removal is recorded verbatim rather than performed silently.
REMINDER_RE = re.compile(r"\n+REMINDER:[^\n]*\s*\Z")

HEADER_RE = re.compile(r'\AWeb search results for query: "(?P<query>.*)"\s*\n', re.S)
LINKS_RE = re.compile(r"^Links: (?P<json>\[.*\])\s*$", re.M)


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- #
# dispatch
# --------------------------------------------------------------------------- #

@dataclass
class Dispatch:
    """One `claude -p` process, parsed out of its stream-json transcript.

    Every field here is read from the transcript. Nothing is assumed and nothing
    is defaulted to a plausible value -- a field the runtime did not expose is
    None, and the callers treat None as UNOBSERVABLE rather than as zero.
    """
    agent: str
    prompt_sha: str
    returncode: int
    wall_s: float
    session_id: str | None = None
    init_tools: list[str] | None = None          # tool surface the runtime realized
    init_model: str | None = None                # model the runtime says it started with
    tool_calls: list[dict] = field(default_factory=list)   # {name, input}
    tool_results: list[str] = field(default_factory=list)  # raw content strings
    final_text: str | None = None
    models_used: list[str] = field(default_factory=list)
    web_search_requests: int | None = None       # AUTHORITATIVE: sum over modelUsage
    server_tool_use: dict | None = None          # known-defective on this path; kept to show it
    num_turns: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    thinking_tokens: int | None = None
    cost_usd: float | None = None
    duration_ms: int | None = None
    permission_denials: list | None = None
    is_error: bool | None = None
    stop_reason: str | None = None
    parse_error: str | None = None
    stderr_head: str | None = None

    def to_json(self) -> dict:
        return asdict(self)


def parse_stream(lines: list[str]) -> dict:
    """Pull the load-bearing records out of a stream-json transcript."""
    out: dict = {"tool_calls": [], "tool_results": [], "final_text": None,
                 "init_tools": None, "init_model": None, "session_id": None, "result": None}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except Exception:
            continue
        t = rec.get("type")
        if t == "system" and rec.get("subtype") == "init":
            out["init_tools"] = sorted(rec.get("tools") or [])
            out["init_model"] = rec.get("model")
            out["session_id"] = rec.get("session_id")
        elif t == "assistant":
            for b in (rec.get("message") or {}).get("content") or []:
                if b.get("type") == "tool_use":
                    out["tool_calls"].append({"name": b.get("name"), "input": b.get("input")})
                elif b.get("type") == "text":
                    out["final_text"] = b.get("text")
        elif t == "user":
            for b in (rec.get("message") or {}).get("content") or []:
                if b.get("type") == "tool_result":
                    c = b.get("content")
                    if isinstance(c, list):      # some tools return block lists
                        c = "".join(x.get("text", "") for x in c if isinstance(x, dict))
                    out["tool_results"].append(c if isinstance(c, str) else json.dumps(c))
        elif t == "result":
            out["result"] = rec
    return out


def dispatch(agent: str, prompt: str, allowed_tools: list[str] | None = None,
             timeout: int = 600, model: str = CMD_MODEL) -> Dispatch:
    """Dispatch one fresh-context agent and record what the runtime exposed.

    Fresh context is a property of the process: a new `claude -p` invocation
    carries no conversation state from any previous one. That is the isolation
    the C arm depends on, and the runtime gate measures it rather than trusting
    this docstring.
    """
    cmd = ["claude", "-p", "--agent", agent, "--model", model,
           "--output-format", "stream-json", "--verbose"]
    if allowed_tools:
        cmd += ["--allowedTools", *allowed_tools]
    t0 = time.time()
    proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout)
    wall = round(time.time() - t0, 2)

    d = Dispatch(agent=agent, prompt_sha=sha(prompt), returncode=proc.returncode, wall_s=wall)
    d.stderr_head = (proc.stderr or "")[:2000] or None
    try:
        p = parse_stream(proc.stdout.splitlines())
    except Exception as exc:                                  # HARNESS FAILURE
        d.parse_error = f"stream parse failed: {exc}"
        return d

    d.session_id = p["session_id"]
    d.init_tools = p["init_tools"]
    d.init_model = p["init_model"]
    d.tool_calls = p["tool_calls"]
    d.tool_results = p["tool_results"]
    d.final_text = p["final_text"]

    r = p["result"]
    if r is None:
        d.parse_error = "no result record in stream"
        return d
    mu = r.get("modelUsage") or {}
    d.models_used = sorted(mu.keys())
    # AUTHORITATIVE search-attempt indicator. `usage.server_tool_use` reports 0
    # on this harness path even when a search demonstrably ran (measured
    # 2026-09-03, and the same defect made Stage 0A-M's retrieval_failure_rate
    # vacuous). WebSearch is billed to the model that services it -- observed on
    # claude-haiku-4-5, not on the solver model -- so the sum over ALL models is
    # the indicator, never the solver model's own count.
    d.web_search_requests = sum(int(v.get("webSearchRequests") or 0) for v in mu.values()) if mu else None
    u = r.get("usage") or {}
    d.server_tool_use = u.get("server_tool_use")
    d.num_turns = r.get("num_turns")
    d.input_tokens = u.get("input_tokens")
    d.output_tokens = u.get("output_tokens")
    d.thinking_tokens = (u.get("output_tokens_details") or {}).get("thinking_tokens")
    d.cost_usd = r.get("total_cost_usd")
    d.duration_ms = r.get("duration_ms")
    d.permission_denials = r.get("permission_denials")
    d.is_error = r.get("is_error")
    d.stop_reason = r.get("stop_reason")
    return d


# --------------------------------------------------------------------------- #
# the treatment artifact
# --------------------------------------------------------------------------- #

@dataclass
class ExposureBlock:
    """The parsed runtime search-result block, and the text actually injected.

    `raw` is what the runtime handed the searcher, byte for byte.
    `injected` is `raw` minus the trailing runtime imperative, and nothing else.
    Both are hashed, because they are different objects and conflating them is
    how a treatment stops being the thing the contract names.
    """
    raw: str
    raw_sha: str
    injected: str
    injected_sha: str
    header_query: str | None          # the query the runtime echoed back
    links: list[dict]                 # [{title, url}] -- titles and URLs only
    link_count: int
    summary_text: str | None          # runtime-synthesised prose answer, or None
    has_summary: bool
    reminder_stripped: str | None     # the exact imperative removed, for audit
    parse_ok: bool
    parse_note: str | None = None

    def to_json(self) -> dict:
        return asdict(self)


def parse_exposure_block(raw: str) -> ExposureBlock:
    """Parse a runtime WebSearch tool_result into the Stage 0B treatment artifact.

    Measured shape (2026-09-03, Claude Code 2.1.259):

        Web search results for query: "<query>"
        <blank>
        Links: [{"title":...,"url":...}, ...]
        <blank>
        <model-synthesised prose answer>
        <blank>
        REMINDER: You MUST include the sources above ...

    Every one of those parts is optional in this parser and its absence is
    recorded rather than raised, because a parser that throws on an unseen shape
    turns a TREATMENT REALIZATION FAILURE into a HARNESS FAILURE and the two have
    different consequences for the trial.
    """
    note = []
    m = REMINDER_RE.search(raw)
    reminder = m.group(0).strip() if m else None
    injected = REMINDER_RE.sub("", raw).rstrip() if m else raw.rstrip()
    if reminder is None:
        note.append("no trailing REMINDER imperative found")

    h = HEADER_RE.search(raw)
    header_query = h.group("query") if h else None
    if header_query is None:
        note.append("no header line")

    links: list[dict] = []
    lm = LINKS_RE.search(raw)
    if lm:
        try:
            parsed = json.loads(lm.group("json"))
            if isinstance(parsed, list):
                links = [x for x in parsed if isinstance(x, dict)]
        except Exception as exc:
            note.append(f"Links array did not parse: {exc}")
    else:
        note.append("no Links array")

    # The summary is whatever remains after the header, the Links line and the
    # reminder are removed. It is the runtime's own answer to the query and is
    # the part that varies between two dispatches of an identical query.
    rest = injected
    if h:
        rest = rest[h.end():]
    if lm:
        rest = LINKS_RE.sub("", rest)
    summary = rest.strip() or None
    if summary is None:
        note.append("no synthesised summary paragraph")

    parse_ok = bool(links) or bool(summary)
    if not parse_ok:
        note.append("block carries neither links nor summary: not a usable treatment artifact")

    return ExposureBlock(
        raw=raw, raw_sha=sha(raw),
        injected=injected, injected_sha=sha(injected),
        header_query=header_query, links=links, link_count=len(links),
        summary_text=summary, has_summary=summary is not None,
        reminder_stripped=reminder, parse_ok=parse_ok,
        parse_note="; ".join(note) or None,
    )


def relevance_flags(block: ExposureBlock, accept_aliases: list[str],
                    reject_aliases: list[str]) -> dict:
    """Deterministic, model-free flags over the INJECTED block.

    Computed on `injected`, because that is what an answerer sees. Case-folded
    substring containment and nothing cleverer: the flag is a property of the
    treatment environment, and any judgement here would make item selection
    depend on a model.

    KNOWN LIMITATION, MEASURED RATHER THAN ASSUMED
    ----------------------------------------------
    Containment fires on incidental text. Measured on the real Lovelace block
    (2026-09-03): the reject alias "1852" matched inside the link title "Ada
    Lovelace (1815 - 1852)" -- a biographical date range, carrying no displacing
    claim at all. A flag that reported only `reject_present` would have called
    that item divergent and spent a production slot on it.

    So the match is located as well as detected. `reject_in_summary` is the
    strong signal: the summary is the runtime's own assertion about the answer,
    and an alias there is a claim. `reject_in_links_only` is the weak one, and
    the selection rule is written on `divergent`, which requires the strong
    signal. Both are recorded, so a later analysis can separate them without
    re-running a search.
    """
    def _hits(aliases, hay):
        return sorted({a for a in aliases if a and a.casefold() in hay})

    whole = block.injected.casefold()
    summary = (block.summary_text or "").casefold()
    links_text = json.dumps(block.links).casefold()

    acc = _hits(accept_aliases, whole)
    rej = _hits(reject_aliases, whole)
    acc_sum = _hits(accept_aliases, summary)
    rej_sum = _hits(reject_aliases, summary)
    rej_links = _hits(reject_aliases, links_text)

    if acc and rej:
        cls = "both"
    elif rej:
        cls = "reject_only"
    elif acc:
        cls = "accept_only"
    else:
        cls = "neither"
    return {
        "accept_present": bool(acc), "reject_present": bool(rej),
        "accept_matched": acc, "reject_matched": rej,
        "accept_in_summary": bool(acc_sum), "reject_in_summary": bool(rej_sum),
        "reject_in_summary_matched": rej_sum,
        "reject_in_links_only": bool(rej_links) and not rej_sum,
        "classification": cls,
        # The selection rule. An item whose search returns no displacing CLAIM
        # cannot be displaced, and including it spends an item on a foregone
        # null; an item whose only reject match is an incidental substring in a
        # link title is that same foregone null wearing a flag.
        "divergent": bool(rej_sum),
    }


# --------------------------------------------------------------------------- #
# the searcher
# --------------------------------------------------------------------------- #

SEARCHER_PACKET = (
    "QUERY: {QUERY}\n\n"
    "Execute exactly this query once and report the results.\n"
)


@dataclass
class SearchResult:
    """One execution of one query through the Stage 0B search mechanism."""
    requested_query: str
    realized_query: str | None            # tool_use.input.query, byte-compared
    query_faithful: bool | None           # realized == requested
    executed: bool                        # a WebSearch tool_result came back
    search_requests: int | None           # authoritative telemetry
    block: ExposureBlock | None
    dispatch: Dispatch
    failure: str | None                   # a Stage 0B failure class, or None

    def to_json(self) -> dict:
        d = asdict(self)
        return d


def execute_search(query: str, timeout: int = 600) -> SearchResult:
    """Run one query through the ONE Stage 0B search mechanism.

    Arms C and D both call this function, with the same agent, the same model,
    the same tool grant and the same packet. The only thing that differs between
    them is the string in `query` -- which is the whole point of the C/D
    contrast, and is enforced by there being no other parameter to differ in.
    """
    packet = SEARCHER_PACKET.replace("{QUERY}", query)
    d = dispatch(SEARCHER_AGENT, packet, allowed_tools=["WebSearch"], timeout=timeout)

    searches = [c for c in d.tool_calls if c.get("name") == "WebSearch"]
    realized = None
    if searches:
        realized = (searches[0].get("input") or {}).get("query")
    faithful = (realized == query) if realized is not None else None

    block = None
    if d.tool_results:
        block = parse_exposure_block(d.tool_results[0])

    failure = None
    if d.returncode != 0 or d.is_error or d.parse_error:
        failure = "HARNESS_FAILURE"
    elif not searches:
        failure = "SEARCH_REALIZATION_FAILURE"       # the searcher never called WebSearch
    elif not d.tool_results:
        failure = "SEARCH_REALIZATION_FAILURE"       # called, but nothing came back
    elif block is None or not block.parse_ok:
        failure = "INJECTION_FAILURE"                # nothing parsable to inject
    elif faithful is False:
        failure = "QUERY_FIDELITY_FAILURE"           # the searcher reworded the query
    elif len(searches) > 1:
        failure = "SEARCH_REALIZATION_FAILURE"       # more than one search: not one dose

    return SearchResult(
        requested_query=query, realized_query=realized, query_faithful=faithful,
        executed=bool(d.tool_results), search_requests=d.web_search_requests,
        block=block, dispatch=d, failure=failure,
    )
