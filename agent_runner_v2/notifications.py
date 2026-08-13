#!/usr/bin/env python3
"""
notifications.py — Notification service for agent_runner_v2.

Sends Pushover notifications on workflow completion/failure events.
Non-blocking: failures are logged but don't halt workflow execution.
"""
from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from typing import Any

from .runtime_context import PROJECT_ROOT
from .qwenpaw_client import notify_qwenpaw_agent


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Configuration loading helpers
# ---------------------------------------------------------------------------

def _load_env_file():
    """Load .env file from project root if it exists."""
    try:
        from dotenv import load_dotenv
        
        # Try multiple possible locations for .env
        possible_paths = [
            Path(".env"),  # Current directory
            Path(__file__).parent.parent / ".env",  # Repo root (one level up from agent_runner_v2)
        ]
        
        # Also try PROJECT_ROOT if available
        try:
            if PROJECT_ROOT:
                possible_paths.insert(0, Path(str(PROJECT_ROOT)) / ".env")
        except Exception:
            pass
        
        for env_path in possible_paths:
            if env_path.exists():
                print(f"[notifications] Loading .env from {env_path.resolve()}", flush=True)
                load_dotenv(env_path, override=True)
                return
        
        print(f"[notifications] No .env file found in searched locations", flush=True)
    except ImportError:
        print(f"[notifications] python-dotenv not installed, skipping .env load", flush=True)
    except Exception as exc:
        print(f"[notifications] Error loading .env: {exc}", flush=True)


def _resolve_credentials() -> tuple[str | None, str | None]:
    """Resolve Pushover credentials from .env or config.json.
    
    Resolution order:
    1. Environment variables (PUSHOVER_API_TOKEN, PUSHOVER_USER_KEY)
    2. Global config.json (%USERPROFILE%\\.ukbe-runner\\config.json)
    
    Returns (api_token, user_key) or (None, None) if not found.
    """
    # Load .env file first
    _load_env_file()
    
    # Priority 1: Environment variables
    api_token = os.environ.get("PUSHOVER_API_TOKEN", "").strip() or None
    user_key = os.environ.get("PUSHOVER_USER_KEY", "").strip() or None
    
    if api_token and user_key:
        return api_token, user_key
    
    # Priority 2: Global config.json
    try:
        config_path = Path.home() / ".ukbe-runner" / "config.json"
        if config_path.exists():
            config = json.loads(config_path.read_text(encoding="utf-8"))
            notification_cfg = config.get("notification", {})
            credentials = notification_cfg.get("credentials", {})
            
            if not api_token:
                api_token = credentials.get("api_token", "").strip() or None
            if not user_key:
                user_key = credentials.get("user_key", "").strip() or None
    except Exception as exc:
        print(f"[notifications] Failed to load config.json for credentials: {exc}", flush=True)

    return api_token, user_key


def _load_notification_config() -> dict[str, Any]:
    """Load notification configuration from global config.json.
    
    Returns dict with keys:
    - enabled: bool
    - notify_api_url: str (Pushover API endpoint)
    - message_config: dict (message formatting options)
    - priority_by_status: dict (status → priority mapping)
    """
    default_config = {
        "enabled": False,
        "notify_api_url": "https://api.pushover.net/1/messages.json",
        "message_config": {
            "include_job_id": True,
            "include_workflow_name": True,
            "include_template_group": True,
            "include_duration": True,
            "include_failed_step": True,
            "include_retry_counts": False,
            "include_artifacts_summary": False,
            "custom_template": None,
        },
        "priority_by_status": {
            "COMPLETED": 0,
            "FAILED": 1,
            "WAITING_FOR_HUMAN_INTERVENTION": 0,
            "WAITING_FOR_HUMAN_MAXRETRIED": 0,
            "STEP_REJECTED": 0,
        }
    }
    
    try:
        config_path = Path.home() / ".ukbe-runner" / "config.json"
        if not config_path.exists():
            return default_config
        
        config = json.loads(config_path.read_text(encoding="utf-8"))
        notification_cfg = config.get("notification", {})
        
        # Merge with defaults
        result = dict(default_config)
        result.update({k: v for k, v in notification_cfg.items() if k in default_config})
        
        # Deep merge message_config
        if "message_config" in notification_cfg:
            result["message_config"].update(notification_cfg["message_config"])
        
        # Deep merge priority_by_status
        if "priority_by_status" in notification_cfg:
            result["priority_by_status"].update(notification_cfg["priority_by_status"])
        
        return result
    except Exception as exc:
        print(f"[notifications] Failed to load notification config: {exc}", flush=True)
        return default_config


