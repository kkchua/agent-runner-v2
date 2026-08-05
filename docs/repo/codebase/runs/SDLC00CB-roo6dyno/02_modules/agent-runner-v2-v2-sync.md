---
title: "Module Documentation: agent_runner_v2.v2.sync"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/v2/sync.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-v2-sync.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-roo6dyno / 2026-08-05T23:43:32+08:00"
created: "2026-08-05T23:43:32+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.v2.sync

## 1. Module Overview

### 1.1 Purpose

V2 sync adapter -- outcome-only sync and config resolution.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `os` | stdlib module | imported dependency |
| `time` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `config_loader` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### resolve_v2_backend_url()

**Signature**: `resolve_v2_backend_url()`

**Purpose**: Resolve the V2 backend URL from config or environment.

**Returns**: `str | None`

---

#### resolve_v2_api_key()

**Signature**: `resolve_v2_api_key()`

**Purpose**: Resolve the V2 backend API key from config or environment.

**Returns**: `str | None`

---

#### is_v2_enabled()

**Signature**: `is_v2_enabled()`

**Purpose**: Return True if V2 backend is configured and should be used.

**Returns**: `bool`

---

#### build_v2_outcome_payload()

**Signature**: `build_v2_outcome_payload(*, step_result: dict[str, Any], state: dict[str, Any])`

**Purpose**: Build an outcome-only payload for the V2 backend.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `step_result` | `dict[str, Any]` | -- | -- |
| `state` | `dict[str, Any]` | -- | -- |

**Returns**: `dict[str, Any]`

---

#### sync_outcome_v2()

**Signature**: `sync_outcome_v2(*, backend_url: str, step_run_id: str, step_result: dict[str, Any], state: dict[str, Any], max_attempts: int = 4, backoff_base: float = 1.0)`

**Purpose**: Send outcome to V2 backend and return the routing decision.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `backend_url` | `str` | -- | -- |
| `step_run_id` | `str` | -- | -- |
| `step_result` | `dict[str, Any]` | -- | -- |
| `state` | `dict[str, Any]` | -- | -- |
| `max_attempts` | `int` | `4` | -- |
| `backoff_base` | `float` | `1.0` | -- |

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
| 2026-08-05 | Initial baseline generated from repository scan | sdlc_00_codebase_v1 |
