# Current Research Status

> Coordination document only. Experiment-specific frozen artifacts remain authoritative for their scope.

## Current phase

**Stage 0A-M is EXECUTED, COMPLETE and INDEPENDENTLY REVIEWED. Result: a null that
could not have been anything else — at the realized discordant count D=2, the
smallest attainable exact p is 1/4. Stage 0B's INSTRUMENT is BUILT, MEASURED and
CORRESPONDENCE-TESTED, and as of the THIRD pass of 2026-09-03 its CALIBRATION
PLAN has survived a final red team that found and fixed two load-bearing defects in
the second pass's own corrections: decision A, ready to run the calibration bank. No
Stage 0B production dispatch has occurred, none is permitted, no calibration item
has been dispatched, and no production item exists or has been authored.**

- Stage 0A-M: 130/130 dispatches under freeze `a1f4efb`, all `claude-opus-5`,
  0 voids. Neither primary class rejected. Report:
  `runs/exp004_stage0am/EXP004_STAGE0AM_REPORT.md`.
- Independent review (2026-09-02, separate session):
  `docs/EXP004_STAGE0AM_INDEPENDENT_REVIEW_2026-09-02.md`. Execution valid;
  primary reconstruction exact; the null uninformative for reasons partly
  different from those the report gives.
- The `anchored_v1` battery is at **complete** ceiling for Opus 5 (130/130 under
  a repaired grader) and is retired for confirmation.
- Stage 0B design: `docs/EXP004_STAGE0B_DESIGN_DRAFT.md`; authoring protocol
  `docs/EXP004_STAGE0B_BATTERY_AUTHORING_PROTOCOL.md`; contract
  `experiments/exp004_stage0b/causal_contract.yaml` (draft, [OPEN] fields).
- Frozen fingerprints, unchanged: battery `1ec90754f1de2696`, Stage 0A-M grader
  `10adaf1dac94ea70`, schedule `321c3a2397958c30`.
- Stage 0B instrument (2026-09-03): searcher/exposure harness, divergence probe,
  live correspondence gate 14/14 PASS with 0 UNOBSERVABLE, real sanitized runtime
  fixture. Treatment renamed on measurement to
  `runtime_exposed_search_result_block_exposure`.
- Stage 0B calibration plan (2026-09-03, third pass): batch 1 = **64 authored → 48
  screen-passing items, 400 dispatches, ~$14.32**; cap 80 screen-passing items, 588
  dispatches, ~$23.96. `lab/stage0b_calibration.py`, `lab/stage0b_adjudication.py`;
  `runs/exp004_stage0b_design/calibration_plan.json`. Stopping rules frozen and
  fingerprinted before the first calibration outcome exists.
- **Human adjudication prerequisite: ~29 of 144 batch-1 answers**, to be discharged
  BEFORE the candidate grader is run on them.
- Full suite: 1656 passing (was 1618).

## 2026-09-03 (third pass) — FINAL PRE-CALIBRATION RED TEAM

**Decision: A — CALIBRATION READY.** No calibration datum exists; **no live call
was made.** An independent review of `120620c` found that **two of the second
pass's own corrections were wrong**, and both were load-bearing. This is what the
red team was for.

**1. The grader bound pooled dependent observations.** The second pass counted
(A,C) and (A,D) as two Bernoulli trials per item, on an "exchangeability"
argument. **Exchangeability is not independence.** Both pairs are built from the
*same* closed-arm verdict on the *same* closed-arm answer, so one closed-arm
defect produced two counted events — one draw written down twice. A binomial bound
at n = 2 × items is therefore **narrower than the evidence supports**, and for an
*instrument defect* that error **under-sizes production** — the exact failure mode
§7.1 exists to prevent. It also bounded the wrong estimand: `g_one` is a property
of the A-vs-C pair, because A-vs-C is the primary.

