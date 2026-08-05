---
title: "Module Documentation: agent_runner_v2.constants_legacy_backup_20260717"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/constants_legacy_backup_20260717.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-constants-legacy-backup-20260717.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-20260723-e1c86100 / 2026-07-23T21:41:19+08:00"
created: "2026-07-23T21:41:19+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.constants_legacy_backup_20260717

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

#### docs_site_rel()

**Signature**: `docs_site_rel(*parts: str)`

**Purpose**: Get path relative to DOCS_SITE_ROOT.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### stakeholder_site_rel()

**Signature**: `stakeholder_site_rel(*parts: str)`

**Purpose**: Get path relative to STAKEHOLDER_SITE_ROOT.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### developer_site_rel()

**Signature**: `developer_site_rel(*parts: str)`

**Purpose**: Get path relative to DEVELOPER_SITE_ROOT.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### operator_site_rel()

**Signature**: `operator_site_rel(*parts: str)`

**Purpose**: Get path relative to OPERATOR_SITE_ROOT.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### tester_site_rel()

**Signature**: `tester_site_rel(*parts: str)`

**Purpose**: Get path relative to TESTER_SITE_ROOT.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `*parts` | `str` | -- | -- |

**Returns**: `str`

---

#### user_site_rel()

**Signature**: `user_site_rel(*parts: str)`

**Purpose**: Get path relative to USER_SITE_ROOT.

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

#### legacy_docs_site_rel()

**Signature**: `legacy_docs_site_rel(*parts: str)`

**Purpose**: Get path relative to the legacy site root.

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

#### architecture_site_rel()

**Signature**: `architecture_site_rel(*parts: str)`

**Purpose**: Get path relative to ARCHITECTURE_SITE_ROOT (legacy alias for DOCS_SITE_ROOT).

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

#### audience_site_artifacts()

**Signature**: `audience_site_artifacts()`

**Purpose**: Map artifact keys to their paths for all audience sites.

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

#### architecture_site_pages()

**Signature**: `architecture_site_pages()`

**Purpose**: Master index site pages (50_architecture_site_v1).

**Returns**: `dict[str, str]`

---

#### stakeholder_site_pages()

**Signature**: `stakeholder_site_pages()`

**Purpose**: Stakeholder documentation site pages (51_stakeholder_docs_v1).

**Returns**: `dict[str, str]`

---

#### developer_site_pages()

**Signature**: `developer_site_pages()`

**Purpose**: Developer documentation site pages (52_developer_docs_v1).

**Returns**: `dict[str, str]`

---

#### operator_site_pages()

**Signature**: `operator_site_pages()`

**Purpose**: Operator documentation site pages (53_operator_docs_v1).

**Returns**: `dict[str, str]`

---

#### tester_site_pages()

**Signature**: `tester_site_pages()`

**Purpose**: Tester documentation site pages (54_tester_docs_v1).

**Returns**: `dict[str, str]`

---

#### user_site_pages()

**Signature**: `user_site_pages()`

**Purpose**: User documentation site pages (55_user_docs_v1).

