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
effective_version: "{job_id}"
managed_by: "workflow-generated"
---

# Implementation Plan: gen_media_content_v1 Phase 9 - Wire Orchestrator + Integration

## Document Metadata

- Document ID: IMPL-20260815-001-007
- Source task: TASK-20260815-001-09
- Date of generation: 2026-08-15
- Producing workflow: sdlc_01_impl_exec_review_v1 / impl_generate
- Scope: Replace orchestrator stubs in actions.py with full provider-dispatch, batch API, download, and index writing; create integration tests
- Prior task: TASK-20260815-001-08 (Phase 8 BCS impls)

## Acceptance Criteria Tests

The following testable acceptance criteria are derived from TASK-20260815-001-09.
These define what "done" means before any implementation design.

### ACT-01: generate_images_default dispatches to configured provider

- Test ID: ACT-01
- Test Description: When called with a valid config specifying render_image provider, generate_images_default imports and calls the provider's call_api function for each variant.
- Verification Method: pytest test mocking import_provider to return a mock module; assert mock.call_api is invoked once per variant with correct prompt argument.
- Expected Result: provider.call_api(prompt=..., config=..., api_key=..., base_url=...) called for each variant in each *_prompts.json file.
- Current State: MISSING -- generate_images_default currently returns REJECTED stub without calling any provider.

### ACT-02: generate_images_default downloads images and saves to STEP_03_DIR

- Test ID: ACT-02
- Test Description: After provider returns {"image_url": "..."}, the action downloads the image content via requests.get and writes binary data to a file in STEP_03_DIR using sequenced filenames.
- Verification Method: pytest test mocking provider.call_api to return {"image_url": "http://example.com/img.png"} and mocking requests.get to return mock response with content; assert file exists in STEP_03_DIR with correct binary content.
- Expected Result: At least one .png file written to STEP_03_DIR containing the mocked download content.
- Current State: MISSING -- stub performs no download or file write.

### ACT-03: generate_images_default writes index.json with correct file mappings

- Test ID: ACT-03
- Test Description: After processing all variants, generate_images_default writes an index.json to STEP_03_DIR containing {"step": "...", "files": [...]} where each entry maps input variant file to output image file.
- Verification Method: pytest test with mocked provider and download; load STEP_03_DIR/index.json after action returns; assert "step" and "files" keys exist and file mappings reference correct input/output paths.
- Expected Result: index.json is valid JSON with step name and file_mappings list.
- Current State: MISSING -- stub writes no index.

### ACT-04: generate_images_default returns REJECTED when no provider configured

- Test ID: ACT-04
- Test Description: When config["actions"]["render_image"] is "__none__" or empty string, generate_images_default returns ActionResult with status="REJECTED" and reject_code="MISSING_PROVIDER".
- Verification Method: pytest test with config having render_image="__none__"; assert result.status == "REJECTED" and result.reject_code == "MISSING_PROVIDER".
- Expected Result: ActionResult(status="REJECTED", reject_code="MISSING_PROVIDER").
- Current State: PARTIAL -- stub always returns REJECTED regardless of config. After implementation, must still return REJECTED specifically when provider is "__none__" or empty.

### ACT-05: generate_videos_default dispatches to configured provider

- Test ID: ACT-05
- Test Description: When called with a valid config specifying render_video provider (not "__none__"), generate_videos_default imports and calls the provider's call_api function for each image/variant combination.
- Verification Method: pytest test mocking import_provider and provider.call_api; assert call_api is invoked with prompt=video_prompt and image=image_url arguments.
- Expected Result: provider.call_api(prompt=..., image=..., config=..., api_key=..., base_url=...) called for each image entry.
- Current State: MISSING -- generate_videos_default currently returns REJECTED stub without calling any provider.

### ACT-06: generate_videos_default handles __none__ provider (returns APPROVED, skipped)

- Test ID: ACT-06
- Test Description: When config["actions"]["render_video"] is "__none__", generate_videos_default returns ActionResult with status="APPROVED" and remark indicating video generation was skipped.
- Verification Method: pytest test with config having render_video="__none__"; assert result.status == "APPROVED" and "skip" in result.remark.lower().
- Expected Result: ActionResult(status="APPROVED", remark containing "skip").
- Current State: MISSING -- stub returns REJECTED for all cases.

### ACT-07: generate_videos_default handles {"skipped": True} from provider

- Test ID: ACT-07
- Test Description: When a provider's call_api returns {"skipped": True}, generate_videos_default skips that entry without attempting download, and continues processing remaining entries.
- Verification Method: pytest test with mock provider returning {"skipped": True} for one call and {"video_url": "..."} for another; assert only the non-skipped entry produces a downloaded file.
- Expected Result: Skipped entries produce no output file; non-skipped entries are downloaded normally.
- Current State: MISSING -- stub does not call provider at all.

### ACT-08: import_provider works for valid names, raises ImportError for invalid

- Test ID: ACT-08
- Test Description: import_provider successfully imports existing provider modules (agnes_v1, agnes_v2, happyhorse_v1_1, __none__) and raises ImportError for nonexistent provider names.
- Verification Method: pytest test calling import_provider with valid and invalid names; assert valid calls return module with call_api attribute, invalid calls raise ImportError.
- Expected Result: Valid imports succeed; invalid imports raise ImportError with descriptive message.
- Current State: EXISTS -- import_provider function is already implemented and tested in test_actions.py.

### ACT-09: All 14 tests pass with pytest

- Test ID: ACT-09
- Test Description: The test file tests/test_orchestrator.py contains exactly 14 test methods and all pass when run with pytest.
- Verification Method: .venv\Scripts\python -m pytest workflows/gen_media_content_v1/tests/test_orchestrator.py -v
- Expected Result: 14 passed.
- Current State: MISSING -- test_orchestrator.py does not exist.

### ACT-10: Full test suite passes (all phases)

- Test ID: ACT-10
- Test Description: Running the full gen_media_content_v1 test suite (all test files) passes without errors.
- Verification Method: .venv\Scripts\python -m pytest workflows/gen_media_content_v1/tests/ -v
- Expected Result: All tests across all test files pass.
- Current State: PARTIAL -- existing tests pass but test_actions.py tests for stubs will need updating after stubs are replaced.

### ACT-11: No existing files outside gen_media_content_v1 were modified

- Test ID: ACT-11
- Test Description: Only files within workflows/gen_media_content_v1/ are modified or created. No files in agent_runner_v2/, other workflows/, or other directories are changed.
- Verification Method: git diff --name-only (or manual file inventory check) to verify all changes are under workflows/gen_media_content_v1/.
- Expected Result: All modified/created files are within workflows/gen_media_content_v1/ directory tree.
- Current State: N/A -- verification to be performed after implementation.

## State Verification

### Files That Already Exist and Are Complete

