# exp003a experiment readiness report

**Status: NOT RUNNABLE.** The preflight answers its binary question **NO** at
20/25 checks. Zero solver trials have been dispatched at any point in steps 3, 4
or 5.

## The Step-5 objective, restated

Step 5 is not "finish the setup". It is the stage at which the experiment either
becomes *runnable* — in the sense that matters — or is shown not to be. The
experiment is runnable only if all of the following are true **before the first
dispatch**:

1. **Every rule that could change the result is already fixed in writing.** The
   battery, the treatments, the scoring, the rubrics, the judge, the exclusion
   criteria, the power statement, and what each verdict means.
2. **Every screen has actually run**, on criteria chosen before any solver
   output existed. A screen whose thresholds could still move is a selection
   effect with a screen's name.
3. **The specification claims nothing the runtime cannot produce.** No item may
   be specified to reach a retrieval state the environment cannot reach.
4. **Every named condition has a text or protocol**, not a label. A condition
   assembled at dispatch time is a treatment nobody pre-registered.
5. **The measurement can distinguish the mechanisms it claims to distinguish**,
   or the confounds it cannot separate are written down in advance with a
   bounding plan.
6. **The exact runnable artefact is identifiable** — one commit, one battery
   fingerprint, one treatment fingerprint.

The operative test is a single question, and the preflight exists to answer it:

> **CAN THE EXPERIMENT RUN WITHOUT CHANGING ANY EXPERIMENTAL RULE AFTER SEEING
> SOLVER RESULTS?**

It fails closed. An unknown check is a FAIL, an unrun screen is BLOCKED, and
`runnable` is the conjunction of all twenty-five checks. There is no "mostly
ready".

---

## A. IMPLEMENTED

| Component | What it does | Where |
|---|---|---|
| **Routing screen** | Compares each item's declared claim type against the one the router actually produces. Deterministic, no solver, runs now. | `lab/screens.py` |
| **Knowledge screen** | Ceiling/floor on baseline correctness, thresholds frozen at ≥0.90 / ≤0.10. Reports `NOT_SCREENED` — never `KEEP` — without probe results. | `lab/screens.py` |
| **Power recomputation** | Recomputes plan §6 per cell from surviving items. Reports `AS PLANNED` / `REDUCED` / `SINGLE-ITEM` / `DEAD`, and refuses a consistency claim below two items. | `lab/screens.py` |
| **Frozen retrieval scout** | Per cell-D item: the loaded query a solver would issue, and the frozen neutral topic for the claim-blind gatherer. Run and committed. | `lab/scout.py`, `runs/screens/retrieval_scout.json` |
| **`A_only`** | The directive's own framing sentence on a carrier built by the placebo machinery, reusing the placebo's text almost verbatim. | `lab/treatments.py` |
| **`search_selfcheck`** | Two dispatches. Reviewer sees question + draft, **not** the snippets — frozen, so the arm measures re-reading its own claim rather than re-reading evidence. | `lab/treatments.py` |
| **`search_independent`** | Three dispatches. Gatherer receives a **frozen neutral topic string**, not the question, which is what makes claim-blindness real: every cell-D question contains its own false premise. | `lab/treatments.py` |
| **`elaboration_only`** | The compute control (FD-11). Written and frozen, deliberately **not** adopted into the battery — that is the operator's decision. | `lab/treatments.py` |
| **Dispatch accounting** | `DISPATCH_COUNT` is the single source: selfcheck = 2, independent = 3. An undeclared condition raises rather than defaulting to 1. | `lab/treatments.py` |
| **Preflight** | 25 checks, fail-closed, one binary verdict. | `lab/preflight.py` |
| **CLI** | `python -m lab screens`, `python -m lab preflight`, `python -m lab spec`. | `lab/__main__.py` |

---

## B. VERIFIED

Each of these is asserted by a test, not by this document.

* **`A_only` is length-matched by the placebo machinery** on all 25 items: word
  count within 10%, and bullet count, section headers, paragraph blocks and
  em-dash count matched **exactly**. It differs from `directive_placebo` on at
  most four lines, and every bullet but the last is the placebo's text verbatim.
