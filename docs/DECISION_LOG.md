# Program Decision Log

> Records durable project-level decisions. Experiment-specific preregistrations remain authoritative for their own scope.

## 2026-08-29 — GitHub is canonical memory

**Decision:** Treat chat sessions as working contexts and GitHub as the source of truth.

**Reason:** The project spans GPT, Claude Code, multiple chats, long experiments, and frozen artifacts. Cross-chat continuity should not depend on model memory.

**Operational consequence:** substantial research actions end with committed status/handoff updates.

---

## 2026-08-29 — Separate research direction from execution value

**Decision:** Add a permanent execution lane to the program.

**Reason:** A system that improves benchmark/judge scores but cannot accomplish useful work has not demonstrated sufficient value.

**Execution standard:** every claimed capability improvement should eventually survive a task with an external success criterion.

**Preferred first domain:** coding / repository work, where build, tests, runtime behavior, regressions, cost, latency, repair cycles, and human intervention provide objective evidence.

---

## 2026-08-29 — Do not productize before internal proof

**Decision:** Prefer using the eventual system internally on real work before abstracting it into an API/platform.

**Reason:** Practical execution provides stronger evidence and exposes failure modes that benchmark-only development can miss.

---

## 2026-08-29 — Recursive improvement is a later research stage

**Decision:** Do not build recursive procedure optimization until the laboratory can reliably detect real procedure differences and those improvements generalize to unseen tasks.

**Reason:** Otherwise recursive search will optimize measurement quirks or the benchmark.

**Required progression:** trustworthy measurement → intervention effect → controllability → execution value → generalization → automated procedure discovery → recursive improvement.

---

## 2026-08-29 — Champion procedures must be frozen and versioned

**Decision:** Future procedure search will distinguish baseline, candidate, champion, and retired procedures.

**Reason:** A promising candidate must not overwrite the incumbent before independent validation.

**Future structure candidate:**
```text
procedures/
  baseline/
  candidates/
  champions/
  retired/
```

Do not create this engineering structure until procedure-discovery work is actually authorized.

---

## 2026-08-29 — External execution evidence outranks model-only judgment

**Decision:** Model judges can be useful instruments, but eventual practical claims require external checks wherever feasible.

Examples:
- coding → build/tests/runtime;
- factual research → evidence/citation checks;
- file transformations → exact artifact assertions;
- workflows → completion/error/intervention metrics.

This does not invalidate judge-based experiments; it limits what they are allowed to prove.

---

## 2026-08-29 — Positive findings remain provisional by default

**Decision:** An interesting or statistically positive result does not directly become a verified mechanism or architecture component.

**Promotion ladder:** signal → replicated → mechanistically narrowed → transferred → execution-valid → operational candidate → broader claim.

**Reason:** Throughout this project, apparently meaningful results have already been vulnerable to alternative explanations including grader effects, key definitions, missing replication, screening, selection bias, invalid null calibration, and environment constraints.

**Operational consequence:** after a positive result, identify and test the most plausible competing explanations before promoting the mechanism. Prefer simpler explanations/components when they reproduce the effect.

---

## 2026-08-29 — Order future research by interpretability dependencies

**Decision:** World-epistemology experiments precede evidence-grounded self-model experiments; self-modeling and execution evidence precede recursive procedure search; combinations follow interpretable single-component tests.

**Reason:** A complex positive result is hard to interpret if its component mechanisms have never been isolated.

**Detailed program:** `docs/EXPERIMENTAL_PROGRAM_2026-08-29.md`.

---

## 2026-08-29 — Retire repeated-trial A_minus Stage-0 design

**Decision:** Do not use the n=18, R=10 fixed-LFC A_minus design as the primary Stage-0 inference.

**Reason:** Simulated within-item×arm replicate ICC as small as 0.02 inflated nominal Type-I from ~0.05 to ~0.09, with larger inflation at modest ICC. Affordable diagnostics have essentially no power to certify ICC below the required level.

**Consequence:** The old independence-diagnostic completion plan, n=18 recommendation, R=10 recommendation, and 0.1444 critical value are retired.

---

## 2026-08-29 — Candidate replacement uses R=1 exact discordant-pair inference

**Decision:** Advance an R=1 per-arm exact discordant-pair / McNemar-style design as the candidate replacement for Stage 0.

**Reason:** With no within-arm replicate set, within-arm ICC cannot contaminate the statistic. Tested Type-I behavior remained conservative/nominal across tied, heterogeneous, and burst-correlated configurations.

**Status:** Candidate, not frozen. Feasibility depends on reversal prevalence and must be established before production design.

---

## 2026-08-29 — Reversal prevalence is an outcome, never a selection criterion

**Decision:** Candidate items may be authored from treatment-blind, reversal-plausible task classes, but observed reversal direction/prevalence must never determine item inclusion.

**Reason:** Selecting on treatment outcome would recreate the ascertainment failure already observed with the scout.

**Consequence:** A prevalence pilot may estimate feasibility/sample size, but individual pilot items may not be retained or excluded based on whether they reversed.

---

## 2026-08-29 — Auditability gap for 27 screen dispatches

**Decision required:** The 27 prior screen-class independence-check dispatches were not persisted to the repository. Before the next pilot, explicitly either:
1. reconstruct/persist them as a clearly labeled non-analysis screen artifact if the raw records are available and trustworthy; or
2. record them as discarded/non-reusable because provenance is incomplete.

Do not leave them in an ambiguous middle state.

---

## 2026-08-29 — Split Stage 0 into discovery, confirmation, naturalistic validation, and controller phases

**Decision:** Stop trying to prove controller value in one large Stage-0 experiment.

**Reason:** [SUPERSEDED 2026-08-30 — the class-stratified exact test does NOT validly establish a class-level mean effect; H0_mean has no valid test in this package and the class average is descriptive only. See the final pre-freeze entry below.] The class-stratified exact test can validly establish a negative class-level mean retrieval effect, but it cannot distinguish a trivial class rule from a general controller, cannot detect within-class sign heterogeneity, and says nothing about naturalistic prevalence.

**Architecture:**
1. Stage 0A — treatment-blind class mechanism discovery.
2. Stage 0B — fresh independent confirmation and query-construction challenge.
3. Stage 0C — naturalistic validation on unenriched tasks.
4. Stage 0D — held-out mixed-task router/controller comparison.
5. Stage 0E — richer action space only after binary control earns value.

---

## 2026-08-29 — Retire the prevalence-pilot-first architecture

**Decision:** Do not run a separate prevalence pilot before Stage 0A.

**Reason:** A per-class pilot informative enough to size production costs roughly production scale while producing no stronger scientific claim. Fixed-n discovery produces both feasibility information and a testable mechanism hypothesis for similar or lower cost.

---

## 2026-08-29 — Class-stratified discovery is mechanism evidence, not general controller evidence

**Decision:** A significant class-level discovery may support:
- retrieval harm under a preregistered stress condition;
- a hand-authored class rule on that distribution.

It does **not** support:
- general sign heterogeneity;
- existing-router performance;
- learned-router discoverability;
- naturalistic prevalence;
- held-out controller value.

---

## 2026-08-29 — Query-generation failure is the primary planned alternative explanation

**Decision:** Log search queries in Stage 0A and predefine a fixed/high-quality query arm for fresh Stage 0B confirmation.

**Interpretation rule:** If ordinary-search harm replicates but disappears under fixed-query search, classify the mechanism primarily as query-construction failure rather than retrieval intrinsically harming the class.

---

## 2026-08-29 — Stage 0A blocked by grading objectivity

**Decision:** Do not freeze or author Stage 0A until the grading architecture is resolved.

**Reason:** Frozen-data audit shows the harm-plausible classes (false-premise, contested quantity/definition, stale/renamed) escalated entirely to judge-based grading, while deterministic/arithmetic graded cleanly. This creates an anti-correlation between scientific relevance and objective gradability.

**Implication:** Runtime judge fallback is prohibited because it makes grader route depend on the answer and therefore on treatment outcome.

**Open remediation paths:**
1. deterministic relational/structured grading validated before dispatch;
2. judged-primary measurement with independently established bias properties;
3. deterministic-only classes with narrower scientific scope.

**Additional decision:** contested-quantity/definition should not be treated as a clean confirmatory class while its defining feature is answer ambiguity; if retained, its definition/key must be reformulated so the target answer is unambiguous.

