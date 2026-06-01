"""Tests for agent_runner_v2.model_config.

Covers model alias resolution, mapping loading, and API key retrieval.
Uses real temporary directories for mapping files.
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from agent_runner_v2.model_config import (
    get_api_key,
    load_model_mapping,
    resolve_coder,
    _mapping_path,
    _runner_root,
)


# ---------------------------------------------------------------------------
# Helper: clear module-level cache before each test
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _reset_cache():
    import agent_runner_v2.model_config as mc
    mc._MAPPING = None
    mc._MAPPING_PATH = None
    yield
    mc._MAPPING = None
    mc._MAPPING_PATH = None


# ---------------------------------------------------------------------------
# load_model_mapping
# ---------------------------------------------------------------------------

class TestLoadModelMapping:

    def test_file_not_found_returns_empty(self, tmp_path):
        """When no mapping file exists, returns empty dict."""
        mapping = load_model_mapping(path=tmp_path / "nonexistent.json")
        assert mapping == {}

    def test_empty_mapping_file(self, tmp_path):
        p = tmp_path / "mapping.json"
        p.write_text("{}")
        mapping = load_model_mapping(path=p)
        assert mapping == {}

    def test_loads_coder_aliases(self, tmp_path):
        p = tmp_path / "mapping.json"
        data = {
            "coder_aliases": {
                "qwen-deepseek": {
                    "model": "deepseek-v3",
                    "auth_type": "openai",
                    "openai_api_key_env": "DEEPSEEK_API_KEY",
                },
            }
        }
        p.write_text(json.dumps(data))
        mapping = load_model_mapping(path=p)
        assert mapping == {
            "qwen-deepseek": {
                "model": "deepseek-v3",
                "auth_type": "openai",
                "openai_api_key_env": "DEEPSEEK_API_KEY",
            },
        }

    def test_multiple_aliases(self, tmp_path):
        p = tmp_path / "mapping.json"
        data = {
            "coder_aliases": {
                "alias-a": {"model": "model-a"},
                "alias-b": {"model": "model-b"},
            }
        }
        p.write_text(json.dumps(data))
        mapping = load_model_mapping(path=p)
        assert len(mapping) == 2
        assert mapping["alias-a"]["model"] == "model-a"
        assert mapping["alias-b"]["model"] == "model-b"

    def test_caching(self, tmp_path):
        """Subsequent calls return the cached result without re-reading."""
        p = tmp_path / "mapping.json"
        data = {"coder_aliases": {"x": {"model": "m"}}}
        p.write_text(json.dumps(data))
        first = load_model_mapping(path=p)

        # Overwrite the file — should NOT affect cached result
        data2 = {"coder_aliases": {"x": {"model": "changed"}}}
        p.write_text(json.dumps(data2))

        second = load_model_mapping(path=p)
        assert first == second
        assert first["x"]["model"] == "m"

    def test_different_path_bypasses_cache(self, tmp_path):
        """Loading from a different path still returns cached result (global cache)."""
        import agent_runner_v2.model_config as mc

        p1 = tmp_path / "mapping1.json"
        p1.write_text(json.dumps({"coder_aliases": {"a": {"model": "first"}}}))
        load_model_mapping(path=p1)

        # Cache is populated — second call returns cached regardless of path
        p2 = tmp_path / "mapping2.json"
        p2.write_text(json.dumps({"coder_aliases": {"a": {"model": "second"}}}))
        result = load_model_mapping(path=p2)
        assert result["a"]["model"] == "first"

    def test_invalid_json_raises(self, tmp_path):
        p = tmp_path / "mapping.json"
        p.write_text("{bad json}")
        with pytest.raises(json.JSONDecodeError):
            load_model_mapping(path=p)

    def test_coder_aliases_not_a_dict(self, tmp_path):
        """If coder_aliases is a list, it gets returned as-is (no validation)."""
        p = tmp_path / "mapping.json"
        p.write_text('{"coder_aliases": ["a", "b"]}')
        mapping = load_model_mapping(path=p)
        assert mapping == ["a", "b"]

    def test_top_level_keys_ignored(self, tmp_path):
        """Keys other than coder_aliases are ignored."""
        p = tmp_path / "mapping.json"
        data = {
            "coder_aliases": {"qwen": {"model": "qwen-turbo"}},
            "other_config": {"foo": "bar"},
        }
        p.write_text(json.dumps(data))
        mapping = load_model_mapping(path=p)
        assert "other_config" not in mapping
        assert mapping["qwen"]["model"] == "qwen-turbo"


# ---------------------------------------------------------------------------
# resolve_coder
# ---------------------------------------------------------------------------

class TestResolveCoder:

    def test_resolves_alias(self, tmp_path):
        p = tmp_path / "mapping.json"
        data = {
            "coder_aliases": {
                "qwen-deepseek": {"model": "deepseek-v3", "auth_type": "openai"},
            }
        }
        p.write_text(json.dumps(data))

        result = resolve_coder("qwen-deepseek", mapping_path=p)
        assert result is not None
        assert result["model"] == "deepseek-v3"
        assert result["auth_type"] == "openai"

    def test_unknown_coder_returns_none(self, tmp_path):
        p = tmp_path / "mapping.json"
        data = {"coder_aliases": {"known-alias": {"model": "x"}}}
        p.write_text(json.dumps(data))

        result = resolve_coder("unknown-coder", mapping_path=p)
        assert result is None

    def test_plain_coder_passes_through(self, tmp_path):
        """Plain coders like 'claude', 'qwen', 'codex' are not in aliases."""
        p = tmp_path / "mapping.json"
        data = {"coder_aliases": {"custom-alias": {"model": "x"}}}
        p.write_text(json.dumps(data))

        for name in ("claude", "qwen", "codex", "my-custom-tool"):
            result = resolve_coder(name, mapping_path=p)
            assert result is None

    def test_no_mapping_file(self, tmp_path):
        result = resolve_coder("anything", mapping_path=tmp_path / "nope.json")
        assert result is None

    def test_empty_mapping(self, tmp_path):
        p = tmp_path / "mapping.json"
        p.write_text("{}")
        result = resolve_coder("qwen", mapping_path=p)
        assert result is None

    def test_alias_config_has_multiple_fields(self, tmp_path):
        p = tmp_path / "mapping.json"
        data = {
            "coder_aliases": {
                "my-coder": {
                    "model": "gpt-4",
                    "auth_type": "openai",
                    "openai_api_key_env": "OPENAI_API_KEY",
                    "openai_base_url": "https://api.openai.com/v1",
                },
            }
        }
        p.write_text(json.dumps(data))
        result = resolve_coder("my-coder", mapping_path=p)
        assert result["model"] == "gpt-4"
        assert result["auth_type"] == "openai"
        assert result["openai_api_key_env"] == "OPENAI_API_KEY"
        assert result["openai_base_url"] == "https://api.openai.com/v1"


# ---------------------------------------------------------------------------
# get_api_key
# ---------------------------------------------------------------------------

class TestGetApiKey:

    def test_retrieves_from_env(self, monkeypatch):
        monkeypatch.setenv("MY_API_KEY", "sk-secret-key-12345")
        config = {"openai_api_key_env": "MY_API_KEY"}
        assert get_api_key(config) == "sk-secret-key-12345"

    def test_env_key_not_set(self, monkeypatch):
        monkeypatch.delenv("NONEXISTENT_KEY_VAR", raising=False)
        config = {"openai_api_key_env": "NONEXISTENT_KEY_VAR"}
        assert get_api_key(config) is None

    def test_no_env_key_in_config(self):
        config = {"model": "gpt-4"}
        assert get_api_key(config) is None

    def test_empty_config(self):
        assert get_api_key({}) is None

    def test_empty_env_key_string(self, monkeypatch):
        monkeypatch.delenv("", raising=False)
        config = {"openai_api_key_env": ""}
        assert get_api_key(config) is None

    def test_env_value_empty_string(self, monkeypatch):
        monkeypatch.setenv("EMPTY_KEY", "")
        config = {"openai_api_key_env": "EMPTY_KEY"}
        # os.environ.get returns "" which is truthy as a string
        result = get_api_key(config)
        assert result == ""

    def test_multiple_env_keys(self, monkeypatch):
        monkeypatch.setenv("KEY_A", "value-a")
        monkeypatch.setenv("KEY_B", "value-b")
        config = {"openai_api_key_env": "KEY_B"}
        assert get_api_key(config) == "value-b"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

class TestInternalHelpers:

    def test_runner_root_is_path(self):
        result = _runner_root()
        assert isinstance(result, Path)

    def test_mapping_path_constructed(self):
        result = _mapping_path()
        assert isinstance(result, Path)
        assert result.name == "model_mapping.json"
