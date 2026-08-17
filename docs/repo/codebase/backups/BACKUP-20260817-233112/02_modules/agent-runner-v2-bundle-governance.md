---
title: "Module Documentation: agent_runner_v2.bundle_governance"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/bundle_governance.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-bundle-governance.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-bgmxg5vi / 2026-08-06T07:04:04+08:00"
created: "2026-08-06T07:04:04+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.bundle_governance

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
| `pathlib` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `workflow_packages.base` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### load_bundle_governance()

**Signature**: `load_bundle_governance(bundle_root: Path)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `bundle_root` | `Path` | -- | -- |

**Returns**: `BundleGovernance | None`

---

#### render_bundle_governance_target()

**Signature**: `render_bundle_governance_target(governance: BundleGovernance, *, bundle_name: str, bundle_label: str, target: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `governance` | `BundleGovernance` | -- | -- |
| `bundle_name` | `str` | -- | -- |
| `bundle_label` | `str` | -- | -- |
| `target` | `str` | -- | -- |

**Returns**: `str`

---

#### render_prompt_governance_block()

**Signature**: `render_prompt_governance_block(governance: BundleGovernance, *, bundle_name: str, bundle_label: str, step_name: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `governance` | `BundleGovernance` | -- | -- |
| `bundle_name` | `str` | -- | -- |
| `bundle_label` | `str` | -- | -- |
| `step_name` | `str` | -- | -- |

**Returns**: `str`

---

#### generate_bundle_governance_adapters()

**Signature**: `generate_bundle_governance_adapters(governance: BundleGovernance, *, bundle_name: str, bundle_label: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `governance` | `BundleGovernance` | -- | -- |
| `bundle_name` | `str` | -- | -- |
| `bundle_label` | `str` | -- | -- |

**Returns**: `dict[str, Path]`

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
