from __future__ import annotations

from agent_runner_v2 import notification_manager
from agent_runner_v2.notification_manager import _enrich_context


def test_enrich_context_preserves_manual_job_id() -> None:
    enriched = _enrich_context(
        {
            "job_id": "00CORE-001",
            "template_group": "00_core_governance_bootstrap_v1",
            "workflow_name": "00_core_governance_bootstrap_v1",
        }
    )

    assert enriched["job_id"] == "00CORE-001"
    assert enriched["template_group"] == "00_core_governance_bootstrap_v1"
    assert enriched["workflow_name"] == "00_core_governance_bootstrap_v1"


def test_enrich_context_maps_daemon_run_code_to_job_id() -> None:
    enriched = _enrich_context(
        {
            "id": "run-1",
            "run_code": "00CORE-20260714-003",
            "workflow_name": "00_core_governance_bootstrap_v1",
            "status": "completed",
        }
    )

    assert enriched["job_id"] == "00CORE-20260714-003"
    assert enriched["run_code"] == "00CORE-20260714-003"
    assert enriched["workflow_run_id"] == "run-1"
    assert enriched["template_group"] == "00_core_governance_bootstrap_v1"
    assert enriched["workflow_name"] == "00_core_governance_bootstrap_v1"


def test_send_step_notification_sends_step_completed_when_event_enabled(monkeypatch) -> None:
    monkeypatch.setattr(notification_manager, "should_send_notifications", lambda: True)
    monkeypatch.setattr(notification_manager, "_is_step_event_enabled", lambda status: True)
    monkeypatch.setattr(notification_manager, "_send_notification", lambda status, context: True)

    result = notification_manager.send_step_notification(
        "STEP_COMPLETED",
        {"job_id": "JOB-1"},
        "generate_docs",
        {"enable_notifications": True},
    )

    assert result is True


def test_send_step_notification_honors_step_event_toggle(monkeypatch) -> None:
    monkeypatch.setattr(notification_manager, "should_send_notifications", lambda: True)
    monkeypatch.setattr(notification_manager, "_is_step_event_enabled", lambda status: False)
    monkeypatch.setattr(notification_manager, "_send_notification", lambda status, context: True)

    result = notification_manager.send_step_notification(
        "STEP_COMPLETED",
        {"job_id": "JOB-1"},
        "generate_docs",
        {"enable_notifications": True},
    )

    assert result is False


def test_send_step_notification_still_sends_step_failed(monkeypatch) -> None:
    captured: dict[str, object] = {}

    monkeypatch.setattr(notification_manager, "should_send_notifications", lambda: True)
    monkeypatch.setattr(notification_manager, "_is_step_event_enabled", lambda status: True)

    def fake_send(status, context):
        captured["status"] = status
        captured["context"] = context
        return True

    monkeypatch.setattr(notification_manager, "_send_notification", fake_send)

    result = notification_manager.send_step_notification(
        "STEP_FAILED",
        {"job_id": "JOB-1", "template_group": "wf"},
        "generate_docs",
        {"enable_notifications": True},
    )

    assert result is True
    assert captured["status"] == "STEP_FAILED"
    assert captured["context"]["step_name"] == "generate_docs"


def test_send_step_notification_sends_step_rejected(monkeypatch) -> None:
    captured: dict[str, object] = {}

    monkeypatch.setattr(notification_manager, "should_send_notifications", lambda: True)
    monkeypatch.setattr(notification_manager, "_is_step_event_enabled", lambda status: True)

    def fake_send(status, context):
        captured["status"] = status
        captured["context"] = context
        return True

    monkeypatch.setattr(notification_manager, "_send_notification", fake_send)

    result = notification_manager.send_step_notification(
        "STEP_REJECTED",
        {"job_id": "JOB-1", "template_group": "wf"},
        "review_docs",
        {"enable_notifications": True},
    )

    assert result is True
    assert captured["status"] == "STEP_REJECTED"
    assert captured["context"]["step_name"] == "review_docs"


def test_send_step_notification_includes_step_duration_seconds(monkeypatch) -> None:
    captured: dict[str, object] = {}

    monkeypatch.setattr(notification_manager, "should_send_notifications", lambda: True)
    monkeypatch.setattr(notification_manager, "_is_step_event_enabled", lambda status: True)

    def fake_send(status, context):
        captured["status"] = status
        captured["context"] = context
        return True

    monkeypatch.setattr(notification_manager, "_send_notification", fake_send)

    result = notification_manager.send_step_notification(
        "STEP_FAILED",
        {
            "job_id": "JOB-1",
            "template_group": "wf",
            "step_usage": {
                "review_docs": {
                    "duration_ms": 1250,
                }
            },
        },
        "review_docs",
        {"enable_notifications": True},
    )

    assert result is True
    assert captured["context"]["step_duration_seconds"] == 1.25
