---
template_id: "SYS-03-IM"
version: "1.0.0"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "implementation plan for task execution"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "SDLC50IMP-7zblrwi8"
managed_by: "workflow-generated"
---

# Implementation Plan: gen_media_content_v1 Phase 3 - API Provider render_image (agnes_v1)

## Document Metadata

- Document ID: IMPL-20260815-001-002
- Source task: TASK-20260815-001-03
- Date of generation: 2026-08-15
- Producing workflow: sdlc_50_implementation_v1
- Producing agent: qwen3.7-plus

## 1. Acceptance Criteria Tests

The following testable acceptance criteria are derived from TASK-20260815-001-03. Each criterion defines what "done" means before implementation design.

### ACT-01: Module Existence and Validity

- **Test ID**: ACT-01
- **Test Description**: agnes_v1/__init__.py exists and is valid Python with no syntax errors.
- **Verification Method**: Run `.venv\Scripts\python -c "import ast; ast.parse(open('workflows/gen_media_content_v1/api_actions/render_image/agnes_v1/__init__.py').read())"` and verify exit code 0.
- **Expected Result**: File parses without SyntaxError.
- **Current State**: MISSING (directory and file do not exist on disk).

### ACT-02: call_api Importability

- **Test ID**: ACT-02
- **Test Description**: call_api() is importable from the module via import_provider or direct import.
- **Verification Method**: Run `.venv\Scripts\python -c "from workflows.gen_media_content_v1.api_actions.render_image.agnes_v1 import call_api"` and verify exit code 0.
- **Expected Result**: call_api resolves without ImportError.
- **Current State**: MISSING (module does not exist).

### ACT-03: Successful Image Generation Return

- **Test ID**: ACT-03
- **Test Description**: call_api() returns dict with "image_url" key on successful HTTP 200 response.
- **Verification Method**: Unit test: mock requests.post to return 200 with `{"data": [{"url": "https://example.com/image.png"}]}`, verify returned dict contains `"image_url"` with correct value.
- **Expected Result**: Return value is `{"image_url": "https://example.com/image.png", "revised_prompt": "<prompt>"}`.
- **Current State**: MISSING (function not implemented).

### ACT-04: Missing Image URL Raises RuntimeError

- **Test ID**: ACT-04
- **Test Description**: call_api() raises RuntimeError when image URL is missing from response.
- **Verification Method**: Unit test: mock requests.post to return 200 with `{"data": []}` (empty data array), verify RuntimeError is raised.
- **Expected Result**: RuntimeError raised with descriptive message.
- **Current State**: MISSING (function not implemented).

### ACT-05: HTTP Error Raises RuntimeError

- **Test ID**: ACT-05
- **Test Description**: call_api() raises RuntimeError on HTTP errors (500, etc.).
- **Verification Method**: Unit test: mock requests.post to raise requests.exceptions.HTTPError or return 500 status, verify RuntimeError is raised.
- **Expected Result**: RuntimeError raised on HTTP error conditions.
- **Current State**: MISSING (function not implemented).

### ACT-06: Correct Payload Structure

- **Test ID**: ACT-06
- **Test Description**: call_api() sends correct payload structure with model, prompt, size, ratio fields.
- **Verification Method**: Unit test: mock requests.post, call call_api() with known arguments, inspect the json= keyword argument passed to requests.post. Verify it contains `{"model": "<model>", "prompt": "<prompt>", "size": "<size>", "ratio": "<ratio>"}`.
- **Expected Result**: Payload matches spec: model from config["model"], prompt from argument, size from config["size"], ratio from config.get("ratio", "").
- **Current State**: MISSING (function not implemented).

### ACT-07: Correct Endpoint URL Construction

- **Test ID**: ACT-07
- **Test Description**: call_api() constructs correct endpoint URL ({base_url}/v1/images/generations).
- **Verification Method**: Unit test: mock requests.post, call call_api() with base_url="https://api.example.com", verify requests.post was called with URL "https://api.example.com/v1/images/generations".
- **Expected Result**: URL is `{base_url}/v1/images/generations` with proper slash handling.
- **Current State**: MISSING (function not implemented).

### ACT-08: All Tests Pass with pytest

