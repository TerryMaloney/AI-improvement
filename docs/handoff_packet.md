# Epistemic Control System — Handoff Packet for Claude Code
### Everything needed to pick this up and keep building, without re-deriving anything.

---

## 0. What this project is, in one paragraph

A control layer that sits between a user's question and a model's answer, deciding (a) what type of claim is being made, (b) whether it needs external verification at all, and (c) how to verify it cheaply if so — instead of either blindly trusting the model or expensively verifying everything. Built and tested by hand across a long design session before any real code existed; three working Python files now exist as a first Phase 2 implementation. The single biggest open question — does this beat a well-prompted frontier model at comparable cost — is still untested. That's Phase 3, and it's the highest-priority thing to build next.

---

## 1. Current code state — what's actually built and tested

Three files, all working, all run and verified during the design session (not just written and assumed correct):

- **`epistemic_layer.py`** — Phase 2 deterministic layer. `classify_claim()` routes a question into EMPIRICAL / NORMATIVE / PREDICTIVE / DEFINITIONAL / DETERMINISTIC. `EntityRegistry` + `EntityRecord` implement the three-bucket TTL system (VOLATILE / SCHEDULED / STABLE). `BudgetCeiling` is a hard call-count backstop. `route()` is the entry point tying it together.
- **`question_battery.py`** — the actual 15-question test set accumulated across the session, as structured data, with known answers and trap-flags where already verified.
- **`harness.py`** — runs the battery through `route()`, logs decisions and metrics. **`call_baseline_model()` and `call_verified_model()` are unimplemented stubs on purpose** — no API key was available in the environment that built this. Wiring these to real calls IS Phase 3.

