---
doc_type: "test_criteria"
lifecycle_status: "draft"
effective_version: "WFBUILD-20260725-61c44baa"
spec_reference: "agnes_media_gen_v1"
created_at: "2026-07-26"
workflow_builder_run: "WFBUILD-20260725-61c44baa"
---

# Test Criteria: Agnes Media Generation v1

## Spec Objective Summary

The agnes_media_gen_v1 workflow implements an end-to-end media generation
pipeline that transforms raw images placed by a user into animated videos.
The pipeline has five stages: (1) LLM vision extracts structured descriptions
from input images, (2) LLM generates multiple prompt variants per description,
(3) Agnes Image 2.1 Flash API generates images from those prompts, (4) Agnes
Video V2.0 API converts generated images into videos using image-to-video mode,
and (5) a terminal completion step. Each processing step is gated by a human
review approval gate, where rejection causes the step to be re-run. The workflow
is a mixed type combining prompt-driven LLM steps (extract_descriptions,
generate_prompts) with action-driven steps (generate_images, generate_videos).
All configuration (models, dimensions, variant counts, delays, timeouts, retries)
is read from a config.json file at runtime. The workflow defines its own folder
structure (step_00 through step_04 with corresponding archive folders) and
operates in any target repo providing that structure. There are no user-provided
inputs; all context variables are hardcoded in context_extensions.py and resolved
at runtime from the target repo root.

## Criteria for analyze_spec step

The analyze_spec step produces a WORKFLOW_REQUIREMENTS document that captures
the full scope of the specification for downstream consumption by the package
generation steps.

### Workflow Type Classification

1. The requirements document MUST classify the workflow type as "mixed" --
   containing both prompt-driven steps (extract_descriptions, generate_prompts)
   and action-driven steps (generate_images, generate_videos, step_completion).

2. The requirements document MUST identify exactly four processing steps plus
   one terminal step: extract_descriptions (prompt), generate_prompts (prompt),
   generate_images (action), generate_videos (action), and stepCompletion
   (action/terminal).

### Input/Output Artifact Identification

3. The requirements document MUST state that there are no user-provided inputs
   (required_inputs must be empty for all steps). All paths are resolved at
   runtime from the target repo root via context_extensions.py.

4. The requirements document MUST identify the following output artifacts:
   IMAGE_DESCRIPTIONS (step_01/index.json), PROMPT_VARIANTS (step_02/index.json),
   IMAGE_INDEX (step_03/index.json), and VIDEO_INDEX (step_04/index.json).

5. The requirements document MUST identify the following context variables:
   STEP_00_DIR, STEP_00_ARCHIVE, STEP_01_DIR, STEP_01_ARCHIVE, STEP_02_DIR,
   STEP_02_ARCHIVE, STEP_03_DIR, STEP_03_ARCHIVE, STEP_04_DIR, STEP_04_ARCHIVE,
   MEDIA_CONFIG, GOVERNANCE_RUNTIME_ROOT, and PLATFORM_RUNTIME_ROOT.

### Step-by-Step Requirements Capture

6. The requirements document MUST capture the purpose of extract_descriptions:
   scan step_00/ for images (PNG, JPG, WEBP), use LLM vision to produce
   structured description JSONs with nested schema (subject_attributes,
   scene_attributes, composition_attributes, lighting_attributes,
   style_attributes, color_attributes, mood_attributes, motion_potential,
   extraction_confidence), save to step_01/, archive processed images to
   step_00_archive/.

7. The requirements document MUST capture the purpose of generate_prompts:
   scan step_01/ for description JSONs, generate N variant prompt sets
   (configurable, default 4) each with t2i_prompt1, save to step_02/,
   archive processed JSONs to step_01_archive/.

8. The requirements document MUST capture the purpose of generate_images:
   scan step_02/ for variant JSONs, call Agnes Image 2.1 Flash API for each
   variant using t2i_prompt1, download images to step_03/, update JSONs with
   image_url, save updated JSONs to step_03/, archive processed JSONs to
   step_02_archive/, produce step_03/index.json.

9. The requirements document MUST capture the purpose of generate_videos:
   scan step_03/ for JSONs containing image_url, call Agnes Video V2.0 API
   (image-to-video mode) using image_url and t2i_prompt1, poll until complete,
   download videos to step_04/, archive processed files to step_03_archive/,
   produce step_04/index.json.

