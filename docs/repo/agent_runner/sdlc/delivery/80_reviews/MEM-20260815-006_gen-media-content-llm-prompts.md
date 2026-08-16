---
template_id: "SYS-03-MM"
version: "1.0.0"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "lessons learned and memory capture"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "approved"
effective_version: "20260815-001-005"
managed_by: "workflow-generated"
---

# Memory Document: gen_media_content_v1 Phase 7 -- LLM Prompts

## Memory Overview

This memory document captures lessons learned, technical insights, and process insights from the gen_media_content_v1 Phase 7 initiative. The initiative implemented two LLM prompt templates (extract_desc, generate_prompts) and a test suite for the gen_media_content_v1 workflow package.

The memory is derived from the approved validation report (VAL-20260815-006), the execution record (EXEC-20260815-001-005), and the adversarial challenge resolution process (CHALLENGE-VAL-20260815-006). Its purpose is to provide reusable knowledge for future prompt template adaptation initiatives within the agent-runner-v2 ecosystem.

## Validation Traceability

This memory document traces to the same approved validation chain as the review document:

| Reference | Document ID | Status |
|---|---|---|
| Task | TASK-20260815-001-07 | 9 acceptance criteria |
| Implementation Plan | IMPL-20260815-001-006 | 4 steps |
| Execution Record | EXEC-20260815-001-005 | Approved |
| Validation Report | VAL-20260815-006 | Approved |
| Challenge Document | CHALLENGE-VAL-20260815-006 | Resolved |
| Review Document | REV-20260815-006 | Draft (this cycle) |

## What Went Well

### WW-01: Clean File Creation with Zero Regressions

All 3 files were created as new untracked files. No existing tracked files were modified (the SPECIALIZED_STEPS.md modification was pre-existing from a prior task). The baseline test suite remained unaffected at 117 passed, 1 pre-existing failure. This demonstrates disciplined scope control during implementation.

### WW-02: Comprehensive Test Coverage Exceeding Requirements

The test suite delivered 13 test methods across 8 classes, exceeding the 9-test minimum specified in AC-08. Tests cover all 9 acceptance criteria plus 2 supplementary content length checks. The use of pytest fixtures for content reuse and Path-based resolution for portability shows good test engineering practices.

### WW-03: Effective Source Adaptation

The adaptation from agnes_media_gen_v1 to gen_media_content_v1 correctly addressed all required transformations:

- Hardcoded paths (D:/path/to/repo/step_01_imagedesc/index.json) replaced with placeholder references ({STEP_01_DIR}/index.json)
- Shell commands (shuf) replaced with descriptive English instructions
- Archiving logic removed with explanatory notes about automatic handling
- U+2192 right arrows systematically replaced with ASCII "->" (31 replacements)
- All placeholder mappings verified in context_extensions.py

### WW-04: Transparent Issue Documentation

The EXEC document proactively documented the 17 remaining U+2193 characters as Issue 2 before the validation phase. This transparency allowed the validation to focus on confirming and classifying the deviation rather than discovering it. Proactive issue documentation is a model practice for future initiatives.

### WW-05: Adversarial Challenge Strengthened the Output

The challenge process (CHALLENGE-VAL-20260815-006) identified 5 findings that materially improved the validation report:

- 2 issues reclassified from LOW to MEDIUM severity
- New validation criterion VC-11 added (ASCII-only compliance)
- New validation result VR-10 added with full character scan evidence
- Explicit regex scope analysis with documented coverage and gaps
- Timing evidence presented with multi-run comparison table

## What Could Improve

### WI-01: ASCII-Only Convention Enforcement Was Not Automated

The 17 U+2193 characters in generate_prompts/standard.txt survived the implementation phase because no automated test enforced ASCII-only content. The convention was known (documented in AGENTS.md) but not machine-checkable during the development workflow.

Root cause: The acceptance criteria (AC-01 through AC-09) did not include an ASCII-only test requirement. The convention existed at the project level but was not decomposed into a task-level acceptance criterion.

### WI-02: Placeholder Coverage Was Incomplete in Tests

The {IMAGE_DESCRIPTIONS} placeholder is present in extract_desc/standard.txt and mapped in context_extensions.py, but has no automated test coverage. This gap was not discovered until the adversarial challenge process raised it as Finding 4.

Root cause: Tests were written to match the stated acceptance criteria, not to exhaustively cover all mapped placeholders. The task specification did not list {IMAGE_DESCRIPTIONS} as an explicit requirement.

### WI-03: Absolute Path Regex Has Theoretical Coverage Gaps

