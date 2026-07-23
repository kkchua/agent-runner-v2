---
title: "Module Documentation: agent_runner_v2.runner_logger"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/runner_logger.py"
module_area: "backend"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-runner-logger.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-20260723-c66bc6aa / 2026-07-23T20:12:07+08:00"
created: "2026-07-23T20:12:07+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.runner_logger

## 1. Module Overview

### 1.1 Purpose

Structured logger for the agent runner.

### 1.2 Responsibility

This module belongs to the `backend` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `datetime` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `sys` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `runtime_context` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### log_event()

**Signature**: `log_event(step: str, coder: str, *, model: str = '', model_id: str = '', connection: str = '', auth_type: str = '', event: str = 'info', duration_ms: int | None = None, return_code: int | None = None, status: str = '', message: str = '')`

**Purpose**: Log one event to both console and file.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `step` | `str` | -- | -- |
| `coder` | `str` | -- | -- |
| `model` | `str` | `''` | -- |
| `model_id` | `str` | `''` | -- |
| `connection` | `str` | `''` | -- |
| `auth_type` | `str` | `''` | -- |
| `event` | `str` | `'info'` | -- |
| `duration_ms` | `int | None` | `None` | -- |
| `return_code` | `int | None` | `None` | -- |
| `status` | `str` | `''` | -- |
| `message` | `str` | `''` | -- |

**Returns**: `None`

---

#### log_invocation_start()

**Signature**: `log_invocation_start(step: str, coder: str, *, model: str = '', model_id: str = '', connection: str = '', auth_type: str = '', command: list[str] | None = None)`

**Purpose**: Log that a coder invocation is about to start.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `step` | `str` | -- | -- |
| `coder` | `str` | -- | -- |
| `model` | `str` | `''` | -- |
| `model_id` | `str` | `''` | -- |
| `connection` | `str` | `''` | -- |
| `auth_type` | `str` | `''` | -- |
| `command` | `list[str] | None` | `None` | -- |

**Returns**: `None`

---

#### log_invocation_result()

**Signature**: `log_invocation_result(step: str, coder: str, *, model: str = '', model_id: str = '', connection: str = '', auth_type: str = '', return_code: int, duration_ms: int, status: str, message: str = '', usage: dict[str, Any] | None = None)`

**Purpose**: Log the result of a coder invocation.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `step` | `str` | -- | -- |
| `coder` | `str` | -- | -- |
| `model` | `str` | `''` | -- |
| `model_id` | `str` | `''` | -- |
| `connection` | `str` | `''` | -- |
| `auth_type` | `str` | `''` | -- |
| `return_code` | `int` | -- | -- |
| `duration_ms` | `int` | -- | -- |
| `status` | `str` | -- | -- |
| `message` | `str` | `''` | -- |
| `usage` | `dict[str, Any] | None` | `None` | -- |

**Returns**: `None`

---

#### log_error()

**Signature**: `log_error(step: str, coder: str, *, model: str = '', model_id: str = '', connection: str = '', auth_type: str = '', error: str = '')`

**Purpose**: Log a coder invocation error.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `step` | `str` | -- | -- |
| `coder` | `str` | -- | -- |
| `model` | `str` | `''` | -- |
| `model_id` | `str` | `''` | -- |
| `connection` | `str` | `''` | -- |
| `auth_type` | `str` | `''` | -- |
| `error` | `str` | `''` | -- |

**Returns**: `None`

---

#### log_resolver()

**Signature**: `log_resolver(coder_input: str, resolved: str, *, is_alias: bool)`

**Purpose**: Log coder alias resolution.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `coder_input` | `str` | -- | -- |
| `resolved` | `str` | -- | -- |
| `is_alias` | `bool` | -- | -- |

**Returns**: `None`

---


### 2.3 Constants / Configuration

| Name | Purpose |
|------|--------|
| `_COLOURS` | module configuration |
| `_COLOUR_SUPPORTED` | module configuration |


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
