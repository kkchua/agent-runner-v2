# DELIVERY_STATUS_RULES_v1.md: Artifact Lifecycle & Authority Model

---

## Metadata

| Field | Value |
|-------|-------|
| **Document Type** | agent_contract (Workflow Status Rules) |
| **Version** | v1.0 |
| **Status** | Active |
| **Owner** | Architect |
| **Project** | agent-runner-v2 (LLM Workflow Orchestration Engine) |
| **Complexity** | Advanced |
| **Last Updated** | 2026-06-03 |
| **Valid From** | 2026-06-03 onwards |

---

## Core Principles (Non-Negotiable)

1. **Explicit Status:** Every artifact has an explicit, durable status stored in meta.json sidecar.
2. **Centralized Approval:** Approval is runner-enforced via sidecar decisions, not artifact body content.
3. **Execution ≠ Approval:** Generation, implementation, review, and validation do NOT advance state unless runner accepts the required sidecar decision.
4. **Durable State:** State lives in artifacts, metadata frontmatter, and **authoritative meta.json sidecars only**.
5. **Rejection Stops Progression:** Rejection stops forward movement and routes to refinement or explicit failure handling.
6. **Authority Precedence:** Runner logic > SOP + Status Rules > Artifact metadata > Artifact body content.
7. **Contract-Driven:** Contracts are the source of truth. Artifacts outside the approved contract are invalid.
8. **Sidecar-Only Communication:** meta.json is the ONLY communication channel between agents and runner. No stdout JSON parsing, markdown write-backs, or disk recovery.

## Global Workflow Discipline (Binding Rules)

- **No Phase Skipping:** Phases must execute in order. The runner will reject any attempt to skip phases or execute out of order.
- **No Inference:** Do not infer approval from artifact body content. Approval is only valid when recorded in meta.json sidecar.
- **No Superseded Inputs:** Never use a Superseded artifact as an active input. Only use the latest non-superseded version.
- **Never Overwrite Approved:** Do not modify approved or final artifacts. Create a new version with explicit supersession links.
- **Sidecar-Only Communication:** Use meta.json sidecars as the only coder-to-runner communication channel. No stdout JSON fallback, no markdown write-back.
- **Immediate Failure Routing:** Hard failures route immediately through `route_after_failure()`. No silent recovery.
- **Budget Enforcement:** Runner enforces budget before generation or agent invocation. Insufficient budget triggers failure routing.
- **Reproducible Snapshots:** Retain snapshots that enable reproducible execution and deterministic audit trails.
- **No Pre-Invocation Sidecars:** Runner never writes meta.json sidecars before agent invocation. Agents are responsible for creating sidecars.

## Artifact Lifecycle Rules

### Initiative
**Allowed States:** Draft → Approved → Completed | Draft or Approved → Superseded

**Rules:**
- Architect approval required before planning can start
- Completion occurs only when entire delivery workflow is completed
- Once approved, cannot be modified (must create new version with supersession link if changes needed)
- Supersession allows scope expansion without modifying original (preserves audit trail)

**Sidecar:** INIT-YYYYMMDD-NN.meta.json

---

### Plan
**Allowed States:** Draft → Reviewed → Approved → Completed | Draft or Approved → Superseded

**Rules:**
- Reviewer assessment and Architect approval required before task decomposition
- Completion occurs when entire delivery is completed
- Once approved, cannot be modified
- Must reference approved initiative ID
- Supersession allows refinement without modifying original

**Sidecar:** PLAN-YYYYMMDD-NN.meta.json

---

### Task Graph
**Allowed States:** Draft → Reviewed → Approved | Draft or Approved → Superseded

**Rules:**
- Must encode all dependencies, parallel-safe branches, and upstream plan ID
- Reviewer assessment and Architect approval required before task execution
- Cannot be modified once approved (must supersede)
- All task nodes must have corresponding task artifacts

**Sidecar:** TASK-GRAPH-YYYYMMDD-NN.meta.json

---

### Task
**Allowed States:** 
- Normal flow: Pending → In Progress → Implemented → Approved
- Blocking: Pending or In Progress → Blocked
- Cancellation: Pending or In Progress → Cancelled
- Supersession: any non-terminal state → Superseded

