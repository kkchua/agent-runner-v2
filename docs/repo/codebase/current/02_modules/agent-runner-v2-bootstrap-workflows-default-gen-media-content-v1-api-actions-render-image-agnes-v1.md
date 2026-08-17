---
title: "Module Documentation: agent_runner_v2.bootstrap.workflows.default.gen_media_content_v1.api_actions.render_image.agnes_v1"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/api_actions/render_image/agnes_v1.py"
module_area: "bootstrap"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-api-actions-render-image-agnes-v1.md"
last_verified_by_change: "sdlc_00_codebase_scaffold_v1 / SDLC00CS-1zcrrbbs / 2026-08-17T21:19:17+08:00"
created: "2026-08-17T21:19:17+08:00"
owner: "sdlc_00_codebase_scaffold_v1"
---

# Module Documentation: agent_runner_v2.bootstrap.workflows.default.gen_media_content_v1.api_actions.render_image.agnes_v1

## 1. Module Overview

### 1.1 Purpose

Agnes Image 2.1 Flash provider for render_image step.

### 1.2 Responsibility

This module belongs to the `bootstrap` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `logging` | stdlib module | imported dependency |
| `requests` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### call_api()

**Signature**: `call_api(prompt: str, config: dict, api_key: str, base_url: str)`

**Purpose**: Generate an image using Agnes Image 2.1 Flash API.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `prompt` | `str` | -- | -- |
| `config` | `dict` | -- | -- |
| `api_key` | `str` | -- | -- |
| `base_url` | `str` | -- | -- |

**Returns**: `dict`

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
| 2026-08-17 | Initial baseline generated from repository scan | sdlc_00_codebase_scaffold_v1 |