---

## 2026-08-29 — Adopt anchored-stem objective mechanism assay for Stage 0A-M

**Decision:** Use question-stem anchoring, not output-side epistemic scaffolds, as the candidate route to objective Stage 0A primary measurement.

**Primary candidate classes:**
- date-anchored / time-indexed;
- definition-anchored / definition-fixed quantity;
- arithmetic / deterministic.

**Reason:** Explicitly fixing date/definition/scope in the question creates an objective target while preserving ordinary answer format. By contrast, fields such as `premise_status`, PROCEED/REJECT, or forced correction explicitly cue the reasoning step whose spontaneous failure is under study.

**Claim limitation:** Stage 0A-M may support only retrieval-induced displacement on an authored anchored stress sample. It does not support naturalistic prevalence, controller value, or within-class sign heterogeneity.

---

## 2026-08-29 — Split objective mechanism assay from naturalistic manifestation

**Decision:** Distinguish:
- **Stage 0A-M:** objective anchored mechanism assay;
- **Stage 0A-N:** separate naturalistic free-text manifestation study.

**Reason:** Objective and naturalistic measurement require different instruments. Mixing judge-mediated free text into the confirmatory primary would sacrifice the objectivity gained by anchored keys.

**Naturalistic instrument candidate:** arm-blinded pairwise judging with randomized/reversed presentation, reported separately and not pooled with Stage 0A-M.

---

## 2026-08-29 — False-premise moves out of the objective Stage 0A primary

**Decision:** Do not force false-premise items into an objective structured-output primary.

**Reason:** The observed false-premise failure involved failure to inspect the premise at all. A premise-status or forced-choice field would directly force that inspection and could eliminate the mechanism by measurement.

**Future homes:** Stage 0A-N naturalistic free-text work and execution-grounded tasks where accepting a false premise leads to an objectively invalid downstream action.

---

## 2026-08-29 — Explicit epistemic structure is a separate intervention hypothesis

**Decision:** Register, later and separately from exp004, the hypothesis that explicit epistemic structure (premise status, temporal scope, definition scope, source status, etc.) may itself reduce retrieval-induced displacement.

**Reason:** If structured epistemic representation changes performance, that is a substantive procedure effect, not neutral grading calibration. It belongs to the epistemic-system research branch and must be evaluated as its own intervention.

---

## 2026-08-29 — Stage 0A-M final spec audit: null hypothesis vs stated claim

**Finding (external review, confirmed):** the committed proof in `lab/stage0am.py`
established validity against the POINTWISE null (delta_i >= 0 for every item),
while the specification described the estimand as a CLASS-AVERAGE effect. Those
are different hypotheses, and the mean null is strictly larger.

**Resolution:**
- H0_pointwise validity is PROVEN and is now the primary licensed claim:
  a rejection means *at least one item in the class is harmed*.
- H0_mean validity is PROVEN under Poissonization and, in the exact Bernoulli
  model, SEARCHED rather than proven: exact 2-D convolution over a structured
  grid plus random search, hill-climbing and simulated annealing at n=25 found a
  worst case of 0.030 at alpha=0.05 and 0.0105 at alpha=0.025, with worst
  configurations on the boundary sum(a)=sum(b). The class-average reading is
  reported as a clearly-labelled secondary with weaker warrant.

**Other corrections in the same audit:**
- Treatment frozen as RETRIEVAL-ENABLED (intent-to-treat), not mandatory
  retrieval. Trials where the model declines to search stay in the arm; analysis
  is never conditioned on observed tool use.
- Negative-control headline metric changed from the conditional discordance share
  to the harm RATE n10/n with an exact Clopper-Pearson upper bound, because the
  old metric returned 1.0 for a perfectly clean control.
- "Generic tool-use tax" demoted from an invalidation rule to diagnostic-only;
  "comparable harm" was an undefined outcome-contingent judgement.
- Stage 0B advancement no longer conditions on query quality. The fixed-query arm
  is the experiment that settles query-vs-retrieval harm; screening on it at 0A
  would pre-empt that experiment and may discard a real finding.
- §14 criteria split into formal invalidation rules, power sensitivities and
  interpretive limitations. Class purity is latent and is a power parameter only,
  never an invalidation rule.
- Null-result language frozen before outcomes.

---

## 2026-08-29 — Stage 0A-M: the cross-item dependence assumption, named and defended

**Question:** what dependence assumption across items does the exact conditional
binomial argument actually require?

**Within-item: none.** [PROVEN] a_i - b_i = p_closed_i - p_search_i for an
arbitrary joint distribution of the two arm outcomes; the both-correct terms
cancel. Within-item arm correlation is irrelevant to the test.

**Across items: a real and breakable assumption.** [MEASURED] Type-I at n=25,
alpha=0.05, under structures satisfying H0_pointwise only marginally: one shared
orientation coin 0.498; exchangeable beta mixture c=0.5 0.324; five blocks of
five 0.144; shared pi ~ U(0.2,0.8) 0.121; even a mild beta mixture at c=10
reaches 0.063. Arbitrary cross-item dependence breaks this test badly.

**Weakest sufficient condition, and it is weaker than independence:** the
sequential conditional inequality — for a preregistered ordering, conditioning on
the discordance pattern, P(baseline-favouring | earlier orientations) <= 1/2 for
every discordant item. [PROVEN] by sequential coupling to iid uniforms: X_j <=
1{U_j <= 1/2} pointwise, so the sum is dominated by Binomial(D, 1/2).

It holds automatically when H0_pointwise holds conditional on every realisation
of any shared latent state, and fails when the null holds only marginally.
[MEASURED] conditionally-safe cases are conservative: shared pi ~ U(0,0.5) gives
0.003, an adversary held at the bound 0.028, a history-adaptive adversary 0.000.

**Consequences adopted:**
- A frozen dispatch schedule is now part of the specification, because the defence
  is procedural rather than statistical: arm order randomised independently within
  each item (the key control — it prevents temporal drift from becoming systematic
  orientation correlation), arms of an item paired in time, item order randomised
  from a recorded seed, classes interleaved rather than dispatched in bursts,
  fresh context per trial, runtime metadata recorded.
- Dependence diagnostics are reported but may never exclude an item, class or run.
  At D ~ 13 they have very little power and must not become a fake gate.
- The earlier "burst correlation is conservative" simulation result is reclassified
  as model-specific evidence, not a theorem. It simulated a shared shift in outcome
  probability, not shared ORIENTATION, which is the structure that breaks this test.
- Primary claim wording frozen, about response probabilities and scoped to the
  frozen authored items rather than the semantic class.
- The class-average effect is demoted from a formal secondary claim to a
  descriptive estimate with no inferential content.
- Interpretive consequence carried: because the assumption is
  conditional-on-environment, a degraded index during the run is part of the
  alternative rather than a Type-I threat. Stage 0B's replication separates them.

---

## 2026-08-30 — Stage 0A-M candidate battery authored; key verification incomplete

**Authored:** 25 date-anchored, 25 definition-anchored, 15 arithmetic control = 65
items, 130 implied dispatches. Keys quarantined in
`batteries/answers.anchored_v1.yaml`; questions carry route names only.

**Seven authoring defects were caught by the battery's own tests before freeze:**
three stems contained their own answer (the Facebook, Twitter and Google items
named the entity in the question), two numeric items had accept/reject tolerances
that overlapped, and two items (Burj Khalifa architectural-top vs tip, Earth
equatorial vs mean diameter) had competing values 1.8 m and 14 km apart -- too
close to grade numerically -- and were replaced.

**One test was rescoped, not weakened.** The answer-leak check originally scanned
the whole battery file and flagged a04's answer appearing in a21's stem. A trial
packet carries exactly one question, so the correct invariant is per item; a
weaker cross-item overlap check was added alongside it as a diversity signal.

**Blocking gap: 32 of 50 primary keys are unverified.** 18 were confirmed against
public sources in-session; the rest were authored from careful recollection with
the intended source named. They are marked
`PENDING_INDEPENDENT_VERIFICATION` and `production_eligible: false`. Freezing an
unchecked key is the failure this lab exists to prevent, so they are labelled
rather than assumed.

