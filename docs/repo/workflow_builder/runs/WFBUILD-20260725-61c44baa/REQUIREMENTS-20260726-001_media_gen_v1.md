---
doc_type: "workflow_design"
lifecycle_status: "draft"
effective_version: "WFBUILD-20260725-61c44baa"
workflow_name: "agnes_media_gen_v1"
job_id: "WFBUILD-20260725-61c44baa"
slug: "agnes_media_gen_v1"
source_spec: "docs/repo/workflow_builder/specs/agnes_media_gen_v1.md"
---

# Workflow Requirements: Agnes Media Generation v1

## Overview

Agnes Media Generation v1 is an end-to-end media creation pipeline that
transforms raw images into animated videos. The workflow extracts structured
image descriptions via LLM vision, generates multiple prompt variants per
description, calls the Agnes Image 2.1 Flash API to produce new images from
those prompts, and then calls the Agnes Video V2.0 API to generate
image-to-video animations. Each step includes a human review gate where the
operator can approve (advance to next step) or reject (rerun the same step).
The workflow defines its own folder structure (step_00/ through step_04/
with corresponding _archive/ folders) and can run in any repository that
provides this structure.

## Workflow Type

Mixed.

Justification: The workflow contains both prompt-driven steps and
action-driven steps:

- Prompt-driven steps: extract_descriptions (LLM vision to produce
  structured JSON descriptions from images) and generate_prompts (LLM
  to produce N prompt variants per description).
- Action-driven steps: generate_images (Python action calling Agnes
  Image 2.1 Flash API with batch processing and retry logic) and
  generate_videos (Python action calling Agnes Video V2.0 API with
  polling and download). The terminal step (step_completion) is also
  an action.

The spec explicitly confirms this classification.

## Input Artifacts

The specification states there are no user-provided input artifacts
consumed via the SDLC artifact mechanism. All runtime inputs are resolved
as context variables by context_extensions.py from the target repository
root, not declared as required_inputs or optional_inputs in workflow.toml.

The following table documents the runtime context variables that the
workflow depends on. These are NOT artifact inputs in the SDLC sense;
they are environment-level paths resolved at runtime.

| Context Variable | Description | Required/Optional |
|---|---|---|
| STEP_00_DIR | Absolute path to step_00/ where user places input images | Required |
| STEP_00_ARCHIVE | Absolute path to step_00_archive/ for processed images | Required |
| STEP_01_DIR | Absolute path to step_01/ for description JSONs | Required |
| STEP_01_ARCHIVE | Absolute path to step_01_archive/ | Required |
| STEP_02_DIR | Absolute path to step_02/ for variant JSONs | Required |
| STEP_02_ARCHIVE | Absolute path to step_02_archive/ | Required |
| STEP_03_DIR | Absolute path to step_03/ for generated images and JSONs | Required |
| STEP_03_ARCHIVE | Absolute path to step_03_archive/ | Required |
| STEP_04_DIR | Absolute path to step_04/ for generated videos | Required |
| STEP_04_ARCHIVE | Absolute path to step_04_archive/ | Required |
| MEDIA_CONFIG | Absolute path to the media configuration file | Required |
| GOVERNANCE_RUNTIME_ROOT | Layer 1 governance docs (standard) | Required |
| PLATFORM_RUNTIME_ROOT | Layer 2 platform docs (standard) | Required |

Environment variables loaded from .env:

| Variable | Description | Required/Optional |
|---|---|---|
| AGNES_API_KEY | API key for Agnes services | Required |
| AGNES_BASE_URL | Base URL for Agnes API endpoints | Required |

## Output Artifacts

| Artifact Key | Description | Required/Optional |
|---|---|---|
| IMAGE_DESCRIPTIONS | Index file (index.json) in step_01/ listing all
  per-image structured description JSON files produced by the
  extract_descriptions step | Required |
| PROMPT_VARIANTS | Index file (index.json) in step_02/ listing all
  per-image prompt variant JSON files produced by the
  generate_prompts step | Required |
