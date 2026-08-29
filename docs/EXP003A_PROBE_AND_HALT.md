# exp003a — knowledge probe results and halt

## VERDICT: **NOT RUNNABLE**

Not because a check failed to pass. Because the frozen screen, applied
mechanically to its own results, **empties both PRIMARY cells and deletes the
instrument-validity gate**. There is no confirmatory cell, no primary cell, and
no version of this battery that answers the original question on this model.

**Zero solver trials for exp003a have been dispatched.** The 60 dispatches below
are `dispatch_class: screen` and are permanently excluded from any primary
analysis by a data-model invariant.

---

## A. Knowledge probe results

Run against the frozen configuration `experiments/exp003a_knowledge_probe.yaml`,
baseline only, k=5, thresholds frozen at commit 8da1b92 **before** any probe
existed: ceiling ≥ 0.90, floor ≤ 0.10.

Nothing was modified: no threshold, no item content, no treatment definition, no
scoring rule. Grading ran through the ordinary deterministic path.

| Item | Cell | n | Baseline rate | Decision | Frozen reason |
|---|---|---|---|---|---|
| L01 | L | 5 | **1.00** | EXCLUDE | ceiling: 1.00 ≥ 0.90 |
| L02 | L | 5 | **1.00** | EXCLUDE | ceiling |
| L03 | L | 5 | **1.00** | EXCLUDE | ceiling |
| L04 | L | 5 | **1.00** | EXCLUDE | ceiling |
| L05 | L | 5 | **1.00** | EXCLUDE | ceiling |
| L06 | L | 5 | **1.00** | EXCLUDE | ceiling |
| R01 | R | 5 | **1.00** | EXCLUDE | ceiling |
| R02 | R | 5 | **1.00** | EXCLUDE | ceiling |
| R03 | R | 5 | **1.00** | EXCLUDE | ceiling |
| R04 | R | 5 | **1.00** | EXCLUDE | ceiling |
| C01 | C | 5 | **0.00** | EXCLUDE | floor: 0.00 ≤ 0.10 |
| C02 | C | 5 | **0.00** | EXCLUDE | floor |

**12 of 23 items screened; 12 of 12 excluded.** Every cell-L and cell-R item
answered correctly on all five replicates. Both cell-C items abstained correctly
on all five.

### Why the probe was halted at 60 of 115 dispatches

Deliberately, and stated rather than quietly. Three reasons, none of which is
resource conservation:

1. **The verdict cannot change.** Cells L and R are the only PRIMARY cells and
   both are empty. No result from cells N, D or U can restore a primary or
   confirmatory claim; those cells are DIAGNOSTIC by the tier wall and cannot
   carry a mechanism effect at all.
2. **The screen's scope is now known to be invalid for two of the remaining
   cells** (§B.2). Spending 55 more dispatches on a rule that should not be
   applied to them would be spending on a measurement with no defined use.
3. **Continuing would look like searching for a survivable subset.** With both
   primary cells gone, running the diagnostic cells until something passes is
   the exact behaviour the pre-registration discipline exists to prevent.

The 55 unrun dispatches are recorded as unrun. No item is reported as screened
that was not.

---

## B. Screened battery

### B.1 The mechanical result

| Cell | Items before | Excluded by screen | Surviving | Consequence |
|---|---|---|---|---|
| **L** | 6 | **6** | **0** | PRIMARY cell empty; E1 untestable |
| **R** | 4 | **4** | **0** | PRIMARY cell empty; E2 untestable |
| **C** | 2 | **2** | **0** | gate deleted (but see B.2) |
| N | 4 | not screened | — | DIAGNOSTIC only |
| D | 3 | not screened | — | DIAGNOSTIC only |
| U | 4 | unscreenable | — | see B.2 |

**Is L still ≥ 5 items? No — it is at zero.** The pre-registered rule fires in
its strongest form: not "no confirmatory cell", but no primary cell of any kind.

**Does the confirmatory claim survive? No.** It required 5 or 6 cell-L items
agreeing. Cell L has none.

### B.2 Two scope defects in the frozen screen, found by running it

These are reported rather than worked around, and neither is fixed here.

**The floor rule deletes the gate it depends on.** Cell C exists to fail
closed-book: its items are post-cutoff facts, and a correct baseline response is
an abstention. Both scored 0.00 — *the designed outcome* — and the frozen floor
rule therefore excludes them. Applied mechanically, the screen removes the
instrument-validity tripwire on the grounds that it did exactly what it was built
to do. Cell C's own pre-registered criterion runs the other way ("excluded if
baseline is correct above chance"), so the battery contains two rules pointing in
opposite directions for the same items.

**The screen cannot evaluate cell U at all.** Cell U's items are `rubric_only`
with no ground truth by construction — there is nothing to be correct about, so a
ceiling/floor rule on correctness is undefined for them. They can only be
`NOT_SCREENED`, permanently, under the current design.

The ceiling/floor rule was written for cell L's latent-knowledge logic, where
"the model already knows it" and "the model cannot know it" are both reasons to
exclude. It was then applied battery-wide without checking that the reasoning
transfers. It does not transfer to a tripwire, and it does not apply to items
with no correctness.

