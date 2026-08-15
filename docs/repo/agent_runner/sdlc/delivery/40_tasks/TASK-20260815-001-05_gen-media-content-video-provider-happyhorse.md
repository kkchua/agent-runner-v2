---
template_id: SYS-03-TK
version: "1.0.0"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved task specification for gen_media_content_v1 Phase 5 video provider (happyhorse_v1_1)"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
---

# Task: gen_media_content_v1 Phase 5 - API Provider render_video (happyhorse_v1_1)

## Document Metadata

- Document ID: TASK-20260815-001-05
- Source backlog reference: WI-20260814-001 (gen_media_content_v1 workflow)
- Task IDs covered: WI-20260814-001-05
- Date of generation: 2026-08-15
- Producing workflow: Manual initiation
- Producing agent: default (Kai)
- Prior task: TASK-20260815-001-04 (Phase 4 agnes_v2 video provider)

## Task Overview

Create the HappyHorse v1.1 video rendering provider module at `api_actions/render_video/happyhorse_v1_1/`. This provider implements a pure `call_api()` function that submits video generation jobs via the DashScope API and polls until completion.

This is a different API style from Agnes: DashScope uses an async header (`X-DashScope-Async: enable`), nested payload structure (`input` + `parameters`), and different status values (`SUCCEEDED`/`FAILED`).

Expected outcome: A valid Python module with `call_api()` that submits to DashScope, polls for task completion, and returns video URLs.

## Detailed Implementation Steps

### Step 1: Create Provider Module

Create `workflows/gen_media_content_v1/api_actions/render_video/happyhorse_v1_1/__init__.py`:

#### 1a: call_api(prompt, image, config, api_key, base_url)

Signature:
```python
def call_api(prompt: str, image: str, config: dict, api_key: str, base_url: str) -> dict:
```

Submit phase:
- HTTP POST to `{base_url}/api/v1/services/aigc/video-generation/video-synthesis`
- Headers: `{"Authorization": "Bearer {api_key}", "Content-Type": "application/json", "X-DashScope-Async": "enable"}`
- Payload (nested structure):
  ```json
  {
    "model": "happyhorse-1.1-i2v",
    "input": {
      "prompt": "<prompt>",
      "media": [{"type": "first_frame", "url": "<image_url>"}]
    },
    "parameters": {
      "resolution": "480P",
      "ratio": "9:16",
      "duration": 15
    }
  }
  ```
- Image sent as URL string in `media[0].url` (NOT base64)
- Extract `task_id` from `response["output"]["task_id"]`

Poll phase:
- HTTP GET to `{base_url}/api/v1/tasks/{task_id}`
- Headers: `{"Authorization": "Bearer {api_key}"}` (NO X-DashScope-Async, NO Content-Type)
- Poll interval: 15 seconds, max 120 attempts
- On `task_status == "SUCCEEDED"`: extract URL from `output.video_url`, fallback to `output.results[0].url`
- On `task_status == "FAILED"`: raise RuntimeError
- On all polls exhausted: raise RuntimeError

Return: `{"video_url": "<download_url>"}`

Input validation:
- Check `base_url` is non-empty
- Check required config keys: `model`, `resolution`

### Step 2: Create Unit Tests

Create `workflows/gen_media_content_v1/tests/test_video_provider_happyhorse_v1_1.py` with tests for:

- Successful submit + poll cycle returns video_url
- Submit response missing task_id raises RuntimeError
- Poll returns FAILED status raises RuntimeError
- HTTP error on submit raises RuntimeError
- Connection error on submit raises RuntimeError
- Correct nested payload structure (input + parameters)
- Submit has X-DashScope-Async header
- Correct submit endpoint URL
- Correct poll endpoint URL
- Poll does NOT have X-DashScope-Async header
- Correct headers (Authorization Bearer + Content-Type)
- Empty base_url raises RuntimeError
- Missing config keys raises RuntimeError
- Poll timeout raises RuntimeError
- Fallback URL from results[0].url when video_url is empty
- Image sent as URL string, not base64

## Technical Specifications

- DashScope API base URL default: `https://dashscope.aliyuncs.com`
- Config dict structure:
  ```json
  {
    "model": "happyhorse-1.1-i2v",
    "resolution": "480P",
    "ratio": "9:16",
    "duration": 15
  }
  ```

## Reference Files

| File | Purpose |
|---|---|
| workflows/gen_media_content_v1/api_actions/render_video/agnes_v2/__init__.py | Phase 4 provider -- follow same error handling pattern |
| workflows/agnes_gen_video_v1/impls/happyhorse_v1_1/actions.py | Existing HappyHorse API flow (DashScope endpoints, headers, payload) |
| workflows/gen_media_content_v1/config.json.sample | Config structure with happyhorse_v1_1 settings |
| docs/QwenPaw/gen_media_content_v1/REQUIREMENTS.md | Section 7.3 -- API contract |

## Test Requirements

- All HTTP calls must be mocked.
- Patch `time.sleep` to avoid real delays.
- Tests must run with: `.venv\Scripts\python -m pytest workflows/gen_media_content_v1/tests/test_video_provider_happyhorse_v1_1.py -v`

## Acceptance Criteria

- AC-01: happyhorse_v1_1/__init__.py exists and is valid Python.
- AC-02: call_api() is importable from the module.
- AC-03: call_api() returns dict with "video_url" on successful cycle.
- AC-04: call_api() raises RuntimeError when task_id missing from submit response.
- AC-05: call_api() raises RuntimeError on FAILED task status.
- AC-06: Submit payload uses nested input + parameters structure.
- AC-07: Submit headers include X-DashScope-Async: enable.
- AC-08: Poll headers do NOT include X-DashScope-Async.
- AC-09: Image sent as URL string, not base64.
- AC-10: Fallback URL extraction from results[0].url works.
- AC-11: All 16 tests pass with pytest.
- AC-12: No existing files were modified.

## Definition of Done

- api_actions/render_video/happyhorse_v1_1/__init__.py created with call_api().
- tests/test_video_provider_happyhorse_v1_1.py created with 16 test cases.
- All tests pass.
- No existing files modified.

## Source Reference

- Source requirements: docs/QwenPaw/gen_media_content_v1/REQUIREMENTS.md (Section 7.3)
- Source plan: docs/QwenPaw/gen_media_content_v1/PLAN.md (Phase 5)
- Reference workflow: workflows/agnes_gen_video_v1/impls/happyhorse_v1_1/actions.py
- Prior task: TASK-20260815-001-04 (Phase 4 agnes_v2 video provider)
