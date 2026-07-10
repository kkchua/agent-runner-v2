---
title: "Module Documentation: agent_runner_v2.bundle_taxonomy"
template_id: "CB-02"
status: "active"
module_path: "agent_runner_v2/bundle_taxonomy.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/codebase/02_modules/agent-runner-v2-bundle-taxonomy.md"
last_verified_by_change: "00_master_docs_bootstrap_v2 / 00DOC-20260710-0098bf53 / 2026-07-10T19:43:53+08:00"
created: "2026-07-10T19:43:53+08:00"
owner: "00_master_docs_bootstrap_v2"
---

# Module Documentation: agent_runner_v2.bundle_taxonomy

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
| `doc_paths` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

#### BundleSelection

**Decorators**: `@dataclass`

**Purpose**: Public class

**Methods**:

- `to_dict()` → `dict[str, Any]` — method


### 2.2 Functions

#### bundle_manifest()

**Signature**: `bundle_manifest(*, workflow_name: str, domain: str = DEFAULT_DOMAIN_BUNDLE, profile: str = DEFAULT_BUNDLE_PROFILE)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `workflow_name` | `str` | — | — |
| `domain` | `str` | `DEFAULT_DOMAIN_BUNDLE` | — |
| `profile` | `str` | `DEFAULT_BUNDLE_PROFILE` | — |

**Returns**: `dict[str, Any]`

---

#### bundle_manifest_path()

**Signature**: `bundle_manifest_path(runner_home: Path)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `runner_home` | `Path` | — | — |

**Returns**: `Path`

---


### 2.3 Constants / Configuration

| Name | Purpose |
|------|--------|
| `CORE_BUNDLE_NAME` | module configuration |
| `DEFAULT_DOMAIN_BUNDLE` | module configuration |
| `DEFAULT_BUNDLE_PROFILE` | module configuration |
| `DOMAIN_BUNDLE_NAMES` | module configuration |
| `CORE_DOCS` | module configuration |
| `WORKFLOW_DOCS` | module configuration |
| `DOMAIN_DOCS` | module configuration |


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
| 2026-07-10 | Initial baseline generated from repository scan | 00_master_docs_bootstrap_v2 |
