# exp003a decision packet

**Nothing here is implemented.** No option applied, no configuration written, no
battery modified, no trial dispatched. This document exists so the next
implementation pass is mechanical: executing a frozen design rather than making
design choices while coding.

**One correction to my own recommendation, up front.** The design review costed
option D at +34 trials. That was wrong. It ignored the fact that the intended
directive is **68 words shorter** than the routed one on every cell-R item
(211 → 143 words, 5 bullets → 4, budget 2 → 0). A routed-vs-intended contrast
without a matched control for each block is confounded with prompt length and
format — E4 and E5, the exact confounds this experiment exists to exclude. The
corrected costs are in §1.2, and the recommendation changes to a hybrid.

---

# Part I — §J in full

The nine proposed pre-registration changes, each with the wording as it stands
today, the wording proposed, and why.

### J1 — D1 routing decision

**Current.** No decision recorded. `docs/EXP003A_FROZEN_DECISIONS.md` FD-12 states
the problem and the three options; the preflight FAILs on `routing_consistency`.

**Proposed.** Adopt **option D′** (§1): reword L05; accept the routed directive in
cell N and label that cell's estimand θ_system; and in cell R only, cross routed
against intended with a matched placebo for each block. Total 388 trials (+40).

**Reason.** Cell R is the only cell where the directive's *content* is the
question, where the misroute is total (4 of 4), and where no rewrite exists that
does not damage the construct. It is also the only cell where paying for a
matched placebo per block is worth it.

---

### J2 — Reword L05

**Current wording** (`batteries/diagnostic_v1.yaml`, line 350):

> `In which year was the first successful human-to-human heart transplant performed?`

**Proposed wording:**

> `In what year was the first successful human-to-human heart transplant performed?`

**Reason.** `which … first` matches the classifier's choice-framing pattern and
routes the item NORMATIVE at 0.90 confidence. `what` does not. The question, its
answer, its ground truth, its difficulty and its construct are untouched — this
is a one-word surface change, verified against the real classifier. It removes
one item from the disputed set for free.

---

### J3 — Do not reword any cell-R item

**Current.** No record; the option is open by default.

**Proposed.** Record as a *rejected* option with its evidence, so it cannot be
revisited casually after results exist.

**Reason.** Tested against the real classifier:

| Item | Only rewrite that routes DETERMINISTIC | Why it is rejected |
|---|---|---|
| R01 | *"Calculate: start from 240 multiplied by 5/8, then subtract 45, then add one third of that result."* | Hands the solver the **entire decomposition**. R01's construct is multi-step reasoning; the rewrite converts it into arithmetic execution. This is not a rewording, it is a different item measuring a different thing. |
| R02 | **none exists** | "March" and "Sunday" trip the proper-noun entity veto, which demotes the item out of DETERMINISTIC even when a compute verb is present. A calendar question cannot drop month names. |
| R03 | prefix *"Calculate the remaining time."* | Inserts a **task-type cue** into the stimulus. Identical across conditions, so not a between-condition confound — but it tells the solver what kind of problem it is facing, which is a fragment of the treatment moved into the baseline, and it makes the item less representative of how such questions arrive. |
| R04 | prefix *"Compute the count."* | Same. |

---

### J4 — Amend FD-11: withdraw the response-token covariate

**Current wording** (`docs/EXP003A_FROZEN_DECISIONS.md`, lines 515–523):

> **Smallest change that BOUNDS it without new trials** — free, and adopted now:
> Response tokens are already recorded per dispatch (step 3). Every cell-L and
> cell-R contrast is reported with a **response-token covariate**, and any
> contrast whose effect is absorbed by it is reported as NOT ESTABLISHED as a
> reasoning effect. This is strictly weaker than the arm, and the reason must be
> stated wherever it is used: response length is a **mediator** of the treatment,
> not a pre-treatment covariate, so conditioning on it can under-correct or
> over-correct and cannot identify the direct effect. It bounds; it does not
> measure.

**Proposed wording:**

> **There is no free bound. The covariate is withdrawn.** Response length is a
> post-treatment mediator, and item difficulty causes both it and the outcome.
> Conditioning on it (a) removes the portion of the total effect that flows
> through it, which changes the estimand from a total to a direct effect
> identified only under assumptions that do not hold here, and (b) opens a
> collider path `Z → L ← U → S`, which can bias the estimate **away from** zero as
> easily as toward it. An adjusted estimate would therefore be not a weak bound
> but a biased one.
>
> Response length is instead reported as a **manipulation check**: did the
> directive change it, and by how much. A directive that did not move response
> length cannot have worked through response length, which is informative and
> costs nothing. Decomposition requires exogenous manipulation of length, not
> adjustment for it — see `elaboration_only`, deferred to a follow-up experiment.

