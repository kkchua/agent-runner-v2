---
doc_type: "step_architecture"
lifecycle_status: "draft"
effective_version: "WFBUILD-20260725-61c44baa"
workflow_name: "agnes_media_gen_v1"
job_id: "WFBUILD-20260725-61c44baa"
slug: "agnes_media_gen_v1"
source_requirements: "docs/repo/workflow_builder/runs/WFBUILD-20260725-61c44baa/REQUIREMENTS-20260726-001_media_gen_v1.md"
source_artifacts: "docs/repo/workflow_builder/runs/WFBUILD-20260725-61c44baa/ARTIFACTS-20260726-001_media_gen_v1.md"
---

# Step Architecture: Agnes Media Generation v1

## Step Sequence

The workflow executes 5 steps in the following order:

1. extract_descriptions - Prompt-driven step (LLM vision). Role policy: architect_standard. Reads input images from step_00/ and produces structured description JSON files in step_01/ with an index.json manifest.

2. generate_prompts - Prompt-driven step (LLM text generation). Role policy: architect_standard. Reads description JSONs from step_01/ and produces prompt variant JSON files in step_02/ with an index.json manifest.

3. generate_images - Action-driven step (Python API call). No role policy. Reads prompt variant JSONs from step_02/ and calls the Agnes Image 2.1 Flash API to produce images in step_03/ with an index.json manifest.

4. generate_videos - Action-driven step (Python API call). No role policy. Reads updated variant JSONs with image_url from step_03/ and calls the Agnes Video V2.0 API to produce video files in step_04/ with an index.json manifest.

5. stepCompletion - Action-driven step (built-in terminal action). No role policy. Marks the workflow as COMPLETED.

All four operational steps (extract_descriptions, generate_prompts, generate_images, generate_videos) carry requires_human_approval_after = true. Each step uses a self-referencing on_reject_refine pattern: when the human operator rejects the step output, the same step re-executes from scratch.

## Step Details

### extract_descriptions

| Field | Value |
|---|---|
| Name | extract_descriptions |
| Type | prompt-driven |
| Prompt file | prompts/01_extract_descriptions.txt |
| Role policy | architect_standard |
| requires_human_approval_after | true |

Artifact bindings:

| Binding | Keys |
|---|---|
| required_inputs | (none - uses context variables STEP_00_DIR, STEP_00_ARCHIVE, STEP_01_DIR, STEP_01_ARCHIVE, MEDIA_CONFIG, GOVERNANCE_RUNTIME_ROOT, PLATFORM_RUNTIME_ROOT) |
| produces | IMAGE_DESCRIPTIONS |
| result_meta_key | IMAGE_DESCRIPTIONS |

Routing rules:

| Rule | Target |
|---|---|
| onsuccess | generate_prompts |
| on_reject_refine.step | extract_descriptions |
| on_reject_refine.artifact | IMAGE_DESCRIPTIONS |
| on_reject_refine.max_iterations | 1 |
| on_reject_refine.exhausted_failure_code | DESCRIPTION_EXTRACT_EXHAUSTED |
| on_reject_refine.exhausted_failure_class | HUMAN_RETRY_REQUIRED |

Notes: The coder reads each image in STEP_00_DIR, uses LLM vision to produce a structured description JSON per image, writes per-image JSONs to STEP_01_DIR, writes index.json to STEP_01_DIR, and archives processed images from STEP_00_DIR to STEP_00_ARCHIVE. The self-referencing on_reject_refine means that if the human operator rejects the output, the entire extract_descriptions step re-executes.

### generate_prompts

| Field | Value |
|---|---|
| Name | generate_prompts |
| Type | prompt-driven |
| Prompt file | prompts/02_generate_prompts.txt |
| Role policy | architect_standard |
| requires_human_approval_after | true |

Artifact bindings:

| Binding | Keys |
|---|---|
| required_inputs | IMAGE_DESCRIPTIONS |
| produces | PROMPT_VARIANTS |
| result_meta_key | PROMPT_VARIANTS |

Routing rules:

| Rule | Target |
|---|---|
| onsuccess | generate_images |
| on_reject_refine.step | generate_prompts |
| on_reject_refine.artifact | PROMPT_VARIANTS |
| on_reject_refine.max_iterations | 1 |
| on_reject_refine.exhausted_failure_code | PROMPT_GENERATION_EXHAUSTED |
| on_reject_refine.exhausted_failure_class | HUMAN_RETRY_REQUIRED |

Notes: The coder reads each description JSON from STEP_01_DIR, generates N prompt variants per description (N from MEDIA_CONFIG num_variants, default 4), writes per-image variant JSONs to STEP_02_DIR, writes index.json to STEP_02_DIR, and archives processed description JSONs from STEP_01_DIR to STEP_01_ARCHIVE.

### generate_images

| Field | Value |
|---|---|
| Name | generate_images |
| Type | action-driven |
| Action function | generate_images |
| Role policy | (none - action steps do not use role policies) |
| requires_human_approval_after | true |

Artifact bindings:

| Binding | Keys |
|---|---|
| required_inputs | PROMPT_VARIANTS, MEDIA_CONFIG |
| produces | IMAGE_INDEX |
| result_meta_key | IMAGE_INDEX |

Routing rules:

| Rule | Target |
|---|---|
| onsuccess | generate_videos |
| on_reject_refine.step | generate_images |
| on_reject_refine.artifact | IMAGE_INDEX |
| on_reject_refine.max_iterations | 1 |
| on_reject_refine.exhausted_failure_code | IMAGE_GENERATION_EXHAUSTED |
| on_reject_refine.exhausted_failure_class | HUMAN_RETRY_REQUIRED |

Notes: The action function reads variant JSONs from STEP_02_DIR, calls Agnes Image 2.1 Flash API for each variant with batch processing and retry logic for 503 errors, downloads generated images to STEP_03_DIR, updates variant JSONs with image_url field, writes index.json to STEP_03_DIR, and archives processed variant JSONs from STEP_02_DIR to STEP_02_ARCHIVE. On partial failure (some images succeed, some fail), the action returns REJECTED with detailed error messages. The human review gate allows the operator to inspect partial results and decide whether to approve or re-run.

### generate_videos

| Field | Value |
|---|---|
| Name | generate_videos |
| Type | action-driven |
| Action function | generate_videos |
| Role policy | (none - action steps do not use role policies) |
| requires_human_approval_after | true |

Artifact bindings:

| Binding | Keys |
|---|---|
| required_inputs | IMAGE_INDEX, MEDIA_CONFIG |
| produces | VIDEO_INDEX |
| result_meta_key | VIDEO_INDEX |

Routing rules:

| Rule | Target |
|---|---|
| onsuccess | stepCompletion |
| on_reject_refine.step | generate_videos |
| on_reject_refine.artifact | VIDEO_INDEX |
| on_reject_refine.max_iterations | 1 |
| on_reject_refine.exhausted_failure_code | VIDEO_GENERATION_EXHAUSTED |
| on_reject_refine.exhausted_failure_class | HUMAN_RETRY_REQUIRED |

Notes: The action function reads updated variant JSONs from STEP_03_DIR (which now contain image_url), calls Agnes Video V2.0 API for each image with submission, status polling, and download, saves video files to STEP_04_DIR, writes index.json to STEP_04_DIR, and archives processed inputs from STEP_03_DIR to STEP_03_ARCHIVE. On partial failure, returns REJECTED with detailed error messages per the DD-004 design decision.

### stepCompletion

| Field | Value |
|---|---|
| Name | stepCompletion |
| Type | action-driven |
| Action function | step_completion (built-in) |
| Role policy | (none) |
| requires_human_approval_after | false |

Artifact bindings:

| Binding | Keys |
|---|---|
| required_inputs | VIDEO_INDEX |
| produces | (none) |
| result_meta_key | (none) |

Routing rules:

| Rule | Target |
|---|---|
| onsuccess | (terminal) |

Notes: Built-in terminal action. Marks the workflow job as COMPLETED. No human approval gate on this step.

## Routing Diagram

The following ASCII diagram shows the complete step flow including conditional branches.

