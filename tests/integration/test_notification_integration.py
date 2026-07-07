#!/usr/bin/env python3
"""
Integration test to verify notification hooks are properly wired.
"""
import sys
from pathlib import Path

# Add project root to path (tests/ is a subdirectory of the root)
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_job_state_has_notification_import():
    """Verify job_state.py imports send_notification."""
    project_root = Path(__file__).parent.parent
    with open(project_root / "agent_runner_v2" / "job_state.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "from .notifications import send_notification" in content
    print("✓ job_state.py has notification import")


def test_workflow_router_has_notification_import():
    """Verify workflow_router.py imports send_notification."""
    project_root = Path(__file__).parent.parent
    with open(project_root / "agent_runner_v2" / "workflow_router.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "from .notifications import send_notification" in content
    print("✓ workflow_router.py has notification import")


def test_run_agent_has_notification_calls():
    """Verify run_agent.py has notification calls in worker mode."""
    project_root = Path(__file__).parent.parent
    with open(project_root / "agent_runner_v2" / "run_agent.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    assert 'send_notification("COMPLETED"' in content
    assert 'send_notification("FAILED"' in content
    print("✓ run_agent.py has notification calls")


def test_job_state_completed_hooks():
    """Verify job_state.py calls send_notification on COMPLETED transitions."""
    project_root = Path(__file__).parent.parent
    with open(project_root / "agent_runner_v2" / "job_state.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Count occurrences of send_notification("COMPLETED"
    count = content.count('send_notification("COMPLETED"')
    assert count >= 5, f"Expected at least 5 COMPLETED notifications, found {count}"
    print(f"✓ job_state.py has {count} COMPLETED notification hooks")


def test_workflow_router_failed_hooks():
    """Verify workflow_router.py calls send_notification on FAILED transitions."""
    project_root = Path(__file__).parent.parent
    with open(project_root / "agent_runner_v2" / "workflow_router.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Count occurrences of send_notification("FAILED"
    count = content.count('send_notification("FAILED"')
    assert count >= 2, f"Expected at least 2 FAILED notifications, found {count}"
    print(f"✓ workflow_router.py has {count} FAILED notification hooks")


def test_env_example_has_pushover_vars():
    """Verify .env.example includes Pushover configuration."""
    project_root = Path(__file__).parent.parent
    with open(project_root / ".env.example", "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "PUSHOVER_API_TOKEN" in content
    assert "PUSHOVER_USER_KEY" in content
    print("✓ .env.example has Pushover credentials")


def test_config_json_example_exists():
    """Verify config.json.example exists and has notification section."""
    project_root = Path(__file__).parent.parent
    assert (project_root / "config.json.example").exists()
    
    with open(project_root / "config.json.example", "r", encoding="utf-8") as f:
        content = f.read()
    
    assert '"notification"' in content
    assert '"enabled"' in content
    assert '"pushover"' in content
    print("✓ config.json.example exists with notification section")


def main():
    """Run all integration tests."""
    print("Testing notification integration...\n")
    
    test_job_state_has_notification_import()
    test_workflow_router_has_notification_import()
    test_run_agent_has_notification_calls()
    test_job_state_completed_hooks()
    test_workflow_router_failed_hooks()
    test_env_example_has_pushover_vars()
    test_config_json_example_exists()
    
    print("\n✅ All integration tests passed!")


if __name__ == "__main__":
    main()
