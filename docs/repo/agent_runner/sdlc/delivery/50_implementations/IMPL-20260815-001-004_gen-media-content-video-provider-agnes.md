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
effective_version: "20260815-sdlc_01_impl_exec_review_v1"
managed_by: "workflow-generated"
---

# Implementation Plan: gen_media_content_v1 Phase 4 - API Provider render_video (agnes_v2)

## Document Metadata

- Document ID: IMPL-20260815-001-004
- Source task: TASK-20260815-001-04
- Task backlog reference: WI-20260814-001 (gen_media_content_v1 workflow)
- Task IDs covered: WI-20260814-001-04
- Date of generation: 2026-08-15
- Prior implementation: IMPL-20260815-001-03 (Phase 3 image provider -- completed)

---

## 1. Acceptance Criteria Tests

The following acceptance criteria tests define what "done" means before any implementation is performed. Each test is derived from the approved task specification (TASK-20260815-001-04).

| Test ID | Test Description | Verification Method | Expected Result | Current State |
|---------|-----------------|-------------------|-----------------|---------------|
| ACT-01 | Successful submit + poll cycle returns video_url | Unit test: mock POST submit returning video_id, mock GET poll returning status=completed with url, assert result contains video_url | call_api() returns {"video_url": "<url>"} with a valid URL string | MISSING |
| ACT-02 | Submit response missing video_id raises RuntimeError | Unit test: mock POST submit returning empty dict (no video_id or id), assert RuntimeError | RuntimeError raised with message referencing missing video_id | MISSING |
| ACT-03 | Poll returns "failed" status raises RuntimeError | Unit test: mock POST submit returning valid video_id, mock GET poll returning status="failed", assert RuntimeError | RuntimeError raised with message referencing failed status | MISSING |
| ACT-04 | Poll returns "error" status raises RuntimeError | Unit test: mock POST submit returning valid video_id, mock GET poll returning status="error", assert RuntimeError | RuntimeError raised with message referencing error status | MISSING |
| ACT-05 | HTTP error on submit raises RuntimeError | Unit test: mock POST submit raising requests.exceptions.HTTPError, assert RuntimeError | RuntimeError raised with message referencing request failure | MISSING |
| ACT-06 | Connection error on submit raises RuntimeError | Unit test: mock POST submit raising requests.exceptions.ConnectionError, assert RuntimeError | RuntimeError raised with message containing "request failed" | MISSING |
| ACT-07 | Timeout error on submit raises RuntimeError | Unit test: mock POST submit raising requests.exceptions.Timeout, assert RuntimeError | RuntimeError raised with message containing "request failed" | MISSING |
| ACT-08 | Correct submit payload structure | Unit test: inspect mock POST call args, assert payload contains model, prompt, image, width, height, num_frames, frame_rate keys with correct values | All 7 required payload fields present with correct values | MISSING |
| ACT-09 | negative_prompt included when present in config | Unit test: config with negative_prompt key, inspect payload, assert negative_prompt present | payload["negative_prompt"] matches config value | MISSING |
| ACT-10 | negative_prompt omitted when absent from config | Unit test: config without negative_prompt key, inspect payload, assert negative_prompt NOT in payload | "negative_prompt" key absent from payload dict | MISSING |
| ACT-11 | Correct submit endpoint URL | Unit test: inspect mock POST call URL, assert equals {base_url}/v1/videos | URL == "https://apihub.agnes-ai.com/v1/videos" | MISSING |
| ACT-12 | Correct poll endpoint URL | Unit test: inspect mock GET call URL, assert equals {base_url}/agnesapi?video_id={id} | URL contains "/agnesapi?video_id=" with the correct video_id value | MISSING |
| ACT-13 | Correct headers (Authorization Bearer + Content-Type) | Unit test: inspect both POST and GET call args headers | Both calls include {"Authorization": "Bearer <key>"}; POST includes "Content-Type": "application/json" | MISSING |
| ACT-14 | Empty base_url raises RuntimeError | Unit test: call call_api() with base_url="", assert RuntimeError | RuntimeError raised with message referencing "base_url" | MISSING |
| ACT-15 | Missing config keys raises RuntimeError | Unit test: call call_api() with config={}, assert RuntimeError | RuntimeError raised with message referencing "missing required keys" | MISSING |
| ACT-16 | Poll timeout after max attempts raises RuntimeError | Unit test: mock POST submit returning valid video_id, mock GET poll always returning status="processing", patch time.sleep, assert RuntimeError after 120 attempts | RuntimeError raised referencing polling timeout | MISSING |
| ACT-17 | video_id extracted from "id" field (fallback) | Unit test: mock POST submit returning {"id": "vid-123"} (no video_id key), assert poll URL uses "vid-123" | Poll request URL contains video_id=vid-123 | MISSING |
| ACT-18 | video_url extracted from "video_url" field (fallback) | Unit test: mock poll returning {"status": "completed", "video_url": "https://..."} (no url key), assert result contains video_url | result["video_url"] == "https://..." | MISSING |
| ACT-19 | Poll returns "cancelled" status raises RuntimeError | Unit test: mock POST submit returning valid video_id, mock GET poll returning status="cancelled", assert RuntimeError | RuntimeError raised with message referencing cancelled status | MISSING |
| ACT-20 | HTTP error during polling does not crash (continues loop, eventually times out) | Unit test: mock POST submit returning valid video_id, mock GET poll raising requests.exceptions.HTTPError on every call, patch time.sleep, assert RuntimeError after max attempts | RuntimeError raised referencing polling timeout (not unhandled HTTPError) | MISSING |
| ACT-21 | Completed poll response missing both url and video_url raises RuntimeError | Unit test: mock POST submit returning valid video_id, mock GET poll returning {"status": "completed"} (no url keys), assert RuntimeError | RuntimeError raised referencing missing video URL | MISSING |

