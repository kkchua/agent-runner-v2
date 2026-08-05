---
title: "Module Documentation: agent_runner_v2.runtime_context"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/runtime_context.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-runtime-context.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-mqe50g5d / 2026-08-06T05:49:37+08:00"
created: "2026-08-06T05:49:37+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.runtime_context

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `core` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `dataclasses` | stdlib module | imported dependency |
| `datetime` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `tempfile` | stdlib module | imported dependency |
| `types` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |

## 2. Public API

### 2.1 Classes

#### RuntimeContext

**Decorators**: `@dataclass`

**Purpose**: Process-local runtime context for the agent runner.

#### PathProxy

**Purpose**: Lightweight Path-like proxy that resolves lazily from current context.


### 2.2 Functions

#### set_context()

**Signature**: `set_context(*, workspace_root: Path, workflow_name: str | None = None, workflow_root: Path | None = None, workflow_module: ModuleType | None = None, delivery_root: Path | None = None)`

**Purpose**: Set process-local runtime context and return it.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `workspace_root` | `Path` | -- | Project workspace root path. |
| `workflow_name` | `str | None` | `None` | Workflow name (preserves current if None). |
| `workflow_root` | `Path | None` | `None` | Workflow bundle root path. |
| `workflow_module` | `ModuleType | None` | `None` | Optional workflow Python module. |
| `delivery_root` | `Path | None` | `None` | Override root for delivery scaffold artifacts. |

**Returns**: `RuntimeContext`

---

#### get_context()

**Signature**: `get_context()`

**Purpose**: Return the current process-local runtime context.

**Returns**: `RuntimeContext`

---

#### get_workspace_root()

**Signature**: `get_workspace_root()`

**Purpose**: Return the project workspace root path.

**Returns**: `Path`

---

#### get_repo_root()

**Signature**: `get_repo_root()`

**Purpose**: Return the agent-runner-v2 repo root from config, or workspace_root.

**Returns**: `Path`

---

#### get_runner_home()

**Signature**: `get_runner_home()`

**Purpose**: Return the global runner home path (~/.ukbe-runner).

**Returns**: `Path`

---

#### get_jobs_root()

**Signature**: `get_jobs_root()`

**Purpose**: Return the jobs root path (~/.ukbe-runner/jobs).

**Returns**: `Path`

---

#### get_queue_root()

**Signature**: `get_queue_root()`

**Purpose**: Return the outcome queue root path (~/.ukbe-runner/queue).

**Returns**: `Path`

---

#### get_governance_runtime_root()

**Signature**: `get_governance_runtime_root()`

**Purpose**: Return the Layer 1 governance runtime root (global bundle path).

**Returns**: `Path`

---

#### get_platform_runtime_root()

**Signature**: `get_platform_runtime_root()`

**Purpose**: Return the Layer 2 platform runtime root (global bundle path).

**Returns**: `Path`

---

#### get_workflow_root()

**Signature**: `get_workflow_root()`

**Purpose**: Return the workflow bundle root path.

**Returns**: `Path`

---

#### get_workflow_module()

**Signature**: `get_workflow_module()`

**Purpose**: Return the workflow Python module, if loaded.

**Returns**: `ModuleType | None`

---

#### set_workflow_module()

**Signature**: `set_workflow_module(module: ModuleType)`

**Purpose**: Set the workflow module in the current context.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `module` | `ModuleType` | -- | The workflow Python module to set. |

**Returns**: `None`

---

#### get_delivery_root()

**Signature**: `get_delivery_root()`

**Purpose**: Return the delivery scaffold override root, if set.

**Returns**: `Path | None`

---

#### set_delivery_root()

**Signature**: `set_delivery_root(root: Path | None)`

**Purpose**: Set the delivery root in the current context.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `root` | `Path | None` | -- | The delivery root path, or None to clear. |

**Returns**: `None`

---

#### resolve_artifact_root()

**Signature**: `resolve_artifact_root()`

**Purpose**: Return the root for resolving artifact paths.

**Returns**: `Path`

---

#### resolve_repo_or_runtime_path()

**Signature**: `resolve_repo_or_runtime_path(path_str: str, *, project_root: Path | None = None, runtime_root: Path | None = None)`

