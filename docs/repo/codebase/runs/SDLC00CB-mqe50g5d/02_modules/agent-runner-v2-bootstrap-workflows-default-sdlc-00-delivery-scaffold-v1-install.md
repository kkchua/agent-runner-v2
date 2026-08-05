---
title: "Module Documentation: agent_runner_v2.bootstrap.workflows.default.sdlc_00_delivery_scaffold_v1.install"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/bootstrap/workflows/default/sdlc_00_delivery_scaffold_v1/install.py"
module_area: "bootstrap"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-delivery-scaffold-v1-install.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-mqe50g5d / 2026-08-06T05:49:37+08:00"
created: "2026-08-06T05:49:37+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.bootstrap.workflows.default.sdlc_00_delivery_scaffold_v1.install

## 1. Module Overview

### 1.1 Purpose

Install SDLC scaffold to global runner home.

### 1.2 Responsibility

This module belongs to the `bootstrap` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `shutil` | stdlib module | imported dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### install_workflow()

**Signature**: `install_workflow(*, project_root: Path, runner_home: Path)`

**Purpose**: Install SDLC scaffold to global path.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `project_root` | `Path` | -- | Repository root directory. |
| `runner_home` | `Path` | -- | Global runner home directory (~/.ukbe-runner/). |

**Returns**: `dict`

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