**Also frozen:** dispatch schedule with recorded seeds (item order 20260830, arm
order 8302026), classes interleaved with no class running more than four
consecutive positions and the control spread across the run; arm packets
differing by three lines, all inside the TOOLS block, with no phantom search
budget in the closed arm and no solver-visible arm label; report skeleton with
both the primary and null-result wordings; preflight checklist.

**Zero dispatches. No production item has been shown to any solver in either arm.**

---

## 2026-08-30 — Stage 0A-M: all 50 primary keys source-verified

**Result: 50/50 primary keys verified, 65/65 items production-eligible.** The 12
pending date-anchored and 20 pending definition-anchored keys were each checked
against source evidence rather than re-read from the authoring note.

**Two items were replaced at verification, not patched.** b09 asked for India's
2023 nominal GDP per the IMF WEO; that value could not be confirmed against a
primary source. b25 asked for the UK's, and the best available figure (3.38
trillion) differed from the authored key (3.34) and came from a secondary
aggregator. The common cause is that IMF GDP figures are revised between WEO
vintages, which makes them a poor basis for a frozen key. Both were replaced with
euro-area membership scope (20 EU states, verified against ECB and Council of the
EU) and Pacific-coast state count (3 contiguous vs 5 including Alaska and Hawaii).

**One key was corrected.** b11's Lake Michigan surface area was re-keyed from
58,030 to NOAA's 57,573 km2. Published figures vary by a few hundred km2 between
sources; the 1,500 km2 tolerance absorbs that spread and remains far from the
Michigan-Huron combined value.

**One provenance defect was repaired.** The 18 items verified during authoring
carried no verification timestamp or verifier-pass marker. They are now recorded
as pass-1 with an offset-aware UTC timestamp, alongside the 32 pass-2 records.

**Environment finding with experimental consequences.** Direct page fetches to
en.wikipedia.org and www.bls.gov were refused by the network egress proxy while
web search worked normally. If the retrieval arm can search but not fetch major
authoritative domains, "retrieval-enabled" here means degraded retrieval, and a
positive result could reflect the retrieval environment rather than retrieval as
such. The egress probe must record per-domain search and fetch reachability, and
the report must carry that set under alternative explanations.

**Battery fingerprint after verification: afc208e1e8d1bd00.** Zero dispatches; no
production item has been shown to any solver in either arm.

## 2026-08-30 — Post-verification battery audit (Stage 0A-M)

Audited the battery as changed by source verification, not the pre-verification
one. Production dispatches remain 0.

**b11 replaced, not repaired.** The verification pass re-keyed it to NOAA's
57,573 km2 for Lake Michigan's surface area with a 1,500 km2 tolerance. The
tolerance was load-bearing: published areas span roughly 57,573-58,030 km2, so
the stem did not determine the answer and the acceptance interval was repairing
an ambiguity that belonged in the question. Source-anchoring the stem to NOAA -
the preferred fix, and the pattern b03, b18 and b20 already use - does not work
here: the NOAA page gives "57,573 square kilometers or 22,300 square miles", and
22,300 sq mi is 57,757 km2. The single named source contradicts itself by 184 km2
for the same quantity, so no tolerance both respects it and means anything.
Replaced with an exact-integer item on the same Michigan-Huron definitional
split, keeping subtype, domain and mechanism.

**b03 tightened — a second instance of the same defect, found by generalising
it.** Turning the b11 lesson into a checkable rule surfaced b03, which nothing
had flagged before: its accept band, 8,848.86 +/- 0.5 m, reached within 0.36 m of
the pre-2020 elevation it exists to reject, so a rounding of the *displacing*
value would have graded correct. Its stem is already survey-anchored, so the band
was the defect; tightened to +/-0.2 m. The rule is now enforced by the suite: no
accept band may reach halfway to the value it must reject. It is derived from the
frozen principle rather than fitted - it flags exactly b03 across all 27 numeric
items with rejects, and every other item clears it with margin.

**b09 and b25 classifications confirmed, with a named residual.** Added the
class-assignment rule to specification §3: a date in the stem does not make an
item `date_anchored`; the class is decided by what the displacing answer is. b09
is `definition_anchored` because its operative constraint is scope and its
primary displacing answer, 27, is a scope error - the date freezes a key that
Bulgaria's 2026 euro accession would otherwise rot. Its secondary reject 19 is a
genuine temporal channel that cannot be removed from any dated euro-area item; it
is recorded as a bounded limitation rather than deleted, since deleting it would
change no grading outcome and only remove the evidence that the channel exists.
b25 is unambiguous. b18's refinement (8,850 -> 8,851.8) was confirmed to move no
grading boundary: both values fall identically outside [20,696, 21,696].

**Fingerprints are now reproducible.** They were computed by a one-shot script
outside the repository, so nothing committed could regenerate them and a
hand-edited key would have kept its recorded fingerprint. `lab/stage0am_fingerprint.py`
derives them from the committed YAML using the original algorithm, and the suite
asserts the manifest agrees. Verified it reproduces the pre-audit fingerprint
`afc208e1e8d1bd00` exactly before any change was made. Lineage is recorded in the
manifest: authoring `a53d4d59856fc1db` -> verification `afc208e1e8d1bd00` ->
final audited `1ec90754f1de2696`.

**Treatment scope defined by the procedure, not by an idealised capability.**
Pre-registered a fixed egress probe (frozen domain set, search and fetch probed
separately, committed in 46ebdd9 before any result was observed). Orchestrator
arm: WebFetch refused for 5 of 5 targets *including example.com* - the block is
total, not domain-selective - while WebSearch returned substantive page text.
This corrects the prior turn, which reported the wikipedia and bls.gov refusals in
terms that implied a per-domain block. The probe's second arm, the same probe
inside a solver-web subagent, died on an API rate limit before issuing a call and
returned no data; it is recorded as INCONCLUSIVE and claims nothing in either
direction. Under the pre-registered transfer rule, the key-verification
environment's blockage is therefore NOT asserted as a property of the solver's
environment. Specification §6.3 scopes every treatment claim to the granted tool
surface under the reachability set of the arm that produced the dispatches, and
requires the report to say plainly that a search-only environment is a weaker
intervention than web access wherever "retrieval" appears - including in the
null-result language of §15. The probe has no gate: no observable value makes the
experiment invalid, and no item is ever dropped or reweighted for reachability.

**Packet aligned with the grant.** `solver-web` is granted WebSearch and
WebFetch, but the retrieval packet named only search. Since the estimand is
intent-to-treat over the granted surface, the packet now names both. Arms still
differ in exactly 3 lines, all inside the TOOLS block.


## 2026-08-30 — Final pre-freeze audit (Stage 0A-M)

Production dispatches remain 0. Battery fingerprint unchanged at `1ec90754f1de2696`:
no stem and no key changed this turn.

**Solver egress measured.** The frozen probe's missing arm was re-run unchanged
and completed. The solver-web subagent matched the orchestrator on all seven
targets: WebFetch refused 5/5 including `example.com`, WebSearch 2/2 returning
substantive page text. `E` = search-capable, fetch-blocked, now licensed by
measurement of the solver's own path rather than by architectural expectation.
Recorded in `egress_probe.results.json`; the design was not touched after any
result was seen.

**Failure semantics resolved (§6.3 vs §7).** The proposed A/B split survived
audit, but the reason matters more than the split: voiding on retrieval-tool
failure is post-treatment selection on a variable only the treatment arm can
exhibit, because the closed arm has no tools and can never register one. It would
also delete part of the phenomenon — a model that searched, got nothing and
confabulated anyway is one of the mechanisms by which retrieval causes harm. The
discriminating question is not which tool failed but whether the dispatch yielded
a gradeable final answer. Case B voids the pair because a half-missing pair
cannot enter a paired test at all — mechanically forced, not chosen; the only
policy choice is that voiding stays symmetric across arms. Now executable in
`lab/stage0am.py` and pinned by 21 tests.

**Estimand resolved (§4 vs §1).** §4's `Estimand: the class-average effect` was
stale and is gone. The inferential target is violation of the pointwise null;
H0_mean is not tested; the power table is relabelled a design sensitivity.

