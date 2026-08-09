"""Unit tests for resolve_input_specs() and context_extensions guard.

Tests that:
- resolve_input_specs() resolves bare filenames, absolute paths, and blanks
- The guard in build_context_extensions() prevents overwriting resolved specs
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest


class TestResolveInputSpecs:
    """Test the standalone resolve_input_specs() function."""

    def test_bare_filename_resolved_to_specs_dir(self, tmp_path):
        from agent_runner_v2.workflow_packages.extensions_base import (
            resolve_input_specs,
        )

        specs_dir = tmp_path / "workflows" / "default" / "my_workflow" / "Specs"
        specs_dir.mkdir(parents=True)

        result: dict[str, str] = {}
        state = {"artifacts": {"WORKFLOW_SPEC_FILE": "codebase_to_meta_v1.md"}}

        with patch(
            "agent_runner_v2.workflow_packages.extensions_base.get_runner_home",
            return_value=tmp_path,
        ):
            resolve_input_specs(
                result, state, "my_workflow", ["WORKFLOW_SPEC_FILE"]
            )

        assert result["WORKFLOW_SPEC_FILE"] == str(
            specs_dir / "codebase_to_meta_v1.md"
        )

    def test_absolute_path_extracts_filename(self, tmp_path):
        """Backend-resolved absolute paths should extract filename → Specs/."""
        from agent_runner_v2.workflow_packages.extensions_base import (
            resolve_input_specs,
        )

        specs_dir = tmp_path / "workflows" / "default" / "my_workflow" / "Specs"
        specs_dir.mkdir(parents=True)

        result: dict[str, str] = {}
        state = {
            "artifacts": {
                "WORKFLOW_SPEC_FILE": "D:/workspace/docs/repo/specs/codebase_to_meta_v1.md"
            }
        }

        with patch(
            "agent_runner_v2.workflow_packages.extensions_base.get_runner_home",
            return_value=tmp_path,
        ):
            resolve_input_specs(
                result, state, "my_workflow", ["WORKFLOW_SPEC_FILE"]
            )

        # Should extract just the filename, not preserve the absolute path
        assert result["WORKFLOW_SPEC_FILE"] == str(
            specs_dir / "codebase_to_meta_v1.md"
        )
        assert "D:/workspace" not in result["WORKFLOW_SPEC_FILE"]

    def test_blank_value_resolves_to_default(self, tmp_path):
        from agent_runner_v2.workflow_packages.extensions_base import (
            resolve_input_specs,
        )

        specs_dir = tmp_path / "workflows" / "default" / "my_workflow" / "Specs"
        specs_dir.mkdir(parents=True)

        result: dict[str, str] = {}
        state = {"artifacts": {"WORKFLOW_SPEC_FILE": ""}}

        with patch(
            "agent_runner_v2.workflow_packages.extensions_base.get_runner_home",
            return_value=tmp_path,
        ):
            resolve_input_specs(
                result, state, "my_workflow", ["WORKFLOW_SPEC_FILE"]
            )

        assert result["WORKFLOW_SPEC_FILE"] == str(
            specs_dir / "default_spec.md"
        )

    def test_none_value_resolves_to_default(self, tmp_path):
        from agent_runner_v2.workflow_packages.extensions_base import (
            resolve_input_specs,
        )

        specs_dir = tmp_path / "workflows" / "default" / "my_workflow" / "Specs"
        specs_dir.mkdir(parents=True)

        result: dict[str, str] = {}
        state = {"artifacts": {"WORKFLOW_SPEC_FILE": None}}

        with patch(
            "agent_runner_v2.workflow_packages.extensions_base.get_runner_home",
            return_value=tmp_path,
        ):
            resolve_input_specs(
                result, state, "my_workflow", ["WORKFLOW_SPEC_FILE"]
            )

        assert result["WORKFLOW_SPEC_FILE"] == str(
            specs_dir / "default_spec.md"
        )

    def test_missing_key_resolves_to_default(self, tmp_path):
        from agent_runner_v2.workflow_packages.extensions_base import (
            resolve_input_specs,
        )

        specs_dir = tmp_path / "workflows" / "default" / "my_workflow" / "Specs"
        specs_dir.mkdir(parents=True)

        result: dict[str, str] = {}
        state = {"artifacts": {}}  # key not present

        with patch(
            "agent_runner_v2.workflow_packages.extensions_base.get_runner_home",
            return_value=tmp_path,
        ):
            resolve_input_specs(
                result, state, "my_workflow", ["WORKFLOW_SPEC_FILE"]
            )

        assert result["WORKFLOW_SPEC_FILE"] == str(
            specs_dir / "default_spec.md"
        )

    def test_only_spec_keys_are_touched(self, tmp_path):
        """Output artifact keys must not be affected."""
        from agent_runner_v2.workflow_packages.extensions_base import (
            resolve_input_specs,
        )

        specs_dir = tmp_path / "workflows" / "default" / "my_workflow" / "Specs"
        specs_dir.mkdir(parents=True)

        result: dict[str, str] = {}
        state = {
            "artifacts": {
                "WORKFLOW_SPEC_FILE": "my_spec.md",
                "TEST_CRITERIA_FILE": None,
                "COMPONENT_SCHEMA_FILE": None,
            }
        }

        with patch(
            "agent_runner_v2.workflow_packages.extensions_base.get_runner_home",
            return_value=tmp_path,
        ):
            resolve_input_specs(
                result, state, "my_workflow", ["WORKFLOW_SPEC_FILE"]
            )

        # Only WORKFLOW_SPEC_FILE should be in result
        assert "WORKFLOW_SPEC_FILE" in result
        assert "TEST_CRITERIA_FILE" not in result
        assert "COMPONENT_SCHEMA_FILE" not in result

    def test_multiple_spec_keys(self, tmp_path):
        from agent_runner_v2.workflow_packages.extensions_base import (
            resolve_input_specs,
        )

        specs_dir = tmp_path / "workflows" / "default" / "my_workflow" / "Specs"
        specs_dir.mkdir(parents=True)

        result: dict[str, str] = {}
        state = {
            "artifacts": {
                "INPUT_SPEC_FILE": "spec_a.md",
                "CONFIG_SPEC_FILE": "spec_b.md",
            }
        }

        with patch(
            "agent_runner_v2.workflow_packages.extensions_base.get_runner_home",
            return_value=tmp_path,
        ):
            resolve_input_specs(
                result,
                state,
                "my_workflow",
                ["INPUT_SPEC_FILE", "CONFIG_SPEC_FILE"],
            )

        assert result["INPUT_SPEC_FILE"] == str(specs_dir / "spec_a.md")
        assert result["CONFIG_SPEC_FILE"] == str(specs_dir / "spec_b.md")


class TestBuildContextExtensionsGuard:
    """Test that build_context_extensions() preserves resolved spec paths."""

    def test_guard_preserves_resolved_spec(self, tmp_path):
        """resolve_input_specs() result must not be overwritten by the loop."""
        from agent_runner_v2.workflow_packages.extensions_base import (
            resolve_input_specs,
        )

        runner_home = tmp_path / "runner_home"
        specs_dir = runner_home / "workflows" / "default" / "my_workflow" / "Specs"
        specs_dir.mkdir(parents=True)
        workspace_root = tmp_path / "workspace"
        workspace_root.mkdir()

        # Simulate: resolve_input_specs() sets the Specs/ path
        result: dict[str, str] = {}
        state = {
            "artifacts": {
                "WORKFLOW_SPEC_FILE": "D:/workspace/docs/specs/my_spec.md",
                "OUTPUT_FILE": None,
            }
        }

        with patch(
            "agent_runner_v2.workflow_packages.extensions_base.get_runner_home",
            return_value=runner_home,
        ):
            resolve_input_specs(
                result, state, "my_workflow", ["WORKFLOW_SPEC_FILE"]
            )

        # Simulate the loop in build_context_extensions()
        register_artifact_keys = {
            "WORKFLOW_SPEC_FILE": "docs/repo/specs/{slug}.md",
            "OUTPUT_FILE": "docs/repo/runs/{job_id}/OUTPUT-{seq}.md",
        }
        artifacts = state.get("artifacts") or {}
        for key, rel_path in register_artifact_keys.items():
            # Guard: skip if already resolved
            if key in result:
                continue
            if key in artifacts and artifacts[key]:
                existing = artifacts[key]
                if Path(existing).is_absolute():
                    result[key] = existing
                    continue
            result[key] = str(workspace_root / rel_path)

        # WORKFLOW_SPEC_FILE should be the Specs/ path, not the workspace path
        assert result["WORKFLOW_SPEC_FILE"] == str(
            specs_dir / "my_spec.md"
        )
        assert "D:/workspace" not in result["WORKFLOW_SPEC_FILE"]

        # OUTPUT_FILE should be the workspace path (normal resolution)
        assert "workspace" in result["OUTPUT_FILE"]


class TestArMetaBuilderV1SpecResolution:
    """Integration test: real ArMetaBuilderV1Extensions resolves specs correctly."""

    def test_backend_resolved_path_redirected_to_specs_dir(self, tmp_path):
        """When backend sends an absolute workspace path, the workflow
        redirects it to the Specs/ directory."""
        import sys
        from pathlib import Path
        from unittest.mock import patch

        # Load the real workflow extension
        workflow_dir = Path(__file__).parent.parent.parent / "workflows" / "ar_meta_builder_v1"
        sys.path.insert(0, str(workflow_dir))
        try:
            from context_extensions import ArMetaBuilderV1Extensions
        finally:
            sys.path.pop(0)

        ext = ArMetaBuilderV1Extensions()

        runner_home = tmp_path / "runner_home"
        specs_dir = runner_home / "workflows" / "default" / "ar_meta_builder_v1" / "Specs"
        specs_dir.mkdir(parents=True)
        workspace_root = tmp_path / "workspace"
        workspace_root.mkdir()

        # Simulate backend-resolved absolute path for input spec
        state = {
            "artifacts": {
                "WORKFLOW_SPEC_FILE": str(
                    workspace_root / "docs" / "repo" / "workflow_builder" / "specs" / "codebase_to_meta_v1.md"
                ),
                "TEST_CRITERIA_FILE": None,
            }
        }

        with patch(
            "agent_runner_v2.workflow_packages.extensions_base.get_runner_home",
            return_value=runner_home,
        ):
            with patch(
                "agent_runner_v2.runtime_context.get_workspace_root",
                return_value=workspace_root,
            ):
                with patch(
                    "agent_runner_v2.runtime_context.get_governance_runtime_root",
                    return_value=runner_home / "governance",
                ):
                    with patch(
                        "agent_runner_v2.runtime_context.get_platform_runtime_root",
                        return_value=runner_home / "platform",
                    ):
                        result = ext.build_context_extensions(
                            state=state,
                            step="generate_test_criteria",
                            step_cfg={},
                            ctx={},
                        )

        # WORKFLOW_SPEC_FILE must point to Specs/ dir, NOT workspace
        assert result["WORKFLOW_SPEC_FILE"] == str(
            specs_dir / "codebase_to_meta_v1.md"
        )
        assert str(workspace_root) not in result["WORKFLOW_SPEC_FILE"]

        # TEST_CRITERIA_FILE should NOT point to Specs/ dir (it's an output artifact)
        assert "Specs" not in result["TEST_CRITERIA_FILE"]
