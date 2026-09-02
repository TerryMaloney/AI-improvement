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

**R1′ scored again, n=2.** The grader was deterministic, fingerprinted, and
covered by a 51-case golden corpus, and it mis-scored 30 of 130 production trials
in two independent ways while 1,397 tests passed. As with the 2026-09-02
`live_agent_registry` defect, every check read the rule and none read a realized
output. SUPPORTS R1′ over the churn rival.

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