---

## 2. State Verification

### Pre-Implementation File System Check

The following paths were verified on 2026-08-15 against the actual filesystem:

#### Files That Need to Be Created From Scratch

| File Path | Status | Evidence |
|-----------|--------|----------|
| `workflows/gen_media_content_v1/api_actions/render_video/agnes_v2/__init__.py` | MISSING | Directory `render_video/agnes_v2/` does not exist. Only `render_video/__init__.py` exists. `Test-Path` returned False. |
| `workflows/gen_media_content_v1/tests/test_video_provider_agnes_v2.py` | MISSING | File does not exist. `Test-Path` returned False. Glob search returned no matches. |

#### Files That Already Exist (Read-Only References)

| File Path | Status | Purpose |
|-----------|--------|---------|
| `workflows/gen_media_content_v1/api_actions/render_video/__init__.py` | EXISTS | Registry module for video providers. Not modified. |
| `workflows/gen_media_content_v1/api_actions/render_image/agnes_v1/__init__.py` | EXISTS | Phase 3 image provider reference -- 89 lines, provides structural pattern to follow. |
| `workflows/gen_media_content_v1/tests/test_image_provider_agnes_v1.py` | EXISTS | Phase 3 test reference -- 362 lines, provides test pattern to follow. |
| `workflows/agnes_media_gen_v1/impls/agnes_media_v1/actions.py` | EXISTS | Lines 325-399 contain `_process_single_video()` with the existing video API flow (submit, poll, download). Provides the canonical polling logic pattern. |
| `workflows/gen_media_content_v1/config.json.sample` | EXISTS | Config structure with `agnes_v2` settings (model, width, height, num_frames, frame_rate). |

#### Files That Need Modification

None. The task specification explicitly states: "Do NOT modify any existing workflow files." (AC-12).

---

## 3. Implementation Overview

### Summary

This implementation creates the Agnes v2 video rendering provider for the gen_media_content_v1 workflow. The provider is a pure `call_api()` function that:

1. Validates inputs (base_url non-empty, required config keys present).
2. Submits a video generation job via HTTP POST to `{base_url}/v1/videos`.
3. Polls for completion via HTTP GET to `{base_url}/agnesapi?video_id={id}` every 10 seconds, up to 120 attempts.
4. Returns `{"video_url": "<download_url>"}` on success.
5. Raises `RuntimeError` on any failure condition.

### Approach

The implementation follows the established pattern from the Phase 3 image provider (`render_image/agnes_v1/__init__.py`). Key differences from the image provider:

- **Async two-phase flow**: The video provider has a submit phase and a poll phase, unlike the synchronous image provider.
- **Additional `image` parameter**: Video generation is image-to-video, requiring an input image URL.
- **Polling loop with time.sleep**: The provider must poll for status, requiring `time.sleep(10)` between attempts (patched in tests).
- **Multiple response key fallbacks**: video_id extracted from `video_id` or `id`; video_url extracted from `url` or `video_url`.
- **Trailing slash normalization**: base_url has trailing slashes stripped via `base_url.rstrip('/')` before URL construction (following Phase 3 pattern at `agnes_v1/__init__.py` line 54).
- **Poll error resilience**: HTTP exceptions during polling are caught and the loop continues, only timing out after max attempts (following reference pattern at `actions.py` lines 372-375).
- **Three terminal statuses**: The poll loop raises RuntimeError for `failed`, `error`, AND `cancelled` status values (TASK AC-05, Step 1 line 59).
- **JSON decode error handling**: Non-JSON responses during both submit and poll phases are caught via `ValueError` and re-raised as `RuntimeError` (following Phase 3 pattern at `agnes_v1/__init__.py` lines 74-79).

### State Statement

All work described in this plan needs to be created from scratch. No existing files will be modified. The implementation creates exactly 2 new files:
- 1 provider module (`agnes_v2/__init__.py`)
- 1 test module (`test_video_provider_agnes_v2.py`) with 21 unit tests

---

## 4. Task Traceability

