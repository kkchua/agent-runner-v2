"""
Unit Test: Prompt Slot Resolution (Real Files)
Verifies that the runtime logic correctly selects different prompt files 
based on implementation_name and prompt_selections.
"""
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the repo root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent_runner_v2.step_execution_runtime import resolve_prompt_slot

def setup_test_bundle(base_dir: Path):
    """Create a realistic bundle structure on disk."""
    # Structure:
    # base_dir/
    #   impls/
    #     impl_v1/
    #       impl.yaml
    #       prompts/
    #         standard.txt
    #         detailed.txt
    
    impl_dir = base_dir / "impls" / "impl_v1"
    prompts_dir = impl_dir / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    # Create real prompt files
    (prompts_dir / "standard.txt").write_text("Standard Prompt Content")
    (prompts_dir / "detailed.txt").write_text("Detailed Prompt Content")

    # Create real impl.yaml
    impl_yaml_content = """
name: impl_v1
description: "Test Implementation V1"

prompt_slots:
  step_1_extract:
    label: "Step 1: Extract"
    default: "standard"
    options:
      - name: "standard"
        file: "prompts/standard.txt"
      - name: "detailed"
        file: "prompts/detailed.txt"
"""
    (impl_dir / "impl.yaml").write_text(impl_yaml_content)
    return base_dir

class MockBundle:
    """Simple mock object to hold bundle_root path."""
    def __init__(self, root):
        self.bundle_root = root

def test_select_detailed_prompt():
    """Test: When user selects 'detailed', code must return 'detailed.txt'."""
    print("\n--- Test 1: Select 'detailed' prompt ---")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        bundle_root = setup_test_bundle(Path(tmpdir))
        bundle = MockBundle(bundle_root)

        # Input data
        step_cfg = {"prompt_file": "{{ slot.step_1_extract }}"}
        state = {"prompt_selections": {"step_1_extract": "detailed"}}
        group_cfg = {"implementation_name": "impl_v1"}

        # Execute
        result_path = resolve_prompt_slot(step_cfg, state, group_cfg, bundle)
        
        print(f"Result Path: {result_path}")
        
        # Assertions
        assert result_path is not None, "FAIL: Path was None"
        assert result_path.endswith("impl_v1\\prompts\\detailed.txt") or result_path.endswith("impl_v1/prompts/detailed.txt"), \
               f"FAIL: Path did not point to detailed.txt. Got: {result_path}"
        assert Path(result_path).exists(), "FAIL: Returned file path does not exist!"
        assert "Detailed Prompt Content" in Path(result_path).read_text(), "FAIL: File content mismatch"
        
        print("[OK] SUCCESS: Correctly resolved to detailed.txt")

def test_select_default_prompt_when_empty():
    """Test: When selection is empty, code must return 'standard.txt' (the default)."""
    print("\n--- Test 2: Default Fallback (Empty Selection) ---")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        bundle_root = setup_test_bundle(Path(tmpdir))
        bundle = MockBundle(bundle_root)

        # Input data: Selection is empty
        step_cfg = {"prompt_file": "{{ slot.step_1_extract }}"}
        state = {"prompt_selections": {}}
        group_cfg = {"implementation_name": "impl_v1"}

        # Execute
        result_path = resolve_prompt_slot(step_cfg, state, group_cfg, bundle)
        
        print(f"Result Path: {result_path}")
        
        # Assertions
        assert result_path is not None, "FAIL: Path was None"
        assert result_path.endswith("impl_v1\\prompts\\standard.txt") or result_path.endswith("impl_v1/prompts/standard.txt"), \
               f"FAIL: Path did not point to standard.txt. Got: {result_path}"
        assert Path(result_path).exists(), "FAIL: Returned file path does not exist!"
        assert "Standard Prompt Content" in Path(result_path).read_text(), "FAIL: File content mismatch"
        
        print("[OK] SUCCESS: Correctly resolved to standard.txt (default)")

if __name__ == "__main__":
    test_select_detailed_prompt()
    test_select_default_prompt_when_empty()
    print("\nAll Real-File Unit Tests Passed.")
