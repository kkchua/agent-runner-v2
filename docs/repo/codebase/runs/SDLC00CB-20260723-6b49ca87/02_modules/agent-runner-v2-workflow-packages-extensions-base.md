---
title: "Module Documentation: agent_runner_v2.workflow_packages.extensions_base"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/workflow_packages/extensions_base.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-packages-extensions-base.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-20260723-6b49ca87 / 2026-07-23T21:17:05+08:00"
created: "2026-07-23T21:17:05+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.workflow_packages.extensions_base

## 1. Module Overview

### 1.1 Purpose

Base class for workflow plugin lifecycle hooks.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |

## 2. Public API

### 2.1 Classes

#### WorkflowExtensions

**Purpose**: Base class for workflow plugin lifecycle hooks.

**Methods**:

- `register_artifact_keys(*, job_id: str = '{job_id}', mode: str = '{mode}')` -> `dict[str, str]` -- Return artifact key to relative-path mappings.
- `build_context_extensions(*, state: dict[str, Any], step: str, step_cfg: dict[str, Any], ctx: dict[str, str], project_root: Path | None = None)` -> `dict[str, str]` -- Return additional context variables for prompt rendering.
- `init(*, workspace_root: Path, runner_home: Path)` -> `None` -- One-time initialization when ``ukbe-run-agent init`` runs.


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
