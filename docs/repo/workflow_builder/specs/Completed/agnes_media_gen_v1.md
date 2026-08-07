# Workflow Specification: Agnes Media Generation v1

## Overview

**Workflow name:** `agnes_media_gen_v1`
**Label:** Agnes Media Generation v1
**Job prefix:** `AMGEN`
**Description:** End-to-end media generation pipeline — extracts image descriptions via
LLM vision, generates prompt variants, calls Agnes Image 2.1 Flash API for image
generation, and Agnes Video V2.0 API for image-to-video generation.

## Purpose

Automates the full media creation pipeline from raw images to animated videos:

1. User drops images into `step_00/` folder
2. LLM vision extracts detailed structured descriptions → `step_01/`
3. LLM generates multiple prompt variants per description → `step_02/`
4. Agnes Image API generates images from prompts → `step_03/`
5. Agnes Video API generates videos (image-to-video) → `step_04/`

Each step has a human review gate (approve/reject). Reject reruns the same step.
The workflow defines its own folder structure (step_00/ through step_04/ with
corresponding _archive/ folders) and can run in any repo that provides this structure.

## Workflow Type

**Mixed** — Prompt-driven steps (extract descriptions, generate prompts) combined with
action steps (image API calls, video API calls).

## Input Artifacts

**No user-provided inputs.** All paths are hardcoded in `context_extensions.py`:

| Context Variable | Hardcoded Path | Description |
|---|---|---|
| `IMAGE_INPUT_DIR` | `{repo_root}/step_00` | Directory where user places input images |
| `IMAGE_INPUT_ARCHIVE` | `{repo_root}/step_00_archive` | Archive for processed input images |
| `MEDIA_CONFIG` | `{repo_root}/config.json` | Media generation configuration file |

**Important:** Do NOT declare these as `required_inputs` in workflow.toml. They are
resolved at runtime from the target repo root, not provided by the user.

## Output Artifacts

Each step produces an **index.json** file that lists all per-image output files.
Output filenames match input image filenames (e.g., `image001.png` → `image001.json`).

| Artifact Key | Path | Description |
|---|---|---|
| `IMAGE_DESCRIPTIONS` | `step_01/index.json` | Index listing all `{stem}.json` description files |
| `PROMPT_VARIANTS` | `step_02/index.json` | Index listing all `{stem}.json` variant files |
| `IMAGE_INDEX` | `step_03/index.json` | Index listing all generated images + updated JSONs |
| `VIDEO_INDEX` | `step_04/index.json` | Index listing all generated video files |

**Index file structure:** Each `index.json` contains a manifest of all files produced
by that step, with metadata about input→output mapping. Example:
```json
{
  "step": "extract_descriptions",
  "files": [
    {"input": "step_00/image001.png", "output": "step_01/image001.json"},
    {"input": "step_00/image002.png", "output": "step_01/image002.json"}
  ]
}
```

## Step Sequence

### Step 1: extract_descriptions

```
Step: extract_descriptions
Type: prompt
Role: architect_standard
Purpose: Scan step_00/ for images (PNG, JPG, WEBP). For each image, use LLM vision
  to read the image and produce a structured description JSON matching the nested
  schema (subject_attributes, scene_attributes, composition_attributes,
  lighting_attributes, style_attributes, color_attributes, mood_attributes,
  motion_potential, extraction_confidence). Save each JSON to step_01/.
  Copy processed images to step_00_archive/, remove from step_00/.
On success: → human approval gate (approve → generate_prompts, reject → rerun)
```

### Step 2: generate_prompts

```
Step: generate_prompts
Type: prompt
Role: architect_standard
Purpose: Scan step_01/ for description JSONs. For each JSON, generate N variant
  prompt sets (configurable, default 4). Each variant has t2i_prompt1 (used for
  both image generation and video motion). Save to step_02/.
  Archive processed JSONs to step_01_archive/.
On success: → human approval gate (approve → generate_images, reject → rerun)
```

### Step 3: generate_images

```
Step: generate_images
Type: action (generate_images)
Purpose: Scan step_02/ for variant JSONs. For each JSON, iterate over variants
  and call Agnes Image 2.1 Flash API using t2i_prompt1. Download generated images
  to step_03/. Update the JSON with image_url for each variant. Save the updated
  JSON to step_03/ alongside images. Archive processed JSONs to step_02_archive/.
  Apply PROCESS_DELAY between API calls. Handle 503 errors with retry.
On success: → human approval gate (approve → generate_videos, reject → rerun)
```

### Step 4: generate_videos

```
Step: generate_videos
Type: action (generate_videos)
Purpose: Scan step_03/ for JSONs (containing image_url + t2i_prompt1). For each
  JSON, iterate over variants and call Agnes Video V2.0 API (image-to-video mode)
  using image_url and t2i_prompt1. Poll until complete, download videos to step_04/.
  Archive processed files to step_03_archive/.
  Apply PROCESS_DELAY between API calls. Handle 503 errors with retry.
On success: → stepCompletion
```