The regex pattern for detecting hardcoded absolute paths does not cover Windows UNC paths (\\server\share\format). While this gap has zero practical impact on the current prompt files (no absolute paths exist), it represents an incomplete implementation of the detection capability.

Root cause: The regex was designed for common path patterns (Windows drive letters, Unix absolute paths) without considering all possible absolute path forms.

### WI-04: Timing Claims in Execution Reports Create Unnecessary Verification Burden

The EXEC report included specific timing measurements (0.79s), which the validation then had to independently verify. Timing is environment-dependent and non-reproducible, making it an unsuitable validation criterion. The challenge process correctly identified this as an evidence quality concern.

Root cause: The execution record template or convention does not distinguish between deterministic outcomes (pass/fail) and non-deterministic measurements (timing).

## Technical Insights

### TI-01: Placeholder-Based Path Resolution Is the Standard Pattern

The gen_media_content_v1 workflow uses a consistent placeholder-based path resolution pattern:

- Prompt files contain {PLACEHOLDER_NAME} tokens
- context_extensions.py maps placeholders to resolved filesystem paths
- workflow.toml references prompt slots via {{ slot.slot_name }} syntax

This pattern eliminates hardcoded paths and enables portable workflow execution across different environments. All prompt template adaptation tasks should follow this pattern.

### TI-02: Source Prompt Adaptation Checklist

When adapting prompts from one workflow package to another, the following transformations are required:

1. Replace all hardcoded absolute paths with {PLACEHOLDER} tokens
2. Replace shell-specific commands (shuf, grep, etc.) with descriptive English
3. Remove or adapt archiving/cleanup logic that is handled by the target workflow
4. Normalize Unicode characters to ASCII equivalents
5. Verify all {PLACEHOLDER} tokens are mapped in the target context_extensions.py
6. Verify workflow.toml references the new prompt slot paths

### TI-03: Regex Scope for Absolute Path Detection

The current regex pattern `(?:[A-Z]:[/\\])|(?:/(?:home|usr|etc|tmp|var|opt)/)|(?:^/[^{])` covers:

- Windows drive-letter paths: C:\, D:/, etc.
- Common Unix absolute paths: /home/, /usr/, /etc/, /tmp/, /var/, /opt/
- Root-relative paths at line start: any / at line start followed by non-{ character

Known gaps:

- Windows UNC paths: \\server\share\format (no pattern for \\ prefix)
- Mid-line absolute Unix paths not starting with common directories

For practical purposes, the current regex is sufficient for prompt files that should contain zero absolute paths. The gaps are theoretical edge cases.

### TI-04: Test Timing Variance Is Environmental, Not Deterministic

Test execution timing varied from 0.12s to 0.79s across 4 independent runs of the same 13 tests. This 6.5x variance is caused by system load, filesystem caching, and OS process scheduling. Pass/fail outcomes are deterministic; timing is not. Validation should rely on deterministic outcomes only.

**Recommendation:** Future execution records should either exclude timing measurements entirely or present them with explicit environmental caveats (platform, Python version, system load state, filesystem cache state). If timing is included, the record should note that timing values are illustrative and not reproducible across environments. This prevents downstream validators from treating timing as a verification criterion and eliminates unnecessary verification burden.

## Process Insights

### PI-01: Proactive Issue Documentation Accelerates Validation

The EXEC document's explicit documentation of the U+2193 deviation (Issue 2) allowed the validation to proceed efficiently. The validator could focus on confirming the deviation and classifying its severity rather than discovering it independently. This practice should be standard for all execution records.

### PI-02: Adversarial Challenge Adds Measurable Value

The challenge process transformed 2 LOW-severity issues into MEDIUM-severity issues, added a new validation criterion and result, and provided detailed regex scope analysis. Without the challenge, the validation would have been less rigorous and the issues less visible.

Recommendation: Continue the adversarial challenge practice for all validation reports, especially those involving convention compliance and test coverage assessment.

### PI-03: Acceptance Criteria Should Include Convention Compliance Tests

The task acceptance criteria covered functional requirements (file existence, placeholder presence, test execution) but did not include convention compliance (ASCII-only content). This gap allowed a convention violation to persist through implementation.

Recommendation: Future prompt template tasks should include ASCII-only compliance as an explicit acceptance criterion, or the project should establish a standing convention that all prompt files must pass an ASCII-only validation.

### PI-04: Test Coverage Should Match Placeholder Mappings

When a workflow maps N placeholders in context_extensions.py, the test suite should verify at least N placeholders are present in the prompt files. This ensures that placeholder mappings do not become stale or disconnected from actual prompt content.

Recommendation: For prompt template tasks, include a "placeholder completeness" acceptance criterion that requires tests for all mapped placeholders.

## Actionable Recommendations

### ACT-01: Immediate -- Replace U+2193 Characters

Replace the 17 U+2193 characters in generate_prompts/standard.txt (lines 32, 161-191) with ASCII equivalents. Suggested replacement: "-->" (consistent with the U+2192 replacements already made).

Estimated effort: Low (single file edit, 17 character replacements).

### ACT-02: Immediate -- Add ASCII-Only Test

Add a test method to test_prompt_slots.py that reads each prompt file and asserts all characters have ord(c) <= 127. This test should fail fast with a clear message identifying the non-ASCII characters and their line numbers.

Estimated effort: Low (1 new test method, approximately 15 lines).

### ACT-03: Short-term -- Add IMAGE_DESCRIPTIONS Placeholder Test

Add a test method to test_prompt_slots.py that verifies {IMAGE_DESCRIPTIONS} is present in extract_desc/standard.txt. This closes the supplementary coverage gap documented as VAL-I4.

Estimated effort: Low (1 new test method, approximately 10 lines).

### ACT-04: Short-term -- Expand Absolute Path Regex

Add Windows UNC path detection to the regex in test_prompt_slots.py. Suggested pattern addition: `(?:\\\\[^\\]+\\[^\\]+)` to match \\server\share patterns.

Estimated effort: Low (regex modification, 1 additional test case).

### ACT-05: Medium-term -- Address Pre-existing Baseline Failures

The baseline test suite has 11 failed + 38 errors (without -x flag) across multiple modules. Schedule a maintenance task to address these failures and improve overall test suite health.

Estimated effort: Medium (multiple modules affected, requires investigation per module).

### ACT-06: Process -- Update Task Template for Prompt Adaptation

Update the task template or checklist for prompt adaptation tasks to include:

1. ASCII-only compliance as an explicit acceptance criterion
2. Placeholder completeness test requirement
3. Regex scope documentation for path detection tests
4. Instruction to exclude timing claims from execution records

Estimated effort: Low (template update, approximately 30 minutes).

## Knowledge Artifacts

### KA-01: gen_media_content_v1 Prompt Template Structure

The prompt template structure for gen_media_content_v1 serves as a reference for future prompt adaptation tasks:

- workflows/gen_media_content_v1/prompts/extract_desc/standard.txt
- workflows/gen_media_content_v1/prompts/generate_prompts/standard.txt
- workflows/gen_media_content_v1/tests/test_prompt_slots.py

### KA-02: Source Adaptation Reference

The agnes_media_gen_v1 workflow package served as the source for adaptation:

- Source: workflows/agnes_media_gen_v1/step_1_extract/standard.txt
- Source: workflows/agnes_media_gen_v1/step_2_generate_prompts/standard.txt (inferred)

The adaptation patterns documented in this initiative can be reused for future cross-workflow prompt migrations.

### KA-03: Validation Methodology Reference

The validation report (VAL-20260815-006) documents a comprehensive validation methodology including:

- Independent file existence verification
- Independent test re-execution
- AST-based test structure verification
- String search for placeholder presence
- Regex-based absolute path scanning
- Character-based Unicode scanning
- Git status inspection for modification tracking
- Adversarial challenge resolution

This methodology can serve as a template for future validation reports.

### KA-04: Challenge Resolution Patterns

The 5 challenge findings and their resolutions document useful patterns for adversarial review:

- Finding 1 (Timing Evidence): Demonstrates how to handle non-deterministic measurements in validation
- Finding 2 (Missing ASCII Test): Demonstrates how to identify and address methodological gaps
- Finding 3 (UNC Path Gap): Demonstrates how to distinguish theoretical from practical coverage gaps
- Finding 4 (IMAGE_DESCRIPTIONS): Demonstrates how to classify supplementary vs. required coverage
- Finding 5 (Verification Source): Demonstrates how to improve evidence traceability in summary tables

### KA-05: context_extensions.py Placeholder Mapping Pattern

The context_extensions.py file demonstrates the standard placeholder mapping pattern:

- Step directories mapped via workspace_root relative paths (STEP_00_DIR, STEP_01_DIR, STEP_02_DIR)
- Configuration files mapped via workspace_root / filename (MEDIA_CONFIG -> config.json)
- Index files mapped via workspace_root / step_dir / filename (IMAGE_DESCRIPTIONS -> step_01_imagedesc/index.json)

This pattern is reusable for any workflow package that needs placeholder-based path resolution.