### Special Requirements Capture

10. The requirements document MUST capture that every step uses human review
    gates (requires_human_approval_after = true) with on_reject_refine pointing
    to itself (rerun same step on reject).

11. The requirements document MUST capture configurable parameters from
    config.json: image model/size/ratio, video model/width/height/num_frames/
    frame_rate, num_variants, process_delay, coder_timeout, api_timeout,
    api_max_retries.

12. The requirements document MUST capture the API retry logic: 503 errors
    trigger automatic retry with exponential backoff up to api_max_retries.

13. The requirements document MUST capture that credentials (AGNES_API_KEY,
    AGNES_BASE_URL) are loaded from .env file in the target repo.

14. The requirements document MUST capture the per-image filename convention:
    output filenames match input image stems (e.g., image001.png produces
    image001.json).

15. The requirements document MUST capture the image description JSON schema
    with all nine nested attribute groups as specified in the spec.

16. The requirements document MUST capture the prompt variant JSON schema:
    mode, subject, variations array with t2i_prompt1, image_filename,
    image_url (empty after step_02, filled by step_03).

### Negative Criteria for analyze_spec

17. The requirements document MUST NOT declare any required_inputs for any
    step -- the spec explicitly states all paths are hardcoded in
    context_extensions.py, not user-provided.

18. The requirements document MUST NOT include any steps beyond the four
    processing steps and the terminal stepCompletion step.

19. The requirements document MUST NOT reference ComfyUI as a backend --
    the spec explicitly states image/video generation uses Agnes API directly.

20. The requirements document MUST NOT reference negative_prompt or
    workflowKey fields -- these are legacy and explicitly excluded.

21. The requirements document MUST NOT specify Chinese as the prompt
    language -- the spec requires English prompts.

## Criteria for generate_package step

The generate_package step produces the complete workflow package files:
workflow.toml, context_extensions.py, prompt templates, and actions.py.

### Files That Must Be Generated

22. The package MUST include a workflow.toml file at the package root with
    valid TOML syntax parseable by standard TOML libraries.

23. The package MUST include a context_extensions.py file implementing the
    WorkflowExtensions interface with workflow_name set to "agnes_media_gen_v1".

24. The package MUST include a prompts/ directory containing prompt template
    files for the two prompt-driven steps: extract_descriptions and
    generate_prompts.

25. The package MUST include an actions.py file containing custom action
    functions decorated with @action() for generate_images and
    generate_videos.

### Files That Must NOT Be Generated

26. The package MUST NOT include a bundle_governance.toml file unless
    explicitly required by the spec (the spec does not require it).

27. The package MUST NOT include an install.py file (the spec does not
    require global installation hooks).

28. The package MUST NOT import from or copy code from the existing skill
    scripts (~/.qwen/skills/scripts/agnes_image_gen.py or
    agnes_video_gen.py). The spec explicitly requires fresh action code.

### workflow.toml Structure

29. The workflow.toml MUST set [workflow] name to "agnes_media_gen_v1",
    job_prefix to "AMGEN", and label to "Agnes Media Generation v1".

30. The workflow.toml MUST declare init_step as "extract_descriptions"
    (the first processing step).

31. The workflow.toml MUST declare exactly five [[step]] entries in this
    order: extract_descriptions, generate_prompts, generate_images,
    generate_videos, stepCompletion.

32. The extract_descriptions step MUST have: prompt = "prompts/01_extract_descriptions.txt"
    (or similar numbered name), requires_human_approval_after = true,
    onsuccess = "generate_prompts", and role_policy = "architect_standard".

33. The generate_prompts step MUST have: prompt referencing a file in
    prompts/, requires_human_approval_after = true,
    onsuccess = "generate_images", and role_policy = "architect_standard".

34. The generate_images step MUST have: action = "generate_images",
    requires_human_approval_after = true, onsuccess = "generate_videos".
    It MUST NOT have a prompt field.

35. The generate_videos step MUST have: action = "generate_videos",
    requires_human_approval_after = true, onsuccess = "stepCompletion".
    It MUST NOT have a prompt field.

36. The stepCompletion step MUST have: action = "step_completion" and
    MUST be the final step.

37. Each processing step MUST have on_reject_refine configured to point
    to itself (rerun same step on reject), with appropriate
    exhausted_failure_code values.

