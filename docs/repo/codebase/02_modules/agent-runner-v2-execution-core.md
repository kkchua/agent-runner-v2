---
title: "Module Documentation: agent_runner_v2.execution_core"
template_id: "CB-02"
status: "active"
module_path: "agent_runner_v2/execution_core.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/02_modules/agent-runner-v2-execution-core.md"
last_verified_by_change: "00_repo_master_docs_bootstrap_v1 / 00RMD-20260716-5ee28fa5 / 2026-07-16T22:09:16+08:00"
created: "2026-07-16T22:09:16+08:00"
owner: "00_repo_master_docs_bootstrap_v1"
---

# Module Documentation: agent_runner_v2.execution_core

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `dataclasses` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `execution_support` | external module | repository dependency |
| `step_runner` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

#### StepExecutionFailure

**Decorators**: `@dataclass`

**Purpose**: Public class

#### StepExecutionAttempt

**Decorators**: `@dataclass`

**Purpose**: Public class

**Methods**:

- `succeeded()` → `bool` — method

#### RoutedStepExecution

**Decorators**: `@dataclass`

**Purpose**: Public class

**Methods**:

- `succeeded()` → `bool` — method


### 2.2 Functions

#### invoke_prepared_step()

**Signature**: `invoke_prepared_step(*, executor: PreparedStepExecutor, prepared: Any, template_group: str, group_cfg: dict[str, Any], state: dict[str, Any], step: str, step_cfg: dict[str, Any], effective_root: Path)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `executor` | `PreparedStepExecutor` | — | — |
| `prepared` | `Any` | — | — |
| `template_group` | `str` | — | — |
| `group_cfg` | `dict[str, Any]` | — | — |
| `state` | `dict[str, Any]` | — | — |
| `step` | `str` | — | — |
| `step_cfg` | `dict[str, Any]` | — | — |
| `effective_root` | `Path` | — | — |

**Returns**: `StepExecutionAttempt`

---

#### execute_routed_step()

**Signature**: `execute_routed_step(*, executor: PreparedStepExecutor, failure_router: FailureRouter, step_router: StepRouter, prepared: Any, group_name: str, group_cfg: dict[str, Any], state: dict[str, Any], step: str, step_cfg: dict[str, Any], coder_used: str, max_rejects: int, effective_root: Path)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `executor` | `PreparedStepExecutor` | — | — |
| `failure_router` | `FailureRouter` | — | — |
| `step_router` | `StepRouter` | — | — |
| `prepared` | `Any` | — | — |
| `group_name` | `str` | — | — |
| `group_cfg` | `dict[str, Any]` | — | — |
| `state` | `dict[str, Any]` | — | — |
| `step` | `str` | — | — |
| `step_cfg` | `dict[str, Any]` | — | — |
| `coder_used` | `str` | — | — |
| `max_rejects` | `int` | — | — |
| `effective_root` | `Path` | — | — |

**Returns**: `RoutedStepExecution`

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
