---
title: "Module Documentation: agent_runner_v2.submitter"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/submitter.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-submitter.md"
last_verified_by_change: "sdlc_00_codebase_scaffold_v1 / SDLC00CS-1zcrrbbs / 2026-08-17T21:19:17+08:00"
created: "2026-08-17T21:19:17+08:00"
owner: "sdlc_00_codebase_scaffold_v1"
---

# Module Documentation: agent_runner_v2.submitter

## 1. Module Overview

### 1.1 Purpose

submitter.py -- ComfyUI API client for agent-runner-v2.

### 1.2 Responsibility

This module belongs to the `core` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `dataclasses` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `os` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `time` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `urllib.error` | stdlib module | imported dependency |
| `urllib.request` | stdlib module | imported dependency |

## 2. Public API

### 2.1 Classes

#### SubmissionResult

**Decorators**: `@dataclass`

**Purpose**: Result of a single entry submission.

#### SubmissionSummary

**Decorators**: `@dataclass`

**Purpose**: Summary of a batch submission.


### 2.2 Functions

#### load_config()

**Signature**: `load_config(config_path: str | Path | None = None)`

**Purpose**: Load ComfyUI config from JSON file, resolving env var placeholders.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `config_path` | `str | Path | None` | `None` | -- |

**Returns**: `dict[str, Any]`

---

#### login()

**Signature**: `login(base_url: str, email: str, password: str)`

**Purpose**: Authenticate and return JWT token.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `base_url` | `str` | -- | -- |
| `email` | `str` | -- | -- |
| `password` | `str` | -- | -- |

**Returns**: `str`

---

#### execute_workflow()

**Signature**: `execute_workflow(base_url: str, token: str, workflow_key: str, entry: dict[str, Any], test_mode: bool = False)`

**Purpose**: Submit a single entry to the ComfyUI workflow.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `base_url` | `str` | -- | -- |
| `token` | `str` | -- | -- |
| `workflow_key` | `str` | -- | -- |
| `entry` | `dict[str, Any]` | -- | -- |
| `test_mode` | `bool` | `False` | -- |

**Returns**: `tuple[bool, str | None]`

---

#### submit_files()

**Signature**: `submit_files(run_dir: str | Path, *, workflow_key_override: str | None = None, test_mode: bool = False, config: dict | None = None)`

**Purpose**: Submit all JSON files in run_dir to ComfyUI.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `run_dir` | `str | Path` | -- | Directory containing *.json prompt files (from gen_prompts step). |
| `workflow_key_override` | `str | None` | `None` | If set, overrides workflowKey in all entries. |
| `test_mode` | `bool` | `False` | If True, sends test_mode=true in the request body. |
| `config` | `dict | None` | `None` | Pre-loaded config dict. If None, loads from default config file. |

**Returns**: `SubmissionSummary`

---

#### main()

**Signature**: `main()`

**Returns**: `int`

---


### 2.3 Constants / Configuration

| Name | Purpose |
|------|--------|
| `PACKAGE_ROOT` | module configuration |
| `DEFAULT_CONFIG_PATH` | module configuration |


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
| 2026-08-17 | Initial baseline generated from repository scan | sdlc_00_codebase_scaffold_v1 |
