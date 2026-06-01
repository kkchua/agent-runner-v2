"""Tests for agent_runner_v2.coder_adapters.

Exercises JSON extraction, usage parsing, sidecar validation, key masking,
timeout configuration, coerce helpers, and payload parsing — all with real
temporary directories and minimal mocking (only for subprocess/coder invocation).
"""
from __future__ import annotations

import json
import os
import subprocess
import textwrap
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from agent_runner_v2.coder_adapters import (
    DEFAULT_CODER_TIMEOUT_SECONDS,
    SIDECAR_GRACE_PERIOD_SECONDS,
    SIDECAR_POLL_INTERVAL_SECONDS,
    SIDECAR_SETTLE_DELAY_SECONDS,
    CoderInvocationError,
    InvocationManifest,
    InvocationResult,
    UsageData,
    _coerce_float,
    _coerce_int,
    _collect_usage_metrics,
    _coder_timeout_seconds,
    _extract_json_object,
    _extract_result_from_payload,
    _extract_result_from_qwen_payload,
    _is_valid_sidecar_json,
    _looks_like_qwen_error_text,
    _mask_api_key,
    _parse_json_payload,
    _parse_single_json_payload,
    _payload_to_raw_events,
    _usage_from_json_events,
    _usage_from_payload,
    merge_usage,
    dataclass_dict,
)


# ---------------------------------------------------------------------------
# _extract_json_object
# ---------------------------------------------------------------------------

