from __future__ import annotations

import json

from agent_runner_v2.model_config import resolve_coder_role, resolve_role_alias


def test_resolve_coder_role_from_bundle_local_registry(tmp_path):
    bundle_root = tmp_path / "workflow_bundle"
    bundle_root.mkdir()
    (bundle_root / "coder_roles.json").write_text(
        json.dumps(
            {
                "roles": {
                    "architect_primary": {
                        "alias": "qwen-architect",
                        "role_type": "architect",
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    role = resolve_coder_role("architect_primary", bundle_root=bundle_root)

    assert role is not None
    assert role["alias"] == "qwen-architect"
    assert resolve_role_alias("architect_primary", bundle_root=bundle_root) == "qwen-architect"
