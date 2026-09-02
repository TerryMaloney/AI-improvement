# Zero-dispatch tests of P1, P7 and M2 — 2026-09-02

No solver or model dispatch. SQLite, packets, git history and tests only.

## P1 — judge-route × treatment interaction: NOT TESTABLE WITH EXISTING DATA

Cohort definition written before querying: *unique solver responses graded under
both a deterministic route and the judge route.* `runs/exp002/results.db` holds
75 trials with exactly one grade each; methods are `contains_any`,
`trap_detected`, `numeric` (42 trials) or `judge_k3_median` (33 trials).
Overlap of the deterministic-graded set with the judge-packet set and the
`grades_multi` set: **0**. `runs/exp001/results.db` holds 120 trials and 0
grades (its v1 grades live in `exp001pilot`). No item was ever graded by both
routes, so the interaction cannot be formed. Comparability was not
manufactured.

## P7 — narrative outruns ledger at handoff boundaries: NOT TESTABLE (mechanically)

Definitions fixed before counting: *completion claim* = a line in STATUS.md or
NEXT.md at any historical commit matching a completion verb, not negated, and
naming a repository path; *supporting artifact* = that path exists at that
commit (`git cat-file -e`); *handoff commit* = subject matching
`docs: set|next action|handoff|status|pre-freeze action|next gate`. Result over
25 commits touching those files: **2 claim-lines naming a path, both
supported, neither at a handoff commit.** The coordination documents rarely
name artifacts in completion sentences, so the mechanical definition has no
power. The two known unsupported-claim episodes (27 dispatches reported as 80;
"R=20 complete") lived in session prose and reports, not in STATUS/NEXT, and
were construction evidence for R2′ in any case. Boundary timing for session
compaction is not reconstructable from git. **Non-discriminating between R2′
and generic memory/compaction error.** Raw output:
`experiments/meta_r1r2/p7_handoff_audit_raw.txt`.

## M2 — see `CAUSAL_INTROSPECTION_M2.md`

Downgraded and partly reversed: the premise "no budget line in verified_flat"
was false. The data no longer disfavour ceiling-anchored reporting.

## Synthesis — did R1′/R2′ predict anything already testable that came out right?

| prediction | result | note |
|---|---|---|
| P1 | NOT TESTABLE | no dual-route cohort exists |
| P7 | NOT TESTABLE / NON-DISCRIMINATING | mechanical definition has no power |
| M2 as previously stated | **COUNTEREVIDENCE to the memo's claim** (not to R1′/R2′) | the memo's own factual premise failed — which is itself a G7 instance, but retrospective, so it does not count as confirmation |
| P6 (grader golden corpus) | corpus built; **current grader passed all cases unchanged** | this is a safeguard, not a test of the theory |

**Verdict: R1′/R2′ are UNCHANGED — no prospective confirmation and no
prospective disconfirmation exists yet.** The only prospective test now on
record is `experiments/meta_r1r2/prospective_component_table.yaml`
(fingerprint in `FINGERPRINT.txt`), which will be scored at the next
independent audit. Nothing in this pass may be counted toward it.