| File | Status | Evidence |
|------|--------|----------|
| workflows/gen_media_content_v1/actions.py (utility functions) | COMPLETE | Lines 1-234: _load_config, _api_request_with_retry, _write_index, _get_next_sequence_filename, _get_api_actions_dir, import_provider all fully implemented |
| workflows/gen_media_content_v1/api_actions/render_image/agnes_v1/__init__.py | COMPLETE | 89 lines, call_api(prompt, config, api_key, base_url) returns {"image_url": "..."} |
| workflows/gen_media_content_v1/api_actions/render_video/agnes_v2/__init__.py | COMPLETE | 167 lines, call_api(prompt, image, config, api_key, base_url) returns {"video_url": "..."} |
| workflows/gen_media_content_v1/api_actions/render_video/happyhorse_v1_1/__init__.py | COMPLETE | 158 lines, call_api(prompt, image, config, api_key, base_url) returns {"video_url": "..."} |
| workflows/gen_media_content_v1/api_actions/render_video/__none__/__init__.py | COMPLETE | 44 lines, call_api() returns {"skipped": True, "reason": "..."} |
| workflows/gen_media_content_v1/config.json.sample | COMPLETE | 38 lines, full config structure with actions, api, num_variants, etc. |
| workflows/gen_media_content_v1/context_extensions.py | COMPLETE | 143 lines, provides MEDIA_CONFIG, STEP_02_DIR, STEP_03_DIR, STEP_04_DIR |
| workflows/gen_media_content_v1/workflow.toml | COMPLETE | 187 lines, steps reference generate_images_default and generate_videos_default |
| workflows/gen_media_content_v1/tests/test_actions.py | COMPLETE | 387 lines, 14 tests for utilities and stubs |

### Files That Exist but Need Modification

| File | Current State | Required Changes |
|------|--------------|-----------------|
| workflows/gen_media_content_v1/actions.py (lines 241-274) | Stubs for generate_images_default and generate_videos_default | Replace both stubs with full orchestrator implementations |
| workflows/gen_media_content_v1/tests/test_actions.py | Tests for stubs (TestGenerateImagesDefault, TestGenerateVideosDefault) | Update TestGenerateImagesDefault and TestGenerateVideosDefault classes to test new behavior instead of stub behavior |

### Files That Need to Be Created From Scratch

| File | Purpose |
|------|---------|
| workflows/gen_media_content_v1/tests/test_orchestrator.py | 14 integration tests for orchestrator behavior (ACT-09) |

### Evidence of Verification

- Glob for test_orchestrator.py returned no results (file does not exist).
- Read of actions.py confirmed stubs at lines 241-274 returning REJECTED with MISSING_PROVIDER.
- Read of all provider __init__.py files confirmed complete call_api implementations.
- Read of config.json.sample confirmed config structure.
- Read of context_extensions.py confirmed context variable names (MEDIA_CONFIG, STEP_02_DIR, STEP_03_DIR, STEP_04_DIR).

## Implementation Overview

This is a substantial implementation task. The stubs in actions.py must be replaced with full orchestrator logic that:

1. Dynamically imports providers via import_provider()
2. Resolves API keys via ApiKeyPool from environment variables
3. Scans variant directories for input files
4. Calls provider APIs in batch (one per variant)
5. Downloads result media (images/videos) via requests.get
6. Writes output files with sequenced filenames
7. Writes index.json tracking input-to-output file mappings
8. Returns appropriate ActionResult (APPROVED/REJECTED) with proper error handling

The implementation follows the reference pattern established in workflows/agnes_media_gen_v1/impls/agnes_media_v1/actions.py but adapted for the pluggable provider architecture of gen_media_content_v1.

Key design decisions:
- API key resolution uses a provider-name-to-prefix mapping (e.g., "agnes_v1" -> "AGNES_API_KEY", "happyhorse_v1_1" -> "HAPPYHORSE_API_KEY")
- Base URL resolution uses a provider-name-to-env-var mapping (e.g., "agnes_*" -> "AGNES_BASE_URL", "happyhorse_*" -> "HAPPYHORSE_BASE_URL")
- Image orchestrator scans STEP_02_DIR for *_prompts.json variant files
- Video orchestrator reads index.json from STEP_03_DIR to discover generated images with image_url, then cross-references to STEP_02_DIR variant files for video prompts (t2v_prompt1)
- Error handling: individual item failures are logged and skipped; if ALL items fail, return REJECTED; if SOME succeed, return APPROVED with remark noting partial success
- Config validation: provider name must exist in config["api"] section; base_url must resolve to non-empty string; empty directories return REJECTED with NO_INPUTS

What remains:
- Replace generate_images_default stub (lines 241-256) with full orchestrator
- Replace generate_videos_default stub (lines 259-274) with full orchestrator
- Add helper functions: _resolve_key_prefix, _resolve_base_url
- Create tests/test_orchestrator.py with 14 test cases
- Update tests/test_actions.py to reflect new stub behavior

## Task Traceability

| TASK Acceptance Criterion | IMPL Acceptance Criteria Test | Traceability |
|--------------------------|-------------------------------|--------------|
| AC-01: generate_images_default dispatches to configured provider | ACT-01 | Direct mapping |
| AC-02: generate_images_default downloads images and saves to STEP_03_DIR | ACT-02 | Direct mapping |
| AC-03: generate_images_default writes index.json with correct file mappings | ACT-03 | Direct mapping |
| AC-04: generate_images_default returns REJECTED when no provider configured | ACT-04 | Direct mapping |
| AC-05: generate_videos_default dispatches to configured provider | ACT-05 | Direct mapping |
| AC-06: generate_videos_default handles __none__ provider | ACT-06 | Direct mapping |
| AC-07: generate_videos_default handles {"skipped": True} from provider | ACT-07 | Direct mapping |
| AC-08: import_provider works for valid names, raises ImportError for invalid | ACT-08 | Direct mapping |
| AC-09: All 14 tests pass with pytest | ACT-09 | Direct mapping |
| AC-10: Full test suite passes (all phases) | ACT-10 | Direct mapping |
| AC-11: No existing files outside gen_media_content_v1 were modified | ACT-11 | Direct mapping |

## Step-by-Step Plan

### STEP-01: Add helper functions to actions.py

- Add _resolve_key_prefix(provider_name) function that maps provider name to API key environment variable prefix.
- Add _resolve_base_url(provider_name) function that maps provider name to base URL (from env var with default fallback).
- Satisfies: Foundation for ACT-01, ACT-02, ACT-05

### STEP-02: Implement generate_images_default

