"""Unit tests for api_key_pool module.

Tests cover:
- Key discovery from environment variables (numbered and bare fallback)
- Round-robin rotation behavior
- Empty pool handling
- Thread safety
- load_env_from_project helper
"""
from __future__ import annotations

import os
import threading
from pathlib import Path
from unittest.mock import patch

import pytest

from agent_runner_v2.api_key_pool import ApiKeyPool, load_env_from_project, mask_api_key


@pytest.fixture(autouse=True)
def clean_env():
    """Remove all AGNES_API_KEY* vars before each test to avoid leakage."""
    keys_to_remove = [
        k for k in os.environ if k.startswith("AGNES_API_KEY")
    ]
    for k in keys_to_remove:
        del os.environ[k]
    yield
    keys_to_remove = [
        k for k in os.environ if k.startswith("AGNES_API_KEY")
    ]
    for k in keys_to_remove:
        del os.environ[k]


class TestApiKeyDiscovery:
    """Tests for key discovery from environment variables."""

    def test_discover_numbered_keys(self):
        """Should discover PREFIX_1, PREFIX_2, PREFIX_3 in order."""
        os.environ["AGNES_API_KEY_1"] = "key-alpha"
        os.environ["AGNES_API_KEY_2"] = "key-beta"
        os.environ["AGNES_API_KEY_3"] = "key-gamma"

        pool = ApiKeyPool("AGNES_API_KEY", load_env=False)

        assert len(pool) == 3
        assert pool.keys == ["key-alpha", "key-beta", "key-gamma"]

    def test_discover_non_contiguous_numbered_keys(self):
        """Should handle gaps in numbering (e.g., _1, _3, _5)."""
        os.environ["AGNES_API_KEY_1"] = "key-first"
        os.environ["AGNES_API_KEY_3"] = "key-third"
        os.environ["AGNES_API_KEY_5"] = "key-fifth"

        pool = ApiKeyPool("AGNES_API_KEY", load_env=False)

        assert len(pool) == 3
        assert pool.keys == ["key-first", "key-third", "key-fifth"]

    def test_discover_single_numbered_key(self):
        """Should work with just PREFIX_1."""
        os.environ["AGNES_API_KEY_1"] = "only-key"

        pool = ApiKeyPool("AGNES_API_KEY", load_env=False)

        assert len(pool) == 1
        assert pool.keys == ["only-key"]

    def test_fallback_to_bare_key(self):
        """Should fall back to bare PREFIX when no numbered keys exist."""
        os.environ["AGNES_API_KEY"] = "bare-key"

        pool = ApiKeyPool("AGNES_API_KEY", load_env=False)

        assert len(pool) == 1
        assert pool.keys == ["bare-key"]

    def test_numbered_keys_take_precedence_over_bare(self):
        """Should prefer numbered keys over bare PREFIX."""
        os.environ["AGNES_API_KEY"] = "bare-key"
        os.environ["AGNES_API_KEY_1"] = "numbered-key"

        pool = ApiKeyPool("AGNES_API_KEY", load_env=False)

        assert len(pool) == 1
        assert pool.keys == ["numbered-key"]

    def test_empty_pool_when_no_keys(self):
        """Should return empty list when no matching keys exist."""
        pool = ApiKeyPool("AGNES_API_KEY", load_env=False)

        assert len(pool) == 0
        assert pool.keys == []

    def test_empty_values_are_skipped(self):
        """Should skip keys with empty string values."""
        os.environ["AGNES_API_KEY_1"] = "good-key"
        os.environ["AGNES_API_KEY_2"] = ""
        os.environ["AGNES_API_KEY_3"] = "another-good-key"

        pool = ApiKeyPool("AGNES_API_KEY", load_env=False)

        assert len(pool) == 2
        assert pool.keys == ["good-key", "another-good-key"]

    def test_different_prefixes_are_independent(self):
        """Should only discover keys matching the specified prefix."""
        os.environ["AGNES_API_KEY_1"] = "agnes-key"
        os.environ["OTHER_API_KEY_1"] = "other-key"

        pool = ApiKeyPool("AGNES_API_KEY", load_env=False)

        assert len(pool) == 1
        assert pool.keys == ["agnes-key"]


