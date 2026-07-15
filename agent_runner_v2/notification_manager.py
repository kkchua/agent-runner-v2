"""
notification_manager.py - Centralized notification management for all execution modes.

Provides unified interface for sending workflow and step notifications with consistent
context enrichment and logging.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .notifications import send_notification as _send_notification


def should_send_notifications() -> bool:
    """Check if notifications are enabled globally."""
    try:
        config_path = Path.home() / ".ukbe-runner" / "config.json"
        if not config_path.exists():
            return False
        config = json.loads(config_path.read_text(encoding="utf-8"))
        return bool(config.get("notification", {}).get("enabled", False))
    except Exception:
        return False


def _load_notification_settings() -> dict[str, Any]:
    try:
        config_path = Path.home() / ".ukbe-runner" / "config.json"
        if not config_path.exists():
            return {}
        config = json.loads(config_path.read_text(encoding="utf-8"))
        notification_cfg = config.get("notification", {})
        return notification_cfg if isinstance(notification_cfg, dict) else {}
    except Exception:
        return {}


def _is_step_event_enabled(status: str) -> bool:
    settings = _load_notification_settings()
    step_events = settings.get("step_events")
    if not isinstance(step_events, dict):
        return True

    event_map = {
        "STEP_COMPLETED": "completed",
        "STEP_REJECTED": "rejected",
        "STEP_FAILED": "failed",
    }
    key = event_map.get(status)
    if not key:
        return True

    value = step_events.get(key)
    return True if value is None else bool(value)


def _enrich_context(context: dict[str, Any]) -> dict[str, Any]:
    """Ensure context has all required fields for notifications.
    
    Adds missing fields with sensible defaults:
    - workflow_name: Falls back to template_group if not present
    - template_group: Falls back to workflow_name if not present
    - job_id: Falls back to run_code, workflow_run_id, or id before "unknown"
    - current_step: Ensures step name is available for step notifications
    """
    enriched = dict(context)
    
    # Ensure workflow_name is set (fallback to template_group)
    if not enriched.get("workflow_name"):
        enriched["workflow_name"] = enriched.get("template_group", "unknown")

    # Ensure template_group is set for backend/daemon payloads that only carry workflow_name
    if not enriched.get("template_group"):
        enriched["template_group"] = enriched.get("workflow_name", "unknown")
    
    # Ensure job_id is set across manual and backend/daemon payload variants
    if not enriched.get("job_id"):
        enriched["job_id"] = (
            enriched.get("run_code")
            or enriched.get("workflow_run_id")
            or enriched.get("id")
            or "unknown"
        )

    # Backfill backend aliases so downstream formatters can rely on both names
    if not enriched.get("workflow_run_id") and enriched.get("id"):
        enriched["workflow_run_id"] = enriched["id"]
    if not enriched.get("run_code") and enriched.get("job_id") and enriched.get("job_id") != "unknown":
        enriched["run_code"] = enriched["job_id"]
    
    return enriched


def send_workflow_notification(status: str, context: dict[str, Any]) -> bool:
    """Send workflow-level notification (COMPLETED, FAILED, WAITING_FOR_HUMAN_INTERVENTION).
    
    Args:
        status: One of COMPLETED, FAILED, WAITING_FOR_HUMAN_INTERVENTION
        context: Job state dict or relevant context
        
    Returns:
        True if notification sent successfully, False otherwise
    """
    if not should_send_notifications():
        print(f"[notification_manager] Notifications disabled, skipping {status}", flush=True)
        return False
    
    enriched = _enrich_context(context)
    print(f"[notification_manager] Sending WORKFLOW notification: {status} for job {enriched.get('job_id')}", flush=True)
    
    result = _send_notification(status, enriched)
    print(f"[notification_manager] Workflow notification result: {result}", flush=True)
    return result


def send_step_notification(status: str, context: dict[str, Any], step: str, step_cfg: dict[str, Any]) -> bool:
    """Send step-level notification (STEP_COMPLETED, STEP_FAILED, STEP_REJECTED).
    
    Checks global config, per-event config, and step-level enable_notifications.
    
    Args:
        status: One of STEP_COMPLETED, STEP_FAILED, STEP_REJECTED
        context: Job state dict
        step: Step name
        step_cfg: Step configuration dict (to check enable_notifications)
        
    Returns:
        True if notification sent successfully, False otherwise
    """
    # Check step-level flag first
    if not step_cfg.get("enable_notifications", False):
        return False
    
    # Check global config
    if not should_send_notifications():
        return False

    if not _is_step_event_enabled(status):
        return False
    
    enriched = _enrich_context(context)
    enriched["current_step"] = step
    enriched["step_name"] = step
    step_usage = ((context or {}).get("step_usage") or {}).get(step) if isinstance((context or {}).get("step_usage"), dict) else None
    if isinstance(step_usage, dict):
        duration_ms = step_usage.get("duration_ms")
        if isinstance(duration_ms, (int, float)) and duration_ms >= 0:
            enriched["step_duration_seconds"] = float(duration_ms) / 1000.0
    
    print(f"[notification_manager] Sending STEP notification: {status} for step {step}", flush=True)
    
    result = _send_notification(status, enriched)
    print(f"[notification_manager] Step notification result: {result}", flush=True)
    return result