# ---------------------------------------------------------------------------
# Message building
# ---------------------------------------------------------------------------

def _build_message(status: str, context: dict[str, Any], config: dict[str, Any]) -> tuple[str, str, int]:
    """Build Pushover message from status and context.
    
    Args:
        status: Job status (COMPLETED, FAILED, etc.)
        context: Job state dict with relevant fields
        config: Notification configuration dict
    
    Returns:
        (title, message, priority) tuple
    """
    msg_cfg = config.get("message_config", {})
    priorities = config.get("priority_by_status", {})
    
    # Check for custom template
    custom_template = msg_cfg.get("custom_template")
    if custom_template:
        title, message = _format_custom_template(custom_template, status, context)
    else:
        title, message = _format_default_message(status, context, msg_cfg)
    
    # Determine priority
    priority = priorities.get(status, 0)
    
    # For FAILED status with priority 1, add emergency retry/expire
    if priority == 1:
        # Emergency priority: retry every 60 seconds for 1 hour
        context["_pushover_extras"] = {
            "retry": 60,
            "expire": 3600,
        }
    
    return title, message, priority


def _format_default_message(status: str, context: dict[str, Any], msg_cfg: dict[str, Any]) -> tuple[str, str]:
    """Format standard notification message."""
    job_id = context.get("job_id", "unknown")
    workflow_name = context.get("workflow_name", "unknown")
    template_group = context.get("template_group", "unknown")

    # Build title with status-specific icon
    if status in ("COMPLETED", "STEP_COMPLETED"):
        status_emoji = "✅"
        status_type = "Workflow" if status == "COMPLETED" else "Step"
    elif status in ("FAILED", "STEP_FAILED", "STEP_REJECTED"):
        status_emoji = "❌"
        status_type = "Workflow" if status == "FAILED" else "Step"
    elif status == "WAITING_FOR_HUMAN_INTERVENTION":
        status_emoji = "⚠️"
        status_type = "Workflow"
    elif status == "WAITING_FOR_HUMAN_MAXRETRIED":
        status_emoji = "🔄"
        status_type = "Workflow"
    else:
        status_emoji = "ℹ️"
        status_type = "Workflow"
    
    title = f"{status_emoji} {status_type} {status}"
    
    # Build message body
    lines = []

    if msg_cfg.get("include_workflow_name"):
        lines.append(f"**Workflow:** {workflow_name}")

    # Skip template_group since it's usually the same as workflow_name

    if msg_cfg.get("include_job_id"):
        lines.append(f"**Job ID:** `{job_id}`")

    # Add step name for step-level notifications
    step_name = context.get("step_name") or context.get("current_step")
    if step_name and status in ("STEP_COMPLETED", "STEP_FAILED", "STEP_REJECTED"):
        lines.append(f"**Step:** {step_name}")

    # Add duration if available
    if msg_cfg.get("include_duration"):
        duration_seconds = _extract_duration_seconds(status, context)
        if duration_seconds is not None:
            minutes, seconds = divmod(duration_seconds, 60)
            if minutes > 0:
                lines.append(f"**Duration:** {int(minutes)}m {int(seconds)}s")
            else:
                lines.append(f"**Duration:** {int(seconds)}s")
    
    # Add failure details
    if status == "FAILED" and msg_cfg.get("include_failed_step"):
        failed_step = context.get("last_failure_step") or context.get("current_step")
        if failed_step:
            lines.append(f"**Failed at step:** {failed_step}")
        
        failure_reason = context.get("last_failure_reason")
        if failure_reason:
            # Truncate long messages
            reason = failure_reason[:200] + "..." if len(failure_reason) > 200 else failure_reason
            lines.append(f"**Reason:** {reason}")
        
        failure_code = context.get("last_failure_code")
        if failure_code:
            lines.append(f"**Error code:** `{failure_code}`")
    
    # Add retry counts if requested
    if msg_cfg.get("include_retry_counts"):
        reject_counts = context.get("reject_counts", {})
        if reject_counts:
            total_retries = sum(reject_counts.values())
            if total_retries > 0:
                lines.append(f"**Total retries:** {total_retries}")
    
    # Add artifacts summary if requested
    if msg_cfg.get("include_artifacts_summary"):
        artifacts = context.get("artifacts", {})
        completed_artifacts = {k: v for k, v in artifacts.items() if v}
        if completed_artifacts:
            lines.append(f"**Artifacts:** {len(completed_artifacts)} generated")
    
    message = "\n".join(lines)
    return title, message


