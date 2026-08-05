---
title: "Module Documentation: agent_runner_v2.workflow_packages.loader"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/workflow_packages/loader.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-packages-loader.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-roo6dyno / 2026-08-05T23:43:32+08:00"
created: "2026-08-05T23:43:32+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.workflow_packages.loader

## 1. Module Overview

### 1.1 Purpose

Parse workflow.toml manifests and adapt them to the TEMPLATE_GROUPS dict format.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `sys` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `base` | external module | repository dependency |
| `bundle_governance` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### load_workflow_package()

**Signature**: `load_workflow_package(package_dir: Path)`

**Purpose**: Parse *package_dir/workflow.toml* and return a validated WorkflowBundle.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `package_dir` | `Path` | -- | -- |

**Returns**: `WorkflowBundle`

---

#### bundle_to_template_group_dict()

**Signature**: `bundle_to_template_group_dict(bundle: WorkflowBundle)`

**Purpose**: Adapt a ``WorkflowBundle`` into a ``TEMPLATE_GROUPS``-style dict.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `bundle` | `WorkflowBundle` | -- | -- |

**Returns**: `dict[str, Any]`

---


### 2.3 Constants / Configuration

| Name | Purpose |
|------|--------|
| `_STEP_DIRECT_KEYS` | module configuration |
| `_KNOWN_STEP_KEYS` | module configuration |


## 3. Error Handling

No documented exceptions.


## 4. Testing

### 4.1 Test Coverage

| Test File | Coverage Area |
|-----------|---------------|
| `tests/conftest.py` | `agent_runner_v2.workflow_packages.loader` |


## 5. Change Log

| Date | Change | Verified By |
|------|--------|-------------|
| 2026-08-05 | Initial baseline generated from repository scan | sdlc_00_codebase_v1 |