| TASK Acceptance Criterion | IMPL Acceptance Criteria Test(s) |
|--------------------------|--------------------------------|
| AC-01: agnes_v2/__init__.py exists and is valid Python | ACT-01 (import validation via test execution) |
| AC-02: call_api() is importable from the module | ACT-01 (import statement in test module) |
| AC-03: Returns dict with "video_url" on success | ACT-01 |
| AC-04: Raises RuntimeError when video_id missing | ACT-02 |
| AC-05: Raises RuntimeError on failed/error/cancelled poll | ACT-03, ACT-04, ACT-19 |
| AC-06: Raises RuntimeError on HTTP errors during submit | ACT-05, ACT-06, ACT-07 |
| AC-07: Raises RuntimeError on polling timeout | ACT-16, ACT-20 |
| AC-08: Correct submit payload | ACT-08, ACT-09, ACT-10 |
| AC-09: Correct submit URL | ACT-11 |
| AC-10: Correct poll URL | ACT-12 |
| AC-11: All 21 tests pass with pytest | ACT-01 through ACT-21 (all must pass) |
| AC-12: No existing files modified | Verified by checking git status after implementation |

Additional tests for header validation (ACT-13), input validation (ACT-14, ACT-15), response key fallbacks (ACT-17, ACT-18), missing video_url in completed response (ACT-21), and poll-phase HTTP error resilience (ACT-20) cover the detailed test requirements listed in TASK Step 2 plus challenge-identified gaps.

---

## 5. Step-by-Step Plan

| Step | Description | Acceptance Criteria Tests Satisfied | Dependencies |
|------|-------------|-------------------------------------|--------------|
| STEP-01 | Create directory `workflows/gen_media_content_v1/api_actions/render_video/agnes_v2/` | N/A (directory creation) | None |
| STEP-02 | Create `workflows/gen_media_content_v1/api_actions/render_video/agnes_v2/__init__.py` with `call_api()` function implementing input validation, submit POST, poll GET loop, and error handling | ACT-01 through ACT-21 | STEP-01 |
| STEP-03 | Create `workflows/gen_media_content_v1/tests/test_video_provider_agnes_v2.py` with 21 unit test cases | ACT-01 through ACT-21 | STEP-02 |
| STEP-04 | Run tests: `.venv\Scripts\python -m pytest workflows/gen_media_content_v1/tests/test_video_provider_agnes_v2.py -v` | ACT-11 | STEP-03 |
| STEP-05 | Verify no existing files modified: `git status` shows only new files added | AC-12 | STEP-04 |

### Step Dependency Graph

```
STEP-01 (create dir)
    |
    v
STEP-02 (create provider module)
    |
    v
STEP-03 (create test module)
    |
    v
STEP-04 (run tests)
    |
    v
STEP-05 (verify no modifications to existing files)
```

---

## 6. Code Changes

### Files to Create

#### 6.1 workflows/gen_media_content_v1/api_actions/render_video/agnes_v2/__init__.py

New file. Provider module with `call_api(prompt, image, config, api_key, base_url)` function.

Structure:
- Module docstring explaining the provider's purpose.
- Import `requests` and `time`.
- `call_api()` function signature matching the task specification.
- Input validation block (base_url non-empty, required config keys).
- Submit phase: POST to `{base_url}/v1/videos` with payload and headers.
- Poll phase: GET to `{base_url}/agnesapi?video_id={id}` in a loop of 120 attempts with 10-second intervals.
- Return `{"video_url": "<url>"}` on success.
- RuntimeError on all failure conditions.

Key implementation details:
- Input validation: `if not base_url or not base_url.strip(): raise RuntimeError(...)` (following Phase 3 pattern at `agnes_v1/__init__.py` line 44).
- Trailing slash normalization: `endpoint = f"{base_url.rstrip('/')}/v1/videos"` (following Phase 3 pattern at `agnes_v1/__init__.py` line 54).
- Extract video_id: `submit_data.get("video_id", "") or submit_data.get("id", "")`
- Extract video_url: `status_data.get("url", "") or status_data.get("video_url", "")`
- Submit JSON parse: wrapped in `try/except ValueError` to catch non-JSON responses, re-raised as RuntimeError (following Phase 3 pattern at `agnes_v1/__init__.py` lines 74-79).
- Payload includes negative_prompt only if present in config (conditional key).
- Submit headers include both Authorization and Content-Type.
- Poll headers include Authorization only (no Content-Type needed for GET).
- Poll loop: HTTP exceptions during poll requests.get are caught (`except requests.exceptions.RequestException`), loop continues to next attempt, only timing out after max attempts (following reference pattern at `actions.py` lines 372-375).
- Poll JSON parse: wrapped in `try/except ValueError` to catch non-JSON poll responses.
- Terminal poll statuses: `if vid_status in ("failed", "error", "cancelled"): raise RuntimeError(...)`.
- Missing video_url after completed status: `if not video_url: raise RuntimeError(...)`.

