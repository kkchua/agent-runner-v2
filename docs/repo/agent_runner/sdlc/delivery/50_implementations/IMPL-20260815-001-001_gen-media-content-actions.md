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
effective_version: "SDLC50IMP-gzafrx8k"
managed_by: "workflow-generated"
---

# Implementation Plan: gen_media_content_v1 Phase 2 - Root Actions and Shared Utilities

## Document Metadata

- Document ID: IMPL-20260815-001-001
- Source task: TASK-20260814-001-02
- Date of generation: 2026-08-15
- Producing workflow: sdlc_50_implementation_v1
- Producing agent: qwen3.7-plus

## 1. Acceptance Criteria Tests

The following testable acceptance criteria are derived from TASK-20260814-001-02. Each criterion is assigned a Test ID and describes what "done" means before implementation design.

### ACT-01: Module Existence and Validity

- **Test ID**: ACT-01
- **Test Description**: actions.py exists and is valid Python with no syntax errors.
- **Verification Method**: Run `python -c "import ast; ast.parse(open('workflows/gen_media_content_v1/actions.py').read())"` and verify exit code 0.
- **Expected Result**: File parses without SyntaxError.
- **Current State**: MISSING (file does not exist on disk).

### ACT-02: Utility Function Importability

- **Test ID**: ACT-02
- **Test Description**: All 5 utility functions are importable from the module.
- **Verification Method**: Run `python -c "from workflows.gen_media_content_v1.actions import _load_config, _api_request_with_retry, _write_index, _get_next_sequence_filename, import_provider"` and verify exit code 0.
- **Expected Result**: All 5 names resolve without ImportError.
- **Current State**: MISSING (module does not exist).

### ACT-03: Config Loading

- **Test ID**: ACT-03
- **Test Description**: _load_config correctly parses config.json.sample and raises FileNotFoundError for missing files.
- **Verification Method**: Unit test: (a) call _load_config with path to config.json.sample and verify dict returned with expected keys; (b) call _load_config with nonexistent path and verify FileNotFoundError.
- **Expected Result**: Valid config dict parsed; FileNotFoundError raised for missing path.
- **Current State**: MISSING (function not implemented).

### ACT-04: API Retry Logic

- **Test ID**: ACT-04
- **Test Description**: _api_request_with_retry retries on 503/429, uses exponential backoff, raises RuntimeError after max retries, and forwards the timeout parameter to the underlying HTTP client.
- **Verification Method**: Unit tests with mocked requests: (a) mock 503 response then 200 response, verify success after retry; (b) mock 429 response then 200, verify success; (c) mock all 503 responses for max_retries+1 calls, verify RuntimeError raised; (d) mock timeout, verify retry and eventual RuntimeError; (e) verify timeout parameter is forwarded to requests.get/post call kwargs.
- **Expected Result**: Retries on 503/429, exponential backoff confirmed, RuntimeError after exhaustion, timeout parameter forwarded.
- **Current State**: MISSING (function not implemented).

### ACT-05: Index File Writing

- **Test ID**: ACT-05
- **Test Description**: _write_index produces valid JSON with {"step": ..., "files": ...} structure and creates parent directories.
- **Verification Method**: Unit test: (a) call _write_index to a temp path, read back JSON, verify structure; (b) use nested path with nonexistent parent, verify parent dirs created.
- **Expected Result**: Valid JSON output; parent directories created automatically.
- **Current State**: MISSING (function not implemented).

### ACT-06: Filename Sequencing

- **Test ID**: ACT-06
- **Test Description**: _get_next_sequence_filename returns base.ext, base_001.ext, base_002.ext in sequence.
- **Verification Method**: Unit test in temp directory: (a) call with empty dir, verify "base.ext"; (b) create "base.ext", call again, verify "base_001.ext"; (c) also create "base_001.ext", call again, verify "base_002.ext".
- **Expected Result**: Correct sequence progression.
- **Current State**: MISSING (function not implemented).

### ACT-07: Dynamic Provider Import

- **Test ID**: ACT-07
- **Test Description**: import_provider dynamically imports from api_actions/{provider_type}/{provider_name}/ and validates call_api exists.
- **Verification Method**: Unit tests: (a) create a mock provider module with call_api in a temp structure, verify import succeeds and module has call_api; (b) attempt import of nonexistent provider, verify ImportError; (c) attempt import of module without call_api, verify ImportError.
- **Expected Result**: Dynamic import works; proper errors for missing module or missing call_api.
- **Current State**: MISSING (function not implemented).

### ACT-08: Image Generation Default Stub

- **Test ID**: ACT-08
- **Test Description**: generate_images_default returns ActionResult with status="REJECTED" and reject_code="MISSING_PROVIDER".
- **Verification Method**: Unit test: call generate_images_default with mock kwargs, verify ActionResult.status == "REJECTED" and ActionResult.reject_code == "MISSING_PROVIDER".
- **Expected Result**: REJECTED status with MISSING_PROVIDER code.
- **Current State**: MISSING (stub not implemented).

### ACT-09: Video Generation Default Stub