### Terminal: stepCompletion

```
Step: stepCompletion
Type: action (step_completion)
```

## Context Variables

- `STEP_00_DIR` — Absolute path to step_00/ (image input)
- `STEP_00_ARCHIVE` — Absolute path to step_00_archive/
- `STEP_01_DIR` — Absolute path to step_01/ (description JSONs)
- `STEP_01_ARCHIVE` — Absolute path to step_01_archive/
- `STEP_02_DIR` — Absolute path to step_02/ (variant JSONs)
- `STEP_02_ARCHIVE` — Absolute path to step_02_archive/
- `STEP_03_DIR` — Absolute path to step_03/ (images + JSONs)
- `STEP_03_ARCHIVE` — Absolute path to step_03_archive/
- `STEP_04_DIR` — Absolute path to step_04/ (videos)
- `STEP_04_ARCHIVE` — Absolute path to step_04_archive/
- `MEDIA_CONFIG` — Absolute path to media_config.json
- `GOVERNANCE_RUNTIME_ROOT` — Layer 1 governance docs (standard)
- `PLATFORM_RUNTIME_ROOT` — Layer 2 platform docs (standard)

## Special Requirements

- **Human review gate on every step** — Each step uses `requires_human_approval_after = true`
  with `on_reject_refine` pointing to itself (rerun same step on reject).
- **Configurable resolution** — Image size/ratio and video width/height/frames read from
  `media_config.json`.
- **Configurable variant count** — Number of prompt variants per description (default 4)
  read from `media_config.json`.
- **Configurable delays** — `process_delay` in `media_config.json` for pause between API calls.
- **Configurable timeouts** — `coder_timeout` for LLM steps (vision/prompt gen takes long),
  `api_timeout` for HTTP requests.
- **API retry logic** — 503 "server busy" errors trigger automatic retry with exponential
  backoff (up to `api_max_retries` from config).
- **Archive pattern** — Each step archives processed inputs to the corresponding `_archive`
  folder (copy to archive, remove from input).
- **step_03 special** — The updated JSON (with image_url filled in) is saved directly into
  step_03/ alongside the generated images. step_04 reads from step_03/.
- **Credentials from .env** — `AGNES_API_KEY` and `AGNES_BASE_URL` loaded from `.env` file.

## Custom Actions

**Important:** The workflow builder must generate **new, robust action code** for
`generate_images` and `generate_videos`. Do NOT reuse the existing skill scripts
(`~/.qwen/skills/scripts/agnes_image_gen.py`, `agnes_video_gen.py`) directly — they
are simple single-item generators without batch processing, retry logic, or index
file generation.

The existing scripts can serve as **reference** for API call patterns (endpoints,
payload structure, authentication), but the generated actions must include:

### Required Action Features

1. **Batch processing** — iterate over all files in the input step directory
2. **Retry logic** — 503 "server busy" errors trigger automatic retry with exponential
   backoff (up to `api_max_retries` from config.json)
3. **Configurable timeouts** — HTTP request timeouts from `api_timeout` in config.json
4. **Config reading** — load settings from `config.json` (image/video params, delays, retries)
5. **Index file generation** — produce `index.json` listing all input→output file mappings
6. **Archive pattern** — copy processed inputs to `_archive` folder, remove from input
7. **Per-image filenames** — output filenames match input image stems
8. **Process delay** — pause between API calls (`process_delay` from config.json)
9. **Error handling** — graceful failure with detailed error messages, partial progress saved
10. **ActionResult return** — return APPROVED/REJECTED with remark and artifacts dict

### Action: generate_images

```
Action: generate_images
Purpose: Scan step_02/ for variant JSONs. For each JSON, call Agnes Image 2.1 Flash API
  for each variant using t2i_prompt1. Download images to step_03/. Update JSON with
  image_url. Save updated JSON to step_03/. Archive processed JSONs to step_02_archive/.
  Produce step_03/index.json listing all generated images.
Returns: APPROVED when all images generated, REJECTED with reject_code on failure.
```

### Action: generate_videos

```
Action: generate_videos
Purpose: Scan step_03/ for JSONs with image_url. For each JSON, call Agnes Video V2.0 API
  (image-to-video) using image_url and t2i_prompt1. Poll until complete. Download videos
  to step_04/. Archive processed files to step_03_archive/. Produce step_04/index.json
  listing all generated videos.
Returns: APPROVED when all videos generated, REJECTED with reject_code on failure.
```

### API Reference (from existing scripts)

**Image API:**
- Endpoint: `https://apihub.agnes-ai.com/v1/images/generations`
- Model: `agnes-image-2.1-flash`
- Payload: `{"model": "...", "prompt": "...", "size": "..."}`
- Response: `{"data": [{"url": "..."}]}`

**Video API:**
- Endpoint: `https://apihub.agnes-ai.com/v1/videos`
- Status: `https://apihub.agnes-ai.com/agnesapi?video_id=<ID>`
- Model: `agnes-video-v2.0`
- Payload: `{"model": "...", "prompt": "...", "image": "<url>", "width": ..., "height": ..., "num_frames": ..., "frame_rate": ...}`
- Poll until `status == "completed"`, then download from `url`

