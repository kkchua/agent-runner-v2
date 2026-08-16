---
template_id: "SYS-03-IM"
version: "1.0.0"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "implementation plan for task execution"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "Approved"
effective_version: "SDLC01IER-xqzdanu5"
managed_by: "workflow-generated"
---

# Implementation Plan: gen_media_content_v1 Phase 4 - Video Provider (agnes_v2)

## Document Metadata

- Document ID: IMPL-20260815-001-003
- Source task: TASK-20260815-001-04
- Task title: gen_media_content_v1 Phase 4 - API Provider render_video (agnes_v2)
- Date of generation: 2026-08-15
- Producing workflow: impl_generate step (SDLC pipeline)
- Prior plan: IMPL-20260815-001-002 (Phase 3 image provider -- completed)

---

## 1. Acceptance Criteria Tests

The following testable acceptance criteria are derived from TASK-20260815-001-04.
Each criterion defines what "done" means before implementation design begins.

| Test ID | Test Description | Verification Method | Expected Result | Current State |
|---|---|---|---|---|
| ACT-01 | agnes_v2/__init__.py exists and is valid Python with no syntax errors | `python -c "import ast; ast.parse(open('workflows/gen_media_content_v1/api_actions/render_video/agnes_v2/__init__.py').read())"` | Exit code 0, no SyntaxError | MISSING |
| ACT-02 | call_api() is importable from the module | `python -c "from workflows.gen_media_content_v1.api_actions.render_video.agnes_v2 import call_api; assert callable(call_api)"` | Exit code 0, no ImportError or AttributeError | MISSING |
| ACT-03 | call_api() returns dict with "video_url" key on successful submit + poll cycle | pytest test: mock POST submit returning video_id, mock GET poll returning completed + url; assert result["video_url"] is correct URL | Returns {"video_url": "https://..."} dict | MISSING |
| ACT-04 | call_api() raises RuntimeError when video_id is missing from submit response | pytest test: mock POST submit returning dict with no video_id or id keys | RuntimeError raised | MISSING |
| ACT-05 | call_api() raises RuntimeError when poll returns failed/error/cancelled status | pytest test: mock GET poll returning status="failed"; also test "error" and "cancelled" (3 separate test methods) | RuntimeError raised for each terminal status | MISSING |
| ACT-06 | call_api() raises RuntimeError on HTTP errors during submit | pytest test: mock POST submit raising requests.exceptions.HTTPError | RuntimeError raised | MISSING |
| ACT-07 | call_api() raises RuntimeError when polling times out after max attempts | pytest test: mock GET poll returning status="processing" for 120+ attempts; patch time.sleep | RuntimeError raised after max attempts | MISSING |
| ACT-08 | call_api() sends correct submit payload with model, prompt, image, width, height, num_frames, frame_rate | pytest test: inspect mock_requests.post call_args for json payload keys and values | Payload contains all 7 required keys with correct values | MISSING |
| ACT-09 | call_api() constructs correct submit URL ({base_url}/v1/videos) | pytest test: inspect mock_requests.post call_args[0][0] for URL string | URL equals "https://apihub.agnes-ai.com/v1/videos" | MISSING |
| ACT-10 | call_api() constructs correct poll URL ({base_url}/agnesapi?video_id={id}) | pytest test: inspect mock_requests.get call_args[0][0] for URL string | URL equals "https://apihub.agnes-ai.com/agnesapi?video_id=test-id-123" | MISSING |
| ACT-11 | All 21 tests pass with pytest | `.venv/Scripts/python -m pytest workflows/gen_media_content_v1/tests/test_video_provider_agnes_v2.py -v` | 21 passed, 0 failed | MISSING |
| ACT-12 | No existing files were modified | `git diff --name-only` shows only new files under agnes_v2/ and tests/ | Only new files created, no modifications to existing tracked files | MISSING |
| ACT-13 | call_api() raises RuntimeError on connection error during submit | pytest test: mock POST submit raising requests.exceptions.ConnectionError | RuntimeError raised | MISSING |
| ACT-14 | call_api() raises RuntimeError on timeout error during submit | pytest test: mock POST submit raising requests.exceptions.Timeout | RuntimeError raised | MISSING |
| ACT-15 | negative_prompt included in payload when present in config | pytest test: config with negative_prompt key; verify payload includes it | Payload contains "negative_prompt" key | MISSING |
| ACT-16 | negative_prompt omitted from payload when absent from config | pytest test: config without negative_prompt key; verify payload does not include it | Payload does not contain "negative_prompt" key | MISSING |
| ACT-17 | Correct headers (Authorization Bearer + Content-Type for POST) | pytest test: inspect mock call headers dict | Headers contain "Authorization": "Bearer {api_key}" and "Content-Type": "application/json" | MISSING |
| ACT-18 | video_id extracted from "id" field (fallback) | pytest test: submit response contains {"id": "..."} but no "video_id" key | call_api() succeeds using the "id" value as video_id | MISSING |
| ACT-19 | video_url extracted from "video_url" field (fallback) | pytest test: poll response contains {"status": "completed", "video_url": "..."} but no "url" key | call_api() succeeds using the "video_url" value | MISSING |
| ACT-20 | Empty base_url raises RuntimeError | pytest test: call call_api() with base_url="" | RuntimeError raised with message containing "base_url" | MISSING |
| ACT-21 | Missing config keys raises RuntimeError | pytest test: call call_api() with config={} missing model/width/height | RuntimeError raised with message containing "missing required keys" | MISSING |
| ACT-22 | Poll-phase network error raises RuntimeError on final attempt | pytest test: mock GET poll raising requests.exceptions.ConnectionError on every attempt | RuntimeError raised after final attempt | MISSING |
| ACT-23 | Poll-phase JSON decode error raises RuntimeError on final attempt | pytest test: mock GET poll returning non-JSON response (ValueError on .json()) | RuntimeError raised on final attempt | MISSING |

