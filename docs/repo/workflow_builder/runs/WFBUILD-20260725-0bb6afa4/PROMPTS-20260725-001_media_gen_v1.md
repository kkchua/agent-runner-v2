---
doc_type: "prompts_index"
lifecycle_status: "draft"
effective_version: "WFBUILD-20260725-0bb6afa4"
workflow_name: "agnes_media_gen_v1"
job_prefix: "AMGEN"
---

# Prompts Index: Agnes Media Generation v1

This document lists all prompt template files generated for the
agnes_media_gen_v1 workflow package.

## Prompt Files

| # | Step Name | Prompt File | Role Policy | Purpose |
|---|---|---|---|---|
| 1 | extract_descriptions | prompts/01_extract_descriptions.txt | architect_standard | Scan input images from step_00 directory, use LLM vision to extract structured image descriptions into 9 attribute groups (49 fields), produce description JSONs and index manifest in step_01. |
| 2 | generate_prompts | prompts/02_generate_prompts.txt | architect_standard | Read structured descriptions from step_01, generate N variant prompt sets per image (configurable via MEDIA_CONFIG), produce variant JSONs and index manifest in step_02. |

## Action-Driven Steps (No Prompt Files)

| # | Step Name | Action Function | Purpose |
|---|---|---|---|
| 3 | generate_images | generate_images | Read prompt variant JSONs from step_02, call Agnes Image 2.1 Flash API for text-to-image generation, save images and updated JSONs to step_03. |
| 4 | generate_videos | generate_videos | Read updated variant JSONs from step_03 (with image_url populated), call Agnes Video V2.0 API for image-to-video generation, save videos to step_04. |
| 5 | stepCompletion | step_completion | Built-in terminal action that marks the workflow as COMPLETED. |

## Prompt File Naming Convention

Prompt files follow the pattern: prompts/NN_step_name.txt
where NN is the step sequence number (zero-padded to 2 digits).

## Prompt Content Rules

- All prompt files use bare {ARTIFACT_KEY} placeholders (never backtick-wrapped).
- All content is ASCII-only.
- Each prompt includes Objective, Reference Inputs, and Output Instructions sections.
- Placeholder values are resolved at runtime by the runner from context_extensions.py.
