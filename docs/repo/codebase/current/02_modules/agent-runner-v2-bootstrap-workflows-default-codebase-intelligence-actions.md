---
title: "Module Documentation: agent_runner_v2.bootstrap.workflows.default.codebase_intelligence.actions"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/bootstrap/workflows/default/codebase_intelligence/actions.py"
module_area: "bootstrap"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-codebase-intelligence-actions.md"
last_verified_by_change: "sdlc_00_codebase_scaffold_v1 / SDLC00CS-1zcrrbbs / 2026-08-17T21:19:17+08:00"
created: "2026-08-17T21:19:17+08:00"
owner: "sdlc_00_codebase_scaffold_v1"
---

# Module Documentation: agent_runner_v2.bootstrap.workflows.default.codebase_intelligence.actions

## 1. Module Overview

### 1.1 Purpose

Domain actions for codebase_intelligence.

### 1.2 Responsibility

This module belongs to the `bootstrap` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `ast` | stdlib module | imported dependency |
| `datetime` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `os` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `re` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `agent_runner_v2.action_result` | internal module | repository dependency |
| `agent_runner_v2.codebase_docs` | internal module | repository dependency |
| `agent_runner_v2.workflow_packages.actions` | internal module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### scan_codebase_files()

**Decorators**: `@action`

**Signature**: `scan_codebase_files(*, context: dict, state: dict, step_cfg: dict, project_root: Any)`

**Purpose**: Walk codebase docs and source directories, produce a structured JSON inventory.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | `dict` | -- | -- |
| `state` | `dict` | -- | -- |
| `step_cfg` | `dict` | -- | -- |
| `project_root` | `Any` | -- | -- |

**Returns**: `ActionResult`

---

#### build_import_graph()

**Decorators**: `@action`

**Signature**: `build_import_graph(*, context: dict, state: dict, step_cfg: dict, project_root: Any)`

**Purpose**: Parse Python source files using AST, extract imports, build directed dependency graph with cycle detection.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | `dict` | -- | -- |
| `state` | `dict` | -- | -- |
| `step_cfg` | `dict` | -- | -- |
| `project_root` | `Any` | -- | -- |

**Returns**: `ActionResult`

---

#### validate_intelligence_outputs()

**Decorators**: `@action`

**Signature**: `validate_intelligence_outputs(*, context: dict, state: dict, step_cfg: dict, project_root: Any)`

**Purpose**: Validate all generated intelligence reports for structural completeness, evidence backing, self-containment, and cross-report consistency.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | `dict` | -- | -- |
| `state` | `dict` | -- | -- |
| `step_cfg` | `dict` | -- | -- |
| `project_root` | `Any` | -- | -- |

**Returns**: `ActionResult`

---


### 2.3 Constants / Configuration

| Name | Purpose |
|------|--------|
| `_TEXT_EXTENSIONS` | module configuration |


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