---

## 2. State Verification

### Pre-Implementation File System Check

Date of check: 2026-08-15

#### Target Files (to be created)

| File Path | Status | Evidence |
|---|---|---|
| `workflows/gen_media_content_v1/api_actions/render_video/agnes_v2/__init__.py` | MISSING | glob **/render_video/agnes_v2/** returned no files |
| `workflows/gen_media_content_v1/tests/test_video_provider_agnes_v2.py` | MISSING | glob **/test_video_provider_agnes_v2.py returned no files |

#### Parent Directories (exist, ready for new subdirectory)

| Path | Status | Evidence |
|---|---|---|
| `workflows/gen_media_content_v1/api_actions/render_video/` | EXISTS | Contains __init__.py (registry docstring) |
| `workflows/gen_media_content_v1/api_actions/render_video/__init__.py` | EXISTS | 6 lines, registry docstring mentioning dynamic import by name |
| `workflows/gen_media_content_v1/tests/` | EXISTS | Contains __init__.py, test_image_provider_agnes_v1.py, test_context.py, test_actions.py |

#### Reference Files (read-only, exist and verified)

| Path | Status | Content Summary |
|---|---|---|
| `workflows/gen_media_content_v1/api_actions/render_image/agnes_v1/__init__.py` | EXISTS | Phase 3 image provider: 89 lines, call_api(prompt, config, api_key, base_url) -> dict, uses requests.post, input validation, unified error handling |
| `workflows/gen_media_content_v1/tests/test_image_provider_agnes_v1.py` | EXISTS | Phase 3 tests: 362 lines, 14 test methods in TestCallApi class, all HTTP mocked, patches requests module |
| `workflows/agnes_media_gen_v1/impls/agnes_media_v1/actions.py` | EXISTS | Reference video flow at lines 321-395: _process_single_video with submit + poll pattern, payload structure, polling logic |
| `workflows/gen_media_content_v1/config.json.sample` | EXISTS | Config structure with agnes_v2 section: model, width, height, num_frames, frame_rate |
| `workflows/gen_media_content_v1/api_actions/render_video/__init__.py` | EXISTS | Registry docstring: dynamic import by name, call_api(prompt, image, config, api_key, base_url) signature |

#### Scope Assessment

All work described in TASK-20260815-001-04 is NEW. No files need modification.
Both target deliverables must be created from scratch.

---

## 3. Implementation Overview

### Approach

This implementation creates the Agnes v2 video rendering provider module following the exact same structural pattern as the Phase 3 image provider (agnes_v1), adapted for the asynchronous submit-then-poll video API flow.

The implementation is divided into two files:

1. **Provider module** (`agnes_v2/__init__.py`): Pure `call_api()` function that validates inputs, submits a video generation job via HTTP POST, then polls for completion via HTTP GET until the video URL is available or an error/timeout occurs.

2. **Test module** (`test_video_provider_agnes_v2.py`): 21 unit tests covering all acceptance criteria, with all HTTP calls mocked and time.sleep patched to avoid delays.

### Key Design Decisions

- **Follow Phase 3 pattern**: The input validation, error handling, and test structure mirror the agnes_v1 image provider for consistency.
- **Two-phase API flow**: Unlike the synchronous image API, the video API requires submit + poll. The function encapsulates both phases.
- **Pure function**: No file I/O, no directory scanning, no state mutation. The function only makes HTTP requests and returns a result dict.
- **Polling strategy**: 10-second interval, 120 max attempts (20 minutes maximum). Matches the existing _process_single_video reference implementation.
- **Fallback field extraction**: video_id checks both "video_id" and "id" keys. video_url checks both "url" and "video_url" keys. This matches the existing reference implementation.

### What Remains

Everything described in TASK-20260815-001-04. No partial work exists.

---

## 4. Task Traceability

### TASK Acceptance Criteria to Implementation Test Mapping

| TASK AC | IMPL Test ID | Description |
|---|---|---|
| AC-01 | ACT-01 | Module exists and is valid Python |
| AC-02 | ACT-02 | call_api() is importable |
| AC-03 | ACT-03 | Returns dict with video_url on success |
| AC-04 | ACT-04 | RuntimeError when video_id missing |
| AC-05 | ACT-05 | RuntimeError on failed/error/cancelled poll status |
| AC-06 | ACT-06, ACT-13, ACT-14 | RuntimeError on HTTP/connection/timeout errors |
| AC-07 | ACT-07 | RuntimeError on poll timeout |
| AC-08 | ACT-08 | Correct submit payload structure |
| AC-09 | ACT-09 | Correct submit endpoint URL |
| AC-10 | ACT-10 | Correct poll endpoint URL |
| AC-11 | ACT-11 | All 21 tests pass |
| AC-12 | ACT-12 | No existing files modified |