38. The workflow.toml MUST NOT declare any required_inputs for any step.
    All context variables are resolved at runtime from context_extensions.py.

39. The workflow.toml MUST declare produces for each step matching the
    spec artifacts: extract_descriptions produces IMAGE_DESCRIPTIONS,
    generate_prompts produces PROMPT_VARIANTS, generate_images produces
    IMAGE_INDEX, generate_videos produces VIDEO_INDEX.

### context_extensions.py Structure

40. The context_extensions.py MUST define a class inheriting from
    WorkflowExtensions with workflow_name = "agnes_media_gen_v1".

41. The register_artifact_keys() method MUST return mappings for all
    output artifact keys: IMAGE_DESCRIPTIONS, PROMPT_VARIANTS,
    IMAGE_INDEX, VIDEO_INDEX, with paths matching the spec
    (step_01/index.json, step_02/index.json, step_03/index.json,
    step_04/index.json respectively).

42. The build_context_extensions() method MUST resolve ALL step directory
    paths to absolute paths: STEP_00_DIR, STEP_00_ARCHIVE, STEP_01_DIR,
    STEP_01_ARCHIVE, STEP_02_DIR, STEP_02_ARCHIVE, STEP_03_DIR,
    STEP_03_ARCHIVE, STEP_04_DIR, STEP_04_ARCHIVE.

43. The build_context_extensions() method MUST resolve MEDIA_CONFIG to
    an absolute path pointing to config.json at the repo root.

44. The build_context_extensions() method MUST resolve
    GOVERNANCE_RUNTIME_ROOT and PLATFORM_RUNTIME_ROOT using
    get_runner_home() per the standard pattern.

45. All paths in build_context_extensions() MUST be resolved to absolute
    paths using the workspace_root (from project_root or
    get_workspace_root() fallback), never relative paths.

46. The context_extensions.py MUST NOT declare any user-provided inputs
    as artifacts. The hardcoded paths (IMAGE_INPUT_DIR, IMAGE_INPUT_ARCHIVE,
    MEDIA_CONFIG) are runtime-resolved, not user inputs.

### Prompt Templates

47. The extract_descriptions prompt MUST instruct the LLM to scan the
    directory referenced by {STEP_00_DIR} for image files with extensions
    PNG, JPG, and WEBP.

48. The extract_descriptions prompt MUST instruct the LLM to use vision
    capabilities to read each image and produce a structured JSON with
    the nine nested attribute groups (subject_attributes,
    scene_attributes, composition_attributes, lighting_attributes,
    style_attributes, color_attributes, mood_attributes, motion_potential,
    extraction_confidence).

49. The extract_descriptions prompt MUST instruct the LLM to save each
    description JSON to {STEP_01_DIR} with filename matching the input
    image stem (e.g., image001.png -> image001.json).

50. The extract_descriptions prompt MUST instruct the LLM to copy
    processed images to {STEP_00_ARCHIVE} and remove them from
    {STEP_00_DIR}.

51. The extract_descriptions prompt MUST instruct the LLM to produce an
    index.json in {STEP_01_DIR} listing all input-to-output file mappings.

52. The generate_prompts prompt MUST instruct the LLM to scan
    {STEP_01_DIR} for description JSON files.

53. The generate_prompts prompt MUST instruct the LLM to generate N
    variant prompt sets per description (N configurable, default 4),
    where each variant has a t2i_prompt1 field.

54. The generate_prompts prompt MUST instruct the LLM to save variant
    JSONs to {STEP_02_DIR} following the variant schema (mode, subject,
    variations array with t2i_prompt1 and image_filename).

55. The generate_prompts prompt MUST instruct the LLM to archive
    processed description JSONs to {STEP_01_ARCHIVE}.

56. The generate_prompts prompt MUST instruct the LLM to produce an
    index.json in {STEP_02_DIR} listing all input-to-output mappings.

57. All prompt files MUST use bare {ARTIFACT_KEY} placeholders, never
    backtick-wrapped placeholders.

58. All prompt files MUST be ASCII-only with no Unicode characters.

### Action Code: generate_images

59. The generate_images action MUST be decorated with
    @action("generate_images") and accept keyword arguments context,
    state, step_cfg, project_root.

60. The generate_images action MUST read configuration from config.json
    (referenced by MEDIA_CONFIG context variable), including image model,
    size, ratio, process_delay, api_timeout, and api_max_retries.

