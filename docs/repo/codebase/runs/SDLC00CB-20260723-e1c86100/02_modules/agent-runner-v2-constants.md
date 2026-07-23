---
title: "Module Documentation: agent_runner_v2.constants"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/constants.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-constants.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-20260723-e1c86100 / 2026-07-23T21:41:19+08:00"
created: "2026-07-23T21:41:19+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.constants

## 1. Module Overview

### 1.1 Purpose

Centralized artifact path constants and path generation for agent-runner-v2.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### artifact_path()

**Signature**: `artifact_path(artifact_key: str, folder_key: str, extension: str = EXT_MD)`

**Purpose**: Construct artifact path by combining folder base with artifact key and extension.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `artifact_key` | `str` | -- | Artifact identifier (e.g., ARTIFACT_KEY_PROJECT_ANALYSIS) |
| `folder_key` | `str` | -- | Base directory path (e.g., FOLDER_KEY_SYSTEM_BOOTSTRAP) |
| `extension` | `str` | `EXT_MD` | File extension (default: EXT_MD) |

**Returns**: `str`

---

#### placeholder()

**Signature**: `placeholder(key: str)`

**Purpose**: Convert an artifact key to a prompt placeholder.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `key` | `str` | -- | Artifact key (e.g., ARTIFACT_KEY_PROJECT_ANALYSIS) |

**Returns**: `str`

---

#### relpath()

**Signature**: `relpath(*parts: str)`

**Purpose**: Join path fragments into a repository-relative POSIX path.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### file_in_folder()

**Signature**: `file_in_folder(folder_key: str, filename: str)`

**Purpose**: Build a repository-relative path for a literal filename in a known folder.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `folder_key` | `str` | -- | -- |
| `filename` | `str` | -- | -- |

**Returns**: `str`

---

#### artifact_meta_path()

**Signature**: `artifact_meta_path(artifact_rel: str)`

**Purpose**: Return the sidecar path for an artifact path.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `artifact_rel` | `str` | -- | -- |

**Returns**: `str`

---

#### get_master_docs_output_paths()

**Signature**: `get_master_docs_output_paths(job_id: str = '{job_id}', mode: str = '{mode}')`

**Purpose**: Generate output path mappings for master bootstrap workflow.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `job_id` | `str` | `'{job_id}'` | Job identifier (can contain {job_id} placeholder for template) |
| `mode` | `str` | `'{mode}'` | Workflow mode (can contain {mode} placeholder for template) |

**Returns**: `dict[str, str]`

---

#### system_doc_rel()

**Signature**: `system_doc_rel(*parts: str)`

**Purpose**: Get path relative to SYSTEM_DOC_ROOT.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### codebase_doc_rel()

**Signature**: `codebase_doc_rel(*parts: str)`

**Purpose**: Get path relative to CODEBASE_DOC_ROOT.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### repo_governance_rel()

**Signature**: `repo_governance_rel(*parts: str)`

**Purpose**: Get path relative to REPO_GOVERNANCE (Layer 2 repo master docs).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### delivery_doc_rel()

**Signature**: `delivery_doc_rel(*parts: str)`

**Purpose**: Get path relative to DELIVERY_DOC_ROOT.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### system_delivery_template_rel()

**Signature**: `system_delivery_template_rel(*parts: str)`

**Purpose**: Get path relative to SYSTEM_DELIVERY_TEMPLATE_ROOT.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### system_codebase_template_rel()

**Signature**: `system_codebase_template_rel(*parts: str)`

**Purpose**: Get path relative to SYSTEM_CODEBASE_TEMPLATE_ROOT.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### legacy_codebase_doc_rel()

**Signature**: `legacy_codebase_doc_rel(*parts: str)`

**Purpose**: Get path relative to the legacy CODEBASE_DOC_ROOT.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### legacy_delivery_doc_rel()

**Signature**: `legacy_delivery_doc_rel(*parts: str)`

**Purpose**: Get path relative to the legacy DELIVERY_DOC_ROOT.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### repo_doc_rel()

**Signature**: `repo_doc_rel(*parts: str)`

**Purpose**: Get path relative to DOCS_ROOT (docs/ folder).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### docs_root_rel()

**Signature**: `docs_root_rel(*parts: str)`

**Purpose**: Get path relative to DOCS_ROOT (docs/ folder) - alias for repo_doc_rel.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### system_template_rel()

**Signature**: `system_template_rel(*parts: str)`

**Purpose**: Get path relative to SYSTEM_TEMPLATE_ROOT.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### delivery_scaffold_docs()

**Signature**: `delivery_scaffold_docs()`

**Purpose**: Get all delivery scaffold documentation paths using centralized constants.

**Returns**: `dict[str, str]`

---

#### known_artifact_paths()