**A third defect, found by this audit, biased toward the hypothesis.** Probing
the repaired b11 showed that on the numeric route a reject overrode a correct
answer, so `"13 individual golds, out of 23 total"` and four others like it
graded incorrect. Each answers correctly and names the contrast to show the
distinction was understood — the behaviour the anchored-stem design exists to
elicit. A solver that has just retrieved a source is likelier to state both
figures, so the false negatives concentrate in the retrieval-enabled arm and
manufacture n10: a false HARM signal, pointing the way the hypothesis predicts.
Fixed before any outcome was visible, at no cost: the separation invariant
already puts every reject outside its accept band, so a bare displacing answer
still fails on the accept test alone — reject-precedence could only ever have
converted correct answers into incorrect ones. Reject-precedence is retained on
the entity route, where naming the displacing entity genuinely is a non-answer.
Spelled-out integers 0-20 are now extracted alongside digits for the same
arm-correlation reason.

**Grader fingerprinted separately.** The battery fingerprint covers stems and
keys, not the grader, and two runs under different grading semantics are not
comparable. `grading_semantics.sha256_16` is now in the manifest.

**Stale lifecycle wording scrubbed.** The specification no longer says the
production battery does not exist. The authoring protocol is retained and marked
historical, because it is the rationale the authored battery must be judged
against.


## 2026-09-01 — Red-team of the agent-symmetry remediation; runtime validation blocked

Production dispatches remain 0. The remediation (0fb8a7f) survived audit on every
load-bearing point: bodies byte-identical, `model: inherit` both arms, tool
difference exactly {WebSearch, WebFetch}, packets differing only in TOOLS. Three
bounded repairs: arm labels removed from agent `description` metadata; the
symmetry record's body hash recomputed with the test's own method (it had been a
bookkeeping mismatch, not an asymmetry); one brittle string-matching test replaced
with a check of the actual invariant against the dedicated agent. The GPT
session's TOOLS rewording was accepted — "you have none" had been false.

Found: `.claude/agents` is loaded at session start, so this session (begun
2026-08-27) cannot dispatch the dedicated agents. Every runtime gate is therefore
blocked here. No workaround was taken, deliberately: the generic agents can read
the answer key, the shared solvers are the confound, and a spawned child session
would run validation and 130 dispatches unsupervised on a budget the ledger shows
is marginal. Freeze record with recomputable hashes committed; a fresh session
performs the runtime gates and, if the measured per-trial cost fits, the run.


## 2026-09-02 — Last pre-results pass: safeguards implemented, one memo claim retracted

**Decisions:**
- Adopt `EXPERIMENT_CAUSAL_CONTRACT` prospectively for every future experiment
  family (`docs/EXPERIMENT_CAUSAL_CONTRACT.md`). Stage 0A-M is mapped only as a
  documentation fixture; the rule is not applied to it retroactively.
- Robust EVOI: reject the optimistic-max wording; use ordinary EVOI where an
  instrument's reliability is measured, and a lower bound over the plausible
  reliability set plus a bounded, pre-declared calibration budget where it is not.
- Configured effort is a pre-treatment symmetry invariant to be recorded in
  freeze records; realized effort is a per-trial mediator/outcome and is never
  equalised across arms.
- Freeze the R1′/R2′ prospective component table before any further audit;
  churn is defined mechanically from git; the table may not be edited to fit.

**Retraction:** the 2026-09-01 memos claimed `verified_flat` had no visible
budget line. The packets show `SEARCH BUDGET: 3 searches`. The M2 claim is
downgraded (`docs/results/CAUSAL_INTROSPECTION_M2.md`); the original text is
struck through, not deleted.

**Unchanged:** Stage 0A-M battery, keys, grader, schedule, treatment, inference.
Production dispatches 0. Grader golden corpus (51 cases) passed unchanged.


## 2026-09-02 — Stage 0A-M execution attempt blocked; closed arm unspawnable

**Observation:** with the production model set to Opus 5, `stage0am-solver-closed`
could not be launched. `TodoWrite` is not a recognized subagent tool in Claude
Code 2.1.248; the closed arm's declared tool list resolves to the empty set and
the harness refuses a zero-tool agent. The retrieval arm launched with realized
tools `{WebSearch, WebFetch}` — `TodoWrite` dropped there too.

**Decision:** STOP before production. Do not repair the tool surface in an
execution session. Every available fix changes the treatment definition, and no
recognized non-informational tool safe for both arms (key quarantine intact) was
identified. Recorded, not resolved.

**Decision:** the realized-vs-declared tool surface needs a correspondence check.
Every existing symmetry check reads the committed frontmatter; none binds it to
the runtime. 1,397 tests passed while the closed arm was undispatchable.

**Measured and unchanged:** `E_current` = search-capable, fetch-blocked, matching
the previously recorded `E` (WebFetch 5/5 refused including `example.com`;
WebSearch 2/2 OK). No split-environment problem.

**Prospective prediction scored:** the defect fell in the pre-declared
`live_agent_registry` cell — R1′ high risk, churn low. SUPPORTS R1′ over the
churn rival at n=1; the component was named in advance, the mechanism was not.

**Unchanged:** battery `1ec90754f1de2696`, grader `10adaf1dac94ea70`, schedule,
keys, hypothesis, inference, R. Production dispatches 0; treatment exposure NONE.


## 2026-09-02 — Stage 0A-M executed: null at low realized sensitivity

**Executed** 130/130 dispatches under freeze `a1f4efb`, all on `claude-opus-5`,
0 voids, 0 dispatch failures. Neither primary class rejected (date_anchored
D=2 p=0.750; definition_anchored D=0 p=1.000). Arithmetic control 15/15.

**Decision: report the null as nearly uninformative rather than as evidence
retrieval is safe.** Only 2 of 65 items were discordant. Definition-anchored and
arithmetic sat at a complete ceiling; date-anchored difficulty was largely an
instrument artifact, with 28 of 50 trials naming the correct anchored entity yet
graded incorrect under entity-route reject-precedence. Both discordant pairs are
that same artifact.

**Decision: do NOT repair the grader after outcome visibility.** The entity-route
reject rule is defective — it cannot separate "X, who succeeded Y" from "Y, who
was succeeded by X" — but it was frozen and the run is scored under it. The fix
is specified for Stage 0B, to be frozen before any Stage 0B outcome.

**Decision: dispatch repair was mechanism-only.** Identical command lines per
arm; agent frontmatter left unedited because an empty `tools:` value risks
"inherit all tools" and would break key quarantine. TodoWrite recorded as inert.

**Decision: a live runtime correspondence gate is now mandatory before
production.** Static frontmatter tests could not see that the closed arm was
undispatchable while 1,397 tests passed.

**Prediction scoring:** P2 no fallback; P3 no effect at near-zero power; P4 not
supported (realized effort near-identical, closed marginally higher).


## 2026-09-02 — Independent review of Stage 0A-M: the null was structurally impossible to avoid

**Reviewed by a separate session from the persisted artifacts only.** Execution
validity was confirmed without qualification and the primary result was
reconstructed exactly (`date_anchored` D=2, p = 3/4 exact; `definition_anchored`
D=0). Reproduce: `python -m lab.stage0am_review`.

**Decision: record that Stage 0A-M could not have rejected, and treat that as the
finding.** The exact test spends discordant pairs; at D=2 the smallest attainable
p is 1/4, against thresholds of 0.05 and 0.025. This is stronger than "low
power": no orientation of the observed data reaches any threshold. Every future
design in this program is sized on **expected discordance**, not on n.

**Decision: the `anchored_v1` battery is RETIRED, not merely noted as easy.**
Under a first-mention / first-polarity-token rule the run scores **130/130** with
D=0 in every class. All 30 incorrect grades were instrument artifacts — 28 on the
entity route, 2 on a previously unreported boolean-route defect. The battery
contains zero items Opus 5 answers incorrectly. Production-exposed and at ceiling,
`date_anchored` and `definition_anchored` are retired for confirmation;
`date_anchored` survives only as a grader regression corpus. The arithmetic
control is reused, plus 5 fresh items so an exposure effect would be visible.

**Decision: correct the report's ceiling reasoning, without changing its numbers.**
"Zero discordance is possible at a ceiling, so those classes contributed no
information whatsoever" is wrong in its stated mechanism. The specification's own
power model says a *closed-arm* ceiling is the most favourable condition. What
produced D=0 was that the retrieval arm was also 25/25 — a measurement of the
effect, not an absence of one, and the run's tightest harm bound (≤0.113).

