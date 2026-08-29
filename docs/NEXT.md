# Next Action

> This is the short cross-chat handoff file. Update it at the end of every substantial research action.

## Next authorized research action

Resolve the **Stage 0A grading architecture**. No solver dispatches and no Stage 0A item authoring yet.

The design red-team found that the main harm-plausible classes are not cleanly deterministic under the current grading system. The next task is to compare, mathematically and operationally, the three candidate remediation paths:

1. deterministic acceptance criteria with pre-dispatch coverage validation;
2. judged-primary analysis with a pre-registered measurement-bias audit;
3. deterministic-only class restriction.

### Required questions

- Can free-text false-premise / stale-state answers be converted into objective relational checks rather than brittle lexical markers?
- Can deterministic grading be validated on authored paraphrase/adversarial answer sets without leaking treatment outcomes?
- If judge-based grading is used, what estimand is actually measured?
- Can judge bias be bounded strongly enough before production to support a directional harm claim?
- Is the measured exp003c length effect transferable enough to justify calling judged-primary conservative, or is that an unsupported extrapolation?
- Can multiple independent judges, pairwise ranking, blinded arm labels, response normalization, or structured response formats reduce measurement bias?
- Would forcing the solver into a categorical/structured answer format eliminate the need for free-text judging while preserving the harm mechanism?
- Does changing response format itself change the intervention being studied?
- Which classes should be dropped/redefined, especially contested-quantity?
- What is the simplest grading design that keeps the scientific question meaningful?

### Stale test

Separately assess the proposed replacement for the stale knowledge-probe test:
- preserve frozen evidence;
- restore suite signal;
- assert the actual invariant that screen-class probe data never enters solver-experiment manifests.

Do not change it unless the grading investigation concludes the replacement is clearly infrastructure-only and authorized.

## Hard stop

Do not:
- freeze Stage 0A;
- author production items;
- run production solver calls;
- permit runtime judge escalation;
- pool deterministic and judged outcomes without a frozen measurement model.

## Final gate for next turn

Return one:
A. OBJECTIVE GRADING PATH FOUND
B. JUDGED-PRIMARY PATH DEFENSIBLE WITH SPECIFIC CALIBRATION
C. ONLY DETERMINISTIC-CLASS DESIGN IS DEFENSIBLE
D. STAGE 0A QUESTION MUST BE REFORMULATED
E. NO CURRENTLY DEFENSIBLE GRADING PATH

If a future stage requires Terry to manually install, authorize, connect, or physically configure anything, begin with the mandatory manual-setup alert defined in `docs/EXTERNAL_COGNITIVE_TOOLS_AND_TOPOLOGY_2026-08-29.md`.
