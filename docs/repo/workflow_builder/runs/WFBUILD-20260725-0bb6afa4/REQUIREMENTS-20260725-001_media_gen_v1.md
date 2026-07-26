---
doc_type: "workflow_design"
lifecycle_status: "draft"
effective_version: "WFBUILD-20260725-0bb6afa4.2"
workflow_name: "agnes_media_gen_v1"
job_prefix: "AMGEN"
---

# Workflow Requirements: Agnes Media Generation v1

## Overview

The Agnes Media Generation v1 workflow is an end-to-end media creation pipeline
that automates the transformation of raw input images into animated videos. It
operates through four sequential stages: (1) LLM vision-based extraction of
structured image descriptions, (2) LLM-based generation of multiple prompt
variants per description, (3) Agnes Image 2.1 Flash API calls to generate new
images from those prompts, and (4) Agnes Video V2.0 API calls to produce
image-to-video animations. Each stage is gated by human review, with rejection
triggering a rerun of the same step. The workflow defines its own folder
structure (step_00 through step_04 with corresponding archive directories) and
can execute in any repository that provides this structure.

## Workflow Type

Mixed. The workflow combines prompt-driven steps and action-driven steps within
a single pipeline.

Justification:

- Steps extract_descriptions and generate_prompts are prompt-driven. They
  require LLM invocation: step 1 uses LLM vision to analyze images and produce
  structured JSON descriptions, and step 2 uses LLM text generation to produce
  multiple prompt variants from those descriptions.
- Steps generate_images and generate_videos are action-driven. They execute
  Python functions that call external HTTP APIs (Agnes Image 2.1 Flash and
  Agnes Video V2.0), handle retries, manage batch processing, and produce
  index files.
- The terminal step stepCompletion is a built-in action.

## Input Artifacts

The workflow has no user-provided input artifacts. All input paths are resolved
at runtime from the target repository root via context_extensions.py. The
following context variables are injected into prompts and actions but are NOT
declared as required_inputs in workflow.toml.

| Artifact Key | Description | Required/Optional |
|---|---|---|
| IMAGE_INPUT_DIR | Directory where user places input images (PNG, JPG, WEBP). Resolved at runtime to {repo_root}/step_00. | Runtime context (not a workflow input artifact) |
| IMAGE_INPUT_ARCHIVE | Archive directory for processed input images. Resolved at runtime to {repo_root}/step_00_archive. | Runtime context (not a workflow input artifact) |
| MEDIA_CONFIG | Path to media generation configuration file. Contains image/video parameters, variant count, delays, timeouts, and retry settings. See Design Decisions Required section regarding the canonical filename. | Runtime context (not a workflow input artifact) |
| GOVERNANCE_RUNTIME_ROOT | Layer 1 governance documentation root. Standard across all workflows. | Runtime context (not a workflow input artifact) |
| PLATFORM_RUNTIME_ROOT | Layer 2 platform documentation root. Standard across all workflows. | Runtime context (not a workflow input artifact) |

## Output Artifacts

Each step produces an index.json manifest file that lists all per-image output
files with input-to-output mapping metadata. Output filenames are derived from
input image filenames (e.g., image001.png produces image001.json in
subsequent steps).

| Artifact Key | Description | Required/Optional |
|---|---|---|
| IMAGE_DESCRIPTIONS | Index manifest (step_01/index.json) listing all structured description JSON files produced by the extract_descriptions step. Each JSON contains subject_attributes, scene_attributes, composition_attributes, lighting_attributes, style_attributes, color_attributes, mood_attributes, motion_potential, and extraction_confidence. | Required |
| PROMPT_VARIANTS | Index manifest (step_02/index.json) listing all prompt variant JSON files produced by the generate_prompts step. Each JSON contains mode, subject, and a variations array with t2i_prompt1 for each variant. | Required |
| IMAGE_INDEX | Index manifest (step_03/index.json) listing all generated images and updated JSON files (with image_url populated) produced by the generate_images action. | Required |
| VIDEO_INDEX | Index manifest (step_04/index.json) listing all generated video files produced by the generate_videos action. | Required |

## Context Variables

