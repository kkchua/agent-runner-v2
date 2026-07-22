# 🧠 UKBE AI Dev Workflow SOP v1 (Agent-Orchestrated Delivery System)

## 📌 Metadata

* Document Type: SOP
* Version: v1.0
* Status: Active
* Owner: Architect
* Created At: 2026-04-08

---

# 🎯 Purpose

Define a standardized, repeatable workflow for coordinating multi-agent software development using:

* Claude (Planner / Decomposer)
* Codex (Reviewer / Tester)
* Qwen (Executor)
* ChatGPT (Architect support)

This SOP ensures:

* Deterministic delivery
* Clear ownership per stage
* Structured artifacts
* Scalable orchestration (future automation-ready)

---

# 🧠 Core Principle

> The system is **document-driven + state-driven**, not prompt-driven.

Every step:

* Produces a document artifact
* Transitions a workflow state
* Is validated before moving forward

## Authority Precedence

When interpretation conflicts occur:

1. Runner runtime enforcement logic
2. `DELIVERY_STATUS_RULES_v1.md` / `WORKFLOW_SOP_v1.md`
3. Artifact metadata / document status fields
4. Artifact body content / prose descriptions

Lower-precedence layers may describe higher-precedence behavior, but may not override it.

## Workflow Approval Authority

- Workflow approval progression is process-owned and runner-enforced.
- Artifact metadata may mirror workflow state for readability, but does not itself authorize downstream execution.
- Artifact metadata is observational/documentary unless explicitly reconciled by runner-owned synchronization logic.
- Human approval that advances workflow must be recorded through the runner-owned approval action.
- Manual document edits alone do not advance workflow state.

---

# ⚙️ Workflow State Machine

```
INITIATIVE_CREATED
    ↓
PLAN_PROPOSED
    ↓
PLAN_APPROVED
    ↓
TASK_GRAPH_PROPOSED
    ↓
TASK_GRAPH_APPROVED
    ↓
TASK_DEFINED
    ↓
TASK_REVIEWED
    ↓
IMPLEMENTATION_PLAN_PROPOSED
    ↓
IMPLEMENTATION_APPROVED
    ↓
IMPLEMENTATION_DONE
    ↓
VALIDATION_PLAN_PROPOSED
    ↓
VALIDATION_APPROVED
    ↓
VALIDATION_DONE
    ↓
COMPLETED
```

---

# 🧩 Agent Roles

| Role      | Agent           | Responsibility                     |
| --------- | --------------- | ---------------------------------- |
| Architect | Human + ChatGPT | Define initiative, direction       |
| Planner   | Claude          | Create plans and task graphs       |
| Reviewer  | Codex           | Validate correctness and readiness |
| Executor  | Qwen            | Implement code and tests           |
| Tester    | Codex / Claude  | Validate implementation            |

---

# 🚀 Workflow Phases

---

## 🔹 Phase 0 — Initiative Creation

**Owner:** Architect

### Input

* Idea / feature / fix

### Action

* Create initiative document

### Output

```
docs/delivery/01_initiatives/INIT-*.md
```

### State

```
INITIATIVE_CREATED
```

---

## 🔹 Phase 1 — Planning

**Agent:** Claude (Planner)

### Input

* Initiative doc
* Relevant specs

### Action

* Generate Master PLAN

### Output

```
docs/delivery/02_plans/PLAN-*.md
```

### State Transition

```
PLAN_PROPOSED → PLAN_APPROVED
```

### Approval Rule

- Approval mechanics for this phase are owned by the workflow system, not by PLAN prose content.
- PLAN documents may reference existing workflow gates, but must not redefine approval authority unless the governing initiative explicitly declares workflow governance in scope.

---

## 🔹 Phase 2 — Task Decomposition

**Agent:** Claude (Task Decomposer)

### Input

* Approved PLAN

### Action

1. Generate task graph
2. Await approval
3. Generate task document

### Outputs

Task Graph:

```
docs/delivery/02_plans/artifacts/
```

Task Doc:

```
docs/delivery/03_tasks/TASK-*.md
```

### State Transition

```
TASK_GRAPH_PROPOSED → TASK_GRAPH_APPROVED → TASK_DEFINED
```

### Approval Rule

- Task graph approval progression is owned by workflow governance and enforced by the runner.
- Task graph design artifacts may document dependencies and readiness, but must not redefine approval authority unless workflow governance is explicitly in scope for the governing initiative.

---

## 🔹 Phase 3 — Task Review

**Agent:** Codex (Reviewer)

### Input

* Task doc
* PLAN reference

### Action

* Validate:

  * Scope correctness
  * Missing steps
  * Execution readiness

### Output

```
docs/delivery/05_reviews/REVIEW-*.md
```

### Decision

* approved / rejected

### State Transition

```
TASK_DEFINED → TASK_REVIEWED
```

---

## 🔹 Phase 4 — Implementation Planning

**Agent:** Qwen

### Input

* Task doc

### Action

* Propose implementation plan

### Output

```
docs/delivery/04_implementation_plans/IMPL-*.md
```

### State Transition

```
IMPLEMENTATION_PLAN_PROPOSED → IMPLEMENTATION_APPROVED
```

---

## 🔹 Phase 5 — Implementation

**Agent:** Qwen

### Input

* Approved implementation plan

### Action

* Implement code
* Include unit tests

### Output

* Code changes
* Test files

### State Transition

```
IMPLEMENTATION_APPROVED → IMPLEMENTATION_DONE
```

---

## 🔹 Phase 6 — Validation

**Agent:** Codex / Claude

### Input

* Task doc
* Implementation output

### Action

1. Create validation plan
2. Execute validation

### Outputs

```
docs/delivery/05_reviews/VALIDATION-*.md
```

### State Transition

```
VALIDATION_PLAN_PROPOSED → VALIDATION_APPROVED → VALIDATION_DONE
```

---

## 🔹 Phase 7 — Completion

### Criteria

* Implementation validated
* All checks passed
* No outstanding issues

### State

```
COMPLETED
```

---

# 🧠 Standard Rules (CRITICAL)

## 1. DELIVERY_STATUS_RULES_v1 (Mandatory)

All agents MUST:

* Respect current state
* Not skip phases
* Not overwrite approved artifacts
* Only operate within assigned role

---

## 2. No Scope Drift

Agents MUST:

* Not expand beyond task scope
* Not introduce new features unless explicitly requested

---

## 3. Deterministic Outputs

All outputs MUST:

* Be structured
* Be reproducible
* Avoid ambiguity

---

## 4. Single Source of Truth

All logic MUST align with:

* Contract Builder spec
* Core Data Model
* Artifact spec

---

## 5. Document-First Execution

No step is considered complete unless:

* Output is saved as a document
* State transition is clear

---

# 📂 Folder Structure

```
docs/delivery/
├── 00_templates/
├── 01_initiatives/
├── 02_plans/
│   └── artifacts/
├── 03_tasks/
├── 04_implementation_plans/
├── 05_reviews/
```

---

# 🧪 Validation Philosophy

Validation is:

* Independent
* Structured
* Mandatory before completion

Validation includes:

* Unit tests
* Integration tests
* Logical consistency checks

---

# 🔄 Execution Model

Current:

> Human-orchestrated multi-agent workflow

Future:

> Fully automated AI Control Plane

---

# 🚀 Future Extensions (v2+)

* Job Manager (task orchestration engine)
* State tracking DB
* Agent routing automation
* UI control panel
* Parallel task execution
* Cost tracking + optimization

---

# 📝 Notes

* This SOP is the **foundation of the AI Software Factory**
* Designed to evolve into a fully automated system
* Current manual orchestration is intentional and part of validation phase

---

# ✅ Summary

This SOP ensures:

* Clear separation of roles
* Controlled execution flow
* High-quality outputs
* Scalable architecture

---

# 🔥 Final Principle

> “No guessing. No skipping. No drifting.
> Every step is explicit, validated, and traceable.”