### Additional Test Coverage (derived from TASK Step 2 detailed list and reference implementation)

| TASK Step 2 Item | IMPL Test ID |
|---|---|
| negative_prompt included when present | ACT-15 |
| negative_prompt omitted when absent | ACT-16 |
| Correct headers | ACT-17 |
| video_id from "id" fallback | ACT-18 |
| video_url from "video_url" fallback | ACT-19 |
| Empty base_url validation | ACT-20 |
| Missing config keys validation | ACT-21 |
| Poll-phase network error handling (reference pattern) | ACT-22 |
| Poll-phase JSON decode error handling (robustness improvement) | ACT-23 |

---

## 5. Step-by-Step Plan

### STEP-01: Create provider module directory and __init__.py

- **Action**: Create directory `workflows/gen_media_content_v1/api_actions/render_video/agnes_v2/` and file `__init__.py`.
- **Satisfies**: ACT-01
- **Details**: Implement call_api(prompt, image, config, api_key, base_url) with:
  - Input validation (base_url non-empty, required config keys: model, width, height)
  - Submit phase: POST to {base_url}/v1/videos with correct payload and headers
  - Extract video_id from response (check "video_id" then "id")
  - Poll phase: GET {base_url}/agnesapi?video_id={video_id} every 10s, max 120 attempts
  - On poll network error (RequestException): continue polling unless final attempt, then raise RuntimeError (matches reference _process_single_video pattern)
  - On poll JSON decode error (ValueError from resp.json()): raise RuntimeError on final attempt (robustness improvement over reference implementation)
  - Extract video_url from completed response (check "url" then "video_url")
  - RuntimeError on all failure modes

### STEP-02: Create test module

- **Action**: Create file `workflows/gen_media_content_v1/tests/test_video_provider_agnes_v2.py`.
- **Satisfies**: ACT-02 through ACT-21 (all test-based criteria)
- **Details**: Implement 21 test methods covering all acceptance criteria. All HTTP calls mocked via unittest.mock.patch. time.sleep patched to avoid real delays. Follow the test structure pattern from test_image_provider_agnes_v1.py.

### STEP-03: Run tests and verify all pass

- **Action**: Execute `.venv/Scripts/python -m pytest workflows/gen_media_content_v1/tests/test_video_provider_agnes_v2.py -v`
- **Satisfies**: ACT-11
- **Details**: All 21 tests must pass. If any fail, iterate on the provider module or tests until all pass.

### STEP-04: Verify no existing files were modified

- **Action**: Run `git diff --name-only` and `git status` to confirm only new files exist.
- **Satisfies**: ACT-12
- **Details**: The output should show only two new untracked files and no modifications to tracked files.

---

## 6. Code Changes

### Files to Create

#### 6a. workflows/gen_media_content_v1/api_actions/render_video/agnes_v2/__init__.py

New file. Agnes v2 video rendering provider module.

Structure:
- Module docstring describing the provider
- Import: `from __future__ import annotations`, `import time`, `import requests`
- Function: `call_api(prompt: str, image: str, config: dict, api_key: str, base_url: str) -> dict`
  - Input validation section
  - Build submit request section (endpoint, payload, headers)
  - Execute submit with try/except for requests.exceptions.RequestException
  - Parse submit response, extract video_id with fallback
  - Poll loop: for attempt in range(max_poll_attempts), time.sleep, GET request, check status
  - Poll error handling: catch RequestException (continue unless final attempt, then raise RuntimeError); catch ValueError from resp.json() (raise RuntimeError)
  - Return {"video_url": download_url}

#### 6b. workflows/gen_media_content_v1/tests/test_video_provider_agnes_v2.py

New file. Unit tests for agnes_v2 video provider.

Structure:
- Module docstring
- Imports: sys, pathlib, unittest.mock (MagicMock, patch), pytest, requests as real_requests
- sys.path setup for project root
- Import call_api from the provider module
- class TestCallApi with 21 test methods:
  1. test_successful_submit_and_poll_returns_video_url (ACT-03)
  2. test_missing_video_id_raises_runtime_error (ACT-04)
  3. test_poll_failed_status_raises_runtime_error (ACT-05)
  4. test_poll_error_status_raises_runtime_error (ACT-05)
  5. test_poll_cancelled_status_raises_runtime_error (ACT-05)
  6. test_http_error_on_submit_raises_runtime_error (ACT-06)
  7. test_connection_error_on_submit_raises_runtime_error (ACT-13)
  8. test_timeout_error_on_submit_raises_runtime_error (ACT-14)
  9. test_correct_submit_payload_structure (ACT-08)
  10. test_negative_prompt_included_when_present (ACT-15)
  11. test_negative_prompt_omitted_when_absent (ACT-16)
  12. test_correct_submit_endpoint_url (ACT-09)
  13. test_correct_poll_endpoint_url (ACT-10)
  14. test_correct_headers (ACT-17)
  15. test_empty_base_url_raises_runtime_error (ACT-20)
  16. test_missing_config_keys_raises_runtime_error (ACT-21)
  17. test_poll_timeout_raises_runtime_error (ACT-07)
  18. test_video_id_from_id_field_fallback (ACT-18)
  19. test_video_url_from_video_url_field_fallback (ACT-19)
  20. test_poll_network_error_on_final_attempt_raises_runtime_error (ACT-22)
  21. test_poll_json_decode_error_on_final_attempt_raises_runtime_error (ACT-23)