**Rules:**
- Executable only when dependencies are approved and runner marks task ready
- Blocked tasks cannot progress until blocker is resolved
- Cancelled tasks are removed from scope
- Superseded tasks are replaced by new version
- Task approval requires implementation review AND validation approval
- Cannot transition directly from Pending to Approved or Implemented

**Sidecar:** TASK-YYYYMMDD-NN.meta.json

---

### Implementation Plan
**Allowed States:** Draft → Approved | Draft or Approved → Superseded

**Rules:**
- Must link one or more approved tasks
- Must define scoped edits, tests, evidence locations, and rollback notes
- Architect approval required before execution
- Cannot modify once approved (must supersede)
- Scope drift forbidden (executor cannot expand scope)

**Sidecar:** IMPL-YYYYMMDD-NN.meta.json

---

### Implementation Record (per task)
**Allowed States:** Draft → Final

**Rules:**
- Records actual implementation work and evidence
- Final state indicates work is complete and evidence is collected
- Cannot be modified after Final (new version required for changes)
- References approved implementation plan
- Links to code changes, test results, build artifacts

**Sidecar:** IMPL-RECORD-YYYYMMDD-NN.meta.json

---

### Review (Plan, Task Graph, Implementation)
**Allowed States:** Draft → Final

**Rules:**
- Independent review (reviewer must not be executor or architect)
- Final state records decision (APPROVED or REJECTED), findings, and evidence
- Decision is binding (runner enforces transitions based on decision)
- Rejection routes workflow back to owning phase
- Cannot modify after Final (retained as immutable evidence)

**Sidecar:** REVIEW-YYYYMMDD-NN.meta.json  
**Decision Options:** APPROVED | REJECTED | CHANGES_REQUIRED

---

### Validation
**Allowed States:** Draft → Final

**Rules:**
- Independent validation (validator must not be reviewer or executor)
- Mandatory before workflow completion
- Final state records decision (APPROVED or REJECTED), test results, and evidence
- Decision is binding (runner enforces transitions)
- Rejection routes workflow back to execution phase
- Cannot modify after Final (retained as immutable evidence)

**Sidecar:** VALIDATION-YYYYMMDD-NN.meta.json  
**Decision Options:** APPROVED | REJECTED

---

### Memory
**Allowed States:** Draft → Active → Superseded | Active → Archived

**Rules:**
- Compact durable context for future workflows
- Active memory informs downstream work but cannot override runner state or approved artifacts
- Preserves decisions, constraints, risks, snapshots, and supersession links
- Superseded when replaced by new memory version
- Archived when no longer active but retained for audit trail

**Sidecar:** MEMORY-YYYYMMDD-NN.meta.json

## Authority Model

**No Role can Exceed Its Authority.** Authority is strictly bounded.

| Role | **CAN** | **CANNOT** |
|------|--------|----------|
| **Runner** | Enforce state, budgets, retries, sidecar validation, approval transitions, failure routing, timeout enforcement | Infer success from artifact body or stdout; silently recover failures; write pre-invocation sidecars; modify artifact body |
| **Architect** | Define scope, approve gates, authorize supersession, confirm completion, route exceptions, restart workflow | Approve work lacking required evidence; skip validation; bypass sidecar requirements; modify executor's work |
| **Planner** | Draft and refine plans; propose phases and milestones | Approve own plan; expand initiative scope; execute work; make final decisions |
| **Task Decomposer** | Draft and refine task graphs and task artifacts; define dependencies | Mark dependencies satisfied without runner validation; execute tasks; approve work |
| **Implementation Planner** | Draft scoped implementation plans; define approach and tests | Execute unapproved work; self-approve plans; change task scope |
| **Executor** | Implement approved tasks; record evidence; request scope clarification | Change approval state; overwrite approved artifacts; expand scope without escalating |
| **Reviewer** | Independently assess plans, implementations, evidence; issue structured decisions | Modify implementation being reviewed; approve own work; make final workflow decisions |
| **Validator** | Independently assess behavior, contracts, acceptance criteria; issue decisions | Mark workflow completed directly; approve work; modify implementation |
| **Memory Manager** | Maintain compact durable context, snapshots, supersession links | Override runner state; ignore approved artifacts; modify upstream decisions |

