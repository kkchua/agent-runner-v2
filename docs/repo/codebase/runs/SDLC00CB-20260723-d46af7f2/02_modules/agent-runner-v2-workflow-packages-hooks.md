---
title: "Module Documentation: agent_runner_v2.workflow_packages.hooks"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/workflow_packages/hooks.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-packages-hooks.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-20260723-d46af7f2 / 2026-07-23T20:54:20+08:00"
created: "2026-07-23T20:54:20+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.workflow_packages.hooks

## 1. Module Overview

### 1.1 Purpose

Scanner and lifecycle hook dispatcher for workflow extensions.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `importlib.util` | stdlib module | imported dependency |
| `logging` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `extensions_base` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### get_extension()

**Signature**: `get_extension(template_group: str)`

**Purpose**: Return the cached extension instance for a workflow.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `template_group` | `str` | -- | Workflow package name (e.g. ``"sdlc_10_requirement_v1"``). |

**Returns**: `WorkflowExtensions | None`

---

#### get_legacy_context_hook()

**Signature**: `get_legacy_context_hook(template_group: str)`

**Purpose**: Return the legacy free-function ``build_context_extensions`` (or None).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `template_group` | `str` | -- | -- |

**Returns**: `Any | None`

---

#### scan_all()

**Signature**: `scan_all(hook_name: str, **kwargs: Any)`

**Purpose**: Call *hook_name* on every discovered workflow's Extensions class.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `hook_name` | `str` | -- | Method name on ``WorkflowExtensions`` (e.g. |
| `**kwargs` | `Any` | -- | -- |

**Returns**: `dict[str, Any]`

---

#### register_all_artifact_keys()

**Signature**: `register_all_artifact_keys(*, job_id: str, mode: str)`

**Purpose**: Call ``register_artifact_keys()`` on all workflows.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `job_id` | `str` | -- | -- |
| `mode` | `str` | -- | -- |

**Returns**: `None`

---

#### init_all()

**Signature**: `init_all(*, workspace_root: Path, runner_home: Path)`

**Purpose**: Call ``init()`` on all workflows.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `workspace_root` | `Path` | -- | -- |
| `runner_home` | `Path` | -- | -- |

**Returns**: `None`

---

#### clear_cache()

**Signature**: `clear_cache()`

**Purpose**: Clear all cached extensions and modules.

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
| 2026-07-23 | Initial baseline generated from repository scan | sdlc_00_codebase_v1 |
