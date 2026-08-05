---
title: "Module Documentation: agent_runner_v2.api_key_pool"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/api_key_pool.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-api-key-pool.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-zcezjfyu / 2026-08-05T13:02:54+08:00"
created: "2026-08-05T13:02:54+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.api_key_pool

## 1. Module Overview

### 1.1 Purpose

Round-robin API key pool for external API calls.

### 1.2 Responsibility

This module belongs to the `core` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `logging` | stdlib module | imported dependency |
| `os` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `re` | stdlib module | imported dependency |
| `threading` | stdlib module | imported dependency |

## 2. Public API

### 2.1 Classes

#### ApiKeyPool

**Purpose**: Round-robin pool of API keys loaded from environment variables.

**Methods**:

- `next_key()` -> `str` -- Get the next API key in round-robin order.
- `current_index()` -> `int` -- Get the index (0-based) of the last returned key.


### 2.2 Functions

#### mask_api_key()

**Signature**: `mask_api_key(key: str, show_last: int = 6)`

**Purpose**: Mask an API key for safe logging, showing only the last N characters.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `key` | `str` | -- | The API key to mask. |
| `show_last` | `int` | `6` | Number of trailing characters to reveal (default 6). |

**Returns**: `str`

---

#### load_env_from_project()

**Signature**: `load_env_from_project(project_root: Path | str | None = None)`

**Purpose**: Load environment variables from .env file in project root.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `project_root` | `Path | str | None` | `None` | Root path of the target repository. If None, uses |

**Returns**: `None`

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
