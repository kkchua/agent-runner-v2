---
title: "Module Documentation: agent_runner_v2.config.section_requirements"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/config/section_requirements.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-config-section-requirements.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-20260723-e1c86100 / 2026-07-23T21:41:19+08:00"
created: "2026-07-23T21:41:19+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.config.section_requirements

## 1. Module Overview

### 1.1 Purpose

Central section requirements for all generated documents.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `pathlib` | stdlib module | imported dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### get_required_sections()

**Signature**: `get_required_sections(doc_path: str)`

**Purpose**: Get required sections for a document by path or name.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `doc_path` | `str` | -- | Full path or just filename (e.g., "PROJECT_ANALYSIS.md") |

**Returns**: `list[str]`

**Raises**:

- `ValueError` -- If document has no defined section requirements

---

#### list_all_documented_files()

**Signature**: `list_all_documented_files()`

**Purpose**: List all documents with defined section requirements.

**Returns**: `list[str]`

---


### 2.3 Constants / Configuration

| Name | Purpose |
|------|--------|
| `CODEBASE_SOP_REQUIRED_SECTIONS` | module configuration |
| `CODEBASE_STATUS_RULES_REQUIRED_SECTIONS` | module configuration |
| `DELIVERY_SOP_REQUIRED_SECTIONS` | module configuration |
| `DELIVERY_STATUS_RULES_REQUIRED_SECTIONS` | module configuration |


## 3. Error Handling

| Exception | When | Raised By |
|-----------|------|----------|
| `ValueError` | If document has no defined section requirements | `get_required_sections` |


## 4. Testing

### 4.1 Test Coverage

| Test File | Coverage Area |
|-----------|---------------|
| (none) | No test references found |


## 5. Change Log

| Date | Change | Verified By |
|------|--------|-------------|
| 2026-07-23 | Initial baseline generated from repository scan | sdlc_00_codebase_v1 |
