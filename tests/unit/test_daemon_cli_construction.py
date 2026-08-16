"""
Unit Test: Daemon CLI Argument Construction
Tests the specific function that transforms Backend JSON data into CLI arguments.
"""
import sys
import os

# Add the repo root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent_runner_v2.daemon_v2 import _build_cli_args

def test_cli_args_include_implementation_name():
    """Verify that if the backend data has implementation_name, it becomes --impl-name."""
    
    # 1. Realistic Backend Response Data (from test_daemon_claim.py result)
    real_run_data = {
        "run_id": "123-abc",
        "run_code": "AMGEN-test123",
        "workflow_name": "agnes_media_gen_v1",
        "project_root": "D:\\MyProjectSpace\\01_Workflows\\agnes-AI",
        "implementation_name": "agnes_media_v1",  # The critical field
        "prompt_selections": {}
    }
    
    real_step_data = {
        "step_run_id": "xyz-789",
        "step_name": "extract_descriptions"
    }

    # 2. Execute the specific function
    cli_args = _build_cli_args(
        run_data=real_run_data,
        step_data=real_step_data,
        project_root=real_run_data["project_root"],
        job_id_to_pass="AMGEN-test123"
    )

    # 3. Verify the output
    print(f"Generated CLI Args: {cli_args}")

    assert "--impl-name" in cli_args, "FAIL: --impl-name flag is missing!"
    
    # Find the index to check the value
    impl_index = cli_args.index("--impl-name")
    assert cli_args[impl_index + 1] == "agnes_media_v1", "FAIL: Value is incorrect!"
    
    print("[OK] SUCCESS: implementation_name was correctly passed to CLI args.")

def test_cli_args_missing_implementation_name():
    """Verify that if the backend data lacks implementation_name, no flag is added."""
    
    run_data = {
        "run_id": "123-abc",
        "run_code": "AMGEN-test123",
        "workflow_name": "agnes_media_gen_v1",
        "project_root": "D:\\MyProjectSpace",
        "implementation_name": None  # Explicitly missing
    }
    
    step_data = {
        "step_run_id": "xyz-789",
        "step_name": "extract_descriptions"
    }

    cli_args = _build_cli_args(
        run_data=run_data,
        step_data=step_data,
        project_root=run_data["project_root"],
        job_id_to_pass="AMGEN-test123"
    )

    assert "--impl-name" not in cli_args, "FAIL: --impl-name should not be present when value is None!"
    print("[OK] SUCCESS: Missing implementation_name handled correctly.")

if __name__ == "__main__":
    test_cli_args_include_implementation_name()
    test_cli_args_missing_implementation_name()
    print("\nAll Unit Tests Passed.")