**Reason.** The original wording called the covariate "strictly weaker" and
adopted it. "Weaker" understates the problem: it is biased in an unknown
direction. Adopting a measurable variable because it is measurable is exactly the
error to avoid, and the current text would have led the analysis into it.

---

### J5 — `elaboration_only` deferred, not adopted

**Current.** FD-11 offers it as the "smallest change that MEASURES" the compute
confound, at +20 trials, with the decision left open.

**Proposed.** **Do not add it to exp003a.** Record it as a specified,
pre-written, frozen follow-up (exp003d or exp004), and constrain the cell-R claim
accordingly (§3.6, §8).

**Reason.** Adding it would change cell R's estimand mid-design, and the operator
has directed that it not be added absent a compelling reason that leaves the
estimand intact. There is no such reason: its whole purpose is to decompose the
estimand. Deferring costs only claim strength, and the constrained claim is
stated exactly in §8 so nothing is lost silently.

---

### J6 — Amend plan §6

**Current wording** (`docs/EXP003_IMPLEMENTATION_PLAN.md`, lines 286–291):

> **Restated plainly:** exp003 is powered to detect a mechanism that changes an
> individual item's outcome rate by roughly 0.4 or more. It is **not** powered to
> detect a uniform few-point battery-wide shift, and the battery mean is not a
> primary outcome. If the effect we care about is smaller than that, this design
> cannot see it and the design must change before solver calls are spent.

**Proposed wording:** replaced wholesale by §3.5 of this packet.

**Reason.** "Powered to detect … 0.4 or more" is false as a statistical claim. At
k=5, a 0.4 shift gives Fisher one-sided p ≈ 0.22–0.26. The threshold for p < 0.05
is **0.8**. And on direction-consistency, cells with fewer than five items cannot
reach p < 0.05 even with unanimous agreement. §6 conflates descriptive resolution
with statistical significance; §3.5 separates them.

---

### J7 — Record routing accuracy as unmeasured

**Current.** The 60% agreement figure appears in the readiness report and FD-12
without an explicit statement of what it is not.

**Proposed.** Add to FD-12: *"The 15/25 agreement figure is agreement on a battery
authored for specific diagnostic properties. It is **not** an estimate of routing
accuracy on any task distribution, and may not be cited as one. What generalises
is the two identified failure modes — word problems never reach DETERMINISTIC,
and temporal superlatives route NORMATIVE at high confidence — not the rate."*

**Reason.** A percentage in a report gets quoted. Without this sentence, 60% will
eventually be read as the classifier's field accuracy, which nothing here measures.

---

### J8 — C3 frozen as a limitation

**Current.** C3 appears in the readiness report as an open risk.

**Proposed.** Freeze it with the counts stated in §5, and require them to appear
in any exp003a result rather than in a footnote.

**Reason.** Four routes to independence were considered and all rejected (§5.2).
None can be had before dispatch without adding a forbidden capability or
manufacturing the appearance of independence.

---

### J9 — No dispatch until the gate clears

**Current.** The readiness report lists D1–D5.

**Proposed.** The gate is: D1, D2, D6, D7 resolved; one operative power table
committed; `experiments/exp003a_mechanism.yaml` written and naming every
fingerprint; preflight answering YES against the dispatch commit.

**Reason.** Unchanged in substance; restated so the gate is one list rather than
several.

---

# Part II — Decision Packet

## 1. D1 — routing crossed factor, fully specified

### 1.1 Scope

Ten items misroute; **eight** are route-dependent (a routed directive or the
routed framing is actually injected). D04 and C02 sit in cells D and C, which
inject neither, and need no remedy. Asserted by test.

### 1.2 The length problem, and what it costs

The intended directive is shorter than the routed one on every affected item:

| Item | Routed | Intended | Words | Bullets | Budget |
|---|---|---|---|---|---|
| R01–R04, N02, N03 | EMPIRICAL | DETERMINISTIC | 211 → 143 (**−68, −32%**) | 5 → 4 | 2 → 0 |
| N04 | EMPIRICAL | DEFINITIONAL | 211 → 167 (−44) | 5 → 5 | 2 → 1 |
| L05 | NORMATIVE | EMPIRICAL | 156 → 185 (+29) | 4 → 4 | 0 → 2 |

