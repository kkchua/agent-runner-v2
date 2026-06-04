# WORKFLOW_SOP_v1.md: Delivery Workflow Standard Operating Procedure

---

## Metadata

| Field | Value |
|-------|-------|
| **Document Type** | SOP (Standard Operating Procedure) |
| **Version** | v1.0 |
| **Status** | Active |
| **Owner** | Architect |
| **Project** | agent-runner-v2 (LLM Workflow Orchestration Engine) |
| **Complexity** | Advanced |
| **Last Updated** | 2026-06-03 |
| **Valid From** | 2026-06-03 onwards |

---

## 1. Purpose

This SOP governs end-to-end delivery for the **agent-runner-v2** project—a sophisticated Python 3.11+ LLM workflow orchestration engine that manages multi-agent, multi-step delivery pipelines. It ensures:

- **Deterministic execution** through document-driven state machines (not prompt-driven ad-hoc decisions)
- **Clear authority precedence**: Runner logic > SOP + Status Rules > Artifact metadata > Artifact body
- **No phase skipping**, no artifact overwriting, no scope drift
- **Single source of truth** for workflow state, persisted in structured artifacts with meta.json sidecars
- **Scalable multi-agent orchestration** with approval gates, independent review loops, and validation checkpoints
- **Reproducible execution** for parallel tasks, multiple LLM providers (Claude, Codex, Qwen, DeepSeek), and human-in-the-loop scenarios

This SOP applies to all delivery work initiated through the runner: CLI execution, daemon mode, and programmatic API invocations.

---

## 2. Core Principle: Document-Driven + State-Driven Execution

**Workflow execution is driven by artifact state and runner-enforced transitions, not by LLM-generated instructions or dynamic prompts.**

- **Artifacts are the contracts**: Each delivery phase produces an artifact (initiative, plan, task graph, task, implementation plan, review, validation, memory) with explicit state and metadata.
- **State machine is canonical**: The runner enforces transitions. No phase is entered until upstream artifacts reach required states. No artifact is modified after approval without explicit supersession.
- **Authority is centralized**: The Architect (project owner) approves workflow scope, plans, and reviews. Executors operate within approved scope. Reviewers and Validators work independently.
- **Templates define contracts**: Workflow step configurations in `template_groups.py` serve as agent invocation contracts. Agent master prompts are deprecated—templates define what agents must produce, not how they reason.
- **Sidecars are the only communication channel**: meta.json sidecars are the ONLY source of truth for state, approval decisions, and runtime events. No stdout JSON parsing, no markdown write-backs, no disk recovery.

---

## 3. Authority Precedence Hierarchy (Strict)

When resolving conflicts or validating decisions, apply this precedence (highest to lowest):

1. **Runner Logic** (highest): The runner enforces state machines, budget/timeout constraints, artifact validation, and sidecar decisions. Runner decisions override all lower tiers. No Architect override of runner enforcement.
2. **This SOP**: Workflow phases, role definitions, execution discipline, validation requirements.
3. **DELIVERY_STATUS_RULES_v1.md**: Artifact lifecycle rules, approval gates, forbidden transitions, authority model.
4. **Artifact Metadata** (meta.json, frontmatter): Status, owner, dependencies, approval records, timestamps.
5. **Artifact Body Content** (lowest): Plan details, implementation notes, review findings, memory snapshots—inform decisions but do not override state rules.

**Implication**: If an artifact's body suggests a transition but state rules forbid it, the state rule wins. If budget is exhausted, the runner rejects invocation regardless of artifact content. Approval authority is role-based—only Architect can approve workflows; Reviewers and Validators cannot.

---

## 4. Workflow Approval Authority

**Approval is runner-enforced, not artifact-defined. Execution requires explicit approval recorded in meta.json sidecars.**

- **Architect**: Approves initiatives (scope-lock), plans (decomposition-lock), implementation plans (strategy-lock), and reviews (go/no-go on code). Architect decisions are durable and binding.
- **Reviewer** (independent agent): Conducts code review, contract-compliance validation; produces review artifacts but DOES NOT approve workflow transitions. Findings are submitted to Architect for decision.
- **Validator** (independent agent): Conducts acceptance testing, contract fulfillment verification; produces validation artifacts but DOES NOT approve. Final sign-off is Architect's.
- **Executor**: Implements within approved plan scope; cannot approve own work.
- **Memory Manager**: Preserves context, tracks supersessions, generates snapshots; informs Architect decisions but does not approve.
- **Runner**: Enforces approval gates—rejects invalid transitions regardless of content or who requests them.

Approval is **durable** and **binding**—once an artifact is approved, its scope is locked. Changes require new artifact + explicit supersession links + Architect re-approval.

---

## 5. Complete Workflow State Machine

The runner enforces this deterministic state machine for all delivery initiatives:

```
┌─ INITIATIVE_CREATED (draft)
│  ↓ [Architect review + approval]
├─ INITIATIVE_APPROVED (locked scope)
│  ↓ [Planner generates plan]
├─ PLAN_CREATED (draft)
│  ↓ [Reviewer assesses; Architect approves]
├─ PLAN_APPROVED (locked plan)
│  ↓ [Task Decomposer creates task graph]
├─ TASK_GRAPH_CREATED (draft)
│  ↓ [Reviewer assesses; Architect approves]
├─ TASK_GRAPH_APPROVED (locked decomposition)
│  ↓ [Implementation Planner details strategy per task]
├─ IMPL_PLAN_CREATED (draft)
│  ↓ [Architect approves strategy]
├─ IMPL_PLAN_APPROVED (locked strategy)
│  ↓ [Executor begins work; tasks transition Pending → In Progress]
├─ TASK_EXECUTION_STARTED (parallel execution allowed per task graph)
│  ↓ [tasks transition In Progress → Implemented]
├─ IMPLEMENTATION_COMPLETED (all approved tasks Implemented)
│  ↓ [Reviewer analyzes code, tests, contract compliance]
├─ REVIEW_SUBMITTED (draft review artifact created)
│  ↓ [Reviewer finalizes; Architect reviews findings + decision]
├─ REVIEW_APPROVED (findings accepted; code approved or rework requested)
│  │  ├─ [if rework required: route back to TASK_EXECUTION_STARTED]
│  │  └─ [if approved: proceed to validation]
│  ↓
├─ VALIDATION_STARTED (Validator executes acceptance tests)
│  ↓ [Validator produces test results + compliance matrix]
├─ VALIDATION_COMPLETED (final artifact signed)
│  │  ├─ [if acceptance fails: route back to TASK_EXECUTION_STARTED]
│  │  └─ [if acceptance passes: proceed to completion]
│  ↓
├─ WORKFLOW_COMPLETED (Architect final sign-off; terminal state)
│
└─ Alternative Terminal States:
   ├─ SUPERSEDED (Architect initiates; cancels all downstream work; preserves prior state)
   ├─ CANCELLED (Architect initiates; terminates immediately; no recovery)
   └─ BLOCKED (deadlock state; awaits Architect resolution or supersession)
```

