---
doc_type: "artifact_contract"
lifecycle_status: "draft"
effective_version: "WFBUILD-20260725-61c44baa"
workflow_name: "agnes_media_gen_v1"
job_id: "WFBUILD-20260725-61c44baa"
slug: "agnes_media_gen_v1"
source_requirements: "docs/repo/workflow_builder/runs/WFBUILD-20260725-61c44baa/REQUIREMENTS-20260726-001_media_gen_v1.md"
---

# Artifact Contract: Agnes Media Generation v1

## Artifact Key Summary

| Key | Path Pattern | Description | Required |
|---|---|---|---|
| IMAGE_DESCRIPTIONS | step_01/index.json | Index manifest of structured image description JSON files produced by extract_descriptions step | yes |
| PROMPT_VARIANTS | step_02/index.json | Index manifest of prompt variant JSON files produced by generate_prompts step | yes |
| IMAGE_INDEX | step_03/index.json | Index manifest of generated images and updated JSONs produced by generate_images step | yes |
| VIDEO_INDEX | step_04/index.json | Index manifest of generated video files produced by generate_videos step | yes |
| MEDIA_CONFIG | config.json | Media generation configuration file (JSON) providing image/video parameters, variant counts, delays, timeouts, and retry limits | yes |
| REVIEW_FILE_SUGGESTED | docs/repo/agnes_media_gen_v1/runs/{job_id}/REVIEW-{date}-{seq}_{slug}.md | Review document summarizing workflow execution status, errors, and partial results for human operator approval | no |

## Input Artifacts

The workflow declares no SDLC input artifacts consumed via required_inputs or optional_inputs in workflow.toml. All runtime inputs are resolved as context variables by context_extensions.py from the target repository root at job start time.

Runtime context variables (resolved by context_extensions.py, not SDLC artifact inputs):

- STEP_00_DIR: Absolute path to step_00/ where operator places input images (PNG, JPG, WEBP)
- STEP_00_ARCHIVE: Absolute path to step_00_archive/ for archiving processed input images
- STEP_01_DIR: Absolute path to step_01/ for structured description JSON files
- STEP_01_ARCHIVE: Absolute path to step_01_archive/ for archiving processed description JSONs
- STEP_02_DIR: Absolute path to step_02/ for prompt variant JSON files
- STEP_02_ARCHIVE: Absolute path to step_02_archive/ for archiving processed variant JSONs
- STEP_03_DIR: Absolute path to step_03/ for generated images and updated JSONs with image_url
- STEP_03_ARCHIVE: Absolute path to step_03_archive/ for archiving processed step_03 inputs
- STEP_04_DIR: Absolute path to step_04/ for generated video files
- STEP_04_ARCHIVE: Absolute path to step_04_archive/ for archiving processed step_04 inputs
- MEDIA_CONFIG: Absolute path to the media generation configuration file (JSON format)
- GOVERNANCE_RUNTIME_ROOT: Layer 1 governance documentation root (standard runtime variable)
- PLATFORM_RUNTIME_ROOT: Layer 2 platform documentation root (standard runtime variable)

Environment variables loaded from .env at runtime:

- AGNES_API_KEY: API key for Agnes services
- AGNES_BASE_URL: Base URL for Agnes API endpoints

## Output Artifacts

### IMAGE_DESCRIPTIONS

Produced by: extract_descriptions step (step_01)

Content: Index file (index.json) listing all per-image structured description JSON files. Each entry maps an input image path to its corresponding output description JSON path. The index structure contains:

```json
{
  "step": "extract_descriptions",
  "files": [
    {"input": "step_00/image.png", "output": "step_01/image.json"}
  ]
}
```

Each referenced output JSON contains a structured description with 9 attribute groups (subject_attributes, scene_attributes, composition_attributes, lighting_attributes, style_attributes, color_attributes, mood_attributes, motion_potential, extraction_confidence) totaling approximately 49 fields. File naming: {image_stem}.json matching the input image stem.

### PROMPT_VARIANTS

Produced by: generate_prompts step (step_02)

Content: Index file (index.json) listing all per-image prompt variant JSON files. Each entry maps an input description file path to its corresponding output variant JSON path. The index structure contains:

```json
{
  "step": "generate_prompts",
  "files": [
    {"input": "step_01/image.json", "output": "step_02/image.json"}
  ]
}
```

Each referenced output JSON contains a mode identifier, subject identifier, and an array of variant objects (count from config, default 4). Each variant contains t2i_prompt1 (detailed text prompt), image_filename ({stem}_NN.png pattern), and image_url (populated by step_03).

### IMAGE_INDEX

Produced by: generate_images step (step_03)

Content: Index file (index.json) listing all generated images and updated JSON files. Each entry maps an input variant file path to its corresponding output image and updated JSON paths. The index structure contains:

```json
{
  "step": "generate_images",
  "files": [
    {
      "input": "step_02/image.json",
      "output": "step_03/image_01.png",
      "updated_json": "step_03/image.json"
    }
  ]
}
```

