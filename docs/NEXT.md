# Next Action

> This is the short cross-chat handoff file. Update it at the end of every substantial research action.

## Current state

Stage 0A-M candidate battery has now been fully source-verified at commit `a262b89`.

Reported state:
- 25 date-anchored primary items;
- 25 definition-anchored primary items;
- 15 arithmetic negative controls;
- 65 total items / 130 eventual production dispatches;
- 50/50 primary keys source-verified;
- 65/65 production-eligible;
- 1281 non-dispatch tests passed;
- 0 production solver/model dispatches;
- no production run directory;
- battery fingerprint `afc208e1e8d1bd00`.

Verification forced legitimate pre-treatment changes:
- b09 and b25 replaced;
- b11 key corrected;
- b18 reject refined;
- pass-1 provenance metadata repaired.

Because the battery changed during verification, a fresh bounded audit is required before final freeze/execution authorization.

## Next authorized action — post-verification battery / retrieval-environment audit

No production solver dispatches.

### 1. Re-audit the changed items

Independently inspect:
- b09 replacement: euro-area membership scope;
- b25 replacement: contiguous Pacific-coast state count;
- b11 corrected Lake Michigan item/key/tolerance;
- b18 refined reject;
- provenance/fingerprint consistency after the verification pass.

For each confirm:
- it still satisfies exactly one frozen class;
- the answer is deterministic under the stem;
- the principal alternative/reject is genuinely outside the accepted answer region;
- no answer leakage was introduced;
- no source-verification change weakened the intended displacement mechanism;
- manifest, answer-key, provenance and grading fingerprints agree.

### 2. Resolve b11 explicitly

Current stem:
> What is the surface area of Lake Michigan alone, excluding Lake Huron, in square kilometres?

Verification found multiple defensible published figures (including NOAA 57,573 and other commonly published figures around 58,000), and the key currently uses a ±1,500 km² tolerance.

This may conflict with the frozen definition-anchored principle that ambiguity should be eliminated in the question rather than absorbed by a broad grading tolerance.

Choose one pre-treatment resolution:
- source-anchor the stem (for example, to NOAA) and tighten the grading rule appropriately;
- replace the item with a cleaner scope-contrast item;
- or provide a rigorous reason the present acceptance-region formulation still gives an objective binary endpoint and remains consistent with the frozen specification.

Do not preserve the current form merely to keep the fingerprint unchanged.

### 3. Re-audit b09 and b25 class identity

b09 contains both a date and a scope restriction. Confirm its primary mechanism/classification is definition/scope displacement (20 euro adopters vs 27 EU members), not a date-anchored item that would violate the one-class-per-item design.

b25 should cleanly test contiguous geographic scope (3 vs 5 including Alaska/Hawaii).

If classification is ambiguous, repair before production exposure.

### 4. Retrieval environment must become part of treatment provenance

During key verification, web search worked while direct fetches to at least `en.wikipedia.org` and `www.bls.gov` were refused by the network egress proxy.

Do not treat this merely as an after-the-fact caveat.

The treatment is the actual **retrieval-enabled procedure available in the production environment**.

Before final freeze, define and record the retrieval surface:
- exact tool(s) available to the solver;
- search capability;
- fetch/source-access capability if exposed;
- query/tool-call policy;
- search/fetch failure semantics;
- environment/model/tool versions where available.

### 5. Run a fixed non-production egress probe if it can be done without production-item exposure

This turn explicitly authorizes a **screen-class / diagnostic-only egress probe** provided it does NOT expose any production item and does NOT count as a `solver_experiment` dispatch.

Probe a fixed, treatment-blind representative set covering at minimum:
- one clearly reachable general web domain;
- BLS or another known refused authoritative domain;
- Wikipedia or another known refused domain;
- at least two authoritative domains heavily represented in the battery, chosen independently of production outcomes.

Where the actual production tool stack supports both search and fetch, test both separately.

Record:
- domain;
- operation (search/fetch);
- success/failure;
- failure class;
- timestamp;
- environment/tool identity.

Do not tune the domain set based on what succeeds.

