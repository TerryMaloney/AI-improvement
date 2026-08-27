"""Trial packet generation — building the prompts that go to solver agents.

This is the experimental instrument, so the details matter more than they look:

* The response schema is IDENTICAL in every condition. An earlier draft asked
  solvers to self-report a claim type, which would have been a treatment in
  itself (asking "what kind of question is this?" prompts the reflection the
  epistemic layer is supposed to supply). Claim-type conduct is instead graded
  from the answer text by a judge that never sees which condition produced it.

* Only the `verified` condition gets the route-derived search budget. A
  search-enabled condition without the directive gets a flat default budget,
  because a budget tuned per claim type is *part of* the treatment — handing it
  to the control would leak the treatment into the control.

* Nothing here imports the answer key. `lab.battery.load_answers` is called by
  the grading path only.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml

from epistemic.registry import EntityRegistry, seed_registry
from epistemic.router import Route, route
from lab.battery import Battery, Question, load_batteries
from lab.store import Store, TrialRow

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPERIMENT_DIR = REPO_ROOT / "experiments"
RUNS_DIR = REPO_ROOT / "runs"


RESPONSE_SCHEMA = """{
  "answer": "<your full answer, as you would give it to the person who asked>",
  "confidence": "<high | medium | low>",
  "abstained": <true if you declined to give a substantive answer, else false>,
  "searches_used": <integer count of searches you actually ran; 0 if you have no tools>,
  "sources": ["<for each source you actually used: what it was and what it told you>"],
  "notes": "<anything about how you arrived at this; optional>"
}"""


COMMON_PREAMBLE = """You are answering ONE question as part of a controlled evaluation.

Answer it as well as you can. Then return your response as a single JSON object
matching this schema, and nothing else — no preamble, no markdown fence, no
commentary outside the JSON:

{schema}

Be honest in the JSON. `searches_used` and `sources` are audited against what
you actually did; inflating them or reporting sources you did not consult
corrupts the measurement this evaluation exists to produce."""


CLOSED_BLOCK = """TOOLS: you have none. No search, no browsing, no files. Answer from what you
already know.

If you do not know, or your knowledge may be out of date, say that in the
answer rather than producing a plausible-sounding guess. A clearly-flagged "I
am not confident, and here is why" is a better answer here than a confident
wrong one — but refusing to engage with a question you could reasonably address
is also a failure. Set `searches_used` to 0."""


WEB_BLOCK = """TOOLS: you have WebSearch and WebFetch. You have no other tools — no file
access, no code execution."""

# Only the no-directive conditions state the budget here; when a directive is
# injected it carries the route-derived budget itself, and saying it twice in
# one prompt is noise that differs between conditions for no reason.
WEB_BUDGET_BLOCK = """SEARCH BUDGET: {budget}. Treat it as a ceiling, not a target. Spend nothing on
a question you can already answer well; spend up to the ceiling on one you
cannot. Report the true count in `searches_used`."""


QUESTION_BLOCK = """--------------------------------------------------------------------------
THE QUESTION
--------------------------------------------------------------------------
{question}
--------------------------------------------------------------------------"""


@dataclass
class Condition:
    name: str
    agent: str
    inject_directive: bool = False
    allow_search: bool = False
    description: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "Condition":
        return cls(
            name=d["name"],
            agent=d["agent"],
            inject_directive=bool(d.get("inject_directive", False)),
            allow_search=bool(d.get("allow_search", False)),
            description=(d.get("description") or "").strip(),
        )


@dataclass
class ExperimentConfig:
    id: str
    title: str
    hypothesis: str
    batteries: list[str]
    conditions: list[Condition]
    models: list[str]
    repeats: int = 1
    asked_as_of: str | None = None
    default_search_budget: int = 3
    notes: str = ""
    raw: dict = None  # type: ignore[assignment]

    @classmethod
    def load(cls, name_or_path: str | Path) -> "ExperimentConfig":
        path = Path(name_or_path)
        if not path.exists():
            matches = sorted(EXPERIMENT_DIR.glob(f"{name_or_path}*.yaml"))
            if not matches:
                raise FileNotFoundError(f"no experiment config matching {name_or_path!r}")
            path = matches[0]
        raw = yaml.safe_load(path.read_text())
        return cls(
            id=raw["id"],
            title=raw.get("title", raw["id"]),
            hypothesis=raw.get("hypothesis", ""),
            batteries=raw["batteries"],
            conditions=[Condition.from_dict(c) for c in raw["conditions"]],
            models=raw["models"],
            repeats=int(raw.get("repeats", 1)),
            asked_as_of=raw.get("asked_as_of"),
            default_search_budget=int(raw.get("default_search_budget", 3)),
            notes=(raw.get("notes") or "").strip(),
            raw=raw,
        )

    def run_dir(self) -> Path:
        return RUNS_DIR / self.id


def _display_path(path: Path) -> str:
    """Repo-relative when it can be, absolute otherwise (tests run in tmpdirs)."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def build_prompt(question: Question, condition: Condition, rt: Route, default_budget: int) -> str:
    """Assemble the exact text a solver agent receives."""
    parts = [COMMON_PREAMBLE.format(schema=RESPONSE_SCHEMA), ""]

    if condition.allow_search:
        parts += [WEB_BLOCK, ""]
        if not condition.inject_directive:
            b = default_budget
            parts += [WEB_BUDGET_BLOCK.format(budget=f"{b} search" + ("" if b == 1 else "es")), ""]
    else:
        parts += [CLOSED_BLOCK, ""]

    if condition.inject_directive:
        parts += [
            "--------------------------------------------------------------------------",
            "HANDLING GUIDANCE FOR THIS QUESTION",
            "--------------------------------------------------------------------------",
            rt.prompt_block(),
            "",
        ]

    parts += [QUESTION_BLOCK.format(question=question.text), "", "Return only the JSON object."]
    return "\n".join(parts)


