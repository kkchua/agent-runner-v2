---
doc_type: "workflow_review"
lifecycle_status: "draft"
effective_version: "WFBUILD-20260725-61c44baa"
spec_reference: "agnes_media_gen_v1"
review_date: "2026-07-26"
verdict: "APPROVED"
---

# Review: Agnes Media Generation v1

## Summary

The generated workflow package for agnes_media_gen_v1 successfully implements the complete end-to-end media generation pipeline as specified. All five steps are correctly defined in the proper sequence: extract_descriptions (prompt-driven with LLM vision), generate_prompts (prompt-driven), generate_images (action-driven with Agnes Image API), generate_videos (action-driven with Agnes Video API), and stepCompletion (terminal). The workflow.toml, context_extensions.py, actions.py, and prompt templates are structurally correct, internally consistent, and fully compliant with the workflow creation guide. All test criteria pass, with correct API endpoints, model identifiers, artifact keys, retry logic, configuration reading, index file generation, and human review gates. No critical issues found.

## workflow.toml Findings

| Check | Result | Evidence |
|---|---|---|
| stepCompletion terminal step present | PASS | Line 113-115: `name = "stepCompletion"` with `action = "step_completion"` is the final step |
| init_step matches first step name | PASS | Line 10: `init_step = "extract_descriptions"` matches first step |
| All onsuccess targets valid | PASS | Lines 28, 52, 76, 97: targets "generate_prompts", "generate_images", "generate_videos", "stepCompletion" all exist |
| onsuccess at step level | PASS | Lines 28, 52, 76, 97: onsuccess is at [[step]] level, not inside [step.artifacts] |
| Prompt steps have [step.coder] with role_policy | PASS | Lines 34-35, 58-59: extract_descriptions and generate_prompts have `role_policy = "architect_standard"` |
| Prompt steps have [step.artifacts] with produces | PASS | Lines 30-32, 54-56: produces and result_meta_key defined correctly |
| Review steps have requires_human_approval_after | PASS | Lines 27, 51, 75, 96: all processing steps have `requires_human_approval_after = true` |
| Review steps have on_reject_refine to self | PASS | Lines 37-42, 61-66, 82-87, 103-108: all point to same step for rerun |
| Step names lowercase_with_underscores | PASS | All step names use lowercase_with_underscores format |
| No required_inputs declared | PASS | No `required_inputs` field in any step - all paths runtime-resolved |

## context_extensions.py Findings

| Check | Result | Evidence |
|---|---|---|
| WorkflowExtensions class present | PASS | Line 26: `class AgnesMediaGenExtensions(WorkflowExtensions)` |
| workflow_name matches directory | PASS | Line 37: `workflow_name = "agnes_media_gen_v1"` matches directory name |
| register_artifact_keys returns correct paths | PASS | Lines 53-58: IMAGE_DESCRIPTIONS, PROMPT_VARIANTS, IMAGE_INDEX, VIDEO_INDEX map to step_01/index.json through step_04/index.json |
| build_context_extensions returns absolute paths | PASS | Lines 91-104: all step directories resolved via `str(workspace_root / dirname)` |
| MEDIA_CONFIG resolved to absolute path | PASS | Line 107: `result["MEDIA_CONFIG"] = str(workspace_root / "config.json")` |
| GOVERNANCE_RUNTIME_ROOT resolved | PASS | Lines 109-112: calls `get_governance_runtime_root()` |
| PLATFORM_RUNTIME_ROOT resolved | PASS | Lines 114-117: calls `get_platform_runtime_root()` |
| install_to_global method present | PASS | Lines 125-131: returns `{"status": "NO_OP"}` |
| sync_to_backend method present | PASS | Lines 133-138: returns `{"status": "NO_OP"}` |
| All artifact keys from workflow.toml present | PASS | IMAGE_DESCRIPTIONS, PROMPT_VARIANTS, IMAGE_INDEX, VIDEO_INDEX all registered |
| Docstrings present | PASS | Module docstring (lines 1-12), class docstring (lines 27-35), method docstrings (lines 39-52, 60-82, 125-131, 133-138) |

## Prompt File Findings

| Check | Result | Evidence |
|---|---|---|
| 01_extract_descriptions.txt exists | PASS | File found at prompts/01_extract_descriptions.txt |
| 02_generate_prompts.txt exists | PASS | File found at prompts/02_generate_prompts.txt |
| Placeholders use bare format | PASS | All placeholders like `{STEP_00_DIR}`, `{STEP_01_DIR}`, etc. are bare, not backtick-wrapped |
| Content ASCII-only | PASS | Both files verified to contain 0 non-ASCII characters |
| extract_descriptions has required sections | PASS | Contains Objective (line 1), Reference Inputs (line 13), Output Instructions (line 22), Artifacts (line 130) |
| generate_prompts has required sections | PASS | Contains Objective (line 1), Reference Inputs (line 16), Output Instructions (line 25), Artifacts (line 91) |
| Artifact key references match contract | PASS | extract_descriptions references IMAGE_DESCRIPTIONS (line 132), generate_prompts references PROMPT_VARIANTS (line 92) |
| extract_descriptions instructs 9 attribute groups | PASS | Lines 35-102: all 9 groups listed (subject_attributes through extraction_confidence) |
| generate_prompts instructs t2i_prompt1 generation | PASS | Lines 43-65: t2i_prompt1 field specified in variant schema |

## Supplementary File Findings

