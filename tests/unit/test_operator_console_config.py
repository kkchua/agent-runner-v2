from __future__ import annotations

import json

import pytest

from agent_runner_v2.operator_console import config as console_config


def test_load_global_settings_requires_backend_url_and_worker_id(monkeypatch) -> None:
    monkeypatch.setattr(console_config, "load_runner_config", lambda: {})

    with pytest.raises(console_config.ConsoleConfigError) as exc:
        console_config.load_global_settings()

    assert "backend_url" in str(exc.value)
    assert "worker_id" in str(exc.value)


def test_load_console_config_parses_repos_and_workflows(tmp_path) -> None:
    config_path = tmp_path / "operator-console.json"
    config_path.write_text(
        json.dumps(
            {
                "repos": [
                    {
                        "name": "Main Repo",
                        "path": str(tmp_path / "repo"),
                        "workflows": [
                            {
                                "name": "Governance",
                                "workflow_name": "01_governance_foundation_v1",
                                "template_group": "01_governance_foundation_v1",
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    loaded = console_config.load_console_config(str(config_path))

    assert loaded.repos[0].name == "Main Repo"
    assert loaded.repos[0].workflows[0].workflow_name == "01_governance_foundation_v1"
    assert loaded.repos[0].workflows[0].template_group == "01_governance_foundation_v1"


def test_load_console_config_rejects_duplicate_repo_names(tmp_path) -> None:
    config_path = tmp_path / "operator-console.json"
    config_path.write_text(
        json.dumps(
            {
                "repos": [
                    {"name": "Main Repo", "path": str(tmp_path / "repo-1"), "workflows": [{"name": "WF", "workflow_name": "wf"}]},
                    {"name": "Main Repo", "path": str(tmp_path / "repo-2"), "workflows": [{"name": "WF", "workflow_name": "wf"}]},
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(console_config.ConsoleConfigError) as exc:
        console_config.load_console_config(str(config_path))

    assert "Duplicate repo name" in str(exc.value)
