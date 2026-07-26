---
doc_type: "workflow_review"
lifecycle_status: "draft"
effective_version: "WFBUILD-20260725-61c44baa"
spec_reference: "agnes_media_gen_v1"
created_at: "2026-07-26"
review_target: "TEST_CRITERIA-20260726-001_media_gen_v1.md"
---

# Review: Test Criteria for Agnes Media Generation v1

## Summary

The test criteria document for agnes_media_gen_v1 is comprehensive, well-structured, and accurately reflects the workflow specification. All 150 criteria are specific, verifiable, and correctly aligned with the spec's requirements. The document correctly captures the mixed workflow type, the five-stage pipeline (extract descriptions, generate prompts, generate images, generate videos, stepCompletion), human review gates, configurable parameters, API specifications, and data flow between steps. Negative criteria properly constrain what must NOT be generated. No contradictory criteria were found. All content is ASCII-only.

## Findings

### 1. Spec Objective Summary

**PASS** - Lines 12-29 accurately capture the workflow's end-to-end transformation:
- Correctly describes the five-stage pipeline: images in step_00 -> LLM vision descriptions in step_01 -> prompt variants in step_02 -> generated images in step_03 -> generated videos in step_04
- Correctly identifies the workflow type as "mixed" (prompt-driven + action-driven)
- Correctly states that all configuration is read from config.json at runtime
- Correctly notes that no user-provided inputs exist (all paths hardcoded in context_extensions.py)
- Matches the spec's stated purpose (spec lines 13-24) exactly

### 2. Criteria for analyze_spec step

**PASS** - All spec requirements are covered:

| Requirement | Coverage | Evidence |
|-------------|----------|----------|
| Workflow type classification | Lines 37-46 | Correctly identifies "mixed" type with prompt and action steps |
| Step count (4 processing + 1 terminal) | Lines 43-46 | Explicitly listed: extract_descriptions, generate_prompts, generate_images, generate_videos, stepCompletion |
| No user-provided inputs | Lines 50-52, 120-122 | States required_inputs must be empty; all paths resolved from target repo |
| Output artifacts | Lines 54-56 | IMAGE_DESCRIPTIONS, PROMPT_VARIANTS, IMAGE_INDEX, VIDEO_INDEX correctly mapped to step_01-04/index.json |
| Context variables | Lines 58-61 | All 12 variables listed: STEP_00_DIR through STEP_04_ARCHIVE, MEDIA_CONFIG, GOVERNANCE_RUNTIME_ROOT, PLATFORM_RUNTIME_ROOT |
| Human review gates | Lines 92-94 | requires_human_approval_after = true with self-referencing on_reject_refine |
| Configurable parameters | Lines 96-99 | Model, size, ratio, dimensions, num_variants, delays, timeouts, retries from config.json |
| API retry logic | Lines 101-102 | 503 errors with exponential backoff |
| Credentials from .env | Lines 104-105 | AGNES_API_KEY, AGNES_BASE_URL |
| Filename convention | Lines 107-109 | Output filenames match input image stems |
| JSON schemas | Lines 111-116 | Nine-attribute nested schema for descriptions; variant schema with t2i_prompt1 |
| Negative criteria | Lines 118-134 | No required_inputs, no extra steps, no ComfyUI, no legacy fields, English prompts only |

### 3. Criteria for generate_package step

**PASS** - All required files and semantic criteria are specified:

**Files That Must Be Generated (Lines 142-155):**
- workflow.toml, context_extensions.py, prompts/, actions.py - all listed
- Negative criteria (lines 158-167): No bundle_governance.toml, no install.py, no imports from skill scripts

**workflow.toml Structure (Lines 169-211):**
- Lines 172-173: name, job_prefix, label correctly specified
- Lines 175-176: init_step = "extract_descriptions"
- Lines 178-179: Five steps in correct order
- Lines 181-198: Each step has correct configuration (prompt/action fields, onsuccess chain, human approval gates)
- Line 200-202: on_reject_refine points to self
- Lines 204-205: No required_inputs
- Lines 207-210: produces declarations match spec artifacts

**context_extensions.py Structure (Lines 213-241):**
- Lines 214-215: Inherits from WorkflowExtensions, workflow_name = "agnes_media_gen_v1"
- Lines 217-221: register_artifact_keys returns all four artifact keys with correct paths
- Lines 223-226: build_context_extensions resolves all step directories to absolute paths
- Lines 228-229: MEDIA_CONFIG resolves to config.json at repo root
- Lines 231-233: GOVERNANCE_RUNTIME_ROOT and PLATFORM_RUNTIME_ROOT use get_runner_home()
- Lines 235-237: All paths resolved to absolute paths from workspace_root
- Lines 239-241: No user-provided inputs declared

**Prompt Templates (Lines 243-287):**
- Lines 245-265: extract_descriptions prompt instructions are complete (scan, vision, JSON schema, archive, index)
- Lines 267-282: generate_prompts prompt instructions are complete (scan, N variants, t2i_prompt1, archive, index)
- Lines 284-287: Bare placeholders, ASCII-only

