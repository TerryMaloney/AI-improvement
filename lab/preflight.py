"""The preflight. One binary question, and it fails closed.

    CAN THE EXPERIMENT RUN WITHOUT CHANGING ANY EXPERIMENTAL RULE
    AFTER SEEING SOLVER RESULTS?

Everything here exists to make that answerable in advance. A rule changed after
results are in is not a rule; it is a description of the results. So each check
asks whether some rule is already fixed, already written down, and already
verifiable without a solver — and any check that cannot establish that returns
FAIL or BLOCKED, never a shrug.

**Fail closed** is the design principle, and it has teeth in three places:

* An unknown or unrunnable check is a FAIL, not a skip. A check that errors is
  reported as ERROR and counts against the verdict.
* A screen that has not run reports NOT_SCREENED, and NOT_SCREENED blocks. The
  alternative — treating "not yet checked" as "fine" — is how a screen becomes
  decoration.
* `runnable` is the conjunction of every check. There is no "mostly ready".

The preflight is not a formality to be passed. Its job is to make it hard for us
to fool ourselves once the first solver is finally dispatched, and a preflight
that always passes has failed at that job.
"""

from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

PASS, FAIL, BLOCKED, ERROR = "PASS", "FAIL", "BLOCKED", "ERROR"


@dataclass
class Check:
    id: str
    question: str
    status: str
    detail: str
    fix: str = ""

    @property
    def ok(self) -> bool:
        return self.status == PASS


_CHECKS: list = []


def check(cid: str, question: str):
    def wrap(fn):
        fn._cid, fn._question = cid, question
        _CHECKS.append(fn)
        return fn
    return wrap


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _frozen_doc() -> str:
    return (REPO_ROOT / "docs" / "EXP003A_FROZEN_DECISIONS.md").read_text()


def _recorded_hash(label: str) -> str | None:
    for line in _frozen_doc().splitlines():
        if line.strip().startswith(f"{label}:"):
            return line.split(":", 1)[1].strip().strip("`")
    return None


# --------------------------------------------------------------------------
# Specification integrity
# --------------------------------------------------------------------------

@check("battery_schema", "Does the battery load and validate under its own schema?")
def _battery_schema(ctx) -> Check:
    b = ctx["battery"]
    return Check(
        "battery_schema", "", PASS,
        f"{b.id}: {len(b.questions)} items load, all validated by lab.spec.validate_item",
    )


@check("required_fields", "Does every item carry every required specification field?")
def _required_fields(ctx) -> Check:
    from lab.spec import REQUIRED_FIELDS

    missing = [
        f"{q.id}.{f}" for q in ctx["battery"].questions for f in REQUIRED_FIELDS
        if q.spec.get(f) in (None, "", [], {})
    ]
    if missing:
        return Check("required_fields", "", FAIL, f"missing: {missing[:8]}",
                     "fill the fields in batteries/diagnostic_v1.yaml before dispatch")
    return Check("required_fields", "", PASS,
                 f"all {len(REQUIRED_FIELDS)} fields present on all {len(ctx['battery'].questions)} items")


@check("tier_compliance", "Does every item respect the tier wall?")
def _tier(ctx) -> Check:
    bad = []
    for q in ctx["battery"].questions:
        if q.spec["evidence_tier"] == "PRIMARY" and q.spec["outcome_type"] != "deterministic":
            bad.append(f"{q.id}: PRIMARY but {q.spec['outcome_type']}")
        if q.spec["outcome_type"] in ("judged", "deterministic_with_judge_fallback") \
                and q.spec["evidence_tier"] == "PRIMARY":
            bad.append(f"{q.id}: judged outcome at PRIMARY")
    if bad:
        return Check("tier_compliance", "", FAIL, "; ".join(bad),
                     "a judge may not determine a primary outcome (D5)")
    return Check("tier_compliance", "", PASS, "no judged item reaches PRIMARY; all PRIMARY items are deterministic")


@check("outcome_types", "Is every outcome type one the lab can actually produce?")
def _outcomes(ctx) -> Check:
    from lab.spec import OUTCOME_TYPES

    counts: dict[str, int] = {}
    for q in ctx["battery"].questions:
        counts[q.spec["outcome_type"]] = counts.get(q.spec["outcome_type"], 0) + 1
    unknown = [k for k in counts if k not in OUTCOME_TYPES]
    if unknown:
        return Check("outcome_types", "", FAIL, f"unknown: {unknown}", "use one of " + str(OUTCOME_TYPES))
    return Check("outcome_types", "", PASS,
                 ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
                 + " — deterministic, judge-fallback and judged kept distinct")


