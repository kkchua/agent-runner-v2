---
title: "Module Documentation: agent_runner_v2.operator_console.services.runner_service"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/operator_console/services/runner_service.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-operator-console-services-runner-service.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-20260723-e1c86100 / 2026-07-23T21:41:19+08:00"
created: "2026-07-23T21:41:19+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.operator_console.services.runner_service

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `contextlib` | stdlib module | imported dependency |
| `io` | stdlib module | imported dependency |
| `logging` | stdlib module | imported dependency |
| `os` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `backend_client` | external module | repository dependency |
| `models` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

#### ActionExecutionError

**Inherits from**: `RuntimeError`

**Purpose**: Public class

#### RunnerActionService

**Purpose**: Public class

**Methods**:

- `submit_job(*, repo_path: str, workflow: WorkflowEntry, initiative_id: str = '', coder: str = '')` -> `str` -- method
- `init_workspace(*, repo_path: str, workflow_name: str = 'default', bundle_domain: str = 'general', bundle_profile: str = 'core+workflow')` -> `str` -- method
- `bootstrap_publish(*, repo_path: str)` -> `str` -- method
- `sync_workflow(*, repo_path: str, workflow: WorkflowEntry | None = None)` -> `str` -- method
- `cleanup_execution(*, workflow_name: str, dry_run: bool = False)` -> `str` -- method
- `approve_step(*, repo_path: str, template_group: str, job_id: str, step_name: str)` -> `str` -- method
- `override_step(*, repo_path: str, template_group: str, job_id: str, step_name: str)` -> `str` -- method


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