**Corrected: the unit is the ITEM, and the bound is the (A,C) pair alone.** (A,D)
becomes a diagnostic and the only exercise arm D's answer form gets before a
production run that grades arm D too; an item-level union bound is reported as a
conservative companion. **Consequence: a clean 24-item holdout bounds `g_one` at
0.117, not 0.061 — above the 0.08 PASS threshold. Batch 1 as specified could not
have passed however clean it came back.** The holdout rises to 36 items and batch 1
to 48 screen-passing items.

**2. `q_D = 1.0 by construction` was false, and the repository already held the
refutation.** The screen tests ONE execution of the fixed query; the artifact is
**not reproducible** (§12.3) and `run_arm` **re-executes** arm D's fixed query at
answering time. The screened block is never the injected block. Freezing the
screened artifact was **rejected** — a stale D block against a contemporaneous C
block would break the one structural guarantee the C/D contrast rests on. **Arm D
re-runs its query, and the parameter is `r_D`, measured** by a second fixed-query
execution per calibration item. A non-divergent re-execution is **the measurement,
not a failure**. `CvDScenario.from_exposure` now requires `r_D` with no default.

**3. The p PASS rule tested a claim the design never made.** Requiring the 95%
lower bound to clear 0.90 rejects a recipe sitting **on this design's own point of
0.95** five times in six at n=36, and rejects one exactly at the band edge by
construction. §2.2 sets a **band**, not a certification. The band is now checked on
the **point estimate**; **sizing** uses the lower bound, the conservative
direction. Errors cost production items instead of triggering a false stop.

**4. The negative-control count is provisional.** 30 was derived against n=50 while
the same document superseded n=50. The rule is a function of the final primary n:
50→30, 66→40, **72→42**, 90→54. No control item is authored until production n is
fixed.

**5. Terminology.** Stage 0B has **no frozen preregistration**.
`Q_GAP_PREREGISTERED` → `PRECALIBRATION_COMMITTED_Q_GAP`, with lineage to the
2026-09-02 displacement-scale 0.20 recorded rather than backdated.

**6. Ground truth has a named producer and a stated cost.**
`lab/stage0b_adjudication.py`: a deterministic tier-1 reference that does **not**
import the grader and decides only what the key can decide, plus **human**
adjudication on the six classes where a positional rule is known to be unreliable —
deciding those by rule would certify the grader against its own blind spot. The
candidate grader producing its own ground truth is a **schema error**. **Manual
prerequisite: ~29 of 144 batch-1 answers, flagged before dispatch.**

**Tests: 1656 passing (was 1618).** 38 added, all offline. **Zero live calls.**

**LIVE REVALIDATION: NOT REQUIRED.** No packet, agent, searcher or parser semantics
changed; the arm-D re-execution is what the committed harness already did. The
14-check runtime correspondence gate still describes the instrument in the tree.

## 2026-09-03 (second pass) — PRE-CALIBRATION DESIGN RECONCILIATION

**Decision: A — CALIBRATION DESIGN READY TO RUN.** No calibration datum exists and
**no live call was made in this pass.** Everything below is a design and statistics
change made before spending the calibration budget, which is the only time such
changes are free of the data.

**Six statements in the authoring protocol described a runtime nobody had run.**
Enumerated and superseded in place at
`docs/EXP004_STAGE0B_BATTERY_AUTHORING_PROTOCOL.md` §0, not edited away. The
load-bearing three: "top-5 results" names an object that does not cross the
boundary; whole-block reject matching would have admitted an item on a link-title
date range; and "run the calibration bank closed-book" cannot measure three of the
four things the bank exists for.