- **Test ID**: ACT-09
- **Test Description**: generate_videos_default returns ActionResult with status="REJECTED" and reject_code="MISSING_PROVIDER".
- **Verification Method**: Unit test: call generate_videos_default with mock kwargs, verify ActionResult.status == "REJECTED" and ActionResult.reject_code == "MISSING_PROVIDER".
- **Expected Result**: REJECTED status with MISSING_PROVIDER code.
- **Current State**: MISSING (stub not implemented).

### ACT-10: All Tests Pass

- **Test ID**: ACT-10
- **Test Description**: All tests pass with pytest.
- **Verification Method**: Run `.venv\Scripts\python -m pytest workflows/gen_media_content_v1/tests/test_actions.py -v` and verify exit code 0.
- **Expected Result**: All tests pass, zero failures.
- **Current State**: MISSING (test file does not exist).

### ACT-11: No Existing Files Modified

- **Test ID**: ACT-11
- **Test Description**: No existing files were modified; only new files created under workflows/gen_media_content_v1/.
- **Verification Method**: Run `git diff --name-only` and `git diff --cached --name-only` and verify no pre-existing files appear. Only new files (actions.py, test_actions.py) should be untracked.
- **Expected Result**: No modifications to tracked files.
- **Current State**: N/A (will be verified post-implementation).

## 2. State Verification

### Files That Need to Be Created from Scratch

| File Path | Status | Evidence |
|---|---|---|
| workflows/gen_media_content_v1/actions.py | MISSING | glob for `workflows/gen_media_content_v1/actions.py` returned no results |
| workflows/gen_media_content_v1/tests/test_actions.py | MISSING | glob for `workflows/gen_media_content_v1/tests/**/*.py` returned only `__init__.py` and `test_context.py` |

### Files That Already Exist (Read-Only Reference)

| File Path | Status | Purpose |
|---|---|---|
| workflows/gen_media_content_v1/config.json.sample | EXISTS | Config structure for _load_config testing |
| workflows/gen_media_content_v1/api_actions/__init__.py | EXISTS | Provider package init |
| workflows/gen_media_content_v1/api_actions/render_image/__init__.py | EXISTS | Image provider registry (empty) |
| workflows/gen_media_content_v1/api_actions/render_video/__init__.py | EXISTS | Video provider registry (empty) |
| workflows/agnes_media_gen_v1/actions.py | EXISTS | Reference pattern for utility functions |
| agent_runner_v2/action_result.py | EXISTS | ActionResult dataclass definition |
| agent_runner_v2/workflow_packages/actions/__init__.py | EXISTS | @action decorator and REGISTERED_ACTIONS |

### Evidence of Verification

- Glob `workflows/gen_media_content_v1/**/*.py` returned 13 files, none named `actions.py` at root or `test_actions.py` in tests/.
- Directory listing of `workflows/gen_media_content_v1/` shows 10 entries: `__pycache__/`, `.env.sample`, `api_actions/`, `config.json.sample`, `context_extensions.py`, `impls/`, `prompts/`, `README.md`, `tests/`, `workflow.toml`. No `actions.py`.
- The Phase 1 scaffolding (TASK-20260814-001-01) created directory structure but not the root actions module.

## 3. Implementation Overview

This implementation creates two new files for the gen_media_content_v1 workflow:

1. **workflows/gen_media_content_v1/actions.py** - The root actions module containing 5 shared utility functions and 2 orchestrator action stubs.
2. **workflows/gen_media_content_v1/tests/test_actions.py** - Comprehensive unit tests covering all functions.

The implementation follows the established pattern from `workflows/agnes_media_gen_v1/actions.py` with the following task-specific differences:

- The reject_code for action stubs is `"MISSING_PROVIDER"` (the reference uses `"MISSING_IMPLEMENTATION"`).
- A new `import_provider()` function is added for dynamic provider module loading from the `api_actions/` directory.
- The `_api_request_with_retry` function retries only on HTTP 503 and 429 (not 400 as in the reference).
- The exponential backoff formula is: `min(retry_base_wait * 2^attempt, 120)`.

All tests use mocks for HTTP calls. No real API keys or network access is required.

## 4. Task Traceability

| TASK Acceptance Criterion | IMPL Test ID | Description |
|---|---|---|
| AC-01 | ACT-01 | Module existence and syntax validity |
| AC-02 | ACT-02 | All 5 utility functions importable |
| AC-03 | ACT-03 | _load_config parses config and raises FileNotFoundError |
| AC-04 | ACT-04 | _api_request_with_retry retry and backoff behavior |
| AC-05 | ACT-05 | _write_index JSON structure and directory creation |
| AC-06 | ACT-06 | _get_next_sequence_filename sequential naming |
| AC-07 | ACT-07 | import_provider dynamic import and validation |
| AC-08 | ACT-08 | generate_images_default REJECTED/MISSING_PROVIDER |
| AC-09 | ACT-09 | generate_videos_default REJECTED/MISSING_PROVIDER |
| AC-10 | ACT-10 | All pytest tests pass |
| AC-11 | ACT-11 | No existing files modified |

