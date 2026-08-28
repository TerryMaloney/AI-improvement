"""Loading question batteries and the quarantined answer key.

The two are loaded by different functions on purpose. `load_battery()` is safe
to call anywhere. `load_answers()` is called by exactly one module
(`lab.grading`) and by the refresh check — never by anything that builds a
prompt. Keeping the import graph honest is most of what makes the quarantine
real rather than aspirational.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from lab.labels import validate as validate_labels

REPO_ROOT = Path(__file__).resolve().parent.parent
BATTERY_DIR = REPO_ROOT / "batteries"
ANSWERS_PATH = BATTERY_DIR / "answers.yaml"

# Ground-truth statuses that may be used for automatic scoring. Anything else
# is reported as ungraded rather than guessed at. See answers.yaml's header for
# why this refusal exists.
SCORABLE_STATUSES = {"verified", "rubric_only"}


@dataclass
class Question:
    id: str
    text: str
    battery_id: str
    category: str = ""
    expected_claim_type: str | None = None
    probes: list[str] = field(default_factory=list)
    why: str = ""
    correct_handling: str = ""
    trap: bool = False
    entity_key: str | None = None
    grading: dict = field(default_factory=lambda: {"method": "judge"})
    task_labels: dict[str, str] | None = None
    """The six task axes (lab/labels.py), or None for a battery authored before
    they existed. `None` means UNLABELLED, never a default label set: an item
    silently defaulted would be assigned to the wrong diagnostic cell while
    looking deliberate. Batteries that declare `requires_task_labels: true`
    reject unlabelled items at load."""

    @property
    def grading_method(self) -> str:
        return self.grading.get("method", "judge")

    @property
    def labelled(self) -> bool:
        return self.task_labels is not None


@dataclass
class Battery:
    id: str
    description: str
    asked_as_of: str
    questions: list[Question]
    path: Path | None = None
    requires_task_labels: bool = False

    def by_id(self, qid: str) -> Question:
        for q in self.questions:
            if q.id == qid:
                return q
        raise KeyError(f"no question {qid!r} in battery {self.id!r}")


def load_battery(name_or_path: str | Path) -> Battery:
    path = Path(name_or_path)
    if not path.exists():
        path = BATTERY_DIR / f"{name_or_path}.yaml"
    raw = yaml.safe_load(path.read_text())
    # Opt-in rather than global: `factual` and `abstract` predate the task axes
    # and are frozen as regression batteries, so requiring labels everywhere
    # would mean editing frozen material to satisfy new instrumentation.
    requires_labels = bool(raw.get("requires_task_labels", False))
    questions = [
        Question(
            id=q["id"],
            text=q["text"],
            battery_id=raw["id"],
            category=q.get("category", ""),
            expected_claim_type=q.get("expected_claim_type"),
            probes=q.get("probes", []) or [],
            why=(q.get("why") or "").strip(),
            correct_handling=(q.get("correct_handling") or "").strip(),
            trap=bool(q.get("trap", False)),
            entity_key=q.get("entity_key"),
            grading=q.get("grading") or {"method": "judge"},
            task_labels=(
                validate_labels(q.get("task_labels"), where=f"{raw['id']}/{q['id']}")
                if (requires_labels or q.get("task_labels"))
                else None
            ),
        )
        for q in raw["questions"]
    ]
    return Battery(
        id=raw["id"],
        description=(raw.get("description") or "").strip(),
        asked_as_of=str(raw.get("asked_as_of", "")),
        questions=questions,
        path=path,
        requires_task_labels=requires_labels,
    )


def load_batteries(names: list[str]) -> list[Battery]:
    return [load_battery(n) for n in names]


def load_answers(path: str | Path = ANSWERS_PATH) -> dict:
    """Load the quarantined answer key.

    Callers: lab.grading and lab.refresh only. If you find yourself importing
    this into anything that builds a model-facing prompt, stop — that is the
    leak this whole design is arranged to prevent.
    """
    return yaml.safe_load(Path(path).read_text())


def scorable(answer_entry: dict | None) -> bool:
    return bool(answer_entry) and answer_entry.get("status") in SCORABLE_STATUSES


def ground_truth_strings(answers: dict) -> list[str]:
    """Every string in the answer key that would constitute a leak if it
    appeared in a TRIAL PACKET. Used by tests/test_no_answer_leakage.py.

    This is the right set for checking packets, where "Dali Rajic" appearing at
    all is a leak. It is the WRONG set for auditing answers — see
    `leak_probe_strings` below.
    """
    out: list[str] = []

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                # Rubrics and provenance are about *conduct*, not the answer,
                # and some are legitimately echoed into judge packets. They are
                # never put in a solver packet, which the test checks directly.
                if k in {"judge_rubric", "notes", "source", "status", "bucket", "verified_as_of"}:
                    continue
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
        elif isinstance(node, str) and len(node.strip()) >= 4:
            out.append(node.strip())
        elif isinstance(node, (int, float)):
            out.append(str(node))

    walk(answers.get("answers", {}))
    return out


def leak_probe_strings(answers: dict, min_len: int = 40) -> list[str]:
    """Strings whose appearance in a SOLVER'S ANSWER would suggest the answer
    key was read, rather than the question answered.

    This is a much narrower set than `ground_truth_strings`, and the reason is
    a false-positive problem found by running the audit on real data:

        LEAK-SUSPECT: answer contains an answer-key string: 'Andy Burnham'
        LEAK-SUSPECT: answer contains an answer-key string: 'false premise'

    Both flags were on CORRECT answers. Of course they were — `accept` strings
    and `accept_trap_markers` are precisely what a right answer contains, so
    matching on them flags every success as a suspected cheat. An alarm that
    fires on the good case is worse than no alarm: it trains you to ignore it.

    What actually discriminates is long, distinctive prose that exists only in
    the answer-key document — the narrative `ground_truth` write-ups. A solver
    reproducing forty consecutive characters of those did not arrive there by
    reasoning. Short accept-strings are excluded because they cannot tell
    "leaked" from "got it right", which is the whole question.

    The structural sandbox (no filesystem tools) remains the real defence. This
    is a backstop, and a deliberately quiet one.
    """
    out: list[str] = []
    for entry in (answers.get("answers") or {}).values():
        if not isinstance(entry, dict):
            continue
        gt = entry.get("ground_truth")
        if isinstance(gt, str) and len(gt.strip()) >= min_len:
            out.append(" ".join(gt.split()))
    return out
