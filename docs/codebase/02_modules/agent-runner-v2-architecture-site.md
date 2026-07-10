---
title: "Module Documentation: agent_runner_v2.architecture_site"
template_id: "CB-02"
status: "active"
module_path: "agent_runner_v2/architecture_site.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/codebase/02_modules/agent-runner-v2-architecture-site.md"
last_verified_by_change: "00_master_docs_bootstrap_v2 / 00DOC-GEN-20260710-004 / 2026-07-10T14:00:58+08:00"
created: "2026-07-10T14:00:58+08:00"
owner: "00_master_docs_bootstrap_v2"
---

# Module Documentation: agent_runner_v2.architecture_site

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `html` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `constants` | external module | repository dependency |
| `doc_paths` | external module | repository dependency |
| `site_styles` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### render_master_index()

**Signature**: `render_master_index(snapshot: dict[str, Any], project_root: Path)`

**Purpose**: Generate the master index/navigation page.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `snapshot` | `dict[str, Any]` | — | Build snapshot (unused for master index, kept for API consistency) |
| `project_root` | `Path` | — | Repository root path |

**Returns**: `dict[str, str]`

---

#### render_architecture_site()

**Signature**: `render_architecture_site(snapshot: dict[str, Any], project_root: Path)`

**Purpose**: Legacy function - now delegates to render_master_index.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `snapshot` | `dict[str, Any]` | — | — |
| `project_root` | `Path` | — | — |

**Returns**: `dict[str, str]`

---


### 2.3 Constants / Configuration

| Name | Purpose |
|------|--------|
| `SITE_PAGES` | module configuration |
| `AUDIENCE_SITES` | module configuration |


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