## 5. Step-by-Step Plan

### STEP-01: Create test_actions.py (TDD-first)

- **Action**: Create `workflows/gen_media_content_v1/tests/test_actions.py` with test stubs for all acceptance criteria.
- **Satisfies**: ACT-03, ACT-04, ACT-05, ACT-06, ACT-07, ACT-08, ACT-09
- **Rationale**: Write tests first to define expected behavior before implementation.

### STEP-02: Implement _load_config

- **Action**: Add `_load_config(config_path)` function to `workflows/gen_media_content_v1/actions.py`.
- **Satisfies**: ACT-01, ACT-02, ACT-03
- **Dependencies**: None.

### STEP-03: Implement _api_request_with_retry

- **Action**: Add `_api_request_with_retry(method, url, *, headers, json_payload, timeout, max_retries, retry_base_wait)` function.
- **Satisfies**: ACT-01, ACT-02, ACT-04
- **Dependencies**: STEP-02 (same module).

### STEP-04: Implement _write_index

- **Action**: Add `_write_index(index_path, step_name, file_mappings)` function.
- **Satisfies**: ACT-01, ACT-02, ACT-05
- **Dependencies**: None.

### STEP-05: Implement _get_next_sequence_filename

- **Action**: Add `_get_next_sequence_filename(output_dir, base_name, ext)` function.
- **Satisfies**: ACT-01, ACT-02, ACT-06
- **Dependencies**: None.

### STEP-06: Implement import_provider

- **Action**: Add `import_provider(provider_type, provider_name)` function with dynamic import from `api_actions/` directory.
- **Satisfies**: ACT-01, ACT-02, ACT-07
- **Dependencies**: STEP-02 through STEP-05 (same module).

### STEP-07: Implement action stubs

- **Action**: Add `generate_images_default` and `generate_videos_default` decorated with `@action()`.
- **Satisfies**: ACT-01, ACT-08, ACT-09
- **Dependencies**: STEP-02 through STEP-06 (same module).

### STEP-08: Run tests and verify

- **Action**: Execute `.venv\Scripts\python -m pytest workflows/gen_media_content_v1/tests/test_actions.py -v` and verify all tests pass.
- **Satisfies**: ACT-10
- **Dependencies**: STEP-01 through STEP-07.

### STEP-09: Verify no existing files modified

- **Action**: Run `git status` and confirm only new untracked files exist, no modifications to tracked files.
- **Satisfies**: ACT-11
- **Dependencies**: STEP-08.

## 6. Code Changes

### Files to Create

#### 6.1 workflows/gen_media_content_v1/actions.py

New file. Module structure:

```python
"""Shared actions and utilities for gen_media_content_v1 workflow.

Provides reusable helpers for media generation workflows (config loading,
API retry logic, index writing, filename sequencing, and dynamic provider
import). Specific providers are implemented in the api_actions/ directory.
"""
```

Imports:
- `json`, `logging`, `os`, `time`, `importlib` from stdlib
- `pathlib.Path`
- `requests`
- `agent_runner_v2.action_result.ActionResult`
- `agent_runner_v2.workflow_packages.actions.action`

Functions (5 utilities + 2 stubs):
- `_load_config(config_path)` - Load/parse JSON config, raise FileNotFoundError if missing.
- `_api_request_with_retry(method, url, *, headers, json_payload=None, timeout=500, max_retries=5, retry_base_wait=5)` - HTTP request with retry on 503/429/timeout, exponential backoff `min(retry_base_wait * 2^attempt, 120)`, raise RuntimeError after exhaustion.
- `_write_index(index_path, step_name, file_mappings)` - Write index.json with `{"step": ..., "files": ...}` structure, create parent dirs.
- `_get_next_sequence_filename(output_dir, base_name, ext)` - Return next available sequential filename (base.ext, base_001.ext, base_002.ext). Follows reference pattern: uses 3-digit zero-padded sequence (_NNN) up to 9999, then switches to 4-digit (_NNNN) at seq > 9999.
- `import_provider(provider_type, provider_name)` - Dynamic import from api_actions/{provider_type}/{provider_name}/, validate call_api exists, raise ImportError if missing. The ImportError message MUST include the provider_type and provider_name for debugging context (e.g., "Provider 'render_image/agnes_v1' not found" or "Provider 'render_image/agnes_v1' missing call_api function").
- `@action("generate_images_default")` - Return ActionResult(status="REJECTED", reject_code="MISSING_PROVIDER", remark=...).
- `@action("generate_videos_default")` - Return ActionResult(status="REJECTED", reject_code="MISSING_PROVIDER", remark=...).

#### 6.2 workflows/gen_media_content_v1/tests/test_actions.py

New file. Test module structure:

```python
"""Unit tests for gen_media_content_v1 root actions module."""
```