**`c_disp` is renamed and split by arm, because it named content that does not
exist.** It said "P(retrieved content carries displacing information)"; no
retrieved page content crosses the boundary. Now `q_C` = P(the **C-arm** block's
runtime-synthesised summary carries a reject alias | screen-passing), **measured
from the C arm** by a query-writer dispatch plus a C search — and `q_D`, which the
divergence screen pins at **1.0 by construction** on the production pool and which
is therefore never estimated. The fixed-query rate may not substitute for the
C-arm rate. `Scenario.c_disp` → `Scenario.q_exposure`. `δ` stays a **preregistered**
0.30: it is the estimand, and measuring it in calibration would size the run on a
first look at its own effect.

**The "≥3× production" calibration rule had no derivation, and was wrong in both
directions.** Asserted in four documents, computed in none. Too *small* for what it
had to measure (design draft §2.4 dispatches calibration items closed-book only,
so no `q_C`, no `q_D`, no grader behaviour on exposed answers); too *large* under
the realized six-dispatch structure (~$35 for 150 items, more than the run it
protected). Replaced by a bank sized from the four decisions it resolves, with a
frozen sequential plan and a cap where calibration costs about what production
costs.

**The finding that changes the recommended n.** At n=50 the design holds 80% power
only while the *asymmetric* grader defect rate `g_one` ≤ **0.014**, and bounding
that with zero observations needs **213 clean closed/exposed pairs** — four times
the production run. **No affordable calibration bank certifies the grader for
n=50.** So production is sized AT the bound calibration can actually reach: `q_C`
at its point estimate, `g_one` at its 95% upper bound. At the achievable bound of
0.08 the required n is **72**. The §7.2 recommendation of n=50 is superseded. This
is §7.1's own conclusion — prefer fixing the instrument over increasing n — arriving
with a price attached.

**What makes that bound affordable:** one calibration item yields **two**
closed/exposed pairs, (A,C) and (A,D), not one. Exchangeability rests on the
packet, block format and answerer agent being byte-identical between C and D, and
the two pair-wise defect counts are reported **separately** so the licence can be
falsified rather than assumed.

**Negative controls: 30, derived — not 15 and not 20.** Both prior numbers were in
the repository at once. 15 was Stage 0A-M's realized `arithmetic_control` size
carried into the power module; 20 was design draft §8's 15 reused + 5 fresh.
Neither excludes a generic exposure tax of **0.10** — the entire minimum
rejectable primary signal at n=50. The primary cannot reject below D=5, so a clean
control's 95% upper bound must clear 5/50: n=29 is the exact minimum (0.098), and
30 is taken so the composition stays 15 reused + 15 fresh. It is a **function of
the primary n**, recomputed if power re-derivation moves it. Brittleness declared:
one harm lifts the bound to 0.149, and the preregistered response is a **reporting
rule**, not more items.

**The direct query→answerer path: the claim is narrowed, not engineered away.** The
runtime block echoes the query, so C and D differ through the query text, the
synthesised answer and the link list at once. **Keep the echo** (stripping it would
make the injected block differ from what the runtime exposes — the exact mistake
the "verbatim" claim already cost this design), **no arm added**, and C-vs-D now
estimates *the total downstream effect of the query-construction procedure under
this realized search runtime*. It is **not** a claim about retrieved page content;
decomposition is a named follow-on. Enforced in `authorize()`'s `claim` field.

**The grader development/validation wall.** The trap — "the grader failed, so we
edit it until these answers pass" — is closed by three rules: the hand-derived
verdict is recorded **before** the grader runs (`hand_verdict_recorded_first`, a
schema error if absent); repairs are developed on the **development** subset only
and must be general semantic rules; the rate is bounded on the **holdout** only,
and a repair informed by a holdout answer **burns** that holdout.

**Stopping rules frozen and fingerprinted before the first calibration outcome.**
PASS / CONTINUE / REVISE-RECIPE / REVISE-GRADER / REVISE-DESIGN are implemented in
`lab.stage0b_calibration.decide`, added to `instrument_fingerprints.json`, and
pinned by test — for the same reason the grader is fingerprinted: a stopping rule
that can be edited once the data arrives is not a stopping rule.

