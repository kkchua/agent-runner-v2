---
template_id: "SYS-00-DSR"
title: "Delivery Status Rules v1"
status: "active"
version: "1.0"
generated: "2026-07-09T10:30:00+08:00"
workflow: "10_execution_scaffold_v1"
step: "generate_sop"
change_id: "10SCAFFOLD-20260708-8a4445fc"
managed_by: workflow-generated
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_sop`
> This file is workflow-generated and protected from manual edits.

# Delivery Status Rules v1

## Core Principles

1. **Explicit state transitions** — Every workflow artifact moves through defined states; implicit transitions prohibited
2. **Document-first discipline** — No code or configuration change without corresponding delivery document
3. **Traceability mandatory** — Every artifact traces to originating initiative, plan, task, and implementation
4. **Approval gates enforce quality** — Critical transitions require human-in-the-loop approval
5. **Failure routing explicit** — Hard failures route through runner failure handling; no silent recovery

## Global Workflow Discipline

All delivery workflows must adhere to these global rules regardless of specific workflow family:

### State Machine Enforcement

- Workflows define valid state transitions using arrow notation (`→`)
- Invalid transitions rejected by workflow router
- Current state recorded in job.json with timestamp
- Transition history preserved for audit

### Artifact Completeness

- Required artifacts defined per workflow step
- Missing artifacts trigger validation failure
- Artifact paths pre-computed from `constants.py`; zero hardcoded strings
- Meta.json sidecar mandatory for every coder/runner step

### Review Loop Limits

- Max rejects threshold defined per workflow
- Exceeded thresholds route to failure state
- Rejection reasons must be specific and actionable
- Refine context preserved across attempts

## Lifecycle Rules

### Initiative Intake Lifecycle (`20_initiative_intake_v1`)

**Valid States:** `draft → active → planned → executing → completed`

**Transition Rules:**
- `draft → active`: Requires `DRAFT_INIT_FILE` present and validated
- `active → planned`: Requires `PRE_INIT_FILE` and `INIT_FILE` produced and approved
- `planned → executing`: Requires downstream planning complete (plan + task graph)
- `executing → completed`: Requires all planned tasks executed and validated

**Forbidden Transitions:**
- `draft → planned` (skip active) — Initiative must be activated before planning
- `active → executing` (skip planned) — Must produce init documents first
- `planned → completed` (skip executing) — Planned work must be executed

### Delivery Planning Lifecycle (`30_delivery_planning_v1`)

**Valid States:** `draft → active → task_graph_ready → task_graph_validated → executing → completed`

**Transition Rules:**
- `draft → active`: Requires `INIT_FILE` from initiative intake
- `active → task_graph_ready`: Requires `PLAN_FILE` produced and approved
- `task_graph_ready → task_graph_validated`: Task graph passes structural validation
- `task_graph_validated → executing`: Tasks ready for execution phase
- `executing → completed`: All tasks decomposed and contracts written

**Forbidden Transitions:**
- `draft → task_graph_ready` (skip active) — Plan must be activated first
- `active → task_graph_validated` (skip ready) — Graph must be ready before validation
- `task_graph_ready → completed` (skip validated/executing) — Validation and execution required

### Task Execution Lifecycle (`31_task_execution_v1`)

**Valid States:** `draft → active → implementing → reviewing → validating → completed`

**Transition Rules:**
- `draft → active`: Requires `TASK_FILE` from delivery planning
- `active → implementing`: Task contract loaded; implementation planner engaged
- `implementing → reviewing`: `IMPL_FILE` produced; executor completed modifications
- `reviewing → validating`: Review approved; `REVIEW_FILE` produced
- `validating → completed`: Validation passed; `VALIDATION_FILE` produced

**Review Loop Transitions:**
- `reviewing → implementing`: Review rejected; refine cycle restarts (max_rejects counter incremented)
- `validating → implementing`: Validation failed; implementation requires rework

**Forbidden Transitions:**
- `draft → implementing` (skip active) — Task must be activated first
- `implementing → validating` (skip reviewing) — Implementation must be reviewed before validation
- `reviewing → completed` (skip validating) — Reviewed code must pass validation gate

### Documentation Sync Lifecycle (`40_documentation_sync_v1`)

**Valid States:** `draft → active → reconciling → validated → completed`

**Transition Rules:**
- `draft → active`: Triggered by code drift detection or periodic maintenance schedule
- `active → reconciling`: Repository scan initiated; stale guidance identified
- `reconciling → validated`: Module docs, component docs, inventory updated
- `validated → completed`: Change impacts recorded; sync complete

**Forbidden Transitions:**
- `draft → reconciling` (skip active) — Sync must be activated first
- `reconciling → completed` (skip validated) — Updated docs must pass validation

### Architecture Site Lifecycle (`50_architecture_site_v1`)

**Valid States:** `draft → active → generating → publishing → completed`

**Transition Rules:**
- `draft → active`: System documentation set current; site generation requested
- `active → generating`: HTML templates rendered; audience folders populated
- `generating → publishing`: Site structure validated; links verified
- `publishing → completed`: Site published to `docs/site/`; ready for consumption

**Forbidden Transitions:**
- `draft → generating` (skip active) — Site generation must be activated first
- `generating → completed` (skip publishing) — Generated site must be published and validated

## Authority Model

When multiple sources provide conflicting guidance on workflow status, apply this precedence:

1. **Job state (job.json)** — Authoritative record of current workflow state and transition history
2. **Meta.json sidecar** — Step-level result reporting; overrides any markdown artifact claims
3. **Workflow router logs** — Router decisions take precedence over manual state assumptions
4. **Generated artifacts** — Markdown documents reflect state but do not define it
5. **Manual annotations** — Prohibited; use source prompts and re-run workflows instead

## Approval Gates

Critical workflow transitions require explicit human approval before proceeding:

### Mandatory Approval Points

| Workflow | Transition | Artifact | Approver Role |
|----------|-----------|----------|---------------|
| `20_initiative_intake_v1` | `active → planned` | `INIT_FILE` | Product Owner / Stakeholder |
| `30_delivery_planning_v1` | `task_graph_ready → task_graph_validated` | `TASK_GRAPH_FILE` | Architect / Tech Lead |
| `31_task_execution_v1` | `implementing → reviewing` | `IMPL_FILE` | Senior Engineer / Reviewer |
| `31_task_execution_v1` | `reviewing → validating` | `REVIEW_FILE` | Code Owner |
| `50_architecture_site_v1` | `generating → publishing` | Generated HTML | Documentation Owner |

### Approval Recording

- Approver identity captured (username, role)
- Timestamp recorded in job.json
- Approval rationale optional but recommended
- Rejection triggers refine cycle with specific findings

### Approval Bypass

- Emergency fixes may bypass approval with documented justification
- Bypass recorded in job.json with reason code
- Post-hoc review required within 24 hours

## Forbidden Transitions

The following transitions are explicitly forbidden and will be rejected by the workflow router:

### Cross-Phase Skipping

- `20_initiative_intake_v1` → `31_task_execution_v1` (skip planning)
- `30_delivery_planning_v1` → `50_architecture_site_v1` (skip execution)
- Any workflow → `completed` without producing required artifacts

### State Regression

- `completed → active` (reopen completed workflow) — Create new initiative instead
- `failed → active` (retry without fix) — Address failure cause first
- `cancelled → executing` (resume cancelled work) — Restart as new workflow

### Artifact Omission

- `implementing → reviewing` without `IMPL_FILE`
- `reviewing → validating` without `REVIEW_FILE`
- `validating → completed` without `VALIDATION_FILE`
- Any step completion without `meta.json` sidecar

### Silent Failure Recovery

- `failed → active` without addressing root cause
- `rejected → approving` without refine cycle
- Error suppression or masking in meta.json

## Document-First

The document-first principle governs all delivery workflows:

### Rule Statement

No code modification, configuration change, or architectural decision occurs without a corresponding delivery document that captures:

- **Intent** — Why the change is needed (links to initiative, plan, or task)
- **Scope** — What is affected (modules, components, interfaces)
- **Design** — How the change is implemented (implementation plan, review findings)
- **Validation** — Evidence that the change meets requirements (validation results)

### Application

1. **Code Changes** — Require `IMPL_FILE` describing implementation approach before executor modifies source files
2. **Documentation Updates** — Require task contract specifying which docs to update and why
3. **Configuration Changes** — Require plan item justifying configuration modification
4. **Architectural Decisions** — Require initiative document capturing decision context and alternatives considered

### Enforcement

- Executor action validates `IMPL_FILE` presence before modifying code
- Documentation sync workflow validates task linkage before updating module docs
- Workflow router rejects transitions missing required artifacts
- Protected document guardrails prevent manual edits to generated docs

## Traceability

Every delivery artifact must maintain traceability links to its origin and dependents:

### Traceability Chain

```
INIT_FILE → PLAN_FILE → TASK_GRAPH_FILE → TASK_FILE → IMPL_FILE → REVIEW_FILE → VALIDATION_FILE
```

Each artifact references its predecessor via:

- **Change ID** — Unique identifier linking related artifacts (e.g., `10SCAFFOLD-20260708-8a4445fc`)
- **Workflow name** — Workflow family that produced the artifact (e.g., `31_task_execution_v1`)
- **Step name** — Specific step within workflow (e.g., `execute_implementation`)
- **Source artifact path** — Relative or absolute path to predecessor artifact

### Job State Traceability

Job.json maintains complete traceability:

- **Template group** — Workflow family name
- **Step history** — Ordered list of executed steps with timestamps
- **Retry history** — Previous attempts with failure codes and remarks
- **Artifact registry** — Map of artifact keys to produced file paths

### Cross-Reference Requirements

1. **Initiative to Plan** — `INIT_FILE` change_id referenced in `PLAN_FILE` frontmatter
2. **Plan to Tasks** — `PLAN_FILE` change_id referenced in each `TASK_FILE`
3. **Task to Implementation** — `TASK_FILE` change_id referenced in `IMPL_FILE`
4. **Implementation to Review** — `IMPL_FILE` change_id referenced in `REVIEW_FILE`
5. **Review to Validation** — `REVIEW_FILE` change_id referenced in `VALIDATION_FILE`

### Memory Integration

Institutional knowledge captured in memory entries must reference:

- **Artifact path** — Which delivery document contains the decision/lesson
- **Change ID** — Link back to workflow execution
- **Expiry condition** — When the memory becomes stale (project completion, next refactor, etc.)

---

*Generated by workflow: 10_execution_scaffold_v1 | Step: generate_sop | Change: 10SCAFFOLD-20260708-8a4445fc*
