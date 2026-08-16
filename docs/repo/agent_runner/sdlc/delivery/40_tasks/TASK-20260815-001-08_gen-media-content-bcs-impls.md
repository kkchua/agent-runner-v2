---
template_id: SYS-03-TK
version: "1.0.0"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved task specification for gen_media_content_v1 Phase 8 BCS impls"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
---

# Task: gen_media_content_v1 Phase 8 - BCS Impls (Presets)

## Document Metadata

- Document ID: TASK-20260815-001-08
- Source backlog reference: WI-20260814-001 (gen_media_content_v1 workflow)
- Task IDs covered: WI-20260814-001-08
- Date of generation: 2026-08-15
- Producing workflow: Manual initiation
- Producing agent: default (Kai)
- Prior task: TASK-20260815-001-07 (Phase 7 LLM prompts)

## Task Overview

Create the three BCS implementation preset bundles for gen_media_content_v1: `agnes_full`, `happyhorse_product`, and `video_only`. Each impl has an `impl.yaml` (with prompt_slots and action overrides) and a `preset.json` (with UI dropdown defaults).

Expected outcome: Six files (3 impl.yaml + 3 preset.json) that define valid BCS presets mapping to the correct providers and prompts.

## Detailed Implementation Steps

### Step 1: Create agnes_full impl

Create `workflows/gen_media_content_v1/impls/agnes_full/impl.yaml`:
- prompt_slots: extract_desc -> prompts/extract_desc/standard.txt, generate_prompts -> prompts/generate_prompts/standard.txt
- overrides: generate_images -> generate_images_default, generate_videos -> generate_videos_default

Create `workflows/gen_media_content_v1/impls/agnes_full/preset.json`:
- actions: render_image=agnes_v1, render_video=agnes_v2

### Step 2: Create happyhorse_product impl

Create `workflows/gen_media_content_v1/impls/happyhorse_product/impl.yaml`:
- Same prompt_slots as agnes_full
- Same overrides as agnes_full

Create `workflows/gen_media_content_v1/impls/happyhorse_product/preset.json`:
- actions: render_image=agnes_v1, render_video=happyhorse_v1_1

### Step 3: Create video_only impl

Create `workflows/gen_media_content_v1/impls/video_only/impl.yaml`:
- Same prompt_slots as agnes_full
- Same overrides as agnes_full

Create `workflows/gen_media_content_v1/impls/video_only/preset.json`:
- actions: render_image=__none__, render_video=agnes_v2
- review_images_before_video: false

### Step 4: Create Tests

Create `workflows/gen_media_content_v1/tests/test_impls.py` with tests verifying:

- All 3 impls have impl.yaml and preset.json
- YAML and JSON are valid
- impl names match directory names
- prompt_slots reference files that exist on disk
- preset action names correspond to existing provider directories

## Reference Files

| File | Purpose |
|---|---|
| workflows/agnes_media_gen_v1/impls/agnes_media_v1/impl.yaml | Reference impl.yaml pattern |
| workflows/gen_media_content_v1/workflow.toml | Implementation declarations |
| workflows/gen_media_content_v1/config.json.sample | Config structure for preset defaults |

## Acceptance Criteria

- AC-01: All 3 impl directories contain impl.yaml and preset.json.
- AC-02: All impl.yaml files are valid YAML.
- AC-03: All preset.json files are valid JSON.
- AC-04: impl.yaml name matches directory name for all 3 impls.
- AC-05: All prompt_slots reference files that exist on disk.
- AC-06: agnes_full preset uses agnes_v1 + agnes_v2.
- AC-07: happyhorse_product preset uses agnes_v1 + happyhorse_v1_1.
- AC-08: video_only preset uses __none__ + agnes_v2.
- AC-09: All 10 tests pass with pytest.
- AC-10: No existing files were modified.

## Definition of Done

- 3 impl.yaml files created.
- 3 preset.json files created.
- tests/test_impls.py created with 10 test cases.
- All tests pass.

## Source Reference

- Source requirements: docs/QwenPaw/gen_media_content_v1/REQUIREMENTS.md (Sections 8.1, 8.2)
- Source plan: docs/QwenPaw/gen_media_content_v1/PLAN.md (Phase 8)
- Prior task: TASK-20260815-001-07 (Phase 7 LLM prompts)