**Cost plan.** Measured Stage 0B unit costs replace the estimates: searcher
$0.0640 (mean of six real dispatches), query-writer $0.0136, exposed answerer
$0.0276 (was a $0.025 estimate). Batch 1 **228 dispatches / $8.44**; maximum
**532 / $19.69**.

**Contract: still VALID as `draft`,** 7 open fields. Four bindings added —
`calibration_bank_sizing`, `grader_validation_holdout`, `negative_control_sizing`,
`query_echo_direct_path` — and `item_selection_rule` moves from `[OPEN]` to bound
with its fingerprint still open.

**Tests: 1618 passing (was 1569).** 49 added, all offline. **Zero live calls.** The
14-check runtime correspondence gate was NOT re-run: nothing in this pass changes
the instrument it measured.

**Unchanged:** every Stage 0A-M frozen artifact; the grader, which is still not
frozen and was not touched.

## 2026-09-03 — STAGE 0B INSTRUMENT BUILT AND MEASURED; R1′ SCORING CORRECTED

**Decision: A — READY TO AUTHOR/RUN THE CALIBRATION BANK.** The blocker that forced
decision B is cleared. **The calibration bank was deliberately NOT run in this
pass**: it is the first thing that produces solver outcomes and should start from a
committed, reviewed instrument rather than one built in the same breath.

**The design draft was wrong about the runtime in three ways, and the corrections
are the substance of this pass** (`docs/EXP004_STAGE0B_DESIGN_DRAFT.md` §12):

1. **"The searcher returns the block verbatim" is false.** The searcher model
   reformats into markdown, drops the header and the trailing instruction, and
   duplicates the source list *because that instruction told it to*. The recorded
   artifact is therefore taken from the runtime's own `tool_result` block, exposed by
   `--output-format stream-json`, and the searcher's prose is audit-only. A model no
   longer sits between the query and the recorded content.
2. **There are no snippets.** The runtime block is: a header echoing the query, a
   `Links:` array of **titles and URLs only**, a **model-synthesised prose answer to
   the query**, and a trailing imperative addressed to the reader. The treatment is
   renamed `runtime_exposed_search_result_block_exposure`. Because the synthesised
   paragraph is a second model's answer generated inside the search tool, a
   displacement effect could originate there rather than in any retrieved page, and
   no Stage 0B claim may say "retrieved content" without that qualification.
3. **The artifact is not reproducible.** Two dispatches of an identical query gave a
   byte-identical `Links:` array and a *different* synthesised paragraph. The hash is
   per-trial provenance, not a reproducibility guarantee. Both fixtures are committed
   so the distinction is testable.

**The trailing imperative is stripped before injection, and the stripped text is
recorded.** Left in, it would tell C and D answerers to emit markdown source lists —
a format change arm A never receives, landing on the grader's leading-sentence span
rule. That is the treatment-correlated instrument risk the design rejects structured
output for.

**Live correspondence: 14/14 PASS, 0 UNOBSERVABLE, 6 dispatches, $0.19.**
`experiments/exp004_stage0b/runtime_correspondence.json`. Every check dispatches.
Fresh context is measured with a planted marker; key quarantine as an empty realized
tool surface plus self-report; C/D symmetry on realized command lines and realized
tool surfaces. Query fidelity byte-checked against `tool_use.input.query`: 6/6.

**Divergence probe ran on canaries only:** 4/4 executed, 4/4 queries faithful, 4/4
pre-recorded predictions matched, 3 divergent, no solver, no answer, no outcome.
`runs/exp004_stage0b_instrument/divergence_probe.json`.

**The divergence flag had to be made to locate its matches.** On the real Lovelace
block the reject alias `1852` matched inside the link title "Ada Lovelace (1815 -
1852)" — a date range asserting nothing. Whole-block containment would have admitted
that item. `divergent` now requires the alias in the runtime's synthesised summary.

