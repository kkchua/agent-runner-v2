---
title: "Module Documentation: agent_runner_v2.actions.submit_comfyui"
template_id: "CB-02"
status: "active"
module_path: "agent_runner_v2/actions/submit_comfyui.py"
module_area: "actions"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/02_modules/agent-runner-v2-actions-submit-comfyui.md"
last_verified_by_change: "00_repo_master_docs_bootstrap_v1 / 00RMD-20260716-5ee28fa5 / 2026-07-16T22:09:16+08:00"
created: "2026-07-16T22:09:16+08:00"
owner: "00_repo_master_docs_bootstrap_v1"
---

# Module Documentation: agent_runner_v2.actions.submit_comfyui

## 1. Module Overview

### 1.1 Purpose

actions/submit_comfyui.py - Submit prompt entries to ComfyUI remote API.

### 1.2 Responsibility

This module belongs to the `actions` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `datetime` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `os` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `time` | stdlib module | imported dependency |
| `urllib.error` | stdlib module | imported dependency |
| `urllib.request` | stdlib module | imported dependency |
| `action_result` | external module | repository dependency |
| `runtime_context` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### submit_comfyui()

**Signature**: `submit_comfyui(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path)`

**Purpose**: Submit all prompt entries from IMAGE_CSV_RUN_DIR to ComfyUI API.

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
| `_PACKAGE_ROOT` | module configuration |


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
