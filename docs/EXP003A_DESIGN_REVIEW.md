# exp003a design review — the D1 fork

**Nothing in this document has been implemented.** No option has been applied to
the battery, no configuration written, no solver trial dispatched at any point in
steps 3, 4, 5 or here. The guiding question is not whether the experiment can be
made to survive, but whether it can support the claim we eventually want to make.

---

## A. D1 option analysis

### A.0 A correction that changes the scope: 8 items, not 10

Ten items misroute. Only **eight** can affect anything, because a misroute can
only matter where the routed claim type actually reaches the solver — that is,
where a condition injects the routed directive (`directive_only`,
`search_directive`) or the routed framing (`A_only`).

| Cell | Conditions | Route-dependent? |
|---|---|---|
| L | baseline, directive_placebo, A_only, directive_only | **yes** |
| R | baseline, directive_placebo, directive_only | **yes** |
| U | baseline, directive_placebo, A_only, directive_only, search_only | **yes** |
| N | baseline, search_only, search_directive | **yes** |
| D | closed_book, search_only, search_selfcheck, search_independent | **no** |
| C | baseline, search_only | **no** |

So **D04 and C02 need no remedy at all**: cells D and C inject no directive, and
their misroutes have no causal path to any treatment. The live set is:

> **L05, R01, R02, R03, R04, N02, N03, N04** — one cell-L item, all four cell-R
> items, three of four cell-N items.

Asserted by test (`test_route_dependence_is_confined_to_the_cells_that_inject_a_directive`)
so this scoping cannot quietly drift.

### A.1 Why each item misroutes

Two mechanisms, both in the classifier, both systematic:

1. **DETERMINISTIC needs an operator between two numbers.** `_ARITH_PATTERNS`
   matches `12 + 5`, `17 multiplied by 23`, and similar. A word problem whose
   quantities are separated by prose matches nothing, so it falls to the
   EMPIRICAL default. This is every cell-R item and N02/N03.
2. **Entity vetoes then block DETERMINISTIC even when arithmetic is found.**
   R01 trips `current-state framing` on the word "now"; R02 trips
   `proper noun present` on "March" and "Sunday". A calendar question cannot
   avoid month names.

Plus, for the two inert items, a third: `\bwhich\b.*\bfirst\b` reads "In which
year … first" as choice framing, and `\bbest\b` reads "Best Picture" as an
evaluative comparative — both NORMATIVE at **0.90 confidence**, i.e. confidently
wrong rather than hedged.

### A.2 Option B tested rather than assumed

The operator's preference was to establish whether rewording can fix this without
changing the substantive questions. Candidate rewrites were run through the real
classifier. Result:

| Item | Cleanly rewordable? | Evidence |
|---|---|---|
| **L05** | **Yes** | "In *which* year" → "In *what* year" routes EMPIRICAL. Pure surface change; the question, its answer, and its construct are untouched. |
| D04, C02 | n/a | Inert — no directive arm. C02 is in any case *not* cleanly rewordable: every variant naming "Best Picture" fires the evaluative pattern, and the only variant that routes correctly replaces the award's name with "the top prize", which makes the referent ambiguous. |
| **R01** | **No** | Routes DETERMINISTIC only as *"Calculate: start from 240 multiplied by 5/8, then subtract 45, then add one third of that result."* That **hands the solver the decomposition** — which is the multi-step reasoning the item exists to measure. It converts an E2 item into an arithmetic-execution item. |
| **R02** | **No** | No variant reaches DETERMINISTIC. "March" and "Sunday" trip the proper-noun veto, which demotes the item even when a compute verb is present. A calendar question cannot drop month names. |
| **R03, R04** | **No, not without a construct change** | Route correctly only with a prepended *"Calculate the remaining time."* / *"Compute the count."* That is a task-type cue inserted into the stimulus. It is identical across conditions, so it is not a between-condition confound — but it changes the baseline task and makes the items less representative of how such questions arrive. |
| **N02, N03** | **No** | String inspection and sorting are not arithmetic. The classifier has no pattern that could fire, under any phrasing. |
| **N04** | **No, not without signposting** | Routes DEFINITIONAL only as *"**By definition,** how many days does a Gregorian leap year contain?"* — a cue that tells the solver the question's type, which is a fragment of the treatment inserted into the stimulus. |