**Decision: the distinction that governs all future claims is AVAILABILITY vs
CONSUMPTION.** Retrieval was attempted in 8/65 treated trials, **all 8 in the
class at 100% accuracy in both arms, and 0/25 in `date_anchored`** — the only
class with outcome variance. Both discordant retrieval-arm trials issued zero
searches, so the two discordant pairs are provably grading artifacts. Stage 0A-M
measured availability. The entire evidential basis about retrieved content is 8
trials, bound ≤0.312.

**Decision: `analysis.json`'s `retrieval_failure_rate` is a defective field and
must not be cited.** `analyse_run` constructs every `TrialOutcome` with empty
`retrieval_outcomes`, so it reports `attempted_retrieval: 0` by construction. The
primary result does not depend on it. Future analyses bind retrieval fields to
values actually recorded per trial.

**Decision: the freeze/grade/analyse driver is itself load-bearing and must be
committed before the first dispatch.** Stage 0A-M's was first committed in the
same commit that first persisted outcomes, with 33 of 130 answers on disk. The
freeze holds — the grading rule and test statistic were frozen at `9c57635`, well
before any outcome, and are byte-identical from the freeze commit to HEAD — but
the window is real and is closed prospectively rather than argued away.

**~~R1′ scored again, n=2.~~ CORRECTED 2026-09-03 — see the entry of that date.**
The empirical finding is unchanged: the grader was deterministic, fingerprinted
and covered by a 51-case golden corpus, and it mis-scored 30 of 130 production
trials in two independent ways while 1,397 tests passed. The *scoring* was wrong.
The frozen prospective table classifies `grader` as symmetric, checked and
**R1′-low**; a defect there is `HURT_BOTH` under the table's own rules, not a
confirmation. Prospective confirmations of R1′ remain **n=1**.

**Unchanged:** Stage 0A-M raw outcomes, graded ledger, frozen grader
`10adaf1dac94ea70`, official primary result, battery `1ec90754f1de2696`, schedule.


## 2026-09-02 — Stage 0B design: fix the instrument, force the dose, do not author yet

**Decision: Stage 0B studies retrieved CONTENT, with uptake forced to 1.0 by
harness construction.** Objective: whether the content returned by an
actually-executed search can displace an otherwise-correct anchored answer, and
whether displacement is caused by the content or by the query that fetched it.
Instructing a model to search is what Stage 0A-M effectively did; the dose is now
structural — the harness executes the search and injects the results.

**Decision: arms A (closed) + C (required, model-written query) + D (required,
fixed query). ARM B (optional retrieval) is dropped.** Not for budget: at Stage
0A-M's realized uptake an optional arm is unpowered at every n ≤ 120, and the
question it answers is already answered. A vs C identifies the total effect;
C vs D decomposes it into query-construction and content components. Dropping D
would leave a null in C uninterpretable.

**Decision: the construct changes, and it is renamed rather than smuggled.** This
is `search_snippet_exposure`, not agentic retrieval and not unrestricted web
retrieval. `E` is search-capable and fetch-blocked; a fetch-capable replication is
a named follow-on and no result may be pooled across environments.

**Decision: direct-answer-first span grading, not a structured answer field.**
Three candidates were compared. Whole-answer parsing is rejected — it demonstrably
cannot separate "Bolsonaro… later succeeded by Lula" from "Lula was president". A
structured JSON field is the most parseable but changes the task the model
performs, and format compliance can interact with the arm; that is a
treatment-correlated instrument risk of exactly the kind that destroyed Stage
0A-M, so it is a robustness replication, never primary. The span rule costs
nothing behaviourally: 32/32 entity and 14/14 boolean Stage 0A-M answers already
led with the direct answer. Implemented at `lab/grading_v2.py` with a hand-derived
semantic corpus; it repairs all 30 false negatives, introduces none, and its two
residual failures are enumerated and pinned by test.

**Decision: pre-treatment difficulty calibration with three disjoint pools and a
hard wall.** A calibration bank ≥3× production size that may NEVER enter
production; a held-out production pool no solver sees before dispatch; a frozen
selection rule; and a scripted retrieval-divergence probe that dispatches no
solver and generates no outcome. Estimand is explicitly finite-selected-set.
**Target closed-book accuracy 0.90–1.00, not a middling band** — at baseline ≤0.65
the design is unreachable at n ≤ 120, because genuine repairs cancel harms in a
one-sided paired test.

**Decision: prefer fixing the instrument over increasing n — as a computed result.**
At Stage 0A-M's measured grader false-negative rates the design is unpowered at
every n up to 120. A 20-point symmetric rate costs 14 items; an 8-point asymmetric
rate costs 33. Symmetric and asymmetric grader error are modelled separately
because they fail differently: symmetric silently deletes at-risk items,
asymmetric manufactures discordance — and Stage 0A-M's entire discordant sample
was the latter.

**Sizing:** n=50 primary items, K=1 primary family (A vs C) at α=0.05, C vs D as a
preregistered secondary in its own family, 15 control items, E[D]=7.1,
power 0.858, MDE δ=0.30, 390 dispatches, ≈$15.

**DECISION: B — MORE DESIGN WORK REQUIRED. Battery authoring is NOT authorized.**
The searcher and injection harness are unbuilt, so the divergence probe cannot
run, so the calibration bank cannot run, so the recipe is unvalidated. A is not
available, and choosing it to show progress is how a second uninformative null
gets funded.


---

## 2026-09-03 — Stage 0B instrument built and measured; the treatment is renamed a second time

**Decision: A — READY TO AUTHOR/RUN THE CALIBRATION BANK.** The single blocker
behind the previous entry's decision B is cleared. **The calibration bank was
deliberately not run in this pass.** It is the first step that produces solver
outcomes, and it should begin from a committed, reviewed instrument rather than one
built in the same breath as the run that depends on it.

**Decision: the recorded treatment artifact is read from the runtime, not from the
searcher model.** The design said a searcher agent would "return the result block
verbatim". Measured against the live runtime, that is false: the searcher reformats
into markdown, drops the header and the trailing instruction, and duplicates the
source list *because that instruction told it to*. `--output-format stream-json`
exposes the `tool_result` block the runtime handed the agent; that string is the
artifact. The searcher's prose is kept for audit and is never data. **The model in
the middle is reduced to issuing the call**, and whether it issued the *requested*
query is byte-checked against `tool_use.input.query`.

**Decision: the treatment is renamed to `runtime_exposed_search_result_block_exposure`.**
`search_snippet_exposure` was itself a rename made for honesty two days ago, and it
was also wrong: **there are no snippets.** What crosses the boundary is a header
echoing the query, a `Links:` array of titles and URLs only, a **model-synthesised
prose answer to the query**, and an imperative addressed to the reader. Because that
paragraph is a second model's answer generated inside the search tool, **a
displacement effect could originate there rather than in any retrieved page**, and
no Stage 0B claim may say "retrieved content" without that qualification. Naming is
not cosmetic here: twice now the name has been the first thing measurement falsified.

**Decision: the runtime's trailing imperative is stripped before injection, and the
stripped text is recorded verbatim.** Left in, it would instruct C and D answerers
to emit markdown source lists — a format change arm A never receives, landing
directly on the grader's leading-sentence span rule. That is the
treatment-correlated instrument risk for which structured output was already
rejected as primary. The strip is a named transformation in the contract, not a
silent cleanup.

**Decision: one direct query→answerer path is kept and declared.** The block's
header echoes the query, so the query text reaches the answerer. Removing it would
make the injected block differ from what the runtime exposes, and the whole lesson
is to bind to what actually crosses the boundary. It is written into the causal
contract as a declared edge rather than left for a later review to find.

**Decision: the search-attempt indicator is `sum(modelUsage[*].webSearchRequests)`
over ALL models.** `usage.server_tool_use` reports 0 on a dispatch that demonstrably
searched — the same defect that made Stage 0A-M's `retrieval_failure_rate` vacuous.
WebSearch is billed to the model that services it, measured as `claude-haiku-4-5`,
not the solver; reading the solver's own count would report zero on every trial.

**Decision: a per-trial artifact hash is provenance, not reproducibility.** Two
dispatches of an identical query returned a byte-identical `Links:` array and a
different synthesised paragraph. Both are committed as fixtures so the distinction
is testable rather than remembered.