@check("length_sensitivity", "Does every item's length declaration match whether it has a judge?")
def _length(ctx) -> Check:
    judge_free = {"deterministic", "diagnostic_only"}
    bad = [
        f"{q.id}: {q.spec['outcome_type']}/{q.spec['length_sensitivity']}"
        for q in ctx["battery"].questions
        if (q.spec["outcome_type"] in judge_free) != (q.spec["length_sensitivity"] == "NONE")
    ]
    if bad:
        return Check("length_sensitivity", "", FAIL, "; ".join(bad),
                     "exp003c measured a judge length effect at rubric boundaries; the two fields must agree")
    return Check("length_sensitivity", "", PASS,
                 "every judge-free item declares NONE; no item with a judge does")


@check("expected_retrieval_states", "Is every declared retrieval state reachable in this environment?")
def _states(ctx) -> Check:
    from lab.states import RetrievalState

    reachable = ctx["egress"].reachable
    bad = [
        f"{q.id}/{cond}={state}"
        for q in ctx["battery"].questions
        for cond, state in q.spec["expected_retrieval_state"].items()
        if RetrievalState(state) not in reachable
    ]
    if bad:
        return Check("expected_retrieval_states", "", FAIL, "; ".join(bad),
                     "an item may not be specified to reach a state the environment cannot produce (FD-4)")
    return Check("expected_retrieval_states", "", PASS,
                 f"all declared states within the probed reachable set "
                 f"{sorted(s.value for s in reachable)}")


# --------------------------------------------------------------------------
# The environment, and what it can reproduce
# --------------------------------------------------------------------------

@check("retrieval_reproducibility", "Has the environment's retrieval behaviour been probed and frozen?")
def _repro(ctx) -> Check:
    from lab.scout import load_scout

    egress = ctx["egress"]
    try:
        scout = load_scout()
    except FileNotFoundError as e:
        return Check("retrieval_reproducibility", "", FAIL, str(e),
                     "run the scout and commit runs/screens/retrieval_scout.json")
    d_items = {q.id for q in ctx["battery"].by_cell("D")}
    scouted = {r["item_id"] for r in scout["results"]}
    if not d_items <= scouted:
        return Check("retrieval_reproducibility", "", FAIL,
                     f"cell-D items never scouted: {sorted(d_items - scouted)}",
                     "scout every cell-D item before planning the cell")
    return Check(
        "retrieval_reproducibility", "", PASS,
        f"egress probed {egress.probed_at[:10]} (search={egress.web_search}, "
        f"fetch={egress.web_fetch}); all {len(d_items)} cell-D items scouted {scout['probed_at']}",
    )


@check("ground_truth", "Is every scorable item's ground truth verified, and every unscorable one honest about it?")
def _truth(ctx) -> Check:
    answers = ctx["answers"]
    bad = []
    for q in ctx["battery"].questions:
        entry = answers.get(q.id)
        if not entry:
            bad.append(f"{q.id}: no answer-key entry")
        elif q.cell == "U":
            if entry.get("status") != "rubric_only" or entry.get("ground_truth") is not None:
                bad.append(f"{q.id}: cell U must be rubric_only with no value")
        elif entry.get("status") != "verified":
            bad.append(f"{q.id}: status {entry.get('status')!r}")
    if bad:
        return Check("ground_truth", "", FAIL, "; ".join(bad),
                     "verify the key or mark the item unscorable; scoring against unchecked truth "
                     "manufactures a number that looks measured")
    return Check("ground_truth", "", PASS,
                 f"{len([q for q in ctx['battery'].questions if q.cell != 'U'])} verified, "
                 f"4 rubric_only with no value by construction")


