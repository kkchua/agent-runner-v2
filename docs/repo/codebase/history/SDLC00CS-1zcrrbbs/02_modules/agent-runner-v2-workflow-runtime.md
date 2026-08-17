---
title: "Module Documentation: agent_runner_v2.workflow_runtime"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/workflow_runtime.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-runtime.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-bgmxg5vi / 2026-08-06T07:04:04+08:00"
created: "2026-08-06T07:04:04+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.workflow_runtime

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `core` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `bundle_loader` | external module | repository dependency |
| `constants` | external module | repository dependency |
| `runtime_context` | external module | repository dependency |
| `workflow_packages.loader` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### ensure_delivery_folders()

**Signature**: `ensure_delivery_folders(target_root: Path)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `target_root` | `Path` | -- | -- |

**Returns**: `None`

---

#### load_group()

**Signature**: `load_group(group_name: str, *, workspace_root: Path | None = None, workflow_root: Path | None = None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | -- | -- |
| `workspace_root` | `Path | None` | `None` | -- |
| `workflow_root` | `Path | None` | `None` | -- |

**Returns**: `dict[str, Any]`

---

#### validate_static_reference_files()

**Signature**: `validate_static_reference_files(workspace_root: Path, *, group_cfg: dict[str, Any] | None = None, template_group: str = '')`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `workspace_root` | `Path` | -- | -- |
| `group_cfg` | `dict[str, Any] | None` | `None` | -- |
| `template_group` | `str` | `''` | -- |

**Returns**: `None`

---

#### missing_artifacts()

**Signature**: `missing_artifacts(keys: list[str], state: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `keys` | `list[str]` | -- | -- |
| `state` | `dict[str, Any]` | -- | -- |

**Returns**: `list[str]`

---

#### parse_key_value_pairs()

**Signature**: `parse_key_value_pairs(values: list[str])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `values` | `list[str]` | -- | -- |

**Returns**: `dict[str, str]`

---

#### build_config_from_request()

**Signature**: `build_config_from_request(template_group: str, step_name: str, *, workspace_root: Path | None = None, workflow_root: Path | None = None, step_execution_spec: dict[str, Any] | None = None)`

**Purpose**: Build group_cfg and step_cfg from request with fallback to spec.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `template_group` | `str` | -- | Template group identifier |
| `step_name` | `str` | -- | Step name to configure |
| `workspace_root` | `Path | None` | `None` | Workspace directory for plugin workflows |
| `workflow_root` | `Path | None` | `None` | Workflow bundle root directory |
| `step_execution_spec` | `dict[str, Any] | None` | `None` | Backend execution spec for fallback |

**Returns**: `tuple[dict[str, Any], dict[str, Any]]`

**Raises**:

- `ValueError` -- If neither workflow package nor spec can provide config

---


### 2.3 Constants / Configuration

| Name | Purpose |
|------|--------|
| `_REPO_BASED_REFERENCE_KEYS` | module configuration |


## 3. Error Handling

| Exception | When | Raised By |
|-----------|------|----------|
| `ValueError` | If neither workflow package nor spec can provide config | `build_config_from_request` |


## 4. Testing

### 4.1 Test Coverage

| Test File | Coverage Area |
|-----------|---------------|
| (none) | No test references found |


## 5. Change Log

| Date | Change | Verified By |
|------|--------|-------------|
| 2026-08-06 | Initial baseline generated from repository scan | sdlc_00_codebase_v1 |