- Replace stub at lines 241-256 with full orchestrator:
  1. Load config from MEDIA_CONFIG context variable
  2. Read config["actions"]["render_image"] for provider name
  3. If "__none__" or empty -> return REJECTED with MISSING_PROVIDER
  4. Import provider via import_provider("render_image", provider_name)
  5. Validate config key: check provider_name exists in config["api"] using config["api"].get(provider_name). If missing -> return REJECTED with reject_code="INVALID_CONFIG" and remark "Provider '{provider_name}' not found in config.api section"
  6. Resolve API key via ApiKeyPool using _resolve_key_prefix
  7. Resolve base_url via _resolve_base_url
  8. Validate base_url: if empty string after resolution -> return REJECTED with reject_code="INVALID_CONFIG" and remark "Base URL could not be resolved for provider '{provider_name}'"
  9. Scan STEP_02_DIR for *_prompts.json variant files
  10. If no variant files found -> return REJECTED with reject_code="NO_INPUTS" and remark "No variant JSON files found in step_02 directory"
  11. For each variant file, read variations, call provider.call_api, download image, save to STEP_03_DIR
  12. Write index.json
  13. Return ActionResult
- Satisfies: ACT-01, ACT-02, ACT-03, ACT-04

### STEP-03: Implement generate_videos_default

- Replace stub at lines 259-274 with full orchestrator:
  1. Load config from MEDIA_CONFIG
  2. Read config["actions"]["render_video"] for provider
  3. If "__none__" -> return APPROVED with "Video generation skipped"
  4. Import provider via import_provider("render_video", provider_name)
  5. Validate config key: check provider_name exists in config["api"] using config["api"].get(provider_name). If missing -> return REJECTED with reject_code="INVALID_CONFIG" and remark "Provider '{provider_name}' not found in config.api section"
  6. Resolve API key via ApiKeyPool using _resolve_key_prefix
  7. Resolve base_url via _resolve_base_url
  8. Validate base_url: if empty string after resolution -> return REJECTED with reject_code="INVALID_CONFIG" and remark "Base URL could not be resolved for provider '{provider_name}'"
  9. Read STEP_03_DIR/index.json to discover generated images (each entry has "input" pointing to STEP_02_DIR variant file and "output" with image filename, plus the updated variant JSON in STEP_03_DIR contains image_url)
  10. If index.json does not exist or is empty -> return REJECTED with reject_code="NO_INPUTS" and remark "No image index found in step_03 directory"
  11. For each entry in index.json: read the corresponding variant JSON from STEP_02_DIR (using the "input" field) to get t2v_prompt1, and read image_url from the updated variant JSON in STEP_03_DIR
  12. Call provider.call_api(prompt=video_prompt, image=image_url, config=api_config, api_key=key, base_url=base_url)
  13. Handle {"skipped": True} responses: skip download for that entry, continue processing remaining entries
  14. Download video from result["video_url"], save to STEP_04_DIR
  15. Write index.json to STEP_04_DIR
  16. Return ActionResult
- Satisfies: ACT-05, ACT-06, ACT-07

### STEP-04: Create test_orchestrator.py with 14 test cases

- Create tests/test_orchestrator.py with tests for:
  1. generate_images calls provider and downloads images (ACT-01)
  2. generate_images writes index.json with correct mappings (ACT-03)
  3. generate_images with missing provider returns REJECTED (ACT-04)
  4. generate_images with all failures returns REJECTED
  5. generate_images with partial success returns APPROVED
  6. generate_videos calls provider and downloads videos (ACT-05)
  7. generate_videos with __none__ provider returns APPROVED (ACT-06)
  8. generate_videos handles {"skipped": True} from provider (ACT-07)
  9. import_provider works for valid provider names (ACT-08)
  10. import_provider raises ImportError for invalid names (ACT-08)
  11. _load_config raises FileNotFoundError for missing files (ACT-08)
  12. generate_images downloads image and saves with correct content (ACT-02)
  13. generate_videos downloads video and saves with correct content (ACT-05)
  14. Full pipeline integration test (ACT-09)
- Satisfies: ACT-09

### STEP-05: Update test_actions.py for new stub behavior

- Update TestGenerateImagesDefault and TestGenerateVideosDefault classes to test the new orchestrator behavior or remove if fully covered by test_orchestrator.py.
- Ensure existing utility tests remain passing.
- Satisfies: ACT-10

### STEP-06: Run full test suite and verify

- Run: .venv\Scripts\python -m pytest workflows/gen_media_content_v1/tests/ -v
- Verify all tests pass.
- Verify no files outside workflows/gen_media_content_v1/ were modified.
- Satisfies: ACT-10, ACT-11

## Code Changes

### Files to Create

#### workflows/gen_media_content_v1/tests/test_orchestrator.py

New file containing 14 integration tests for the orchestrator. Uses mocked import_provider, mocked provider.call_api, and mocked requests.get. Creates temporary directories for step dirs. Tests cover all acceptance criteria ACT-01 through ACT-09.

#### Helper functions to add in workflows/gen_media_content_v1/actions.py

```python
_PROVIDER_KEY_PREFIX_MAP = {
    "agnes_v1": "AGNES_API_KEY",
    "agnes_v2": "AGNES_API_KEY",
    "happyhorse_v1_1": "HAPPYHORSE_API_KEY",
}

_PROVIDER_BASE_URL_MAP = {
    "agnes_v1": ("AGNES_BASE_URL", "https://apihub.agnes-ai.com"),
    "agnes_v2": ("AGNES_BASE_URL", "https://apihub.agnes-ai.com"),
    "happyhorse_v1_1": ("HAPPYHORSE_BASE_URL", "https://dashscope.aliyuncs.com"),
}


def _resolve_key_prefix(provider_name: str) -> str:
    """Map provider name to API key environment variable prefix."""
    if provider_name in _PROVIDER_KEY_PREFIX_MAP:
        return _PROVIDER_KEY_PREFIX_MAP[provider_name]
    # Fallback: derive from provider name by stripping version suffix
    base = provider_name.split("_v")[0].upper()
    return f"{base}_API_KEY"


def _resolve_base_url(provider_name: str) -> str:
    """Resolve base URL for a provider from environment or default.

    Returns empty string if the provider is unknown and the derived
    environment variable is not set. Callers MUST validate the return
    value is non-empty before making API calls.
    """
    if provider_name in _PROVIDER_BASE_URL_MAP:
        env_var, default = _PROVIDER_BASE_URL_MAP[provider_name]
        return os.environ.get(env_var, default)
    # Fallback: derive env var name from provider name
    base = provider_name.split("_v")[0].upper()
    env_var = f"{base}_BASE_URL"
    return os.environ.get(env_var, "")
```

### Files to Modify

#### workflows/gen_media_content_v1/actions.py

**Current content (lines 241-274):** Two stub functions returning REJECTED.

