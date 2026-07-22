# 📋 Implementation Plan: {{TASK_ID}} — {{TASK_TITLE}}

---

## 📌 Metadata

* **Doc Type:** 04_implementation_plan
* **Template Version:** v1
* **Plan ID:** {{PLAN_ID}}
* **Task ID:** {{TASK_ID}}
* **Title:** {{TASK_TITLE}}
* **Status:** draft
* **Created At:** {{DATE}}
* **Author:** implementation_planner

---

## 🎯 Objective

Describe how the task will be implemented.

* Focus on **HOW**, not WHAT
* Must align strictly with task contract
* No code in this section

---

## 📥 Inputs

| Type           | Reference            |
| -------------- | -------------------- |
| Task Document  | {{TASK_DOC_PATH}}    |
| Plan Document  | {{PLAN_DOC_PATH}}    |
| Dependencies   | {{DEPENDENCY_TASKS}} |
| Reference Code | {{REFERENCE_PATHS}}  |

---

## 📤 Outputs

| Artifact   | Path       | Description       |
| ---------- | ---------- | ----------------- |
| {{FILE_1}} | {{PATH_1}} | {{DESCRIPTION_1}} |
| {{FILE_2}} | {{PATH_2}} | {{DESCRIPTION_2}} |

---

## 🧠 Scope Clarification

### ✅ Included

* Explicitly describe what will be implemented

### ❌ Excluded

* List what is intentionally NOT part of this task
* Prevent scope creep

---

## 📦 File Plan (MANDATORY)

List ALL files to be created or modified.

```text
<repo_root>/
├── path/to/file1.py      [NEW]
├── path/to/file2.py      [MODIFY]
├── path/to/file3.py      [NEW]
```

---

## 🧩 Module Responsibilities

Describe what each file/module is responsible for.

### file1.py

* Responsibility:
* Key behavior:

### file2.py

* Responsibility:
* Key behavior:

---

## ♻️ Reuse Strategy (CRITICAL)

List existing components to reuse.

| Component    | Location | Usage        |
| ------------ | -------- | ------------ |
| {{MODULE_1}} | {{PATH}} | {{HOW_USED}} |

Rules:

* Prefer reuse over reimplementation
* Only create new logic if reuse is not possible

---

## 🔄 Data Flow

Describe execution flow step-by-step.

```text
Input → Processing → Transformation → Output
```

Example:

1. Receive input from runtime
2. Transform into internal model
3. Apply processing logic
4. Produce output artifact

---

## 🧪 Test Plan

### Test Files

```text
tests/unit/.../{{TEST_FILE}}
```

### Test Cases

* test_case_01 — description
* test_case_02 — description

### Test Constraints

* No external dependencies
* Deterministic results
* Use fixtures/mock data

---

## 🔒 Constraints

* Do NOT modify unrelated modules
* Do NOT introduce new architecture layers
* Must follow task scope strictly
* Must maintain compatibility with existing system

---

## ⚠️ Risks & Mitigations

| Risk       | Impact     | Mitigation     |
| ---------- | ---------- | -------------- |
| {{RISK_1}} | {{IMPACT}} | {{MITIGATION}} |

---

## 📦 Dependencies

* {{DEPENDENCY_TASK_1}}
* {{DEPENDENCY_TASK_2}}

---

## 🧾 Notes

* Any additional implementation considerations
* Assumptions made during planning

---

## ✅ Ready for Execution

This plan is ready for the Executor agent if:

* File plan is complete
* Scope is clearly bounded
* Reuse strategy is defined
* No ambiguity remains