**Action Code: generate_images (Lines 289-345):**
- Lines 291-293: Correct decorator and parameters
- Lines 295-297: Config reading with all parameters
- Lines 299-300: Scan step_02 for variant JSONs
- Lines 302-306: Correct API endpoint and payload structure
- Lines 308-309: AGNES_API_KEY authentication
- Lines 311-314: Download images, update JSON with image_url
- Lines 316-319: Save updated JSONs to step_03
- Lines 321-326: Archive pattern and index.json
- Lines 328-334: Retry logic, timeouts, process_delay
- Lines 336-340: ActionResult return
- Lines 342-344: Partial failure handling

**Action Code: generate_videos (Lines 346-397):**
- Lines 348-350: Correct decorator and parameters
- Lines 352-356: Config reading with all video parameters
- Lines 358-359: Scan step_03 for JSONs with image_url and t2i_prompt1
- Lines 361-364: Correct API endpoint and payload structure
- Lines 366-367: AGNES_API_KEY authentication
- Lines 369-371: Polling logic for video status
- Lines 373-374: Download completed videos
- Lines 376-380: Archive pattern and index.json
- Lines 382-388: Retry logic, timeouts, process_delay
- Lines 390-394: ActionResult return
- Lines 396-397: Partial failure handling

**Negative Criteria for generate_package (Lines 399-428):**
- Lines 401-402: No required_inputs in workflow.toml
- Lines 404-406: No extra steps beyond spec
- Lines 408-411: No imports from existing scripts, no ComfyUI
- Lines 413-418: No hardcoded paths, no user inputs as artifacts
- Lines 420-424: No backtick placeholders, no legacy fields
- Lines 426-428: No README.md, .env, config.json in package

### 4. Criteria for validate_bundle step

**PASS** - Both structural and semantic checks included:

**Structural Checks (Lines 435-475):**
- Lines 437-443: TOML parsing, required fields in [workflow] section
- Lines 445-448: name matches directory name, init_step correct
- Lines 450-454: Prompt files exist, action functions decorated
- Lines 456-460: onsuccess chain valid, stepCompletion is final
- Lines 462-468: Artifact keys registered in context_extensions.py
- Lines 470-474: Correct imports and workflow_name

**Semantic Checks (Lines 477-519):**
- Lines 479-494: generate_images contains HTTP logic, download, retry, config reading, index.json
- Lines 496-511: generate_videos contains HTTP logic, polling, retry, config reading, index.json
- Lines 513-518: Prompts contain instructions for correct JSON schemas

**File Completeness (Lines 521-531):**
- Lines 522-527: Required files and prompts directory
- Lines 529-531: No extraneous files

**Negative Criteria for validate_bundle (Lines 533-544):**
- Lines 535-537: No empty/stub action functions
- Lines 539-541: Artifact key case-sensitive matching
- Lines 543-544: No broken onsuccess chains

### 5. Criteria for review_package step

**PASS** - Spec fulfillment and data flow verification included:

**Spec Fulfillment (Lines 551-567):**
- Lines 553-556: End-to-end pipeline verification
- Lines 558-561: Correct API endpoints verified
- Lines 563-564: Correct model identifiers verified
- Lines 566-567: Human review gates verified

**Step-by-Step Verification (Lines 569-590):**
- Lines 571-574: extract_descriptions verification
- Lines 576-578: generate_prompts verification
- Lines 580-583: generate_images verification
- Lines 585-587: generate_videos verification
- Lines 589-590: stepCompletion verification

**Data Flow Verification (Lines 592-611):**
- Lines 594-596: step_01 JSONs feed step_02
- Lines 598-600: step_03 reads from step_02, saves updated JSONs
- Lines 602-604: step_04 reads from step_03 JSONs (image_url + t2i_prompt1)
- Lines 606-608: Archive pattern consistency
- Lines 610-611: index.json file production

**No Hallucinations Check (Lines 613-635):**
- Lines 615-617: No extra config files
- Lines 619-621: Correct model identifiers
- Lines 623-624: No unnecessary required_inputs
- Lines 626-628: No additional steps
- Lines 630-631: Credentials from .env, not hardcoded
- Lines 633-635: No dependency on legacy scripts

**Negative Criteria for review_package (Lines 637-651):**
- Lines 639-641: No stub actions
- Lines 643-644: No backtick placeholders
- Lines 646-648: No broken data flow
- Lines 650-651: No partial implementations

### 6. Quality checks

**PASS** - All quality criteria met:

| Check | Result | Evidence |
|-------|--------|----------|
| Every criterion is specific and verifiable | PASS | All 150 criteria use concrete terms (MUST, MUST NOT) with specific file names, field names, and API endpoints |
| No contradictory criteria | PASS | No conflicts found between criteria |
| All content is ASCII-only | PASS | No em-dashes, curly quotes, or Unicode characters detected |
| YAML frontmatter present | PASS | Lines 1-8 contain valid YAML frontmatter |
| YAML frontmatter correct | PASS | All required fields present with correct values |

## Issues

No issues found. The test criteria document is complete, accurate, and ready for use.

## Verdict

APPROVED