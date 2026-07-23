---
title: "Module Documentation: agent_runner_v2.operator_console.config"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/operator_console/config.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-operator-console-config.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-20260723-d46af7f2 / 2026-07-23T20:54:20+08:00"
created: "2026-07-23T20:54:20+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.operator_console.config

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `os` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `config_loader` | external module | repository dependency |
| `models` | external module | repository dependency |
| `runtime_context` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

#### ConsoleConfigError

**Inherits from**: `RuntimeError`

**Purpose**: Public class


### 2.2 Functions

#### load_global_settings()

**Signature**: `load_global_settings()`

**Returns**: `GlobalSettings`

---

#### resolve_console_config_path()

**Signature**: `resolve_console_config_path(path: str | None = None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `path` | `str | None` | `None` | -- |

**Returns**: `Path`

---

#### load_console_config()

**Signature**: `load_console_config(path: str | None = None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `path` | `str | None` | `None` | -- |

**Returns**: `ConsoleConfig`

---


### 2.3 Constants / Configuration

| Name | Purpose |
|------|--------|
| `DEFAULT_CONSOLE_CONFIG_PATH` | module configuration |


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
