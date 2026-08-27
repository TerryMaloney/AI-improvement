# Lab manual

How the testing lab works, what its numbers mean, and — the part that usually
goes unwritten — what they don't.

---

## 1. The loop

The lab exists to run one cycle repeatedly:

```
hypothesis → experiment design → trials → grading → report → what changed? → next hypothesis
```

The last two steps are the ones that make it a lab rather than a pile of runs.
A result that updates nothing in `docs/hypotheses.md` is either a badly chosen
hypothesis or an unread result, and both are worth noticing.

Operationally: `docs/hypotheses.md` holds the open questions,
`experiments/*.yaml` holds the designs, `runs/<exp>/report.md` holds the
findings, and `.claude/skills/run-experiment/` holds the protocol a Claude
session follows to execute one.

---

## 2. Models under test, without an API key

There is no Anthropic API key in this environment, so the lab does not call the
API. Instead the orchestrating Claude Code session **spawns subagents as the
models under test**, using the `Agent` tool's per-spawn `model` override to run
the same battery across haiku, sonnet, and opus.

This is not a workaround with a hidden cost — it has one specific, real cost
(no token accounting; see §5) and one specific, real benefit: the "model" under
test is the same harness a user would actually be using, including its search
tooling, rather than a bare API call that resembles it.

### The sandbox

The threat is obvious once stated: a subagent with file tools can read
`batteries/answers.yaml` and score 100%. The defence is structural, not
instructional — solvers are not *asked* not to cheat, they are *unable* to.

| Agent | Tools | Used for |
|---|---|---|
| `solver-closed` | none at all | `baseline`, `directive_only` |
| `solver-web` | `WebSearch`, `WebFetch` | `search_only`, `verified` |
| `grader-judge` | none at all | all judge grading |

Four layers, in order of how much they'd have to fail simultaneously:

1. **Tool restriction.** Declared in each agent's frontmatter. `solver-closed`
   has no tools; `solver-web` has web tools and no filesystem access. Neither
   can read the answer key by any route.
   `tests/test_no_answer_leakage.py` parses the frontmatter and fails if a
   filesystem tool ever appears — a frontmatter edit is exactly the kind of
   change that would silently open the hole.
2. **Prompt quarantine.** No packet handed to a solver contains any string from
   the answer key. Tested by generating every packet for a real experiment and
   searching all of them against every answer-key string.
3. **Router redaction.** The router consults the entity registry, which holds
   cached facts. It emits *freshness verdicts* about those records and never
   their values — including dates. This one was caught by the test rather than
   by design: an earlier version put the Fed Chair's term-end date in the
   prompt block, which is half the answer to question `f03`, and would have
   handed the treatment condition a free point for a reason unrelated to the
   procedure being tested.
4. **Post-hoc audit.** Ingestion flags a closed-condition trial reporting
   searches (which would mean the sandbox itself is broken), a solver over its
   budget, and any answer containing answer-key text verbatim.

**A grader with tools is the same hole in a different place.** A judge that can
search will substitute its own retrieval for ground truth and silently become
the answer key. `grader-judge` has no tools, and when ground truth is not
established the packet tells it so explicitly and restricts it to grading
conduct.

---

## 3. Experimental design rules

### Don't confound treatments

The handoff packet proposes Phase 3 as "baseline vs. verified". Run that way,
the treatment bundles two changes — the epistemic directive *and* web search —
and if it wins, the result cannot say which half did the work. Since the two
have very different costs, that is precisely the thing we need to know.

`exp001` is therefore a 2×2:

|  | no directive | directive |
|---|---|---|
| **no search** | `baseline` | `directive_only` |
| **search** | `search_only` | `verified` |

`directive_only` is the interesting cell. If telling a model what kind of claim
it is facing improves its conduct with no retrieval at all, that is a nearly
free win. If it doesn't, the layer's value is entirely in how it *spends*
searches, which is a different and more expensive claim.

### Keep the control clean

Anything derived from the treatment must not reach a condition that is supposed
to lack it. Two live examples:

- `search_only` gets a **flat** search budget, not the route-derived one. A
  budget tuned per claim type is part of the treatment.
- The response schema is **identical** across conditions. An earlier draft
  asked solvers to self-report a claim type — but asking "what kind of question
  is this?" prompts exactly the reflection the epistemic layer is supposed to
  supply, so the control would have been receiving a dose of the treatment.
  Claim-type conduct is instead graded from the answer text by a blind judge.

### One question per agent

Batching several questions into one agent lets it notice that three of them are
false-premise traps, which inflates trap detection and measures your batching
rather than the model.

---

## 4. Grading

Deterministic first, judge only where deterministic cannot reach — mirroring
the system under test, and for the same reason: a judge that grades what a
string comparison could have graded is an expensive way to add variance.

| Method | Used for | Decides |
|---|---|---|
| `contains_any` | named officeholders | accepted string present |
| `numeric` | arithmetic | value within tolerance, distractors rejected |
| `trap_detected` | false premises | premise rejected; escalates if worded unusually |
| `judge` | everything else | blind rubric grading |

Three outcomes that are **not** scores, and are real results rather than errors:

