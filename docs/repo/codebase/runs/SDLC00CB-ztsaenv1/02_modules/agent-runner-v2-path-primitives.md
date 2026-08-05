---
title: "Module Documentation: agent_runner_v2.path_primitives"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/path_primitives.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-path-primitives.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-ztsaenv1 / 2026-08-05T15:42:22+08:00"
created: "2026-08-05T15:42:22+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.path_primitives

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

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### relpath()

**Signature**: `relpath(*parts: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### artifact_path()

**Signature**: `artifact_path(artifact_key: str, folder_key: str, extension: str = EXT_MD)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `artifact_key` | `str` | -- | -- |
| `folder_key` | `str` | -- | -- |
| `extension` | `str` | `EXT_MD` | -- |

**Returns**: `str`

---

#### placeholder()

**Signature**: `placeholder(key: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `key` | `str` | -- | -- |

**Returns**: `str`

---

#### file_in_folder()

**Signature**: `file_in_folder(folder_key: str, filename: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `folder_key` | `str` | -- | -- |
| `filename` | `str` | -- | -- |

**Returns**: `str`

---

#### artifact_meta_path()

**Signature**: `artifact_meta_path(artifact_rel: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `artifact_rel` | `str` | -- | -- |

**Returns**: `str`

---

#### system_doc_rel()

**Signature**: `system_doc_rel(*parts: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### codebase_doc_rel()

**Signature**: `codebase_doc_rel(*parts: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### repo_governance_rel()

**Signature**: `repo_governance_rel(*parts: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### delivery_doc_rel()

**Signature**: `delivery_doc_rel(*parts: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### system_delivery_template_rel()

**Signature**: `system_delivery_template_rel(*parts: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### system_codebase_template_rel()

**Signature**: `system_codebase_template_rel(*parts: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### docs_site_rel()

**Signature**: `docs_site_rel(*parts: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### stakeholder_site_rel()

**Signature**: `stakeholder_site_rel(*parts: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### developer_site_rel()

**Signature**: `developer_site_rel(*parts: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### operator_site_rel()

**Signature**: `operator_site_rel(*parts: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### tester_site_rel()

**Signature**: `tester_site_rel(*parts: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### user_site_rel()

**Signature**: `user_site_rel(*parts: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### legacy_codebase_doc_rel()

**Signature**: `legacy_codebase_doc_rel(*parts: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### legacy_delivery_doc_rel()

**Signature**: `legacy_delivery_doc_rel(*parts: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### legacy_docs_site_rel()

**Signature**: `legacy_docs_site_rel(*parts: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### repo_doc_rel()

**Signature**: `repo_doc_rel(*parts: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### docs_root_rel()

**Signature**: `docs_root_rel(*parts: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### system_template_rel()

**Signature**: `system_template_rel(*parts: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### architecture_site_rel()

**Signature**: `architecture_site_rel(*parts: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---


### 2.3 Constants / Configuration

| Name | Purpose |
|------|--------|
| `EXT_MD` | module configuration |
| `EXT_JSON` | module configuration |
| `EXT_HTML` | module configuration |
| `EXT_PDF` | module configuration |
| `FILENAME_CHANGE_LOG_PATTERN` | module configuration |
| `FILENAME_VALIDATION_PATTERN` | module configuration |
| `FILENAME_BOOTSTRAP_SUMMARY_PATTERN` | module configuration |
| `FILENAME_SNAPSHOT_PATTERN` | module configuration |
| `FILENAME_CODEBASE_INVENTORY` | module configuration |
| `FILENAME_DELIVERY_TEMPLATE_REGISTRY` | module configuration |
| `FILENAME_DELIVERY_INITIATIVE_TEMPLATE` | module configuration |
| `FILENAME_DELIVERY_PLAN_TEMPLATE` | module configuration |
| `FILENAME_DELIVERY_TASK_GRAPH_TEMPLATE` | module configuration |
| `FILENAME_DELIVERY_TASK_TEMPLATE` | module configuration |
| `FILENAME_DELIVERY_IMPL_TEMPLATE` | module configuration |
| `FILENAME_DELIVERY_REVIEW_TEMPLATE` | module configuration |
| `FILENAME_DELIVERY_VALIDATION_TEMPLATE` | module configuration |
| `FILENAME_DELIVERY_MEMORY_TEMPLATE` | module configuration |
| `FILENAME_CODEBASE_TEMPLATE_REGISTRY` | module configuration |
| `FILENAME_CODEBASE_INVENTORY_TEMPLATE` | module configuration |
| `FILENAME_CODEBASE_MODULE_TEMPLATE` | module configuration |
| `FILENAME_CODEBASE_COMPONENT_TEMPLATE` | module configuration |
| `FILENAME_CODEBASE_CHANGE_TEMPLATE` | module configuration |
| `FILENAME_SITE_INDEX_HTML` | module configuration |
| `FILENAME_SITE_MANIFEST_JSON` | module configuration |
| `FILENAME_SITE_CONTENT_MD` | module configuration |
| `FILENAME_SITE_INDEX_BASE` | module configuration |
| `FILENAME_META_JSON` | module configuration |
| `FILENAME_SUBMISSION_RESULTS_JSON` | module configuration |
| `FILENAME_SUBMISSION_RESULTS_META_JSON` | module configuration |
| `FILENAME_BUG_REPORT` | module configuration |
| `FILENAME_BUG_REPRODUCTION` | module configuration |
| `FILENAME_ROOT_CAUSE` | module configuration |
| `FILENAME_PATCH` | module configuration |
| `FILENAME_ARCH_STAKEHOLDER_HTML` | module configuration |
| `FILENAME_ARCH_DEVELOPER_HTML` | module configuration |
| `FILENAME_ARCH_FUNCTIONAL_HTML` | module configuration |
| `FILENAME_ARCH_RUNTIME_HTML` | module configuration |
| `FILENAME_ARCH_COMPONENTS_HTML` | module configuration |
| `FILENAME_ARCH_VALIDATION_MD` | module configuration |
| `FOLDER_KEY_DOCS` | module configuration |
| `FOLDER_KEY_REPO_DOC_ROOT` | module configuration |
| `FOLDER_KEY_SYSTEM_DOC_ROOT` | module configuration |
| `FOLDER_KEY_SYSTEM_TEMPLATE_ROOT` | module configuration |
| `FOLDER_KEY_SYSTEM_DELIVERY_TEMPLATE_ROOT` | module configuration |
| `FOLDER_KEY_SYSTEM_CODEBASE_TEMPLATE_ROOT` | module configuration |
| `FOLDER_KEY_CODEBASE_DOC_ROOT` | module configuration |
| `FOLDER_KEY_DELIVERY_DOC_ROOT` | module configuration |
| `FOLDER_KEY_AUDIENCE_DOC_ROOT` | module configuration |
| `FOLDER_KEY_DOCS_SITE_ROOT` | module configuration |
| `FOLDER_KEY_ARCHITECTURE_SITE_ROOT` | module configuration |
| `FOLDER_KEY_STAKEHOLDER_SITE_ROOT` | module configuration |
| `FOLDER_KEY_DEVELOPER_SITE_ROOT` | module configuration |
| `FOLDER_KEY_OPERATOR_SITE_ROOT` | module configuration |
| `FOLDER_KEY_TESTER_SITE_ROOT` | module configuration |
| `FOLDER_KEY_USER_SITE_ROOT` | module configuration |
| `FOLDER_KEY_LEGACY_CODEBASE_DOC_ROOT` | module configuration |
| `FOLDER_KEY_LEGACY_DELIVERY_DOC_ROOT` | module configuration |
| `FOLDER_KEY_LEGACY_DOCS_SITE_ROOT` | module configuration |
| `FOLDER_KEY_SYSTEM_BOOTSTRAP` | module configuration |
| `FOLDER_KEY_CODEBASE_ANALYSIS` | module configuration |
| `FOLDER_KEY_CODEBASE_STANDARDS` | module configuration |
| `FOLDER_KEY_CODEBASE_INVENTORY` | module configuration |
| `FOLDER_KEY_CODEBASE_MODULES` | module configuration |
| `FOLDER_KEY_CODEBASE_COMPONENTS` | module configuration |
| `FOLDER_KEY_CODEBASE_CHANGES` | module configuration |
| `FOLDER_KEY_REPO_GOVERNANCE` | module configuration |
| `FOLDER_KEY_DELIVERY_STANDARDS` | module configuration |
| `FOLDER_KEY_DELIVERY_INITIATIVES` | module configuration |
| `FOLDER_KEY_DELIVERY_PLANS` | module configuration |
| `FOLDER_KEY_DELIVERY_TASKS` | module configuration |
| `FOLDER_KEY_DELIVERY_IMPLEMENTATIONS` | module configuration |
| `FOLDER_KEY_DELIVERY_REVIEWS` | module configuration |
| `FOLDER_KEY_DELIVERY_VALIDATIONS` | module configuration |
| `FOLDER_KEY_DELIVERY_MEMORY` | module configuration |
| `FOLDER_KEY_DELIVERY_AGENTS` | module configuration |
| `FOLDER_KEY_DELIVERY_TEMPLATES` | module configuration |
| `FOLDER_KEY_CODEBASE_TEMPLATES` | module configuration |
| `FOLDER_KEY_SDLC_DOC_ROOT` | module configuration |
| `FOLDER_KEY_SDLC_GOVERNANCE` | module configuration |
| `FOLDER_KEY_SDLC_REQUIREMENTS` | module configuration |
| `FOLDER_KEY_SDLC_PLANNING` | module configuration |
| `FOLDER_KEY_SDLC_BACKLOG` | module configuration |
| `FOLDER_KEY_SDLC_TASKS` | module configuration |
| `FOLDER_KEY_SDLC_IMPLEMENTATION` | module configuration |
| `FOLDER_KEY_SDLC_REVIEW` | module configuration |
| `FOLDER_KEY_SDLC_EXECUTION` | module configuration |
| `FOLDER_KEY_SDLC_VALIDATION` | module configuration |
| `FOLDER_KEY_SDLC_MEMORY` | module configuration |
| `FOLDER_KEY_SDLC_ARCHIVE` | module configuration |
| `FOLDER_KEY_GLOBAL_BUNDLES` | module configuration |
| `FOLDER_KEY_GLOBAL_FOUNDATION` | module configuration |
| `FOLDER_KEY_GLOBAL_PLATFORM` | module configuration |
| `FOLDER_KEY_DOCS_SITE` | module configuration |
| `FOLDER_KEY_STAKEHOLDER_SITE` | module configuration |
| `FOLDER_KEY_DEVELOPER_SITE` | module configuration |
| `FOLDER_KEY_OPERATOR_SITE` | module configuration |
| `FOLDER_KEY_TESTER_SITE` | module configuration |
| `FOLDER_KEY_USER_SITE` | module configuration |


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
