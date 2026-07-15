from __future__ import annotations

import json

from agent_runner_v2.model_config import (
    resolve_coder_role,
    resolve_effective_coder,
    resolve_role_policy,
)


def test_resolve_coder_role_from_bundle_local_registry(tmp_path):
    bundle_root = tmp_path / "workflow_bundle"
    bundle_root.mkdir()
    registry_root = tmp_path / "_registry"
    registry_root.mkdir()
    (registry_root / "coder_roles.json").write_text(
        json.dumps(
            {
                "roles": {
                    "architect_primary": {
                        "coder": "opencode",
                        "connection": "opencode_go",
                        "model_id": "deepseek-v4-flash",
                        "role_type": "architect",
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    (registry_root / "coder_connections.json").write_text(
        json.dumps(
            {
                "connections": {
                    "opencode_go": {
                        "provider": "opencode_go",
                        "supported_coders": ["opencode"],
                        "model_format": "provider/model_id",
                        "provider_prefix": "opencode-go",
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    role = resolve_coder_role("architect_primary", bundle_root=bundle_root)

    assert role is not None
    assert role["coder"] == "opencode"
    assert role["connection"] == "opencode_go"


def test_resolve_effective_coder_from_registry(tmp_path):
    registry_root = tmp_path / "_registry"
    registry_root.mkdir()
    (registry_root / "coder_connections.json").write_text(
        json.dumps(
            {
                "connections": {
                    "deepseek": {
                        "provider": "deepseek",
                        "supported_coders": ["qwen", "claude"],
                        "model_format": "model_id",
                        "auth_type": "openai",
                        "openai_api_key_env": "DEEPSEEK_API_KEY",
                        "openai_base_url": "https://api.deepseek.com/v1",
                    },
                    "opencode_go": {
                        "provider": "opencode_go",
                        "supported_coders": ["opencode"],
                        "model_format": "provider/model_id",
                        "provider_prefix": "opencode-go",
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    (registry_root / "coder_roles.json").write_text(
        json.dumps(
            {
                "roles": {
                    "architect_primary": {
                        "coder": "opencode",
                        "connection": "opencode_go",
                        "model_id": "deepseek-v4-flash",
                        "role_type": "architect",
                    },
                    "reviewer_primary": {
                        "coder": "qwen",
                        "connection": "deepseek",
                        "model_id": "deepseek-v4-flash",
                        "role_type": "reviewer",
                    },
                    "reviewer_secondary": {
                        "coder": "codex",
                        "model_id": "gpt-5.4-nano",
                        "role_type": "reviewer",
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    (registry_root / "role_policies.json").write_text(
        json.dumps(
            {
                "role_policies": {
                    "architect_standard": {
                        "default_role": "architect_primary",
                        "allowed_roles": ["architect_primary"],
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    bundle_root = tmp_path / "workflow_bundle"
    bundle_root.mkdir()

    architect = resolve_effective_coder(role_name="architect_primary", bundle_root=bundle_root)
    reviewer = resolve_effective_coder(role_name="reviewer_primary", bundle_root=bundle_root)
    codex = resolve_effective_coder(role_name="reviewer_secondary", bundle_root=bundle_root)

    assert architect["coder"] == "opencode"
    assert architect["connection"] == "opencode_go"
    assert architect["model_id"] == "deepseek-v4-flash"
    assert architect["model"] == "opencode-go/deepseek-v4-flash"
    assert architect["provider_family"] == "opencode_go"
    assert architect["provider_key"] == "opencode_go"

    assert reviewer["coder"] == "qwen"
    assert reviewer["connection"] == "deepseek"
    assert reviewer["model"] == "deepseek-v4-flash"
    assert reviewer["auth_type"] == "openai"
    assert reviewer["openai_api_key_env"] == "DEEPSEEK_API_KEY"
    assert reviewer["openai_base_url"] == "https://api.deepseek.com/v1"
    assert reviewer["provider_family"] == "deepseek"
    assert reviewer["provider_key"] == "deepseek-v4-flash@https://api.deepseek.com/v1"

    assert codex["coder"] == "codex"
    assert codex["connection"] is None
    assert codex["model"] == "gpt-5.4-nano"
    assert codex["provider_family"] is None
    assert codex["provider_key"] is None

    policy = resolve_role_policy("architect_standard", bundle_root=bundle_root)
    assert policy is not None
    assert policy["default_role"] == "architect_primary"


def test_resolve_effective_coder_normalizes_base_url_in_provider_key(tmp_path):
    registry_root = tmp_path / "_registry"
    registry_root.mkdir()
    (registry_root / "coder_connections.json").write_text(
        json.dumps(
            {
                "connections": {
                    "openai_primary": {
                        "provider": "openai",
                        "supported_coders": ["qwen"],
                        "model_format": "model_id",
                        "auth_type": "openai",
                        "openai_api_key_env": "OPENAI_API_KEY",
                        "openai_base_url": "HTTPS://API.OPENAI.COM/v1/",
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    (registry_root / "coder_roles.json").write_text(
        json.dumps(
            {
                "roles": {
                    "reviewer_primary": {
                        "coder": "qwen",
                        "connection": "openai_primary",
                        "model_id": "gpt-5.4-nano",
                        "role_type": "reviewer",
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    bundle_root = tmp_path / "workflow_bundle"
    bundle_root.mkdir()

    reviewer = resolve_effective_coder(role_name="reviewer_primary", bundle_root=bundle_root)

    assert reviewer["provider_key"] == "gpt-5.4-nano@https://api.openai.com/v1"


def test_resolve_effective_coder_distinguishes_same_model_across_base_urls(tmp_path):
    registry_root = tmp_path / "_registry"
    registry_root.mkdir()
    (registry_root / "coder_connections.json").write_text(
        json.dumps(
            {
                "connections": {
                    "deepseek_primary": {
                        "provider": "deepseek",
                        "supported_coders": ["qwen"],
                        "model_format": "model_id",
                        "auth_type": "openai",
                        "openai_api_key_env": "DEEPSEEK_API_KEY",
                        "openai_base_url": "https://api.deepseek.com/v1",
                    },
                    "deepseek_proxy": {
                        "provider": "deepseek",
                        "supported_coders": ["qwen"],
                        "model_format": "model_id",
                        "auth_type": "openai",
                        "openai_api_key_env": "DEEPSEEK_API_KEY",
                        "openai_base_url": "https://proxy.example.com/deepseek/v1/",
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    (registry_root / "coder_roles.json").write_text(
        json.dumps(
            {
                "roles": {
                    "reviewer_primary": {
                        "coder": "qwen",
                        "connection": "deepseek_primary",
                        "model_id": "deepseek-v4-flash",
                        "role_type": "reviewer",
                    },
                    "reviewer_secondary": {
                        "coder": "qwen",
                        "connection": "deepseek_proxy",
                        "model_id": "deepseek-v4-flash",
                        "role_type": "reviewer",
                    },
                }
            }
        ),
        encoding="utf-8",
    )

    bundle_root = tmp_path / "workflow_bundle"
    bundle_root.mkdir()

    primary = resolve_effective_coder(role_name="reviewer_primary", bundle_root=bundle_root)
    secondary = resolve_effective_coder(role_name="reviewer_secondary", bundle_root=bundle_root)

    assert primary["provider_key"] == "deepseek-v4-flash@https://api.deepseek.com/v1"
    assert secondary["provider_key"] == "deepseek-v4-flash@https://proxy.example.com/deepseek/v1"
    assert primary["provider_key"] != secondary["provider_key"]
