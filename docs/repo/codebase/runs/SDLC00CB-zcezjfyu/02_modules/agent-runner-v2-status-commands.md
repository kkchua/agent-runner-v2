---
title: "Module Documentation: agent_runner_v2.status_commands"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/status_commands.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-status-commands.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-zcezjfyu / 2026-08-05T13:02:54+08:00"
created: "2026-08-05T13:02:54+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.status_commands

## 1. Module Overview

### 1.1 Purpose

Show status of daemon and workers.

### 1.2 Responsibility

This module belongs to the `core` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `subprocess` | stdlib module | imported dependency |
| `sys` | stdlib module | imported dependency |
| `time` | stdlib module | imported dependency |
| `config_loader` | external module | repository dependency |
| `runtime_context` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### main()

**Signature**: `main(argv: list[str] | None = None)`

**Purpose**: Show status of daemon and workers.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `argv` | `list[str] | None` | `None` | -- |

**Returns**: `int`

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
