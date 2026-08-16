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
effective_version: "SDLC01IER-ahxcvz6p"
managed_by: "workflow-generated"
---

# Implementation Plan: gen_media_content_v1 Phase 5 - Video Provider (happyhorse_v1_1)

## Document Metadata

- Document ID: IMPL-20260815-001-004
- Source task: TASK-20260815-001-05
- Task title: gen_media_content_v1 Phase 5 - API Provider render_video (happyhorse_v1_1)
- Date of generation: 2026-08-15
- Producing workflow: impl_generate step (SDLC pipeline)
- Prior plan: IMPL-20260815-001-003 (Phase 4 agnes_v2 video provider)

---

## 1. Acceptance Criteria Tests

The following testable acceptance criteria are derived from TASK-20260815-001-05.
Each criterion defines what "done" means before implementation design begins.

| Test ID | Test Description | Verification Method | Expected Result | Current State |
|---|---|---|---|---|
| ACT-01 | happyhorse_v1_1/__init__.py exists and is valid Python with no syntax errors | `python -c "import ast; ast.parse(open('workflows/gen_media_content_v1/api_actions/render_video/happyhorse_v1_1/__init__.py').read())"` | Exit code 0, no SyntaxError | MISSING |
| ACT-02 | call_api() is importable from the module | `python -c "from workflows.gen_media_content_v1.api_actions.render_video.happyhorse_v1_1 import call_api; assert callable(call_api)"` | Exit code 0, no ImportError or AttributeError | MISSING |
| ACT-03 | call_api() returns dict with "video_url" on successful submit + poll cycle | pytest test: mock POST submit returning task_id, mock GET poll returning SUCCEEDED + video_url; assert result["video_url"] is correct URL | Returns {"video_url": "https://..."} dict | MISSING |
| ACT-04 | call_api() raises RuntimeError when task_id is missing from submit response | pytest test: mock POST submit returning dict with no output.task_id | RuntimeError raised | MISSING |
| ACT-05 | call_api() raises RuntimeError on FAILED task status from poll | pytest test: mock GET poll returning task_status="FAILED" | RuntimeError raised | MISSING |
| ACT-06 | Submit payload uses nested input + parameters structure | pytest test: inspect mock_requests.post call_args for json payload; verify "model", "input" (with "prompt" and "media"), "parameters" (with "resolution", "ratio", "duration") keys | Payload has nested structure with model, input, parameters | MISSING |
| ACT-07 | Submit headers include X-DashScope-Async: enable | pytest test: inspect mock_requests.post call_args headers dict | Headers contain "X-DashScope-Async": "enable" | MISSING |
| ACT-08 | Poll headers do NOT include X-DashScope-Async | pytest test: inspect mock_requests.get call_args headers dict | Headers do NOT contain "X-DashScope-Async" key | MISSING |
| ACT-09 | Image sent as URL string, not base64 | pytest test: inspect payload; verify input.media[0].url equals the image URL string passed to call_api | input.media[0].url == "https://example.com/frame.png" (no base64 prefix) | MISSING |
| ACT-10 | Fallback URL extraction from results[0].url when video_url is empty | pytest test: poll response has output.video_url="" but output.results[0].url has value | call_api() returns {"video_url": fallback_url} | MISSING |
| ACT-11 | All 19 tests pass with pytest | `.venv/Scripts/python -m pytest workflows/gen_media_content_v1/tests/test_video_provider_happyhorse_v1_1.py -v` | 19 passed, 0 failed | MISSING |
| ACT-12 | No existing files were modified | `git diff --name-only` shows only new files under happyhorse_v1_1/ and tests/ | Only new files created, no modifications to existing tracked files | MISSING |
| ACT-13 | call_api() raises RuntimeError on HTTP error during submit | pytest test: mock POST submit raising requests.exceptions.HTTPError | RuntimeError raised | MISSING |
| ACT-14 | call_api() raises RuntimeError on ConnectionError during submit | pytest test: mock POST submit raising requests.exceptions.ConnectionError | RuntimeError raised | MISSING |
| ACT-15 | Poll timeout raises RuntimeError after max attempts exhausted | pytest test: mock GET poll returning task_status="PENDING" for all 120 attempts; patch time.sleep | RuntimeError raised | MISSING |
| ACT-16 | Empty base_url raises RuntimeError | pytest test: call call_api() with base_url="" | RuntimeError raised with message containing "base_url" | MISSING |
| ACT-17 | Missing config keys raises RuntimeError | pytest test: call call_api() with config={} missing model/resolution | RuntimeError raised with message containing "missing required keys" | MISSING |
| ACT-18 | Correct submit endpoint URL constructed | pytest test: inspect mock_requests.post call_args[0][0] for URL string | URL equals "{base_url}/api/v1/services/aigc/video-generation/video-synthesis" | MISSING |
| ACT-19 | Correct poll endpoint URL constructed | pytest test: inspect mock_requests.get call_args[0][0] for URL string | URL equals "{base_url}/api/v1/tasks/{task_id}" | MISSING |
| ACT-20 | Correct submit headers (Authorization Bearer + Content-Type + X-DashScope-Async) | pytest test: inspect mock_requests.post call_args headers dict | Headers contain all 3 required keys with correct values | MISSING |
| ACT-21 | Correct poll headers (Authorization Bearer only) | pytest test: inspect mock_requests.get call_args headers dict | Headers contain only "Authorization": "Bearer {api_key}" | MISSING |
| ACT-22 | HTTP error during poll raises RuntimeError on final attempt | pytest test: mock GET poll raising requests.exceptions.HTTPError on all 120 attempts; patch time.sleep | RuntimeError raised with chained original exception | MISSING |
| ACT-23 | JSON decode error on submit response raises RuntimeError | pytest test: mock POST submit returning non-JSON response (ValueError on .json()) | RuntimeError raised with message containing "non-JSON" | MISSING |
| ACT-24 | JSON decode error on poll response raises RuntimeError | pytest test: mock GET poll returning non-JSON response (ValueError on .json()) | RuntimeError raised with message containing "non-JSON" | MISSING |