**Key Rules**:
- **Forward only**: No backward transitions except through explicit rework routing or supersession.
- **No skipping**: Each state must be reached in order. Runner rejects attempts to skip phases.
- **Approval gated**: Transitions marked `[Architect review + approval]` require runner-enforced approval in upstream artifact meta.json.
- **Idempotent phase re-entry**: If a phase re-executes (retry), state does not advance unless upstream artifact changes.
- **Rejection routing**: Review or validation rejection routes work back to TASK_EXECUTION_STARTED for executor rework; Architect reviews revised implementation before re-approval.

---

## 6. Agent Roles Table (Advanced Complexity)

| Role | Primary Responsibility | Output Artifact | Authority | Notes |
|------|---|---|---|---|
| **Architect** | Initiative scope approval, plan review, code review decision, final sign-off, scope/timeline adjustments | Approval decisions recorded in meta.json | Approves initiatives, plans, reviews, validates; only role authorized to lock/unlock scope | Project owner; makes binding decisions; no role subordination |
| **Planner** | High-level delivery plan, phases, milestones, resource/timeline estimates | Plan artifact (structured phases, timeline, risk assessment) | Informed by approved initiative; submits plan to Architect for approval | No authority to approve own plan |
| **Task Decomposer** | Dependency-aware task graph generation, parallelism analysis, sequencing | Task graph artifact (nodes, edges, dependencies, parallel-safe branches) | Operates on approved plan; graph submitted to Architect for approval | No authority to approve own decomposition |
| **Implementation Planner** | Per-task implementation strategy, scope boundaries, acceptance criteria, success metrics, risk mitigation | Implementation plan artifact (per-task detailed strategy, acceptance criteria) | Works within approved plan; submits plan to Architect for approval | No authority to approve own plan |
| **Executor** | Code implementation, feature development, integration testing, metrics collection | Task artifact with implemented code, test results, metrics | Works strictly within approved implementation plan; reports blockers to Architect | No authority to approve own implementation |
| **Reviewer** | Independent code review, contract-compliance validation, architectural alignment, risk assessment | Review artifact with findings, recommendations, risk score, compliance matrix | Independent of executor; submits findings to Architect for approval decision | Does NOT approve workflow; findings are advisory |
| **Validator** | Acceptance testing, success criteria verification, contract fulfillment validation, deployment readiness | Validation artifact with test results, compliance matrix, deployment checklist | Independent post-implementation; validates against approved contract | Does NOT approve workflow; findings are advisory |
| **Memory Manager** | Context preservation, supersession tracking, decision snapshots, learned constraints | Memory artifacts with decision history, constraints, supersession chain | Supports Architect decisions and refine/replan loops; preserves audit trail | Enables reproducible execution and future planning |
| **Runner** | State machine enforcement, budget/timeout management, artifact validation, phase routing, sidecar management | meta.json sidecars, state transition validation, failure routing | Enforces legal transitions; no Architect override of runner rules | Strict enforcement; cannot be bypassed |

---

## 7. Workflow Phases (Advanced Complexity)

### 7.1 Phase 1: Initiative & Scope Lock (INITIATIVE_CREATED → INITIATIVE_APPROVED)

| Attribute | Detail |
|-----------|--------|
| **Owner** | Architect |
| **Agent(s)** | None (Architect-driven; no agent invocation) |
| **Input** | User request, business context, high-level objectives, constraints |
| **Action** | Create initiative artifact; document scope, success criteria, out-of-scope items, stakeholders, timeline estimate |
| **Output** | Initiative artifact (draft → approved) with locked scope metadata |
| **Sidecar** | initiative.meta.json with status: approved, approved_by: Architect, approved_at: ISO timestamp |
| **State After** | `INITIATIVE_APPROVED` (scope is now locked; downstream phases must respect this scope) |

**Mandatory Sections** (initiative artifact must include):
- Title, objective, success criteria (measurable)
- Out-of-scope items (explicit boundary)
- Stakeholders and decision authority
- Timeline estimate and key milestones
- Constraints (budget, dependencies, integration points)
- Risks and assumptions

**Rules**:
- Architect approves scope—this locks the scope for all downstream phases.
- No plan may be created until initiative is approved.
- Once approved, scope modifications require new initiative + explicit supersession link (preserves audit trail).
- Supersession maintains prior context: Memory Manager tracks scope evolution.

---

### 7.2 Phase 2: Planning (PLAN_CREATED → PLAN_APPROVED)

| Attribute | Detail |
|-----------|--------|
| **Owner** | Planner |
| **Agent(s)** | Planner (plan generation from approved initiative) |
| **Input** | Approved initiative artifact (read-only) |
| **Action** | Generate high-level delivery plan: phases, milestones, resource needs, timeline, risk assessment |
| **Output** | Plan artifact (draft → reviewed → approved) |
| **Sidecar** | plan.meta.json with status progression: draft → (reviewer input) → approved_by: Architect |
| **State After** | `PLAN_APPROVED` (plan is locked; task decomposition proceeds) |

**Mandatory Sections** (plan artifact must include):
- Phase breakdown (each phase with owner, duration, deliverables)
- Milestones and timeline
- Resource estimate (people, time, budget)
- Risk assessment and mitigation
- Dependencies on external systems/teams
- Rollback/failure recovery strategy

**Rules**:
- Planner reads approved initiative, produces plan respecting scope boundaries.
- Reviewer assesses plan quality and contract alignment; submits findings.
- Architect reviews plan + reviewer findings; approves or requests rework.
- Once approved, plan cannot be modified (supersession required for changes).
- Plan must explicitly reference approved initiative ID.

---

### 7.3 Phase 3: Task Decomposition (TASK_GRAPH_CREATED → TASK_GRAPH_APPROVED)

| Attribute | Detail |
|-----------|--------|
| **Owner** | Task Decomposer |
| **Agent(s)** | Task Decomposer (dependency analysis, parallelism detection) |
| **Input** | Approved plan artifact (read-only) |
| **Action** | Decompose plan into tasks: task nodes, dependencies, parallelism analysis, sequencing constraints |
| **Output** | Task graph artifact (draft → reviewed → approved) with all tasks explicitly listed |
| **Sidecar** | task_graph.meta.json with status progression: draft → approved_by: Architect |
| **State After** | `TASK_GRAPH_APPROVED` (decomposition locked; implementation planning begins) |

**Mandatory Sections** (task graph artifact must include):
- Task node definitions: ID, title, owner, estimated effort, acceptance criteria
- Dependency edges: which tasks block which tasks
- Parallelism analysis: which tasks can run in parallel (DAG structure)
- Critical path identification
- Sequencing constraints (ordering, blocking relationships)
- Resource requirements per task (human, compute, budget)