Each generated image filename matches the pattern {stem}_NN.png where NN is two-digit zero-padded variant number. The workflow calls Agnes Image 2.1 Flash API with batch processing and retry logic for 503 errors. Output images are downloaded to step_03/ and corresponding JSON files are updated with image_url field.

### VIDEO_INDEX

Produced by: generate_videos step (step_04)

Content: Index file (index.json) listing all generated video files. Each entry maps an input image path to its corresponding output video path. The index structure contains:

```json
{
  "step": "generate_videos",
  "files": [
    {"input": "step_03/image_01.png", "output": "step_04/image_01.mp4"}
  ]
}
```

The workflow calls Agnes Video V2.0 API with submission, status polling, and download. Video generation uses the t2i_prompt1 from the variant JSON as the motion prompt and the generated image URL as the source. Output videos are downloaded to step_04/ with filenames matching the input image stem.

### MEDIA_CONFIG

Produced by: workflow initialization (operator-provided configuration file)

Content: Media generation configuration file in JSON format providing parameter groups for image generation (model, size, ratio), video generation (model, width, height, num_frames, frame_rate), workflow behavior (num_variants default 4, process_delay default 15 seconds, coder_timeout default 900 seconds, api_timeout default 500 seconds, api_max_retries default 5). Filename: config.json (per existing implementation pattern). The context variable MEDIA_CONFIG resolves to the absolute path of this file.

### REVIEW_FILE_SUGGESTED

Produced by: human review gate steps (one per workflow step)

Content: Review document summarizing execution status for the current step. Includes step name, success/failure counts, specific error messages for failed items, partial results manifest, and recommendation for operator decision (approve to advance or reject to rerun). Format: Markdown with YAML frontmatter. Used by the human operator to inspect step results before approving or rejecting.

## Shared Artifacts

The workflow uses the following framework-level artifact keys defined in agent_runner_v2/constants.py and agent_runner_v2/artifact_keys.py:

- REVIEW_FILE_SUGGESTED: Standard review artifact key used by the human review gate mechanism. The workflow produces this artifact after each step execution to support the requires_human_approval_after = true routing pattern. Path pattern follows the workflow_builder_v1 convention with date, sequence number, and slug placeholders.

No other shared artifact keys from the core SDLC chain (REQ_FILE, PLAN_FILE, TASK_FILE, etc.) are used by this workflow. The workflow operates in its own artifact namespace under docs/repo/agnes_media_gen_v1/.

## Naming Rationale

### Artifact Key Names

All artifact keys use UPPER_SNAKE_CASE as required by the workflow framework conventions. Key naming choices:

- IMAGE_DESCRIPTIONS, PROMPT_VARIANTS, IMAGE_INDEX, VIDEO_INDEX: Descriptive names reflecting the content type and step that produces them. These names match the Output Artifacts table in the source specification exactly.

- MEDIA_CONFIG: Key name for the media configuration file. The on-disk filename is config.json (per existing implementation). The key name MEDIA_CONFIG clearly identifies the purpose of the file without ambiguity.

- REVIEW_FILE_SUGGESTED: Standard framework-level key name defined in agent_runner_v2/constants.py. Not redefined or renamed for this workflow. Ensures compatibility with the human review gate mechanism and workflow routing logic.

### Path Pattern Conventions

Output artifacts follow two distinct path patterns:

Runtime step artifacts (IMAGE_DESCRIPTIONS, PROMPT_VARIANTS, IMAGE_INDEX, VIDEO_INDEX):
- Base directory: step_XX/ (where XX is the step number 01-04)
- Filename: index.json (fixed name, overwritten each run)
- Historical tracking: Archive pattern copies processed files to step_XX_archive/
- These paths are relative to the target repository root, not the workflow_builder run directory
- All paths resolved to absolute by context_extensions.py using get_workspace_root()

Review artifacts (REVIEW_FILE_SUGGESTED):
- Base directory: docs/repo/{workflow_name}/runs/{job_id}/
- Filename prefix: REVIEW-
- Date component: {date} placeholder resolved to YYYYMMDD format at runtime
- Sequence number: {seq} placeholder resolved by resolve_next_seq() to prevent overwrites
- Slug component: {slug} extracted from input specification filename
- File extension: .md

Media configuration (MEDIA_CONFIG):
- Base directory: target repository root
- Filename: config.json (fixed name)
- This is an input artifact provided by the operator before workflow execution

Path patterns use forward slashes (/) as directory separators even on Windows, per framework convention.

### Collision Avoidance

Artifact keys IMAGE_DESCRIPTIONS, PROMPT_VARIANTS, IMAGE_INDEX, VIDEO_INDEX are unique to this workflow. No existing workflow in the core SDLC chain uses these keys. Verified against agent_runner_v2/artifact_keys.py. Note: A prior build run (WFBUILD-20260725-0bb6afa4) used these same keys, confirming the naming convention for this workflow type.

MEDIA_CONFIG: Used as the configuration file artifact key. The existing implementation maps this to config.json at the target repository root. No collision with core SDLC artifact keys.

REVIEW_FILE_SUGGESTED is a shared framework key defined in agent_runner_v2/constants.py. All workflows that implement human review gates use this key. The path pattern includes {job_id} to ensure uniqueness across concurrent workflow executions.
