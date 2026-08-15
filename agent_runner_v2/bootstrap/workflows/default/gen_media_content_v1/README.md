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

## Implementations

| Implementation | Description |
|---|---|
| agnes_full | Full pipeline using Agnes APIs for both image and video |
| happyhorse_product | Product-focused: Agnes images + HappyHorse video |
| video_only | Skip LLM/image steps, render videos from existing images |

Selecting an implementation auto-fills all dropdown defaults. Any value can
still be overridden per-job.

## Prerequisites

- Python 3.10+ with the agent-runner-v2 virtual environment activated
- API credentials for selected providers (see .env.sample)
- Target repository with step_00_inputimage/ through step_04_generatedvideo/

## Usage

```
ukbe-run-agent run --template-group gen_media_content_v1 --new-job
```
