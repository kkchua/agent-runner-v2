---
template_id: SYS-03-TK
version: "1.0.0"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved task specification for gen_media_content_v1 Phase 9 orchestrator integration"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
---

# Task: gen_media_content_v1 Phase 9 - Wire Orchestrator + Integration

## Document Metadata

- Document ID: TASK-20260815-001-09
- Source backlog reference: WI-20260814-001 (gen_media_content_v1 workflow)
- Task IDs covered: WI-20260814-001-09
- Date of generation: 2026-08-15
- Producing workflow: Manual initiation
- Producing agent: default (Kai)
- Prior task: TASK-20260815-001-08 (Phase 8 BCS impls)

## Task Overview

Replace the orchestrator stubs in root `actions.py` with full implementations that dynamically import providers, scan variant directories, batch API calls, download results, and write index files. This is the final integration phase that connects all providers, prompts, and impls into a working pipeline.

Expected outcome: `generate_images_default` and `generate_videos_default` actions fully implemented with provider dispatch, batching, download, and index writing. Integration tests verify the full mock pipeline.

## Detailed Implementation Steps

### Step 1: Implement generate_images_default

Update `workflows/gen_media_content_v1/actions.py` -- replace the `generate_images_default` stub:

1. Load config from `{MEDIA_CONFIG}` context variable
2. Read `config["actions"]["render_image"]` to determine provider name
3. If provider is `"__none__"` or empty -> return REJECTED with MISSING_PROVIDER
4. Import provider via `import_provider("render_image", provider_name)`
5. Read API config from `config["api"][provider_name]`
6. Resolve API key from env vars (AGNES_API_KEY_* for agnes_v1)
7. Scan `{STEP_02_DIR}` for variant JSON files (*_prompts.json)
8. For each variant:
   a. Read variant data (t2i_prompt1, image_filename, etc.)
   b. Call `provider.call_api(prompt=variant["t2i_prompt1"], config=api_config, api_key=key, base_url=base_url)`
   c. Download image from `result["image_url"]`
   d. Save to `{STEP_03_DIR}` using `_get_next_sequence_filename`
   e. Track file mapping
9. Write `index.json` to `{STEP_03_DIR}` using `_write_index`
10. Return ActionResult(status="APPROVED", ...)

Error handling: If a single image fails, log and continue. If ALL fail -> REJECTED. If some succeed -> APPROVED with remark.

### Step 2: Implement generate_videos_default

Update `workflows/gen_media_content_v1/actions.py` -- replace the `generate_videos_default` stub:

1. Load config from `{MEDIA_CONFIG}`
2. Read `config["actions"]["render_video"]` to determine provider
3. If provider is `"__none__"` -> return APPROVED with "Video generation skipped"
4. Import provider via `import_provider("render_video", provider_name)`
5. Read API config from `config["api"][provider_name]`
6. Resolve API key from env vars (AGNES_API_KEY_* for agnes_v2, HAPPYHORSE_API_KEY_* for happyhorse)
7. Scan `{STEP_03_DIR}` for generated images (via index.json)
8. For each image:
   a. Read corresponding variant JSON from `{STEP_02_DIR}` for video prompt (t2v_prompt1)
   b. Call `provider.call_api(prompt=video_prompt, image=image_url, config=api_config, api_key=key, base_url=base_url)`
   c. If result has `{"skipped": True}` -> skip
   d. Download video from `result["video_url"]`
   e. Save to `{STEP_04_DIR}` using `_get_next_sequence_filename`
   f. Track file mapping
9. Write `index.json` to `{STEP_04_DIR}` using `_write_index`
10. Return ActionResult(status="APPROVED", ...)

### Step 3: Create Integration Tests

Create `workflows/gen_media_content_v1/tests/test_orchestrator.py` with tests for:

- generate_images calls provider and downloads images
- generate_images writes index.json with correct mappings
- generate_images with missing provider returns REJECTED
- generate_images with all failures returns REJECTED
- generate_images with partial success returns APPROVED
- generate_videos calls provider and downloads videos
- generate_videos with __none__ provider returns APPROVED (skipped)
- generate_videos handles {"skipped": True} from provider
- import_provider works for valid provider names
- import_provider raises ImportError for invalid names
- _load_config raises FileNotFoundError for missing files

## Reference Files

| File | Purpose |
|---|---|
| workflows/gen_media_content_v1/actions.py | Current stubs to replace |
| workflows/agnes_media_gen_v1/impls/agnes_media_v1/actions.py | Reference orchestrator logic (batching, download, index) |
| workflows/gen_media_content_v1/config.json.sample | Config structure |
| workflows/gen_media_content_v1/api_actions/render_image/agnes_v1/__init__.py | Provider interface |
| workflows/gen_media_content_v1/api_actions/render_video/agnes_v2/__init__.py | Provider interface |

## Test Requirements

- Mock `import_provider` to return mock provider modules.
- Mock provider `call_api` to return controlled responses.
- Mock `requests.get` for download calls.
- Create temporary directories for step dirs.
- Tests must run with: `.venv\Scripts\python -m pytest workflows/gen_media_content_v1/tests/test_orchestrator.py -v`

## Acceptance Criteria

- AC-01: generate_images_default dispatches to configured provider.
- AC-02: generate_images_default downloads images and saves to STEP_03_DIR.
- AC-03: generate_images_default writes index.json with correct file mappings.
- AC-04: generate_images_default returns REJECTED when no provider configured.
- AC-05: generate_videos_default dispatches to configured provider.
- AC-06: generate_videos_default handles __none__ provider (returns APPROVED, skipped).
- AC-07: generate_videos_default handles {"skipped": True} from provider.
- AC-08: import_provider works for valid names, raises ImportError for invalid.
- AC-09: All 14 tests pass with pytest.
- AC-10: Full test suite passes (all phases).
- AC-11: No existing files outside gen_media_content_v1 were modified.

## Definition of Done

- generate_images_default fully implemented in actions.py.
- generate_videos_default fully implemented in actions.py.
- tests/test_orchestrator.py created with 14 test cases.
- All tests pass including full suite across all phases.
- No existing files outside gen_media_content_v1 modified.

## Source Reference

- Source requirements: docs/QwenPaw/gen_media_content_v1/REQUIREMENTS.md (Sections 3.3, 3.4)
- Source plan: docs/QwenPaw/gen_media_content_v1/PLAN.md (Phase 9)
- Reference workflow: workflows/agnes_media_gen_v1/impls/agnes_media_v1/actions.py
- Prior task: TASK-20260815-001-08 (Phase 8 BCS impls)
