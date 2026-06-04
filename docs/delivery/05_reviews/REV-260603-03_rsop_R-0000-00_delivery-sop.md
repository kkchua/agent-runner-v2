# SOP & Status Rules Review — REV-260603-03

**Review Date:** 2026-06-03  
**Reviewer Role:** SOP Reviewer (Mandatory Gate)  
**Target Artifacts:**
- /workspace/projects/agent-runner-v2/docs/delivery/00_templates/delivery_sop.json
- /workspace/projects/agent-runner-v2/docs/delivery/00_templates/delivery_status_rules.json

**Governing Reference:**
- /workspace/projects/agent-runner-v2/delivery_scaffold_v1/SCAFFOLD-GEN-20260603-008/00_project_analysis/project_analysis.json

---

## Executive Summary

**Status: REJECTED**

The SOP and Status Rules documents contain a critical **state machine inconsistency** that prevents approval. The SOP's state diagram for Plan and Task Graph artifacts does not match the Status Rules' requirement for a Reviewed state before Architect approval.

---

## Review Findings

### 1. Phase Coverage ✓ PASS

**Criterion:** Does the SOP cover all phases identified in the project analysis?

**Finding:** Both SOP and Status Rules comprehensively cover all 8 phases recommended in the project analysis:
1. Initiative
2. Planning
3. Task Graph Creation
4. Task Execution (Parallelizable)
5. Implementation Planning (Optional)
6. Review (Optional but Recommended)
7. Validation (Optional but Recommended)
8. Memory Management (Ongoing)

**Evidence:** 
- SOP sections: "Workflow Phases" with Phase 1–8 detailed
- Status Rules: Artifact Lifecycle Rules with all 8 types specified
- Project Analysis: "Recommended Workflow Scope" lists all phases

**Conclusion:** Phase coverage is complete and aligned.

---

### 2. State Machine Consistency ✗ FAIL — CRITICAL

**Criterion:** Are approval gates and status transitions clearly defined and consistent between SOP and Status Rules?

**Finding:** **Critical inconsistency discovered** in Plan and Task Graph state transitions.

**SOP State Diagram (Actual):**
```
PLAN_DRAFT → PLAN_APPROVED (Architect)
TASK_GRAPH_DRAFT → TASK_GRAPH_APPROVED (Architect)
```
*(Reference: SOP "Workflow State Machine" section, Full State Diagram)*

**Status Rules Artifact Lifecycle (Actual):**
```
Plan: Draft → Reviewed → Approved → Completed
Task Graph: Draft → Reviewed → Approved
```
*(Reference: Status Rules "Artifact Lifecycle Rules" section, Plan and Task Graph entries)*

**Status Rules Forbidden Transitions (Actual):**
```
"Plan Draft → Approved (without review) - Forbidden Transition"
"Task Graph Draft → Approved (without review) - Forbidden Transition"
```
*(Reference: Status Rules "Forbidden Transitions" table)*

**Status Rules Approval Gates (Actual):**
```
2. Plan Draft → Approved
   Requires: Reviewer assessment + Architect approval decision

3. Task Graph Draft → Approved
   Requires: Reviewer assessment + Architect approval decision
```
*(Reference: Status Rules "Approval Gates (Architect-Enforced)" section, Gates 2 and 3)*

**Conflict:**
- SOP shows direct transition from Draft → Approved (no Reviewed state)
- Status Rules mandate Draft → Reviewed → Approved (Reviewed state required)
- Status Rules explicitly forbid bypassing Reviewed state
- Status Rules require "Reviewer assessment" before Architect approval for both Plan and Task Graph

**Impact:**
1. Runner cannot enforce consistent state transitions (SOP and Status Rules define different paths)
2. Executor may transition to Approved without review (violating Status Rules)
3. Reviewer role authority undefined in SOP state machine for Plan and Task Graph
4. Authority precedence cannot be resolved: SOP overrides Status Rules or vice versa?

**Root Cause:** SOP's full state diagram was simplified and omitted the Reviewed state that Status Rules require.

---

### 3. Authority Model Consistency ✓ PASS

**Criterion:** Are approval gates and role boundaries clearly defined?

**Finding:** Authority boundaries are clearly defined in both documents and are **consistent in intent**, despite the state machine issue above.

- Both define exclusive Architect approval authority for gates ✓
- Both define independent Reviewer authority for review artifacts ✓
- Both define independent Validator authority for validation artifacts ✓
- Both forbid self-approval (no role can approve own work) ✓
- Role table in Status Rules and Agent Roles table in SOP align ✓

**Conclusion:** Authority model is sound; state machine inconsistency is the issue, not roles.

---

### 4. Communication Protocol Consistency ✓ PASS

**Criterion:** Are meta.json sidecar and communication rules consistent?

**Finding:** Both documents consistently define:
- meta.json as the **only** communication channel ✓
- Schema v2 as required ✓
- No pre-invocation sidecar writes ✓
- No markdown write-backs ✓
- Sidecar fields (status, decision, artifacts, findings, evidence, upstream_refs, recorded_at) ✓
- Runner-enforced state transitions via sidecar ✓

