---
title: "Module Documentation: agent_runner_v2.run_agent"
template_id: "CB-02"
status: "active"
module_path: "agent_runner_v2/run_agent.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/02_modules/agent-runner-v2-run-agent.md"
last_verified_by_change: "00_repo_master_docs_bootstrap_v1 / 00RMD-20260716-5ee28fa5 / 2026-07-16T22:09:16+08:00"
created: "2026-07-16T22:09:16+08:00"
owner: "00_repo_master_docs_bootstrap_v1"
---

# Module Documentation: agent_runner_v2.run_agent

## 1. Module Overview

### 1.1 Purpose

run_agent.py â€” Main CLI entry point for agent_runner_v2.

### 1.2 Responsibility

This module belongs to the `core` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `argparse` | stdlib module | imported dependency |
| `datetime` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `os` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `re` | stdlib module | imported dependency |
| `shutil` | stdlib module | imported dependency |
| `sys` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `backend_client` | external module | repository dependency |
| `bundle_loader` | external module | repository dependency |
| `constants` | external module | repository dependency |
| `doc_paths` | external module | repository dependency |
| `documentation_guardrails` | external module | repository dependency |
| `exceptions` | external module | repository dependency |
| `execution_core` | external module | repository dependency |
| `execution_request` | external module | repository dependency |
| `execution_result` | external module | repository dependency |
| `failure_runtime` | external module | repository dependency |
| `job_state` | external module | repository dependency |
| `model_config` | external module | repository dependency |
| `routing_runtime` | external module | repository dependency |
| `runner_logger` | external module | repository dependency |
| `runtime_context` | external module | repository dependency |
| `step_runner` | external module | repository dependency |
| `task_runtime` | external module | repository dependency |
| `workflow_packages.loader` | external module | repository dependency |
| `workflow_router` | external module | repository dependency |
| `workflow_specs` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### parse_args()

**Signature**: `parse_args(argv: list[str] | None = None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `argv` | `list[str] | None` | `None` | — |

**Returns**: `argparse.Namespace`

---

#### main()

**Signature**: `main(argv: list[str] | None = None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `argv` | `list[str] | None` | `None` | — |

**Returns**: `int`

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
| 2026-07-16 | Initial baseline generated from repository scan | 00_repo_master_docs_bootstrap_v1 |
