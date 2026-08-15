# Phase 1: gen_media_content_v1 — Scaffolding

You are implementing Phase 1 of `gen_media_content_v1`, a new workflow package for agent-runner-v2.

**CRITICAL: Do NOT modify any existing workflow files.** Create everything under `workflows/gen_media_content_v1/`.

## Reference

Read these existing workflows to follow the exact same patterns:
- `workflows/agnes_media_gen_v1/workflow.toml`
- `workflows/agnes_media_gen_v1/context_extensions.py`
- `workflows/agnes_gen_video_v1/workflow.toml`

## Deliverables

### 1. Directory Structure

Create these directories with `__init__.py` (empty) in each:

```
workflows/gen_media_content_v1/
├── prompts/
│   ├── extract_desc/__init__.py
│   └── generate_prompts/__init__.py
├── api_actions/
│   ├── render_image/__init__.py
│   └── render_video/__init__.py
├── impls/
│   ├── agnes_full/__init__.py
│   ├── happyhorse_product/__init__.py
│   └── video_only/__init__.py
└── tests/__init__.py
```

### 2. workflow.toml

Read `agnes_media_gen_v1/workflow.toml` as reference. Create a new workflow.toml for `gen_media_content_v1` with:

- **workflow header**: name="gen_media_content_v1", version="1.0.0", label="Media Content Generation v1", job_prefix="MEDIA", visibility="canonical", init_step="extract_descriptions"
- **3 implementations**: agnes_full, happyhorse_product, video_only (under `[[workflow.implementation]]`)
- **Steps**:
  1. `extract_descriptions` — prompt-driven, uses `{{ slot.extract_desc }}`, produces IMAGE_DESCRIPTIONS, coder role_policy="architect_standard", on_reject_refine to itself
  2. `archive_step_00` — action archive_inputs, source_dir=step_00_inputimage, archive_dir=step_00_inputimage_archive, index_file=step_01_imagedesc/index.json
  3. `generate_prompts` — prompt-driven, uses `{{ slot.generate_prompts }}`, produces PROMPT_VARIANTS, coder role_policy="image_video", on_reject_refine to itself
  4. `archive_step_01` — action archive_inputs, source_dir=step_01_imagedesc, archive_dir=step_01_imagedesc_archive
  5. `generate_images` — action, uses `generate_images_default`, requires_human_approval_after=true, produces IMAGE_INDEX
  6. `archive_step_02` — action archive_inputs, source_dir=step_02_promptvariant, archive_dir=step_02_promptvariant_archive, index_file=step_03_generatedimage/index.json
  7. `generate_videos` — action, uses `generate_videos_default`, produces VIDEO_INDEX
  8. `archive_step_03` — action archive_inputs, source_dir=step_03_generatedimage, archive_dir=step_03_generatedimage_archive
  9. `stepCompletion` — action step_completion

### 3. context_extensions.py

Read `agnes_media_gen_v1/context_extensions.py` as reference. Create a new context_extensions.py that extends context with:

- `STEP_00_DIR` → `{workspace_root}/step_00_inputimage`
- `STEP_01_DIR` → `{workspace_root}/step_01_imagedesc`
- `STEP_02_DIR` → `{workspace_root}/step_02_promptvariant`
- `STEP_03_DIR` → `{workspace_root}/step_03_generatedimage`
- `STEP_04_DIR` → `{workspace_root}/step_04_generatedvideo`
- `MEDIA_CONFIG` → `{workspace_root}/config.json`

Follow the exact same class structure, imports, and method patterns as the reference.

### 4. config.json.sample

Create a sample config.json with:

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

### 5. .env.sample

Create a .env.sample with:

```
# Agnes API (image + video)
AGNES_API_KEY_1=your_api_key_here
AGNES_BASE_URL=https://apihub.agnes-ai.com

# HappyHorse API (DashScope-based video generation)
HAPPYHORSE_API_KEY_1=your_api_key_here
HAPPYHORSE_BASE_URL=https://dashscope.aliyuncs.com
```

### 6. README.md

Create a brief README.md describing:
- What the workflow does (unified media generation with pluggable prompts and API providers)
- Directory structure overview
- How to configure (config.json, .env)
- How to select implementations

### 7. tests/test_context.py

Create unit tests that verify context_extensions.py produces the expected keys. Follow the test patterns in existing workflow tests. Test that:
- All 5 STEP_*_DIR keys are present
- MEDIA_CONFIG key is present
- Paths are constructed correctly from workspace_root

## Progress Reporting (MANDATORY)

As you work, write a JSONL progress file to:
`C:\Users\kengk\.ukbe-runner\jobs\20260814\gen_media_content_v1\PHASE1\progress\status.jsonl`

Append one JSON line per milestone:
```jsonl
{"timestamp": "2026-08-14T10:00:00", "phase": "Phase 1", "status": "started", "milestone": "reading reference files"}
{"timestamp": "2026-08-14T10:05:00", "phase": "Phase 1", "status": "in_progress", "milestone": "created directory structure"}
{"timestamp": "2026-08-14T10:10:00", "phase": "Phase 1", "status": "in_progress", "milestone": "created workflow.toml"}
...
{"timestamp": "2026-08-14T10:30:00", "phase": "Phase 1", "status": "completed", "milestone": "all files created", "files_count": 20}
```

Milestones to report:
1. Started / reading reference files
2. Each deliverable completed (directory structure, workflow.toml, context_extensions.py, etc.)
3. Validation passed / failed
4. All done

Create the directory first if it doesn't exist.

## Validation

After creating all files:
- Verify workflow.toml is valid TOML
- Verify config.json.sample is valid JSON
- Verify .env.sample has the correct format
- Verify context_extensions.py has no syntax errors
- Verify tests/test_context.py has no syntax errors