**Signature**: `known_artifact_paths()`

**Purpose**: Map artifact keys to their known repository-relative paths.

**Returns**: `dict[str, str]`

---

#### all_artifact_keys()

**Signature**: `all_artifact_keys()`

**Purpose**: Return all canonical artifact key literals declared in this module.

**Returns**: `list[str]`

---

#### legacy_artifact_paths()

**Signature**: `legacy_artifact_paths()`

**Purpose**: Map artifact keys to legacy repository-relative paths.

**Returns**: `dict[str, list[str]]`

---

#### prompt_literal_substitutions()

**Signature**: `prompt_literal_substitutions()`

**Purpose**: Map known literal file paths to canonical prompt placeholders.

**Returns**: `dict[str, str]`

---

#### register_artifact_paths()

**Signature**: `register_artifact_paths(paths: dict[str, str])`

**Purpose**: Merge workflow-contributed paths into the global registry.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `paths` | `dict[str, str]` | -- | Dict mapping artifact key strings to repo-relative |

**Returns**: `None`

---

#### get_artifact_path()

**Signature**: `get_artifact_path(key: str, default: str = '')`

**Purpose**: Look up an artifact path from the global registry.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `key` | `str` | -- | Artifact key (e.g. ``"INIT_FILE"``). |
| `default` | `str` | `''` | Value to return when the key is not registered. |

**Returns**: `str`

---

#### resolve_next_seq()

**Signature**: `resolve_next_seq(directory: Path, prefix: str)`

