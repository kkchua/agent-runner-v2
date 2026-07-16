---
title: "Module Documentation: agent_runner_v2.step_execution_runtime"
template_id: "CB-02"
status: "active"
module_path: "agent_runner_v2/step_execution_runtime.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/02_modules/agent-runner-v2-step-execution-runtime.md"
last_verified_by_change: "00_repo_master_docs_bootstrap_v1 / 00RMD-20260716-5ee28fa5 / 2026-07-16T22:09:16+08:00"
created: "2026-07-16T22:09:16+08:00"
owner: "00_repo_master_docs_bootstrap_v1"
---

# Module Documentation: agent_runner_v2.step_execution_runtime

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
| `shutil` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `constants` | external module | repository dependency |
| `documentation_guardrails` | external module | repository dependency |
| `model_config` | external module | repository dependency |
| `runner_logger` | external module | repository dependency |
| `step_runner` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

#### PreparedStepExecution

**Decorators**: `@dataclass`

**Purpose**: Public class


### 2.2 Functions

#### prepare_step_execution()

**Signature**: `prepare_step_execution(*, template_group: str, group_cfg: dict[str, Any], state: dict[str, Any], step: str, step_cfg: dict[str, Any], project_root: Path, workflow_key_override: str = '', cli_coder: str | None = None, hooks: Any)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `template_group` | `str` | — | — |
| `group_cfg` | `dict[str, Any]` | — | — |
| `state` | `dict[str, Any]` | — | — |
| `step` | `str` | — | — |
| `step_cfg` | `dict[str, Any]` | — | — |
| `project_root` | `Path` | — | — |
| `workflow_key_override` | `str` | `''` | — |
| `cli_coder` | `str | None` | `None` | — |
| `hooks` | `Any` | — | — |

**Returns**: `PreparedStepExecution`

---

#### augment_generated_doc_prompt()

**Signature**: `augment_generated_doc_prompt(template_text: str, *, template_group: str, step: str, step_cfg: dict[str, Any], state: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `template_text` | `str` | — | — |
| `template_group` | `str` | — | — |
| `step` | `str` | — | — |
| `step_cfg` | `dict[str, Any]` | — | — |
| `state` | `dict[str, Any]` | — | — |

**Returns**: `str`

---

#### generated_doc_frontmatter_contract()

**Signature**: `generated_doc_frontmatter_contract(*, template_group: str, step: str, step_cfg: dict[str, Any], state: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `template_group` | `str` | — | — |
| `step` | `str` | — | — |
| `step_cfg` | `dict[str, Any]` | — | — |
| `state` | `dict[str, Any]` | — | — |

**Returns**: `str`

---

#### master_bootstrap_frontmatter_rows()

**Signature**: `master_bootstrap_frontmatter_rows(*, step_cfg: dict[str, Any], state: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `step_cfg` | `dict[str, Any]` | — | — |
| `state` | `dict[str, Any]` | — | — |

**Returns**: `list[tuple[str, str, str]]`

---

#### execute_prepared_step()

**Signature**: `execute_prepared_step(*, prepared: PreparedStepExecution, template_group: str, group_cfg: dict[str, Any], state: dict[str, Any], step: str, step_cfg: dict[str, Any], effective_root: Path, hooks: Any)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `prepared` | `PreparedStepExecution` | — | — |
| `template_group` | `str` | — | — |
| `group_cfg` | `dict[str, Any]` | — | — |
| `state` | `dict[str, Any]` | — | — |
| `step` | `str` | — | — |
| `step_cfg` | `dict[str, Any]` | — | — |
| `effective_root` | `Path` | — | — |
| `hooks` | `Any` | — | — |

**Returns**: `StepResult`

---

#### resolve_step_coder()

**Signature**: `resolve_step_coder(*, group_cfg: dict[str, Any], state: dict[str, Any], step: str, step_cfg: dict[str, Any], cli_coder: str | None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_cfg` | `dict[str, Any]` | — | — |
| `state` | `dict[str, Any]` | — | — |
| `step` | `str` | — | — |
| `step_cfg` | `dict[str, Any]` | — | — |
| `cli_coder` | `str | None` | — | — |

**Returns**: `tuple[str, str | None, str | None, dict[str, Any] | None]`

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
