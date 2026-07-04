---
title: Delivery Workflow SOP
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: generate_sop
created: 2026-07-04
version: 1
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_sop`
> This file is workflow-generated and protected from manual edits.

# Delivery Workflow SOP

## Purpose

This Standard Operating Procedure defines the end-to-end delivery workflow for governed repositories managed by `10_execution_scaffold_v1`. It covers the complete lifecycle from initiative intake through planning, task decomposition, implementation, review, validation, and completion.

The delivery SOP establishes:
- The authoritative sequence of workflow phases
- Agent roles and responsibilities at each phase
- State transitions and approval gates
- Folder structure and artifact routing
- Validation contracts that must be satisfied before advancement

This SOP applies universally to every repository governed by the scaffold. Repository-specific profiles (DDD, EDA, microservices, etc.) refine but do not replace this baseline.

## Core Principle

**Document-first, sidecar-gated, workflow-protected.**

Every delivery decision, plan, task, and outcome is recorded as a protected markdown document with a `meta.json` sidecar. No phase advances without a valid sidecar. No sidecar is valid without the required artifacts. No manual edits override workflow-generated content.

The delivery workflow is a **state machine**, not a checklist. Each phase has defined entry criteria, exit criteria, and transition rules. Skipping or reordering phases invalidates the delivery.

## Authority Precedence

When conflicts arise between documents, the following precedence applies (highest first):

1. **`meta.json` sidecar** (v2 schema) — the runtime source of truth for step outcomes
2. **This SOP** (`WORKFLOW_SOP_v1.md`) — the workflow contract
3. **`DELIVERY_STATUS_RULES_v1.md`** — lifecycle and transition rules
4. **Workflow templates** (initiative, plan, task graph, task, impl, review, validation, memory)
5. **Agent role contracts** (planner, task-decomposer, impl-planner, executor, reviewer, memory-manager)
6. **Repository-specific conventions** (when documented and approved)
7. **Ad-hoc notes or comments** — never authoritative

## Workflow State Machine

The primary delivery lifecycle follows this state transition sequence:

```
draft → active → planned → task_graph_ready → task_graph_validated → executing → completed
```

Detailed phase transitions:

```
intake_draft → intake_active → intake_approved
    → plan_draft → plan_active → plan_approved
    → task_graph_draft → task_graph_ready → task_graph_validated
    → task_pending → task_implementing → task_reviewing → task_validating → task_completed
    → delivery_reviewing → delivery_validating → delivery_completed
