---
title: "Module Documentation: agent_runner_v2.artifact_paths"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/artifact_paths.py"
module_area: "schema"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-artifact-paths.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-20260723-c66bc6aa / 2026-07-23T20:12:07+08:00"
created: "2026-07-23T20:12:07+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.artifact_paths

## 1. Module Overview

### 1.1 Purpose

artifact_paths.py -- Single source of truth for all step artifact paths.

### 1.2 Responsibility

This module belongs to the `schema` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `datetime` | stdlib module | imported dependency |
| `hashlib` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `logging` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `re` | stdlib module | imported dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### compute_paths()

**Signature**: `compute_paths(*, node_id: str, title: str = '', output_dir: str, ext: str = '.md')`

**Purpose**: Return (artifact_path, meta_json_path) -- single source of truth.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `node_id` | `str` | -- | Task node ID from task graph (e.g., "TASK-20260413-07_supersede-workflow"). |
| `title` | `str` | `''` | Human-readable title (e.g., "Supersede Workflow Implementation"). |
| `output_dir` | `str` | -- | Relative output directory (e.g., "docs/delivery/03_tasks"). |
| `ext` | `str` | `'.md'` | Artifact file extension (default ".md"). |

**Returns**: `tuple[str, str]`

---

#### meta_json_path_for_artifact()

**Signature**: `meta_json_path_for_artifact(artifact_path: str)`

**Purpose**: Return the meta.json path for any artifact path.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `artifact_path` | `str` | -- | -- |

**Returns**: `str`

---

#### load_meta_json()

**Signature**: `load_meta_json(artifact_path: str)`

**Purpose**: Load coder-written meta.json. Returns None if missing.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `artifact_path` | `str` | -- | -- |

**Returns**: `dict | None`

---

#### read_coder_result()

**Signature**: `read_coder_result(artifact_path: str)`

**Purpose**: Read coder_result from meta.json. Returns None if missing or invalid.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `artifact_path` | `str` | -- | -- |

**Returns**: `dict | None`

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
