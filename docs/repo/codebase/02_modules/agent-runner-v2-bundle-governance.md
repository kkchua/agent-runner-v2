---
title: "Module Documentation: agent_runner_v2.bundle_governance"
template_id: "CB-02"
status: "active"
module_path: "agent_runner_v2/bundle_governance.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/02_modules/agent-runner-v2-bundle-governance.md"
last_verified_by_change: "00_repo_master_docs_bootstrap_v1 / 00RMD-20260716-5ee28fa5 / 2026-07-16T22:09:16+08:00"
created: "2026-07-16T22:09:16+08:00"
owner: "00_repo_master_docs_bootstrap_v1"
---

# Module Documentation: agent_runner_v2.bundle_governance

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

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
| `bundle_root` | `Path` | — | — |

**Returns**: `BundleGovernance | None`

---

#### render_bundle_governance_target()

**Signature**: `render_bundle_governance_target(governance: BundleGovernance, *, bundle_name: str, bundle_label: str, target: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `governance` | `BundleGovernance` | — | — |
| `bundle_name` | `str` | — | — |
| `bundle_label` | `str` | — | — |
| `target` | `str` | — | — |

**Returns**: `str`

---

#### render_prompt_governance_block()

**Signature**: `render_prompt_governance_block(governance: BundleGovernance, *, bundle_name: str, bundle_label: str, step_name: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `governance` | `BundleGovernance` | — | — |
| `bundle_name` | `str` | — | — |
| `bundle_label` | `str` | — | — |
| `step_name` | `str` | — | — |

**Returns**: `str`

---

#### generate_bundle_governance_adapters()

**Signature**: `generate_bundle_governance_adapters(governance: BundleGovernance, *, bundle_name: str, bundle_label: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `governance` | `BundleGovernance` | — | — |
| `bundle_name` | `str` | — | — |
| `bundle_label` | `str` | — | — |

**Returns**: `dict[str, Path]`

---

#### bundle_governance_summary()

**Signature**: `bundle_governance_summary(governance: BundleGovernance)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `governance` | `BundleGovernance` | — | — |

**Returns**: `dict[str, Any]`

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