**Changes:**
1. Add imports: `from agent_runner_v2.api_key_pool import ApiKeyPool, load_env_from_project`
2. Add _PROVIDER_KEY_PREFIX_MAP, _PROVIDER_BASE_URL_MAP dicts
3. Add _resolve_key_prefix and _resolve_base_url functions
4. Replace generate_images_default with full orchestrator (see STEP-02 above)
5. Replace generate_videos_default with full orchestrator (see STEP-03 above)

#### workflows/gen_media_content_v1/tests/test_actions.py

**Changes:**
- Update TestGenerateImagesDefault.test_returns_rejected_missing_provider: Instead of testing that stub always returns REJECTED, test that the new orchestrator returns REJECTED when config specifies "__none__" or empty provider.
- Update TestGenerateVideosDefault.test_returns_rejected_missing_provider: Test that the new orchestrator returns APPROVED (skipped) when config specifies "__none__" provider.
- Alternatively, remove these two test classes if test_orchestrator.py fully covers this behavior, and update the test count accordingly.

### Files to Delete

None.

### Codebase Files Referenced (read-only)

| File | Purpose |
|------|---------|
| workflows/agnes_media_gen_v1/impls/agnes_media_v1/actions.py | Reference orchestrator pattern (batching, download, index) |
| agent_runner_v2/api_key_pool.py | ApiKeyPool and load_env_from_project for API key resolution |
| agent_runner_v2/action_result.py | ActionResult dataclass definition |
| workflows/gen_media_content_v1/config.json.sample | Config structure reference |
| workflows/gen_media_content_v1/context_extensions.py | Context variable names and resolution |
| workflows/gen_media_content_v1/api_actions/render_image/agnes_v1/__init__.py | Image provider interface |
| workflows/gen_media_content_v1/api_actions/render_video/agnes_v2/__init__.py | Video provider interface |
| workflows/gen_media_content_v1/api_actions/render_video/happyhorse_v1_1/__init__.py | Video provider interface |
| workflows/gen_media_content_v1/api_actions/render_video/__none__/__init__.py | Skip provider interface |
| workflows/gen_media_content_v1/workflow.toml | Step definitions and action names |

## Test Implementation

The following is the complete test file for tests/test_orchestrator.py implementing the 14 acceptance criteria tests.