**Conclusion on B: it fixes 1 of the 8 live items cleanly.** Four more are
fixable only by changing the construct, and three are unfixable at any phrasing.
Rewording cannot rescue cell R, which is where E2 lives.

### A.3 The options, quantified

Item counts are after the frozen scout's exclusions (D01, D02). k is 5 in cells
L/R/D and 3 in U/N/C, as in plan §6.

| Option | L | R | D | U | N | C | Trials | Dead cells |
|---|---|---|---|---|---|---|---|---|
| **A** — override the 8 | 6/6 | 4/4 | 3/5 | 4/4 | 4/4 | 2/2 | **348** | none |
| **B1** — reword only what is clean, exclude the rest | 6/6 | **0/4** | 3/5 | 4/4 | 1/4 | 2/2 | 261 | **R** |
| **B2** — reword including construct changes, exclude the impossible | 6/6 | 3/4 | 3/5 | 4/4 | 2/4 | 2/2 | 315 | none |
| **C** — exclude the 8 | 5/6 | **0/4** | 3/5 | 4/4 | 1/4 | 2/2 | 241 | **R** |
| **D** — routing as a crossed within-item factor on the 8 | 6/6 | 4/4 | 3/5 | 4/4 | 4/4 | 2/2 | **382** | none |

### A.4 Statistical sensitivity, computed rather than asserted

Two numbers that constrain every option, and one of which contradicts plan §6.

**Per item, k=5 versus k=5 (Fisher exact, one-sided):**

| Treatment | Control | Shift | p |
|---|---|---|---|
| 2/5 | 0/5 | 0.4 | 0.222 |
| 3/5 | 1/5 | 0.4 | 0.262 |
| 4/5 | 0/5 | 0.8 | **0.024** |
| 5/5 | 1/5 | 0.8 | **0.024** |

Plan §6 claims a per-item MDE of 0.4. **That is not a significance threshold.** A
0.4 shift at k=5 lands at p ≈ 0.22–0.26. Only a shift of **0.8** is individually
significant. §6's figure is a descriptive detection threshold and must be
relabelled as one.

**Per cell, direction consistency across items (sign test, null p=0.5):**

| Items | Best achievable p (every item agrees) |
|---|---|
| 3 | 0.125 — cannot reach 0.05 |
| 4 | 0.0625 — cannot reach 0.05 |
| 5 | 0.031 |
| 6 | 0.016 |

**Only cell L can reach conventional significance on direction-consistency, and
only if 5 or 6 of its items agree.** Cells R (4), D (3), U (4), N (4) and C (2)
cannot, under *any* option — this is a property of the plan's item counts, not of
the D1 decision. It is a §6 claim that must be weakened regardless.

### A.5 The seven criteria, per option

| | A (override) | B1 (clean reword) | B2 (reword+construct) | C (exclude) | D (crossed factor) |
|---|---|---|---|---|---|
| **Surviving items** | 23 | 20 | 22 | 19 | 23 |
| **Trials** | 348 | 261 | 315 | 241 | 382 |
| **Power** | unchanged from §6-as-corrected | cell R gone; E2 untested | cell R at 3 items, best p=0.125 | cell R gone; E2 untested | unchanged, plus a new within-item contrast |
| **Estimand** | directive efficacy **under correct routing** (θ_directive) | θ_directive on a battery that no longer covers reasoning | θ_directive on partly-rewritten items | θ_system on whatever survives | **both** θ_directive and θ_system, and their difference |
| **New bias introduced** | removes the router's own failure mode from the measurement; breaks comparability with exp001/exp002, which measured θ_system | construct drift on the one rewritten item is nil, but selection is now correlated with classifier behaviour | **construct drift**: R01-style rewrites hand over the decomposition; prefixes insert task-type cues | **selection on instrument behaviour** — items are dropped for a property of the classifier, not of the item | none identified; adds analytic complexity |
| **Independent of solver outcomes?** | **yes** — routing is deterministic code | yes | yes | yes | yes |
| **Changes the mechanism tested?** | yes: from "system including routing" to "directive content" | yes: E2 is dropped entirely | partly: cell R measures a cued variant | yes: E2 dropped | **no** — it measures both, and separates them |
| **Representativeness** | *worse*: real deployments route with the classifier | worse: the battery loses its reasoning items | worse: cued arithmetic is not how such questions arrive | worse: items selected by classifier behaviour | *best*: the routed arm is exactly the deployed behaviour |