**Role Boundaries:**
- **Reviewer and Executor MUST be different agents.** No one can review their own work.
- **Validator MUST be different from Reviewer and Executor.** Independent validation is mandatory.
- **Architect gates all major transitions.** Approval is role-based (Architect for scope, Reviewer for implementation, Validator for behavior).

**Agent Contracts:**
- Agent contracts in `08_agents/` define role boundaries and handoff rules only (not prompt content).
- Workflow step configurations in `template_groups.py` define invocation contracts.
- **Agent master prompts are deprecated.** Do not create `07_master_prompts/`.

## Approval Gates (Architect-Enforced)

The runner enforces these gates. **Explicit sidecar decision required** to transition:

1. **Initiative Draft → Approved**
   - Requires: Architect approval decision in meta.json
   - Precondition: Initiative artifact complete with scope, criteria, constraints
   - Effect: Enables planning phase

2. **Plan Draft → Approved**
   - Requires: Reviewer assessment + Architect approval decision in meta.json
   - Precondition: Plan artifact linked to approved initiative; reviewed for completeness
   - Effect: Enables task decomposition

3. **Task Graph Draft → Approved**
   - Requires: Reviewer assessment + Architect approval decision in meta.json
   - Precondition: Task graph artifact with dependencies; all task artifacts created; reviewed
   - Effect: Marks tasks ready for execution (with dependency checks)

4. **Implementation Plan Draft → Approved**
   - Requires: Architect approval decision in meta.json
   - Precondition: Plan artifact linked to approved task; scope and tests defined
   - Effect: Enables task execution

5. **Task Pending → In Progress**
   - Requires: Runner verification that dependencies are approved and task is marked ready
   - Precondition: Upstream task dependencies in Approved state
   - Effect: Marks task eligible for execution

6. **Task In Progress → Implemented**
   - Requires: Implementation record sidecar accepted with evidence links
   - Precondition: Code changes completed, tests passed, evidence collected
   - Effect: Marks task ready for review

7. **Task Implemented → Approved**
   - Requires: Implementation review approval + Validation approval + Architect gate
   - Precondition: Review is Final with APPROVED decision; Validation is Final with APPROVED decision
   - Effect: Task is complete; counts toward workflow completion

8. **Workflow COMPLETED**
   - Requires: Validation Final with APPROVED decision + Architect gate
   - Precondition: All in-scope tasks are Approved; no rejected reviews/validations
   - Effect: Workflow terminates; delivery is final
   - **Forbidden:** Workflow cannot move to COMPLETED while any in-scope task is not Approved

---

## Forbidden Transitions

The runner will **reject** these state transitions:

| Forbidden Transition | Reason |
|---|---|
| Initiative Draft → Completed | Must pass through Approved |
| Initiative Draft → Approved (without sidecar) | Approval requires sidecar decision |
| Plan Draft → Completed | Must pass through Approved |
| Plan Draft → Approved (without review) | Review required before approval |
| Task Graph Draft → Approved (without review) | Review required before approval |
| Task Pending → Implemented | Must pass through In Progress |
| Task Pending → Approved | Must pass through In Progress and Implemented |
| Task In Progress → Approved | Must pass through Implemented |
| Task Blocked → Implemented | Blocked tasks cannot progress until resolved |
| Task Cancelled → any active state | Cancelled is terminal for that task |
| Task any non-terminal → Approved (without review + validation) | Review and validation required |
| Implementation Plan Draft → Execution | Must pass through Approved |
| Review Draft → Workflow gate decision | Must be Final before affecting workflow |
| Validation Draft → Workflow gate decision | Must be Final before affecting workflow |
| Validation Rejected → Workflow COMPLETED | Rejection stops progression; cannot skip back |
| Workflow COMPLETED (with rejected review/validation) | All reviews/validations must be Approved |
| Workflow COMPLETED (with any Pending/In Progress task) | All in-scope tasks must be Approved |
| Any approved artifact → Modified directly | Must supersede (create new version) |
| Any superseded artifact → Used as active input | Must use latest version |
| Any transition skipping phase | Phases must execute in order |
| Any transition bypassing sidecar requirement | Sidecar is mandatory for state changes |