**Rules**:
- Task Decomposer reads approved plan, produces task graph with clear dependencies.
- Reviewer assesses decomposition correctness, parallelism safety, effort estimates.
- Architect approves task graph; decomposition is now locked.
- All tasks in graph must have corresponding task artifacts created before execution.
- Task graph must explicitly reference approved plan ID.

---

### 7.4 Phase 4: Implementation Planning (IMPL_PLAN_CREATED → IMPL_PLAN_APPROVED)

| Attribute | Detail |
|-----------|--------|
| **Owner** | Implementation Planner |
| **Agent(s)** | Implementation Planner (per-task detail planning) |
| **Input** | Approved task graph artifact (read-only) |
| **Action** | For each approved task: detail implementation strategy, scope, acceptance criteria, success metrics, risk mitigation, test plan |
| **Output** | Implementation plan artifact (draft → approved) with per-task strategies |
| **Sidecar** | implementation_plan.meta.json with status: approved_by: Architect |
| **State After** | `IMPL_PLAN_APPROVED` (strategy locked; execution phase begins) |

**Mandatory Sections** (implementation plan artifact must include):
- Per-task implementation strategy (approach, tools, techniques)
- Scope boundaries (what is in/out of task scope)
- Acceptance criteria (measurable completion conditions)
- Test plan (unit, integration, system testing)
- Risk mitigation and rollback strategies
- Success metrics (code coverage, performance, compliance)
- Dependencies and integration points

**Rules**:
- Implementation Planner respects approved task graph—no reordering or parallelism changes.
- Architect approves strategy and acceptance criteria—this locks them.
- Once approved, changes require explicit plan supersession.
- Implementation plan must reference approved task graph ID and plan ID.

---

### 7.5 Phase 5: Implementation & Execution (TASK_EXECUTION_STARTED → IMPLEMENTATION_COMPLETED)

| Attribute | Detail |
|-----------|--------|
| **Owner** | Executor |
| **Agent(s)** | Executor (code implementation, testing, integration) |
| **Input** | Approved implementation plan + approved task graph (read-only) |
| **Action** | Execute each task in sequence/parallel per task graph; produce code, tests, documentation; verify acceptance criteria |
| **Output** | Task artifacts (one per task) with implementation, test results, metrics |
| **Sidecar** | task.meta.json with status progression: pending → in_progress → implemented |
| **State After** | `IMPLEMENTATION_COMPLETED` (all approved tasks transitioned to Implemented state) |

**Task State Progression** (per task):
1. **Pending**: Task created, awaiting executor assignment
2. **In Progress**: Executor claims task, work begins
3. **Implemented**: Executor submits task artifact with code, tests, and metrics; sidecar written
4. **Approved**: (After review + validation) Task formally approved; ready for production

**Rules**:
- Executor follows approved task graph and implementation plan strictly—no scope changes without approval.
- Each task produces a task artifact with: implemented code, test results, test coverage, metrics, blockers/deviations.
- Task artifacts must reference task graph task ID, plan ID, and implementation plan ID.
- No task may be marked `Implemented` without passing acceptance criteria + test evidence.
- Budget and timeout enforced by runner—overages trigger escalation to Architect.
- Blocked tasks remain `In Progress` until blocker resolved; Architect may supersede blocked task.
- Executor reports progress, risks, and blockers to Architect via task metadata.

---

### 7.6 Phase 6: Independent Review (REVIEW_SUBMITTED → REVIEW_APPROVED)

| Attribute | Detail |
|-----------|--------|
| **Owner** | Reviewer |
| **Agent(s)** | Reviewer (code review, contract validation, risk assessment) |
| **Input** | Completed task artifacts + approved implementation plan (read-only) |
| **Action** | Independently review code, test coverage, contract compliance, architectural alignment, risk; produce detailed findings |
| **Output** | Review artifact (draft → final) with findings, recommendations, risk score, compliance matrix |
| **Sidecar** | review.meta.json with status: final (reviewed_by: Reviewer, reviewed_at: ISO timestamp) |
| **State After** | `REVIEW_APPROVED` (Architect decision on review findings; go/no-go on code) |

**Reviewer Assessment** (review artifact must include):
- **Code correctness**: Logic errors, edge cases, test coverage gaps
- **Contract compliance**: Acceptance criteria fulfillment, success metrics met
- **Architectural alignment**: Design consistency, patterns, no tech-debt regression
- **Risk assessment**: Security, performance, maintainability, operational risks
- **Recommendations**: Rework items, optimizations, improvements
- **Risk score**: Low (green-light), Medium (conditional approval), High (requires rework)

**Rules**:
- Reviewer works independently of executor—does not coordinate during review.
- Review findings are advisory; Architect makes go/no-go decision.
- If Architect approves (low/medium risk + findings acceptable): proceed to validation.
- If Architect requests rework (high risk, blockers): route back to TASK_EXECUTION_STARTED for executor rework.
- Review artifact must reference approved implementation plan ID and task artifact IDs.
- Reviewer does NOT approve workflow state; Architect approval is recorded in workflow meta.json.

---

### 7.7 Phase 7: Validation & Acceptance (VALIDATION_STARTED → VALIDATION_COMPLETED)

| Attribute | Detail |
|-----------|--------|
| **Owner** | Validator |
| **Agent(s)** | Validator (acceptance testing, contract fulfillment verification) |
| **Input** | Approved review artifact + task artifacts (read-only) |
| **Action** | Execute acceptance tests, verify success criteria (from initiative), check contract fulfillment, confirm deployment readiness |
| **Output** | Validation artifact (draft → final) with test results, compliance matrix, deployment checklist, sign-off |
| **Sidecar** | validation.meta.json with status: final, validated_by: Validator, validated_at: ISO timestamp |
| **State After** | `VALIDATION_COMPLETED` (Architect final sign-off) |

**Validation Checklist** (validation artifact must include):
- **Success criteria verification**: Each initiative success criterion tested and passed/failed
- **Acceptance test results**: Automated test runs, coverage report, pass rate
- **Contract fulfillment matrix**: Mapped against task artifacts and approved acceptance criteria
- **Integration validation**: If applicable, integration with external systems tested
- **Deployment readiness**: Configuration, documentation, runbooks, rollback plan
- **Sign-off recommendation**: Ready for production or requires rework

**Rules**:
- Validation is independent of review—validator focuses on behavior, not code.
- Validator uses acceptance tests to verify contract fulfillment (not code review).
- If acceptance tests pass and deployment checklist complete: Validator recommends approval.
- If acceptance tests fail or deployment blockers exist: route back to TASK_EXECUTION_STARTED for rework.
- Validator does NOT approve workflow; Architect reviews validation artifact and makes final decision.
- Validation artifact must reference approved review artifact ID and task artifact IDs.

---

### 7.8 Phase 8: Workflow Completion (WORKFLOW_COMPLETED)