61. The generate_images action MUST scan {STEP_02_DIR} for all JSON files
    containing variant data.

62. For each variant in each JSON, the generate_images action MUST call
    the Agnes Image 2.1 Flash API at the endpoint
    https://apihub.agnes-ai.com/v1/images/generations with payload
    containing model (from config), prompt (t2i_prompt1 from variant),
    and size (from config).

63. The generate_images action MUST authenticate API calls using
    AGNES_API_KEY loaded from .env file.

64. The generate_images action MUST download the generated image from the
    API response URL (data[0].url) and save it to {STEP_03_DIR} with a
    filename matching the variant's image_filename field.

65. The generate_images action MUST update each variant's JSON with the
    image_url field containing the API-returned URL.

66. The generate_images action MUST save the updated JSON (with image_url
    filled in) to {STEP_03_DIR} alongside the downloaded images.

67. The generate_images action MUST archive processed JSONs from
    {STEP_02_DIR} to {STEP_02_ARCHIVE} (copy then remove).

68. The generate_images action MUST produce {STEP_03_DIR}/index.json
    listing all input-to-output file mappings (JSON inputs, image outputs,
    updated JSON outputs).

69. The generate_images action MUST implement retry logic for HTTP 503
    responses with exponential backoff, retrying up to api_max_retries
    times (from config).

70. The generate_images action MUST enforce configurable HTTP timeouts
    (api_timeout from config) on all API requests.

71. The generate_images action MUST pause for process_delay seconds
    (from config) between consecutive API calls.

72. The generate_images action MUST return ActionResult with
    status="APPROVED" on success and status="REJECTED" with a
    reject_code on failure, including a descriptive remark.

73. The generate_images action MUST handle partial failures gracefully --
    if some images succeed and others fail, the successfully processed
    files must be saved and the error must be reported in the remark.

### Action Code: generate_videos

74. The generate_videos action MUST be decorated with
    @action("generate_videos") and accept keyword arguments context,
    state, step_cfg, project_root.

75. The generate_videos action MUST read configuration from config.json
    (referenced by MEDIA_CONFIG context variable), including video model,
    width, height, num_frames, frame_rate, process_delay, api_timeout,
    and api_max_retries.

76. The generate_videos action MUST scan {STEP_03_DIR} for all JSON files
    containing image_url and t2i_prompt1 fields.

77. For each variant in each JSON, the generate_videos action MUST call
    the Agnes Video V2.0 API at the endpoint
    https://apihub.agnes-ai.com/v1/videos with payload containing model
    (from config), prompt (t2i_prompt1), image (image_url from JSON),
    width, height, num_frames, and frame_rate (all from config).

78. The generate_videos action MUST authenticate API calls using
    AGNES_API_KEY loaded from .env file.

