---
title: "Delivery Status Rules v1"
template_id: "DELIVERY-STATUS-RULES-v1"
status: "active"
version: "1.0"
generated: "2026-07-04T07:00:00+08:00"
workflow: "10_execution_scaffold_v1"
step: "generate_sop"
managed_by: workflow-generated
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_sop`
> This file is workflow-generated and protected from manual edits.

# Delivery Status Rules v1

## Core Principles

1. **Every artifact has exactly one status at any time.** No artifact may exist without a status, and no artifact may hold multiple statuses simultaneously.
2. **Status transitions are deterministic.** Only explicitly allowed transitions may occur. All others are forbidden by default.
3. **Status reflects reality, not intent.** An artifact's status must match its actual state in the world, not the desired or planned state.
4. **Evidence gates transitions.** No status change occurs without completed workflow phase output validated by a `meta.json` sidecar.
5. **Terminal states are final.** Once an artifact reaches `completed` or `superseded`, it cannot transition to any other state.

## Global Workflow Discipline

| Rule | Description |
|------|-------------|
| **Sequential enforcement** | Phases execute in order: `20_initiative_intake_v1` → `30_delivery_planning_v1` → `31_task_execution_v1` → `40_documentation_sync_v1`. Parallel execution is only allowed for independent tasks within a validated task-graph. |
| **No skip-rule** | No phase may be skipped. Every initiative must pass through all four workflow families. |
| **No rollback-rule** | Once a phase completes and its sidecar reports `APPROVED`, the phase output is immutable. Corrections happen via new initiatives, not by editing completed phase output. |
| **Sidecar required** | Every phase completion must produce a valid `meta.json` sidecar. No sidecar = phase not complete. |
| **Bounded loops** | Refine loops: max 2. Replan loops: max 1. Exceeding the cap escalates to human intervention. |
| **Single current-truth** | `40_documentation_sync_v1` is the single workflow for reconciling documentation against actual code state. |

## Lifecycle Rules

### Initiative Lifecycle

| From | To | Condition |
|------|----|-----------|
| _(none)_ | `draft` | Created by `20_initiative_intake_v1` step |
| `draft` | `active` | Initiative approved by review gate |
| `active` | `planned` | `30_delivery_planning_v1` produces an approved plan |
| `planned` | `executing` | Task decomposition complete, execution begins |
| `executing` | `completed` | All tasks validated and completed |
| any non-terminal | `superseded` | A newer initiative replaces this one |

Arrow form: `draft → active → planned → executing → completed`
Arrow form (supersession): `any non-terminal → superseded`

### Plan Lifecycle

| From | To | Condition |
|------|----|-----------|
| _(none)_ | `draft` | Created by `30_delivery_planning_v1` plan step |
| `draft` | `active` | Plan approved by review gate |
| `active` | `task_graph_ready` | Task-graph decomposition complete |
| `task_graph_ready` | `task_graph_validated` | Task-graph reviewed and approved |
| `task_graph_validated` | `executing` | First task begins execution |
| `executing` | `completed` | All tasks in the plan completed |
| any non-terminal | `superseded` | A newer plan replaces this one |

Arrow form: `draft → active → task_graph_ready → task_graph_validated → executing → completed`
Arrow form (supersession): `any non-terminal → superseded`

### Task Lifecycle

| From | To | Condition |
|------|----|-----------|
| _(none)_ | `draft` | Created by task decomposition step |
| `draft` | `active` | Task approved (acceptance criteria validated) |
| `active` | `implementing` | Executor begins work |
| `implementing` | `reviewing` | Implementation complete, submitted for review |
| `reviewing` | `rework` | Review found issues requiring fix |
| `rework` | `reviewing` | Rework complete, resubmitted (bounded: max 2 refine loops) |
| `reviewing` | `validating` | Review passed, no issues or issues resolved |
| `validating` | `completed` | Validation passed |
| `validating` | `rework` | Validation failed, return to rework (bounded: max 1 replan loop) |
| any non-terminal | `superseded` | A newer task replaces this one |

Arrow form: `draft → active → implementing → reviewing → validating → completed`
Arrow form (rework): `reviewing → rework → reviewing`
Arrow form (validation failure): `validating → rework → reviewing`

### Implementation Lifecycle

| From | To | Condition |
|------|----|-----------|
| _(none)_ | `draft` | Implementation plan created |
| `draft` | `active` | Implementation complete, awaiting review |
| `active` | `reviewing` | Submitted for review |
| `reviewing` | `rework` | Review found issues |
| `rework` | `reviewing` | Rework complete, resubmitted |
| `reviewing` | `validating` | Review passed |
| `validating` | `completed` | Validation passed |
| any non-terminal | `superseded` | Replaced by a newer implementation |

Arrow form: `draft → active → reviewing → validating → completed`

### Documentation Sync Lifecycle

| From | To | Condition |
|------|----|-----------|
| _(none)_ | `scanning` | `40_documentation_sync_v1` begins |
| `scanning` | `analyzing` | Scanning complete, drift data collected |
| `analyzing` | `flagging` | Analysis complete, stale entries identified |
| `flagging` | `completed` | All stale entries flagged |
| any state | `completed` | Sync operation concluded (early termination) |

Arrow form: `scanning → analyzing → flagging → completed`

## Authority Model

| Actor | Can Set Status | Cannot Override |
|-------|---------------|-----------------|
| **Workflow steps** | Their own phase outputs | Other phases' outputs |
| **Reviewer** | `reviewing → rework` or `reviewing → validating` | Task completion status |
| **Validator** | `validating → completed` | Review status |
| **Memory Manager** | Recording status in memory documents | Any live artifact status |
| **Runner actions** | Structural validation results | Content quality judgments |
| **Human operator** | Any status (manual override) | Must document override reason |

## Approval Gates

Every initiative and plan must pass an approval gate before its status advances from `draft` to `active`. The gate checks:

1. **Completeness** — all required sections present per template.
2. **Clarity** — acceptance criteria are specific and testable.
3. **Scope** — documentation scope fully enumerated, stale-guidance risks identified.
4. **Risk** — risks identified and mitigated or accepted.
5. **Traceability** — parent references are valid, child references are resolvable.

If the gate rejects, the artifact returns to `draft` for correction. The correction is tracked as a refine iteration.

## Forbidden Transitions

The following transitions are **always forbidden**, regardless of context:

| Forbidden | Reason |
|-----------|--------|
| `completed → any non-terminal` | Completed artifacts are immutable. Corrections require a new initiative. |
| `superseded → any` | Superseded artifacts are terminal. |
| `draft → completed` (any artifact type) | Skips all intermediate phases. |
| `active → completed` (initiative or plan) | Skips planning or execution phases. |
| `draft → implementing` (task) | Skips the approval gate. |
| `draft → executing` (initiative) | Skips the planning phase entirely. |
| Any state → `draft` (after first transition from draft) | No rollback to draft once an artifact has left draft. |
| Any state → `active` (from a terminal state) | Terminal states are final. |
| `reviewing → implementing` (task) | Must go through `rework` or `validating` first. |
| `validating → reviewing` (task) | Validation failure goes to `rework`, not back to `reviewing`. |

## Document-First

All delivery artifacts are documents. Code is secondary. The sequence is:

1. Document the requirement (initiative).
2. Document the solution (plan).
3. Document the tasks (task-graph).
4. Document the implementation plan.
5. Execute the code.
6. Update the documentation (co-change).
7. Validate everything.

If code exists without a corresponding approved document, it is unauthorized and must be captured via a new initiative. This rule applies equally to source code changes and documentation-only changes.

### Document-First Implications

- **No orphan code.** Code without documentation is incomplete.
- **No orphan documentation.** Documentation without a corresponding source or plan is stale.
- **Co-change is mandatory.** Documentation updates happen in the same delivery task as the code changes they describe.
- **Flagging is the escape hatch.** If a doc cannot be updated in the current cycle, it must be flagged as `stale_pending` rather than silently left outdated.

## Traceability

Every delivery artifact must maintain a chain of references back to its origin:

- **Task** references its parent plan.
- **Plan** references its parent initiative.
- **Implementation plan** references its parent task.
- **Review record** references its parent implementation plan.
- **Validation record** references its parent review record.
- **Memory record** references all artifacts in the delivery chain.

This chain enables:

- **Backward traceability** — from any artifact to its origin initiative.
- **Forward traceability** — from an initiative to all derived artifacts.
- **Impact analysis** — when a source file changes, which delivery artifacts are affected?
- **Audit trail** — who approved what, when, and why.

### Traceability Requirements

| Artifact | Required References |
|----------|-------------------|
| Initiative | None (root artifact) |
| Plan | `parent_initiative` |
| Task | `parent_plan`, `parent_task_graph` |
| Implementation plan | `parent_task` |
| Review record | `parent_impl_plan`, `parent_task` |
| Validation record | `parent_review` |
| Memory record | `initiative`, `plan`, `tasks[]`, `reviews[]` |
| Change record (codebase) | `parent_task` (if triggered by a delivery task) |
