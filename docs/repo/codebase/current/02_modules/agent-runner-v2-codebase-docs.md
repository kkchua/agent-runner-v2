---
title: "Module Documentation: agent_runner_v2.codebase_docs"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/codebase_docs.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-codebase-docs.md"
last_verified_by_change: "sdlc_00_codebase_scaffold_v1 / SDLC00CS-1zcrrbbs / 2026-08-17T21:19:17+08:00"
created: "2026-08-17T21:19:17+08:00"
owner: "sdlc_00_codebase_scaffold_v1"
---

# Module Documentation: agent_runner_v2.codebase_docs

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `core` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `ast` | stdlib module | imported dependency |
| `dataclasses` | stdlib module | imported dependency |
| `datetime` | stdlib module | imported dependency |
| `fnmatch` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `re` | stdlib module | imported dependency |
| `subprocess` | stdlib module | imported dependency |
| `sys` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `bundle_loader` | external module | repository dependency |
| `doc_paths` | external module | repository dependency |
| `doc_text` | external module | repository dependency |
| `runtime_context` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

#### ScanItem

**Decorators**: `@dataclass`

**Purpose**: Public class


### 2.2 Functions

#### build_snapshot()

**Signature**: `build_snapshot(project_root: Path, *, mode: str, job_id: str, step: str, workflow_name: str | None = None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `project_root` | `Path` | -- | -- |
| `mode` | `str` | -- | -- |
| `job_id` | `str` | -- | -- |
| `step` | `str` | -- | -- |
| `workflow_name` | `str | None` | `None` | -- |

**Returns**: `dict[str, Any]`

---

#### render_inventory()

**Signature**: `render_inventory(snapshot: dict[str, Any], *, title: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `snapshot` | `dict[str, Any]` | -- | -- |
| `title` | `str` | -- | -- |

**Returns**: `str`

---

#### render_module_doc()

**Signature**: `render_module_doc(snapshot: dict[str, Any], module_record: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `snapshot` | `dict[str, Any]` | -- | -- |
| `module_record` | `dict[str, Any]` | -- | -- |

**Returns**: `str`

---

#### render_component_doc()

**Signature**: `render_component_doc(snapshot: dict[str, Any], *, component_name: str, rows: list[dict[str, str]], overview: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `snapshot` | `dict[str, Any]` | -- | -- |
| `component_name` | `str` | -- | -- |
| `rows` | `list[dict[str, str]]` | -- | -- |
| `overview` | `str` | -- | -- |

**Returns**: `str`

---

#### render_change_impact()

**Signature**: `render_change_impact(snapshot: dict[str, Any], *, title: str, changed_files: list[str], docs_created: list[str], docs_updated: list[str], stale_docs: list[str])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `snapshot` | `dict[str, Any]` | -- | -- |
| `title` | `str` | -- | -- |
| `changed_files` | `list[str]` | -- | -- |
| `docs_created` | `list[str]` | -- | -- |
| `docs_updated` | `list[str]` | -- | -- |
| `stale_docs` | `list[str]` | -- | -- |

**Returns**: `str`

---

#### render_validation()

**Signature**: `render_validation(snapshot: dict[str, Any], *, title: str, checks: list[tuple[str, bool, str]])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `snapshot` | `dict[str, Any]` | -- | -- |
| `title` | `str` | -- | -- |
| `checks` | `list[tuple[str, bool, str]]` | -- | -- |

**Returns**: `str`

---


### 2.3 Constants / Configuration

| Name | Purpose |
|------|--------|
| `SCAN_IGNORE_FILE` | module configuration |
| `EXCLUDED_DIRS` | module configuration |
| `STD_LIBS` | module configuration |
| `_NON_PACKAGE_DIRS` | module configuration |
| `_DIR_AREA_MAP` | module configuration |
| `_FULL_DOC_DIRS` | module configuration |


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
