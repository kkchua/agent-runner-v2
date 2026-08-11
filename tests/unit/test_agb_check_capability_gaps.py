"""Tests for the AGB check_capability_gaps action.

Verifies that the action correctly detects blocking capability gaps
and returns REJECTED with install instructions when libraries are missing.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[2] / "workflows" / "artifact_generator_builder"),
)

from actions import check_capability_gaps, _extract_import_name
from agent_runner_v2.action_result import ActionResult


def _write_analysis(tmp_path: Path, gaps: list[dict]) -> Path:
    """Write a minimal Analysis JSON with the given capability_gaps."""
    analysis = {
        "identity": {"name": "test", "codename": "test"},
        "domain_steps": [],
        "artifact_keys": {"inputs": [], "outputs": []},
        "implementations": [],
        "capability_gaps": gaps,
    }
    path = tmp_path / "ANALYSIS_JSON-001.json"
    path.write_text(json.dumps(analysis), encoding="utf-8")
    return path


def _make_state(analysis_path: str) -> dict:
    return {"artifacts": {"ANALYSIS_JSON_FILE": analysis_path}}


def _make_context():
    return {}


def _make_step_cfg():
    return {}


class TestCheckCapabilityGaps:
    def test_no_gaps_approved(self, tmp_path):
        path = _write_analysis(tmp_path, [])
        result = check_capability_gaps(
            context=_make_context(),
            state=_make_state(str(path)),
            step_cfg=_make_step_cfg(),
            project_root=str(tmp_path),
        )
        assert result.status == "APPROVED"
        assert "No blocking" in result.remark

    def test_non_blocking_gaps_approved(self, tmp_path):
        gaps = [
            {
                "requirement": "optional PDF support",
                "missing_capability": "PDF parsing",
                "proposed_solution": "pip install PyPDF2",
                "blocking": False,
            }
        ]
        path = _write_analysis(tmp_path, gaps)
        result = check_capability_gaps(
            context=_make_context(),
            state=_make_state(str(path)),
            step_cfg=_make_step_cfg(),
            project_root=str(tmp_path),
        )
        assert result.status == "APPROVED"

    def test_blocking_gap_unmet_rejected(self, tmp_path):
        gaps = [
            {
                "requirement": "Support .pdf input",
                "missing_capability": "PDF parsing",
                "proposed_solution": "pip install PyPDF2",
                "blocking": True,
            }
        ]
        path = _write_analysis(tmp_path, gaps)
        # Mock importlib to simulate library not installed
        with patch("actions.importlib.import_module", side_effect=ImportError("No module")):
            result = check_capability_gaps(
                context=_make_context(),
                state=_make_state(str(path)),
                step_cfg=_make_step_cfg(),
                project_root=str(tmp_path),
            )
        assert result.status == "REJECTED"
        assert result.reject_code == "CAPABILITY_GAP_BLOCKING"
        assert "pip install PyPDF2" in result.remark
        assert "PyPDF2" in result.remark

    def test_blocking_gap_resolved_approved(self, tmp_path):
        gaps = [
            {
                "requirement": "Support .pdf input",
                "missing_capability": "PDF parsing",
                "proposed_solution": "pip install PyPDF2",
                "blocking": True,
            }
        ]
        path = _write_analysis(tmp_path, gaps)
        # Mock importlib to simulate library installed
        with patch("actions.importlib.import_module", return_value=True):
            result = check_capability_gaps(
                context=_make_context(),
                state=_make_state(str(path)),
                step_cfg=_make_step_cfg(),
                project_root=str(tmp_path),
            )
        assert result.status == "APPROVED"
        assert "resolved" in result.remark.lower()

    def test_missing_analysis_json_rejected(self, tmp_path):
        result = check_capability_gaps(
            context=_make_context(),
            state={"artifacts": {}},
            step_cfg=_make_step_cfg(),
            project_root=str(tmp_path),
        )
        assert result.status == "REJECTED"
        assert result.reject_code == "MISSING_ANALYSIS_JSON"

    def test_nonexistent_analysis_file_rejected(self, tmp_path):
        result = check_capability_gaps(
            context=_make_context(),
            state=_make_state(str(tmp_path / "nonexistent.json")),
            step_cfg=_make_step_cfg(),
            project_root=str(tmp_path),
        )
        assert result.status == "REJECTED"
        assert result.reject_code == "MISSING_ANALYSIS_JSON"

    def test_multiple_gaps_mixed_blocking(self, tmp_path):
        gaps = [
            {
                "requirement": "Support .pdf input",
                "missing_capability": "PDF parsing",
                "proposed_solution": "pip install PyPDF2",
                "blocking": True,
            },
            {
                "requirement": "Support .docx input",
                "missing_capability": "DOCX parsing",
                "proposed_solution": "pip install python-docx",
                "blocking": True,
            },
        ]
        path = _write_analysis(tmp_path, gaps)
        with patch("actions.importlib.import_module", side_effect=ImportError("No module")):
            result = check_capability_gaps(
                context=_make_context(),
                state=_make_state(str(path)),
                step_cfg=_make_step_cfg(),
                project_root=str(tmp_path),
            )
        assert result.status == "REJECTED"
        assert "PyPDF2" in result.remark
        assert "python-docx" in result.remark or "docx" in result.remark


class TestExtractImportName:
    def test_explicit_import_name(self):
        gap = {"import_name": "custom_module", "proposed_solution": "pip install custom-pkg"}
        assert _extract_import_name(gap) == "custom_module"

    def test_pip_install_extraction(self):
        gap = {"proposed_solution": "pip install PyPDF2"}
        assert _extract_import_name(gap) == "PyPDF2"

    def test_pip_install_with_version(self):
        gap = {"proposed_solution": "pip install PyPDF2==2.0"}
        assert _extract_import_name(gap) == "PyPDF2"

    def test_python_docx_mapping(self):
        gap = {"proposed_solution": "pip install python-docx"}
        assert _extract_import_name(gap) == "docx"

    def test_pillow_mapping(self):
        gap = {"proposed_solution": "pip install Pillow"}
        assert _extract_import_name(gap) == "PIL"

    def test_no_solution_returns_none(self):
        gap = {"proposed_solution": ""}
        assert _extract_import_name(gap) is None
