"""Tests for agent_runner_v2.action_result."""
from __future__ import annotations

import pytest

from agent_runner_v2.action_result import ActionResult


# ---------------------------------------------------------------------------
# Basic construction
# ---------------------------------------------------------------------------

class TestActionResultConstruction:
    def test_minimal_required_fields(self):
        result = ActionResult(status="APPROVED", remark="ok", artifacts={})
        assert result.status == "APPROVED"
        assert result.remark == "ok"
        assert result.artifacts == {}
        assert result.reject_code is None

    def test_with_reject_code(self):
        result = ActionResult(status="REJECTED", remark="bad", artifacts={}, reject_code="INVALID_FORMAT")
        assert result.reject_code == "INVALID_FORMAT"

    def test_with_artifacts(self):
        artifacts = {"INIT_FILE": "docs/init.md"}
        result = ActionResult(status="APPROVED", remark="done", artifacts=artifacts)
        assert result.artifacts is artifacts


# ---------------------------------------------------------------------------
# Dataclass behavior
# ---------------------------------------------------------------------------

class TestActionResultDataclass:
    def test_equality(self):
        a = ActionResult(status="APPROVED", remark="ok", artifacts={})
        b = ActionResult(status="APPROVED", remark="ok", artifacts={})
        assert a == b

    def test_inequality_status(self):
        a = ActionResult(status="APPROVED", remark="ok", artifacts={})
        b = ActionResult(status="REJECTED", remark="ok", artifacts={})
        assert a != b

    def test_inequality_remark(self):
        a = ActionResult(status="APPROVED", remark="ok", artifacts={})
        b = ActionResult(status="APPROVED", remark="not ok", artifacts={})
        assert a != b

    def test_inequality_reject_code(self):
        a = ActionResult(status="REJECTED", remark="bad", artifacts={}, reject_code="CODE_A")
        b = ActionResult(status="REJECTED", remark="bad", artifacts={}, reject_code="CODE_B")
        assert a != b

    def test_repr(self):
        result = ActionResult(status="APPROVED", remark="ok", artifacts={})
        r = repr(result)
        assert "ActionResult" in r
        assert "APPROVED" in r

    def test_order(self):
        """Dataclass fields are in declaration order."""
        result = ActionResult(status="REJECTED", remark="nope", artifacts={}, reject_code="FAIL")
        fields = result.__dataclass_fields__
        keys = list(fields.keys())
        assert keys == ["status", "remark", "artifacts", "reject_code"]


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestActionResultEdgeCases:
    def test_empty_remark(self):
        result = ActionResult(status="APPROVED", remark="", artifacts={})
        assert result.remark == ""

    def test_none_in_artifacts(self):
        result = ActionResult(status="APPROVED", remark="ok", artifacts={"KEY": None})
        assert result.artifacts["KEY"] is None

    def test_reject_code_none_explicit(self):
        result = ActionResult(status="APPROVED", remark="ok", artifacts={}, reject_code=None)
        assert result.reject_code is None

    def test_mutable_artifacts_not_shared(self):
        """Each instance gets its own artifacts dict when passed."""
        artifacts = {"x": 1}
        a = ActionResult(status="APPROVED", remark="a", artifacts=artifacts)
        b = ActionResult(status="APPROVED", remark="b", artifacts={"y": 2})
        assert a.artifacts is artifacts
        assert b.artifacts != a.artifacts

    def test_reject_code_with_approved_status(self):
        """Nothing prevents reject_code on APPROVED (API allows it)."""
        result = ActionResult(status="APPROVED", remark="ok", artifacts={}, reject_code="CODE")
        assert result.reject_code == "CODE"
        assert result.status == "APPROVED"