---

## B. Recommended D1 decision

**Option D — add routing as a crossed, within-item factor on the eight live
items.** On each, the existing directive arm is run twice: once with the
directive the classifier selects (`*_routed`) and once with the directive the
item's specification predicts about (`*_intended`). +34 trials, 382 total.

Justification, in order of weight:

1. **It converts the problem into a measurement.** Every other option makes a
   choice *about* routing. D measures routing's contribution directly: within
   item, within model, same prompt but for the injected block. For cell R that
   contrast is "does the correct directive beat the incorrect one on arithmetic?"
   — arguably the single most informative comparison available anywhere in the
   battery, and none of A, B or C can make it.
2. **It preserves comparability with exp001 and exp002**, which measured the
   system *including* the classifier. Option A silently changes the estimand
   mid-programme, so an exp003a null could not be compared with exp001's effect.
   Under D the routed arm remains directly comparable.
3. **It is the only option that does not throw away either estimand.** A gives up
   θ_system; B and C give up cell R and therefore E2.
4. **Its cost is small and known**: +34 trials, +10%.

Its honest costs: more conditions on an already-underpowered design, so the
routed-vs-intended contrast is **descriptive** at these item counts (best
achievable p on cell R's four items is 0.0625); and the analysis plan grows an
arm that must be pre-registered rather than explored.

**If the operator prefers to avoid the added complexity**, the fallback is A —
override — and then §C's language constraint becomes mandatory rather than merely
advisable. B1 and B2 are not recommended: B1 and C both kill cell R, and B2 buys
cell R back only by handing the solver the reasoning the cell exists to measure.

**One free change to adopt under any option:** reword L05 from "In which year" to
"In what year". It is a pure surface change, the construct is untouched, and it
removes one item from the disputed set at no cost. Under D it is unnecessary but
harmless; recorded so the choice is deliberate rather than forgotten.

---

## C. Routing causal analysis

### C.1 The chain

    q ──► C(q)=claim type ──► d = D[C(q)] ──► prompt P(q,d) ──► response Y ──► score S
          (classifier)         (directive)                        ▲
                                                                  │
                                            tools ────────────────┘   (only where a
                                            judge ────────────────┘    condition allows)

### C.2 Two estimands, which are not the same quantity

* **θ_system** = E[ S(d = D[C(q)]) − S(d = ∅) ] — what the deployed epistemic
  layer does, classifier included. This is what exp001 and exp002 measured.
* **θ_directive** = E[ S(d = D[c\*(q)]) − S(d = placebo) ], where c\* is the
  correct claim type — what the directive's *content* does when it is the right
  directive.

They are related through routing accuracy α:

    θ_system  ≈  α · θ_directive  +  (1 − α) · θ_wrong-directive

θ_directive is therefore an **upper bound** on the per-item contribution of the
directive content, and α is a separate multiplier that must be estimated
separately.

### C.3 Is routing part of the mechanism?

**It is part of the deployed system, and it is not part of the hypothesis
exp003a tests.** The eight competing explanations E1–E8 are all propositions
about what the *directive text* does relative to a length- and format-matched
control: latent-knowledge access, reasoning improvement, stochastic variation,
prompt length, format prescription, retrieval benefit, retrieval displacement,
judge phrasing. None of them is a proposition about classification accuracy. The
classifier is an **upstream selector** that determines which treatment is
administered — a moderator of the treatment's delivery, not the treatment.

This is why an override is methodologically legitimate *in principle*: it is the
standard move of administering the intended treatment in order to estimate the
treatment effect, leaving delivery fidelity to be estimated separately. It is the
difference between "does this drug work" and "does this prescribing system work".

It becomes **illegitimate** the moment the resulting number is reported as
θ_system — which is exactly what would happen if exp003a's headline were compared
against exp001's without the distinction being stated.

### C.4 The distinction, stated as the operator asked

* *"The router successfully identifies the intended treatment"* — a claim about
  α. **This experiment does not measure it, under any option.** The 60% agreement
  figure is agreement on 25 items authored for specific diagnostic properties,
  not a sample from any task distribution. What the screen does establish is
  qualitative and does generalise: the classifier has two **identified systematic
  failure modes** — word problems never reach DETERMINISTIC, and temporal
  superlatives read as evaluative at high confidence. Failure *modes* transfer;
  the *rate* does not.
* *"The experiment deliberately bypasses the router to test the treatment
  itself"* — a claim about θ_directive. This is what an override measures, and it
  must be labelled as such wherever it appears.

Option D is recommended precisely because it does not force the choice: it
estimates θ_directive on the intended arm, θ_system on the routed arm, and their
within-item difference is the routing cost on these items.

---

## D. D2 — the knowledge probe: a correction

**The knowledge probe has not been dispatched.** The premise that it had is
incorrect, and I am not able to report results from it.

Verified just now:

* `runs/screens/knowledge_probe.json` — **does not exist**
* `runs/exp003a/` — **does not exist**; no answers, grades or database anywhere
* `lab.screens.knowledge_screen` returns `NOT_SCREENED` for **25 of 25** items
* the preflight reports `screens_complete` as **BLOCKED** for that reason

No solver trial has been dispatched at any point in steps 3, 4 or 5. The ~125
figure was my own estimate of what the probe *would* cost (25 items × k=5,
baseline only), stated in the step-5 readiness report under blocker D2.

### The freeze discipline, audited as if it had run

The five properties asked about are all in place *in advance*, which is the only
time they can be:

| Property | Status |
|---|---|
| Thresholds frozen before results are observed | **Yes.** `CEILING = 0.90`, `FLOOR = 0.10`, `PROBE_REPLICATES = 5` are module constants in `lab/screens.py`, committed at 8da1b92, before any probe exists. A test asserts their values. |
| Results cannot modify thresholds retroactively | **Structurally.** `knowledge_screen()` takes the probe as an argument and compares against the constants; there is no code path by which a result adjusts a threshold. Changing one is a source edit, which changes `SCORING_FREEZE`'s neighbours and shows in the diff. |
| Probe cannot leak into the battery or treatments | **Yes.** The probe is `baseline` only — no directive, no placebo, no `A_only` — so it exercises no treatment text. It reads the battery and writes only `runs/screens/knowledge_probe.json`. Neither the battery nor `lab/treatments.py` reads that path. |
| Separated from solver-trial results | **Yes, by location and by schema.** Probe output lives in `runs/screens/`; experiment results live in `runs/<exp>/results.db`. The preflight's `no_solver_contamination` check fails if `runs/exp003a/` acquires answers, grades or a database. |
| Not used to select favourable items after the fact | **Cannot be, as specified.** The rule is symmetric and mechanical: exclude at ≥0.90, exclude at ≤0.10, keep otherwise. It has no access to any treatment arm — it only sees `baseline` — so it cannot preferentially retain items where the directive happens to help. |

**Actual screen outcome: none. Items affected: none yet.** Two items were
authored as deliberate ceiling-band candidates and are the most likely to be
excluded when it runs — **L06** (Zambezi; likely at ceiling) and **D05**
(Declaration wording; the easiest cell-D item). If L06 goes, cell L falls to 5
items and its best achievable consistency p moves from 0.016 to 0.031 — still the
only cell that can reach 0.05. If D05 goes, cell D falls to 2 items and can no
longer support a direction claim at all.

Nothing in the battery has been altered on the basis of the probe, because there
is no probe.

---

## E. FD-11 causal analysis — and a correction to what I wrote

### E.1 The diagram for the primary (cell R) comparison

    Z (condition: baseline / directive_placebo / directive_only)
     │
     ├──► P (prompt: length- and format-matched across arms by construction)
     │     │
     │     ├──► K (internal computation: how much serial work is done)
     │     │     │
     │     │     ├──► L (response tokens / written intermediate steps)   ◄── observable
     │     │     │
     │     │     └──► A (answer)
     │     │            │
     │     │            └──► S (score: deterministic grader, no judge)
     │     │
     U ───┴──► L,  A,  S      U = item difficulty and item-specific properties

Where the other channels could enter, and why they do not here:

* **Retrieval / external information** — enters only through a tool-bearing
  condition. Cell R has none: every arm is closed-book. Path absent.
* **Repeated attempts** — would enter as a max over dispatches. Cell R is single
  dispatch and the k=5 replicates are scored **independently**, never as a best-of.
  Path absent.
* **Judging** — would enter at A → S. Cell R is graded by exact numeric and
  string match. Path absent, which is why cell R is `outcome_type: deterministic`
  and eligible for PRIMARY under the tier wall.
* **Tools of any other kind** — absent by sandbox, verified behaviourally.

### E.2 What kind of variable is response length?

**L is a mediator and a post-treatment variable. It is not a confound.**

* Not a confound: a confound is a common cause of treatment and outcome. Z is
  *assigned*, so nothing causes Z. There is no back-door path from Z to S to
  block.
* Post-treatment: L is caused by Z (the directive's "show the steps" instruction
  is precisely an instruction to increase L).
* Mediator: L sits on Z → K → L → A → S. Part of the directive's total effect, if
  any, flows through it.

**Therefore conditioning on L is wrong for the primary estimand, twice over:**

1. It removes the portion of the total effect that flows through L, so the
   remainder is a *direct* effect — a different quantity, identified only under
   assumptions (no unmeasured mediator–outcome confounding) that do not hold here.
2. It opens a collider path. U (item difficulty) causes both L and S. Conditioning
   on L, a collider on Z → L ← U → S, induces a spurious association between Z and
   S of unknown sign. The "adjusted" estimate can be biased *away* from zero as
   easily as toward it.

**This corrects what FD-11 currently says.** FD-11 records the response-token
covariate as "adopted now" and describes it as a weak bound. That is too generous:
it is not a weak bound, it is a biased one, and adopting it would be exactly the
error the operator warned against — conditioning on a variable because it is
measurable. FD-11 must be amended before freezing.

### E.3 What to do instead

* **Primary estimand: the total effect, unconditioned.** Z → S, with L not in the
  model.
* **L reported as a manipulation check**, descriptively: did the directive
  actually change response length, and by how much? A directive that did not move
  L cannot have worked *through* L, which is informative and costs nothing.
* **Decomposition requires exogenous manipulation of L**, not adjustment for it.
  That is `elaboration_only`: an arm that moves L with no epistemic content.
  `elaboration_only − directive_placebo` estimates the compute path;
  `directive_only − elaboration_only` estimates the content path with compute
  held at a comparable level. This is a design solution, and it is the only sound
  one available.

### E.4 What the primary R-cell claim can legitimately be

Without `elaboration_only`:

> **"Under a closed-book, single-dispatch protocol with k = 5 independent
> replicates and a word-count-, structure- and format-matched placebo, injecting
> directive X changed the per-item correct-answer rate on N arithmetic and logic
> items by Δ, with the directive also changing mean response length by ΔL."**

That is the whole of it. Specifically **not** supportable:

* *"Directive X improves reasoning"* — the compute path is unseparated.
* *"Directive X improves reasoning efficiency"* — nothing measures effort per
  unit of correctness.
* any claim generalising beyond arithmetic and calendar/counting items.
* any claim at conventional significance from a 4-item cell, whose best
  achievable consistency p is 0.0625.

With `elaboration_only` adopted, the stronger claim becomes available:

> "…and the change was not accounted for by the increase in response length
> alone, since a length-matched arm carrying only a stepwise-working instruction
> produced Δ_e < Δ."

---

## F. C3 — battery-construction bias

### F.1 What we can honestly say

| Quantity | Value |
|---|---|
| Items in `diagnostic_v1` | 25 |
| Authored by the same process that authored the mechanism | **25 (100%)** |
| Drawn from an external source | 0 |
| Authored by a party blind to the mechanism | 0 |
| Task axes that vary across the battery | 6 of 6 |
| Task axes collinear with `claim_type` | 0 of 6 |

The last two rows establish that the axes **carry information the router does not
already have**. They establish nothing whatever about independence from the
mechanism's design, and must never be reported as if they did. Axis variation is
a property of the labelling; independence is a property of the *authoring
process*, and that process was not independent.

### F.2 Can an independent construction procedure be added before dispatch?

Four routes considered:

1. **External benchmark subset** (ARC, SWE-bench, MMLU) — excluded by the
   standing constraint against adding frontier capabilities, and it would be a
   substantial capability addition rather than a battery tweak.
2. **A blind author** — no party is available who has not seen the mechanism.
3. **Programmatic generation from a pre-registered schema** — the schema would
   itself be written by the same process. It moves the bias from the items to the
   generator without reducing it, while adding an appearance of objectivity.
   Actively worse than doing nothing.
4. **Replication on frozen `factual_v1`** — the one partially-independent asset.
   It was authored before the exp003 mechanism analysis and is frozen. But it was
   authored *with the layer's claim types in mind* (recorded as limitation 4 in
   the lab manual), so it is not independent either — only *less* contaminated,
   and by an unmeasured amount.