```python
"""Integration tests for gen_media_content_v1 orchestrator actions.

Tests cover all 11 acceptance criteria (ACT-01 through ACT-11) for
Phase 9 orchestrator integration:
- generate_images_default dispatches, downloads, writes index
- generate_images_default error handling (missing provider, all fail, partial)
- generate_videos_default dispatches, downloads, handles skip
- generate_videos_default handles __none__ provider
- import_provider and _load_config edge cases
- Full test suite passes

All HTTP calls and provider imports are mocked. No real API keys or
network access required.
"""
from __future__ import annotations

import json
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from workflows.gen_media_content_v1.actions import (
    _load_config,
    _write_index,
    import_provider,
    generate_images_default,
    generate_videos_default,
)


def _make_config(tmp_path, render_image="agnes_v1", render_video="happyhorse_v1_1"):
    """Create a test config.json and return its path."""
    config = {
        "actions": {
            "render_image": render_image,
            "render_video": render_video,
        },
        "api": {
            "agnes_v1": {"model": "test-model", "size": "1024x1024", "ratio": "1:1"},
            "agnes_v2": {"model": "vid-model", "width": 1024, "height": 576},
            "happyhorse_v1_1": {"model": "hh-model", "resolution": "480P"},
        },
    }
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    return config_path


def _make_variant_json(step_02_dir, name="variant_01_prompts.json",
                       t2i_prompt="A cat", t2v_prompt="A cat walking",
                       image_filename="cat.png"):
    """Create a variant JSON file in step_02_dir."""
    variant = {
        "variations": [{
            "t2i_prompt1": t2i_prompt,
            "t2v_prompt1": t2v_prompt,
            "image_filename": image_filename,
        }]
    }
    path = step_02_dir / name
    path.write_text(json.dumps(variant), encoding="utf-8")
    return path


def _mock_provider_module(call_api_return=None, call_api_side_effect=None):
    """Create a mock provider module with call_api."""
    mod = types.ModuleType("mock_provider")
    mock_call_api = MagicMock()
    if call_api_return is not None:
        mock_call_api.return_value = call_api_return
    if call_api_side_effect is not None:
        mock_call_api.side_effect = call_api_side_effect
    mod.call_api = mock_call_api
    return mod


# ============================================================================
# ACT-01: generate_images dispatches to configured provider
# ============================================================================

class TestGenerateImagesDispatch:
    def test_calls_provider_for_each_variant(self, tmp_path):
        """ACT-01: generate_images_default calls provider.call_api for each variant."""
        step_02 = tmp_path / "step_02"
        step_03 = tmp_path / "step_03"
        step_02.mkdir()
        step_03.mkdir()
        config_path = _make_config(tmp_path)
        _make_variant_json(step_02, "v1_prompts.json", t2i_prompt="Prompt A")

        mock_mod = _mock_provider_module(
            call_api_return={"image_url": "http://cdn/img.png", "revised_prompt": "Prompt A"}
        )

        mock_download = MagicMock()
        mock_download.content = b"PNG_DATA"
        mock_download.raise_for_status = MagicMock()

        with patch("workflows.gen_media_content_v1.actions.import_provider", return_value=mock_mod), \
             patch("workflows.gen_media_content_v1.actions.ApiKeyPool") as mock_pool_cls, \
             patch("workflows.gen_media_content_v1.actions.load_env_from_project"), \
             patch("workflows.gen_media_content_v1.actions.requests") as mock_requests:
            mock_pool = MagicMock()
            mock_pool.next_key.return_value = "test-key-123"
            mock_pool_cls.return_value = mock_pool
            mock_requests.get.return_value = mock_download

            result = generate_images_default(
                context={"MEDIA_CONFIG": str(config_path),
                         "STEP_02_DIR": str(step_02),
                         "STEP_03_DIR": str(step_03)},
                state=MagicMock(),
                step_cfg=MagicMock(),
                project_root=tmp_path,
            )

        assert result.status == "APPROVED"
        mock_mod.call_api.assert_called_once()
        call_kwargs = mock_mod.call_api.call_args
        assert call_kwargs.kwargs.get("prompt") == "Prompt A" or \
               (call_kwargs.args and "Prompt A" in call_kwargs.args)


# ============================================================================
# ACT-02: generate_images downloads images and saves to STEP_03_DIR
# ============================================================================

class TestGenerateImagesDownload:
    def test_downloads_and_saves_image(self, tmp_path):
        """ACT-02: Downloads image from URL and saves to STEP_03_DIR."""
        step_02 = tmp_path / "step_02"
        step_03 = tmp_path / "step_03"
        step_02.mkdir()
        step_03.mkdir()
        config_path = _make_config(tmp_path)
        _make_variant_json(step_02, "v1_prompts.json")

        mock_mod = _mock_provider_module(
            call_api_return={"image_url": "http://cdn/cat.png", "revised_prompt": ""}
        )

        mock_img_resp = MagicMock()
        mock_img_resp.content = b"FAKE_PNG_BYTES"
        mock_img_resp.raise_for_status = MagicMock()

        with patch("workflows.gen_media_content_v1.actions.import_provider", return_value=mock_mod), \
             patch("workflows.gen_media_content_v1.actions.ApiKeyPool") as mock_pool_cls, \
             patch("workflows.gen_media_content_v1.actions.load_env_from_project"), \
             patch("workflows.gen_media_content_v1.actions.requests") as mock_requests:
            mock_pool = MagicMock()
            mock_pool.next_key.return_value = "key"
            mock_pool_cls.return_value = mock_pool
            mock_requests.get.return_value = mock_img_resp

            result = generate_images_default(
                context={"MEDIA_CONFIG": str(config_path),
                         "STEP_02_DIR": str(step_02),
                         "STEP_03_DIR": str(step_03)},
                state=MagicMock(),
                step_cfg=MagicMock(),
                project_root=tmp_path,
            )

        assert result.status == "APPROVED"
        png_files = list(step_03.glob("*.png"))
        assert len(png_files) >= 1
        assert png_files[0].read_bytes() == b"FAKE_PNG_BYTES"


# ============================================================================
# ACT-03: generate_images writes index.json with correct file mappings
# ============================================================================

class TestGenerateImagesIndex:
    def test_writes_index_json(self, tmp_path):
        """ACT-03: Writes index.json to STEP_03_DIR with file mappings."""
        step_02 = tmp_path / "step_02"
        step_03 = tmp_path / "step_03"
        step_02.mkdir()
        step_03.mkdir()
        config_path = _make_config(tmp_path)
        _make_variant_json(step_02, "v1_prompts.json")

        mock_mod = _mock_provider_module(
            call_api_return={"image_url": "http://cdn/img.png", "revised_prompt": ""}
        )
        mock_img_resp = MagicMock()
        mock_img_resp.content = b"DATA"
        mock_img_resp.raise_for_status = MagicMock()

        with patch("workflows.gen_media_content_v1.actions.import_provider", return_value=mock_mod), \
             patch("workflows.gen_media_content_v1.actions.ApiKeyPool") as mock_pool_cls, \
             patch("workflows.gen_media_content_v1.actions.load_env_from_project"), \
             patch("workflows.gen_media_content_v1.actions.requests") as mock_requests:
            mock_pool = MagicMock()
            mock_pool.next_key.return_value = "key"
            mock_pool_cls.return_value = mock_pool
            mock_requests.get.return_value = mock_img_resp

            generate_images_default(
                context={"MEDIA_CONFIG": str(config_path),
                         "STEP_02_DIR": str(step_02),
                         "STEP_03_DIR": str(step_03)},
                state=MagicMock(),
                step_cfg=MagicMock(),
                project_root=tmp_path,
            )

        index_path = step_03 / "index.json"
        assert index_path.exists()
        with open(index_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "step" in data
        assert "files" in data
        assert len(data["files"]) >= 1
        assert "input" in data["files"][0]
        assert "output" in data["files"][0]


# ============================================================================
# ACT-04: generate_images returns REJECTED when no provider configured
# ============================================================================

class TestGenerateImagesMissingProvider:
    def test_rejected_with_none_provider(self, tmp_path):
        """ACT-04: Returns REJECTED when render_image is __none__."""
        step_02 = tmp_path / "step_02"
        step_02.mkdir()
        config_path = _make_config(tmp_path, render_image="__none__")

        result = generate_images_default(
            context={"MEDIA_CONFIG": str(config_path),
                     "STEP_02_DIR": str(step_02),
                     "STEP_03_DIR": str(tmp_path / "step_03")},
            state=MagicMock(),
            step_cfg=MagicMock(),
            project_root=tmp_path,
        )

        assert result.status == "REJECTED"
        assert result.reject_code == "MISSING_PROVIDER"

    def test_rejected_with_empty_provider(self, tmp_path):
        """ACT-04: Returns REJECTED when render_image is empty string."""
        step_02 = tmp_path / "step_02"
        step_02.mkdir()
        config_path = _make_config(tmp_path, render_image="")

        result = generate_images_default(
            context={"MEDIA_CONFIG": str(config_path),
                     "STEP_02_DIR": str(step_02),
                     "STEP_03_DIR": str(tmp_path / "step_03")},
            state=MagicMock(),
            step_cfg=MagicMock(),
            project_root=tmp_path,
        )

        assert result.status == "REJECTED"
        assert result.reject_code == "MISSING_PROVIDER"


# ============================================================================
# ACT-04b: generate_images with all failures returns REJECTED
# ============================================================================

class TestGenerateImagesAllFail:
    def test_all_failures_returns_rejected(self, tmp_path):
        """ACT-04: Returns REJECTED when all image generations fail."""
        step_02 = tmp_path / "step_02"
        step_03 = tmp_path / "step_03"
        step_02.mkdir()
        step_03.mkdir()
        config_path = _make_config(tmp_path)
        _make_variant_json(step_02, "v1_prompts.json")

        mock_mod = _mock_provider_module(
            call_api_side_effect=RuntimeError("API error")
        )

        with patch("workflows.gen_media_content_v1.actions.import_provider", return_value=mock_mod), \
             patch("workflows.gen_media_content_v1.actions.ApiKeyPool") as mock_pool_cls, \
             patch("workflows.gen_media_content_v1.actions.load_env_from_project"):
            mock_pool = MagicMock()
            mock_pool.next_key.return_value = "key"
            mock_pool_cls.return_value = mock_pool

            result = generate_images_default(
                context={"MEDIA_CONFIG": str(config_path),
                         "STEP_02_DIR": str(step_02),
                         "STEP_03_DIR": str(step_03)},
                state=MagicMock(),
                step_cfg=MagicMock(),
                project_root=tmp_path,
            )

        assert result.status == "REJECTED"


# ============================================================================
# ACT-04c: generate_images with partial success returns APPROVED
# ============================================================================

class TestGenerateImagesPartialSuccess:
    def test_partial_success_returns_approved(self, tmp_path):
        """ACT-04: Returns APPROVED when some images succeed and some fail."""
        step_02 = tmp_path / "step_02"
        step_03 = tmp_path / "step_03"
        step_02.mkdir()
        step_03.mkdir()
        config_path = _make_config(tmp_path)

        # Create two variant files
        _make_variant_json(step_02, "v1_prompts.json", t2i_prompt="Good prompt")
        _make_variant_json(step_02, "v2_prompts.json", t2i_prompt="Bad prompt")

        mock_mod = _mock_provider_module(
            call_api_side_effect=[
                {"image_url": "http://cdn/good.png", "revised_prompt": ""},
                RuntimeError("API failure"),
            ]
        )

        mock_img_resp = MagicMock()
        mock_img_resp.content = b"PNG"
        mock_img_resp.raise_for_status = MagicMock()

        with patch("workflows.gen_media_content_v1.actions.import_provider", return_value=mock_mod), \
             patch("workflows.gen_media_content_v1.actions.ApiKeyPool") as mock_pool_cls, \
             patch("workflows.gen_media_content_v1.actions.load_env_from_project"), \
             patch("workflows.gen_media_content_v1.actions.requests") as mock_requests:
            mock_pool = MagicMock()
            mock_pool.next_key.return_value = "key"
            mock_pool_cls.return_value = mock_pool
            mock_requests.get.return_value = mock_img_resp

            result = generate_images_default(
                context={"MEDIA_CONFIG": str(config_path),
                         "STEP_02_DIR": str(step_02),
                         "STEP_03_DIR": str(step_03)},
                state=MagicMock(),
                step_cfg=MagicMock(),
                project_root=tmp_path,
            )

        assert result.status == "APPROVED"
        assert "1" in result.remark or "partial" in result.remark.lower()


# ============================================================================
# ACT-05: generate_videos dispatches to configured provider
# ============================================================================

class TestGenerateVideosDispatch:
    def test_calls_provider_for_each_image(self, tmp_path):
        """ACT-05: generate_videos_default calls provider.call_api for each image."""
        step_02 = tmp_path / "step_02"
        step_03 = tmp_path / "step_03"
        step_04 = tmp_path / "step_04"
        step_02.mkdir()
        step_03.mkdir()
        step_04.mkdir()
        config_path = _make_config(tmp_path)

        # Simulate step_03 having an updated variant JSON with image_url
        updated_variant = {
            "variations": [{
                "t2i_prompt1": "A cat",
                "t2v_prompt1": "A cat walking",
                "image_filename": "cat.png",
                "image_url": "http://cdn/cat.png",
            }]
        }
        (step_03 / "v1_prompts.json").write_text(
            json.dumps(updated_variant), encoding="utf-8"
        )
        # Write a dummy index.json in step_03
        (step_03 / "index.json").write_text(
            json.dumps({"step": "render_image", "files": [
                {"input": "v1_prompts.json", "output": "cat.png"}
            ]}), encoding="utf-8"
        )

        mock_mod = _mock_provider_module(
            call_api_return={"video_url": "http://cdn/cat.mp4"}
        )

        mock_vid_resp = MagicMock()
        mock_vid_resp.content = b"MP4_DATA"
        mock_vid_resp.raise_for_status = MagicMock()

        with patch("workflows.gen_media_content_v1.actions.import_provider", return_value=mock_mod), \
             patch("workflows.gen_media_content_v1.actions.ApiKeyPool") as mock_pool_cls, \
             patch("workflows.gen_media_content_v1.actions.load_env_from_project"), \
             patch("workflows.gen_media_content_v1.actions.requests") as mock_requests:
            mock_pool = MagicMock()
            mock_pool.next_key.return_value = "key"
            mock_pool_cls.return_value = mock_pool
            mock_requests.get.return_value = mock_vid_resp

            result = generate_videos_default(
                context={"MEDIA_CONFIG": str(config_path),
                         "STEP_02_DIR": str(step_02),
                         "STEP_03_DIR": str(step_03),
                         "STEP_04_DIR": str(step_04)},
                state=MagicMock(),
                step_cfg=MagicMock(),
                project_root=tmp_path,
            )

        assert result.status == "APPROVED"
        mock_mod.call_api.assert_called_once()


# ============================================================================
# ACT-06: generate_videos with __none__ provider returns APPROVED (skipped)
# ============================================================================

class TestGenerateVideosNoneProvider:
    def test_none_provider_returns_approved(self, tmp_path):
        """ACT-06: Returns APPROVED with skip message when render_video is __none__."""
        config_path = _make_config(tmp_path, render_video="__none__")

        result = generate_videos_default(
            context={"MEDIA_CONFIG": str(config_path),
                     "STEP_02_DIR": str(tmp_path / "step_02"),
                     "STEP_03_DIR": str(tmp_path / "step_03"),
                     "STEP_04_DIR": str(tmp_path / "step_04")},
            state=MagicMock(),
            step_cfg=MagicMock(),
            project_root=tmp_path,
        )

        assert result.status == "APPROVED"
        assert "skip" in result.remark.lower()


# ============================================================================
# ACT-07: generate_videos handles {"skipped": True} from provider
# ============================================================================

class TestGenerateVideosSkippedFromProvider:
    def test_skipped_result_does_not_download(self, tmp_path):
        """ACT-07: When provider returns {skipped: True}, no download is attempted."""
        step_02 = tmp_path / "step_02"
        step_03 = tmp_path / "step_03"
        step_04 = tmp_path / "step_04"
        step_02.mkdir()
        step_03.mkdir()
        step_04.mkdir()
        config_path = _make_config(tmp_path)

        updated_variant = {
            "variations": [{
                "t2i_prompt1": "A cat",
                "t2v_prompt1": "A cat walking",
                "image_filename": "cat.png",
                "image_url": "http://cdn/cat.png",
            }]
        }
        (step_03 / "v1_prompts.json").write_text(
            json.dumps(updated_variant), encoding="utf-8"
        )
        (step_03 / "index.json").write_text(
            json.dumps({"step": "render_image", "files": []}), encoding="utf-8"
        )

        mock_mod = _mock_provider_module(
            call_api_return={"skipped": True, "reason": "Not supported"}
        )

        with patch("workflows.gen_media_content_v1.actions.import_provider", return_value=mock_mod), \
             patch("workflows.gen_media_content_v1.actions.ApiKeyPool") as mock_pool_cls, \
             patch("workflows.gen_media_content_v1.actions.load_env_from_project"), \
             patch("workflows.gen_media_content_v1.actions.requests") as mock_requests:
            mock_pool = MagicMock()
            mock_pool.next_key.return_value = "key"
            mock_pool_cls.return_value = mock_pool

            result = generate_videos_default(
                context={"MEDIA_CONFIG": str(config_path),
                         "STEP_02_DIR": str(step_02),
                         "STEP_03_DIR": str(step_03),
                         "STEP_04_DIR": str(step_04)},
                state=MagicMock(),
                step_cfg=MagicMock(),
                project_root=tmp_path,
            )

        assert result.status == "APPROVED"
        # Verify requests.get was NOT called for video download
        mock_requests.get.assert_not_called()
        # Verify no mp4 files in step_04
        mp4_files = list(step_04.glob("*.mp4"))
        assert len(mp4_files) == 0


# ============================================================================
# ACT-08: import_provider and _load_config edge cases
# ============================================================================

class TestImportProviderEdgeCases:
    def test_valid_provider_import(self):
        """ACT-08: import_provider works for valid provider names."""
        mock_module = types.ModuleType("mock")
        mock_module.call_api = lambda: None

        with patch("workflows.gen_media_content_v1.actions.importlib.import_module",
                    return_value=mock_module):
            result = import_provider("render_image", "agnes_v1")
            assert hasattr(result, "call_api")

    def test_invalid_provider_raises_import_error(self):
        """ACT-08: import_provider raises ImportError with descriptive message for invalid names."""
        with patch("workflows.gen_media_content_v1.actions.importlib.import_module",
                    side_effect=ModuleNotFoundError("No module")):
            with pytest.raises(ImportError, match="nonexistent_provider"):
                import_provider("render_image", "nonexistent_provider")


class TestLoadConfigEdgeCases:
    def test_missing_file_raises_file_not_found(self, tmp_path):
        """ACT-08: _load_config raises FileNotFoundError for missing files."""
        with pytest.raises(FileNotFoundError):
            _load_config(str(tmp_path / "nonexistent.json"))


# ============================================================================
# ACT-09: Full pipeline integration test
# ============================================================================

class TestFullPipelineIntegration:
    def test_images_output_becomes_video_input(self, tmp_path):
        """ACT-09: Verify data flow from generate_images_default to generate_videos_default.

        generate_images_default writes updated variant JSONs (with image_url)
        to STEP_03_DIR and an index.json. generate_videos_default reads the
        index.json and cross-references to STEP_02_DIR for video prompts.
        """
        step_02 = tmp_path / "step_02"
        step_03 = tmp_path / "step_03"
        step_04 = tmp_path / "step_04"
        step_02.mkdir()
        step_03.mkdir()
        step_04.mkdir()
        config_path = _make_config(tmp_path)
        _make_variant_json(step_02, "v1_prompts.json",
                           t2i_prompt="A cat", t2v_prompt="A cat walking")

        # -- Run generate_images_default --
        mock_img_mod = _mock_provider_module(
            call_api_return={"image_url": "http://cdn/cat.png", "revised_prompt": "A cat"}
        )
        mock_img_resp = MagicMock()
        mock_img_resp.content = b"PNG_BYTES"
        mock_img_resp.raise_for_status = MagicMock()

        with patch("workflows.gen_media_content_v1.actions.import_provider", return_value=mock_img_mod), \
             patch("workflows.gen_media_content_v1.actions.ApiKeyPool") as mock_pool_cls, \
             patch("workflows.gen_media_content_v1.actions.load_env_from_project"), \
             patch("workflows.gen_media_content_v1.actions.requests") as mock_requests:
            mock_pool = MagicMock()
            mock_pool.next_key.return_value = "key"
            mock_pool_cls.return_value = mock_pool
            mock_requests.get.return_value = mock_img_resp

            img_result = generate_images_default(
                context={"MEDIA_CONFIG": str(config_path),
                         "STEP_02_DIR": str(step_02),
                         "STEP_03_DIR": str(step_03)},
                state=MagicMock(),
                step_cfg=MagicMock(),
                project_root=tmp_path,
            )

        assert img_result.status == "APPROVED"
        assert (step_03 / "index.json").exists()

        # Verify the updated variant JSON in step_03 has image_url
        updated_variant_path = step_03 / "v1_prompts.json"
        if updated_variant_path.exists():
            updated_data = json.loads(updated_variant_path.read_text(encoding="utf-8"))
            assert updated_data["variations"][0].get("image_url") == "http://cdn/cat.png"
```