def _extract_duration_seconds(status: str, context: dict[str, Any]) -> float | None:
    """Resolve the most accurate duration for the notification payload.

    Step notifications should prefer per-step timing, not workflow lifetime.
    Workflow notifications can use explicit duration_seconds or timestamp deltas.
    """
    if status in ("STEP_COMPLETED", "STEP_FAILED", "STEP_REJECTED"):
        step_duration = context.get("step_duration_seconds")
        if isinstance(step_duration, (int, float)) and step_duration >= 0:
            return float(step_duration)

    explicit_duration = context.get("duration_seconds")
    if isinstance(explicit_duration, (int, float)) and explicit_duration >= 0:
        return float(explicit_duration)

    for start_key, end_key in (("started_at", "completed_at"), ("created_at", "updated_at")):
        start_value = context.get(start_key)
        end_value = context.get(end_key)
        if start_value and end_value:
            try:
                from datetime import datetime

                start = datetime.fromisoformat(str(start_value))
                end = datetime.fromisoformat(str(end_value))
                duration = (end - start).total_seconds()
                if duration >= 0:
                    return duration
            except Exception:
                continue

    return None


def _format_custom_template(template: str, status: str, context: dict[str, Any]) -> tuple[str, str]:
    """Format message using custom template string.
    
    Template supports {variable} substitution from context dict.
    First line becomes title, remaining lines become message.
    """
    try:
        # Simple variable substitution
        formatted = template
        for key, value in context.items():
            placeholder = "{" + key + "}"
            if isinstance(value, str):
                formatted = formatted.replace(placeholder, value)
            elif isinstance(value, dict):
                formatted = formatted.replace(placeholder, json.dumps(value, indent=2))
        
        # Split into title and message
        lines = formatted.split("\n", 1)
        title = lines[0].strip()
        message = lines[1].strip() if len(lines) > 1 else ""
        
        return title, message
    except Exception:
        # Fallback to default on error
        return _format_default_message(status, context, {})


# ---------------------------------------------------------------------------
# Pushover API
# ---------------------------------------------------------------------------

def _pushover_api_call(api_token: str, user_key: str, title: str, message: str, priority: int, api_url: str, extras: dict[str, Any] | None = None) -> bool:
    """Send notification via Pushover API.

    Args:
        api_token: Pushover application token
        user_key: Pushover user key
        title: Notification title
        message: Notification message (supports markdown)
        priority: Priority level (-2 to 2)
        api_url: Pushover API endpoint URL
        extras: Optional extra parameters (retry, expire, etc.)

    Returns:
        True if successful, False otherwise
    """
    payload = {
        "token": api_token,
        "user": user_key,
        "title": title,
        "message": message,
        "html": 1,  # Enable HTML/markdown formatting
        "priority": priority,
    }
    
    # Add emergency retry/expire if present
    if extras:
        payload.update(extras)

    data = urllib.parse.urlencode(payload).encode("utf-8")

    try:
        req = urllib.request.Request(api_url, data=data, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")

        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode("utf-8"))

            if result.get("status") == 1:
                return True
            else:
                print(f"[notifications] Pushover API returned error: {result.get('errors', ['Unknown error'])}", flush=True)
                return False
    except urllib.error.HTTPError as exc:
        print(f"[notifications] Pushover HTTP error {exc.code}: {exc.reason}", flush=True)
        return False
    except Exception as exc:
        print(f"[notifications] Pushover API call failed: {exc}", flush=True)
        return False