**Answer: no.** C3 cannot be honestly fixed before dispatch. It stays an explicit
limitation.

### F.3 What is proposed instead

* **A directional pre-registration, free.** If the battery is biased toward the
  mechanism, effects should be *larger* on `diagnostic_v1` than on any less
  contaminated set. Pre-register that direction now so it is a prediction rather
  than a later rationalisation.
* **An optional bias probe, priced.** Replicating cell L's four-arm contrast on
  six `factual_v1` items at k=3 costs 72 trials. It would not establish
  independence — `factual_v1` is not independent — but a substantially smaller
  effect there would be evidence of fitting. Offered as an option, not
  recommended, because the comparison set is too weak to carry the weight.
* **exp004 as the real answer.** An externally-authored or blind-authored
  battery, pre-registered before anyone sees exp003a's results, is the only thing
  that retires C3. It belongs in the next experiment, not in a patch to this one.

C3 must appear in any exp003a result, in the result's own words, not in a
footnote.

---

## G. A_only / placebo verification

Implemented as `tests/test_a_only_placebo_regression.py`, deterministic, 208
assertions across all 25 items. Suite is now **963 passing**, the original
130-test baseline unmodified.

| Property required | How it is proved |
|---|---|
| Carrier text identical | Every bullet but the last is the placebo's text verbatim; section headers identical; line and paragraph counts identical. |
| Only the treatment-bearing portion differs | The set of differing line indices is a subset of {header, prose slots, last bullet} on every item — asserted per item, not in aggregate. |
| Length and axis matching hold | Word count within 10% of the routed directive, and bullets, section headers, inline headers, em dashes, paragraph blocks and indent depth match **exactly** — against the directive *and* against the placebo. |
| No hidden channel through formatting or ordering | The *roles* of the differing lines never include a structural header, so the block's shape does not encode the routed type. The placebo's register word is seeded from question text and is shown to vary within a claim type, so it cannot serve as a covert label. |
| The placebo cannot become an active treatment | No generated placebo contains any `FORBIDDEN` mechanism term or any `SIZE_TERMS` response-size instruction, and no numeral appears outside the register line. A companion test asserts `A_only` *does* contain mechanism vocabulary — if it ever passed the inertness check it would have stopped carrying the treatment. |
| Deterministic | Byte-stable across calls for all 25 items. |

