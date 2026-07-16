---
title: "Module Documentation: agent_runner_v2.bootstrap.workflows.default.00_bootstrap_lifecycle_admin_v1.actions"
template_id: "CB-02"
status: "active"
module_path: "agent_runner_v2/bootstrap/workflows/default/00_bootstrap_lifecycle_admin_v1/actions.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/02_modules/agent-runner-v2-bootstrap-workflows-default-00-bootstrap-lifecycle-admin-v1-actions.md"
last_verified_by_change: "00_repo_master_docs_bootstrap_v1 / 00RMD-20260716-5ee28fa5 / 2026-07-16T22:09:16+08:00"
created: "2026-07-16T22:09:16+08:00"
owner: "00_repo_master_docs_bootstrap_v1"
---

# Module Documentation: agent_runner_v2.bootstrap.workflows.default.00_bootstrap_lifecycle_admin_v1.actions

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `agent_runner_v2.action_result` | internal module | repository dependency |
| `agent_runner_v2.bundle_loader` | internal module | repository dependency |
| `agent_runner_v2.runtime_context` | internal module | repository dependency |
| `agent_runner_v2.workflow_bundle_validator` | internal module | repository dependency |
| `agent_runner_v2.workflow_packages.actions` | internal module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### validate_bootstrap_lifecycle_sources()

**Decorators**: `@action`

**Signature**: `validate_bootstrap_lifecycle_sources(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | `dict[str, str]` | — | — |
| `state` | `dict` | — | — |
| `step_cfg` | `dict` | — | — |
| `project_root` | `Path` | — | — |

**Returns**: `ActionResult`

---

#### publish_bootstrap_lifecycle_bundle()

**Decorators**: `@action`

**Signature**: `publish_bootstrap_lifecycle_bundle(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | `dict[str, str]` | — | — |
| `state` | `dict` | — | — |
| `step_cfg` | `dict` | — | — |
| `project_root` | `Path` | — | — |

**Returns**: `ActionResult`

---

#### init_bootstrap_lifecycle_workspace()

**Decorators**: `@action`

**Signature**: `init_bootstrap_lifecycle_workspace(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | `dict[str, str]` | — | — |
| `state` | `dict` | — | — |
| `step_cfg` | `dict` | — | — |
| `project_root` | `Path` | — | — |

**Returns**: `ActionResult`

---

#### write_bootstrap_lifecycle_summary()

**Decorators**: `@action`

**Signature**: `write_bootstrap_lifecycle_summary(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | `dict[str, str]` | — | — |
| `state` | `dict` | — | — |
| `step_cfg` | `dict` | — | — |
| `project_root` | `Path` | — | — |

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
| 2026-07-16 | Initial baseline generated from repository scan | 00_repo_master_docs_bootstrap_v1 |
