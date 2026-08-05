---
title: "Module Documentation: agent_runner_v2.backend_execution"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/backend_execution.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-backend-execution.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-roo6dyno / 2026-08-05T23:43:32+08:00"
created: "2026-08-05T23:43:32+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.backend_execution

## 1. Module Overview

### 1.1 Purpose

[V1 DEPRECATED] Backend execution -- V1 sync and execution logic.

### 1.2 Responsibility

This module belongs to the `core` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `execution_request` | external module | repository dependency |
| `execution_result` | external module | repository dependency |
| `runtime_context` | external module | repository dependency |
| `state_defaults` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### build_group_cfg_from_execution_spec()

**Signature**: `build_group_cfg_from_execution_spec(spec: dict[str, Any], template_group: str, step_name: str)`

**Purpose**: Build group and step config from execution spec.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `spec` | `dict[str, Any]` | -- | -- |
| `template_group` | `str` | -- | -- |
| `step_name` | `str` | -- | -- |

**Returns**: `tuple[dict[str, Any], dict[str, Any]]`

---

#### execute_step_command()

**Signature**: `execute_step_command(request_path: Path, result_path: Path | None = None, *, hooks: Any)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `request_path` | `Path` | -- | -- |
| `result_path` | `Path | None` | `None` | -- |
| `hooks` | `Any` | -- | -- |

**Returns**: `int`

---

#### build_execution_state()

**Signature**: `build_execution_state(*, request: ExecutionRequest, group_cfg: dict[str, Any], hooks: Any)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `request` | `ExecutionRequest` | -- | -- |
| `group_cfg` | `dict[str, Any]` | -- | -- |
| `hooks` | `Any` | -- | -- |

**Returns**: `dict[str, Any]`

---

#### publish_backend_artifacts()

**Signature**: `publish_backend_artifacts(*, state: dict[str, Any], step: str, artifacts: dict[str, str], project_root: Path, hooks: Any)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | -- | -- |
| `step` | `str` | -- | -- |
| `artifacts` | `dict[str, str]` | -- | -- |
| `project_root` | `Path` | -- | -- |
| `hooks` | `Any` | -- | -- |

**Returns**: `dict[str, str]`

---

#### execute_backend_step_request()

**Signature**: `execute_backend_step_request(*, request: ExecutionRequest, group_cfg: dict[str, Any], step_cfg: dict[str, Any], state: dict[str, Any], effective_root: Path, hooks: Any)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `request` | `ExecutionRequest` | -- | -- |
| `group_cfg` | `dict[str, Any]` | -- | -- |
| `step_cfg` | `dict[str, Any]` | -- | -- |
| `state` | `dict[str, Any]` | -- | -- |
| `effective_root` | `Path` | -- | -- |
| `hooks` | `Any` | -- | -- |

**Returns**: `ExecutionResult`

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
| 2026-08-05 | Initial baseline generated from repository scan | sdlc_00_codebase_v1 |