| IMAGE_INDEX | Index file (index.json) in step_03/ listing all
  generated images and updated JSON files produced by the
  generate_images step | Required |
| VIDEO_INDEX | Index file (index.json) in step_04/ listing all
  generated video files produced by the generate_videos step | Required |

Each index.json contains a manifest of all files produced by its step,
with metadata about input-to-output file mapping. Output filenames
match input image filenames (stem-based mapping). Example index structure:

```
{
  "step": "<step_name>",
  "files": [
    {"input": "step_XX/filename.ext", "output": "step_YY/filename.json"}
  ]
}
```

All four artifact keys (IMAGE_DESCRIPTIONS, PROMPT_VARIANTS, IMAGE_INDEX,
VIDEO_INDEX) are traceable to the specification's Output Artifacts table.
No inferred or unsupported artifact keys are included.

## Constraints

### Governance Layer

- Layer 1 (governance) and Layer 2 (platform constitution) documents
  are read-only authority. This workflow must not redefine or contradict
  them.
- The workflow references GOVERNANCE_RUNTIME_ROOT and
  PLATFORM_RUNTIME_ROOT as standard runtime context variables.
- The workflow package lives under workflows/agnes_media_gen_v1/ in the
  agent-runner-v2 repository.

### Naming Conventions

- Artifact keys use UPPER_SNAKE_CASE (e.g., IMAGE_DESCRIPTIONS,
  PROMPT_VARIANTS, IMAGE_INDEX, VIDEO_INDEX).
- Workflow slug is agnes_media_gen_v1, which must match:
  - The directory name under workflows/
  - The name field in workflow.toml
  - The workflow_name attribute in context_extensions.py
- Job prefix is AMGEN.
- Per-run design documents follow the naming pattern:
  {TYPE}-{YYYYMMDD}-{seq}_{slug}.md
- Prompt files follow the pattern: {NN}_{step_name}.txt

### External Dependencies

- Agnes Image 2.1 Flash API for image generation.
- Agnes Video V2.0 API for image-to-video generation.
- LLM with vision capability for image description extraction.
- LLM for prompt variant generation.
- .env file providing AGNES_API_KEY and AGNES_BASE_URL.
- Configuration file providing image/video parameters, variant counts,
  delays, timeouts, and retry limits.

### Role Policies

- Prompt-driven steps (extract_descriptions, generate_prompts) use
  the architect_standard role policy.
- Action steps do not require role policies.

### Behavioral Constraints

- Human review gate on every step (requires_human_approval_after = true).
- On reject, rerun the same step (on_reject_refine self-reference).
- API calls must include retry logic for 503 errors with exponential
  backoff.
- Configurable process_delay between API calls.
- Archive pattern: each step copies processed inputs to the
  corresponding _archive/ folder and removes them from the input folder.
- Action code must be generated fresh (not reused from existing skill
  scripts).

## Context Variables

The following context variables are declared in the specification and
must be resolved by context_extensions.py at runtime. These are
variable names and their purposes -- resolved file paths are handled
by the define_artifacts step.

| Variable | Purpose |
|---|---|
| STEP_00_DIR | Absolute path to step_00/ directory where user places input images (PNG, JPG, WEBP) |
| STEP_00_ARCHIVE | Absolute path to step_00_archive/ directory for archiving processed input images |
| STEP_01_DIR | Absolute path to step_01/ directory for structured description JSON files |
| STEP_01_ARCHIVE | Absolute path to step_01_archive/ directory for archiving processed description JSONs |
| STEP_02_DIR | Absolute path to step_02/ directory for prompt variant JSON files |
| STEP_02_ARCHIVE | Absolute path to step_02_archive/ directory for archiving processed variant JSONs |
| STEP_03_DIR | Absolute path to step_03/ directory for generated images and updated JSONs with image_url |
| STEP_03_ARCHIVE | Absolute path to step_03_archive/ directory for archiving processed step_03 inputs |
| STEP_04_DIR | Absolute path to step_04/ directory for generated video files |
| STEP_04_ARCHIVE | Absolute path to step_04_archive/ directory for archiving processed step_04 inputs |
| MEDIA_CONFIG | Absolute path to the media generation configuration file (JSON format) |
| GOVERNANCE_RUNTIME_ROOT | Layer 1 governance documentation root (standard runtime variable) |
| PLATFORM_RUNTIME_ROOT | Layer 2 platform documentation root (standard runtime variable) |

