---
title: "Module Documentation: agent_runner_v2.coder_registry"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/coder_registry.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-coder-registry.md"
last_verified_by_change: "sdlc_00_codebase_scaffold_v1 / SDLC00CS-1zcrrbbs / 2026-08-17T21:19:17+08:00"
created: "2026-08-17T21:19:17+08:00"
owner: "sdlc_00_codebase_scaffold_v1"
---

# Module Documentation: agent_runner_v2.coder_registry

## 1. Module Overview

### 1.1 Purpose

Coder connection, semantic role, and role-policy resolver for the agent runner.

### 1.2 Responsibility

This module belongs to the `core` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `os` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `urllib.parse` | stdlib module | imported dependency |
| `exceptions` | external module | repository dependency |
| `runtime_context` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### load_coder_connections()

**Signature**: `load_coder_connections(bundle_root: Path | str | None = None)`

**Purpose**: Load coder connections from registry.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `bundle_root` | `Path | str | None` | `None` | Optional bundle root for workflow registry lookup. |

**Returns**: `dict[str, dict[str, Any]]`

---

#### load_role_policies()

**Signature**: `load_role_policies(bundle_root: Path | str | None = None)`

**Purpose**: Load role policies from registry.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `bundle_root` | `Path | str | None` | `None` | Optional bundle root for workflow registry lookup. |

**Returns**: `dict[str, dict[str, Any]]`

---

#### coder_roles_path()

**Signature**: `coder_roles_path(bundle_root: Path | str | None = None)`

**Purpose**: Return the path to coder_roles.json registry file.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `bundle_root` | `Path | str | None` | `None` | Optional bundle root for workflow registry lookup. |

**Returns**: `Path`

**Raises**:

- `NotFoundError` -- If coder_roles.json is not found in any registry.

---

#### load_coder_roles()

**Signature**: `load_coder_roles(bundle_root: Path | str | None = None)`

**Purpose**: Load coder roles from registry.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `bundle_root` | `Path | str | None` | `None` | Optional bundle root for workflow registry lookup. |

**Returns**: `dict[str, dict[str, Any]]`

---

#### resolve_connection()

**Signature**: `resolve_connection(connection_name: str, *, bundle_root: Path | str | None = None)`

**Purpose**: Resolve a named connection configuration.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `connection_name` | `str` | -- | Connection name to look up. |
| `bundle_root` | `Path | str | None` | `None` | Optional bundle root for workflow registry lookup. |

**Returns**: `dict[str, Any] | None`

---

#### resolve_role_policy()

**Signature**: `resolve_role_policy(policy_name: str, *, bundle_root: Path | str | None = None)`

**Purpose**: Resolve a named role policy.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `policy_name` | `str` | -- | Policy name to look up. |
| `bundle_root` | `Path | str | None` | `None` | Optional bundle root for workflow registry lookup. |

**Returns**: `dict[str, Any] | None`

---

#### resolve_coder_role()

**Signature**: `resolve_coder_role(role_name: str, *, bundle_root: Path | str | None = None)`

**Purpose**: Resolve a named coder role configuration.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `role_name` | `str` | -- | Role name to look up. |
| `bundle_root` | `Path | str | None` | `None` | Optional bundle root for workflow registry lookup. |

**Returns**: `dict[str, Any] | None`

---

#### resolve_effective_coder()

**Signature**: `resolve_effective_coder(*, role_name: str, bundle_root: Path | str | None = None)`

**Purpose**: Resolve a coder role to an effective coder configuration.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `role_name` | `str` | -- | Coder role name to resolve. |
| `bundle_root` | `Path | str | None` | `None` | Optional bundle root for workflow registry lookup. |

**Returns**: `dict[str, Any]`

**Raises**:

- `ValueError` -- If role, connection, or model is invalid or missing.

---

#### get_api_key()

**Signature**: `get_api_key(coder_config: dict[str, Any])`

**Purpose**: Retrieve an API key for a resolved coder config from environment variables.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `coder_config` | `dict[str, Any]` | -- | -- |

**Returns**: `str | None`

---


### 2.3 Constants / Configuration

No public constants.


## 3. Error Handling

| Exception | When | Raised By |
|-----------|------|----------|
| `NotFoundError` | If coder_roles.json is not found in any registry. | `coder_roles_path` |
| `ValueError` | If role, connection, or model is invalid or missing. | `resolve_effective_coder` |


## 4. Testing

### 4.1 Test Coverage

| Test File | Coverage Area |
|-----------|---------------|
| (none) | No test references found |


## 5. Change Log

| Date | Change | Verified By |
|------|--------|-------------|
| 2026-08-17 | Initial baseline generated from repository scan | sdlc_00_codebase_scaffold_v1 |
