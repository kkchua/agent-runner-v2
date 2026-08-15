"""Unit tests for Base Composition Standard (BCS) prompt slot resolution."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

import pytest

# Import the function we are testing. 
# We assume it has been refactored into a helper in step_execution_runtime.
from agent_runner_v2.step_execution_runtime import resolve_prompt_slot


class TestResolvePromptSlot:
    """Tests for resolve_prompt_slot helper function."""

    def test_no_slot_reference(self):
        """Should return None if prompt_file is not a slot reference."""
        step_cfg = {"prompt_file": "prompts/standard.txt"}
        state = {}
        group_cfg = {"implementation_name": "impl_a"}
        bundle = MagicMock()
        
        result = resolve_prompt_slot(step_cfg, state, group_cfg, bundle)
        assert result is None

    def test_successful_resolution_with_default(self):
        """Should resolve to default option if no selection is provided."""
        step_cfg = {"prompt_file": "{{ slot.step_1_extract }}"}
        state = {}
        group_cfg = {"implementation_name": "impl_a"}
        
        # Mock bundle
        bundle = MagicMock()
        bundle.bundle_root = Path(tempfile.gettempdir())
        
        # Mock impl.yaml content
        mock_impl_data = {
            "prompt_slots": {
                "step_1_extract": {
                    "label": "Step 1",
                    "default": "standard",
                    "options": [
                        {"name": "standard", "file": "prompts/step_1/standard.txt"},
                        {"name": "detailed", "file": "prompts/step_1/detailed.txt"}
                    ]
                }
            }
        }

        # Mock the bundle root existence check and yaml loading
        with patch("agent_runner_v2.step_execution_runtime.yaml") as mock_yaml, \
             patch("builtins.open", mock_open(read_data="dummy")):
            mock_yaml.safe_load.return_value = mock_impl_data
            
            # We need to ensure the path exists for the function to proceed
            with patch.object(Path, "exists", return_value=True):
                result = resolve_prompt_slot(step_cfg, state, group_cfg, bundle)
                
                assert result.endswith("impls\\impl_a\\prompts\\step_1\\standard.txt") or result.endswith("impls/impl_a/prompts/step_1/standard.txt")

    def test_successful_resolution_with_selection(self):
        """Should resolve to the user-selected option."""
        step_cfg = {"prompt_file": "{{ slot.step_1_extract }}"}
        state = {"prompt_selections": {"step_1_extract": "detailed"}}
        group_cfg = {"implementation_name": "impl_a"}
        
        bundle = MagicMock()
        bundle.bundle_root = Path(tempfile.gettempdir())
        
        mock_impl_data = {
            "prompt_slots": {
                "step_1_extract": {
                    "label": "Step 1",
                    "default": "standard",
                    "options": [
                        {"name": "standard", "file": "prompts/step_1/standard.txt"},
                        {"name": "detailed", "file": "prompts/step_1/detailed.txt"}
                    ]
                }
            }
        }

        with patch("agent_runner_v2.step_execution_runtime.yaml") as mock_yaml, \
             patch("builtins.open", mock_open(read_data="dummy")):
            mock_yaml.safe_load.return_value = mock_impl_data
            
            with patch.object(Path, "exists", return_value=True):
                result = resolve_prompt_slot(step_cfg, state, group_cfg, bundle)
                
                assert result.endswith("impls\\impl_a\\prompts\\step_1\\detailed.txt") or result.endswith("impls/impl_a/prompts/step_1/detailed.txt")

    def test_fallback_on_invalid_selection(self):
        """Should fallback to default if selection is invalid."""
        step_cfg = {"prompt_file": "{{ slot.step_1_extract }}"}
        state = {"prompt_selections": {"step_1_extract": "non_existent_option"}}
        group_cfg = {"implementation_name": "impl_a"}
        
        bundle = MagicMock()
        bundle.bundle_root = Path(tempfile.gettempdir())
        
        mock_impl_data = {
            "prompt_slots": {
                "step_1_extract": {
                    "label": "Step 1",
                    "default": "standard",
                    "options": [
                        {"name": "standard", "file": "prompts/step_1/standard.txt"}
                    ]
                }
            }
        }

        with patch("agent_runner_v2.step_execution_runtime.yaml") as mock_yaml, \
             patch("builtins.open", mock_open(read_data="dummy")):
            mock_yaml.safe_load.return_value = mock_impl_data
            
            with patch.object(Path, "exists", return_value=True):
                result = resolve_prompt_slot(step_cfg, state, group_cfg, bundle)
                
                # Should fall back to standard because 'non_existent_option' is invalid
                assert result.endswith("impls\\impl_a\\prompts\\step_1\\standard.txt") or result.endswith("impls/impl_a/prompts/step_1/standard.txt")

    def test_shared_prompt_fallback(self):
        """Should fall back to shared prompt when impl-specific prompt does not exist."""
        step_cfg = {"prompt_file": "{{ slot.step_1_extract }}"}
        state = {}
        group_cfg = {"implementation_name": "impl_a"}

        bundle = MagicMock()
        bundle.bundle_root = Path(tempfile.mkdtemp())

        # Create impl.yaml (so it IS found)
        impl_dir = bundle.bundle_root / "impls" / "impl_a"
        impl_dir.mkdir(parents=True, exist_ok=True)
        impl_yaml = impl_dir / "impl.yaml"
        impl_yaml.write_text("prompt_slots: {}", encoding="utf-8")

        # Do NOT create the impl-specific prompt file
        # (impls/impl_a/prompts/step_1/standard.txt does not exist)
        # The shared prompt file also does not exist on disk, but the
        # fallback should still resolve to bundle_root/prompts/... path.

        mock_impl_data = {
            "prompt_slots": {
                "step_1_extract": {
                    "label": "Step 1",
                    "default": "standard",
                    "options": [
                        {"name": "standard", "file": "prompts/step_1/standard.txt"},
                    ]
                }
            }
        }

        with patch("agent_runner_v2.step_execution_runtime.yaml") as mock_yaml, \
             patch("builtins.open", mock_open(read_data="dummy")):
            mock_yaml.safe_load.return_value = mock_impl_data

            result = resolve_prompt_slot(step_cfg, state, group_cfg, bundle)

            # Should resolve to shared path (bundle_root/prompts/...),
            # NOT impl-specific path (bundle_root/impls/impl_a/prompts/...)
            assert result is not None
            assert "impls" not in str(result)
            assert result.endswith("prompts\\step_1\\standard.txt") or result.endswith("prompts/step_1/standard.txt")

    def test_missing_impl_yaml(self):
        """Should fall back to convention path when impl.yaml is not found."""
        step_cfg = {"prompt_file": "{{ slot.step_1_extract }}"}
        state = {}
        group_cfg = {"implementation_name": "impl_a"}

        bundle = MagicMock()
        tmpdir = Path(tempfile.mkdtemp())
        bundle.bundle_root = tmpdir

        # Create convention path: prompts/step_1_extract/standard.txt
        convention_dir = tmpdir / "prompts" / "step_1_extract"
        convention_dir.mkdir(parents=True, exist_ok=True)
        convention_file = convention_dir / "standard.txt"
        convention_file.write_text("test prompt", encoding="utf-8")

        # impl.yaml does NOT exist
        result = resolve_prompt_slot(step_cfg, state, group_cfg, bundle)
        assert result is not None
        assert str(result).endswith("standard.txt")
        assert "prompts" in str(result)

    def test_missing_implementation_name(self):
        """Should fall back to convention path when no implementation_name is set."""
        step_cfg = {"prompt_file": "{{ slot.step_1_extract }}"}
        state = {}
        group_cfg = {}  # No implementation_name

        bundle = MagicMock()
        tmpdir = Path(tempfile.mkdtemp())
        bundle.bundle_root = tmpdir

        # Create convention path
        convention_dir = tmpdir / "prompts" / "step_1_extract"
        convention_dir.mkdir(parents=True, exist_ok=True)
        convention_file = convention_dir / "standard.txt"
        convention_file.write_text("test prompt", encoding="utf-8")

        result = resolve_prompt_slot(step_cfg, state, group_cfg, bundle)
        assert result is not None
        assert str(result).endswith("standard.txt")

    def test_convention_fallback_not_found(self):
        """Should return None when neither impl.yaml nor convention path exists."""
        step_cfg = {"prompt_file": "{{ slot.step_1_extract }}"}
        state = {}
        group_cfg = {}  # No implementation_name

        bundle = MagicMock()
        tmpdir = Path(tempfile.mkdtemp())
        bundle.bundle_root = tmpdir

        # No convention path created, no impl.yaml
        result = resolve_prompt_slot(step_cfg, state, group_cfg, bundle)
        assert result is None

    def test_convention_fallback_with_impl_name_no_prompt_slots(self):
        """Should fall back to convention when impl.yaml exists but has no prompt_slots."""
        step_cfg = {"prompt_file": "{{ slot.my_step }}"}
        state = {}
        group_cfg = {"implementation_name": "standard"}

        bundle = MagicMock()
        tmpdir = Path(tempfile.mkdtemp())
        bundle.bundle_root = tmpdir

        # Create impl.yaml with no prompt_slots
        impl_dir = tmpdir / "impls" / "standard"
        impl_dir.mkdir(parents=True, exist_ok=True)
        (impl_dir / "impl.yaml").write_text("name: standard\n", encoding="utf-8")

        # Create convention path
        convention_dir = tmpdir / "prompts" / "my_step"
        convention_dir.mkdir(parents=True, exist_ok=True)
        (convention_dir / "standard.txt").write_text("test", encoding="utf-8")

        result = resolve_prompt_slot(step_cfg, state, group_cfg, bundle)
        assert result is not None
        assert "prompts" in str(result)
        assert "my_step" in str(result)