---

## C. Final manifest counts

The prepared experiment is unchanged and remains on disk, but it can no longer be
run as specified:

| | Value |
|---|---|
| Prepared trials | 388 |
| Prepared dispatches | 433 |
| Trials whose items survive screening | **0 in cells L, R, C** |
| Solver dispatches executed | **0** |
| Knowledge-probe dispatches executed | **60** of a planned 115 |
| Qualification dispatches (all classes, cumulative) | 96 judge calls (exp003c) + 60 screen + 0 solver |
| Probe dispatch class | `screen`, isolated by invariant |

Regenerating the manifest against the screened battery is not meaningful: with
cells L, R and C empty, what remains is a diagnostic-only run that cannot address
the experiment's question.

---

## D. Final estimands — status

| Estimand | Status after screening |
|---|---|
| θ_directive | **unmeasurable** — cell R empty |
| θ_system | **unmeasurable in cell R**; cell N unscreened |
| θ_routing | **unmeasurable** — required both cell-R arms |
| θ_framing | **unmeasurable** — cell L empty |
| δ_displacement | cell D unscreened; DIAGNOSTIC only |
| mode_shift | cell U unscreenable |
| gate | **deleted by the floor rule** |

---

## E. Final confirmatory claim

**None.** There is no confirmatory cell and no primary cell. Under the
pre-registered rule this is stated first, not in a discussion section.

---

## F. Limitations, and one that has become the headline

**The battery is calibrated to the wrong difficulty for this model.** That is now
the dominant limitation, and it was invisible until the probe ran. Every cell-L
and cell-R item — chosen deliberately to span a difficulty range, including two
authored as ceiling-band candidates — is at 1.00 for haiku. The intended
measurable band does not exist here.

The previously recorded limitations all stand: C3 battery-construction bias
(25/25 same-process, 0 external, 0 blind), compute not separated from reasoning,
self-correction not separated from a second pass, SOURCE_ACCESS and VERIFICATION
unreachable, cell D reduced to three items, routing accuracy unmeasured, FD-1
frozen, FD-13 disclosed.

### What did screening potentially remove from the problem distribution?

This is the question that matters most, and the answer is not reassuring.

**Screening did not trim the distribution. On this battery it inverted it.** The
ceiling rule removes every item the model can already do. When the model can do
all of them, what the rule retains is by construction *only the items the model
fails* — a population defined by the model's weaknesses rather than by the
scientific question. Had a few items survived, they would not have been a
representative sample of "questions where epistemic handling matters"; they would
have been the residue of haiku's specific failure modes on a battery written by
the same process that wrote the mechanism.

Specifically at risk of systematic removal:

* **Well-established facts** — exactly the population E1 (latent-knowledge
  access) is about. If the model reliably surfaces them unaided, the mechanism
  has no room to act, and the screen removes them. E1 may be untestable on any
  battery of stable facts for a model of this capability.
* **Clean multi-step reasoning items**, for the same reason. Cell R's four items
  were chosen because their failure modes were distinguishable; the model made
  none of those failures.
* **Items designed to fail baseline** — the tripwire — which the floor rule
  removes for succeeding at its purpose.
* **Ambiguous or unresolvable items** — cell U — which the screen cannot evaluate
  at all, so they survive by exemption rather than by passing.

The screening threshold was pre-registered, and that makes it honest. It does
**not** make it neutral. A pre-registered rule can still change the population
being tested, and here it changes it completely.

---

## G. Preflight result

Not re-run as a pass/fail gate, because the gating question has been overtaken:
the preflight checks whether a specified experiment can run without changing its
rules, and the experiment no longer has the items its specification requires. Its
last recorded state was 33/34 at commit `4cd2300`, blocked on this probe. The
probe has now run and the blocker resolves into a larger finding.

---

## H. Remaining blockers

Not a list of things to tick off. One decision, which is the operator's:

**The experiment as designed cannot answer its question on this model.** Three
directions, none of which may be chosen by an implementation pass:

1. **Change the model under test.** The battery may be correctly calibrated for a
   smaller or older model. This changes what the result generalises to.
2. **Re-author the battery at a difficulty the model does not saturate.** This is
   a new battery and a new pre-registration, and it re-opens C3 — with the added
   hazard that items selected for being *hard for haiku* are selected on the
   model's weaknesses, which is a worse bias than the one C3 already names.
3. **Change the question.** If the model answers every stable-fact and
   closed-reasoning item unaided, then E1 and E2 may simply not be where the
   epistemic layer could help, and the programme's hypothesis should move toward
   the cells where behaviour still varies — retrieval displacement, tool
   restraint, and uncertainty conduct.

Two smaller items must be resolved whichever direction is taken:

* **The floor rule and cell C's own criterion contradict each other.** One of
  them must be withdrawn.
* **The screen has no defined behaviour for `rubric_only` items.** Either an
  explicit exemption or a separate judged criterion is needed.

---

**Nothing further has been implemented. No solver trial has been dispatched. The
probe data is tagged `screen` and cannot enter a solver analysis.**
