"""Unit tests for config_loader module.

Tests load_runner_config() path resolution, JSON parsing,
and error handling for missing/invalid config files.
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from agent_runner_v2.config_loader import load_runner_config


class TestLoadRunnerConfig:
    def test_returns_empty_dict_when_file_missing(self, tmp_path):
        """Returns {} when ~/.ukbe-runner/config.json doesn't exist."""
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        # No .ukbe-runner directory
        with patch("agent_runner_v2.config_loader.Path.home", return_value=fake_home):
            result = load_runner_config()
        assert result == {}

    def test_returns_parsed_dict_when_valid(self, tmp_path):
        """Returns parsed config when file is valid JSON."""
        fake_home = tmp_path / "home"
        config_dir = fake_home / ".ukbe-runner"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.json"
        config_data = {
            "backend_url": "http://localhost:8100",
            "worker_id": "worker-1",
            "worker_label": "live",
        }
        config_file.write_text(json.dumps(config_data), encoding="utf-8")

        with patch("agent_runner_v2.config_loader.Path.home", return_value=fake_home):
            result = load_runner_config()

        assert result == config_data

    def test_returns_empty_dict_when_invalid_json(self, tmp_path):
        """Returns {} when config file contains invalid JSON."""
        fake_home = tmp_path / "home"
        config_dir = fake_home / ".ukbe-runner"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.json"
        config_file.write_text("{invalid json content", encoding="utf-8")

        with patch("agent_runner_v2.config_loader.Path.home", return_value=fake_home):
            result = load_runner_config()

        assert result == {}

    def test_returns_empty_dict_when_json_is_list(self, tmp_path):
        """Returns {} when JSON root is a list, not a dict."""
        fake_home = tmp_path / "home"
        config_dir = fake_home / ".ukbe-runner"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.json"
        config_file.write_text("[1, 2, 3]", encoding="utf-8")

        with patch("agent_runner_v2.config_loader.Path.home", return_value=fake_home):
            result = load_runner_config()

        assert result == {}

    def test_returns_empty_dict_when_json_is_string(self, tmp_path):
        """Returns {} when JSON root is a string, not a dict."""
        fake_home = tmp_path / "home"
        config_dir = fake_home / ".ukbe-runner"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.json"
        config_file.write_text('"just a string"', encoding="utf-8")

        with patch("agent_runner_v2.config_loader.Path.home", return_value=fake_home):
            result = load_runner_config()

        assert result == {}

    def test_returns_empty_dict_when_file_empty(self, tmp_path):
        """Returns {} when config file is empty."""
        fake_home = tmp_path / "home"
        config_dir = fake_home / ".ukbe-runner"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.json"
        config_file.write_text("", encoding="utf-8")

        with patch("agent_runner_v2.config_loader.Path.home", return_value=fake_home):
            result = load_runner_config()

        assert result == {}

    def test_reads_from_correct_path(self, tmp_path):
        """Config is read from ~/.ukbe-runner/config.json."""
        fake_home = tmp_path / "home"
        config_dir = fake_home / ".ukbe-runner"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.json"
        config_file.write_text(json.dumps({"key": "value"}), encoding="utf-8")

        with patch("agent_runner_v2.config_loader.Path.home", return_value=fake_home):
            result = load_runner_config()

        assert result == {"key": "value"}

    def test_preserves_all_config_fields(self, tmp_path):
        """All config fields are preserved in the returned dict."""
        fake_home = tmp_path / "home"
        config_dir = fake_home / ".ukbe-runner"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.json"
        config_data = {
            "backend_url": "http://192.168.1.100:8100",
            "worker_id": "my-worker-01",
            "worker_label": "production",
            "cleanup_keep_days": 14,
            "nested": {"key": "value"},
        }
        config_file.write_text(json.dumps(config_data), encoding="utf-8")

        with patch("agent_runner_v2.config_loader.Path.home", return_value=fake_home):
            result = load_runner_config()

        assert result["backend_url"] == "http://192.168.1.100:8100"
        assert result["worker_id"] == "my-worker-01"
        assert result["cleanup_keep_days"] == 14
        assert result["nested"] == {"key": "value"}
