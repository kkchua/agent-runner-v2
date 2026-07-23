---
title: "Module Documentation: agent_runner_v2.bootstrap.workflows.default.sdlc_60_execution_v1.context_extensions"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/bootstrap/workflows/default/sdlc_60_execution_v1/context_extensions.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-60-execution-v1-context-extensions.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-20260723-d46af7f2 / 2026-07-23T20:54:20+08:00"
created: "2026-07-23T20:54:20+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.bootstrap.workflows.default.sdlc_60_execution_v1.context_extensions

## 1. Module Overview

### 1.1 Purpose

Context extensions for sdlc_60_execution_v1 workflow.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `datetime` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `re` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `agent_runner_v2.constants` | internal module | repository dependency |
| `agent_runner_v2.runtime_context` | internal module | repository dependency |
| `agent_runner_v2.workflow_packages.extensions_base` | internal module | repository dependency |

## 2. Public API

### 2.1 Classes

#### Sdlc60ExecutionExtensions

**Inherits from**: `WorkflowExtensions`

**Purpose**: Workflow extension hooks for sdlc_60_execution_v1.

**Methods**:

- `register_artifact_keys(*, job_id: str = '{job_id}', mode: str = '{mode}')` -> `dict[str, str]` -- method
- `build_context_extensions(*, state: dict[str, Any], step: str, step_cfg: dict[str, Any], ctx: dict[str, str], project_root: Path | None = None)` -> `dict[str, str]` -- method


### 2.2 Functions

No public functions.


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
