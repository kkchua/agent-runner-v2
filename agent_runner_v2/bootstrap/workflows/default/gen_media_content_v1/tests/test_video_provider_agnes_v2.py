"""Unit tests for agnes_v2 video rendering provider.

Tests cover successful submit+poll cycle, error handling (missing video_id,
failed/error status, HTTP errors, connection errors, timeout), payload
structure, endpoint URL construction, header validation, input validation,
negative_prompt conditional inclusion, polling timeout, and response key
fallbacks. All HTTP calls are mocked; time.sleep is patched to avoid delays.
No real API keys or network access required.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest
import requests as real_requests

# Ensure the project root is importable
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from workflows.gen_media_content_v1.api_actions.render_video.agnes_v2 import call_api


MODULE_PATH = "workflows.gen_media_content_v1.api_actions.render_video.agnes_v2"


class TestCallApi:
    """Tests for call_api function in agnes_v2 provider."""

    def test_successful_submit_and_poll_returns_video_url(self):
        """ACT-01: Returns dict with video_url on successful submit + poll cycle."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"video_id": "vid-abc-123"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.json.return_value = {
            "status": "completed",
            "url": "https://cdn.agnes-ai.com/video/vid-abc-123.mp4"
        }
        poll_resp.raise_for_status = MagicMock()

        config = {
            "model": "agnes-video-v2.0",
            "width": 1024,
            "height": 576,
            "num_frames": 72,
            "frame_rate": 24,
        }

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            result = call_api(
                prompt="a cat walking in a garden",
                image="https://example.com/cat.png",
                config=config,
                api_key="test-key-123",
                base_url="https://apihub.agnes-ai.com",
            )

        assert "video_url" in result
        assert result["video_url"] == "https://cdn.agnes-ai.com/video/vid-abc-123.mp4"

    def test_missing_video_id_raises_runtime_error(self):
        """ACT-02: Raises RuntimeError when video_id is missing from submit response."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {}
        submit_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="video_id"):
                call_api(
                    prompt="a sunset",
                    image="https://example.com/sunset.png",
                    config=config,
                    api_key="test-key-123",
                    base_url="https://apihub.agnes-ai.com",
                )

    def test_poll_failed_status_raises_runtime_error(self):
        """ACT-03: Raises RuntimeError when poll returns failed status."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"video_id": "vid-fail"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.json.return_value = {"status": "failed"}
        poll_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="failed"):
                call_api(
                    prompt="a mountain",
                    image="https://example.com/mountain.png",
                    config=config,
                    api_key="test-key-123",
                    base_url="https://apihub.agnes-ai.com",
                )

    def test_poll_error_status_raises_runtime_error(self):
        """ACT-04: Raises RuntimeError when poll returns error status."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"video_id": "vid-err"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.json.return_value = {"status": "error"}
        poll_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="error"):
                call_api(
                    prompt="a river",
                    image="https://example.com/river.png",
                    config=config,
                    api_key="test-key-123",
                    base_url="https://apihub.agnes-ai.com",
                )

    def test_http_error_on_submit_raises_runtime_error(self):
        """ACT-05: Raises RuntimeError on HTTP error during submit."""
        submit_resp = MagicMock()
        submit_resp.status_code = 500
        submit_resp.raise_for_status.side_effect = real_requests.exceptions.HTTPError(
            "500 Server Error"
        )

        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="request failed"):
                call_api(
                    prompt="a forest",
                    image="https://example.com/forest.png",
                    config=config,
                    api_key="test-key-123",
                    base_url="https://apihub.agnes-ai.com",
                )

    def test_connection_error_on_submit_raises_runtime_error(self):
        """ACT-06: Raises RuntimeError on ConnectionError during submit."""
        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.side_effect = real_requests.exceptions.ConnectionError(
                "Connection refused"
            )
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="request failed"):
                call_api(
                    prompt="a lake",
                    image="https://example.com/lake.png",
                    config=config,
                    api_key="test-key-123",
                    base_url="https://apihub.agnes-ai.com",
                )

    def test_timeout_error_on_submit_raises_runtime_error(self):
        """ACT-07: Raises RuntimeError on Timeout during submit."""
        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.side_effect = real_requests.exceptions.Timeout(
                "Request timed out"
            )
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="request failed"):
                call_api(
                    prompt="a cloud",
                    image="https://example.com/cloud.png",
                    config=config,
                    api_key="test-key-123",
                    base_url="https://apihub.agnes-ai.com",
                )

    def test_correct_submit_payload_structure(self):
        """ACT-08: Sends correct submit payload with all required fields."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"video_id": "vid-payload"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.json.return_value = {"status": "completed", "url": "https://cdn.example.com/v.mp4"}
        poll_resp.raise_for_status = MagicMock()

        config = {
            "model": "agnes-video-v2.0",
            "width": 1024,
            "height": 576,
            "num_frames": 72,
            "frame_rate": 24,
        }

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a bird flying",
                image="https://example.com/bird.png",
                config=config,
                api_key="test-key-123",
                base_url="https://apihub.agnes-ai.com",
            )

            mock_requests.post.assert_called_once()
            call_kwargs = mock_requests.post.call_args
            payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")

            assert payload["model"] == "agnes-video-v2.0"
            assert payload["prompt"] == "a bird flying"
            assert payload["image"] == "https://example.com/bird.png"
            assert payload["width"] == 1024
            assert payload["height"] == 576
            assert payload["num_frames"] == 72
            assert payload["frame_rate"] == 24

    def test_negative_prompt_included_when_present(self):
        """ACT-09: negative_prompt included in payload when present in config."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"video_id": "vid-neg"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.json.return_value = {"status": "completed", "url": "https://cdn.example.com/v.mp4"}
        poll_resp.raise_for_status = MagicMock()

        config = {
            "model": "agnes-video-v2.0",
            "width": 1024,
            "height": 576,
            "negative_prompt": "blurry, distorted",
        }

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a clear sky",
                image="https://example.com/sky.png",
                config=config,
                api_key="test-key-123",
                base_url="https://apihub.agnes-ai.com",
            )

            call_kwargs = mock_requests.post.call_args
            payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
            assert payload["negative_prompt"] == "blurry, distorted"

    def test_negative_prompt_omitted_when_absent(self):
        """ACT-10: negative_prompt omitted from payload when not in config."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"video_id": "vid-noneg"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.json.return_value = {"status": "completed", "url": "https://cdn.example.com/v.mp4"}
        poll_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a tree",
                image="https://example.com/tree.png",
                config=config,
                api_key="test-key-123",
                base_url="https://apihub.agnes-ai.com",
            )

            call_kwargs = mock_requests.post.call_args
            payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
            assert "negative_prompt" not in payload

    def test_correct_submit_endpoint_url(self):
        """ACT-11: Constructs correct submit URL {base_url}/v1/videos."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"video_id": "vid-url"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.json.return_value = {"status": "completed", "url": "https://cdn.example.com/v.mp4"}
        poll_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a flower",
                image="https://example.com/flower.png",
                config=config,
                api_key="test-key-123",
                base_url="https://apihub.agnes-ai.com",
            )

            call_url = mock_requests.post.call_args[0][0]
            assert call_url == "https://apihub.agnes-ai.com/v1/videos"

    def test_correct_poll_endpoint_url(self):
        """ACT-12: Constructs correct poll URL {base_url}/agnesapi?video_id={id}."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"video_id": "vid-poll-url"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.json.return_value = {"status": "completed", "url": "https://cdn.example.com/v.mp4"}
        poll_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a star",
                image="https://example.com/star.png",
                config=config,
                api_key="test-key-123",
                base_url="https://apihub.agnes-ai.com",
            )

            mock_requests.get.assert_called()
            poll_url = mock_requests.get.call_args[0][0]
            assert poll_url == "https://apihub.agnes-ai.com/agnesapi?video_id=vid-poll-url"

    def test_correct_headers(self):
        """ACT-13: Verifies Authorization Bearer + Content-Type headers."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"video_id": "vid-hdr"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.json.return_value = {"status": "completed", "url": "https://cdn.example.com/v.mp4"}
        poll_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a hill",
                image="https://example.com/hill.png",
                config=config,
                api_key="my-secret-key",
                base_url="https://apihub.agnes-ai.com",
            )

            # Verify submit headers
            post_kwargs = mock_requests.post.call_args
            post_headers = post_kwargs.kwargs.get("headers") or post_kwargs[1].get("headers")
            assert post_headers["Authorization"] == "Bearer my-secret-key"
            assert post_headers["Content-Type"] == "application/json"

            # Verify poll headers
            get_kwargs = mock_requests.get.call_args
            get_headers = get_kwargs.kwargs.get("headers") or get_kwargs[1].get("headers")
            assert get_headers["Authorization"] == "Bearer my-secret-key"

    def test_empty_base_url_raises_runtime_error(self):
        """ACT-14: Empty base_url raises RuntimeError."""
        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with pytest.raises(RuntimeError, match="base_url"):
            call_api(
                prompt="a moon",
                image="https://example.com/moon.png",
                config=config,
                api_key="test-key",
                base_url="",
            )

    def test_missing_config_keys_raises_runtime_error(self):
        """ACT-15: Missing required config keys raises RuntimeError."""
        with pytest.raises(RuntimeError, match="missing required keys"):
            call_api(
                prompt="a sun",
                image="https://example.com/sun.png",
                config={},
                api_key="test-key",
                base_url="https://apihub.agnes-ai.com",
            )

    def test_poll_timeout_after_max_attempts_raises_runtime_error(self):
        """ACT-16: Raises RuntimeError when polling times out after 120 attempts."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"video_id": "vid-timeout"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.json.return_value = {"status": "processing"}
        poll_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="[Tt]imed out|max.*attempts|poll"):
                call_api(
                    prompt="a planet",
                    image="https://example.com/planet.png",
                    config=config,
                    api_key="test-key-123",
                    base_url="https://apihub.agnes-ai.com",
                )

    def test_video_id_extracted_from_id_field_fallback(self):
        """ACT-17: video_id extracted from 'id' field when video_id key is absent."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"id": "vid-from-id-field"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.json.return_value = {"status": "completed", "url": "https://cdn.example.com/v.mp4"}
        poll_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a galaxy",
                image="https://example.com/galaxy.png",
                config=config,
                api_key="test-key-123",
                base_url="https://apihub.agnes-ai.com",
            )

            poll_url = mock_requests.get.call_args[0][0]
            assert "video_id=vid-from-id-field" in poll_url

    def test_video_url_extracted_from_video_url_field_fallback(self):
        """ACT-18: video_url extracted from 'video_url' field when url key is absent."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"video_id": "vid-vurl"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.json.return_value = {
            "status": "completed",
            "video_url": "https://cdn.example.com/fallback-video.mp4"
        }
        poll_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            result = call_api(
                prompt="a nebula",
                image="https://example.com/nebula.png",
                config=config,
                api_key="test-key-123",
                base_url="https://apihub.agnes-ai.com",
            )

        assert result["video_url"] == "https://cdn.example.com/fallback-video.mp4"

    def test_poll_cancelled_status_raises_runtime_error(self):
        """ACT-19: Raises RuntimeError when poll returns cancelled status."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"video_id": "vid-cancel"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.json.return_value = {"status": "cancelled"}
        poll_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="cancelled"):
                call_api(
                    prompt="a bird",
                    image="https://example.com/bird.png",
                    config=config,
                    api_key="test-key-123",
                    base_url="https://apihub.agnes-ai.com",
                )

    def test_http_error_during_polling_continues_and_times_out(self):
        """ACT-20: HTTP errors during polling do not crash; loop continues until timeout."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"video_id": "vid-poll-err"}
        submit_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.side_effect = real_requests.exceptions.HTTPError(
                "500 Server Error"
            )
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="[Tt]imed out|max.*attempts|poll"):
                call_api(
                    prompt="a deer",
                    image="https://example.com/deer.png",
                    config=config,
                    api_key="test-key-123",
                    base_url="https://apihub.agnes-ai.com",
                )

    def test_completed_poll_missing_video_url_raises_runtime_error(self):
        """ACT-21: Completed poll response missing both url and video_url raises RuntimeError."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"video_id": "vid-nourl"}
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.json.return_value = {"status": "completed"}
        poll_resp.raise_for_status = MagicMock()

        config = {"model": "agnes-video-v2.0", "width": 1024, "height": 576}

        with patch(f"{MODULE_PATH}.requests") as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="video.*[Uu][Rr][Ll]|url|download"):
                call_api(
                    prompt="a fox",
                    image="https://example.com/fox.png",
                    config=config,
                    api_key="test-key-123",
                    base_url="https://apihub.agnes-ai.com",
                )
