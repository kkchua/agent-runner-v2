---
title: "Module Documentation: agent_runner_v2.routing_runtime"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/routing_runtime.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-routing-runtime.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-mqe50g5d / 2026-08-06T05:49:37+08:00"
created: "2026-08-06T05:49:37+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.routing_runtime

## 1. Module Overview

### 1.1 Purpose

[V1 DEPRECATED] Routing runtime -- step routing and state advancement.

### 1.2 Responsibility

This module belongs to the `core` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `task_runtime` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### get_next_step_skipping_refine_replan()

**Signature**: `get_next_step_skipping_refine_replan(group_cfg: dict[str, Any], completed_steps: list[str])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_cfg` | `dict[str, Any]` | -- | -- |
| `completed_steps` | `list[str]` | -- | -- |

**Returns**: `str | None`

---

#### predict_next_step_after_approved()

**Signature**: `predict_next_step_after_approved(*, group_cfg: dict[str, Any], state: dict[str, Any], step: str, step_cfg: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_cfg` | `dict[str, Any]` | -- | -- |
| `state` | `dict[str, Any]` | -- | -- |
| `step` | `str` | -- | -- |
| `step_cfg` | `dict[str, Any]` | -- | -- |

**Returns**: `str | None`

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
| 2026-08-06 | Initial baseline generated from repository scan | sdlc_00_codebase_v1 |
