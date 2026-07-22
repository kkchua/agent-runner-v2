# 🤖 UKBE Agent System Registry and Orchestration Contract (v2)

## 📌 Metadata
- Doc Type: 08_agent_registry
- Template Version: v2
- Document ID: AGENTS-SYSTEM-v2
- Status: active
- Created At: 2026-04-08
- Owner: UKBE architect

---

## 🎯 Purpose

Define the authoritative registry, handoff contracts, execution order, and coordination rules for the UKBE multi-agent delivery system.

This document is the system-level orchestration contract for:
- Planner
- Task Decomposer
- Implementation Planner
- Executor
- Reviewer
- Memory Manager

It ensures:
- deterministic handoffs
- clear role boundaries
- explicit workflow order
- document-driven execution
- future automation readiness

---

## 🧠 Core Principle

> Agents do not coordinate by conversation memory alone.  
> Agents coordinate through approved documents, explicit status, and typed handoff contracts.

---

## 🔗 Governing Documents

All agents MUST follow:
1. `docs/delivery/08_agents/DELIVERY_STATUS_RULES_v1.md`
2. `docs/delivery/00_templates/WORKFLOW_SOP_v1.md`
3. Relevant canonical specs for the initiative or task
4. Their own individual agent contract in `docs/delivery/08_agents/`

If there is conflict:
1. Canonical specs
2. DELIVERY_STATUS_RULES_v1
3. WORKFLOW_SOP_v1
4. AGENTS.md
5. Individual agent file

---

## 🧩 Agent Registry

| Agent | Role | Primary Input | Primary Output | Folder |
|------|------|---------------|----------------|--------|
| Planner | planning | `01_initiative` | `02_plan` | `02_plans/` |
| Task Decomposer | task decomposition | `02_plan` | task-graph artifact + `03_task` | `02_plans/artifacts/`, `03_tasks/` |
| Implementation Planner | implementation planning | `03_task` | `04_implementation_plan` | `04_implementation_plans/` |
| Executor | code execution | `04_implementation_plan` | code + tests + execution summary | repo files |
| Reviewer | review / validation | task, plan, implementation, evidence | `05_review` / `05_validation` | `05_reviews/` |
| Memory Manager | delivery memory maintenance | approved artifacts | memory updates | `06_memory/` |

---

## 🧭 Workflow Order

The standard delivery flow is:

1. Initiative created
2. Plan proposed
3. Plan approved
4. Task graph proposed
5. Task graph approved
6. Task document created
7. Task reviewed and accepted for execution
8. Implementation plan proposed
9. Implementation plan approved
10. Implementation executed
11. Validation plan proposed
12. Validation approved
13. Validation executed
14. Task approved / completed
15. Memory updated if required

---

## 🔄 Handoff Contracts

### 1. Architect / Human → Planner
**Input**
- Approved or active initiative document
- Relevant specs
- Optional supporting context

**Output**
- One plan document in `02_plans/`

**Rule**
- Planner must not produce tasks directly

---

### 2. Planner → Task Decomposer
**Input**
- Approved plan
- Relevant specs
- Optional reviewer guidance

**Output**
- Task graph artifact
- One or more task documents in `03_tasks/`

**Rule**
- Task Decomposer must define WHAT to build, not HOW to code it

---

### 3. Task Decomposer → Reviewer
**Input**
- Task document
- Linked plan

**Output**
- Review decision for execution readiness

**Rule**
- Reviewer checks scope integrity, readiness, and missing constraints without expanding scope

---

### 4. Reviewer / Architect → Implementation Planner
**Input**
- Approved task document
- Linked plan
- Review findings if applicable

**Output**
- One implementation plan in `04_implementation_plans/`

**Rule**
- Implementation Planner defines HOW to execute within task scope, without writing code

---

### 5. Implementation Planner → Executor
**Input**
- Approved implementation plan
- Linked task
- Linked plan
- Relevant code references

**Output**
- Code changes
- Tests
- Execution summary / implementation notes if required

**Rule**
- Executor must follow the implementation plan exactly and must not redesign the architecture

---

### 6. Executor → Reviewer
**Input**
- Implemented code
- Tests
- Task document
- Implementation plan

**Output**
- Validation plan and/or validation result
- Review / validation decision

