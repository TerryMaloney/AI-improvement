# exp003a — final pre-dispatch audit

## VERDICT: **NOT RUNNABLE**

Preflight 33/34 against the committed artefact. One blocker: the knowledge probe
has not been dispatched. **Zero solver trials have been run at any point in steps
3, 4 or 5, or in this implementation pass.**

I did not run the probe. It is authorised, prepared and ready as a single
operation, but it is 115 dispatches, and running it was permitted rather than
required. Reporting NOT RUNNABLE with one named, prepared blocker is the honest
state; clearing it is a focused next step, not a side effect of this one.

---

## Experiment identity

| Field | Value |
|---|---|
| Experiment id | `exp003a` |
| Configuration | `experiments/exp003a_mechanism.yaml` |
| Commit | `5be672a322ff667fcdb3775eb6f171f278f08c82` |
| Battery | `diagnostic_v1`, 25 items authored, 23 prepared |
| Model | `haiku` |
| Dispatch seed | `20260829` |
| Egress probe | 2026-08-28 — WebSearch open, WebFetch `EGRESS_BLOCKED` on three unrelated hosts |
| Retrieval scout | 2026-08-28, frozen, five cell-D items |
| Judge calibration | exp003c (AMBER, Δ_length = −0.125, σ_judge = 0) |
| `TREATMENT_FREEZE` | `4623768955413fa4…` |
| `SCORING_FREEZE` | recorded in `docs/EXP003A_FROZEN_DECISIONS.md`, verified by preflight |
| `JUDGE_FREEZE` | recorded, verified by preflight |
| Tests | **999 passing**; the original 130-test baseline unmodified |

---

## Final battery composition

25 items authored; 2 excluded before preparation by the frozen retrieval scout,
against each item's own pre-registered criterion:

* **D01** — the search space *corrects* the premise; top result titled "Why
  didn't Einstein get the Nobel Prize for the theory of relativity?"
* **D02** — every first-page result debunks the claim.

Both test retrieval benefit, not displacement. **23 items prepared.**

| Tier | Count | Items |
|---|---|---|
| `PRIMARY` | 10 | all of L, all of R |
| `DIAGNOSTIC` | 13 | all of D, U, N |
| `MEASUREMENT_VALIDITY` | 2 | C01, C02 (both gates) |

Routing dispositions, each verified against the classifier's actual behaviour:
`agrees` 11 · `inert_no_directive_arm` 7 · `crossed` 4 · `accepted_as_system` 3.

---

## Final trial count — read from the generated manifest, not computed

**388 trials · 433 dispatches.** Verified from `runs/exp003a/manifest.json`. The
independently-computed power model in `runs/screens/power.json` agrees at 388.

Two arithmetic errors were caught by doing this rather than trusting the decision
packet:

1. A single global `repeats` cannot express plan §6's per-cell k. The first
   manifest held **500** trials.
2. The scout's exclusions were never applied at preparation. Cell D was
   generating five items' worth of trials.

### Trials per cell

| Cell | Items | Conditions | k | Trials |
|---|---|---|---|---|
| L | 6 | 4 | 5 | 120 |
| R | 4 | 5 | 5 | 100 |
| D | 3 | 4 | 5 | 60 |
| U | 4 | 5 | 3 | 60 |
| N | 4 | 3 | 3 | 36 |
| C | 2 | 2 | 3 | 12 |
| **Total** | **23** | | | **388** |

### Routed / intended

| | Trials |
|---|---|
| `routed` — the directive the classifier selects | **348** |
| `intended` — the directive the item was written for | **40** |

The 40 intended trials are cell R's `placebo_intended` (20) and
`directive_intended` (20). No other cell crosses.

### Placebo counts

| Arm | Trials | Matched to |
|---|---|---|
| `directive_placebo` | 42 | the routed block (cells L, U) |
| `placebo_routed` | 20 | cell R's **routed** block |
| `placebo_intended` | 20 | cell R's **intended** block |
| **Total placebo** | **82** | |

Two placebos in cell R because the intended block is **68 words shorter** than
the routed one (211 → 143, 5 bullets → 4, budget 2 → 0). A single placebo would
have left one arm uncontrolled and put E4 and E5 back into the routing contrast.

### All conditions

`baseline` 80 · `A_only` 42 · `directive_only` 42 · `directive_placebo` 42 ·
`search_only` 45 · `directive_routed` 20 · `directive_intended` 20 ·
`placebo_routed` 20 · `placebo_intended` 20 · `closed_book` 15 ·
`search_selfcheck` 15 · `search_independent` 15 · `search_directive` 12.