#### 6.2 workflows/gen_media_content_v1/tests/test_video_provider_agnes_v2.py

New file. 21 unit tests following the pattern from `test_image_provider_agnes_v1.py`.

Test class: `TestCallApi` with 21 test methods.

All tests must:
- Mock `requests` at the module path `workflows.gen_media_content_v1.api_actions.render_video.agnes_v2.requests`.
- Patch `time.sleep` to avoid real delays.
- Import `call_api` from the provider module.
- Use `real_requests.exceptions` for exception type references.

### Files to Modify

None. (AC-12 compliance.)

### Files to Delete

None.

### Codebase Files Referenced (Read-Only)

| File | Purpose |
|------|---------|
| `workflows/gen_media_content_v1/api_actions/render_image/agnes_v1/__init__.py` | Structural pattern reference for call_api() layout. |
| `workflows/gen_media_content_v1/tests/test_image_provider_agnes_v1.py` | Test pattern reference for mocking and assertion style. |
| `workflows/agnes_media_gen_v1/impls/agnes_media_v1/actions.py` (lines 325-399) | Reference for video submit/poll logic, payload structure, and polling constants. |
| `workflows/gen_media_content_v1/config.json.sample` | Config structure reference for agnes_v2 settings. |
| `workflows/gen_media_content_v1/api_actions/render_video/__init__.py` | Registry module (not modified, but context for module placement). |

---

## 7. Test Implementation

The following is the complete test module implementing all 21 Acceptance Criteria Tests. This code will be written to `workflows/gen_media_content_v1/tests/test_video_provider_agnes_v2.py`.

