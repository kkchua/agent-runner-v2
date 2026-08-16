"""Tests for date-based job directory structure and _extract_date_from_job_id."""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from agent_runner_v2.job_state import (
    _extract_date_from_job_id,
    group_dir,
    job_dir,
    _legacy_group_dir,
)


class TestExtractDateFromJobId:
    def test_standard_format(self):
        assert _extract_date_from_job_id("AMGEN-20260804-001") == "20260804"

    def test_with_source_id(self):
        assert _extract_date_from_job_id("SDLC-INIT-20260715-003") == "20260715"

    def test_with_gen_source(self):
        assert _extract_date_from_job_id("CORE-GEN-20260101-042") == "20260101"

    def test_no_date_returns_none(self):
        assert _extract_date_from_job_id("NO-DATE-HERE") is None

    def test_empty_string_returns_none(self):
        assert _extract_date_from_job_id("") is None

    def test_single_segment_returns_none(self):
        assert _extract_date_from_job_id("SINGLE") is None

    def test_non_numeric_date_returns_none(self):
        assert _extract_date_from_job_id("PRE-ABCD-001") is None

    def test_short_date_returns_none(self):
        assert _extract_date_from_job_id("PRE-1234-001") is None


class TestGroupDir:
    def test_default_date_is_today(self):
        from datetime import datetime
        today = datetime.now().strftime("%Y%m%d")
        result = group_dir("my_workflow")
        # Check that the path ends with the expected components
        assert result.name == "my_workflow"
        assert result.parent.name == today

    def test_explicit_date(self):
        result = group_dir("my_workflow", date="20260804")
        assert result.name == "my_workflow"
        assert result.parent.name == "20260804"


class TestLegacyGroupDir:
    def test_no_date_prefix(self):
        result = _legacy_group_dir("my_workflow")
        assert result.name == "my_workflow"
        # Parent should be the jobs root, not a date folder
        assert not result.parent.name.isdigit()


class TestJobDir:
    def test_env_var_overrides_computation(self, tmp_path: Path):
        custom_path = str(tmp_path / "custom" / "job" / "dir")
        with patch.dict(os.environ, {"AGENT_RUNNER_JOB_DIR": custom_path}):
            result = job_dir("any_workflow", "ANY-20260804-001")
            assert str(result) == custom_path

    def test_empty_env_var_uses_computation(self):
        with patch.dict(os.environ, {"AGENT_RUNNER_JOB_DIR": ""}):
            result = job_dir("my_workflow", "MY-GEN-20260804-001")
            assert "20260804" in str(result)
            assert "my_workflow" in str(result)
            assert "MY-GEN-20260804-001" in str(result)

    def test_date_extracted_from_job_id(self):
        result = job_dir("wf", "WF-GEN-20260715-003")
        assert "20260715" in str(result)

    def test_legacy_fallback_when_date_path_missing(self, tmp_path: Path, monkeypatch):
        """When date-based path doesn't exist but legacy path does, use legacy."""
        # Create a legacy job dir
        legacy = tmp_path / "jobs" / "wf" / "WF-GEN-20260101-001"
        legacy.mkdir(parents=True)

        monkeypatch.setattr("agent_runner_v2.job_state.JOBS_ROOT", tmp_path / "jobs")
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("AGENT_RUNNER_JOB_DIR", None)
            result = job_dir("wf", "WF-GEN-20260101-001")
            # Should find the legacy path
            assert result == legacy

    def test_new_job_uses_date_path(self, tmp_path: Path, monkeypatch):
        """When neither path exists, default to date-based path."""
        monkeypatch.setattr("agent_runner_v2.job_state.JOBS_ROOT", tmp_path / "jobs")
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("AGENT_RUNNER_JOB_DIR", None)
            result = job_dir("wf", "WF-GEN-20260804-001")
            assert "20260804" in str(result)
