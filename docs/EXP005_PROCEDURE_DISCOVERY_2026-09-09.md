# EXP005 — Procedure Discovery / Inference-Time Capability Lift

**Status:** DESIGN ONLY. No EXP005 outcome exists. No model dispatch has been run.

**Branch:** `openai/exp005-procedure-discovery`

## 1. North-star question

Can a **frozen general-purpose language model** be made measurably more capable by changing only its inference-time procedure — prompts, decomposition, independent sampling, verification, refinement, routing, tools or multi-agent structure — without changing model weights?

The target is not a clever prompt. The target is a procedure that improves the **system-level capability frontier** and survives:

1. a compute/cost-matched baseline;
2. held-out tasks;
3. at least two additional model families without redesigning the procedure;
4. later, task families with externally executable outcomes.

A procedure that beats one greedy answer only because it spends more inference does **not** count as making the model smarter.

## 2. Why this branch exists now

Stage 0A-M and Stage 0B exposed a repeated failure mode: a high-level procedure description can differ materially from the executed system. Hidden transformations, evaluator defects, tool-runtime mediation, correlated measurements and selection rules can create a convincing capability story without measuring the intended construct.

EXP005 uses those failures as design constraints rather than treating them as retrieval-specific history.

Permanent lessons imported into EXP005:

- configuration is not realized runtime;
- every load-bearing construct needs implementation + fingerprint + correspondence evidence;
- an evaluator can dominate the measured effect;
- selection and stopping rules must precede outcomes;
- more machinery can hurt;
- call count, token count and dollar cost are different notions of inference budget;
- positive findings remain local until transferred.

Stage 0B remains active and unchanged. EXP005 is a parallel program branch, not a replacement or reinterpretation of Stage 0B.

## 3. Prior-art position (2026-09-09)

The individual ingredients are established research areas, so novelty must not be claimed for them:

- self-consistency / best-of-N / test-time scaling;
- self-refinement;
- verifier-guided repair;
- multi-agent debate / mixture-of-agents;
- adaptive test-time compute;
- model routing and cascades.

Recent signals relevant to the design include:

- Wunderlich et al., ACL 2026, **Multi-Agent Reasoning Improves Compute Efficiency: Pareto-Optimal Test-Time Scaling** — compute-matched inference strategies can occupy different Pareto frontiers; mixture-of-agents and debate sometimes beat self-consistency at equal budget, but benefits depend on regime.
- Wan et al., ACL Findings 2026 / arXiv:2601.15808, **Inference-Time Scaling of Verification** — rubric-guided verification can improve difficult deep-research subsets, reinforcing the need to compare verification against simpler extra-compute baselines.
- Bilal et al., arXiv:2608.05643, **Refining Over Resampling** — refinement can outperform wider resampling on mathematical reasoning in some model regimes.
- Zhu et al., ACL Findings 2026, **Demystifying Multi-Agent Debate** — vanilla debate can fail to beat simple majority voting; diversity/confidence are plausible mechanisms.
- Becker et al., EACL Findings 2026, **Stay Focused: Problem Drift in Multi-Agent Debate** — extra interaction can introduce a distinct harm mechanism.

Therefore the defensible novelty target is not “verification/refinement/multi-agent helps.” A more useful target is:

> a model-agnostic experimental framework that discovers, cost-normalizes, routes and transfers inference-time procedures while refusing capability claims that fail simple-compute, held-out and cross-model controls.

That target remains a **hypothesis about useful methodology**, not an established novelty claim.

## 4. Capability Lift Curve

The core object is a **Capability Lift Curve (CLC)**:

`task success` as a function of `realized inference budget`.

Record at least three budget views separately:

- number of model invocations;
- billed/generated tokens where exposed;
- realized dollar cost and wall time where exposed.

Do not collapse them into one scalar unless a later analysis explicitly defines and justifies the conversion.

A procedure earns a capability-lift claim only if it moves the success frontier upward relative to a simple baseline at comparable budget.

### 4.1 Primary local estimand for EXP005A

For each candidate 3-call procedure `P`:

> paired correctness difference between `P` and **three independent direct solutions + deterministic majority** on the same tasks, with the same frozen model/configuration and the same per-call output cap.