```python
"""Unit tests for agnes_v2 video rendering provider.

Tests cover successful submit+poll cycle, error handling (missing video_id,
failed/error status, HTTP errors, connection errors, timeout), payload
structure, endpoint URL construction, header validation, input validation,
negative_prompt conditional inclusion, polling timeout, and response key
fallbacks. All HTTP calls are mocked; time.sleep is patched to avoid delays.
No real API keys or network access required.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest
import requests as real_requests

# Ensure the project root is importable
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from workflows.gen_media_content_v1.api_actions.render_video.agnes_v2 import call_api


MODULE_PATH = "workflows.gen_media_content_v1.api_actions.render_video.agnes_v2"


class TestCallApi:
    """Tests for call_api function in agnes_v2 provider."""

    def test_successful_submit_and_poll_returns_video_url(self):
        """ACT-01: Returns dict with video_url on successful submit + poll cycle."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"video_id": "vid-abc-123"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.json.return_value = {
            "status": "completed",
            "url": "https://cdn.agnes-ai.com/video/vid-abc-123.mp4"
        }
        poll_resp.raise_for_status = MagicMock()

        config = {
            "model": "agnes-video-v2.0",
            "width": 1024,
            "height": 576,
            "num_frames": 72,
            "frame_rate": 24,
        }

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            result = call_api(
                prompt="a cat walking in a garden",
                image="https://example.com/cat.png",
                config=config,
                api_key="test-key-123",
                base_url="https://apihub.agnes-ai.com",
            )

        assert "video_url" in result
        assert result["video_url"] == "https://cdn.agnes-ai.com/video/vid-abc-123.mp4"

    def test_missing_video_id_raises_runtime_error(self):
        """ACT-02: Raises RuntimeError when video_id is missing from submit response."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {}
        submit_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="video_id"):
                call_api(
                    prompt="a sunset",
                    image="https://example.com/sunset.png",
                    config=config,
                    api_key="test-key-123",
                    base_url="https://apihub.agnes-ai.com",
                )

    def test_poll_failed_status_raises_runtime_error(self):
        """ACT-03: Raises RuntimeError when poll returns failed status."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"video_id": "vid-fail"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.json.return_value = {"status": "failed"}
        poll_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="failed"):
                call_api(
                    prompt="a mountain",
                    image="https://example.com/mountain.png",
                    config=config,
                    api_key="test-key-123",
                    base_url="https://apihub.agnes-ai.com",
                )

    def test_poll_error_status_raises_runtime_error(self):
        """ACT-04: Raises RuntimeError when poll returns error status."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"video_id": "vid-err"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.json.return_value = {"status": "error"}
        poll_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="error"):
                call_api(
                    prompt="a river",
                    image="https://example.com/river.png",
                    config=config,
                    api_key="test-key-123",
                    base_url="https://apihub.agnes-ai.com",
                )

    def test_http_error_on_submit_raises_runtime_error(self):
        """ACT-05: Raises RuntimeError on HTTP error during submit."""
        submit_resp = MagicMock()
        submit_resp.status_code = 500
        submit_resp.raise_for_status.side_effect = real_requests.exceptions.HTTPError(
            "500 Server Error"
        )

        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="request failed"):
                call_api(
                    prompt="a forest",
                    image="https://example.com/forest.png",
                    config=config,
                    api_key="test-key-123",
                    base_url="https://apihub.agnes-ai.com",
                )

    def test_connection_error_on_submit_raises_runtime_error(self):
        """ACT-06: Raises RuntimeError on ConnectionError during submit."""
        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.side_effect = real_requests.exceptions.ConnectionError(
                "Connection refused"
            )
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="request failed"):
                call_api(
                    prompt="a lake",
                    image="https://example.com/lake.png",
                    config=config,
                    api_key="test-key-123",
                    base_url="https://apihub.agnes-ai.com",
                )

    def test_timeout_error_on_submit_raises_runtime_error(self):
        """ACT-07: Raises RuntimeError on Timeout during submit."""
        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.side_effect = real_requests.exceptions.Timeout(
                "Request timed out"
            )
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="request failed"):
                call_api(
                    prompt="a cloud",
                    image="https://example.com/cloud.png",
                    config=config,
                    api_key="test-key-123",
                    base_url="https://apihub.agnes-ai.com",
                )

    def test_correct_submit_payload_structure(self):
        """ACT-08: Sends correct submit payload with all required fields."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"video_id": "vid-payload"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.json.return_value = {"status": "completed", "url": "https://cdn.example.com/v.mp4"}
        poll_resp.raise_for_status = MagicMock()

        config = {
            "model": "agnes-video-v2.0",
            "width": 1024,
            "height": 576,
            "num_frames": 72,
            "frame_rate": 24,
        }

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a bird flying",
                image="https://example.com/bird.png",
                config=config,
                api_key="test-key-123",
                base_url="https://apihub.agnes-ai.com",
            )

            mock_requests.post.assert_called_once()
            call_kwargs = mock_requests.post.call_args
            payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")

            assert payload["model"] == "agnes-video-v2.0"
            assert payload["prompt"] == "a bird flying"
            assert payload["image"] == "https://example.com/bird.png"
            assert payload["width"] == 1024
            assert payload["height"] == 576
            assert payload["num_frames"] == 72
            assert payload["frame_rate"] == 24

    def test_negative_prompt_included_when_present(self):
        """ACT-09: negative_prompt included in payload when present in config."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"video_id": "vid-neg"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.json.return_value = {"status": "completed", "url": "https://cdn.example.com/v.mp4"}
        poll_resp.raise_for_status = MagicMock()

        config = {
            "model": "agnes-video-v2.0",
            "width": 1024,
            "height": 576,
            "negative_prompt": "blurry, distorted",
        }

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a clear sky",
                image="https://example.com/sky.png",
                config=config,
                api_key="test-key-123",
                base_url="https://apihub.agnes-ai.com",
            )

            call_kwargs = mock_requests.post.call_args
            payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
            assert payload["negative_prompt"] == "blurry, distorted"

    def test_negative_prompt_omitted_when_absent(self):
        """ACT-10: negative_prompt omitted from payload when not in config."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"video_id": "vid-noneg"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.json.return_value = {"status": "completed", "url": "https://cdn.example.com/v.mp4"}
        poll_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a tree",
                image="https://example.com/tree.png",
                config=config,
                api_key="test-key-123",
                base_url="https://apihub.agnes-ai.com",
            )

            call_kwargs = mock_requests.post.call_args
            payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
            assert "negative_prompt" not in payload

    def test_correct_submit_endpoint_url(self):
        """ACT-11: Constructs correct submit URL {base_url}/v1/videos."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"video_id": "vid-url"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.json.return_value = {"status": "completed", "url": "https://cdn.example.com/v.mp4"}
        poll_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a flower",
                image="https://example.com/flower.png",
                config=config,
                api_key="test-key-123",
                base_url="https://apihub.agnes-ai.com",
            )

            call_url = mock_requests.post.call_args[0][0]
            assert call_url == "https://apihub.agnes-ai.com/v1/videos"

    def test_correct_poll_endpoint_url(self):
        """ACT-12: Constructs correct poll URL {base_url}/agnesapi?video_id={id}."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"video_id": "vid-poll-url"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.json.return_value = {"status": "completed", "url": "https://cdn.example.com/v.mp4"}
        poll_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a star",
                image="https://example.com/star.png",
                config=config,
                api_key="test-key-123",
                base_url="https://apihub.agnes-ai.com",
            )

            mock_requests.get.assert_called()
            poll_url = mock_requests.get.call_args[0][0]
            assert poll_url == "https://apihub.agnes-ai.com/agnesapi?video_id=vid-poll-url"

    def test_correct_headers(self):
        """ACT-13: Verifies Authorization Bearer + Content-Type headers."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"video_id": "vid-hdr"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.json.return_value = {"status": "completed", "url": "https://cdn.example.com/v.mp4"}
        poll_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a hill",
                image="https://example.com/hill.png",
                config=config,
                api_key="my-secret-key",
                base_url="https://apihub.agnes-ai.com",
            )

            # Verify submit headers
            post_kwargs = mock_requests.post.call_args
            post_headers = post_kwargs.kwargs.get("headers") or post_kwargs[1].get("headers")
            assert post_headers["Authorization"] == "Bearer my-secret-key"
            assert post_headers["Content-Type"] == "application/json"

            # Verify poll headers
            get_kwargs = mock_requests.get.call_args
            get_headers = get_kwargs.kwargs.get("headers") or get_kwargs[1].get("headers")
            assert get_headers["Authorization"] == "Bearer my-secret-key"

    def test_empty_base_url_raises_runtime_error(self):
        """ACT-14: Empty base_url raises RuntimeError."""
        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with pytest.raises(RuntimeError, match="base_url"):
            call_api(
                prompt="a moon",
                image="https://example.com/moon.png",
                config=config,
                api_key="test-key",
                base_url="",
            )

    def test_missing_config_keys_raises_runtime_error(self):
        """ACT-15: Missing required config keys raises RuntimeError."""
        with pytest.raises(RuntimeError, match="missing required keys"):
            call_api(
                prompt="a sun",
                image="https://example.com/sun.png",
                config={},
                api_key="test-key",
                base_url="https://apihub.agnes-ai.com",
            )

    def test_poll_timeout_after_max_attempts_raises_runtime_error(self):
        """ACT-16: Raises RuntimeError when polling times out after 120 attempts."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"video_id": "vid-timeout"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.json.return_value = {"status": "processing"}
        poll_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="[Tt]imed out|max.*attempts|poll"):
                call_api(
                    prompt="a planet",
                    image="https://example.com/planet.png",
                    config=config,
                    api_key="test-key-123",
                    base_url="https://apihub.agnes-ai.com",
                )

    def test_video_id_extracted_from_id_field_fallback(self):
        """ACT-17: video_id extracted from 'id' field when video_id key is absent."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"id": "vid-from-id-field"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.json.return_value = {"status": "completed", "url": "https://cdn.example.com/v.mp4"}
        poll_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a galaxy",
                image="https://example.com/galaxy.png",
                config=config,
                api_key="test-key-123",
                base_url="https://apihub.agnes-ai.com",
            )

            poll_url = mock_requests.get.call_args[0][0]
            assert "video_id=vid-from-id-field" in poll_url

    def test_video_url_extracted_from_video_url_field_fallback(self):
        """ACT-18: video_url extracted from 'video_url' field when url key is absent."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"video_id": "vid-vurl"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.json.return_value = {
            "status": "completed",
            "video_url": "https://cdn.example.com/fallback-video.mp4"
        }
        poll_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            result = call_api(
                prompt="a nebula",
                image="https://example.com/nebula.png",
                config=config,
                api_key="test-key-123",
                base_url="https://apihub.agnes-ai.com",
            )

        assert result["video_url"] == "https://cdn.example.com/fallback-video.mp4"

    def test_poll_cancelled_status_raises_runtime_error(self):
        """ACT-19: Raises RuntimeError when poll returns cancelled status."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"video_id": "vid-cancel"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.json.return_value = {"status": "cancelled"}
        poll_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="cancelled"):
                call_api(
                    prompt="a bird",
                    image="https://example.com/bird.png",
                    config=config,
                    api_key="test-key-123",
                    base_url="https://apihub.agnes-ai.com",
                )

    def test_http_error_during_polling_continues_and_times_out(self):
        """ACT-20: HTTP errors during polling do not crash; loop continues until timeout."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"video_id": "vid-poll-err"}
        submit_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.side_effect = real_requests.exceptions.HTTPError(
                "500 Server Error"
            )
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="[Tt]imed out|max.*attempts|poll"):
                call_api(
                    prompt="a deer",
                    image="https://example.com/deer.png",
                    config=config,
                    api_key="test-key-123",
                    base_url="https://apihub.agnes-ai.com",
                )

    def test_completed_poll_missing_video_url_raises_runtime_error(self):
        """ACT-21: Completed poll response missing both url and video_url raises RuntimeError."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"video_id": "vid-nourl"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.json.return_value = {"status": "completed"}
        poll_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="video.*[Uu][Rr][Ll]|url|download"):
                call_api(
                    prompt="a fox",
                    image="https://example.com/fox.png",
                    config=config,
                    api_key="test-key-123",
                    base_url="https://apihub.agnes-ai.com",
                )
```