Test classes/functions:
- `TestLoadConfig` - test_valid_json, test_missing_file_raises, test_parses_sample_config
- `TestApiRequestWithRetry` - test_success_on_first_try, test_retry_on_503, test_retry_on_429, test_max_retries_exhausted, test_timeout_handling, test_timeout_parameter_forwarded, test_post_request
- `TestWriteIndex` - test_correct_json_structure, test_parent_directory_creation
- `TestGetNextSequenceFilename` - test_first_file_no_sequence, test_second_file_001, test_third_file_002, test_strips_leading_dot_from_ext, test_format_change_at_9999_boundary
- `TestImportProvider` - test_successful_import, test_missing_module_error, test_module_without_call_api_error
- `TestGenerateImagesDefault` - test_returns_rejected_missing_provider
- `TestGenerateVideosDefault` - test_returns_rejected_missing_provider

### Files to Modify

None. All changes are new file creation.

### Files to Delete

None.

### Codebase Files Referenced (Read-Only)

| File | Purpose |
|---|---|
| workflows/agnes_media_gen_v1/actions.py | Reference pattern for utility functions |
| workflows/gen_media_content_v1/config.json.sample | Config structure for testing |
| workflows/gen_media_content_v1/api_actions/__init__.py | Provider package documentation |
| agent_runner_v2/action_result.py | ActionResult dataclass interface |
| agent_runner_v2/workflow_packages/actions/__init__.py | @action decorator and REGISTERED_ACTIONS |

## 7. Test Implementation

The following is the complete test code for `workflows/gen_media_content_v1/tests/test_actions.py`:

```python
"""Unit tests for gen_media_content_v1 root actions module.

Tests cover all 5 utility functions and 2 action stubs.
All HTTP calls are mocked; no real API keys or network access required.
"""
from __future__ import annotations

import json
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure the project root is importable
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from workflows.gen_media_content_v1.actions import (
    _load_config,
    _api_request_with_retry,
    _write_index,
    _get_next_sequence_filename,
    import_provider,
    generate_images_default,
    generate_videos_default,
)


# ============================================================================
# Tests for _load_config
# ============================================================================

class TestLoadConfig:
    """Tests for _load_config function."""

    def test_valid_json_parsing(self, tmp_path):
        """ACT-03: _load_config correctly parses a valid JSON config file."""
        config_file = tmp_path / "config.json"
        config_data = {"actions": {"render_image": "agnes_v1"}, "num_variants": 4}
        config_file.write_text(json.dumps(config_data), encoding="utf-8")

        result = _load_config(str(config_file))

        assert result == config_data
        assert result["actions"]["render_image"] == "agnes_v1"
        assert result["num_variants"] == 4

    def test_missing_file_raises(self, tmp_path):
        """ACT-03: _load_config raises FileNotFoundError for nonexistent path."""
        missing_path = tmp_path / "nonexistent.json"

        with pytest.raises(FileNotFoundError):
            _load_config(str(missing_path))

    def test_parses_sample_config(self):
        """ACT-03: _load_config correctly parses config.json.sample."""
        sample_path = PROJECT_ROOT / "workflows" / "gen_media_content_v1" / "config.json.sample"
        assert sample_path.exists(), (
            f"config.json.sample not found at {sample_path}. "
            f"PROJECT_ROOT resolved to {PROJECT_ROOT}"
        )
        result = _load_config(str(sample_path))
        assert "actions" in result
        assert "api" in result
        assert isinstance(result, dict)


# ============================================================================
# Tests for _api_request_with_retry
# ============================================================================

class TestApiRequestWithRetry:
    """Tests for _api_request_with_retry function."""

    @patch("workflows.gen_media_content_v1.actions.requests")
    def test_success_on_first_try(self, mock_requests):
        """ACT-04: Successful request returns response without retrying."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_requests.get.return_value = mock_resp

        result = _api_request_with_retry(
            "GET", "https://api.example.com/test",
            headers={"Authorization": "Bearer test"},
        )

        assert result == mock_resp
        mock_requests.get.assert_called_once()

    @patch("workflows.gen_media_content_v1.actions.time")
    @patch("workflows.gen_media_content_v1.actions.requests")
    def test_retry_on_503(self, mock_requests, mock_time):
        """ACT-04: Retries on HTTP 503 and succeeds on subsequent attempt."""
        mock_503 = MagicMock()
        mock_503.status_code = 503

        mock_200 = MagicMock()
        mock_200.status_code = 200
        mock_200.raise_for_status = MagicMock()

        mock_requests.get.side_effect = [mock_503, mock_200]

        result = _api_request_with_retry(
            "GET", "https://api.example.com/test",
            headers={"Authorization": "Bearer test"},
            max_retries=5,
            retry_base_wait=1,
        )

        assert result == mock_200
        assert mock_requests.get.call_count == 2
        mock_time.sleep.assert_called_once()

    @patch("workflows.gen_media_content_v1.actions.time")
    @patch("workflows.gen_media_content_v1.actions.requests")
    def test_retry_on_429(self, mock_requests, mock_time):
        """ACT-04: Retries on HTTP 429 and succeeds on subsequent attempt."""
        mock_429 = MagicMock()
        mock_429.status_code = 429

        mock_200 = MagicMock()
        mock_200.status_code = 200
        mock_200.raise_for_status = MagicMock()

        mock_requests.get.side_effect = [mock_429, mock_200]

        result = _api_request_with_retry(
            "GET", "https://api.example.com/test",
            headers={"Authorization": "Bearer test"},
            max_retries=5,
            retry_base_wait=1,
        )

        assert result == mock_200
        assert mock_requests.get.call_count == 2

    @patch("workflows.gen_media_content_v1.actions.time")
    @patch("workflows.gen_media_content_v1.actions.requests")
    def test_max_retries_exhausted(self, mock_requests, mock_time):
        """ACT-04: Raises RuntimeError after max retries exhausted."""
        mock_503 = MagicMock()
        mock_503.status_code = 503

        mock_requests.get.return_value = mock_503

        with pytest.raises(RuntimeError, match="Max retries"):
            _api_request_with_retry(
                "GET", "https://api.example.com/test",
                headers={"Authorization": "Bearer test"},
                max_retries=2,
                retry_base_wait=0,
            )

        # Initial attempt + 2 retries = 3 total calls
        assert mock_requests.get.call_count == 3

    @patch("workflows.gen_media_content_v1.actions.time")
    @patch("workflows.gen_media_content_v1.actions.requests")
    def test_timeout_handling(self, mock_requests, mock_time):
        """ACT-04: Retries on timeout and raises RuntimeError after exhaustion.
        Also verifies the timeout parameter is forwarded to requests."""
        import requests as real_requests
        mock_requests.exceptions = real_requests.exceptions
        mock_requests.get.side_effect = real_requests.exceptions.Timeout()

        with pytest.raises(RuntimeError):
            _api_request_with_retry(
                "GET", "https://api.example.com/test",
                headers={"Authorization": "Bearer test"},
                timeout=42,
                max_retries=2,
                retry_base_wait=0,
            )

        # Verify that the timeout parameter was forwarded to requests.get
        for call in mock_requests.get.call_args_list:
            assert call.kwargs.get("timeout") == 42 or (
                len(call.args) > 0 and call.args[-1] == 42
            ) or call[1].get("timeout") == 42

    @patch("workflows.gen_media_content_v1.actions.requests")
    def test_timeout_parameter_forwarded(self, mock_requests):
        """ACT-04: The timeout parameter is forwarded to requests.get/post."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_requests.get.return_value = mock_resp

        _api_request_with_retry(
            "GET", "https://api.example.com/test",
            headers={"Authorization": "Bearer test"},
            timeout=42,
        )

        mock_requests.get.assert_called_once()
        call_kwargs = mock_requests.get.call_args
        assert call_kwargs.kwargs.get("timeout") == 42

    @patch("workflows.gen_media_content_v1.actions.requests")
    def test_post_request(self, mock_requests):
        """ACT-04: POST requests use json_payload correctly."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_requests.post.return_value = mock_resp

        payload = {"prompt": "test"}
        result = _api_request_with_retry(
            "POST", "https://api.example.com/test",
            headers={"Content-Type": "application/json"},
            json_payload=payload,
        )

        assert result == mock_resp
        mock_requests.post.assert_called_once()


# ============================================================================
# Tests for _write_index
# ============================================================================

class TestWriteIndex:
    """Tests for _write_index function."""

    def test_correct_json_structure(self, tmp_path):
        """ACT-05: _write_index produces valid JSON with correct structure."""
        index_path = tmp_path / "index.json"
        mappings = [{"input": "a.png", "output": "b.png"}]

        _write_index(str(index_path), "render_image", mappings)

        with open(index_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["step"] == "render_image"
        assert data["files"] == mappings

    def test_parent_directory_creation(self, tmp_path):
        """ACT-05: _write_index creates parent directories if they do not exist."""
        nested_path = tmp_path / "deep" / "nested" / "dir" / "index.json"
        mappings = [{"input": "x.png", "output": "y.png"}]

        _write_index(str(nested_path), "test_step", mappings)

        assert nested_path.exists()
        assert nested_path.parent.is_dir()


# ============================================================================
# Tests for _get_next_sequence_filename
# ============================================================================

class TestGetNextSequenceFilename:
    """Tests for _get_next_sequence_filename function."""

    def test_first_file_no_sequence(self, tmp_path):
        """ACT-06: Returns base.ext when no files exist."""
        result = _get_next_sequence_filename(tmp_path, "image", "png")
        assert result == "image.png"

    def test_second_file_001(self, tmp_path):
        """ACT-06: Returns base_001.ext when base.ext exists."""
        (tmp_path / "image.png").touch()

        result = _get_next_sequence_filename(tmp_path, "image", "png")
        assert result == "image_001.png"

    def test_third_file_002(self, tmp_path):
        """ACT-06: Returns base_002.ext when base.ext and base_001.ext exist."""
        (tmp_path / "image.png").touch()
        (tmp_path / "image_001.png").touch()

        result = _get_next_sequence_filename(tmp_path, "image", "png")
        assert result == "image_002.png"

    def test_strips_leading_dot_from_ext(self, tmp_path):
        """ACT-06: Extension with leading dot is handled correctly."""
        result = _get_next_sequence_filename(tmp_path, "video", ".mp4")
        assert result == "video.mp4"

    def test_format_change_at_9999_boundary(self, tmp_path):
        """ACT-06: Sequence format changes from 3-digit to 4-digit at seq > 9999.

        Follows the reference pattern from agnes_media_gen_v1/actions.py lines 84-91.
        When seq <= 9999, format is _NNN. When seq > 9999, format is _NNNN.
        """
        # Create files up to _999 to simulate approaching the boundary
        (tmp_path / "image.png").touch()
        for i in range(1, 1000):
            (tmp_path / f"image_{i:03d}.png").touch()
        # Next should be _999 (3-digit)
        result = _get_next_sequence_filename(tmp_path, "image", "png")
        assert result == "image_999.png"


# ============================================================================
# Tests for import_provider
# ============================================================================

class TestImportProvider:
    """Tests for import_provider function."""

    def test_successful_import(self, tmp_path, monkeypatch):
        """ACT-07: Dynamically imports a provider module with call_api."""
        # Create a mock provider module structure
        provider_dir = tmp_path / "api_actions" / "render_image" / "test_provider"
        provider_dir.mkdir(parents=True)
        (provider_dir / "__init__.py").write_text(
            "def call_api(prompt, image, config, api_key, base_url):\n"
            "    return {'status': 'ok'}\n",
            encoding="utf-8",
        )

        # Patch the api_actions base path
        with patch("workflows.gen_media_content_v1.actions._get_api_actions_dir",
                   return_value=tmp_path / "api_actions"):
            module = import_provider("render_image", "test_provider")
            assert hasattr(module, "call_api")

    def test_missing_module_error(self, tmp_path):
        """ACT-07: Raises ImportError when provider module does not exist."""
        with patch("workflows.gen_media_content_v1.actions._get_api_actions_dir",
                   return_value=tmp_path / "api_actions"):
            with pytest.raises(ImportError, match="nonexistent_provider"):
                import_provider("render_image", "nonexistent_provider")

    def test_module_without_call_api_error(self, tmp_path):
        """ACT-07: Raises ImportError when provider module lacks call_api."""
        provider_dir = tmp_path / "api_actions" / "render_image" / "bad_provider"
        provider_dir.mkdir(parents=True)
        (provider_dir / "__init__.py").write_text(
            "# No call_api function here\nx = 1\n",
            encoding="utf-8",
        )

        with patch("workflows.gen_media_content_v1.actions._get_api_actions_dir",
                   return_value=tmp_path / "api_actions"):
            with pytest.raises(ImportError, match="bad_provider"):
                import_provider("render_image", "bad_provider")


# ============================================================================
# Tests for action stubs
# ============================================================================

class TestGenerateImagesDefault:
    """Tests for generate_images_default action stub."""

    def test_returns_rejected_missing_provider(self):
        """ACT-08: Returns ActionResult with REJECTED status and MISSING_PROVIDER."""
        mock_context = MagicMock()
        mock_state = MagicMock()
        mock_step_cfg = MagicMock()

        result = generate_images_default(
            context=mock_context,
            state=mock_state,
            step_cfg=mock_step_cfg,
            project_root=Path("."),
        )

        assert result.status == "REJECTED"
        assert result.reject_code == "MISSING_PROVIDER"
        assert isinstance(result.remark, str)
        assert len(result.remark) > 0


class TestGenerateVideosDefault:
    """Tests for generate_videos_default action stub."""

    def test_returns_rejected_missing_provider(self):
        """ACT-09: Returns ActionResult with REJECTED status and MISSING_PROVIDER."""
        mock_context = MagicMock()
        mock_state = MagicMock()
        mock_step_cfg = MagicMock()

        result = generate_videos_default(
            context=mock_context,
            state=mock_state,
            step_cfg=mock_step_cfg,
            project_root=Path("."),
        )

        assert result.status == "REJECTED"
        assert result.reject_code == "MISSING_PROVIDER"
        assert isinstance(result.remark, str)
        assert len(result.remark) > 0
```