If the probe would require a genuine solver/model production call, STOP and leave it for the final execution turn instead.

### 6. Interpretation of degraded retrieval

Do not automatically invalidate Stage 0A-M merely because some domains cannot be fetched.

Instead determine exactly what a positive result would mean under the observed retrieval surface.

Candidate scope:
> the retrieval-enabled procedure available in this recorded environment lowers correctness probability for at least one frozen authored item.

Explicitly separate that from:
> ideal unrestricted web retrieval intrinsically harms the item.

Stage 0B replication/fixed-query work remains the place to distinguish query/tool/environment mechanisms.

If the environment is so degraded that retrieval is functionally unavailable on most/all trials, that may be a preflight failure rather than an interpretable treatment. Define an objective rule before outcomes if needed.

### 7. Do not create a post-outcome reachability filter

Per-item source/domain reachability may be logged after execution, but it must not determine inclusion/exclusion based on observed answer direction.

Do not say:
- keep items whose sources were reachable;
- drop items whose sites were blocked;

unless such a rule is formally justified and frozen before outcomes. The current preference is ITT: the available retrieval procedure, including its environment limitations, is the treatment.

### 8. Re-run complete consistency audit

After any b11 or other pre-treatment correction verify:
- exactly 25 + 25 + 15 items;
- all 50 primary keys source-verified;
- all 65 items production-eligible;
- all grading tests green;
- wrong-state/alternative-definition rejects remain outside acceptance regions;
- no duplicate IDs/stems;
- class/diversity limits remain satisfied;
- schedule IDs/classes still match;
- randomization seeds are preserved or transparently regenerated if required;
- packet hashes/diffs are updated consistently;
- report skeleton remains frozen;
- treatment exposure remains zero;
- no production run directory exists.

### 9. Recompute all fingerprints affected by changes

If b11 or anything else changes, regenerate the battery/key/manifest hashes as required.

Never retain a stale fingerprint after a legitimate pre-treatment repair.

### 10. Final preflight inventory

List exactly what would remain for the execution turn after this audit:
- commit SHA/freeze fingerprint;
- model snapshot/version;
- environment fingerprint;
- egress/retrieval-surface result;
- telemetry dry run if still pending;
- fresh-context verification;
- run-directory initialization;
- any other execution-only checks.

Do not dispatch production items in this turn.

## Hard stop

Still prohibited:
- production Stage 0A-M solver/model dispatches;
- closed/retrieval trial on any production item;
- production-item search scout;
- outcome-based item changes;
- runtime re-keying;
- Stage 0A-N or Stage 0B execution.

## Final gate

Return exactly one:

A. POST-VERIFICATION AUDIT CLEAN — READY FOR FINAL FREEZE / EXECUTION TURN
B. CLEAN AFTER SPECIFIC PRE-TREATMENT REPAIRS — READY FOR FINAL FREEZE / EXECUTION TURN
C. BATTERY STILL HAS OBJECTIVITY / CLASSIFICATION DEFECTS
D. RETRIEVAL ENVIRONMENT IS TOO DEGRADED TO DELIVER THE FROZEN TREATMENT
E. NEW LOAD-BEARING DESIGN FLAW FOUND

Report:

COMMIT:
TESTS:
PRODUCTION DISPATCHES: 0
DIAGNOSTIC/SCREEN CALLS:

RESULT:

CHANGED-ITEM AUDIT:
B11 RESOLUTION:
B09 CLASSIFICATION:
B25 CLASSIFICATION:
BATTERY FINGERPRINT:
KEY / MANIFEST CONSISTENCY:
RETRIEVAL TOOL SURFACE:
EGRESS PROBE:
POSITIVE-RESULT SCOPE:
PREFLIGHT REMAINING:
TREATMENT-EXPOSURE AUDIT:
OPEN:
DO NOT:

If a future stage requires Terry to manually install, authorize, connect, or physically configure anything, begin with the mandatory manual-setup alert defined in `docs/EXTERNAL_COGNITIVE_TOOLS_AND_TOPOLOGY_2026-08-29.md`.