| Attribute | Detail |
|-----------|--------|
| **Owner** | Architect |
| **Agent(s)** | None (Architect sign-off; optional Memory Manager snapshot) |
| **Input** | Approved validation artifact (read-only) |
| **Action** | Architect reviews validation results, signs off on completion, triggers optional memory snapshot |
| **Output** | Workflow marked COMPLETED in initiative meta.json; optional memory artifact with context snapshot |
| **Sidecar** | initiative.meta.json updated: status = completed, completed_by: Architect, completed_at: ISO timestamp |
| **State After** | `WORKFLOW_COMPLETED` (terminal state; no further execution) |

**Rules**:
- Architect final decision: approve validation or request rework.
- Approval triggers workflow completion and optional memory snapshot.
- Memory snapshot preserves decisions, constraints, and learned patterns for future projects.
- Completed workflows are archived; cannot be modified without explicit new initiative.

---

### 7.9 Phase 9: Memory & Context Preservation (Parallel to Phases 1-8)

| Attribute | Detail |
|-----------|--------|
| **Owner** | Memory Manager |
| **Agent(s)** | Memory Manager (snapshot generation, supersession tracking, constraint capture) |
| **Input** | All artifacts from all phases (read-only) |
| **Action** | Capture decisions, constraints, learned patterns; track supersession chains; generate snapshots for refine/replan loops |
| **Output** | Memory artifacts with context preservation, supersession links, decision history |
| **Sidecar** | memory.meta.json with status: final, created_by: Memory Manager |
| **State After** | Continuous—memory updated at each phase transition (no state gate blocking memory creation) |

**Memory Artifact Sections**:
- **Decision history**: What was decided (scope, plan, implementation strategy), why, by whom, when
- **Constraints discovered**: Budget overruns, timeline pressures, technical blockers, stakeholder changes
- **Learned patterns**: What worked, what didn't, best practices for similar projects
- **Supersession chain**: Original artifacts → modified versions → final state (preserves audit trail)
- **Effort snapshots**: Actual vs. estimated effort per phase (informs future planning)

**Rules**:
- Memory manager runs in parallel—does not block any phase.
- Memory artifacts preserve all context (decisions, deviations, constraints).
- Refine/replan loops (Architect-triggered): revisit and adjust plan/implementation without losing prior context.
- Memory enables reproducible execution and continuous process improvement.
- Supersession links in memory prevent orphaned prior versions; all versions traceable.

---

## 8. Standard Rules (Mandatory for All Phases)

### 8.1 No Phase Skipping
- Workflow proceeds through phases in order: Initiative → Planning → Decomposition → Implementation Planning → Execution → Review → Validation → Completion.
- Runner strictly enforces: Phase N+1 entry requires Phase N artifact at required state.
- Example: Task execution cannot begin until TASK_GRAPH_APPROVED is true. Validation cannot start until REVIEW_APPROVED is true.

### 8.2 No Overwriting Approved Artifacts
- Once an artifact reaches `approved` state, it cannot be modified in-place—only superseded.
- Modifications require: new artifact, explicit supersession link to prior artifact, Architect approval of new artifact.
- This prevents silent scope creep, maintains approval durability, and preserves audit trail.

### 8.3 No Scope Drift
- Scope is locked at initiative approval. Expand scope only via new initiative or explicit Architect-approved supersession.
- Implementation must operate strictly within approved plan scope. Any deviation requires plan approval change.
- Reviewer and Validator flag out-of-scope work—triggers executor rework or Architect override decision.
- Memory Manager tracks scope changes (original vs. actual) for future reference.

### 8.4 Deterministic Outputs
- Given same input (approved artifacts, runner config, seeded LLM parameters), phases must produce consistent results.
- Non-determinism sources (LLM randomness, agent variance): mitigated by fixed templates, seeded parameters, and repeat-run validation.
- Executor and Reviewer use version-pinned tools, fixed test data, and reproducible build environments.
- Snapshots enable deterministic audit trails and reproducible execution.

### 8.5 Single Source of Truth
- Artifact state (`meta.status`) is the authoritative lifecycle record. Runner updates this; agents read it.
- No parallel artifact versioning—supersession is explicit (prior artifact links to new artifact; no orphans).
- All decisions (approvals, rework requests, escalations) recorded in artifact metadata and meta.json sidecars.
- Runner enforces: no work begins without approved upstream artifact; no artifact approved twice.

### 8.6 Document-First Execution
- No work is executed without: documented artifact + approved upstream plan + runner-recognized state transition.
- Verbal agreements, Slack decisions, or undocumented approvals do NOT authorize work.
- Architect approvals recorded in artifact metadata: `approved_by`, `approved_at`, `approved_reason`.
- Budget and timeout enforcement precede agent invocation—runner validates before execution.

---

## 9. Folder Structure (Standard `docs/delivery/`)

```
docs/delivery/
├── 00_templates/
│   ├── WORKFLOW_SOP_v1.md                    ← This document
│   ├── DELIVERY_STATUS_RULES_v1.md           ← Status rules engine
│   ├── template_registry.md                  ← Artifact-template mapping
│   ├── 01_initiative.template.md             ← Initiative contract
│   ├── 02_plan.template.md                   ← Plan contract
│   ├── 02a_taskgraph.template.md             ← Task graph contract
│   ├── 03_task.template.md                   ← Task contract
│   ├── 04_implementation_plan.template.md    ← Implementation plan contract
│   ├── 05_review.template.md                 ← Review contract
│   ├── 06_validation.template.md             ← Validation contract
│   └── 07_memory.template.md                 ← Memory contract
│
├── 01_initiatives/
│   ├── INIT-{YYYYMMDD}-{NN}/
│   │   ├── initiative.md                     ← Artifact (scope, criteria, risks)
│   │   └── meta.json                         ← State: draft|approved|completed|superseded
│   │
│   ├── draft/                                ← Pre-approval drafts
│   │   └── {draft initiative}.md
│   │
│   └── pre_init/                             ← Exploration, not in workflow
│       └── {discovery}.md
│
├── 02_plans/
│   ├── PLAN-{YYYYMMDD}-{NN}/
│   │   ├── plan.md                           ← Artifact (phases, timeline, risks)
│   │   ├── artifacts/
│   │   │   ├── TASK-GRAPH-{ID}.md            ← Task decomposition
│   │   │   └── {supporting docs}
│   │   └── meta.json                         ← State: draft|reviewed|approved|completed
│   │
│   └── draft/
│       └── {draft plan}.md
│
├── 03_tasks/
│   ├── TASK-{YYYYMMDD}-{NN}/
│   │   ├── task.md                           ← Artifact (implementation, metrics)
│   │   ├── results/                          ← Test output, code diffs
│   │   │   ├── test_results.json
│   │   │   └── {metrics}
│   │   └── meta.json                         ← State: pending|in_progress|implemented|approved|blocked|cancelled
│   │
│   └── blocked/
│       └── {blocked task}.md
│
├── 04_implementation_plans/
│   ├── IMPL-{YYYYMMDD}-{NN}/
│   │   ├── implementation_plan.md             ← Artifact (per-task strategy, criteria)
│   │   ├── artifacts/
│   │   │   └── {supporting docs}
│   │   └── meta.json                         ← State: draft|approved
│   │
│   └── draft/
│       └── {draft impl plan}.md
│
├── 05_reviews/
│   ├── REVIEW-{YYYYMMDD}-{NN}/
│   │   ├── review.md                         ← Artifact (findings, risk assessment)
│   │   ├── artifacts/
│   │   │   ├── coverage_report.txt
│   │   │   └── risk_analysis.md
│   │   └── meta.json                         ← State: draft|final (Architect approves workflow state)
│   │
│   └── draft/
│       └── {draft review}.md
│
├── 06_validation/
│   ├── VALIDATION-{YYYYMMDD}-{NN}/
│   │   ├── validation.md                     ← Artifact (test results, compliance matrix)
│   │   ├── artifacts/
│   │   │   ├── test_results.json
│   │   │   └── compliance_matrix.md
│   │   └── meta.json                         ← State: draft|final (Architect approves workflow state)
│   │
│   └── draft/
│       └── {draft validation}.md
│
├── 08_agents/
│   ├── AGENTS.md                             ← Agent role definitions (no master prompts)
│   ├── planner.contract.md                   ← Agent invocation contract
│   ├── task_decomposer.contract.md
│   ├── implementation_planner.contract.md
│   ├── executor.contract.md
│   ├── reviewer.contract.md
│   ├── validator.contract.md
│   └── memory_manager.contract.md
│
└── 09_memory/
    ├── MEMORY-{YYYYMMDD}-{NN}/
    │   ├── memory.md                         ← Artifact (decisions, constraints, snapshots)
    │   ├── artifacts/
    │   │   ├── decisions.md
    │   │   ├── constraints.md
    │   │   └── supersession_chain.md
    │   └── meta.json                         ← State: final
    │
    └── snapshots/
        └── {periodic context snapshots}
```