## Data Schemas

The specification defines two structured JSON schemas for intermediate
outputs. Below is a summary of each schema's structure and key fields.

### Image Description JSON (step_01 output)

Produced by the extract_descriptions step. One JSON file per input image.
File naming: {image_stem}.json (matching the input image stem).

Top-level fields (2):
- image_filename: Original input image filename
- image_stem: Filename without extension, used for output naming
- descriptions: Array of description objects (one entry per image)

Each description object contains 9 attribute groups:

1. subject_attributes (6 fields): main_subject, subject_type,
   subject_description, distinctive_features (array),
   recognizable_objects (array), subject_state_or_pose
2. scene_attributes (9 fields): setting, environment, foreground,
   midground, background, time_of_day, season_or_weather,
   spatial_depth, parallax_potential
3. composition_attributes (7 fields): orientation, framing,
   camera_angle, subject_position, negative_space, visual_flow,
   depth_layers (array)
4. lighting_attributes (6 fields): lighting_type, light_direction,
   light_quality, color_temperature, shadow_highlight_behavior,
   atmospheric_lighting
5. style_attributes (5 fields): visual_style, medium,
   realism_level, texture_quality, rendering_treatment
6. color_attributes (4 fields): dominant_colors (array),
   accent_colors (array), color_contrast, palette_mood
7. mood_attributes (3 fields): emotional_tone, atmosphere,
   viewer_feeling
8. motion_potential (7 fields): primary_motion_candidate,
   subject_motion_candidates (array),
   environmental_motion_candidates (array),
   camera_motion_candidates (array),
   motion_intensity_suggestion, motion_pacing_suggestion,
   motion_constraints (array)
9. extraction_confidence (2 fields): overall_confidence,
   uncertain_attributes (array)

Total: approximately 49 fields across 9 attribute groups.

### Prompt Variant JSON (step_02 output)

Produced by the generate_prompts step. One JSON file per input image.
File naming: {image_stem}.json (matching the description file stem).

Top-level fields (3):
- mode: Workflow mode identifier (e.g., "BASE")
- subject: Image stem identifier
- variations: Array of variant objects (count from config, default 4)

Each variant object contains 3 fields:
- t2i_prompt1: Detailed text prompt used for both image generation
  (step_03) and video motion (step_04)
- image_filename: Output image filename pattern ({stem}_NN.png)
- image_url: URL to generated image (empty after step_02, populated
  by step_03)

Total: 6 fields across top-level and variant structure.

### Index File Structure (all steps)

Each step produces an index.json file with this structure:
- step: Step name identifier
- files: Array of file mapping objects, each containing:
  - input: Source file path
  - output: Output file path

## Implementation Notes

The specification references several legacy artifacts and API patterns
that downstream implementation steps should be aware of.

### Legacy Prompt References (for adaptation, not direct reuse)

- Extract descriptions prompt adapted from:
  Agnes.AI/image_csv_gen_v2/01_extract_desc.txt
- Generate prompts adapted from:
  Agnes.AI/image_csv_gen_v2/02_gen_prompts.txt

Key differences from legacy that prompt templates must account for:
- Description format: nested schema (not flat)
- Prompt language: English (not Chinese)
- No negative_prompt or workflowKey fields
- Image/video generation uses Agnes API directly (not ComfyUI backend)

### API Call Pattern References (for reference, not direct reuse)

- Image generation script: ~/.qwen/skills/scripts/agnes_image_gen.py
- Video generation script: ~/.qwen/skills/scripts/agnes_video_gen.py

