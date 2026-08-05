---
title: "Module Documentation: agent_runner_v2.workflow_bundle_validator"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/workflow_bundle_validator.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-bundle-validator.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-zcezjfyu / 2026-08-05T13:02:54+08:00"
created: "2026-08-05T13:02:54+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.workflow_bundle_validator

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
| `pathlib` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `runtime_context` | external module | repository dependency |
| `workflow_packages.loader` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

#### ValidationFinding

**Decorators**: `@dataclass`

**Purpose**: Public class

#### WorkflowBundleValidationReport

**Decorators**: `@dataclass`

**Purpose**: Public class

**Methods**:

- `to_dict()` -> `dict[str, Any]` -- method


### 2.2 Functions

#### validate_workflow_bundle_dir()

**Signature**: `validate_workflow_bundle_dir(bundle_root: Path)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `bundle_root` | `Path` | -- | -- |

**Returns**: `WorkflowBundleValidationReport`

---

#### validate_named_workflow_bundles()

**Signature**: `validate_named_workflow_bundles(*, workflows_root: Path | None = None, workflow_names: list[str] | None = None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `workflows_root` | `Path | None` | `None` | -- |
| `workflow_names` | `list[str] | None` | `None` | -- |

**Returns**: `list[WorkflowBundleValidationReport]`

---


### 2.3 Constants / Configuration

| Name | Purpose |
|------|--------|
| `DEFAULT_BOOTSTRAP_WORKFLOWS_ROOT` | module configuration |


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
