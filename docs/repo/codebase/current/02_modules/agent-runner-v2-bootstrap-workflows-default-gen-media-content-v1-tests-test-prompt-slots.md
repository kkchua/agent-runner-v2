---
title: "Module Documentation: agent_runner_v2.bootstrap.workflows.default.gen_media_content_v1.tests.test_prompt_slots"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/tests/test_prompt_slots.py"
module_area: "bootstrap"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-tests-test-prompt-slots.md"
last_verified_by_change: "sdlc_00_codebase_scaffold_v1 / SDLC00CS-1zcrrbbs / 2026-08-17T21:19:17+08:00"
created: "2026-08-17T21:19:17+08:00"
owner: "sdlc_00_codebase_scaffold_v1"
---

# Module Documentation: agent_runner_v2.bootstrap.workflows.default.gen_media_content_v1.tests.test_prompt_slots

## 1. Module Overview

### 1.1 Purpose

Tests for gen_media_content_v1 LLM prompt slot placeholders.

### 1.2 Responsibility

This module belongs to the `bootstrap` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `re` | stdlib module | imported dependency |
| `pytest` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

#### TestExtractDescExists

**Purpose**: Public class

**Methods**:

- `test_file_exists()` -> `None` -- method
- `test_valid_utf8()` -> `None` -- method

#### TestGeneratePromptsExists

**Purpose**: Public class

**Methods**:

- `test_file_exists()` -> `None` -- method
- `test_valid_utf8()` -> `None` -- method

#### TestExtractDescStep00Dir

**Purpose**: Public class

**Methods**:

- `test_contains_step_00_dir(extract_desc_content: str)` -> `None` -- method

#### TestExtractDescStep01Dir

**Purpose**: Public class

**Methods**:

- `test_contains_step_01_dir(extract_desc_content: str)` -> `None` -- method

#### TestGeneratePromptsStepDirs

**Purpose**: Public class

**Methods**:

- `test_contains_step_01_dir(generate_prompts_content: str)` -> `None` -- method
- `test_contains_step_02_dir(generate_prompts_content: str)` -> `None` -- method

#### TestGeneratePromptsMediaConfig

**Purpose**: Public class

**Methods**:

- `test_contains_media_config(generate_prompts_content: str)` -> `None` -- method

#### TestNoHardcodedPaths

**Purpose**: Public class

**Methods**:

- `test_extract_desc_no_absolute_paths(extract_desc_content: str)` -> `None` -- method
- `test_generate_prompts_no_absolute_paths(generate_prompts_content: str)` -> `None` -- method

#### TestContentLength

**Purpose**: Public class

**Methods**:

- `test_extract_desc_meaningful_content(extract_desc_content: str)` -> `None` -- method
- `test_generate_prompts_meaningful_content(generate_prompts_content: str)` -> `None` -- method


### 2.2 Functions

#### extract_desc_content()

**Decorators**: `@pytest.fixture`

**Signature**: `extract_desc_content()`

**Purpose**: Read extract_desc prompt as UTF-8.

**Returns**: `str`

---

#### generate_prompts_content()

**Decorators**: `@pytest.fixture`

**Signature**: `generate_prompts_content()`

**Purpose**: Read generate_prompts prompt as UTF-8.

**Returns**: `str`

---


### 2.3 Constants / Configuration

| Name | Purpose |
|------|--------|
| `WORKFLOW_ROOT` | module configuration |
| `EXTRACT_DESC_PROMPT` | module configuration |
| `GENERATE_PROMPTS_PROMPT` | module configuration |
| `_ABS_PATH_PATTERN` | module configuration |


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
