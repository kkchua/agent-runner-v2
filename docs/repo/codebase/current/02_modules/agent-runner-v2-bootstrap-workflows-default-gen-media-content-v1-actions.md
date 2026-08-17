---
title: "Module Documentation: agent_runner_v2.bootstrap.workflows.default.gen_media_content_v1.actions"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/actions.py"
module_area: "bootstrap"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-actions.md"
last_verified_by_change: "sdlc_00_codebase_scaffold_v1 / SDLC00CS-1zcrrbbs / 2026-08-17T21:19:17+08:00"
created: "2026-08-17T21:19:17+08:00"
owner: "sdlc_00_codebase_scaffold_v1"
---

# Module Documentation: agent_runner_v2.bootstrap.workflows.default.gen_media_content_v1.actions

## 1. Module Overview

### 1.1 Purpose

Shared actions and utilities for gen_media_content_v1 workflow.

### 1.2 Responsibility

This module belongs to the `bootstrap` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `importlib` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `logging` | stdlib module | imported dependency |
| `os` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `time` | stdlib module | imported dependency |
| `agent_runner_v2.action_result` | internal module | repository dependency |
| `agent_runner_v2.actions.preset_config` | internal module | repository dependency |
| `agent_runner_v2.api_key_pool` | internal module | repository dependency |
| `agent_runner_v2.workflow_packages.actions` | internal module | repository dependency |
| `requests` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### import_provider()

**Signature**: `import_provider(provider_type, provider_name)`

**Purpose**: Dynamically import a provider module from the api_actions directory.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `provider_type` | -- | -- | -- |
| `provider_name` | -- | -- | -- |

---

#### generate_images_default()

**Decorators**: `@action`

**Signature**: `generate_images_default(*, context, state, step_cfg, project_root)`

**Purpose**: Default orchestrator for image generation.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | -- | -- | -- |
| `state` | -- | -- | -- |
| `step_cfg` | -- | -- | -- |
| `project_root` | -- | -- | -- |

**Returns**: `ActionResult`

---

#### generate_videos_default()

**Decorators**: `@action`

**Signature**: `generate_videos_default(*, context, state, step_cfg, project_root)`

**Purpose**: Default orchestrator for video generation.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | -- | -- | -- |
| `state` | -- | -- | -- |
| `step_cfg` | -- | -- | -- |
| `project_root` | -- | -- | -- |

**Returns**: `ActionResult`

---


### 2.3 Constants / Configuration

| Name | Purpose |
|------|--------|
| `_PROVIDER_KEY_PREFIX_MAP` | module configuration |
| `_PROVIDER_BASE_URL_MAP` | module configuration |


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
