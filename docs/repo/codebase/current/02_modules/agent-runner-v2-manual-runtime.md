---
title: "Module Documentation: agent_runner_v2.manual_runtime"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/manual_runtime.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-manual-runtime.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-bgmxg5vi / 2026-08-06T07:04:04+08:00"
created: "2026-08-06T07:04:04+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.manual_runtime

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `core` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `dataclasses` | stdlib module | imported dependency |
| `os` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `job_state` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

#### ManualRunResolution

**Decorators**: `@dataclass`

**Purpose**: Public class


### 2.2 Functions

#### sync_local_from_backend()

**Signature**: `sync_local_from_backend(state: dict[str, Any], backend_state: dict[str, Any])`

**Purpose**: Reconcile local job state with authoritative backend state.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | -- | -- |
| `backend_state` | `dict[str, Any]` | -- | -- |

**Returns**: `bool`

---

#### resolve_manual_run()

**Signature**: `resolve_manual_run(*, args: Any, group_cfg: dict[str, Any], hooks: Any, mode: str = 'manual')`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `args` | `Any` | -- | -- |
| `group_cfg` | `dict[str, Any]` | -- | -- |
| `hooks` | `Any` | -- | -- |
| `mode` | `str` | `'manual'` | -- |

**Returns**: `ManualRunResolution`

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
