"""Unit tests for agnes_v1 image rendering provider.

Tests cover successful generation, error handling, payload structure,
endpoint URL construction, header validation, input validation,
network error handling, JSON decode error handling, and timeout.
All HTTP calls are mocked; no real API keys or network access required.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests as real_requests

# Ensure the project root is importable
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from workflows.gen_media_content_v1.api_actions.render_image.agnes_v1 import call_api


class TestCallApi:
    """Tests for call_api function in agnes_v1 provider."""

    def test_successful_image_generation(self):
        """ACT-03: Returns dict with image_url and revised_prompt on successful 200 response."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": [{"url": "https://example.com/generated.png"}]
        }
        mock_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-image-2.1-flash", "size": "1024x1024", "ratio": "1:1"}

        with patch(
            "workflows.gen_media_content_v1.api_actions.render_image.agnes_v1.requests"
        ) as mock_requests:
            mock_requests.post.return_value = mock_resp
            mock_requests.exceptions = real_requests.exceptions

            result = call_api(
                prompt="a cat in a garden",
                config=config,
                api_key="test-key-123",
                base_url="https://apihub.agnes-ai.com",
            )

        assert "image_url" in result
        assert result["image_url"] == "https://example.com/generated.png"
        assert "revised_prompt" in result
        assert result["revised_prompt"] == "a cat in a garden"

    def test_missing_image_url_raises_runtime_error(self):
        """ACT-04: Raises RuntimeError when image URL is missing from response."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"data": []}
        mock_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-image-2.1-flash", "size": "1024x1024"}

        with patch(
            "workflows.gen_media_content_v1.api_actions.render_image.agnes_v1.requests"
        ) as mock_requests:
            mock_requests.post.return_value = mock_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError):
                call_api(
                    prompt="a sunset",
                    config=config,
                    api_key="test-key-123",
                    base_url="https://apihub.agnes-ai.com",
                )

    def test_http_error_raises_runtime_error(self):
        """ACT-05: Raises RuntimeError on HTTP errors (500)."""
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.raise_for_status.side_effect = real_requests.exceptions.HTTPError(
            "500 Server Error"
        )

        config = {"model": "agnes-image-2.1-flash", "size": "1024x1024"}

        with patch(
            "workflows.gen_media_content_v1.api_actions.render_image.agnes_v1.requests"
        ) as mock_requests:
            mock_requests.post.return_value = mock_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError):
                call_api(
                    prompt="a mountain",
                    config=config,
                    api_key="test-key-123",
                    base_url="https://apihub.agnes-ai.com",
                )

    def test_connection_error_raises_runtime_error(self):
        """ACT-05 supplementary: Raises RuntimeError on network-level ConnectionError."""
        config = {"model": "agnes-image-2.1-flash", "size": "1024x1024"}

        with patch(
            "workflows.gen_media_content_v1.api_actions.render_image.agnes_v1.requests"
        ) as mock_requests:
            mock_requests.post.side_effect = real_requests.exceptions.ConnectionError(
                "Connection refused"
            )
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="request failed"):
                call_api(
                    prompt="a river",
                    config=config,
                    api_key="test-key-123",
                    base_url="https://apihub.agnes-ai.com",
                )

    def test_timeout_error_raises_runtime_error(self):
        """ACT-05 supplementary: Raises RuntimeError on Timeout."""
        config = {"model": "agnes-image-2.1-flash", "size": "1024x1024"}

        with patch(
            "workflows.gen_media_content_v1.api_actions.render_image.agnes_v1.requests"
        ) as mock_requests:
            mock_requests.post.side_effect = real_requests.exceptions.Timeout(
                "Request timed out"
            )
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="request failed"):
                call_api(
                    prompt="a forest",
                    config=config,
                    api_key="test-key-123",
                    base_url="https://apihub.agnes-ai.com",
                )

    def test_json_decode_error_raises_runtime_error(self):
        """ACT-04/ACT-05 supplementary: Raises RuntimeError on non-JSON response."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.side_effect = ValueError("No JSON found")

        config = {"model": "agnes-image-2.1-flash", "size": "1024x1024"}

        with patch(
            "workflows.gen_media_content_v1.api_actions.render_image.agnes_v1.requests"
        ) as mock_requests:
            mock_requests.post.return_value = mock_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="non-JSON"):
                call_api(
                    prompt="a lake",
                    config=config,
                    api_key="test-key-123",
                    base_url="https://apihub.agnes-ai.com",
                )

    def test_correct_payload_structure(self):
        """ACT-06: Sends correct payload with model, prompt, size, ratio fields."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": [{"url": "https://example.com/img.png"}]
        }
        mock_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-image-2.1-flash", "size": "1024x1024", "ratio": "1:1"}

        with patch(
            "workflows.gen_media_content_v1.api_actions.render_image.agnes_v1.requests"
        ) as mock_requests:
            mock_requests.post.return_value = mock_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a flower",
                config=config,
                api_key="test-key-123",
                base_url="https://apihub.agnes-ai.com",
            )

            mock_requests.post.assert_called_once()
            call_kwargs = mock_requests.post.call_args
            payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")

            assert payload["model"] == "agnes-image-2.1-flash"
            assert payload["prompt"] == "a flower"
            assert payload["size"] == "1024x1024"
            assert payload["ratio"] == "1:1"

    def test_correct_endpoint_url(self):
        """ACT-07: Constructs correct endpoint URL {base_url}/v1/images/generations."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": [{"url": "https://example.com/img.png"}]
        }
        mock_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-image-2.1-flash", "size": "1024x1024"}

        with patch(
            "workflows.gen_media_content_v1.api_actions.render_image.agnes_v1.requests"
        ) as mock_requests:
            mock_requests.post.return_value = mock_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a tree",
                config=config,
                api_key="test-key-123",
                base_url="https://apihub.agnes-ai.com",
            )

            mock_requests.post.assert_called_once()
            call_url = mock_requests.post.call_args[0][0]
            assert call_url == "https://apihub.agnes-ai.com/v1/images/generations"

    def test_correct_headers(self):
        """ACT-06/ACT-07 supplementary: Verifies Authorization and Content-Type headers."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": [{"url": "https://example.com/img.png"}]
        }
        mock_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-image-2.1-flash", "size": "1024x1024"}

        with patch(
            "workflows.gen_media_content_v1.api_actions.render_image.agnes_v1.requests"
        ) as mock_requests:
            mock_requests.post.return_value = mock_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a bird",
                config=config,
                api_key="my-secret-key",
                base_url="https://apihub.agnes-ai.com",
            )

            mock_requests.post.assert_called_once()
            call_kwargs = mock_requests.post.call_args
            headers = call_kwargs.kwargs.get("headers") or call_kwargs[1].get("headers")

            assert headers["Authorization"] == "Bearer my-secret-key"
            assert headers["Content-Type"] == "application/json"

    def test_ratio_defaults_to_empty_string(self):
        """ACT-06 supplementary: ratio defaults to empty string when not in config."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": [{"url": "https://example.com/img.png"}]
        }
        mock_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-image-2.1-flash", "size": "1024x1024"}

        with patch(
            "workflows.gen_media_content_v1.api_actions.render_image.agnes_v1.requests"
        ) as mock_requests:
            mock_requests.post.return_value = mock_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a sky",
                config=config,
                api_key="test-key",
                base_url="https://apihub.agnes-ai.com",
            )

            call_kwargs = mock_requests.post.call_args
            payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
            assert payload["ratio"] == ""

    def test_timeout_parameter_passed(self):
        """ACT-06 supplementary: Verifies timeout=500 is passed to requests.post."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": [{"url": "https://example.com/img.png"}]
        }
        mock_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-image-2.1-flash", "size": "1024x1024"}

        with patch(
            "workflows.gen_media_content_v1.api_actions.render_image.agnes_v1.requests"
        ) as mock_requests:
            mock_requests.post.return_value = mock_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a cloud",
                config=config,
                api_key="test-key",
                base_url="https://apihub.agnes-ai.com",
            )

            call_kwargs = mock_requests.post.call_args
            timeout = call_kwargs.kwargs.get("timeout") or call_kwargs[1].get("timeout")
            assert timeout == 500

    def test_empty_base_url_raises_runtime_error(self):
        """Input validation: Empty base_url raises RuntimeError."""
        config = {"model": "agnes-image-2.1-flash", "size": "1024x1024"}

        with pytest.raises(RuntimeError, match="base_url"):
            call_api(
                prompt="a star",
                config=config,
                api_key="test-key",
                base_url="",
            )

    def test_missing_config_keys_raises_runtime_error(self):
        """Input validation: Missing required config keys raises RuntimeError."""
        with pytest.raises(RuntimeError, match="missing required keys"):
            call_api(
                prompt="a moon",
                config={},
                api_key="test-key",
                base_url="https://apihub.agnes-ai.com",
            )

    def test_trailing_slash_in_base_url_stripped(self):
        """ACT-07 supplementary: Trailing slash in base_url is handled correctly."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": [{"url": "https://example.com/img.png"}]
        }
        mock_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-image-2.1-flash", "size": "1024x1024"}

        with patch(
            "workflows.gen_media_content_v1.api_actions.render_image.agnes_v1.requests"
        ) as mock_requests:
            mock_requests.post.return_value = mock_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a hill",
                config=config,
                api_key="test-key",
                base_url="https://apihub.agnes-ai.com/",
            )

            call_url = mock_requests.post.call_args[0][0]
            assert call_url == "https://apihub.agnes-ai.com/v1/images/generations"