## Rejection Routing
| Gate | Failure Category | Allowed Destination State | Supersession Behavior |
| --- | --- | --- | --- |
| Initiative approval | Initiative scope or constraints | INITIATIVE_CREATED | Supersede replaced initiative drafts. |
| Plan review or approval | Initiative scope defect | INITIATIVE_CREATED | Supersede affected downstream versions. |
| Plan review or approval | Plan defect | PLAN_DRAFTED | Supersede replaced plan versions. |
| Task graph review or approval | Initiative scope defect | INITIATIVE_CREATED | Supersede affected downstream versions. |
| Task graph review or approval | Plan defect | PLAN_DRAFTED | Supersede affected graph and task versions. |
| Task graph review or approval | Task graph or task defect | TASK_GRAPH_DRAFTED | Supersede replaced graph or task versions. |
| Implementation plan approval | Task graph or task defect | TASK_GRAPH_DRAFTED | Supersede affected implementation plan and replaced upstream versions. |
| Implementation plan approval | Implementation plan defect | IMPLEMENTATION_PLANNED | Supersede the replaced implementation plan. |
| Implementation review | Execution defect | EXECUTION_IN_PROGRESS | Keep rejected review final; emit corrected implementation record version. |
| Implementation review | Implementation plan defect | IMPLEMENTATION_PLANNED | Supersede the affected implementation plan. |
| Validation | Execution defect | EXECUTION_IN_PROGRESS | Keep rejected validation final; emit corrected implementation evidence. |
| Validation | Implementation plan defect | IMPLEMENTATION_PLANNED | Supersede the affected implementation plan. |
| Validation | Task graph or task defect | TASK_GRAPH_DRAFTED | Supersede affected downstream versions. |
| Validation | Plan defect | PLAN_DRAFTED | Supersede affected downstream versions. |
| Validation | Initiative scope defect | INITIATIVE_CREATED | Supersede affected downstream versions. |

The accepted rejection sidecar records the failure category. The runner selects the most upstream applicable category and rejects destinations outside this table.

## Document-First Rule

**No step is complete without ALL of the following:**

1. **Artifact Body:** The required markdown artifact with all required sections (per template)
2. **Folder Placement:** Artifact in the correct folder (see Naming and Folder Discipline below)
3. **Meta.json Sidecar:** Matching sidecar with schema v2, status, decision (if gate), and all required fields
4. **Upstream Linkage:** Artifact references the artifact IDs it depends on (initiative → plan → task graph → tasks)
5. **Runner-Accepted Transition:** Runner has accepted and validated the sidecar before marking state change

**Violation:** Any artifact lacking these five elements is invalid. The runner will reject it and request resubmission.

---

## Review and Validation Decision Rule

Every Review and Validation artifact **must record:**

| Field | Requirement | Details |
|---|---|---|
| **Target** | Artifact ID, version, path | Exactly what is being reviewed (e.g., PLAN-20260603-01, TASK-20260603-02) |
| **Decision** | APPROVED or REJECTED | Binding decision; determines workflow routing |
| **Findings** | Structured observations | Organized by severity (Critical, Major, Minor); include issue description, location, impact |
| **Evidence** | Tests, hashes, logs, references | Concrete proof supporting the decision (test results, code reviews, contract checks, performance metrics) |
| **Follow-up** | Corrections required, owner, routing | If rejected, specify what must be fixed, who fixes it, where workflow returns |

**Decision Binding:**
- **APPROVED:** Workflow advances to next phase
- **REJECTED:** Workflow routes back to owning phase (executor must address findings and re-implement)

Approval is effective **only after runner accepts the sidecar**. Decision in artifact body is advisory; decision in sidecar is authoritative.

---

## Naming and Folder Discipline

Every artifact must be placed in the correct folder with a stable, deterministic ID.