| Check | Result | Evidence |
|---|---|---|
| README.md exists | PASS | File found at README.md |
| README.md has Overview section | PASS | Lines 3-22: Overview section present |
| README.md has Prerequisites section | PASS | Lines 24-42: Prerequisites section present |
| README.md has Installation section | PASS | Lines 44-64: Installation section present |
| README.md has Configuration section | PASS | Lines 66-94: Configuration section present |
| README.md has Usage section | PASS | Lines 96-124: Usage section present |
| README.md has Step Reference section | PASS | Lines 126-137: Step Reference section present |
| README.md has Artifact Keys section | PASS | Lines 139-147: Artifact Keys section present |
| README.md step reference matches workflow.toml | PASS | Table shows 5 steps matching workflow.toml sequence |
| .env.sample exists | PASS | File found at .env.sample |
| .env.sample has descriptive comments | PASS | Lines 1-10: Comments describe AGNES_API_KEY and AGNES_BASE_URL |
| .env.sample has placeholder values | PASS | Line 6: `AGNES_API_KEY=your_api_key_here`, Line 10: `AGNES_BASE_URL=https://apihub.agnes-ai.com` |
| config.json.sample exists | PASS | File found at config.json.sample |
| config.json.sample is valid JSON | PASS | Parsed successfully with correct structure |
| config.json.sample has sensible defaults | PASS | Lines 1-18: Correct model identifiers (agnes-image-2.1-flash, agnes-video-v2.0) and reasonable parameter values |

## Cross-File Consistency

| Check | Result | Evidence |
|---|---|---|
| Artifact keys match workflow.toml to context_extensions.py | PASS | IMAGE_DESCRIPTIONS, PROMPT_VARIANTS, IMAGE_INDEX, VIDEO_INDEX in both files |
| Step names match prompt file naming | PASS | extract_descriptions -> 01_extract_descriptions.txt, generate_prompts -> 02_generate_prompts.txt |
| onsuccess routing targets valid steps | PASS | All targets (generate_prompts, generate_images, generate_videos, stepCompletion) exist as steps |
| README.md artifact keys match context_extensions.py | PASS | Table at lines 141-146 lists same keys as register_artifact_keys() |
| README.md configuration matches sample files | PASS | Configuration section describes .env and config.json parameters matching sample files |

## Spec Fulfillment

### Test Criteria Verification (items 127-150)

| Criterion | Result | Evidence |
|---|---|---|
| 127: Complete end-to-end pipeline | PASS | workflow.toml defines 5 steps: extract_descriptions -> generate_prompts -> generate_images -> generate_videos -> stepCompletion |
| 128: Correct API endpoints | PASS | actions.py line 266: `/v1/images/generations`, lines 528-529: `/v1/videos` with polling at `/agnesapi` |
| 129: Correct model identifiers | PASS | config.json.sample line 3: `agnes-image-2.1-flash`, line 8: `agnes-video-v2.0`; actions.py reads from config |
| 130: Human review gates on all steps | PASS | workflow.toml lines 27, 51, 75, 96: all processing steps have `requires_human_approval_after = true` |
| 131: extract_descriptions implements spec | PASS | Prompt lines 3-11 instruct vision analysis, 9 attribute schema (lines 35-102), archive pattern (lines 116-118) |
| 132: generate_prompts implements spec | PASS | Prompt lines 3-14 instruct N variants from config, t2i_prompt1 field (lines 43-65), archive pattern (lines 78-80) |
| 133: generate_images implements spec | PASS | actions.py lines 180-434: Image API calls, downloads, JSON updates, archive, index.json |
| 134: generate_videos implements spec | PASS | actions.py lines 436-756: Video API submit, polling, download, archive, index.json |
| 135: stepCompletion is terminal | PASS | workflow.toml lines 113-115: action = "step_completion" with no routing |
| 136: Data flow step_01 -> step_02 | PASS | extract_descriptions saves to step_01, generate_prompts reads from step_01 |
| 137: Data flow step_02 -> step_03 | PASS | generate_images reads from step_02, saves images+JSONs to step_03 |
| 138: Data flow step_03 -> step_04 | PASS | generate_videos reads from step_03 (image_url + t2i_prompt1), saves videos to step_04 |
| 139: Archive pattern consistent | PASS | All processing steps implement copy-to-archive then remove pattern |
| 140: index.json produced by all steps | PASS | actions.py lines 397-399 (generate_images), lines 717-719 (generate_videos); prompts instruct index.json for LLM steps |
| 141: No extra config files | PASS | Only config.json referenced, no additional JSON/YAML/TOML configs |
| 142: No wrong model identifiers | PASS | Models exactly "agnes-image-2.1-flash" and "agnes-video-v2.0" |
| 143: No unnecessary required_inputs | PASS | workflow.toml has zero required_inputs declarations |
| 144: No extra steps beyond spec | PASS | Exactly 5 steps (4 processing + 1 terminal) |
| 145: Credentials from .env | PASS | actions.py lines 30-43: _load_env() loads AGNES_API_KEY and AGNES_BASE_URL from .env |
| 146: No dependency on legacy scripts | PASS | actions.py implements fresh code, no imports from ~/.qwen/skills/scripts/ |
| 147: Actions not stubs | PASS | actions.py contains full implementation: HTTP requests, retry logic, config parsing, file I/O |
| 148: No backtick-wrapped placeholders | PASS | All prompt placeholders are bare format |
| 149: Data flow not broken | PASS | Each step reads from previous step directory, archives after processing |
| 150: All spec requirements implemented | PASS | All functionality implemented with actual code, not partial or placeholder |

## Issues

None. All test criteria pass.

## Verdict

APPROVED