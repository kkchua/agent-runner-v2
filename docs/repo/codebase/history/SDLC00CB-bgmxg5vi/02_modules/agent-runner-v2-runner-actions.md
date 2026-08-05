---
title: "Module Documentation: agent_runner_v2.runner_actions"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/runner_actions.py"
module_area: "schema"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-runner-actions.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-20260723-e1c86100 / 2026-07-23T21:41:19+08:00"
created: "2026-07-23T21:41:19+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.runner_actions

## 1. Module Overview

### 1.1 Purpose

runner_actions.py -- Registry and dispatch for non-coder step actions.

### 1.2 Responsibility

This module belongs to the `schema` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `logging` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `action_result` | external module | repository dependency |
| `actions.copy_artifact` | external module | repository dependency |
| `actions.finalize_bootstrap` | external module | repository dependency |
| `actions.promote_artifact` | external module | repository dependency |
| `actions.promote_init` | external module | repository dependency |
| `actions.scan_repo_codebase` | external module | repository dependency |
| `actions.sdlc_shared_actions` | external module | repository dependency |
| `actions.step_completion` | external module | repository dependency |
| `actions.sync_codebase_docs` | external module | repository dependency |
| `actions.sync_system_docs` | external module | repository dependency |
| `actions.validate_codebase_docs` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### execute()

**Signature**: `execute(*, action_name: str, context: dict[str, str], state: dict, step_cfg: dict, step: str, project_root: Path)`

**Purpose**: Dispatch to a registered action function.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `action_name` | `str` | -- | -- |
| `context` | `dict[str, str]` | -- | -- |
| `state` | `dict` | -- | -- |
| `step_cfg` | `dict` | -- | -- |
| `step` | `str` | -- | -- |
| `project_root` | `Path` | -- | -- |

**Returns**: `ActionResult`

**Raises**:

- `KeyError` -- if action_name is not found in either registry.
- `Exception` -- action-specific failures (caller routes to failure).

---

#### get_registered_actions()

**Signature**: `get_registered_actions()`

**Purpose**: Return sorted list of registered action names.

**Returns**: `list[str]`

---


### 2.3 Constants / Configuration

No public constants.


## 3. Error Handling

| Exception | When | Raised By |
|-----------|------|----------|
| `Exception` | action-specific failures (caller routes to failure). | `execute` |
| `KeyError` | if action_name is not found in either registry. | `execute` |


## 4. Testing

### 4.1 Test Coverage

| Test File | Coverage Area |
|-----------|---------------|
| (none) | No test references found |


## 5. Change Log

| Date | Change | Verified By |
|------|--------|-------------|
| 2026-07-23 | Initial baseline generated from repository scan | sdlc_00_codebase_v1 |
