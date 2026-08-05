---
title: "Module Documentation: agent_runner_v2.workflow_packages.registry"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/workflow_packages/registry.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-packages-registry.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-zcezjfyu / 2026-08-05T13:02:54+08:00"
created: "2026-08-05T13:02:54+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.workflow_packages.registry

## 1. Module Overview

### 1.1 Purpose

Workflow package registry -- discovery, caching, and lookup.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `base` | external module | repository dependency |
| `loader` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

#### WorkflowRegistry

**Purpose**: Directory of available workflow packages on local disk.

**Methods**:

- `add_search_path(path: str | Path)` -> `None` -- Register a directory to scan for workflow packages.
- `set_search_paths(paths: list[str | Path])` -> `None` -- Replace all search paths (clears previous paths).
- `discover()` -> `None` -- Scan all search paths and index discovered workflow packages.
- `get(name: str)` -> `WorkflowBundle` -- Return a previously discovered workflow bundle.
- `list_workflows()` -> `list[str]` -- Return sorted names of all discovered workflow packages.
- `has(name: str)` -> `bool` -- Check whether a workflow package with *name* exists.
- `create(*, search_paths: list[str | Path] | None = None)` -> `WorkflowRegistry` -- Factory: build a registry, add paths, and discover.
- `from_project_root(project_root: str | Path, *, additional_paths: list[str | Path] | None = None)` -> `WorkflowRegistry` -- Factory: scan ``<project_root>/workflows/`` plus any extra paths.


### 2.2 Functions

#### get_global_registry()

**Signature**: `get_global_registry()`

**Purpose**: Return the process-wide singleton registry (lazily created).

**Returns**: `WorkflowRegistry`

---

#### set_global_registry()

**Signature**: `set_global_registry(registry: WorkflowRegistry)`

**Purpose**: Replace the process-wide singleton registry.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `registry` | `WorkflowRegistry` | -- | -- |

**Returns**: `None`

---

#### discover_workflow_package()

**Signature**: `discover_workflow_package(name: str, *, project_root: str | Path | None = None, workflow_root: str | Path | None = None)`

**Purpose**: Convenience: discover a single package by name.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `name` | `str` | -- | -- |
| `project_root` | `str | Path | None` | `None` | -- |
| `workflow_root` | `str | Path | None` | `None` | -- |

**Returns**: `WorkflowBundle | None`

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