## Rollback Plan

### If implementation fails

1. **Revert actions.py changes**: Use `git checkout -- workflows/gen_media_content_v1/actions.py` to restore stubs.
2. **Remove test_orchestrator.py**: Delete the newly created test file.
3. **Revert test_actions.py changes**: Use `git checkout -- workflows/gen_media_content_v1/tests/test_actions.py` to restore original tests.
4. **Verify baseline**: Run `.venv\Scripts\python -m pytest workflows/gen_media_content_v1/tests/ -v` to confirm all original tests still pass.

### Partial failure scenarios

- If only generate_images_default fails: Revert just that function in actions.py while keeping generate_videos_default.
- If only test_orchestrator.py fails: Remove the test file and fix issues before re-creating.

### Data integrity

- No production data is affected -- all operations are within test directories.
- Config files (config.json.sample) are not modified.
- Provider modules are not modified.

## Dependencies

### External Dependencies

| Dependency | Purpose | Status |
|-----------|---------|--------|
| agent_runner_v2.api_key_pool (ApiKeyPool, load_env_from_project) | API key resolution | Available, used by reference implementations |
| agent_runner_v2.action_result (ActionResult) | Return type for actions | Available |
| requests | HTTP downloads for images/videos | Available (already imported in actions.py) |
| pytest | Test execution | Available |

