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
import random
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path

import yaml

from epistemic.registry import EntityRegistry, seed_registry
from epistemic.router import Route
from lab.battery import Battery, Question, load_batteries
from lab.placebo import build as build_placebo
from lab.routing import ROUTE_MODES, ROUTED, route_for
from lab.store import Store, TrialRow
from lab.treatments import build_a_only

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


# What block, if any, is injected above the question. `inject_directive` is
# retained so that exp001 and exp002 configurations still load unchanged; when
# `block` is not given it is derived from that flag.
BLOCK_NONE, BLOCK_PLACEBO, BLOCK_A_ONLY, BLOCK_DIRECTIVE = (
    "none", "placebo", "a_only", "directive",
)
BLOCK_KINDS = (BLOCK_NONE, BLOCK_PLACEBO, BLOCK_A_ONLY, BLOCK_DIRECTIVE)

# Every dispatch is classified before it is generated, and the class is stored
# with the trial. See docs/EXP003A_DECISION_PACKET.md §7: screening and
# qualification dispatches must never enter a primary analysis, and the rule is
# enforced in the data model rather than remembered.
DISPATCH_CLASSES = (
    "instrument_qualification",
    "screen",
    "retrieval_qualification",
    "treatment_validation",
    "solver_experiment",
)
PRIMARY_DISPATCH_CLASS = "solver_experiment"


