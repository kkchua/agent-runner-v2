---
doc_type: "step_architecture"
lifecycle_status: "draft"
effective_version: "WFBUILD-20260725-0bb6afa4"
workflow_name: "agnes_media_gen_v1"
job_prefix: "AMGEN"
---

# Step Architecture: Agnes Media Generation v1

## Step Sequence

The workflow consists of 5 steps: 4 pipeline steps (2 prompt-driven, 2
action-driven) followed by the terminal stepCompletion action. All pipeline
steps require human approval after execution.

| # | Step Name | Type | Role Policy | Produces | Routes To |
|---|---|---|---|---|---|
| 1 | extract_descriptions | prompt-driven | architect_standard | IMAGE_DESCRIPTIONS | generate_prompts |
| 2 | generate_prompts | prompt-driven | architect_standard | PROMPT_VARIANTS | generate_images |
| 3 | generate_images | action-driven | (none) | IMAGE_INDEX | generate_videos |
| 4 | generate_videos | action-driven | (none) | VIDEO_INDEX | stepCompletion |
| 5 | stepCompletion | action-driven | (none) | (terminal) | terminal |

Notes:
- Steps 1 and 2 are prompt-driven LLM invocations. Step 1 uses LLM vision
  to extract structured image descriptions. Step 2 uses LLM text generation
  to produce prompt variants from those descriptions.
- Steps 3 and 4 are action-driven Python functions that call external
  Agnes APIs for image generation and video generation respectively.
- Step 5 is the built-in terminal action that marks workflow completion.
- Role policy is only assigned to prompt-driven steps. Action steps do
  not use role policies.

## Step Details

### extract_descriptions

- Step name: extract_descriptions
- Step type: prompt-driven
- Prompt file: prompts/01_extract_descriptions.txt
- Role policy: architect_standard

Artifact bindings:
- required_inputs: (none)
- produces: IMAGE_DESCRIPTIONS
- result_meta_key: IMAGE_DESCRIPTIONS

Notes:
- This step scans IMAGE_INPUT_DIR (resolved at runtime to step_00/) for
  PNG, JPG, and WEBP image files.
- If no images are found, the step must return REJECTED with reject_code
  NO_INPUT_IMAGES and a descriptive remark.
- The step produces one structured description JSON per input image,
  plus an index.json manifest at step_01/index.json.
- After successful extraction, processed input images are copied to
  IMAGE_INPUT_ARCHIVE (step_00_archive/) and removed from step_00/.

Routing rules:
- onsuccess: generate_prompts
- requires_human_approval_after: true
- on_reject_refine: self-referencing (step = extract_descriptions,
  artifact = IMAGE_DESCRIPTIONS)
- Rejection reruns the same step with fresh LLM invocation.

### generate_prompts

- Step name: generate_prompts
- Step type: prompt-driven
- Prompt file: prompts/02_generate_prompts.txt
- Role policy: architect_standard

Artifact bindings:
- required_inputs: IMAGE_DESCRIPTIONS
- produces: PROMPT_VARIANTS
- result_meta_key: PROMPT_VARIANTS

Notes:
- This step reads the structured description JSONs from step_01/ and
  produces N variant prompt sets per image (N from MEDIA_CONFIG
  num_variants, default 4).
- Per design decision DD-002, granularity is per-image (one variant
  JSON per input image), not per-description-entry.
- The step produces one prompt variant JSON per input image, plus an
  index.json manifest at step_02/index.json.
- After successful generation, processed description JSONs are copied
  to step_01_archive/ and removed from step_01/.

Routing rules:
- onsuccess: generate_images
- requires_human_approval_after: true
- on_reject_refine: self-referencing (step = generate_prompts,
  artifact = PROMPT_VARIANTS)
- Rejection reruns the same step with fresh LLM invocation.

### generate_images

- Step name: generate_images
- Step type: action-driven
- Action function: generate_images
- Role policy: (none - action steps do not use role policies)

Artifact bindings:
- required_inputs: PROMPT_VARIANTS
- produces: IMAGE_INDEX
- result_meta_key: IMAGE_INDEX

Notes:
- This step reads prompt variant JSONs from step_02/ and calls the
  Agnes Image 2.1 Flash API for text-to-image generation.
- Each variant object contains a t2i_prompt1 text prompt. The action
  calls the images/generations endpoint for each variant.
- Generated images are saved to step_03/ with filenames derived from
  the variant JSON image_filename field (format: {stem}_{NN}.png).
- The action also updates the variant JSON files by populating the
  image_url field with the returned URL from the API.
- The step produces an index.json manifest at step_03/index.json.
- After successful generation, processed variant JSONs are copied to
  step_02_archive/ and removed from step_02/.
- The action includes: batch processing, retry logic with exponential
  backoff for 503 errors, configurable timeouts, per-image filename
  handling, process delay between API calls, error handling with
  partial progress saving, and ActionResult return values.

Routing rules:
- onsuccess: generate_videos
- requires_human_approval_after: true
- on_reject_refine: self-referencing (step = generate_images,
  artifact = IMAGE_INDEX)
- Rejection reruns the same action, re-executing all API calls.

