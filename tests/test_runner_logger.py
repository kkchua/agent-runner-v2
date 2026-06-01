"""Tests for runner_logger.py — console output, file output, colour support.

Uses mock.patch for I/O side-effects (print, file writes).
Uses real temporary directories for the log directory.
"""
import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import agent_runner_v2.runner_logger as logger_module
from agent_runner_v2.runner_logger import (
    log_event,
    log_invocation_start,
    log_invocation_result,
    log_error,
    log_resolver,
    _colour,
    _now_iso,
    _log_dir,
    _ensure_log_file,
    _print_console,
    _write_file,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reset_logger_state():
    """Reset module-level log file state between tests."""
    logger_module._LOG_FILE = None


# ====================================================================
# _colour
# ====================================================================

class TestColour:
    def test_colour_supported(self):
        """When colour is supported, wraps text with ANSI codes."""
        with patch.object(logger_module, "_COLOUR_SUPPORTED", True):
            result = _colour("hello", "green")
            assert "\033[32m" in result
            assert "\033[0m" in result
            assert "hello" in result

    def test_colour_not_supported(self):
        """When colour is not supported, returns text unchanged."""
        with patch.object(logger_module, "_COLOUR_SUPPORTED", False):
            result = _colour("hello", "green")
            assert result == "hello"
            assert "\033[" not in result

    def test_unknown_colour_name(self):
        """Unknown colour names should not add codes."""
        with patch.object(logger_module, "_COLOUR_SUPPORTED", True):
            result = _colour("hello", "nonexistent")
            assert result == "hello"

    def test_bold_colour(self):
        with patch.object(logger_module, "_COLOUR_SUPPORTED", True):
            result = _colour("text", "bold")
            assert "\033[1m" in result

    def test_red_colour(self):
        with patch.object(logger_module, "_COLOUR_SUPPORTED", True):
            result = _colour("error", "red")
            assert "\033[31m" in result


# ====================================================================
# _now_iso
# ====================================================================

class TestNowIso:
    def test_returns_utc_iso(self):
        result = _now_iso()
        # Should contain timezone info (UTC)
        assert "+00:00" in result or result.endswith("Z")

    def test_parsable_as_iso(self):
        from datetime import datetime, timezone
        result = _now_iso()
        # Should be parseable
        dt = datetime.fromisoformat(result)
        assert dt.tzinfo == timezone.utc


# ====================================================================
# _log_dir / _ensure_log_file
# ====================================================================

class TestLogDir:
    def test_returns_runner_home_logs(self):
        with patch.object(logger_module, "RUNNER_HOME", Path("/tmp/test-runner")):
            result = _log_dir()
            assert str(result).endswith("logs")


class TestEnsureLogFile:
    def test_creates_log_dir_and_sets_path(self, tmp_path):
        _reset_logger_state()
        log_dir = tmp_path / "logs"
        log_dir.mkdir(parents=True)
        log_file = log_dir / "runner.log"

        with patch.object(logger_module, "_log_dir", return_value=log_dir):
            result = _ensure_log_file()

        # _ensure_log_file sets the path but doesn't create the file itself;
        # the file is created on first _write_file call.
        assert result is not None
        assert result == log_file
        _reset_logger_state()

    def test_returns_existing_file(self, tmp_path):
        _reset_logger_state()
        log_dir = tmp_path / "logs"
        log_dir.mkdir(parents=True)
        expected = log_dir / "runner.log"
        expected.write_text("existing\n", encoding="utf-8")

        with patch.object(logger_module, "_log_dir", return_value=log_dir):
            result = _ensure_log_file()

        assert result == expected
        _reset_logger_state()

    def test_returns_none_on_os_error(self):
        _reset_logger_state()
        with patch.object(logger_module, "_log_dir") as mock_log_dir:
            mock_log_dir.side_effect = OSError("no access")
            result = _ensure_log_file()
            assert result is None
        _reset_logger_state()

    def test_singleton(self, tmp_path):
        """Multiple calls should return the same Path object."""
        _reset_logger_state()
        log_dir = tmp_path / "logs"
        log_dir.mkdir(parents=True)

        with patch.object(logger_module, "_log_dir", return_value=log_dir):
            f1 = _ensure_log_file()
            f2 = _ensure_log_file()

        assert f1 == f2
        _reset_logger_state()


# ====================================================================
# log_event
# ====================================================================

class TestLogEvent:
    def test_records_all_fields(self, capsys):
        _reset_logger_state()
        with patch.object(logger_module, "_write_file"):
            log_event(
                step="review_task",
                coder="qwen",
                model="qwen-plus",
                auth_type="default",
                event="invocation_start",
                duration_ms=500,
                return_code=0,
                status="OK",
                message="[review_task] invoking qwen",
            )

        captured = capsys.readouterr()
        assert "[review_task] invoking qwen" in captured.out
        _reset_logger_state()

    def test_omits_optional_fields(self, capsys):
        _reset_logger_state()
        with patch.object(logger_module, "_write_file"):
            log_event(
                step="step",
                coder="qwen",
                event="info",
                message="just info",
            )

        captured = capsys.readouterr()
        assert "just info" in captured.out
        _reset_logger_state()

    def test_writes_jsonl_to_file(self, tmp_path):
        _reset_logger_state()
        log_dir = tmp_path / "logs"
        log_dir.mkdir(parents=True)

        with patch.object(logger_module, "_log_dir", return_value=log_dir), \
             patch.object(logger_module, "_print_console"):
            log_event(
                step="test_step",
                coder="qwen",
                event="test_event",
                message="test message",
            )

        log_file = log_dir / "runner.log"
        assert log_file.exists()
        content = log_file.read_text(encoding="utf-8").strip()
        record = json.loads(content)
        assert record["step"] == "test_step"
        assert record["coder"] == "qwen"
        assert record["event"] == "test_event"
        assert record["message"] == "test message"
        assert "timestamp" in record
        _reset_logger_state()

    def test_duration_ms_only_included_when_provided(self, tmp_path):
        _reset_logger_state()
        log_dir = tmp_path / "logs"
        log_dir.mkdir(parents=True)

        with patch.object(logger_module, "_log_dir", return_value=log_dir), \
             patch.object(logger_module, "_print_console"):
            log_event(
                step="s", coder="qwen", event="info", message="m",
            )
            log_event(
                step="s", coder="qwen", event="info", message="m",
                duration_ms=100,
            )

        lines = (log_dir / "runner.log").read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        r1 = json.loads(lines[0])
        r2 = json.loads(lines[1])
        assert "duration_ms" not in r1
        assert r2["duration_ms"] == 100
        _reset_logger_state()

    def test_return_code_only_included_when_provided(self, tmp_path):
        _reset_logger_state()
        log_dir = tmp_path / "logs"
        log_dir.mkdir(parents=True)

        with patch.object(logger_module, "_log_dir", return_value=log_dir), \
             patch.object(logger_module, "_print_console"):
            log_event(step="s", coder="qwen", event="info", message="m")
            log_event(step="s", coder="qwen", event="info", message="m", return_code=1)

        lines = (log_dir / "runner.log").read_text(encoding="utf-8").strip().splitlines()
        r1 = json.loads(lines[0])
        r2 = json.loads(lines[1])
        assert "return_code" not in r1
        assert r2["return_code"] == 1
        _reset_logger_state()

    def test_no_message_no_output(self, capsys):
        _reset_logger_state()
        with patch.object(logger_module, "_write_file"):
            log_event(
                step="s",
                coder="qwen",
                event="info",
            )

        captured = capsys.readouterr()
        assert captured.out == ""
        _reset_logger_state()


# ====================================================================
# log_invocation_start
# ====================================================================

class TestLogInvocationStart:
    def test_calls_log_event_with_correct_args(self):
        with patch.object(logger_module, "log_event") as mock_log:
            log_invocation_start("step_name", "qwen", model="qwen-plus", auth_type="default")

        mock_log.assert_called_once()
        # log_invocation_start passes step, coder as positional args
        call_args = mock_log.call_args[0]
        call_kwargs = mock_log.call_args[1]
        assert call_args[0] == "step_name"  # step
        assert call_args[1] == "qwen"       # coder
        assert call_kwargs["model"] == "qwen-plus"
        assert call_kwargs["auth_type"] == "default"
        assert call_kwargs["event"] == "invocation_start"

    def test_default_model_is_n_a(self):
        with patch.object(logger_module, "log_event") as mock_log:
            log_invocation_start("step", "qwen")

        kwargs = mock_log.call_args[1]
        assert "model=n/a" in kwargs["message"]
        assert "auth=default" in kwargs["message"]

    def test_message_format(self):
        with patch.object(logger_module, "log_event") as mock_log:
            log_invocation_start("review_sop", "claude", model="sonnet", auth_type="oauth")

        kwargs = mock_log.call_args[1]
        assert "[review_sop]" in kwargs["message"]
        assert "coder=claude" in kwargs["message"]
        assert "model=sonnet" in kwargs["message"]


# ====================================================================
# log_invocation_result
# ====================================================================

class TestLogInvocationResult:
    def test_success_green(self, capsys):
        with patch.object(logger_module, "_COLOUR_SUPPORTED", True), \
             patch.object(logger_module, "_write_file"):
            log_invocation_result(
                step="step", coder="qwen", model="qwen-plus",
                auth_type="default", return_code=0,
                duration_ms=100, status="OK",
            )

        captured = capsys.readouterr()
        assert "\033[32m" in captured.out  # green

    def test_failure_red(self, capsys):
        with patch.object(logger_module, "_COLOUR_SUPPORTED", True), \
             patch.object(logger_module, "_write_file"):
            log_invocation_result(
                step="step", coder="qwen", return_code=1,
                duration_ms=100, status="FAILED",
            )

        captured = capsys.readouterr()
        assert "\033[31m" in captured.out  # red

    def test_records_fields(self):
        with patch.object(logger_module, "log_event") as mock_log:
            log_invocation_result(
                step="step", coder="qwen",
                return_code=0, duration_ms=500, status="OK",
                message="custom message",
            )

        kwargs = mock_log.call_args[1]
        assert kwargs["return_code"] == 0
        assert kwargs["duration_ms"] == 500
        assert kwargs["status"] == "OK"
        assert kwargs["message"] == "custom message"

    def test_default_message_format(self):
        with patch.object(logger_module, "log_event") as mock_log:
            log_invocation_result(
                step="gen", coder="qwen", model="plus",
                return_code=0, duration_ms=200, status="OK",
            )

        kwargs = mock_log.call_args[1]
        assert "[gen]" in kwargs["message"]
        assert "coder=qwen" in kwargs["message"]
        assert "rc=0 OK" in kwargs["message"]
        assert "200ms" in kwargs["message"]


# ====================================================================
# log_error
# ====================================================================

class TestLogError:
    def test_sets_error_event(self):
        with patch.object(logger_module, "log_event") as mock_log:
            log_error(step="step", coder="qwen", error="something broke")

        kwargs = mock_log.call_args[1]
        assert kwargs["event"] == "error"
        assert kwargs["status"] == "ERROR"
        assert "something broke" in kwargs["message"]

    def test_default_error_message(self):
        with patch.object(logger_module, "log_event") as mock_log:
            log_error(step="review", coder="qwen")

        kwargs = mock_log.call_args[1]
        assert "[review]" in kwargs["message"]
        assert "coder=qwen" in kwargs["message"]

    def test_console_output_red(self, capsys):
        with patch.object(logger_module, "_COLOUR_SUPPORTED", True), \
             patch.object(logger_module, "_write_file"):
            log_error(step="step", coder="qwen", error="error msg")

        captured = capsys.readouterr()
        assert "\033[31m" in captured.out  # red


# ====================================================================
# log_resolver
# ====================================================================

class TestLogResolver:
    def test_alias_resolution(self, capsys):
        log_resolver("my-alias", "actual-coder", is_alias=True)
        captured = capsys.readouterr()
        assert "'my-alias'" in captured.out
        assert "'actual-coder'" in captured.out
        assert "→" in captured.out
        assert "resolved alias" in captured.out

    def test_plain_coder_name(self, capsys):
        log_resolver("qwen", "qwen", is_alias=False)
        captured = capsys.readouterr()
        assert "using plain coder name" in captured.out

    def test_dim_format(self, capsys):
        with patch.object(logger_module, "_COLOUR_SUPPORTED", True):
            log_resolver("alias", "coder", is_alias=True)
            captured = capsys.readouterr()
            assert "\033[2m" in captured.out  # dim


# ====================================================================
# _print_console
# ====================================================================

class TestPrintConsole:
    def test_invocation_start_cyan(self, capsys):
        with patch.object(logger_module, "_COLOUR_SUPPORTED", True):
            _print_console({
                "event": "invocation_start",
                "message": "[step] invoking",
            })
        captured = capsys.readouterr()
        assert "\033[36m" in captured.out  # cyan

    def test_invocation_result_success_green(self, capsys):
        with patch.object(logger_module, "_COLOUR_SUPPORTED", True):
            _print_console({
                "event": "invocation_result",
                "return_code": 0,
                "message": "[step] rc=0 OK",
            })
        captured = capsys.readouterr()
        assert "\033[32m" in captured.out  # green

    def test_invocation_result_failure_red(self, capsys):
        with patch.object(logger_module, "_COLOUR_SUPPORTED", True):
            _print_console({
                "event": "invocation_result",
                "return_code": 1,
                "message": "[step] rc=1 FAILED",
            })
        captured = capsys.readouterr()
        assert "\033[31m" in captured.out  # red

    def test_error_red(self, capsys):
        with patch.object(logger_module, "_COLOUR_SUPPORTED", True):
            _print_console({
                "event": "error",
                "message": "error happened",
            })
        captured = capsys.readouterr()
        assert "\033[31m" in captured.out  # red

    def test_other_event_no_colour(self, capsys):
        with patch.object(logger_module, "_COLOUR_SUPPORTED", True):
            _print_console({
                "event": "info",
                "message": "plain info",
            })
        captured = capsys.readouterr()
        assert "plain info" in captured.out
        assert "\033[" not in captured.out

    def test_empty_message_no_output(self, capsys):
        _print_console({
            "event": "info",
            "message": "",
        })
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_missing_message_no_output(self, capsys):
        _print_console({
            "event": "info",
        })
        captured = capsys.readouterr()
        assert captured.out == ""


# ====================================================================
# _write_file
# ====================================================================

class TestWriteFile:
    def test_appends_json_line(self, tmp_path):
        _reset_logger_state()
        log_dir = tmp_path / "logs"
        log_dir.mkdir(parents=True)

        with patch.object(logger_module, "_log_dir", return_value=log_dir):
            _write_file({"step": "s", "coder": "qwen", "event": "e"})

        log_file = log_dir / "runner.log"
        line = log_file.read_text(encoding="utf-8").strip()
        data = json.loads(line)
        assert data["step"] == "s"
        assert data["coder"] == "qwen"
        _reset_logger_state()

    def test_no_log_file_no_write(self, tmp_path):
        _reset_logger_state()
        with patch.object(logger_module, "_ensure_log_file", return_value=None):
            _write_file({"step": "s"})
        # No exception — should be silent
        _reset_logger_state()

    def test_os_error_silently_ignored(self, tmp_path):
        _reset_logger_state()
        log_dir = tmp_path / "logs"
        log_dir.mkdir(parents=True)
        fake_path = log_dir / "runner.log"

        with patch.object(logger_module, "_ensure_log_file", return_value=fake_path):
            with patch("builtins.open", side_effect=OSError("disk full")):
                # Should not raise
                _write_file({"step": "s"})
        _reset_logger_state()

    def test_ensures_ascii_false(self, tmp_path):
        _reset_logger_state()
        log_dir = tmp_path / "logs"
        log_dir.mkdir(parents=True)

        with patch.object(logger_module, "_log_dir", return_value=log_dir):
            _write_file({"message": "日本語テスト"})

        log_file = log_dir / "runner.log"
        content = log_file.read_text(encoding="utf-8")
        assert "日本語テスト" in content
        _reset_logger_state()


# ====================================================================
# Integration: full logging flow
# ====================================================================

class TestLoggingIntegration:
    def test_start_then_result_writes_two_lines(self, tmp_path):
        _reset_logger_state()
        log_dir = tmp_path / "logs"
        log_dir.mkdir(parents=True)

        with patch.object(logger_module, "_log_dir", return_value=log_dir), \
             patch.object(logger_module, "_print_console"):
            log_invocation_start("step", "qwen", model="plus")
            log_invocation_result("step", "qwen", return_code=0, duration_ms=100, status="OK")

        lines = (log_dir / "runner.log").read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        r1 = json.loads(lines[0])
        r2 = json.loads(lines[1])
        assert r1["event"] == "invocation_start"
        assert r2["event"] == "invocation_result"
        assert r2["return_code"] == 0
        _reset_logger_state()

    def test_error_appends_to_existing_log(self, tmp_path):
        _reset_logger_state()
        log_dir = tmp_path / "logs"
        log_dir.mkdir(parents=True)

        with patch.object(logger_module, "_log_dir", return_value=log_dir), \
             patch.object(logger_module, "_print_console"):
            log_event("s", "qwen", event="info", message="first")
            log_error("s", "qwen", error="second")

        lines = (log_dir / "runner.log").read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        _reset_logger_state()

    def test_log_file_is_singleton(self, tmp_path):
        """Multiple calls should use the same log file, not create new ones."""
        _reset_logger_state()
        log_dir = tmp_path / "logs"
        log_dir.mkdir(parents=True)

        with patch.object(logger_module, "_log_dir", return_value=log_dir), \
             patch.object(logger_module, "_print_console"):
            f1 = _ensure_log_file()
            f2 = _ensure_log_file()

        assert f1 == f2
        # The file may not be created yet (only the path is set)
        # but the returned paths should be the same.
        assert f1.name == "runner.log"
        _reset_logger_state()
