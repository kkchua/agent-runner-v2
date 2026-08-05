---
title: "Module Documentation: agent_runner_v2.workflow_router"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/workflow_router.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-router.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-bgmxg5vi / 2026-08-06T07:04:04+08:00"
created: "2026-08-06T07:04:04+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.workflow_router

## 1. Module Overview

### 1.1 Purpose

[V1 DEPRECATED] workflow_router.py -- Post-step routing for agent_runner_v2.

### 1.2 Responsibility

This module belongs to the `core` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `datetime` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `re` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `coder_adapters` | external module | repository dependency |
| `constants` | external module | repository dependency |
| `exceptions` | external module | repository dependency |
| `failure_runtime` | external module | repository dependency |
| `job_state` | external module | repository dependency |
| `notification_manager` | external module | repository dependency |
| `notifications` | external module | repository dependency |
| `recovery_runtime` | external module | repository dependency |
| `runtime_context` | external module | repository dependency |
| `step_runner` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### route_after_step()

**Signature**: `route_after_step(*, group_name: str, group_cfg: dict, state: dict, step: str, step_cfg: dict, step_result: StepResult, coder_used: str, max_rejects: int)`

**Purpose**: Route job state after a successful step invocation.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | -- | -- |
| `group_cfg` | `dict` | -- | -- |
| `state` | `dict` | -- | -- |
| `step` | `str` | -- | -- |
| `step_cfg` | `dict` | -- | -- |
| `step_result` | `StepResult` | -- | -- |
| `coder_used` | `str` | -- | -- |
| `max_rejects` | `int` | -- | -- |

**Returns**: `tuple[dict, int]`

---

#### route_after_failure()

**Signature**: `route_after_failure(*, group_name: str, state: dict, step: str, step_cfg: dict | None = None, coder_used: str, exc: Exception, max_rejects: int, usage_data: dict)`

**Purpose**: Route job state after a hard failure (exception from run_step).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | -- | -- |
| `state` | `dict` | -- | -- |
| `step` | `str` | -- | -- |
| `step_cfg` | `dict | None` | `None` | -- |
| `coder_used` | `str` | -- | -- |
| `exc` | `Exception` | -- | -- |
| `max_rejects` | `int` | -- | -- |
| `usage_data` | `dict` | -- | -- |

**Returns**: `tuple[dict, int]`

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
