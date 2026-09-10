"""Frozen-shape procedure packets for EXP005A.

This module builds messages only; it does not dispatch a model. The executor must
record the realized model/configuration and treat the context policy here as a
load-bearing construct.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Sequence

PROCEDURES = ("A0", "B3", "C3", "D3")

COMMON_SYSTEM = (
    "You are solving one item in a controlled reasoning evaluation. Do not use tools, "
    "web search, files, or external information. Follow the requested response format "
    "exactly. Do not mention the experiment."
)

DIRECT_INSTRUCTION = (
    "Solve the task carefully. You may give at most 6 short reasoning lines. "
    "End with exactly one line `FINAL: <answer>`."
)

SELF_CRITIQUE_INSTRUCTION = (
    "Review your immediately previous solution for a concrete reasoning or arithmetic error. "
    "Do not change the answer in this turn. Give at most 3 short findings, then end with "
    "`REVIEW: OK` if no specific error is found or `REVIEW: FIX` if one is found."
)

SELF_REPAIR_INSTRUCTION = (
    "Now solve the original task again using your review. Do not preserve the previous answer "
    "merely for consistency. Give at most 6 short reasoning lines and end with exactly one "
    "line `FINAL: <answer>`."
)

VERIFIER_SYSTEM = (
    "You are an independent verifier in a controlled reasoning evaluation. You did not produce "
    "the candidate answer. Do not use tools, web search, files, or external information. "
    "Independently solve the task before judging the candidate."
)

VERIFIER_INSTRUCTION = (
    "Independently solve the TASK, then evaluate CANDIDATE FINAL. Do not assume the candidate "
    "is correct. Give at most 4 short verification lines. End with `VERIFY: OK` if the candidate "
    "is correct, otherwise `VERIFY: FIX`, followed by one line `PROPOSED: <answer>`."
)

INDEPENDENT_REPAIR_SYSTEM = (
    "You are the repairer in a controlled reasoning evaluation. Do not use tools, web search, "
    "files, or external information. Treat the verifier report as advice, not ground truth; "
    "solve the task yourself before giving the final answer."
)

INDEPENDENT_REPAIR_INSTRUCTION = (
    "Using the TASK, CANDIDATE FINAL and VERIFIER REPORT below, produce the best answer. "
    "The verifier may be wrong. Give at most 6 short reasoning lines and end with exactly one "
    "line `FINAL: <answer>`."
)


@dataclass(frozen=True)
class DispatchSpec:
    step: str
    context_policy: str
    system: str
    user: str

    def fingerprint(self) -> str:
        payload = json.dumps({"step": self.step, "context_policy": self.context_policy,
                              "system": self.system, "user": self.user},
                             sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode()).hexdigest()[:16]


def a0(task_prompt: str) -> list[DispatchSpec]:
    return [DispatchSpec("direct", "fresh", COMMON_SYSTEM,
                         f"TASK:\n{task_prompt}\n\n{DIRECT_INSTRUCTION}")]


def b3(task_prompt: str) -> list[DispatchSpec]:
    spec = DispatchSpec("direct", "fresh", COMMON_SYSTEM,
                        f"TASK:\n{task_prompt}\n\n{DIRECT_INSTRUCTION}")
    return [spec, spec, spec]


def c3_initial(task_prompt: str) -> DispatchSpec:
    return a0(task_prompt)[0]


def c3_critique() -> DispatchSpec:
    return DispatchSpec("self_critique", "continue", COMMON_SYSTEM, SELF_CRITIQUE_INSTRUCTION)


def c3_repair() -> DispatchSpec:
    return DispatchSpec("self_repair", "continue", COMMON_SYSTEM, SELF_REPAIR_INSTRUCTION)


def d3_initial(task_prompt: str) -> DispatchSpec:
    return a0(task_prompt)[0]


def d3_verifier(task_prompt: str, candidate_final: str) -> DispatchSpec:
    return DispatchSpec(
        "independent_verify", "fresh", VERIFIER_SYSTEM,
        f"TASK:\n{task_prompt}\n\nCANDIDATE FINAL:\n{candidate_final}\n\n{VERIFIER_INSTRUCTION}",
    )


def d3_repair(task_prompt: str, candidate_final: str, verifier_report: str) -> DispatchSpec:
    return DispatchSpec(
        "independent_repair", "fresh", INDEPENDENT_REPAIR_SYSTEM,
        f"TASK:\n{task_prompt}\n\nCANDIDATE FINAL:\n{candidate_final}\n\n"
        f"VERIFIER REPORT:\n{verifier_report}\n\n{INDEPENDENT_REPAIR_INSTRUCTION}",
    )


def majority_vote(final_answers: Sequence[str | None]) -> str | None:
    """Deterministic B3 aggregation: plurality/majority, first-sample tie break."""
    if len(final_answers) != 3:
        raise ValueError("B3 requires exactly three samples")
    vals = [a.strip().casefold() if a is not None else None for a in final_answers]
    nonmissing = [v for v in vals if v is not None]
    if not nonmissing:
        return None
    counts = {v: nonmissing.count(v) for v in set(nonmissing)}
    best = max(counts.values())
    winners = {v for v, n in counts.items() if n == best}
    for original, norm in zip(final_answers, vals):
        if norm in winners:
            return original.strip() if original is not None else None
    raise AssertionError("unreachable")


def static_fingerprints() -> dict[str, str]:
    bodies = {
        "common_system": COMMON_SYSTEM,
        "direct_instruction": DIRECT_INSTRUCTION,
        "self_critique_instruction": SELF_CRITIQUE_INSTRUCTION,
        "self_repair_instruction": SELF_REPAIR_INSTRUCTION,
        "verifier_system": VERIFIER_SYSTEM,
        "verifier_instruction": VERIFIER_INSTRUCTION,
        "independent_repair_system": INDEPENDENT_REPAIR_SYSTEM,
        "independent_repair_instruction": INDEPENDENT_REPAIR_INSTRUCTION,
    }
    return {k: hashlib.sha256(v.encode()).hexdigest()[:16] for k, v in bodies.items()}
