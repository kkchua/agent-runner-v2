---
title: Delivery Status Rules
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: generate_sop
created: 2026-07-04
version: 1
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_sop`
> This file is workflow-generated and protected from manual edits.

# Delivery Status Rules

## Core Principles

1. **Status is a state machine, not a label.** Every delivery artifact carries a status that reflects its position in the workflow lifecycle. Status transitions are governed by explicit rules — arbitrary status changes are forbidden.

2. **The sidecar is the source of truth.** The `meta.json` sidecar's `coder_result.status` field is the only authoritative status indicator. A document's internal claims about its own status are secondary to the sidecar.

3. **No forward transition without approval.** An artifact cannot advance to a later lifecycle phase unless the preceding phase has been approved via a valid sidecar with `status: APPROVED`.

4. **Traceability is mandatory.** Every status change must be attributable to a specific workflow step, agent role, and timestamp.

5. **Rejection is a controlled transition.** Rejected artifacts must be reworked, not deleted. The rejection reason must be recorded in the sidecar remark.

## Global Workflow Discipline

### Phase Ordering
Workflow phases MUST execute in the defined sequence:

```
20_initiative_intake_v1 → 30_delivery_planning_v1 → 31_task_execution_v1
```

Post-execution reconciliation and publication:

```
31_task_execution_v1 → 40_documentation_sync_v1 → 50_architecture_site_v1
```

### Concurrent Work
- Multiple tasks within a validated task graph MAY execute concurrently
- Multiple initiatives MUST NOT share a delivery plan — each initiative gets its own plan
- Documentation sync (`40_documentation_sync_v1`) MAY run independently of active deliveries

### Scope Boundaries
- A delivery plan addresses exactly one initiative
- A task graph belongs to exactly one delivery plan
- A task belongs to exactly one task graph
- Cross-delivery task dependencies are forbidden — split into separate deliveries

## Lifecycle Rules

### Initiative Lifecycle

```
intake_draft → intake_active → intake_approved
```

- `intake_draft`: Initiative is being authored; not yet submitted for review
- `intake_active`: Initiative is under review
- `intake_approved`: Initiative scope, documentation scope, and stale-guidance risk have been assessed and accepted

### Plan Lifecycle

```
plan_draft → plan_active → plan_approved
```

- `plan_draft`: Plan is being authored
- `plan_active`: Plan is under review; documentation obligations are being validated
- `plan_approved`: Plan is accepted; task decomposition may begin

### Task Graph Lifecycle

```
task_graph_draft → task_graph_ready → task_graph_validated
```

- `task_graph_draft`: Tasks are being defined with dependencies
- `task_graph_ready`: All tasks have implementation plans; dependencies validated
- `task_graph_validated`: Task graph passes structural validation; execution may begin

### Task Lifecycle

```
task_pending → task_implementing → task_reviewing → task_validating → task_completed
```

- `task_pending`: Task is queued for implementation
- `task_implementing`: Executor is actively implementing the task
- `task_reviewing`: Reviewer is examining implementation and documentation updates
- `task_validating`: Validator is confirming task completion criteria are met
- `task_completed`: Task is fully done; artifacts and documentation are finalized

### Delivery Lifecycle

```
draft → active → planned → task_graph_ready → task_graph_validated → executing → completed
```

- `draft`: Delivery is initialized
- `active`: Initiative is approved; planning begins
- `planned`: Plan is approved
- `task_graph_ready`: Task graph is ready
- `task_graph_validated`: Task graph is validated
- `executing`: At least one task is in implementation
- `completed`: All tasks completed; delivery review passed

## Authority Model

### Document Authority Hierarchy

1. `meta.json` sidecar (v2 schema)
2. `WORKFLOW_SOP_v1.md` (this SOP)
3. `DELIVERY_STATUS_RULES_v1.md` (this document)
4. Workflow templates
5. Agent role contracts
6. Repository-specific conventions
7. Informal notes (non-authoritative)

### Agent Authority

| Agent | Can Approve | Can Reject | Can Escalate |
|---|---|---|---|
| Planner | Initiative, Plan | Initiative, Plan | Yes |
| Task Decomposer | Task Graph | Task Graph | Yes |
| Impl Planner | Implementation Plan | Implementation Plan | Yes |
| Executor | — | — | Yes |
| Reviewer | Task, Delivery | Task, Delivery | Yes |
| Memory Manager | — | — | Yes |

## Approval Gates

### Initiative Approval Gate
- **Required before**: `30_delivery_planning_v1` begins
- **Criteria**: Initiative document has valid sidecar with `status: APPROVED`; documentation scope and stale-guidance risk are captured
- **Approver**: Planner agent

### Plan Approval Gate
- **Required before**: Task decomposition begins
- **Criteria**: Plan document has valid sidecar with `status: APPROVED`; documentation obligations are defined per task
- **Approver**: Planner agent

### Task Graph Validation Gate
- **Required before**: Task execution begins
- **Criteria**: Task graph has valid sidecar with `status: APPROVED`; all dependencies are acyclic; all tasks have implementation plans
- **Approver**: Task Decomposer + Reviewer

### Task Completion Gate
- **Required before**: Task advances to `task_completed`
- **Criteria**: Implementation passes review; codebase documentation is updated; sidecar is valid
- **Approver**: Reviewer

### Delivery Completion Gate
- **Required before**: Delivery advances to `completed`
- **Criteria**: All tasks in `task_completed`; `validate_codebase_docs` passes; no stale documentation in touched modules
- **Approver**: Reviewer

## Forbidden Transitions

The following transitions are **explicitly forbidden**:

1. **Skipping phases**: `intake_draft → plan_draft` (initiative must be approved first)
2. **Backward status change**: `task_completed → task_implementing` (completed is terminal)
3. **Status without sidecar**: Any status change without a corresponding `meta.json` update
4. **Parallel plan authoring**: Two plans for the same initiative simultaneously
5. **Cross-delivery tasks**: A task belonging to multiple task graphs
6. **Manual override**: Changing status outside of workflow step execution
7. **Deletion of rejected artifacts**: Rejected artifacts must be reworked, not deleted
8. **Advancing on rejected sidecar**: No phase advances when the preceding sidecar has `status: REJECTED`
9. **Unvalidated task graph execution**: Tasks cannot begin implementation until the task graph is validated
10. **Documentation skip**: Task completion without corresponding codebase documentation update

## Document-First Rule

All delivery decisions, plans, and outcomes MUST be recorded as markdown documents before execution begins. Implementation without a preceding document is forbidden.

### Document-First Enforcement
- No code changes without an approved implementation plan
- No task decomposition without an approved delivery plan
- No initiative execution without an approved initiative document
- Documentation updates are part of the task, not a follow-up

### Exception
Emergency hotfixes MAY proceed with reduced documentation, but MUST be retroactively documented within the same delivery cycle. The exception must be recorded in the sidecar remark.

## Traceability

### Required Traceability Links
- Every plan MUST reference its source initiative
- Every task graph MUST reference its source plan
- Every task MUST reference its source task graph
- Every implementation MUST reference its source task
- Every review MUST reference the artifacts it reviewed
- Every validation MUST reference the criteria it validated

### Sidecar Traceability
- `coder_result.status` — outcome of the step
- `coder_result.remark` — human-readable summary
- `coder_result.artifacts` — exact paths of generated documents
- `coder_result.recorded_at` — ISO 8601 timestamp

### Decision Recording
- The Memory Manager records all significant decisions in workflow memory
- Rejection reasons MUST be preserved across rework cycles
- Escalation decisions MUST include the reason and the escalation target
