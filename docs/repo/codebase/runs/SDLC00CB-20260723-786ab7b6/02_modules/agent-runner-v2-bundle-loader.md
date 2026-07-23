---
title: "Module Documentation: agent_runner_v2.bundle_loader"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/bundle_loader.py"
module_area: "bootstrap"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-bundle-loader.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-20260723-786ab7b6 / 2026-07-23T21:25:54+08:00"
created: "2026-07-23T21:25:54+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.bundle_loader

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `bootstrap` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `datetime` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `shutil` | stdlib module | imported dependency |
| `sys` | stdlib module | imported dependency |
| `types` | stdlib module | imported dependency |
| `bundle_governance` | external module | repository dependency |
| `bundle_taxonomy` | external module | repository dependency |
| `constants` | external module | repository dependency |
| `doc_paths` | external module | repository dependency |
| `runtime_context` | external module | repository dependency |
| `workflow_bundle_validator` | external module | repository dependency |
| `workflow_packages.loader` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

#### WorkflowBundlePublishValidationError

**Inherits from**: `RuntimeError`

**Purpose**: Raised when repo-root workflow bundles fail preflight validation.


### 2.2 Functions

#### bundles_root()

**Signature**: `bundles_root()`

**Returns**: `Path`

---

#### core_bundles_root()

**Signature**: `core_bundles_root()`

**Returns**: `Path`

---

#### domain_bundles_root()

**Signature**: `domain_bundles_root()`

**Returns**: `Path`

---

#### workflow_bundles_root()

**Signature**: `workflow_bundles_root()`

**Returns**: `Path`

---

#### config_path()

**Signature**: `config_path(workspace_root: Path)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `workspace_root` | `Path` | -- | -- |

**Returns**: `Path`

---

#### workflows_root()

**Signature**: `workflows_root(workspace_root: Path)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `workspace_root` | `Path` | -- | -- |

**Returns**: `Path`

---

#### workflow_root()