Four slots remain free — header, lead, last bullet, closing — because the word and
em-dash budgets must land somewhere: a framing sentence with no em dash where the
placebo's lead had one leaves a deficit the closing alone cannot always absorb
(found on U03). This is documented in the generator and asserted, not left
implicit.

---

## H. Recomputed power — conditional, not yet operative

Under the recommended option D, and after the frozen scout's exclusions:

| Cell | Items | Conditions | k | Trials | Best achievable consistency p |
|---|---|---|---|---|---|
| L | 6/6 | 4 (+1 on L05) | 5 | 125 | **0.016** |
| R | 4/4 | 3 (+1 on all four) | 5 | 80 | 0.0625 — cannot reach 0.05 |
| D | 3/5 | 4 | 5 | 60 | 0.125 — cannot reach 0.05 |
| U | 4/4 | 5 | 3 | 60 | 0.0625 — cannot reach 0.05 |
| N | 4/4 | 3 (+1 on three) | 3 | 45 | 0.0625 — cannot reach 0.05 |
| C | 2/2 | 2 | 3 | 12 | tripwire only |
| **Total** | **23/25** | | | **382** | |

**This table is not operative.** It is the consequence of a decision that has not
been taken. One operative table will be generated and committed once D1 is
resolved, and the plan's §6 figures will be replaced rather than kept alongside.

