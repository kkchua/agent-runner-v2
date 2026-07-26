---
doc_type: "artifact_contract"
lifecycle_status: "draft"
effective_version: "WFBUILD-20260725-0bb6afa4"
workflow_name: "agnes_media_gen_v1"
job_prefix: "AMGEN"
---

# Artifact Contract: Agnes Media Generation v1

## Artifact Key Summary

| Key | Path Pattern | Description | Required |
|---|---|---|---|
| IMAGE_DESCRIPTIONS | step_01/index.json | Index manifest listing all structured description JSON files produced by extract_descriptions step. One entry per input image. | yes |
| PROMPT_VARIANTS | step_02/index.json | Index manifest listing all prompt variant JSON files produced by generate_prompts step. One entry per input image. | yes |
| IMAGE_INDEX | step_03/index.json | Index manifest listing all generated images and updated JSON files (with image_url populated) produced by generate_images action. | yes |
| VIDEO_INDEX | step_04/index.json | Index manifest listing all generated video files produced by generate_videos action. | yes |
| REVIEW_FILE_SUGGESTED | REVIEW-{date}-{seq}_{slug}.md | Human review gate output document. Written at target repo root. | yes |
| MEDIA_CONFIG | config.json | Media generation configuration file at target repo root. Contains image/video parameters, variant count, delays, timeouts, and retry settings. | yes |
| IMAGE_INPUT_DIR | step_00/ | Directory at target repo root where user places input images (PNG, JPG, WEBP). | yes |
| IMAGE_INPUT_ARCHIVE | step_00_archive/ | Archive directory at target repo root for processed input images. | yes |
| GOVERNANCE_RUNTIME_ROOT | (global path) | Layer 1 governance documentation root. Standard across all workflows. Resolved at runtime. | yes |
| PLATFORM_RUNTIME_ROOT | (global path) | Layer 2 platform documentation root. Standard across all workflows. Resolved at runtime. | yes |
| STEP_00_DIR | step_00/ | Absolute path to step_00/ directory. Runtime context variable. | yes |
| STEP_00_ARCHIVE | step_00_archive/ | Absolute path to step_00_archive/ directory. Runtime context variable. | yes |
| STEP_01_DIR | step_01/ | Absolute path to step_01/ directory for structured description JSONs. Runtime context variable. | yes |
| STEP_01_ARCHIVE | step_01_archive/ | Absolute path to step_01_archive/ directory. Runtime context variable. | yes |
| STEP_02_DIR | step_02/ | Absolute path to step_02/ directory for prompt variant JSONs. Runtime context variable. | yes |
| STEP_02_ARCHIVE | step_02_archive/ | Absolute path to step_02_archive/ directory. Runtime context variable. | yes |
| STEP_03_DIR | step_03/ | Absolute path to step_03/ directory for generated images and updated JSONs. Runtime context variable. | yes |
| STEP_03_ARCHIVE | step_03_archive/ | Absolute path to step_03_archive/ directory. Runtime context variable. | yes |
| STEP_04_DIR | step_04/ | Absolute path to step_04/ directory for generated video files. Runtime context variable. | yes |
| STEP_04_ARCHIVE | step_04_archive/ | Absolute path to step_04_archive/ directory. Runtime context variable. | yes |

Notes:

- The index.json output artifacts (IMAGE_DESCRIPTIONS, PROMPT_VARIANTS,
  IMAGE_INDEX, VIDEO_INDEX) do not use {seq} or {slug} placeholders. They
  reside in fixed step directories at the target repo root and are overwritten
  each run. Historical tracking is handled by the archive pattern (each step
  copies processed inputs to the corresponding _archive folder).
- The REVIEW_FILE_SUGGESTED uses {date}, {seq}, and {slug} placeholders
  following the standard workflow_builder pattern. The {slug} is derived from
  the input specification filename (e.g., "media_gen_v1" from
  "REQUIREMENTS-20260725-001_media_gen_v1.md").
- All step directory paths (STEP_XX_DIR, STEP_XX_ARCHIVE) are relative to the
  target repo root. They are resolved to absolute paths at runtime by
  context_extensions.py.
- GOVERNANCE_RUNTIME_ROOT and PLATFORM_RUNTIME_ROOT are global paths resolved
  at runtime by context_extensions.py using get_governance_runtime_root() and
  get_platform_runtime_root().

## Input Artifacts

This workflow has no user-provided input artifacts declared in workflow.toml
required_inputs. All input paths are resolved at runtime from the target
repository root via context_extensions.py.

The following context variables are injected into prompts and actions but are
NOT declared as required_inputs:

### IMAGE_INPUT_DIR