The following context variables are declared by the specification and resolved
at runtime by context_extensions.py. They are injected into prompt context and
action parameters. No resolved file paths are assigned at this stage (path
resolution is handled by the define_artifacts step and context_extensions.py).

| Variable | Purpose |
|---|---|
| STEP_00_DIR | Absolute path to step_00/ directory where user places input images |
| STEP_00_ARCHIVE | Absolute path to step_00_archive/ for archiving processed input images |
| STEP_01_DIR | Absolute path to step_01/ directory for structured description JSONs |
| STEP_01_ARCHIVE | Absolute path to step_01_archive/ for archiving processed description JSONs |
| STEP_02_DIR | Absolute path to step_02/ directory for prompt variant JSONs |
| STEP_02_ARCHIVE | Absolute path to step_02_archive/ for archiving processed variant JSONs |
| STEP_03_DIR | Absolute path to step_03/ directory for generated images and updated JSONs |
| STEP_03_ARCHIVE | Absolute path to step_03_archive/ for archiving processed step_03 files |
| STEP_04_DIR | Absolute path to step_04/ directory for generated video files |
| STEP_04_ARCHIVE | Absolute path to step_04_archive/ for archiving processed step_04 files |
| MEDIA_CONFIG | Absolute path to the media generation configuration file |
| GOVERNANCE_RUNTIME_ROOT | Layer 1 governance documentation root (standard across all workflows) |
| PLATFORM_RUNTIME_ROOT | Layer 2 platform documentation root (standard across all workflows) |

## Data Schemas

### Image Description JSON (step_01 output)

Produced by the extract_descriptions step. Each file corresponds to one input
image. Top-level fields: image_filename, image_stem, and a descriptions array.
The descriptions array contains one or more description entries, each with nine
attribute groups:

- subject_attributes: 6 fields (main_subject, subject_type, subject_description,
  distinctive_features list, recognizable_objects list, subject_state_or_pose)
- scene_attributes: 9 fields (setting, environment, foreground, midground,
  background, time_of_day, season_or_weather, spatial_depth, parallax_potential)
- composition_attributes: 7 fields (orientation, framing, camera_angle,
  subject_position, negative_space, visual_flow, depth_layers list)
- lighting_attributes: 6 fields (lighting_type, light_direction, light_quality,
  color_temperature, shadow_highlight_behavior, atmospheric_lighting)
- style_attributes: 5 fields (visual_style, medium, realism_level,
  texture_quality, rendering_treatment)
- color_attributes: 4 fields (dominant_colors list, accent_colors list,
  color_contrast, palette_mood)
- mood_attributes: 3 fields (emotional_tone, atmosphere, viewer_feeling)
- motion_potential: 7 fields (primary_motion_candidate, subject_motion_candidates
  list, environmental_motion_candidates list, camera_motion_candidates list,
  motion_intensity_suggestion, motion_pacing_suggestion, motion_constraints list)
- extraction_confidence: 2 fields (overall_confidence, uncertain_attributes list)

Total: 49 attribute fields across 9 groups, plus 2 top-level identity fields.

### Prompt Variant JSON (step_02 output)

Produced by the generate_prompts step. Each file corresponds to one input image
(or one description entry, depending on design decision DD-002). Top-level
fields: mode (string, value "BASE" for v1), subject (image stem string),
variations (array of variant objects).

Each variant object contains:
- t2i_prompt1: Text prompt used for both image generation (step_03) and video
  motion (step_04). Required.
- image_filename: Output image filename in format {stem}_{NN}.png where NN is
  1-based variant index. Required.
- image_url: URL of the generated image. Absent after step_02; populated by
  step_03 (generate_images action).

Total: 3 top-level fields, 3 fields per variant object.

### Index JSON (all steps)

Each step produces an index.json manifest file at the root of its output
directory. Structure:
- step: String identifier for the step that produced the index
- files: Array of objects, each with "input" (source file path) and "output"
  (produced file path) fields

## Constraints

### Governance Layer

- Layer 1 (foundation governance) and Layer 2 (platform constitution) are
  read-only authority. This workflow must not redefine or contradict them.
- The workflow must reference governance documents via GOVERNANCE_RUNTIME_ROOT
  and PLATFORM_RUNTIME_ROOT context variables.
