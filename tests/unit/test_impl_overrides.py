"""Unit tests for implementation override resolution (impl.yaml).

Tests cover:
- load_workflow_package() with impl_name parameter
- _load_impl_overrides() YAML parsing
- _apply_impl_overrides() StepConfig replacement
- Validation: unknown steps, missing prompt/action, malformed YAML
- Integration: bundle_to_template_group_dict reflects overrides
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from agent_runner_v2.workflow_packages.loader import (
    _apply_impl_overrides,
    _load_impl_overrides,
    load_workflow_package,
)


# ---------------------------------------------------------------------------
# Helpers — build minimal workflow packages in tmp_path
# ---------------------------------------------------------------------------

_MINIMAL_TOML = """\
[workflow]
name = "test_wf"
job_prefix = "TEST"
init_step = "step_a"

[[step]]
name = "step_a"
prompt = "prompts/01_step_a.txt"
onsuccess = "step_b"

[[step]]
name = "step_b"
action = "do_thing"
onsuccess = "step_c"

[[step]]
name = "step_c"
prompt = "prompts/03_step_c.txt"
"""


def _make_workflow(tmp_path: Path, toml_content: str = _MINIMAL_TOML) -> Path:
    """Create a minimal workflow package directory with workflow.toml."""
    pkg = tmp_path / "test_wf"
    pkg.mkdir()
    (pkg / "workflow.toml").write_text(toml_content, encoding="utf-8")
    # Create referenced prompt files so path resolution doesn't fail
    prompts = pkg / "prompts"
    prompts.mkdir()
    (prompts / "01_step_a.txt").write_text("prompt a", encoding="utf-8")
    (prompts / "03_step_c.txt").write_text("prompt c", encoding="utf-8")
    return pkg


def _make_impl(
    pkg_dir: Path,
    impl_name: str,
    impl_yaml: dict,
    actions_py: str | None = None,
    impl_prompts: dict[str, str] | None = None,
) -> Path:
    """Create an impl directory with impl.yaml and optional extras."""
    impl_dir = pkg_dir / "impls" / impl_name
    impl_dir.mkdir(parents=True)
    (impl_dir / "impl.yaml").write_text(
        yaml.dump(impl_yaml, default_flow_style=False), encoding="utf-8"
    )
    if actions_py:
        (impl_dir / "actions.py").write_text(actions_py, encoding="utf-8")
    if impl_prompts:
        prompts_dir = impl_dir / "prompts"
        prompts_dir.mkdir()
        for name, content in impl_prompts.items():
            (prompts_dir / name).write_text(content, encoding="utf-8")
    return impl_dir


# ---------------------------------------------------------------------------
# Tests — load_workflow_package with impl_name
# ---------------------------------------------------------------------------


class TestLoadWorkflowPackageWithImpl:
    """load_workflow_package() accepts impl_name and applies overrides."""

    def test_no_impl_name_returns_default(self, tmp_path):
        pkg = _make_workflow(tmp_path)
        bundle = load_workflow_package(pkg)
        assert bundle.steps["step_a"].prompt_file == "prompts/01_step_a.txt"
        assert bundle.steps["step_b"].action == "do_thing"
        assert bundle.steps["step_c"].prompt_file == "prompts/03_step_c.txt"

    def test_impl_name_default_is_noop(self, tmp_path):
        pkg = _make_workflow(tmp_path)
        bundle = load_workflow_package(pkg, impl_name="default")
        assert bundle.steps["step_a"].prompt_file == "prompts/01_step_a.txt"
        assert bundle.steps["step_b"].action == "do_thing"

    def test_impl_overrides_prompt(self, tmp_path):
        pkg = _make_workflow(tmp_path)
        _make_impl(
            pkg, "anime",
            {"name": "anime", "overrides": {
                "step_a": {"prompt": "impls/anime/prompts/01_step_a.txt"},
            }},
            impl_prompts={"01_step_a.txt": "anime prompt a"},
        )
        bundle = load_workflow_package(pkg, impl_name="anime")
        # Overridden step
        assert bundle.steps["step_a"].prompt_file == "impls/anime/prompts/01_step_a.txt"
        # Non-overridden steps unchanged
        assert bundle.steps["step_b"].action == "do_thing"
        assert bundle.steps["step_c"].prompt_file == "prompts/03_step_c.txt"

    def test_impl_overrides_action(self, tmp_path):
        pkg = _make_workflow(tmp_path)
        _make_impl(
            pkg, "watercolor",
            {"name": "watercolor", "overrides": {
                "step_b": {"action": "render_watercolor"},
            }},
        )
        bundle = load_workflow_package(pkg, impl_name="watercolor")
        assert bundle.steps["step_b"].action == "render_watercolor"
        # Others unchanged
        assert bundle.steps["step_a"].prompt_file == "prompts/01_step_a.txt"
        assert bundle.steps["step_c"].prompt_file == "prompts/03_step_c.txt"

    def test_impl_overrides_both_prompt_and_action(self, tmp_path):
        pkg = _make_workflow(tmp_path)
        _make_impl(
            pkg, "full_override",
            {"name": "full_override", "overrides": {
                "step_a": {"prompt": "impls/full_override/prompts/new_a.txt"},
                "step_b": {"action": "new_action"},
            }},
            impl_prompts={"new_a.txt": "new prompt"},
        )
        bundle = load_workflow_package(pkg, impl_name="full_override")
        assert bundle.steps["step_a"].prompt_file == "impls/full_override/prompts/new_a.txt"
        assert bundle.steps["step_b"].action == "new_action"
        # step_c not overridden
        assert bundle.steps["step_c"].prompt_file == "prompts/03_step_c.txt"

    def test_partial_override_only_changes_listed_steps(self, tmp_path):
        """Override only 1 of 3 steps — the other 2 must be untouched."""
        pkg = _make_workflow(tmp_path)
        _make_impl(
            pkg, "minimal",
            {"name": "minimal", "overrides": {
                "step_c": {"prompt": "impls/minimal/prompts/new_c.txt"},
            }},
            impl_prompts={"new_c.txt": "new c"},
        )
        bundle = load_workflow_package(pkg, impl_name="minimal")
        assert bundle.steps["step_a"].prompt_file == "prompts/01_step_a.txt"
        assert bundle.steps["step_b"].action == "do_thing"
        assert bundle.steps["step_c"].prompt_file == "impls/minimal/prompts/new_c.txt"

    def test_empty_overrides_is_valid(self, tmp_path):
        """An impl.yaml with empty overrides: {} is valid (identical to default)."""
        pkg = _make_workflow(tmp_path)
        _make_impl(pkg, "noop", {"name": "noop", "overrides": {}})
        bundle = load_workflow_package(pkg, impl_name="noop")
        assert bundle.steps["step_a"].prompt_file == "prompts/01_step_a.txt"
        assert bundle.steps["step_b"].action == "do_thing"

    def test_step_order_preserved(self, tmp_path):
        pkg = _make_workflow(tmp_path)
        _make_impl(
            pkg, "anime",
            {"overrides": {"step_a": {"prompt": "impls/anime/prompts/x.txt"}}},
            impl_prompts={"x.txt": "x"},
        )
        bundle = load_workflow_package(pkg, impl_name="anime")
        assert bundle.step_order == ["step_a", "step_b", "step_c"]


# ---------------------------------------------------------------------------
# Tests — validation errors
# ---------------------------------------------------------------------------


class TestImplOverrideValidation:
    """Invalid impl.yaml files produce clear errors."""

    def test_missing_impl_yaml_raises(self, tmp_path):
        pkg = _make_workflow(tmp_path)
        with pytest.raises(FileNotFoundError, match="impl.yaml"):
            load_workflow_package(pkg, impl_name="nonexistent")

    def test_unknown_step_reference_raises(self, tmp_path):
        pkg = _make_workflow(tmp_path)
        _make_impl(
            pkg, "bad",
            {"overrides": {"nonexistent_step": {"prompt": "x.txt"}}},
        )
        with pytest.raises(ValueError, match="unknown step 'nonexistent_step'"):
            load_workflow_package(pkg, impl_name="bad")

    def test_override_without_prompt_or_action_raises(self, tmp_path):
        pkg = _make_workflow(tmp_path)
        _make_impl(
            pkg, "empty_override",
            {"overrides": {"step_a": {"description": "no prompt or action"}}},
        )
        with pytest.raises(ValueError, match="at least one of: prompt, action"):
            load_workflow_package(pkg, impl_name="empty_override")

    def test_malformed_impl_yaml_raises(self, tmp_path):
        pkg = _make_workflow(tmp_path)
        impl_dir = pkg / "impls" / "broken"
        impl_dir.mkdir(parents=True)
        (impl_dir / "impl.yaml").write_text("not: a: valid: yaml: [", encoding="utf-8")
        with pytest.raises(Exception):
            load_workflow_package(pkg, impl_name="broken")


# ---------------------------------------------------------------------------
# Tests — _load_impl_overrides standalone
# ---------------------------------------------------------------------------


class TestLoadImplOverrides:
    """Direct tests for the _load_impl_overrides helper."""

    def test_returns_parsed_dict(self, tmp_path):
        pkg = _make_workflow(tmp_path)
        _make_impl(pkg, "test", {"name": "test", "overrides": {"step_a": {"prompt": "x"}}})
        data = _load_impl_overrides(pkg, "test")
        assert data["name"] == "test"
        assert "overrides" in data

    def test_file_not_found(self, tmp_path):
        pkg = _make_workflow(tmp_path)
        with pytest.raises(FileNotFoundError):
            _load_impl_overrides(pkg, "missing")


# ---------------------------------------------------------------------------
# Tests — integration with bundle_to_template_group_dict
# ---------------------------------------------------------------------------


class TestImplOverridesInAdapter:
    """Overrides must propagate through bundle_to_template_group_dict."""

    def test_overridden_prompt_resolves_to_absolute(self, tmp_path):
        from agent_runner_v2.workflow_packages.loader import (
            bundle_to_template_group_dict,
        )

        pkg = _make_workflow(tmp_path)
        _make_impl(
            pkg, "anime",
            {"overrides": {
                "step_a": {"prompt": "impls/anime/prompts/01_step_a.txt"},
            }},
            impl_prompts={"01_step_a.txt": "anime prompt"},
        )
        bundle = load_workflow_package(pkg, impl_name="anime")
        group_dict = bundle_to_template_group_dict(bundle)

        step_a_cfg = group_dict["step_configs"]["step_a"]
        # Prompt path should be resolved to absolute
        assert "impls" in step_a_cfg["prompt_file"]
        assert "anime" in step_a_cfg["prompt_file"]
        assert Path(step_a_cfg["prompt_file"]).is_absolute()

    def test_non_overridden_steps_unchanged_in_adapter(self, tmp_path):
        from agent_runner_v2.workflow_packages.loader import (
            bundle_to_template_group_dict,
        )

        pkg = _make_workflow(tmp_path)
        _make_impl(
            pkg, "anime",
            {"overrides": {
                "step_a": {"prompt": "impls/anime/prompts/01_step_a.txt"},
            }},
            impl_prompts={"01_step_a.txt": "anime prompt"},
        )
        bundle = load_workflow_package(pkg, impl_name="anime")
        group_dict = bundle_to_template_group_dict(bundle)

        # step_b action unchanged
        assert group_dict["step_configs"]["step_b"]["action"] == "do_thing"
        # step_c prompt unchanged
        step_c_prompt = group_dict["step_configs"]["step_c"]["prompt_file"]
        assert "03_step_c.txt" in step_c_prompt