**Rule**
- Reviewer validates correctness, evidence, and task completion against the task and implementation plan

---

### 7. Reviewer / Architect → Memory Manager
**Input**
- Approved plans, tasks, reviews, and implementation outcomes

**Output**
- Delivery memory update if warranted

**Rule**
- Memory Manager records stable knowledge only; do not persist transient or rejected material as durable memory

---

## ✅ Entry Criteria by Agent

### Planner
May start only when:
- initiative exists
- initiative is active or approved
- governing references are available

### Task Decomposer
May start only when:
- plan exists
- plan is approved or explicitly authorized for decomposition

### Implementation Planner
May start only when:
- task exists
- task is approved for implementation planning
- scope is stable enough to define file-level execution

### Executor
May start only when:
- implementation plan exists
- implementation plan is approved
- task is not blocked/cancelled/superseded

### Reviewer
May start when:
- there is a review target
- input artifacts are available
- evidence exists or can be produced

### Memory Manager
May start only when:
- final approved artifacts exist
- the knowledge is worth preserving

---

## ⛔ Exit Criteria by Agent

### Planner
Complete when:
- one valid plan document is created
- plan is saved in the correct folder
- initiative linkage is preserved

### Task Decomposer
Complete when:
- task graph artifact is saved
- task document(s) are created and linked correctly

### Implementation Planner
Complete when:
- one valid implementation plan is created
- linked Task ID and Plan ID are preserved
- file plan and test plan are explicit

### Executor
Complete when:
- required code changes are made
- required tests are added/updated
- implementation remains in scope
- execution-ready output exists for review

### Reviewer
Complete when:
- review or validation document is produced
- decision is explicit: approved / rejected
- evidence is recorded

### Memory Manager
Complete when:
- stable memory update is saved in the correct location
- source links are preserved

---

## 📏 Cross-Agent Rules

### Rule 1 — Role Isolation
Each agent must stay within its assigned role.
No silent cross-role behavior.

### Rule 2 — Document-First
Every meaningful output must exist as a file artifact.

### Rule 3 — No Scope Drift
Agents must not silently widen objectives, redesign architecture, or add unapproved features.

### Rule 4 — Explicit Decisions
Review and validation artifacts must include an explicit decision and supporting evidence.

### Rule 5 — Canonical Linking
Every output must preserve upstream IDs:
- Initiative ID
- Plan ID
- Task ID
- Related review / validation IDs where relevant

### Rule 6 — Deterministic Naming
All output files must follow the naming convention of their document type.

### Rule 7 — Approved Inputs Only
Downstream agents should prefer approved upstream artifacts. If operating on draft materials, that must be explicitly stated.

### Rule 8 — Rejected Means Stop
If a review or validation result is rejected, no downstream execution may continue until the issue is resolved.

### Rule 9 — Superseded Means Inactive
Superseded artifacts must not be used as execution sources.

### Rule 10 — Traceability is Mandatory
Every output must reference the governing input documents and key dependencies.

---

## 🧪 Validation Model

Validation is independent from implementation.
Implementation completion does not equal approval.

Required pattern:
- implementation completed
- validation performed
- review decision recorded
- architect approves where required

---

## 📂 Folder Responsibilities

| Folder | Purpose |
|------|---------|
| `00_templates/` | canonical output templates and SOP |
| `01_initiatives/` | initiatives |
| `02_plans/` | master plans |
| `02_plans/artifacts/` | task graphs and plan-side artifacts |
| `03_tasks/` | task contracts |
| `04_implementation_plans/` | implementation plans |
| `05_reviews/` | review and validation docs |
| `06_memory/` | delivery memory |
| `08_agents/` | agent contracts and coordination rules |

---

## 🚀 Future Automation Notes

This registry is designed so a future control plane can:
- route work by document type
- enforce state transitions automatically
- validate entry/exit criteria
- trigger the next agent deterministically

---

## 📝 Notes

- This document defines orchestration, not project scope.
- Individual agent files define role-specific contracts.
- Templates remain the output shape authority for each document type.

---

## ✅ Conclusion

`AGENTS.md` is the coordination layer for the UKBE AI Dev Workflow.

It guarantees:
- stable handoffs
- role clarity
- workflow discipline
- readiness for later automation