**Decision: divergence is defined on the runtime's synthesised summary, not on the
whole block.** Containment fires on incidental text: on the real Lovelace block the
reject alias `1852` matched inside the link title "Ada Lovelace (1815 - 1852)", a
date range asserting nothing. Whole-block containment would have admitted that item
to production and spent a slot on a foregone null. `reject_in_links_only` keeps the
weak signal analysable without re-running a search.

**Decision: every correspondence check dispatches; a static config test may not
substitute for one.** 14 checks, 14 PASS, **0 UNOBSERVABLE**, 6 dispatches, $0.19.
Fresh context is measured with a planted marker; key quarantine as an empty realized
tool surface plus self-report; C/D symmetry on realized command lines and realized
tool surfaces. Unobservable is a recorded status, never a silent pass.

**Decision: failure semantics are four classes, not one, and are fixed before any
outcome.** HARNESS / TREATMENT REALIZATION / ANSWER / ENVIRONMENT DRIFT, 14 rules.
Retry is barred wherever retrying would condition the sample on a realized outcome —
a tested invariant, not a convention. **A search that returns nothing displacing is
not a failure; it is the measurement**, and voiding it would select the treatment
for potency.

**Decision on C-vs-D: not promoted to primary, and put on notice.** It is the *only*
support for the objective's second claim, so it must be capable of discriminating.
It is two-sided, needing 6 discordant pairs before it can reject at all. **At the
recommended n=50 it has power 0.60 against the preregistered gap of 0.20 and needs
n=76**; under Stage 0A-M's symmetric 20% grader error it is unpowered at every n up
to 240 — there, symmetric noise *manufactures balanced discordance*, the opposite of
its silent-deletion behaviour in the one-sided primary. Three rules are fixed before
outcomes: a realized discordant count below 6 is reported as **UNINFORMATIVE —
INCAPABLE OF REJECTING** and never as "no evidence"; `authorize()` runs on measured
values before freeze and **withdraws the query-construction claim** if it fails; arm
D is retained either way, because its interpretive job does not require C-vs-D to
reject. **Nothing was resized on assumed values** — sizing on assumptions is what
produced Stage 0A-M.

**Decision: the R1′ scoring of the grader defect is corrected.** The independent
review recorded "supported again, n=2". The frozen prospective table classifies
`grader` as symmetric, `check_executed: true`, `r1_prime_predicted_risk: low`. R1′
predicted that cell was safe, so under the table's own `what_future_observations_mean`
a load-bearing defect there is **`HURT_BOTH`** — disconfirming, not confirming.
**Prospective confirmations of R1′ remain n=1.** The empirical grader failure is
untouched; only the theory scoring changed. R1′ was **not** widened to cover the
observation: redefining "unchecked" to mean "not checked against the right thing"
would make it unfalsifiable. A successor hypothesis (**R3′** — a check binds a
component only to the representation it actually reads) is recorded as a candidate
with **zero** prospective evidence until its own table is frozen.

**Decision: `query_writer` is added to the shared causal-contract node vocabulary.**
A multi-dispatch trial puts a second model inside one arm, and the edges that matter
— `query_writer → outcome` (must be absent) and `query_writer → tool_use` (the one
licensed path) — could not otherwise be written down. An assumption that cannot be
written down is the kind this contract exists to catch.

**Contract status: VALID as `draft`**, 7 open fields, 4 `[OPEN]` bindings. Not
`freeze_ready`, and it must not be until the calibration bank, the grader freeze and
the measured power re-derivation exist.

**Tests: 1569 passing (was 1466).** The parser tests run against a real sanitized
runtime transcript rather than invented examples — which is precisely why the
"verbatim" claim did not survive this pass, and no author-derived corpus would have
caught it.

**Unchanged:** every Stage 0A-M frozen artifact — raw outcomes, graded ledger,
frozen grader `10adaf1dac94ea70`, official primary result, battery
`1ec90754f1de2696`, schedule `321c3a2397958c30`.


---

## 2026-09-03 (second pass) — Pre-calibration design reconciliation

**Decision: A — CALIBRATION DESIGN READY TO RUN.** No calibration datum exists and
no live call was made. Every change below was made *before* spending the
calibration budget, which is the only point at which such changes are free of the
data they would otherwise be reacting to.

**Decision: `c_disp` is renamed and split by arm, because it named content that
does not cross the boundary.** It read "P(retrieved content carries displacing
information)". Measured, no retrieved page content reaches the answerer at all —
the block is a query echo, a titles-and-URLs link array, and a prose answer
synthesised inside the search runtime. The parameter is redefined on the
representation that does cross: **`q_C`** = P(the C-arm block's runtime-synthesised
summary carries a predeclared reject alias | the item passed the fixed-query
screen), **measured from the C arm** by a query-writer dispatch plus a C search;
**`q_D`** is **1.0 by construction** on the production pool, because the divergence
screen admits on exactly that condition, and is never estimated. **The fixed-query
divergence rate may not substitute for the C-arm rate** — they are different
queries producing different blocks, and substituting one for the other is the
hypothesis assumed rather than measured. `Scenario.c_disp` → `Scenario.q_exposure`.
`δ` remains a **preregistered** minimum interesting effect of 0.30: it is the
estimand, and measuring it in calibration would size the run on a first look at its
own effect.

**Decision: the ">= 3× production" calibration rule is REPLACED, not reproduced.**
It is asserted in the authoring protocol, the design draft §2.4, `docs/NEXT.md` and
the 2026-09-02 entry above, and derived in none of them. It is wrong in **both**
directions at once: too small for what it had to measure (§2.4 dispatches
calibration items *closed-book only*, which measures `p` and nothing else — no
`q_C`, no `q_D`, no grader behaviour on exposed answers), and too large under the
realized six-dispatch structure (~$35 for 150 items, more than the production run
it was protecting). Replaced by a bank sized from the four decisions it resolves,
with a frozen sequential plan: **batch 1 = 48 authored → 36 screen-passing items,
228 dispatches, $8.44**; batches 2–3 of 24 screen-passing items if triggered; **cap
84 screen-passing items, 532 dispatches, $19.69** — the point at which calibration
costs about what production costs.

**Decision: the minimum per-item dispatch structure is six, and screened first.**
One fixed-query search on **every authored item** (the screen, and the pass rate
`s`); then on passers only — closed-book answerer (`p`), query-writer and C search
(`q_C`), and two exposed answerers (the grader pairs). Every calibration estimand
is conditional on screen-passing because every production item is, so an item the
screen rejects is a different population, not a cheaper calibration item. **No
exposed answerer is bought to estimate exposure divergence** — divergence is
measured on the block, before any answerer exists.

**Decision: production is sized AT the grader bound calibration can reach, because
it cannot reach the one n=50 needs.** At n=50, α=0.05, p=0.95, q_C=0.50, δ=0.30,
power holds at 0.80 only while the asymmetric grader defect rate `g_one` ≤ **0.014**.
Bounding that with zero observations needs **213 clean closed/exposed pairs**, four
times the production run. No affordable bank certifies the instrument for n=50. So
sizing enters `q_C` at its **point estimate** (an unbiased measurement of the
environment, whose error moves power either way) and `g_one` at its **95% upper
bound** (an instrument defect, and §7.1 is the reason it is never assumed small).
At the achievable bound of 0.08 the required n is **72**. **The n=50 recommendation
is superseded.** What makes the bound affordable: one item yields **two** pairs,
(A,C) and (A,D), exchangeable because the packet, block format and answerer agent
are byte-identical between C and D — and the two counts are reported separately so
the licence can be falsified.

**Decision: negative controls are 30, derived — not 15 and not 20.** Both numbers
sat in the repository at once and neither came from what the control establishes.
15 was Stage 0A-M's *realized* `arithmetic_control` size carried into the power
module; 20 was design draft §8's "15 reused + 5 fresh". The control's job, per the
frozen code's own docstring, is an exact upper bound on the **generic exposure
tax**, and in Stage 0B it is the *only* handle on it, because the divergence screen
leaves no dosed-vs-undosed contrast inside the primary class. The primary cannot
reject below D=5, which at n=50 is a harm rate of **0.10**; a clean control's 95%
Clopper-Pearson upper bound must clear it. n=15 gives 0.181 and n=20 gives 0.139 —
**neither excludes a tax the size of the entire minimum rejectable primary signal.**
n=29 is the exact minimum (0.098); **30** is taken so the composition stays 15
reused + 15 fresh. It is a **function of the primary n**, not a constant.
Brittleness declared with its reporting rule fixed now: one harm lifts the bound to
0.149, and the response is that the primary is reported with the generic exposure
tax explicitly not excluded — not more items.

