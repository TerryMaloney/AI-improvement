# Tool-environment equivalence check (2026-08-28)

Run before exp002's new condition, to establish that the retrieval environment
is the same across conditions AND the same as it was during exp001. A changed
proxy allowlist between runs would confound `verified_flat` against exp001's
`search_only` just as thoroughly as a changed prompt.

## Method

Two independent `solver-web` probes, identical prompts, run in parallel. Each
was told to list its actual tool inventory, run one WebSearch, and attempt a
WebFetch on five domains that exp001 recorded as blocked — reporting the literal
outcome for each rather than reasoning about what it expected.

## Result: byte-identical across both probes

| Check | Probe A | Probe B |
|---|---|---|
| Tools available | `WebSearch`, `WebFetch` | `WebSearch`, `WebFetch` |
| WebSearch | succeeded, ~9 results | succeeded, ~9 results |
| Observed tool calls | 6 | 6 |
| census.gov | `EGRESS_BLOCKED` | `EGRESS_BLOCKED` |
| en.wikipedia.org | `EGRESS_BLOCKED` | `EGRESS_BLOCKED` |
| worldometers.info | `EGRESS_BLOCKED` | `EGRESS_BLOCKED` |
| federalreserve.gov | `EGRESS_BLOCKED` | `EGRESS_BLOCKED` |
| nato.int | `EGRESS_BLOCKED` | `EGRESS_BLOCKED` |

Error text was identical in every case:
`EGRESS_BLOCKED: Access to <host> is blocked by the network egress proxy.`

## What this establishes

1. **Tool inventory is identical** across `solver-web` invocations, and matches
   the declaration. All three search-enabled conditions (`search_only`,
   `verified`, `verified_flat`) use this same agent, so tool availability is
   equivalent by construction and confirmed empirically.
2. **The retrieval environment has not changed since exp001.** Every domain
   exp001 recorded as blocked is still blocked, with the same error. So
   `verified_flat` faces the same retrieval ceiling exp001's conditions faced,
   and the comparison is not confounded by an allowlist change.
3. **The environment is deterministic**, not flaky: two independent probes
   produced identical outcomes on all seven checks.

## What this does NOT establish, and it matters

**`WebFetch` is effectively unusable in this environment.** Every primary source
tried — the US Census, the Federal Reserve, NATO, Wikipedia, Worldometers — is
blocked. Search-enabled conditions can reach **search-result snippets and
nothing else**.

This is a hard ceiling on the entire search arm, and it bears directly on the
question exp002 is asking. The epistemic directive instructs the model to judge
source independence by content and to resolve conflicts with one more cheap
retrieval. Neither move is fully available when the only reachable evidence is
snippets from an aggregator layer. **The directive is being tested in an
environment that cannot support part of what it asks for**, and any conclusion
about the directive has to carry that caveat.

It also plausibly contributes to exp001's f15 result, where both search
conditions converged on an excess-mortality figure contradicting the WHO
estimate: the primary source that would have settled it was unreachable.

## Reproducing

Re-run both probes before any experiment that compares against exp001 or
exp002. If the blocked set changes, cross-run comparisons involving search
conditions are no longer valid and must be re-baselined.