### generate_videos

- Step name: generate_videos
- Step type: action-driven
- Action function: generate_videos
- Role policy: (none - action steps do not use role policies)

Artifact bindings:
- required_inputs: IMAGE_INDEX
- produces: VIDEO_INDEX
- result_meta_key: VIDEO_INDEX

Notes:
- This step reads the updated variant JSONs from step_03/ (with
  image_url populated) and calls the Agnes Video V2.0 API for
  image-to-video generation.
- Each variant object contains a t2i_prompt1 text prompt used as the
  motion prompt for video generation. The image_url provides the
  source image for animation.
- The action calls the videos endpoint, then polls the status
  endpoint until status equals completed, then downloads the video
  from the returned URL.
- Generated videos are saved to step_04/ with filenames derived from
  image stems.
- The step produces an index.json manifest at step_04/index.json.
- After successful generation, processed step_03 files are copied to
  step_03_archive/ and removed from step_03/.
- The action includes: batch processing, retry logic with exponential
  backoff for 503 errors, configurable timeouts, status polling,
  video download, per-image filename handling, process delay between
  API calls, error handling with partial progress saving, and
  ActionResult return values.

Routing rules:
- onsuccess: stepCompletion
- requires_human_approval_after: true
- on_reject_refine: self-referencing (step = generate_videos,
  artifact = VIDEO_INDEX)
- Rejection reruns the same action, re-executing all API calls.

### stepCompletion

- Step name: stepCompletion
- Step type: action-driven (built-in terminal action)
- Action function: step_completion
- Role policy: (none)

Artifact bindings:
- required_inputs: (none)
- produces: (none)
- result_meta_key: (none)

Notes:
- Built-in terminal action that marks the workflow as COMPLETED.
- No prompt file, no role policy, no artifact bindings.
- This step is required by all workflows. Without it, the workflow
  never reaches COMPLETED status.

Routing rules:
- This is the terminal step. No onsuccess routing.

## Routing Diagram

The following ASCII diagram shows the step flow including conditional
branches. Each pipeline step has a human approval gate. On rejection,
the step reruns itself (self-referencing pattern per DD-003).

```
+------------------------+
| extract_descriptions   |  (prompt, architect_standard)
| produces:              |
|   IMAGE_DESCRIPTIONS   |
+------------------------+
          |
          | onsuccess (human approved)
          v
+------------------------+
| generate_prompts       |  (prompt, architect_standard)
| requires:              |
|   IMAGE_DESCRIPTIONS   |
| produces:              |
|   PROMPT_VARIANTS      |
+------------------------+
          |
          | onsuccess (human approved)
          v
+------------------------+
| generate_images        |  (action: generate_images)
| requires:              |
|   PROMPT_VARIANTS      |
| produces:              |
|   IMAGE_INDEX          |
+------------------------+
          |
          | onsuccess (human approved)
          v
+------------------------+
| generate_videos        |  (action: generate_videos)
| requires:              |
|   IMAGE_INDEX          |
| produces:              |
|   VIDEO_INDEX          |
+------------------------+
          |
          | onsuccess (human approved)
          v
+------------------------+
| stepCompletion         |  (action: step_completion)
| terminal               |
+------------------------+
```

Rejection routing (applies to each pipeline step):

```
                  +-------------------+
                  | Human Review Gate |
                  | requires_human_   |
                  | approval_after    |
                  +-------------------+
                     /             \
          approved  /               \  rejected
                   /                 \
                  v                   v
          advance to            rerun same step
          next step             (self-referencing)
```

Self-reference detail per step:

```
extract_descriptions --[reject]--> extract_descriptions
generate_prompts     --[reject]--> generate_prompts
generate_images      --[reject]--> generate_images
generate_videos      --[reject]--> generate_videos
```

The default_max_rejects setting (3) provides a safety limit on the
number of consecutive rejections before the workflow terminates with
failure.

## Terminal Steps

| Step Name | Type | Action Function | Purpose |
|---|---|---|---|
| stepCompletion | action | step_completion | Marks workflow as COMPLETED |

Failure routing:
- If a pipeline step exceeds the maximum rejection count
  (default_max_rejects = 3), the workflow terminates with failure.
  The exhausted_failure_class is HUMAN_RETRY_REQUIRED.
- If an action step returns REJECTED and the rejection count is
  exceeded, the same termination applies.
- There is no fallback or replan step. The workflow ends.

## Configuration Summary

| Setting | Value |
|---|---|
| init_step | extract_descriptions |
| default_max_rejects | 3 |
| enable_notifications | true (on all pipeline steps) |

Notes:
- init_step is set to extract_descriptions, the first step in the
  pipeline.
- default_max_rejects is 3, providing a safety limit on rejections.
  Each step inherits this limit unless overridden at the step level.
- enable_notifications is set to true on all 4 pipeline steps. The
  terminal stepCompletion step does not use notifications.
- All 4 pipeline steps have requires_human_approval_after = true.
  This is the primary quality gate mechanism for the workflow.
- The on_reject_refine routing uses the self-referencing pattern per
  design decision DD-003. Each step points to itself for re-execution
  on rejection.