- `UNGRADED` — the answer key entry is `stale` or `unverified`. See §6.
- `NEEDS_JUDGE` — deterministic grading was attempted and couldn't decide. A
  trap rejected in wording the marker list doesn't cover escalates rather than
  failing, because scoring it `FAIL` would penalise vocabulary rather than
  reasoning.
- `NO_ANSWER` — the trial never ran or returned nothing parseable.

Judges are told to penalise **both** directions of error. A correct number
asserted with false certainty where the rubric requires a range does not pass;
neither does hedging out of a question the rubric says was answerable. Grading
only overconfidence would train the lab toward a system that abstains from
everything and scores well doing it.

---

## 5. What is measured — and what isn't

**Honestly measured:** correctness against verified ground truth; premise
rejection on traps; hedging and abstention rates; search counts; answer length;
claim-type routing (recorded for every trial, including controls, so routing
accuracy can be analysed independently of whether the route was injected).

**Not measured, and no substitute pretends otherwise:**

- **Token counts and dollar cost.** Without API access there is no token
  accounting. The lab uses *cost proxies* — search count, answer length, trial
  count — and every report labels them as such. Where the packet asks for "real
  token counts, not eyeballed estimates", this is the honest gap: the search
  counts are real and measured, the token costs are not available at all.
- **Latency.** Subagent wall-clock time is dominated by scheduling, not model
  work.
- **Budget enforcement on solvers.** `BudgetCeiling` hard-gates the routing
  layer deterministically and is tested against a runaway EIG spiral. But a
  solver's search budget is enforced by instruction plus post-hoc audit, not by
  interception — the orchestrator cannot intercept a subagent's tool calls. An
  over-budget trial is flagged, kept, and makes that condition's cost figure an
  underestimate.
- **Statistical significance.** With 15 questions and one repeat, differences of
  a few points are noise. Treat single-run findings as directional. `repeats`
  exists in the config for when a specific question needs it; spending repeats
  uniformly across a battery mostly buys precision where it wasn't needed.

---

## 6. The refusal that matters most

**The lab will not score an answer against ground truth nobody has verified.**

`batteries/answers.yaml` marks each entry `verified`, `stale`, or `unverified`.
Only `verified` (and `rubric_only`, which has no factual answer by
construction) is eligible for scoring. Everything else reports `UNGRADED`, and
the report names those questions and tells you to run `python -m lab refresh`.

This is not fastidiousness. Handoff packet §5 applies the project's own TTL
rule to the project's own facts and finds four carried-over values that were
never re-checked. Scoring against those would produce a number that looks
measured and isn't — the exact failure the whole project exists to prevent. A
lab that exempts itself from its own standard is not measuring anything.

`python -m lab refresh` prints the queue: entities past their TTL, and answer
entries not scorable. Working that queue is a real task with a real cost, which
is why the tool reports it rather than silently searching.

---

## 7. Threats to validity

Written down because the ones you haven't named are the ones that get you.

1. **Judge-generator correlation.** The judge is a Claude model grading Claude
   models. Shared blind spots pass unnoticed. Partly mitigated by
   deterministic-first grading and by rubrics written before any answers
   existed. Not solved. The packet's own defence — use a different model family
   for the judge — isn't available without an API key.
2. **Small n.** 15 factual questions, hand-written by the people who built the
   layer. They probe failures the design session already found, which makes
   them a fair test of "does the layer fix what we built it for" and a weak
   test of "does the layer help in general."
3. **Battery authorship bias.** The questions were written with the layer's
   claim types in mind. A battery written by someone who had never seen the
   layer would be a stronger test, and is worth doing.
4. **Self-reported search counts.** Audited for the impossible cases
   (closed-condition searches, over-budget) but not independently verified. A
   solver that under-reports makes its condition look cheaper than it was.
5. **Ground truth drift.** Volatile facts go stale *during* a run. Every answer
   entry carries `verified_as_of` so a stale-at-grading-time result can be
   identified after the fact rather than silently absorbed.
6. **Goodhart on the lab.** Iterating directive wording against this battery
   will eventually tune the directive to these 15 questions. The packet lists
   "Goodhart on the controller itself" as an untested failure; a held-out
   battery, never used for iteration, is the standard defence and does not
   exist yet. This is the most likely way the lab quietly stops measuring
   anything.

---

## 8. Extending the lab

**A new question** goes in the relevant `batteries/*.yaml` with a `why:` field
saying which failure mode it probes that the existing questions don't. Its
ground truth goes in `answers.yaml` with an honest `status`. If you can't
verify it now, mark it `unverified` and let it report as ungraded — that is
working as intended.

**A new experiment**: copy `experiments/exp001_factorial.yaml`. State the
hypothesis so that a specific, possible result would count against it. If no
result would, it's a slogan.

**A change to the directives** in `epistemic/router.py` changes the treatment,
so it belongs to a new experiment rather than a re-run of an old one. Re-running
`exp001` after editing a directive produces two numbers labelled `exp001` that
measure different things.

**A new claim type or routing rule** goes in `epistemic/`, with a test. The
classifier's two historical bugs are permanent regression tests in
`tests/test_classifier.py`; both were found by running the thing against real
questions, not by reading it, which is the argument for adding the test at the
same time as the rule.