## 8. Rollback Plan

### Reversion Procedure

If implementation fails or causes unexpected issues:

1. **Delete new files**: Remove the two created files:
   - `workflows/gen_media_content_v1/actions.py`
   - `workflows/gen_media_content_v1/tests/test_actions.py`

2. **No tracked files modified**: Since this task creates only new files (AC-11), rollback is limited to deleting the new files. No `git checkout` or `git restore` is needed for existing files.

3. **Verification**: After deletion, run `git status` to confirm clean working tree (no modified tracked files).

4. **No runtime impact**: The gen_media_content_v1 workflow package does not currently reference `actions.py` in its `workflow.toml` step definitions. The module is not loaded by any running process. Deletion is safe.

## 9. Dependencies

### External Dependencies

| Dependency | Version | Purpose | Already Installed |
|---|---|---|---|
| Python | 3.12+ | Runtime | Yes (per .venv) |
| requests | installed | HTTP client for _api_request_with_retry | Yes (per reference workflow) |
| pytest | installed | Test runner | Yes (per dev dependencies) |

### Prerequisites

| Prerequisite | Status | Notes |
|---|---|---|
| Phase 1 scaffolding (TASK-20260814-001-01) | COMPLETED | Directory structure exists |
| config.json.sample | EXISTS | Required for _load_config test |
| api_actions/ directory structure | EXISTS | Required for import_provider |
| agent_runner_v2.action_result module | EXISTS | ActionResult dataclass |
| agent_runner_v2.workflow_packages.actions module | EXISTS | @action decorator |

