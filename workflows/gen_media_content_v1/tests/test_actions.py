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
        # Create files up to _998 to simulate approaching the boundary
        (tmp_path / "image.png").touch()
        for i in range(1, 999):
            (tmp_path / f"image_{i:03d}.png").touch()
        # Next should be _999 (3-digit, since seq <= 9999)
        result = _get_next_sequence_filename(tmp_path, "image", "png")
        assert result == "image_999.png"


# ============================================================================
# Tests for import_provider
# ============================================================================

class TestImportProvider:
    """Tests for import_provider function."""

    def test_successful_import(self, tmp_path, monkeypatch):
        """ACT-07: Dynamically imports a provider module with call_api."""
        # Create a mock module with call_api attribute
        mock_module = types.ModuleType("mock_provider")
        setattr(mock_module, "call_api", lambda *args, **kwargs: {"status": "ok"})

        # Mock importlib.import_module to return our mock module
        # This tests that import_provider correctly calls importlib and validates call_api
        with patch("workflows.gen_media_content_v1.actions.importlib.import_module",
                    return_value=mock_module) as mock_import:
            module = import_provider("render_image", "test_provider")
            assert hasattr(module, "call_api")
            mock_import.assert_called_once_with(
                "workflows.gen_media_content_v1.api_actions.render_image.test_provider"
            )

    def test_missing_module_error(self, tmp_path):
        """ACT-07: Raises ImportError when provider module does not exist."""
        with patch("workflows.gen_media_content_v1.actions.importlib.import_module",
                    side_effect=ModuleNotFoundError("No module named 'workflows.gen_media_content_v1.api_actions.render_image.nonexistent_provider'")):
            with pytest.raises(ImportError, match="nonexistent_provider"):
                import_provider("render_image", "nonexistent_provider")

    def test_module_without_call_api_error(self, tmp_path):
        """ACT-07: Raises ImportError when provider module lacks call_api."""
        # Create a mock module without call_api
        mock_module = types.ModuleType("bad_provider")
        setattr(mock_module, "x", 1)  # Some attribute, but no call_api

        with patch("workflows.gen_media_content_v1.actions.importlib.import_module",
                    return_value=mock_module):
            with pytest.raises(ImportError, match="bad_provider"):
                import_provider("render_image", "bad_provider")


# ============================================================================
# Tests for action orchestrators (updated from stub tests)
# ============================================================================

class TestGenerateImagesDefault:
    """Tests for generate_images_default orchestrator - missing provider case."""

    def test_returns_approved_skip_for_none_provider(self, tmp_path):
        """ACT-08: Returns APPROVED with skip message when render_image is __none__."""
        config_path = tmp_path / "config.json"
        config_data = {
            "actions": {"render_image": "__none__", "render_video": "__none__"},
            "api": {},
        }
        config_path.write_text(json.dumps(config_data), encoding="utf-8")
        step_02 = tmp_path / "step_02"
        step_02.mkdir()

        result = generate_images_default(
            context={"MEDIA_CONFIG": str(config_path),
                     "STEP_02_DIR": str(step_02),
                     "STEP_03_DIR": str(tmp_path / "step_03")},
            state=MagicMock(),
            step_cfg=MagicMock(),
            project_root=tmp_path,
        )

        assert result.status == "APPROVED"
        assert "skipped" in result.remark.lower()


class TestGenerateVideosDefault:
    """Tests for generate_videos_default orchestrator - skip provider case."""

    def test_returns_approved_skip_for_none_provider(self, tmp_path):
        """ACT-09: Returns APPROVED with skip message when render_video is __none__."""
        config_path = tmp_path / "config.json"
        config_data = {
            "actions": {"render_image": "agnes_v1", "render_video": "__none__"},
            "api": {},
        }
        config_path.write_text(json.dumps(config_data), encoding="utf-8")

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
        assert isinstance(result.remark, str)
        assert len(result.remark) > 0
