---
template_id: SYS-03-TK
version: "1.0.0"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved task specification document for gen_media_content_v1 Phase 1"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
---

# Task: gen_media_content_v1 Phase 1 - Scaffolding

## Document Metadata

- Document ID: TASK-20260814-001-01
- Source backlog reference: Pending creation (initiating first initiative)
- Task IDs covered: WI-20260814-001-01
- Date of generation: 2026-08-14
- Producing workflow: Manual initiation (first SDLC cycle for gen_media_content_v1)
- Producing agent: default (Kai)

## Task Overview

Create the initial scaffolding for the gen_media_content_v1 workflow package. This is the foundation task that establishes the directory structure, workflow.toml manifest, context extensions, and sample configuration files. No implementation code is produced in this phase -- only the structural skeleton that subsequent tasks will build upon.

Expected outcome: A valid, parseable workflow package that can be loaded by the agent-runner-v2 workflow system, with all files passing basic syntax validation.

## Detailed Implementation Steps

### Step 1: Create Directory Structure

Create the following directory structure under workflows/gen_media_content_v1/ with __init__.py (empty file) in each directory:

```
workflows/gen_media_content_v1/
prompts/
prompts/extract_desc/
prompts/generate_prompts/
api_actions/
api_actions/render_image/
api_actions/render_video/
impls/
impls/agnes_full/
impls/happyhorse_product/
impls/video_only/
tests/
```

Expected result: All directories exist with __init__.py files.

### Step 2: Create workflow.toml

Read workflows/agnes_media_gen_v1/workflow.toml as reference for the exact TOML structure, field names, and conventions. Create a new workflow.toml for gen_media_content_v1 with:

- workflow header: name="gen_media_content_v1", version="1.0.0", label="Media Content Generation v1", job_prefix="MEDIA", visibility="canonical", init_step="extract_descriptions"
- 3 implementations declared under [[workflow.implementation]]: agnes_full, happyhorse_product, video_only
- Steps defined as [[step]] blocks:
  1. extract_descriptions -- prompt-driven, uses "{{ slot.extract_desc }}", produces IMAGE_DESCRIPTIONS, coder role_policy="architect_standard", on_reject_refine to itself
  2. archive_step_00 -- action archive_inputs, source_dir=step_00_inputimage, archive_dir=step_00_inputimage_archive, index_file=step_01_imagedesc/index.json
  3. generate_prompts -- prompt-driven, uses "{{ slot.generate_prompts }}", produces PROMPT_VARIANTS, coder role_policy="image_video", on_reject_refine to itself
  4. archive_step_01 -- action archive_inputs, source_dir=step_01_imagedesc, archive_dir=step_01_imagedesc_archive
  5. generate_images -- action, uses generate_images_default, requires_human_approval_after=true, produces IMAGE_INDEX
  6. archive_step_02 -- action archive_inputs, source_dir=step_02_promptvariant, archive_dir=step_02_promptvariant_archive, index_file=step_03_generatedimage/index.json
  7. generate_videos -- action, uses generate_videos_default, produces VIDEO_INDEX
  8. archive_step_03 -- action archive_inputs, source_dir=step_03_generatedimage, archive_dir=step_03_generatedimage_archive
  9. stepCompletion -- action step_completion

Expected result: A valid TOML file that parses without errors, following the same structure as agnes_media_gen_v1/workflow.toml.

### Step 3: Create context_extensions.py

Read workflows/agnes_media_gen_v1/context_extensions.py as reference for the exact class structure, imports, and method patterns. Create a new context_extensions.py that extends the workflow context with:

- STEP_00_DIR -> {workspace_root}/step_00_inputimage
- STEP_01_DIR -> {workspace_root}/step_01_imagedesc
- STEP_02_DIR -> {workspace_root}/step_02_promptvariant
- STEP_03_DIR -> {workspace_root}/step_03_generatedimage
- STEP_04_DIR -> {workspace_root}/step_04_generatedvideo
- MEDIA_CONFIG -> {workspace_root}/config.json

Follow the exact same class structure, imports, and method patterns as the reference file. The class should inherit from BaseWorkflowExtensions (or whatever the reference uses) and implement the extend_context() method returning a dict of key -> value mappings.

Expected result: A valid Python file with no syntax errors, following the same patterns as the reference.

### Step 4: Create config.json.sample