**Decision: the query echo is KEPT and the C-vs-D claim is NARROWED.** The runtime
block echoes the query, so C and D differ through the query text, the synthesised
answer and the link list simultaneously; C-vs-D does not isolate "retrieved
information caused the effect" and on this runtime never could. Stripping the echo
symmetrically was **rejected**: it would make the injected block differ from what
the runtime exposes — the exact mistake the "verbatim" claim already cost this
design once — trading a declared artifact for an undeclared one. **No arm is
added.** C-vs-D estimates *the total downstream effect of the query-construction
procedure under this realized search runtime*, bundling all three channels and
attributing to none. Decomposition is a **named follow-on**. Also declared: the
screen pins `q_D` at 1, so under the common-δ decomposition D is expected to
displace at least as often as C; the test stays two-sided because a C query can
return a different and more potent claim.

**Decision: the grader development/validation wall, and adjudication before
grading.** The trap is "the grader failed, so we edit it until these answers pass".
Three rules close it: the hand-derived verdict is recorded **before** the grader
runs, and a row graded without `hand_verdict_recorded_first` or without a grader
fingerprint is a **schema error**; repairs are developed on the **development**
subset only and must be expressible as general semantic rules, re-run against the
frozen 130-answer regression corpus with zero regressions; the rate is bounded on
the **holdout** only, and a repair informed by a holdout answer **burns** it,
requiring a fresh one. No production item may serve either purpose.

**Decision: the stopping rules are frozen AND fingerprinted before the first
calibration outcome.** PASS / CONTINUE / REVISE-RECIPE / REVISE-GRADER /
REVISE-DESIGN are implemented in `lab.stage0b_calibration.decide`, added to
`instrument_fingerprints.json` and pinned by test — for the same reason the grader
is fingerprinted: a stopping rule that can be edited once the data arrives is not a
stopping rule. The **evaluation order** is part of the rule: a recipe that fails
cannot be rescued by a grader repair.

**Decision: the calibration ledger schema is specified before anything runs.**
`lab.stage0b_calibration.CalibrationRow`, with `REQUIRED_FOR_EACH_STATISTIC`
mapping every statistic to the fields it is computed from. A statistic with no
entry there may not be computed — the rule Stage 0A-M lacked when `analyse_run`
built `retrieval_failure_rate` out of empty tuples and reported a plausible number
with no lineage. `None` means UNOBSERVABLE and never zero.

**Costs: measured values replace estimates.** Searcher $0.0640 (mean of the six
real `stage0b-searcher` dispatches), query-writer $0.0136, exposed answerer $0.0276
(was a $0.025 extrapolation).

**Contract: VALID as `draft`,** 7 open fields. Four bindings added —
`calibration_bank_sizing`, `grader_validation_holdout`, `negative_control_sizing`,
`query_echo_direct_path` — and `item_selection_rule` moves from `[OPEN]` to bound
with its fingerprint still open, because it cannot be fixed until the recipe it
selects on has been validated.

**Tests: 1618 passing (was 1569), all offline. Zero live calls this pass.** The
14-check runtime correspondence gate was deliberately **not** re-run: nothing here
changes the instrument it measured, and re-running a passing live gate to feel
thorough is how quota gets spent on nothing.

**Unchanged:** every Stage 0A-M frozen artifact; the candidate grader, still not
frozen and not touched.


---

## 2026-09-03 (third pass) — Final pre-calibration red team

**Decision: A — CALIBRATION READY.** No calibration datum exists and no live call
was made. An independent review of `120620c` found that **two of the second pass's
own corrections were wrong**, and both were load-bearing. Finding them here rather
than in the bank's output is what the red team was for.

**Decision: the grader-defect sampling unit is the ITEM, and the bound is computed
on the (A,C) pair alone.** The second pass pooled (A,C) and (A,D) into two
Bernoulli trials per item, licensed by "exchangeability". **Exchangeability is not
independence.** Both pairs are built from the same closed-arm verdict on the same
closed-arm answer, so a single closed-arm defect produced two counted `g_one`
events — one draw written down twice. A Clopper-Pearson bound at n = 2 × items
assumes 2m independent trials and so returns an interval **narrower than the
evidence supports**; for an *instrument defect* that runs in the dangerous
direction and **under-sizes production**. It also bounded the wrong estimand:
`g_one` is a property of the A-vs-C pair, because A-vs-C is the primary, and
folding in (A,D) rests on an assumption about model behaviour that no packet-level
symmetry establishes. **(A,D) is retained as a diagnostic and as the only exercise
arm D's answer form gets before a production run that grades arm D too; it enters
no bound.** An item-level union bound is reported as a conservative companion.

**Consequence, and it is not cosmetic:** a clean 24-item holdout bounds `g_one` at
**0.117**, not 0.061 — above the 0.08 PASS threshold. **Batch 1 as specified could
not have passed even with a flawless holdout.** The holdout rises to **36 items**
(the smallest clean holdout that reaches the threshold at all) and batch 1 to 48
screen-passing items.

**Decision: arm D re-executes its fixed query at answering time, and the parameter
is `r_D`, measured.** `q_D = 1.0 by construction` was **false**, and this
repository already held the refutation: the search artifact is not reproducible
(design draft §12.3) and `lab/stage0b_harness.py:run_arm` executes arm D's fixed
query freshly at answering time, so the screened block is never the injected block.
`q_D = 1` was true of an artifact the experiment never uses. Freezing the screened
block was **rejected** — it would give arm D a stale block against a contemporaneous
C block, breaking the one structural guarantee the C/D contrast rests on
(`execute_search(query)` takes one parameter, so C and D can differ in nothing
else). Freezing both arms' blocks was rejected as unnecessary. **The screen is a
filter on item propensity, not a guaranteed dose**, and a production D trial whose
re-executed block is non-divergent is **the measurement, not a failure**.
`CvDScenario.from_exposure` now **requires** `r_D` and has no default: a default is
how an unmeasured value re-enters a power calculation. The inference that "D must
displace at least as often as C" is withdrawn with its premise.

**Decision: the p certification is withdrawn; the band is checked on the point
estimate and sizing uses the lower bound.** Requiring a 95% one-sided lower bound
to clear 0.90 rejects a recipe sitting **on this design's own point of p=0.95**
about five times in six at n=36 (P(pass)=0.158), and rejects one exactly at the
band edge with probability ≥0.95 by construction. Design draft §2.2 sets a **band
on the measured accuracy**, not a certification that its edge is exceeded. The
criterion is changed to match the intended claim — not because certification was
expensive. Errors in the bank now cost production items rather than triggering a
near-certain false stop, and the affordability cap stays the binding gate.

**Decision: the negative-control count is PROVISIONAL and 30 was never a
commitment.** It is a function of the final primary n, which does not exist until
the bank has run — and the same document that reported 30 superseded the n=50 it
was derived against. The rule gives 50→30, 66→40, **72→42**, 90→54. No control item
is authored until production n is fixed.

**Decision: Stage 0B thresholds are PRE-CALIBRATION COMMITMENTS, not
preregistration.** Stage 0B has no frozen preregistration — the design draft says
"DRAFT. Not frozen" and the contract validates as `draft`. `Q_GAP_PREREGISTERED` is
renamed `PRECALIBRATION_COMMITTED_Q_GAP`; it was created at `120620c`, after the
runtime was characterised, by restating the 2026-09-02 displacement-scale 0.20 onto
the exposure scale, and calling it "preregistered" backdated a commitment by a day
and a runtime discovery. `PARAMETER_LINEAGE` records the old quantity, scale,
conversion and date.

