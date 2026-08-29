# External Cognitive Tools and Memory Topology Research Map — 2026-08-29

Status: program-level research context. Not a preregistration. Does not alter exp004 or other frozen experiments.

## Core question

What external representations, workspaces, and execution tools measurably expand the effective capability of a fixed LLM?

The focus is not "give the model more plugins." It is to test whether specific external cognitive structures improve reliability, memory, planning, calibration, execution, or cost.

## Candidate tool classes

### T1 — Plain persistent filesystem
Provide a writable persistent workspace with structured folders such as:
- /inbox
- /facts
- /evidence
- /hypotheses
- /plans
- /failed
- /self
- /archive

Question: does explicit file-based organization improve long-horizon continuity over ordinary context/memory?

### T2 — Git / GitHub as versioned cognition
Use commits, diffs, branches, tags, rollback, and lineage as persistent external state.

Potential uses:
- competing hypotheses on branches;
- frozen champion procedures;
- rollback after regression;
- provenance of self-model and epistemic updates;
- independent multi-agent worktrees.

Question: does versioned state reduce regression and improve traceability compared with mutable memory alone?

### T3 — SQLite epistemic ledger
Store claims, evidence bindings, time, provenance, status, dependencies, contradictions, supersession, and execution observations.

Question: does structured state outperform ordinary RAG/context when evidence is held constant?

### T4 — Graph memory
Use NetworkX or a similarly lightweight graph representation for:
- dependency traversal;
- evidence lineage;
- multi-agent provenance;
- contradiction links;
- identity relationships;
- causal/functional paths.

Question: does explicit relational topology improve reasoning where semantic similarity is insufficient?

### T5 — Timeline / event log
Append-only chronological record of observations, actions, outcomes, state changes, and revisions.

Question: does temporal queryability improve knowledge updating and long-horizon task continuity?

### T6 — Hypothesis manager
Maintain multiple live hypotheses with:
- support;
- counterevidence;
- predicted observations;
- falsification conditions;
- dependencies;
- status.

Question: does explicit competition among hypotheses reduce premature closure?

### T7 — Safe execution sandbox
Docker/local process sandbox for:
- code execution;
- build/test;
- artifact generation;
- deterministic verification;
- simulations.

Question: does execution-fed evidence improve repair and belief revision beyond prose reflection?

### T8 — Browser automation
Playwright or equivalent for structured interaction with websites, forms, and dynamic applications.

Question: does active browser interaction add value beyond search/RAG for real execution tasks?

### T9 — Symbolic/deterministic tools
Python, SymPy, calculators, parsers, linters, static analyzers.

Question: where should the model delegate deterministic subproblems rather than reason in language?

### T10 — Spatial / topological memory
Represent persistent memory in a stable low-dimensional space.

Possible mappings:
- proximity = conceptual/functional relation;
- edges = dependency/evidence;
- regions = domains;
- height/axis = abstraction, certainty, time, or another tested property;
- self = persistent region inside the wider state.

Important: 3D is an experimental representation, not an assumed improvement.

## Memory-topology experiment family

### TOPO-001 — Text vs RAG vs graph vs learned topology
Same experiences and same model.

Conditions:
A. chronological text memory;
B. vector/RAG retrieval;
C. explicit graph memory;
D. learned topology whose edge weights/positions adapt from task experience.

Outcomes:
- recall;
- long-horizon continuity;
- dependency reasoning;
- contradiction resolution;
- context/token cost;
- transfer to unseen tasks.

### TOPO-002 — 2D vs 3D spatial topology
Hold information and topology constant as much as possible.
Compare low-dimensional embeddings/coordinates against literal 3D spatial organization.

Purpose: determine whether any gain is due to stable topology rather than 3D itself.

### TOPO-003 — Human-designed vs learned topology
A. manually specified relations;
B. relations strengthened/weakened from observed task usefulness.

Question: can experience reorganize memory in a way that improves later action?

### TOPO-004 — Path retrieval vs semantic retrieval
Construct tasks where the useful bridge facts are not strongly semantically similar to the query but lie on a dependency/path chain.

Compare:
- semantic nearest-neighbor retrieval;
- graph/path traversal;
- hybrid.

### TOPO-005 — Epistemic compression
Retrieve the minimal dependency-grounded subgraph needed for the current decision.

Compare against:
- full history;
- large context;
- standard RAG;
- graph slice.

Measure quality at matched token/cost budgets.

### TOPO-006 — Self inside world topology
Represent the agent's self-model as a node/subgraph inside the same world/epistemic state rather than as separate system text.

Question: does unified topology improve procedure selection or create harmful self-referential coupling?

### TOPO-007 — Topology adaptation loop
EXPERIENCE
→ update topology
→ different memory becomes accessible
→ different action
→ new experience
→ update topology.

Primary question: does adaptive external organization produce cumulative gains on unseen tasks?

## Tool-combination experiments

After isolated components earn inclusion:

### TOOL-C1 — Filesystem × Git
Does writable memory plus version history outperform either alone?

