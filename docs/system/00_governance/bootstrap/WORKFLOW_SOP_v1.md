---
title: "Delivery Workflow SOP v1"
template_id: "WORKFLOW-SOP-v1"
status: "active"
version: "1.0"
generated: "2026-07-04T07:00:00+08:00"
workflow: "10_execution_scaffold_v1"
step: "generate_sop"
managed_by: workflow-generated
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_sop`
> This file is workflow-generated and protected from manual edits.

# Delivery Workflow SOP v1

## Purpose

This Standard Operating Procedure defines the end-to-end delivery lifecycle for every repository governed by the UKBE runner. It governs how initiatives are captured, planned, decomposed, executed, reviewed, validated, and remembered through the structured workflow families:

- `20_initiative_intake_v1` — requirement capture and pre-init refinement
- `30_delivery_planning_v1` — plan creation, task-graph decomposition, task decomposition
- `31_task_execution_v1` — implementation, review, validation, documentation sync
- `40_documentation_sync_v1` — current-truth reconciliation of code against documentation

All delivery activity flows through these workflows under deterministic governance rules. No delivery artifact may exist outside this SOP's state machine.

This SOP applies to every governed repository regardless of the repository's selected architecture profile or migration mode. Architecture profiles and migration modes refine the baseline defined here; they do not replace it.

## Core Principle

**Every delivery unit follows the same lifecycle.** Whether it is a bug fix, a feature, a refactor, or a documentation sync, every unit passes through initiative intake, planning, task decomposition, execution, review, validation, and memory recording. The workflows enforce this sequence; the state machine prevents shortcuts.

Three corollaries:

1. **Document-first.** Documents precede code. Requirements, plans, and task specs are written before implementation begins.
2. **Sidecar-verified.** Every workflow step produces a `meta.json` sidecar. The sidecar is the only structured output channel between coder steps and the runner.
3. **Never-delete.** Superseded artifacts are marked `superseded` with a pointer to the replacement. No delivery artifact is ever deleted.

## Authority Precedence

When conflicts arise between governance artifacts, this order determines which takes priority:

1. **Runner actions** (deterministic validation steps, e.g., `validate_delivery_docs`, `validate_system_docs`) — these are ground truth.
2. **This SOP** (`WORKFLOW_SOP_v1.md`) — structural rules, state machine, roles.
3. **Status Rules** (`DELIVERY_STATUS_RULES_v1.md`) — lifecycle state definitions, forbidden transitions.
4. **Codebase SOP** (`CODEBASE_DOC_SOP_v1.md`) and **Codebase Status Rules** (`CODEBASE_DOC_STATUS_RULES_v1.md`) — codebase documentation obligations.
5. **Template Registry** (`templates/delivery/01_delivery_template_registry.md`) — artifact format contracts.
6. **Agent Contracts** (`docs/delivery/00_standards/DELIVERY_AGENT_*.md`) — role-specific behavior rules.
7. **Project Analysis** (`docs/delivery/project_analysis.md`) — repo-specific scope and recommendations.

A lower-precedence artifact may never contradict a higher-precedence one. When a contradiction is detected, the higher-precedence rule wins and the lower artifact must be corrected.

The `07_master_prompts` directory is **deprecated** and must not appear in any governance reference, template, or SOP.

## Workflow State Machine

### Primary Lifecycle (Arrow Form)

```
draft → active → planned → executing → completed
```

### Detailed Lifecycle (Arrow Form)

```
draft → active → task_graph_ready → task_graph_validated → executing → completed
```

### Per-Entity State Machines (Arrow Form)

**Initiative lifecycle:**

```
draft → active → planned → executing → completed
draft → superseded
active → superseded
planned → superseded
executing → superseded
```

**Plan lifecycle:**

```
draft → active → task_graph_ready → task_graph_validated → executing → completed
draft → superseded
active → superseded
task_graph_ready → superseded
task_graph_validated → superseded
executing → superseded
```

**Task lifecycle:**

```
draft → active → implementing → reviewing → validating → completed
reviewing → rework → reviewing → validating → completed
draft → superseded
active → superseded
implementing → superseded
reviewing → superseded
rework → superseded
validating → superseded
```

**Implementation lifecycle:**

```
draft → active → reviewing → validating → completed
reviewing → rework → reviewing → validating → completed
draft → superseded
active → superseded
reviewing → superseded
rework → superseded
validating → superseded
```

**Documentation sync lifecycle:**

```
scanning → analyzing → flagging → completed
scanning → completed
analyzing → completed
any_state → completed (early termination)
```

### State Transition Summary Tables

#### Initiative States

| State | Description | Valid Transitions |
|-------|-------------|-------------------|
| `draft` | Intake in progress | `active`, `superseded` |
| `active` | Approved, awaiting planning | `planned`, `superseded` |
| `planned` | Plan approved, task-graph in progress | `executing`, `superseded` |
| `executing` | Tasks being executed | `completed`, `superseded` |
| `completed` | All tasks done, validated | Terminal |
| `superseded` | Replaced by a newer initiative | Terminal |

#### Plan States

| State | Description | Valid Transitions |
|-------|-------------|-------------------|
| `draft` | Plan in progress | `active`, `superseded` |
| `active` | Approved, awaiting decomposition | `task_graph_ready`, `superseded` |
| `task_graph_ready` | Task-graph decomposition complete | `task_graph_validated`, `superseded` |
| `task_graph_validated` | Task-graph validated, ready for execution | `executing`, `superseded` |
| `executing` | Tasks being executed | `completed`, `superseded` |
| `completed` | All tasks done, validated | Terminal |
| `superseded` | Replaced by a newer plan | Terminal |

#### Task States

| State | Description | Valid Transitions |
|-------|-------------|-------------------|
| `draft` | Task spec in progress | `active`, `superseded` |
| `active` | Task approved, awaiting implementation | `implementing`, `superseded` |
| `implementing` | Implementation in progress | `reviewing`, `superseded` |
| `reviewing` | Review in progress | `rework`, `validating`, `superseded` |
| `rework` | Fixing issues from review | `reviewing`, `superseded` |
| `validating` | Validation in progress | `completed`, `superseded` |
| `completed` | Implementation reviewed and validated | Terminal |
| `superseded` | Replaced by a newer task | Terminal |

#### Documentation Sync States

| State | Description | Valid Transitions |
|-------|-------------|-------------------|
| `scanning` | Scanning codebase for drift | `analyzing`, `completed` |
| `analyzing` | Analyzing identified drift | `flagging`, `completed` |
| `flagging` | Flagging stale documentation | `completed` |
| `completed` | Sync complete, stale guidance recorded | Terminal |

## Agent Roles

| Role | Responsibility | Assigned Workflow Phases |
|------|---------------|-------------------------|
| **Planner** | Scopes initiative, produces plan with solution strategy | `20_initiative_intake_v1`, `30_delivery_planning_v1` |
| **Task Decomposer** | Converts plan into task-graph, then decomposes into task specs | `30_delivery_planning_v1` |
| **Impl Planner** | Produces implementation plan for each task | `31_task_execution_v1` |
| **Executor** | Implements solution, produces deliverables, writes docs | `31_task_execution_v1` |
| **Reviewer** | Reviews implementation against task spec and acceptance criteria | `31_task_execution_v1` |
| **Memory Manager** | Records delivery memory, maintains governance artifacts | `31_task_execution_v1`, `40_documentation_sync_v1` |

Each agent operates within its authority boundary. No agent may override another agent's artifacts without going through the review loop.

## Workflow Phases

### Phase 1: Initiative Intake (`20_initiative_intake_v1`)

**Purpose**: Capture the requirement, scope documentation obligations, identify stale-guidance risks.

1. Capture the requirement (problem statement, context, constraints).
2. Identify **documentation scope** — which codebase modules, components, or configurations will be affected?
3. **Flag stale-guidance risk** for any existing docs that reference the affected area.
4. Produce the initiative document at `docs/delivery/01_initiatives/`.
5. Route to approval gate. On approval, status moves `draft → active`.

The initiative document must include a **Documentation Scope** section listing all affected doc files and their stale-guidance risk level.

### Phase 2: Delivery Planning (`30_delivery_planning_v1`)

**Purpose**: Convert documentation scope and initiative into plan, task-graph, and per-task implementation plans.

1. Convert initiative into a plan with solution strategy, scope, and risk assessment.
2. Produce the plan document at `docs/delivery/02_plans/`.
3. Decompose plan into a task-graph (ordered dependencies, parallel tracks).
4. Decompose each graph node into a task spec with acceptance criteria.
5. **Convert documentation scope into concrete plan/task obligations** — each task that touches code must have a corresponding doc-update subtask.
6. Produce task documents at `docs/delivery/03_tasks/`.
7. Route to approval gate. On approval, status moves `task_graph_ready → task_graph_validated`.

### Phase 3: Task Execution (`31_task_execution_v1`)

**Purpose**: Execute each task, review the implementation, validate, and update codebase documentation.

1. For each task: produce an implementation plan at `docs/delivery/04_implementation_plans/`.
2. Executor implements the solution.
3. **Executor updates all codebase documentation** identified in the documentation scope.
4. Reviewer reviews implementation against task spec and acceptance criteria.
5. If issues found, executor reworks and reviewer re-reviews (max 2 refine loops).
6. Validator validates deliverables against acceptance criteria, including documentation accuracy.
7. If validation fails, executor reworks (max 1 replan loop).
8. On validation pass, task status moves `validating → completed`.
9. Memory Manager records delivery memory at `docs/delivery/06_memory/`.

### Phase 4: Documentation Sync (`40_documentation_sync_v1`)

**Purpose**: Reconcile current code against active documentation and flag stale guidance.

**`40_documentation_sync_v1` is the single current-truth synchronization workflow.** It reconciles the actual codebase state against all active documentation (system docs, codebase module docs, component docs, agent contracts, templates).

1. **Scan** — walks all source files and compares against the inventory.
2. **Detect** — identifies missing docs (new files without docs), orphaned docs (docs for deleted files), and stale docs (docs that don't match current source).
3. **Report** — produces a drift report listing all discrepancies with severity levels.
4. **Flag** — updates inventory entries to `stale_pending` for docs that need correction.

After the sync completes:

- If the drift report shows **critical stale guidance** (active misdirection), create an emergency correction task.
- If the drift report shows **high/medium/low staleness**, create a delivery initiative to batch-correct the flagged docs.
- If system docs (`docs/system/`) or operations guidance (`docs/delivery/`) are stale because the runner behavior or agent contracts changed, run `10_execution_scaffold_v1` again to refresh them.

## Standard Rules

1. **No artifact without a parent.** Every initiative, plan, task, and implementation must reference its parent in the hierarchy.
2. **No execution without a validated task spec.** Executors must only implement against an approved, validated task document.
3. **No task completion without documentation updates.** Code changes that are not accompanied by corresponding documentation updates are not considered complete.
4. **No state transition without evidence.** Every state change must be backed by a completed workflow phase with `meta.json` sidecar validation.
5. **Review loops are bounded.** Refine loops cap at 2 iterations. Replan loops cap at 1 iteration. Exceeding the cap escalates to human review.
6. **Supersession over deletion.** When an artifact is replaced, the old version is marked `superseded` with a pointer to the replacement. No artifact is ever deleted.
7. **Memory is mandatory.** Every completed delivery unit produces a memory record.
8. **Stale guidance must be flagged.** When documentation cannot be updated in the current delivery cycle, it must be flagged in the memory record.
9. **Single current-truth workflow.** `40_documentation_sync_v1` is the single workflow for reconciling documentation against actual code state. No other workflow may perform current-truth synchronization.
10. **Deprecated directory.** The `07_master_prompts` directory is deprecated. It must not appear in any governance reference, template, or SOP.

## Ecosystem Baseline

The delivery lifecycle defined in this SOP rests on a universal ecosystem baseline that applies to every repository governed by the runner. Repo-level profiles and migration modes layer on top of this baseline — they refine it; they do not replace it.

### Universal Baseline

The following rules apply to every governed repository, regardless of domain, size, or technology:

1. **Sequential delivery lifecycle.** Every unit of work passes through initiative intake → delivery planning → task execution → documentation sync. No shortcuts.
2. **Sidecar-based result tracking.** Every workflow step produces a `meta.json` sidecar. The sidecar is the only structured communication channel between coder steps and the runner.
3. **Document-first delivery.** Documents precede code. Requirements, plans, and task specs are written before implementation begins.
4. **Documentation co-change.** Any source code change requires corresponding documentation updates in the same delivery task.
5. **Supersession over deletion.** No delivery artifact is ever deleted. Replaced artifacts are marked `superseded` with a pointer to the replacement.
6. **Bounded review loops.** Refine loops cap at 2 iterations; replan loops cap at 1. Exceeding the cap escalates to human review.
7. **Inventory completeness.** Every source file appears in the codebase inventory with an explicit status.
8. **Freshness discipline.** Documentation stale beyond 30 days is flagged. Critical misdirection triggers emergency correction.

### Repo-Selected Architecture Profile

Repositories may select an architecture profile that extends the universal baseline with domain-specific standards. Profile selection is a **repo-level decision** made during onboarding and recorded in the project analysis document.

Available profiles (non-exhaustive):

| Profile | Description | Additional Requirements |
|---------|-------------|------------------------|
| **none** (default) | No architecture profile. Universal baseline only. | — |
| **ddd** | Domain-Driven Design conventions | Aggregate boundaries documented; bounded contexts mapped; ubiquitous vocabulary maintained |
| **eda** | Event-Driven Architecture conventions | Event schema registry maintained; producer/consumer contracts versioned; event lifecycle documented |
| **layered** | Traditional layered architecture | Layer dependency rules enforced; cross-layer calls via interfaces only |
| **clean** | Clean/Hexagonal architecture | Domain layer isolated; adapters documented; dependency rule enforced |

**Important:** DDD, EDA, and similar architecture standards are **conditional profile choices**, not universal defaults. A repository without an explicit profile selection operates on the universal baseline alone. Profile-specific requirements are enforced by the reviewer during task validation only when the profile is explicitly selected.

### Migration Mode

Repositories may also declare a migration mode that affects how the delivery lifecycle operates during transitional periods:

| Mode | Description | Effect on Lifecycle |
|------|-------------|--------------------|
| **none** (default) | No active migration. Standard lifecycle applies. | — |
| **bootstrap** | Initial onboarding from legacy state | First pass generates all docs; subsequent passes follow standard lifecycle |
| **format-migration** | Workflow bundle format upgrade in progress | `sync_system_docs` action runs after every delivery task until migration complete |
| **docs-reconciliation** | Large-scale documentation remediation | `40_documentation_sync_v1` runs continuously until drift report shows zero critical/high items |

Migration mode is set in the project analysis and cleared when migration objectives are met.

### Conditional Standards

The following standards are **not** part of the universal baseline. They apply only when explicitly selected via architecture profile, migration mode, or repo-specific governance extension:

- Aggregate boundary enforcement (DDD profile only)
- Event schema registry maintenance (EDA profile only)
- Layer dependency enforcement (layered profile only)
- Hexagonal adapter contracts (clean profile only)
- Continuous sync reconciliation (docs-reconciliation migration mode only)
- Post-delivery bootstrap sync (bootstrap migration mode only)

Repo-specific governance extensions must be documented in the project analysis and approved through the same authority precedence chain as this SOP.

## Folder Structure

All delivery artifacts reside under `docs/delivery/`:

```
docs/delivery/
  00_standards/          # Governance SOPs, status rules, agent contracts
    AGENTS.md                  (agent registry)
    DELIVERY_AGENT_PLANNER.md
    DELIVERY_AGENT_TASK_DECOMPOSER.md
    DELIVERY_AGENT_IMPL_PLANNER.md
    DELIVERY_AGENT_EXECUTOR.md
    DELIVERY_AGENT_REVIEWER.md
    DELIVERY_AGENT_MEMORY_MANAGER.md
  01_initiatives/        # Initiative documents
  02_plans/              # Delivery plan documents
  03_tasks/              # Task specification documents
  04_implementation_plans/ # Implementation plan documents
  05_reviews/            # Review records with meta.json sidecars
  06_memory/             # Delivery memory records
  DELIVERY_FOLDER_MAP.json
  project_analysis.md    # Project-specific analysis (input to scaffold)
