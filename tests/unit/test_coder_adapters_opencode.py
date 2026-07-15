from __future__ import annotations

import pytest

from agent_runner_v2 import coder_adapters


def test_invoke_opencode_builds_run_command_with_provider_model(monkeypatch, tmp_path):
    captured: dict[str, object] = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        return 0, '{"status":"APPROVED","remark":"ok","artifacts":{}}', ""

    monkeypatch.setattr(coder_adapters, "_run_with_sidecar_poll", fake_run)

    result = coder_adapters._invoke_opencode(
        step="implement",
        prompt_text="Write the file",
        cwd=tmp_path,
        coder_config={"model": "opencode-go/glm-5.2"},
        sidecar_path=None,
        timeout_seconds_override=15,
    )

    assert captured["command"] == [
        "opencode",
        "run",
        "--model",
        "opencode-go/glm-5.2",
    ]
    assert captured["kwargs"] == {
        "cwd": tmp_path,
        "input_text": "Write the file",
        "timeout_seconds": 15,
        "sidecar_path": None,
        "step": "implement",
    }
    assert result["parsed_result"]["status"] == "APPROVED"


def test_invoke_opencode_builds_provider_model_from_connection_profile(monkeypatch, tmp_path):
    captured: dict[str, object] = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        return 0, '{"status":"APPROVED","remark":"ok","artifacts":{}}', ""

    monkeypatch.setattr(coder_adapters, "_run_with_sidecar_poll", fake_run)

    result = coder_adapters._invoke_opencode(
        step="implement",
        prompt_text="Write the file",
        cwd=tmp_path,
        coder_config={
            "connection": "opencode_go",
            "connection_profile": {"provider_prefix": "opencode-go"},
            "model_id": "deepseek-v4-flash",
        },
        sidecar_path=None,
        timeout_seconds_override=15,
    )

    assert captured["command"] == [
        "opencode",
        "run",
        "--model",
        "opencode-go/deepseek-v4-flash",
    ]
    assert result["parsed_result"]["status"] == "APPROVED"


def test_invoke_opencode_rejects_model_without_provider_prefix(tmp_path):
    with pytest.raises(ValueError, match="provider"):
        coder_adapters._invoke_opencode(
            step="implement",
            prompt_text="Write the file",
            cwd=tmp_path,
            coder_config={"model": "glm-5.2"},
            sidecar_path=None,
            timeout_seconds_override=15,
        )


def test_invoke_opencode_sidecar_validity_short_circuits_stdout_json_parse(monkeypatch, tmp_path):
    sidecar_path = tmp_path / "meta.json"
    sidecar_path.write_text(
        '{"schema_version":"v2","coder_result":{"status":"APPROVED","remark":"ok","artifacts":{"IMPL_FILE":"docs/system/impl.md"},"recorded_at":"2026-07-01T00:00:00"}}',
        encoding="utf-8",
    )

    monkeypatch.setattr(coder_adapters, "_run_with_sidecar_poll", lambda *args, **kwargs: (0, "plain text output", ""))
    monkeypatch.setattr(coder_adapters, "_is_valid_sidecar_json", lambda path: True)

    result = coder_adapters._invoke_opencode(
        step="implement",
        prompt_text="Write the file",
        cwd=tmp_path,
        coder_config={"model": "opencode-go/glm-5.2"},
        sidecar_path=sidecar_path,
        timeout_seconds_override=15,
    )

    assert result["return_code"] == 0
    assert result["parsed_result"] == {}