@dataclass
class Condition:
    name: str
    agent: str
    inject_directive: bool = False
    allow_search: bool = False
    block: str | None = None
    """Which block is injected: none / placebo / a_only / directive. Defaults to
    directive-or-none from `inject_directive` so older configs load unchanged."""
    route_mode: str = ROUTED
    """`routed` uses the classifier's own claim type — the deployed behaviour, and
    the arm comparable to exp001/exp002. `intended` uses the item's declared type:
    what the router would have produced had it classified correctly. The two are
    byte-identical on any item where the classifier already agrees."""
    dispatch_class: str = PRIMARY_DISPATCH_CLASS
    protocol: str | None = None
    """Names a multi-dispatch protocol (`selfcheck`, `independent`) whose later
    dispatches the orchestrator runs from lab/treatments.py. `prepare()` emits the
    FIRST dispatch's prompt; the trial still counts as one trial and as two or
    three dispatches, which is why cost reads `DISPATCH_COUNT` and not the trial
    table."""
    description: str = ""
    flat_budget_override: int | None = None
    """Replace the route-derived search budget with a fixed number, while
    keeping the directive otherwise intact.

    This exists for exactly one purpose: exp001 could not separate "the
    directive is unhelpful" from "the directive's budget policy starved the
    condition", because `verified` received a route-derived budget (2 on most
    questions, 0 on deterministic) while its control `search_only` received a
    flat 3 — and `verified` then made FEWER observed tool calls, 30 against 39,
    while scoring lower. Overriding the budget alone isolates the two."""

    def __post_init__(self) -> None:
        if self.block is None:
            self.block = BLOCK_DIRECTIVE if self.inject_directive else BLOCK_NONE
        if self.block not in BLOCK_KINDS:
            raise ValueError(f"{self.name}: unknown block {self.block!r}; expected {BLOCK_KINDS}")
        if self.route_mode not in ROUTE_MODES:
            raise ValueError(f"{self.name}: unknown route_mode {self.route_mode!r}")
        if self.dispatch_class not in DISPATCH_CLASSES:
            raise ValueError(
                f"{self.name}: unknown dispatch_class {self.dispatch_class!r}; expected "
                f"{DISPATCH_CLASSES}"
            )
        # Keep the legacy flag consistent with the block so nothing downstream
        # that still reads it can disagree with what was actually injected.
        self.inject_directive = self.block == BLOCK_DIRECTIVE

    @classmethod
    def from_dict(cls, d: dict) -> "Condition":
        override = d.get("flat_budget_override")
        return cls(
            name=d["name"],
            agent=d["agent"],
            inject_directive=bool(d.get("inject_directive", False)),
            allow_search=bool(d.get("allow_search", False)),
            block=d.get("block"),
            route_mode=d.get("route_mode", ROUTED),
            dispatch_class=d.get("dispatch_class", PRIMARY_DISPATCH_CLASS),
            protocol=d.get("protocol"),
            description=(d.get("description") or "").strip(),
            flat_budget_override=int(override) if override is not None else None,
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
    dispatch_seed: int | None = None
    """Seed for the dispatch ORDER. See `prepare()` — this randomises the order
    in which trials are sent, never which treatment an item receives."""
    repeats_by_cell: dict = None  # type: ignore[assignment]
    """Replicates per cell. Plan §6 sets k=5 for L/R/D and k=3 for U/N/C, and a
    single global `repeats` cannot express that — an earlier version of this
    config silently produced 500 trials instead of 388 because of it. A cell
    named here overrides `repeats`; anything unnamed uses `repeats`."""
    exclude_items: dict = None  # type: ignore[assignment]
    """Item id -> reason. Exclusions are pre-registration decisions, so they are
    declared in the configuration with their reason rather than inferred at
    preparation time from whatever artefact happens to be on disk."""
    use_item_conditions: bool = False
    """When true, each item runs the conditions its own specification declares,
    looked up by name in this config's condition registry. Cells differ in their
    condition sets, so a single flat list cannot express the design."""
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
            dispatch_seed=(None if raw.get("dispatch_seed") is None
                           else int(raw["dispatch_seed"])),
            use_item_conditions=bool(raw.get("use_item_conditions", False)),
            repeats_by_cell=dict(raw.get("repeats_by_cell") or {}),
            exclude_items=dict(raw.get("exclude_items") or {}),
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


def _block_text(question: Question, condition: Condition, rt: Route) -> str | None:
    """The guidance block for this condition, or None when there is none.

    The header and framing around the block are IDENTICAL across every block
    kind, so a solver cannot tell a placebo from a directive by its wrapper. The
    placebo and `A_only` are generated against `rt`, so a condition declared with
    `route_mode: intended` gets a placebo matched to the INTENDED block's length
    and shape — which is the whole point of having two placebos in cell R.
    """
    if condition.block == BLOCK_NONE:
        return None
    if condition.block == BLOCK_PLACEBO:
        return build_placebo(rt.prompt_block(), question.text)
    if condition.block == BLOCK_A_ONLY:
        return build_a_only(rt, question.text)
    # A flat-budget override changes the number in the directive's budget line
    # and NOTHING else — same claim type, same handling text, same freshness
    # warnings, same routing caveats.
    if condition.flat_budget_override is not None:
        rt = replace(rt, search_budget=condition.flat_budget_override)
    return rt.prompt_block()


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

    block_text = _block_text(question, condition, rt)
    if block_text is not None:
        parts += [
            "--------------------------------------------------------------------------",
            "HANDLING GUIDANCE FOR THIS QUESTION",
            "--------------------------------------------------------------------------",
            block_text,
            "",
        ]

    parts += [QUESTION_BLOCK.format(question=question.text), "", "Return only the JSON object."]
    return "\n".join(parts)


def prepare(config: ExperimentConfig, registry: EntityRegistry | None = None) -> dict:
    """Generate every trial packet for an experiment.

    Writes `runs/<exp>/manifest.json` (all trials with prompts inline, so an
    orchestrator can read one file instead of N) plus one packet file per trial
    under `runs/<exp>/packets/` for human inspection and diffing.

    ## What is randomised, and what is not

    **Randomised: the ORDER in which trials are dispatched.** One shuffle, from
    `config.dispatch_seed`, applied once to the full list. This exists because the
    design now contains paired within-item contrasts (routed against intended),
    and dispatching arm-by-arm would let any drift over the run — a model version
    change, a capacity event — land unevenly across the pair and masquerade as an
    effect.

    **NOT randomised: treatment assignment.** Every item receives every condition
    its specification declares. There is no sampling, no allocation, and nothing
    to allocate: this is a full within-item factorial, so "randomised assignment"
    has no referent here. Conflating the two would be a real error — the seed
    protects against time-correlated drift, and provides no protection whatever
    against confounding, because there is no assignment step to confound.

    The order is reproducible from the frozen configuration: same seed, same
    battery, same conditions gives byte-identical ordering, which `preflight`
    verifies rather than assumes.
    """
    from lab.treatments import dispatch_count

    registry = registry if registry is not None else seed_registry()
    batteries: list[Battery] = load_batteries(config.batteries)
    asked_on = date.fromisoformat(config.asked_as_of) if config.asked_as_of else date.today()
    by_name = {c.name: c for c in config.conditions}

    run_dir = config.run_dir()
    packets_dir = run_dir / "packets"
    packets_dir.mkdir(parents=True, exist_ok=True)
    for sub in ("answers", "grades", "judge_packets"):
        (run_dir / sub).mkdir(parents=True, exist_ok=True)

    rows: list[TrialRow] = []
    manifest_trials: list[dict] = []

    excluded = dict(config.exclude_items or {})
    for battery in batteries:
        for q in battery.questions:
            if q.id in excluded:
                continue
            reps = (config.repeats_by_cell or {}).get(q.cell, config.repeats)
            if config.use_item_conditions:
                names = (q.spec or {}).get("conditions")
                if not names:
                    raise ValueError(
                        f"{q.id}: use_item_conditions is set but the item declares none. "
                        f"An item with no declared conditions would silently contribute "
                        f"zero trials."
                    )
                missing = [n for n in names if n not in by_name]
                if missing:
                    raise ValueError(
                        f"{q.id}: declares conditions {missing} that this experiment does "
                        f"not define. Refusing rather than dropping them."
                    )
                conditions = [by_name[n] for n in names]
            else:
                conditions = list(config.conditions)

            for condition in conditions:
                rt = route_for(
                    q.text, q.expected_claim_type, condition.route_mode, asked_on, registry
                )
                for model in config.models:
                    for rep in range(1, reps + 1):
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
                                dispatch_class=condition.dispatch_class,
                                route_mode=condition.route_mode,
                                block_kind=condition.block,
                                intended_claim_type=q.expected_claim_type,
                            )
                        )
                        manifest_trials.append(
                            {
                                "trial_id": trial_id,
                                "question_id": q.id,
                                "cell": q.cell,
                                "battery": battery.id,
                                "condition": condition.name,
                                "block": condition.block,
                                "route_mode": condition.route_mode,
                                "routed_claim_type": rt.claim_type.value,
                                "intended_claim_type": q.expected_claim_type,
                                "dispatch_class": condition.dispatch_class,
                                "protocol": condition.protocol,
                                "dispatches": dispatch_count(condition.name),
                                "agent": condition.agent,
                                "model": model,
                                "repeat": rep,
                                "prompt": prompt,
                            }
                        )

    # Order the dispatch list once, deterministically. Sorted first so the input
    # to the shuffle does not depend on dict or filesystem iteration order.
    manifest_trials.sort(key=lambda t: t["trial_id"])
    if config.dispatch_seed is not None:
        random.Random(config.dispatch_seed).shuffle(manifest_trials)
    for position, trial in enumerate(manifest_trials, start=1):
        trial["dispatch_position"] = position

    store = Store(run_dir / "results.db")
    store.save_experiment(config.id, config.raw or {})
    store.save_trials(rows)
    store.close()

    classes = sorted({t["dispatch_class"] for t in manifest_trials})
    manifest = {
        "experiment": config.id,
        "title": config.title,
        "hypothesis": config.hypothesis,
        "asked_as_of": asked_on.isoformat(),
        "answers_dir": _display_path(run_dir / "answers"),
        "how_to_run": (
            "Dispatch in `dispatch_position` order. For each trial: spawn the named agent "
            "with the named model override and pass `prompt` verbatim as the agent's task. "
            "Write the JSON object the agent returns to <answers_dir>/<trial_id>.json. "
            "A trial with a `protocol` needs its follow-up dispatches from lab/treatments.py "
            "before it is complete. Then run `python -m lab ingest <exp>`."
        ),
        "dispatch_seed": config.dispatch_seed,
        "randomisation": (
            "The dispatch ORDER is shuffled once from `dispatch_seed`. Treatment "
            "assignment is NOT randomised and could not be: every item receives every "
            "condition it declares, so the design is a full within-item factorial with no "
            "allocation step. The seed guards against time-correlated drift across paired "
            "arms; it provides no protection against confounding."
        ),
        "dispatch_classes": classes,
        "excluded_items": excluded,
        "repeats_by_cell": dict(config.repeats_by_cell or {}),
        "trial_count": len(manifest_trials),
        "dispatch_count": sum(t["dispatches"] for t in manifest_trials),
        "by_cell": {
            cell: sum(1 for t in manifest_trials if t["cell"] == cell)
            for cell in sorted({t["cell"] for t in manifest_trials if t["cell"]})
        },
        "by_route_mode": {
            mode: sum(1 for t in manifest_trials if t["route_mode"] == mode)
            for mode in sorted({t["route_mode"] for t in manifest_trials})
        },
        "by_block": {
            block: sum(1 for t in manifest_trials if t["block"] == block)
            for block in sorted({t["block"] for t in manifest_trials})
        },
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