Create a sample config.json file at workflows/gen_media_content_v1/config.json.sample with the following structure:

```json
{
  "prompts": {
    "extract_desc": "standard",
    "generate_prompts": "standard"
  },
  "actions": {
    "render_image": "agnes_v1",
    "render_video": "happyhorse_v1_1"
  },
  "review_images_before_video": true,
  "api": {
    "agnes_v1": {
      "model": "agnes-image-2.1-flash",
      "size": "1024x1024",
      "ratio": "1:1"
    },
    "agnes_v2": {
      "model": "agnes-video-v2.0",
      "width": 1024,
      "height": 576,
      "num_frames": 72,
      "frame_rate": 24
    },
    "happyhorse_v1_1": {
      "model": "happyhorse-1.1-i2v",
      "resolution": "480P",
      "ratio": "9:16",
      "duration": 15
    }
  },
  "num_variants": 4,
  "max_concurrent": 2,
  "process_delay": 15,
  "coder_timeout": 900,
  "api_timeout": 500,
  "api_max_retries": 5,
  "retry_base_wait": 5
}
```

Expected result: A valid JSON file that parses without errors.

### Step 5: Create .env.sample

Create a .env.sample file at workflows/gen_media_content_v1/.env.sample with:

```
# Agnes API (image + video)
AGNES_API_KEY_1=your_api_key_here
AGNES_BASE_URL=https://apihub.agnes-ai.com

# HappyHorse API (DashScope-based video generation)
HAPPYHORSE_API_KEY_1=your_api_key_here
HAPPYHORSE_BASE_URL=https://dashscope.aliyuncs.com
```

Expected result: A valid .env format file with placeholder values and descriptive comments.

### Step 6: Create README.md

Create a brief README.md at workflows/gen_media_content_v1/README.md describing:

- What the workflow does (unified media generation with pluggable prompts and API providers)
- Directory structure overview
- How to configure (config.json, .env)
- How to select implementations

Expected result: A valid Markdown file with clear documentation.

### Step 7: Create tests/test_context.py

Create unit tests at workflows/gen_media_content_v1/tests/test_context.py that verify context_extensions.py produces the expected keys. Test that:

- All 5 STEP_*_DIR keys are present
- MEDIA_CONFIG key is present
- Paths are constructed correctly from workspace_root

Follow the test patterns in existing workflow tests (e.g., tests/unit/ directory patterns in agent-runner-v2).

Expected result: A valid Python test file with no syntax errors.

## Technical Specifications

- All file paths are relative to agent-runner-v2 project root (D:\MyProjectSpace\01_Workflows\agent-runner-v2).
- Do NOT modify any existing workflow files. Only create new files under workflows/gen_media_content_v1/.
- All Python files must be valid and parseable (no syntax errors).
- All TOML files must be valid and parseable.
- All JSON files must be valid and parseable.
- Follow the exact same patterns, conventions, and code style as existing workflow packages (agnes_media_gen_v1, agnes_gen_video_v1).

## Test Requirements

- Unit test for context_extensions.py (test_context.py) verifying all expected keys are produced.
- All files must pass basic syntax validation (Python files parse, TOML parses, JSON parses).

## Acceptance Criteria

- AC-01: All directories exist with __init__.py files.
- AC-02: workflow.toml is valid TOML and declares all 9 steps and 3 implementations.
- AC-03: context_extensions.py is valid Python and produces all 6 context keys.
- AC-04: config.json.sample is valid JSON with all required sections (prompts, actions, api, settings).
- AC-05: .env.sample is valid format with all required environment variables.
- AC-06: README.md exists with workflow description, directory structure, and configuration instructions.
- AC-07: tests/test_context.py is valid Python with tests for all expected keys.
- AC-08: No existing files were modified.

## Definition of Done

- All files created under workflows/gen_media_content_v1/.
- All Python files parse without errors.
- workflow.toml parses without errors.
- config.json.sample parses without errors.
- tests/test_context.py runs and passes.
- No existing files were modified.
- Code follows the same patterns as reference workflows.

## Source Reference

- Source requirements: docs/QwenPaw/gen_media_content_v1/REQUIREMENTS.md
- Source plan: docs/QwenPaw/gen_media_content_v1/PLAN.md
- Reference workflows: workflows/agnes_media_gen_v1/, workflows/agnes_gen_video_v1/
