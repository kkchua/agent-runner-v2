---
title: "Module Documentation: agent_runner_v2.bootstrap.workflows.default.agnes_media_gen_v1.actions"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/bootstrap/workflows/default/agnes_media_gen_v1/actions.py"
module_area: "bootstrap"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-agnes-media-gen-v1-actions.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-bgmxg5vi / 2026-08-06T07:04:04+08:00"
created: "2026-08-06T07:04:04+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.bootstrap.workflows.default.agnes_media_gen_v1.actions

## 1. Module Overview

### 1.1 Purpose

Custom actions for agnes_media_gen_v1 workflow.

### 1.2 Responsibility

This module belongs to the `bootstrap` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `dataclasses` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `logging` | stdlib module | imported dependency |
| `os` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `time` | stdlib module | imported dependency |
| `agent_runner_v2.action_result` | internal module | repository dependency |
| `agent_runner_v2.api_key_pool` | internal module | repository dependency |
| `agent_runner_v2.concurrent_api` | internal module | repository dependency |
| `agent_runner_v2.workflow_packages.actions` | internal module | repository dependency |
| `requests` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### generate_images()

**Decorators**: `@action`

**Signature**: `generate_images(*, context, state, step_cfg, project_root)`

**Purpose**: Generate images from prompt variants using Agnes Image 2.1 Flash API.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | -- | -- | Prompt context dictionary with resolved paths. |
| `state` | -- | -- | Workflow state dictionary with artifacts and job metadata. |
| `step_cfg` | -- | -- | Step configuration dictionary from workflow.toml. |
| `project_root` | -- | -- | Root path of the target repository. |

**Returns**: `ActionResult`

---

#### generate_videos()

**Decorators**: `@action`

**Signature**: `generate_videos(*, context, state, step_cfg, project_root)`

**Purpose**: Generate videos from images using Agnes Video V2.0 API.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | -- | -- | Prompt context dictionary with resolved paths. |
| `state` | -- | -- | Workflow state dictionary with artifacts and job metadata. |
| `step_cfg` | -- | -- | Step configuration dictionary from workflow.toml. |
| `project_root` | -- | -- | Root path of the target repository. |

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
| 2026-08-06 | Initial baseline generated from repository scan | sdlc_00_codebase_v1 |
