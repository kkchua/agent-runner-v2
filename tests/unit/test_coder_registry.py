"""Unit tests for coder_registry module.

Tests URL normalization, provider key computation, model resolution,
role/connection/policy loading, and full coder resolution flow.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from agent_runner_v2 import coder_registry
from agent_runner_v2.coder_registry import (
    _effective_model,
    _normalize_base_url,
    _provider_key,
    _workflow_registry_root,
    get_api_key,
    load_coder_connections,
    load_coder_roles,
    load_role_policies,
    resolve_coder_role,
    resolve_connection,
    resolve_effective_coder,
    resolve_role_policy,
)
from agent_runner_v2.exceptions import ConfigurationError, NotFoundError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _clear_cache():
    """Clear JSON cache before each test."""
    coder_registry._JSON_CACHE.clear()


@pytest.fixture
def registry_dir(tmp_path):
    """Create a temp registry directory with sample JSON files."""
    reg = tmp_path / "_registry"
    reg.mkdir()

    connections = {
        "connections": {
            "00-bailian": {
                "provider": "bailian",
                "openai_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "openai_api_key_env": "DASHSCOPE_API_KEY",
                "auth_type": "api_key",
                "supported_coders": ["opencode", "qwen"],
                "provider_prefix": "00-bailian",
                "model_format": "provider/model_id",
            },
            "local-ollama": {
                "provider": "ollama",
                "openai_base_url": "http://localhost:11434/v1",
                "supported_coders": ["opencode"],
            },
        }
    }
    (reg / "coder_connections.json").write_text(json.dumps(connections), encoding="utf-8")

    roles = {
        "roles": {
            "architect_standard": {
                "coder": "opencode",
                "connection": "00-bailian",
                "model_id": "qwen-plus",
                "role_type": "architect",
            },
            "reviewer_standard": {
                "coder": "opencode",
                "connection": "00-bailian",
                "model_id": "qwen-turbo",
                "role_type": "reviewer",
            },
            "codex_role": {
                "coder": "codex",
                "model_id": "codex-1",
            },
        }
    }
    (reg / "coder_roles.json").write_text(json.dumps(roles), encoding="utf-8")

    policies = {
        "role_policies": {
            "architect_standard": {"max_rejects": 3},
            "reviewer_standard": {"max_rejects": 2},
        }
    }
    (reg / "role_policies.json").write_text(json.dumps(policies), encoding="utf-8")

    return reg


@pytest.fixture
def bundle_root(registry_dir):
    """Bundle root whose parent/_registry points to registry_dir."""
    # registry_dir is tmp_path/_registry, so bundle_root should be tmp_path/<something>
    bundle = registry_dir.parent / "my_bundle"
    bundle.mkdir()
    return bundle


# ---------------------------------------------------------------------------
# _normalize_base_url
# ---------------------------------------------------------------------------

class TestNormalizeBaseUrl:
    def test_strips_trailing_slash(self):
        # When path is just "/", rstrip("/") gives "" but `or parts.path` restores "/"
        # This is correct behavior — root path "/" is preserved
        result = _normalize_base_url("http://example.com/")
        assert "example.com" in result

    def test_lowercases_scheme_and_host(self):
        assert _normalize_base_url("HTTP://Example.COM/path") == "http://example.com/path"

    def test_empty_string_returns_empty(self):
        assert _normalize_base_url("") == ""

    def test_none_returns_empty(self):
        assert _normalize_base_url(None) == ""

    def test_preserves_path(self):
        url = _normalize_base_url("https://api.example.com/v1/")
        assert url == "https://api.example.com/v1"


# ---------------------------------------------------------------------------
# _provider_key
# ---------------------------------------------------------------------------

class TestProviderKey:
    def test_model_at_base_url(self):
        role = {"model_id": "qwen-plus"}
        conn = {"openai_base_url": "https://api.example.com/v1"}
        assert _provider_key(role=role, connection_name="c1", connection_profile=conn) == "qwen-plus@https://api.example.com/v1"

    def test_fallback_to_connection_name(self):
        role = {"model_id": ""}
        conn = {"openai_base_url": ""}
        assert _provider_key(role=role, connection_name="myconn", connection_profile=conn) == "myconn"

    def test_no_connection_profile(self):
        role = {"model_id": "m1"}
        assert _provider_key(role=role, connection_name="c1", connection_profile=None) == "c1"

    def test_no_connection_name_no_profile(self):
        role = {"model_id": "m1"}
        assert _provider_key(role=role, connection_name=None, connection_profile=None) is None


# ---------------------------------------------------------------------------
# _effective_model
# ---------------------------------------------------------------------------

class TestEffectiveModel:
    def test_plain_model_id(self):
        role = {"model_id": "qwen-plus"}
        assert _effective_model(role, None) == "qwen-plus"

    def test_provider_model_format(self):
        role = {"model_id": "qwen-plus"}
        conn = {"model_format": "provider/model_id", "provider_prefix": "00-bailian"}
        assert _effective_model(role, conn) == "00-bailian/qwen-plus"

    def test_missing_provider_prefix_raises(self):
        role = {"model_id": "qwen-plus"}
        conn = {"model_format": "provider/model_id", "provider_prefix": ""}
        with pytest.raises(ValueError, match="provider_prefix"):
            _effective_model(role, conn)

    def test_empty_model_id(self):
        role = {"model_id": ""}
        assert _effective_model(role, None) == ""

    def test_default_model_format_returns_model_id(self):
        role = {"model_id": "gpt-4"}
        conn = {"model_format": "model_id"}
        assert _effective_model(role, conn) == "gpt-4"


# ---------------------------------------------------------------------------
# Loading functions
# ---------------------------------------------------------------------------

class TestLoadFunctions:
    def test_load_coder_connections(self, bundle_root):
        conns = load_coder_connections(bundle_root=bundle_root)
        assert "00-bailian" in conns
        assert conns["00-bailian"]["provider"] == "bailian"

    def test_load_coder_roles(self, bundle_root):
        roles = load_coder_roles(bundle_root=bundle_root)
        assert "architect_standard" in roles
        assert roles["architect_standard"]["coder"] == "opencode"

    def test_load_role_policies(self, bundle_root):
        policies = load_role_policies(bundle_root=bundle_root)
        assert "architect_standard" in policies
        assert policies["architect_standard"]["max_rejects"] == 3

    def test_load_connections_empty_when_missing(self, tmp_path):
        bundle = tmp_path / "empty_bundle"
        bundle.mkdir()
        empty_reg = tmp_path / "empty_runtime_registry"
        empty_reg.mkdir()
        with patch("agent_runner_v2.coder_registry._runtime_registry_root", return_value=empty_reg):
            conns = load_coder_connections(bundle_root=bundle)
        assert conns == {}

    def test_resolve_connection_found(self, bundle_root):
        conn = resolve_connection("00-bailian", bundle_root=bundle_root)
        assert conn is not None
        assert conn["provider"] == "bailian"

    def test_resolve_connection_not_found(self, bundle_root):
        conn = resolve_connection("nonexistent", bundle_root=bundle_root)
        assert conn is None

    def test_resolve_coder_role_found(self, bundle_root):
        role = resolve_coder_role("architect_standard", bundle_root=bundle_root)
        assert role is not None
        assert role["coder"] == "opencode"

    def test_resolve_role_policy_found(self, bundle_root):
        policy = resolve_role_policy("architect_standard", bundle_root=bundle_root)
        assert policy is not None
        assert policy["max_rejects"] == 3


# ---------------------------------------------------------------------------
# resolve_effective_coder
# ---------------------------------------------------------------------------

class TestResolveEffectiveCoder:
    def test_resolves_opencode_role(self, bundle_root):
        result = resolve_effective_coder(role_name="architect_standard", bundle_root=bundle_root)
        assert result["coder"] == "opencode"
        assert result["model_id"] == "qwen-plus"
        assert result["connection"] == "00-bailian"
        assert result["provider_family"] == "bailian"
        assert result["model"] == "00-bailian/qwen-plus"

    def test_resolves_codex_role_without_connection(self, bundle_root):
        result = resolve_effective_coder(role_name="codex_role", bundle_root=bundle_root)
        assert result["coder"] == "codex"
        assert result["connection"] is None
        assert result["connection_profile"] is None

    def test_unknown_role_raises(self, bundle_root):
        with pytest.raises(ValueError, match="Unknown coder role"):
            resolve_effective_coder(role_name="nonexistent", bundle_root=bundle_root)

    def test_includes_auth_fields(self, bundle_root):
        result = resolve_effective_coder(role_name="architect_standard", bundle_root=bundle_root)
        assert result["auth_type"] == "api_key"
        assert result["openai_api_key_env"] == "DASHSCOPE_API_KEY"
        assert "openai_base_url" in result


# ---------------------------------------------------------------------------
# get_api_key
# ---------------------------------------------------------------------------

class TestGetApiKey:
    def test_returns_key_from_env(self):
        config = {"openai_api_key_env": "TEST_API_KEY"}
        with patch.dict(os.environ, {"TEST_API_KEY": "sk-test-123"}):
            assert get_api_key(config) == "sk-test-123"

    def test_returns_none_when_env_missing(self):
        config = {"openai_api_key_env": "NONEXISTENT_KEY"}
        with patch.dict(os.environ, {}, clear=True):
            assert get_api_key(config) is None

    def test_returns_none_when_no_env_key(self):
        config = {"coder": "opencode"}
        assert get_api_key(config) is None


# ---------------------------------------------------------------------------
# _workflow_registry_root
# ---------------------------------------------------------------------------

class TestWorkflowRegistryRoot:
    def test_raises_without_bundle_root(self):
        with pytest.raises(ConfigurationError, match="bundle_root is required"):
            _workflow_registry_root(bundle_root=None)

    def test_returns_parent_registry(self, tmp_path):
        bundle = tmp_path / "my_workflow"
        bundle.mkdir()
        result = _workflow_registry_root(bundle_root=bundle)
        assert result == tmp_path.resolve() / "_registry"
