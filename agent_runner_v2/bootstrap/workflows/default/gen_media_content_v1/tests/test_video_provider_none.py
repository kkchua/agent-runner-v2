"""Unit tests for __none__ skip video rendering provider.

Tests cover:
- Returns exact skip marker dict with "skipped": True (ACT-02)
- Return value is stable and exact across multiple calls (ACT-02)
- No side effects: no HTTP, no file I/O (ACT-03)
- Source-level verification: no HTTP or file I/O imports (ACT-03)
- Accepts arbitrary arguments without error (ACT-03)
- Accepts all-default arguments without error (ACT-03)

All tests are self-contained. No network access or API keys required.
"""
from __future__ import annotations

import inspect
import sys
from pathlib import Path
from unittest.mock import patch

# Ensure the project root is importable
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from workflows.gen_media_content_v1.api_actions.render_video.__none__ import call_api


MODULE_PATH = "workflows.gen_media_content_v1.api_actions.render_video.__none__"

EXPECTED_REASON = "Video generation disabled (__none__ provider)"


class TestCallApiReturnsSkipMarker:
    """ACT-02: call_api returns a skip marker dict with exact values."""

    def test_returns_skipped_true(self):
        """call_api returns dict with skipped=True."""
        result = call_api()
        assert result["skipped"] is True

    def test_returns_exact_reason(self):
        """call_api returns dict with the exact expected reason string."""
        result = call_api()
        assert result["reason"] == EXPECTED_REASON

    def test_reason_contains_none_marker(self):
        """reason field identifies this as the __none__ provider."""
        result = call_api()
        assert "__none__" in result["reason"]


class TestCallApiReturnValueStability:
    """ACT-02: call_api returns the same value on every invocation."""

    def test_return_value_is_stable(self):
        """Multiple calls return the exact same dict."""
        result1 = call_api()
        result2 = call_api()
        assert result1 == result2
        assert result1["skipped"] == result2["skipped"]
        assert result1["reason"] == result2["reason"]

    def test_return_value_is_identity(self):
        """Return value contains no variable components (no timestamps, no randomness)."""
        results = [call_api() for _ in range(10)]
        reasons = {r["reason"] for r in results}
        assert len(reasons) == 1
        assert reasons.pop() == EXPECTED_REASON


class TestCallApiNoSideEffects:
    """ACT-03: call_api makes no HTTP calls, no file I/O, no exceptions."""

    def test_no_http_calls(self):
        """call_api does not invoke the requests module."""
        with patch("requests.get") as mock_get, \
             patch("requests.post") as mock_post:
            call_api(
                prompt="test prompt",
                image="https://example.com/img.png",
                config={"model": "test"},
                api_key="fake-key",
                base_url="https://example.com",
            )
            mock_get.assert_not_called()
            mock_post.assert_not_called()

    def test_no_file_io(self):
        """call_api does not perform any file I/O operations."""
        with patch("builtins.open") as mock_open:
            call_api()
            mock_open.assert_not_called()

    def test_no_exceptions_raised(self):
        """call_api completes without raising any exceptions."""
        # Should not raise under any argument combination
        result = call_api(
            prompt="any prompt",
            image="any image",
            config={"any": "config"},
            api_key="any key",
            base_url="any url",
        )
        assert isinstance(result, dict)


class TestCallApiSourceIntegrity:
    """ACT-03: Source-level verification that module has no side-effect imports."""

    def test_no_http_imports_in_source(self):
        """Module source contains no imports of HTTP libraries."""
        source = inspect.getsource(sys.modules[call_api.__module__])
        forbidden = ["import requests", "import urllib", "import httpx",
                     "import aiohttp", "import httplib"]
        for pattern in forbidden:
            assert pattern not in source, (
                f"Provider module must not import HTTP libraries. "
                f"Found: {pattern}"
            )

    def test_no_file_io_imports_in_source(self):
        """Module source contains no imports related to file I/O."""
        source = inspect.getsource(sys.modules[call_api.__module__])
        forbidden = ["import os", "import shutil", "import pathlib"]
        for pattern in forbidden:
            assert pattern not in source, (
                f"Provider module must not import file I/O libraries. "
                f"Found: {pattern}"
            )


class TestCallApiArgumentFlexibility:
    """ACT-03: call_api accepts any arguments without error."""

    def test_accepts_arbitrary_arguments(self):
        """call_api accepts arbitrary string, dict, and None arguments."""
        result = call_api(
            prompt="a description",
            image="https://example.com/image.png",
            config={"model": "some-model", "resolution": "480P"},
            api_key="secret-key-123",
            base_url="https://api.example.com",
        )
        assert result["skipped"] is True

    def test_accepts_none_arguments(self):
        """call_api accepts None for optional parameters.

        Note: Python type annotations are not enforced at runtime.
        Passing None to parameters typed as str does not raise an error
        because annotations are hints only (and are stringified by
        'from __future__ import annotations').
        """
        result = call_api(
            prompt=None,
            image=None,
            config=None,
            api_key=None,
            base_url=None,
        )
        assert result["skipped"] is True


class TestCallApiDefaultArguments:
    """ACT-03: call_api works with all-default arguments."""

    def test_all_defaults_return_skip_marker(self):
        """call_api() with no arguments returns skip marker."""
        result = call_api()
        assert result["skipped"] is True
        assert result["reason"] == EXPECTED_REASON
