---
title: "Module Documentation: agent_runner_v2.bootstrap.workflows.default.workflow_builder_v1.actions"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/bootstrap/workflows/default/workflow_builder_v1/actions.py"
module_area: "bootstrap"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-workflow-builder-v1-actions.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-zcezjfyu / 2026-08-05T13:02:54+08:00"
created: "2026-08-05T13:02:54+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.bootstrap.workflows.default.workflow_builder_v1.actions

## 1. Module Overview

### 1.1 Purpose

Custom actions for workflow_builder_v1.

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
| `agent_runner_v2.workflow_packages.actions` | internal module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### validate_workflow_bundle()

**Decorators**: `@action`

**Signature**: `validate_workflow_bundle(*, context, state, step_cfg, project_root)`

**Purpose**: Validate the generated workflow package using structural and semantic checks.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | -- | -- | -- |
| `state` | -- | -- | -- |
| `step_cfg` | -- | -- | -- |
| `project_root` | -- | -- | -- |

---

#### promote_workflow_package()

**Decorators**: `@action`

**Signature**: `promote_workflow_package(*, context, state, step_cfg, project_root)`

**Purpose**: Promote the generated workflow package to the repo workflows directory.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | -- | -- | -- |
| `state` | -- | -- | -- |
| `step_cfg` | -- | -- | -- |
| `project_root` | -- | -- | -- |

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
| 2026-08-05 | Initial baseline generated from repository scan | sdlc_00_codebase_v1 |