**Search-attempt indicator bound to a value that exists:**
`sum(modelUsage[*].webSearchRequests)` over ALL models. `usage.server_tool_use`
reports 0 on a dispatch that demonstrably searched, and WebSearch is billed to
`claude-haiku-4-5`, not the solver — reading the solver's count would give zero
every trial.

**C-vs-D is underpowered for the claim it exists to support.** At n=50 it has power
**0.60** against the preregistered gap of 0.20 (needs n=76); under Stage 0A-M's
symmetric 20% grader error it is unpowered at every n ≤ 240 — symmetric noise
*manufactures balanced discordance* there, unlike in the one-sided primary where it
deletes items silently. Not promoted to primary. A pre-freeze `authorize()` gate and
a fixed reporting rule (< 6 discordant pairs ⇒ "UNINFORMATIVE — INCAPABLE OF
REJECTING", never "no evidence") are committed. `lab/stage0b_cvd.py`.

**R1′ SCORING CORRECTED.** The review's "supported again, n=2" is not licensed by the
frozen prospective table, which classifies `grader` as symmetric, `check_executed:
true`, R1′ risk **low**. Under the table's own rules a defect there is `HURT_BOTH`.
**Prospective confirmations of R1′ remain n=1.** The empirical grader failure is
untouched; only the theory scoring changed, and R1′ was *not* rewritten to win — a
successor hypothesis (R3′, realized-output correspondence) is recorded as a
candidate with **zero** prospective evidence until its own table is frozen.
`experiments/meta_r1r2/observation_2026-09-03_grader.md`.

**Causal contract: VALID as `draft`,** with 7 genuinely open fields and 4 `[OPEN]`
bindings. Not `freeze_ready`, and must not be. New node `query_writer` added to the
shared vocabulary, because a multi-dispatch trial puts a second model inside one arm
and the edge `query_writer → outcome` could not otherwise be written down.

**Tests: 1569 passing (was 1466).** 103 added. Parser tests run against a real
sanitized runtime transcript, not invented examples — which is exactly why the
"verbatim" claim did not survive.

**Unchanged:** every Stage 0A-M frozen artifact.

## Red-team of the remediation (2026-09-01)

Survived: bodies byte-identical; `model: inherit` on both; tool difference exactly {WebSearch, WebFetch}; TodoWrite symmetric and non-informational; packets differ only in the TOOLS block; no hooks; no user-scope shadow of the dedicated agents (user scope holds only the shared `solver-*` agents, which is why they appeared twice in the agent list — harmless, but recorded).

Repaired: the two `description` fields carried arm labels ("closed arm" / "retrieval-enabled arm"). Bounded, not load-bearing — the packet already reveals tool availability — but metadata should not name the treatment; now identical. The symmetry record's body hash had been computed by a different method than the test uses (file hashes matched, bodies were identical); recomputed. One earlier test string-matched a paraphrase ("web search") and broke when the GPT session reworded the TOOLS block to name the tools; it now checks the actual invariant against the dedicated agent.

Accepted as improvements: the GPT session's TOOLS rewording — the closed arm's old "you have none" was literally false with TodoWrite present.

## Budget

See `experiments/exp004_stage0am/cost_ledger.md`. Production is **not affordable from this session** (~$49 projected at its ~200K-token context) and only marginally so from a fresh one (~$24–38). The budget-start rule requires a measured per-trial cost from the canaries before any production dispatch.

## Newly found arm-symmetry confound

The Stage 0A-M packet templates were nearly arm-symmetric, but the actual shared Claude subagents were not.

`.claude/agents/solver-web.md` adds web-arm-specific system instructions including premise checking, source-independence reasoning, dating claims and conflict-resolution guidance.

`.claude/agents/solver-closed.md` carries a different epistemic system prompt concerning stale knowledge, premise doubt, confidence and abstention.

Because custom Claude Code agent markdown bodies are system prompts, executing Stage 0A-M with those agents would contrast **instructions + retrieval access**, not retrieval permission alone. This was discovered before any production output existed.

## Candidate repair

Stage 0A-M now has dedicated agents:
- `.claude/agents/stage0am-solver-closed.md`
- `.claude/agents/stage0am-solver-web.md`

Their markdown bodies are byte-identical. Both use `model: inherit` and retain `TodoWrite`; the retrieval-enabled agent differs in tool access only by `WebSearch` and `WebFetch`.

Machine-readable candidate invariants/hashes:
`experiments/exp004_stage0am/agent_symmetry.candidate.json`

Regression tests:
`tests/test_stage0am_agent_symmetry.py`

Authoritative remediation note:
`docs/EXP004_STAGE0A_M_AGENT_SYMMETRY_REMEDIATION.md`

The shared solvers were deliberately left unchanged because older experiments may depend on their behavior.

## Retrieval environment already measured

The previous frozen probe established on the old shared solver-web path:
- WebFetch: 5/5 `REFUSED_BY_PROXY`, including `example.com`;
- WebSearch: 2/2 `OK`, with substantive extracted text.

`E` was therefore search-capable, fetch-blocked.

Because Stage 0A-M now uses a dedicated web agent, execution-time preflight must re-run the same neutral environment check through `stage0am-solver-web`. Reachability is expected to match but must be measured, not assumed.

## 2026-09-02 — INDEPENDENT POST-RESULT REVIEW OF STAGE 0A-M + STAGE 0B DESIGN

**Independent review by a separate session.** Full verdict table:
`docs/EXP004_STAGE0AM_INDEPENDENT_REVIEW_2026-09-02.md`. Reproduce with
`python -m lab.stage0am_review`. **Nothing frozen was altered.**

**EXECUTION VALIDITY: clean, no qualification.** 130 raw files ≡ 130 ledger rows
≡ 130 graded rows; 65 complete pairs; one freeze commit `a1f4efb` across all
trials; 0 voids, 0 dispatch failures, 0 permission denials, 0 harness errors;
schedule compliance errors 0/65; all freeze hashes recomputed and matched.

**PRIMARY RECONSTRUCTION: reproduces the official result exactly.** Re-running the
frozen grader on the frozen answers gives all 130 grades with 0 mismatches.
`date_anchored` 14/1/1/9, D=2, p = **3/4** in exact rationals; `definition_anchored`
D=0 p=1; control 15/15. Every field of `analysis.json` agrees. No material
disagreement on the result — the disagreements are about its interpretation.

**Four findings that go beyond the Stage 0A-M report:**

1. **The run could not have rejected.** At D=2 the smallest attainable exact p is
   **1/4**. Rejection needs D≥5 at α=0.05, D≥6 at the Holm first step. Stage 0A-M
   was incapable of rejecting before a single grade was read.
2. **A second, unreported grading artifact, on the boolean route.** `a09` opened
   with "Yes." in *both* arms and was graded incorrect in both, because `no`
   matches inside "no longer a member state" 409 characters later. The rule is
   polarity-asymmetric: only `expected=True` items are exposed, and 6 of 7 boolean
   items expected False, which hid it.
3. **The battery is at COMPLETE ceiling, not mostly.** All 32 entity trials named
   the correct entity; in all 28 graded-incorrect cases it appeared *strictly
   before* the reject. Under a repaired grader the run scores **130/130** with D=0
   in every class. All 30 incorrect grades in the experiment are instrument
   artifacts. `anchored_v1` contains zero items Opus 5 gets wrong.
4. **All 8 retrieval attempts landed in the ceiling class.** `definition_anchored`
   8/25; **`date_anchored` 0/25**; control 0/15. The only class with outcome
   variance received zero doses of the mechanism. Both discordant retrieval-arm
   trials issued **zero searches**, so the two discordant pairs are provably
   grading artifacts, not inferred ones.

**Corrections to the report's reasoning, not its numbers:** "ceiling ⇒ no
information" is wrong — the spec's own power model says a *closed-arm* ceiling is
the most favourable condition, and `definition_anchored` produced the run's
tightest harm bound (≤0.113 availability; ≤0.312 restricted to the 8 trials that
actually retrieved). And `analysis.json`'s `retrieval_failure_rate`
(`attempted_retrieval: 0`) is **vacuous** — `analyse_run` fed it empty tuples;
it must not be cited. The primary result does not depend on it.

**STAGE 0B DESIGNED, NOT AUTHORIZED.** `docs/EXP004_STAGE0B_DESIGN_DRAFT.md`.
Objective: whether **retrieved content** can displace an otherwise-correct
anchored answer, and whether displacement comes from the content or the query —
with uptake forced to 1.0 by harness construction rather than requested.
Arms **A (closed) + C (required, model query) + D (required, fixed query)**;
**B dropped**, because an optional arm at Stage 0A-M's uptake is unpowered at
every n≤120. Grader repaired (`lab/grading_v2.py`, span-scoped, three verdicts):
repairs all 30 false negatives, adds none, two enumerated residuals. Power sized
on **expected discordance** (`lab/stage0b_power.py`): n=50 primary, K=1, α=0.05,
E[D]=7.1, power 0.858, MDE δ=0.30, ≈$15. Battery: `date_anchored` and
`definition_anchored` **RETIRED**, arithmetic control **REUSED** plus 5 fresh items.
Environment scoped as `search_snippet_exposure`, fetch-blocked, replication planned.

**DECISION: B — MORE DESIGN WORK REQUIRED.** The searcher and results-injection
harness are unbuilt, so the divergence probe cannot run, so the calibration bank
cannot run, so the item recipe is unvalidated. Authoring against an unvalidated
recipe would repeat Stage 0A-M's actual mistake.

**Tests:** 1466 passing (was 1404).

## 2026-09-02 — STAGE 0A-M EXECUTED AND COMPLETE

**130/130 dispatches, 0 voids, 0 dispatch failures, all on `claude-opus-5` under freeze `a1f4efb`.** Report: `runs/exp004_stage0am/EXP004_STAGE0AM_REPORT.md`.

**Result: NULL at a realized sensitivity far below plan.** Neither primary class rejected. `date_anchored` n00=14 n01=1 n10=1 n11=9, D=2, p=0.750. `definition_anchored` n11=25, D=0, p=1.000. Arithmetic control 15/15, D=0. Licensed claim: no claim that any authored item is harmed by the retrieval-enabled procedure.

**Why the null is nearly uninformative — two independent power failures:**
- `definition_anchored` (25/25) and arithmetic (15/15) sat at a **complete ceiling** in both arms; zero discordance is possible there.
- `date_anchored` scored 10/25 in both arms mostly through a **grading artifact**: 28 of 50 trials named the correct anchored entity but were graded incorrect because the frozen `exact_entity` rule gives rejects precedence and Opus 5 supplies temporal context naming the successor.
- **Both discordant pairs are the same artifact.** In all four trials the solver named the correct entity; only whether it also mentioned the successor differed. The lone "harm" and lone "help" are elaboration style, not displacement.

**The grader was not changed after outcomes.** The defect is reported, not repaired.

**Retrieval was barely exercised:** attempted in 8/65 treated trials, declined in 57. Among the 8 that retrieved, 8/8 correct and their closed partners 8/8 — zero discordance. Realized effort near-identical across arms (P4 not supported); no served-model fallback (P2); availability-without-use showed no effect at near-zero power (P3).

**Dispatch repair that made execution possible:** identical command line per arm, `claude -p --agent <agent> --model opus --allowedTools WebSearch WebFetch`; realized surfaces closed `[]` / retrieval `[WebSearch, WebFetch]`; agent frontmatter deliberately unedited (an empty `tools:` risks "inherit all tools" and would break key quarantine). A **live** runtime correspondence gate now blocks production if realized surfaces drift — the static tests could not see this class of failure.

## 2026-09-02 — execution attempt blocked at runtime preflight (superseded)

**Stage 0A-M did not run. Production dispatches 0; treatment exposure NONE.** Three screen-class synthetic dispatches; no production stem shown to any model.

**Blocker:** `stage0am-solver-closed` cannot be spawned — `TodoWrite` is unrecognized in Claude Code 2.1.248, so the closed arm's tool list resolves to empty and the harness refuses a zero-tool agent. Realized surfaces: closed `[]`, retrieval `[WebSearch, WebFetch]`. The informational difference is still exactly the two retrieval tools, but the recorded "both arms carry TodoWrite" symmetry justification is **false at runtime**, and 1,397 green tests missed it because every check reads the file, none the runtime.

**Not repaired here:** every fix changes the treatment definition (tool surface of both arms) and no safe recognized non-informational tool was identified. Options and a recommendation are in `docs/results/STAGE0AM_RUNTIME_BLOCKER_2026-09-02.md`.

**Passed:** static suite 1,397/0; environment `E_current` = search-capable, fetch-blocked, **matching E exactly** (WebFetch 5/5 refused incl. example.com; WebSearch 2/2 OK); retrieval canary launched and returned gradeable JSON on `claude-opus-5`.

**Open:** arm model symmetry UNVERIFIED (closed arm never ran); fresh-context isolation UNTESTED.

**Prospective prediction scored:** the defect landed in a pre-declared R1′-high / churn-low cell (`live_agent_registry`). SUPPORTS R1′ over churn, n=1 — `experiments/meta_r1r2/observation_2026-09-02.md`.

## 2026-09-02 — last pre-results pass (zero dispatches)

- **Causal contract implemented** (`lab/causal_contract.py`, tests, example, Stage 0B draft, Stage 0A-M retrospective fixture). Prospective rule for future families; not a Stage 0A-M gate.
- **Grader golden corpus** (`tests/golden/…`, 51 hand-derived cases): the frozen grader passed **unchanged**; corpus pinned to grader sha `10adaf1dac94ea70`.
- **R1′/R2′ prospective table frozen** at `experiments/meta_r1r2/` (fingerprint in `FINGERPRINT.txt`, churn mechanical from git). Scored at the next independent audit; nothing from this pass counts.
- **Robust-EVOI wording corrected** (no optimistic max; lower bound over the plausible set + bounded calibration budget). **Configured vs realized effort** separated: configured = symmetry invariant; realized = mediator/outcome, never equalised.
- **Zero-dispatch tests:** P1 NOT TESTABLE (no dual-route cohort); P7 NOT TESTABLE mechanically; **M2 downgraded** — the memo's "no budget line in verified_flat" premise was false. R1′/R2′ **unchanged**. See `docs/results/`.

## 2026-09-01 note

- The dedicated `stage0am-solver-closed` / `stage0am-solver-web` agents became registered in the original session after a context reload landed on a later turn; the runtime gates in `docs/NEXT.md` can now be run from that session or a fresh one. No gate has been run yet.
- A research-discovery memo (`docs/FABLE_5_1_RESEARCH_DISCOVERY_2026-09-01.md`) proposes pre-registering Stage 0A-M *secondary* analyses before outcomes and three zero-design-change freeze-record additions (`effort_level`, live agent list, grader golden corpus). These are proposals; nothing frozen changed.

## Still prohibited

Until the candidate repair passes the full non-production suite and synthetic Claude canaries:
- no Stage 0A-M production dispatch;
- no production-item exposure;
- no production run directory;
- no outcome-based battery change;
- no runtime re-keying/reclassification;
- no Stage 0A-N or Stage 0B execution.

See `docs/NEXT.md`.