These scripts can serve as reference for endpoint URLs, payload
structure, and authentication patterns. However, the workflow requires
new action code with batch processing, retry logic, config reading,
and index file generation. Do NOT copy or import from these scripts.

### Image API Pattern

- Endpoint: https://apihub.agnes-ai.com/v1/images/generations
- Model: agnes-image-2.1-flash
- Request payload: model, prompt, size
- Response: data array with url field
- Authentication: API key from .env (AGNES_API_KEY)

### Video API Pattern

- Submission endpoint: https://apihub.agnes-ai.com/v1/videos
- Status polling endpoint: https://apihub.agnes-ai.com/agnesapi?video_id=<ID>
- Model: agnes-video-v2.0
- Request payload: model, prompt, image (URL), width, height,
  num_frames, frame_rate
- Polling: poll status endpoint until status == "completed"
- Download: fetch video from url field in completed response
- Authentication: API key from .env (AGNES_API_KEY)

### Reference Data Files

- Description schema reference: download (1a).json
- Variant schema reference: ugc_20260718_001.json

### Configuration File Structure

The configuration file (see Design Decision DD-001 for filename
resolution) provides these parameter groups:
- image: model, size, ratio
- video: model, width, height, num_frames, frame_rate
- num_variants: number of prompt variants per description (default 4)
- process_delay: seconds between API calls (default 15)
- coder_timeout: seconds for LLM step timeouts (default 900)
- api_timeout: seconds for HTTP request timeouts (default 500)
- api_max_retries: maximum retry attempts for 503 errors (default 5)

## Resolved Questions

All questions from the step 1 open questions list have been resolved
against the source specification or classified as design decisions.

RQ-001: Video frame_rate parameter -- Is frame_rate hardcoded or
configurable?
Answer: The configuration file JSON in the specification explicitly
includes "frame_rate": 24 under the "video" object. Frame rate is
a configurable parameter, not hardcoded.
Incorporated in: Context Variables (MEDIA_CONFIG), Data Schemas
(Configuration File Structure).

RQ-004: Description array cardinality -- Should the LLM produce one or
multiple descriptions per image?
Answer: The step description says "For each image, use LLM vision to
read the image and produce a structured description JSON" (singular).
The schema defines descriptions as an array, but the workflow intent
is one description per image. The array structure provides schema
flexibility but each image produces exactly one entry (array length 1).
Incorporated in: Data Schemas (Image Description JSON).

RQ-007: Bundle governance file -- Should this workflow include a
bundle_governance.toml?
Answer: The specification does not mention bundle_governance.toml.
The WORKFLOW_CREATION_GUIDE confirms it is optional (only 3 of 14
existing workflows include it). This workflow should omit it.
Incorporated in: Constraints (no bundle_governance.toml declared).

## Design Decisions Required

The following items require human review. Each includes a recommended
approach, alternatives considered, and trade-offs.

### DD-001: Configuration file canonical name

Problem: The specification uses two different filenames for the
configuration file. The Context Variables section says "media_config.json",
the Configuration File section header says "(media_config.json)", and the
Special Requirements section references "media_config.json" throughout.
However, the Input Artifacts table shows "{repo_root}/config.json" and the
Required Action Features repeatedly reference "config.json".

Recommended approach: Use "media_config.json" as the canonical filename.
Justification: The dedicated Configuration File section and the Special
Requirements section both use "media_config.json". The name is more
specific and avoids collision with other config files in the repo. The
Input Artifacts table and action feature descriptions likely used
"config.json" as shorthand.

Alternative approaches considered:
- Use "config.json" -- simpler name, but less specific and risks
  collision with other configuration files.
- Use both names via symlink -- adds complexity with no benefit.

Trade-offs and risks: If downstream implementation uses "config.json"
from the action feature descriptions, there will be a mismatch. The
design_steps and generate_package steps must consistently use
"media_config.json".

### DD-002: AGNES_BASE_URL usage pattern