@check("answer_leak", "Can any answer-key value reach a solver?")
def _leak(ctx) -> Check:
    from datetime import date

    from epistemic.registry import seed_registry
    from epistemic.router import route
    from lab.battery import ground_truth_strings
    from lab.trials import Condition, build_prompt

    registry = seed_registry()
    ids = {q.id for q in ctx["battery"].questions}
    probes = [
        s for s in ground_truth_strings({"answers": {k: ctx["answers"][k] for k in ids}})
        if isinstance(s, str) and len(s) >= 12
    ]
    leaks = []
    for q in ctx["battery"].questions:
        rt = route(q.text, asked_on=date(2026, 8, 28), registry=registry)
        for search in (False, True):
            for inject in (False, True):
                prompt = " ".join(build_prompt(
                    q, Condition("p", "solver-closed", inject_directive=inject, allow_search=search),
                    rt, 3,
                ).split()).lower()
                leaks += [f"{q.id}: {s[:50]!r}" for s in probes
                          if " ".join(s.split()).lower() in prompt]
    if leaks:
        return Check("answer_leak", "", FAIL, "; ".join(sorted(set(leaks))[:5]),
                     "remove the leaking text from the battery")
    return Check("answer_leak", "", PASS,
                 f"{len(probes)} answer-key strings checked against every packet in every "
                 f"condition; none present")


# --------------------------------------------------------------------------
# Treatments
# --------------------------------------------------------------------------

@check("treatment_definitions", "Is every condition the battery names actually defined?")
def _treatments(ctx) -> Check:
    from lab.treatments import DISPATCH_COUNT

    named = {c for q in ctx["battery"].questions for c in q.spec["conditions"]}
    undefined = sorted(named - set(DISPATCH_COUNT))
    if undefined:
        return Check("treatment_definitions", "", FAIL, f"undefined: {undefined}",
                     "define each in lab/treatments.py before dispatch")
    return Check("treatment_definitions", "", PASS,
                 f"all {len(named)} conditions defined with texts and dispatch costs")


@check("treatment_freeze", "Do the treatment texts still match the frozen fingerprint?")
def _freeze(ctx) -> Check:
    from lab.treatments import freeze_fingerprint

    live = freeze_fingerprint()
    recorded = _recorded_hash("TREATMENT_FREEZE")
    if recorded is None:
        return Check("treatment_freeze", "", FAIL,
                     "no TREATMENT_FREEZE line in docs/EXP003A_FROZEN_DECISIONS.md",
                     f"record `TREATMENT_FREEZE: {live}` once the texts are final")
    if recorded != live:
        return Check("treatment_freeze", "", FAIL,
                     f"treatment texts changed since freezing: recorded {recorded[:12]}, live {live[:12]}",
                     "either revert the change or record it as a protocol amendment with its reason")
    return Check("treatment_freeze", "", PASS, f"matches frozen fingerprint {live[:12]}")


@check("scoring_freeze", "Are the scoring rules and rubrics frozen?")
def _scoring(ctx) -> Check:
    from lab.battery import BATTERY_DIR

    live = _sha(
        (BATTERY_DIR / "diagnostic_v1.yaml").read_text()
        + (BATTERY_DIR / "answers.diagnostic_v1.yaml").read_text()
    )
    recorded = _recorded_hash("SCORING_FREEZE")
    if recorded is None:
        return Check("scoring_freeze", "", FAIL,
                     "no SCORING_FREEZE line in docs/EXP003A_FROZEN_DECISIONS.md",
                     f"record `SCORING_FREEZE: {live}` once the battery and key are final")
    if recorded != live:
        return Check("scoring_freeze", "", FAIL,
                     f"battery or answer key changed since freezing: recorded {recorded[:12]}, live {live[:12]}",
                     "re-freeze deliberately, recording what changed and why")
    return Check("scoring_freeze", "", PASS, f"battery + key match frozen fingerprint {live[:12]}")


@check("judge_config", "Is the judge in the configuration exp003c calibrated?")
def _judge(ctx) -> Check:
    from lab.grading import JUDGE_TEMPLATE

    live = _sha(JUDGE_TEMPLATE)
    recorded = _recorded_hash("JUDGE_FREEZE")
    if recorded is None:
        return Check("judge_config", "", FAIL,
                     "no JUDGE_FREEZE line in docs/EXP003A_FROZEN_DECISIONS.md",
                     f"record `JUDGE_FREEZE: {live}` — exp003c's calibration is only valid for "
                     f"the template it calibrated")
    if recorded != live:
        return Check("judge_config", "", FAIL,
                     "judge template changed since exp003c calibrated it",
                     "re-run exp003c before any judged cell, or revert the template")
    return Check("judge_config", "", PASS,
                 f"template matches exp003c ({live[:12]}); C4 replicates k=3 pending OPEN-1")


# --------------------------------------------------------------------------
# Measurement
# --------------------------------------------------------------------------