```
                          WORKFLOW START
                              |
                              v
                 +---> extract_descriptions ----+
                 |      (prompt, human gate)     |
                 |                               |
                 |         onsuccess             |
                 |              |                |
                 |              v                |
                 |      generate_prompts --------+
                 |      (prompt, human gate)     |
                 |                               |
                 |         onsuccess             |
                 |              |                |
                 |              v                |
                 |      generate_images ---------+
                 |      (action, human gate)     |
                 |                               |
                 |         onsuccess             |
                 |              |                |
                 |              v                |
                 |      generate_videos ---------+
                 |      (action, human gate)     |
                 |                               |
                 |         onsuccess             |
                 |              |                |
                 |              v                |
                 |       stepCompletion          |
                 |         (terminal)            |
                 |                               |
                 +-------------------------------+
                     on_reject_refine (self)

  Detail for each step:
  +---------------------------+
  | APPROVED by human         | --> onsuccess --> next step
  |                           |
  | REJECTED by human         | --> on_reject_refine --> same step (re-run)
  |                           |
  | REJECTED x max_iterations | --> exhausted_failure --> job FAILED
  |   (exhausted)             |     HUMAN_RETRY_REQUIRED
  +---------------------------+
```

Conditional branch summary per step:

```
extract_descriptions:
  APPROVED  --> generate_prompts
  REJECTED  --> extract_descriptions (re-run, max 1 iteration)
  EXHAUSTED --> job FAILED (DESCRIPTION_EXTRACT_EXHAUSTED)

generate_prompts:
  APPROVED  --> generate_images
  REJECTED  --> generate_prompts (re-run, max 1 iteration)
  EXHAUSTED --> job FAILED (PROMPT_GENERATION_EXHAUSTED)

generate_images:
  APPROVED  --> generate_videos
  REJECTED  --> generate_images (re-run, max 1 iteration)
  EXHAUSTED --> job FAILED (IMAGE_GENERATION_EXHAUSTED)

generate_videos:
  APPROVED  --> stepCompletion
  REJECTED  --> generate_videos (re-run, max 1 iteration)
  EXHAUSTED --> job FAILED (VIDEO_GENERATION_EXHAUSTED)
```

## Terminal Steps

| Step | Type | Behavior |
|---|---|---|
| stepCompletion | action (step_completion) | Built-in terminal action. Marks workflow job as COMPLETED. No routing beyond this step. |

Failure routing:

- When any step exhausts its max_rejects (max_iterations reached in on_reject_refine), the workflow job transitions to FAILED status with the corresponding exhausted_failure_code.
- The exhausted_failure_class for all steps is HUMAN_RETRY_REQUIRED, indicating the operator must manually retry the entire workflow job.
- There is no on_exhaust_replan routing in this workflow. Each step uses self-referencing rejection, so exhaustion means the operator rejected the same step output twice (original run + 1 retry).

## Configuration Summary

| Parameter | Value | Notes |
|---|---|---|
| init_step | extract_descriptions | First step in the workflow sequence |
| default_max_rejects | 3 | Framework default; each step overrides with on_reject_refine.max_iterations = 1 |
| enable_notifications | true | Set on all operational steps (extract_descriptions, generate_prompts, generate_images, generate_videos). Not set on stepCompletion. |

Additional configuration flags:

| Flag | Value | Applied To |
|---|---|---|
| requires_human_approval_after | true | extract_descriptions, generate_prompts, generate_images, generate_videos |
| requires_human_approval_after | false | stepCompletion |

Traceability matrix:

| Step ID | Source Requirement | Artifact Produced |
|---|---|---|
| extract_descriptions | REQUIREMENTS: Output Artifacts (IMAGE_DESCRIPTIONS), Constraints (Role Policies) | IMAGE_DESCRIPTIONS |
| generate_prompts | REQUIREMENTS: Output Artifacts (PROMPT_VARIANTS), Constraints (Role Policies) | PROMPT_VARIANTS |
| generate_images | REQUIREMENTS: Output Artifacts (IMAGE_INDEX), Constraints (External Dependencies) | IMAGE_INDEX |
| generate_videos | REQUIREMENTS: Output Artifacts (VIDEO_INDEX), Constraints (External Dependencies) | VIDEO_INDEX |
| stepCompletion | WORKFLOW_CREATION_GUIDE: terminal step requirement | (none) |
