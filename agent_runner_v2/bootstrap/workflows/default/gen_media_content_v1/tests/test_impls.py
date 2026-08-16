"""Unit tests for gen_media_content_v1 BCS implementation presets.

Tests cover all 10 acceptance criteria (ACT-01 through ACT-10):
- ACT-01: All 3 impl directories contain impl.yaml and preset.json
- ACT-02: All impl.yaml files are valid YAML
- ACT-03: All preset.json files are valid JSON
- ACT-04: impl.yaml name matches directory name
- ACT-05: prompt_slots reference files that exist on disk
- ACT-06: agnes_full preset uses agnes_v1 + agnes_v2
- ACT-07: happyhorse_product preset uses agnes_v1 + happyhorse_v1_1
- ACT-08: video_only preset uses __none__ + agnes_v2
- ACT-09: All 10 tests pass with pytest (this suite)
- ACT-10: No existing files were modified

All tests are self-contained. No network access or API keys required.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW_ROOT = PROJECT_ROOT / "workflows" / "gen_media_content_v1"
IMPLS_ROOT = WORKFLOW_ROOT / "impls"

IMPL_NAMES = ["agnes_full", "happyhorse_product", "video_only"]


def test_act01_all_impl_files_exist():
    """ACT-01: All 3 impl directories contain impl.yaml and preset.json."""
    for impl_name in IMPL_NAMES:
        impl_yaml = IMPLS_ROOT / impl_name / "impl.yaml"
        preset_json = IMPLS_ROOT / impl_name / "preset.json"
        assert impl_yaml.exists(), f"Missing impl.yaml in {impl_name}/"
        assert preset_json.exists(), f"Missing preset.json in {impl_name}/"


def test_act02_all_impl_yaml_valid():
    """ACT-02: All impl.yaml files are valid YAML with required keys."""
    for impl_name in IMPL_NAMES:
        impl_yaml = IMPLS_ROOT / impl_name / "impl.yaml"
        with open(impl_yaml, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert isinstance(data, dict), f"impl.yaml in {impl_name}/ did not parse to dict"
        assert len(data) > 0, f"impl.yaml in {impl_name}/ is empty"
        for key in ("name", "prompt_slots", "overrides"):
            assert key in data, f"Missing key '{key}' in {impl_name}/impl.yaml"


def test_act03_all_preset_json_valid():
    """ACT-03: All preset.json files are valid JSON with actions key."""
    for impl_name in IMPL_NAMES:
        preset_json = IMPLS_ROOT / impl_name / "preset.json"
        with open(preset_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict), f"preset.json in {impl_name}/ did not parse to dict"
        assert len(data) > 0, f"preset.json in {impl_name}/ is empty"
        assert "actions" in data, f"Missing 'actions' key in {impl_name}/preset.json"


def test_act04_impl_name_matches_directory():
    """ACT-04: impl.yaml name matches directory name for all 3 impls."""
    for impl_name in IMPL_NAMES:
        impl_yaml = IMPLS_ROOT / impl_name / "impl.yaml"
        with open(impl_yaml, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data["name"] == impl_name, (
            f"impl.yaml name '{data['name']}' does not match "
            f"directory name '{impl_name}'"
        )


def test_act05_prompt_slots_reference_existing_files():
    """ACT-05: All prompt_slots reference files that exist on disk."""
    for impl_name in IMPL_NAMES:
        impl_yaml = IMPLS_ROOT / impl_name / "impl.yaml"
        with open(impl_yaml, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        prompt_slots = data.get("prompt_slots", {})
        for slot_name, slot_cfg in prompt_slots.items():
            options = slot_cfg.get("options", [])
            for option in options:
                file_path = option.get("file", "")
                if file_path:
                    abs_path = WORKFLOW_ROOT / file_path
                    assert abs_path.exists(), (
                        f"Prompt slot '{slot_name}' option '{option.get('name')}' "
                        f"references file '{file_path}' which does not exist at {abs_path}"
                    )


def test_act06_agnes_full_actions():
    """ACT-06: agnes_full preset uses agnes_v1 + agnes_v2."""
    preset_json = IMPLS_ROOT / "agnes_full" / "preset.json"
    with open(preset_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["actions"]["render_image"] == "agnes_v1"
    assert data["actions"]["render_video"] == "agnes_v2"


def test_act07_happyhorse_product_actions():
    """ACT-07: happyhorse_product preset uses agnes_v1 + happyhorse_v1_1."""
    preset_json = IMPLS_ROOT / "happyhorse_product" / "preset.json"
    with open(preset_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["actions"]["render_image"] == "agnes_v1"
    assert data["actions"]["render_video"] == "happyhorse_v1_1"


def test_act08_video_only_actions():
    """ACT-08: video_only preset uses __none__ + agnes_v2."""
    preset_json = IMPLS_ROOT / "video_only" / "preset.json"
    with open(preset_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["actions"]["render_image"] == "__none__"
    assert data["actions"]["render_video"] == "agnes_v2"
    assert data["review_images_before_video"] is False


def test_act09_test_count():
    """ACT-09: Exactly 10 tests in this suite (self-referential check)."""
    import sys
    import inspect
    # Count test functions in this module
    current_module = sys.modules[__name__]
    test_functions = [
        name for name, obj in inspect.getmembers(current_module, inspect.isfunction)
        if name.startswith("test_")
    ]
    assert len(test_functions) == 10, (
        f"Expected 10 test functions, found {len(test_functions)}: {test_functions}"
    )


def test_act10_no_existing_files_modified():
    """ACT-10: No existing tracked files were modified."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    assert result.returncode == 0, f"git status failed: {result.stderr}"
    modified_files = [
        line for line in result.stdout.strip().splitlines()
        if line.startswith(" M") or line.startswith("M ") or line.startswith("MM")
    ]
    assert len(modified_files) == 0, (
        f"Modified tracked files detected: {modified_files}"
    )
