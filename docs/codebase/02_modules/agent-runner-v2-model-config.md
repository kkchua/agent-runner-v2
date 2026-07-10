---
title: "Module Documentation: agent_runner_v2.model_config"
template_id: "CB-02"
status: "active"
module_path: "agent_runner_v2/model_config.py"
module_area: "coder"
documentation_mode: "summary"
owner_doc_path: "docs/codebase/02_modules/agent-runner-v2-model-config.md"
last_verified_by_change: "00_master_docs_bootstrap_v1 / 00DOC-GEN-20260710-004 / 2026-07-10T09:40:54+08:00"
created: "2026-07-10T09:40:54+08:00"
owner: "00_master_docs_bootstrap_v1"
---

# Module Documentation: agent_runner_v2.model_config

## 1. Module Overview

### 1.1 Purpose

Model alias resolver for the agent runner.

### 1.2 Responsibility

This module belongs to the `coder` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `os` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `runtime_context` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### load_model_mapping()

**Signature**: `load_model_mapping(path: Path | str | None = None)`

**Purpose**: Load the model mapping file.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `path` | `Path | str | None` | `None` | — |

**Returns**: `dict[str, dict[str, Any]]`

---

#### resolve_coder()

**Signature**: `resolve_coder(name: str, *, mapping_path: Path | str | None = None)`

**Purpose**: Resolve a coder name into a full invocation config.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `name` | `str` | — | — |
| `mapping_path` | `Path | str | None` | `None` | — |

**Returns**: `dict[str, Any] | None`

---

#### get_api_key()

**Signature**: `get_api_key(coder_config: dict[str, Any])`

**Purpose**: Retrieve the API key for a coder config from environment variables.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `coder_config` | `dict[str, Any]` | — | — |

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
| 2026-07-10 | Initial baseline generated from repository scan | 00_master_docs_bootstrap_v1 |