| Artifact Type | Folder | ID Format | Example |
|---|---|---|---|
| SOP, status rules, templates, registry | `docs/delivery/00_templates/` | Fixed | `WORKFLOW_SOP_v1.md` |
| Initiative | `docs/delivery/01_initiatives/` | INIT-YYYYMMDD-NN | `INIT-20260603-01_scope-description.md` |
| Plan | `docs/delivery/02_plans/` | PLAN-YYYYMMDD-NN | `PLAN-20260603-01_phases.md` |
| Task Graph | `docs/delivery/02_plans/artifacts/` | TASK-GRAPH-YYYYMMDD-NN | `TASK-GRAPH-20260603-01.md` |
| Task | `docs/delivery/03_tasks/` | TASK-YYYYMMDD-NN | `TASK-20260603-01_implementation.md` |
| Implementation Plan | `docs/delivery/04_implementation/` | IMPL-YYYYMMDD-NN | `IMPL-20260603-01_approach.md` |
| Implementation Record | `docs/delivery/04_implementation/` | IMPL-REC-YYYYMMDD-NN | `IMPL-REC-20260603-01_evidence.md` |
| Review | `docs/delivery/05_reviews/` | REVIEW-YYYYMMDD-NN | `REVIEW-20260603-01_plan-assessment.md` |
| Validation | `docs/delivery/05_reviews/` | VAL-YYYYMMDD-NN | `VAL-20260603-01_final-check.md` |
| Memory | `docs/delivery/06_memory/` | MEMORY-YYYYMMDD-NN | `MEMORY-20260603-01_snapshot.md` |
| Agent Contracts | `docs/delivery/08_agents/` | Fixed | `AGENTS.md`, `planner_contract.md` |

**Do not create `07_master_prompts/`.** Agent master prompts are deprecated.

**Stable IDs:**
- Use format: `TYPE-YYYYMMDD-NN` where NN increments per day per type
- IDs must be deterministic and reproducible
- Every superseding artifact must explicitly reference the artifact ID it replaces
- Use deterministic hashes for content validation

---

## Traceability Rule

Every artifact preserves a **complete upstream linkage chain** in its metadata:

- **Initiative:** Standalone; no upstream requirement
- **Plan:** Links initiative ID (e.g., `upstream: [INIT-20260603-01]`)
- **Task Graph:** Links plan ID (e.g., `upstream: [PLAN-20260603-01]`)
- **Task:** Links task graph ID and plan ID (e.g., `upstream: [TASK-GRAPH-20260603-01, PLAN-20260603-01]`)
- **Implementation Plan:** Links approved task IDs (e.g., `upstream: [TASK-20260603-01]`)
- **Implementation Record:** Links approved implementation plan and task (e.g., `upstream: [IMPL-20260603-01, TASK-20260603-01]`)
- **Review:** Links reviewed artifact (e.g., `upstream: [PLAN-20260603-01]`)
- **Validation:** Links validated artifact (e.g., `upstream: [TASK-20260603-01]`)
- **Memory:** Links summarized artifacts and snapshots (e.g., `upstream: [INIT-20260603-01, PLAN-20260603-01, decisions]`)

**Checkpoint Hashes:**
- Record content hash of approved artifacts (enables reproducibility)
- Store hashes in implementation records and reviews as evidence
- Compare hashes during validation to detect untracked changes

---

## Sidecar Rule (meta.json Authority)

The **meta.json sidecar is authoritative** for coder results and runner state transitions.

**Sidecar Schema (v2 - REQUIRED):**

```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "Draft | Reviewed | Approved | Final | Implemented | Completed | Superseded | Cancelled",
    "decision": true | false,
    "remark": "Brief summary of result",
    "artifacts": {
      "artifact_name": "/absolute/path/to/file",
      "other_artifact": "/absolute/path/to/file2"
    },
    "findings": [
      {
        "severity": "Critical | Major | Minor",
        "issue": "Description",
        "location": "File:line or section",
        "impact": "What breaks or degrades"
      }
    ],
    "evidence": [
      {
        "type": "test_result | hash | log | screenshot",
        "path": "/absolute/path",
        "hash_sha256": "hex_string",
        "notes": "Context"
      }
    ],
    "upstream_refs": ["INIT-20260603-01", "PLAN-20260603-01"],
    "recorded_at": "2026-06-03T10:30:00Z"
  }
}
```

**Sidecar Requirements:**

- **Schema:** Must be v2 (string field `schema_version`)
- **Status:** Must be valid for artifact type (Draft, Approved, Final, etc.)
- **Decision:** Required for approval gates (boolean: true=approved, false=rejected)
- **Remark:** Brief human-readable summary
- **Artifacts:** Map of artifact names to **absolute file paths** that exist on disk
- **Findings:** Optional; required for review/validation artifacts
- **Evidence:** Optional; required for review/validation artifacts with findings
- **Upstream Refs:** List of artifact IDs this depends on (enables traceability)
- **Recorded Timestamp:** ISO 8601 format; immutable once written

