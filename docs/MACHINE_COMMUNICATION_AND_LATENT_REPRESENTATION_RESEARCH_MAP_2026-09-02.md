# Machine Communication and Latent Representation Research Map — 2026-09-02

Status: program-level hypothesis branch. Not a preregistration. Does not alter Stage 0A-M, Stage 0B, or any frozen artifact.

## Why this branch exists

Natural language is a convenient interface for humans, but it is not obviously the optimal representation for communication among AI systems. A multi-agent procedure may waste substantial bandwidth converting internal state into readable prose, transmitting that prose, then reconstructing task state in another model. Conversely, removing human-readable communication may improve efficiency while making correlated errors, provenance loss, or hidden coordination harder to detect.

The research question is therefore not simply "can models communicate in Neuralese?"

> **As we progressively remove the requirement that collaborating AI systems communicate in ordinary human language, can we increase useful collaborative intelligence per unit compute without losing the independence, provenance, robustness, and error-correction properties required to trust the result?**

This branch treats communication representation as an experimentally selectable **procedure component**, not as an assumed architecture.

## Important terminology

### Symbolic machine interlingua
A protocol constructed from ordinary tokens but optimized for machines rather than readers. Example only:

`H3|p=.62|e17+e22|conflict:e8|test:q4`

This is still token communication. Closed models such as hosted frontier APIs can be tested here because no hidden activations need to be exposed.

### Continuous / latent reasoning
Reasoning performed using internal continuous representations rather than decoding every intermediate state into natural-language tokens.

### True latent inter-agent communication
One model transmits hidden-state or activation-space representations directly to another model or agent. This requires model-internal access and is therefore an open-weight / research-model experiment, not something a prompt can create in a closed API model.

Do not call symbolic shorthand "latent communication" merely because humans cannot immediately read it.

## Prior-art anchors and novelty discipline

This branch is deliberately framed as an experimental extension rather than a claim that latent reasoning or latent communication is new.

Relevant prior work includes:

- **Coconut — Training Large Language Models to Reason in a Continuous Latent Space** (Hao et al., 2024): continuous hidden-state reasoning rather than decoding every intermediate step into language.
- **CODI — Compressing Chain-of-Thought into Continuous Space via Self-Distillation** (Shen et al., 2025): continuous reasoning with substantial token compression while matching explicit CoT on reported tasks.
- **Interlat — Enabling Agents to Communicate Entirely in Latent Space** (Du et al., ACL 2026): direct hidden-state communication between agents; reported gains over comparison baselines and substantial inference acceleration under compression.
- **Latent Agents — A Post-Training Procedure for Internalized Multi-Agent Debate** (Yi et al., ACL 2026): internalizes multi-agent debate into latent agent-specific subspaces with large reported token savings.
- Reliability critiques of continuous reasoning also exist; therefore benchmark gains must not be treated as proof that a latent representation contains faithful or causally load-bearing reasoning.

The potentially interesting contribution here is not "latent communication exists." It is the **controlled reliability/efficiency/error-correction ladder**, especially the comparison between human-readable, agent-designed symbolic, and true latent communication under common external outcome criteria.

### Astra note

OpenAI has publicly stated that Astra is substantially more token-efficient than GPT-5.6 Sol on some evaluations and has described large capability gains. As of 2026-09-02 OpenAI has **not publicly established that Astra uses latent inter-agent communication or any specific Neuralese architecture**. Treat Astra as motivation to investigate efficiency, not as evidence for a mechanism.

## Dependency placement in the larger program

This branch must not interrupt current Stage 0B retrieval work.

Its components enter at different points:

1. **Protocol baselines and symbolic machine interlingua** enter after the laboratory is trustworthy and after there is a meaningful multi-agent/execution task with externally checkable outcomes. This naturally touches Phase F2/G8 and Phase D execution grounding.
2. **Agent-designed communication protocols** become a Phase G interaction experiment once ordinary multi-agent and provenance baselines exist.
3. **Automatic protocol discovery/evolution** belongs in Phase I automated procedure discovery.
4. **Recursive protocol mutation and promotion** belongs in Phase J recursive procedure improvement.
5. **True hidden-state/activation communication** is a later open-weight branch after symbolic baselines are established and model-internal instrumentation is available.
6. Any protocol that survives may later become an action available to the model-agnostic runtime; it is not assumed in advance.

## COMM-000 — Feasibility and measurement foundation

Before testing capability gains, define a communication ledger that records at minimum:

- sender identity;
- receiver identity;
- message/protocol version;
- exact payload or latent artifact identifier;
- token/byte/vector dimensional cost;
- wall time;
- task state before and after communication where observable;
- provenance / evidence references if the protocol supports them;
- confidence or uncertainty representation if the protocol supports it;
- final externally checked outcome.