- Type: Runtime context variable
- Source: Resolved to {repo_root}/step_00 at runtime
- Description: Directory where the user places input images (PNG, JPG, WEBP)
  before starting the workflow. The extract_descriptions step scans this
  directory for image files.
- Required/Optional: Required at runtime. If empty, extract_descriptions
  returns REJECTED with reject_code "NO_INPUT_IMAGES".

### IMAGE_INPUT_ARCHIVE

- Type: Runtime context variable
- Source: Resolved to {repo_root}/step_00_archive at runtime
- Description: Archive directory for processed input images. After
  extract_descriptions processes images from step_00, they are copied here
  and removed from step_00.
- Required/Optional: Required at runtime. Created automatically if it does
  not exist.

### MEDIA_CONFIG

- Type: Runtime context variable
- Source: Resolved to {repo_root}/config.json at runtime
- Description: Path to the media generation configuration file. Contains
  image parameters (model, size, ratio), video parameters (model, width,
  height, num_frames, frame_rate), and pipeline parameters (num_variants,
  process_delay, coder_timeout, api_timeout, api_max_retries).
- Required/Optional: Required at runtime. The canonical filename is
  "config.json" per design decision DD-001.

### GOVERNANCE_RUNTIME_ROOT

- Type: Runtime context variable (standard across all workflows)
- Source: Resolved via get_governance_runtime_root() at runtime
- Description: Layer 1 governance documentation root. Provides read-only
  access to foundation governance documents.
- Required/Optional: Required. Standard infrastructure variable.

### PLATFORM_RUNTIME_ROOT

- Type: Runtime context variable (standard across all workflows)
- Source: Resolved via get_platform_runtime_root() at runtime
- Description: Layer 2 platform documentation root. Provides read-only
  access to platform constitution documents.
- Required/Optional: Required. Standard infrastructure variable.

## Output Artifacts

### IMAGE_DESCRIPTIONS

- Type: Output artifact (index manifest)
- Path: step_01/index.json (relative to target repo root)
- Produced by: extract_descriptions step (step 1)
- Content: JSON index manifest with "step" identifier and "files" array.
  Each entry maps an input image path to its corresponding structured
  description JSON file. Each description JSON contains 9 attribute groups
  (subject_attributes, scene_attributes, composition_attributes,
  lighting_attributes, style_attributes, color_attributes, mood_attributes,
  motion_potential, extraction_confidence) with 49 total attribute fields.
- Required/Optional: Required
- Notes: One description JSON per input image. Filename derived from input
  image stem (e.g., image001.png produces image001.json).

### PROMPT_VARIANTS

- Type: Output artifact (index manifest)
- Path: step_02/index.json (relative to target repo root)
- Produced by: generate_prompts step (step 2)
- Content: JSON index manifest with "step" identifier and "files" array.
  Each entry maps a description JSON path to its corresponding prompt
  variant JSON file. Each variant JSON contains: mode ("BASE" for v1),
  subject (image stem string), and a variations array with N variant
  objects. Each variant object has t2i_prompt1 (text prompt) and
  image_filename ({stem}_{NN}.png format).
- Required/Optional: Required
- Notes: One variant JSON per input image. Default N=4 variants per image
  (configurable via MEDIA_CONFIG num_variants). Per design decision DD-002,
  granularity is per-image, not per-description-entry.

### IMAGE_INDEX

- Type: Output artifact (index manifest)
- Path: step_03/index.json (relative to target repo root)
- Produced by: generate_images action (step 3)
- Content: JSON index manifest with "step" identifier and "files" array.
  Each entry maps a prompt variant JSON path to generated image files and
  updated JSON files (with image_url populated). Generated images use the
  {stem}_{NN}.png naming convention.
- Required/Optional: Required
- Notes: Calls Agnes Image 2.1 Flash API for text-to-image generation.
  Includes retry logic with exponential backoff for 503 errors. Saves
  updated JSONs alongside generated images.

### VIDEO_INDEX

- Type: Output artifact (index manifest)
- Path: step_04/index.json (relative to target repo root)
- Produced by: generate_videos action (step 4)
- Content: JSON index manifest with "step" identifier and "files" array.
  Each entry maps an updated JSON path (from step_03) to its corresponding
  generated video file. Video filenames derived from image stems.
- Required/Optional: Required
- Notes: Calls Agnes Video V2.0 API for image-to-video generation. Uses
  t2i_prompt1 from variant JSON as motion prompt. Includes status polling
  until completion, then downloads video from returned URL.

### REVIEW_FILE_SUGGESTED

