"""The freeze record must describe the files it claims to describe.

A hash recorded by hand drifts silently; this recomputes every hash from the
committed artifact so an edit to an agent, packet, schedule or grader after
freeze cannot keep its recorded fingerprint. Nothing here dispatches.
"""
from __future__ import annotations

import hashlib
import json
import pathlib

import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
REC = json.loads((REPO / "experiments" / "exp004_stage0am" / "freeze_record.json").read_text())
SYM = json.loads((REPO / "experiments" / "exp004_stage0am" / "agent_symmetry.candidate.json").read_text())
AG = REPO / ".claude" / "agents"
EX = REPO / "experiments" / "exp004_stage0am"


def sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def body(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_text().split("---\n", 2)[2].encode()).hexdigest()[:16]


def test_every_recorded_hash_recomputes_from_its_artifact():
    h = REC["hashes"]
    assert h["common_agent_body_sha256_16"] == body(AG / "stage0am-solver-closed.md") == body(AG / "stage0am-solver-web.md")
    assert h["closed_agent_file_sha256_16"] == sha(AG / "stage0am-solver-closed.md")
    assert h["retrieval_agent_file_sha256_16"] == sha(AG / "stage0am-solver-web.md")
    assert h["closed_packet_sha256_16"] == sha(EX / "packet_closed.template.md")
    assert h["retrieval_packet_sha256_16"] == sha(EX / "packet_retrieval_enabled.template.md")
    assert h["schedule_sha256_16"] == sha(EX / "schedule.json")
    from lab.stage0am_fingerprint import audit
    assert h["battery_fingerprint"] == audit()["battery_fingerprint_recomputed"]
    assert h["grader_sha256_16"] == sha(REPO / "lab" / "anchored_grading.py")


def test_freeze_record_and_symmetry_record_agree():
    assert REC["hashes"]["common_agent_body_sha256_16"] == SYM["common_body_sha256_16"]
    assert REC["hashes"]["closed_agent_file_sha256_16"] == SYM["agent_file_sha256_16"]["closed"]
    assert REC["hashes"]["retrieval_agent_file_sha256_16"] == SYM["agent_file_sha256_16"]["retrieval_enabled"]


def test_agent_metadata_carries_no_arm_label():
    """The body is identical; the description must be too, or the frontmatter
    itself becomes an arm-specific instruction if it is ever rendered."""
    metas = []
    for f in ("stage0am-solver-closed.md", "stage0am-solver-web.md"):
        fm = yaml.safe_load((AG / f).read_text().split("---\n", 2)[1])
        metas.append(fm)
        assert fm["model"] == "inherit"
        for word in ("closed arm", "retrieval-enabled arm", "closed-book", "search arm"):
            assert word not in fm["description"].lower()
    assert metas[0]["description"] == metas[1]["description"]


def test_no_stage0am_agent_is_shadowed_at_user_scope():
    user_agents = pathlib.Path.home() / ".claude" / "agents"
    if not user_agents.exists():
        return
    names = {p.name for p in user_agents.glob("*.md")}
    assert not names & {"stage0am-solver-closed.md", "stage0am-solver-web.md"}


def test_record_asserts_zero_production_exposure():
    assert REC["production_dispatches"] == 0
    assert REC["treatment_exposure"] == "NONE"
    assert REC["runtime_validation"]["status"] == "BLOCKED" or REC["runtime_validation"].get("all_gates_passed") is True
