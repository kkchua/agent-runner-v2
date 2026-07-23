---
title: "Module Documentation: agent_runner_v2.workflow_specs"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/workflow_specs.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-specs.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-20260723-d46af7f2 / 2026-07-23T20:54:20+08:00"
created: "2026-07-23T20:54:20+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.workflow_specs

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `copy` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `bundle_loader` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### load_workflow_definition()

**Signature**: `load_workflow_definition(*, workspace_root: Path, workflow_name: str = 'default')`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `workspace_root` | `Path` | -- | -- |
| `workflow_name` | `str` | `'default'` | -- |

**Returns**: `tuple[Any, dict[str, Any]]`

---

#### get_template_group_cfg()

**Signature**: `get_template_group_cfg(*, template_group: str, workspace_root: Path, workflow_name: str = 'default')`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `template_group` | `str` | -- | -- |
| `workspace_root` | `Path` | -- | -- |
| `workflow_name` | `str` | `'default'` | -- |

**Returns**: `dict[str, Any]`

---

#### build_transport_raw_config()

**Signature**: `build_transport_raw_config(step_cfg: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `step_cfg` | `dict[str, Any]` | -- | -- |

**Returns**: `dict[str, Any]`

---

#### build_step_execution_spec()

**Signature**: `build_step_execution_spec(*, template_group: str, step_name: str, group_cfg: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `template_group` | `str` | -- | -- |
| `step_name` | `str` | -- | -- |
| `group_cfg` | `dict[str, Any]` | -- | -- |

**Returns**: `dict[str, Any]`

---

#### build_workflow_step_specs()

**Signature**: `build_workflow_step_specs(*, template_group: str, workspace_root: Path, workflow_name: str = 'default')`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `template_group` | `str` | -- | -- |
| `workspace_root` | `Path` | -- | -- |
| `workflow_name` | `str` | `'default'` | -- |

**Returns**: `list[dict[str, Any]]`

---

#### reconcile_step_execution_spec()

**Signature**: `reconcile_step_execution_spec(*, template_group: str, step_name: str, workspace_root: Path, workflow_name: str = 'default', backend_spec: dict[str, Any] | None = None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `template_group` | `str` | -- | -- |
| `step_name` | `str` | -- | -- |
| `workspace_root` | `Path` | -- | -- |
| `workflow_name` | `str` | `'default'` | -- |
| `backend_spec` | `dict[str, Any] | None` | `None` | -- |

**Returns**: `dict[str, Any]`

---


### 2.3 Constants / Configuration

| Name | Purpose |
|------|--------|
| `AUTHORITATIVE_STEP_SPEC_KEYS` | module configuration |
| `TRANSPORT_RAW_CONFIG_KEYS` | module configuration |


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