This is a **call-matched** estimand. Because sequential procedures ingest previous outputs and therefore can consume more input tokens, EXP005A must not call it exact compute matching. Realized token/cost differences are reported and become a second efficiency axis.

A later confirmation stage must build a measured budget frontier if exact cost matching is needed.

## 5. EXP005A — cheap procedure-discovery experiment

### 5.1 Model scope

Use one frozen model/configuration for discovery. Model identity, served identity, reasoning/effort setting, temperature, output limit and system instructions are recorded per dispatch.

The model used to help design EXP005 may be used for **discovery**, but no generality claim follows. Transfer is a separate stage.

### 5.2 No tools in EXP005A

No web search, calculator, code execution, file access or external retrieval in the treatment arms.

Reason: EXP005A asks whether **cognitive procedure alone** adds useful capability beyond spending the same number of calls on independent direct attempts. Tool access becomes EXP005B after this construct is measured.

### 5.3 Task families

Start with deterministic, procedurally generated closed-world tasks so answer-key/evaluator uncertainty is minimized.

Provisional families:

1. **multi-step arithmetic state problems** — generated numeric parameters, exact numeric key;
2. **ordering / constraint logic** — generated finite constraints with unique multiple-choice or exact-order solution;
3. **algorithm/state-machine tracing** — generated transitions, exact final state/output;
4. **finite-world multi-hop inference** — generated facts + rules + query, exact truth/entity answer.

Every task generator must independently compute the key and reject invalid/non-unique instances before model exposure.

This battery tests reasoning procedures, not general world knowledge. Generality beyond reasoning is explicitly deferred.

### 5.4 Discovery bank

Provisional first bank: **48 held-out experimental items, 12 per family**, plus a separate development/calibration bank used to validate formatting, grading and procedure execution.

48 is a discovery budget, not a confirmatory-power claim. A procedure cannot be promoted from EXP005A on p-value alone. Promotion requires replication on a larger untouched bank.

No development item may enter the 48-item discovery bank.

### 5.5 Arms

#### A0 — single direct answer

One fresh-context direct solution. Measures the ordinary one-call floor.

#### B3 — simple-compute baseline

Three independent fresh-context direct solutions. Final answer is selected by a **deterministic majority rule** over the normalized exact answer.

For three distinct answers with no majority, use a precommitted deterministic tie rule (for example first sample) and report tie rate separately. Do not add an adjudicator call: that would change the budget.

This is the primary comparator for the 3-call procedures.

#### C3 — self-refine

1. direct solve;
2. critique in the same logical conversation/context lineage;
3. repair/final answer using the original answer + critique.

The final answer from call 3 is scored.

#### D3 — independent verifier + repair

1. direct solve;
2. **fresh-context verifier** receives only the task, candidate final answer and frozen verification rubric — not the solver's hidden reasoning history;
3. fresh repairer receives the task, candidate answer and verifier report, and emits the final answer.

The contrast C3 vs D3 tests whether independent verification provides information beyond self-critique. It is secondary in discovery.

### 5.6 Why multi-agent adjudication is not in the first four arms

Two independent solvers + an LLM adjudicator is valuable, but it introduces another evaluator-like model and a distinct aggregation construct. It becomes the first add-on if B3/C3/D3 do not dominate it in a small calibration pilot; it should not expand the first production family merely because it is fashionable.

## 6. Budget fairness

EXP005A makes two separate claims:

1. **call-matched:** B3, C3 and D3 each use exactly three model invocations;
2. **realized-efficiency:** report actual input/output tokens, dollar cost and wall time.

Do not state “same compute” merely because call count matches.

A procedure is not a useful capability multiplier if its accuracy gain disappears when compared with B3 or if its realized cost per additional correct item is dominated by B3.

### 6.1 Output-length control

Each call gets the same maximum generated-token budget unless the role intrinsically requires a smaller cap; any role-specific cap must be precommitted and included in the budget accounting.

Final-answer extraction is deterministic and identical across arms.

## 7. Hypotheses and rivals

