---
title: "Module Documentation: agent_runner_v2.state_defaults"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/state_defaults.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-state-defaults.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-20260723-6b49ca87 / 2026-07-23T21:17:05+08:00"
created: "2026-07-23T21:17:05+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.state_defaults

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### default_review_state()

**Signature**: `default_review_state()`

**Returns**: `dict[str, Any]`

---

#### default_task_execution_binding()

**Signature**: `default_task_execution_binding()`

**Returns**: `dict[str, Any]`

---

#### default_loop_context()

**Signature**: `default_loop_context(*, active: bool = False, loop_step: str | None = None, refine_step: str | None = None, target_artifact: str | None = None, review_file: str | None = None, iteration: int = 0, pre_refine_checksum: str | None = None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `active` | `bool` | `False` | -- |
| `loop_step` | `str | None` | `None` | -- |
| `refine_step` | `str | None` | `None` | -- |
| `target_artifact` | `str | None` | `None` | -- |
| `review_file` | `str | None` | `None` | -- |
| `iteration` | `int` | `0` | -- |
| `pre_refine_checksum` | `str | None` | `None` | -- |

**Returns**: `dict[str, Any]`

---

#### default_replan_context()

**Signature**: `default_replan_context(*, active: bool = False, source_review_step: str | None = None, replan_step: str | None = None, target_artifact: str | None = None, review_file: str | None = None, replan_attempt: int = 0, pre_replan_checksum: str | None = None, trigger_reason: str | None = None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `active` | `bool` | `False` | -- |
| `source_review_step` | `str | None` | `None` | -- |
| `replan_step` | `str | None` | `None` | -- |
| `target_artifact` | `str | None` | `None` | -- |
| `review_file` | `str | None` | `None` | -- |
| `replan_attempt` | `int` | `0` | -- |
| `pre_replan_checksum` | `str | None` | `None` | -- |
| `trigger_reason` | `str | None` | `None` | -- |

**Returns**: `dict[str, Any]`

---


### 2.3 Constants / Configuration

No public constants.


## 3. Error Handling

No documented exceptions.


## 4. Testing

### 4.1 Test Coverage

| Test File | Coverage Area |
|-----------|---------------|
| (none) | No test references found |


## 5. Change Log

| Date | Change | Verified By |
|------|--------|-------------|
| 2026-07-23 | Initial baseline generated from repository scan | sdlc_00_codebase_v1 |