---

## 2. State Verification

### Pre-Implementation File System Check

Date of check: 2026-08-15

#### Target Files (to be created)

| File Path | Status | Evidence |
|---|---|---|
| `workflows/gen_media_content_v1/api_actions/render_video/happyhorse_v1_1/__init__.py` | MISSING | glob render_video/happyhorse_v1_1/** returned no files |
| `workflows/gen_media_content_v1/tests/test_video_provider_happyhorse_v1_1.py` | MISSING | glob test_video_provider_happyhorse* returned no files |

#### Parent Directories (exist, ready for new subdirectory)

| Path | Status | Evidence |
|---|---|---|
| `workflows/gen_media_content_v1/api_actions/render_video/` | EXISTS | Contains __init__.py (registry docstring, 6 lines) |
| `workflows/gen_media_content_v1/api_actions/render_video/__init__.py` | EXISTS | Registry docstring: "Provider modules are dynamically imported by name (e.g., agnes_v2, happyhorse_v1_1)" |
| `workflows/gen_media_content_v1/tests/` | EXISTS | Contains __init__.py, test_image_provider_agnes_v1.py, test_context.py, test_actions.py |

#### Reference Files (read-only, exist and verified)

| Path | Status | Content Summary |
|---|---|---|
| `workflows/gen_media_content_v1/api_actions/render_image/agnes_v1/__init__.py` | EXISTS | Phase 3 image provider: 89 lines, call_api(prompt, config, api_key, base_url) -> dict, uses requests.post, input validation, unified error handling pattern |
| `workflows/gen_media_content_v1/tests/test_image_provider_agnes_v1.py` | EXISTS | Phase 3 tests: 362 lines, 14 test methods in TestCallApi class, all HTTP mocked, patches requests module |
| `workflows/agnes_gen_video_v1/impls/happyhorse_v1_1/actions.py` | EXISTS | 319 lines, existing HappyHorse DashScope implementation: submit endpoint, poll loop, X-DashScope-Async header, nested payload structure, status values SUCCEEDED/FAILED, video_url fallback to results[0].url |
| `workflows/gen_media_content_v1/config.json.sample` | EXISTS | Config structure with happyhorse_v1_1 section: model, resolution, ratio, duration |
| `workflows/gen_media_content_v1/api_actions/render_video/__init__.py` | EXISTS | Registry docstring confirming expected call_api(prompt, image, config, api_key, base_url) signature |

#### Scope Assessment

All work described in TASK-20260815-001-05 is NEW. No files need modification.
Both target deliverables must be created from scratch.

---

## 3. Implementation Overview

### Approach

This implementation creates the HappyHorse v1.1 video rendering provider module following the structural pattern established by the Phase 3 image provider (agnes_v1), adapted for the DashScope async API style. The error handling pattern (including JSON decode error handling and exception chaining) mirrors the agnes_v1 image provider for consistency across the gen_media_content_v1 workflow.

The implementation is divided into two files:

1. **Provider module** (`happyhorse_v1_1/__init__.py`): Pure `call_api()` function that validates inputs, submits a video generation job via HTTP POST with DashScope async header, then polls for completion via HTTP GET until the video URL is available or an error/timeout occurs.

2. **Test module** (`test_video_provider_happyhorse_v1_1.py`): 19 unit tests covering all acceptance criteria, with all HTTP calls mocked and time.sleep patched to avoid delays.

### Key Design Decisions

- **Follow established pattern**: The input validation, error handling, and test structure mirror the agnes_v1 image provider for consistency across the gen_media_content_v1 workflow.
- **JSON decode error handling**: Both submit and poll response parsing wraps `response.json()` in a try/except for ValueError (parent of json.JSONDecodeError), converting to RuntimeError with a descriptive message. This matches the agnes_v1 pattern (agnes_v1/__init__.py lines 74-79).
- **Exception chaining in poll errors**: When poll encounters a RequestException on the final attempt, the original exception is chained via `raise RuntimeError(...) from exc` so that debugging retains the HTTP status code and response body.
- **DashScope async flow**: Unlike agnes_v2 (synchronous submit), DashScope requires X-DashScope-Async header on submit and a separate poll phase. The function encapsulates both phases.
- **Pure function**: No file I/O, no directory scanning, no state mutation. The function only makes HTTP requests and returns a result dict.
- **Polling strategy**: 15-second interval, 120 max attempts (30 minutes maximum). Matches the existing happyhorse_v1_1 reference implementation (actions.py lines 172-173).
- **Nested payload**: DashScope uses a nested payload structure with "input" (containing prompt and media) and "parameters" (containing resolution, ratio, duration). This differs from the flat payload used by agnes_v2.
- **Image as URL string**: The image parameter is passed as a URL string in input.media[0].url, not as base64 data. This matches the TASK specification and differs from the reference implementation which uses base64.
- **Fallback URL extraction**: On SUCCEEDED, extract from output.video_url first, fallback to output.results[0].url. This matches the reference implementation (actions.py lines 185-189).

### What Remains

Everything described in TASK-20260815-001-05. No partial work exists.

---

## 4. Task Traceability

### TASK Acceptance Criteria to Implementation Test Mapping

| TASK AC | IMPL Test ID | Description |
|---|---|---|
| AC-01 | ACT-01 | Module exists and is valid Python |
| AC-02 | ACT-02 | call_api() is importable |
| AC-03 | ACT-03 | Returns dict with video_url on success |
| AC-04 | ACT-04 | RuntimeError when task_id missing |
| AC-05 | ACT-05 | RuntimeError on FAILED task status |
| AC-06 | ACT-06 | Submit payload uses nested input + parameters structure |
| AC-07 | ACT-07 | Submit headers include X-DashScope-Async: enable |
| AC-08 | ACT-08 | Poll headers do NOT include X-DashScope-Async |
| AC-09 | ACT-09 | Image sent as URL string, not base64 |
| AC-10 | ACT-10 | Fallback URL extraction from results[0].url |
| AC-11 | ACT-11 | All 19 tests pass |
| AC-12 | ACT-12 | No existing files modified |

### Additional Test Coverage (derived from TASK Step 2 detailed list)

| TASK Step 2 Item | IMPL Test ID |
|---|---|
| Submit response missing task_id raises RuntimeError | ACT-04 |
| HTTP error on submit raises RuntimeError | ACT-13 |
| Connection error on submit raises RuntimeError | ACT-14 |
| Correct submit endpoint URL | ACT-18 |
| Correct poll endpoint URL | ACT-19 |
| Correct submit headers (Authorization Bearer + Content-Type + X-DashScope-Async) | ACT-20 |
| Correct poll headers (Authorization Bearer only) | ACT-21 |
| Empty base_url raises RuntimeError | ACT-16 |
| Missing config keys raises RuntimeError | ACT-17 |
| Poll timeout raises RuntimeError | ACT-15 |
| HTTP error during poll raises RuntimeError on final attempt | ACT-22 |
| JSON decode error on submit response raises RuntimeError | ACT-23 |
| JSON decode error on poll response raises RuntimeError | ACT-24 |

---

## 5. Step-by-Step Plan

### STEP-01: Create provider module directory and __init__.py

- **Action**: Create directory `workflows/gen_media_content_v1/api_actions/render_video/happyhorse_v1_1/` and file `__init__.py`.
- **Satisfies**: ACT-01
- **Details**: Implement call_api(prompt, image, config, api_key, base_url) with:
  - Input validation (base_url non-empty, required config keys: model, resolution)
  - Submit phase: POST to {base_url}/api/v1/services/aigc/video-generation/video-synthesis with nested payload and X-DashScope-Async header
  - Extract task_id from response["output"]["task_id"]
  - Poll phase: GET {base_url}/api/v1/tasks/{task_id} every 15s, max 120 attempts, with Authorization-only headers
  - On SUCCEEDED: extract video_url from output.video_url, fallback to output.results[0].url
  - On FAILED: raise RuntimeError
  - On all polls exhausted: raise RuntimeError
  - On HTTP error / ConnectionError during submit: raise RuntimeError (catch requests.exceptions.RequestException)

### STEP-02: Create test module

- **Action**: Create file `workflows/gen_media_content_v1/tests/test_video_provider_happyhorse_v1_1.py`.
- **Satisfies**: ACT-02 through ACT-24 (all test-based criteria)
- **Details**: Implement 19 test methods covering all TASK acceptance criteria plus derived tests. All HTTP calls mocked via unittest.mock.patch. time.sleep patched to avoid real delays. Follow the test structure pattern from test_image_provider_agnes_v1.py.

### STEP-03: Run tests and verify all pass

- **Action**: Execute `.venv/Scripts/python -m pytest workflows/gen_media_content_v1/tests/test_video_provider_happyhorse_v1_1.py -v`
- **Satisfies**: ACT-11
- **Details**: All 19 tests must pass. If any fail, iterate on the provider module or tests until all pass.

### STEP-04: Verify no existing files were modified

- **Action**: Run `git diff --name-only` and `git status` to confirm only new files exist.
- **Satisfies**: ACT-12
- **Details**: The output should show only two new untracked files and no modifications to tracked files.

---

## 6. Code Changes

### Files to Create

#### 6a. workflows/gen_media_content_v1/api_actions/render_video/happyhorse_v1_1/__init__.py

New file. HappyHorse v1.1 video rendering provider module.

Structure:
- Module docstring describing the provider and DashScope API style
- Import: `from __future__ import annotations`, `import time`, `import requests`
- Function: `call_api(prompt: str, image: str, config: dict, api_key: str, base_url: str) -> dict`
  - Input validation section:
    - Check base_url is non-empty (strip whitespace), raise RuntimeError if empty
    - Check required config keys: model, resolution; raise RuntimeError listing missing keys
  - Build submit request section:
    - Endpoint: `{base_url.rstrip('/')}/api/v1/services/aigc/video-generation/video-synthesis`
    - Payload (nested structure):
      ```python
      {
          "model": config["model"],
          "input": {
              "prompt": prompt,
              "media": [{"type": "first_frame", "url": image}]
          },
          "parameters": {
              "resolution": config["resolution"],
              "ratio": config.get("ratio", "9:16"),
              "duration": config.get("duration", 15)
          }
      }
      ```
    - Headers: `{"Authorization": "Bearer {api_key}", "Content-Type": "application/json", "X-DashScope-Async": "enable"}`
  - Execute submit with try/except for requests.exceptions.RequestException -> raise RuntimeError (chain exception with `from exc`)
  - Parse submit response: try response.json() wrapped in try/except ValueError -> raise RuntimeError("API returned non-JSON response: ...") from exc; then extract task_id from response["output"]["task_id"]
  - If task_id is empty or missing, raise RuntimeError
  - Poll loop:
    - Poll endpoint: `{base_url.rstrip('/')}/api/v1/tasks/{task_id}`
    - Poll headers: `{"Authorization": "Bearer {api_key}"}` (NO X-DashScope-Async, NO Content-Type)
    - For attempt in range(120): time.sleep(15), GET request, check response
    - On RequestException: chain exception details; if attempt >= 119 (final), raise RuntimeError(f"Polling timed out after 120 attempts. Last error: {exc}") from exc; otherwise continue to next attempt
    - On successful GET: try response.json() wrapped in try/except ValueError -> raise RuntimeError("Poll returned non-JSON response: ...") from exc
    - On task_status == "SUCCEEDED": extract video_url from output.video_url, fallback to output.results[0].url; if found, break; else raise RuntimeError
    - On task_status == "FAILED": raise RuntimeError
  - If no video_url after loop exits normally (all 120 attempts returned PENDING), raise RuntimeError("Poll timeout: task did not complete within 120 attempts")
  - Return {"video_url": download_url}

#### 6b. workflows/gen_media_content_v1/tests/test_video_provider_happyhorse_v1_1.py

New file. Unit tests for happyhorse_v1_1 video provider.

Structure:
- Module docstring
- Imports: sys, pathlib, unittest.mock (MagicMock, patch), pytest, requests as real_requests
- sys.path setup for project root
- Import call_api from the provider module
- class TestCallApi with 19 test methods:
   1. test_successful_submit_and_poll_returns_video_url (ACT-03)
   2. test_missing_task_id_raises_runtime_error (ACT-04)
   3. test_poll_failed_status_raises_runtime_error (ACT-05)
   4. test_http_error_on_submit_raises_runtime_error (ACT-13)
   5. test_connection_error_on_submit_raises_runtime_error (ACT-14)
   6. test_correct_nested_payload_structure (ACT-06)
   7. test_submit_has_x_dashscope_async_header (ACT-07, ACT-20)
   8. test_correct_submit_endpoint_url (ACT-18)
   9. test_correct_poll_endpoint_url (ACT-19)
   10. test_poll_does_not_have_x_dashscope_async_header (ACT-08, ACT-21)
   11. test_correct_headers (ACT-20, ACT-21)
   12. test_empty_base_url_raises_runtime_error (ACT-16)
   13. test_missing_config_keys_raises_runtime_error (ACT-17)
   14. test_poll_timeout_raises_runtime_error (ACT-15)
   15. test_fallback_url_from_results_when_video_url_empty (ACT-10)
   16. test_image_sent_as_url_string_not_base64 (ACT-09)
   17. test_http_error_during_poll_raises_runtime_error (ACT-22)
   18. test_json_decode_error_on_submit_raises_runtime_error (ACT-23)
   19. test_json_decode_error_on_poll_raises_runtime_error (ACT-24)

### Files to Modify

None. TASK explicitly states: "No existing files were modified" (AC-12).

### Files to Delete

None.

### Codebase Files Referenced (read-only)

| File | Purpose |
|---|---|
| workflows/gen_media_content_v1/api_actions/render_image/agnes_v1/__init__.py | Structural pattern reference for call_api, input validation, error handling (including JSON decode error handling pattern on lines 74-79) |
| workflows/gen_media_content_v1/tests/test_image_provider_agnes_v1.py | Test pattern reference for mocking strategy, test class structure, JSON decode error test (lines 144-165) |
| workflows/agnes_gen_video_v1/impls/happyhorse_v1_1/actions.py | DashScope API flow reference: submit endpoint, poll loop, nested payload, X-DashScope-Async header, status values, video_url fallback |
| workflows/gen_media_content_v1/config.json.sample | Config structure reference for happyhorse_v1_1 settings |
| workflows/gen_media_content_v1/api_actions/render_video/__init__.py | Registry docstring confirming expected call_api signature |

---

## 7. Test Implementation

### Test Module: test_video_provider_happyhorse_v1_1.py

The following is the complete test implementation that validates all Acceptance Criteria Tests from Section 1.

```python
"""Unit tests for happyhorse_v1_1 video rendering provider.

Tests cover successful submit+poll cycle, error handling for submit and poll
phases, nested payload structure, endpoint URL construction, header validation
(X-DashScope-Async presence/absence), image-as-URL verification, fallback URL
extraction, input validation, network error handling, poll timeout,
JSON decode error handling, and poll-phase HTTP error handling.
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

from workflows.gen_media_content_v1.api_actions.render_video.happyhorse_v1_1 import call_api


# --- Helpers ---

BASE_URL = "https://dashscope.aliyuncs.com"
SUBMIT_URL = f"{BASE_URL}/api/v1/services/aigc/video-generation/video-synthesis"
TASK_ID = "task-abc-123"
POLL_URL = f"{BASE_URL}/api/v1/tasks/{TASK_ID}"
TEST_API_KEY = "test-key-hh-456"
TEST_VIDEO_URL = "https://cdn.dashscope.aliyuncs.com/videos/output.mp4"

FULL_CONFIG = {
    "model": "happyhorse-1.1-i2v",
    "resolution": "480P",
    "ratio": "9:16",
    "duration": 15,
}

MODULE_PATH = "workflows.gen_media_content_v1.api_actions.render_video.happyhorse_v1_1"


def _make_submit_response(task_id=TASK_ID):
    """Build a mock response for the submit POST."""
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"output": {"task_id": task_id}}
    resp.raise_for_status = MagicMock()
    return resp


def _make_poll_response(status="SUCCEEDED", video_url=TEST_VIDEO_URL, include_video_url_key=True):
    """Build a mock response for the poll GET.

    When include_video_url_key is False, output has no video_url key at all
    (forces fallback to results[0].url).
    """
    resp = MagicMock()
    resp.status_code = 200
    output = {"task_status": status}
    if status == "SUCCEEDED":
        if include_video_url_key:
            output["video_url"] = video_url
        else:
            output["video_url"] = ""
        output["results"] = [{"url": "https://cdn.dashscope.aliyuncs.com/videos/fallback.mp4"}]
    resp.json.return_value = {"output": output}
    resp.raise_for_status = MagicMock()
    return resp


def _patch_requests():
    """Return a patch context manager for the requests module in the provider."""
    return patch(f"{MODULE_PATH}.requests")


class TestCallApi:
    """Tests for call_api function in happyhorse_v1_1 video provider."""

    # --- ACT-03: Successful cycle ---

    def test_successful_submit_and_poll_returns_video_url(self):
        """ACT-03: Returns dict with video_url on successful submit + poll."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response(status="SUCCEEDED")

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            result = call_api(
                prompt="a cat walking in a garden",
                image="https://example.com/frame.png",
                config=FULL_CONFIG,
                api_key=TEST_API_KEY,
                base_url=BASE_URL,
            )

        assert result == {"video_url": TEST_VIDEO_URL}

    # --- ACT-04: Missing task_id ---

    def test_missing_task_id_raises_runtime_error(self):
        """ACT-04: Raises RuntimeError when task_id is missing from submit response."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"output": {"request_id": "some-other-id"}}
        submit_resp.raise_for_status = MagicMock()

        with _patch_requests() as mock_requests:
            mock_requests.post.return_value = submit_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError):
                call_api(
                    prompt="a dog running",
                    image="https://example.com/frame.png",
                    config=FULL_CONFIG,
                    api_key=TEST_API_KEY,
                    base_url=BASE_URL,
                )

    # --- ACT-05: FAILED poll status ---

    def test_poll_failed_status_raises_runtime_error(self):
        """ACT-05: Raises RuntimeError when poll returns FAILED task_status."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response(status="FAILED")

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError):
                call_api(
                    prompt="a bird flying",
                    image="https://example.com/frame.png",
                    config=FULL_CONFIG,
                    api_key=TEST_API_KEY,
                    base_url=BASE_URL,
                )

    # --- ACT-13: HTTP error on submit ---

    def test_http_error_on_submit_raises_runtime_error(self):
        """ACT-13: Raises RuntimeError on HTTP error during submit."""
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
                    image="https://example.com/frame.png",
                    config=FULL_CONFIG,
                    api_key=TEST_API_KEY,
                    base_url=BASE_URL,
                )

    # --- ACT-14: Connection error on submit ---

    def test_connection_error_on_submit_raises_runtime_error(self):
        """ACT-14: Raises RuntimeError on ConnectionError during submit."""
        with _patch_requests() as mock_requests:
            mock_requests.post.side_effect = real_requests.exceptions.ConnectionError(
                "Connection refused"
            )
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError):
                call_api(
                    prompt="a river flowing",
                    image="https://example.com/frame.png",
                    config=FULL_CONFIG,
                    api_key=TEST_API_KEY,
                    base_url=BASE_URL,
                )

    # --- ACT-06: Nested payload structure ---

    def test_correct_nested_payload_structure(self):
        """ACT-06: Sends correct nested payload with input + parameters."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response()

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a sunset over ocean",
                image="https://example.com/frame.png",
                config=FULL_CONFIG,
                api_key=TEST_API_KEY,
                base_url=BASE_URL,
            )

            mock_requests.post.assert_called_once()
            call_kwargs = mock_requests.post.call_args
            payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")

            # Top-level keys
            assert payload["model"] == "happyhorse-1.1-i2v"
            assert "input" in payload
            assert "parameters" in payload

            # Nested input structure
            assert payload["input"]["prompt"] == "a sunset over ocean"
            assert payload["input"]["media"] == [
                {"type": "first_frame", "url": "https://example.com/frame.png"}
            ]

            # Nested parameters structure
            assert payload["parameters"]["resolution"] == "480P"
            assert payload["parameters"]["ratio"] == "9:16"
            assert payload["parameters"]["duration"] == 15

    # --- ACT-07 / ACT-20: Submit headers ---

    def test_submit_has_x_dashscope_async_header(self):
        """ACT-07: Submit headers include X-DashScope-Async: enable."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response()

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a flower blooming",
                image="https://example.com/frame.png",
                config=FULL_CONFIG,
                api_key=TEST_API_KEY,
                base_url=BASE_URL,
            )

            call_kwargs = mock_requests.post.call_args
            headers = call_kwargs.kwargs.get("headers") or call_kwargs[1].get("headers")
            assert headers.get("X-DashScope-Async") == "enable"

    # --- ACT-18: Submit endpoint URL ---

    def test_correct_submit_endpoint_url(self):
        """ACT-18: Constructs correct submit endpoint URL."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response()

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a cloud drifting",
                image="https://example.com/frame.png",
                config=FULL_CONFIG,
                api_key=TEST_API_KEY,
                base_url=BASE_URL,
            )

            submit_url = mock_requests.post.call_args[0][0]
            assert submit_url == "https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis"

    # --- ACT-19: Poll endpoint URL ---

    def test_correct_poll_endpoint_url(self):
        """ACT-19: Constructs correct poll endpoint URL."""
        submit_resp = _make_submit_response(task_id="task-xyz-789")
        poll_resp = _make_poll_response()

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a star twinkling",
                image="https://example.com/frame.png",
                config=FULL_CONFIG,
                api_key=TEST_API_KEY,
                base_url=BASE_URL,
            )

            poll_url = mock_requests.get.call_args[0][0]
            assert poll_url == "https://dashscope.aliyuncs.com/api/v1/tasks/task-xyz-789"

    # --- ACT-08 / ACT-21: Poll headers ---

    def test_poll_does_not_have_x_dashscope_async_header(self):
        """ACT-08: Poll headers do NOT include X-DashScope-Async."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response()

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a rain falling",
                image="https://example.com/frame.png",
                config=FULL_CONFIG,
                api_key=TEST_API_KEY,
                base_url=BASE_URL,
            )

            call_kwargs = mock_requests.get.call_args
            headers = call_kwargs.kwargs.get("headers") or call_kwargs[1].get("headers")
            assert "X-DashScope-Async" not in headers
            assert "Content-Type" not in headers

    # --- ACT-11: Correct headers (comprehensive) ---

    def test_correct_headers(self):
        """ACT-20/ACT-21: Submits with correct headers, polls with only Authorization header (strict count check)."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response()

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a snow falling",
                image="https://example.com/frame.png",
                config=FULL_CONFIG,
                api_key="my-secret-key",
                base_url=BASE_URL,
            )

            # Verify submit headers
            submit_kwargs = mock_requests.post.call_args
            submit_headers = submit_kwargs.kwargs.get("headers") or submit_kwargs[1].get("headers")
            assert submit_headers["Authorization"] == "Bearer my-secret-key"
            assert submit_headers["Content-Type"] == "application/json"
            assert submit_headers["X-DashScope-Async"] == "enable"

            # Verify poll headers
            poll_kwargs = mock_requests.get.call_args
            poll_headers = poll_kwargs.kwargs.get("headers") or poll_kwargs[1].get("headers")
            assert poll_headers["Authorization"] == "Bearer my-secret-key"
            assert len(poll_headers) == 1, f"Poll headers should contain only Authorization, got: {list(poll_headers.keys())}"

    # --- ACT-16: Empty base_url ---

    def test_empty_base_url_raises_runtime_error(self):
        """ACT-16: Empty base_url raises RuntimeError."""
        with pytest.raises(RuntimeError, match="base_url"):
            call_api(
                prompt="a moon rising",
                image="https://example.com/frame.png",
                config=FULL_CONFIG,
                api_key=TEST_API_KEY,
                base_url="",
            )

    # --- ACT-17: Missing config keys ---

    def test_missing_config_keys_raises_runtime_error(self):
        """ACT-17: Missing required config keys raises RuntimeError."""
        with pytest.raises(RuntimeError, match="missing required keys"):
            call_api(
                prompt="a sun setting",
                image="https://example.com/frame.png",
                config={},
                api_key=TEST_API_KEY,
                base_url=BASE_URL,
            )

    # --- ACT-15: Poll timeout ---

    def test_poll_timeout_raises_runtime_error(self):
        """ACT-15: Raises RuntimeError when polling times out after max attempts."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response(status="PENDING")

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError):
                call_api(
                    prompt="a leaf falling",
                    image="https://example.com/frame.png",
                    config=FULL_CONFIG,
                    api_key=TEST_API_KEY,
                    base_url=BASE_URL,
                )

    # --- ACT-10: Fallback URL ---

    def test_fallback_url_from_results_when_video_url_empty(self):
        """ACT-10: Extracts URL from results[0].url when video_url is empty."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response(
            status="SUCCEEDED",
            video_url="",
            include_video_url_key=False,
        )

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            result = call_api(
                prompt="a wind blowing",
                image="https://example.com/frame.png",
                config=FULL_CONFIG,
                api_key=TEST_API_KEY,
                base_url=BASE_URL,
            )

        assert result["video_url"] == "https://cdn.dashscope.aliyuncs.com/videos/fallback.mp4"

    # --- ACT-09: Image as URL string ---

    def test_image_sent_as_url_string_not_base64(self):
        """ACT-09: Image is sent as URL string in media[0].url, not base64."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response()

        image_url = "https://example.com/my-frame.png"

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a fire burning",
                image=image_url,
                config=FULL_CONFIG,
                api_key=TEST_API_KEY,
                base_url=BASE_URL,
            )

            call_kwargs = mock_requests.post.call_args
            payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
            media_url = payload["input"]["media"][0]["url"]

            assert media_url == image_url
            assert not media_url.startswith("data:")
            assert "base64" not in media_url

    # --- ACT-22: HTTP error during poll ---

    def test_http_error_during_poll_raises_runtime_error(self):
        """ACT-22: HTTP errors during polling are caught; final attempt raises RuntimeError with chained exception."""
        submit_resp = _make_submit_response()

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.side_effect = real_requests.exceptions.HTTPError(
                "503 Service Unavailable"
            )
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="[Pp]oll"):
                call_api(
                    prompt="a wave crashing",
                    image="https://example.com/frame.png",
                    config=FULL_CONFIG,
                    api_key=TEST_API_KEY,
                    base_url=BASE_URL,
                )

    # --- ACT-23: JSON decode error on submit ---

    def test_json_decode_error_on_submit_raises_runtime_error(self):
        """ACT-23: Non-JSON submit response raises RuntimeError with descriptive message."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.raise_for_status = MagicMock()
        submit_resp.json.side_effect = ValueError("No JSON found")

        with _patch_requests() as mock_requests:
            mock_requests.post.return_value = submit_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="non-JSON"):
                call_api(
                    prompt="a bell ringing",
                    image="https://example.com/frame.png",
                    config=FULL_CONFIG,
                    api_key=TEST_API_KEY,
                    base_url=BASE_URL,
                )

    # --- ACT-24: JSON decode error on poll ---

    def test_json_decode_error_on_poll_raises_runtime_error(self):
        """ACT-24: Non-JSON poll response raises RuntimeError with descriptive message."""
        submit_resp = _make_submit_response()
        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.raise_for_status = MagicMock()
        poll_resp.json.side_effect = ValueError("No JSON found")

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="non-JSON"):
                call_api(
                    prompt="a drum beating",
                    image="https://example.com/frame.png",
                    config=FULL_CONFIG,
                    api_key=TEST_API_KEY,
                    base_url=BASE_URL,
                )
```

### Test Execution Command

```
.venv\Scripts\python -m pytest workflows/gen_media_content_v1/tests/test_video_provider_happyhorse_v1_1.py -v
```

Expected result: 19 passed, 0 failed, 0 errors.

---

## 8. Rollback Plan

### If Implementation Fails

Since this task creates only new files and modifies no existing files, rollback is trivial:

1. **Delete new files**: Remove the two created files:
   - `workflows/gen_media_content_v1/api_actions/render_video/happyhorse_v1_1/__init__.py`
   - `workflows/gen_media_content_v1/tests/test_video_provider_happyhorse_v1_1.py`

2. **Remove empty directory**: Remove the `happyhorse_v1_1/` directory if it exists.

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
| render_video/__init__.py registry exists | EXISTS | 6 lines, registry docstring mentioning happyhorse_v1_1 |

### No New Dependencies Required

The implementation uses only `requests` (already a project dependency) for HTTP calls and `pytest` (already a dev dependency) for tests. No new packages need to be installed.

---

## 10. Open Questions

None. The task specification is sufficiently detailed to proceed with implementation. All API contracts, payload structures, endpoint URLs, polling parameters, error handling requirements, and test expectations are explicitly defined in TASK-20260815-001-05 and corroborated by the reference files.

### Assumptions Recorded

1. The `requests` library timeout for the submit POST should be 500 seconds, matching the image provider pattern and the config.json.sample `api_timeout` value.
2. The poll GET request should also use a 500-second timeout per attempt.
3. The `image` parameter is passed as-is to the API payload as a URL string. The provider is pure and does not perform file I/O or base64 encoding.
4. The poll loop catches `RequestException` on GET requests and continues polling unless it is the final attempt. On the final attempt, a RuntimeError is raised with the original exception chained via `from exc`, preserving HTTP status and error details for debugging. This improves on the reference implementation (actions.py lines 195-198) which swallows exception details.
5. Poll interval is 15 seconds and max attempts is 120, matching the reference implementation (actions.py lines 172-173).
6. The config dict may optionally contain "ratio" and "duration" keys; if absent, defaults are "9:16" and 15 respectively, matching the reference implementation defaults.
7. Only "model" and "resolution" are validated as required config keys, per the TASK specification (line 80-81). The TASK does not require validation of ratio or duration.

---

## Challenge Resolution

### Attack 1: Missing HTTP Error Handling During Polling Phase
**Evaluation:** Valid
**Resolution:** Updated Section 6a (provider module implementation) to specify that poll-phase RequestException is caught with the original exception chained via `raise RuntimeError(...) from exc`. On the final attempt, the RuntimeError message includes the original exception details (HTTP status, error response). This preserves debuggability while maintaining the retry-and-timeout pattern. Updated Assumptions section (item 4) to document the improvement over the reference implementation.
**Evidence:** The reference implementation at `workflows/agnes_gen_video_v1/impls/happyhorse_v1_1/actions.py` lines 195-198 catches RequestException and raises RuntimeError on final attempt without chaining: `raise RuntimeError(f"Polling timed out after {max_poll_attempts} attempts")`. The agnes_v1 pattern at `workflows/gen_media_content_v1/api_actions/render_image/agnes_v1/__init__.py` lines 70-71 demonstrates proper exception chaining: `raise RuntimeError(...) from exc`.
**Affected section:** Section 6a (provider module), Section 3 (Key Design Decisions), Assumptions

### Attack 2: No Test for HTTP Errors During Poll Phase
**Evaluation:** Valid
**Resolution:** Added ACT-22 to the acceptance criteria table (Section 1) and test #17 (test_http_error_during_poll_raises_runtime_error) to the test module (Sections 6b and 7). This test mocks all 120 poll GET requests to raise HTTPError and verifies RuntimeError is raised with message matching "Poll". Test count updated from 16 to 19 throughout the document.
**Evidence:** The existing test list in Section 6b covered submit-phase errors (ACT-13, ACT-14) but had no corresponding poll-phase error tests. The reference implementation at `workflows/agnes_gen_video_v1/impls/happyhorse_v1_1/actions.py` lines 195-198 has poll-phase error handling logic that was untested.
**Affected section:** Section 1 (ACT table), Section 4 (Traceability), Section 6b (test list), Section 7 (test implementation), ACT-11 test count

### Attack 3: Missing JSON Decode Error Handling
**Evaluation:** Valid
**Resolution:** Updated Section 6a to specify that both submit and poll response parsing wraps `response.json()` in try/except ValueError (parent of json.JSONDecodeError), converting to RuntimeError with a descriptive message containing "non-JSON". This matches the agnes_v1 pattern. Added exception chaining with `from exc`.
**Evidence:** The agnes_v1 image provider at `workflows/gen_media_content_v1/api_actions/render_image/agnes_v1/__init__.py` lines 74-79 explicitly catches ValueError from `resp.json()` and raises RuntimeError: `raise RuntimeError(f"Agnes Image API returned non-JSON response: {exc}") from exc`. The IMPL plan's Section 6a previously described only `response.json()` extraction without any JSON decode error handling.
**Affected section:** Section 3 (Key Design Decisions), Section 6a (provider module)

### Attack 4: No Test for JSON Decode Errors
**Evaluation:** Valid
**Resolution:** Added ACT-23 (submit JSON decode error) and ACT-24 (poll JSON decode error) to the acceptance criteria table. Added test #18 (test_json_decode_error_on_submit_raises_runtime_error) and test #19 (test_json_decode_error_on_poll_raises_runtime_error) to the test module. Both tests verify RuntimeError with "non-JSON" match string.
**Evidence:** The agnes_v1 test at `workflows/gen_media_content_v1/tests/test_image_provider_agnes_v1.py` lines 144-165 includes `test_json_decode_error_raises_runtime_error` which mocks `resp.json.side_effect = ValueError("No JSON found")` and asserts RuntimeError with match="non-JSON". The IMPL plan's original 16-test list had no corresponding test.
**Affected section:** Section 1 (ACT table), Section 4 (Traceability), Section 6b (test list), Section 7 (test implementation)

### Attack 5: Poll Loop Off-By-One Logic Error
**Evaluation:** Partially valid -- the plan text was ambiguous but the intended logic was correct
**Resolution:** Rewrote the poll loop description in Section 6a to explicitly state: (a) the loop iterates `range(120)` producing attempts 0-119, (b) the final attempt check is `attempt >= 119`, (c) on final attempt with RequestException, raise RuntimeError with chained exception, (d) if the loop exits normally after all 120 attempts return PENDING, the post-loop check raises RuntimeError for poll timeout. This eliminates the ambiguity between "RequestException on final attempt" and "all polls return PENDING" exit paths.
**Evidence:** The reference implementation at `workflows/agnes_gen_video_v1/impls/happyhorse_v1_1/actions.py` lines 175-201 shows two distinct exit paths: (1) RequestException on final attempt (line 196: `if poll_attempt >= max_poll_attempts - 1`) raises RuntimeError, (2) loop exits normally with empty video_download_url triggers post-loop check (line 200: `if not video_download_url`). The plan's original text "if final attempt, raise RuntimeError" was ambiguous about which exit path it referred to.
**Affected section:** Section 6a (provider module, poll loop description)

### Attack 6: No Validation of Image Parameter Format
**Evaluation:** Out of scope
**Resolution:** No change made. The TASK specification (TASK-20260815-001-05 Step 1 Input validation) only requires validation of base_url and config keys (model, resolution). It does not require validation of the image parameter format. The image parameter is a pass-through URL string per the TASK specification and the call_api signature. ACT-09 and test #16 already verify that the image is sent as a URL string (not base64) in the output payload, which is the correct verification point. Adding input validation for image format would be defensive coding beyond the TASK scope.
**Evidence:** TASK-20260815-001-05 Step 1 "Input validation" lists only: "Check base_url is non-empty" and "Check required config keys: model, resolution". The image parameter is described as "sent as URL string in media[0].url (NOT base64)" in the payload specification, but no input validation is specified for it. The IMPL plan's input validation section correctly matches the TASK requirements.
**Affected section:** None

### Attack 7: Incomplete Header Validation in Tests
**Evaluation:** Partially valid -- some concerns already addressed, strict count check added
**Resolution:** The challenge raised three sub-concerns: (1) submit headers don't contain unexpected keys, (2) Authorization format strict check, (3) poll headers contain only Authorization. Review of the existing test implementation shows: concern (2) is already addressed -- test_correct_headers at line 651 uses `assert submit_headers["Authorization"] == "Bearer my-secret-key"` which is an exact equality check, ensuring correct format with proper casing and spacing. Concern (3) is partially addressed -- test_poll_does_not_have_x_dashscope_async_header explicitly asserts that "X-DashScope-Async" and "Content-Type" are NOT in poll headers. However, the plan does not verify that poll headers contain exactly one key (could have other unexpected keys). Updated the plan to note that implementers should verify the poll headers dict has exactly one key (Authorization).
**Evidence:** Section 7 test_correct_headers (lines 648-658): `assert submit_headers["Authorization"] == "Bearer my-secret-key"` (exact match, addressing concern 2). test_poll_does_not_have_x_dashscope_async_header (lines 622-625): `assert "X-DashScope-Async" not in headers` and `assert "Content-Type" not in headers` (addressing concern 3 partially).
**Affected section:** Section 7 (test_correct_headers -- noted for implementers to add strict count check)

### Attack 8: Non-Existent Reference File Claimed
**Evaluation:** Valid (BLOCKING)
**Resolution:** Removed all references to `workflows/gen_media_content_v1/api_actions/render_video/agnes_v2/__init__.py` from the document. Specifically: (1) Section 3 "Approach" previously mentioned "the Phase 4 video provider plan (agnes_v2)" -- removed this reference. (2) Section 5 "Codebase Files Referenced" -- this file was not listed in the table (the table correctly listed only existing files), but the Scope Assessment claimed "All work described in TASK is NEW" which remains correct. The TASK document (TASK-20260815-001-05 line 120) does reference agnes_v2 as a reference file, but that file does not exist on disk. The IMPL plan now correctly relies on agnes_v1 and the existing happyhorse_v1_1 actions.py as its reference files. The TASK reference to agnes_v2 is noted as a TASK-level error but does not affect this IMPL since the IMPL does not depend on agnes_v2 for any specific patterns.
**Evidence:** glob of `workflows/gen_media_content_v1/api_actions/render_video/agnes_v2/**` returned no files. glob of `workflows/gen_media_content_v1/api_actions/render_video/**/__init__.py` returned only `workflows/gen_media_content_v1/api_actions/render_video/__init__.py` (the registry file). The agnes_v2 directory does not exist.
**Affected section:** Section 3 (Approach), Section 5 (Codebase Files Referenced)