| ID | hypothesis | principal rival / falsifier |
|---|---|---|
| H1 | C3 self-refinement beats B3 at similar call budget on at least one task family | extra calls help only by independent resampling; refinement adds no information |
| H2 | D3 verifier-repair beats C3 because fresh verification reduces correlated self-error | verifier shares solver blind spots or merely adds persuasive noise |
| H3 | no one procedure dominates all task families | a single method dominates, making routing unnecessary |
| H4 | procedure benefit depends on baseline difficulty/regime | apparent regime effects are noise/selection |
| H5 | at least one frozen procedure transfers positively to other model families | effect is model-specific prompt exploitation |
| H6 | later adaptive routing can capture most oracle procedure benefit at lower mean cost | routing overhead/errors erase oracle value |

Global rivals that must always be checked:

- output-length differences explain the score;
- evaluator/parser artifacts explain the score;
- candidate procedure merely spends more realized tokens/cost;
- gains concentrate in a handful of load-bearing tasks;
- one family improves while another is materially harmed;
- model/provider quirks drive the effect;
- sequential context causes conformity/error lock-in rather than correction.

## 8. Discovery promotion / kill rules

EXP005A is a **screen**, not confirmation.

A candidate procedure is eligible for confirmatory design only if all hold on the untouched discovery bank:

1. paired accuracy is at least **+8 percentage points** above B3 overall **or** a clearly predeclared task-family interaction justifies a narrower procedure claim;
2. repairs exceed harms relative to B3 rather than gain arising from grading/ties;
3. no task family shows >10 percentage-point harm without an explicitly narrowed claim;
4. realized dollar/token cost is reported and does not make the candidate strictly dominated by B3;
5. result is not dependent on fewer than four net changed items;
6. evaluator/parser audits are clean.

These thresholds are **discovery promotion rules**, not significance thresholds and not preregistration.

Kill / merge rules:

- if C3 and D3 are behaviorally and outcome-equivalent, merge the mechanism question before scaling;
- if neither beats B3, do not add more elaborate multi-agent machinery until a concrete rival mechanism says why it should;
- if B3 itself provides no meaningful gain over A0, characterize the model/task regime before spending on procedures;
- if deterministic task generation or grading is not correspondence-valid, stop before model dispatch.

## 9. Confirmation and transfer ladder

### EXP005A-D — discovery

One model, 48 untouched tasks, A0/B3/C3/D3.

### EXP005A-C — confirmation

New generator seeds / untouched items. Sample size derived from the observed repair/harm discordance but **effect size is shrunk prospectively** rather than copied at face value. Frozen winning procedure versus B3 only.

### EXP005A-T — cross-model transfer

Apply the confirmed procedure **unchanged** to at least two additional model families/configurations. No model-specific prompt edits before the primary transfer result.

Transfer claim requires positive paired lift on more than the discovery model and no catastrophic family-specific harm.

### EXP005B — tools

Selective tools versus always-on tools versus no tools, with tool execution itself correspondence-tested.

### EXP005C — routing

A cheap controller chooses A0/B3/champion procedure before outcome visibility. Compare with always-expensive and oracle retrospective routing.

### EXP005D — automatic procedure evolution

Model proposes prompt/control-logic mutations on development data. Champion changes only via untouched validation. Evaluator quality and lineage are part of the experiment.

### EXP005E — external execution

Coding/other tasks with success defined outside the judging model.

## 10. What would actually count as “made the model smarter”

The phrase is licensed only at the **system/procedure level**, not as a claim that the neural network's internal weights changed.

Strongest target statement:

> For a frozen base model, a frozen inference-time procedure achieves higher externally valid task success than a simple extra-compute baseline at comparable realized inference budget, and the procedure transfers without redesign across models and unseen task families.

Anything weaker should be named more narrowly: prompt improvement, local benchmark gain, verifier benefit, routing benefit, etc.

## 11. Execution blocker in the current ChatGPT environment

As of 2026-09-09 this chat can directly read/write the GitHub repository and perform local analytical computation, but it does **not** expose a general model-inference dispatch API for launching hundreds of isolated fresh-context trials.

Therefore EXP005 may proceed through:

- design;
- task-generator specification/code;
- deterministic grading;
- power/sensitivity work;
- causal-contract drafting;
- repository changes and review;

but a paid multi-dispatch model run requires a separately available inference execution surface. The absence of that surface is an environment-state fact, not evidence about EXP005 feasibility or model capability.