```

All governance SOPs and status rules reside under `docs/system/00_governance/bootstrap/`:

```
docs/system/00_governance/bootstrap/
  WORKFLOW_SOP_v1.md           (this file)
  DELIVERY_STATUS_RULES_v1.md
  EXISTING_REPO_WORKFLOW_SOP.md
```

All codebase documentation standards reside under `docs/codebase/00_standards/`:

```
docs/codebase/00_standards/
  CODEBASE_DOC_SOP_v1.md
  CODEBASE_DOC_STATUS_RULES_v1.md
```

All governance templates reside under `docs/system/00_governance/bootstrap/templates/`:

```
docs/system/00_governance/bootstrap/templates/
  delivery/              # Delivery artifact templates
    01_delivery_template_registry.md
    02_delivery_initiative_template.md
    03_delivery_plan_template.md
    04_delivery_task_graph_template.md
    05_delivery_task_template.md
    06_delivery_impl_template.md
    07_delivery_review_template.md
    08_delivery_validation_template.md
    09_delivery_memory_template.md
  codebase/              # Codebase artifact templates
    01_codebase_template_registry.md
    02_codebase_inventory_template.md
    03_codebase_module_template.md
    04_codebase_component_template.md
    05_codebase_change_template.md
```

## Validation

All delivery artifacts are validated at two levels:

### Structural Validation (Deterministic)

- File exists in the correct directory.
- Filename matches the template ID convention.
- Frontmatter contains all required fields (`title`, `status`, `workflow`, `step`).
- The `managed_by` field is present for workflow-generated files.

### Content Validation (LLM-Driven)

- All required sections are present per the template.
- Cross-references between artifacts are valid (initiative references plan, plan references tasks, etc.).
- Acceptance criteria are testable (not vague).
- Documentation scope covers all affected modules and components.

### Validation Gates

| Gate | Workflow Phase | Method | Pass Criteria |
|------|---------------|--------|---------------|
| Initiative validation | `20_initiative_intake_v1` | Runner action | Required sections present, documentation scope defined |
| Plan validation | `30_delivery_planning_v1` | Runner action | Plan references valid initiative, task graph has dependencies |
| Task graph validation | `30_delivery_planning_v1` | `validate_delivery_docs` | All tasks have acceptance criteria, no circular dependencies |
| Implementation validation | `31_task_execution_v1` | `validate_delivery_docs` | Impl plan references valid task, code changes present |
| Review validation | `31_task_execution_v1` | `validate_delivery_docs` | Review references valid implementation, verdict is explicit |
| Documentation sync validation | `40_documentation_sync_v1` | `validate_delivery_docs` | Drift report produced, reconciliation actions defined |

### Sidecar Validation

Each workflow step produces a `meta.json` sidecar in the job directory. The sidecar must contain:

```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED" | "REJECTED",
    "remark": "<summary>",
    "artifacts": { ... },
    "recorded_at": "<ISO-8601>"
  }
}
```

A step's output is only considered complete when its sidecar reports `APPROVED`.
