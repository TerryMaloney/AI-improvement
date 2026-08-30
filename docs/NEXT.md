# Next Action

> This is the short cross-chat handoff file. Update it at the end of every substantial research action.

## Current state

Stage 0A-M candidate battery is authored at commit `4c7725f`.

Reported state:
- 65 items total: 25 date-anchored + 25 definition-anchored + 15 arithmetic control;
- 1279 non-dispatch tests passed;
- 0 solver/model dispatches;
- schedule, arm packets, quarantined keys, provenance, grading tests, preflight checklist and report skeleton exist;
- no production run directory exists;
- no production item has been shown to the target solver.

**Execution is still blocked.**

The only current blocking remediation is independent public-source verification of **32 of the 50 primary keys**.

18/50 primary keys are already verified. The remaining 32 are marked `PENDING_INDEPENDENT_VERIFICATION` / `production_eligible: false` and must stay that way until direct source inspection supports them.

## Next authorized action — source verification only

Verify every pending primary item using authoritative public source material.

This is KEY-CONSTRUCTION EVIDENCE, not EXPERIMENTAL RETRIEVAL EVIDENCE.

### Required verification for each pending item

Check directly from source material:

1. **Canonical answer**
   - Does the source actually support the frozen answer?

2. **Anchor / scope / definition**
   - Date-anchored: does the source support the answer specifically at the requested date/state?
   - Definition-anchored: does the source support the exact requested definition, scope, unit, period and convention?

3. **Objective gradability**
   - Is there a unique production key under the stem as written?
   - Are aliases/tolerances correct and disjoint from the principal wrong answer?

4. **Mechanism metadata**
   - Where the item records a newer state or alternative definition/value, confirm that it is genuinely distinct if practical from authoritative authoring evidence.
   - This is construct metadata only; never select the item based on target-model behavior.

5. **Provenance**
   Record enough for audit:
   - authoritative source/provider;
   - URL or stable source identifier;
   - access date;
   - relevant table/page/section/date where available;
   - short paraphrased evidence note;
   - verification status.

Do not store long copyrighted passages.

### Source hierarchy

Prefer, in order where applicable:
- primary official/statistical/government/intergovernmental source;
- first-party corporate filing/report for company figures;
- governing sports/scientific body for official records/definitions;
- other authoritative reference only when a primary source is unavailable.

Do not mark a key verified merely because multiple secondary websites repeat it.

### If verification disagrees with the authored battery

This is still pre-treatment, so correction is permitted.

If direct source evidence shows a pending item is wrong or ambiguous:
- keep an audit note of the original authored version;
- correct the key/stem/accepted representation if the class mechanism remains intact;
- replace the item if necessary using the same treatment-blind authoring rules;
- re-run all grading/diversity/schedule/manifest tests affected by the change;
- update fingerprints/hashes/schedule only as required by the actual changed artifacts.

Do not preserve an incorrect remembered answer for the sake of keeping the battery unchanged.

Do not use any solver/model answer to resolve the disagreement.

### Verification must not become a scout

Forbidden:
- asking the target solver to answer an item;
- answering with and without search to see whether it reverses;
- asking another frontier model whether the item is likely to fool the target;
- dropping/replacing an item because it appears too easy/hard for a model;
- inspecting future experimental retrieval results.

Direct source lookup for factual key construction is authorized.

## After all pending keys are resolved

Required state before gate A:
- 50/50 primary keys independently source-verified;
- 15/15 arithmetic controls deterministically verified;
- every production item `production_eligible: true`;
- no unresolved ambiguity flags;
- battery/answers/provenance fingerprints updated consistently;
- schedule and packet integrity tests green;
- treatment-exposure audit still zero;
- full non-dispatch suite green;
- no run directory and no production dispatch.

Then commit/push the verified candidate freeze package and STOP for final execution review.

## Still not authorized

- no Stage 0A-M production dispatch;
- no egress/production probe if it would create a solver dispatch unless separately allowed by the existing preflight protocol;
- no Stage 0A-N;
- no Stage 0B;
- no controller work.

## Final gate

Return exactly one:

A. ALL PRIMARY KEYS VERIFIED — READY FOR FINAL FREEZE/EXECUTION REVIEW
B. VERIFICATION INCOMPLETE — SPECIFIC KEYS REMAIN BLOCKED
C. VERIFICATION FORCED NONTRIVIAL BATTERY REPAIRS — REAUDIT REQUIRED
D. SOURCE EVIDENCE EXPOSED A LOAD-BEARING DESIGN PROBLEM

Regardless of gate: **DISPATCHES: 0**.

Return:

COMMIT:
TESTS:
DISPATCHES: 0

RESULT:
VERIFIED PRIMARY KEYS:
REPAIRED / REPLACED ITEMS:
UNRESOLVED ITEMS:
PROVENANCE AUDIT:
GRADING AUDIT:
BATTERY FINGERPRINT:
TREATMENT-EXPOSURE AUDIT:
PREFLIGHT STATUS:
OPEN:
DO NOT:

If a future stage requires Terry to manually install, authorize, connect, or physically configure anything, begin with the mandatory manual-setup alert defined in `docs/EXTERNAL_COGNITIVE_TOOLS_AND_TOPOLOGY_2026-08-29.md`.
