"""Tests for agent_runner_v2.bundle_loader.

Covers workspace bootstrapping, config persistence, workflow module loading,
and bundle seeding — all with real temporary directories (no filesystem mocks).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

from agent_runner_v2.bundle_loader import (
    config_path,
    init_workspace,
    load_project_config,
    load_workflow_module,
    save_project_config,
    seed_workflow_bundle,
    workflow_root,
    workflows_root,
)

from agent_runner_v2.runtime_context import DEFAULT_RUNNER_HOME, PACKAGE_ROOT


# ---------------------------------------------------------------------------
# config_path / workflows_root / workflow_root helpers
# ---------------------------------------------------------------------------

class TestPathHelpers:

    def test_config_path(self, tmp_path):
        result = config_path(tmp_path)
        assert result == tmp_path / DEFAULT_RUNNER_HOME / "config.json"

    def test_workflows_root(self, tmp_path):
        result = workflows_root(tmp_path)
        assert result == tmp_path / DEFAULT_RUNNER_HOME / "workflows"

    def test_workflow_root(self, tmp_path):
        result = workflow_root(tmp_path, "my_workflow")
        assert result == tmp_path / DEFAULT_RUNNER_HOME / "workflows" / "my_workflow"


# ---------------------------------------------------------------------------
# load_project_config
# ---------------------------------------------------------------------------

class TestLoadProjectConfig:

    def test_missing_config_returns_defaults(self, tmp_path):
        """No config.json → default config with 'default' workflow."""
        config = load_project_config(tmp_path)
        assert config["default_workflow"] == "default"
        assert "default" in config["workflows"]
        default_wf = config["workflows"]["default"]
        expected_rel = str(
            workflow_root(tmp_path, "default").relative_to(tmp_path)
        )
        assert default_wf["path"] == expected_rel

    def test_existing_config_loaded(self, tmp_path):
        cfg = {
            "default_workflow": "production",
            "workflows": {
                "production": {"path": ".ukbe-runner/workflows/production"},
                "staging": {"path": ".ukbe-runner/workflows/staging"},
            },
        }
        (tmp_path / DEFAULT_RUNNER_HOME).mkdir(parents=True)
        config_p = tmp_path / DEFAULT_RUNNER_HOME / "config.json"
        config_p.write_text(json.dumps(cfg))

        loaded = load_project_config(tmp_path)
        assert loaded == cfg

    def test_config_preserves_extra_keys(self, tmp_path):
        cfg = {
            "default_workflow": "default",
            "custom_key": "custom_value",
            "workflows": {},
        }
        (tmp_path / DEFAULT_RUNNER_HOME).mkdir(parents=True)
        config_p = tmp_path / DEFAULT_RUNNER_HOME / "config.json"
        config_p.write_text(json.dumps(cfg))

        loaded = load_project_config(tmp_path)
        assert loaded["custom_key"] == "custom_value"

    def test_invalid_json_raises(self, tmp_path):
        (tmp_path / DEFAULT_RUNNER_HOME).mkdir(parents=True)
        config_p = tmp_path / DEFAULT_RUNNER_HOME / "config.json"
        config_p.write_text("{bad json}")

        with pytest.raises(json.JSONDecodeError):
            load_project_config(tmp_path)


# ---------------------------------------------------------------------------
# save_project_config
# ---------------------------------------------------------------------------

class TestSaveProjectConfig:

    def test_creates_parent_dirs(self, tmp_path):
        runner = tmp_path / DEFAULT_RUNNER_HOME
        assert not runner.exists()

        save_project_config(tmp_path, {"foo": "bar"})

        config_p = runner / "config.json"
        assert config_p.exists()
        loaded = json.loads(config_p.read_text())
        assert loaded == {"foo": "bar"}

    def test_overwrites_existing(self, tmp_path):
        cfg1 = {"version": 1}
        save_project_config(tmp_path, cfg1)
        cfg2 = {"version": 2, "extra": True}
        save_project_config(tmp_path, cfg2)

        config_p = config_path(tmp_path)
        loaded = json.loads(config_p.read_text())
        assert loaded == cfg2

    def test_pretty_printed(self, tmp_path):
        save_project_config(tmp_path, {"a": 1, "b": 2})
        content = config_path(tmp_path).read_text()
        # json.dumps with indent=2 should produce multi-line output
        assert "\n" in content

    def test_ensure_ascii_false(self, tmp_path):
        save_project_config(tmp_path, {"name": "测试"})
        content = config_path(tmp_path).read_text()
        assert "测试" in content

    def test_empty_dict(self, tmp_path):
        save_project_config(tmp_path, {})
        loaded = json.loads(config_path(tmp_path).read_text())
        assert loaded == {}


# ---------------------------------------------------------------------------
# load_workflow_module
# ---------------------------------------------------------------------------

class TestLoadWorkflowModule:

    def test_loads_real_module(self, tmp_path):
        """Create a real template_groups.py and load it as a module."""
        wf = workflow_root(tmp_path, "my_wf")
        wf.mkdir(parents=True)
        module_path = wf / "template_groups.py"
        module_path.write_text(
            "ARTIFACT_KEYS = ['A', 'B']\n"
            "TEMPLATE_GROUPS = {}\n"
        )

        config = {
            "workflows": {
                "my_wf": {"path": str(wf.relative_to(tmp_path))},
            }
        }

        mod = load_workflow_module(tmp_path, "my_wf", config=config)
        assert isinstance(mod, ModuleType)
        assert mod.ARTIFACT_KEYS == ["A", "B"]
        assert mod.TEMPLATE_GROUPS == {}

    def test_uses_default_path_when_not_in_config(self, tmp_path):
        """When config is empty dict and workflow not in map, raises ValueError."""
        with pytest.raises(ValueError, match="Unknown workflow 'default'"):
            load_workflow_module(tmp_path, "default", config={})

    def test_raises_for_unknown_workflow(self, tmp_path):
        """Config lists some workflows but requested name is not among them."""
        config = {
            "workflows": {
                "alpha": {"path": ".ukbe-runner/workflows/alpha"},
                "beta": {"path": ".ukbe-runner/workflows/beta"},
            }
        }
        with pytest.raises(ValueError, match="Unknown workflow 'gamma'"):
            load_workflow_module(tmp_path, "gamma", config=config)

    def test_raises_for_unknown_workflow_shows_available(self, tmp_path):
        config = {
            "workflows": {
                "alpha": {"path": ".ukbe-runner/workflows/alpha"},
                "beta": {"path": ".ukbe-runner/workflows/beta"},
            }
        }
        with pytest.raises(ValueError, match="Available workflows: alpha, beta"):
            load_workflow_module(tmp_path, "gamma", config=config)

    def test_raises_for_missing_template_groups(self, tmp_path):
        """Workflow root exists but template_groups.py is missing."""
        wf = workflow_root(tmp_path, "my_wf")
        wf.mkdir(parents=True)
        # No template_groups.py

        config = {
            "workflows": {
                "my_wf": {"path": str(wf.relative_to(tmp_path))},
            }
        }
        with pytest.raises(FileNotFoundError, match="Workflow bundle not found"):
            load_workflow_module(tmp_path, "my_wf", config=config)

    def test_config_with_path_override(self, tmp_path):
        """Config can specify an absolute or custom path."""
        custom_wf = tmp_path / "custom" / "workflow"
        custom_wf.mkdir(parents=True)
        module_path = custom_wf / "template_groups.py"
        module_path.write_text("CUSTOM = True\n")

        config = {
            "workflows": {
                "my_wf": {"path": str(custom_wf)},
            }
        }

        mod = load_workflow_module(tmp_path, "my_wf", config=config)
        assert mod.CUSTOM is True

    def test_empty_config_workflows_key(self, tmp_path):
        """config has 'workflows' key but it's None — treated as no workflows."""
        with pytest.raises(ValueError, match="Unknown workflow 'default'"):
            load_workflow_module(tmp_path, "default", config={"workflows": None})

    def test_no_config_uses_default(self, tmp_path):
        """config=None should fall back to default workflow path."""
        wf = workflow_root(tmp_path, "default")
        wf.mkdir(parents=True)
        (wf / "template_groups.py").write_text("NOCONFIG = True\n")

        mod = load_workflow_module(tmp_path, "default", config=None)
        assert mod.NOCONFIG is True

    def test_module_name_includes_workflow_name(self, tmp_path):
        """The loaded module should have a name reflecting the workflow."""
        wf = workflow_root(tmp_path, "special_wf")
        wf.mkdir(parents=True)
        (wf / "template_groups.py").write_text("pass\n")

        config = {
            "workflows": {"special_wf": {"path": str(wf.relative_to(tmp_path))}},
        }
        mod = load_workflow_module(tmp_path, "special_wf", config=config)
        assert "special_wf" in mod.__name__