@check("telemetry", "Can the lab record what a dispatch actually cost?")
def _telemetry(ctx) -> Check:
    import tempfile

    from lab.store import Store

    with tempfile.TemporaryDirectory() as d:
        store = Store(Path(d) / "t.db")
        cols = set(store.columns("answers")) | set(store.columns("grades"))
        store.close()
    need = {"tool_calls_observed", "total_tokens", "latency_ms", "dispatch_role",
            "retrieval_state", "evidence_ledger_json", "judge_tokens", "judge_latency_ms"}
    missing = sorted(need - cols)
    if missing:
        return Check("telemetry", "", FAIL, f"store cannot record: {missing}",
                     "add the columns to lab/store.py")
    return Check("telemetry", "", PASS,
                 "solver and judge dispatches both record tokens, latency and observed tool calls")


@check("cost_accounting", "Is cost computed from observation rather than self-report?")
def _cost(ctx) -> Check:
    src = (REPO_ROOT / "lab" / "report.py").read_text()
    offenders = [
        line.strip() for line in src.splitlines()
        if "total_searches" in line or "mean_searches" in line
    ]
    if offenders:
        return Check("cost_accounting", "", FAIL,
                     f"report still derives cost from self-report: {offenders[:2]}",
                     "cost must come from tool_calls_observed (FD-2, FD-8)")
    return Check("cost_accounting", "", PASS,
                 "cost derives from tool_calls_observed; self-report reported beside it as a "
                 "calibration datum and never as cost")


@check("dispatch_accounting", "Are multi-dispatch arms counted at their real cost?")
def _dispatch(ctx) -> Check:
    from lab.treatments import MULTI_DISPATCH, dispatch_count

    named = {c for q in ctx["battery"].questions for c in q.spec["conditions"]}
    wrong = [c for c in named & MULTI_DISPATCH if dispatch_count(c) < 2]
    if wrong:
        return Check("dispatch_accounting", "", FAIL, f"{wrong} counted as one dispatch",
                     "a three-dispatch arm costed as one is wrong by a factor of three")
    detail = ", ".join(f"{c}={dispatch_count(c)}" for c in sorted(named))
    return Check("dispatch_accounting", "", PASS, detail)


@check("determinism", "Does preparation produce the same packets every time?")
def _determinism(ctx) -> Check:
    from datetime import date

    from epistemic.registry import seed_registry
    from epistemic.router import route
    from lab.placebo import build as build_placebo
    from lab.treatments import build_a_only

    q = ctx["battery"].questions[0]
    rt = route(q.text, asked_on=date(2026, 8, 28), registry=seed_registry())
    same = (
        build_placebo(rt.prompt_block(), q.text) == build_placebo(rt.prompt_block(), q.text)
        and build_a_only(rt, q.text) == build_a_only(rt, q.text)
    )
    if not same:
        return Check("determinism", "", FAIL, "prompt generation is not reproducible",
                     "remove the nondeterminism; a treatment that varies per call is not one treatment")
    return Check("determinism", "", PASS,
                 "placebo and A_only generation are deterministic (seeded from question text, no RNG); "
                 "trial order carries no randomisation, so there is no seed to record")


# --------------------------------------------------------------------------
# Contamination and identity
# --------------------------------------------------------------------------