- Role policies must be selected from those defined in role_policies.json.

### Naming Conventions

- Workflow directory name: agnes_media_gen_v1
- Workflow name in workflow.toml: agnes_media_gen_v1
- workflow_name attribute in context_extensions.py: agnes_media_gen_v1
- Job prefix: AMGEN
- All artifact keys use UPPER_SNAKE_CASE.
- Per-run documents follow the pattern: {TYPE}-{YYYYMMDD}-{seq}_{slug}.md

### External Dependencies

- Agnes Image 2.1 Flash API at https://apihub.agnes-ai.com/v1/images/generations
  for text-to-image generation.
  - Model: agnes-image-2.1-flash
  - Payload: {"model": "...", "prompt": "...", "size": "..."}
  - Response: {"data": [{"url": "..."}]}
- Agnes Video V2.0 API at https://apihub.agnes-ai.com/v1/videos for
  image-to-video generation.
  - Model: agnes-video-v2.0
  - Payload: {"model": "...", "prompt": "...", "image": "<url>", "width": ...,
    "height": ..., "num_frames": ..., "frame_rate": ...}
  - Status polling: https://apihub.agnes-ai.com/agnesapi?video_id=<ID>
  - Poll until status == "completed", then download from returned URL
- Credentials AGNES_API_KEY and AGNES_BASE_URL loaded from .env file in the
  runtime repository.

### Action Code Constraints

- Custom action code for generate_images and generate_videos must be generated
  fresh. Existing skill scripts (agnes_image_gen.py, agnes_video_gen.py) may
  serve as reference for API call patterns only and must not be reused directly.
- Actions must include: batch processing, retry logic with exponential backoff
  for 503 errors, configurable timeouts, config reading from configuration file,
  index file generation, archive pattern, per-image filenames, process delay
  between API calls, error handling with partial progress saving, and
  ActionResult return values.

### Workflow Behavior Constraints

- Every step requires human approval after execution
  (requires_human_approval_after = true).
- Rejection reruns the same step (on_reject_refine points to itself).
  See Design Decision DD-003 regarding routing pattern.
- Archive pattern: each step copies processed inputs to the corresponding
  _archive folder and removes them from the input folder.
- step_03 saves updated JSONs (with image_url filled in) alongside generated
  images. step_04 reads from step_03.
- If step_00 contains no images, extract_descriptions must return REJECTED
  with reject_code "NO_INPUT_IMAGES" and a descriptive remark.

### Configuration Constraints

- All configurable parameters are read from the media configuration file.
- Image parameters: model, size, ratio (from config "image" section).
- Video parameters: model, width, height, num_frames, frame_rate (from config
  "video" section).
- Pipeline parameters: num_variants (default 4), process_delay, coder_timeout,
  api_timeout, api_max_retries.
- 503 "server busy" errors trigger automatic retry with exponential backoff,
  up to api_max_retries attempts.

## Implementation Notes

### Legacy References

The specification references the following legacy artifacts for adaptation
purposes only. These must NOT be reused directly but serve as design references.

| Reference | Type | Purpose |
|---|---|---|
| Agnes.AI/image_csv_gen_v2/01_extract_desc.txt | Legacy prompt | Reference for extract_descriptions prompt adaptation. Key differences: legacy uses flat schema, new workflow uses nested schema with 9 attribute groups. |
| Agnes.AI/image_csv_gen_v2/02_gen_prompts.txt | Legacy prompt | Reference for generate_prompts prompt adaptation. Key differences: legacy produces Chinese prompts, new workflow produces English prompts; legacy includes negative_prompt and workflowKey fields, new workflow does not. |
| ~/.qwen/skills/scripts/agnes_image_gen.py | Legacy script | Reference for Agnes Image API call patterns (endpoint, payload, auth). Must NOT be imported or reused. The new generate_images action must add batch processing, retry logic, index file generation, and archive pattern. |
| ~/.qwen/skills/scripts/agnes_video_gen.py | Legacy script | Reference for Agnes Video API call patterns (endpoint, payload, polling, auth). Must NOT be imported or reused. The new generate_videos action must add batch processing, retry logic, index file generation, and archive pattern. |

### Key Differences from Legacy

