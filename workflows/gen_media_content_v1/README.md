# Media Content Generation v1

## Overview

Media Content Generation v1 is a unified media generation pipeline with
pluggable LLM prompts and API providers. It transforms raw images placed
by an operator into animated videos through a four-step process:

1. **extract_descriptions** - LLM vision analyzes input images and produces
   structured JSON descriptions with attribute groups.
2. **generate_prompts** - LLM generates multiple prompt variants per
   description for image generation.
3. **generate_images** - Configurable image API provider generates images
   from the prompt variants.
4. **generate_videos** - Configurable video API provider converts generated
   images into animated videos.

Unlike the legacy workflows (agnes_media_gen_v1, agnes_gen_video_v1), this
workflow decouples steps from implementations. LLM prompts and API providers
are selected via dropdown (or impl preset), allowing any combination without
modifying the workflow definition.

## Directory Structure

```
gen_media_content_v1/
├── workflow.toml              # Pipeline definition (steps, slots, routing)
├── actions.py                 # Orchestrator + shared utilities (Phase 2)
├── context_extensions.py      # Step directory paths, config path injection
├── config.json.sample         # Sample runtime configuration
├── .env.sample                # Sample environment variables
├── README.md                  # This file
│
├── prompts/                   # LLM prompt pool (dropdown source)
│   ├── extract_desc/
│   └── generate_prompts/
│
├── api_actions/               # API provider pool (dynamically imported)
│   ├── render_image/          # Image generation providers
│   └── render_video/          # Video generation providers
│
├── impls/                     # BCS preset bundles
│   ├── agnes_full/
│   ├── happyhorse_product/
│   └── video_only/
│
└── tests/                     # Unit tests for this package
```

## Step-by-Step Pipeline

### Step 1: extract_descriptions (prompt-driven)

LLM vision scans input images and produces structured JSON descriptions.

| | |
|---|---|
| **Type** | Prompt-driven (LLM vision) |
| **Prompt slot** | `{{ slot.extract_desc }}` |
| **Input folder** | `step_00_inputimage/` — raw PNG/JPG/WEBP images placed by operator |
| **Output folder** | `step_01_imagedesc/` — one JSON per image + `index.json` |
| **Artifact** | `IMAGE_DESCRIPTIONS` → `step_01_imagedesc/index.json` |
| **On reject** | Refine loop (max 1 iteration) |

Each output JSON contains 9 attribute groups describing the image (subject,
environment, lighting, camera, composition, style, color, texture, mood).

### Step 1b: archive_step_00 (action-driven)

Archives processed input images from `step_00_inputimage/` to
`step_00_inputimage_archive/`. Uses `step_01_imagedesc/index.json` to
identify which files were processed. Deletes `index.json` files.

### Step 2: generate_prompts (prompt-driven)

LLM converts each image description JSON into multiple prompt variants
for image and video generation.

| | |
|---|---|
| **Type** | Prompt-driven (LLM text) |
| **Prompt slot** | `{{ slot.generate_prompts }}` |
| **Input folder** | `step_01_imagedesc/` — description JSONs from Step 1 |
| **Output folder** | `step_02_promptvariant/` — one `*_prompts.json` per description + `index.json` |
| **Artifact** | `PROMPT_VARIANTS` → `step_02_promptvariant/index.json` |
| **On reject** | Refine loop (max 1 iteration) |

Each output JSON contains N variations (configurable via `num_variants`),
each with `t2i_prompt1` (image generation) and `t2v_prompt1` (video
generation) fields.

### Step 2b: archive_step_01 (action-driven)

Archives all files from `step_01_imagedesc/` to `step_01_imagedesc_archive/`.
Deletes `index.json` files.

### Step 3: generate_images (action-driven)

Dynamically imports the configured `render_image` provider and calls the
API for each variant to generate images.

| | |
|---|---|
| **Type** | Action-driven (`generate_images_default`) |
| **Input folder** | `step_02_promptvariant/` — variant JSON files with `t2i_prompt1` |
| **Output folder** | `step_03_generatedimage/` — generated PNGs + updated variant JSONs + `index.json` |
| **Artifact** | `IMAGE_INDEX` → `step_03_generatedimage/index.json` |
| **Human approval** | Required before proceeding |

Provider selection via `config.json` → `actions.render_image`. The provider
module is loaded from `api_actions/render_image/{provider_name}/`. API key
rotation via `ApiKeyPool`. Supports partial success (some variants fail).

### Step 3b: archive_step_02 (action-driven)

Archives processed prompt variant files from `step_02_promptvariant/` to
`step_02_promptvariant_archive/`. Uses `step_03_generatedimage/index.json`
to identify processed files. Deletes `index.json` files. Runs after image
generation approval.