def prepare(config: ExperimentConfig, registry: EntityRegistry | None = None) -> dict:
    """Generate every trial packet for an experiment.

    Writes `runs/<exp>/manifest.json` (all trials with prompts inline, so an
    orchestrator can read one file instead of N) plus one packet file per trial
    under `runs/<exp>/packets/` for human inspection and diffing.
    """
    registry = registry if registry is not None else seed_registry()
    batteries: list[Battery] = load_batteries(config.batteries)
    asked_on = date.fromisoformat(config.asked_as_of) if config.asked_as_of else date.today()

    run_dir = config.run_dir()
    packets_dir = run_dir / "packets"
    packets_dir.mkdir(parents=True, exist_ok=True)
    for sub in ("answers", "grades", "judge_packets"):
        (run_dir / sub).mkdir(parents=True, exist_ok=True)

    rows: list[TrialRow] = []
    manifest_trials: list[dict] = []

    for battery in batteries:
        for q in battery.questions:
            rt = route(q.text, asked_on=asked_on, registry=registry)
            for condition in config.conditions:
                for model in config.models:
                    for rep in range(1, config.repeats + 1):
                        trial_id = f"{config.id}-{q.id}-{condition.name}-{model}-r{rep}"
                        prompt = build_prompt(q, condition, rt, config.default_search_budget)
                        (packets_dir / f"{trial_id}.md").write_text(prompt)
                        rows.append(
                            TrialRow(
                                trial_id=trial_id,
                                experiment_id=config.id,
                                question_id=q.id,
                                battery_id=battery.id,
                                condition=condition.name,
                                model=model,
                                repeat=rep,
                                agent=condition.agent,
                                routed_claim_type=rt.claim_type.value,
                                route_json=json.dumps(rt.as_dict(), default=str),
                                prompt=prompt,
                            )
                        )
                        manifest_trials.append(
                            {
                                "trial_id": trial_id,
                                "question_id": q.id,
                                "battery": battery.id,
                                "condition": condition.name,
                                "agent": condition.agent,
                                "model": model,
                                "repeat": rep,
                                "prompt": prompt,
                            }
                        )

    store = Store(run_dir / "results.db")
    store.save_experiment(config.id, config.raw or {})
    store.save_trials(rows)
    store.close()

    manifest = {
        "experiment": config.id,
        "title": config.title,
        "hypothesis": config.hypothesis,
        "asked_as_of": asked_on.isoformat(),
        "answers_dir": _display_path(run_dir / "answers"),
        "how_to_run": (
            "For each trial: spawn the named agent with the named model override and pass "
            "`prompt` verbatim as the agent's task. Write the JSON object the agent returns "
            "to <answers_dir>/<trial_id>.json. Then run `python -m lab ingest <exp>`."
        ),
        "trial_count": len(manifest_trials),
        "trials": manifest_trials,
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    return {
        "experiment": config.id,
        "trials": len(rows),
        "questions": sum(len(b.questions) for b in batteries),
        "conditions": [c.name for c in config.conditions],
        "models": config.models,
        "run_dir": str(run_dir),
    }
