---
title: "Module Documentation: agent_runner_v2.bootstrap.workflows.default.01_governance_foundation_v1.context_extensions"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/context_extensions.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-01-governance-foundation-v1-context-extensions.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-20260723-e1c86100 / 2026-07-23T21:41:19+08:00"
created: "2026-07-23T21:41:19+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.bootstrap.workflows.default.01_governance_foundation_v1.context_extensions

## 1. Module Overview

### 1.1 Purpose

Context extensions for 01_governance_foundation_v1.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `agent_runner_v2.constants` | internal module | repository dependency |
| `agent_runner_v2.runtime_context` | internal module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### build_output_paths()

**Signature**: `build_output_paths(*, job_id: str = '{job_id}', mode: str = '{mode}', loop_iteration: int = 0)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `job_id` | `str` | `'{job_id}'` | -- |
| `mode` | `str` | `'{mode}'` | -- |
| `loop_iteration` | `int` | `0` | -- |

**Returns**: `dict[str, str]`

---

#### build_context_extensions()

**Signature**: `build_context_extensions(*, state: dict, step: str, step_cfg: dict, ctx: dict[str, str], project_root: Path | None = None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict` | -- | -- |
| `step` | `str` | -- | -- |
| `step_cfg` | `dict` | -- | -- |
| `ctx` | `dict[str, str]` | -- | -- |
| `project_root` | `Path | None` | `None` | -- |

**Returns**: `dict[str, str]`

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
