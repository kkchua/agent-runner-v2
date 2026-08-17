---
title: "Module Documentation: agent_runner_v2.bootstrap.workflows.default.artifact_generator_builder.actions"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/actions.py"
module_area: "bootstrap"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-artifact-generator-builder-actions.md"
last_verified_by_change: "sdlc_00_codebase_scaffold_v1 / SDLC00CS-1zcrrbbs / 2026-08-17T21:19:17+08:00"
created: "2026-08-17T21:19:17+08:00"
owner: "sdlc_00_codebase_scaffold_v1"
---

# Module Documentation: agent_runner_v2.bootstrap.workflows.default.artifact_generator_builder.actions

## 1. Module Overview

### 1.1 Purpose

Custom actions for Artifact Generator Builder.

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

#### promote_workflow_package()

**Decorators**: `@action`

**Signature**: `promote_workflow_package(*, context, state, step_cfg, project_root)`

**Purpose**: Promote all deliverables to workflows/{codename}/.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | -- | -- | -- |
| `state` | -- | -- | -- |
| `step_cfg` | -- | -- | -- |
| `project_root` | -- | -- | -- |

---

#### assemble_package()

**Decorators**: `@action`

**Signature**: `assemble_package(*, context, state, step_cfg, project_root)`

**Purpose**: Deterministically build workflow.toml, context_extensions.py, and impl.yaml

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | -- | -- | -- |
| `state` | -- | -- | -- |
| `step_cfg` | -- | -- | -- |
| `project_root` | -- | -- | -- |

---

#### validate_structure()

**Decorators**: `@action`

**Signature**: `validate_structure(*, context, state, step_cfg, project_root)`

**Purpose**: Run deterministic structural validation on the generated package.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | -- | -- | -- |
| `state` | -- | -- | -- |
| `step_cfg` | -- | -- | -- |
| `project_root` | -- | -- | -- |

---

#### noop_action()

**Decorators**: `@action`

**Signature**: `noop_action(*, context, state, step_cfg, project_root)`

**Purpose**: No-operation action -- returns success immediately.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | -- | -- | -- |
| `state` | -- | -- | -- |
| `step_cfg` | -- | -- | -- |
| `project_root` | -- | -- | -- |

---

#### copy_infrastructure_action()

**Decorators**: `@action`

**Signature**: `copy_infrastructure_action(*, context, state, step_cfg, project_root)`

**Purpose**: Copy AGB infrastructure (actions.py + prompts/) to output workflow.

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
| 2026-08-17 | Initial baseline generated from repository scan | sdlc_00_codebase_scaffold_v1 |
