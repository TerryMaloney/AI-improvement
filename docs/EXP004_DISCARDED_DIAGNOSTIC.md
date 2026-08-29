# exp004 — discarded replicate-independence diagnostic

**Status: DISCARDED / NON-REUSABLE FOR INFERENCE**

## What happened

During exp004 Stage-0 design, a replicate-independence diagnostic was
pre-registered (4 items x R=20, baseline arm only, `dispatch_class: screen`)
and partially executed. **27 screen-class solver calls occurred.** The design
called for 80. The shortfall was mis-stated as complete in the working session
before being caught and corrected.

## Disposition

The 27 calls are recorded here as an event. **None of their answer-level
observations are preserved, and none may be used** in:

- the prevalence pilot,
- any production analysis,
- any formal statistical evidence.

**Reason for discard: incomplete persisted provenance.** The observations were
never written to a run directory at dispatch time. Reconstructing them after the
fact from session prose would produce data with no verifiable chain of custody —
the precise failure mode this lab exists to prevent. Numbers that cannot be
audited back to their dispatch are not measurements.

This disposition is not a judgement about the answers themselves. It is a
judgement about their provenance.

## What the episode did establish (methodologically, not numerically)

Two design findings survive, because they rest on computation rather than on the
discarded observations:

1. **The diagnostic could not have worked.** Between-batch dispersion tests have
   approximately 6% power to detect an intraclass correlation of 0.02 at a
   60-dispatch budget, and about 23% at 1200 dispatches. The repeated-trial
   design being tested required ICC below roughly 0.01. No affordable
   measurement could certify that.

2. **Item selection for the diagnostic was poor.** Three of the four items were
   degenerate (every replicate produced the same graded outcome), which carries
   no information about dispersion. Intermediate-difficulty items are required
   and were not verified in advance.

Both findings motivated retiring the repeated-trial estimator entirely in favour
of a design that does not depend on an uncertifiable assumption.

## Rule going forward

Screen-class dispatches are written to a run directory **at dispatch time**, with
item id, prompt hash, dispatch order, timestamp and model snapshot, or they do
not count as evidence.
