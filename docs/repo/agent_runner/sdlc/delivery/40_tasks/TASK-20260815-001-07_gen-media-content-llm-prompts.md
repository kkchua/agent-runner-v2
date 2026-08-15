---
template_id: SYS-03-TK
version: "1.0.0"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved task specification for gen_media_content_v1 Phase 7 LLM prompts"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
---

# Task: gen_media_content_v1 Phase 7 - LLM Prompts

## Document Metadata

- Document ID: TASK-20260815-001-07
- Source backlog reference: WI-20260814-001 (gen_media_content_v1 workflow)
- Task IDs covered: WI-20260814-001-07
- Date of generation: 2026-08-15
- Producing workflow: Manual initiation
- Producing agent: default (Kai)
- Prior task: TASK-20260815-001-06 (Phase 6 __none__ provider)

## Task Overview

Create the LLM prompt templates for the two prompt-driven steps in gen_media_content_v1: `extract_desc` and `generate_prompts`. These prompts are adapted from the existing agnes_media_gen_v1 workflow prompts, with hardcoded paths replaced by slot placeholders.

Expected outcome: Two prompt files under `prompts/` that render correctly when slot variables are substituted, plus tests verifying placeholder presence.

## Detailed Implementation Steps

### Step 1: Create extract_desc Prompt

Create `workflows/gen_media_content_v1/prompts/extract_desc/standard.txt`:

Adapt from `workflows/agnes_media_gen_v1/impls/agnes_media_v1/prompts/step_1_extract/standard.txt`.

Key requirements:
- Scan `{STEP_00_DIR}` for PNG/JPG/WEBP images
- Use vision to produce structured JSON descriptions per image
- Extract 9 attribute groups: subject, scene, composition, lighting, style, color, mood, motion_potential, extraction_confidence
- Write individual JSONs to `{STEP_01_DIR}` plus `index.json`
- Report `IMAGE_DESCRIPTIONS` artifact
- Replace all hardcoded paths with slot placeholders: `{STEP_00_DIR}`, `{STEP_01_DIR}`, `{MEDIA_CONFIG}`, `{GOVERNANCE_RUNTIME_ROOT}`, `{PLATFORM_RUNTIME_ROOT}`

### Step 2: Create generate_prompts Prompt

Create `workflows/gen_media_content_v1/prompts/generate_prompts/standard.txt`:

Adapt from `workflows/agnes_media_gen_v1/impls/agnes_media_v1/prompts/step_2_generate/standard.txt`.

Key requirements:
- Read description JSONs from `{STEP_01_DIR}` (NOT from index.json)
- Produce N variants per image (controlled by `num_variants` in `{MEDIA_CONFIG}`)
- Each variant: `t2i_prompt1`, `t2v_prompt1`, `negative_prompt_video`, `image_filename`, `image_url`
- Enforce photorealistic-only style
- Three-layer video prompt defense (Golden Rule + Forbidden Verbs + Scene Triggers)
- Output to `{STEP_02_DIR}` with `index.json`

### Step 3: Create Tests

Create `workflows/gen_media_content_v1/tests/test_prompt_slots.py` with tests verifying:

- Both prompt files exist at correct paths
- extract_desc contains `{STEP_00_DIR}` and `{STEP_01_DIR}` placeholders
- generate_prompts contains `{STEP_01_DIR}`, `{STEP_02_DIR}`, `{MEDIA_CONFIG}` placeholders
- Both files have meaningful content (>100 chars)

## Reference Files

| File | Purpose |
|---|---|
| workflows/agnes_media_gen_v1/impls/agnes_media_v1/prompts/step_1_extract/standard.txt | Source prompt for extract_desc |
| workflows/agnes_media_gen_v1/impls/agnes_media_v1/prompts/step_2_generate/standard.txt | Source prompt for generate_prompts |
| workflows/gen_media_content_v1/context_extensions.py | Available context variables |
| workflows/gen_media_content_v1/workflow.toml | Slot names (extract_desc, generate_prompts) |

## Acceptance Criteria

- AC-01: prompts/extract_desc/standard.txt exists and is valid UTF-8.
- AC-02: prompts/generate_prompts/standard.txt exists and is valid UTF-8.
- AC-03: extract_desc prompt contains {STEP_00_DIR} placeholder.
- AC-04: extract_desc prompt contains {STEP_01_DIR} placeholder.
- AC-05: generate_prompts prompt contains {STEP_01_DIR} and {STEP_02_DIR} placeholders.
- AC-06: generate_prompts prompt contains {MEDIA_CONFIG} placeholder.
- AC-07: No hardcoded absolute paths in either prompt.
- AC-08: All 9 tests pass with pytest.
- AC-09: No existing files were modified.

## Definition of Done

- prompts/extract_desc/standard.txt created.
- prompts/generate_prompts/standard.txt created.
- tests/test_prompt_slots.py created with 9 test cases.
- All tests pass.

## Source Reference

- Source requirements: docs/QwenPaw/gen_media_content_v1/REQUIREMENTS.md (Section 5)
- Source plan: docs/QwenPaw/gen_media_content_v1/PLAN.md (Phase 7)
- Prior task: TASK-20260815-001-06 (Phase 6 __none__ provider)
