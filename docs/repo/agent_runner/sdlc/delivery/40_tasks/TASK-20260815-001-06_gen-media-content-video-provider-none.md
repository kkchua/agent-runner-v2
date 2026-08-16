---
template_id: SYS-03-TK
version: "1.0.0"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved task specification for gen_media_content_v1 Phase 6 video provider (__none__ skip)"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
---

# Task: gen_media_content_v1 Phase 6 - API Provider render_video (__none__ / Skip)

## Document Metadata

- Document ID: TASK-20260815-001-06
- Source backlog reference: WI-20260814-001 (gen_media_content_v1 workflow)
- Task IDs covered: WI-20260814-001-06
- Date of generation: 2026-08-15
- Producing workflow: Manual initiation
- Producing agent: default (Kai)
- Prior task: TASK-20260815-001-05 (Phase 5 happyhorse video provider)

## Task Overview

Create the `__none__` skip provider at `api_actions/render_video/__none__/`. This provider returns a skip marker to bypass video generation entirely, enabling image-only workflows via the implementation dropdown.

Expected outcome: A minimal provider module that returns `{"skipped": True}` with no side effects.

## Detailed Implementation Steps

### Step 1: Create Provider Module

Create `workflows/gen_media_content_v1/api_actions/render_video/__none__/__init__.py`:

```python
def call_api(prompt="", image=None, config=None, api_key="", base_url=""):
    return {"skipped": True, "reason": "Video generation disabled (__none__ provider)"}
```

### Step 2: Create Unit Tests

Create `workflows/gen_media_content_v1/tests/test_video_provider_none.py` with tests for:

- Returns skip marker dict with "skipped": True
- No side effects (no files, no HTTP, no exceptions)
- Accepts any arguments without error
- Accepts no arguments (all defaults)

## Reference Files

| File | Purpose |
|---|---|
| workflows/gen_media_content_v1/api_actions/render_video/__init__.py | Registry mentions __none__ provider |
| docs/QwenPaw/gen_media_content_v1/REQUIREMENTS.md | Section 7.4 -- skip provider contract |

## Acceptance Criteria

- AC-01: __none__/__init__.py exists and is valid Python.
- AC-02: call_api() returns {"skipped": True, "reason": "..."}.
- AC-03: No HTTP calls, no file I/O, no exceptions.
- AC-04: All 4 tests pass with pytest.
- AC-05: No existing files were modified.

## Definition of Done

- api_actions/render_video/__none__/__init__.py created.
- tests/test_video_provider_none.py created with 4 test cases.
- All tests pass.

## Source Reference

- Source requirements: docs/QwenPaw/gen_media_content_v1/REQUIREMENTS.md (Section 7.4)
- Source plan: docs/QwenPaw/gen_media_content_v1/PLAN.md (Phase 6)
- Prior task: TASK-20260815-001-05 (Phase 5 happyhorse video provider)
