---
title: "Module Documentation: agent_runner_v2.site_styles"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/site_styles.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-site-styles.md"
last_verified_by_change: "sdlc_00_codebase_scaffold_v1 / SDLC00CS-1zcrrbbs / 2026-08-17T21:19:17+08:00"
created: "2026-08-17T21:19:17+08:00"
owner: "sdlc_00_codebase_scaffold_v1"
---

# Module Documentation: agent_runner_v2.site_styles

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `core` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `html` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### page_shell()

**Signature**: `page_shell(*, title: str, subtitle: str, workflow: str, step: str, nav_links: list[tuple[str, str]], body: str, site_comment: str = '')`

**Purpose**: Generate a complete HTML page with common styling.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `title` | `str` | -- | Page title |
| `subtitle` | `str` | -- | Page subtitle/description |
| `workflow` | `str` | -- | Workflow name for metadata |
| `step` | `str` | -- | Step name for metadata |
| `nav_links` | `list[tuple[str, str]]` | -- | List of (url, label) tuples for navigation |
| `body` | `str` | -- | Main content HTML |
| `site_comment` | `str` | `''` | Optional HTML comment for the page |

**Returns**: `str`

---

#### card()

**Signature**: `card(title: str, text: str, link: str | None = None)`

**Purpose**: Generate a styled card element.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `title` | `str` | -- | Card title |
| `text` | `str` | -- | Card description |
| `link` | `str | None` | `None` | Optional link URL |

**Returns**: `str`

---

#### table()

**Signature**: `table(headers: list[str], rows: list[list[str]])`

**Purpose**: Generate a styled HTML table.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `headers` | `list[str]` | -- | Column headers |
| `rows` | `list[list[str]]` | -- | Table rows (list of lists) |

**Returns**: `str`

---

#### section()

**Signature**: `section(title: str, content: str)`

**Purpose**: Generate a styled section element.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `title` | `str` | -- | Section title |
| `content` | `str` | -- | Section content HTML |

**Returns**: `str`

---

#### manifest_json()

**Signature**: `manifest_json(*, workflow: str, step: str, pages: dict[str, str], index_path: str)`

**Purpose**: Generate manifest.json content for a site.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `workflow` | `str` | -- | Workflow name |
| `step` | `str` | -- | Step name |
| `pages` | `dict[str, str]` | -- | Dict mapping page paths to titles |
| `index_path` | `str` | -- | Path to the index page |

**Returns**: `str`

---


### 2.3 Constants / Configuration

| Name | Purpose |
|------|--------|
| `COMMON_CSS` | module configuration |


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
