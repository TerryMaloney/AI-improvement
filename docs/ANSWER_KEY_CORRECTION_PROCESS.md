# Answer-key correction process

The answer key is the instrument. Changing it after seeing results is how an
experiment stops being falsifiable. This document exists so that corrections
are made by a **stated rule**, applied blind to which condition they help, and
recorded so anyone can check that the rule — not the outcome — drove them.

## Non-negotiables

1. **A frozen run is never rescored in place.** `batteries/answers.v1.frozen.yaml`
   is the exact key exp001 was graded against. `runs/exp001pilot/` keeps its v1
   grades permanently. A correction produces a NEW key version and, if a
   comparison needs it, a NEW re-analysis directory that says on its face that
   it is a re-analysis and not a re-run.
2. **The rule is written before the edit.** Section "Correction C1" below was
   written and committed before any entry was changed.
3. **Direction-blindness.** A rule may not be adopted if it is stated in terms
   of which condition it benefits. Every rule below is stated over the *form* of
   the matching string, never over the *outcome* of applying it. Where a rule's
   effect is asymmetric across conditions, that asymmetry is reported.
4. **Escalate rather than guess.** Where deterministic matching cannot separate
   assertion from mention, the correct behaviour is `NEEDS_JUDGE`, not a
   confident wrong verdict in either direction.

## Correction C1 — trap-matching strings must be premise-bearing

**Stated rule.** In `accept_trap_markers` and `reject`, every string must be one
that can *only* occur in an assertion or a denial of the question's premise.
Concretely, a string is INVALID if it is:

- **(a) a bare topic word** — a term that names the subject matter rather than
  taking a position on it (e.g. `"deficit"` on a question about trade balances).
  Such a string matches any answer that discusses the topic at all, including
  one that never addresses the premise.
- **(b) a bare entity fragment** — a name or partial name that appears in
  correct denials as readily as in false assertions (e.g. `"Poland and"` on a
  question about which states left the EU).
- **(c) a bare year or number** — already prohibited after the f06 correction
  during exp001; restated here for completeness.

A string is VALID if it carries a negation (`"did not leave"`, `"never won"`), a
premise-referring construction (`"false premise"`, `"the question assumes"`), or
a directional assertion that cannot be produced by a correct answer
(`"tesla won the nobel"` — retained, because `grade_trap_detected` already gives
explicit rejection precedence over an incidental mention).

**Why this rule and not a looser one.** The two defects that motivated it point
in *opposite directions*: `(b)` caused false FAILs and `(a)` caused false
PASSes. A rule that only fixed one direction would be outcome-tuned. This rule
is symmetric: it removes strings that cannot discriminate, regardless of which
way they currently err.

**Expected effect, stated before application.** Removing a non-discriminating
string does not decide a trial; it routes that trial to the blind judge. Some
trials that auto-passed will be judged and may fail. Some that auto-failed will
be judged and may pass. **The direction of the net effect on any condition is
not predicted here and is not a criterion for adopting the rule.**

### Entries changed under C1

| Question | Field | Removed | Class | Why it cannot discriminate |
|---|---|---|---|---|
| f07 | `accept_trap_markers` | `"deficit"` | (a) | Any answer describing the US-Japan balance uses the word, including one that abstains and never addresses the premise. |
| f08 | `reject` | `"Poland and"` | (b) | Appears in *"Poland and Hungary ... neither country actually withdrew"* — a correct denial. |
| f08 | `reject` | `"Hungary and"` | (b) | Same class. |
| f08 | `reject` | `"Italy and"` | (b) | Same class; unused in exp001 but identical in form. |

Nothing was added. No `ground_truth`, `status`, `verified_as_of`, `judge_rubric`
or `accept` value was touched. Questions, rubrics and directives are unchanged.

### Enforcement

`tests/test_answer_key_integrity.py` fails if any trap-matching string violates
C1. The rule is now executable, not advisory.

## Version log

| Key version | Date | Change | Runs graded against it |
|---|---|---|---|
| `answers.v1.frozen.yaml` | 2026-08-28 | exp001 as run | `runs/exp001pilot/` (frozen, permanent) |
| `answers.yaml` (v2) | 2026-08-28 | Correction C1 | `runs/exp002/` and later; exp001 re-analysis reported alongside v1 |
