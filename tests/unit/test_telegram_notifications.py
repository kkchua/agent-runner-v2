"""Unit tests for Telegram notification channel in notifications.py."""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from agent_runner_v2 import notifications


class TestResolveTelegramCredentials:
    def test_loads_credentials_from_env_file(self) -> None:
        """Verify that credentials are actually loaded from the .env file."""
        token, chat_id = notifications._resolve_telegram_credentials()
        
        # Assert that values are present (not None)
        assert token is not None, "Expected TELEGRAM_BOT_TOKEN from .env"
        assert chat_id is not None, "Expected TELEGRAM_CHAT_ID from .env"
        
        # Basic validation of format (Token usually has a colon)
        assert ":" in token, f"Token should contain a colon, got {token[:10]}..."

    def test_returns_none_when_not_configured(self, monkeypatch) -> None:
        # This test verifies behavior when .env is MISSING.
        # We simulate this by hiding the file path.
        monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
        monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)

        with patch.object(notifications, "_load_env_file"):
            with patch("pathlib.Path.exists", return_value=False):
                token, chat_id = notifications._resolve_telegram_credentials()

        assert token is None
        assert chat_id is None

    def test_strips_whitespace(self) -> None:
        """Verify that the loaded credentials are stripped of whitespace."""
        token, chat_id = notifications._resolve_telegram_credentials()
        
        # Check that the actual loaded token has no leading/trailing spaces
        assert token == token.strip()
        assert chat_id == chat_id.strip()


class TestFormatTelegramMessage:
    def test_intervention_message_format(self) -> None:
        context = {
            "job_id": "AGBUILD-20260812-001-Test",
            "workflow_name": "artifact_generator_builder_v3",
            "last_failure_step": "gatekeep_package",
            "last_failure_reason": "STEP_CONTRACT_MISMATCH",
            "last_failure_code": "validator_failure",
        }

        text = notifications._format_telegram_message("WAITING_FOR_HUMAN_INTERVENTION", context)

        assert "⚠️" in text
        assert "WAITING_FOR_HUMAN_INTERVENTION" in text
        assert "artifact_generator_builder_v3" in text
        assert "AGBUILD-20260812-001-Test" in text
        assert "gatekeep_package" in text
        assert "STEP_CONTRACT_MISMATCH" in text
        assert "validator_failure" in text

    def test_completed_message_format(self) -> None:
        context = {
            "job_id": "JOB-123",
            "workflow_name": "test_workflow",
        }

        text = notifications._format_telegram_message("COMPLETED", context)

        assert "✅" in text
        assert "COMPLETED" in text
        assert "test_workflow" in text
        assert "JOB-123" in text

    def test_failed_message_includes_error_details(self) -> None:
        context = {
            "job_id": "JOB-456",
            "workflow_name": "broken_workflow",
            "last_failure_step": "validate",
            "last_failure_reason": "Schema validation failed",
            "last_failure_code": "SCHEMA_ERROR",
        }

        text = notifications._format_telegram_message("FAILED", context)

        assert "❌" in text
        assert "FAILED" in text
        assert "validate" in text
        assert "Schema validation failed" in text
        assert "SCHEMA_ERROR" in text

    def test_step_notification_includes_step_name(self) -> None:
        context = {
            "job_id": "JOB-789",
            "workflow_name": "step_wf",
            "step_name": "generate_docs",
        }

        text = notifications._format_telegram_message("STEP_COMPLETED", context)

        assert "generate_docs" in text
        assert "Step" in text

    def test_html_tags_present(self) -> None:
        context = {"job_id": "J1", "workflow_name": "wf"}
        text = notifications._format_telegram_message("COMPLETED", context)

        assert "<b>" in text
        assert "<code>" in text

    def test_truncates_long_reason(self) -> None:
        context = {
            "job_id": "J1",
            "workflow_name": "wf",
            "last_failure_reason": "x" * 500,
        }

        text = notifications._format_telegram_message("FAILED", context)

        assert "..." in text
        assert len(text) < 600


class TestTelegramApiCall:
    def test_successful_send(self) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"ok": True}).encode("utf-8")
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response):
            result = notifications._telegram_api_call("token", "123", "hello")

        assert result is True

    def test_api_error_returns_false(self) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"ok": False, "description": "Bad Request"}).encode("utf-8")
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response):
            result = notifications._telegram_api_call("token", "123", "hello")

        assert result is False

    def test_network_error_returns_false(self) -> None:
        with patch("urllib.request.urlopen", side_effect=Exception("network down")):
            result = notifications._telegram_api_call("token", "123", "hello")

        assert result is False


