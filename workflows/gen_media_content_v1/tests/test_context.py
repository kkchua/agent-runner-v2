"""Unit tests for gen_media_content_v1 context extensions.

Verifies that context_extensions.py produces the expected keys and
constructs paths correctly from workspace_root.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import patch

import pytest


def _load_context_extensions_module():
    """Load the context_extensions module from the workflow package."""
    module_path = (
        Path(__file__).resolve().parents[2]
        / "workflows"
        / "gen_media_content_v1"
        / "context_extensions.py"
    )
    spec = importlib.util.spec_from_file_location(
        "gen_media_content_v1.context_extensions", module_path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"Unable to load context_extensions module from {module_path}"
        )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestContextExtensionKeys:
    """Verify all expected context keys are produced."""

    @patch("agent_runner_v2.runtime_context.get_governance_runtime_root")
    @patch("agent_runner_v2.runtime_context.get_platform_runtime_root")
    @patch("agent_runner_v2.runtime_context.get_workspace_root")
    def test_step_dir_keys_present(self, mock_get_ws, mock_get_platform, mock_get_gov):
        """All 5 STEP_*_DIR keys are present in the context."""
        context_ext = _load_context_extensions_module()

        workspace_root = Path("D:/TestWorkspace")
        mock_get_ws.return_value = str(workspace_root)
        mock_get_gov.return_value = Path("D:/Governance")
        mock_get_platform.return_value = Path("D:/Platform")

        ext = context_ext.GenMediaContentExtensions()
        result = ext.build_context_extensions(
            state={}, step="test", step_cfg={}, ctx={}
        )

        expected_dir_keys = [
            "STEP_00_DIR",
            "STEP_01_DIR",
            "STEP_02_DIR",
            "STEP_03_DIR",
            "STEP_04_DIR",
        ]
        for key in expected_dir_keys:
            assert key in result, f"Missing expected key: {key}"

    @patch("agent_runner_v2.runtime_context.get_governance_runtime_root")
    @patch("agent_runner_v2.runtime_context.get_platform_runtime_root")
    @patch("agent_runner_v2.runtime_context.get_workspace_root")
    def test_media_config_key_present(self, mock_get_ws, mock_get_platform, mock_get_gov):
        """MEDIA_CONFIG key is present in the context."""
        context_ext = _load_context_extensions_module()

        workspace_root = Path("D:/TestWorkspace")
        mock_get_ws.return_value = str(workspace_root)
        mock_get_gov.return_value = Path("D:/Governance")
        mock_get_platform.return_value = Path("D:/Platform")

        ext = context_ext.GenMediaContentExtensions()
        result = ext.build_context_extensions(
            state={}, step="test", step_cfg={}, ctx={}
        )

        assert "MEDIA_CONFIG" in result


class TestContextExtensionPaths:
    """Verify paths are constructed correctly from workspace_root."""

    @patch("agent_runner_v2.runtime_context.get_governance_runtime_root")
    @patch("agent_runner_v2.runtime_context.get_platform_runtime_root")
    @patch("agent_runner_v2.runtime_context.get_workspace_root")
    def test_step_dirs_use_workspace_root(self, mock_get_ws, mock_get_platform, mock_get_gov):
        """Step directory paths are absolute and rooted at workspace_root."""
        context_ext = _load_context_extensions_module()

        workspace_root = Path("D:/TestWorkspace")
        mock_get_ws.return_value = str(workspace_root)
        mock_get_gov.return_value = Path("D:/Governance")
        mock_get_platform.return_value = Path("D:/Platform")

        ext = context_ext.GenMediaContentExtensions()
        result = ext.build_context_extensions(
            state={}, step="test", step_cfg={}, ctx={}
        )

        expected_mappings = {
            "STEP_00_DIR": "step_00_inputimage",
            "STEP_01_DIR": "step_01_imagedesc",
            "STEP_02_DIR": "step_02_promptvariant",
            "STEP_03_DIR": "step_03_generatedimage",
            "STEP_04_DIR": "step_04_generatedvideo",
        }
        for key, dirname in expected_mappings.items():
            expected_path = str(workspace_root / dirname)
            assert result[key] == expected_path, (
                f"{key}: expected {expected_path}, got {result[key]}"
            )

    @patch("agent_runner_v2.runtime_context.get_governance_runtime_root")
    @patch("agent_runner_v2.runtime_context.get_platform_runtime_root")
    @patch("agent_runner_v2.runtime_context.get_workspace_root")
    def test_media_config_path(self, mock_get_ws, mock_get_platform, mock_get_gov):
        """MEDIA_CONFIG points to config.json in workspace_root."""
        context_ext = _load_context_extensions_module()

        workspace_root = Path("D:/TestWorkspace")
        mock_get_ws.return_value = str(workspace_root)
        mock_get_gov.return_value = Path("D:/Governance")
        mock_get_platform.return_value = Path("D:/Platform")

        ext = context_ext.GenMediaContentExtensions()
        result = ext.build_context_extensions(
            state={}, step="test", step_cfg={}, ctx={}
        )

        expected_config = str(workspace_root / "config.json")
        assert result["MEDIA_CONFIG"] == expected_config

    @patch("agent_runner_v2.runtime_context.get_governance_runtime_root")
    @patch("agent_runner_v2.runtime_context.get_platform_runtime_root")
    @patch("agent_runner_v2.runtime_context.get_workspace_root")
    def test_archive_dirs_present(self, mock_get_ws, mock_get_platform, mock_get_gov):
        """Archive directory keys are also present for completeness."""
        context_ext = _load_context_extensions_module()

        workspace_root = Path("D:/TestWorkspace")
        mock_get_ws.return_value = str(workspace_root)
        mock_get_gov.return_value = Path("D:/Governance")
        mock_get_platform.return_value = Path("D:/Platform")

        ext = context_ext.GenMediaContentExtensions()
        result = ext.build_context_extensions(
            state={}, step="test", step_cfg={}, ctx={}
        )

        expected_archive_keys = [
            "STEP_00_ARCHIVE",
            "STEP_01_ARCHIVE",
            "STEP_02_ARCHIVE",
            "STEP_03_ARCHIVE",
            "STEP_04_ARCHIVE",
        ]
        for key in expected_archive_keys:
            assert key in result, f"Missing expected archive key: {key}"

    @patch("agent_runner_v2.runtime_context.get_governance_runtime_root")
    @patch("agent_runner_v2.runtime_context.get_platform_runtime_root")
    @patch("agent_runner_v2.runtime_context.get_workspace_root")
    def test_governance_and_platform_roots(self, mock_get_ws, mock_get_platform, mock_get_gov):
        """Governance and platform runtime roots are injected."""
        context_ext = _load_context_extensions_module()

        workspace_root = Path("D:/TestWorkspace")
        mock_get_ws.return_value = str(workspace_root)
        mock_get_gov.return_value = Path("D:/Governance")
        mock_get_platform.return_value = Path("D:/Platform")

        ext = context_ext.GenMediaContentExtensions()
        result = ext.build_context_extensions(
            state={}, step="test", step_cfg={}, ctx={}
        )

        assert result["GOVERNANCE_RUNTIME_ROOT"] == str(Path("D:/Governance"))
        assert result["PLATFORM_RUNTIME_ROOT"] == str(Path("D:/Platform"))


class TestArtifactKeyRegistration:
    """Verify register_artifact_keys produces expected mappings."""

    @patch("agent_runner_v2.runtime_context.get_workspace_root")
    def test_artifact_keys_registered(self, mock_get_ws):
        """All 4 index.json artifact keys are registered."""
        context_ext = _load_context_extensions_module()

        workspace_root = Path("D:/TestWorkspace")
        mock_get_ws.return_value = str(workspace_root)

        ext = context_ext.GenMediaContentExtensions()
        keys = ext.register_artifact_keys()

        expected_keys = {
            "IMAGE_DESCRIPTIONS": f"{workspace_root}/step_01_imagedesc/index.json",
            "PROMPT_VARIANTS": f"{workspace_root}/step_02_promptvariant/index.json",
            "IMAGE_INDEX": f"{workspace_root}/step_03_generatedimage/index.json",
            "VIDEO_INDEX": f"{workspace_root}/step_04_generatedvideo/index.json",
        }
        assert keys == expected_keys