**Purpose**: Resolve a path using the repo/runtime namespace convention.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `path_str` | `str` | -- | -- |
| `project_root` | `Path | None` | `None` | -- |
| `runtime_root` | `Path | None` | `None` | -- |

**Returns**: `Path`

---

#### format_report_path()

**Signature**: `format_report_path(path_str: str, *, project_root: Path | None = None, runtime_root: Path | None = None)`

**Purpose**: Resolve repo/runtime paths for outward-facing result payloads.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `path_str` | `str` | -- | Path string to resolve. |
| `project_root` | `Path | None` | `None` | Optional project root override. |
| `runtime_root` | `Path | None` | `None` | Optional runtime root override. |

**Returns**: `str`

---

#### format_report_artifacts()

**Signature**: `format_report_artifacts(artifacts: dict[str, Any], *, project_root: Path | None = None, runtime_root: Path | None = None)`

**Purpose**: Format artifact paths for JSON output.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `artifacts` | `dict[str, Any]` | -- | Dict of artifact key to path value. |
| `project_root` | `Path | None` | `None` | Optional project root override. |
| `runtime_root` | `Path | None` | `None` | Optional runtime root override. |

**Returns**: `dict[str, Any]`

---

#### repo_doc_root()

**Signature**: `repo_doc_root(*parts: str)`

**Purpose**: Return the repo docs root path (docs/).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `Path`

---

#### system_doc_root()

**Signature**: `system_doc_root(*parts: str)`

**Purpose**: Return the system governance docs root path.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `Path`

---

#### codebase_doc_root()

**Signature**: `codebase_doc_root(*parts: str)`

**Purpose**: Return the codebase docs root path.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `Path`

---

#### delivery_doc_root()

**Signature**: `delivery_doc_root(*parts: str)`

**Purpose**: Return the delivery docs root path.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `Path`

---

#### architecture_site_root()

**Signature**: `architecture_site_root(*parts: str)`

**Purpose**: Return the architecture site root path.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `Path`

---

#### artifact_rel_to_meta_rel()

**Signature**: `artifact_rel_to_meta_rel(artifact_rel: str)`

**Purpose**: Return the meta.json sibling path for a repo/runtime-relative artifact.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `artifact_rel` | `str` | -- | -- |

**Returns**: `str`

---

#### write_meta_sidecar()

**Signature**: `write_meta_sidecar(meta_path_like: str | Path, *, status: str, remark: str, artifacts: dict, project_root: Path | None = None, runtime_root: Path | None = None, extra: dict[str, Any] | None = None)`

**Purpose**: Write a v2 meta.json sidecar using the shared path resolver.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `meta_path_like` | `str | Path` | -- | -- |
| `status` | `str` | -- | -- |
| `remark` | `str` | -- | -- |
| `artifacts` | `dict` | -- | -- |
| `project_root` | `Path | None` | `None` | -- |
| `runtime_root` | `Path | None` | `None` | -- |
| `extra` | `dict[str, Any] | None` | `None` | -- |

**Returns**: `Path`

---

#### resolve_step_meta_rel()

**Signature**: `resolve_step_meta_rel(*, context: dict[str, str], state: dict, context_key: str, default_step: str)`

**Purpose**: Resolve the meta.json relative path for a step-owned artifact.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | `dict[str, str]` | -- | -- |
| `state` | `dict` | -- | -- |
| `context_key` | `str` | -- | -- |
| `default_step` | `str` | -- | -- |

**Returns**: `str`

---


### 2.3 Constants / Configuration

| Name | Purpose |
|------|--------|
| `PACKAGE_ROOT` | module configuration |
| `DEFAULT_RUNNER_HOME` | module configuration |
| `GLOBAL_RUNNER_HOME` | module configuration |
| `DEFAULT_WORKFLOW_NAME` | module configuration |
| `_CTX` | module configuration |
| `PROJECT_ROOT` | module configuration |
| `RUNNER_HOME` | module configuration |
| `RUNNER_ROOT` | module configuration |
| `JOBS_ROOT` | module configuration |
| `QUEUE_ROOT` | module configuration |
| `DELIVERY_ROOT` | module configuration |
| `ARTIFACT_ROOT` | module configuration |


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
| 2026-08-06 | Initial baseline generated from repository scan | sdlc_00_codebase_v1 |
