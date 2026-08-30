# Next Action

> This is the short cross-chat handoff file. Update it at the end of every substantial research action.

## Current state

Stage 0A-M has passed the successive design audits far enough to begin **production item authoring**.

Latest load-bearing audit commit: `3015ea6`.

Authoring is now authorized. **Solver/model dispatch is still not authorized.**

## Next authorized research action

Create the complete candidate Stage 0A-M production battery and prefreeze package without exposing any production item to the retrieval treatment.

### Required battery

Primary classes:
- 25 date-anchored / time-indexed items;
- 25 definition-anchored / definition-fixed quantity items.

Negative control:
- 15 arithmetic / deterministic items.

Total: 65 items.

### Authoring rules

1. Follow `docs/EXP004_STAGE0A_M_SPECIFICATION.md` exactly.
2. One primary class per item; no overlap.
3. No production item may be selected, rewritten, dropped, or reclassified based on any model/search-arm outcome.
4. Do not run the experiment, a pilot, a scout, or a retrieval dry-run on these items.
5. Public authoritative sources may be used to create/verify keys only as **KEY-CONSTRUCTION EVIDENCE**.
6. Store key-construction provenance separately from future **EXPERIMENTAL RETRIEVAL EVIDENCE**.
7. Every key must be objective before freeze; no runtime judge route and no runtime re-keying.
8. Independently verify class membership, stem interpretation, date/definition/scope, accepted-answer representation, and provenance.
9. For date-anchored items, the target date/state must be explicit and stable enough to support an objective key.
10. For definition-anchored items, definition/scope/unit/date/convention must be explicit enough that incompatible quantities are wrong by construction rather than merely debatable.
11. Arithmetic controls must be exact, deterministic, and unrelated enough to the anchored mechanisms to function as a diagnostic negative control.

### Stress-sample discipline

The battery may deliberately enrich for plausible displacement mechanisms using treatment-blind properties and public key-construction evidence.

That enrichment must be documented. It does not license prevalence or semantic-class generalization.

Do not use observed model behavior to improve “purity.” True harm-purity remains latent and is only a power-sensitivity parameter.

### Create/freeze-support artifacts

Create the candidate production artifacts required by the specification, including as applicable:
- item manifest;
- objective keys / accepted-answer representation;
- class assignments and subtype covariates;
- key-construction provenance;
- independent verification record;
- arm templates/wrapper hashes or preflight-ready packet artifacts;
- randomized item-order seed and resulting schedule;
- independent within-item arm-order seed/rules;
- report skeleton;
- statistical/preflight metadata needed for the later freeze.

The final production freeze commit must still occur only after the authored battery passes the audit below.

### Required prefreeze audit

Before declaring the battery ready:

- verify exactly 25 + 25 + 15 items;
- verify no duplicate or near-duplicate mechanism templates that collapse effective diversity;
- verify one-class-per-item;
- verify objective deterministic grading for every item;
- verify key-construction provenance exists for every non-arithmetic item;
- verify no experimental retrieval evidence exists;
- independently re-check all date anchors and definition anchors;
- run ambiguity/adversarial checks on stems and accepted-answer rules without using solver-treatment outputs;
- verify closed/retrieval-enabled packet differences are limited to the frozen retrieval permission;
- verify dispatch schedule interleaves primary classes and randomizes arm order;
- verify fresh-context requirement is enforceable;
- run full non-dispatch tests.

### Hard stop

Do **not**:
- dispatch any solver/model call on production items;
- run retrieval/search as an experimental arm on production items;
- inspect how the target model answers the production items;
- replace hard items based on predicted/observed solver difficulty from model outcomes;
- alter a key after treatment outcomes exist;
- begin Stage 0A-N, Stage 0B, or controller work.

Key-construction web/source research is permitted; experimental treatment exposure is not.

## Final gate for this authoring turn

Return exactly one:

A. BATTERY AUTHORED AND PREFREEZE AUDIT CLEAN — READY FOR FINAL FREEZE/EXECUTION REVIEW
B. BATTERY AUTHORED BUT SPECIFIC NON-DISPATCH REMEDIATIONS REQUIRED
C. DATE-ANCHORED CLASS COULD NOT SUPPLY 25 OBJECTIVE ITEMS
D. DEFINITION-ANCHORED CLASS COULD NOT SUPPLY 25 OBJECTIVE ITEMS
E. NEGATIVE CONTROL DESIGN FAILED AUTHORING
F. AUTHORING EXPOSED A NEW LOAD-BEARING DESIGN FLAW

Regardless of gate: **DISPATCHES must remain 0.**

Return:

COMMIT:
TESTS:
DISPATCHES: 0

RESULT:

BATTERY COUNTS:

DATE-ANCHORED SUMMARY:

DEFINITION-ANCHORED SUMMARY:

NEGATIVE CONTROL SUMMARY:

KEY/PROVENANCE AUDIT:

DIVERSITY / DUPLICATION AUDIT:

AMBIGUITY AUDIT:

SCHEDULE / RANDOMIZATION:

PREFLIGHT STATUS:

CHANGED:

OPEN:

DO NOT:

If a future stage requires Terry to manually install, authorize, connect, or physically configure anything, begin with the mandatory manual-setup alert defined in `docs/EXTERNAL_COGNITIVE_TOOLS_AND_TOPOLOGY_2026-08-29.md`.
