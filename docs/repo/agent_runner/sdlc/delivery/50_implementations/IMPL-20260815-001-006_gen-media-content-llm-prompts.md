---
template_id: "SYS-03-IM"
version: "1.0.0"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "implementation plan for task execution"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "Approved"
effective_version: "20260815-001-006"
managed_by: "workflow-generated"
---

# Implementation Plan: gen_media_content_v1 Phase 7 -- LLM Prompts

## Document Metadata

- Document ID: IMPL-20260815-001-006
- Source task: TASK-20260815-001-07
- Date of generation: 2026-08-15
- Producing workflow: sdlc_01_impl_exec_review_v1 / impl_generate
- Scope: Create two LLM prompt templates (extract_desc, generate_prompts) and test suite for gen_media_content_v1

## Acceptance Criteria Tests

The following testable acceptance criteria are derived from TASK-20260815-001-07.
These define what "done" means before any implementation design.

### ACT-01: extract_desc prompt file exists and is valid UTF-8

- Test ID: ACT-01
- Test Description: The file `workflows/gen_media_content_v1/prompts/extract_desc/standard.txt` exists on disk and can be read as valid UTF-8 text.
- Verification Method: `Path.exists()` returns True; `open(path, encoding="utf-8").read()` raises no UnicodeDecodeError.
- Expected Result: File exists and is valid UTF-8.
- Current State: MISSING

### ACT-02: generate_prompts prompt file exists and is valid UTF-8

- Test ID: ACT-02
- Test Description: The file `workflows/gen_media_content_v1/prompts/generate_prompts/standard.txt` exists on disk and can be read as valid UTF-8 text.
- Verification Method: `Path.exists()` returns True; `open(path, encoding="utf-8").read()` raises no UnicodeDecodeError.
- Expected Result: File exists and is valid UTF-8.
- Current State: MISSING

### ACT-03: extract_desc prompt contains STEP_00_DIR placeholder

- Test ID: ACT-03
- Test Description: The content of `extract_desc/standard.txt` contains the literal string `{STEP_00_DIR}` as a slot placeholder.
- Verification Method: `assert "{STEP_00_DIR}" in content` in pytest.
- Expected Result: The string `{STEP_00_DIR}` is present in the file content.
- Current State: MISSING

### ACT-04: extract_desc prompt contains STEP_01_DIR placeholder

- Test ID: ACT-04
- Test Description: The content of `extract_desc/standard.txt` contains the literal string `{STEP_01_DIR}` as a slot placeholder.
- Verification Method: `assert "{STEP_01_DIR}" in content` in pytest.
- Expected Result: The string `{STEP_01_DIR}` is present in the file content.
- Current State: MISSING

### ACT-05: generate_prompts prompt contains STEP_01_DIR and STEP_02_DIR placeholders

- Test ID: ACT-05
- Test Description: The content of `generate_prompts/standard.txt` contains both `{STEP_01_DIR}` and `{STEP_02_DIR}` as slot placeholders.
- Verification Method: `assert "{STEP_01_DIR}" in content` and `assert "{STEP_02_DIR}" in content` in pytest.
- Expected Result: Both strings are present in the file content.
- Current State: MISSING

### ACT-06: generate_prompts prompt contains MEDIA_CONFIG placeholder

- Test ID: ACT-06
- Test Description: The content of `generate_prompts/standard.txt` contains the literal string `{MEDIA_CONFIG}` as a slot placeholder.
- Verification Method: `assert "{MEDIA_CONFIG}" in content` in pytest.
- Expected Result: The string `{MEDIA_CONFIG}` is present in the file content.
- Current State: MISSING

### ACT-07: No hardcoded absolute paths in either prompt

