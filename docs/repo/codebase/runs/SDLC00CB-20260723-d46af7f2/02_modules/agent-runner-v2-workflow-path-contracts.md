---
title: "Module Documentation: agent_runner_v2.workflow_path_contracts"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/workflow_path_contracts.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-path-contracts.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-20260723-d46af7f2 / 2026-07-23T20:54:20+08:00"
created: "2026-07-23T20:54:20+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.workflow_path_contracts

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `functools` | stdlib module | imported dependency |
| `importlib.util` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `types` | stdlib module | imported dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### resolve_workflow_output_paths()

**Signature**: `resolve_workflow_output_paths(*, template_group: str, job_id: str = '{job_id}', mode: str = '{mode}')`

**Purpose**: Resolve artifact output paths for a workflow.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `template_group` | `str` | -- | Workflow package name. |
| `job_id` | `str` | `'{job_id}'` | Job identifier for path construction. |
| `mode` | `str` | `'{mode}'` | Execution mode. |

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