- **Test ID**: ACT-08
- **Test Description**: All unit tests in test_image_provider_agnes_v1.py pass.
- **Verification Method**: Run `.venv\Scripts\python -m pytest workflows/gen_media_content_v1/tests/test_image_provider_agnes_v1.py -v` and verify exit code 0 with all tests passing.
- **Expected Result**: All tests pass; no failures, no errors.
- **Current State**: MISSING (test file does not exist).

### ACT-09: No Existing Files Modified

- **Test ID**: ACT-09
- **Test Description**: No existing files were modified; only new files were created.
- **Verification Method**: Run `git diff --name-only` and verify no existing files appear in the diff. Only new (untracked) files should be present.
- **Expected Result**: Only two new files created: agnes_v1/__init__.py and test_image_provider_agnes_v1.py.
- **Current State**: N/A (will verify after implementation).

## 2. State Verification

### Files That Already Exist and Are Complete

| File | Status | Evidence |
|------|--------|----------|
| `workflows/gen_media_content_v1/actions.py` | EXISTS (274 lines) | Read from disk; contains import_provider() function |
| `workflows/gen_media_content_v1/api_actions/__init__.py` | EXISTS | Exists as empty package init |
| `workflows/gen_media_content_v1/api_actions/render_image/__init__.py` | EXISTS (5 lines) | Registry docstring only |
| `workflows/gen_media_content_v1/config.json.sample` | EXISTS (38 lines) | Config structure with agnes_v1 section |
| `workflows/gen_media_content_v1/tests/__init__.py` | EXISTS | Exists as empty package init |
| `workflows/gen_media_content_v1/tests/test_actions.py` | EXISTS (387 lines) | Phase 2 tests, complete |
| `workflows/agnes_media_gen_v1/impls/agnes_media_v1/actions.py` | EXISTS (544 lines) | Reference for API pattern |

### Files That Need to Be Created From Scratch

| File | Purpose | Parent Dir Exists? |
|------|---------|-------------------|
| `workflows/gen_media_content_v1/api_actions/render_image/agnes_v1/__init__.py` | Provider module with call_api() | NO (agnes_v1/ dir does not exist) |
| `workflows/gen_media_content_v1/tests/test_image_provider_agnes_v1.py` | Unit tests for agnes_v1 provider | YES (tests/ dir exists) |

### Summary

All prerequisite infrastructure (parent packages, registry, config, reference workflow) is in place from Phase 1 and Phase 2. This Phase 3 task creates exactly 2 new files and modifies 0 existing files.

## 3. Implementation Overview

This implementation creates the Agnes v1 image rendering provider as a standalone module. The provider is a pure function (call_api) that makes a single HTTP POST to the Agnes Image API, parses the response, and returns the image URL. It follows the same API interaction pattern observed in the reference workflow (`agnes_media_gen_v1/impls/agnes_media_v1/actions.py`, lines 117-172 for _process_single_image).

The module will be dynamically importable by the root actions.py via `import_provider("render_image", "agnes_v1")`, which constructs the module path `workflows.gen_media_content_v1.api_actions.render_image.agnes_v1` and validates that `call_api` exists.

**Implementation approach:**
1. Create directory `workflows/gen_media_content_v1/api_actions/render_image/agnes_v1/`
2. Create `__init__.py` with `call_api(prompt, config, api_key, base_url)` function
3. Use `requests` library (v2.33.0 installed) for HTTP POST
4. Create comprehensive unit tests with mocked HTTP calls
5. Verify no existing files were modified

**Key design decisions:**
- Pure function: no side effects, no file I/O, no state mutation
- Use `requests.post()` directly (not the retry utility from root actions.py) -- the TASK specifies a pure call_api, and the retry logic belongs at the workflow orchestration level
- Follow the response parsing pattern from reference: `resp_data.get("data", [])[0].get("url", "")`
- Use `resp.raise_for_status()` for HTTP error detection
- Return dict with `image_url` and `revised_prompt` keys

## 4. Task Traceability