A bare routed-vs-intended contrast therefore differs in prompt length, bullet
count and budget line simultaneously. Costed properly:

| Variant | Trials | Δ | Verdict |
|---|---|---|---|
| D naive — +1 arm, no matched control | 382 | +34 | **rejected**: confounded with E4/E5 |
| D full — matched placebo per block on all 8 | 412 | +64 | sound but pays for cells that do not need it |
| **D′ hybrid — reword L05, accept routed in N, cross R with matched placebos** | **388** | **+40** | **recommended** |

### 1.3 The recommended structure — option D′

**Cell R (4 items, k=5, 5 conditions, 100 trials):**

| Condition | Block injected | Purpose |
|---|---|---|
| `baseline` | none | floor |
| `placebo_routed` | inert carrier matched to the **routed** block | control for the routed arm |
| `placebo_intended` | inert carrier matched to the **intended** block | control for the intended arm |
| `directive_routed` | the EMPIRICAL directive the classifier selects | θ_system arm |
| `directive_intended` | the DETERMINISTIC directive the spec predicts about | θ_directive arm |

Both placebos come from the existing generator, each matched to its own block on
word count within 10% and on bullets, headers, paragraph blocks and em dashes
exactly. This makes the routing contrast a **difference in differences**:

    θ_routing = (directive_routed − placebo_routed) − (directive_intended − placebo_intended)

which is length-controlled on both sides, whereas the raw difference is not.

**Cell L:** L05 reworded (J2); all six items then route as declared; conditions
unchanged at four. 120 trials.

**Cell N:** unchanged at three conditions, 36 trials. The routed directive is
accepted, and **cell N's estimand is relabelled θ_system**. This is not a
concession: cell N asks whether the deployed system suppresses unnecessary tool
use, and the deployed system delivers the routed directive. The routed budget of
2 on items needing 0 searches *is* the deployed behaviour, and measuring it is the
point.

**Cells D, U, C:** unchanged.

### 1.4 Randomisation and dispatch order

There is no randomisation in the design today, and the preflight currently
records "no seed to record". **Under D′ that must change.** A paired within-item
contrast is vulnerable to time-correlated drift — a model version change or a
capacity event mid-run would land unevenly across arms if arms are dispatched in
blocks.

**Proposed:** the full dispatch list (item × condition × replicate) is shuffled
once with a **recorded seed**, committed in the experiment configuration before
dispatch, and dispatched in that order. The seed becomes part of the experiment
identity, and `preflight.determinism` is extended to verify that the same seed
reproduces the same order.

### 1.5 Trial counting

`DISPATCH_COUNT` remains the single source. Every condition in cell R is a single
dispatch, so cell R's 100 trials are 100 dispatches. The multi-dispatch arms
remain confined to cell D (`search_selfcheck` = 2, `search_independent` = 3), and
the cost table continues to report dispatches, not trials, for cost.

### 1.6 Analysis — separate, always

`directive_routed` and `directive_intended` are **never pooled**. They are
different treatments. Any table that averages them is a reporting error, and the
report must fail rather than produce the average.

### 1.7 Is routed-vs-intended itself a pre-registered estimand?

**Yes**, as a pre-registered **secondary, descriptive** estimand (θ_routing,
§8.3). It is secondary because cell R has four items, whose best achievable
sign-test p is 0.0625 — it cannot reach conventional significance under any
outcome. Pre-registering it stops it becoming an exploratory finding dressed up
as a planned one.

### 1.8 Does this change the interpretation of E1–E8?

No explanation is added or removed. Two are sharpened:

* **E2 (reasoning improvement)** is now tested with the *correct* directive
  present, which it was not before — the intended arm is the only place E2 was
  ever testable.
* **E4/E5 (length, format)** gain a second control per block, so the routing
  contrast does not smuggle them back in.

The remaining six are untouched: cells L, D, U, N, C carry E1, E3, E6, E7, E8 as
specified.

### 1.9 Resulting counts

| Cell | Items | Conditions | k | Trials |
|---|---|---|---|---|
| L | 6/6 | 4 | 5 | 120 |
| R | 4/4 | **5** | 5 | **100** |
| D | 3/5 | 4 | 5 | 60 |
| U | 4/4 | 5 | 3 | 60 |
| N | 4/4 | 3 | 3 | 36 |
| C | 2/2 | 2 | 3 | 12 |
| **Total** | **23/25** | | | **388** |

---

## 2. Why A, B and C were rejected — retained record