### Files to Modify

None. TASK explicitly states: "Do NOT modify any existing workflow files."

### Files to Delete

None.

### Codebase Files Referenced (read-only)

| File | Purpose |
|---|---|
| workflows/gen_media_content_v1/api_actions/render_image/agnes_v1/__init__.py | Structural pattern reference for call_api, input validation, error handling |
| workflows/gen_media_content_v1/tests/test_image_provider_agnes_v1.py | Test pattern reference for mocking strategy, test class structure |
| workflows/agnes_media_gen_v1/impls/agnes_media_v1/actions.py (lines 321-395) | Video API flow reference: submit payload, poll loop, field extraction |
| workflows/gen_media_content_v1/config.json.sample | Config structure reference for agnes_v2 settings |
| workflows/gen_media_content_v1/api_actions/render_video/__init__.py | Registry docstring confirming expected call_api signature |
| docs/QwenPaw/gen_media_content_v1/REQUIREMENTS.md (Section 7.2, 7.5) | API contract: endpoints, status values, common interface |

---

## 7. Test Implementation

### Test Module: test_video_provider_agnes_v2.py

The following is the complete test implementation that validates all Acceptance Criteria Tests from Section 1.

```python
"""Unit tests for agnes_v2 video rendering provider.

Tests cover successful submit+poll cycle, error handling for submit and poll
phases, payload structure, endpoint URL construction, header validation,
input validation, network error handling, negative_prompt conditional inclusion,
field fallback extraction, and poll timeout. All HTTP calls are mocked;
no real API keys or network access required.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest
import requests as real_requests

# Ensure the project root is importable
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from workflows.gen_media_content_v1.api_actions.render_video.agnes_v2 import call_api


# --- Helpers ---

SUBMIT_URL = "https://apihub.agnes-ai.com/v1/videos"
POLL_URL_TEMPLATE = "https://apihub.agnes-ai.com/agnesapi?video_id={}"
TEST_API_KEY = "test-key-123"
TEST_BASE_URL = "https://apihub.agnes-ai.com"
TEST_VIDEO_ID = "vid-abc-123"
TEST_VIDEO_URL = "https://cdn.agnes-ai.com/videos/output.mp4"

FULL_CONFIG = {
    "model": "agnes-video-v2.0",
    "width": 1024,
    "height": 576,
    "num_frames": 72,
    "frame_rate": 24,
}

CONFIG_WITH_NEGATIVE = {
    **FULL_CONFIG,
    "negative_prompt": "blurry, distorted",
}

MODULE_PATH = "workflows.gen_media_content_v1.api_actions.render_video.agnes_v2"


def _make_submit_response(video_id=TEST_VIDEO_ID):
    """Build a mock response for the submit POST."""
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"video_id": video_id}
    resp.raise_for_status = MagicMock()
    return resp


def _make_poll_response(status="completed", url=TEST_VIDEO_URL, video_url_key="url"):
    """Build a mock response for the poll GET."""
    resp = MagicMock()
    resp.status_code = 200
    data = {"status": status}
    if status == "completed":
        data[video_url_key] = url
    resp.json.return_value = data
    resp.raise_for_status = MagicMock()
    return resp


def _patch_requests():
    """Return a patch context manager for the requests module in the provider."""
    return patch(f"{MODULE_PATH}.requests")


class TestCallApi:
    """Tests for call_api function in agnes_v2 video provider."""

    # --- ACT-03: Successful cycle ---

    def test_successful_submit_and_poll_returns_video_url(self):
        """ACT-03: Returns dict with video_url on successful submit + poll."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response(status="completed")

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            result = call_api(
                prompt="a cat walking",
                image="https://example.com/img.png",
                config=FULL_CONFIG,
                api_key=TEST_API_KEY,
                base_url=TEST_BASE_URL,
            )

        assert result == {"video_url": TEST_VIDEO_URL}

    # --- ACT-04: Missing video_id ---

    def test_missing_video_id_raises_runtime_error(self):
        """ACT-04: Raises RuntimeError when video_id is missing from submit response."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"request_id": "some-other-id"}
        submit_resp.raise_for_status = MagicMock()

        with _patch_requests() as mock_requests:
            mock_requests.post.return_value = submit_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError):
                call_api(
                    prompt="a dog running",
                    image="https://example.com/img.png",
                    config=FULL_CONFIG,
                    api_key=TEST_API_KEY,
                    base_url=TEST_BASE_URL,
                )

    # --- ACT-05: Terminal poll statuses ---

    def test_poll_failed_status_raises_runtime_error(self):
        """ACT-05: Raises RuntimeError when poll returns 'failed' status."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response(status="failed")

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError):
                call_api(
                    prompt="a bird flying",
                    image="https://example.com/img.png",
                    config=FULL_CONFIG,
                    api_key=TEST_API_KEY,
                    base_url=TEST_BASE_URL,
                )

    def test_poll_error_status_raises_runtime_error(self):
        """ACT-05: Raises RuntimeError when poll returns 'error' status."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response(status="error")

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError):
                call_api(
                    prompt="a fish swimming",
                    image="https://example.com/img.png",
                    config=FULL_CONFIG,
                    api_key=TEST_API_KEY,
                    base_url=TEST_BASE_URL,
                )

    def test_poll_cancelled_status_raises_runtime_error(self):
        """ACT-05: Raises RuntimeError when poll returns 'cancelled' status."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response(status="cancelled")

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError):
                call_api(
                    prompt="a whale diving",
                    image="https://example.com/img.png",
                    config=FULL_CONFIG,
                    api_key=TEST_API_KEY,
                    base_url=TEST_BASE_URL,
                )

    # --- ACT-06 / ACT-13 / ACT-14: Submit HTTP errors ---

    def test_http_error_on_submit_raises_runtime_error(self):
        """ACT-06: Raises RuntimeError on HTTP error during submit."""
        submit_resp = MagicMock()
        submit_resp.status_code = 500
        submit_resp.raise_for_status.side_effect = real_requests.exceptions.HTTPError(
            "500 Server Error"
        )

        with _patch_requests() as mock_requests:
            mock_requests.post.return_value = submit_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError):
                call_api(
                    prompt="a tree swaying",
                    image="https://example.com/img.png",
                    config=FULL_CONFIG,
                    api_key=TEST_API_KEY,
                    base_url=TEST_BASE_URL,
                )

    def test_connection_error_on_submit_raises_runtime_error(self):
        """ACT-13: Raises RuntimeError on ConnectionError during submit."""
        with _patch_requests() as mock_requests:
            mock_requests.post.side_effect = real_requests.exceptions.ConnectionError(
                "Connection refused"
            )
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError):
                call_api(
                    prompt="a river flowing",
                    image="https://example.com/img.png",
                    config=FULL_CONFIG,
                    api_key=TEST_API_KEY,
                    base_url=TEST_BASE_URL,
                )

    def test_timeout_error_on_submit_raises_runtime_error(self):
        """ACT-14: Raises RuntimeError on Timeout during submit."""
        with _patch_requests() as mock_requests:
            mock_requests.post.side_effect = real_requests.exceptions.Timeout(
                "Request timed out"
            )
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError):
                call_api(
                    prompt="a mountain view",
                    image="https://example.com/img.png",
                    config=FULL_CONFIG,
                    api_key=TEST_API_KEY,
                    base_url=TEST_BASE_URL,
                )

    # --- ACT-08: Payload structure ---

    def test_correct_submit_payload_structure(self):
        """ACT-08: Sends correct submit payload with all required fields."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response()

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a sunset over ocean",
                image="https://example.com/img.png",
                config=FULL_CONFIG,
                api_key=TEST_API_KEY,
                base_url=TEST_BASE_URL,
            )

            mock_requests.post.assert_called_once()
            call_kwargs = mock_requests.post.call_args
            payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")

            assert payload["model"] == "agnes-video-v2.0"
            assert payload["prompt"] == "a sunset over ocean"
            assert payload["image"] == "https://example.com/img.png"
            assert payload["width"] == 1024
            assert payload["height"] == 576
            assert payload["num_frames"] == 72
            assert payload["frame_rate"] == 24

    # --- ACT-15 / ACT-16: negative_prompt conditional ---

    def test_negative_prompt_included_when_present(self):
        """ACT-15: negative_prompt is included in payload when present in config."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response()

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a forest scene",
                image="https://example.com/img.png",
                config=CONFIG_WITH_NEGATIVE,
                api_key=TEST_API_KEY,
                base_url=TEST_BASE_URL,
            )

            call_kwargs = mock_requests.post.call_args
            payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
            assert "negative_prompt" in payload
            assert payload["negative_prompt"] == "blurry, distorted"

    def test_negative_prompt_omitted_when_absent(self):
        """ACT-16: negative_prompt is omitted from payload when absent from config."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response()

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a city street",
                image="https://example.com/img.png",
                config=FULL_CONFIG,
                api_key=TEST_API_KEY,
                base_url=TEST_BASE_URL,
            )

            call_kwargs = mock_requests.post.call_args
            payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
            assert "negative_prompt" not in payload

    # --- ACT-09: Submit URL ---

    def test_correct_submit_endpoint_url(self):
        """ACT-09: Constructs correct submit URL {base_url}/v1/videos."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response()

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a flower blooming",
                image="https://example.com/img.png",
                config=FULL_CONFIG,
                api_key=TEST_API_KEY,
                base_url=TEST_BASE_URL,
            )

            submit_url = mock_requests.post.call_args[0][0]
            assert submit_url == "https://apihub.agnes-ai.com/v1/videos"

    # --- ACT-10: Poll URL ---

    def test_correct_poll_endpoint_url(self):
        """ACT-10: Constructs correct poll URL {base_url}/agnesapi?video_id={id}."""
        submit_resp = _make_submit_response(video_id="vid-xyz-789")
        poll_resp = _make_poll_response()

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a cloud drifting",
                image="https://example.com/img.png",
                config=FULL_CONFIG,
                api_key=TEST_API_KEY,
                base_url=TEST_BASE_URL,
            )

            poll_url = mock_requests.get.call_args[0][0]
            assert poll_url == "https://apihub.agnes-ai.com/agnesapi?video_id=vid-xyz-789"

    # --- ACT-17: Headers ---

    def test_correct_headers(self):
        """ACT-17: Submits with correct Authorization and Content-Type headers."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response()

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a star twinkling",
                image="https://example.com/img.png",
                config=FULL_CONFIG,
                api_key="my-secret-key",
                base_url=TEST_BASE_URL,
            )

            call_kwargs = mock_requests.post.call_args
            headers = call_kwargs.kwargs.get("headers") or call_kwargs[1].get("headers")
            assert headers["Authorization"] == "Bearer my-secret-key"
            assert headers["Content-Type"] == "application/json"

    # --- ACT-20: Empty base_url ---

    def test_empty_base_url_raises_runtime_error(self):
        """ACT-20: Empty base_url raises RuntimeError."""
        with pytest.raises(RuntimeError, match="base_url"):
            call_api(
                prompt="a moon rising",
                image="https://example.com/img.png",
                config=FULL_CONFIG,
                api_key=TEST_API_KEY,
                base_url="",
            )

    # --- ACT-21: Missing config keys ---

    def test_missing_config_keys_raises_runtime_error(self):
        """ACT-21: Missing required config keys raises RuntimeError."""
        with pytest.raises(RuntimeError, match="missing required keys"):
            call_api(
                prompt="a sun setting",
                image="https://example.com/img.png",
                config={},
                api_key=TEST_API_KEY,
                base_url=TEST_BASE_URL,
            )

    # --- ACT-07: Poll timeout ---

    def test_poll_timeout_raises_runtime_error(self):
        """ACT-07: Raises RuntimeError when polling times out after max attempts."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response(status="processing")

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError):
                call_api(
                    prompt="a rain falling",
                    image="https://example.com/img.png",
                    config=FULL_CONFIG,
                    api_key=TEST_API_KEY,
                    base_url=TEST_BASE_URL,
                )

    # --- ACT-18: video_id fallback ---

    def test_video_id_from_id_field_fallback(self):
        """ACT-18: Extracts video_id from 'id' field when 'video_id' is absent."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"id": "fallback-id-456"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = _make_poll_response()

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            result = call_api(
                prompt="a snow falling",
                image="https://example.com/img.png",
                config=FULL_CONFIG,
                api_key=TEST_API_KEY,
                base_url=TEST_BASE_URL,
            )

        assert result["video_url"] == TEST_VIDEO_URL
        poll_url = mock_requests.get.call_args[0][0]
        assert "video_id=fallback-id-456" in poll_url

    # --- ACT-19: video_url fallback ---

    def test_video_url_from_video_url_field_fallback(self):
        """ACT-19: Extracts video_url from 'video_url' field when 'url' is absent."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response(
            status="completed",
            url="https://cdn.agnes-ai.com/videos/alt-output.mp4",
            video_url_key="video_url",
        )

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            result = call_api(
                prompt="a leaf falling",
                image="https://example.com/img.png",
                config=FULL_CONFIG,
                api_key=TEST_API_KEY,
                base_url=TEST_BASE_URL,
            )

        assert result["video_url"] == "https://cdn.agnes-ai.com/videos/alt-output.mp4"

    # --- ACT-22: Poll-phase network error ---

    def test_poll_network_error_on_final_attempt_raises_runtime_error(self):
        """ACT-22: Raises RuntimeError when poll GET raises ConnectionError on final attempt."""
        submit_resp = _make_submit_response()

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.side_effect = real_requests.exceptions.ConnectionError(
                "Connection refused"
            )
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError):
                call_api(
                    prompt="a wind blowing",
                    image="https://example.com/img.png",
                    config=FULL_CONFIG,
                    api_key=TEST_API_KEY,
                    base_url=TEST_BASE_URL,
                )

    # --- ACT-23: Poll-phase JSON decode error ---

    def test_poll_json_decode_error_on_final_attempt_raises_runtime_error(self):
        """ACT-23: Raises RuntimeError when poll response is not valid JSON on final attempt."""
        submit_resp = _make_submit_response()
        bad_poll_resp = MagicMock()
        bad_poll_resp.status_code = 200
        bad_poll_resp.json.side_effect = ValueError("No JSON found")
        bad_poll_resp.raise_for_status = MagicMock()

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = bad_poll_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError):
                call_api(
                    prompt="a fire burning",
                    image="https://example.com/img.png",
                    config=FULL_CONFIG,
                    api_key=TEST_API_KEY,
                    base_url=TEST_BASE_URL,
                )
```

