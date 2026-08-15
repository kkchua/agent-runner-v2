---
template_id: SYS-03-TK
version: "1.0.0"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved task specification for gen_media_content_v1 Phase 3 image provider"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
---

# Task: gen_media_content_v1 Phase 3 - API Provider render_image (agnes_v1)

## Document Metadata

- Document ID: TASK-20260815-001-03
- Source backlog reference: WI-20260814-001 (gen_media_content_v1 workflow)
- Task IDs covered: WI-20260814-001-03
- Date of generation: 2026-08-15
- Producing workflow: Manual initiation
- Producing agent: default (Kai)
- Prior task: TASK-20260814-001-02 (Phase 2 root actions — completed)

## Task Overview

Create the Agnes v1 image rendering provider module at `api_actions/render_image/agnes_v1/`. This provider implements a pure `call_api()` function that generates images from text prompts using the Agnes Image API.

The provider is a standalone module that can be dynamically imported by the root `actions.py` via `import_provider("render_image", "agnes_v1")`. It must export a `call_api()` function with a standardized signature.

Expected outcome: A valid Python module with `call_api()` that makes HTTP requests to Agnes Image API, returns image URLs, and is covered by unit tests with mocked HTTP.

## Detailed Implementation Steps

### Step 1: Create Provider Module

Create `workflows/gen_media_content_v1/api_actions/render_image/agnes_v1/__init__.py`:

#### 1a: call_api(prompt, config, api_key, base_url)
- Make HTTP POST to `{base_url}/v1/images/generations`
- Payload: `{"model": config["model"], "prompt": prompt, "size": config["size"], "ratio": config.get("ratio", "")}`
- Headers: `{"Authorization": "Bearer {api_key}", "Content-Type": "application/json"}`
- Return dict: `{"image_url": "<url>", "revised_prompt": "<prompt>"}`
- Raise `RuntimeError` on HTTP errors or missing image URL in response

### Step 2: Create Unit Tests

Create `workflows/gen_media_content_v1/tests/test_image_provider_agnes_v1.py` with tests for:

- call_api: successful image generation (mocked 200 response with image URL)
- call_api: missing image URL in response (raises RuntimeError)
- call_api: HTTP error handling (mocked 500 response)
- call_api: correct payload structure (verify model, prompt, size, ratio fields)
- call_api: correct endpoint URL construction

All tests must use mocks for HTTP calls. No real API keys required.

## Technical Specifications

- All file paths are relative to agent-runner-v2 project root (D:\MyProjectSpace\01_Workflows\agent-runner-v2).
- Do NOT modify any existing workflow files. Only create/modify files under workflows/gen_media_content_v1/api_actions/render_image/agnes_v1/ and workflows/gen_media_content_v1/tests/.
- Follow the same patterns as workflows/agnes_media_gen_v1/impls/agnes_media_v1/actions.py for API interaction.
- Use `requests` library for HTTP calls.
- The `call_api()` function must be pure — no side effects, no file I/O, no state mutation.
- Config dict structure from config.json.sample:
  ```json
  {
    "api": {
      "agnes_v1": {
        "model": "agnes-image-2.1-flash",
        "size": "1024x1024",
        "ratio": "1:1"
      }
    }
  }
  ```

## Reference Files

| File | Purpose |
|---|---|
| workflows/agnes_media_gen_v1/impls/agnes_media_v1/actions.py | Reference for Agnes API interaction pattern (lines 100-200) |
| workflows/gen_media_content_v1/config.json.sample | Config structure with agnes_v1 settings |
| workflows/gen_media_content_v1/actions.py | Root actions with import_provider() function |
| workflows/gen_media_content_v1/api_actions/render_image/__init__.py | Registry docstring |

## Test Requirements

- Unit tests for call_api() function.
- All HTTP calls must be mocked (use unittest.mock or pytest-mock).
- Tests must run with: `.venv\Scripts\python -m pytest workflows/gen_media_content_v1/tests/test_image_provider_agnes_v1.py -v`
- Tests must NOT require real API keys or network access.

## Acceptance Criteria

- AC-01: agnes_v1/__init__.py exists and is valid Python with no syntax errors.
- AC-02: call_api() is importable from the module.
- AC-03: call_api() returns dict with "image_url" key on successful response.
- AC-04: call_api() raises RuntimeError when image URL is missing from response.
- AC-05: call_api() raises RuntimeError on HTTP errors (500, etc.).
- AC-06: call_api() sends correct payload structure (model, prompt, size, ratio).
- AC-07: call_api() constructs correct endpoint URL ({base_url}/v1/images/generations).
- AC-08: All tests pass with pytest.
- AC-09: No existing files were modified (only new files created).

## Definition of Done

- api_actions/render_image/agnes_v1/__init__.py created with call_api() function.
- tests/test_image_provider_agnes_v1.py created with comprehensive test coverage.
- All tests pass.
- No existing files modified.
- Code follows the same patterns as the reference workflow (agnes_media_gen_v1).

## Source Reference

- Source requirements: docs/QwenPaw/gen_media_content_v1/REQUIREMENTS.md (Section 3.3)
- Source plan: docs/QwenPaw/gen_media_content_v1/PLAN.md (Phase 3)
- Reference workflow: workflows/agnes_media_gen_v1/impls/agnes_media_v1/actions.py
- Prior task: TASK-20260814-001-02 (Phase 2 root actions)