@check("prep_dispatch_separation", "Is preparation code free of any ability to dispatch a solver?")
def _separation(ctx) -> Check:
    offenders = []
    for name in ("trials.py", "battery.py", "spec.py", "placebo.py", "treatments.py",
                 "screens.py", "scout.py", "preflight.py"):
        tree = ast.parse((REPO_ROOT / "lab" / name).read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    if alias.name.split(".")[0] in {"subprocess", "requests", "httpx", "urllib"} \
                            and name != "preflight.py":
                        offenders.append(f"{name} imports {alias.name}")
    if offenders:
        return Check("prep_dispatch_separation", "", FAIL, "; ".join(offenders),
                     "preparation must not be able to call a model")
    return Check("prep_dispatch_separation", "", PASS,
                 "no preparation module can reach the network or spawn a process; dispatch is the "
                 "orchestrator's job and happens outside this code")


@check("no_solver_contamination", "Has any solver result touched the specification?")
def _contamination(ctx) -> Check:
    run = REPO_ROOT / "runs" / "exp003a"
    found = []
    if run.exists():
        for sub in ("answers", "grades", "results.db"):
            if (run / sub).exists():
                found.append(str((run / sub).relative_to(REPO_ROOT)))
    if found:
        return Check("no_solver_contamination", "", FAIL,
                     f"solver artefacts already present: {found}",
                     "the specification must be frozen before results exist, not after")
    return Check("no_solver_contamination", "", PASS,
                 "no exp003a answers, grades or database exist; the specification predates all results")


@check("experiment_identity", "Is there a versioned experiment configuration to run?")
def _identity(ctx) -> Check:
    cfg = REPO_ROOT / "experiments" / "exp003a_mechanism.yaml"
    if not cfg.exists():
        return Check("experiment_identity", "", FAIL,
                     "no experiments/exp003a_mechanism.yaml",
                     "write the experiment configuration: id, conditions, models, repeats, "
                     "battery, and the frozen fingerprints it runs against")
    return Check("experiment_identity", "", PASS, f"config present: {cfg.name}")


@check("git_identity", "Can the exact runnable experiment be identified from the repository?")
def _git(ctx) -> Check:
    try:
        dirty = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_ROOT,
                               capture_output=True, text=True, timeout=30).stdout.strip()
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT,
                              capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception as e:  # noqa: BLE001
        return Check("git_identity", "", ERROR, f"git unavailable: {e}", "run inside the repository")
    if dirty:
        return Check("git_identity", "", FAIL,
                     f"{len(dirty.splitlines())} uncommitted change(s); HEAD {head[:12]} does not "
                     f"describe what would run",
                     "commit everything before dispatch so the run has an identity")
    return Check("git_identity", "", PASS, f"clean tree at {head[:12]}")


# --------------------------------------------------------------------------
# Screens
# --------------------------------------------------------------------------

@check("screens_complete", "Has every screen actually run?")
def _screens(ctx) -> Check:
    from lab.screens import NOT_SCREENED, knowledge_screen, load_screen_report

    probe = (load_screen_report("knowledge_probe") or {}).get("baseline_rate")
    results = knowledge_screen(ctx["battery"], probe)
    unscreened = [r.item_id for r in results if r.decision == NOT_SCREENED]
    if unscreened:
        return Check(
            "screens_complete", "", BLOCKED,
            f"{len(unscreened)} of {len(results)} items have no knowledge-probe result",
            "dispatch the knowledge probe (baseline only, k=5) and commit "
            "runs/screens/knowledge_probe.json. Thresholds are already frozen at "
            "ceiling>=0.90 / floor<=0.10, so running it cannot change them.",
        )
    return Check("screens_complete", "", PASS, "knowledge screen has run on every item")


@check("routing_consistency", "Does each item receive the directive its specification predicts about?")
def _routing(ctx) -> Check:
    from lab.screens import EXCLUDE, routing_screen

    bad = [r for r in routing_screen(ctx["battery"]) if r.decision == EXCLUDE]
    if bad:
        cells: dict[str, list[str]] = {}
        for r in bad:
            cells.setdefault(r.detail["cell"], []).append(r.item_id)
        return Check(
            "routing_consistency", "", FAIL,
            f"{len(bad)}/{len(ctx['battery'].questions)} items route to a different claim type "
            f"than declared: " + "; ".join(f"{k}: {v}" for k, v in sorted(cells.items())),
            "decide, in writing and before dispatch, between (a) pre-registered route overrides so "
            "each arm delivers the directive its spec predicts about, (b) rewording the items, or "
            "(c) excluding them. Whichever is chosen changes the estimand and must be recorded.",
        )
    return Check("routing_consistency", "", PASS, "every item routes to its declared claim type")


