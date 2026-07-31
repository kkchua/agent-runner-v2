"""Unit tests for operator_console config module.

Tests config loading, parsing, validation, and error handling.
"""
from __future__ import annotations

import json

import pytest

from agent_runner_v2.operator_console import config as console_config


class TestLoadGlobalSettings:
    def test_requires_backend_url_and_worker_id(self, monkeypatch):
        monkeypatch.setattr(console_config, "load_runner_config", lambda: {})
        with pytest.raises(console_config.ConsoleConfigError) as exc:
            console_config.load_global_settings()
        assert "backend_url" in str(exc.value)
        assert "worker_id" in str(exc.value)

    def test_requires_backend_url_only(self, monkeypatch):
        monkeypatch.setattr(
            console_config, "load_runner_config",
            lambda: {"worker_id": "w1"},
        )
        with pytest.raises(console_config.ConsoleConfigError) as exc:
            console_config.load_global_settings()
        assert "backend_url" in str(exc.value)

    def test_requires_worker_id_only(self, monkeypatch):
        monkeypatch.setattr(
            console_config, "load_runner_config",
            lambda: {"backend_url": "http://localhost:8100"},
        )
        with pytest.raises(console_config.ConsoleConfigError) as exc:
            console_config.load_global_settings()
        assert "worker_id" in str(exc.value)

    def test_loads_all_settings(self, monkeypatch):
        monkeypatch.setattr(
            console_config, "load_runner_config",
            lambda: {
                "backend_url": "http://localhost:8100",
                "worker_id": "worker-1",
                "worker_label": "production",
            },
        )
        settings = console_config.load_global_settings()
        assert settings.backend_url == "http://localhost:8100"
        assert settings.worker_id == "worker-1"
        assert settings.worker_label == "production"

    def test_default_worker_label_is_live(self, monkeypatch):
        monkeypatch.setattr(
            console_config, "load_runner_config",
            lambda: {
                "backend_url": "http://localhost:8100",
                "worker_id": "worker-1",
            },
        )
        settings = console_config.load_global_settings()
        assert settings.worker_label == "live"

    def test_empty_worker_label_defaults_to_live(self, monkeypatch):
        monkeypatch.setattr(
            console_config, "load_runner_config",
            lambda: {
                "backend_url": "http://localhost:8100",
                "worker_id": "worker-1",
                "worker_label": "",
            },
        )
        settings = console_config.load_global_settings()
        assert settings.worker_label == "live"