### §6 claims that must be weakened, regardless of which option is chosen

1. **"Per-item MDE 0.4"** → a 0.4 shift at k=5 gives p ≈ 0.22–0.26. Restate as a
   *descriptive detection threshold*; the per-item significance threshold at k=5
   is **0.8**.
2. **"A consistent direction across ≥3 of 6 items"** → 3 of 6 is p = 0.66 under
   the null and is not evidence of anything. Cell L reaches 0.05 only at 5/6
   (p = 0.031) or 6/6 (p = 0.016).
3. **Cells R, D, U, N and C cannot reach p < 0.05 on direction consistency at
   all**, even with unanimous agreement. Their results are **descriptive**, and
   the memo's language must say so. This is a property of the item counts chosen
   in the plan, not a consequence of D1.
4. **Cell D is REDUCED to 3 items** by the frozen scout, so the displacement
   hypothesis — the f15 follow-up that motivated much of exp003 — can now only be
   reported descriptively.

---

## I. Exact remaining blockers

| # | Blocker | Status | What clears it |
|---|---|---|---|
| **D1** | routing_consistency | **open — decision required** | The operator picks an option. Recommendation: D. Nothing implemented. |
| **D2** | screens_complete | **open — dispatch required** | The knowledge probe, ~125 trials, baseline only. Thresholds are already frozen and cannot move. |
| **D3** | power_recomputed | blocked on D1 | One operative table, replacing §6. |
| **D4** | experiment_identity | blocked on D1 and D2 | `experiments/exp003a_mechanism.yaml`, naming the three freeze fingerprints, the battery fingerprint, the egress probe date, the scout date, and the commit. |
| **D5** | git_identity | clears at dispatch | Clean tree, preflight re-run against the dispatch commit. |

