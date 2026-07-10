---
title: "Module Documentation: agent_runner_v2.actions.validate_delivery_docs"
template_id: "CB-02"
status: "active"
module_path: "agent_runner_v2/actions/validate_delivery_docs.py"
module_area: "actions"
documentation_mode: "full"
owner_doc_path: "docs/codebase/02_modules/agent-runner-v2-actions-validate-delivery-docs.md"
last_verified_by_change: "00_master_docs_bootstrap_v2 / 00DOC-20260710-0098bf53 / 2026-07-10T19:43:53+08:00"
created: "2026-07-10T19:43:53+08:00"
owner: "00_master_docs_bootstrap_v2"
---

# Module Documentation: agent_runner_v2.actions.validate_delivery_docs

## 1. Module Overview

### 1.1 Purpose

actions/validate_delivery_docs.py — Deterministic validation of scaffolded delivery docs.

### 1.2 Responsibility

This module belongs to the `actions` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `datetime` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `logging` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `re` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `action_result` | external module | repository dependency |
| `constants` | external module | repository dependency |
| `doc_paths` | external module | repository dependency |
| `documentation_validation_core` | external module | repository dependency |
| `runtime_context` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### validate_delivery_docs()

**Signature**: `validate_delivery_docs(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path)`

**Purpose**: Validate the complete delivery documentation scaffold.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | `dict[str, str]` | — | — |
| `state` | `dict` | — | — |
| `step_cfg` | `dict` | — | — |
| `project_root` | `Path` | — | — |

**Returns**: `ActionResult`

---


### 2.3 Constants / Configuration

| Name | Purpose |
|------|--------|
| `DELIVERY_FOLDERS` | module configuration |
| `REQUIRED_TEMPLATES` | module configuration |
| `REQUIRED_CODEBASE_FILES` | module configuration |
| `REQUIRED_SYSTEM_FILES` | module configuration |
| `AGENT_CONTRACT_PATHS` | module configuration |
| `AGENT_REGISTRY_ENTRY_PATTERN` | module configuration |


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
