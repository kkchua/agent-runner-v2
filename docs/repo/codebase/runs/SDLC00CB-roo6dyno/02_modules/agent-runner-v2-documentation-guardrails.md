---
title: "Module Documentation: agent_runner_v2.documentation_guardrails"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/documentation_guardrails.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-documentation-guardrails.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-roo6dyno / 2026-08-05T23:43:32+08:00"
created: "2026-08-05T23:43:32+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.documentation_guardrails

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `core` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `constants` | external module | repository dependency |
| `doc_paths` | external module | repository dependency |
| `workflow_path_contracts` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### managed_banner()

**Signature**: `managed_banner(*, workflow: str, step: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `workflow` | `str` | -- | -- |
| `step` | `str` | -- | -- |

**Returns**: `str`

---

#### master_bootstrap_doc_paths()

**Signature**: `master_bootstrap_doc_paths(*, job_id: str, mode: str)`

**Purpose**: Get all master bootstrap workflow document paths.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `job_id` | `str` | -- | -- |
| `mode` | `str` | -- | -- |

**Returns**: `list[str]`

---

#### scan_workflow_generated_paths()

**Signature**: `scan_workflow_generated_paths(*, project_root: Path, template_group: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `project_root` | `Path` | -- | -- |
| `template_group` | `str` | -- | -- |

**Returns**: `list[str]`

---

#### workflow_canonical_doc_paths()

**Signature**: `workflow_canonical_doc_paths(*, template_group: str, state: dict)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `template_group` | `str` | -- | -- |
| `state` | `dict` | -- | -- |

**Returns**: `list[str]`

---

#### workflow_legacy_doc_paths()

**Signature**: `workflow_legacy_doc_paths(*, template_group: str, state: dict)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `template_group` | `str` | -- | -- |
| `state` | `dict` | -- | -- |

**Returns**: `list[str]`

---

#### master_bootstrap_artifact_candidates()

**Signature**: `master_bootstrap_artifact_candidates(*, template_group: str, job_id: str, mode: str)`

**Purpose**: Get artifact path candidates for master bootstrap workflow.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `template_group` | `str` | -- | -- |
| `job_id` | `str` | -- | -- |
| `mode` | `str` | -- | -- |

**Returns**: `dict[str, list[str]]`

---

#### execution_scaffold_doc_paths()

**Signature**: `execution_scaffold_doc_paths()`

**Purpose**: Get all execution scaffold workflow document paths.

**Returns**: `list[str]`

---

#### workflow_generated_doc_paths()

**Signature**: `workflow_generated_doc_paths(*, template_group: str, state: dict)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `template_group` | `str` | -- | -- |
| `state` | `dict` | -- | -- |

**Returns**: `list[str]`

---

#### workflow_stale_generated_doc_paths()

**Signature**: `workflow_stale_generated_doc_paths(*, template_group: str, state: dict, project_root: Path)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `template_group` | `str` | -- | -- |
| `state` | `dict` | -- | -- |
| `project_root` | `Path` | -- | -- |

**Returns**: `list[str]`

---

#### workflow_owned_doc_paths_for_cleanup()

**Signature**: `workflow_owned_doc_paths_for_cleanup(*, template_group: str, state: dict, project_root: Path)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `template_group` | `str` | -- | -- |
| `state` | `dict` | -- | -- |
| `project_root` | `Path` | -- | -- |

**Returns**: `list[str]`

---

#### generated_doc_manifest()

**Signature**: `generated_doc_manifest(*, template_group: str, state: dict)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `template_group` | `str` | -- | -- |
| `state` | `dict` | -- | -- |

**Returns**: `str`

---

#### snapshot_paths()

**Signature**: `snapshot_paths(*, project_root: Path, rel_paths: Iterable[str])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `project_root` | `Path` | -- | -- |
| `rel_paths` | `Iterable[str]` | -- | -- |

**Returns**: `dict[str, str]`

---


### 2.3 Constants / Configuration

| Name | Purpose |
|------|--------|
| `ARCHITECTURE_SITE_WORKFLOW` | module configuration |
| `WORKFLOW_GENERATED_MARKER` | module configuration |
| `DEFAULT_LEGACY_QUARANTINE_DIR` | module configuration |


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
| 2026-08-05 | Initial baseline generated from repository scan | sdlc_00_codebase_v1 |
