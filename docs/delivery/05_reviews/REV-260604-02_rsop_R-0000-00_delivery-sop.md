# SOP Review: delivery_sop.json & delivery_status_rules.json

**Review Date:** 2026-06-04  
**Reviewer:** SOP Reviewer  
**Reviewed Artifacts:**
- `/workspace/projects/agent-runner-v2/docs/delivery/00_templates/delivery_sop.json`
- `/workspace/projects/agent-runner-v2/docs/delivery/00_templates/delivery_status_rules.json`

**Governing Reference:**
- `/workspace/projects/agent-runner-v2/delivery_scaffold_v1/SCAFFOLD-GEN-20260603-008/00_project_analysis/project_analysis.json`

---

## Review Criteria

1. Does the SOP cover all phases identified in the project analysis?
2. Are approval gates and status transitions clearly defined?
3. Are the status rules consistent with the SOP?
4. Are there any missing sections or incomplete areas?

---

## Evaluation Results

### 1. Phase Coverage ✓

**Finding:** Both SOP and Status Rules comprehensively cover all phases and roles identified in the project analysis:

- **Phases (8):** Initiative, Planning, Task Graph, Task Execution, Implementation Planning, Review, Validation, Memory Management — all present with owner, action, output, gates, next state
- **Roles (9):** Planner, Task Decomposer, Implementation Planner, Executor, Reviewer, Validator, Memory Manager, Architect, Runner — all documented in Agent Roles Table with authority boundaries
- **Workflow scope:** Matches project analysis recommendations exactly

**Verdict:** Complete coverage. ✓

---

### 2. Approval Gates & State Transitions ✓

**Finding:** Both documents define approval gates and state transitions with high clarity:

**SOP:**
- Full state diagram with 14 named states
- State Definitions table with conditions and transitions
- Authority Precedence hierarchy (Runner > SOP > Metadata > Body)
- Explicit approval gate descriptions (Initiative → Plan → Task Graph → Task → Review → Validation)

**Status Rules:**
- Artifact Lifecycle Rules for each document type
- Authority Model role boundaries table
- 8 explicit Approval Gates with preconditions and effects
- Forbidden Transitions section enumerating 20+ invalid state jumps

**Verdict:** Clear and well-structured. ✓

---

### 3. Consistency Between SOP & Status Rules ✗

**FINDING — CRITICAL INTERNAL CONTRADICTION in Status Rules:**

The Status Rules document contains **irreconcilable contradictions** between its "Artifact Lifecycle Rules" section and its "Approval Gates" section:

#### Plan Artifact Inconsistency:
- **Artifact Lifecycle Rules** (line 35): "Plan: **Allowed States:** Draft → Reviewed → Approved → Completed"
- **Approval Gates** (section 2, line in document): "Plan Draft → Approved" (no intermediate Reviewed state)

These two statements cannot both be true. Either:
- Plan has a `PLAN_REVIEWED` state (Lifecycle is correct), or
- Plan transitions directly from Draft to Approved (Approval Gates is correct)

#### Task Graph Artifact Inconsistency:
- **Artifact Lifecycle Rules** (line 42): "Task Graph: **Allowed States:** Draft → Reviewed → Approved"
- **Approval Gates** (section 3): "Task Graph Draft → Approved" (no intermediate Reviewed state)

Same contradiction: either Reviewed is a required state or it is not.

#### SOP State Machine Gap:
The SOP state machine:
- **Includes:** `PLAN_DRAFT` and `PLAN_APPROVED`
- **Missing:** `PLAN_REVIEWED` state
- **Also missing:** `TASK_GRAPH_REVIEWED` state

The SOP state diagram (line ~19-35 in content) does not show an intermediate "Reviewed" state for Plans or Task Graphs, which creates misalignment with Status Rules' lifecycle definitions.

#### Impact:
This inconsistency creates **execution ambiguity**:
- When a Plan or Task Graph is submitted, does the runner expect it to move through a Reviewed intermediate state before Architect approval?
- Or does it skip directly to Approved?
- The two documents give different answers, which will cause implementation bugs and approval workflow failures.

**Verdict:** Not acceptable; requires resolution before binding. ✗

---

### 4. Missing Sections & Incomplete Areas ✗

#### A. Meta.json Sidecar Schema Mismatch (MAJOR)

**SOP definition** (Communication Protocol section):
- 8 fields: status, decision, remark, artifacts, findings, evidence, upstream_refs, recorded_at

**Status Rules definition** (Sidecar Rule section):
- 10 fields: status, decision, remark, artifacts, findings, evidence, upstream_refs, **supersedes, superseded_by**, recorded_at

The SOP is missing `supersedes` and `superseded_by` fields, which are critical for artifact versioning and supersession tracking (defined as a core rule in both documents).