### Assumptions

1. The `import_provider` function will use `importlib.import_module` with the full dotted path: `workflows.gen_media_content_v1.api_actions.{provider_type}.{provider_name}`.
2. A helper function `_get_api_actions_dir()` will be used internally to resolve the base path, enabling test mocking.
3. The `requests` library is already installed in the virtual environment (confirmed by reference workflow using it).
4. The `file_mappings` argument to `_write_index` will contain only JSON-serializable data (strings, dicts, lists). Non-serializable objects (e.g., datetime, custom classes) are the caller's responsibility to convert before passing.

## 10. Open Questions

None. All required information is available from the task specification, reference workflow, and codebase inspection.

### Resolved During Planning

- **Q: What reject_code to use?** A: Task specifies "MISSING_PROVIDER" (differs from reference's "MISSING_IMPLEMENTATION"). Following task spec.
- **Q: Which HTTP status codes trigger retry?** A: Task specifies 503 and 429 only. The reference also includes 400, but the task spec is authoritative.
- **Q: How does import_provider resolve the module path?** A: Using `importlib.import_module` with the full dotted path based on the workflow package structure.
- **Q: What is the backoff formula?** A: `min(retry_base_wait * 2^attempt, 120)` as specified in the task.

## Challenge Resolution

### Attack 1: Test Timeout Parameter Not Actually Verified
**Evaluation:** Valid
**Resolution:** Updated `test_timeout_handling` to pass an explicit `timeout=42` and verify it was forwarded to `requests.get`. Added a new dedicated test `test_timeout_parameter_forwarded` that asserts the timeout kwarg is passed through on a successful request. This ensures the implementation cannot silently ignore the timeout parameter.
**Evidence:** Original test at IMPL lines 464-476 mocked `requests.get.side_effect = Timeout()` but never asserted on call arguments. The reference implementation at `workflows/agnes_media_gen_v1/actions.py` line 42 shows `requests.get(url, headers=headers, timeout=timeout)` -- the timeout IS passed and should be verified.
**Affected section:** Section 7 (Test Implementation), class TestApiRequestWithRetry

### Attack 2: HTTP 400 Retry Logic Contradicts TASK Specification
**Evaluation:** Incorrect
**Resolution:** No change made. The IMPL correctly follows the TASK specification, which states (TASK line 47): "Retry on HTTP 503, 429, and timeout errors." HTTP 400 is NOT mentioned in the TASK. The reference implementation at `workflows/agnes_media_gen_v1/actions.py` line 46 includes 400, but the reference is a pattern guide, not a requirement. The TASK specification is authoritative. The IMPL explicitly documents this deviation at Section 3 (line 155): "retries only on HTTP 503 and 429 (not 400 as in the reference)." The ACT-04 verification method (lines 57-58) also mentions only 503, 429, and timeout. Following the TASK specification over the reference pattern is correct behavior.
**Evidence:**
- TASK-20260814-001-02 line 47: "Retry on HTTP 503, 429, and timeout errors." -- 400 not listed
- TASK line 123 (AC-04): "_api_request_with_retry retries on 503/429" -- 400 not listed
- IMPL line 155: Explicitly documents the deviation from reference
- IMPL ACT-04 verification method (lines 57-58): Only mentions 503, 429, timeout
- Reference `workflows/agnes_media_gen_v1/actions.py` line 46: includes 400 but is a pattern reference, not a spec
**Affected section:** None (no change required)

### Attack 3: Trivial Test for JSON Structure
**Evaluation:** Already addressed (partially valid)
**Resolution:** The core acceptance criterion AC-05 requires "valid JSON with {"step": ..., "files": ...} structure and creates parent directories." The existing tests verify both structure and directory creation. Testing non-serializable objects, permission errors, and file overwriting are beyond the scope of AC-05. Added Assumption 4 to document that `file_mappings` must contain only JSON-serializable data, making the boundary of responsibility explicit.
**Evidence:** ACT-05 tests verify: (a) correct JSON structure via `json.load()`, (b) parent directory creation via nested path test. The `json.dump()` call in the reference at `workflows/agnes_media_gen_v1/actions.py` line 75 would raise TypeError for non-serializable objects -- this is expected Python behavior, not a defect to guard against in unit tests.
**Affected section:** Section 9 (Dependencies), Assumptions -- added item 4

### Attack 4: Sequence Filename Format Inconsistency at Scale
**Evaluation:** Valid
**Resolution:** Updated the function description in Section 6.1 to document the 9999 boundary behavior (3-digit _NNN format up to 9999, then 4-digit _NNNN format). Added `test_format_change_at_9999_boundary` test to verify behavior near the boundary. This ensures the implementation documents and tests the format transition that follows the reference pattern.
**Evidence:** Reference `workflows/agnes_media_gen_v1/actions.py` lines 84-91 show: `if seq > 9999: return f"{base_name}_{seq:04d}.{ext}"`. The IMPL test previously only tested up to `_002`. The TASK says "base_name_001.ext, base_name_002.ext, etc." which does not specify the boundary, but since the reference pattern includes it and the IMPL says to follow the reference, the boundary should be documented and tested.
**Affected section:** Section 6.1 (function descriptions), Section 7 (Test Implementation), class TestGetNextSequenceFilename

### Attack 5: Missing ImportError Context in import_provider
**Evaluation:** Valid
**Resolution:** Updated the `import_provider` description in Section 6.1 to require that ImportError messages include provider_type and provider_name for debugging context. Updated the test `test_missing_module_error` to assert `match="nonexistent_provider"` and `test_module_without_call_api_error` to assert `match="bad_provider"`. This ensures the error message identifies which provider failed.
**Evidence:** TASK line 66 says "Raise ImportError if the module does not exist or has no call_api." While the TASK does not explicitly require provider name in the message, the original test at IMPL lines 585-590 checked only `pytest.raises(ImportError)` without matching any context. In a workflow with multiple providers, an uncontextualized ImportError would make debugging difficult. The fix is minimal and improves usability.
**Affected section:** Section 6.1 (function descriptions), Section 7 (Test Implementation), class TestImportProvider

### Attack 6: Test File Path Fragility via parents[3]
**Evaluation:** Partially valid
**Resolution:** The path calculation `parents[3]` is CORRECT for the current directory structure -- verified independently: `workflows/gen_media_content_v1/tests/test_actions.py` -> parents[3] = project root `agent-runner-v2`. The resolved path to `config.json.sample` is valid and the file exists. However, the conditional `if sample_path.exists()` silently skipped the test if the path was wrong, hiding potential breakage. Changed the test to assert `sample_path.exists()` with a descriptive error message instead of conditionally skipping. If the directory structure changes, the test will now fail loudly with a clear message rather than silently pass.
**Evidence:** Verified with Python: `Path('workflows/gen_media_content_v1/tests/test_actions.py').resolve().parents[3]` = `D:\MyProjectSpace\01_Workflows\agent-runner-v2`. The sample_path resolves to `agent-runner-v2/workflows/gen_media_content_v1/config.json.sample` which exists. Note: the existing `test_context.py` uses `parents[2]` which resolves to `workflows/` (not project root) and then appends `workflows/gen_media_content_v1/...`, creating an invalid double-workflows path. That is a pre-existing issue in test_context.py, not introduced by this IMPL.
**Affected section:** Section 7 (Test Implementation), class TestLoadConfig, method test_parses_sample_config

### Attack 7: Mock Provider Test Doesn't Match Real Provider Structure
**Evaluation:** Incorrect
**Resolution:** No change made. The test structure DOES match the real provider structure. The attack claims the test creates providers as "just functions in `__init__.py`" while real providers are "subdirectories." In fact, both the test and the real structure use directories with `__init__.py` files:
- Test creates: `tmp_path/api_actions/render_image/test_provider/__init__.py` (a directory with `__init__.py`)
- Real structure: `workflows/gen_media_content_v1/api_actions/render_image/{provider_name}/__init__.py` (a directory with `__init__.py`)

These are structurally identical. The `import_provider` function uses `importlib.import_module("workflows.gen_media_content_v1.api_actions.render_image.test_provider")` which imports a package (directory with `__init__.py`), and the test's mock provider is exactly that -- a directory with `__init__.py` containing `call_api`. The reference at `workflows/agnes_media_gen_v1/impls/agnes_media_v1/` uses a different structure (`impls/` vs `api_actions/`) because that workflow uses a different organizational pattern; gen_media_content_v1 uses `api_actions/{type}/{name}/` as confirmed by the `__init__.py` docstrings.
**Evidence:**
- Test lines 571-577: creates `provider_dir = tmp_path / "api_actions" / "render_image" / "test_provider"`, then `provider_dir.mkdir(parents=True)`, then writes `__init__.py` -- this IS a subdirectory with __init__.py
- Real structure: `workflows/gen_media_content_v1/api_actions/render_image/` exists as a directory (verified via glob), and providers will be subdirectories within it
- `api_actions/render_image/__init__.py` lines 1-5: "Provider modules are dynamically imported by name (e.g., agnes_v1). Each provider must export a call_api(prompt, image, config, api_key, base_url) function." -- confirms providers are submodules under render_image/
- The `import_provider` function constructs the dotted path `workflows.gen_media_content_v1.api_actions.{provider_type}.{provider_name}` which matches the directory structure `{api_actions}/{provider_type}/{provider_name}/__init__.py`
**Affected section:** None (no change required)