| TASK Acceptance Criterion | IMPL Acceptance Criteria Test | Relationship |
|--------------------------|-------------------------------|--------------|
| AC-01: agnes_v1/__init__.py exists and is valid Python | ACT-01: Module Existence and Validity | Direct mapping |
| AC-02: call_api() is importable | ACT-02: call_api Importability | Direct mapping |
| AC-03: Returns dict with "image_url" on success | ACT-03: Successful Image Generation Return | Direct mapping |
| AC-04: Raises RuntimeError when URL missing | ACT-04: Missing Image URL Raises RuntimeError | Direct mapping |
| AC-05: Raises RuntimeError on HTTP errors | ACT-05: HTTP Error Raises RuntimeError | Direct mapping |
| AC-06: Sends correct payload structure | ACT-06: Correct Payload Structure | Direct mapping |
| AC-07: Constructs correct endpoint URL | ACT-07: Correct Endpoint URL Construction | Direct mapping |
| AC-08: All tests pass with pytest | ACT-08: All Tests Pass with pytest | Direct mapping |
| AC-09: No existing files modified | ACT-09: No Existing Files Modified | Direct mapping |

Source references:
- TASK: TASK-20260815-001-03 (gen_media_content_v1 Phase 3)
- Requirements: docs/QwenPaw/gen_media_content_v1/REQUIREMENTS.md (Section 3.3)
- Plan: docs/QwenPaw/gen_media_content_v1/PLAN.md (Phase 3)
- Prior task: TASK-20260814-001-02 (Phase 2 root actions -- completed)

## 5. Step-by-Step Plan

### STEP-01: Create agnes_v1 Provider Directory and Module

- **Action**: Create directory `workflows/gen_media_content_v1/api_actions/render_image/agnes_v1/` and file `__init__.py` containing the `call_api()` function.
- **Satisfies**: ACT-01, ACT-02, ACT-03, ACT-04, ACT-05, ACT-06, ACT-07
- **Details**:
  - Module docstring describing purpose
  - Import `requests` library
  - Define `call_api(prompt: str, config: dict, api_key: str, base_url: str) -> dict`
  - **Validate inputs** (defensive checks -- raises RuntimeError on bad input):
    - If `base_url` is empty or whitespace-only, raise RuntimeError("base_url must be a non-empty string")
    - If `config` is missing required keys "model" or "size", raise RuntimeError with descriptive message listing missing keys
  - Construct endpoint URL: `f"{base_url.rstrip('/')}/v1/images/generations"`
  - Build payload: `{"model": config["model"], "prompt": prompt, "size": config["size"], "ratio": config.get("ratio", "")}`
  - Set headers: `{"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}`
  - **Wrap all network and parsing operations in a single try/except** to convert all failure modes to RuntimeError:
    - Call `requests.post(endpoint, headers=headers, json=payload, timeout=500)`
    - Catch `requests.exceptions.RequestException` (base class covering ConnectionError, Timeout, HTTPError from raise_for_status, etc.) and re-raise as RuntimeError
    - Call `resp.raise_for_status()` to detect HTTP errors
    - Call `resp.json()` to parse response; catch `ValueError` (covers JSONDecodeError) and re-raise as RuntimeError
  - Parse response: `data = resp.json().get("data", [])`
  - Extract URL: `image_url = data[0].get("url", "")` if data is non-empty
  - If image_url is empty, raise RuntimeError
  - Return `{"image_url": image_url, "revised_prompt": prompt}`
- **Note on signature**: The registry docstring at `render_image/__init__.py` line 4 mentions a 5-parameter signature `call_api(prompt, image, config, api_key, base_url)` that includes an `image` parameter. However, the authoritative TASK specification (TASK-20260815-001-03, Step 1a) explicitly defines a 4-parameter signature `call_api(prompt, config, api_key, base_url)` for text-to-image generation. For text-to-image, there is no input image. The `image` parameter in the docstring appears to be inherited from the render_video template (where image-to-video DOES require an input image). The `import_provider()` function in `actions.py` (line 230) only checks `hasattr(module, "call_api")` -- it does not enforce signature. This implementation follows the TASK specification. Fixing the registry docstring is out of scope for this task (AC-09 prohibits modifying existing files).

### STEP-02: Create Unit Tests

- **Action**: Create file `workflows/gen_media_content_v1/tests/test_image_provider_agnes_v1.py` with comprehensive tests.
- **Satisfies**: ACT-03, ACT-04, ACT-05, ACT-06, ACT-07, ACT-08
- **Details**:
  - Test class: `TestCallApi`
  - Test 1: `test_successful_image_generation` -- mock 200 response with valid data, verify return dict
  - Test 2: `test_missing_image_url_raises_runtime_error` -- mock 200 response with empty data, verify RuntimeError
  - Test 3: `test_http_error_raises_runtime_error` -- mock 500 response, verify RuntimeError
  - Test 4: `test_correct_payload_structure` -- mock requests.post, inspect call args for model/prompt/size/ratio
  - Test 5: `test_correct_endpoint_url` -- verify URL is `{base_url}/v1/images/generations`
  - Test 6: `test_correct_headers` -- verify Authorization and Content-Type headers
  - All tests use `unittest.mock.patch` to mock `requests.post`