# ---------------------------------------------------------------------------
# seed_workflow_bundle
# ---------------------------------------------------------------------------

class TestSeedWorkflowBundle:

    def test_copies_all_expected_files(self, tmp_path):
        wf_root = seed_workflow_bundle(tmp_path, workflow_name="default")
        assert wf_root.exists()

        expected_files = [
            "template_groups.py",
            "job_schema.json",
            "llm_response_schema.json",
            "model_mapping.json",
            "usage_schema.json",
        ]
        for fname in expected_files:
            assert (wf_root / fname).exists(), f"{fname} not copied"

    def test_copies_prompts_directory(self, tmp_path):
        """Prompts dir from PACKAGE_ROOT should be copied."""
        wf_root = seed_workflow_bundle(tmp_path, workflow_name="default")
        prompts_dst = wf_root / "prompts"
        assert prompts_dst.exists()
        assert prompts_dst.is_dir()
        # Should contain the prompt files from PACKAGE_ROOT/prompts
        assert any(prompts_dst.iterdir()), "prompts directory should not be empty"

    def test_custom_workflow_name(self, tmp_path):
        wf_root = seed_workflow_bundle(tmp_path, workflow_name="production")
        assert wf_root.name == "production"
        expected_parent = tmp_path / DEFAULT_RUNNER_HOME / "workflows" / "production"
        assert wf_root == expected_parent

    def test_idempotent_overwrites(self, tmp_path):
        """Running seed twice should overwrite existing prompts dir."""
        seed_workflow_bundle(tmp_path, workflow_name="default")
        wf_root = workflow_root(tmp_path, "default")
        prompts_dst = wf_root / "prompts"
        # Create a stale file in prompts
        stale = prompts_dst / "stale.txt"
        stale.touch()
        assert stale.exists()

        seed_workflow_bundle(tmp_path, workflow_name="default")
        # The copytree with shutil.rmtree first should remove stale
        assert not stale.exists()

    def test_returns_workflow_root(self, tmp_path):
        result = seed_workflow_bundle(tmp_path)
        assert isinstance(result, Path)
        assert result == workflow_root(tmp_path, "default")


