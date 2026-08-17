---
title: "Module Documentation: agent_runner_v2.bootstrap.workflows.default.gen_media_content_v1.tests.test_context"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/tests/test_context.py"
module_area: "bootstrap"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-tests-test-context.md"
last_verified_by_change: "sdlc_00_codebase_scaffold_v1 / SDLC00CS-1zcrrbbs / 2026-08-17T21:19:17+08:00"
created: "2026-08-17T21:19:17+08:00"
owner: "sdlc_00_codebase_scaffold_v1"
---

# Module Documentation: agent_runner_v2.bootstrap.workflows.default.gen_media_content_v1.tests.test_context

## 1. Module Overview

### 1.1 Purpose

Unit tests for gen_media_content_v1 context extensions.

### 1.2 Responsibility

This module belongs to the `bootstrap` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `importlib.util` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `unittest.mock` | stdlib module | imported dependency |
| `pytest` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

#### TestContextExtensionKeys

**Purpose**: Verify all expected context keys are produced.

**Methods**:

- `test_step_dir_keys_present(mock_get_ws, mock_get_platform, mock_get_gov)` -- All 5 STEP_*_DIR keys are present in the context.
- `test_media_config_key_present(mock_get_ws, mock_get_platform, mock_get_gov)` -- MEDIA_CONFIG key is present in the context.

#### TestContextExtensionPaths

**Purpose**: Verify paths are constructed correctly from workspace_root.

**Methods**:

- `test_step_dirs_use_workspace_root(mock_get_ws, mock_get_platform, mock_get_gov)` -- Step directory paths are absolute and rooted at workspace_root.
- `test_media_config_path(mock_get_ws, mock_get_platform, mock_get_gov)` -- MEDIA_CONFIG points to config.json in workspace_root.
- `test_archive_dirs_present(mock_get_ws, mock_get_platform, mock_get_gov)` -- Archive directory keys are also present for completeness.
- `test_governance_and_platform_roots(mock_get_ws, mock_get_platform, mock_get_gov)` -- Governance and platform runtime roots are injected.

#### TestArtifactKeyRegistration

**Purpose**: Verify register_artifact_keys produces expected mappings.

**Methods**:

- `test_artifact_keys_registered(mock_get_ws)` -- All 4 index.json artifact keys are registered.


### 2.2 Functions

No public functions.


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
| 2026-08-17 | Initial baseline generated from repository scan | sdlc_00_codebase_scaffold_v1 |