**Signature**: `workflow_root(workspace_root: Path, workflow_name: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `workspace_root` | `Path` | -- | -- |
| `workflow_name` | `str` | -- | -- |

**Returns**: `Path`

---

#### global_workflows_root()

**Signature**: `global_workflows_root()`

**Returns**: `Path`

---

#### global_workflow_root()

**Signature**: `global_workflow_root(workflow_name: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `workflow_name` | `str` | -- | -- |

**Returns**: `Path`

---

#### package_bootstrap_root()

**Signature**: `package_bootstrap_root()`

**Returns**: `Path`

---

#### global_bootstrap_root()

**Signature**: `global_bootstrap_root()`

**Returns**: `Path`

---

#### bootstrap_source_root()

**Signature**: `bootstrap_source_root(workspace_root: Path)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `workspace_root` | `Path` | -- | -- |

**Returns**: `Path`

---

#### published_workflows_root()

**Signature**: `published_workflows_root(workspace_root: Path)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `workspace_root` | `Path` | -- | -- |

**Returns**: `Path`

---

#### publish_bootstrap_bundle()

**Signature**: `publish_bootstrap_bundle(workspace_root: Path, *, source_root: Path | None = None, package_root: Path | None = None, plugin_workflows_root: Path | None = None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `workspace_root` | `Path` | -- | -- |
| `source_root` | `Path | None` | `None` | -- |
| `package_root` | `Path | None` | `None` | -- |
| `plugin_workflows_root` | `Path | None` | `None` | -- |

**Returns**: `dict`

---

#### install_bootstrap_bundle()

**Signature**: `install_bootstrap_bundle(workspace_root: Path, *, runner_home: Path | None = None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `workspace_root` | `Path` | -- | -- |
| `runner_home` | `Path | None` | `None` | -- |

**Returns**: `dict`

---

#### install_platform_bundle()

**Signature**: `install_platform_bundle(workspace_root: Path, *, runner_home: Path | None = None)`

**Purpose**: Install Layer 2 platform bundles to the global runner home.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `workspace_root` | `Path` | -- | Repository root directory. |
| `runner_home` | `Path | None` | `None` | Override for the global runner home path. |

**Returns**: `dict`

---

#### install_workflow_plugins()

**Signature**: `install_workflow_plugins(workspace_root: Path, *, runner_home: Path | None = None)`

**Purpose**: Scan workflow folders for install.py scripts and execute them.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `workspace_root` | `Path` | -- | Repository root directory. |
| `runner_home` | `Path | None` | `None` | Override for the global runner home path. |

**Returns**: `dict`

---

#### resolve_workflow_root()

**Signature**: `resolve_workflow_root(workspace_root: Path, workflow_name: str, *, config: dict | None = None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `workspace_root` | `Path` | -- | -- |
| `workflow_name` | `str` | -- | -- |
| `config` | `dict | None` | `None` | -- |

**Returns**: `Path`

---

#### load_project_config()

**Signature**: `load_project_config(workspace_root: Path)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `workspace_root` | `Path` | -- | -- |

**Returns**: `dict`

---

#### save_project_config()

**Signature**: `save_project_config(workspace_root: Path, config: dict)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `workspace_root` | `Path` | -- | -- |
| `config` | `dict` | -- | -- |

**Returns**: `None`

---

#### load_workflow_module()

**Signature**: `load_workflow_module(workspace_root: Path, workflow_name: str, *, config: dict | None = None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `workspace_root` | `Path` | -- | -- |
| `workflow_name` | `str` | -- | -- |
| `config` | `dict | None` | `None` | -- |

**Returns**: `ModuleType`

---

#### seed_workflow_bundle()

**Signature**: `seed_workflow_bundle(target_root: Path, workflow_name: str = 'default')`

**Purpose**: Copy the entire bootstrap workflows/default/ tree into the target global workflow location.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `target_root` | `Path` | -- | -- |
| `workflow_name` | `str` | `'default'` | -- |

**Returns**: `Path`

---

#### seed_workflow_packages()

**Signature**: `seed_workflow_packages(workspace_root: Path, workflow_name: str = 'default', *, source_root: Path | None = None)`

**Purpose**: Copy published workflow packages into the global runner home.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `workspace_root` | `Path` | -- | -- |
| `workflow_name` | `str` | `'default'` | -- |
| `source_root` | `Path | None` | `None` | -- |

**Returns**: `list[Path]`

---

#### init_workspace()

**Signature**: `init_workspace(workspace_root: Path, workflow_name: str = 'default', *, domain: str = DEFAULT_DOMAIN_BUNDLE, bundle_profile: str = DEFAULT_BUNDLE_PROFILE)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `workspace_root` | `Path` | -- | -- |
| `workflow_name` | `str` | `'default'` | -- |
| `domain` | `str` | `DEFAULT_DOMAIN_BUNDLE` | -- |
| `bundle_profile` | `str` | `DEFAULT_BUNDLE_PROFILE` | -- |

**Returns**: `dict`

---


### 2.3 Constants / Configuration

| Name | Purpose |
|------|--------|
| `GLOBAL_RUNNER_HOME` | module configuration |
| `BOOTSTRAP_ROOT` | module configuration |
| `BOOTSTRAP_SOURCE_ROOT` | module configuration |
| `FOUNDATION_CURRENT_ROOT_REL` | module configuration |
| `PLATFORM_CURRENT_ROOT_REL` | module configuration |
| `PACKAGE_BOOTSTRAP_ROOT` | module configuration |
| `PACKAGED_BOOTSTRAP_EXCLUDE_PATTERNS` | module configuration |
| `PACKAGED_BOOTSTRAP_EXCLUDED_WORKFLOWS` | module configuration |


## 3. Error Handling

No documented exceptions.


## 4. Testing

### 4.1 Test Coverage

| Test File | Coverage Area |
|-----------|---------------|
| `tests/conftest.py` | `agent_runner_v2.bundle_loader` |


## 5. Change Log

| Date | Change | Verified By |
|------|--------|-------------|
| 2026-07-23 | Initial baseline generated from repository scan | sdlc_00_codebase_v1 |