# ---------------------------------------------------------------------------
# init_workspace
# ---------------------------------------------------------------------------

class TestInitWorkspace:

    def test_creates_directory_structure(self, tmp_path):
        init_workspace(tmp_path, workflow_name="default")

        runner_home = tmp_path / DEFAULT_RUNNER_HOME
        assert runner_home.exists()
        assert (runner_home / "jobs").exists()
        assert (runner_home / "logs").exists()
        assert (runner_home / "workflows").exists()

    def test_seeds_workflow_bundle(self, tmp_path):
        init_workspace(tmp_path, workflow_name="default")

        wf_root = workflow_root(tmp_path, "default")
        assert wf_root.exists()
        assert (wf_root / "template_groups.py").exists()
        assert (wf_root / "job_schema.json").exists()

    def test_creates_config(self, tmp_path):
        result = init_workspace(tmp_path, workflow_name="default")

        config_p = tmp_path / DEFAULT_RUNNER_HOME / "config.json"
        assert config_p.exists()

        config = json.loads(config_p.read_text())
        assert config["default_workflow"] == "default"
        assert "default" in config["workflows"]

    def test_returns_result_dict(self, tmp_path):
        result = init_workspace(tmp_path, workflow_name="default")

        assert "workspace_root" in result
        assert "runner_home" in result
        assert "workflow_name" in result
        assert "workflow_root" in result
        assert "config_path" in result

        assert Path(result["workspace_root"]) == tmp_path.resolve()
        assert result["workflow_name"] == "default"

    def test_custom_workflow_name(self, tmp_path):
        result = init_workspace(tmp_path, workflow_name="production")

        assert result["workflow_name"] == "production"

        config = json.loads(config_path(tmp_path).read_text())
        # default_workflow was set by load_project_config defaults, then preserved
        # because load_project_config already set default_workflow="default"
        assert "production" in config["workflows"]

        wf_root = workflow_root(tmp_path, "production")
        assert wf_root.exists()
        assert (wf_root / "template_groups.py").exists()

    def test_preserves_existing_config(self, tmp_path):
        """init_workspace should preserve existing config keys and workflows."""
        # Create an existing config
        cfg = {
            "default_workflow": "alpha",
            "workflows": {
                "alpha": {"path": ".ukbe-runner/workflows/alpha"},
            },
            "custom_setting": True,
        }
        save_project_config(tmp_path, cfg)

        # Init with a different workflow
        init_workspace(tmp_path, workflow_name="beta")

        config = json.loads(config_path(tmp_path).read_text())
        # default_workflow should be preserved (already set)
        assert config["default_workflow"] == "alpha"
        # custom_setting should be preserved
        assert config["custom_setting"] is True
        # alpha should still be there
        assert "alpha" in config["workflows"]
        # beta should be added
        assert "beta" in config["workflows"]

    def test_default_workflow_set_if_empty(self, tmp_path):
        """If no default_workflow exists in config, it gets set to the new workflow."""
        # Create config without default_workflow
        save_project_config(tmp_path, {"workflows": {}})
        init_workspace(tmp_path, workflow_name="gamma")

        config = json.loads(config_path(tmp_path).read_text())
        assert config["default_workflow"] == "gamma"

    def test_resolves_workspace(self, tmp_path):
        """workspace_root should be resolved to absolute path."""
        # This test just verifies resolve() is called
        result = init_workspace(tmp_path)
        ws = Path(result["workspace_root"])
        assert ws.is_absolute()

    def test_runner_home_mkdir_parents(self, tmp_path):
        """Runner home should be created with parents if needed."""
        deep = tmp_path / "a" / "b" / "c"
        result = init_workspace(deep, workflow_name="default")
        runner_home = deep / DEFAULT_RUNNER_HOME
        assert runner_home.exists()

    def test_existing_runner_home_not_cleared(self, tmp_path):
        """Existing directories in runner home should not be cleared."""
        init_workspace(tmp_path, workflow_name="default")

        # Create a file in runner_home
        marker = tmp_path / DEFAULT_RUNNER_HOME / "marker.txt"
        marker.write_text("hello")

        # Re-init
        init_workspace(tmp_path, workflow_name="second")

        assert marker.exists()
        assert marker.read_text() == "hello"