Problem: The specification lists AGNES_BASE_URL as a .env variable but
the API Reference section shows hardcoded endpoint URLs
(https://apihub.agnes-ai.com/...). It is unclear whether action code
should construct full URLs from AGNES_BASE_URL or use hardcoded endpoints.

Recommended approach: Use AGNES_BASE_URL from .env as the base URL and
construct endpoint paths relative to it. For example, if AGNES_BASE_URL
is "https://apihub.agnes-ai.com", the image endpoint would be
"{AGNES_BASE_URL}/v1/images/generations". The hardcoded URLs in the API
Reference section serve as documentation of the default/expected values.
Justification: Loading the base URL from .env allows the workflow to
target different API environments (staging, production, mock) without
code changes. This is standard practice for API integration.

Alternative approaches considered:
- Hardcode all endpoint URLs -- simpler but inflexible. Cannot switch
  environments.
- Use AGNES_BASE_URL for some endpoints and hardcode others --
  inconsistent and error-prone.

Trade-offs and risks: If AGNES_BASE_URL is set incorrectly in .env,
all API calls will fail. The action code should validate that
AGNES_BASE_URL is set before making API calls.

### DD-003: Variant numbering format

Problem: The variant JSON schema shows image_filename as "{stem}_01.png"
(two-digit zero-padded). The default num_variants is 4. The specification
does not explicitly address what happens when num_variants exceeds 9.

Recommended approach: Use two-digit zero-padded numbering (_01 through
_99). This matches the example pattern in the specification and supports
up to 99 variants, which is sufficient for any reasonable configuration.
Justification: Consistent with the spec example. Two digits is the
simplest format that covers practical use cases.

Alternative approaches considered:
- Dynamic padding based on num_variants (e.g., _001 for 100+ variants)
  -- more flexible but adds complexity for no practical benefit.
- Single-digit with no padding -- inconsistent with spec example.

Trade-offs and risks: If a user configures num_variants > 99, numbering
will break. This is an acceptable limitation given the default is 4.

### DD-004: Partial failure ActionResult status

Problem: The specification states action steps should have "graceful
failure with detailed error messages, partial progress saved" but does
not specify whether partial success returns APPROVED or REJECTED.

Recommended approach: Return REJECTED when any item fails, with a remark
detailing which items succeeded and which failed. Partial progress (index
file, generated files) should still be written to disk. The human review
gate allows the operator to inspect partial results and decide whether
to accept them (approve the step despite the rejection) or rerun.
Justification: The human review gate is designed precisely for this
scenario. Returning REJECTED ensures the operator sees the partial
results before deciding. Returning APPROVED would silently bypass the
quality gate.

Alternative approaches considered:
- Return APPROVED with warning remark -- risks unnoticed failures.
- Return REJECTED and discard partial results -- wastes API calls and
  time. The spec says "partial progress saved."

Trade-offs and risks: The operator may need to understand partial
failure details. The remark field must clearly list success/failure
counts and specific error messages per failed item.

### DD-005: Prompt schema embedding strategy

Problem: The specification provides detailed JSON schemas for step_01
(descriptions, ~49 fields) and step_02 (variants, ~6 fields). Should
the full schema be embedded in prompt template files, or should prompts
reference external schema documentation?

Recommended approach: Embed the essential schema structure and field
names directly in the prompt template files. For step_01, include the
9 attribute group names and their key fields. For step_02, include
the full variant structure. Do not reference external schema files.
Justification: Prompt templates must be self-contained. The coder
invoked by the runner needs the schema in the prompt itself to produce
correct output. External references would require additional file reads
that are not guaranteed to be available in the prompt context.

Alternative approaches considered:
- Reference external schema JSON files -- reduces prompt size but
  adds dependency on file availability and increases coder complexity.
- Minimal schema with only group names -- insufficient for the LLM
  to produce the correct nested structure.

Trade-offs and risks: Embedding the full schema increases prompt token
usage. For step_01 (~49 fields), this is moderate. The benefit of
self-contained prompts outweighs the token cost.