**Verdict:** Schemas must be aligned. The SOP schema is incomplete. ✗

#### B. Reviewer Role Ambiguity (MAJOR)

**SOP Phase 2 (Planning):**
- "Approval Gate: Architect reviews; approves or rejects"

**Status Rules Approval Gate 2 (Plan Draft → Approved):**
- "Requires: Reviewer assessment + Architect approval decision"

These suggest different reviewer roles:
- SOP: Architect performs the review
- Status Rules: Independent Reviewer performs assessment; then Architect approves

**Issue:** The SOP does not clarify whether plan/task graph reviews are:
1. Optional standalone Review artifacts (like Phase 6 & 7), or
2. Mandatory inline assessments by an independent Reviewer role (as Status Rules implies)

This ambiguity will cause confusion during workflow execution.

**Verdict:** SOP must clarify mandatory Reviewer role for plan/task graph assessment. ✗

#### C. File Reference Error (MINOR)

**SOP Authority Precedence** (line 14-16):
- References: "DELIVERY_STATUS_RULES_v1.md"

**Actual file name:**
- `delivery_status_rules.json` (JSON schema, not markdown)

**Impact:** Dead reference; users looking for "v1.md" will not find the file.

**Verdict:** Update reference to match actual file format. ✗

#### D. Agent Contracts Missing (DOCUMENTATION)

Both documents reference agent role contracts in `docs/delivery/08_agents/` (planner_contract.md, executor_contract.md, etc.), but these files are not present in the current review scope.

**Status:** This is expected; agent contracts may exist in separate scaffolding. Not a blocker for SOP review if contracts are planned separately.

---

## Summary of Findings

| Finding | Severity | Location | Resolution |
|---------|----------|----------|-----------|
| **Status Rules internal contradiction (Plan Reviewed state)** | CRITICAL | Status Rules: Artifact Lifecycle vs. Approval Gates | Reconcile whether Plan has Reviewed state |
| **Status Rules internal contradiction (Task Graph Reviewed state)** | CRITICAL | Status Rules: Artifact Lifecycle vs. Approval Gates | Reconcile whether Task Graph has Reviewed state |
| **SOP missing Reviewed states** | MAJOR | SOP: State Definitions table & diagram | Add PLAN_REVIEWED and TASK_GRAPH_REVIEWED states |
| **Meta.json schema mismatch** | MAJOR | SOP: Communication Protocol vs. Status Rules: Sidecar Rule | Add supersedes/superseded_by to SOP schema |
| **Reviewer role ambiguity** | MAJOR | SOP Phase 2 vs. Status Rules Approval Gates | Clarify mandatory Reviewer for plan/task graph assessment |
| **File reference error** | MINOR | SOP: Authority Precedence | Update reference from .md to .json |

---

## Verdict

**Status: REJECTED**

The SOP and Status Rules documents contain critical internal contradictions and misalignments that must be resolved before they can serve as binding governance for the agent-runner-v2 delivery workflow:

1. **Status Rules contradicts itself** on whether Plan and Task Graph have intermediate "Reviewed" states
2. **SOP state machine is incomplete**, missing these states entirely
3. **Meta.json schema definitions differ** between documents (SOP missing 2 required fields)
4. **Reviewer role is ambiguous** across documents (unclear if inline or separate)
5. **File references are incorrect** (markdown vs. JSON)

### Required Actions Before Approval:

1. **Resolve Status Rules contradiction:** Decide whether Plan and Task Graph have explicit `Reviewed` intermediate states, update "Artifact Lifecycle Rules" and "Approval Gates" sections to be consistent
2. **Update SOP state machine:** Add `PLAN_REVIEWED` and `TASK_GRAPH_REVIEWED` states to match Status Rules decision
3. **Align meta.json schemas:** Add `supersedes` and `superseded_by` fields to SOP Communication Protocol schema
4. **Clarify Reviewer role:** Document whether plan/task graph review is inline (precondition to approval) or separate Review artifact
5. **Fix file references:** Update SOP reference from "DELIVERY_STATUS_RULES_v1.md" to "delivery_status_rules.json"

---

## Recommendation

**Do not merge these documents into binding SOP governance until the above contradictions are resolved.** The internal inconsistencies in Status Rules and the gaps in SOP will cause implementation failures and approval workflow ambiguities.

Recommend:
1. Create new versions of both documents (WORKFLOW_SOP_v1.1 and DELIVERY_STATUS_RULES_v1.1) with corrections
2. Use explicit supersession links (old artifact: `superseded_by: <new-ID>`, new artifact: `supersedes: <old-ID>`)
3. Circulate corrected versions for re-review before marking as approved binding documents
