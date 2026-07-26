---
doc_type: "prompts_index"
lifecycle_status: "draft"
effective_version: "WFBUILD-20260725-61c44baa"
workflow_name: "agnes_media_gen_v1"
job_id: "WFBUILD-20260725-61c44baa"
slug: "agnes_media_gen_v1"
---

# Prompts Index: Agnes Media Generation v1

## Prompt Files

| Step Sequence | Filename | Step Name | Purpose |
|---|---|---|---|
| 01 | prompts/01_extract_descriptions.txt | extract_descriptions | LLM vision step: scan input images in step_00/, produce structured description JSONs with 9 attribute groups in step_01/, archive processed images |
| 02 | prompts/02_generate_prompts.txt | generate_prompts | LLM text generation step: read description JSONs from step_01/, generate N prompt variants per description in step_02/, archive processed descriptions |

## Prompt File Details

### 01_extract_descriptions.txt

- Type: Prompt-driven (LLM vision)
- Role policy: architect_standard
- Input context variables: STEP_00_DIR, STEP_01_DIR, STEP_00_ARCHIVE, MEDIA_CONFIG, GOVERNANCE_RUNTIME_ROOT, PLATFORM_RUNTIME_ROOT
- Output artifact: IMAGE_DESCRIPTIONS
- Summary: Scans input directory for images (PNG, JPG, WEBP), uses vision to analyze each image, produces structured JSON with subject_attributes, scene_attributes, composition_attributes, lighting_attributes, style_attributes, color_attributes, mood_attributes, motion_potential, and extraction_confidence groups. Archives processed images and writes index.json.

### 02_generate_prompts.txt

- Type: Prompt-driven (LLM text generation)
- Role policy: architect_standard
- Input context variables: STEP_01_DIR, STEP_02_DIR, STEP_01_ARCHIVE, MEDIA_CONFIG, GOVERNANCE_RUNTIME_ROOT, PLATFORM_RUNTIME_ROOT
- Output artifact: PROMPT_VARIANTS
- Summary: Reads description JSONs, generates N variant prompt sets (N from config, default 4) with t2i_prompt1 field per variant. Saves variant JSONs with mode, subject, and variations array. Archives processed descriptions and writes index.json.