**Key Naming Conventions**:
- Initiative: `INIT-{YYYYMMDD}-{NN}` (date + sequence)
- Plan: `PLAN-{YYYYMMDD}-{NN}`
- Task: `TASK-{YYYYMMDD}-{NN}`
- Implementation Plan: `IMPL-{YYYYMMDD}-{NN}`
- Review: `REVIEW-{YYYYMMDD}-{NN}`
- Validation: `VALIDATION-{YYYYMMDD}-{NN}`
- Memory: `MEMORY-{YYYYMMDD}-{NN}`
- Task Graph (within plan): `TASK-GRAPH-{YYYYMMDD}-PLAN-{PLAN-ID}`

**Critical**: No `07_master_prompts/` folder—agent master prompts are deprecated. Workflow step configurations in `template_groups.py` serve as invocation contracts.

---

## 10. Validation Philosophy

### 10.1 Independent Validation Tiers
- **Review**: Independent of implementation (different agent, no executor input during review).
- **Validation**: Independent of review (new agent, focuses on behavior not code).
- This prevents conflicts of interest and catches implementation drift early.

### 10.2 Structured Validation
- Every artifact includes structured metadata: state, owner, dependencies, approval status.
- Validation checks: (a) required sections present, (b) upstream references valid and approved, (c) status transitions legal per state machine.
- Runner validates artifact structure and sidecar before phase transition—invalid artifacts block progress.

### 10.3 Mandatory Before Completion
- Workflow cannot complete without: (a) all tasks `Implemented`, (b) independent review submitted and approved by Architect, (c) validation complete and approved by Architect, (d) Architect final sign-off.
- Phase failures trigger rework cycle or escalation to Architect.
- No phase may be skipped; no artifact may bypass review.

---

## 11. Approval Gates & Escalation Paths

### 11.1 Explicit Approval Points
1. **Initiative Approval** (Architect): Locks scope for entire workflow. No plan until approved.
2. **Plan + Task Graph Approval** (Architect): Locks decomposition, sequencing, and effort estimates. No execution until approved.
3. **Implementation Plan Approval** (Architect): Locks acceptance criteria and implementation strategy. No code until approved.
4. **Review Approval** (Architect decision on review findings): Approves code for validation or requests rework.
5. **Validation Approval** (Architect decision on validation results): Approves deployment readiness or requests rework.
6. **Final Sign-Off** (Architect): Confirms workflow complete. Workflow transitions to terminal state.

### 11.2 Escalation Triggers
- **Budget overrun**: Task execution exceeds approved budget → Runner escalates to Architect; decision: extend, rework, or cancel.
- **Timeout exceeded**: Phase takes longer than approved → Runner escalates to Architect; decision: extend, rework, or cancel.
- **Review blockers**: Reviewer finds contract violations, security issues, or major rework needed → Architect decides: approve with conditions, request rework, or cancel.
- **Validation failure**: Acceptance criteria not met or deployment blocker → Architect decides: request rework, override (with documented reason), or cancel.

### 11.3 Rework Cycles
- Rework triggered by: Review findings (Architect-approved), Validation failure, Budget/Timeline breach.
- Rework maintains full traceability: new implementation plan references original plan, supersession links preserved, prior artifacts archived.
- Executor has bounded context from prior attempt; Memory Manager provides constraints.
- Refine/replan loops (optional, Architect-initiated): Re-visit plan, re-decompose tasks, or re-scope implementation without losing context.

---

## 12. Runner Integration Points

The runner enforces this SOP through:

1. **State Validation**: Before entering any phase, runner verifies upstream artifacts are at required states. Rejects invalid transitions with clear error.
2. **Approval Gate Enforcement**: Runner checks `approved_by` and `approved_at` fields in artifact meta.json. No transition without valid Architect approval.
3. **Budget/Timeout Enforcement**: Runner tracks agent invocations, costs, and elapsed time per phase. Triggers escalation if exceeded; blocks invocation if insufficient budget.
4. **Artifact Validation**: Runner validates artifact structure (required sections, valid references, correct state). Rejects malformed artifacts; reports validation errors.
5. **Sidecar Management**: Runner writes/updates meta.json sidecar at each phase completion, encoding state, approval, and validation results.
6. **Routing**: Runner routes work to appropriate agents based on phase and approved scope. Executes phase-appropriate templates from `template_groups.py`.
7. **Failure Handling**: Hard failures route immediately through `route_after_failure()`. No silent recovery. Escalation routed to Architect with full context.

**Critical**: The runner is the authority—no Architect override of runner-enforced rules. If the runner rejects a state transition (e.g., budget exhausted, approval missing), the artifact must be fixed or superseded.

---

## 13. Backward Compatibility & Daemon Mode

- **Direct CLI execution** (legacy path): Preserved. `ukbe-run-agent` CLI continues to work for synchronous workflows.
- **Daemon mode** (new): PostgreSQL-backed job management with submit/status/worker/approve/reject/retry/cancel CLI commands.
- **Conservative v1 resume**: Daemon does not auto-recover from crashes. Explicit approval required for retries. Preserves audit trail.
- **Cross-project scaffolding**: `--target-project-root` allows scaffolding this delivery infrastructure into any repository.