```

Failure and recovery transitions:

```
any_phase → rejected → (rework) → active
any_phase → failed → (diagnosis) → active | escalated
task_implementing → blocked → (unblocked) → task_implementing
```

### State Transition Rules

| From | To | Condition |
|---|---|---|
| `draft` | `active` | Initiative or plan is opened for work |
| `active` | `planned` | Plan document emitted with valid sidecar |
| `planned` | `task_graph_ready` | Task graph emitted with valid sidecar |
| `task_graph_ready` | `task_graph_validated` | Task graph passes validation action |
| `task_graph_validated` | `executing` | First task begins implementation |
| `executing` | `completed` | All tasks validated; delivery review passed |
| any | `rejected` | Reviewer or validator rejects; rework required |
| any | `failed` | Unrecoverable error; escalation required |

## Agent Roles

| Role | Phase | Responsibility |
|---|---|---|
| **Planner** | `20_initiative_intake_v1`, `30_delivery_planning_v1` | Captures initiative scope, documentation obligations, and delivery plan. Converts initiative intake into a structured plan with task obligations. |
| **Task Decomposer** | `30_delivery_planning_v1` | Breaks the plan into a task graph with dependencies, documentation update obligations per task, and validation criteria. |
| **Impl Planner** | `31_task_execution_v1` | Produces per-task implementation plans with codebase-doc impact analysis. |
| **Executor** | `31_task_execution_v1` | Runs coder adapters, writes code and documentation artifacts, updates codebase docs alongside code changes. |
| **Reviewer** | `31_task_execution_v1` | Enforces sidecar contract, doc freshness, status rules, and template compliance. |
| **Memory Manager** | All phases | Maintains workflow memory, decision history, and cross-delivery context. |

## Workflow Phases

### Phase 1: Initiative Intake (`20_initiative_intake_v1`)

**Entry**: Initiative request received (user prompt, ticket, or directive).

**Actions**:
1. Parse initiative scope — what changes, what documentation is affected
2. Capture documentation scope — which codebase docs need creation or update
3. Assess stale-guidance risk — identify existing docs that may become stale
4. Produce initiative document with approved sidecar

**Exit**: Initiative document in `intake_approved` state with valid sidecar.

### Phase 2: Delivery Planning (`30_delivery_planning_v1`)

**Entry**: Approved initiative document.

**Actions**:
1. Convert documentation scope into plan-level obligations
2. Define task boundaries with documentation deliverables per task
3. Generate delivery plan document with approved sidecar
4. Generate task graph document with validated sidecar

**Exit**: Plan and task graph both approved with valid sidecars.

### Phase 3: Task Execution (`31_task_execution_v1`)

**Entry**: Validated task graph.

**Actions** (per task):
1. Generate implementation plan (impl planner)
2. Execute code changes (executor)
3. Update codebase documentation alongside code (executor)
4. Review implementation and doc updates (reviewer)
5. Validate task completion including doc freshness (reviewer)

**Exit**: All tasks in `task_completed` state; delivery review passed.

### Phase 4: Documentation Sync (`40_documentation_sync_v1`)

**Entry**: Triggered on-demand or after task execution completes.

**Actions**:
1. Reconcile current code against active documentation
2. Flag stale guidance — documents that no longer match code behavior
3. Generate reconciliation report
4. Queue documentation repair tasks if stale content found

**Exit**: Documentation freshness confirmed or repair tasks queued.

### Phase 5: Architecture Communication (`50_architecture_site_v1`)

**Entry**: Repository posture and docs are synchronized.

**Actions**:
1. Publish browsable HTML architecture views
2. Generate stakeholder, developer, operator, and functional consumer views
3. Validate site renders correctly

**Exit**: Architecture site published and validated.

## Standard Rules

### Sidecar Contract
- Every workflow step MUST produce a `meta.json` sidecar conforming to v2 schema
- The sidecar MUST include `schema_version`, `coder_result.status`, `coder_result.artifacts`, and `coder_result.recorded_at`
- Status MUST be `APPROVED` or `REJECTED` — no other values accepted
- Artifacts MUST list all generated documents with their exact paths

### Document Protection
- Workflow-generated documents carry the `managed_by: workflow-generated` frontmatter field
- Protected documents display the workflow banner immediately after frontmatter
- Manual edits to protected documents are forbidden
- Renaming protected documents is forbidden

### Approval Gates
- No phase advances without a valid sidecar with `status: APPROVED`
- Rejected steps must be reworked and resubmitted
- Failed steps require diagnosis before retry

### Freshness Enforcement
- Codebase documentation MUST be updated in the same delivery as the code change
- Stale documentation blocks delivery advancement
- The `validate_codebase_docs` action enforces freshness at review time

## Folder Structure

```
docs/
├── codebase/
│   ├── 00_standards/          # SOPs and status rules
│   ├── 01_inventory/          # Project analysis and codebase inventory
│   ├── 02_modules/            # Module-level documentation
│   ├── 03_components/         # Component groupings
│   └── 04_changes/            # Change-impact records
├── system/
│   ├── 00_governance/
│   │   └── bootstrap/         # Delivery SOPs, status rules, templates, agent contracts
│   └── 02_architecture_site/  # Published architecture views
└── delivery/                  # Active delivery artifacts (initiatives, plans, tasks)
```

## Validation

### Pre-Delivery Validation
- Initiative document exists and is approved
- Plan document exists and is approved
- Task graph exists and is validated
- All sidecars conform to v2 schema

### In-Delivery Validation
- Each task has a valid implementation plan
- Code changes have corresponding documentation updates
- Reviewer has signed off on each task
- Sidecar artifacts match actual files on disk

### Post-Delivery Validation
- All tasks in `completed` state
- No stale documentation in touched modules
- `validate_codebase_docs` passes
- Memory manager has recorded delivery summary