**Conclusion:** Communication protocol is consistent and well-defined.

---

### 5. Validation Philosophy ✓ PASS

**Criterion:** Are validation requirements and acceptance criteria clearly defined?

**Finding:** Both documents clearly define:
- Independent review and validation requirements ✓
- Structured findings format (severity, issue, location, impact) ✓
- Evidence requirements (test results, hashes, logs, screenshots) ✓
- Decision binding (APPROVED | REJECTED | CHANGES_REQUIRED) ✓
- Rejection routing and remediation ✓

**Conclusion:** Validation philosophy is complete and consistent.

---

### 6. Supporting Documents Referenced ✓ PARTIAL

**Criterion:** Are all necessary supporting documents referenced and available?

**Finding:** Both SOP and Status Rules reference the following supporting documents:

| Document | Referenced | Status | Notes |
|---|---|---|---|
| UKBE_Artifact_v1_FINAL.md | SOP | ✓ Referenced | Upstream specification |
| UKBE_Contract_Builder_v1.1_FINAL.md | SOP | ✓ Referenced | Upstream specification |
| UKBE_Core_Data_Model_v1.2.1_FINAL.md | SOP | ✓ Referenced | Upstream specification |
| template_registry.md | SOP | ✓ Referenced | Should exist in 00_templates/ |
| AGENTS.md | SOP | ✓ Referenced | Should exist in 08_agents/ |
| template_groups.py | SOP | ✓ Referenced | Python module in source |
| Agent role contracts | Status Rules | ✓ Referenced | Should exist in 08_agents/ |
| Delivery templates (01–06) | Status Rules | ✓ Referenced | Should exist in 00_templates/ |

**Note:** The review scope is limited to SOP and Status Rules validation. Template files and agent contracts are not targets of this review but are identified as dependencies.

**Conclusion:** Supporting document structure is defined; full validation depends on templates being present (outside scope of this review).

---

## Summary of Issues

| Severity | Issue | Impact | Recommendation |
|---|---|---|---|
| **CRITICAL** | State machine inconsistency: SOP omits Reviewed state for Plan and Task Graph that Status Rules require | Runner cannot enforce consistent transitions; executor may bypass review | Update SOP state diagram to include Reviewed → Approved transitions for Plan and Task Graph |
| Major | SOP state machine section does not reference Status Rules' Reviewed state | Reader cannot understand required review before approval | Add explicit reference to review requirements in SOP Phase 2 and Phase 3 |
| Minor | SOP and Status Rules use slightly different terminology ("Reviewed" vs. implicit review in phase descriptions) | Minor clarity issue in reading | Harmonize terminology across both documents |

---

## Required Corrections

### 1. Update SOP State Diagram (CRITICAL)

**Current (Incorrect):**
```
PLAN_DRAFT → PLAN_APPROVED (Architect)
TASK_GRAPH_DRAFT → TASK_GRAPH_APPROVED (Architect)
```

**Corrected:**
```
PLAN_DRAFT → PLAN_REVIEWED (Reviewer) → PLAN_APPROVED (Architect)
TASK_GRAPH_DRAFT → TASK_GRAPH_REVIEWED (Reviewer) → TASK_GRAPH_APPROVED (Architect)
```

### 2. Update SOP Phase 2 (Planning) and Phase 3 (Task Graph Creation)

**Add explicit statement:**
- "Phase 2 output (Plan Draft) requires **Reviewer assessment before Architect approval**."
- "Phase 3 output (Task Graph Draft) requires **Reviewer assessment before Architect approval**."

### 3. Update SOP State Definitions Table

**Add rows for:**
- PLAN_REVIEWED: "Plan reviewed by independent Reviewer; ready for Architect gate"
- TASK_GRAPH_REVIEWED: "Task Graph reviewed by independent Reviewer; ready for Architect gate"

### 4. Update SOP Workflow Approval Authority Section

**Clarify review gate:**
- Extend statement: "Reviewer holds authority for Review artifacts **(and mandatory assessment of Plan and Task Graph before Architect approval)**"

---

## Conclusion

The SOP and Status Rules are **comprehensive, well-structured, and mostly aligned**, but the **critical state machine inconsistency must be resolved before approval**. The SOP's simplified state diagram conflicts with Status Rules' explicit requirement for a Reviewed state before Plan and Task Graph approval.

**Recommendation:** **REJECT** this review pending corrections to the SOP state machine. Re-submit after updating the SOP to align with Status Rules' required state transitions.

---

## Evidence

1. **SOP Workflow State Machine** (Full State Diagram section) — shows PLAN_DRAFT → PLAN_APPROVED
2. **Status Rules Artifact Lifecycle Rules** (Plan entry) — defines Plan: Draft → Reviewed → Approved
3. **Status Rules Forbidden Transitions** — lists "Plan Draft → Approved (without review)" as forbidden
4. **Status Rules Approval Gates** — specifies Gate 2 and 3 require "Reviewer assessment"
5. **Project Analysis** — recommends all 8 phases including review gates

---

**Review Completed:** 2026-06-03  
**Next Action:** Architect re-approval after SOP corrections