**Decision: ground truth is two-tier, and the manual burden is a stated
prerequisite.** `lab/stage0b_adjudication.py`. Tier 1 is deterministic, does **not**
import `grading_v2.py` (asserted by test), and reads a flat 240-character window
with whole-answer first-occurrence ordering — deliberately not the span rule under
test. Tier 2 is a human, on the six classes where any positional rule is known to
be unreliable; deciding those by rule would certify the grader against its own
blind spot, which is the honest difficulty here rather than something the design
can engineer away. **The candidate grader may never produce its own ground truth,
and the orchestrating model may never adjudicate an answer whose grader verdict it
has seen** — both are schema errors `validate_row` refuses. **Roughly 29 of 144
batch-1 answers will need human adjudication, before the grader runs**, and that is
flagged as a precondition of dispatch rather than discovered mid-bank. Two of the
escalation classes are themselves REVISE-RECIPE triggers.

**Costs.** Batch 1 rises from 228 dispatches / $8.44 to **400 dispatches / $14.32**
— the larger holdout, plus one extra dispatch per screen-passing item for `r_D`.
Maximum 588 dispatches / $23.96.

**Contract: VALID as `draft`,** 10 open fields (was 7), 25 bindings (was 22). Three
added: `arm_D_treatment_realization`, `grader_defect_sampling_unit`,
`reference_adjudication`.

**Tests: 1656 passing (was 1618), all offline. Zero live calls.** No live
revalidation is required: no packet, agent, searcher or parser semantics changed,
and the arm-D re-execution is what the committed harness already did.

**Unchanged:** every Stage 0A-M frozen artifact; the candidate grader, still not
frozen and not touched.


---

## 2026-09-03 (fourth pass) — Pre-dispatch infrastructure repair

**Decision: A — INFRASTRUCTURE COMPLETE, BANK AUTHORING MAY BEGIN.** Zero live
calls. The calibration-run attempt stopped before authoring an item, dispatching
once or spending a cent, and the stop was correct: five things had to exist before
a single paid dispatch, and two of them were load-bearing defects rather than
missing work.

**Decision: the answer key and the exposure-screen specification are two objects,
and the schema now says so.** `CalibrationRow` carried one alias pair.
`reference_verdict` needs `expected` for a boolean item and
`value`/`tolerance`/`reject_values` for a numeric one, so those routes raised
`KeyError` — a defect that would have surfaced **after** ~350 dispatches were paid
for. The same pair was simultaneously matched against search prose, where the
accept alias `"no"` hits inside `"not"` and the reject alias `"yes"` never appears
as a claim. The two jobs coincide only on `exact_entity`. `lab/stage0b_keys.py`
types both, validates both, refuses every impossible combination, and
`key_for_route()` makes a persisted row self-sufficient on all three routes.

**Decision: the screen is route-aware, and still entirely model-free.** Entity
aliases identify the proposition when the entity is the answer. A boolean screen
uses **premise-bearing propositions** with a negation guard, because without it the
screen fires on a correct denial — C1(b)'s lesson arriving on a new route. A
numeric screen counts a numeral only when it is asserted **of the requested
quantity**, established by subject-term proximity with date-range and citation
contexts excluded, because a bare numeral matches years, ranges and citations.
Invariant **S1** binds both objects and is committed before any item is authored.

**Decision: C1 is not retroactively broadened.** C1 governs the
`accept_trap_markers` and `reject` fields of the exp001 key, matched against a
MODEL ANSWER. C1(a) and C1(b) transfer unchanged. **C1(c)'s flat prohibition on
bare numerals does not transfer**: the Stage 0B numeric screen matches a SEARCH
SUMMARY through a structured mechanism capable of showing that a numeral is
asserted of the requested quantity. Declaring C1(c) universal would broaden a rule
past the evidence that motivated it and would make the numeric route unscreenable
rather than rigorous. S1 is the Stage 0B rule, enforced by test.

**Decision: route composition is precommitted — Option A.** `grading_v2` is a span
parser plus three route mechanisms, and Stage 0A-M produced a measured defect in
two of them (30 entity false negatives; the `a09` boolean polarity class). An
aggregate `g_one` over an unconstrained mixture is a mean over three different
failure modes. The mixture — 0.50 entity / 0.25 boolean / 0.25 numeric — is held
**identical** between the grader-validation holdout and the production pool, which
is exactly what makes the aggregate bound a valid bound on the production-weighted
rate. A **per-route floor of 14 items** (⌈log 0.05 / log 0.80⌉) gives a 95% chance
of surfacing a route-specific defect at rate 0.20, so a broken route cannot hide
behind the aggregate — and PASS already requires **zero** defects, so it trips
REVISE_GRADER when it does. The floor forces a **56-item holdout**, which also
tightens the aggregate clean bound from 0.0798 to **0.0521** and *lowers* the
re-derived production n from 72 to **63**. **Option B**, route-stratified bounding
at a weighted 0.08, was derived and costed at a **106-item holdout** and is
recorded as rejected with its price, so the choice can be re-argued rather than
assumed. Boolean polarity stays balanced within ±1.

**Decision: entity-only was refused.** It would have dodged both schema defects at
a stroke. The only grader defect this project has ever measured was on the
**boolean** route, so an entity-only bank cannot detect a recurrence of the one
failure mode actually observed, while reporting a bound that looks complete.

**Decision: key verification is a defined procedure.** Recipe clause 7 demanded
provenance and named no method, while both `p` and the grader defect rate are
measured against these keys. **One authoritative primary source settles an item**;
otherwise **two independent reputable sources** must corroborate, independence
meaning not republications of one another. There is deliberately **no blanket
two-source rule** — demanding a second source where a definitive primary one exists
buys nothing and invites padding the evidence list. Every source records what it
establishes, when it was accessed and who verified it.

**Decision: key evidence is not experimental evidence.** A query used to verify a
key may never become that item's fixed experimental query. The fixed query stays
derived from the stem alone by the frozen rule. Letting a verification query that
"worked well" become the treatment would optimise the dose using observations made
while building the key — authoring the treatment against the search index. Key
evidence, the fixed query, the model-written C query and the runtime blocks are
logged and fingerprinted separately.

**Decision: ambiguous keys fail authoring mechanically.** Conflicting sources, an
ambiguous anchor, a second legitimate definition, an undetermined tolerance, an
unresolvable boolean premise, a non-unique displacing answer: each is an enumerated
rejection reason, recorded and persisted. Never repaired by picking the most
reasonable answer, and never softened by widening the accept band — both decide the
item's outcome at authoring time. This is the `a08` lesson applied at authoring
rather than discovered from a solver contesting the premise.

**Decision: the calibration driver exists and is committed before the first
dispatch.** `lab/stage0b_calibration_runner.py`. It exercises no scientific
discretion — no authoring, no repair, no re-keying, no retry. Append-only JSONL
ledger, fsynced before the next expensive call, with deterministic content-free
dispatch ids, so a resume re-dispatches nothing; that is **demonstrated** against a
synthetic backend rather than asserted. `authorize_grading()` is the only door to
candidate grading and refuses while any escalated answer lacks an attributed human
verdict, so the ordering cannot be skipped by forgetting it. This binds the
**calibration** driver; the **production** freeze/grade/analyse driver is a
different artifact and stays `[OPEN]`.

**Decision: two adjudicator rules corrected pre-dispatch.** Boolean escalation now
triggers on polarity **disagreement** rather than multiplicity — "No. X was not a
member" carries two reinforcing negatives the key settles, while "Yes, although it
was not ratified" genuinely needs a human — and numeric adjudication reads word
forms. Both reduce Terry's burden by deciding cases the key already settles; neither
weakens validation, because the key still decides and only the surface form widened.

**Costs, reported rather than absorbed.** Batch 1 rises from 400 dispatches /
$14.32 to **528 / $21.48**; human cases from ~29 to **~43**. At the cap calibration
now costs about **$28.64** against a production run of ~$24.3, so the earlier
"calibration ≤ production" heuristic **no longer holds**, and only one further
batch fits. What broke it is the per-route coverage requirement, which is a
validity constraint and not a budget preference.

**Contract: VALID as `draft`,** 31 bindings (was 25), 10 open fields. Added
`typed_answer_key`, `exposure_screen_specification`, `route_composition`,
`key_verification_provenance`, `invalid_key_policy` and
`calibration_freeze_grade_analyse_driver`.

**No calibration item has been authored and no key has been verified.** The schema,
the verification procedure, the invalid-key rules, the route quotas and the driver
are committed; the bank is not.

**Unchanged:** every Stage 0A-M frozen artifact; the candidate grader, still not
frozen and not touched.