### Test Execution Command

```
.venv\Scripts\python -m pytest workflows/gen_media_content_v1/tests/test_video_provider_agnes_v2.py -v
```

Expected result: 21 passed, 0 failed, 0 errors.

---

## 8. Rollback Plan

### If Implementation Fails

Since this task creates only new files and modifies no existing files, rollback is trivial:

1. **Delete new files**: Remove the two created files:
   - `workflows/gen_media_content_v1/api_actions/render_video/agnes_v2/__init__.py`
   - `workflows/gen_media_content_v1/tests/test_video_provider_agnes_v2.py`

2. **Remove empty directory**: Remove the `agnes_v2/` directory if it exists.

3. **Verify clean state**: Run `git status` to confirm no tracked files were modified.

### Partial Failure Scenarios

| Scenario | Action |
|---|---|
| Provider module has syntax errors | Fix syntax, re-run ACT-01 verification |
| Tests fail due to incorrect implementation | Fix provider code to match test expectations |
| Tests fail due to incorrect test mocks | Fix test mocks to match actual provider behavior |
| Import errors | Verify directory structure and __init__.py placement |

---

## 9. Dependencies

### External Dependencies

| Dependency | Version | Purpose | Source |
|---|---|---|---|
| `requests` | Installed in .venv | HTTP client for API calls | Existing dependency |
| `pytest` | Installed in .venv | Test runner | Existing dev dependency |

