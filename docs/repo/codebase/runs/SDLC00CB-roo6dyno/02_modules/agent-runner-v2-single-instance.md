---
title: "Module Documentation: agent_runner_v2.single_instance"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/single_instance.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-single-instance.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-roo6dyno / 2026-08-05T23:43:32+08:00"
created: "2026-08-05T23:43:32+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.single_instance

## 1. Module Overview

### 1.1 Purpose

Cross-platform single-instance enforcement.

### 1.2 Responsibility

This module belongs to the `core` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `os` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `sys` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |

## 2. Public API

### 2.1 Classes

#### SingleInstanceMutex

**Purpose**: Cross-platform single-instance mutex.

**Methods**:

- `acquire()` -> `bool` -- Try to acquire the mutex.
- `release()` -> `None` -- Release the mutex (optional - auto-released on exit).


### 2.2 Functions

#### check_single_instance()

**Signature**: `check_single_instance(name: str, error_message: str, runtime_dir: Path | None = None)`

**Purpose**: Check if this is the only instance, exit if not.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `name` | `str` | -- | Mutex name (e.g., "ukbe-runner-daemon") |
| `error_message` | `str` | -- | Message to print if already running |
| `runtime_dir` | `Path | None` | `None` | Optional runtime directory for lock files |

**Returns**: `SingleInstanceMutex | None`

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