Two new items this review adds:

| **D6** | FD-11 amendment | **new** | Remove the response-token covariate as an adopted analysis step; replace with total effect + manipulation check + the `elaboration_only` option. §E.2. |
| **D7** | §6 amendment | **new** | Weaken the four claims in §H before dispatch, not after. |

---

## J. Proposed final pre-registration changes

Presented for approval. **None is implemented.**

1. **D1 = option D.** Add a crossed routing factor on the eight route-dependent
   misrouted items: each existing directive arm runs as `*_routed` and
   `*_intended`. +34 trials (348 → 382). The routed arm preserves comparability
   with exp001/exp002; the intended arm estimates θ_directive; their within-item
   difference is the routing cost on these items, reported descriptively.
2. **Reword L05** from "In which year" to "In what year" — a pure surface change,
   adopted under any option.
3. **Do not reword any cell-R item**, and record why: the only rewrites that
   route correctly either hand the solver the decomposition (R01) or insert a
   task-type cue (R03, R04), and R02 cannot be rewritten at all.
4. **Amend FD-11**: the response-token covariate is withdrawn as an analysis
   step. Primary estimand is the total effect; L becomes a manipulation check;
   decomposition requires `elaboration_only`.
5. **Decide `elaboration_only`** — adopt (+20 trials, cell R claim becomes
   mechanistic) or decline (cell R claim stays at the constrained wording in
   §E.4). Either is defensible; the wording follows from the choice.
6. **Amend §6** with the four corrections in §H, before dispatch.
7. **Record α as unmeasured.** The 60% agreement figure is not an estimate of
   routing accuracy on any task distribution. What generalises is the two
   identified failure modes, not the rate.
8. **C3 stands as an explicit limitation**, with the counts in §F.1 stated in any
   result, and an externally-authored battery deferred to exp004.
9. **No dispatch** until D1, D2, D6 and D7 are cleared and the preflight answers
   YES against the dispatch commit.