### Prerequisites

| Prerequisite | Status | Evidence |
|---|---|---|
| Python 3.12+ environment with .venv | Required | AGENTS.md environment setup |
| Project root importable via sys.path | Required | Test file setup adds PROJECT_ROOT to sys.path |
| render_video/ parent directory exists | EXISTS | Verified via glob |
| render_video/__init__.py registry exists | EXISTS | 6 lines, registry docstring |

### No New Dependencies Required

The implementation uses only `requests` (already a project dependency) for HTTP calls and `pytest` (already a dev dependency) for tests. No new packages need to be installed.

---

## 10. Open Questions

None. The task specification is sufficiently detailed to proceed with implementation. All API contracts, payload structures, endpoint URLs, polling parameters, error handling requirements, and test expectations are explicitly defined in TASK-20260815-001-04 and corroborated by the reference files.

### Assumptions Recorded

1. The `requests` library timeout for the submit POST should be 500 seconds, matching the image provider pattern and the config.json.sample `api_timeout` value.
2. The poll GET request should also use a 500-second timeout per attempt.
3. The `image` parameter is passed as-is to the API payload (the orchestrator handles whether it is a URL or local path -- the provider is pure and does not perform file I/O).
4. The poll loop checks for `RequestException` on GET requests and continues polling unless it is the final attempt, matching the reference _process_single_video behavior. On JSON decode errors (ValueError from resp.json()), the poll loop raises RuntimeError on the final attempt as a robustness improvement over the reference implementation.