class TestLoadConsoleConfig:
    def _write_config(self, tmp_path, payload):
        config_path = tmp_path / "operator-console.json"
        config_path.write_text(json.dumps(payload), encoding="utf-8")
        return config_path

    def test_parses_repos_and_workflows(self, tmp_path):
        config_path = self._write_config(tmp_path, {
            "repos": [{
                "name": "Main Repo",
                "path": str(tmp_path / "repo"),
                "workflows": [{
                    "name": "Governance",
                    "workflow_name": "01_governance_foundation_v1",
                    "template_group": "01_governance_foundation_v1",
                }],
            }],
        })
        loaded = console_config.load_console_config(str(config_path))
        assert loaded.repos[0].name == "Main Repo"
        assert loaded.repos[0].workflows[0].workflow_name == "01_governance_foundation_v1"
        assert loaded.repos[0].workflows[0].template_group == "01_governance_foundation_v1"

    def test_rejects_duplicate_repo_names(self, tmp_path):
        config_path = self._write_config(tmp_path, {
            "repos": [
                {"name": "Dup", "path": "/p1", "workflows": [{"name": "WF", "workflow_name": "wf"}]},
                {"name": "Dup", "path": "/p2", "workflows": [{"name": "WF", "workflow_name": "wf"}]},
            ],
        })
        with pytest.raises(console_config.ConsoleConfigError, match="Duplicate repo name"):
            console_config.load_console_config(str(config_path))

    def test_rejects_duplicate_workflow_names_in_same_repo(self, tmp_path):
        config_path = self._write_config(tmp_path, {
            "repos": [{
                "name": "Repo",
                "path": "/p",
                "workflows": [
                    {"name": "WF", "workflow_name": "wf1"},
                    {"name": "WF", "workflow_name": "wf2"},
                ],
            }],
        })
        with pytest.raises(console_config.ConsoleConfigError, match="Duplicate workflow name"):
            console_config.load_console_config(str(config_path))

    def test_rejects_empty_repos_array(self, tmp_path):
        config_path = self._write_config(tmp_path, {"repos": []})
        with pytest.raises(console_config.ConsoleConfigError, match="non-empty array"):
            console_config.load_console_config(str(config_path))

    def test_rejects_missing_repos_key(self, tmp_path):
        config_path = self._write_config(tmp_path, {})
        with pytest.raises(console_config.ConsoleConfigError, match="non-empty array"):
            console_config.load_console_config(str(config_path))

    def test_rejects_non_object_repo_entry(self, tmp_path):
        config_path = self._write_config(tmp_path, {"repos": ["not_an_object"]})
        with pytest.raises(console_config.ConsoleConfigError, match="must be an object"):
            console_config.load_console_config(str(config_path))

    def test_rejects_empty_name(self, tmp_path):
        config_path = self._write_config(tmp_path, {
            "repos": [{"name": "", "path": "/p", "workflows": [{"name": "WF", "workflow_name": "wf"}]}],
        })
        with pytest.raises(console_config.ConsoleConfigError, match="non-empty"):
            console_config.load_console_config(str(config_path))

    def test_rejects_empty_path(self, tmp_path):
        config_path = self._write_config(tmp_path, {
            "repos": [{"name": "R", "path": "", "workflows": [{"name": "WF", "workflow_name": "wf"}]}],
        })
        with pytest.raises(console_config.ConsoleConfigError, match="non-empty"):
            console_config.load_console_config(str(config_path))

    def test_rejects_empty_workflows_array(self, tmp_path):
        config_path = self._write_config(tmp_path, {
            "repos": [{"name": "R", "path": "/p", "workflows": []}],
        })
        with pytest.raises(console_config.ConsoleConfigError, match="non-empty"):
            console_config.load_console_config(str(config_path))

    def test_rejects_invalid_json(self, tmp_path):
        config_path = tmp_path / "bad.json"
        config_path.write_text("{invalid json", encoding="utf-8")
        with pytest.raises(console_config.ConsoleConfigError, match="Failed to parse"):
            console_config.load_console_config(str(config_path))

    def test_raises_on_missing_file(self):
        with pytest.raises(console_config.ConsoleConfigError, match="not found"):
            console_config.load_console_config("/nonexistent/path/config.json")

    def test_rejects_non_object_root(self, tmp_path):
        config_path = tmp_path / "array.json"
        config_path.write_text("[1, 2, 3]", encoding="utf-8")
        with pytest.raises(console_config.ConsoleConfigError, match="must be a JSON object"):
            console_config.load_console_config(str(config_path))

    def test_parses_worker_id_and_os_type(self, tmp_path):
        config_path = self._write_config(tmp_path, {
            "repos": [{
                "name": "WSL Repo",
                "path": "/home/user/repo",
                "worker_id": "worker-wsl",
                "os_type": "linux",
                "workflows": [{"name": "WF", "workflow_name": "wf_v1"}],
            }],
        })
        loaded = console_config.load_console_config(str(config_path))
        assert loaded.repos[0].worker_id == "worker-wsl"
        assert loaded.repos[0].os_type == "linux"

    def test_template_group_defaults_to_none(self, tmp_path):
        config_path = self._write_config(tmp_path, {
            "repos": [{
                "name": "R",
                "path": "/p",
                "workflows": [{"name": "WF", "workflow_name": "wf"}],
            }],
        })
        loaded = console_config.load_console_config(str(config_path))
        assert loaded.repos[0].workflows[0].template_group is None


class TestResolveConsoleConfigPath:
    def test_default_path(self, monkeypatch):
        monkeypatch.delenv("AGENT_RUNNER_CONSOLE_CONFIG", raising=False)
        path = console_config.resolve_console_config_path(None)
        assert str(path).endswith("operator-console.json")

    def test_env_var_override(self, monkeypatch):
        monkeypatch.setenv("AGENT_RUNNER_CONSOLE_CONFIG", "/custom/path.json")
        path = console_config.resolve_console_config_path(None)
        assert str(path).replace("\\", "/").endswith("custom/path.json")

    def test_explicit_path_overrides_env(self, monkeypatch):
        monkeypatch.setenv("AGENT_RUNNER_CONSOLE_CONFIG", "/env/path.json")
        path = console_config.resolve_console_config_path("/explicit/path.json")
        assert str(path).replace("\\", "/").endswith("explicit/path.json")