### Step 4: generate_videos (action-driven)

Dynamically imports the configured `render_video` provider and converts
each generated image into an animated video.

| | |
|---|---|
| **Type** | Action-driven (`generate_videos_default`) |
| **Input folder** | `step_03_generatedimage/` — generated images + variant JSONs (for video prompts) |
| **Output folder** | `step_04_generatedvideo/` — generated MP4s + `index.json` |
| **Artifact** | `VIDEO_INDEX` → `step_04_generatedvideo/index.json` |
| **Human approval** | Not required |

Cross-references `step_02_promptvariant/` for `t2v_prompt1` video prompts.
Falls back to image filename as prompt if no variant JSON found (video_only
mode). Provider loaded from `api_actions/render_video/{provider_name}/`.

### Step 4b: archive_step_03 (action-driven)

Archives all files from `step_03_generatedimage/` to
`step_03_generatedimage_archive/`. Archives everything (not filtered by
index) since some video generations may have failed. Deletes `index.json`
files.

### Step 5: stepCompletion (terminal)

Marks the job as complete.

## Target Repository Folder Layout

All step folders live in the target repository root (workspace_root):

```
{target_repo}/
├── config.json                        # Runtime configuration
├── .env                               # API credentials
├── step_00_inputimage/                # [INPUT] Raw images (operator places files here)
├── step_00_inputimage_archive/        # [ARCHIVE] Processed input images
├── step_01_imagedesc/                 # [STEP 1 OUTPUT] Image description JSONs
├── step_01_imagedesc_archive/         # [ARCHIVE] Processed description JSONs
├── step_02_promptvariant/             # [STEP 2 OUTPUT] Prompt variant JSONs
├── step_02_promptvariant_archive/     # [ARCHIVE] Processed prompt variants
├── step_03_generatedimage/            # [STEP 3 OUTPUT] Generated images (PNG)
├── step_03_generatedimage_archive/    # [ARCHIVE] Processed generated images
└── step_04_generatedvideo/            # [STEP 4 OUTPUT] Generated videos (MP4)
```

## Implementations

Each implementation is a preset bundle that auto-fills `config.json`
dropdown values. Any value can still be overridden per-job.

| Implementation | render_image | render_video | Use case |
|---|---|---|---|
| **agnes_full** | `agnes_v1` | `agnes_v2` | Full pipeline, Agnes APIs for both image and video |
| **happyhorse_product** | `agnes_v1` | `happyhorse_v1_1` | Product-focused, Agnes images + HappyHorse video |
| **video_only** | `__none__` (skip) | `agnes_v2` | Skip LLM/image steps, render videos from existing images in step_03 |

### Available API Providers

| Provider type | Provider name | API |
|---|---|---|
| render_image | `agnes_v1` | Agnes Image 2.1 Flash |
| render_video | `agnes_v2` | Agnes Video V2.0 |
| render_video | `happyhorse_v1_1` | HappyHorse 1.1 I2V (DashScope) |
| render_image / render_video | `__none__` | Skip step (no-op) |

## Configuration

### Environment Variables (.env)

| Variable | Description | Example |
|---|---|---|
| AGNES_API_KEY_1 | API key for Agnes services | your_api_key_here |
| AGNES_BASE_URL | Base URL for Agnes API | https://apihub.agnes-ai.com |
| HAPPYHORSE_API_KEY_1 | API key for HappyHorse (DashScope) | your_api_key_here |
| HAPPYHORSE_BASE_URL | Base URL for HappyHorse API | https://dashscope.aliyuncs.com |

### Runtime Configuration (config.json)

The config.json file in the target repository root controls:

| Section | Fields | Purpose |
|---|---|---|
| prompts | extract_desc, generate_prompts | Select prompt template variant |
| actions | render_image, render_video | Select API provider by name |
| api.<provider> | model-specific fields | Per-provider configuration |
| num_variants | int | Number of prompt variants per description |
| max_concurrent | int | Maximum concurrent API calls |
| process_delay | int | Seconds between consecutive API calls |
| coder_timeout | int | Seconds for LLM step timeouts |
| api_timeout | int | Seconds for HTTP request timeouts |
| api_max_retries | int | Maximum retry attempts for transient errors |

## Prerequisites

- Python 3.10+ with the agent-runner-v2 virtual environment activated
- API credentials for selected providers (see .env.sample)
- Target repository with step_00_inputimage/ through step_04_generatedvideo/

## Usage

```
ukbe-run-agent run --template-group gen_media_content_v1 --new-job
```
