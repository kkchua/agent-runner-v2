# 🗺️ Task Graph Template

## 📌 Metadata
- Doc Type: 02_plan_artifact
- Template Version: v1
- Task Graph ID: TASK-GRAPH-{{YYYYMMDD}}-{{PLAN_ID}}
- Plan ID: {{PLAN_ID}}
- Initiative ID: {{INITIATIVE_ID}}
- Title: {{PLAN_TITLE}} — Task Graph
- Status: DRAFT | IN_REVIEW | PENDING_HUMAN_APPROVAL | CHANGES_REQUESTED | APPROVED | FINALIZED
- Created By: {{AUTHOR}}
- Created At: {{YYYY-MM-DD}}
- Review File Path: docs/delivery/02_plans/artifacts/TASK-GRAPH-{{YYYYMMDD}}-{{PLAN_ID}}.md
- Review Decision: PENDING | APPROVED | REJECTED
- Reviewer Step: {{REVIEWER_STEP or TBD}}
- Review Iteration: {{REVIEW_ITERATION or TBD}}
- Model Reviewer: {{MODEL_REVIEWER or TBD}}
- Reviewed At: {{YYYY-MM-DD or TBD}}
- Human Approval Decision: PENDING | APPROVED | REJECTED | NOT_REQUIRED
- Human Approved By: {{HUMAN_APPROVER or TBD}}
- Human Approved At: {{YYYY-MM-DD or TBD}}
- Final Decision: APPROVED | REJECTED | TBD
- Final Decision Source: MODEL | HUMAN | TBD
- Approved At: {{YYYY-MM-DD or TBD}}
- Finalized At: {{YYYY-MM-DD or TBD}}

---

## 🎯 Task Graph Objective
Describe how this task graph decomposes the linked plan into executable, testable, and reviewable tasks. Each task should be narrow, focused, and have clear dependencies.

---

## 📋 Task Graph

<!-- Task IDs below MUST match the Plan's `## 📋 Task Breakdown` table exactly.
     Copy the Task IDs verbatim from the plan — do not renumber or derive new ones. -->

### `TASK-{{YYYYMMDD}}-{{NN}}` — {{TASK_TITLE}}
**Description**: {{TASK_DESCRIPTION}}
**Owner**: {{OWNER}}
**Priority**: low | medium | high | critical
**Depends On**:
**Scope**: {{SCOPE_ITEM_REF}}; {{SUCCESS_CRITERIA_REF}}
**Deliverables**:
- `{{FILE_PATH}}` — {{DESCRIPTION}}
**Testability**: {{HOW_THIS_TASK_CAN_BE_TESTED}}
**Review Criteria**: {{WHAT_MUST_BE_TRUE_FOR_THIS_TASK_TO_PASS_REVIEW}}

### `TASK-{{YYYYMMDD}}-{{NN+1}}` — {{TASK_TITLE}}
**Description**: {{TASK_DESCRIPTION}}
**Owner**: {{OWNER}}
**Priority**: low | medium | high | critical
**Depends On**: TASK-{{YYYYMMDD}}-{{NN}}
**Scope**: {{SCOPE_ITEM_REF}}; {{SUCCESS_CRITERIA_REF}}
**Deliverables**:
- `{{FILE_PATH}}` — {{DESCRIPTION}}
**Testability**: {{HOW_THIS_TASK_CAN_BE_TESTED}}
**Review Criteria**: {{WHAT_MUST_BE_TRUE_FOR_THIS_TASK_TO_PASS_REVIEW}}

---

## 🔄 Execution Flow

**Track A — {{TRACK_A_NAME}}** (describe parallelism intent):
1. TASK-{{YYYYMMDD}}-{{NN}}
2. TASK-{{YYYYMMDD}}-{{NN+1}} (depends on {{NN}})

**Track B — {{TRACK_B_NAME}}** (optional; describe parallelism intent):
3. TASK-{{YYYYMMDD}}-{{NN+2}}

**Validation Layer** (parallel validation tracks — each validates its respective implementation track):
4. TASK-{{YYYYMMDD}}-{{NN+3}} (validates Track A / depends on {{NN}}, {{NN+1}})
5. TASK-{{YYYYMMDD}}-{{NN+4}} (validates Track B / depends on {{NN+2}})

---

## 📏 Task Success Criteria
Each task must meet its specific review criteria as defined above. Overall plan success requires all tasks to be completed and reviewed.

---

## 🔗 References
- Plan: `docs/delivery/02_plans/{{PLAN_FILE}}`
- Initiative: `docs/delivery/01_initiatives/{{INITIATIVE_FILE}}`
- Related architecture docs:
  - 

---

## 📝 Notes
- Tasks are designed to be narrow, executable, testable, and reviewable
- Dependencies follow the plan's execution tracks for parallel work where possible
- Each task has clear deliverables and review criteria
- Task completion order respects dependencies while maximising parallelism
