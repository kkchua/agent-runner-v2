"""Unit tests for Text Summarizer context extensions."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def _load_context_extensions_module():
    module_path = (
        Path(__file__).resolve().parents[4]
        / "workflows"
        / "text_summarizer_ayz"
        / "context_extensions.py"
    )
    spec = importlib.util.spec_from_file_location("text_summarizer_ayz.context_extensions", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load context_extensions module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestDynamicOutputNaming:
    """Verify that context extensions correctly derive output filenames from source documents."""

    @patch("agent_runner_v2.runtime_context.get_governance_runtime_root")
    @patch("agent_runner_v2.runtime_context.get_platform_runtime_root")
    @patch("agent_runner_v2.runtime_context.get_workspace_root")
    def test_output_named_after_source_document(self, mock_get_ws, mock_get_platform, mock_get_gov):
        """Test that OUTPUT_FILE is named after the input document stem."""
        context_ext = _load_context_extensions_module()

        # Setup mocks
        workspace_root = Path("D:/TestWorkspace")
        mock_get_ws.return_value = str(workspace_root)
        mock_get_gov.return_value = Path("D:/Governance")
        mock_get_platform.return_value = Path("D:/Platform")

        # Create extension instance
        ext = context_ext.TextSummarizerAyzExtensions()

        # Mock state with a source document
        job_id = "TEST-001"
        state = {
            "job_id": job_id,
            "artifacts": {
                "SOURCE_DOCUMENT_FILE": "D:/TestWorkspace/input/My Report.pdf"
            },
            "seq": "001",
        }

        # Build context
        result = ext.build_context_extensions(
            state=state, step="test", step_cfg={}, ctx={}
        )

        # Assertions
        expected_filename = "My Report.md"
        expected_path = str(workspace_root / "output" / job_id / expected_filename)

        assert result.get("OUTPUT_FILE") == expected_path, (
            f"Expected {expected_path}, got {result.get('OUTPUT_FILE')}"
        )
        assert result.get("source_doc_filename") == "My Report"

    @patch("agent_runner_v2.runtime_context.get_governance_runtime_root")
    @patch("agent_runner_v2.runtime_context.get_platform_runtime_root")
    @patch("agent_runner_v2.runtime_context.get_workspace_root")
    def test_fallback_to_default_output_when_no_source(self, mock_get_ws, mock_get_platform, mock_get_gov):
        """Test that it falls back to default naming if source document is missing."""
        context_ext = _load_context_extensions_module()

        workspace_root = Path("D:/TestWorkspace")
        mock_get_ws.return_value = str(workspace_root)
        mock_get_gov.return_value = Path("D:/Governance")
        mock_get_platform.return_value = Path("D:/Platform")

        ext = context_ext.TextSummarizerAyzExtensions()

        # State with no source document artifact
        job_id = "TEST-002"
        state = {
            "job_id": job_id,
            "artifacts": {},
            "seq": "001",
        }

        result = ext.build_context_extensions(
            state=state, step="test", step_cfg={}, ctx={}
        )

        # Should fall back to the static path defined in OUTPUT_ARTIFACTS
        expected_path = str(workspace_root / "output" / job_id / "OUTPUT_FILE.md")
        assert result.get("OUTPUT_FILE") == expected_path
