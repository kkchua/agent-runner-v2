---
template_id: SYS-03-TK
version: "1.0.0"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved task specification for gen_media_content_v1 Phase 4 video provider (agnes_v2)"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
---

# Task: gen_media_content_v1 Phase 4 - API Provider render_video (agnes_v2)

## Document Metadata

- Document ID: TASK-20260815-001-04
- Source backlog reference: WI-20260814-001 (gen_media_content_v1 workflow)
- Task IDs covered: WI-20260814-001-04
- Date of generation: 2026-08-15
- Producing workflow: Manual initiation
- Producing agent: default (Kai)
- Prior task: TASK-20260815-001-03 (Phase 3 image provider -- completed)

## Task Overview

Create the Agnes v2 video rendering provider module at `api_actions/render_video/agnes_v2/`. This provider implements a pure `call_api()` function that submits video generation jobs and polls until completion using the Agnes Video V2.0 API.

The provider is asynchronous: submit a job, then poll for status until the video is ready. It returns the video download URL without downloading the file (the orchestrator handles downloads).

Expected outcome: A valid Python module with `call_api()` that submits video jobs, polls for completion, and returns video URLs. Covered by unit tests with mocked HTTP for both submit and poll cycles.

## Detailed Implementation Steps

### Step 1: Create Provider Module

Create `workflows/gen_media_content_v1/api_actions/render_video/agnes_v2/__init__.py`:

#### 1a: call_api(prompt, image, config, api_key, base_url)

Signature:
```python
def call_api(prompt: str, image: str, config: dict, api_key: str, base_url: str) -> dict:
```

Submit phase:
- HTTP POST to `{base_url}/v1/videos`
- Payload: `{"model": config["model"], "prompt": prompt, "image": image, "width": config["width"], "height": config["height"], "num_frames": config["num_frames"], "frame_rate": config["frame_rate"]}`
- Include `negative_prompt` in payload only if present in config
- Headers: `{"Authorization": "Bearer {api_key}", "Content-Type": "application/json"}`
- Extract `video_id` from response (check both `video_id` and `id` keys)

Poll phase:
- HTTP GET to `{base_url}/agnesapi?video_id={video_id}`
- Same Authorization header (no Content-Type needed for GET)
- Poll interval: 10 seconds, max 120 attempts
- On `status == "completed"`: extract URL from `url` or `video_url` key
- On `status` in `("failed", "error", "cancelled")`: raise RuntimeError
- On all polls exhausted: raise RuntimeError

Return: `{"video_url": "<download_url>"}`
Raise `RuntimeError` on validation failures, HTTP errors, or polling timeout.

Input validation:
- Check `base_url` is non-empty
- Check required config keys: `model`, `width`, `height`

### Step 2: Create Unit Tests

Create `workflows/gen_media_content_v1/tests/test_video_provider_agnes_v2.py` with tests for:

- Successful submit + poll cycle returns video_url
- Submit response missing video_id raises RuntimeError
- Poll returns "failed" status raises RuntimeError
- Poll returns "error" status raises RuntimeError
- HTTP error on submit raises RuntimeError
- Connection error on submit raises RuntimeError
- Timeout error on submit raises RuntimeError
- Correct submit payload structure (model, prompt, image, width, height, num_frames, frame_rate)
- negative_prompt included when present in config
- negative_prompt omitted when absent from config
- Correct submit endpoint URL
- Correct poll endpoint URL
- Correct headers (Authorization Bearer + Content-Type)
- Empty base_url raises RuntimeError
- Missing config keys raises RuntimeError
- Poll timeout after max attempts raises RuntimeError
- video_id extracted from "id" field (fallback)
- video_url extracted from "video_url" field (fallback)

All tests must mock HTTP calls and patch time.sleep to avoid delays.

## Technical Specifications

- All file paths relative to agent-runner-v2 project root.
- Do NOT modify any existing workflow files. Only create files under `workflows/gen_media_content_v1/api_actions/render_video/agnes_v2/` and `workflows/gen_media_content_v1/tests/`.
- Use `requests` library for HTTP calls.
- The `call_api()` function must be pure -- no file I/O, no directory scanning, no state mutation.
- Config dict structure:
  ```json
  {
    "model": "agnes-video-v2.0",
    "width": 1024,
    "height": 576,
    "num_frames": 72,
    "frame_rate": 24,
    "negative_prompt": "blurry, distorted"
  }
  ```

## Reference Files

| File | Purpose |
|---|---|
| workflows/gen_media_content_v1/api_actions/render_image/agnes_v1/__init__.py | Phase 3 provider -- follow same structure |
| workflows/gen_media_content_v1/tests/test_image_provider_agnes_v1.py | Phase 3 tests -- follow same pattern |
| workflows/agnes_media_gen_v1/impls/agnes_media_v1/actions.py | Existing video API flow (lines 321-395, _process_single_video) |
| workflows/gen_media_content_v1/config.json.sample | Config structure with agnes_v2 settings |
| docs/QwenPaw/gen_media_content_v1/REQUIREMENTS.md | Section 7.2 -- API contract |

## Test Requirements

- Unit tests for call_api() covering submit, poll, error handling, and payload validation.
- All HTTP calls must be mocked (unittest.mock.patch).
- Patch `time.sleep` to avoid real delays in poll loop.
- Tests must run with: `.venv\Scripts\python -m pytest workflows/gen_media_content_v1/tests/test_video_provider_agnes_v2.py -v`
- Tests must NOT require real API keys or network access.

## Acceptance Criteria

- AC-01: agnes_v2/__init__.py exists and is valid Python with no syntax errors.
- AC-02: call_api() is importable from the module.
- AC-03: call_api() returns dict with "video_url" key on successful submit + poll cycle.
- AC-04: call_api() raises RuntimeError when video_id is missing from submit response.
- AC-05: call_api() raises RuntimeError when poll returns failed/error/cancelled status.
- AC-06: call_api() raises RuntimeError on HTTP errors during submit.
- AC-07: call_api() raises RuntimeError when polling times out after max attempts.
- AC-08: call_api() sends correct submit payload (model, prompt, image, width, height, num_frames, frame_rate).
- AC-09: call_api() constructs correct submit URL ({base_url}/v1/videos).
- AC-10: call_api() constructs correct poll URL ({base_url}/agnesapi?video_id={id}).
- AC-11: All 18 tests pass with pytest.
- AC-12: No existing files were modified.

## Definition of Done

- api_actions/render_video/agnes_v2/__init__.py created with call_api() function.
- tests/test_video_provider_agnes_v2.py created with 18 test cases.
- All tests pass.
- No existing files modified.

## Source Reference

- Source requirements: docs/QwenPaw/gen_media_content_v1/REQUIREMENTS.md (Section 7.2)
- Source plan: docs/QwenPaw/gen_media_content_v1/PLAN.md (Phase 4)
- Reference workflow: workflows/agnes_media_gen_v1/impls/agnes_media_v1/actions.py
- Prior task: TASK-20260815-001-03 (Phase 3 image provider)