---

## 11. Challenge Resolution

Challenge document: gen-media-content-video-provider-agnes-CHALLENGE-50-impl.md
Date of resolution: 2026-08-15

### Attack 1: Missing "Cancelled" Status Test
**Evaluation:** Valid
**Resolution:** Added test_poll_cancelled_status_raises_runtime_error to Section 6b test list (item 5) and Section 7 test code (after test_poll_error_status_raises_runtime_error). The test mocks a poll response with status="cancelled" and asserts RuntimeError is raised. Also added ACT-05 description clarification in Section 1 to indicate 3 separate test methods.
**Evidence:** TASK AC-05 (line 136) requires "RuntimeError when poll returns failed/error/cancelled status". Reference actions.py line 370 explicitly handles "cancelled": `elif vid_status in ("failed", "error", "cancelled"):`. Original plan only had tests for "failed" and "error".
**Affected section:** Section 1 (ACT-05 row), Section 6b (test list items 3-5), Section 7 (new test method)

### Attack 2: Incomplete Config Key Validation
**Evaluation:** Already addressed
**Resolution:** No change to validation scope. The TASK (line 67-68) explicitly states: "Check required config keys: model, width, height" -- only 3 keys. The IMPL correctly implements this exact scope. Adding validation for num_frames and frame_rate would be scope expansion beyond the TASK. The config.json.sample always includes all 5 keys (lines 18-22), so in practice the payload construction will not encounter missing keys. The implementation follows the TASK's explicit validation requirements.
**Evidence:** TASK line 67-68: "Check required config keys: model, width, height". config.json.sample lines 18-22 show agnes_v2 section with all 5 keys present. Phase 3 image provider (agnes_v1/__init__.py line 47) also validates only its used keys: model, size.
**Affected section:** None (no change needed)

### Attack 3: Missing Poll Error Handling
**Evaluation:** Valid
**Resolution:** Added explicit design notes in Section 5 STEP-01 and Section 6a provider structure for poll-phase error handling. Added 2 new tests: test_poll_network_error_on_final_attempt_raises_runtime_error (ACT-22) and test_poll_json_decode_error_on_final_attempt_raises_runtime_error (ACT-23). Updated Section 6b test list to include items 20-21. Updated test count throughout from 18 to 21.
**Evidence:** Reference actions.py lines 372-375 catches RequestException during poll GET and continues unless final attempt. Original plan mentioned this pattern in Assumption 4 but had no tests for it. The image provider (agnes_v1/__init__.py lines 74-79) also handles JSON decode errors, establishing a pattern the video provider should follow.
**Affected section:** Section 1 (ACT-22, ACT-23, ACT-11), Section 3, Section 5 STEP-01, Section 5 STEP-02, Section 6a, Section 6b, Section 7, Section 10 Assumption 4