79. The generate_videos action MUST poll the video status endpoint
    (https://apihub.agnes-ai.com/agnesapi?video_id=<ID>) until status
    equals "completed".

80. The generate_videos action MUST download the completed video from
    the URL returned in the status response and save it to {STEP_04_DIR}.

81. The generate_videos action MUST archive processed files from
    {STEP_03_DIR} to {STEP_03_ARCHIVE} (copy then remove).

82. The generate_videos action MUST produce {STEP_04_DIR}/index.json
    listing all input-to-output file mappings.

83. The generate_videos action MUST implement retry logic for HTTP 503
    responses with exponential backoff, retrying up to api_max_retries
    times (from config).

84. The generate_videos action MUST enforce configurable HTTP timeouts
    (api_timeout from config) on all API requests.

85. The generate_videos action MUST pause for process_delay seconds
    (from config) between consecutive API calls.

86. The generate_videos action MUST return ActionResult with
    status="APPROVED" on success and status="REJECTED" with a
    reject_code on failure, including a descriptive remark.

87. The generate_videos action MUST handle partial failures gracefully --
    successfully processed files must be saved even if other variants fail.

### Negative Criteria for generate_package

88. The workflow.toml MUST NOT declare required_inputs for any step --
    the spec has no user-provided inputs.

89. The workflow.toml MUST NOT include any steps not specified in the
    spec (no review steps, no refine steps, no audit steps beyond what
    the spec defines).

90. The actions.py MUST NOT import from or copy the existing skill scripts
    (agnes_image_gen.py, agnes_video_gen.py). New code must be generated.

91. The actions.py MUST NOT use ComfyUI as a backend for any API calls.

92. The context_extensions.py MUST NOT hardcode absolute filesystem paths
    -- all paths must be derived from project_root or get_workspace_root()
    at runtime.

93. The context_extensions.py MUST NOT include the step directory paths
    as required_inputs or artifact keys that require user provision.

94. Prompt templates MUST NOT use backtick-wrapped {ARTIFACT_KEY}
    placeholders.

95. Prompt templates MUST NOT reference negative_prompt or workflowKey
    fields.

96. The package MUST NOT include a README.md, .env file, or config.json --
    these are not workflow package files (config.json lives in the target
    repo at runtime).

## Criteria for validate_bundle step

The validate_bundle step performs both structural and semantic validation
of the generated workflow package.

### Structural Checks

97. The workflow.toml MUST be valid TOML that parses without errors using
    a standard TOML parser.

98. The workflow.toml [workflow] section MUST contain all required fields:
    name, version, label, job_prefix.

99. The workflow.toml name field MUST exactly match the directory name
    "agnes_media_gen_v1".

100. The workflow.toml MUST declare init_step pointing to the first
     processing step (extract_descriptions).

101. Every prompt file referenced by a [[step]] prompt field MUST exist
     at the specified relative path within the prompts/ directory.

102. Every action referenced by a [[step]] action field MUST have a
     corresponding @action() decorated function in actions.py.

103. The onsuccess chain MUST form a valid linear path from
     extract_descriptions through generate_prompts, generate_images,
     generate_videos, to stepCompletion with no orphan steps.

104. The stepCompletion step MUST be the final step with
     action = "step_completion".

105. All artifact keys declared in step produces fields MUST have
     corresponding entries in register_artifact_keys() in
     context_extensions.py.

106. All artifact keys referenced in prompt templates as
     {ARTIFACT_KEY} placeholders MUST be registered in either
     register_artifact_keys() or build_context_extensions().

107. The context_extensions.py MUST import WorkflowExtensions from
     agent_runner_v2.workflow_packages.extensions_base.

108. The context_extensions.py class MUST set workflow_name to exactly
     "agnes_media_gen_v1".

### Semantic Checks

109. The generate_images action function MUST contain actual HTTP request
     logic calling the Agnes Image API endpoint, not a stub or placeholder.

110. The generate_images action function MUST contain code to download
     image data from a URL (e.g., requests.get on the response URL and
     writing binary content to a file).

111. The generate_images action function MUST contain retry logic --
     a loop or recursive pattern that catches HTTP 503 responses and
     retries with increasing delay.

112. The generate_images action function MUST contain code that reads
     and parses a JSON config file for model, size, timeout, and retry
     parameters.

113. The generate_images action function MUST contain code that writes
     an index.json file listing input-to-output file mappings.

114. The generate_videos action function MUST contain actual HTTP request
     logic calling the Agnes Video API endpoint, not a stub or placeholder.

115. The generate_videos action function MUST contain polling logic --
     a loop that periodically checks a status endpoint until the video
     generation completes.

116. The generate_videos action function MUST contain retry logic for
     HTTP 503 responses with exponential backoff.

117. The generate_videos action function MUST contain code that reads
     and parses a JSON config file for model, dimensions, timeout, and
     retry parameters.

118. The generate_videos action function MUST contain code that writes
     an index.json file listing input-to-output file mappings.

119. The extract_descriptions prompt MUST contain instructions for the
     LLM to produce JSON output matching the nine-group nested schema
     (subject_attributes through extraction_confidence).

120. The generate_prompts prompt MUST contain instructions for the LLM
     to produce variant JSONs with the t2i_prompt1 field per variant.

### File Completeness

121. The package directory MUST contain exactly these required files:
     workflow.toml, context_extensions.py, actions.py.

122. The package directory MUST contain a prompts/ subdirectory with
     at least two .txt prompt files (one for extract_descriptions, one
     for generate_prompts).

123. The package directory MUST NOT contain extraneous files not required
     by the workflow (e.g., no __pycache__/, no .pyc files, no temporary
     files, no .gitignore).

### Negative Criteria for validate_bundle

124. The validate_bundle action MUST NOT report success if any action
     function body is empty, contains only pass/return statements, or
     contains only comments without functional code.

125. The validate_bundle action MUST NOT report success if artifact keys
     in workflow.toml do not match those in context_extensions.py
     (case-sensitive match required).

126. The validate_bundle action MUST NOT report success if the onsuccess
     chain is broken (any step points to a non-existent step name).

## Criteria for review_package step

The review_package step performs a semantic review of the generated
workflow against the original specification.

### Spec Fulfillment

127. The review MUST verify that the workflow implements the complete
     end-to-end pipeline: images in step_00 -> descriptions in step_01 ->
     prompt variants in step_02 -> generated images in step_03 ->
     generated videos in step_04.

128. The review MUST verify that the correct API endpoints are used:
     Agnes Image 2.1 Flash at /v1/images/generations and Agnes Video V2.0
     at /v1/videos with polling at /agnesapi.

129. The review MUST verify that the correct model identifiers are used:
     "agnes-image-2.1-flash" for image generation and "agnes-video-v2.0"
     for video generation (both configurable from config.json).

130. The review MUST verify that human review gates are configured on all
     four processing steps with self-referencing reject routing.

### Step-by-Step Verification

131. The review MUST verify extract_descriptions: the prompt instructs
     the LLM to use vision to analyze images, produce structured JSONs
     with the nine-attribute nested schema, save to step_01/, and archive
     processed images.

132. The review MUST verify generate_prompts: the prompt instructs the LLM
     to read description JSONs, generate N variant prompts with t2i_prompt1
     field, save variant JSONs to step_02/, and archive processed inputs.

133. The review MUST verify generate_images: the action calls the Image API
     for each variant, downloads images, updates JSONs with image_url,
     saves updated JSONs alongside images in step_03/, and produces
     index.json.

134. The review MUST verify generate_videos: the action calls the Video API
     with image_url and t2i_prompt1 for each variant, polls until complete,
     downloads videos to step_04/, and produces index.json.

135. The review MUST verify stepCompletion: is the terminal action
     (step_completion) with no further routing.

### Data Flow Verification

136. The review MUST verify that data flows correctly between steps:
     step_01/ JSONs (with nested description schema) feed into step_02/
     which reads them and produces variant JSONs.

137. The review MUST verify that step_03/ reads variant JSONs from
     step_02/ and that the updated JSONs (with image_url populated) are
     saved in step_03/ -- the same directory where images are stored.

138. The review MUST verify that step_04/ reads from step_03/ JSONs
     (which contain both image_url and t2i_prompt1) and uses both fields
     in the video API call.

139. The review MUST verify that the archive pattern is consistently
     applied: each step copies processed inputs to the corresponding
     _archive folder and removes them from the input folder.

140. The review MUST verify that index.json files are produced by every
     processing step and contain input-to-output file mapping metadata.

### No Hallucinations Check

141. The review MUST verify that no extra configuration files are
     referenced beyond config.json (no additional .json, .yaml, or
     .toml config files not specified in the spec).

142. The review MUST verify that no wrong model identifiers are used
     (e.g., not "agnes-image-2.0" or "agnes-video-v1.0" -- must be
     exactly "agnes-image-2.1-flash" and "agnes-video-v2.0").

143. The review MUST verify that no unnecessary required_inputs are
     declared in workflow.toml -- the spec has zero user-provided inputs.

144. The review MUST verify that no additional steps beyond the four
     processing steps and stepCompletion are present (no extra review,
     audit, or transformation steps).

145. The review MUST verify that credentials are sourced from .env
     (AGNES_API_KEY and AGNES_BASE_URL), not hardcoded in any file.

146. The review MUST verify that the workflow does not reference or
     depend on the legacy skill scripts (agnes_image_gen.py,
     agnes_video_gen.py).

### Negative Criteria for review_package

147. The review MUST NOT approve the package if any action function is a
     stub that delegates entirely to an external script rather than
     implementing the logic directly.

148. The review MUST NOT approve the package if prompt templates contain
     backtick-wrapped placeholders that would prevent path resolution.

149. The review MUST NOT approve the package if the data flow between
     steps is broken (e.g., step_04 cannot find its required inputs
     because step_03 archives them before saving the needed JSONs).

150. The review MUST NOT approve the package if any spec requirement
     is partially implemented (e.g., retry logic mentioned but not
     actually coded).