**Runner Acceptance Criteria:**

- Sidecar path must be `<artifact-basename>.meta.json` (same directory)
- Schema must be v2
- Status must be valid for phase
- All `artifacts` must reference existing files (absolute paths)
- If decision required, decision field must be present (true/false)
- If findings present, must have severity and issue description
- If evidence present, must have type and path
- Recorded timestamp must be recent (within acceptable delta)
- Upstream refs must reference existing artifacts or gate decisions

**Runner Behavior:**

- Runner reads sidecar only; never parses artifact body for decisions
- Runner never writes pre-invocation sidecars (agents are responsible)
- Runner validates schema and linkage before accepting status transition
- Runner rejects missing, malformed, stale, or mismatched sidecars
- Runner preserves sidecar immutability (once written, cannot be modified)
- Runner may enrich with runner-owned metadata but must not modify coder-owned fields

---

## Enforcement & Escalation

### Runner Enforcement Actions
- **Reject:** Invalid state transition (missing approval, skipped phase, forbidden transition). Returns error; no artifact side-effect.
- **Accept:** Valid state transition. Updates artifact meta.json; advances workflow state.
- **Escalate:** Budget exceeded, timeout exceeded, hard failure. Routes to Architect with full context; requires explicit decision.
- **Reroute:** Review/validation rejection. Routes workflow back to execution phase; preserves review/validation as immutable evidence.

### Architect Escalation Decisions
- **Extend:** Increase budget or timeline; update artifact metadata; resume execution.
- **Supersede:** Replace artifact (plan, task, implementation plan) due to scope change or blocker; creates new version with supersession link.
- **Override:** Accept review/validation rejection with documented reason (rare; defaults to rework).
- **Cancel:** Terminate workflow immediately. Records decision in meta.json; no recovery path.

---

## Glossary

| Term | Definition |
|------|-----------|
| **Artifact** | Structured delivery document (initiative, plan, task, review, validation, memory) with explicit state, metadata, and sidecar. Single source of truth for workflow phase. |
| **State** | Current lifecycle position (Draft, Reviewed, Approved, Final, Implemented, Completed, Superseded, Cancelled, Blocked). Authoritative in meta.json; runner-enforced. |
| **Meta.json** | Runtime state file (schema v2) encoding artifact status, approvals, upstream refs, evidence, timestamps. Only source of truth for workflow decisions. |
| **Supersession** | Explicit replacement of one artifact version by a newer version. Preserves traceability. Prior version archived; superseded; no longer active. |
| **Approval** | Architect-recorded decision (in meta.json) authorizing scope, plan, strategy, or code. Durable; cannot be revoked without supersession. |
| **Review** | Independent assessment of artifact quality, completeness, contract compliance. Binding APPROVED/REJECTED decision. Informs Architect approval decision. |
| **Validation** | Independent acceptance testing, success criteria verification, contract fulfillment check. Binding APPROVED/REJECTED decision. Final gate before completion. |
| **Rework Cycle** | Review/validation rejection routes workflow back to execution phase. Executor addresses findings; new implementation plan created; review cycle repeats. |
| **Upstream Ref** | Artifact ID that a downstream artifact depends on (e.g., Plan → Initiative, Task → Task Graph). Enables traceability; validated by runner. |
| **Sidecar** | meta.json file paired with artifact. Contains status, approvals, evidence, timestamps. Runner-read; agent-written. Never modified after initial write. |

---

## Version & Governance

- **Rules Version**: v1.0 (effective 2026-06-03)
- **Status**: Active
- **Supersession**: This document supersedes all prior status rules. Older versions archived in `docs/delivery/01_initiatives/artifacts/`.
- **Changes**: Status rules updates require Architect approval and explicit version bump. Changes recorded in project CHANGELOG.md.
- **Authority**: Runner enforces these rules strictly. No Architect override of runner state machine.

---

**End of DELIVERY_STATUS_RULES_v1.md**  
*Document effective 2026-06-03 for agent-runner-v2 (advanced complexity, LLM orchestration engine)*
