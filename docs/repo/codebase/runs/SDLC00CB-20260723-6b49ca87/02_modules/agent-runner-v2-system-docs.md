---
title: "Module Documentation: agent_runner_v2.system_docs"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/system_docs.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-system-docs.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-20260723-6b49ca87 / 2026-07-23T21:17:05+08:00"
created: "2026-07-23T21:17:05+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.system_docs

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `datetime` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `doc_paths` | external module | repository dependency |
| `doc_text` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### render_system_index()

**Signature**: `render_system_index(snapshot: dict, *, repo_name: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `snapshot` | `dict` | -- | -- |
| `repo_name` | `str` | -- | -- |

**Returns**: `str`

---

#### render_documentation_standard()

**Signature**: `render_documentation_standard(snapshot: dict)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `snapshot` | `dict` | -- | -- |

**Returns**: `str`

---

#### render_bundle_taxonomy()

**Signature**: `render_bundle_taxonomy(snapshot: dict)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `snapshot` | `dict` | -- | -- |

**Returns**: `str`

---

#### render_runtime_governance()

**Signature**: `render_runtime_governance(snapshot: dict)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `snapshot` | `dict` | -- | -- |

**Returns**: `str`

---

#### render_bundle_migration_plan()

**Signature**: `render_bundle_migration_plan(snapshot: dict)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `snapshot` | `dict` | -- | -- |

**Returns**: `str`

---

#### render_system_overview()

**Signature**: `render_system_overview(snapshot: dict, *, repo_name: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `snapshot` | `dict` | -- | -- |
| `repo_name` | `str` | -- | -- |

**Returns**: `str`

---

#### render_business_capabilities()

**Signature**: `render_business_capabilities(snapshot: dict)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `snapshot` | `dict` | -- | -- |

**Returns**: `str`

---

#### render_functional_spec()

**Signature**: `render_functional_spec(snapshot: dict, *, repo_name: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `snapshot` | `dict` | -- | -- |
| `repo_name` | `str` | -- | -- |

**Returns**: `str`

---

#### render_nfr()

**Signature**: `render_nfr(snapshot: dict)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `snapshot` | `dict` | -- | -- |

**Returns**: `str`

---

#### render_system_context()

**Signature**: `render_system_context(snapshot: dict, *, repo_name: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `snapshot` | `dict` | -- | -- |
| `repo_name` | `str` | -- | -- |

**Returns**: `str`

---

#### render_component_architecture()

**Signature**: `render_component_architecture(snapshot: dict)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `snapshot` | `dict` | -- | -- |

**Returns**: `str`

---

#### render_decision_log()

**Signature**: `render_decision_log(snapshot: dict)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `snapshot` | `dict` | -- | -- |

**Returns**: `str`

---

#### render_system_file_structure()

**Signature**: `render_system_file_structure(snapshot: dict)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `snapshot` | `dict` | -- | -- |

**Returns**: `str`

---

#### render_developer_guide()

**Signature**: `render_developer_guide(snapshot: dict)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `snapshot` | `dict` | -- | -- |

**Returns**: `str`

---

#### render_runbook()

**Signature**: `render_runbook(snapshot: dict)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `snapshot` | `dict` | -- | -- |

**Returns**: `str`

---

#### render_system_docs_change_log()

**Signature**: `render_system_docs_change_log(snapshot: dict, *, repo_name: str, doc_paths: list[str])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `snapshot` | `dict` | -- | -- |
| `repo_name` | `str` | -- | -- |
| `doc_paths` | `list[str]` | -- | -- |

**Returns**: `str`

---

#### render_system_docs_validation()

**Signature**: `render_system_docs_validation(snapshot: dict, *, title: str, checks: list[tuple[str, bool, str]])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `snapshot` | `dict` | -- | -- |
| `title` | `str` | -- | -- |
| `checks` | `list[tuple[str, bool, str]]` | -- | -- |

**Returns**: `str`

---


### 2.3 Constants / Configuration

| Name | Purpose |
|------|--------|
| `SYSTEM_BOOTSTRAP_ROOT` | module configuration |
| `CODEBASE_ROOT` | module configuration |
| `DELIVERY_ROOT` | module configuration |


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