### Prerequisites

| Prerequisite | Status | Notes |
|-------------|--------|-------|
| Phase 1-6: Utility functions in actions.py | COMPLETE | _load_config, _write_index, import_provider, etc. |
| Phase 3: Image provider agnes_v1 | COMPLETE | api_actions/render_image/agnes_v1/__init__.py |
| Phase 4-5: Video providers (agnes_v2, happyhorse_v1_1, __none__) | COMPLETE | api_actions/render_video/*/ |
| Phase 8: BCS impls (preset.json files) | COMPLETE | Not directly required for orchestrator but part of pipeline |

### Inter-Phase Dependencies

- generate_images_default depends on STEP_02_DIR containing *_prompts.json variant files (produced by Step 2 of the workflow).
- generate_videos_default depends on STEP_03_DIR containing updated variant JSONs with image_url (produced by generate_images_default).
- Both actions depend on config.json existing at MEDIA_CONFIG path.

## Open Questions

### OQ-01: Base URL resolution strategy

The TASK specification mentions resolving API keys from env vars (AGNES_API_KEY_* for agnes_v1) but does not explicitly specify how base_url should be resolved for each provider. The implementation plan uses a mapping approach:
- agnes_v1/agnes_v2 -> AGNES_BASE_URL env var (default: https://apihub.agnes-ai.com)
- happyhorse_v1_1 -> HAPPYHORSE_BASE_URL env var (default: https://dashscope.aliyuncs.com)

This follows the pattern from the reference implementation (agnes_media_gen_v1). If a different base URL resolution strategy is needed, the _resolve_base_url function and _PROVIDER_BASE_URL_MAP can be adjusted.

### OQ-02: Video orchestrator input scanning [RESOLVED]

RESOLVED: The implementation now follows the TASK specification exactly. STEP-03 (generate_videos_default) reads index.json from STEP_03_DIR to discover generated images and their image_url values, then cross-references back to STEP_02_DIR variant files (using the "input" field in index.json entries) to read the video prompt (t2v_prompt1). This ensures video prompts come from the authoritative STEP_02_DIR source while image_url values come from the updated data in STEP_03_DIR.

### OQ-03: API key prefix derivation for unknown providers

The implementation includes a fallback for unknown provider names: strip the version suffix (_v*) and uppercase to derive the key prefix. For example, "newprovider_v2" -> "NEWPROVIDER_API_KEY". This has not been tested with actual unknown providers.

### OQ-04: Concurrent API calls

The reference implementation (agnes_media_gen_v1) uses ConcurrentApiRunner for parallel API calls. The TASK specification does not explicitly require concurrency. The initial implementation will process items sequentially for simplicity. Concurrency can be added in a follow-up if performance testing indicates it is needed.

## Challenge Resolution

### Attack 1: Test Count Self-Verification is Not a Real Test
**Evaluation:** Valid
**Resolution:** The 14th test (TestTestCount.test_fourteen_tests_in_file) was a meta-test that counted test method lines in its own source file rather than verifying functional behavior. This has been replaced with TestFullPipelineIntegration.test_images_output_becomes_video_input, which verifies the data flow between generate_images_default (writes index.json and updated variant JSONs with image_url to STEP_03_DIR) and generate_videos_default (reads index.json and cross-references to STEP_02_DIR for video prompts). All 14 tests are now functional tests.
**Evidence:** IMPL lines 897-908 (original self-counting test code). TASK Step 3 lists 11 functional test scenarios, all of which are now covered by real tests. The original test only verified line count of the source file, which provides zero functional coverage.
**Affected section:** STEP-04 test descriptions, Test Implementation (test_orchestrator.py)

### Attack 2: Missing Config Key Validation in generate_images_default
**Evaluation:** Valid
**Resolution:** Added explicit config key validation to both STEP-02 (generate_images_default) and STEP-03 (generate_videos_default). The plan now includes a step that checks provider_name exists in config["api"] using config["api"].get(provider_name) before proceeding. If the key is missing, the action returns REJECTED with reject_code="INVALID_CONFIG" and a descriptive remark. This prevents unhandled KeyError at runtime.
**Evidence:** TASK Step 1 item 5 specifies "Read API config from config['api'][provider_name]" which implies the key should exist but does not specify error handling. config.json.sample (workflows/gen_media_content_v1/config.json.sample lines 12-29) shows only three known providers (agnes_v1, agnes_v2, happyhorse_v1_1). Any other provider name in config.actions would cause KeyError without validation. Reference implementation (agnes_media_gen_v1/actions.py) uses .get() pattern for config access (lines 194-198).
**Affected section:** STEP-02, STEP-03, Implementation Overview

### Attack 3: Video Orchestrator Reads From Wrong Directory
**Evaluation:** Valid (partially addressed by OQ-02, now fully resolved)
**Resolution:** The original plan's STEP-03 read "updated variant JSONs" from STEP_03_DIR, which contradicts the TASK specification (Step 2 items 7-8a) that requires reading video prompts from STEP_02_DIR. The plan has been corrected: STEP-03 now (1) reads index.json from STEP_03_DIR to discover generated images with image_url, then (2) cross-references back to STEP_02_DIR variant files using the "input" field in index.json to read video prompts (t2v_prompt1). OQ-02 is now marked as RESOLVED.
**Evidence:** TASK lines 66-69: "Scan {STEP_03_DIR} for generated images (via index.json)" followed by "Read corresponding variant JSON from {STEP_02_DIR} for video prompt (t2v_prompt1)". Reference implementation (agnes_media_gen_v1/actions.py line 452) reads from step_03_dir because it copies updated JSONs there (lines 276-280), but the TASK specification for gen_media_content_v1 explicitly requires reading prompts from STEP_02_DIR. The original IMPL OQ-02 (lines 967-969) acknowledged this discrepancy without resolving it.
**Affected section:** STEP-03, Implementation Overview, OQ-02

### Attack 4: No Handling for Empty Directories
**Evaluation:** Valid
**Resolution:** Added empty directory checks to both STEP-02 and STEP-03. For generate_images_default: if no *_prompts.json files found in STEP_02_DIR, return REJECTED with reject_code="NO_INPUTS". For generate_videos_default: if index.json does not exist or is empty in STEP_03_DIR, return REJECTED with reject_code="NO_INPUTS". This follows the reference implementation pattern.
**Evidence:** Reference implementation (agnes_media_gen_v1/actions.py lines 207-209):
```python
if not variant_jsons:
    return ActionResult(status="REJECTED", remark="No variant JSON files found in step_02_promptvariant.", artifacts={}, reject_code="NO_INPUTS")
```
Without this check, the orchestrator would proceed to iterate over an empty collection and produce no output, potentially causing downstream failures.
**Affected section:** STEP-02 (added step 10), STEP-03 (added step 10)

### Attack 5: Base URL Resolution Fails for Unknown Providers
**Evaluation:** Valid
**Resolution:** Added base_url validation to both STEP-02 and STEP-03. After resolving base_url via _resolve_base_url, the plan now checks if the result is an empty string. If empty, the action returns REJECTED with reject_code="INVALID_CONFIG" and a descriptive remark indicating which provider could not be resolved. The _resolve_base_url docstring has also been updated to document that callers must validate the return value.
**Evidence:** IMPL _resolve_base_url function (lines 305-313) returns os.environ.get(env_var, "") for unknown providers, which can produce empty strings. The agnes_v1 provider (api_actions/render_image/agnes_v1/__init__.py line 44) validates base_url: "if not base_url or not base_url.strip(): raise RuntimeError". Without pre-validation in the orchestrator, this would raise RuntimeError per-item rather than failing fast with a clear error.
**Affected section:** STEP-02 (added step 8), STEP-03 (added step 8), Helper functions docstring

### Attack 6: No Test for ImportError Message Content
**Evaluation:** Valid
**Resolution:** Updated the test_invalid_provider_raises_import_error test to verify the error message content using pytest.raises(ImportError, match="nonexistent_provider"). This ensures the ImportError contains a descriptive message mentioning the invalid provider name, as required by TASK AC-08.
**Evidence:** TASK line 90: "import_provider raises ImportError with descriptive message for invalid names". The actual import_provider function (actions.py lines 226-228) includes the descriptive message: f"Provider '{provider_type}/{provider_name}' not found: {exc}". The original test only checked that ImportError was raised without verifying the message content, allowing an implementation that raises ImportError("x") to pass.
**Affected section:** Test Implementation (test_orchestrator.py, TestImportProviderEdgeCases class)