| Option | What it does | Why rejected |
|---|---|---|
| **A — override** | Force the intended directive everywhere; 348 trials. | Silently changes the estimand from θ_system to θ_directive **mid-programme**, so an exp003a null could not be compared with exp001/exp002, which measured the system including the classifier. It also removes the router's own failure mode from the measurement — making the mechanism look better by deleting a real failure source. Defensible only with the language constraint of §8 made mandatory; strictly dominated by D′, which measures both. |
| **B — reword** | Rewrite items until the classifier agrees. | Tested, not assumed. Fixes **1 of 8** cleanly (L05). Adopted for that one item as J2. Cannot rescue cell R — see below. |
| **C — exclude** | Drop the misrouted items; 241 trials. | **Kills cell R entirely (0/4)** and reduces cell N to one item. E2 becomes untested — not refuted, untested. It also selects items on a property of the *instrument* rather than of the item, which is a selection effect with no principled stopping point. |
| **D′ — crossed** | §1.3; 388 trials. | Recommended. |

### 2.1 Why the R-item rewrites were rejected, specifically

This is the part most likely to be revisited later, so the reasoning is recorded
in full.

The rewrites that route correctly do so by inserting information the item exists
to withhold:

* **R01** measures whether the solver can decompose a three-step word problem.
  The rewrite that routes correctly — *"start from 240 multiplied by 5/8, then
  subtract 45, then add one third of that result"* — **states the decomposition
  in the prompt**. What remains is arithmetic execution. The construct changes
  from "can it find the steps" to "can it do the steps", and every cell-R
  prediction, distractor and discriminator was written for the former.
