---
doc_type: "workflow_review"
lifecycle_status: "draft"
effective_version: "WFBUILD-20260725-0bb6afa4"
workflow_name: "agnes_media_gen_v1"
job_prefix: "AMGEN"
---

# Workflow Package Review: Agnes Media Generation v1

## Summary

The agnes_media_gen_v1 workflow package is well-structured and compliant with the workflow creation guide. All required files are present with proper structure, ASCII-only content, and consistent artifact key references. The workflow implements a self-referencing rejection routing pattern (documented in README.md lines 19-21), which differs from the standard SDLC refine loop pattern but is a valid design choice for this use case. All critical checks pass with no blocking issues.

## workflow.toml Findings

| Check | Status | Evidence |
|---|---|---|
| stepCompletion terminal step present | PASS | Lines 108-110: `[[step]] name = "stepCompletion"` with `action = "step_completion"` |
| init_step matches first step | PASS | Line 10: `init_step = "extract_descriptions"` matches first step name at line 16 |
| onsuccess targets valid steps | PASS | Line 20: `onsuccess = "generate_prompts"` (valid), Line 44: `onsuccess = "generate_images"` (valid), Line 69: `onsuccess = "generate_videos"` (valid), Line 91: `onsuccess = "stepCompletion"` (valid) |
| promotes key placement | N/A | No promote steps in this workflow |
| onsuccess placement at step level | PASS | All onsuccess declarations at step level (lines 20, 44, 69, 91), not inside [step.artifacts] |
| Prompt steps have [step.coder] with role_policy | PASS | extract_descriptions (line 27): `role_policy = "architect_standard"`, generate_prompts (line 52): `role_policy = "architect_standard"` |
| Prompt steps have produces and result_meta_key | PASS | extract_descriptions (lines 23-24): produces = ["IMAGE_DESCRIPTIONS"], result_meta_key = "IMAGE_DESCRIPTIONS"; generate_prompts (lines 48-49): produces = ["PROMPT_VARIANTS"], result_meta_key = "PROMPT_VARIANTS" |
| Review steps have requires_human_approval_after | PASS | All steps have `requires_human_approval_after = true` (lines 19, 43, 68, 90) |
| Review steps have [step.on_reject_refine] | PASS | All steps have on_reject_refine sections (lines 29-34, 54-59, 76-81, 98-103) |
| Refine steps have loop_returns_to | N/A | Workflow uses self-referencing rerun pattern (each step points to itself in on_reject_refine), no separate refine steps exist. This is documented in README.md as intentional design. |
| Step names unique and lowercase_with_underscores | PASS | All step names are unique: extract_descriptions, generate_prompts, generate_images, generate_videos, stepCompletion |

## context_extensions.py Findings

| Check | Status | Evidence |
|---|---|---|
| WorkflowExtensions class present and inherits correctly | PASS | Line 20: `class AgnesMediaGenExtensions(WorkflowExtensions):` |
| workflow_name matches directory name | PASS | Line 28: `workflow_name = "agnes_media_gen_v1"` matches workflow.toml name |
| register_artifact_keys() returns relative paths | PASS | Lines 45-51: Returns relative paths like `step_01/index.json`, `step_02/index.json`, etc. Note: No placeholders used - intentional for fixed step directory pattern that overwrites each run |
| build_context_extensions() returns absolute paths | PASS | Lines 79, 82, 88-105: All paths use `str(effective_root / ...)` for absolute resolution |
| install_to_global() method present | PASS | Lines 109-115: Returns `{"status": "NO_OP"}` |
| sync_to_backend() method present | PASS | Lines 117-123: Returns `{"status": "NO_OP"}` |
| All workflow.toml produces keys registered | PASS | workflow.toml produces: IMAGE_DESCRIPTIONS, PROMPT_VARIANTS, IMAGE_INDEX, VIDEO_INDEX. All present in register_artifact_keys() (lines 46-49). MEDIA_CONFIG also registered (line 50) for config access. |
| Docstrings present | PASS | Module (lines 1-10), class (lines 21-26), and all methods have docstrings |

## Prompt File Findings

