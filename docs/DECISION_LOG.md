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
