---
title: "Module Documentation: agent_runner_v2.runner_actions"
template_id: "CB-02"
status: "active"
module_path: "agent_runner_v2/runner_actions.py"
module_area: "schema"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/02_modules/agent-runner-v2-runner-actions.md"
last_verified_by_change: "00_repo_master_docs_bootstrap_v1 / 00RMD-20260716-5ee28fa5 / 2026-07-16T22:09:16+08:00"
created: "2026-07-16T22:09:16+08:00"
owner: "00_repo_master_docs_bootstrap_v1"
---

# Module Documentation: agent_runner_v2.runner_actions

## 1. Module Overview

### 1.1 Purpose

runner_actions.py — Registry and dispatch for non-coder step actions.

### 1.2 Responsibility

This module belongs to the `schema` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `logging` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `action_result` | external module | repository dependency |
| `actions.archive_previous_version` | external module | repository dependency |
| `actions.assemble_video` | external module | repository dependency |
| `actions.copy_artifact` | external module | repository dependency |
| `actions.execute_i2v` | external module | repository dependency |
| `actions.execute_t2i` | external module | repository dependency |
| `actions.execute_voiceover` | external module | repository dependency |
| `actions.finalize_bootstrap` | external module | repository dependency |
| `actions.generate_site` | external module | repository dependency |
| `actions.generate_site_pdf` | external module | repository dependency |
| `actions.prepare_delivery_scaffold` | external module | repository dependency |
| `actions.promote_artifact` | external module | repository dependency |
| `actions.promote_init` | external module | repository dependency |
| `actions.publish_architecture_site` | external module | repository dependency |
| `actions.scan_repo_codebase` | external module | repository dependency |
| `actions.step_completion` | external module | repository dependency |
| `actions.submit_comfyui` | external module | repository dependency |
| `actions.sync_codebase_docs` | external module | repository dependency |
| `actions.sync_system_docs` | external module | repository dependency |
| `actions.validate_architecture_site` | external module | repository dependency |
| `actions.validate_codebase_docs` | external module | repository dependency |
| `actions.validate_delivery_docs` | external module | repository dependency |
| `actions.validate_developer_site` | external module | repository dependency |
| `actions.validate_operator_site` | external module | repository dependency |
| `actions.validate_stakeholder_site` | external module | repository dependency |
| `actions.validate_tester_site` | external module | repository dependency |
| `actions.validate_user_site` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### execute()

**Signature**: `execute(*, action_name: str, context: dict[str, str], state: dict, step_cfg: dict, step: str, project_root: Path)`

**Purpose**: Dispatch to a registered action function.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `action_name` | `str` | — | — |
| `context` | `dict[str, str]` | — | — |
| `state` | `dict` | — | — |
| `step_cfg` | `dict` | — | — |
| `step` | `str` | — | — |
| `project_root` | `Path` | — | — |

**Returns**: `ActionResult`

**Raises**:

- `KeyError` — if action_name is not found in either registry.
- `Exception` — action-specific failures (caller routes to failure).

---

#### get_registered_actions()

**Signature**: `get_registered_actions()`

**Purpose**: Return sorted list of registered action names.

**Returns**: `list[str]`

---


### 2.3 Constants / Configuration

No public constants.


## 3. Error Handling

| Exception | When | Raised By |
|-----------|------|----------|
| `Exception` | action-specific failures (caller routes to failure). | `execute` |
| `KeyError` | if action_name is not found in either registry. | `execute` |


## 4. Testing

### 4.1 Test Coverage

| Test File | Coverage Area |
|-----------|---------------|
| (none) | No test references found |


## 5. Change Log

| Date | Change | Verified By |
|------|--------|-------------|
| 2026-07-16 | Initial baseline generated from repository scan | 00_repo_master_docs_bootstrap_v1 |
