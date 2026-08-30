"""Stage 0A-M solver-agent symmetry regression checks.

These tests are non-dispatch. They exist because the shared solver-web and
solver-closed agents carried different epistemic instructions even though the
Stage 0A-M specification intended the arms to differ only by retrieval access.
"""
from __future__ import annotations

import hashlib
import json
import pathlib

import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
CLOSED_AGENT = REPO / ".claude" / "agents" / "stage0am-solver-closed.md"
WEB_AGENT = REPO / ".claude" / "agents" / "stage0am-solver-web.md"
RECORD = json.loads(
    (REPO / "experiments" / "exp004_stage0am" / "agent_symmetry.candidate.json").read_text()
)
CLOSED_PACKET = REPO / "experiments" / "exp004_stage0am" / "packet_closed.template.md"
WEB_PACKET = REPO / "experiments" / "exp004_stage0am" / "packet_retrieval_enabled.template.md"


def split_agent(path: pathlib.Path):
    text = path.read_text()
    assert text.startswith("---\n")
    _, frontmatter, body = text.split("---\n", 2)
    return text, yaml.safe_load(frontmatter), body


def sha16(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def strip_tools_block(text: str) -> str:
    lines = text.splitlines()
    out = []
    skipping = False
    for line in lines:
        if line.startswith("TOOLS:"):
            out.append("TOOLS: <ARM-SPECIFIC-EXTERNAL-INFORMATION-PERMISSION>")
            skipping = True
            continue
        if skipping:
            if line.startswith("them if ") or line.startswith("judge it ") or line.startswith("and you may "):
                continue
            if line == "":
                skipping = False
                out.append(line)
                continue
        out.append(line)
    return "\n".join(out)


def test_stage0am_agent_bodies_are_byte_identical():
    _, closed_meta, closed_body = split_agent(CLOSED_AGENT)
    _, web_meta, web_body = split_agent(WEB_AGENT)
    assert closed_body == web_body
    assert closed_meta["model"] == web_meta["model"] == "inherit"
    assert sha16(closed_body) == RECORD["common_body_sha256_16"]


def test_agent_tool_difference_is_exactly_retrieval():
    _, closed_meta, _ = split_agent(CLOSED_AGENT)
    _, web_meta, _ = split_agent(WEB_AGENT)
    closed_tools = {x.strip() for x in closed_meta["tools"].split(",")}
    web_tools = {x.strip() for x in web_meta["tools"].split(",")}
    assert closed_tools == {"TodoWrite"}
    assert web_tools == {"TodoWrite", "WebSearch", "WebFetch"}
    assert web_tools - closed_tools == {"WebSearch", "WebFetch"}
    assert closed_tools - web_tools == set()


def test_agent_file_fingerprints_match_record():
    closed_text, _, _ = split_agent(CLOSED_AGENT)
    web_text, _, _ = split_agent(WEB_AGENT)
    assert sha16(closed_text) == RECORD["agent_file_sha256_16"]["closed"]
    assert sha16(web_text) == RECORD["agent_file_sha256_16"]["retrieval_enabled"]


def test_shared_solver_agents_are_explicitly_superseded_for_stage0am():
    assert RECORD["supersedes_stage0am_agent_assignment"] == {
        "closed": ".claude/agents/solver-closed.md",
        "retrieval_enabled": ".claude/agents/solver-web.md",
    }
    assert RECORD["required_stage0am_agents"] == {
        "closed": ".claude/agents/stage0am-solver-closed.md",
        "retrieval_enabled": ".claude/agents/stage0am-solver-web.md",
    }


def test_packets_are_identical_after_tools_block_is_normalised():
    closed = CLOSED_PACKET.read_text()
    web = WEB_PACKET.read_text()
    assert strip_tools_block(closed) == strip_tools_block(web)
    assert sha16(closed) == RECORD["packet_sha256_16"]["closed"]
    assert sha16(web) == RECORD["packet_sha256_16"]["retrieval_enabled"]


def test_no_agent_body_contains_arm_specific_epistemic_interventions():
    _, _, body = split_agent(CLOSED_AGENT)
    lowered = body.lower()
    forbidden = [
        "check the premise",
        "judge source independence",
        "date your claims",
        "resolve conflicts",
        "your knowledge could be out of date",
        "report your actual epistemic state",
    ]
    assert all(term not in lowered for term in forbidden)