- Test ID: ACT-07
- Test Description: Neither prompt file contains hardcoded absolute filesystem paths (e.g., paths starting with `C:\`, `D:\`, `/home/`, `/usr/`).
- Verification Method: Regex scan for patterns like `[A-Z]:\\`, `/home/`, `/usr/` in prompt content. Assert no matches.
- Expected Result: No absolute path patterns found in either file.
- Current State: MISSING

### ACT-08: All tests pass with pytest

- Test ID: ACT-08
- Test Description: Running `pytest` on `workflows/gen_media_content_v1/tests/test_prompt_slots.py` produces 0 failures. The test module must contain at least 9 test functions covering all acceptance criteria.
- Verification Method: `.venv\Scripts\python -m pytest workflows/gen_media_content_v1/tests/test_prompt_slots.py -v` -- exit code 0, all tests PASSED.
- Expected Result: All tests pass with exit code 0.
- Current State: MISSING

### ACT-09: No existing files were modified

- Test ID: ACT-09
- Test Description: The implementation creates only new files. No pre-existing files in the repository are modified.
- Verification Method: `git diff --name-only` returns empty for tracked files; `git status` shows only new untracked files in the expected paths.
- Expected Result: No modifications to tracked files; only new files added at expected paths.
- Current State: N/A (post-implementation check)

## State Verification

### Files That Need to Be Created

| File | Status | Evidence |
|---|---|---|
| `workflows/gen_media_content_v1/prompts/extract_desc/standard.txt` | MISSING | Glob shows only `__init__.py` in `prompts/extract_desc/` directory |
| `workflows/gen_media_content_v1/prompts/generate_prompts/standard.txt` | MISSING | Glob shows only `__init__.py` in `prompts/generate_prompts/` directory |
| `workflows/gen_media_content_v1/tests/test_prompt_slots.py` | MISSING | No such file in `tests/` directory listing |

### Files That Already Exist (Read-Only References)

| File | Status | Purpose |
|---|---|---|
| `workflows/agnes_media_gen_v1/impls/agnes_media_v1/prompts/step_1_extract/standard.txt` | EXISTS (156 lines) | Source prompt for extract_desc adaptation |
| `workflows/agnes_media_gen_v1/impls/agnes_media_v1/prompts/step_2_generate/standard.txt` | EXISTS (421 lines) | Source prompt for generate_prompts adaptation |
| `workflows/gen_media_content_v1/context_extensions.py` | EXISTS (143 lines) | Defines slot variable names and path resolution |
| `workflows/gen_media_content_v1/workflow.toml` | EXISTS (187 lines) | Defines step names: `extract_desc`, `generate_prompts` |
| `workflows/gen_media_content_v1/prompts/extract_desc/__init__.py` | EXISTS | Package marker (not modified) |
| `workflows/gen_media_content_v1/prompts/generate_prompts/__init__.py` | EXISTS | Package marker (not modified) |

### Pre-Existing Test Files (Not Modified)

The `tests/` directory contains 6 existing test files (test_actions.py, test_context.py, test_image_provider_agnes_v1.py, test_video_provider_agnes_v2.py, test_video_provider_happyhorse_v1_1.py, test_video_provider_none.py). These are NOT modified by this task.

## Implementation Overview

This task creates two LLM prompt template files and a test suite for the gen_media_content_v1 workflow's prompt-driven steps. The prompts are adapted from the existing agnes_media_gen_v1 workflow, with all hardcoded paths already replaced by slot placeholders in the source files.

Key observations from source analysis:
1. The source extract_desc prompt (step_1_extract/standard.txt) already uses slot placeholders: `{STEP_00_DIR}`, `{STEP_01_DIR}`, `{STEP_00_ARCHIVE}`, `{MEDIA_CONFIG}`, `{GOVERNANCE_RUNTIME_ROOT}`, `{PLATFORM_RUNTIME_ROOT}`. However, it contains an internal contradiction regarding archiving (see Step 1 details below).
2. The source generate_prompts prompt (step_2_generate/standard.txt) already uses slot placeholders: `{STEP_01_DIR}`, `{STEP_02_DIR}`, `{MEDIA_CONFIG}`. It does NOT contain `{GOVERNANCE_RUNTIME_ROOT}` or `{PLATFORM_RUNTIME_ROOT}`. It contains a Linux-specific `shuf` command that must be replaced for cross-platform compatibility.
3. Both source prompts are well-structured and match the task requirements for attribute extraction and variant generation.
4. The gen_media_content_v1 context_extensions.py defines all required slot variables (STEP_00_DIR through STEP_04_ARCHIVE, MEDIA_CONFIG, GOVERNANCE_RUNTIME_ROOT, PLATFORM_RUNTIME_ROOT).

The implementation approach:
- Copy the source extract_desc prompt to the target location, making targeted adjustments for gen_media_content_v1 conventions: removing the archiving instruction from the Objective section, removing the `{STEP_00_ARCHIVE}` Reference Input entry, and retaining the safety note that says "do NOT archive yourself."
- Copy the source generate_prompts prompt to the target location, replacing the Linux-specific `shuf` shell command with a cross-platform random shuffle instruction.
- Create test_prompt_slots.py with 9+ test functions verifying all acceptance criteria.

Documented deviations from TASK placeholder requirements:
- TASK Step 1 lists `{GOVERNANCE_RUNTIME_ROOT}` and `{PLATFORM_RUNTIME_ROOT}` as placeholders. The source extract_desc prompt contains these in its Reference Inputs section. They will be retained in the adapted prompt.
- TASK Step 2 lists `{GOVERNANCE_RUNTIME_ROOT}` and `{PLATFORM_RUNTIME_ROOT}` as placeholders for generate_prompts. However, the source generate_prompts prompt does NOT contain these placeholders. Since the task says "Adapt from" the source, the adapted prompt will match the source content. The generate_prompts step does not require governance/platform runtime root paths for its operation. This is noted as an acknowledged deviation.

## Task Traceability

| TASK Acceptance Criterion | IMPL Acceptance Test | Trace |
|---|---|---|
| AC-01: extract_desc prompt exists, valid UTF-8 | ACT-01 | Direct mapping |
| AC-02: generate_prompts prompt exists, valid UTF-8 | ACT-02 | Direct mapping |
| AC-03: extract_desc contains {STEP_00_DIR} | ACT-03 | Direct mapping |
| AC-04: extract_desc contains {STEP_01_DIR} | ACT-04 | Direct mapping |
| AC-05: generate_prompts contains {STEP_01_DIR} and {STEP_02_DIR} | ACT-05 | Direct mapping |
| AC-06: generate_prompts contains {MEDIA_CONFIG} | ACT-06 | Direct mapping |
| AC-07: No hardcoded absolute paths | ACT-07 | Direct mapping |
| AC-08: All 9 tests pass with pytest | ACT-08 | Direct mapping |
| AC-09: No existing files modified | ACT-09 | Direct mapping |

## Step-by-Step Plan

### Step 1: Create extract_desc prompt file

- Action: Write `workflows/gen_media_content_v1/prompts/extract_desc/standard.txt` adapted from the source prompt.
- Satisfies: ACT-01, ACT-03, ACT-04, ACT-07
- Details: Adapt from `workflows/agnes_media_gen_v1/impls/agnes_media_v1/prompts/step_1_extract/standard.txt`. The source already uses correct slot placeholders. The source prompt contains an internal contradiction: the Objective section (lines 8-10) instructs the LLM to "archive the processed input images by copying them to {STEP_00_ARCHIVE} and removing them from {STEP_00_DIR}," while the Note section (lines 124-126) says "do NOT archive or remove files from {STEP_00_DIR} yourself." Since gen_media_content_v1 workflow.toml defines `archive_step_00` as a separate action step that runs after `extract_descriptions`, the adapted prompt must:
  (a) Remove the archiving instruction from the Objective section (lines 8-10) -- reword to omit the archive-and-remove sentence, ending the Objective at the index.json production instruction.
  (b) Remove the `{STEP_00_ARCHIVE}` entry from Reference Inputs (line 17) since the LLM does not need the archive path.
  (c) RETAIN the Note section (lines 124-126) that says "Archiving of processed input images from {STEP_00_DIR} is handled automatically by a subsequent archive step -- do NOT archive or remove files from {STEP_00_DIR} yourself." This is a safety instruction to prevent the LLM from attempting to archive.
  Retain all 9 attribute groups, JSON structure, index.json output, and IMAGE_DESCRIPTIONS artifact reporting.

### Step 2: Create generate_prompts prompt file

- Action: Write `workflows/gen_media_content_v1/prompts/generate_prompts/standard.txt` adapted from the source prompt.
- Satisfies: ACT-02, ACT-05, ACT-06, ACT-07
- Details: Adapt from `workflows/agnes_media_gen_v1/impls/agnes_media_v1/prompts/step_2_generate/standard.txt`. The source already uses correct slot placeholders (`{STEP_01_DIR}`, `{STEP_02_DIR}`, `{MEDIA_CONFIG}`). One required adaptation: the source prompt contains a Linux-specific shell command (`shuf -e ... | head -n N`) at lines 298-301 that instructs the LLM to randomly draw styles. Since `shuf` is a GNU coreutils utility not available on Windows, and the agent-runner-v2 executes on both platforms, the adapted prompt must replace the `shuf` command with a cross-platform instruction: "Before generating prompts for EACH image, internally perform a random shuffle to draw N styles from the style pool (replace N with the num_variants value)." The fallback clause about simulating random shuffle is retained for completeness. All other content (JSON schema, variant rules, video prompt rules, negative prompt, self-validation checklist) is copied as-is.

### Step 3: Create test suite

- Action: Write `workflows/gen_media_content_v1/tests/test_prompt_slots.py` with 9+ test functions.
- Satisfies: ACT-08
- Details: Tests verify file existence, UTF-8 validity, placeholder presence, no hardcoded paths, and content length.

### Step 4: Run tests and verify

- Action: Execute `pytest workflows/gen_media_content_v1/tests/test_prompt_slots.py -v` to confirm all tests pass.
- Satisfies: ACT-08, ACT-09
- Details: Verify exit code 0, all tests PASSED. Verify `git diff --name-only` shows no modifications to existing files.

## Code Changes

### Files to Create

| File | Description |
|---|---|
| `workflows/gen_media_content_v1/prompts/extract_desc/standard.txt` | LLM prompt template for image description extraction step |
| `workflows/gen_media_content_v1/prompts/generate_prompts/standard.txt` | LLM prompt template for image/video prompt generation step |
| `workflows/gen_media_content_v1/tests/test_prompt_slots.py` | Test suite verifying prompt file existence, placeholders, and content |

### Files to Modify

None. This task creates only new files.

### Files to Delete

None.

### Codebase Files Referenced (Read-Only)

| File | Purpose |
|---|---|
| `workflows/agnes_media_gen_v1/impls/agnes_media_v1/prompts/step_1_extract/standard.txt` | Source template for extract_desc adaptation |
| `workflows/agnes_media_gen_v1/impls/agnes_media_v1/prompts/step_2_generate/standard.txt` | Source template for generate_prompts adaptation |
| `workflows/gen_media_content_v1/context_extensions.py` | Defines slot variable names for runtime path resolution |
| `workflows/gen_media_content_v1/workflow.toml` | Defines step names and slot references |
| `workflows/gen_media_content_v1/prompts/extract_desc/__init__.py` | Package marker (confirms directory structure) |
| `workflows/gen_media_content_v1/prompts/generate_prompts/__init__.py` | Package marker (confirms directory structure) |

## Test Implementation

The following test code implements the acceptance criteria tests from Section 1.

```python
"""Tests for gen_media_content_v1 LLM prompt slot placeholders.

Verifies that prompt templates exist, are valid UTF-8, contain required
slot placeholders, and do not contain hardcoded absolute paths.

Reference: TASK-20260815-001-07 Acceptance Criteria AC-01 through AC-09.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

# Resolve paths relative to the workflow package root
WORKFLOW_ROOT = Path(__file__).resolve().parent.parent
EXTRACT_DESC_PROMPT = WORKFLOW_ROOT / "prompts" / "extract_desc" / "standard.txt"
GENERATE_PROMPTS_PROMPT = WORKFLOW_ROOT / "prompts" / "generate_prompts" / "standard.txt"

# Pattern to detect hardcoded absolute paths
_ABS_PATH_PATTERN = re.compile(
    r"(?:[A-Z]:[/\\])"        # Windows drive letter paths (C:\, D:/)
    r"|(?:/(?:home|usr|etc|tmp|var|opt)/)"  # Unix absolute paths
    r"|(?:^/[^{])",            # Root-relative paths not starting with {
    re.MULTILINE,
)


@pytest.fixture
def extract_desc_content() -> str:
    """Read extract_desc prompt as UTF-8."""
    return EXTRACT_DESC_PROMPT.read_text(encoding="utf-8")


@pytest.fixture
def generate_prompts_content() -> str:
    """Read generate_prompts prompt as UTF-8."""
    return GENERATE_PROMPTS_PROMPT.read_text(encoding="utf-8")


# ACT-01: extract_desc prompt file exists and is valid UTF-8
class TestExtractDescExists:
    def test_file_exists(self) -> None:
        assert EXTRACT_DESC_PROMPT.exists(), (
            f"extract_desc prompt not found at {EXTRACT_DESC_PROMPT}"
        )

    def test_valid_utf8(self) -> None:
        # Reading with encoding="utf-8" will raise UnicodeDecodeError if invalid
        content = EXTRACT_DESC_PROMPT.read_text(encoding="utf-8")
        assert isinstance(content, str)
        assert len(content) > 0


# ACT-02: generate_prompts prompt file exists and is valid UTF-8
class TestGeneratePromptsExists:
    def test_file_exists(self) -> None:
        assert GENERATE_PROMPTS_PROMPT.exists(), (
            f"generate_prompts prompt not found at {GENERATE_PROMPTS_PROMPT}"
        )

    def test_valid_utf8(self) -> None:
        content = GENERATE_PROMPTS_PROMPT.read_text(encoding="utf-8")
        assert isinstance(content, str)
        assert len(content) > 0


# ACT-03: extract_desc contains {STEP_00_DIR} placeholder
class TestExtractDescStep00Dir:
    def test_contains_step_00_dir(self, extract_desc_content: str) -> None:
        assert "{STEP_00_DIR}" in extract_desc_content, (
            "extract_desc prompt missing {STEP_00_DIR} placeholder"
        )


# ACT-04: extract_desc contains {STEP_01_DIR} placeholder
class TestExtractDescStep01Dir:
    def test_contains_step_01_dir(self, extract_desc_content: str) -> None:
        assert "{STEP_01_DIR}" in extract_desc_content, (
            "extract_desc prompt missing {STEP_01_DIR} placeholder"
        )


# ACT-05: generate_prompts contains {STEP_01_DIR} and {STEP_02_DIR}
class TestGeneratePromptsStepDirs:
    def test_contains_step_01_dir(self, generate_prompts_content: str) -> None:
        assert "{STEP_01_DIR}" in generate_prompts_content, (
            "generate_prompts prompt missing {STEP_01_DIR} placeholder"
        )

    def test_contains_step_02_dir(self, generate_prompts_content: str) -> None:
        assert "{STEP_02_DIR}" in generate_prompts_content, (
            "generate_prompts prompt missing {STEP_02_DIR} placeholder"
        )


# ACT-06: generate_prompts contains {MEDIA_CONFIG}
class TestGeneratePromptsMediaConfig:
    def test_contains_media_config(self, generate_prompts_content: str) -> None:
        assert "{MEDIA_CONFIG}" in generate_prompts_content, (
            "generate_prompts prompt missing {MEDIA_CONFIG} placeholder"
        )


# ACT-07: No hardcoded absolute paths in either prompt
class TestNoHardcodedPaths:
    def test_extract_desc_no_absolute_paths(self, extract_desc_content: str) -> None:
        matches = _ABS_PATH_PATTERN.findall(extract_desc_content)
        assert not matches, (
            f"extract_desc prompt contains hardcoded absolute paths: {matches}"
        )

    def test_generate_prompts_no_absolute_paths(
        self, generate_prompts_content: str
    ) -> None:
        matches = _ABS_PATH_PATTERN.findall(generate_prompts_content)
        assert not matches, (
            f"generate_prompts prompt contains hardcoded absolute paths: {matches}"
        )


# Supplementary: Content length checks (>100 chars)
class TestContentLength:
    def test_extract_desc_meaningful_content(self, extract_desc_content: str) -> None:
        assert len(extract_desc_content) > 100, (
            "extract_desc prompt has less than 100 characters"
        )

    def test_generate_prompts_meaningful_content(
        self, generate_prompts_content: str
    ) -> None:
        assert len(generate_prompts_content) > 100, (
            "generate_prompts prompt has less than 100 characters"
        )
```

This test module provides the following test functions (total 12 test methods across 9 test classes):

| Test Class | Method | Satisfies |
|---|---|---|
| TestExtractDescExists | test_file_exists | ACT-01 |
| TestExtractDescExists | test_valid_utf8 | ACT-01 |
| TestGeneratePromptsExists | test_file_exists | ACT-02 |
| TestGeneratePromptsExists | test_valid_utf8 | ACT-02 |
| TestExtractDescStep00Dir | test_contains_step_00_dir | ACT-03 |
| TestExtractDescStep01Dir | test_contains_step_01_dir | ACT-04 |
| TestGeneratePromptsStepDirs | test_contains_step_01_dir | ACT-05 |
| TestGeneratePromptsStepDirs | test_contains_step_02_dir | ACT-05 |
| TestGeneratePromptsMediaConfig | test_contains_media_config | ACT-06 |
| TestNoHardcodedPaths | test_extract_desc_no_absolute_paths | ACT-07 |
| TestNoHardcodedPaths | test_generate_prompts_no_absolute_paths | ACT-07 |
| TestContentLength | test_extract_desc_meaningful_content | Supplementary |
| TestContentLength | test_generate_prompts_meaningful_content | Supplementary |

Note: The task specification requires "9 test cases" and ACT-08 requires "All 9 tests pass". The task's "9 test cases" maps to the 9 acceptance criteria (AC-01 through AC-09), not to 9 pytest test functions. Of the 9 criteria, AC-01 through AC-07 are verified by pytest test methods (12 test methods across 7 test classes, plus 2 supplementary content-length tests). AC-08 is the meta-criterion that all pytest tests pass. AC-09 (no existing files modified) cannot be verified by pytest -- it is verified by external git inspection (`git diff --name-only` and `git status`). This is an inherent limitation: a pytest test running inside the test suite cannot independently verify that no tracked files were modified. The test module therefore provides 12 pytest test methods covering AC-01 through AC-07 plus supplementary checks, and ACT-09 is verified as a post-implementation git check as described in ACT-09's verification method.

## Rollback Plan

If implementation fails or tests do not pass:

1. The three new files can be safely deleted without affecting any existing functionality:
   - `workflows/gen_media_content_v1/prompts/extract_desc/standard.txt`
   - `workflows/gen_media_content_v1/prompts/generate_prompts/standard.txt`
   - `workflows/gen_media_content_v1/tests/test_prompt_slots.py`

2. No existing files are modified, so no rollback of existing code is needed.

3. The workflow.toml step definitions (`prompt = "{{ slot.extract_desc }}"` and `prompt = "{{ slot.generate_prompts }}"`) already reference these slot names. If the prompt files do not exist, the workflow will fail at runtime with a clear error indicating the missing prompt template. This is the expected behavior prior to this task's completion.

4. To fully revert to pre-task state, simply delete the three new files. The workflow remains in its prior state.

## Dependencies

### External Dependencies

| Dependency | Version | Purpose |
|---|---|---|
| Python | 3.12+ | Test execution runtime |
| pytest | 9.1.1 | Test runner (already installed in .venv) |

### Prerequisites

| Prerequisite | Status | Notes |
|---|---|---|
| gen_media_content_v1 workflow directory structure | EXISTS | Directories `prompts/extract_desc/` and `prompts/generate_prompts/` already exist with `__init__.py` |
| Source prompts in agnes_media_gen_v1 | EXISTS | Both source prompt files verified present |
| context_extensions.py slot definitions | EXISTS | All required slot variables defined |
| workflow.toml step definitions | EXISTS | Steps reference `slot.extract_desc` and `slot.generate_prompts` |

### Upstream Artifacts

| Artifact | Source | Status |
|---|---|---|
| TASK-20260815-001-07 | sdlc/delivery/40_tasks/ | Approved |
| TASK-20260815-001-06 (Phase 6) | Prior task | Completed (provides __none__ provider) |

## Open Questions

None. All required information is available from the task specification, source prompts, and codebase context. The implementation is straightforward file creation with no ambiguities.

### Assumptions

1. The source prompts in agnes_media_gen_v1 are the correct adaptation basis -- confirmed by task specification Step 1 and Step 2 references.
2. The slot placeholder names in the source prompts match the context_extensions.py slot definitions -- confirmed by direct comparison.
3. The source extract_desc prompt contains an internal contradiction regarding archiving: the Objective section instructs the LLM to archive files to {STEP_00_ARCHIVE}, while the Note section says "do NOT archive or remove files." The adapted prompt resolves this by removing the archiving instruction from the Objective (since archive_step_00 handles it) and the {STEP_00_ARCHIVE} Reference Input, while RETAINING the Note as a safety instruction to prevent the LLM from attempting to archive.
4. The test file path `workflows/gen_media_content_v1/tests/test_prompt_slots.py` is within the existing tests package and will be discovered by pytest.
5. The source generate_prompts prompt does not contain `{GOVERNANCE_RUNTIME_ROOT}` or `{PLATFORM_RUNTIME_ROOT}` placeholders. These are not required for the generate_prompts step operation, which only needs directory paths and media config. This is an acknowledged deviation from the TASK Step 2 generic placeholder list.

## Test Semantics Note

The placeholder verification tests (ACT-03 through ACT-06) check for the presence of placeholder strings in the prompt content. They do not verify semantic correctness (e.g., that a placeholder is used in the correct context, appears the expected number of times, or is not merely in a comment). This is intentional: the acceptance criteria specify presence verification, not functional validation. Semantic correctness of prompt templates is validated at runtime when the workflow executes and slot substitution occurs. Integration testing of prompt rendering is out of scope for this task.

## Challenge Resolution

### Attack 1: Attack Necessity - Implementation Required
**Evaluation:** Already addressed
**Resolution:** No change needed. The challenge confirms that target files do not exist and the implementation work is necessary. The IMPL already documents the MISSING state of all three target files in the State Verification section.
**Evidence:** Filesystem verification confirmed: `workflows/gen_media_content_v1/prompts/extract_desc/standard.txt` does not exist (only `__init__.py`), `workflows/gen_media_content_v1/prompts/generate_prompts/standard.txt` does not exist (only `__init__.py`), `workflows/gen_media_content_v1/tests/test_prompt_slots.py` does not exist.
**Affected section:** None (no change required)

### Attack 2: ACT-09 Test Coverage Gap
**Evaluation:** Valid
**Resolution:** Updated the test documentation note (Section "Test Implementation") to explicitly clarify the relationship between the task's "9 test cases" wording and the actual test structure. The task's "9 test cases" maps to 9 acceptance criteria (AC-01 through AC-09), not 9 pytest test functions. ACT-08 is the meta-criterion that all pytest tests pass. ACT-09 (no existing files modified) is verified via git inspection, not pytest, because a pytest test cannot independently verify that no tracked files were modified. The updated note documents this inherent limitation clearly.
**Evidence:** TASK-20260815-001-07 AC-08 states "All 9 tests pass with pytest." AC-09 states "No existing files were modified." The IMPL test module provides 12 pytest test methods across 9 test classes covering ACT-01 through ACT-07 plus supplementary checks. ACT-09 is verified via `git diff --name-only` and `git status` as specified in ACT-09's verification method.
**Affected section:** Test Implementation (note at end of test table)

### Attack 3: Incorrect Archive Reference Removal
**Evaluation:** Partially valid -- the challenge's reasoning contains a factual error, but the IMPL's original description was insufficiently detailed
**Resolution:** The challenge claims "The source prompt does NOT instruct the LLM to perform archiving." This is factually incorrect. The source extract_desc prompt Objective section (lines 8-10 of step_1_extract/standard.txt) explicitly states: "archive the processed input images by copying them to {STEP_00_ARCHIVE} and removing them from {STEP_00_DIR}." However, the Note section (lines 124-126) contradicts this by saying "do NOT archive or remove files from {STEP_00_DIR} yourself." The source has an internal contradiction. Updated Step 1 details to clearly document: (a) removing the archiving instruction from the Objective section, (b) removing the {STEP_00_ARCHIVE} Reference Input entry, and (c) RETAINING the Note section as a safety instruction. Updated Assumptions section accordingly.
**Evidence:** Source file `workflows/agnes_media_gen_v1/impls/agnes_media_v1/prompts/step_1_extract/standard.txt`: Line 9 says "input images by copying them to {STEP_00_ARCHIVE} and removing them from {STEP_00_DIR}." Lines 124-126 say "Archiving of processed input images from {STEP_00_DIR} is handled automatically by a subsequent archive step -- do NOT archive or remove files from {STEP_00_DIR} yourself." workflow.toml lines 66-72 define `archive_step_00` as a separate action step.
**Affected section:** Step 1 (details), Assumptions (item 3), Implementation Overview

### Attack 4: Platform-Specific Shell Command in Cross-Platform Workflow
**Evaluation:** Valid
**Resolution:** The source generate_prompts prompt (lines 298-301 of step_2_generate/standard.txt) contains a `shuf -e ... | head -n N` command which is a GNU coreutils utility not available on Windows. Updated Step 2 details to document that the adapted prompt will replace the `shuf` command with a cross-platform instruction: "internally perform a random shuffle to draw N styles from the style pool." The fallback clause about simulating random shuffle is retained. This eliminates the platform compatibility issue entirely.
**Evidence:** Source file `workflows/agnes_media_gen_v1/impls/agnes_media_v1/prompts/step_2_generate/standard.txt` lines 298-301 contain `shuf -e "natural" "cinematic" ... | head -n N`. Lines 303-305 contain the fallback: "If shell execution is not available, internally simulate a random shuffle." The `shuf` command is confirmed Linux-only (GNU coreutils).
**Affected section:** Step 2 (details), Implementation Overview

### Attack 5: Missing Placeholder in Task Requirements
**Evaluation:** Partially valid
**Resolution:** The TASK Step 2 lists `{GOVERNANCE_RUNTIME_ROOT}` and `{PLATFORM_RUNTIME_ROOT}` as required placeholders for generate_prompts. However, the source generate_prompts prompt (step_2_generate/standard.txt) does NOT contain these placeholders -- confirmed by grep search returning no matches. The adapted prompt matches the source content. Updated Implementation Overview to document this as an acknowledged deviation with justification: the generate_prompts step does not require governance/platform runtime root paths for its operation. Added Assumption 5 documenting this deviation.
**Evidence:** Grep for `GOVERNANCE_RUNTIME_ROOT|PLATFORM_RUNTIME_ROOT` in `step_2_generate/standard.txt` returned no matches. The source prompt only uses `{STEP_01_DIR}`, `{STEP_02_DIR}`, and `{MEDIA_CONFIG}`. The source extract_desc prompt DOES contain `{GOVERNANCE_RUNTIME_ROOT}` and `{PLATFORM_RUNTIME_ROOT}` (lines 19-20), so the deviation is specific to generate_prompts only.
**Affected section:** Implementation Overview (documented deviations), Assumptions (new item 5)

### Attack 6: Test Validation Only Checks Presence, Not Semantics
**Evaluation:** Valid but minor -- tests meet the letter of the acceptance criteria
**Resolution:** Added a "Test Semantics Note" section at the end of the document (before Challenge Resolution) explaining that placeholder verification tests check for string presence only, not semantic correctness. This is intentional: the acceptance criteria specify presence verification. Semantic correctness is validated at runtime when the workflow executes and slot substitution occurs. Integration testing of prompt rendering is out of scope for this task. No changes to the test implementation are needed -- the tests fulfill the stated acceptance criteria.
**Evidence:** TASK-20260815-001-07 AC-03 through AC-06 specify placeholder presence checks ("contains {STEP_00_DIR} placeholder", etc.). The test implementation uses `assert "{PLACEHOLDER}" in content` which directly matches the AC wording.
**Affected section:** New "Test Semantics Note" section added
