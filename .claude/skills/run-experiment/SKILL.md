---
name: run-experiment
description: Run an experiment in the epistemic testing lab end to end — prepare trial packets, dispatch sandboxed solver agents, ingest and grade answers, and write the report. Use when asked to run, re-run, or extend an experiment (e.g. "run exp001", "test whether X helps", "compare these conditions"), or when a new hypothesis needs an experiment designed for it.
---

# Running an experiment

You are the **operator**. The Python in `lab/` does everything reproducible;
you do the one thing it cannot, which is host the models under test by spawning
sandboxed subagents.

Read `docs/lab_manual.md` once before your first run in a session. It explains
why the sandbox is built this way and what the measurements do and don't mean.

## Before anything: the refresh gate

```bash
python -m lab refresh
```

Anything listed as not-scorable will grade as `UNGRADED`, by design — the lab
refuses to score against ground truth nobody has verified. You have two honest
options and one dishonest one:

1. **Verify it.** Use *your own* WebSearch (you have tools; the solvers don't),
   then update `batteries/answers.yaml` with the value, `verified_as_of:` today,
   and `status: verified`.
2. **Run anyway** and let those questions report as ungraded. Fine for a
   pipeline smoke test, not fine for a result you'll cite.
3. ~~Mark it verified without checking.~~ Never. That converts a guess into the
   experiment's ground truth and every number downstream inherits it.

If you verify a fact, also update the matching `EntityRecord` in
`epistemic/registry.py` via `record_verification()` semantics — a changed value
banks a real turnover interval, which is the data that eventually replaces the
eyeballed 30-day VOLATILE threshold with a measured one.

## 1. Prepare

```bash
python -m lab prepare <exp>
```

Writes `runs/<exp>/manifest.json` — every trial with its full prompt inline —
plus one packet file per trial for inspection.

## 2. Dispatch solvers

Read the manifest **once**, then for each trial spawn the agent it names:

```
Agent(
  subagent_type = trial["agent"],     # solver-closed | solver-web
  model         = trial["model"],     # haiku | sonnet | opus
  prompt        = trial["prompt"],    # verbatim — do not edit, summarise, or add to it
  run_in_background = true
)
```

Rules that keep the results meaningful:

- **Pass the prompt verbatim.** Any word you add is an uncontrolled treatment
  applied to one condition and not the others.
- **One question per agent.** Batching several questions into one agent lets it
  see that three of them are false-premise traps, which inflates trap detection
  and measures your batching rather than the model.
- **Never answer a trial yourself**, and never let a solver's answer inform
  another trial. You have tools the solvers don't; anything you contribute is
  contamination.
- **Spawn in parallel batches** (roughly 8–12 at a time) and wait for each batch
  before the next, so failures stay attributable.

Write each agent's returned JSON to `runs/<exp>/answers/<trial_id>.json`.
If an agent returns prose around the JSON, save it as-is — the ingester
recovers fenced and embedded JSON and records that it had to.

Check progress at any point with `python -m lab status <exp>`.

## 3. Ingest and audit

```bash
python -m lab ingest <exp>
```

Read the `audit_flags` in the output. They are not cosmetic:

- A **SANDBOX** flag (a closed-condition trial reporting searches) means the
  agent definition is wrong and the run is invalid. Fix the agent, re-run those
  trials — do not report the numbers.
- A **BUDGET** flag means a solver exceeded its stated ceiling. Keep the trial,
  but the cost comparison for that condition is now an underestimate and the
  report should say so.
- A **LEAK-SUSPECT** flag means answer-key text appeared verbatim in an answer.
  Investigate before trusting anything.

## 4. Grade

```bash
python -m lab grade <exp>
```

Deterministic graders run first. Whatever they can't decide gets a judge packet
in `runs/<exp>/judge_manifest.json`. For each, spawn:

```
Agent(subagent_type="grader-judge", model="sonnet", prompt=judgment["prompt"], run_in_background=true)
```

Use **one model for every judge in an experiment** — a judge swapped mid-run is
a second uncontrolled variable. Judge packets are blind by construction: they
carry the question, the standard, and the answer, and never the condition or
model. Don't tell the judge anything the packet doesn't.

Write each verdict to `runs/<exp>/grades/<trial_id>.json`, then:

```bash
python -m lab ingest-judgments <exp>
```

## 5. Report and record

```bash
python -m lab report <exp>
python -m lab compare <exp> <other-exp>     # when there's something to compare to
```

Then **append the outcome to `docs/hypotheses.md`** — this is the step that
makes the lab cumulative rather than a pile of runs. For the hypothesis under
test, record: the experiment id, the date, what the result was, and crucially
**what it changed**. A result that updates nothing is either a badly chosen
hypothesis or an unread result.

If the result suggests a new hypothesis, add it to the ledger as `open` with the
experiment that would settle it. That's the loop.

## Designing a new experiment

Copy `experiments/exp001_factorial.yaml` and change what you need. The parts
worth thinking about before you spend trials:

- **Don't confound treatments.** exp001 is a 2×2 rather than the packet's
  proposed baseline-vs-verified precisely because "layer + search" versus
  "model alone" cannot say which half did the work, and the two halves have
  very different costs. If your new condition bundles two changes, split it.
- **Keep the control clean.** Anything derived from the treatment — a
  route-derived search budget, a claim-type hint, a reflective question in the
  response schema — must not reach conditions that are supposed to lack it.
- **Say what would falsify it.** Write the hypothesis so that a specific,
  possible result would count against it. If no result would, you have a
  slogan, not a hypothesis.
- **Prefer adding a condition to an existing battery** over inventing new
  questions; it keeps runs comparable. When you do add questions, say in the
  battery file which failure mode they probe that the existing ones don't.

## Cost discipline

Every trial is an agent spawn. Before running a full grid, run 2–3 trials end to
end and read the answers — a prompt bug found after 120 spawns costs 120 spawns.
Repeats are for questions with genuinely variable answers; spending them
uniformly across a battery mostly buys precision where you didn't need it.