* **R03 and R04** need a *"Calculate the remaining time."* / *"Compute the count."*
  prefix. This is milder — the cue is identical across conditions, so it is not a
  between-condition confound. But it is a **task-type cue**, which is a fragment
  of what the DETERMINISTIC directive itself supplies ("This is DETERMINISTIC —
  compute it"). Putting it in the stimulus moves part of the treatment into the
  baseline and shrinks the effect the cell is trying to detect, in an unknown and
  unmeasured amount.
* **R02** has no rewrite at all.

Rewriting three of four cell-R items in three different ways, each changing the
construct by a different unmeasured amount, would leave a cell whose items are no
longer comparable to each other. That is worse than either accepting the misroute
or measuring it.

---

## 3. Power and inference — what §6 claims versus what the mathematics supports

### 3.1 The four things §6 currently conflates

| Concept | What it is | What §6 says |
|---|---|---|
| Descriptive effect-size resolution | the smallest difference the design can *display* | conflated with the next row |
| Statistical significance | the smallest difference that would be unlikely under the null | claimed at 0.4; actually 0.8 |
| Confidence / uncertainty | how wide the interval around a per-item rate is | not mentioned |
| Direction-consistency | how many items must agree for the pattern to mean something | claimed at ≥3 of 6; that is p = 0.66 |

### 3.2 Per-item significance, k = 5 vs k = 5 (Fisher exact, one-sided)

| Treatment | Control | Shift | p |
|---|---|---|---|
| 2/5 | 0/5 | 0.4 | 0.222 |
| 3/5 | 1/5 | 0.4 | 0.262 |
| 4/5 | 2/5 | 0.4 | 0.262 |
| 3/5 | 0/5 | 0.6 | 0.083 |
| 5/5 | 2/5 | 0.6 | 0.083 |
| **4/5** | **0/5** | **0.8** | **0.024** |
| **5/5** | **1/5** | **0.8** | **0.024** |
| 5/5 | 0/5 | 1.0 | 0.004 |

### 3.3 Per-item uncertainty (Clopper–Pearson 95%)

| Observed | Rate | 95% CI | Width |
|---|---|---|---|
| 0/5 | 0.0 | [0.00, 0.52] | 0.52 |
| 2/5 | 0.4 | [0.05, 0.85] | 0.80 |
| 3/5 | 0.6 | [0.15, 0.95] | 0.80 |
| 5/5 | 1.0 | [0.48, 1.00] | 0.52 |
| *k=3:* 3/3 | 1.0 | [0.29, 1.00] | 0.71 |

**Even a perfect 5/5 has a lower bound of 0.48.** No per-item rate in this design
is known to better than about ±0.4.

### 3.4 Direction-consistency by surviving item count

| Items | Best achievable p (unanimous) | Can reach 0.05? |
|---|---|---|
| 2 | 0.250 | no |
| 3 | 0.125 | no |
| 4 | 0.0625 | no |
| **5** | **0.031** | yes |
| **6** | **0.016** | yes |

Applied to the design as it now stands: **cell L (6) is the only cell that can
reach conventional significance.** R (4), D (3), U (4), N (4), C (2) cannot, under
any option and any outcome.

### 3.5 The replacement for §6

> **What this design can support.**
>
> **Confirmatory, one cell only.** Cell L, six items, k = 5, four conditions. If
> five or six items move in the same direction, that pattern is unlikely under
> the null (p = 0.031 or 0.016) and may be reported as a confirmatory result about
> E1 under the closed-book single-dispatch protocol. Nothing else in the battery
> can produce a confirmatory result.
>
> **Descriptive everywhere else.** Cells R, D, U, N and C report effect sizes,
> per-item rates with Clopper–Pearson intervals, and direction counts. They may
> not report significance, and their language must be descriptive: "on these
> items, X was higher than Y by Δ", never "X improves Y".
>
> **Per-item resolution.** The design displays per-item shifts of about 0.2 and
> above. It reaches p < 0.05 on a single item only at a shift of **0.8**. A 0.4
> shift — the figure §6 previously called the MDE — sits at p ≈ 0.22–0.26 and is
> a *descriptive detection threshold*, not a significance threshold.
>
> **Uncertainty.** No per-item rate is known to better than roughly ±0.4 at k = 5,
> or ±0.45 at k = 3. Every per-item figure ships with its interval.
>
> **Exploratory.** Anything not named above — including θ_routing, the cell-U
> mode distribution, and every cross-cell comparison — is exploratory, is labelled
> as such, and generates hypotheses for a later experiment rather than conclusions
> in this one.
>
> **The battery mean is not an outcome** and is not reported.

### 3.6 If the retained item counts change again

The knowledge screen has not run. If it excludes items, the consequence is
mechanical and is pre-committed here:

| Cell | Now | If it loses 1 | If it loses 2 |
|---|---|---|---|
| L (6) | confirmatory, p ≥ 0.016 | 5 items, p ≥ 0.031 — **still confirmatory, barely** | 4 items — **confirmatory capability lost; cell L becomes descriptive and exp003a has no confirmatory cell at all** |
| R (4) | descriptive | 3, p ≥ 0.125 | 2, p ≥ 0.25 |
| D (3) | descriptive | 2, p ≥ 0.25 | 1 — no direction claim available |
| U (4), N (4) | descriptive | 3 | 2 |
| C (2) | gate | 1 — gate rests on one item | 0 — **gate fails; no search result in the run may be interpreted** |

**Pre-committed rule:** if cell L falls below five items, exp003a has no
confirmatory cell, and that fact is stated in the report's first paragraph rather
than discovered in its discussion.

---

## 4. FD-11 — final causal interpretation, confirmed

### 4.1 The chain

    Z (condition assigned)
     └─► P (prompt; length- and format-matched across arms by construction)
          └─► K (internal computation: how much serial work is done)
               ├─► L (response tokens / written intermediate steps)   ← observable
               └─► A (answer) ─► S (score; deterministic grader, no judge in cell R)

    U (item difficulty) ─► L,  A,  S

Other channels, and why they are absent from the primary cells: **retrieval and
external information** enter only through a tool-bearing condition, and cells L
and R have none; **repeated attempts** would enter as a maximum over dispatches,
and every arm is single-dispatch with k replicates scored *independently*;
**judging** would enter at A → S, and cells L and R are graded by exact numeric
and string match.

### 4.2 Confirmed classification of response length

**L is a post-treatment mediator and a manipulation check. It is not a confound
and is not a covariate.**

* Not a confound: a confound is a common cause of treatment and outcome. Z is
  assigned; nothing causes Z; there is no back-door path to block.
* Post-treatment: L is caused by Z. The directive's "show the steps" is precisely
  an instruction to increase it.
* Mediator: L sits on Z → K → L → A → S.

### 4.3 Why conditioning on it would change the estimand and introduce bias

1. **It changes the estimand.** Conditioning removes the portion of the total
   effect flowing through L. What remains is a *controlled direct effect*, which
   is a different quantity and is identified only under an assumption of no
   unmeasured mediator–outcome confounding.
2. **That assumption fails here.** Item difficulty U causes both L (harder items
   draw longer answers) and S. So the assumption is violated by a variable we
   know exists.
3. **It opens a collider.** L is a collider on `Z → L ← U → S`. Conditioning on a
   collider induces association between Z and S that is not causal. The direction
   of the induced bias is not determined by anything we measure, so the adjusted
   estimate can be biased **away from** zero as readily as toward it.

An adjusted estimate would therefore be worse than the unadjusted one, while
looking more careful.

### 4.4 Confirmed handling

* **Primary: total effect, unconditioned.** Z → S.
* **L reported as a manipulation check**, descriptively, per arm: did the
  directive move response length, and by how much. A directive that did not move
  L cannot have acted through L.
* **`elaboration_only` is NOT added to exp003a.** It is specified, written and
  frozen in `lab/treatments.py`, and deferred to a follow-up experiment. Its
  purpose is to decompose the estimand, so adding it would change the estimand —
  which is exactly the condition the operator set for excluding it.

---

## 5. C3 — frozen as a limitation

### 5.1 The counts, to be stated in any result

| Quantity | Value |
|---|---|
| Items in `diagnostic_v1` | 25 |
| Authored by the same process that authored the mechanism | **25 (100%)** |
| Drawn from an external source | 0 |
| Authored by a party blind to the mechanism | 0 |
| Task axes that vary across the battery | 6 of 6 |
| Task axes collinear with `claim_type` | 0 of 6 |

The last two rows establish that the axes carry information the router does not
already have. They establish **nothing** about independence from the mechanism's
design. Independence is a property of the authoring process; that process was not
independent.

### 5.2 Routes to independence, considered and rejected

| Route | Rejected because |
|---|---|
| External benchmark subset (ARC, MMLU, SWE-bench) | Excluded by the standing constraint against adding frontier capabilities, and it is a capability addition rather than a battery change. |
| A blind author | No party is available who has not seen the mechanism. |
| Programmatic generation from a pre-registered schema | The schema would be written by the same process. It relocates the bias from items to generator while adding an appearance of objectivity — actively worse than doing nothing. |
| Replication on frozen `factual_v1` | Not independent either: authored with the layer's claim types in mind, recorded as limitation 4 in the lab manual. Less contaminated by an unmeasured amount, which is not a basis for a claim. |

**C3 is frozen as a limitation.** No independence is manufactured. The real
remedy — an externally- or blind-authored battery, pre-registered before anyone
sees exp003a's results — belongs to exp004.

---

## 6. D2 — knowledge probe: state verified, scope specified

### 6.1 Current state, re-verified

| Check | Result |
|---|---|
| `runs/screens/knowledge_probe.json` | **does not exist** |
| `runs/exp003a/` | **does not exist** |
| Items reporting `NOT_SCREENED` | **25 of 25** |
| Knowledge-probe trials dispatched | **0** |
| Solver trials dispatched, any experiment, steps 3–5 | **0** |
| Thresholds | `CEILING = 0.90`, `FLOOR = 0.10`, `PROBE_REPLICATES = 5` |
| Threshold provenance | module constants in `lab/screens.py`, committed 8da1b92 (2026-08-29), before any probe exists |
| Result-dependent threshold changes | **none possible** — `knowledge_screen()` takes the probe as an argument and compares against constants; no code path lets a result adjust a threshold |

### 6.2 What the probe will test

**Exactly one quantity per item:** the fraction of k = 5 `baseline` dispatches
that the deterministic grader scores correct. Nothing else. It sees no directive,
no placebo, no `A_only`, no tools.

Its purpose is inclusion, and the rule is symmetric and mechanical: exclude at
≥ 0.90 (ceiling — no headroom for any condition to move into), exclude at ≤ 0.10
(floor — the knowledge is not present to surface), keep otherwise.

**It is purely a screening operation.** It cannot favour the mechanism, because
it never observes the mechanism: it has no treatment arm to compare against.

### 6.3 The rule that matters most

**The probe's baseline results may NOT be reused as the experiment's `baseline`
arm.** This is the subtle failure and it is worth stating plainly: the probe
selects items *on their baseline performance*. Reusing that same data as the
control arm would condition the control on the selection criterion, biasing every
contrast in the experiment through regression to the mean. The experiment
dispatches its own `baseline` arm, independently, after selection.

Not run yet.

---

## 7. Experiment versus instrument qualification

### 7.1 Classification of every planned pre-dispatch trial

| Class | What it is | Planned work | Dispatches | Enters primary dataset? |
|---|---|---|---|---|
| `instrument_qualification` | establishes that the measuring apparatus behaves as described | exp003c judge calibration (**done**, 96 judge calls) | judge only | **no** |
| `retrieval_qualification` | establishes what the environment can retrieve | egress probe (**done**), frozen scout (**done**) | none — orchestrator WebSearch | **no** |
| `screen` | decides which items enter | routing screen (**done**, deterministic), knowledge probe (**not run**, ~125) | solver, baseline only | **no** |
| `treatment_validation` | establishes that a treatment text is what it claims | placebo/A_only axis tests (**done**, no dispatch) | none | **no** |
| `solver_experiment` | the primary dataset | exp003a, 388 under D′ | solver + judge | **yes — this class only** |

### 7.2 The auditable rule

1. **Every dispatch carries a `dispatch_class` assigned at preparation time**,
   stored with the trial, and hashed into the run manifest.
2. **The class is immutable.** Reclassifying a trial after its result exists is
   forbidden, and detectable, because the class is part of the manifest hash
   committed before dispatch.
3. **Storage is separated**: qualification and screening output goes to
   `runs/screens/`; the primary dataset is `runs/exp003a/results.db`. The
   preflight's `no_solver_contamination` check already fails if the experiment
   directory acquires artefacts before dispatch.
4. **The report refuses mixed aggregates.** Any figure computed over more than
   one `dispatch_class` is a test failure, not a warning.
5. **No screening dispatch may be reused as experimental data** (§6.3), even
   where the prompts are byte-identical.

Items 1, 2 and 4 are proposed and **not implemented**; 3 exists; 5 is a rule about
conduct.

---

## 8. Final estimands

Notation: per item *i*, condition *c*, score *S*. All primary quantities are
per-item and are never averaged into a battery mean.

### 8.1 θ_directive — the intended directive's effect, correctly delivered

    θ_directive(i) = E[S | directive_intended] − E[S | placebo_intended]

**Answers:** does the directive the item's specification predicts about change the
outcome, relative to a length-, structure- and format-matched block carrying no
epistemic content, under a closed-book single-dispatch protocol?

**Does not answer:** whether the deployed system does this (the classifier may not
select that directive); whether the change is due to reasoning rather than to
additional computation (the compute path is unseparated — §4); whether it
generalises beyond these items.

### 8.2 θ_system — the deployed system's effect

    θ_system(i) = E[S | directive_routed] − E[S | placebo_routed]

**Answers:** what the epistemic layer as deployed — classifier included — does on
this item, relative to a matched inert block. This is the quantity exp001 and
exp002 measured, so it is the one comparable to them.

**Does not answer:** what the directive's content is worth when correctly
delivered; anything about routing accuracy on a task distribution.

### 8.3 θ_routing — the cost of misrouting (secondary, descriptive)

    θ_routing(i) = θ_system(i) − θ_directive(i)

A difference in differences, so length- and format-controlled on both sides.

**Answers:** on this item, how much outcome is lost by delivering the classifier's
directive instead of the intended one.

**Does not answer:** the expected loss in deployment — that requires routing
accuracy on a representative distribution, which nothing here measures. Cell R has
four items; best achievable sign-test p is 0.0625, so this is descriptive under
every possible outcome.

### 8.4 θ_framing — epistemic framing alone (cells L, U)

    θ_framing(i) = E[S | A_only] − E[S | directive_placebo]

**Answers:** does the claim-type framing sentence alone change the outcome, with
carrier text, length and format held constant.

**Does not answer:** whether the procedural bullets add anything — that is
`directive_only − A_only`, reported alongside.

### 8.5 θ_instruction — the placebo effect (all instructed cells)

    θ_instruction(i) = E[S | directive_placebo] − E[S | baseline]

**Answers:** how much of any directive effect is attributable to being given a
block of serious-looking instructions at all — E4 and E5 together.

**Does not answer:** which of length and format is responsible; they are not
separated.

### 8.6 Cell-level outcome estimands

| Cell | Estimand | Answers | Does not answer |
|---|---|---|---|
| **L** | θ_framing, θ_directive per item | does framing/directive surface knowledge the solver already holds (E1) | whether it would help where the knowledge is absent — floor items are screened out |
| **R** | θ_directive, θ_system, θ_routing per item | does the directive change arithmetic/calendar outcomes under closed book | **whether it improves reasoning** — see §8.7 |
| **D** | δ(i) = E[S \| search_only] − E[S \| closed_book] | does retrieval at snippet depth make the answer worse on false-premise items (E7) | anything about `SOURCE_ACCESS` or `VERIFICATION`, both unreachable (FD-4); 3 items, descriptive only |
| **U** | shift in the categorical response-mode distribution | does the directive change response *shape* where no answer is established | whether calibration improved — mode is shape, not accuracy |
| **N** | κ(i) = E[tool calls \| search_directive] − E[tool calls \| search_only] | does the **deployed** system suppress unnecessary tool use (θ_system by construction) | whether the *intended* directive would — not measured, by decision §1.3 |
| **C** | gate | is the retrieval channel working at all | nothing about any hypothesis; MEASUREMENT_VALIDITY tier |

### 8.7 The language constraint — the thing this packet exists to fix

The cell-R result may be stated as:

> **"Under a closed-book, single-dispatch protocol with k = 5 independent
> replicates and a word-count-, structure- and format-matched placebo, injecting
> directive X changed the per-item correct-answer rate on N arithmetic and
> calendar items by Δ [95% CI], while also changing mean response length by ΔL."**

It may **not** be stated as any of:

* *"Directive X improves reasoning."* — the compute path is unseparated (§4).
* *"Directive X improves reasoning efficiency."* — nothing measures effort per
  unit correctness.
* *"The epistemic layer improves arithmetic."* — that is θ_system, a different
  arm, reported separately.
* anything at conventional significance from a four-item cell (§3.4).
* anything generalising beyond arithmetic and calendar/counting items.

---

## 9. Final decision table

| # | Decision | Options | Consequence | Status |
|---|---|---|---|---|
| **D1** | Routing treatment | A override / B reword / C exclude / **D′ hybrid** | D′: 388 trials (+40); cell R gains 2 conditions; both θ_system and θ_directive estimated; θ_routing as a length-controlled DiD | **awaiting decision** — D′ recommended |
| **D1.1** | Matched placebo per block in cell R | one placebo / **two** | one placebo confounds the routing contrast with a 68-word (32%) length difference | **awaiting decision** — two recommended |
| **D1.2** | Cell N treatment | accept routed / cross | accept: 0 extra trials, cell N's estimand is θ_system, which is the right question for a deployed-restraint claim | **awaiting decision** — accept recommended |
| **D2** | Knowledge probe | dispatch now / defer | ~125 baseline-only screening dispatches; thresholds already frozen; results may not be reused as the experiment's baseline arm | **awaiting decision** — not run |
| **D3** | Power table | recompute / retain §6 | one operative table replacing §6; §3.5 is the replacement text | **blocked on D1** |
| **D4** | Experiment identity | — | `experiments/exp003a_mechanism.yaml` naming battery, treatment, scoring and judge fingerprints, egress and scout dates, dispatch-order seed, and commit | **blocked on D1, D2** |
| **D5** | Git identity | — | clean tree, preflight re-run against the dispatch commit | clears at dispatch |
| **D6** | FD-11 amendment | adopt covariate / **withdraw** | withdraw: primary is the total effect; length becomes a manipulation check | **awaiting decision** — withdraw recommended |
| **D7** | §6 amendment | retain / **replace** | replace with §3.5: one confirmatory cell, everything else descriptive | **awaiting decision** — replace recommended |
| **J1** | D1 decision recorded | — | as D1 | awaiting |
| **J2** | Reword L05 | adopt / decline | one word; construct untouched; removes one item from the disputed set free | **awaiting decision** — adopt recommended |
| **J3** | Cell-R rewrites rejected, recorded | record / leave open | recording stops the option being revisited casually after results exist | **awaiting decision** — record recommended |
| **J4** | Withdraw response-token covariate | = D6 | as D6 | awaiting |
| **J5** | `elaboration_only` | adopt / **defer** | defer: cell-R claim stays at §8.7's constrained wording | **awaiting decision** — defer, per operator direction |
| **J6** | Replace §6 | = D7 | as D7 | awaiting |
| **J7** | Routing accuracy recorded as unmeasured | adopt / decline | stops 60% being cited as field accuracy | **awaiting decision** — adopt recommended |
| **J8** | Freeze C3 | freeze / keep seeking | freeze: counts in §5.1 appear in any result | **awaiting decision** — freeze recommended |
| **J9** | Dispatch gate | — | D1, D2, D6, D7 resolved; power table committed; config written; preflight YES at the dispatch commit | standing |
| **NEW** | Dispatch-order seed | none / **recorded seed** | a paired within-item contrast needs protection from time-correlated drift; seed becomes part of experiment identity | **awaiting decision** — adopt recommended |
| **NEW** | `dispatch_class` field + mixed-aggregate refusal | adopt / decline | makes §7's separation auditable rather than conventional | **awaiting decision** — adopt recommended |

---

**Nothing above is implemented. No trial has been dispatched. The next
implementation pass executes whatever is decided here, and makes no design
choices of its own.**