---

## Exact estimands

| Estimand | Definition | Items | Answers | Does NOT answer |
|---|---|---|---|---|
| **θ_directive** | E[S \| directive_intended] − E[S \| placebo_intended] | 14 | does the directive the item was written for change the outcome, with length and format held constant | what the deployed layer does; whether the change is reasoning rather than computation |
| **θ_system** | E[S \| directive_routed] − E[S \| placebo_routed] | 8 | what the epistemic layer as deployed, classifier included, does — the quantity comparable to exp001/exp002 | what the directive's content is worth when correctly delivered |
| **θ_routing** | (routed − placebo_routed) − (intended − placebo_intended) | 4 | on this item, how much outcome is lost by delivering the classifier's directive instead of the intended one | the expected loss in deployment; routing accuracy is unmeasured |
| **θ_framing** | E[S \| A_only] − E[S \| directive_placebo] | 10 | does the claim-type framing sentence alone change the outcome | whether the procedural bullets add anything |
| **δ_displacement** | E[S \| search_only] − E[S \| closed_book] | 5 | does snippet-depth retrieval make false-premise answers worse | anything about SOURCE_ACCESS or VERIFICATION — both unreachable |
| **mode_shift** | change in the categorical response-mode distribution | 4 | does the directive change response *shape* where no answer is established | whether calibration improved |
| **gate** | search versus closed book on post-cutoff facts | 2 | is the retrieval channel working at all | nothing about any hypothesis |

**Cell N is θ_system by decision**, not θ_directive. It accepts the routed
directive because a claim about tool restraint should be about what the deployed
layer actually delivers. Its items are barred by validation from declaring
θ_directive.

---

## Power and inference

**Confirmatory cell: L, and only L.** Six items; a sign test reaches p = 0.031 at
5/6 and p = 0.016 at 6/6.

**Descriptive cells: R, D, U, N, C.** With fewer than five items, a sign test
cannot reach p < 0.05 even with unanimous agreement — R and U and N cap at
0.0625, D at 0.125, C is a gate. Their language must be "on these items, X was
higher than Y by Δ", never "X improves Y".

**Effect-size resolution.** The design *displays* per-item shifts of about 0.2 and
above. That is descriptive, not inferential.

**Statistical significance.** At k=5 versus k=5, Fisher one-sided: a 0.4 shift
gives p ≈ 0.22–0.26. **p < 0.05 requires a shift of 0.8.** The figure plan §6
formerly called the MDE was a detection threshold, and the old sentence is now
quoted under a SUPERSEDED marker rather than deleted, so the amendment is
auditable.

**Uncertainty.** Clopper–Pearson 95% at k=5: 0/5 → [0.00, 0.52]; 2/5 → [0.05,
0.85]; 5/5 → [0.48, 1.00]. No per-item rate is known to better than about ±0.4,
or ±0.45 at k=3.

**Pre-committed:** if cell L drops below five items after the knowledge screen,
exp003a has **no confirmatory cell at all**, and that goes in the report's first
paragraph. If cell C drops to zero, the gate fails and no search result may be
interpreted.

---

## Randomisation

**Randomised: the dispatch ORDER only.** One shuffle over the full 388-trial list
from seed `20260829`, recorded in the configuration and in the manifest, and
verified reproducible by the preflight rather than assumed. It exists because the
design now contains paired within-item contrasts, and dispatching arm-by-arm
would let drift over the run land unevenly across a pair.

**Not randomised: treatment assignment.** Every item receives every condition it
declares — a full within-item factorial with no allocation step. There is nothing
to allocate, so the seed provides **no protection against confounding**. The
manifest states this in its own words.

---

## Qualification and probe status

| Class | Work | Dispatches | In primary dataset? |
|---|---|---|---|
| `instrument_qualification` | exp003c judge calibration | 96 judge calls (done) | no |
| `retrieval_qualification` | egress probe, frozen scout | 0 solver (done) | no |
| `screen` | routing screen (done, deterministic); **knowledge probe (NOT RUN)** | 0 of a planned 115 | no |
| `treatment_validation` | placebo / A_only / crossed-arm checks | 0 (static) | no |
| `solver_experiment` | exp003a | **0 of 388** | yes — this class only |

**Solver dispatches to date: 0.** The primary database holds 388 prepared trials,
all `solver_experiment`, and zero answers.

Separation is structural, not documentary: `dispatch_class` is assigned before
generation and stored on the trial; the probe has its own configuration, its own
run directory and a single baseline arm; and `dispatch_class_isolation` fails if
the primary database ever holds a non-experimental row. **The probe's baseline may
not be reused as the experiment's control** — it selects items on baseline
performance, so reusing it would condition the control on the selection criterion
— which is why exp003a dispatches its own 80 baseline trials.