### STEP-03: Run Tests and Verify

- **Action**: Execute test suite and verify all pass.
- **Satisfies**: ACT-08
- **Command**: `.venv\Scripts\python -m pytest workflows/gen_media_content_v1/tests/test_image_provider_agnes_v1.py -v`
- **Expected**: All tests pass with exit code 0.

### STEP-04: Verify No Existing Files Modified

- **Action**: Check git status to confirm only new files were created.
- **Satisfies**: ACT-09
- **Command**: `git diff --name-only` (should return empty for tracked files)
- **Expected**: Only untracked new files appear.

## 6. Code Changes

### Files to Create

#### File 1: workflows/gen_media_content_v1/api_actions/render_image/agnes_v1/__init__.py

New provider module implementing call_api() for Agnes Image API.

Structure:
```
"""Agnes v1 image rendering provider.

Pure call_api() function that generates images from text prompts
using the Agnes Image API (v1/images/generations endpoint).

Signature follows TASK-20260815-001-03 Step 1a:
    call_api(prompt, config, api_key, base_url) -> dict

Note: The registry docstring at render_image/__init__.py mentions an
``image`` parameter. That signature applies to video providers (image-to-video).
For text-to-image generation, no input image is required.
"""
from __future__ import annotations

import requests


def call_api(prompt: str, config: dict, api_key: str, base_url: str) -> dict:
    """Generate an image from a text prompt using the Agnes Image API.

    Parameters
    ----------
    prompt : str
        Text description of the image to generate.
    config : dict
        Provider configuration with keys: model, size, ratio.
    api_key : str
        Bearer token for API authentication.
    base_url : str
        Base URL of the Agnes API (e.g., "https://apihub.agnes-ai.com").

    Returns
    -------
    dict
        {"image_url": "<url>", "revised_prompt": "<prompt>"}

    Raises
    ------
    RuntimeError
        If input validation fails, HTTP request fails, response is not
        valid JSON, or response contains no image URL.
    """
    # --- Input validation ---
    if not base_url or not base_url.strip():
        raise RuntimeError("base_url must be a non-empty string")

    missing_keys = [k for k in ("model", "size") if k not in config]
    if missing_keys:
        raise RuntimeError(
            f"config is missing required keys: {missing_keys}"
        )

    # --- Build request ---
    endpoint = f"{base_url.rstrip('/')}/v1/images/generations"
    payload = {
        "model": config["model"],
        "prompt": prompt,
        "size": config["size"],
        "ratio": config.get("ratio", ""),
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # --- Execute request with unified error handling ---
    try:
        resp = requests.post(endpoint, headers=headers, json=payload, timeout=500)
        resp.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Agnes Image API request failed: {exc}") from exc

    # --- Parse response ---
    try:
        resp_data = resp.json()
    except ValueError as exc:
        raise RuntimeError(
            f"Agnes Image API returned non-JSON response: {exc}"
        ) from exc

    data = resp_data.get("data", [])
    image_url = data[0].get("url", "") if data else ""

    if not image_url:
        raise RuntimeError(
            "Agnes Image API response contains no image URL"
        )

    return {"image_url": image_url, "revised_prompt": prompt}
```

#### File 2: workflows/gen_media_content_v1/tests/test_image_provider_agnes_v1.py

New test module with 6 test cases covering all acceptance criteria.

Structure:
```
"""Unit tests for agnes_v1 image rendering provider.

Tests cover successful generation, error handling, payload structure,
endpoint URL construction, and header validation.
All HTTP calls are mocked; no real API keys or network access required.
"""
```

### Files to Modify

None. Per TASK requirement AC-09, no existing files are modified.

### Files to Delete

None.

### Codebase Files Referenced (Read-Only)