* **No arm is called verification.** `is_verification()` returns False for every
  arm under the probed environment, computed from the formal definition —
  corroboration by independent origins at document depth — not from the arm's
  name. It returns True for `search_independent` only under a hypothetical
  open-egress environment, which proves the check is testing the definition.
* **No multi-dispatch arm is counted as one dispatch.**
* **No item is specified to reach an unreachable state.** All declared retrieval
  states are inside the probed reachable set.
* **No answer-key string reaches any packet**, in any condition, on any item.
* **Preparation cannot dispatch.** No preparation module imports `subprocess`,
  `requests`, `httpx` or `urllib`.
* **No solver artefacts exist.** No `runs/exp003a/` answers, grades or database.
* **Generation is deterministic.** Placebo and `A_only` are seeded from question
  text with no RNG; there is no trial-order randomisation, so there is no seed
  to record.
* **Freeze fingerprints are recorded and checked**: `TREATMENT_FREEZE`,
  `SCORING_FREEZE`, `JUDGE_FREEZE`. The preflight recomputes each and FAILS on a
  mismatch rather than warning.
* **Test suite: 756 passing**, the original 130-test baseline unmodified.

### Two findings from the screens, both obtained for zero solver dispatches

**1. The router agrees with the battery on 15 of 25 items (60%).** The
disagreements are systematic, not noise:

* Word problems never reach DETERMINISTIC — the classifier fires only on an
  explicit operator between two numbers, so every cell-R item and two cell-N
  items fall through to the EMPIRICAL default.
* Superlatives read as evaluative — "first successful", "first became
  available", "Best Picture" all route NORMATIVE at **0.90 confidence**, a
  confident wrong classification with a budget of zero.

This is a measurement about the epistemic layer itself, and it holds regardless
of which option is chosen below: a layer that routes 60% of questions correctly
cannot deliver more than 60% of whatever its directives are worth.

**2. Two of five cell-D items were excluded by their own pre-registered scout
criteria.** D01 (Einstein/relativity) and D02 (Coriolis/drain) both have search
spaces that **correct** the premise rather than restating it — D01's top result
is titled "Why didn't Einstein get the Nobel Prize for the theory of
relativity?", and every first-page result for D02 is a debunking. They test
retrieval benefit, not displacement, so they leave the cell.

Cell D therefore runs on three items and is **REDUCED**: the consistency
requirement falls from 2-of-5 to 2-of-3, which is a weaker claim on a smaller
base. D03 is the strongest survivor — its search space is dominated by bookseller
listings for an anthology, and the scout's own retrieved summary accepted the
question's framing without challenge.

---

## C. OPEN RISKS AND LIMITATIONS

**C1 — Additional computation is not separated from reasoning.** The
DETERMINISTIC directive says "Show the steps so the arithmetic is checkable".
More intermediate tokens improve multi-step arithmetic on their own. The placebo
matches the *prompt*; nothing currently matches the *response*. A positive cell-R
result is ambiguous between "the epistemic content helped" and "the directive
elicited more serial computation". Bounded by a response-token covariate
(adopted, free, and weaker than it looks — response length is a mediator, so
conditioning on it can over- or under-correct). Measured properly only by
adopting `elaboration_only`. See **FD-11**.

**C2 — Self-correction is not separated from a second pass.**
`search_selfcheck` differs from `search_only` by review *and* by there being a
second dispatch at all. Reported as "a second dispatch of any kind", never as
"self-correction". Separating them needs a `second_pass_inert` arm (15 trials);
not recommended, since the arm sits in a DIAGNOSTIC cell that cannot carry a
mechanism claim anyway.

**C3 — Battery construction bias is real and is not cured by the checks.** The
items were written by the same process that wrote the mechanism. Every task axis
varies and none is collinear with `claim_type` — but that establishes only that
the axes carry information, **not** that the battery is unbiased. A battery
written by someone who had never seen the epistemic layer would be a stronger
test, and remains the largest unaddressed threat to validity in the programme.
This limitation is not retired by any check in the preflight and must appear in
any result.