- Type: Shared output artifact (human review document)
- Path: REVIEW-{date}-{seq}_{slug}.md (at target repo root)
- Produced by: Human review gate steps
- Content: Markdown document containing review findings, approval or
  rejection decisions, and remarks for each pipeline step.
- Required/Optional: Required
- Notes: Follows the standard workflow_builder naming pattern with
  auto-incrementing {seq} and {slug} derived from input specification
  filename. The {date} is the current date in YYYYMMDD format.

## Shared Artifacts

### REVIEW_FILE_SUGGESTED

- Framework-level key for human review gate output.
- Used by the workflow framework to track review decisions.
- Path pattern: REVIEW-{date}-{seq}_{slug}.md
- This key is declared in constants.py as ARTIFACT_KEY_REVIEW.
- Required by the human approval gate pattern (requires_human_approval_after
  = true on each step).

### GOVERNANCE_RUNTIME_ROOT

- Framework-level key for Layer 1 governance access.
- Standard across all workflows.
- Resolved at runtime via get_governance_runtime_root().

### PLATFORM_RUNTIME_ROOT

- Framework-level key for Layer 2 platform constitution access.
- Standard across all workflows.
- Resolved at runtime via get_platform_runtime_root().

## Naming Rationale

### Output Artifact Keys

- IMAGE_DESCRIPTIONS, PROMPT_VARIANTS, IMAGE_INDEX, VIDEO_INDEX: Named
  after the content type they index. Each key describes what the index
  manifest lists. These match the existing artifact keys defined in the
  bootstrap context_extensions.py for agnes_media_gen_v1.

- REVIEW_FILE_SUGGESTED: Standard framework key for human review output.
  The _SUGGESTED suffix indicates the reviewer proposes changes; final
  approval is gated by the workflow runtime. Matches ARTIFACT_KEY_REVIEW
  in constants.py.

### Runtime Context Variable Keys

- IMAGE_INPUT_DIR, IMAGE_INPUT_ARCHIVE: Named after their purpose (input
  images) and role (active directory vs. archive). The DIR suffix indicates
  an active working directory.

- MEDIA_CONFIG: Named after its purpose (media generation configuration).
  Short and descriptive. Matches the key name used in the requirements
  document and context_extensions.py.

- STEP_XX_DIR, STEP_XX_ARCHIVE: Named after their step number and role.
  The DIR suffix indicates an active working directory; the ARCHIVE suffix
  indicates a historical archive. These are runtime context variables, not
  workflow input/output artifacts.

- GOVERNANCE_RUNTIME_ROOT, PLATFORM_RUNTIME_ROOT: Standard framework keys.
  The _RUNTIME_ROOT suffix indicates a global filesystem root resolved at
  runtime, distinguishing them from Layer 1/Layer 2 document content.

### Path Pattern Decisions

- Index manifests (IMAGE_DESCRIPTIONS, PROMPT_VARIANTS, IMAGE_INDEX,
  VIDEO_INDEX) use fixed paths (step_XX/index.json) rather than the
  standard SDLC pattern with {seq} and {slug}. Rationale: the workflow
  defines its own folder structure at the target repo root (step_00 through
  step_04). Each step directory has a single index.json that is overwritten
  each run. Historical tracking is handled by the archive pattern, not by
  sequence numbers in filenames.

- REVIEW_FILE_SUGGESTED uses the standard workflow_builder pattern with
  {date}, {seq}, and {slug} to prevent overwrites across multiple runs and
  to maintain traceability to the input specification.

- No {job_id} placeholder is used in output paths because the target repo
  root is already scoped to a single workflow execution. The job_id is
  tracked in workflow state, not in filesystem paths.

### Collision Check

All artifact keys defined in this contract have been verified against the
existing artifact keys in constants.py and other workflow
context_extensions.py files. No collisions detected:

- IMAGE_DESCRIPTIONS, PROMPT_VARIANTS, IMAGE_INDEX, VIDEO_INDEX: Unique to
  agnes_media_gen_v1. Not declared in constants.py or other workflows.
- REVIEW_FILE_SUGGESTED: Shared framework key (ARTIFACT_KEY_REVIEW in
  constants.py). Used by multiple workflows. No collision - this is the
  intended shared usage.
- GOVERNANCE_RUNTIME_ROOT, PLATFORM_RUNTIME_ROOT: Shared infrastructure
  keys. Standard across all workflows. No collision.
- Step directory keys (STEP_XX_DIR, STEP_XX_ARCHIVE): Unique to
  agnes_media_gen_v1. Not declared in constants.py or other workflows.
- IMAGE_INPUT_DIR, IMAGE_INPUT_ARCHIVE, MEDIA_CONFIG: Unique to
  agnes_media_gen_v1. Not declared in constants.py or other workflows.
