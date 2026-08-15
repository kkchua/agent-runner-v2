---
template_id: SYS-03-TK
version: "1.0.0"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved task specification for gen_media_content_v1 Phase 2 actions and utilities"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
---

# Task: gen_media_content_v1 Phase 2 - Root Actions and Shared Utilities

## Document Metadata

- Document ID: TASK-20260814-001-02
- Source backlog reference: WI-20260814-001 (gen_media_content_v1 workflow)
- Task IDs covered: WI-20260814-001-02
- Date of generation: 2026-08-15
- Producing workflow: Manual initiation
- Producing agent: default (Kai)
- Prior task: TASK-20260814-001-01 (Phase 1 scaffolding -- completed)

## Task Overview

Create the root `actions.py` module for the gen_media_content_v1 workflow package. This module provides shared utility functions used by all API providers and two orchestrator action stubs that will be wired to dynamic providers in Phase 9.

The actions.py module is the central coordination point for the workflow: it loads configuration, provides retry logic for API calls, writes index files, resolves sequence filenames, and dynamically imports API providers from the `api_actions/` directory.

Expected outcome: A valid Python module with 5 utility functions and 2 action stubs, all covered by unit tests that pass without real API keys.

## Detailed Implementation Steps

### Step 1: Create Shared Utility Functions

Create the following utility functions in `workflows/gen_media_content_v1/actions.py`:

#### 1a: _load_config(config_path)
- Load and parse the media configuration JSON file from the given path.
- Raise FileNotFoundError if the file does not exist.
- Return the parsed dict.

#### 1b: _api_request_with_retry(method, url, *, headers, json_payload=None, timeout=500, max_retries=5, retry_base_wait=5)
- Execute an HTTP request (GET or POST) with retry logic.
- Retry on HTTP 503, 429, and timeout errors.
- Use exponential backoff: wait = min(retry_base_wait * 2^attempt, 120).
- Raise RuntimeError after max retries exhausted.
- Return the response object on success.

#### 1c: _write_index(index_path, step_name, file_mappings)
- Write an index.json file listing input-to-output file mappings.
- Create parent directories if they do not exist.
- Structure: {"step": step_name, "files": file_mappings}

#### 1d: _get_next_sequence_filename(output_dir, base_name, ext)
- Find the next available filename with auto-incrementing sequence number.
- Return base_name.ext if it does not exist, otherwise base_name_001.ext, base_name_002.ext, etc.

#### 1e: import_provider(provider_type, provider_name)
- Dynamically import a provider module from the api_actions/ directory.
- provider_type is "render_image" or "render_video".
- provider_name is the subdirectory name (e.g., "agnes_v1", "happyhorse_v1_1").
- Return the imported module (which must export a call_api function).
- Raise ImportError if the module does not exist or has no call_api.

### Step 2: Create Orchestrator Action Stubs

Create two action stubs in the same actions.py:

#### 2a: @action("generate_images_default")
- Return ActionResult with status="REJECTED", reject_code="MISSING_PROVIDER", remark explaining no provider is configured.

#### 2b: @action("generate_videos_default")
- Return ActionResult with status="REJECTED", reject_code="MISSING_PROVIDER", remark explaining no provider is configured.

### Step 3: Create Unit Tests

Create `workflows/gen_media_content_v1/tests/test_actions.py` with tests for:

- _load_config: valid JSON parsing, missing file error
- _api_request_with_retry: successful request, retry on 503, retry on 429, max retries exhausted, timeout handling
- _write_index: correct JSON structure, parent directory creation
- _get_next_sequence_filename: first file (no sequence), second file (_001), third file (_002)
- import_provider: successful import, missing module error, module without call_api error
- generate_images_default: returns REJECTED with MISSING_PROVIDER
- generate_videos_default: returns REJECTED with MISSING_PROVIDER

All tests must use mocks for HTTP calls. No real API keys required.

## Technical Specifications

- All file paths are relative to agent-runner-v2 project root (D:\MyProjectSpace\01_Workflows\agent-runner-v2).
- Do NOT modify any existing workflow files. Only create/modify files under workflows/gen_media_content_v1/.
- Follow the same patterns as workflows/agnes_media_gen_v1/actions.py for utility functions.
- Use `from agent_runner_v2.workflow_packages.actions import action` for the @action decorator.
- Use `from agent_runner_v2.action_result import ActionResult` for action return types.
- All Python files must be valid and parseable (no syntax errors).

## Reference Files

| File | Purpose |
|---|---|
| workflows/agnes_media_gen_v1/actions.py | Reference for utility function patterns (_load_config, _api_request_with_retry, _write_index, _get_next_sequence_filename) |
| workflows/gen_media_content_v1/config.json.sample | Config structure that _load_config must parse |
| workflows/gen_media_content_v1/api_actions/ | Provider directory structure that import_provider must navigate |
| docs/QwenPaw/gen_media_content_v1/REQUIREMENTS.md | Full requirements (Sections 3.3, 3.4, 6, 7) |

## Test Requirements

- Unit tests for all 5 utility functions.
- Unit tests for both action stubs.
- All HTTP calls must be mocked (use unittest.mock or pytest-mock).
- Tests must run with: `.venv\Scripts\python -m pytest workflows/gen_media_content_v1/tests/test_actions.py -v`
- Tests must NOT require real API keys or network access.

## Acceptance Criteria

- AC-01: actions.py exists and is valid Python with no syntax errors.
- AC-02: All 5 utility functions are importable from the module.
- AC-03: _load_config correctly parses config.json.sample and raises FileNotFoundError for missing files.
- AC-04: _api_request_with_retry retries on 503/429, uses exponential backoff, and raises RuntimeError after max retries.
- AC-05: _write_index produces valid JSON with {"step": ..., "files": ...} structure and creates parent directories.
- AC-06: _get_next_sequence_filename returns base.ext, base_001.ext, base_002.ext in sequence.
- AC-07: import_provider dynamically imports from api_actions/{provider_type}/{provider_name}/ and validates call_api exists.
- AC-08: generate_images_default returns ActionResult with status="REJECTED" and reject_code="MISSING_PROVIDER".
- AC-09: generate_videos_default returns ActionResult with status="REJECTED" and reject_code="MISSING_PROVIDER".
- AC-10: All tests pass with pytest.
- AC-11: No existing files were modified (only new files created under workflows/gen_media_content_v1/).

## Definition of Done

- actions.py created with all 5 utility functions and 2 action stubs.
- tests/test_actions.py created with comprehensive test coverage.
- All tests pass.
- No existing files modified.
- Code follows the same patterns as the reference workflow (agnes_media_gen_v1).

## Source Reference

- Source requirements: docs/QwenPaw/gen_media_content_v1/REQUIREMENTS.md (Sections 3.3, 3.4, 6, 7)
- Source plan: docs/QwenPaw/gen_media_content_v1/PLAN.md (Phase 2)
- Reference workflow: workflows/agnes_media_gen_v1/actions.py
- Prior task: TASK-20260814-001-01 (Phase 1 scaffolding)