---

## 8. Rollback Plan

### Scenario: Implementation Fails or Causes Issues

Since this implementation creates only new files and modifies no existing files, rollback is straightforward:

1. **Delete new files**: Remove the two created files:
   - `workflows/gen_media_content_v1/api_actions/render_video/agnes_v2/__init__.py`
   - `workflows/gen_media_content_v1/tests/test_video_provider_agnes_v2.py`
2. **Remove empty directory**: Remove `workflows/gen_media_content_v1/api_actions/render_video/agnes_v2/` if empty after file deletion.
3. **Verify clean state**: Run `git status` to confirm no other files were modified.
4. **Verify existing tests still pass**: Run `.venv\Scripts\python -m pytest tests/unit/ -v` to confirm no regressions.

### Scenario: Tests Fail After Implementation

1. Review test output to identify which acceptance criteria tests failed.
2. Compare the test expectations against the implementation logic.
3. Fix the implementation to match the test expectations (not the reverse).
4. Re-run tests until all 21 pass.

---

## 9. Dependencies

### External Dependencies

| Dependency | Version/Source | Purpose |
|------------|---------------|---------|
| `requests` | Already installed in project venv | HTTP client for API calls |
| `pytest` | Already installed in project venv (dev dependency) | Test runner |

### Prerequisites

