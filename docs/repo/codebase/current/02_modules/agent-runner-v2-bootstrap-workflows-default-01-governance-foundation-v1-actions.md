---
title: "Module Documentation: agent_runner_v2.bootstrap.workflows.default.01_governance_foundation_v1.actions"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/actions.py"
module_area: "bootstrap"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-01-governance-foundation-v1-actions.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-bgmxg5vi / 2026-08-06T07:04:04+08:00"
created: "2026-08-06T07:04:04+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.bootstrap.workflows.default.01_governance_foundation_v1.actions

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `bootstrap` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `datetime` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `shutil` | stdlib module | imported dependency |
| `agent_runner_v2.action_result` | internal module | repository dependency |
| `agent_runner_v2.actions.documentation_validation_core` | internal module | repository dependency |
| `agent_runner_v2.runtime_context` | internal module | repository dependency |
| `agent_runner_v2.workflow_packages.actions` | internal module | repository dependency |

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

#### collect_governance_context()

**Decorators**: `@action`

**Signature**: `collect_governance_context(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | `dict[str, str]` | -- | -- |
| `state` | `dict` | -- | -- |
| `step_cfg` | `dict` | -- | -- |
| `project_root` | `Path` | -- | -- |

**Returns**: `ActionResult`

---

#### validate_governance_foundation_docs()

**Decorators**: `@action`

**Signature**: `validate_governance_foundation_docs(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | `dict[str, str]` | -- | -- |
| `state` | `dict` | -- | -- |
| `step_cfg` | `dict` | -- | -- |
| `project_root` | `Path` | -- | -- |

**Returns**: `ActionResult`

---

#### publish_governance_foundation_set()

**Decorators**: `@action`

**Signature**: `publish_governance_foundation_set(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | `dict[str, str]` | -- | -- |
| `state` | `dict` | -- | -- |
| `step_cfg` | `dict` | -- | -- |
| `project_root` | `Path` | -- | -- |

**Returns**: `ActionResult`

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
