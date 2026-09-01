# Stage 0A-M cost ledger — Fable 5.1 session

Hard budget: **$40.00 USD** for this task, orchestrator and dispatches included.
Pricing (Fable 5.1): input $10/M · output $50/M · cache write ≈$12.50/M · cache read $0.25/M.
Telemetry source: `get_session` → `external_metadata.usage.cost_usd` (session-lifetime; deltas below).

| checkpoint | cache_read | cache_write | input | output | cost_usd (lifetime) | Δ this task |
|---|---:|---:|---:|---:|---:|---:|
| baseline, ~5 turns into this task (2026-09-01T23:29Z) | 51,263,855 | 1,239,723 | 542,436 | 290,477 | 336.73 | ≈0.60 est. pre-baseline |
| after validation attempt + freeze bookkeeping | see closing line in the final report | | | | | |

## Production projection (no canary measurement available in this session)

The only in-session Fable-era dispatch datum is the 2026-08-30 egress probe: **7,560 subagent tokens** for 7 tool calls, 5 of them fast refusals.

| component | conservative per-trial | × | subtotal |
|---|---:|---:|---:|
| closed trial (≈5K in incl. subagent base prompt, ≈2K thinking+output) | $0.15 | 65 | $9.75 |
| retrieval trial (≈10K in incl. 1–3 searches, ≈4K thinking+output) | $0.40 | 65 | $26.00 |
| orchestration overhead **at this session's ~200K context** (cache read + output per dispatch) | $0.10 | 130 | $13.00 |
| orchestration overhead **from a fresh session** (<20K context) | $0.02 | 130 | $2.60 |

- From **this** session: ≈ **$49** → does not fit $40.
- From a **fresh** session: ≈ **$38** conservative, ≈ $24 optimistic → marginal against $40 with the ~$5 safety margin, and cannot be decided until the two synthetic canaries give a measured per-trial cost.

**Budget-start rule as it stands:** do not begin production until the canaries in a fresh session yield a measured per-trial cost and 130 × that cost + overhead + $5 ≤ remaining budget.