| Prerequisite | Status |
|--------------|--------|
| Python 3.12+ virtual environment with project installed | Assumed ready |
| Project root is git repository | Verified |
| `render_video/` parent directory exists | Verified (contains `__init__.py`) |
| `tests/` directory exists | Verified (contains other test files) |
| `requests` library available | Available via project dependencies |

### No New Dependencies Required

This implementation uses only `requests` (already a project dependency) and `pytest` (already a dev dependency). No new packages need to be installed.

---

## 10. Open Questions

### None

All requirements are fully specified in the approved task specification (TASK-20260815-001-04). The following items are explicitly resolved:

- **Poll interval and max attempts**: 10 seconds, 120 attempts (specified in TASK Step 1).
- **Config required keys**: model, width, height (specified in TASK Step 1).
- **Response key fallbacks**: video_id from "video_id" or "id"; video_url from "url" or "video_url" (specified in TASK Step 1).
- **No file download**: The provider returns the URL, the orchestrator handles downloads (specified in TASK Overview).
- **Pure function**: No file I/O, no directory scanning, no state mutation (specified in TASK Technical Specifications).

### Assumptions Recorded

1. The `time` module is used for `time.sleep()` in the polling loop, and tests patch `time.sleep` at the module level.
2. The `requests` library is imported at module level in the provider, and tests patch `requests` at the module level (following the Phase 3 pattern).
3. The submit phase uses `requests.post()` and the poll phase uses `requests.get()`.
4. The poll GET request does not include `Content-Type` header (only `Authorization`), as specified in the task.
5. HTTP errors during polling are handled gracefully: the poll loop catches `requests.exceptions.RequestException`, continues to the next attempt, and only times out after max attempts. This follows the reference implementation pattern (`actions.py` lines 372-375) and is verified by ACT-20.
6. Non-JSON responses during submit and poll phases are caught via `ValueError` (parent of `json.JSONDecodeError`) and re-raised as `RuntimeError`, following the Phase 3 image provider pattern (`agnes_v1/__init__.py` lines 74-79).
7. The `base_url.rstrip('/')` normalization prevents double-slash URLs when a trailing slash is provided.
8. Input validation for `base_url` checks both empty string and whitespace-only string via `not base_url or not base_url.strip()`.
9. Terminal poll statuses include "failed", "error", AND "cancelled" (TASK AC-05, Step 1 line 59).
10. A completed poll response with no valid URL in either "url" or "video_url" field raises RuntimeError.

---

## Challenge Resolution

### Attack 1: Missing Test for "cancelled" Status
**Evaluation:** Valid
**Resolution:** Added ACT-19 test case for status="cancelled" raising RuntimeError. The TASK specification AC-05 explicitly requires "failed/error/cancelled" to raise RuntimeError, and TASK Step 1 line 59 explicitly lists `"cancelled"` in the terminal status tuple. The implementation guidance in Section 6.1 was updated to specify `if vid_status in ("failed", "error", "cancelled")` as the terminal status check. Test count updated from 18 to 21.
**Evidence:** TASK-20260815-001-04 AC-05: "call_api() raises RuntimeError when poll returns failed/error/cancelled status". TASK Step 1 line 59: 'On `status` in `("failed", "error", "cancelled")`: raise RuntimeError'. Reference code `actions.py` line 370: `elif vid_status in ("failed", "error", "cancelled"):`.
**Affected section:** Section 1 (ACT-19 added), Section 3 (Approach bullet added), Section 4 (traceability row updated), Section 5 (test count), Section 6.1 (implementation details), Section 7 (test code added), Section 8 (rollback test count), Section 10 (assumptions updated).

