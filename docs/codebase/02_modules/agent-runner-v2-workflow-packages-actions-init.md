---
title: "Module Documentation: agent_runner_v2"
template_id: "CB-02"
status: "active"
module_path: "agent_runner_v2/workflow_packages/actions/__init__.py"
module_area: "package"
documentation_mode: "stub"
owner_doc_path: "docs/codebase/02_modules/agent-runner-v2-workflow-packages-actions-init.md"
last_verified_by_change: "00_master_docs_bootstrap_v2 / 00DOC-20260710-0098bf53 / 2026-07-10T19:43:53+08:00"
created: "2026-07-10T19:43:53+08:00"
owner: "00_master_docs_bootstrap_v2"
---

# Module Documentation: agent_runner_v2

## 1. Module Overview

### 1.1 Purpose

Pluggable action decorator and registry for workflow packages.

### 1.2 Responsibility

This module belongs to the `package` area and is documented as `stub`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `action_result` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### action()

**Signature**: `action(name: str | None = None)`

**Purpose**: Decorator that registers a function as a runner action.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `name` | `str | None` | `None` | — |

**Returns**: `Callable[, ActionFn]`

---

#### get_registered_actions()

**Signature**: `get_registered_actions()`

**Purpose**: Return a copy of all decorator-registered actions.

**Returns**: `dict[str, ActionFn]`

---

#### clear_registered_actions()

**Signature**: `clear_registered_actions()`

**Purpose**: Clear all decorator-registered actions (useful in tests).

**Returns**: `None`

---


### 2.3 Constants / Configuration

No public constants.


## 3. Error Handling

No documented exceptions.


## 4. Testing

### 4.1 Test Coverage

| Test File | Coverage Area |
|-----------|---------------|
| `tests/conftest.py` | `agent_runner_v2` |


## 5. Change Log

| Date | Change | Verified By |
|------|--------|-------------|
| 2026-07-10 | Initial baseline generated from repository scan | 00_master_docs_bootstrap_v2 |
