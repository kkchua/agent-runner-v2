---
title: "Module Documentation: agent_runner_v2.path_catalog"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/path_catalog.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-path-catalog.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-20260723-e1c86100 / 2026-07-23T21:41:19+08:00"
created: "2026-07-23T21:41:19+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.path_catalog

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `artifact_keys` | external module | repository dependency |
| `constants` | external module | repository dependency |
| `path_primitives` | external module | repository dependency |
| `workflow_path_contracts` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### delivery_scaffold_docs()

**Signature**: `delivery_scaffold_docs()`

**Returns**: `dict[str, str]`

---

#### audience_site_artifacts()

**Signature**: `audience_site_artifacts()`

**Returns**: `dict[str, str]`

---

#### architecture_site_pages()

**Signature**: `architecture_site_pages()`

**Returns**: `dict[str, str]`

---

#### stakeholder_site_pages()

**Signature**: `stakeholder_site_pages()`

**Returns**: `dict[str, str]`

---

#### developer_site_pages()

**Signature**: `developer_site_pages()`

**Returns**: `dict[str, str]`

---

#### operator_site_pages()

**Signature**: `operator_site_pages()`

**Returns**: `dict[str, str]`

---

#### tester_site_pages()

**Signature**: `tester_site_pages()`

**Returns**: `dict[str, str]`

---

#### user_site_pages()

**Signature**: `user_site_pages()`

**Returns**: `dict[str, str]`

---

#### get_master_docs_output_paths()

**Signature**: `get_master_docs_output_paths(job_id: str = '{job_id}', mode: str = '{mode}')`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `job_id` | `str` | `'{job_id}'` | -- |
| `mode` | `str` | `'{mode}'` | -- |

**Returns**: `dict[str, str]`

---

#### known_artifact_paths()

**Signature**: `known_artifact_paths()`

**Returns**: `dict[str, str]`

---

#### prompt_literal_substitutions()

**Signature**: `prompt_literal_substitutions()`

**Returns**: `dict[str, str]`

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
| 2026-07-23 | Initial baseline generated from repository scan | sdlc_00_codebase_v1 |
