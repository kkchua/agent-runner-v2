# Agnes Media Generation v1

## Overview

The Agnes Media Generation v1 workflow is an end-to-end media creation pipeline
that automates the transformation of raw input images into animated videos. It
operates through four sequential stages:

1. **Extract Descriptions** - LLM vision-based extraction of structured image
   descriptions from input images.
2. **Generate Prompts** - LLM-based generation of multiple prompt variants per
   description for image and video generation.
3. **Generate Images** - Agnes Image 2.1 Flash API calls to generate new images
   from the prompt variants.
4. **Generate Videos** - Agnes Video V2.0 API calls to produce image-to-video
   animations from the generated images.

Each stage is gated by human review. Rejection triggers a rerun of the same
step with fresh execution. The workflow uses a self-referencing rejection
routing pattern where each step points to itself for re-execution on reject,
with a safety limit of 3 consecutive rejections before termination.

## Prerequisites

- agent-runner-v2 installed and initialized (`ukbe-run-agent init`)
- Python 3.10+ with `.venv` virtual environment
- Agnes API credentials (AGNES_API_KEY and AGNES_BASE_URL) configured in the
  target repository `.env` file
- A target repository with the following folder structure at its root:
  - step_00/ (input images)
  - step_00_archive/ (archive for processed input images)
  - step_01/ (structured description JSONs)
  - step_01_archive/
  - step_02/ (prompt variant JSONs)
  - step_02_archive/
  - step_03/ (generated images and updated JSONs)
  - step_03_archive/
  - step_04/ (generated video files)
  - step_04_archive/
- A config.json file at the target repository root with media generation
  parameters (image model/size, video model/dimensions, num_variants,
  process_delay, timeouts, retry settings)
- Network access to the Agnes API hub at https://apihub.agnes-ai.com

## Installation

1. Copy the workflow package directory to the workflows/ directory:

```
workflows/agnes_media_gen_v1/
  workflow.toml
  context_extensions.py
  prompts/
    01_extract_descriptions.txt
    02_generate_prompts.txt
```

2. Initialize the workflow (copies to global bootstrap if needed):

```
ukbe-run-agent init
```

3. Sync the workflow definition to the backend:

```
ukbe-run-agent sync-workflows agnes_media_gen_v1
```

## Configuration

The workflow uses a config.json file at the target repository root. The file
contains the following sections:

- **image**: model (agnes-image-2.1-flash), size, ratio
- **video**: model (agnes-video-v2.0), width, height, num_frames, frame_rate
- **pipeline**: num_variants (default 4), process_delay, coder_timeout,
  api_timeout, api_max_retries

Environment variables required in the target repository .env file:

- AGNES_API_KEY: API key for Agnes API hub authentication
- AGNES_BASE_URL: Base URL for the Agnes API hub
  (https://apihub.agnes-ai.com)

## Usage

### Batch File

Use the run script at the project root:

```
run-agnes_media_gen_v1.bat
```

### Manual Execution

```
.venv\Scripts\activate
ukbe-run-agent run --template-group agnes_media_gen_v1 --new-job
```

### Dry Run

To render prompts without invoking a coder:

```
ukbe-run-agent run --template-group agnes_media_gen_v1 --dry-run --new-job
```

### Operator Notes

- Place input images (PNG, JPG, WEBP) in the step_00/ directory before
  starting the workflow.
- If step_00 is empty, the extract_descriptions step will reject with
  NO_INPUT_IMAGES, allowing the user to add images and re-approve.
- Each step requires human approval after execution.
- The workflow archives processed inputs to corresponding _archive directories.

## Step Reference

| # | Step Name | Type | Role Policy | Purpose |
|---|---|---|---|---|
| 1 | extract_descriptions | prompt | architect_standard | Extract structured image descriptions from input images using LLM vision |
| 2 | generate_prompts | prompt | architect_standard | Generate N prompt variants per image description using LLM text generation |
| 3 | generate_images | action | - | Call Agnes Image 2.1 Flash API for text-to-image generation |
| 4 | generate_videos | action | - | Call Agnes Video V2.0 API for image-to-video animation |
| 5 | stepCompletion | action | - | Built-in terminal action marking workflow as COMPLETED |

## Artifact Keys

| Key | Path | Description |
|---|---|---|
| IMAGE_DESCRIPTIONS | step_01/index.json | Index manifest listing all structured description JSONs produced by extract_descriptions |
| PROMPT_VARIANTS | step_02/index.json | Index manifest listing all prompt variant JSONs produced by generate_prompts |
| IMAGE_INDEX | step_03/index.json | Index manifest listing all generated images and updated JSONs from generate_images |
| VIDEO_INDEX | step_04/index.json | Index manifest listing all generated video files from generate_videos |
| MEDIA_CONFIG | config.json | Media generation configuration file at target repo root |