For symbolic protocols, preserve every exchanged message verbatim.
For true latent protocols, preserve the activation extraction/injection specification, tensor shapes, layer positions, compression transform, seeds, model fingerprints, and hashes of persisted representations where technically possible.

Primary lesson from Stage 0 applies here: **the live communication surface is the treatment, not the configuration file describing it.**

## COMM-001 — Natural language vs human-designed structure vs agent-designed interlingua

### Scientific question

Can collaborating agents improve task-relevant information transfer per communication token by designing their own symbolic protocol rather than using ordinary prose?

### Candidate conditions

A. **Natural language** — agents communicate freely in ordinary language.

B. **Human-designed structured protocol** — a fixed claim/evidence/confidence/provenance schema.

C. **Agent-designed symbolic protocol** — agents are given a protocol-development phase and may invent any token-based representation subject to a communication budget.

Do not add conditions merely for symmetry. Use the smallest contrasts needed for the hypothesis.

### Candidate primary metric

> **Externally correct collaborative decisions per communication token**, under a matched total-compute or explicitly modelled cost regime.

Secondary metrics:

- final correctness / execution success;
- total input + output tokens;
- inter-agent communication tokens specifically;
- latency;
- monetary cost;
- number of revisions;
- disagreement resolution;
- provenance preservation;
- calibration;
- correlated-error rate;
- human auditability as a separately measured property, not an assumed virtue.

### Key confounds

- protocol-development examples leaking test structure;
- extra training/prompt budget granted only to the self-designed condition;
- one protocol receiving more effective context;
- evaluator preference for readable prose;
- compression merely deleting useful caveats while benchmark items remain forgiving;
- hidden model-specific familiarity with the imposed schema.

## COMM-002 — Protocol learning rather than one-shot shorthand

The stronger version of COMM-001 gives agents a dedicated protocol-learning phase.

Possible procedure:

1. Agents receive development tasks that can never appear in production.
2. They may propose communication protocol P0.
3. P0 is frozen and evaluated on held-out tasks.
4. Failures are characterized mechanically/executionally.
5. A later discovery stage may propose P1, but P1 must beat P0 on fresh validation before promotion.

Human interpretability is not an optimization objective unless the experiment explicitly includes it. However, external outcome quality, lineage/provenance, and robustness remain measured constraints.

This allows the program to distinguish:

- "the prompt told agents to be concise";
- "agents invented a useful representation";
- "a representation was automatically improved through held-out evidence."

## COMM-003 — Efficiency versus error correction

Compression may improve speed while making teams more brittle.

### Core hypothesis

> A protocol optimized only for task reward per token will tend to discard uncertainty, provenance, or dissent signals that are low-frequency but important for correcting shared mistakes.

This is a hypothesis, not an assumption.

### Error-injection design

Seed controlled defects into one agent's local evidence/state while leaving other agents clean. Measure:

- probability the bad claim propagates;
- number of agents adopting it;
- time/messages until correction;
- whether the protocol preserves the origin of the claim;
- whether independent agents remain independent;
- final external correctness;
- communication cost.

Compare ordinary prose, human provenance schema, and agent-designed protocol.

A compact protocol that wins ordinary benchmarks but amplifies seeded false claims is not an unqualified improvement.

## COMM-004 — Does provenance emerge spontaneously?

The current research program explicitly values evidence lineage and independence. An agent-designed protocol creates a useful adversarial test of whether those fields are genuinely useful or merely human-preferred bookkeeping.

Question:

> When agents optimize communication for held-out task success under adversarial information conditions, do they independently invent representations corresponding to confidence, provenance, dependency, or dissent?

Possible outcomes:

- they reinvent these concepts: evidence that the structures carry operational value;
- they find a simpler representation with equal robustness: simplify our architecture;
- they omit them and remain robust: current provenance machinery may be unnecessary in that task family;
- they omit them and become brittle: efficiency objective was incomplete.

Do not judge similarity to our existing schema as success. Judge held-out behavior.

## COMM-005 — Corruption and channel robustness

Perturb communication rather than the underlying task:

- delete a message;
- truncate payload;
- flip a protocol field;
- substitute a stale protocol version;
- inject an unsupported high-confidence claim;
- reorder messages;
- corrupt a compressed representation.

Measure graceful degradation, detection, repair, and final outcome.

This is the communication analogue of EGP perturbation: alter the evidence-generating/communication path and observe which downstream claims actually depend on it.

## COMM-006 — Independence and false consensus

Multiple agents can look independent while sharing the same upstream representation or copied conclusion.

Test whether increasingly compressed protocols:

- preserve independent evidence lineages;
- collapse agents onto one hypothesis prematurely;
- increase false consensus;
- suppress useful minority hypotheses;
- improve coordination without destroying diversity.

This connects directly to Phase F2 and G8.

## COMM-007 — Recursive protocol evolution

This is not authorized until the Phase-I discovery machinery is trustworthy.

Loop:

P0 → held-out evaluation → failure decomposition → candidate protocol mutations → validation → adversarial corruption test → execution holdout → P1 or reject.

Keep:

- ancestry;
- exact protocol diff;
- development data exposure;
- evaluation results;
- regressions;
- cost change;
- auditability change;
- error-propagation change.

Never promote because a candidate compresses more. Promotion requires the preregistered multi-objective acceptance rule.

## COMM-008 — True latent inter-agent communication

Requires open-weight/model-internal access.

### Ladder

Compare, where technically feasible:

1. ordinary natural language;
2. fixed human-designed structure;
3. agent-designed symbolic interlingua;
4. learned continuous embeddings / bottleneck communication;
5. direct hidden-state or activation communication.

The progression is important because it distinguishes benefits of **machine-optimized representation** from benefits requiring actual neural-state access.

### Experimental invariants

Hold or explicitly model:

- backbone model;
- total inference compute;
- training/fine-tuning budget;
- task exposure;
- number of communicating agents;
- communication rounds;
- evaluator;
- external success criterion.

Measure both task performance and communication bandwidth.

## COMM-009 — Causal latent-state perturbation

If true latent communication produces a gain, do not infer that the transmitted latent state faithfully represents reasoning.

Perturb:

- individual latent steps;
- communication vectors;
- compressed dimensions/subspaces;
- sender/receiver layer mappings.

Ask:

- does the final answer change predictably?;
- can a supposedly important latent message be removed with no effect?;
- do perturbations alter correctness or merely surface form?;
- can latent messages be replaced by simpler summaries without loss?;

This separates causal load-bearing communication from uninterpretable but behaviorally incidental state.

## COMM-010 — Natural-language self-report versus latent cause

Where internal intervention is possible:

1. perturb the latent communication state without telling the model;
2. observe the final decision;
3. ask for a concise causal/explanatory report;
4. compare the report with the known intervention.

The model's explanation remains a claim, not privileged telemetry.

This can test whether natural-language self-explanation tracks the actual manipulated communication cause.

## COMM-011 — Internalized multi-agent reasoning

A later bridge experiment compares:

- explicit multi-agent collaboration;
- symbolic compressed collaboration;
- a model trained/distilled to internalize the collaboration process.

Questions:

- can collaboration benefits be retained with fewer communication tokens?;
- does internalization eliminate useful independence?
- are failure modes easier or harder to localize?
- does an internalized ensemble behave like independent critics or merely one correlated process wearing several labels?

## Promotion criteria

A communication representation earns promotion only if it demonstrates a meaningful improvement under the program's ordinary promotion ladder.

A useful first-pass acceptance rule should require some combination of:

- non-inferior or improved external task success;
- improved success per unit communication/compute;
- no unacceptable increase in seeded-error propagation;
- no unacceptable loss of independent evidence lineage where independence is load-bearing;
- transfer to held-out tasks;
- later execution validation.

Weights/thresholds must be preregistered for any production experiment. Do not collapse this to one judge-generated scalar after outcomes are visible.

## Kill / merge criteria

Kill or merge a branch if:

- agent-designed symbolic communication reduces only verbosity, with no task/cost advantage over a simple fixed schema;
- a simpler compression baseline reproduces the gain;
- gains disappear under matched total compute;
- gains are evaluator artifacts;
- protocol evolution overfits development tasks and fails holdout;
- latent communication adds no value beyond symbolic machine interlingua at matched cost;
- true latent effects cannot survive causal perturbation or external execution testing.

A null is useful if the instrument had enough expected information to distinguish these alternatives.

## Suggested dependency order

Do not put COMM work into the immediate Stage 0B queue.

Recommended junction:

1. finish Stage 0B and measurement/retrieval foundation;
2. establish at least one external-execution multi-agent task family;
3. establish ordinary multi-agent/provenance baseline (F2/G8);
4. run COMM-001 and COMM-003 before automated search;
5. generalize any signal;
6. only then allow COMM-007 recursive protocol evolution under Phase I/J safeguards;
7. once open-weight infrastructure exists, run COMM-008/009 against the strongest symbolic baseline rather than against prose alone.

## Frontier-model watch item

When Astra's system card or other authoritative architecture information becomes public, inspect whether it discloses mechanisms relevant to:

- recurrent/iterative latent compute;
- continuous reasoning;
- internalized debate;
- learned communication bottlenecks;
- latent inter-agent communication.

Do not reverse-engineer a mechanism claim from token efficiency alone. If Astra later exposes a callable capability that changes the experiment's feasible action space, add it as a new treatment/environment state and re-derive the causal contract rather than silently substituting it.

## Bottom line

The branch is valuable precisely because it can fail in informative ways.

The strongest possible result is not "agents invented a secret language." It is evidence that a machine-optimized representation yields a reproducible, externally validated increase in collaborative capability or efficiency **while preserving or improving error correction** — and that the gain survives simpler baselines, held-out tasks, and causal perturbation.