All workflows (direct or daemon) enforce this SOP and DELIVERY_STATUS_RULES_v1.md.

---

## 14. Version & Change Control

- **SOP Version**: v1.0 (effective 2026-06-03)
- **Status**: Active
- **Supersession**: This SOP supersedes all prior workflow documentation. Older SOPs archived in `docs/delivery/01_initiatives/artifacts/`.
- **Changes**: SOP updates require Architect approval and explicit version bump (v1.0 → v1.1). Changes recorded in `CHANGELOG.md` at project root.
- **Governance**: Changes to SOP or Status Rules require proposal (artifact) → Architect review → approval → version bump.

---

## 15. Glossary

| Term | Definition |
|------|-----------|
| **Artifact** | Structured document (initiative, plan, task, review, validation, memory) representing deliverable state, scope, and metadata. Written to disk; versioned; approved via meta.json sidecar. |
| **State** | Current lifecycle stage of an artifact (draft, reviewed, approved, completed, superseded, blocked, cancelled). Stored in meta.json. Runner-enforced. |
| **Approval** | Architect-recorded decision (in meta.json) to authorize scope, plan, or review findings. Durable—cannot be revoked without explicit supersession. |
| **Supersession** | Explicit linkage of a new artifact to a prior artifact, indicating the new artifact replaces the old. Maintains traceability and audit trail. |
| **Phase** | Workflow stage (initiative, planning, decomposition, implementation planning, execution, review, validation, completion). Each produces an artifact and enforces state transition. |
| **Scope** | Boundary of work—what is in-scope and what is out-of-scope. Locked at initiative approval. Changes require new initiative or explicit supersession. |
| **Contract** | Template + metadata structure that defines what an artifact must contain and what agents must produce. Enforced by runner and templates. |
| **Meta.json Sidecar** | Runtime state file written by runner, encoding artifact status, approvals, dependencies, validation results, timestamps. Runner reads sidecars for all state decisions. |
| **Template** | Structured contract in `template_groups.py` defining agent invocation (input, output format, acceptance criteria). Agent master prompts deprecated. |
| **Agent Role** | Persona (Architect, Planner, Executor, Reviewer, Validator, etc.) with defined authority and responsibility within the workflow. |
| **Rework Cycle** | Path from Review/Validation rejection back to TASK_EXECUTION_STARTED, where executor addresses findings and re-implements. Full traceability maintained. |

---

## 16. References