class TestSendNotificationFanout:
    def test_both_channels_called_when_enabled(self, monkeypatch) -> None:
        pushover_called = []
        telegram_called = []

        def fake_pushover(*args, **kwargs):
            pushover_called.append(True)
            return True

        def fake_telegram(*args, **kwargs):
            telegram_called.append(True)
            return True

        monkeypatch.setattr(notifications, "_load_notification_config", lambda: {"enabled": True})
        monkeypatch.setattr(notifications, "_resolve_credentials", lambda: ("token", "user"))
        monkeypatch.setattr(notifications, "_build_message", lambda s, c, cfg: ("title", "msg", 0))
        monkeypatch.setattr(notifications, "_pushover_api_call", fake_pushover)
        monkeypatch.setattr(notifications, "_is_telegram_enabled", lambda: True)
        monkeypatch.setattr(notifications, "_resolve_telegram_credentials", lambda: ("bot", "chat"))
        monkeypatch.setattr(notifications, "_format_telegram_message", lambda s, c: "tg msg")
        monkeypatch.setattr(notifications, "_telegram_api_call", fake_telegram)
        # Mock QwenPaw client
        monkeypatch.setattr(notifications, "notify_qwenpaw_agent", lambda *a, **kw: True)

        result = notifications.send_notification("COMPLETED", {"job_id": "J1"})

        assert result is True
        assert len(pushover_called) == 1
        assert len(telegram_called) == 1

    def test_telegram_only_when_pushover_unconfigured(self, monkeypatch) -> None:
        telegram_called = []

        def fake_telegram(*args, **kwargs):
            telegram_called.append(True)
            return True

        monkeypatch.setattr(notifications, "_load_notification_config", lambda: {"enabled": True})
        monkeypatch.setattr(notifications, "_resolve_credentials", lambda: (None, None))
        monkeypatch.setattr(notifications, "_is_telegram_enabled", lambda: True)
        monkeypatch.setattr(notifications, "_resolve_telegram_credentials", lambda: ("bot", "chat"))
        monkeypatch.setattr(notifications, "_format_telegram_message", lambda s, c: "tg msg")
        monkeypatch.setattr(notifications, "_telegram_api_call", fake_telegram)
        # Mock QwenPaw client
        monkeypatch.setattr(notifications, "notify_qwenpaw_agent", lambda *a, **kw: False)

        result = notifications.send_notification("COMPLETED", {"job_id": "J1"})

        assert result is True
        assert len(telegram_called) == 1

    def test_returns_false_when_all_channels_fail(self, monkeypatch) -> None:
        monkeypatch.setattr(notifications, "_load_notification_config", lambda: {"enabled": True})
        monkeypatch.setattr(notifications, "_resolve_credentials", lambda: ("token", "user"))
        monkeypatch.setattr(notifications, "_build_message", lambda s, c, cfg: ("t", "m", 0))
        monkeypatch.setattr(notifications, "_pushover_api_call", lambda *a, **kw: False)
        monkeypatch.setattr(notifications, "_is_telegram_enabled", lambda: True)
        monkeypatch.setattr(notifications, "_resolve_telegram_credentials", lambda: ("bot", "chat"))
        monkeypatch.setattr(notifications, "_format_telegram_message", lambda s, c: "msg")
        monkeypatch.setattr(notifications, "_telegram_api_call", lambda *a, **kw: False)
        # Mock QwenPaw client to fail
        monkeypatch.setattr(notifications, "notify_qwenpaw_agent", lambda *a, **kw: False)

        result = notifications.send_notification("FAILED", {"job_id": "J1"})

        assert result is False

    def test_returns_false_when_disabled(self, monkeypatch) -> None:
        monkeypatch.setattr(notifications, "_load_notification_config", lambda: {"enabled": False})

        result = notifications.send_notification("COMPLETED", {"job_id": "J1"})

        assert result is False

    def test_pushover_failure_does_not_block_telegram(self, monkeypatch) -> None:
        telegram_called = []

        def fake_telegram(*args, **kwargs):
            telegram_called.append(True)
            return True

        monkeypatch.setattr(notifications, "_load_notification_config", lambda: {"enabled": True})
        monkeypatch.setattr(notifications, "_resolve_credentials", lambda: ("token", "user"))
        monkeypatch.setattr(notifications, "_build_message", lambda s, c, cfg: ("t", "m", 0))
        monkeypatch.setattr(notifications, "_pushover_api_call", lambda *a, **kw: False)
        monkeypatch.setattr(notifications, "_is_telegram_enabled", lambda: True)
        monkeypatch.setattr(notifications, "_resolve_telegram_credentials", lambda: ("bot", "chat"))
        monkeypatch.setattr(notifications, "_format_telegram_message", lambda s, c: "msg")
        monkeypatch.setattr(notifications, "_telegram_api_call", fake_telegram)
        # Mock QwenPaw client
        monkeypatch.setattr(notifications, "notify_qwenpaw_agent", lambda *a, **kw: False)

        result = notifications.send_notification("FAILED", {"job_id": "J1"})

        assert result is True
        assert len(telegram_called) == 1