class TestExtractJsonObject:
    """_extract_json_object extracts a dict from raw coder output."""

    def test_plain_json(self):
        text = json.dumps({"status": "ok", "count": 42})
        assert _extract_json_object(text) == {"status": "ok", "count": 42}

    def test_plain_json_with_whitespace(self):
        text = "  " + json.dumps({"a": 1}) + "  \n"
        assert _extract_json_object(text) == {"a": 1}

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="empty"):
            _extract_json_object("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError):
            _extract_json_object("   \n  ")

    def test_non_object_json_raises(self):
        with pytest.raises(ValueError, match="not an object"):
            _extract_json_object("[1, 2, 3]")

    def test_plain_string_raises(self):
        with pytest.raises(ValueError):
            _extract_json_object('"hello"')

    def test_number_raises(self):
        with pytest.raises(ValueError):
            _extract_json_object("42")

    # Fenced code block support
    def test_fenced_triple_backticks(self):
        text = '```json\n{"status": "ok"}\n```'
        assert _extract_json_object(text) == {"status": "ok"}

    def test_fenced_no_lang(self):
        text = '```\n{"x": true}\n```'
        assert _extract_json_object(text) == {"x": True}

    def test_fenced_no_closing(self):
        text = '```\n{"x": 1}'
        # Should still work via the depth-matching fallback
        result = _extract_json_object(text)
        assert result == {"x": 1}

    def test_fenced_with_trailing_text(self):
        text = '```\n{"result": "done"}\n```\nextra junk'
        assert _extract_json_object(text) == {"result": "done"}

    # Depth-matching fallback
    def test_json_embedded_in_text(self):
        text = "Here is the result:\n{\"key\": \"value\"}\nThat's it."
        assert _extract_json_object(text) == {"key": "value"}

    def test_nested_json_embedded(self):
        text = (
            "prefix\n"
            '{"outer": {"inner": {"a": 1}}}\n'
            "suffix"
        )
        assert _extract_json_object(text) == {"outer": {"inner": {"a": 1}}}

    def test_json_with_special_chars(self):
        text = '{"msg": "hello\\nworld", "emoji": "🚀"}'
        assert _extract_json_object(text) == {"msg": "hello\nworld", "emoji": "🚀"}

    def test_invalid_json_raises(self):
        with pytest.raises(ValueError, match="Failed to parse"):
            _extract_json_object("this is not json at all")

    def test_unbalanced_braces_raises(self):
        with pytest.raises(ValueError):
            _extract_json_object('{"broken": ')

    def test_multiple_objects_returns_first(self):
        """When output contains multiple JSON objects, the first balanced one wins."""
        text = '{"a":1} {"b":2}'
        assert _extract_json_object(text) == {"a": 1}


# ---------------------------------------------------------------------------
# _parse_single_json_payload
# ---------------------------------------------------------------------------

class TestParseSingleJsonPayload:
    """_parse_single_json_payload — tries to parse entire output as one JSON dict."""

    def test_valid_dict(self):
        text = json.dumps({"result": {"status": "ok"}})
        out = _parse_single_json_payload(text)
        assert out == {"result": {"status": "ok"}}

    def test_empty_string(self):
        assert _parse_single_json_payload("") is None

    def test_whitespace_only(self):
        assert _parse_single_json_payload("  \n  ") is None

    def test_json_array_returns_none(self):
        assert _parse_single_json_payload("[1,2]") is None

    def test_json_string_returns_none(self):
        assert _parse_single_json_payload('"hello"') is None

    def test_invalid_json_returns_none(self):
        assert _parse_single_json_payload("{bad json}") is None

    def test_nested_dict(self):
        text = json.dumps({"a": {"b": {"c": 1}}})
        out = _parse_single_json_payload(text)
        assert isinstance(out, dict)
        assert out["a"]["b"]["c"] == 1


# ---------------------------------------------------------------------------
# _extract_result_from_payload
# ---------------------------------------------------------------------------

class TestExtractResultFromPayload:
    """_extract_result_from_payload — pulls result dict from parsed payload."""

    def test_direct_result_key(self):
        payload = {"result": {"status": "done"}}
        assert _extract_result_from_payload(payload) == {"status": "done"}

    def test_result_not_dict_falls_through(self):
        """When 'result' is not a dict, it falls through to other keys,
        and ultimately wraps the whole payload via _extract_json_object."""
        payload = {"result": "not a dict"}
        # Falls through to structured_output, then output, etc.
        # Finally wraps payload: {"result": "not a dict"} -> valid dict
        result = _extract_result_from_payload(payload)
        assert result == {"result": "not a dict"}

    def test_structured_output_key(self):
        payload = {"structured_output": {"x": 1}}
        assert _extract_result_from_payload(payload) == {"x": 1}

    def test_output_with_status_remark(self):
        """Keys like 'output', 'message' whose value dict has status+remark."""
        payload = {"output": {"status": "ok", "remark": "done"}}
        assert _extract_result_from_payload(payload) == {"status": "ok", "remark": "done"}

    def test_message_with_status_remark(self):
        payload = {"message": {"status": "ok", "remark": "done"}}
        assert _extract_result_from_payload(payload) == {"status": "ok", "remark": "done"}

    def test_response_with_status_remark(self):
        payload = {"response": {"status": "ok", "remark": "done"}}
        assert _extract_result_from_payload(payload) == {"status": "ok", "remark": "done"}

    def test_final_with_status_remark(self):
        payload = {"final": {"status": "ok", "remark": "done"}}
        assert _extract_result_from_payload(payload) == {"status": "ok", "remark": "done"}

    def test_content_with_status_remark(self):
        payload = {"content": {"status": "ok", "remark": "done"}}
        assert _extract_result_from_payload(payload) == {"status": "ok", "remark": "done"}

    def test_value_is_json_string(self):
        """If the value is a JSON string, it should be parsed."""
        payload = {"output": json.dumps({"status": "ok", "remark": "done"})}
        assert _extract_result_from_payload(payload) == {"status": "ok", "remark": "done"}

    def test_value_is_invalid_json_string_fallback(self):
        """Non-JSON string values are skipped; if all keys fail,
        the whole payload is wrapped and parsed."""
        payload = {"output": "not json"}
        result = _extract_result_from_payload(payload)
        assert result == {"output": "not json"}

    def test_no_matching_keys_wraps_payload(self):
        """When no matching keys exist, the whole payload is wrapped
        and parsed as a JSON object."""
        payload = {"foo": "bar"}
        result = _extract_result_from_payload(payload)
        assert result == {"foo": "bar"}

    def test_empty_payload_wraps(self):
        """Empty dict {} wraps to '{}' which parses to {}."""
        result = _extract_result_from_payload({})
        assert result == {}

    def test_result_is_list_falls_through(self):
        """When 'result' is a list, it falls through and eventually wraps the payload."""
        payload = {"result": [1, 2, 3]}
        result = _extract_result_from_payload(payload)
        assert result == {"result": [1, 2, 3]}

    def test_result_not_dict_falls_through_to_structured_output(self):
        payload = {
            "result": "bad",
            "structured_output": {"x": 1},
        }
        assert _extract_result_from_payload(payload) == {"x": 1}


# ---------------------------------------------------------------------------
# _parse_json_payload
# ---------------------------------------------------------------------------

class TestParseJsonPayload:
    """_parse_json_payload — parse entire output as any JSON (not limited to dict)."""

    def test_dict(self):
        text = json.dumps({"a": 1})
        assert _parse_json_payload(text) == {"a": 1}

    def test_list(self):
        text = json.dumps([1, 2, 3])
        assert _parse_json_payload(text) == [1, 2, 3]

    def test_empty(self):
        assert _parse_json_payload("") is None

    def test_invalid(self):
        assert _parse_json_payload("not json") is None

    def test_string(self):
        assert _parse_json_payload('"hello"') == "hello"

    def test_number(self):
        assert _parse_json_payload("42") == 42

    def test_whitespace_padded(self):
        text = "  " + json.dumps({"x": 1}) + "  "
        assert _parse_json_payload(text) == {"x": 1}


# ---------------------------------------------------------------------------
# _payload_to_raw_events
# ---------------------------------------------------------------------------

class TestPayloadToRawEvents:
    """_payload_to_raw_events — converts payload into list of JSON-line strings."""

    def test_dict_payload(self):
        payload = {"type": "result", "data": "ok"}
        events = _payload_to_raw_events(payload, "ignored stdout")
        assert events == [json.dumps(payload)]

    def test_list_payload(self):
        payload = [{"type": "start"}, {"type": "end"}]
        events = _payload_to_raw_events(payload, "ignored")
        assert events == [json.dumps({"type": "start"}), json.dumps({"type": "end"})]

    def test_list_payload_filters_non_dict_non_list(self):
        payload = [{"type": "ok"}, "string", 42, None]
        events = _payload_to_raw_events(payload, "ignored")
        assert len(events) == 1
        assert json.loads(events[0]) == {"type": "ok"}

    def test_scalar_payload_falls_back_to_stdout_lines(self):
        stdout = "line1\nline2\n\n  line3  "
        events = _payload_to_raw_events(42, stdout)
        # Lines are preserved as-is (including trailing whitespace)
        assert events == ["line1", "line2", "  line3  "]

    def test_none_payload_falls_back_to_stdout(self):
        stdout = "hello\nworld"
        events = _payload_to_raw_events(None, stdout)
        assert events == ["hello", "world"]

    def test_empty_lines_skipped(self):
        stdout = "\n\n\n"
        events = _payload_to_raw_events(None, stdout)
        assert events == []


# ---------------------------------------------------------------------------
# _extract_result_from_qwen_payload
# ---------------------------------------------------------------------------

class TestExtractResultFromQwenPayload:
    """_extract_result_from_qwen_payload — handles qwen-specific output shapes."""

    def test_dict_payload_delegates(self):
        payload = {"result": {"status": "ok"}}
        result = _extract_result_from_qwen_payload(payload)
        assert result == {"status": "ok"}

    def test_event_list_with_result_dict(self):
        payload = [
            {"type": "progress", "message": "working..."},
            {"result": {"answer": 42}},
        ]
        result = _extract_result_from_qwen_payload(payload)
        assert result == {"answer": 42}

    def test_event_list_result_is_json_string(self):
        payload = [
            {"result": json.dumps({"status": "ok"})},
        ]
        result = _extract_result_from_qwen_payload(payload)
        assert result == {"status": "ok"}

    def test_event_list_result_is_error_string(self):
        payload = [
            {"result": "[API ERROR: timeout]"},
        ]
        with pytest.raises(ValueError, match="Last agent error"):
            _extract_result_from_qwen_payload(payload)

    def test_event_list_message_content_text(self):
        payload = [
            {
                "message": {
                    "content": [
                        {"type": "text", "text": json.dumps({"final": True})},
                    ]
                }
            }
        ]
        result = _extract_result_from_qwen_payload(payload)
        assert result == {"final": True}

    def test_event_list_message_content_error_text(self):
        payload = [
            {
                "message": {
                    "content": [
                        {"type": "text", "text": "[API ERROR: rate limited]"},
                    ]
                }
            }
        ]
        with pytest.raises(ValueError, match="Last agent error"):
            _extract_result_from_qwen_payload(payload)

    def test_event_list_no_result_raises(self):
        payload = [{"type": "progress"}]
        with pytest.raises(ValueError, match="No JSON object result"):
            _extract_result_from_qwen_payload(payload)

    def test_non_list_non_dict_raises(self):
        with pytest.raises(ValueError, match="neither an object nor an event list"):
            _extract_result_from_qwen_payload("not a dict or list")

    def test_empty_list_raises(self):
        with pytest.raises(ValueError):
            _extract_result_from_qwen_payload([])

    def test_event_list_reversed_order(self):
        """Result in the last event (reversed iteration finds it first)."""
        payload = [
            {"type": "start"},
            {"type": "middle"},
            {"result": {"found": "it"}},
        ]
        result = _extract_result_from_qwen_payload(payload)
        assert result == {"found": "it"}

    def test_event_list_result_json_string_invalid_skipped(self):
        """Non-JSON result strings that don't look like errors are skipped."""
        payload = [
            {"result": "some progress text"},
            {"result": json.dumps({"ok": True})},
        ]
        result = _extract_result_from_qwen_payload(payload)
        assert result == {"ok": True}

    def test_error_message_deduplication(self):
        """Duplicate error messages should be deduplicated."""
        payload = [
            {"result": "[API ERROR: timeout]"},
            {"result": "[API ERROR: timeout]"},
        ]
        with pytest.raises(ValueError) as exc:
            _extract_result_from_qwen_payload(payload)
        # Should mention the error only once
        assert str(exc.value).count("timeout") == 1


# ---------------------------------------------------------------------------
# _looks_like_qwen_error_text
# ---------------------------------------------------------------------------

class TestLooksLikeQwenErrorText:
    """_looks_like_qwen_error_text — heuristic error detection."""

    @pytest.mark.parametrize("text", [
        "[API ERROR: timeout]",
        "[api error: something went wrong]",
        "Connection error: refused",
        "Fetch failed: bad gateway",
        "Error: something broke",
        "error: lowercase ok",
    ])
    def test_matches(self, text):
        assert _looks_like_qwen_error_text(text) is True

    @pytest.mark.parametrize("text", [
        "",
        "   ",
        "this is fine",
        '{"result": "ok"}',
        "All systems operational",
    ])
    def test_no_match(self, text):
        assert _looks_like_qwen_error_text(text) is False

    def test_whitespace_trimming(self):
        assert _looks_like_qwen_error_text("  Error: oops  ") is True


# ---------------------------------------------------------------------------
# _usage_from_json_events
# ---------------------------------------------------------------------------

class TestUsageFromJsonEvents:
    """_usage_from_json_events — parse usage from codex-style NDJSON events."""

    def test_events_with_usage(self):
        lines = [
            json.dumps({"type": "session", "usage": {"input_tokens": 100, "output_tokens": 50}}),
            json.dumps({"type": "result"}),
        ]
        usage = _usage_from_json_events(lines, step="test", coder="codex")
        assert usage.input_tokens == 100
        assert usage.output_tokens == 50
        assert usage.total_tokens == 150
        assert usage.usage_source == "cli_reported"

    def test_events_without_usage(self):
        lines = [json.dumps({"type": "result", "data": "ok"})]
        usage = _usage_from_json_events(lines, step="test", coder="codex")
        assert usage.input_tokens is None
        assert usage.output_tokens is None
        assert usage.total_tokens is None
        assert usage.usage_source == "not_available"

    def test_empty_events(self):
        usage = _usage_from_json_events([], step="test", coder="codex")
        assert usage.usage_source == "not_available"

    def test_mixed_valid_invalid_lines(self):
        lines = [
            "not json",
            json.dumps({"usage": {"input_tokens": 200}}),
            "also not json",
        ]
        usage = _usage_from_json_events(lines, step="test", coder="codex")
        assert usage.input_tokens == 200

    def test_usage_token_aliases(self):
        lines = [json.dumps({"usage": {"prompt_tokens": 50, "completion_tokens": 30}})]
        usage = _usage_from_json_events(lines, step="test", coder="codex")
        assert usage.input_tokens == 50
        assert usage.output_tokens == 30
        assert usage.total_tokens == 80

    def test_cost_extraction(self):
        lines = [json.dumps({"usage": {"cost": 0.042}})]
        usage = _usage_from_json_events(lines, step="test", coder="codex")
        assert usage.cost == 0.042


# ---------------------------------------------------------------------------
# _usage_from_payload
# ---------------------------------------------------------------------------

class TestUsageFromPayload:
    """_usage_from_payload — extract usage from a parsed payload dict."""

    def test_with_usage(self):
        payload = {"events": [{"usage": {"input_tokens": 10, "output_tokens": 5}}]}
        usage = _usage_from_payload(payload, step="s", coder="qwen")
        assert usage.input_tokens == 10
        assert usage.output_tokens == 5
        assert usage.total_tokens == 15
        assert usage.step == "s"
        assert usage.coder_used == "qwen"

    def test_empty_payload(self):
        usage = _usage_from_payload({}, step="s", coder="qwen")
        assert usage.usage_source == "not_available"

    def test_none_payload(self):
        usage = _usage_from_payload(None, step="s", coder="qwen")
        assert usage.usage_source == "not_available"

    def test_token_sum_computed(self):
        payload = {"usage": {"input_tokens": 100, "output_tokens": 200}}
        usage = _usage_from_payload(payload, step="s", coder="qwen")
        assert usage.total_tokens == 300

    def test_total_tokens_not_doubled_when_provided(self):
        payload = {"usage": {"input_tokens": 100, "output_tokens": 200, "total_tokens": 350}}
        usage = _usage_from_payload(payload, step="s", coder="qwen")
        assert usage.total_tokens == 350

    def test_cost_string_coerced(self):
        payload = {"usage": {"cost": "0.01"}}
        usage = _usage_from_payload(payload, step="s", coder="qwen")
        assert usage.cost == 0.01

    def test_usage_source(self):
        payload = {"usage": {"input_tokens": 1}}
        usage = _usage_from_payload(payload, step="s", coder="qwen")
        assert usage.usage_source == "cli_reported"


# ---------------------------------------------------------------------------
# _collect_usage_metrics & merge_usage
# ---------------------------------------------------------------------------

class TestCollectUsageMetrics:
    """_collect_usage_metrics — deep-visit payload to collect usage fields."""

    def test_flat_usage(self):
        payload = {"usage": {"input_tokens": 10, "output_tokens": 5}}
        metrics = _collect_usage_metrics(payload)
        assert metrics["input_tokens"] == 10
        assert metrics["output_tokens"] == 5

    def test_nested_events(self):
        payload = {"events": [{"usage": {"input_tokens": 10}}, {"usage": {"output_tokens": 5}}]}
        metrics = _collect_usage_metrics(payload)
        assert metrics["input_tokens"] == 10
        assert metrics["output_tokens"] == 5

    def test_token_aliases(self):
        payload = {"usage": {"prompt_tokens": 20, "completion_tokens": 30}}
        metrics = _collect_usage_metrics(payload)
        assert metrics["input_tokens"] == 20
        assert metrics["output_tokens"] == 30

    def test_empty_payload(self):
        assert _collect_usage_metrics({}) == {}

    def test_non_dict_payload(self):
        assert _collect_usage_metrics([]) == {}
        assert _collect_usage_metrics("hello") == {}


class TestMergeUsage:
    """merge_usage — merge canonical keys from source aliases."""

    def test_canonical_key_copied(self):
        target: dict = {}
        source = {"input_tokens": 10}
        merge_usage(target, source)
        assert target["input_tokens"] == 10

    def test_alias_mapped(self):
        target: dict = {}
        source = {"prompt_tokens": 25}
        merge_usage(target, source)
        assert target["input_tokens"] == 25

    def test_completion_tokens_alias(self):
        target: dict = {}
        source = {"completionTokens": 100}
        merge_usage(target, source)
        assert target["output_tokens"] == 100

    def test_cost_aliases(self):
        target: dict = {}
        source = {"total_cost": 0.05}
        merge_usage(target, source)
        assert target["cost"] == 0.05

    def test_existing_value_not_overwritten(self):
        target = {"input_tokens": 100}
        source = {"input_tokens": 200}
        merge_usage(target, source)
        assert target["input_tokens"] == 100

    def test_none_value_ignored(self):
        target: dict = {}
        source = {"input_tokens": None}
        merge_usage(target, source)
        assert "input_tokens" not in target

    def test_total_tokens_alias(self):
        target: dict = {}
        source = {"totalTokens": 500}
        merge_usage(target, source)
        assert target["total_tokens"] == 500

    def test_multiple_fields(self):
        target: dict = {}
        source = {"prompt_tokens": 10, "completion_tokens": 20, "totalCost": 0.1}
        merge_usage(target, source)
        assert target["input_tokens"] == 10
        assert target["output_tokens"] == 20
        assert target["cost"] == 0.1


# ---------------------------------------------------------------------------
# _coerce_int / _coerce_float
# ---------------------------------------------------------------------------

class TestCoerceInt:
    def test_none(self):
        assert _coerce_int(None) is None

    def test_int(self):
        assert _coerce_int(42) == 42

    def test_string_int(self):
        assert _coerce_int("42") == 42

    def test_float_truncated(self):
        assert _coerce_int(3.9) == 3

    def test_invalid_string(self):
        assert _coerce_int("abc") is None

    def test_empty_string(self):
        assert _coerce_int("") is None

    def test_list_raises(self):
        assert _coerce_int([1]) is None


class TestCoerceFloat:
    def test_none(self):
        assert _coerce_float(None) is None

    def test_float(self):
        assert _coerce_float(0.042) == pytest.approx(0.042)

    def test_string_float(self):
        assert _coerce_float("0.042") == pytest.approx(0.042)

    def test_int(self):
        assert _coerce_int(1) == 1

    def test_invalid_string(self):
        assert _coerce_float("abc") is None

    def test_empty_string(self):
        assert _coerce_float("") is None


# ---------------------------------------------------------------------------
# _mask_api_key
# ---------------------------------------------------------------------------

class TestMaskApiKey:
    """_mask_api_key — mask sensitive API keys in logs."""

    def test_long_key(self):
        key = "sk-proj-abcdef1234567890xyz"
        masked = _mask_api_key(key)
        assert masked.startswith(key[:4])
        assert masked.endswith(key[-4:])
        assert "****" in masked
        assert masked == "sk-p****0xyz"

    def test_short_key(self):
        assert _mask_api_key("short") == "****"

    def test_8_char_key(self):
        assert _mask_api_key("12345678") == "****"

    def test_9_char_key(self):
        result = _mask_api_key("123456789")
        assert result == "1234****6789"

    def test_empty_key(self):
        assert _mask_api_key("") == "****"


# ---------------------------------------------------------------------------
# _is_valid_sidecar_json
# ---------------------------------------------------------------------------

class TestIsValidSidecarJson:
    """_is_valid_sidecar_json — validate sidecar meta.json files."""

    def test_valid_v2(self, tmp_path):
        data = {
            "schema_version": "v2",
            "coder_result": {
                "status": "APPROVED",
                "artifacts": {},
                "recorded_at": "2026-06-01T00:00:00Z",
            },
        }
        p = tmp_path / "meta.json"
        p.write_text(json.dumps(data))
        assert _is_valid_sidecar_json(p) is True

    def test_valid_v2_rejected(self, tmp_path):
        data = {
            "schema_version": "v2",
            "coder_result": {
                "status": "REJECTED",
                "artifacts": {},
                "recorded_at": "2026-06-01T00:00:00Z",
            },
        }
        p = tmp_path / "meta.json"
        p.write_text(json.dumps(data))
        assert _is_valid_sidecar_json(p) is True

    def test_valid_legacy(self, tmp_path):
        data = {
            "sidecar_version": "artifact_meta_v1",
            "coder_result": {
                "status": "APPROVED",
                "artifacts": {},
                "recorded_at": "2026-06-01T00:00:00Z",
            },
        }
        p = tmp_path / "meta.json"
        p.write_text(json.dumps(data))
        assert _is_valid_sidecar_json(p) is True

    def test_invalid_schema_version(self, tmp_path):
        data = {
            "schema_version": "v1",
            "coder_result": {"status": "APPROVED", "artifacts": {}, "recorded_at": "2026-06-01"},
        }
        p = tmp_path / "meta.json"
        p.write_text(json.dumps(data))
        assert _is_valid_sidecar_json(p) is False

    def test_missing_status(self, tmp_path):
        data = {
            "schema_version": "v2",
            "coder_result": {"artifacts": {}, "recorded_at": "2026-06-01"},
        }
        p = tmp_path / "meta.json"
        p.write_text(json.dumps(data))
        assert _is_valid_sidecar_json(p) is False

    def test_invalid_status(self, tmp_path):
        data = {
            "schema_version": "v2",
            "coder_result": {"status": "PENDING", "artifacts": {}, "recorded_at": "2026-06-01"},
        }
        p = tmp_path / "meta.json"
        p.write_text(json.dumps(data))
        assert _is_valid_sidecar_json(p) is False

    def test_missing_artifacts(self, tmp_path):
        data = {
            "schema_version": "v2",
            "coder_result": {"status": "APPROVED", "recorded_at": "2026-06-01"},
        }
        p = tmp_path / "meta.json"
        p.write_text(json.dumps(data))
        assert _is_valid_sidecar_json(p) is False

    def test_missing_recorded_at(self, tmp_path):
        data = {
            "schema_version": "v2",
            "coder_result": {"status": "APPROVED", "artifacts": {}},
        }
        p = tmp_path / "meta.json"
        p.write_text(json.dumps(data))
        assert _is_valid_sidecar_json(p) is False

    def test_empty_recorded_at(self, tmp_path):
        data = {
            "schema_version": "v2",
            "coder_result": {"status": "APPROVED", "artifacts": {}, "recorded_at": ""},
        }
        p = tmp_path / "meta.json"
        p.write_text(json.dumps(data))
        assert _is_valid_sidecar_json(p) is False

    def test_file_not_exists(self, tmp_path):
        p = tmp_path / "nonexistent.json"
        assert _is_valid_sidecar_json(p) is False

    def test_invalid_json(self, tmp_path):
        p = tmp_path / "meta.json"
        p.write_text("{bad json")
        assert _is_valid_sidecar_json(p) is False

    def test_json_not_dict(self, tmp_path):
        p = tmp_path / "meta.json"
        p.write_text("[1,2,3]")
        assert _is_valid_sidecar_json(p) is False

    def test_case_insensitive_status(self, tmp_path):
        data = {
            "schema_version": "v2",
            "coder_result": {"status": "approved", "artifacts": {}, "recorded_at": "2026-06-01"},
        }
        p = tmp_path / "meta.json"
        p.write_text(json.dumps(data))
        assert _is_valid_sidecar_json(p) is True


# ---------------------------------------------------------------------------
# _coder_timeout_seconds
# ---------------------------------------------------------------------------

class TestCoderTimeoutSeconds:
    """_coder_timeout_seconds — read from env with fallback."""

    def test_default(self, monkeypatch):
        monkeypatch.delenv("AGENT_RUNNER_CODER_TIMEOUT_SECONDS", raising=False)
        assert _coder_timeout_seconds() == DEFAULT_CODER_TIMEOUT_SECONDS

    def test_custom_value(self, monkeypatch):
        monkeypatch.setenv("AGENT_RUNNER_CODER_TIMEOUT_SECONDS", "120")
        assert _coder_timeout_seconds() == 120

    def test_invalid_value_falls_back(self, monkeypatch):
        monkeypatch.setenv("AGENT_RUNNER_CODER_TIMEOUT_SECONDS", "abc")
        assert _coder_timeout_seconds() == DEFAULT_CODER_TIMEOUT_SECONDS

    def test_zero_falls_back(self, monkeypatch):
        monkeypatch.setenv("AGENT_RUNNER_CODER_TIMEOUT_SECONDS", "0")
        assert _coder_timeout_seconds() == DEFAULT_CODER_TIMEOUT_SECONDS

    def test_negative_falls_back(self, monkeypatch):
        monkeypatch.setenv("AGENT_RUNNER_CODER_TIMEOUT_SECONDS", "-10")
        assert _coder_timeout_seconds() == DEFAULT_CODER_TIMEOUT_SECONDS

    def test_whitespace_trimmed(self, monkeypatch):
        monkeypatch.setenv("AGENT_RUNNER_CODER_TIMEOUT_SECONDS", "  300  ")
        assert _coder_timeout_seconds() == 300

    def test_empty_string_falls_back(self, monkeypatch):
        monkeypatch.setenv("AGENT_RUNNER_CODER_TIMEOUT_SECONDS", "")
        assert _coder_timeout_seconds() == DEFAULT_CODER_TIMEOUT_SECONDS


# ---------------------------------------------------------------------------
# dataclass_dict
# ---------------------------------------------------------------------------

class TestDataclassDict:
    """dataclass_dict — convert dataclass to dict."""

    def test_usage_data(self):
        ud = UsageData(
            step="test", coder_used="qwen", usage_source="cli_reported",
            input_tokens=10, output_tokens=5, total_tokens=15,
            cost=0.01, duration_ms=100,
            started_at="2026-06-01T00:00:00", finished_at="2026-06-01T00:00:01",
        )
        d = dataclass_dict(ud)
        assert d["step"] == "test"
        assert d["input_tokens"] == 10
        assert isinstance(d, dict)

    def test_invocation_manifest(self):
        m = InvocationManifest(
            step_name="test", coder_used="qwen", command=["qwen"],
            cwd="/tmp", prompt_checksum="abc123",
            started_at="2026-06-01T00:00:00", finished_at="2026-06-01T00:00:01",
            return_code=0,
        )
        d = dataclass_dict(m)
        assert d["step_name"] == "test"
        assert d["return_code"] == 0


# ---------------------------------------------------------------------------
# Constants sanity
# ---------------------------------------------------------------------------

class TestConstants:
    def test_default_timeout_positive(self):
        assert DEFAULT_CODER_TIMEOUT_SECONDS > 0

    def test_sidecar_grace_period(self):
        assert SIDECAR_GRACE_PERIOD_SECONDS > 0

    def test_sidecar_poll_interval(self):
        assert SIDECAR_POLL_INTERVAL_SECONDS > 0

    def test_sidecar_settle_delay(self):
        assert SIDECAR_SETTLE_DELAY_SECONDS > 0


# ---------------------------------------------------------------------------
# CoderInvocationError
# ---------------------------------------------------------------------------

class TestCoderInvocationError:
    """CoderInvocationError — custom exception for coder failures."""

    def test_str(self):
        exc = CoderInvocationError(
            message="Timeout", command=["qwen"], return_code=124,
            stdout="", stderr="", raw_events=[],
        )
        assert str(exc) == "Timeout"

    def test_has_all_fields(self):
        exc = CoderInvocationError(
            message="oops", command=["a", "b"], return_code=1,
            stdout="out", stderr="err", raw_events=["e1"],
        )
        assert exc.message == "oops"
        assert exc.command == ["a", "b"]
        assert exc.return_code == 1
        assert exc.stdout == "out"
        assert exc.stderr == "err"
        assert exc.raw_events == ["e1"]