## Configuration File (media_config.json)

```json
{
  "image": {
    "model": "agnes-image-2.1-flash",
    "size": "1K",
    "ratio": "9:16"
  },
  "video": {
    "model": "agnes-video-v2.0",
    "width": 768,
    "height": 1344,
    "num_frames": 241,
    "frame_rate": 24
  },
  "num_variants": 4,
  "process_delay": 15,
  "coder_timeout": 900,
  "api_timeout": 500,
  "api_max_retries": 5
}
```

## Image Description JSON Schema (step_01 output)

Each description JSON follows this nested structure (reference: `download (1a).json`):

```json
{
  "image_filename": "original.jpg",
  "image_stem": "original",
  "descriptions": [
    {
      "subject_attributes": {
        "main_subject": "...",
        "subject_type": "...",
        "subject_description": "...",
        "distinctive_features": ["..."],
        "recognizable_objects": ["..."],
        "subject_state_or_pose": "..."
      },
      "scene_attributes": {
        "setting": "...",
        "environment": "...",
        "foreground": "...",
        "midground": "...",
        "background": "...",
        "time_of_day": "...",
        "season_or_weather": "...",
        "spatial_depth": "...",
        "parallax_potential": "..."
      },
      "composition_attributes": {
        "orientation": "...",
        "framing": "...",
        "camera_angle": "...",
        "subject_position": "...",
        "negative_space": "...",
        "visual_flow": "...",
        "depth_layers": ["..."]
      },
      "lighting_attributes": {
        "lighting_type": "...",
        "light_direction": "...",
        "light_quality": "...",
        "color_temperature": "...",
        "shadow_highlight_behavior": "...",
        "atmospheric_lighting": "..."
      },
      "style_attributes": {
        "visual_style": "...",
        "medium": "...",
        "realism_level": "...",
        "texture_quality": "...",
        "rendering_treatment": "..."
      },
      "color_attributes": {
        "dominant_colors": ["..."],
        "accent_colors": ["..."],
        "color_contrast": "...",
        "palette_mood": "..."
      },
      "mood_attributes": {
        "emotional_tone": "...",
        "atmosphere": "...",
        "viewer_feeling": "..."
      },
      "motion_potential": {
        "primary_motion_candidate": "...",
        "subject_motion_candidates": ["..."],
        "environmental_motion_candidates": ["..."],
        "camera_motion_candidates": ["..."],
        "motion_intensity_suggestion": "...",
        "motion_pacing_suggestion": "...",
        "motion_constraints": ["..."]
      },
      "extraction_confidence": {
        "overall_confidence": "...",
        "uncertain_attributes": []
      }
    }
  ]
}
```

## Prompt Variant JSON Schema (step_02 output)

Each variant JSON follows this structure (reference: `ugc_20260718_001.json`):

```json
{
  "mode": "BASE",
  "subject": "{image_stem}",
  "variations": [
    {
      "t2i_prompt1": "Detailed prompt for image generation and video motion...",
      "image_filename": "{stem}_01.png",
      "image_url": "https://..."
    }
  ]
}
```

Note: `image_url` is empty/absent after step_02. It gets filled in by step_03 (generate_images).
The `t2i_prompt1` is used for both image generation (step_03) and video motion (step_04).

## Legacy References

- Extract descriptions prompt adapted from: `Agnes.AI/image_csv_gen_v2/01_extract_desc.txt`
- Generate prompts adapted from: `Agnes.AI/image_csv_gen_v2/02_gen_prompts.txt`
- API call patterns reference: `~/.qwen/skills/scripts/agnes_image_gen.py` and
  `~/.qwen/skills/scripts/agnes_video_gen.py` (for endpoint/payload structure only —
  do NOT reuse these scripts directly, generate new robust action code instead)
- Key differences from legacy:
  - Description format: nested schema (not flat)
  - Prompt language: English (not Chinese)
  - No negative_prompt or workflowKey fields
  - Image/video generation uses Agnes API directly (not ComfyUI backend)
  - Batch processing with retry, timeout, and index file generation (not single-item)

## Notes

- The workflow defines its own folder structure (step_00/ through step_04/ with
  corresponding _archive/ folders). Any repo providing this structure can run this workflow.
- The workflow package lives in agent-runner-v2 repo under `workflows/agnes_media_gen_v1/`.
- The `.env` file in the runtime repo provides `AGNES_API_KEY` and `AGNES_BASE_URL`.
- Legacy prompt references (for adaptation, not direct reuse):
  - Extract descriptions: `image_csv_gen_v2/01_extract_desc.txt`
  - Generate prompts: `image_csv_gen_v2/02_gen_prompts.txt`
- **Action code must be generated fresh** — the workflow builder must create new action
  modules (`actions.py`) with batch processing, retry logic, config reading, and index
  file generation. Do not copy or import from the existing skill scripts.