- Description format: nested schema with 9 attribute groups (not flat).
- Prompt language: English (not Chinese).
- No negative_prompt or workflowKey fields in API payloads.
- Image/video generation uses Agnes API directly (not ComfyUI backend).
- Batch processing with retry, timeout, and index file generation (not
  single-item processing).

### API Call Patterns

The following patterns are extracted from the legacy scripts and must be
replicated in the new action code (with added robustness):

1. Image generation: POST to images/generations endpoint with model, prompt,
   and size parameters. Extract URL from response data[0].url.
2. Video generation: POST to videos endpoint with model, prompt, image URL,
   width, height, num_frames, and frame_rate. Poll status endpoint until
   status == "completed". Download video from returned URL.
3. Authentication: AGNES_API_KEY passed via headers (pattern from legacy
   scripts).
4. Base URL: AGNES_BASE_URL from .env provides the API host.

## Resolved Questions

RQ-001 (was Q3): What modes does the variant JSON "mode" field support?
- Resolution: The specification only defines "BASE" as the mode value. No other
  modes are mentioned anywhere in the spec. BASE is the only mode for v1.
- Incorporated in: Data Schemas section (Prompt Variant JSON), where mode is
  documented as "string, value 'BASE' for v1".

RQ-002 (was Q4): Should frame_rate be read from config or hardcoded?
- Resolution: The configuration file example (Configuration File section)
  includes "frame_rate": 24 under the "video" section. It is a configurable
  parameter read from the config file, not a hardcoded value.
- Incorporated in: Constraints > Configuration Constraints section, which lists
  frame_rate as a video parameter read from the config "video" section.

RQ-003 (was Q5): What is the output filename format for multi-variant images?
- Resolution: The prompt variant JSON schema shows image_filename as
  "{stem}_01.png". This indicates a format of {stem}_{NN}.png where NN is a
  zero-padded 1-based variant index (01, 02, 03, ...).
- Incorporated in: Data Schemas section (Prompt Variant JSON), documenting the
  image_filename format.

RQ-004 (was Q7): Should the workflow take automated action on low
extraction_confidence scores?
- Resolution: The extraction_confidence field is metadata within the description
  JSON schema. The specification does not define any automated action based on
  confidence scores. It is purely informational metadata passed through to
  subsequent steps. The human review gate after extract_descriptions provides
  the opportunity for manual review of low-confidence results.
- Incorporated in: No workflow constraint needed. The field is documented as
  informational in the Data Schemas section.

RQ-005 (was Q8): What happens when step_00 contains no images?
- Resolution: The extract_descriptions step requires input images to process.
  An empty step_00 is an error condition. The step must return REJECTED with
  reject_code "NO_INPUT_IMAGES" and a descriptive remark indicating no images
  were found. The human review gate will then allow the user to either add
  images to step_00 and re-approve, or terminate the job.
- Incorporated in: Constraints > Workflow Behavior Constraints section.

## Design Decisions Required

### DD-001: Canonical Configuration Filename

Background:
The specification uses two different filenames for the configuration file:

- "config.json" appears in: the Input Artifacts table (hardcoded path
  {repo_root}/config.json), and the Custom Actions section (requirement 4:
  "load settings from config.json").
- "media_config.json" appears in: the Context Variables section (MEDIA_CONFIG
  description says "media_config.json"), the Configuration File section heading
  ("Configuration File (media_config.json)"), the Special Requirements section
  (multiple references), and the Configuration File JSON example.

The Input Artifacts table and Custom Actions section are the only places using
"config.json". All other references (5 occurrences) use "media_config.json".

Recommendation:
Use "config.json" as the canonical filename. Rationale: the Input Artifacts
table is the primary contract definition for runtime variables, and it
explicitly states "{repo_root}/config.json". The more generic name also aligns
with common convention for repo-level configuration files. The Configuration
File section heading "media_config.json" may be an editorial label rather than
the actual filename.

Alternative 1: Use "media_config.json". Rationale: the Configuration File
section provides the full JSON example and labels it media_config.json,
suggesting this is the intended filename. The more specific name also avoids
collision with other potential config files in the repo.

Alternative 2: Leave it ambiguous and let context_extensions.py define the
filename. This is fragile and not recommended.

