"""Unit tests for happyhorse_v1_1 video rendering provider.

Tests cover successful submit+poll cycle, error handling for submit and poll
phases, nested payload structure, endpoint URL construction, header validation
(X-DashScope-Async presence/absence), image-as-URL verification, fallback URL
extraction, input validation, network error handling, poll timeout,
JSON decode error handling, and poll-phase HTTP error handling.
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

from workflows.gen_media_content_v1.api_actions.render_video.happyhorse_v1_1 import call_api


# --- Helpers ---

BASE_URL = "https://dashscope.aliyuncs.com"
SUBMIT_URL = f"{BASE_URL}/api/v1/services/aigc/video-generation/video-synthesis"
TASK_ID = "task-abc-123"
POLL_URL = f"{BASE_URL}/api/v1/tasks/{TASK_ID}"
TEST_API_KEY = "test-key-hh-456"
TEST_VIDEO_URL = "https://cdn.dashscope.aliyuncs.com/videos/output.mp4"

FULL_CONFIG = {
    "model": "happyhorse-1.1-i2v",
    "resolution": "480P",
    "ratio": "9:16",
    "duration": 15,
}

MODULE_PATH = "workflows.gen_media_content_v1.api_actions.render_video.happyhorse_v1_1"


def _make_submit_response(task_id=TASK_ID):
    """Build a mock response for the submit POST."""
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"output": {"task_id": task_id}}
    resp.raise_for_status = MagicMock()
    return resp


def _make_poll_response(status="SUCCEEDED", video_url=TEST_VIDEO_URL, include_video_url_key=True):
    """Build a mock response for the poll GET.

    When include_video_url_key is False, output has no video_url key at all
    (forces fallback to results[0].url).
    """
    resp = MagicMock()
    resp.status_code = 200
    output = {"task_status": status}
    if status == "SUCCEEDED":
        if include_video_url_key:
            output["video_url"] = video_url
        else:
            output["video_url"] = ""
        output["results"] = [{"url": "https://cdn.dashscope.aliyuncs.com/videos/fallback.mp4"}]
    resp.json.return_value = {"output": output}
    resp.raise_for_status = MagicMock()
    return resp


def _patch_requests():
    """Return a patch context manager for the requests module in the provider."""
    return patch(f"{MODULE_PATH}.requests")


class TestCallApi:
    """Tests for call_api function in happyhorse_v1_1 video provider."""

    # --- ACT-03: Successful cycle ---

    def test_successful_submit_and_poll_returns_video_url(self):
        """ACT-03: Returns dict with video_url on successful submit + poll."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response(status="SUCCEEDED")

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            result = call_api(
                prompt="a cat walking in a garden",
                image="https://example.com/frame.png",
                config=FULL_CONFIG,
                api_key=TEST_API_KEY,
                base_url=BASE_URL,
            )

        assert result == {"video_url": TEST_VIDEO_URL}

    # --- ACT-04: Missing task_id ---

    def test_missing_task_id_raises_runtime_error(self):
        """ACT-04: Raises RuntimeError when task_id is missing from submit response."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.json.return_value = {"output": {"request_id": "some-other-id"}}
        submit_resp.raise_for_status = MagicMock()

        with _patch_requests() as mock_requests:
            mock_requests.post.return_value = submit_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError):
                call_api(
                    prompt="a dog running",
                    image="https://example.com/frame.png",
                    config=FULL_CONFIG,
                    api_key=TEST_API_KEY,
                    base_url=BASE_URL,
                )

    # --- ACT-05: FAILED poll status ---

    def test_poll_failed_status_raises_runtime_error(self):
        """ACT-05: Raises RuntimeError when poll returns FAILED task_status."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response(status="FAILED")

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError):
                call_api(
                    prompt="a bird flying",
                    image="https://example.com/frame.png",
                    config=FULL_CONFIG,
                    api_key=TEST_API_KEY,
                    base_url=BASE_URL,
                )

    # --- ACT-13: HTTP error on submit ---

    def test_http_error_on_submit_raises_runtime_error(self):
        """ACT-13: Raises RuntimeError on HTTP error during submit."""
        submit_resp = MagicMock()
        submit_resp.status_code = 500
        submit_resp.raise_for_status.side_effect = real_requests.exceptions.HTTPError(
            "500 Server Error"
        )

        with _patch_requests() as mock_requests:
            mock_requests.post.return_value = submit_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError):
                call_api(
                    prompt="a tree swaying",
                    image="https://example.com/frame.png",
                    config=FULL_CONFIG,
                    api_key=TEST_API_KEY,
                    base_url=BASE_URL,
                )

    # --- ACT-14: Connection error on submit ---

    def test_connection_error_on_submit_raises_runtime_error(self):
        """ACT-14: Raises RuntimeError on ConnectionError during submit."""
        with _patch_requests() as mock_requests:
            mock_requests.post.side_effect = real_requests.exceptions.ConnectionError(
                "Connection refused"
            )
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError):
                call_api(
                    prompt="a river flowing",
                    image="https://example.com/frame.png",
                    config=FULL_CONFIG,
                    api_key=TEST_API_KEY,
                    base_url=BASE_URL,
                )

    # --- ACT-06: Nested payload structure ---

    def test_correct_nested_payload_structure(self):
        """ACT-06: Sends correct nested payload with input + parameters."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response()

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a sunset over ocean",
                image="https://example.com/frame.png",
                config=FULL_CONFIG,
                api_key=TEST_API_KEY,
                base_url=BASE_URL,
            )

            mock_requests.post.assert_called_once()
            call_kwargs = mock_requests.post.call_args
            payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")

            # Top-level keys
            assert payload["model"] == "happyhorse-1.1-i2v"
            assert "input" in payload
            assert "parameters" in payload

            # Nested input structure
            assert payload["input"]["prompt"] == "a sunset over ocean"
            assert payload["input"]["media"] == [
                {"type": "first_frame", "url": "https://example.com/frame.png"}
            ]

            # Nested parameters structure
            assert payload["parameters"]["resolution"] == "480P"
            assert payload["parameters"]["ratio"] == "9:16"
            assert payload["parameters"]["duration"] == 15

    # --- ACT-07 / ACT-20: Submit headers ---

    def test_submit_has_x_dashscope_async_header(self):
        """ACT-07: Submit headers include X-DashScope-Async: enable."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response()

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a flower blooming",
                image="https://example.com/frame.png",
                config=FULL_CONFIG,
                api_key=TEST_API_KEY,
                base_url=BASE_URL,
            )

            call_kwargs = mock_requests.post.call_args
            headers = call_kwargs.kwargs.get("headers") or call_kwargs[1].get("headers")
            assert headers.get("X-DashScope-Async") == "enable"

    # --- ACT-18: Submit endpoint URL ---

    def test_correct_submit_endpoint_url(self):
        """ACT-18: Constructs correct submit endpoint URL."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response()

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a cloud drifting",
                image="https://example.com/frame.png",
                config=FULL_CONFIG,
                api_key=TEST_API_KEY,
                base_url=BASE_URL,
            )

            submit_url = mock_requests.post.call_args[0][0]
            assert submit_url == "https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis"

    # --- ACT-19: Poll endpoint URL ---

    def test_correct_poll_endpoint_url(self):
        """ACT-19: Constructs correct poll endpoint URL."""
        submit_resp = _make_submit_response(task_id="task-xyz-789")
        poll_resp = _make_poll_response()

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a star twinkling",
                image="https://example.com/frame.png",
                config=FULL_CONFIG,
                api_key=TEST_API_KEY,
                base_url=BASE_URL,
            )

            poll_url = mock_requests.get.call_args[0][0]
            assert poll_url == "https://dashscope.aliyuncs.com/api/v1/tasks/task-xyz-789"

    # --- ACT-08 / ACT-21: Poll headers ---

    def test_poll_does_not_have_x_dashscope_async_header(self):
        """ACT-08: Poll headers do NOT include X-DashScope-Async."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response()

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a rain falling",
                image="https://example.com/frame.png",
                config=FULL_CONFIG,
                api_key=TEST_API_KEY,
                base_url=BASE_URL,
            )

            call_kwargs = mock_requests.get.call_args
            headers = call_kwargs.kwargs.get("headers") or call_kwargs[1].get("headers")
            assert "X-DashScope-Async" not in headers
            assert "Content-Type" not in headers

    # --- ACT-11: Correct headers (comprehensive) ---

    def test_correct_headers(self):
        """ACT-20/ACT-21: Submits with correct headers, polls with only Authorization header (strict count check)."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response()

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a snow falling",
                image="https://example.com/frame.png",
                config=FULL_CONFIG,
                api_key="my-secret-key",
                base_url=BASE_URL,
            )

            # Verify submit headers
            submit_kwargs = mock_requests.post.call_args
            submit_headers = submit_kwargs.kwargs.get("headers") or submit_kwargs[1].get("headers")
            assert submit_headers["Authorization"] == "Bearer my-secret-key"
            assert submit_headers["Content-Type"] == "application/json"
            assert submit_headers["X-DashScope-Async"] == "enable"

            # Verify poll headers
            poll_kwargs = mock_requests.get.call_args
            poll_headers = poll_kwargs.kwargs.get("headers") or poll_kwargs[1].get("headers")
            assert poll_headers["Authorization"] == "Bearer my-secret-key"
            assert len(poll_headers) == 1, f"Poll headers should contain only Authorization, got: {list(poll_headers.keys())}"

    # --- ACT-16: Empty base_url ---

    def test_empty_base_url_raises_runtime_error(self):
        """ACT-16: Empty base_url raises RuntimeError."""
        with pytest.raises(RuntimeError, match="base_url"):
            call_api(
                prompt="a moon rising",
                image="https://example.com/frame.png",
                config=FULL_CONFIG,
                api_key=TEST_API_KEY,
                base_url="",
            )

    # --- ACT-17: Missing config keys ---

    def test_missing_config_keys_raises_runtime_error(self):
        """ACT-17: Missing required config keys raises RuntimeError."""
        with pytest.raises(RuntimeError, match="missing required keys"):
            call_api(
                prompt="a sun setting",
                image="https://example.com/frame.png",
                config={},
                api_key=TEST_API_KEY,
                base_url=BASE_URL,
            )

    # --- ACT-15: Poll timeout ---

    def test_poll_timeout_raises_runtime_error(self):
        """ACT-15: Raises RuntimeError when polling times out after max attempts."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response(status="PENDING")

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError):
                call_api(
                    prompt="a leaf falling",
                    image="https://example.com/frame.png",
                    config=FULL_CONFIG,
                    api_key=TEST_API_KEY,
                    base_url=BASE_URL,
                )

    # --- ACT-10: Fallback URL ---

    def test_fallback_url_from_results_when_video_url_empty(self):
        """ACT-10: Extracts URL from results[0].url when video_url is empty."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response(
            status="SUCCEEDED",
            video_url="",
            include_video_url_key=False,
        )

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            result = call_api(
                prompt="a wind blowing",
                image="https://example.com/frame.png",
                config=FULL_CONFIG,
                api_key=TEST_API_KEY,
                base_url=BASE_URL,
            )

        assert result["video_url"] == "https://cdn.dashscope.aliyuncs.com/videos/fallback.mp4"

    # --- ACT-09: Image as URL string ---

    def test_image_sent_as_url_string_not_base64(self):
        """ACT-09: Image is sent as URL string in media[0].url, not base64."""
        submit_resp = _make_submit_response()
        poll_resp = _make_poll_response()

        image_url = "https://example.com/my-frame.png"

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            call_api(
                prompt="a fire burning",
                image=image_url,
                config=FULL_CONFIG,
                api_key=TEST_API_KEY,
                base_url=BASE_URL,
            )

            call_kwargs = mock_requests.post.call_args
            payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
            media_url = payload["input"]["media"][0]["url"]

            assert media_url == image_url
            assert not media_url.startswith("data:")
            assert "base64" not in media_url

    # --- ACT-22: HTTP error during poll ---

    def test_http_error_during_poll_raises_runtime_error(self):
        """ACT-22: HTTP errors during polling are caught; final attempt raises RuntimeError with chained exception."""
        submit_resp = _make_submit_response()

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.side_effect = real_requests.exceptions.HTTPError(
                "503 Service Unavailable"
            )
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="[Pp]oll"):
                call_api(
                    prompt="a wave crashing",
                    image="https://example.com/frame.png",
                    config=FULL_CONFIG,
                    api_key=TEST_API_KEY,
                    base_url=BASE_URL,
                )

    # --- ACT-23: JSON decode error on submit ---

    def test_json_decode_error_on_submit_raises_runtime_error(self):
        """ACT-23: Non-JSON submit response raises RuntimeError with descriptive message."""
        submit_resp = MagicMock()
        submit_resp.status_code = 200
        submit_resp.raise_for_status = MagicMock()
        submit_resp.json.side_effect = ValueError("No JSON found")

        with _patch_requests() as mock_requests:
            mock_requests.post.return_value = submit_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="non-JSON"):
                call_api(
                    prompt="a bell ringing",
                    image="https://example.com/frame.png",
                    config=FULL_CONFIG,
                    api_key=TEST_API_KEY,
                    base_url=BASE_URL,
                )

    # --- ACT-24: JSON decode error on poll ---

    def test_json_decode_error_on_poll_raises_runtime_error(self):
        """ACT-24: Non-JSON poll response raises RuntimeError with descriptive message."""
        submit_resp = _make_submit_response()
        poll_resp = MagicMock()
        poll_resp.status_code = 200
        poll_resp.raise_for_status = MagicMock()
        poll_resp.json.side_effect = ValueError("No JSON found")

        with _patch_requests() as mock_requests, \
             patch(f"{MODULE_PATH}.time.sleep"):
            mock_requests.post.return_value = submit_resp
            mock_requests.get.return_value = poll_resp
            mock_requests.exceptions = real_requests.exceptions

            with pytest.raises(RuntimeError, match="non-JSON"):
                call_api(
                    prompt="a drum beating",
                    image="https://example.com/frame.png",
                    config=FULL_CONFIG,
                    api_key=TEST_API_KEY,
                    base_url=BASE_URL,
                )