# ---------------------------------------------------------------------------
# Telegram Bot API
# ---------------------------------------------------------------------------

def _resolve_telegram_credentials() -> tuple[str | None, str | None]:
    """Resolve Telegram credentials from .env or config.json.

    Priority:
    1. TELEGRAM_GROUPCHAT_ID (Env var)
    2. TELEGRAM_CHAT_ID (Env var)
    3. config.json (Fallback)

    Returns (bot_token, chat_id) or (None, None) if not found.
    """
    _load_env_file()

    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip() or None
    
    # Priority 1: Group Chat ID
    chat_id = os.environ.get("TELEGRAM_GROUPCHAT_ID", "").strip() or None
    
    # Priority 2: Private Chat ID
    if not chat_id:
        chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip() or None

    if bot_token and chat_id:
        return bot_token, chat_id

    # Priority 3: Global config.json
    try:
        config_path = Path.home() / ".ukbe-runner" / "config.json"
        if config_path.exists():
            config = json.loads(config_path.read_text(encoding="utf-8"))
            telegram_cfg = config.get("notification", {}).get("telegram", {})

            if not bot_token:
                bot_token = telegram_cfg.get("bot_token", "").strip() or None
            if not chat_id:
                chat_id = telegram_cfg.get("chat_id", "").strip() or None
    except Exception as exc:
        print(f"[notifications] Failed to load config.json for Telegram credentials: {exc}", flush=True)

    return bot_token, chat_id


def _is_telegram_enabled() -> bool:
    """Check if Telegram notifications are enabled in config."""
    try:
        config_path = Path.home() / ".ukbe-runner" / "config.json"
        if not config_path.exists():
            return False
        config = json.loads(config_path.read_text(encoding="utf-8"))
        return bool(config.get("notification", {}).get("telegram", {}).get("enabled", False))
    except Exception:
        return False


def _format_telegram_message(status: str, context: dict[str, Any]) -> str:
    """Build Telegram message in HTML parse_mode.

    Reuses the same title/message logic as Pushover but formats for Telegram HTML.
    """
    job_id = context.get("job_id", "unknown")
    workflow_name = context.get("workflow_name", "unknown")

    if status in ("COMPLETED", "STEP_COMPLETED"):
        emoji = "✅"
        label = "Workflow" if status == "COMPLETED" else "Step"
    elif status in ("FAILED", "STEP_FAILED", "STEP_REJECTED"):
        emoji = "❌"
        label = "Workflow" if status == "FAILED" else "Step"
    elif status == "WAITING_FOR_HUMAN_INTERVENTION":
        emoji = "⚠️"
        label = "Workflow"
    elif status == "WAITING_FOR_HUMAN_MAXRETRIED":
        emoji = "🔄"
        label = "Workflow"
    else:
        emoji = "ℹ️"
        label = "Workflow"

    lines = [f"{emoji} <b>{label} {status}</b>", f"<b>Workflow:</b> {workflow_name}", f"<b>Job ID:</b> <code>{job_id}</code>"]

    step_name = context.get("step_name") or context.get("current_step")
    if step_name and status.startswith("STEP_"):
        lines.append(f"<b>Step:</b> {step_name}")

    if status in ("FAILED", "WAITING_FOR_HUMAN_INTERVENTION", "WAITING_FOR_HUMAN_MAXRETRIED"):
        failed_step = context.get("last_failure_step") or context.get("current_step")
        if failed_step:
            lines.append(f"<b>Failed at step:</b> {failed_step}")
        failure_reason = context.get("last_failure_reason")
        if failure_reason:
            reason = failure_reason[:200] + "..." if len(failure_reason) > 200 else failure_reason
            lines.append(f"<b>Reason:</b> {reason}")
        failure_code = context.get("last_failure_code")
        if failure_code:
            lines.append(f"<b>Error code:</b> <code>{failure_code}</code>")

    duration_seconds = _extract_duration_seconds(status, context)
    if duration_seconds is not None:
        minutes, seconds = divmod(duration_seconds, 60)
        if minutes > 0:
            lines.append(f"<b>Duration:</b> {int(minutes)}m {int(seconds)}s")
        else:
            lines.append(f"<b>Duration:</b> {int(seconds)}s")

    return "\n".join(lines)