| File | Purpose |
|------|---------|
| `workflows/agnes_media_gen_v1/impls/agnes_media_v1/actions.py` | Reference for Agnes API interaction pattern (lines 117-172: payload construction, headers, response parsing) |
| `workflows/gen_media_content_v1/config.json.sample` | Config structure showing agnes_v1 keys (model, size, ratio) |
| `workflows/gen_media_content_v1/actions.py` | Root actions with import_provider() function (line 196-234) |
| `workflows/gen_media_content_v1/api_actions/render_image/__init__.py` | Registry docstring confirming provider contract |
| `workflows/gen_media_content_v1/tests/test_actions.py` | Reference for test structure and mocking patterns |

## 7. Test Implementation

The following test code implements the Acceptance Criteria Tests from Section 1.

```python
"""Unit tests for agnes_v1 image rendering provider.

Tests cover successful generation, error handling, payload structure,
endpoint URL construction, and header validation.
All HTTP calls are mocked; no real API keys or network access required.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests as real_requests

# Ensure the project root is importable
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from workflows.gen_media_content_v1.api_actions.render_image.agnes_v1 import call_api


class TestCallApi:
    """Tests for call_api function in agnes_v1 provider."""

    def test_successful_image_generation(self):
        """ACT-03: Returns dict with image_url on successful 200 response."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": [{"url": "https://example.com/generated.png"}]
        }
        mock_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-image-2.1-flash", "size": "1024x1024", "ratio": "1:1"}

        with patch(
            "workflows.gen_media_content_v1.api_actions.render_image.agnes_v1.requests"
        ) as mock_requests:
            mock_requests.post.return_value = mock_resp

            result = call_api(
                prompt="a cat in a garden",
                config=config,
                api_key="test-key-123",
                base_url="https://apihub.agnes-ai.com",
            )

        assert "image_url" in result
        assert result["image_url"] == "https://example.com/generated.png"
        assert "revised_prompt" in result

    def test_missing_image_url_raises_runtime_error(self):
        """ACT-04: Raises RuntimeError when image URL is missing from response."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"data": []}
        mock_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-image-2.1-flash", "size": "1024x1024"}

        with patch(
            "workflows.gen_media_content_v1.api_actions.render_image.agnes_v1.requests"
        ) as mock_requests:
            mock_requests.post.return_value = mock_resp

            with pytest.raises(RuntimeError):
                call_api(
                    prompt="a sunset",
                    config=config,
                    api_key="test-key-123",
                    base_url="https://apihub.agnes-ai.com",
                )

    def test_http_error_raises_runtime_error(self):
        """ACT-05: Raises RuntimeError on HTTP errors (500)."""
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.raise_for_status.side_effect = real_requests.exceptions.HTTPError(
            "500 Server Error"
        )

        config = {"model": "agnes-image-2.1-flash", "size": "1024x1024"}

        with patch(
            "workflows.gen_media_content_v1.api_actions.render_image.agnes_v1.requests"
        ) as mock_requests:
            mock_requests.post.return_value = mock_resp

            with pytest.raises(RuntimeError):
                call_api(
                    prompt="a mountain",
                    config=config,
                    api_key="test-key-123",
                    base_url="https://apihub.agnes-ai.com",
                )

    def test_correct_payload_structure(self):
        """ACT-06: Sends correct payload with model, prompt, size, ratio fields."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": [{"url": "https://example.com/img.png"}]
        }
        mock_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-image-2.1-flash", "size": "1024x1024", "ratio": "1:1"}

        with patch(
            "workflows.gen_media_content_v1.api_actions.render_image.agnes_v1.requests"
        ) as mock_requests:
            mock_requests.post.return_value = mock_resp

            call_api(
                prompt="a flower",
                config=config,
                api_key="test-key-123",
                base_url="https://apihub.agnes-ai.com",
            )

            mock_requests.post.assert_called_once()
            call_kwargs = mock_requests.post.call_args
            payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")

            assert payload["model"] == "agnes-image-2.1-flash"
            assert payload["prompt"] == "a flower"
            assert payload["size"] == "1024x1024"
            assert payload["ratio"] == "1:1"

    def test_correct_endpoint_url(self):
        """ACT-07: Constructs correct endpoint URL {base_url}/v1/images/generations."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": [{"url": "https://example.com/img.png"}]
        }
        mock_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-image-2.1-flash", "size": "1024x1024"}

        with patch(
            "workflows.gen_media_content_v1.api_actions.render_image.agnes_v1.requests"
        ) as mock_requests:
            mock_requests.post.return_value = mock_resp

            call_api(
                prompt="a tree",
                config=config,
                api_key="test-key-123",
                base_url="https://apihub.agnes-ai.com",
            )

            mock_requests.post.assert_called_once()
            call_url = mock_requests.post.call_args[0][0]
            assert call_url == "https://apihub.agnes-ai.com/v1/images/generations"

    def test_correct_headers(self):
        """ACT-06/ACT-07 supplementary: Verifies Authorization and Content-Type headers."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": [{"url": "https://example.com/img.png"}]
        }
        mock_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-image-2.1-flash", "size": "1024x1024"}

        with patch(
            "workflows.gen_media_content_v1.api_actions.render_image.agnes_v1.requests"
        ) as mock_requests:
            mock_requests.post.return_value = mock_resp

            call_api(
                prompt="a bird",
                config=config,
                api_key="my-secret-key",
                base_url="https://apihub.agnes-ai.com",
            )

            mock_requests.post.assert_called_once()
            call_kwargs = mock_requests.post.call_args
            headers = call_kwargs.kwargs.get("headers") or call_kwargs[1].get("headers")

            assert headers["Authorization"] == "Bearer my-secret-key"
            assert headers["Content-Type"] == "application/json"

    def test_ratio_defaults_to_empty_string(self):
        """ACT-06 supplementary: ratio defaults to empty string when not in config."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": [{"url": "https://example.com/img.png"}]
        }
        mock_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-image-2.1-flash", "size": "1024x1024"}

        with patch(
            "workflows.gen_media_content_v1.api_actions.render_image.agnes_v1.requests"
        ) as mock_requests:
            mock_requests.post.return_value = mock_resp

            call_api(
                prompt="a sky",
                config=config,
                api_key="test-key",
                base_url="https://apihub.agnes-ai.com",
            )

            call_kwargs = mock_requests.post.call_args
            payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
            assert payload["ratio"] == ""
```