class TestRoundRobinRotation:
    """Tests for round-robin key rotation."""

    def test_basic_rotation(self):
        """Should cycle through keys in order."""
        os.environ["AGNES_API_KEY_1"] = "key-1"
        os.environ["AGNES_API_KEY_2"] = "key-2"
        os.environ["AGNES_API_KEY_3"] = "key-3"

        pool = ApiKeyPool("AGNES_API_KEY", load_env=False)

        assert pool.next_key() == "key-1"
        assert pool.next_key() == "key-2"
        assert pool.next_key() == "key-3"

    def test_loops_back_to_start(self):
        """Should wrap around to first key after last."""
        os.environ["AGNES_API_KEY_1"] = "key-1"
        os.environ["AGNES_API_KEY_2"] = "key-2"

        pool = ApiKeyPool("AGNES_API_KEY", load_env=False)

        assert pool.next_key() == "key-1"
        assert pool.next_key() == "key-2"
        assert pool.next_key() == "key-1"  # loops back
        assert pool.next_key() == "key-2"

    def test_single_key_always_returns_same(self):
        """Should return the same key repeatedly for single-key pool."""
        os.environ["AGNES_API_KEY_1"] = "only-key"

        pool = ApiKeyPool("AGNES_API_KEY", load_env=False)

        assert pool.next_key() == "only-key"
        assert pool.next_key() == "only-key"
        assert pool.next_key() == "only-key"

    def test_empty_pool_returns_empty_string(self):
        """Should return empty string when no keys available."""
        pool = ApiKeyPool("AGNES_API_KEY", load_env=False)

        assert pool.next_key() == ""

    def test_current_index_tracks_rotation(self):
        """Should track the index of the last returned key."""
        os.environ["AGNES_API_KEY_1"] = "key-1"
        os.environ["AGNES_API_KEY_2"] = "key-2"
        os.environ["AGNES_API_KEY_3"] = "key-3"

        pool = ApiKeyPool("AGNES_API_KEY", load_env=False)

        pool.next_key()
        assert pool.current_index() == 0

        pool.next_key()
        assert pool.current_index() == 1

        pool.next_key()
        assert pool.current_index() == 2

        pool.next_key()  # wraps
        assert pool.current_index() == 0

    def test_current_index_empty_pool(self):
        """Should return -1 for empty pool."""
        pool = ApiKeyPool("AGNES_API_KEY", load_env=False)
        assert pool.current_index() == -1


class TestThreadSafety:
    """Tests for thread-safe key rotation."""

    def test_concurrent_next_key(self):
        """Should handle concurrent calls without duplicates in short runs."""
        os.environ["AGNES_API_KEY_1"] = "key-1"
        os.environ["AGNES_API_KEY_2"] = "key-2"
        os.environ["AGNES_API_KEY_3"] = "key-3"

        pool = ApiKeyPool("AGNES_API_KEY", load_env=False)
        results = []
        lock = threading.Lock()

        def get_keys(count):
            local_results = []
            for _ in range(count):
                local_results.append(pool.next_key())
            with lock:
                results.extend(local_results)

        threads = [
            threading.Thread(target=get_keys, args=(100,))
            for _ in range(4)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All 400 results should be valid keys
        assert len(results) == 400
        assert all(k in ("key-1", "key-2", "key-3") for k in results)

        # Each key should appear roughly equally (within 20% tolerance)
        for key in ("key-1", "key-2", "key-3"):
            count = results.count(key)
            assert 100 <= count <= 170, (
                f"{key} appeared {count} times, expected ~133"
            )


class TestLoadEnvFromProject:
    """Tests for the load_env_from_project helper."""

    def test_loads_env_from_project_root(self, tmp_path):
        """Should load .env from specified project root."""
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_LOAD_ENV_VAR=hello-from-env\n")

        load_env_from_project(tmp_path)

        assert os.environ.get("TEST_LOAD_ENV_VAR") == "hello-from-env"
        del os.environ["TEST_LOAD_ENV_VAR"]

    def test_falls_back_to_default_when_no_env_file(self, tmp_path):
        """Should not raise when .env doesn't exist in project root."""
        # Should not raise
        load_env_from_project(tmp_path)

    def test_load_env_false_skips_loading(self):
        """Should not load .env when load_env=False."""
        os.environ["AGNES_API_KEY_1"] = "pre-loaded-key"

        pool = ApiKeyPool("AGNES_API_KEY", load_env=False)

        assert pool.keys == ["pre-loaded-key"]


class TestRepr:
    """Tests for string representation."""

    def test_repr_with_keys(self):
        """Should show prefix, count, and next index."""
        os.environ["AGNES_API_KEY_1"] = "key-1"
        os.environ["AGNES_API_KEY_2"] = "key-2"

        pool = ApiKeyPool("AGNES_API_KEY", load_env=False)

        assert "AGNES_API_KEY" in repr(pool)
        assert "keys=2" in repr(pool)

    def test_repr_empty_pool(self):
        """Should handle empty pool gracefully."""
        pool = ApiKeyPool("AGNES_API_KEY", load_env=False)

        assert "keys=0" in repr(pool)


class TestMaskApiKey:
    """Tests for the mask_api_key helper function."""

    def test_masks_long_key_showing_last_6(self):
        """Should show only last 6 characters of a long key."""
        assert mask_api_key("sk-abc123def456ghi789") == "****...ghi789"

    def test_masks_key_with_exact_6_chars(self):
        """Should mask keys with exactly 6 characters."""
        assert mask_api_key("abcdef") == "****"

    def test_masks_short_key(self):
        """Should mask keys shorter than 6 characters."""
        assert mask_api_key("short") == "****"

    def test_masks_empty_string(self):
        """Should mask empty strings."""
        assert mask_api_key("") == "****"

    def test_masks_none(self):
        """Should mask None values."""
        assert mask_api_key(None) == "****"

    def test_custom_show_last(self):
        """Should support custom number of trailing characters."""
        assert mask_api_key("sk-abc123def456", show_last=4) == "****...f456"

    def test_shows_exactly_last_6_by_default(self):
        """Should show exactly the last 6 characters."""
        assert mask_api_key("sk-1234567890abcdef") == "****...abcdef"