**C4 — `SOURCE_ACCESS` and `VERIFICATION` are unreachable.** WebFetch is
egress-blocked. Nothing may be concluded about either, in any direction, from
any trial in this environment (FD-4).

**C5 — The search space is not a constant.** The scout is frozen as of
2026-08-28. If cell D is dispatched much later, the scout is re-run and any
change is reported as a change of instrument, not absorbed.

**C6 — C4/OPEN-1 (judge replicates k=3) remains unresolved**, as instructed. It
is an exp003a pre-registration decision, not a step-5 one.

---

## D. BLOCKERS BEFORE FIRST DISPATCH

Five. Each states exactly what must change and why.

### D1 — `routing_consistency` (FAIL) — the only one requiring a judgement call

**What is wrong.** Ten of 25 items receive a different directive from the one
their specification predicts about. All four cell-R items route EMPIRICAL, so
`directive_only` would deliver premise-checking and source-independence
instruction — plus a two-search budget for tools that do not exist — to
closed-book arithmetic. Cell R would not be testing E2.

**What must change.** A decision, in writing, before dispatch, between:

| Option | Consequence, measured |
|---|---|
| **(a) Pre-registered route overrides** | exp003a measures directive efficacy *under correct routing* — an upper bound — with 60% routing accuracy reported separately as the multiplier converting it to real-world benefit. All cells survive; 348 trials. |
| **(b) Reword the items** | Reverse-engineers the classifier; the items become classifier fixtures rather than natural questions. |
| **(c) Exclude the misrouted items** | **Cell R dies entirely (0/4). Cell N falls to one item. Cell C falls to one tripwire.** 348 → 215 trials, and the cells carrying E2 and tool restraint stop existing. |

**Why.** (a) is recommended and is *not* taken here, because it makes the
mechanism look better by removing its own failure mode from the measurement.
That is exactly the kind of choice the frozen-decisions register exists to stop
anyone making quietly. See **FD-12**.

### D2 — `screens_complete` (BLOCKED)

**What is wrong.** The knowledge probe has not been dispatched, so all 25 items
report `NOT_SCREENED`, and ceiling/floor exclusions are unknown.

**What must change.** Dispatch the probe — `baseline` only, k=5, ~125 solver
trials — and commit `runs/screens/knowledge_probe.json`. The thresholds are
already frozen at ≥0.90 / ≤0.10, so running it **cannot** change them.

**Why.** L06 and D05 were authored as deliberate near-ceiling items to exercise
this screen. Until it runs, nobody knows how many items cell L actually has.

### D3 — `power_recomputed` (BLOCKED)

**What is wrong.** Power is recomputed and committed, but an exclusion set is
still undecided (D1), and the alternative scenario would leave cell R DEAD and
cells N and C at a single item.

**What must change.** Resolve D1, then re-run `lab.screens.power_statement` and
commit the single operative table.

**Why.** The plan §6 figures describe a battery that no longer exists. They are
retained for comparison and are not the operative numbers.

### D4 — `experiment_identity` (FAIL)

**What is wrong.** There is no `experiments/exp003a_mechanism.yaml`.

**What must change.** Write it after D1 and D2 resolve, since its condition list
depends on the routing decision and its item list on the screen. It must name
the three freeze fingerprints it runs against.

**Why.** Without a versioned config there is no artefact that identifies what was
run.

### D5 — `git_identity` (FAIL)

**What is wrong.** Uncommitted changes; HEAD does not describe what would run.

**What must change.** Commit everything immediately before dispatch and re-run
the preflight so the recorded verdict names the dispatch commit.

**Why.** This is a dispatch-time check and is expected to fail during authoring.
It is listed because it must pass at the moment of dispatch, not merely at some
point beforehand.

---

**Nothing dispatches until D1–D5 are cleared and the preflight answers YES.**