def _telegram_api_call(bot_token: str, chat_id: str, text: str) -> bool:
    """Send message via Telegram Bot API.

    Args:
        bot_token: Telegram bot token
        chat_id: Target chat/group/channel ID
        text: Message text (HTML parse_mode)

    Returns:
        True if successful, False otherwise
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    data = urllib.parse.urlencode(payload).encode("utf-8")

    try:
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")

        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode("utf-8"))

            if result.get("ok"):
                return True
            else:
                print(f"[notifications] Telegram API returned error: {result.get('description', 'Unknown error')}", flush=True)
                return False
    except urllib.error.HTTPError as exc:
        print(f"[notifications] Telegram HTTP error {exc.code}: {exc.reason}", flush=True)
        return False
    except Exception as exc:
        print(f"[notifications] Telegram API call failed: {exc}", flush=True)
        return False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def send_notification(status: str, context: dict[str, Any]) -> bool:
    """Send notification for workflow status change.
    
    This is the main entry point. Non-blocking: exceptions are caught and logged.
    
    Args:
        status: Job status (COMPLETED, FAILED, WAITING_FOR_HUMAN_INTERVENTION, etc.)
        context: Job state dict or dict with relevant fields
    
    Returns:
        True if notification sent successfully, False otherwise
    """
    try:
        # Load configuration
        config = _load_notification_config()

        # Check if notifications are enabled globally
        if not config.get("enabled", False):
            print(f"[notifications] Notifications are disabled in config.json", flush=True)
            return False

        job_id = context.get("job_id", "unknown")
        print(f"[notifications] Sending notification: status={status}, job_id={job_id}", flush=True)

        any_success = False

        # --- Pushover channel ---
        api_token, user_key = _resolve_credentials()
        if api_token and user_key:
            title, message, priority = _build_message(status, context, config)
            api_url = config.get("notify_api_url", "https://api.pushover.net/1/messages.json")
            extras = context.pop("_pushover_extras", None)

            if _pushover_api_call(api_token, user_key, title, message, priority, api_url, extras):
                print(f"[notifications] Pushover sent: {status} for job {job_id}", flush=True)
                any_success = True
            else:
                print(f"[notifications] Pushover failed: {status} for job {job_id}", flush=True)
        else:
            print(f"[notifications] Pushover credentials not configured, skipping", flush=True)

        # --- QwenPaw Console channel ---
        if _is_telegram_enabled():
            bot_token, chat_id = _resolve_telegram_credentials()
            if bot_token and chat_id:
                text = _format_telegram_message(status, context)

                # 1. Send to Telegram (for the user)
                if _telegram_api_call(bot_token, chat_id, text):
                    print(f"[notifications] Telegram sent: {status} for job {job_id}", flush=True)
                    any_success = True
                else:
                    print(f"[notifications] Telegram failed: {status} for job {job_id}", flush=True)
                
                # 2. Send to QwenPaw Console (for the agent)
                # TODO: Re-enable when agent monitoring is ready
                # if notify_qwenpaw_agent(text):
                #     print(f"[notifications] QwenPaw Console sent: {status} for job {job_id}", flush=True)
                #     any_success = True
                # else:
                #     print(f"[notifications] QwenPaw Console failed: {status} for job {job_id}", flush=True)
                pass

        return any_success

    except Exception as exc:
        # Never let notification failures affect workflow execution
        print(f"[notifications] Notification failed: {exc}", flush=True)
        return False
