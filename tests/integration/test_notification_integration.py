#!/usr/bin/env python3
"""
Integration test to verify notification hooks are properly wired.
"""
import sys
from pathlib import Path

# Add project root to path (tests/ is a subdirectory of the root)
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_runner_v2.bundle_loader import package_bootstrap_root


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_job_state_has_notification_import():
    """Verify job_state.py imports notification manager hooks."""
    with open(PROJECT_ROOT / "agent_runner_v2" / "job_state.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert "from .notification_manager import send_workflow_notification, send_step_notification" in content


def test_workflow_router_has_notification_import():
    """Verify workflow_router.py imports notification manager hooks."""
    with open(PROJECT_ROOT / "agent_runner_v2" / "workflow_router.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert "from .notification_manager import send_workflow_notification, send_step_notification" in content


def test_run_agent_uses_shared_worker_runtime_helpers():
    """Verify run_agent.py uses shared worker runtime helpers."""
    with open(PROJECT_ROOT / "agent_runner_v2" / "run_agent.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert "_build_worker_request_payload" in content
    assert "_prepare_step_execution" in content


def test_job_state_completed_hooks():
    """Verify job_state.py calls workflow and step completion hooks."""
    with open(PROJECT_ROOT / "agent_runner_v2" / "job_state.py", "r", encoding="utf-8") as f:
        content = f.read()

    completed_count = content.count('send_workflow_notification("COMPLETED"')
    step_count = content.count('send_step_notification("STEP_COMPLETED"')
    assert completed_count >= 5, f"Expected at least 5 COMPLETED workflow notifications, found {completed_count}"
    assert step_count >= 1, f"Expected at least 1 STEP_COMPLETED hook, found {step_count}"


def test_workflow_router_failure_hooks():
    """Verify workflow_router.py calls workflow and step failure hooks."""
    with open(PROJECT_ROOT / "agent_runner_v2" / "workflow_router.py", "r", encoding="utf-8") as f:
        content = f.read()

    failed_count = content.count('send_workflow_notification("FAILED"')
    waiting_count = content.count('send_workflow_notification("WAITING_FOR_HUMAN_INTERVENTION"')
    step_failed_count = content.count('send_step_notification("STEP_FAILED"')
    step_rejected_count = content.count('send_step_notification("STEP_REJECTED"')
    assert failed_count >= 2, f"Expected at least 2 FAILED workflow notifications, found {failed_count}"
    assert waiting_count >= 2, f"Expected at least 2 WAITING_FOR_HUMAN_INTERVENTION notifications, found {waiting_count}"
    assert step_failed_count >= 1, f"Expected at least 1 STEP_FAILED hook, found {step_failed_count}"
    assert step_rejected_count >= 1, f"Expected at least 1 STEP_REJECTED hook, found {step_rejected_count}"


def test_env_example_has_pushover_vars():
    """Verify .env.example includes Pushover configuration."""
    with open(PROJECT_ROOT / ".env.example", "r", encoding="utf-8") as f:
        content = f.read()

    assert "PUSHOVER_API_TOKEN" in content
    assert "PUSHOVER_USER_KEY" in content


def test_config_json_example_exists():
    """Verify packaged config.json.example has notification section."""
    config_example = package_bootstrap_root() / "config.json.example"
    assert config_example.exists()

    with open(config_example, "r", encoding="utf-8") as f:
        content = f.read()

    assert '"notification"' in content
    assert '"enabled"' in content
    assert '"pushover"' in content
    assert '"step_events"' in content