### Attack 4: Missing Config Key "height" Creates Silent Payload Defect
**Evaluation:** Already addressed
**Resolution:** No change needed. This is a downstream consequence of Attack 2. The TASK explicitly limits validation to 3 keys (model, width, height). The config.json.sample always includes height (line 19). The test_correct_submit_payload_structure (ACT-08) verifies height is correctly included when present. If height is absent, the payload construction would raise KeyError, but this scenario is outside the TASK's validation scope and the config will always contain all required keys.
**Evidence:** TASK line 67-68 explicitly lists only 3 validation keys. config.json.sample line 19: `"height": 576`. ACT-08 test asserts `payload["height"] == 576` with a valid config.
**Affected section:** None (no change needed)

### Attack 5: Poll Loop Continues on JSON Decode Error
**Evaluation:** Valid
**Resolution:** Added explicit design note in Section 5 STEP-01 and Section 6a for poll-phase JSON decode error handling. Added test_poll_json_decode_error_on_final_attempt_raises_runtime_error (ACT-23) in Section 6b and Section 7. The provider module is now required to catch ValueError from resp.json() in the poll loop and raise RuntimeError on the final attempt. This is a robustness improvement over the reference implementation (which has the same gap at actions.py line 365).
**Evidence:** Reference actions.py line 365: `status_data = status_resp.json()` with no try/except. Image provider (agnes_v1/__init__.py lines 74-79) catches ValueError from resp.json() and raises RuntimeError, establishing the correct pattern. Original plan had no JSON decode error handling for poll phase.
**Affected section:** Section 1 (ACT-23), Section 5 STEP-01, Section 6a, Section 6b, Section 7

### Attack 6: Missing Test for "Cancelled" Status in ACT-05 (Traceability)
**Evaluation:** Valid
**Resolution:** Same resolution as Attack 1. The test_poll_cancelled_status_raises_runtime_error has been added to the test list and test code. The ACT-05 description in Section 1 now explicitly states "3 separate test methods" to make the traceability clear.
**Evidence:** Section 6b originally listed only 2 tests for ACT-05 (items 3-4). Now lists 3 (items 3-5). The traceability gap between Section 1 (which claimed "failed/error/cancelled") and Section 6b/7 (which only had 2 tests) has been closed.
**Affected section:** Section 1, Section 6b, Section 7

### Attack 7: Timeout Value Assumption Not Verified
**Evaluation:** Already addressed
**Resolution:** No change needed. The 500-second timeout is correctly sourced from config.json.sample line 35: `"api_timeout": 500`. The reference implementation uses `item.api_timeout` (actions.py lines 347, 363, 380) which is populated from `config.get("api_timeout", 500)` (line 446). The timeout applies uniformly to both submit and poll requests in the reference implementation. The plan correctly records this as an assumption (Section 10, items 1-2).
**Evidence:** config.json.sample line 35: `"api_timeout": 500`. Reference actions.py line 446: `api_timeout = config.get("api_timeout", 500)`. Phase 3 image provider (agnes_v1/__init__.py line 68) also uses timeout=500.
**Affected section:** None (no change needed)

### Finding 1: Test Count Discrepancy
**Evaluation:** Already addressed
**Resolution:** The IMPL extends the TASK's 12 AC / 18-test minimum to 21 tests for comprehensive coverage. The additional tests (ACT-13 through ACT-23) are derived from the TASK Step 2 detailed list (lines 71-90) and reference implementation patterns. Section 4 explicitly maps each additional test to its TASK source. ACT-11 has been updated to reflect the new count of 21.
**Evidence:** TASK Step 2 lists 18 specific test items (lines 71-90). The IMPL adds 3 more for robustness (ACT-22 poll network error, ACT-23 poll JSON decode error) and splits ACT-05 into 3 tests. Section 4 Additional Test Coverage table documents the derivation.
**Affected section:** Section 1 (ACT-11), Section 4

### Finding 2: Missing "Cancelled" in Status List
**Evaluation:** Valid
**Resolution:** Same resolution as Attacks 1 and 6. The missing "cancelled" test has been added to Section 6b and Section 7. The design in Section 5 STEP-01 already mentioned "On status in (failed, error, cancelled)" -- the implementation gap was only in the test plan, which has now been corrected.
**Evidence:** Section 6a line 208 (now line 209) mentions "On status in (failed, error, cancelled)". Section 6b and Section 7 now include the test for cancelled status.
**Affected section:** Section 6b, Section 7

### Summary of Changes

- Test count increased from 18 to 21 (3 new tests added)
- New tests: test_poll_cancelled_status_raises_runtime_error, test_poll_network_error_on_final_attempt_raises_runtime_error, test_poll_json_decode_error_on_final_attempt_raises_runtime_error
- New acceptance criteria: ACT-22 (poll network error), ACT-23 (poll JSON decode error)
- Provider design updated to explicitly handle poll-phase RequestException and ValueError
- All test counts updated consistently across Sections 1, 3, 4, 5, 6b, 7
- No changes to validation scope (remains 3 keys per TASK specification)