**Bugs found and fixed during first run (leave this history in the code comments, don't clean it up):** the original arithmetic detector matched a bare `"-"` character, which fired on any hyphenated word ("US-Japan", "entity-hazard") and misrouted false-premise trap questions into "compute, don't search" — silently bypassing verification. A second bug: bare `"how many"` misclassified "how many people died in 1918" as arithmetic because "1918" looked like a digit operand. Both fixed by requiring actual arithmetic word/symbol patterns between two numbers, and by defaulting to EMPIRICAL (safe: costs an extra search) rather than DETERMINISTIC (unsafe: skips verification) whenever the classifier is unsure. **This bug and its fix are themselves the best demonstration in the whole project of why "ship it, then test it against real cases" beats "reason about it until it seems right."**

---

## 2. What to build next, in order

1. **Wire `call_baseline_model` / `call_verified_model` to a real API.** This is the entire unblock for everything else.
2. **Run Phase 3 for real**: baseline (model alone, no procedure) vs. verified (model + Phase 2 routing) on the 15-question battery, extended with the abstract-question battery from §6 below. Log real token counts, call counts, and correctness — not eyeballed estimates like the design session used.
3. **Calibrate the VOLATILE-bucket threshold.** Currently a flat 30-day default in `EntityRecord.needs_reverification()`, chosen by eyeballing two examples (OpenAI CRO turnover, UK PM turnover). This needs actual data — track observed reappointment intervals for a larger sample of entities and set the threshold empirically, not by guess.
4. **Grow `EntityRegistry` past three hardcoded seed records.** Real use needs either a lightweight persistent store (SQLite is enough — do not build a graph database for this) or an ingestion path that adds entities as they're encountered.
5. **Only after Phase 3 shows a measurable, cost-justified win:** add the LLM-judge layer (independence-by-content checking, conflict resolution, the normative/predictive/definitional verification moves) — this is Phase 4 and is explicitly conditional, not automatic.

---

## 3. Full architecture map

```
USER QUERY
    ↓
CHEAP TRIAGE (rules / small classifier — NOT a full model call by default)
    ↓
CLAIM TYPE CHECK
    ↓
┌────────────┬─────────────┬──────────────┬──────────────┐
↓            ↓             ↓              ↓
EMPIRICAL    NORMATIVE     PREDICTIVE     DEFINITIONAL
↓            ↓             ↓              ↓
[factual     [assumption   [forecast,     [surface which
 pipeline]    audit +       calibration,   definition is
              sensitivity]  not verdict]   in use]
    ↓
(empirical path continues:)
PROBLEM COMPILER → FAILURE PREDICTOR → INVESTIGATION PLAN
    ↓
TOOLS/MODELS → EVIDENCE FIREWALL → PROVENANCE/LINEAGE
    ↓
INDEPENDENCE CHECK (content-based, NOT date-matching)
    ↓
CONFLICT DETECTED? → CHEAP RESOLUTION ATTEMPT (1 extra retrieval)
    ↓                        ↓
RESOLVED                STILL AMBIGUOUS
    ↓                        ↓
DETERMINISTIC VERIFICATION   STOP TEST / ABSTAIN
    ↓
ANSWER / CONTINUE / ABSTAIN
    ↓
OUTCOME → EXPERIENCE → FUTURE ROUTING POLICY

Permanent rails: HARD COST/TIME CEILING · ADVERSARIAL CONTROLLER TESTS · FULL AUDIT TRAIL
```

Entity-hazard TTL buckets (used by the EMPIRICAL path):

| Bucket | Signal | Check cost | Known weak point |
|---|---|---|---|
| VOLATILE | High turnover for *this specific entity*, no fixed term | Cheap, one search | Threshold is eyeballed (see §2.3) |
| SCHEDULED | Known term-end date | Free once the date is known | None found yet |
| STABLE | Long typical tenure, nonzero hazard — never treat as infinite | Periodic, not every query | None found yet |

---

## 4. Full failure matrix

### Original 12 (from the source packet)
Hallucination · Sycophancy · AI stacking · RAG error · Tool misuse · Citation washing · Premature stopping · Endless loops · Confirmation bias · Reward hacking · Prompt injection · Memory poisoning.
**Tested this session:** hallucination (confirmed via false-premise trap), AI stacking (confirmed in the wild, OpenAI CRO story), premature stopping (refined into "cheap resolution attempt"), prompt injection (held, cheap). **Not directly tested:** the other eight.

### Found this session
| Failure | Defense | Test status |
|---|---|---|
| Verifier regress | Deterministic checks first; LLM-judge fallback uses different model family than generator | Theoretical only |
| Controller cost > investigation cost | Rules/small-classifier triage before model call | Confirmed: ~1/3 of calls added zero value in early rounds |
| Independence-by-lineage misses paraphrase correlation | Content-value check, not date-matching | Confirmed both directions (OpenAI CRO story = false negative risk; UK PM story = false positive risk) |
| Goodhart on the controller itself | Adversarial eval track | Theoretical only |
| Type-assignment attack surface | Dedicated adversarial suite | Theoretical only |
| Temporal decay of committed facts | Entity-specific TTL, not flat category | Confirmed repeatedly (CRO, UK PM, Fed Chair all caught real stale facts) |
| Unbounded cost on EIG spirals | Hard budget ceiling, independent of EIG math | Theoretical only; `BudgetCeiling` class exists but untested under a real runaway case |
| Novelty illusion | Require specific citation before abandoning a project idea; multi-vocabulary search before claiming novelty | Directly motivated by a real user experience this session |
| False objectivity | Type-label before verifying; normative claims never get "verified," only "consistent given stated priorities" | Found live in the project's own prior output |
| Assumption laundering | State which assumptions a conclusion depends on + sensitivity to reweighting | Tested, held |
| Premature closure on open/predictive questions | Resolution = describe disagreement honestly + what would move it | Tested, held |

---

## 5. Refinement pass — what still holds, what needs re-checking

This section exists because the project's own TTL logic (§3) applies to its own factual claims, not just to test questions. Treat this as the first real application of that rule to itself.

**Facts verified during the session — re-verify before relying on them, per their own bucket:**
| Fact | Bucket | Verified as of | Action before use |
|---|---|---|---|
| OpenAI CRO = Dali Rajic | VOLATILE | Aug 13, 2026 | **Re-verify — this seat changed twice in under two years; treat any gap over ~30 days as stale by the project's own rule.** |
| UK PM = Andy Burnham | VOLATILE | July 20, 2026 | Re-verify — same reasoning, 7 PMs in 10 years. |
| Fed Chair = Kevin Warsh | SCHEDULED | Verified Aug 2026 | Safe until term end (May 21, 2030) barring resignation — lowest-priority re-check of the three. |
| NATO SG = Mark Rutte | scheduled-hybrid | Verified Aug 2026 | Term structure is 4yr/renewable — moderate priority. |

**Reasoning/architecture claims — stable, don't need re-verification, but worth restating rather than assuming carried forward:**
- Deterministic-first build order (Phase 2 before Phase 4) — a normative decision under a stated priority (cost discipline over early coverage of subtler failures), not a fact. Still holds under that priority; would flip if consequence-of-error becomes much higher than cost (e.g., a high-stakes deployment).
- "Independence" as used throughout = non-shared sourcing, NOT true statistical independence. This was named honestly late in the session — don't let it quietly regress back to being treated as the stronger claim.
- The novelty assessment (§7 in the prior map, condensed in §8 below) is reasoned from a real but time-bound prior-art search. **This is the one most likely to have shifted — the field moves fast; re-run the multi-vocabulary search in §8 before treating the "fragmented, open gap" framing as current.**

**What was NOT re-verified in writing this packet:** the specific claims above are stated as of the design session (~Aug 27, 2026). No fresh search was run to write this section — that's intentional, matching the project's own cost discipline (don't spend a verification call unless something is about to be relied on). Whoever picks this up in Claude Code should treat every VOLATILE-bucket fact as needing a fresh check before the harness uses it as ground truth.

---

## 6. Abstract-question battery (for extending Phase 3 beyond factual questions)

| Question | Type | Correct handling |
|---|---|---|
| Should the deterministic layer be built before the LLM-judge layer? | Normative | State the weighting (cost discipline), not a bare verdict |
| Real current-events questions vs. formal benchmarks — which now? | Normative | Depends on stated goal (cheap iteration vs. externally-checkable comparison) |
| Will this system outperform a well-prompted frontier model at comparable cost? | Predictive | Calibrated forecast, not a verdict — this is what Phase 3 itself resolves |
| Will the entity-hazard TTL bucketing hold on 20 more untested entities? | Predictive | Moderate confidence on the logic, low confidence on the thresholds — say so |
| Is evidence-lineage independence the same as statistical independence? | Definitional | No — name the weaker proxy being used |
| What counts as "wasted" verification cost? | Definitional | State which definition is in use; note it changes the accounting |

Score these not on right/wrong (doesn't apply) but on: did the response correctly identify its own claim type and avoid borrowing empirical-style confidence or false abstention.

---

## 7. Phase status

- **Phase 0 (manual hypothesis generation): done.** Diminishing returns reached.
- **Phase 1 (prior-art search): done.** See §8.
- **Phase 2 (deterministic layer): first version done, tested, one real bug found and fixed.** Needs threshold calibration and registry growth (§2).
- **Phase 3 (real baseline-vs-layer harness): not started.** Highest priority. Blocked only on API wiring.
- **Phase 4 (LLM-judge layer): not started, explicitly conditional on Phase 3 results.**

---

## 8. Prior art landscape (re-verify before trusting — see §5)

| Component | Nearest prior art found | Gap |
|---|---|---|
| Verification via generated sub-questions | Chain-of-Verification (CoVe), 2023 | None — direct match |
| Adaptive retrieval routing | Self-RAG | None — direct match |
| Abstention on false premises/stale data/ambiguity | AbstentionBench, 2025 | None — matches closely |
| Reduce over-abstention via cheap extra evidence | ReCoVERR, 2024 | None — matches "cheap resolution attempt" exactly |
| Typed claim grounding + budget-gated decisions | GSAR (Oracle, April 2026) — closest single hit | Narrower scope; no entity-hazard TTL work |
| Full synthesis as unified infrastructure | Survey: *"From Agent Traces to Trust"* (June 2026) calls this fragmented/unsolved | This is the actual open gap, per a recent credentialed source |
| Predictive/forecast tracking | Terry's own `cee-framework` project has a "Forecast Records" component already | Not yet connected to this project |

**Honest bottom line, unchanged:** primitives aren't novel. The specific tested synthesis (entity-hazard TTL, content-based independence, cheap-resolution-before-abstain, claim-type routing) isn't obviously published in this combination as of the search date above.

---

## 9. Where to find questions AI still struggles with (for stress-testing Phase 3 harder, or just genuine research)

Real, current sources — checked as of this session, scores move fast so re-check dates before quoting:

- **ARC-AGI-2** (arcprize.org) — abstract/fluid-reasoning puzzles designed to resist brute-force pattern matching. As of June 2026, top frontier models sit around 77–85% against a ~60% human panel average, and the **85% grand-prize bar remains uncleared on the held-out private set** — genuinely unsolved, not saturated.
- **ARC-AGI-3** (launched March 2026) — interactive/agentic reasoning environments, much harder: frontier models scored **below 1%** in the initial preview while humans solved 100%. The clearest current example of a benchmark models are nowhere close to touching.
- **FrontierMath** (Epoch AI, epoch.ai/benchmarks) — original, unpublished research-level math problems states can't have memorized. Tier 4 (the hardest tier, 43 problems) had a top score around 83% as of late August 2026 from a top reasoning model, but many other frontier models sit far lower, and the *average* across tracked models is much lower than the leader — good source of problems that separate "frontier" from "merely strong."
- **Humanity's Last Exam (HLE)** — 2,500 expert-written questions across math, humanities, and sciences. Best models were around 35% as of early-to-mid 2026 versus ~90% for human domain experts — a real, large, persistent gap, though closing faster than most benchmarks (~30% relative improvement in a year).
- **The "jagged frontier" framing** (Stanford HAI's AI Index, referencing Ethan Mollick's term) is itself a good research starting point — the point isn't one benchmark, it's that capability is highly uneven: a model can medal at the International Mathematical Olympiad and still fail at reliably telling time from a clock, or fail ~1 in 3 structured enterprise agentic tasks in production.
- **Epoch AI's benchmarking hub** (epoch.ai/benchmarks) is the best single current tracker across multiple hard benchmarks with methodology notes, if you want one source instead of many leaderboard-aggregator sites.

For this project specifically, ARC-AGI-2/3 and the "jagged frontier" framing are the more relevant categories to mine — they're about reasoning/generalization failures, closer to what an epistemic control layer could plausibly help with, whereas FrontierMath/HLE are closer to raw knowledge/computation ceilings that a verification layer doesn't obviously address.