**Returns**: `dict[str, str]`

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
| `ARTIFACT_KEY_DRAFT_INIT` | module configuration |
| `ARTIFACT_KEY_PRE_INIT` | module configuration |
| `ARTIFACT_KEY_INIT` | module configuration |
| `ARTIFACT_KEY_PLAN` | module configuration |
| `ARTIFACT_KEY_TASK_GRAPH` | module configuration |
| `ARTIFACT_KEY_TASK` | module configuration |
| `ARTIFACT_KEY_IMPL` | module configuration |
| `ARTIFACT_KEY_REVIEW` | module configuration |
| `ARTIFACT_KEY_VALIDATION` | module configuration |
| `ARTIFACT_KEY_CONTEXT_PACK` | module configuration |
| `ARTIFACT_KEY_IMAGE` | module configuration |
| `ARTIFACT_KEY_IMAGE_FOLDER` | module configuration |
| `ARTIFACT_KEY_IMAGE_DESC_FOLDER` | module configuration |
| `ARTIFACT_KEY_IMAGE_CSV_JSON` | module configuration |
| `ARTIFACT_KEY_IMAGE_CSV_CSV` | module configuration |
| `ARTIFACT_KEY_IMAGE_CSV_SUBMIT_RESULT` | module configuration |
| `ARTIFACT_KEY_NARRATIVE` | module configuration |
| `ARTIFACT_KEY_VIDEOWORKFLOW` | module configuration |
| `ARTIFACT_KEY_GENERATED_IMAGES` | module configuration |
| `ARTIFACT_KEY_GENERATED_VIDEO_CLIPS` | module configuration |
| `ARTIFACT_KEY_GENERATED_AUDIO` | module configuration |
| `ARTIFACT_KEY_FINAL_VIDEO` | module configuration |
| `ARTIFACT_KEY_USER_INPUT` | module configuration |
| `ARTIFACT_KEY_BRIEF_JSON` | module configuration |
| `ARTIFACT_KEY_WORKFLOW_JSON` | module configuration |
| `ARTIFACT_KEY_IMAGE_SUBMIT_RESULT` | module configuration |
| `ARTIFACT_KEY_VIDEO_SUBMIT_RESULT` | module configuration |
| `ARTIFACT_KEY_AUDIO_SUBMIT_RESULT` | module configuration |
| `ARTIFACT_KEY_FINAL_VIDEO_TIKTOK` | module configuration |
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
| `ARTIFACT_KEY_BUG_DRAFT` | module configuration |
| `ARTIFACT_KEY_BUG_REPORT` | module configuration |
| `ARTIFACT_KEY_REPRO` | module configuration |
| `ARTIFACT_KEY_ROOT_CAUSE` | module configuration |
| `ARTIFACT_KEY_PATCH` | module configuration |
| `ARTIFACT_KEY_ARCHITECTURE_SITE_INDEX` | module configuration |
| `ARTIFACT_KEY_ARCHITECTURE_SITE_MANIFEST` | module configuration |
| `ARTIFACT_KEY_STAKEHOLDER_SITE_MARKDOWN` | module configuration |
| `ARTIFACT_KEY_DEVELOPER_SITE_MARKDOWN` | module configuration |
| `ARTIFACT_KEY_OPERATOR_SITE_MARKDOWN` | module configuration |
| `ARTIFACT_KEY_TESTER_SITE_MARKDOWN` | module configuration |
| `ARTIFACT_KEY_USER_SITE_MARKDOWN` | module configuration |
| `ARTIFACT_KEY_STAKEHOLDER_SITE_INDEX` | module configuration |
| `ARTIFACT_KEY_DEVELOPER_SITE_INDEX` | module configuration |
| `ARTIFACT_KEY_OPERATOR_SITE_INDEX` | module configuration |
| `ARTIFACT_KEY_TESTER_SITE_INDEX` | module configuration |
| `ARTIFACT_KEY_USER_SITE_INDEX` | module configuration |
| `ARTIFACT_KEY_STAKEHOLDER_SITE_PDF` | module configuration |
| `ARTIFACT_KEY_DEVELOPER_SITE_PDF` | module configuration |
| `ARTIFACT_KEY_OPERATOR_SITE_PDF` | module configuration |
| `ARTIFACT_KEY_TESTER_SITE_PDF` | module configuration |
| `ARTIFACT_KEY_USER_SITE_PDF` | module configuration |
| `ARTIFACT_KEY_STAKEHOLDER_SITE_MANIFEST` | module configuration |
| `ARTIFACT_KEY_DEVELOPER_SITE_MANIFEST` | module configuration |
| `ARTIFACT_KEY_OPERATOR_SITE_MANIFEST` | module configuration |
| `ARTIFACT_KEY_TESTER_SITE_MANIFEST` | module configuration |
| `ARTIFACT_KEY_USER_SITE_MANIFEST` | module configuration |
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
| `FOLDER_KEY_DOCS_SITE` | module configuration |
| `FOLDER_KEY_STAKEHOLDER_SITE` | module configuration |
| `FOLDER_KEY_DEVELOPER_SITE` | module configuration |
| `FOLDER_KEY_OPERATOR_SITE` | module configuration |
| `FOLDER_KEY_TESTER_SITE` | module configuration |
| `FOLDER_KEY_USER_SITE` | module configuration |
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
| `ARTIFACT_PATH_ARCHITECTURE_SITE_INDEX` | module configuration |
| `ARTIFACT_PATH_STAKEHOLDER_SITE_INDEX` | module configuration |
| `ARTIFACT_PATH_DEVELOPER_SITE_INDEX` | module configuration |
| `ARTIFACT_PATH_OPERATOR_SITE_INDEX` | module configuration |
| `ARTIFACT_PATH_TESTER_SITE_INDEX` | module configuration |
| `ARTIFACT_PATH_USER_SITE_INDEX` | module configuration |
| `ARTIFACT_PATH_STAKEHOLDER_SITE_MARKDOWN` | module configuration |
| `ARTIFACT_PATH_DEVELOPER_SITE_MARKDOWN` | module configuration |
| `ARTIFACT_PATH_OPERATOR_SITE_MARKDOWN` | module configuration |
| `ARTIFACT_PATH_TESTER_SITE_MARKDOWN` | module configuration |
| `ARTIFACT_PATH_USER_SITE_MARKDOWN` | module configuration |
| `DELIVERY_SCAFFOLD_DIRS` | module configuration |
| `RUN_AGENT_REQUIRED_DOC_DIRS` | module configuration |
| `REFERENCE_FILES` | module configuration |
| `FOLDER_ROOT_CONSTANTS` | module configuration |
| `SIDECAR_INSTRUCTION_TEMPLATE` | module configuration |
| `TOOL_INSTRUCTION_TEMPLATE` | module configuration |
| `DELIVERY_SOP_REQUIRED_SECTIONS` | module configuration |
| `DELIVERY_STATUS_RULES_REQUIRED_SECTIONS` | module configuration |
| `CODEBASE_SOP_REQUIRED_SECTIONS` | module configuration |
| `CODEBASE_STATUS_RULES_REQUIRED_SECTIONS` | module configuration |


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