## 8. Rollback Plan

If implementation fails or causes issues:

1. **Delete new files**: Remove the two created files:
   - `workflows/gen_media_content_v1/api_actions/render_image/agnes_v1/__init__.py`
   - `workflows/gen_media_content_v1/api_actions/render_image/agnes_v1/` (directory)
   - `workflows/gen_media_content_v1/tests/test_image_provider_agnes_v1.py`

2. **No existing files to restore**: Since no existing files are modified, rollback is limited to deleting the new files.

3. **Verification**: Run `.venv\Scripts\python -m pytest workflows/gen_media_content_v1/tests/ -v` to confirm Phase 2 tests still pass after cleanup.

4. **Git rollback**: `git clean -fd workflows/gen_media_content_v1/api_actions/render_image/agnes_v1/` and `git clean -f workflows/gen_media_content_v1/tests/test_image_provider_agnes_v1.py`

## 9. Dependencies

### External Dependencies

| Dependency | Version | Purpose | Status |
|------------|---------|---------|--------|
| `requests` | 2.33.0 | HTTP client for API calls | Installed |
| `pytest` | 9.1.1+ | Test runner | Installed |

### Prerequisites

| Prerequisite | Status | Evidence |
|--------------|--------|----------|
| Phase 1: Workflow scaffolding | COMPLETE | api_actions/ directory tree exists with __init__.py files |
| Phase 2: Root actions with import_provider() | COMPLETE | actions.py contains import_provider() at line 196 |
| Parent package render_image/__init__.py | COMPLETE | Registry docstring present |
| config.json.sample with agnes_v1 section | COMPLETE | Config keys: model, size, ratio |

### No New Dependencies Required

This implementation uses only the `requests` library (already a project dependency) and `pytest` (already installed for testing). No new pip packages are needed.

## 10. Open Questions

1. **None at this time.** The TASK specification is sufficiently detailed for implementation. All reference files exist and the API interaction pattern is well-documented in the reference workflow.

### Assumptions

- The Agnes Image API response format follows the pattern `{"data": [{"url": "..."}]}` as observed in the reference workflow (agnes_media_gen_v1, line 140-142).
- The `call_api()` function uses direct `requests.post()` without retry logic. Retry orchestration is the responsibility of the calling workflow action, not the provider module. This aligns with the TASK requirement for a "pure" function.
- The `base_url` parameter may or may not have a trailing slash; the implementation strips it with `rstrip('/')` before appending the endpoint path.
- The `revised_prompt` in the return dict is set to the input `prompt` value, as the TASK does not specify a separate revised prompt field in the API response.