**Purpose**: Scan *directory* for ``.md`` files starting with *prefix*.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `directory` | `Path` | -- | Target directory to scan. |
| `prefix` | `str` | -- | Filename prefix including the date (e.g. ``"BACKLOG-20260723-"``). |

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
| `ARTIFACT_KEY_DRAFT_INIT` | module configuration |
| `ARTIFACT_KEY_PRE_INIT` | module configuration |
| `ARTIFACT_KEY_INIT` | module configuration |
| `ARTIFACT_KEY_PLAN` | module configuration |
| `ARTIFACT_KEY_TASK_GRAPH` | module configuration |
| `ARTIFACT_KEY_TASK` | module configuration |
| `ARTIFACT_KEY_IMPL` | module configuration |
| `ARTIFACT_KEY_REVIEW` | module configuration |
| `ARTIFACT_KEY_AUDIT` | module configuration |
| `ARTIFACT_KEY_VALIDATION` | module configuration |
| `ARTIFACT_KEY_CONTEXT_PACK` | module configuration |
| `ARTIFACT_KEY_PROJECT_CONTEXT` | module configuration |
| `ARTIFACT_KEY_PROJECT_ANALYSIS` | module configuration |
| `ARTIFACT_KEY_DELIVERY_SOP` | module configuration |
| `ARTIFACT_KEY_DELIVERY_STATUS_RULES` | module configuration |
| `ARTIFACT_KEY_DELIVERY_TEMPLATE_REGISTRY` | module configuration |
| `ARTIFACT_KEY_DELIVERY_INITIATIVE_TEMPLATE` | module configuration |
| `ARTIFACT_KEY_DELIVERY_PLAN_TEMPLATE` | module configuration |
| `ARTIFACT_KEY_DELIVERY_TASK_GRAPH_TEMPLATE` | module configuration |
| `ARTIFACT_KEY_DELIVERY_TASK_TEMPLATE` | module configuration |
| `ARTIFACT_KEY_DELIVERY_IMPL_TEMPLATE` | module configuration |
| `ARTIFACT_KEY_DELIVERY_REVIEW_TEMPLATE` | module configuration |
| `ARTIFACT_KEY_DELIVERY_VALIDATION_TEMPLATE` | module configuration |
| `ARTIFACT_KEY_DELIVERY_MEMORY_TEMPLATE` | module configuration |
| `ARTIFACT_KEY_DELIVERY_AGENTS` | module configuration |
| `ARTIFACT_KEY_DELIVERY_AGENT_PLANNER` | module configuration |
| `ARTIFACT_KEY_DELIVERY_AGENT_TASK_DECOMPOSER` | module configuration |
| `ARTIFACT_KEY_DELIVERY_AGENT_IMPL_PLANNER` | module configuration |
| `ARTIFACT_KEY_DELIVERY_AGENT_EXECUTOR` | module configuration |
| `ARTIFACT_KEY_DELIVERY_AGENT_REVIEWER` | module configuration |
| `ARTIFACT_KEY_DELIVERY_AGENT_MEMORY_MANAGER` | module configuration |
| `ARTIFACT_KEY_DOCUMENTATION_STANDARD` | module configuration |
| `ARTIFACT_KEY_WORKFLOW_SOP` | module configuration |
| `ARTIFACT_KEY_DELIVERY_FOLDER_MAP` | module configuration |
| `ARTIFACT_KEY_CODEBASE_DOC_SOP` | module configuration |
| `ARTIFACT_KEY_CODEBASE_DOC_STATUS_RULES` | module configuration |
| `ARTIFACT_KEY_EXISTING_REPO_WORKFLOW_SOP` | module configuration |
| `ARTIFACT_KEY_CODEBASE_TEMPLATE_REGISTRY` | module configuration |
| `ARTIFACT_KEY_CODEBASE_INVENTORY_TEMPLATE` | module configuration |
| `ARTIFACT_KEY_CODEBASE_MODULE_TEMPLATE` | module configuration |
| `ARTIFACT_KEY_CODEBASE_COMPONENT_TEMPLATE` | module configuration |
| `ARTIFACT_KEY_CODEBASE_CHANGE_TEMPLATE` | module configuration |
| `ARTIFACT_KEY_CODEBASE_INVENTORY` | module configuration |
| `ARTIFACT_KEY_CODEBASE_CHANGE_IMPACT` | module configuration |
| `ARTIFACT_KEY_CODEBASE_SCAN_SNAPSHOT` | module configuration |
| `ARTIFACT_KEY_INTEGRATION_MAP` | module configuration |
| `ARTIFACT_KEY_FAILURE_MODES` | module configuration |
| `ARTIFACT_KEY_ARCHITECTURE_FLOW` | module configuration |
| `ARTIFACT_KEY_DELIVERY_FOLDER_MAP` | module configuration |
| `ARTIFACT_KEY_README` | module configuration |
| `ARTIFACT_KEY_SYSTEM_DOCS_INDEX` | module configuration |
| `ARTIFACT_KEY_SYSTEM_DOCS_CHANGE_LOG` | module configuration |
| `ARTIFACT_KEY_SYSTEM_DOCS_VALIDATION` | module configuration |
| `ARTIFACT_KEY_SYSTEM_DOC_STANDARD` | module configuration |
| `ARTIFACT_KEY_BUNDLE_TAXONOMY` | module configuration |
| `ARTIFACT_KEY_RUNTIME_GOVERNANCE` | module configuration |
| `ARTIFACT_KEY_BUNDLE_MIGRATION_PLAN` | module configuration |
| `ARTIFACT_KEY_SYSTEM_OVERVIEW` | module configuration |
| `ARTIFACT_KEY_BUSINESS_CAPABILITIES` | module configuration |
| `ARTIFACT_KEY_FUNCTIONAL_SPEC` | module configuration |
| `ARTIFACT_KEY_NON_FUNCTIONAL_REQUIREMENTS` | module configuration |
| `ARTIFACT_KEY_SYSTEM_CONTEXT` | module configuration |
| `ARTIFACT_KEY_COMPONENT_ARCHITECTURE` | module configuration |
| `ARTIFACT_KEY_DECISION_LOG` | module configuration |
| `ARTIFACT_KEY_SYSTEM_FILE_STRUCTURE` | module configuration |
| `ARTIFACT_KEY_DEVELOPER_GUIDE` | module configuration |
| `ARTIFACT_KEY_RUNBOOK` | module configuration |
| `ARTIFACT_KEY_BOOTSTRAP_SUMMARY` | module configuration |
| `ARTIFACT_KEY_CODEBASE_SCAN_SNAPSHOT` | module configuration |
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
| `FOLDER_KEY_DELIVERY_DOC_ROOT` | module configuration |
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
| `FOLDER_KEY_GLOBAL_BUNDLES` | module configuration |
| `FOLDER_KEY_GLOBAL_FOUNDATION` | module configuration |
| `FOLDER_KEY_GLOBAL_PLATFORM` | module configuration |
| `ARTIFACT_PATH_PROJECT_ANALYSIS` | module configuration |
| `ARTIFACT_PATH_README` | module configuration |
| `ARTIFACT_PATH_DOCUMENTATION_STANDARD` | module configuration |
| `ARTIFACT_PATH_BUNDLE_TAXONOMY` | module configuration |
| `ARTIFACT_PATH_RUNTIME_GOVERNANCE` | module configuration |
| `ARTIFACT_PATH_BUNDLE_MIGRATION_PLAN` | module configuration |
| `ARTIFACT_PATH_SYSTEM_OVERVIEW` | module configuration |
| `ARTIFACT_PATH_BUSINESS_CAPABILITIES` | module configuration |
| `ARTIFACT_PATH_FUNCTIONAL_SPEC` | module configuration |
| `ARTIFACT_PATH_NON_FUNCTIONAL_REQUIREMENTS` | module configuration |
| `ARTIFACT_PATH_SYSTEM_CONTEXT` | module configuration |
| `ARTIFACT_PATH_COMPONENT_ARCHITECTURE` | module configuration |
| `ARTIFACT_PATH_DECISION_LOG` | module configuration |
| `ARTIFACT_PATH_SYSTEM_FILE_STRUCTURE` | module configuration |
| `ARTIFACT_PATH_DEVELOPER_GUIDE` | module configuration |
| `ARTIFACT_PATH_RUNBOOK` | module configuration |
| `ARTIFACT_PATH_EXISTING_REPO_WORKFLOW_SOP` | module configuration |
| `ARTIFACT_PATH_DELIVERY_STATUS_RULES` | module configuration |
| `ARTIFACT_PATH_WORKFLOW_SOP` | module configuration |
| `ARTIFACT_PATH_CODEBASE_INVENTORY` | module configuration |
| `ARTIFACT_PATH_INTEGRATION_MAP` | module configuration |
| `ARTIFACT_PATH_FAILURE_MODES` | module configuration |
| `ARTIFACT_PATH_ARCHITECTURE_FLOW` | module configuration |
| `ARTIFACT_PATH_CODEBASE_DOC_SOP` | module configuration |
| `ARTIFACT_PATH_CODEBASE_DOC_STATUS_RULES` | module configuration |
| `ARTIFACT_PATH_DELIVERY_AGENTS` | module configuration |
| `ARTIFACT_PATH_DELIVERY_AGENT_PLANNER` | module configuration |
| `ARTIFACT_PATH_DELIVERY_AGENT_TASK_DECOMPOSER` | module configuration |
| `ARTIFACT_PATH_DELIVERY_AGENT_IMPL_PLANNER` | module configuration |
| `ARTIFACT_PATH_DELIVERY_AGENT_EXECUTOR` | module configuration |
| `ARTIFACT_PATH_DELIVERY_AGENT_REVIEWER` | module configuration |
| `ARTIFACT_PATH_DELIVERY_AGENT_MEMORY_MANAGER` | module configuration |
| `ARTIFACT_PATH_DELIVERY_FOLDER_MAP` | module configuration |
| `ARTIFACT_PATH_DELIVERY_TEMPLATE_REGISTRY` | module configuration |
| `ARTIFACT_PATH_DELIVERY_INITIATIVE_TEMPLATE` | module configuration |
| `ARTIFACT_PATH_DELIVERY_PLAN_TEMPLATE` | module configuration |
| `ARTIFACT_PATH_DELIVERY_TASK_GRAPH_TEMPLATE` | module configuration |
| `ARTIFACT_PATH_DELIVERY_TASK_TEMPLATE` | module configuration |
| `ARTIFACT_PATH_DELIVERY_IMPL_TEMPLATE` | module configuration |
| `ARTIFACT_PATH_DELIVERY_REVIEW_TEMPLATE` | module configuration |
| `ARTIFACT_PATH_DELIVERY_VALIDATION_TEMPLATE` | module configuration |
| `ARTIFACT_PATH_DELIVERY_MEMORY_TEMPLATE` | module configuration |
| `ARTIFACT_PATH_CODEBASE_TEMPLATE_REGISTRY` | module configuration |
| `ARTIFACT_PATH_CODEBASE_INVENTORY_TEMPLATE` | module configuration |
| `ARTIFACT_PATH_CODEBASE_MODULE_TEMPLATE` | module configuration |
| `ARTIFACT_PATH_CODEBASE_COMPONENT_TEMPLATE` | module configuration |
| `ARTIFACT_PATH_CODEBASE_CHANGE_TEMPLATE` | module configuration |
| `DELIVERY_SCAFFOLD_DIRS` | module configuration |
| `RUN_AGENT_REQUIRED_DOC_DIRS` | module configuration |
| `REFERENCE_FILES` | module configuration |
| `FOLDER_ROOT_CONSTANTS` | module configuration |
| `SIDECAR_INSTRUCTION_TEMPLATE` | module configuration |
| `ASCII_ONLY_INSTRUCTION` | module configuration |
| `SECTION_HEADING_RULE` | module configuration |
| `GOVERNANCE_PATH_REFERENCE_RULE` | module configuration |
| `CODER_SOP_INSTRUCTION_TEMPLATE` | module configuration |
| `TOOL_INSTRUCTION_TEMPLATE` | module configuration |
| `DELIVERY_SOP_REQUIRED_SECTIONS` | module configuration |
| `DELIVERY_STATUS_RULES_REQUIRED_SECTIONS` | module configuration |
| `CODEBASE_SOP_REQUIRED_SECTIONS` | module configuration |
| `CODEBASE_STATUS_RULES_REQUIRED_SECTIONS` | module configuration |
| `SDLC_DELIVERY_BASE` | module configuration |


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
