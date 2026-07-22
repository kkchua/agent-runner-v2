# 📏 UKBE Delivery Status Rules v1

## 📌 Metadata
- Doc Type: 08_agent_contract
- Template Version: v1
- Spec ID: DELIVERY-STATUS-RULES-v1
- Status: active
- Created At: 2026-04-08
- Owner: UKBE architect

---

## 🎯 Purpose

Define the authoritative status rules, approval gates, and transition discipline for all UKBE delivery artifacts and agent actions.

This document governs:
- initiatives
- plans
- task graphs
- tasks
- implementation plans
- reviews / validations
- agent workflow transitions

---

## 🧠 Core Principles

### 1. Status is explicit
No hidden or implicit state changes.

### 2. Approval is centralized
Only the architect (human) approves progression where approval is required.

### 3. Execution does not equal approval
Implemented work must still be reviewed and validated.

### 4. Workflow truth is durable and explicit
Workflow truth lives in runner state plus durable artifacts, not chat memory.

### 5. Rejection stops progression
Rejected artifacts cannot be used for downstream execution until resolved.

### 6. Authority precedence is explicit
When interpretation conflicts occur, precedence is:
1. runner runtime enforcement logic
2. `DELIVERY_STATUS_RULES_v1.md` / `WORKFLOW_SOP_v1.md`
3. artifact metadata / document status fields
4. artifact body content / prose descriptions

Lower-precedence layers may describe but may not override higher-precedence layers.

---

## 🔄 Global Workflow Discipline

- No phase skipping
- No out-of-order execution
- No use of superseded artifacts as active sources
- No downstream execution from rejected artifacts
- No silent overwrite of approved artifacts
- Artifact metadata is observational/documentary unless explicitly reconciled by runner-owned synchronization logic
- Manual artifact edits alone do not advance workflow progression

---

## 🧩 Lifecycle Rules by Artifact Type

### 1. Initiative Lifecycle

#### Allowed Status
- Draft
- Approved
- Completed
- Superseded

#### Flow
`Draft → Approved → Completed`
`Any → Superseded`

#### Rules
- Initiatives begin as `Draft`
- Only architect can mark `Approved`
- Completed means the initiative objectives are achieved or intentionally closed
- Superseded means replaced by a newer authoritative initiative

---

### 2. Plan Lifecycle

#### Allowed Status
- Draft
- Approved
- Completed
- Superseded

#### Flow
`Draft → Approved → Completed`
`Any → Superseded`

#### Rules
- Plans must not be executed downstream unless `Approved`
- Completed means all intended child work is finished or intentionally closed
- Superseded plans are inactive and must not drive new tasks

---

### 3. Task Graph Lifecycle

#### Allowed Status
- Draft
- Approved
- Superseded

#### Flow
`Draft → Approved`
`Any → Superseded`

#### Rules
- Task graph is a planning artifact, not an execution artifact
- Task docs must be derived from the approved task graph when task graph approval is used

---

### 4. Task Lifecycle

#### Allowed Status
- Pending
- In Progress
- Implemented
- Approved
- Blocked
- Cancelled
- Superseded

#### Flow
`Pending → In Progress → Implemented → Approved`

Additional terminal or interrupt states:
- `Pending/In Progress/Implemented → Blocked`
- `Pending/In Progress → Cancelled`
- `Any → Superseded`

#### Rules
- Tasks must not start as `Approved`
- `Implemented` means code or execution output exists, not that it is accepted
- `Approved` requires review / validation evidence
- `Blocked` means execution cannot continue until dependency or issue is resolved
- `Cancelled` means intentionally stopped
- `Superseded` means replaced by newer task(s)

---

### 5. Implementation Plan Lifecycle

#### Allowed Status
- Draft
- Approved
- Superseded

#### Flow
`Draft → Approved`
`Any → Superseded`

#### Rules
- Executor must not proceed from a non-approved implementation plan unless explicitly instructed for draft analysis only
- Superseded implementation plans must not be used for active coding

---

### 6. Review / Validation Lifecycle

#### Allowed Status
- Draft
- Final

#### Flow
`Draft → Final`

#### Rules
- Review and validation documents record findings and evidence
- They do not themselves replace task or plan approval states
- Final review / validation should include explicit decision

---

## 🔐 Authority Model

### Architect
- approves initiatives
- approves plans
- approves task graphs where used
- approves implementation plans where required
- makes final go / no-go decision

### Planner
- creates draft plans

### Task Decomposer
- creates draft task graph and task contracts

### Implementation Planner
- creates draft implementation plans

### Executor
- moves execution work toward implemented state through code delivery

### Reviewer
- produces independent review and validation evidence

### Memory Manager
- preserves final durable knowledge only after authoritative outcomes exist

---

## ✅ Approval Gates

The following transitions require explicit architect approval:

- Initiative: `Draft → Approved`
- Plan: `Draft → Approved`
- Task Graph: `Draft → Approved`
- Implementation Plan: `Draft → Approved`
- Task: `Implemented → Approved` requires review / validation evidence and approval decision

Approval progression rules:
- Workflow approval is process-owned and runner-enforced
- Approval metadata may mirror the outcome for readability, but does not itself authorize the next step
- Human approval that advances workflow must be recorded through the runner-owned approval action

---

## ⛔ Forbidden Transitions

The following are invalid:

- `Draft → Completed` without approval where approval is required
- `Pending → Approved`
- `In Progress → Approved` without implemented output and review evidence
- `Rejected` material continuing as active downstream source
- `Superseded` artifact used as active execution input
- silent overwrite of approved artifacts

---

## 📄 Document-First Rule

No workflow step is complete unless:
- the required output artifact exists
- the artifact is saved in the correct folder
- linkage to upstream artifacts is preserved
- state is explicit

---

## 🔍 Review / Validation Decision Rule

Review or validation artifacts must include:
- target being assessed
- decision: approved / rejected
- findings
- evidence
- follow-up actions if rejected

---

## 🧾 Naming and Folder Discipline

Artifacts must be saved in the correct location:

- Initiatives → `01_initiatives/`
- Plans → `02_plans/`
- Task Graphs → `02_plans/artifacts/`
- Tasks → `03_tasks/`
- Implementation Plans → `04_implementation_plans/`
- Reviews / Validations → `05_reviews/`
- Memory → `06_memory/`
- Agent contracts → `08_agents/`

Approved artifacts must not be silently overwritten.
Updates require:
- a new version, or
- a new document

---

## 🔗 Traceability Rule

Every artifact must preserve the relevant upstream IDs where applicable:
- Initiative ID
- Plan ID
- Task ID
- Review / Validation reference IDs

Every artifact should reference governing documents and important dependencies.

---

## 🚀 Future Automation Notes

These rules are designed for later automation into:
- control plane status tracking
- workflow routing
- approval gates
- deterministic job orchestration

---

## 🔐 Review-Loop Status Enforcement Rules

> **Authoritative source:** `docs/specs/STATUS_MODEL_v1.md` Sections 4–7.
> The rules in this section translate the enforcement requirements defined there into runner-agent-facing operational rules. Do not redefine values or transitions here — refer to the authoritative source.

---

### Preflight Enforcement Rules

These rules apply **before any step executes**. The runner agent must apply all of the following checks in order. If any check fails, the step must not execute and `job_status` must be set to `REJECTED`.

**PREFLIGHT-01 — Read `doc_status` independently**
Before executing a step, the runner must read the current `doc_status` of the target document from the storage layer. Do not infer `doc_status` from `job_status` or any other field.

**PREFLIGHT-02 — Read `review_state` independently**
Before executing a step, the runner must read the current `review_state` fields (`review_decision`, `human_approval_decision`) of the target document from the storage layer. Do not infer `review_state` from `doc_status` or `job_status`.

**PREFLIGHT-03 — Validate intended transition against the transition model**
The runner must verify that the step is authorized to perform its intended `doc_status` transition per the valid transitions table in `STATUS_MODEL_v1.md` Section 4.2. If the intended transition is not listed in that table, the step is blocked — reject with `job_status = REJECTED`.

**PREFLIGHT-04 — Reject steps targeting a FINALIZED document**
If `doc_status = FINALIZED`, the runner must reject any step that attempts to mutate `doc_status`. `FINALIZED` is a terminal state. No transitions are permitted from `FINALIZED` per `STATUS_MODEL_v1.md` Section 5.3.

**PREFLIGHT-05 — Reject explicitly blocked transitions**
The runner must check the step's intended action against the blocked transition block list in `STATUS_MODEL_v1.md` Section 5.2. If the step matches any of the following, reject with `job_status = REJECTED`:
- `refine_impl` attempting to set `doc_status` to `APPROVED` (BLOCK-01)
- `review_impl` invoked on a document with `doc_status = FINALIZED` (BLOCK-02)
- `refine_impl` invoked on a document with `doc_status = FINALIZED` (BLOCK-03)

---

### Step-Completion Enforcement Rules

These rules apply **after a step completes**. The runner agent must apply all of the following requirements. Skipping any write is a violation.

**COMPLETE-01 — Write `job_status` independently**
After the step completes, the runner must write the execution outcome to `job_status`. Allowed values: `COMPLETED`, `FAILED`, `REJECTED`, `SKIPPED` (see `STATUS_MODEL_v1.md` Section 1.2). This write is independent of any `doc_status` update.

**COMPLETE-02 — Write `doc_status` independently (when authorized)**
If the step is authorized to transition `doc_status` per `STATUS_MODEL_v1.md` Section 4.2, and the step completed with `job_status = COMPLETED`, the runner must write the new `doc_status` value. This write is independent of `job_status`.

**COMPLETE-03 — No automatic derivation between fields**
The runner must not derive `doc_status` from `job_status`, or `job_status` from `doc_status`. Each field is written by its authorizing process only. A `COMPLETED` job does not automatically advance `doc_status`.

**COMPLETE-04 — Record transition evidence**
The runner must log the `doc_status` transition with the authorizing step identity and a timestamp. This log is required for audit and traceability per the Traceability Rule above.

**COMPLETE-05 — Do not write unauthorized transitions**
If a step completes but is not authorized to perform a `doc_status` transition (e.g., the step does not appear in the ownership table in `STATUS_MODEL_v1.md` Section 2.5), the runner must not mutate `doc_status`. Write `job_status` only.

---

## ✅ Conclusion

This document is the authoritative workflow discipline contract for UKBE delivery.

It guarantees:
- explicit state
- correct sequencing
- approval discipline
- traceable multi-agent execution
