---
title: "Module Documentation: agent_runner_v2.coder_registry"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/coder_registry.py"
module_area: "coder"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-coder-registry.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-20260723-d46af7f2 / 2026-07-23T20:54:20+08:00"
created: "2026-07-23T20:54:20+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.coder_registry

## 1. Module Overview

### 1.1 Purpose

Coder connection, semantic role, and role-policy resolver for the agent runner.

### 1.2 Responsibility

This module belongs to the `coder` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `os` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `urllib.parse` | stdlib module | imported dependency |
| `runtime_context` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### load_coder_connections()

**Signature**: `load_coder_connections(bundle_root: Path | str | None = None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `bundle_root` | `Path | str | None` | `None` | -- |

**Returns**: `dict[str, dict[str, Any]]`

---

#### load_role_policies()

**Signature**: `load_role_policies(bundle_root: Path | str | None = None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `bundle_root` | `Path | str | None` | `None` | -- |

**Returns**: `dict[str, dict[str, Any]]`

---

#### coder_roles_path()

**Signature**: `coder_roles_path(bundle_root: Path | str | None = None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `bundle_root` | `Path | str | None` | `None` | -- |

**Returns**: `Path | None`

---

#### load_coder_roles()

**Signature**: `load_coder_roles(bundle_root: Path | str | None = None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `bundle_root` | `Path | str | None` | `None` | -- |

**Returns**: `dict[str, dict[str, Any]]`

---

#### resolve_connection()

**Signature**: `resolve_connection(connection_name: str, *, bundle_root: Path | str | None = None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `connection_name` | `str` | -- | -- |
| `bundle_root` | `Path | str | None` | `None` | -- |

**Returns**: `dict[str, Any] | None`

---

#### resolve_role_policy()

**Signature**: `resolve_role_policy(policy_name: str, *, bundle_root: Path | str | None = None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `policy_name` | `str` | -- | -- |
| `bundle_root` | `Path | str | None` | `None` | -- |

**Returns**: `dict[str, Any] | None`

---

#### resolve_coder_role()

**Signature**: `resolve_coder_role(role_name: str, *, bundle_root: Path | str | None = None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `role_name` | `str` | -- | -- |
| `bundle_root` | `Path | str | None` | `None` | -- |

**Returns**: `dict[str, Any] | None`

---

#### resolve_effective_coder()

**Signature**: `resolve_effective_coder(*, role_name: str, bundle_root: Path | str | None = None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `role_name` | `str` | -- | -- |
| `bundle_root` | `Path | str | None` | `None` | -- |

**Returns**: `dict[str, Any]`

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