### TOOL-C2 — SQLite ledger × graph
Keep SQLite as authoritative state; derive graph views for dependency/path queries.

Question: can we get graph benefits without graph-database complexity?

### TOOL-C3 — Epistemic ledger × execution sandbox
Execution result automatically updates/falsifies claims.

### TOOL-C4 — Hypothesis manager × execution
Prefer actions that maximally discriminate among competing hypotheses.

### TOOL-C5 — Self-model × Git lineage
Track changes in model/prompt/tools/procedure and invalidate stale self-beliefs after configuration changes.

### TOOL-C6 — Multiple agents × independent worktrees
Agents work independently in separate branches/worktrees, then results are compared after execution.

Question: does enforced independence reduce fake consensus and improve solution diversity?

### TOOL-C7 — Browser × epistemic provenance
Browser observations are recorded as evidence objects with source/time/action provenance rather than dumped into context.

## Experimental order

1. Plain filesystem baseline.
2. SQLite ledger.
3. Graph/path layer.
4. Timeline/event log.
5. Hypothesis manager.
6. Execution sandbox.
7. Git/versioned cognition.
8. Learned topology.
9. 2D/3D spatial representation.
10. Pairwise interactions among surviving components.
11. Generalization and real execution.
12. Automated procedure search over the tool/action space.

Do not build all tools at once.

## Setup philosophy

Prefer tools that are:
- free/open-source;
- local-first;
- scriptable;
- observable;
- easy to reset;
- deterministic where possible;
- cheap to expose to Claude Code.

Candidate stack:
- SQLite — built into Python.
- NetworkX — Python package.
- DuckDB — Python package / local binary.
- Git — already in use.
- GitHub — already connected.
- Python/SymPy — local.
- Docker Desktop/Engine — optional for stronger isolation.
- Playwright — optional browser automation.
- Blender — optional only for literal spatial/3D experiments.
- OpenMemory/local embeddings — optional comparator for semantic-memory experiments.

## Manual setup classification

### No manual setup expected initially
Claude Code can usually handle:
- Python packages such as networkx, duckdb, sympy;
- SQLite schemas;
- filesystem workspace;
- Git branches/worktrees;
- local JSON/Parquet/event logs;
- graph/topology simulation in Python.

### Likely manual install/authorization only when that experiment is reached
- Docker Desktop/Engine if not already installed/running.
- Playwright browser/runtime if Claude cannot install browser binaries itself in the environment.
- Blender if literal 3D experiments are authorized.
- Any external MCP/server requiring account authorization.

Do not install these now solely because they might be useful later.

## Guardrails

- External memory must remain auditable; never let summaries overwrite raw evidence.
- Learned topology does not confer truth; it only changes accessibility/organization.
- Spatial proximity must not silently become evidential confidence.
- Git history is provenance, not factual validation.
- More tools may degrade performance through distraction; tool count itself is an intervention.
- Match cost/context/tool budgets when comparing architectures.
- Any tool that changes the action space requires a new experimental condition, not a silent enhancement.
- A topology that improves benchmark recall but harms execution is not a winner.

## Highest-value near-term hypothesis after measurement foundation

The simplest strong test is likely:

Same model + same information + same budget:
A. ordinary context/RAG
B. SQLite epistemic ledger
C. ledger + explicit dependency graph

Then test whether C improves tasks where relational paths, contradiction, provenance, or stale-state revision matter.

Only if graph structure earns value should learned spatial topology be tested.


## Mandatory manual-action alert protocol

The user may skim or not read every research message in full. Therefore any stage that cannot continue without a manual install, authorization, login, hardware action, or local configuration MUST NOT bury that requirement in the body of a report.

### Required behavior

When a manual prerequisite becomes necessary, the very beginning of the agent's response/report must contain a conspicuous block in this form:

**MANUAL SETUP REQUIRED BEFORE CONTINUING**

**What Terry needs to do:** <specific action>

**Why it is required now:** <one sentence>

**Do not continue this experimental stage until this is complete.**

Only after that block may the normal report continue.

If setup is optional rather than blocking, label it **OPTIONAL MANUAL SETUP** instead. Never present an optional setup as blocking.

### Known trigger points

- Docker sandbox experiment → check whether Docker Desktop/Engine is installed and running. If not, trigger the mandatory alert.
- Literal 3D / Blender experiment → check whether Blender is installed and script-accessible. If not, trigger the mandatory alert.
- Playwright/browser automation → first attempt automated/runtime setup. If browser binaries, permissions, or user action are required, trigger the mandatory alert.
- External MCP/service/account → trigger the mandatory alert before any required login, authorization, API key, or connection step.
- Hardware/device experiments → trigger the mandatory alert before any cable, headset, developer-mode, permission, or physical-device action required from Terry.
- Any future dependency that Claude cannot safely install/configure itself → trigger the same protocol.

### Coordination rule

Before beginning each new experimental stage, inspect its prerequisites. If a manual trigger is reached, stop at the boundary and request the setup explicitly. Do not silently skip the experiment, substitute a weaker tool, or proceed with a materially different environment merely because manual setup has not happened.