- **DELIVERY_STATUS_RULES_v1.md**: Detailed artifact lifecycle rules, forbidden transitions, authority model.
- **template_registry.md**: Mapping of artifact types to templates.
- **AGENTS.md**: Agent role definitions, responsibilities, authority boundaries.
- **Agent Contracts** (08_agents/*.contract.md): Per-agent invocation rules, input/output validation, success criteria.
- **UKBE Specifications** (docs/specs/): Data models, artifact contracts, core data structures, contract planning.
- **template_groups.py**: Workflow step configurations (agent invocation contracts, no master prompts).

---

**End of WORKFLOW_SOP_v1.md**  
*Document effective 2026-06-03 for agent-runner-v2 (advanced complexity, LLM orchestration engine)*
| **Architect** | Workflow policy, scope decisions, approval gates, exception handling, completion authority | Approve initiatives, plans, task graphs; gate complex decisions; route failures; supersede/cancel workflows | Initiative, Plan, Task Graph, SOP, Status Rules | Final authority; gates workflow progression; can override, restart, or terminate |
| **Planner** | Create delivery plans, define phases, estimate scope, break down work | Draft plans and phases | Plan | Reads approved initiative; outputs plan for review |
| **Task Decomposer** | Create dependency-aware task graphs, define task boundaries and parallelization | Define task IDs, dependencies, parallelization points | Task Graph, Task artifacts | Embedded in plan generation or separate phase |
| **Implementation Planner** | Create scoped implementation plans with approach, tests, rollback notes | Define approach per task; cannot expand scope without re-approval | Implementation Plan | Scoped to approved task; cannot drift scope |
| **Executor** | Implement approved tasks, produce code changes and evidence | Execute within approved scope only | Code changes, test results, implementation artifacts | Cannot expand scope; must escalate to Architect if needed |
| **Reviewer** | Independent review of plans, implementations, designs, evidence | Approve or reject with findings; request changes | Review artifacts | Must not be executor; independent assessment |
| **Validator** | Final validation of behavior, contract compliance, user acceptance | Approve or reject with evidence | Validation artifacts | Must not be reviewer or executor; validates against original criteria |
| **Memory Manager** | Maintain durable context, supersession links, execution snapshots | Archive and preserve audit trail | Memory artifacts | Enables future workflows to resume from known state |
| **Runner** | Automated state enforcement, budget checking, sidecar validation, timeout handling | Enforce all state transitions, reject non-compliant artifacts, route failures | meta.json sidecars, state files | Reads sidecars only; does not parse artifact body; never writes pre-invocation sidecars |

## Workflow Phases (Detailed)

### Phase 1: Initiative (INITIATIVE_CREATED → INITIATIVE_APPROVED)
**Owner:** Architect  
**Agent:** Architect (initiates), Planner (inputs)  
**Input:** Scope statement, success criteria, stakeholder requirements, timeline, budget  
**Action:**
- Architect writes initiative artifact (01_initiative.template.md)
- Define scope boundaries, success criteria, constraints, timeline, failure modes
- Identify rollback strategy and risk mitigation
- Establish budget allocation and approval gates

**Output:** Initiative artifact with metadata, approved scope, success criteria  
**Sidecar:** meta.json with status=Draft → Approved  
**Next:** PLAN_CREATED

---

### Phase 2: Planning (INITIATIVE_APPROVED → PLAN_APPROVED)
**Owner:** Architect (gates), Planner (executes)  
**Agent:** Planner  
**Input:** Approved initiative (read-only context), current memory  
**Action:**
- Planner reads approved initiative
- Decompose work into phases, agents, milestones
- Define task boundaries, dependencies, parallelization points
- Identify review gates and validation checkpoints
- Estimate duration per phase and rollback strategy

**Output:** Plan artifact (02_plan.md), Task Graph artifact (02b_task_graph.md)  
**Sidecar:** meta.json with status=Draft → Reviewed → Approved  
**Next:** TASK_GRAPH_CREATED

---

### Phase 3: Task Decomposition (PLAN_APPROVED → TASK_GRAPH_APPROVED)
**Owner:** Task Decomposer, Reviewer  
**Agent:** Task Decomposer  
**Input:** Approved plan, approved initiative  
**Action:**
- Decompose work into dependency-aware task nodes
- Define task IDs, success criteria, dependencies
- Mark parallelization points (independent tasks)
- Link each task to plan phases

**Output:** Task Graph artifact with task nodes; Task artifacts (03_task.template.md) for each task  
**Sidecar:** meta.json for graph + all task artifacts with status=Draft → Reviewed → Approved  
**Next:** TASK_EXECUTION_STARTED

---

### Phase 4: Task Execution (TASK_GRAPH_APPROVED → all tasks Implemented)
**Owner:** Executor (per task), Task Decomposer (orchestration)  
**Agent:** Executor  
**Input:** Approved task graph, approved tasks, approved plan, approved initiative  
**Action (per task):**
- Executor claims task (Pending → In Progress)
- Read approved task artifact as read-only context
- Implement within approved scope only
- Run tests, produce artifacts
- Mark task Implemented
- Cannot expand scope; escalate to Architect if needed

**Parallelization:** Independent tasks (no upstream dependencies) can execute in parallel with isolated ownership.

**Output (per task):** Code changes, test results, artifacts; task artifact with Implementation section completed  
**Sidecar:** meta.json for each task with status=Pending → In Progress → Implemented  
**Next:** IMPLEMENTATION_REVIEW_STARTED

---

### Phase 5: Implementation Review (all tasks Implemented → Implementation Review Approved or Rejected)
**Owner:** Reviewer (independent of executor)  
**Agent:** Reviewer  
**Input:** All approved artifacts (initiative, plan, task graph, all implemented tasks, code changes)  
**Action:**
- Reviewer reads all approved artifacts as context
- Assess plan quality, task execution quality, code correctness
- Check for scope creep, compliance with task scope, test coverage
- Identify regressions, security issues, design issues
- Produce review findings (04_review.template.md)

**Output:** Review artifact with findings, recommendations, decision (Approved / Rejected / Changes Requested)  
**Sidecar:** meta.json with status=Draft → Final (contains decision)  
**Next:**
- If Approved: VALIDATION_STARTED
- If Rejected: return to TASK_EXECUTION_STARTED; executor addresses findings

---

### Phase 6: Validation (Implementation Review Approved → Validation Approved or Rejected)
**Owner:** Validator (independent of reviewer and executor)  
**Agent:** Validator  
**Input:** Approved initiative (success criteria), approved review, all approved artifacts  
**Action:**
- Validator reads initiative (success criteria) and approved review
- Validate behavior against original success criteria
- Perform user acceptance testing if applicable
- Check contract compliance (API contracts, data models, performance)
- Produce validation findings (05_validation.template.md)

**Output:** Validation artifact with test results, evidence, decision (Approved / Rejected)  
**Sidecar:** meta.json with status=Draft → Final (contains decision)  
**Next:**
- If Approved: COMPLETED
- If Rejected: return to TASK_EXECUTION_STARTED; executor addresses findings

---

### Phase 7: Completion (Validation Approved → COMPLETED)
**Owner:** Architect, Memory Manager  
**Agent:** Memory Manager (optional)  
**Input:** All approved artifacts, validation evidence  
**Action:**
- Archive initiative, plan, task graph, all tasks, reviews, validation
- Create supersession links if replacing prior work
- Update memory tree with execution snapshot
- Mark workflow COMPLETED in runner state
- Generate delivery summary (optional)

**Output:** Archived artifacts, Memory artifact (06_memory.template.md) with supersession links  
**Sidecar:** meta.json with status=Completed  
**Next:** Terminal state

## Standard Rules (Non-Negotiable)

### 1. Respect Current State
- Agents must read artifact status from meta.json sidecars, not from artifact body text
- Approved artifacts are read-only for downstream agents (context only)
- Draft artifacts can be modified by owning agent before approval
- If an artifact is Approved, downstream agents cannot modify or re-execute it

### 2. No Phase Skipping
- Phases must execute in order: Initiative → Plan → Task Graph → Task Execution → Review → Validation → Completion
- The runner will reject any artifact that violates phase order
- Approved upstream artifacts act as gates; downstream phases cannot begin until gates pass

### 3. No Overwriting Approved Artifacts
- Once Approved, an artifact cannot be modified
- If changes are needed, Architect initiates supersession:
  1. Create new artifact (e.g., PLAN_v2.md)
  2. New artifact references superseded artifact ID
  3. Mark old artifact as Superseded
  4. Only new artifact is used downstream
- This preserves audit trail and prevents loss of decisions

### 4. No Scope Drift
- Executors must respect approved task scope
- If scope cannot be met or must expand, escalate to Architect (not silent changes)
- Plan changes require Architect approval and task graph regeneration
- Reviewers can request scope corrections but cannot approve scope expansion

### 5. Deterministic Outputs
- Artifact IDs must be stable (e.g., PLAN-20260603-01, TASK-20260603-01)
- Hashes of generated artifacts must be reproducible (no random components)
- Task graph dependencies must be deterministic (no random ordering)
- Enables idempotent re-execution and verifiable audit trails

### 6. Single Source of Truth
- Artifact status is defined by meta.json sidecar, not artifact body text
- Workflow state is maintained by runner, not by artifacts
- Approval decisions are sidecar-only; no approval decisions in artifact body
- Prevents inconsistency and ensures unambiguous rule enforcement

### 7. Document-First Execution
- Before any work begins, create the required delivery artifact
- All work must have an approved artifact as the reference point
- No off-the-record work; all work is traceable to an approved artifact
- Code execution, tasks, and reviews all require approved artifacts

### 8. Budget and Timeout Enforcement
- Runner checks remaining budget before invoking any agent
- If insufficient budget, runner rejects invocation and routes to failure
- Each phase has a maximum duration (defined in runner config)
- If phase exceeds timeout, runner terminates agent and routes to failure

### 9. No Pre-Invocation Sidecars
- Runner never writes meta.json sidecars before agent invocation
- Agents are responsible for creating and writing sidecars
- This prevents side-channel communication and hidden state

## Sidecar Contract (meta.json)

**meta.json is the ONLY communication channel between agents and runner.**

Every generated artifact requires a matching meta.json sidecar with:
- **Schema:** `v2` (required)
- **Status:** `Draft | Reviewed | Approved | Final | Implemented | Completed | Superseded | Cancelled`
- **Decision:** Approval decision (true/false) for gates
- **Findings:** Structured review or validation findings (for review/validation phases)
- **Evidence:** File paths and checksums of supporting evidence
- **Recorded Timestamp:** ISO 8601 timestamp
- **Upstream References:** IDs of artifacts this depends on
- **Path:** `<artifact-basename>.meta.json` (same directory as artifact)

**Sidecar Structure (exact schema v2):**
```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "Draft | Reviewed | Approved | Final | Implemented | Completed",
    "decision": true | false,
    "remark": "Brief summary",
    "artifacts": {
      "artifact_name": "/path/to/file",
      ...
    },
    "findings": [...],
    "evidence": [...],
    "upstream_refs": [...],
    "recorded_at": "2026-06-03T10:30:00Z"
  }
}
```

**Phase Sidecars Required:**
- Initiative artifact: status=Draft → Approved
- Plan artifact: status=Draft → Reviewed → Approved
- Task Graph artifact: status=Draft → Reviewed → Approved
- Task artifact (per task): status=Pending → In Progress → Implemented → Approved
- Review artifact: status=Draft → Final (contains decision)
- Validation artifact: status=Draft → Final (contains decision)
- Memory artifact: status=Draft → Completed

**Runner Acceptance Criteria:**
- Schema must be v2
- All referenced files must exist
- Status must be valid for phase
- Decision must be present for approval gates
- Recordings must be immutable (once written, cannot be modified)
- Missing, malformed, or stale sidecars prevent runner acceptance

## Folder Structure (Standard `docs/delivery/`)

```
docs/delivery/
├── 00_templates/              (SOP, status rules, templates, registry)
│   ├── WORKFLOW_SOP_v1.md
│   ├── DELIVERY_STATUS_RULES_v1.md
│   ├── template_registry.md
│   ├── 01_initiative.template.md
│   ├── 02_plan.template.md
│   ├── 02b_task_graph.template.md
│   ├── 03_task.template.md
│   ├── 04_implementation_plan.template.md
│   ├── 04_review.template.md
│   ├── 05_validation.template.md
│   └── 06_memory.template.md
├── 08_agents/                 (Agent contracts; role boundaries only)
│   ├── AGENTS.md
│   ├── planner_contract.md
│   ├── executor_contract.md
│   ├── reviewer_contract.md
│   └── [other role contracts]
├── 01_initiatives/            (Initiative artifacts)
│   └── INIT-YYYYMMDD-NN_*.md
├── 02_plans/                  (Plan artifacts)
│   ├── PLAN-YYYYMMDD-NN_*.md
│   └── artifacts/
│       └── TASK-GRAPH-YYYYMMDD-*.md
├── 03_tasks/                  (Task artifacts)
│   └── TASK-YYYYMMDD-NN_*.md
├── 04_implementation/         (Implementation plans and records)
│   ├── IMPL-YYYYMMDD-NN_*.md
│   └── artifacts/
├── 05_reviews/                (Review and validation artifacts)
│   └── REVIEW-YYYYMMDD-NN_*.md
├── 06_memory/                 (Memory and execution snapshots)
│   └── MEMORY-YYYYMMDD-NN_*.md
└── [state files, run logs]
```

**Do not create 07_master_prompts/.** Agent master prompts are deprecated. Workflow step configurations in `template_groups.py` serve as agent invocation contracts.

---

## Parallel Execution (Advanced Feature)

For independent task-graph branches:
1. Runner checks dependencies; marks dependent tasks ready only after upstream tasks are Implemented
2. Parallel tasks execute with isolated ownership (each executor owns one task)
3. Shared resources (database, file system) must be coordinated via task dependencies
4. Each task has its own meta.json sidecar; parallel tasks do not require merging sidecars
5. All parallel tasks must pass review and validation gates independently (no merged reviews)
6. Workflow completion requires all in-scope tasks to be Approved

---

## Memory Management (Advanced Feature)

Memory artifacts (06_memory.template.md) preserve:
- **Execution snapshots:** Key decisions, constraints, risks identified during execution
- **Supersession links:** References to prior work being replaced or superseded
- **Durable context:** Information needed for future workflows to resume from known state
- **Audit trail:** Who did what, when, and why

Memory must be:
- **Compact:** Only essential information; not verbose logs
- **Linked:** References to upstream artifact IDs
- **Updated at handoffs:** At meaningful phase boundaries

Memory **informs** future work but **cannot override** runner state or approved artifacts.

---

## Validation Philosophy

Validation is **independent, structured, and mandatory** before completion.

**Independent:** Performed by an agent who is not the reviewer and not the executor (prevents bias, ensures objective assessment)

**Structured:** Uses predefined criteria from the original initiative (success criteria, acceptance tests, performance requirements, contract compliance)

**Mandatory:** Must complete before workflow can move to Completion. Cannot skip validation or mark workflow Completed if validation is Rejected.

**Evidence-Based:** Validator must provide evidence (test results, metrics, screenshots) to support approval or rejection.

---

## Error Handling and Exception Routing

**Hard Failures:** If an agent encounters an unrecoverable error (budget exhaustion, timeout, malformed output), the runner routes the workflow to `route_after_failure()` immediately. No recovery attempt.

**Soft Failures:** If an agent produces an artifact that fails validation checks (missing sections, invalid metadata), the runner rejects the artifact and requests a new submission.

**Deadlock:** If a workflow is blocked (e.g., conflicting review findings), the Architect is notified and decides to restart, supersede, or cancel.

---

## Backward Compatibility and Daemon Mode

**Direct Execution (v1 - Preserved):**
- CLI invocation without daemon
- Single-threaded synchronous execution
- Fully supported and unchanged

**Daemon Mode (Planned):**
- Asynchronous job queuing
- PostgreSQL-backed job management
- Multi-worker support with atomic job claiming (`SELECT ... FOR UPDATE SKIP LOCKED`)
- Does not change core SOP rules

**Resume Strategy (v1 Daemon - Conservative):**
- No automatic recovery of crashed workers
- Manual restart required after worker crash
- Preserves durability and simplicity for v1

---

## Governance and Change Control

**SOP Changes:** Require Architect approval; must document rationale and effective date

**Status Rule Changes:** Require Architect approval

**Template Changes:** Must be backward-compatible or include migration guidance for existing artifacts

**Agent Contract Changes:** Reviewed and approved by Architect

---

## Quick Reference

**Phase Order:** Initiative → Plan → Task Graph → Task Execution → Review → Validation → Completion

**Approval Authority:** Architect (init/plan/task-graph), Reviewer (implementation), Validator (final), Runner (state enforcement)

**Forbidden Actions:** Phase skipping, overwriting approved artifacts, self-approval, scope expansion without re-planning, pre-invocation sidecar writes

**Key Roles:** Planner, Task Decomposer, Implementation Planner, Executor, Reviewer, Validator, Memory Manager, Architect, Runner

**Document-First Rule:** All work must have an approved artifact as reference; no off-the-record work

**Sidecar Rule:** meta.json is the ONLY source of truth for artifact status and approval decisions; runner reads sidecars only, never parses artifact body

**Budget Rule:** Runner checks remaining budget before any agent invocation; insufficient budget triggers immediate failure routing

---

## Appendix: Related Documents

- **DELIVERY_STATUS_RULES_v1.md** — Artifact lifecycle, approval gates, forbidden transitions
- **template_registry.md** — Index of all delivery templates
- **08_agents/AGENTS.md** — Agent role definitions and contracts
- **pyproject.toml** — Runner configuration, model mappings, CLI entry points
- **template_groups.py** — Workflow step configurations (agent contracts for invocation)