Trade-offs:
- "config.json" is simpler but risks collision with other config files.
- "media_config.json" is more specific but contradicts the Input Artifacts
  table.
- The specification is internally inconsistent regardless of choice.

Risk: Low. The filename only affects context_extensions.py path resolution and
the config-reading code in actions. Once decided, it is a single-value change.

### DD-002: Variant Generation Granularity (Per Image vs Per Description Entry)

Background:
The image description JSON schema contains a "descriptions" array, implying
that a single image may produce multiple description entries. The
generate_prompts step says "For each JSON, generate N variant prompt sets
(configurable, default 4)." The prompt variant JSON schema has a flat
"variations" array with subject set to {image_stem}, suggesting one variant
JSON per image.

The ambiguity: does "For each JSON" mean (a) one variant JSON per input image
(generating N variants total, possibly selecting or merging the best
description entry), or (b) one variant JSON per description entry within each
image (generating N variants per entry)?

Recommendation:
One variant JSON per input image. The generate_prompts step produces N variants
(total, not per entry) in a single variant JSON file per image. The LLM should
consider all description entries when generating prompts. Rationale: the variant
JSON schema uses {image_stem} as subject (not per-entry), and the output
filename pattern {stem}_01.png suggests one set of images per source image.
This is simpler and matches the variant JSON structure.

Alternative 1: One variant JSON per description entry. The output filename
would be {stem}_{entry_index}_{variant_index}.png. This provides more
granularity but contradicts the flat variant JSON schema.

Alternative 2: One variant JSON per image, but N variants per description
entry (N * entries total variants). The variant JSON would need additional
structure to group variants by entry. This contradicts the shown schema.

Trade-offs:
- Per-image is simpler, matches the schema, and produces fewer API calls.
- Per-entry provides more variety but complicates the pipeline and increases
  API costs proportionally.

Risk: Medium. This affects the generate_prompts prompt design, the variant
JSON schema interpretation, and the total number of API calls in steps 3 and 4.

### DD-003: Rejection Routing Pattern (Self-Reference vs Standard Loop)

Background:
The specification states: "requires_human_approval_after = true with
on_reject_refine pointing to itself (rerun same step on reject)." This means
each step rejects to itself, effectively re-running the same prompt or action
on rejection.

The standard workflow pattern (Pattern 2 in the Workflow Creation Guide) uses a
separate refine step with loop_returns_to routing:

  generate --> review --> [reject] --> refine --> review --> [approve] --> next

The self-referencing pattern would be:

  step --> [approve] --> next_step
  step --> [reject] --> step (rerun same step)

The self-referencing approach is unusual and may not be supported by the
routing runtime. The Workflow Creation Guide documents the refine loop pattern
but does not document self-referencing on_reject_refine.

Recommendation:
Use the self-referencing on_reject_refine as specified. Each step has
requires_human_approval_after = true and on_reject_refine pointing to itself.
Rationale: the specification is explicit about this pattern. For prompt steps,
re-running the same prompt with fresh LLM invocation produces new output. For
action steps, re-running re-executes the API calls. The default_max_rejects
setting (3) provides a safety limit. If the routing runtime does not support
self-referencing, this will be caught during bundle validation or dry run.

Alternative 1: Use the standard loop pattern with explicit refine steps for
each of the 4 pipeline steps. This would add 4 refine steps and 4 refine
prompts, significantly increasing the workflow complexity. Each step pair would
be: step --> review gate --> [reject] --> refine_step --> step.

Alternative 2: Use the standard loop pattern but with a single shared refine
step. This is not compatible with the per-step rejection semantics described
in the spec.

Trade-offs:
- Self-referencing is simpler (4 steps, no refine steps) but untested.
- Standard loop pattern is proven but adds 4 extra steps and 4 refine prompts.
- Self-referencing for prompt steps means the LLM re-generates from scratch,
  losing the previous attempt's context. Standard refine pattern preserves the
  prior output and modifies it in-place.

Risk: Medium-High. If the routing runtime rejects self-referencing
on_reject_refine, the workflow must be redesigned with explicit refine steps.
Recommend validating this pattern with a dry run before committing to it.