---

## Remaining limitations

1. **C3 — battery-construction bias.** 25/25 items authored by the same process
   that authored the mechanism; **0** externally sourced; **0** blind-authored.
   Six of six task axes vary and none is collinear with `claim_type` — which
   establishes that the axes carry information, and **nothing** about
   independence. Frozen; the remedy is an exp004 battery authored blind.
2. **Additional computation is not separated from reasoning.** `elaboration_only`
   is written and frozen but deliberately not adopted. The cell-R claim is
   constrained accordingly.
3. **Self-correction is not separated from a second pass.** `search_selfcheck` is
   reported as "a second dispatch of any kind".
4. **SOURCE_ACCESS and VERIFICATION are unreachable.** No conclusion about either,
   in either direction.
5. **Cell D is REDUCED to three items**, so the displacement hypothesis that
   motivated much of exp003 can only be reported descriptively.
6. **Routing accuracy is unmeasured.** 15/25 is agreement on a purpose-built
   battery, not an estimate for any task distribution. The two failure *modes*
   generalise; the rate does not.
7. **FD-1 stands frozen, not fixed.** Closed-book `directive_only` packets still
   contain a search budget for tools that do not exist — part of the treatment
   exp001/exp002 measured.
8. **FD-13.** The intended arm prints a constructed confidence figure (0.90, what
   the router would have produced had it classified correctly), a visible
   one-token difference from the routed arm's 0.60.

---

## Remaining blockers

| # | Blocker | Status | What clears it |
|---|---|---|---|
| **1** | `screens_complete` | **BLOCKED** | Dispatch the knowledge probe: `python -m lab prepare exp003a_knowledge_probe`, 115 baseline-only screening dispatches, then commit `runs/screens/knowledge_probe.json`. Thresholds are already frozen at ≥0.90 / ≤0.10 and cannot move. |

Everything else passes. `git_identity` passes against the audited commit.

---

## The sanity question

> **If the experiment produces a positive result, exactly what will we have
> demonstrated, and what will we still NOT have demonstrated?**

### What a positive result would demonstrate

Concretely, and at most: **that on six specific closed-book recall items, a block
of text containing the epistemic framing produced more correct answers than a
block matched to it in word count, bullet count, structure and formatting markers
but carrying no epistemic content — across five independent single-dispatch
replicates each, on one model.** If five or six of the six items move the same
way, that pattern is unlikely to be chance (p ≤ 0.031).

That is the whole of the confirmatory claim. Everything else in the run —
cell R's arithmetic, cell D's displacement, cell U's response modes, cell N's tool
counts, and the routed-versus-intended contrast — is **descriptive**, because
those cells have too few items for direction-consistency to reach significance
under any outcome.

### What it would NOT demonstrate

* **Not that the directive improves reasoning.** The compute path is unseparated:
  "show the steps" produces more intermediate tokens, and more intermediate
  tokens help arithmetic on their own. We measure the total effect and report
  response length as a manipulation check. "The treatment caused longer
  responses" is supportable; "longer responses caused the effect" is not, and
  cannot be inferred from anything here.
* **Not that the epistemic layer works.** That is θ_system, which includes the
  classifier — and the classifier misroutes 9 of 25 items on this battery. A
  positive θ_directive is an **upper bound** on what correct delivery is worth,
  and routing accuracy is a separate multiplier that this experiment does not
  measure.
* **Not that it generalises.** All 25 items were authored by the process that
  authored the mechanism. No axis check establishes independence.
* **Not that verification helps.** WebFetch is blocked; verification never
  occurred.
* **Not that self-correction works.** Only that a second dispatch of some kind
  did or did not change the answer.
* **Not a battery-wide or model-wide effect.** The battery mean is not an outcome,
  one model is used, and no per-item rate is known to better than about ±0.4.

### Is the answer narrower than the hypothesis?

**Yes, substantially.** The hypothesis under investigation is that an epistemic
control layer makes AI answers more reliable. What a positive result establishes
is that one component of one directive, delivered correctly, moved six recall
items on one model under a closed-book single-dispatch protocol — with the
mechanism of that movement unresolved between latent-knowledge access and
generic instruction-following, and with the deployed system's own routing shown
to deliver the wrong directive on more than a third of the battery.

That gap is the point. The experiment is built to make a small, defensible claim
and to make the size of the remaining gap explicit, rather than to produce a
number that could be mistaken for the larger one.
