---
title: "Module Documentation: agent_runner_v2.cli_runtime"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/cli_runtime.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-cli-runtime.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-mqe50g5d / 2026-08-06T05:49:37+08:00"
created: "2026-08-06T05:49:37+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.cli_runtime

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `core` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `dataclasses` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `os` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `config_loader` | external module | repository dependency |
| `state_defaults` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

#### AdminCommandResolution

**Decorators**: `@dataclass`

**Purpose**: Public class


### 2.2 Functions

#### handle_admin_command()

**Signature**: `handle_admin_command(*, args: Any, group_cfg: dict[str, Any], hooks: Any)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `args` | `Any` | -- | -- |
| `group_cfg` | `dict[str, Any]` | -- | -- |
| `hooks` | `Any` | -- | -- |

**Returns**: `AdminCommandResolution`

---

#### print_failure()

**Signature**: `print_failure(*, remark: str, state: dict[str, Any] | None, template_group: str, step: str | None, coder_used: str | None, failure_class: str, failure_code: str, failure_source: str, hooks: Any)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `remark` | `str` | -- | -- |
| `state` | `dict[str, Any] | None` | -- | -- |
| `template_group` | `str` | -- | -- |
| `step` | `str | None` | -- | -- |
| `coder_used` | `str | None` | -- | -- |
| `failure_class` | `str` | -- | -- |
| `failure_code` | `str` | -- | -- |
| `failure_source` | `str` | -- | -- |
| `hooks` | `Any` | -- | -- |

**Returns**: `None`

---

#### step_progress_parts()

**Signature**: `step_progress_parts(group_cfg: dict[str, Any], step: str | None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_cfg` | `dict[str, Any]` | -- | -- |
| `step` | `str | None` | -- | -- |

**Returns**: `tuple[int | None, int]`

---

#### step_progress_label()

**Signature**: `step_progress_label(group_cfg: dict[str, Any], step: str | None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_cfg` | `dict[str, Any]` | -- | -- |
| `step` | `str | None` | -- | -- |

**Returns**: `str`

---

#### format_job_status_summary()

**Signature**: `format_job_status_summary(state: dict[str, Any], group_cfg: dict[str, Any], *, get_job_status: Any)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | -- | -- |
| `group_cfg` | `dict[str, Any]` | -- | -- |
| `get_job_status` | `Any` | -- | -- |

**Returns**: `str`

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
| 2026-08-06 | Initial baseline generated from repository scan | sdlc_00_codebase_v1 |