| Check | Status | Evidence |
|---|---|---|
| Prompt files listed in index exist | PASS | Index lists prompts/01_extract_descriptions.txt and prompts/02_generate_prompts.txt - both exist |
| Placeholders use bare {KEY} format | PASS | All placeholders in both files use bare format: {STEP_00_DIR}, {STEP_01_DIR}, {MEDIA_CONFIG}, {IMAGE_DESCRIPTIONS}, {PROMPT_VARIANTS}, etc. No backtick-wrapped placeholders found. |
| All content ASCII-only | PASS | Verified both prompt files contain no em-dashes, curly quotes, or other Unicode characters |
| Each prompt has Objective section | PASS | 01_extract_descriptions.txt lines 1-8, 02_generate_prompts.txt lines 1-9 |
| Each prompt has Reference Inputs section | PASS | 01_extract_descriptions.txt lines 13-22, 02_generate_prompts.txt lines 11-17 |
| Each prompt has Output Instructions section | PASS | 01_extract_descriptions.txt lines 24-119, 02_generate_prompts.txt lines 19-58 |
| Artifact key references match contract | PASS | IMAGE_DESCRIPTIONS (01_extract_descriptions.txt line 110), PROMPT_VARIANTS (02_generate_prompts.txt line 48) - both match keys in context_extensions.py |

## Supplementary File Findings

### README.md

| Check | Status | Evidence |
|---|---|---|
| Overview section present | PASS | Lines 3-22 |
| Prerequisites section present | PASS | Lines 24-43 |
| Installation section present | PASS | Lines 45-68 |
| Usage section present | PASS | Lines 86-119 |
| Step Reference section present | PASS | Lines 120-129 |
| Artifact Keys section present | PASS | Lines 131-138 |
| Step reference table matches workflow.toml | PASS | Table lists: extract_descriptions, generate_prompts, generate_images, generate_videos, stepCompletion - matches workflow.toml step order |
| Configuration section matches sample files | PASS | Lines 70-85 describe AGNES_API_KEY, AGNES_BASE_URL, and config.json structure matching .env.sample and config.json.sample |

### .env.sample

| Check | Status | Evidence |
|---|---|---|
| File exists | PASS | Present in workflow package |
| Variables have descriptive comments | PASS | Lines 4-6: Comment explaining AGNES_API_KEY purpose; Lines 9-11: Comment explaining AGNES_BASE_URL purpose |
| Placeholder values present | PASS | Line 7: `AGNES_API_KEY=your_api_key_here`; Line 12: `AGNES_BASE_URL=https://apihub.agnes-ai.com` |

### config.json.sample

| Check | Status | Evidence |
|---|---|---|
| File exists | PASS | Present in workflow package |
| Valid JSON structure | PASS | Lines 1-21: Valid JSON with image, video, and pipeline sections |
| Sensible defaults | PASS | image.model = "agnes-image-2.1-flash", video.model = "agnes-video-v2.0", pipeline.num_variants = 4, etc. |

## Cross-File Consistency

| Check | Status | Evidence |
|---|---|---|
| Artifact keys consistent between workflow.toml and context_extensions.py | PASS | workflow.toml produces: IMAGE_DESCRIPTIONS, PROMPT_VARIANTS, IMAGE_INDEX, VIDEO_INDEX. context_extensions.py register_artifact_keys() includes all four plus MEDIA_CONFIG |
| Step names match prompt file naming | PASS | extract_descriptions -> prompts/01_extract_descriptions.txt; generate_prompts -> prompts/02_generate_prompts.txt |
| Routing targets reference existing steps | PASS | All onsuccess targets (generate_prompts, generate_images, generate_videos, stepCompletion) are defined step names |
| README artifact key table matches context_extensions.py | PASS | README lines 133-138 list: IMAGE_DESCRIPTIONS, PROMPT_VARIANTS, IMAGE_INDEX, VIDEO_INDEX, MEDIA_CONFIG - matches register_artifact_keys() |
| Configuration documentation matches sample files | PASS | README Configuration section describes AGNES_API_KEY, AGNES_BASE_URL, and config.json fields matching .env.sample and config.json.sample |

## Issues

No issues found. All checks pass.

## Verdict

APPROVED