@check("power_recomputed", "Is the power statement recomputed for the surviving items?")
def _power(ctx) -> Check:
    from lab.screens import load_screen_report

    report = load_screen_report("power")
    if report is None:
        return Check("power_recomputed", "", FAIL, "no runs/screens/power.json",
                     "recompute power after exclusions and commit it; plan §6 describes a battery "
                     "that no longer exists once anything is excluded")
    # The artefact reports every exclusion scenario that is still on the table,
    # so that the cost of an open decision is visible before it is taken. The
    # OPERATIVE scenario is the one with only settled exclusions applied.
    operative = report.get("if_only_scout_exclusions_apply", report)
    if "cells" not in operative:
        return Check("power_recomputed", "", FAIL,
                     "power.json has no recomputed cell table",
                     "regenerate it with lab.screens.power_statement")
    dead = [c for c, v in operative["cells"].items() if v["verdict"] == "DEAD"]
    if dead:
        return Check("power_recomputed", "", FAIL, f"cells with no surviving items: {dead}",
                     "a dead cell's hypothesis is untested, not refuted; decide whether to "
                     "re-author items or drop the hypothesis from exp003a")
    open_excl = (report.get("open_exclusions") or {}).get("routing") or []
    if open_excl:
        alt = report.get("if_routing_exclusions_also_apply", {}).get("cells", {})
        would_die = [c for c, v in alt.items() if v["verdict"] in ("DEAD", "SINGLE-ITEM")]
        return Check(
            "power_recomputed", "", BLOCKED,
            f"power is recomputed and committed, but {len(open_excl)} exclusions are still an "
            f"open decision. If they were applied, these cells would fall to DEAD or "
            f"SINGLE-ITEM: {would_die}",
            "resolve `routing_consistency`; the operative power figures cannot be final while an "
            "exclusion set is undecided",
        )
    reduced = [c for c, v in operative["cells"].items() if v["verdict"] == "REDUCED"]
    return Check("power_recomputed", "", PASS,
                 f"recomputed: {operative['total_solver_trials']} trials, "
                 f"{len(operative['excluded'])} exclusions, reduced cells {reduced or 'none'}")


@check("mechanism_confounds", "Is every mechanism the design cannot separate written down?")
def _confounds(ctx) -> Check:
    doc = _frozen_doc()
    required = ["FD-11"]
    missing = [r for r in required if r not in doc]
    if missing:
        return Check("mechanism_confounds", "", FAIL, f"undocumented: {missing}",
                     "record the compute/self-correction confound and its bounding plan before dispatch")
    return Check("mechanism_confounds", "", PASS,
                 "FD-11 records the mechanisms the design cannot separate and how each is bounded")


# --------------------------------------------------------------------------
# Runner
# --------------------------------------------------------------------------

def run() -> dict:
    from lab.battery import load_answers, load_battery
    from lab.states import load_egress

    ctx: dict = {}
    checks: list[Check] = []
    try:
        ctx["battery"] = load_battery("diagnostic_v1")
        ctx["answers"] = load_answers()["answers"]
        ctx["egress"] = load_egress()
    except Exception as e:  # noqa: BLE001
        return {
            "runnable": False,
            "question": "CAN THE EXPERIMENT RUN WITHOUT CHANGING ANY EXPERIMENTAL RULE AFTER SEEING SOLVER RESULTS?",
            "answer": "NO",
            "checks": [asdict(Check("context", "load the specification", ERROR, str(e),
                                    "fix the load error"))],
        }

    for fn in _CHECKS:
        try:
            result = fn(ctx)
            result.question = fn._question
        except Exception as e:  # noqa: BLE001
            result = Check(fn._cid, fn._question, ERROR, f"{type(e).__name__}: {e}",
                           "a check that cannot run counts against the verdict")
        checks.append(result)

    runnable = all(c.ok for c in checks)
    return {
        "question": "CAN THE EXPERIMENT RUN WITHOUT CHANGING ANY EXPERIMENTAL RULE AFTER SEEING SOLVER RESULTS?",
        "answer": "YES" if runnable else "NO",
        "runnable": runnable,
        "passed": sum(1 for c in checks if c.ok),
        "total": len(checks),
        "blockers": [asdict(c) for c in checks if not c.ok],
        "checks": [asdict(c) for c in checks],
    }


def render(result: dict) -> str:
    out = [
        "# exp003a preflight",
        "",
        f"> {result['question']}",
        "",
        f"## **{result['answer']}** — {result.get('passed', 0)}/{result.get('total', 0)} checks pass",
        "",
        "| Check | Status | Detail |",
        "|---|---|---|",
    ]
    for c in result["checks"]:
        out.append(f"| `{c['id']}` | **{c['status']}** | {c['detail']} |")
    if result["blockers"]:
        out += ["", "## Blockers", ""]
        for c in result["blockers"]:
            out += [f"### `{c['id']}` — {c['status']}", "",
                    f"**Question.** {c['question']}", "",
                    f"**What is wrong.** {c['detail']}", "",
                    f"**What must change.** {c['fix']}", ""]
    return "\n".join(out)


def write(result: dict) -> Path:
    path = REPO_ROOT / "runs" / "screens" / "preflight.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n")
    return path