### Attack 2: Missing Test for HTTP Errors During Polling
**Evaluation:** Valid
**Resolution:** Added ACT-20 test case that verifies HTTP errors during polling do not crash the function but instead cause the poll loop to continue until timeout. The Open Questions section previously claimed this behavior existed but had no corresponding test. Updated Section 6.1 to explicitly specify the `except requests.exceptions.RequestException` catch-and-continue pattern in the poll loop. Updated Assumptions section to clarify this is verified by ACT-20.
**Evidence:** Reference code `actions.py` lines 372-375: `except requests.exceptions.RequestException: if poll_attempt >= max_poll_attempts - 1: raise RuntimeError(...); continue`. The original Open Questions (line 845) claimed graceful handling but no test existed.
**Affected section:** Section 1 (ACT-20 added), Section 3 (Approach bullet added), Section 4 (traceability updated), Section 5 (test count), Section 6.1 (implementation details), Section 7 (test code added), Section 10 (assumptions #5 rewritten).

### Attack 3: Fragile Payload Extraction Pattern in Tests
**Evaluation:** Incorrect
**Resolution:** No changes made. The payload extraction pattern `call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")` is correct and proven. In Python 3.8+, `mock.call_args` returns a `call` object (a namedtuple subclass) where `call_args[0]` is positional args, `call_args[1]` is keyword args dict, `call_args.args` is positional args, and `call_args.kwargs` is keyword args dict. Both `call_args.kwargs` and `call_args[1]` return the same dict. The `or` pattern provides backward compatibility. The Phase 3 image provider tests use this exact same pattern and pass successfully.
**Evidence:** Phase 3 test file `test_image_provider_agnes_v1.py` lines 193, 254, 284, 312 all use `call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")` and pass. Python `unittest.mock.call` object supports both tuple indexing (`[1]`) and attribute access (`.kwargs`) since Python 3.8.
**Affected section:** None (no changes required).

### Attack 4: Missing Test for JSON Decode Error During Polling
**Evaluation:** Out of scope for tests, but valid for implementation guidance
**Resolution:** No dedicated test added for poll-phase JSON decode errors (the task specifies exactly which tests to include, and JSON decode error during polling is not among them). However, the implementation guidance in Section 6.1 was updated to specify that poll JSON parsing should be wrapped in `try/except ValueError` following the Phase 3 pattern. Assumption #6 was added to document this behavior. The reference code (`actions.py` line 365) does NOT actually catch this error either (JSONDecodeError is not a RequestException), so adding a test that expects specific handling would require the implementation to diverge from the reference pattern.
**Evidence:** TASK Step 2 lists exactly 18 test cases; JSON decode error during polling is not among them. Reference code `actions.py` line 365 calls `status_resp.json()` inside a `try/except requests.exceptions.RequestException` block, which would NOT catch `json.JSONDecodeError` (a ValueError subclass). Phase 3 image provider `agnes_v1/__init__.py` lines 74-79 catches ValueError for the submit phase only.
**Affected section:** Section 6.1 (implementation details: poll JSON parse guidance added), Section 10 (assumption #6 added).

### Attack 5: Missing Trailing Slash Handling in base_url
**Evaluation:** Valid
**Resolution:** Added trailing slash normalization to implementation guidance. Section 6.1 now specifies `endpoint = f"{base_url.rstrip('/')}/v1/videos"` following the Phase 3 pattern. Approach section updated with a bullet explaining this.
**Evidence:** Phase 3 image provider `agnes_v1/__init__.py` line 54: `endpoint = f"{base_url.rstrip('/')}/v1/images/generations"`. Without this, `base_url="https://apihub.agnes-ai.com/"` would produce `https://apihub.agnes-ai.com//v1/videos` (double slash).
**Affected section:** Section 3 (Approach bullet added), Section 6.1 (implementation details), Section 10 (assumption #7 added).

### Attack 6: No Test for Missing video_url in Completed Response
**Evaluation:** Valid
**Resolution:** Added ACT-21 test case for completed poll response where both "url" and "video_url" keys are missing. Section 6.1 implementation guidance updated to specify `if not video_url: raise RuntimeError(...)` after the poll loop completes with status="completed" but no valid URL. This follows the reference code pattern at `actions.py` lines 377-378.
**Evidence:** Reference code `actions.py` lines 377-378: `if not video_download_url: raise ValueError(...)`. ACT-01 and ACT-18 only test cases where a URL is present. No test covered the missing-URL edge case.
**Affected section:** Section 1 (ACT-21 added), Section 4 (traceability updated), Section 5 (test count), Section 6.1 (implementation details), Section 7 (test code added), Section 10 (assumption #10 added).

### Attack 7: Whitespace-Only base_url Not Tested
**Evaluation:** Valid
**Resolution:** Updated implementation guidance in Section 6.1 to specify `if not base_url or not base_url.strip(): raise RuntimeError(...)` for input validation, matching the Phase 3 pattern. ACT-14 remains unchanged (testing empty string), but the implementation now handles whitespace-only strings as well. Added assumption #8 documenting this approach. No new test added since the TASK specifies exactly which tests to include and whitespace-only is not among them; the implementation guidance ensures correct behavior.
**Evidence:** Phase 3 image provider `agnes_v1/__init__.py` line 44: `if not base_url or not base_url.strip():`. The original IMPL only specified checking for empty base_url without addressing whitespace.
**Affected section:** Section 6.1 (implementation details: input validation updated), Section 10 (assumption #8 added).
