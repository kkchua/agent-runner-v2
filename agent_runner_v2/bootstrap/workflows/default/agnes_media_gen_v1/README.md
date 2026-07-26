# Agnes Media Generation v1

## Overview

Agnes Media Generation v1 is an end-to-end media creation pipeline that
transforms raw images placed by an operator into animated videos. The
workflow consists of five steps:

1. **extract_descriptions** - LLM vision analyzes input images and produces
   structured JSON descriptions with nine attribute groups.
2. **generate_prompts** - LLM generates multiple prompt variants per
   description for image generation.
3. **generate_images** - Agnes Image 2.1 Flash API generates images from
   the prompt variants.
4. **generate_videos** - Agnes Video V2.0 API converts generated images
   into animated videos using image-to-video mode.
5. **stepCompletion** - Terminal step that marks the workflow as completed.

Each processing step includes a human review gate. The operator can approve
(output advances to next step) or reject (step re-executes from scratch).
All configuration (models, dimensions, variant counts, delays, timeouts,
retries) is read from a config.json file in the target repository.

## Prerequisites

- Python 3.10+ with the agent-runner-v2 virtual environment activated
- Agnes API access:
  - AGNES_API_KEY: Valid API key for Agnes services
  - AGNES_BASE_URL: Base URL for the Agnes API (default: https://apihub.agnes-ai.com)
- LLM with vision capability (for extract_descriptions step)
- Target repository with the following folder structure:
  - step_00/ - Input images (PNG, JPG, WEBP)
  - step_00_archive/ - Archive for processed input images
  - step_01/ - Structured description JSONs
  - step_01_archive/ - Archive for processed descriptions
  - step_02/ - Prompt variant JSONs
  - step_02_archive/ - Archive for processed variants
  - step_03/ - Generated images and updated JSONs
  - step_03_archive/ - Archive for processed step_03 inputs
  - step_04/ - Generated video files
  - step_04_archive/ - Archive for processed step_04 inputs
- config.json in the target repository root with media generation parameters

## Installation

1. Copy the workflow package to the workflows directory:
   ```
   cp -r agnes_media_gen_v1/ workflows/agnes_media_gen_v1/
   ```

2. Run the initialization command to seed global paths:
   ```
   ukbe-run-agent init
   ```

3. Sync the workflow definition to the backend:
   ```
   ukbe-run-agent sync-workflows agnes_media_gen_v1
   ```

4. Verify the workflow package:
   ```
   .venv\Scripts\python -c "from agent_runner_v2.workflow_bundle_validator import validate_workflow_bundle_dir; from pathlib import Path; print(validate_workflow_bundle_dir(Path('workflows/agnes_media_gen_v1')).to_dict())"
   ```

## Configuration

### Environment Variables (.env)

| Variable | Description | Example |
|---|---|---|
| AGNES_API_KEY | API key for Agnes services | your_api_key_here |
| AGNES_BASE_URL | Base URL for Agnes API endpoints | https://apihub.agnes-ai.com |

### Runtime Configuration (config.json)

The config.json file must be placed in the target repository root. It
provides the following parameters:

| Parameter | Description | Default |
|---|---|---|
| image.model | Image generation model identifier | agnes-image-2.1-flash |
| image.size | Image dimensions (WxH) | 1024x1024 |
| image.ratio | Image aspect ratio | 1:1 |
| video.model | Video generation model identifier | agnes-video-v2.0 |
| video.width | Video width in pixels | 1024 |
| video.height | Video height in pixels | 576 |
| video.num_frames | Number of frames per video | 72 |
| video.frame_rate | Video frame rate | 24 |
| num_variants | Number of prompt variants per description | 4 |
| process_delay | Seconds between consecutive API calls | 15 |
| coder_timeout | Seconds for LLM step timeouts | 900 |
| api_timeout | Seconds for HTTP request timeouts | 500 |
| api_max_retries | Maximum retry attempts for 503 errors | 5 |

## Usage

### Batch File

Run the workflow using the batch file at the project root:
```
run-agnes_media_gen_v1.bat
```

### Operator Console

Start a new workflow job from the operator console:
```
ukbe-run-agent run --template-group agnes_media_gen_v1 --new-job
```

### Daemon Mode

The workflow can be submitted to the daemon for background processing:
```
ukbe-run-agent submit --template-group agnes_media_gen_v1
```

### Dry Run

Render prompts without invoking a coder (for testing):
```
ukbe-run-agent run --template-group agnes_media_gen_v1 --dry-run --new-job
```

## Step Reference

| Step Name | Type | Role Policy | Purpose |
|---|---|---|---|
| extract_descriptions | prompt | architect_standard | LLM vision analyzes images, produces structured JSON descriptions |
| generate_prompts | prompt | architect_standard | LLM generates N prompt variants per description |
| generate_images | action | (none) | Agnes Image 2.1 Flash API generates images from variants |
| generate_videos | action | (none) | Agnes Video V2.0 API generates videos from images |
| stepCompletion | action | (none) | Terminal step, marks workflow as COMPLETED |

All four processing steps have requires_human_approval_after = true with
self-referencing on_reject_refine (rerun same step on reject).

## Artifact Keys

| Artifact Key | Path Pattern | Description |
|---|---|---|
| IMAGE_DESCRIPTIONS | step_01/index.json | Index manifest of structured image description JSONs |
| PROMPT_VARIANTS | step_02/index.json | Index manifest of prompt variant JSONs |
| IMAGE_INDEX | step_03/index.json | Index manifest of generated images and updated JSONs |
| VIDEO_INDEX | step_04/index.json | Index manifest of generated video files |
| MEDIA_CONFIG | config.json | Media generation configuration file (operator-provided) |
