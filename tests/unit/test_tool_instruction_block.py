"""Tests for TOOL_INSTRUCTION block in coder-facing prompt templates. Related: IMPL-20260609-01."""

from __future__ import annotations

from pathlib import Path

from agent_runner_v2.bundle_loader import BOOTSTRAP_ROOT
from agent_runner_v2.step_runner import render_prompt

_PROMPTS_ROOT = BOOTSTRAP_ROOT / "prompts"

_TEST_CONTEXT = {
    "STEP_NAME": "test_step_name",
    "PROGRESS_FILE": "/workspace/project/.ukbe-runner/jobs/31_task_execution_v1/JOB-001/01_test_step_name/progress.jsonl",
    "TOOLS_DIR": "/workspace/project/agent_runner_v2/agent_runner_v2/tools",
}

_EMPTY_PATH_CONTEXT = {
    "STEP_NAME": "test_step_name",
    "PROGRESS_FILE": "progress.jsonl",
    "TOOLS_DIR": "",
}


def _read_template(group: str, filename: str) -> str:
    """Read a prompt template from disk."""
    return (_PROMPTS_ROOT / group / filename).read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Render tests
# ---------------------------------------------------------------------------


def test_render_contains_workflow_rules_block():
    """Render a coder-facing prompt template and assert Workflow Rules block is present."""
    template = _read_template("31_task_execution_v1", "10_executor.txt")
    rendered = render_prompt(template, _TEST_CONTEXT)
    assert "## Workflow Rules" in rendered


def test_render_documents_create_todos():
    """Assert the rendered block contains create_todos usage."""
    template = _read_template("31_task_execution_v1", "10_executor.txt")
    rendered = render_prompt(template, _TEST_CONTEXT)
    assert "create_todos" in rendered
    assert _TEST_CONTEXT["STEP_NAME"] in rendered
    assert repr(_TEST_CONTEXT["TOOLS_DIR"]) in rendered


def test_render_documents_mark_complete():
    """Assert the rendered block contains mark_complete usage."""
    template = _read_template("31_task_execution_v1", "10_executor.txt")
    rendered = render_prompt(template, _TEST_CONTEXT)
    assert "mark_complete" in rendered
    assert "1-based index" in rendered


def test_render_documents_mark_process():
    """Assert the rendered block contains mark_process usage."""
    template = _read_template("31_task_execution_v1", "10_executor.txt")
    rendered = render_prompt(template, _TEST_CONTEXT)
    assert "mark_process" in rendered
    assert "processing" in rendered


# ---------------------------------------------------------------------------
# Leakage tests
# ---------------------------------------------------------------------------


def test_render_progress_file_in_workflow_rules():
    """Assert the rendered prompt contains the PROGRESS_FILE path in the Workflow Rules block."""
    template = _read_template("31_task_execution_v1", "10_executor.txt")
    rendered = render_prompt(template, _TEST_CONTEXT)
    assert repr(_TEST_CONTEXT["PROGRESS_FILE"]) in rendered


def test_render_uses_python_command_placeholder():
    """Assert the rendered block includes a quoted Python command prefix."""
    template = _read_template("31_task_execution_v1", "10_executor.txt")
    rendered = render_prompt(template, _TEST_CONTEXT)
    assert '"{PYTHON_CMD}"' not in rendered
    assert " -c \"import sys;" in rendered


def test_render_no_database_leakage():
    """Assert the rendered prompt does NOT contain any database table name."""
    template = _read_template("31_task_execution_v1", "10_executor.txt")
    rendered = render_prompt(template, _TEST_CONTEXT)
    # Database table names that should never appear in coder prompts
    # (excludes generic terms that legitimately appear in prompt text)
    forbidden_tables = [
        "workflow_runs",
        "step_runs",
        "workflow_definitions",
    ]
    for table in forbidden_tables:
        assert table not in rendered.lower(), f"Database table '{table}' leaked into prompt"


def test_render_no_backend_url_leakage():
    """Assert the rendered prompt does NOT contain any backend URL."""
    template = _read_template("31_task_execution_v1", "10_executor.txt")
    rendered = render_prompt(template, _TEST_CONTEXT)
    # Common backend URL patterns that should never appear in coder prompts
    forbidden_patterns = [
        "http://localhost",
        "http://127.0.0.1",
        "https://",
        "api/",
        "/api",
        ":8100",
    ]
    for pattern in forbidden_patterns:
        assert pattern not in rendered, f"Backend URL pattern '{pattern}' leaked into prompt"


# ---------------------------------------------------------------------------
# Fallback tests
# ---------------------------------------------------------------------------


def test_render_empty_tools_dir():
    """Render with TOOLS_DIR='' â€” block must be absent (no-op)."""
    template = _read_template("31_task_execution_v1", "10_executor.txt")
    rendered = render_prompt(template, _EMPTY_PATH_CONTEXT)
    assert "## Workflow Rules" not in rendered


def test_render_step_name_substituted():
    """Render with a test STEP_NAME value and assert the value appears in the rendered block."""
    template = _read_template("31_task_execution_v1", "10_executor.txt")
    rendered = render_prompt(template, _TEST_CONTEXT)
    assert _TEST_CONTEXT["STEP_NAME"] in rendered


def test_render_tolerates_none_context_values():
    """Render should coerce None values instead of raising during placeholder replacement."""
    template = "value={NULLISH}"
    rendered = render_prompt(template, {"NULLISH": None, "TOOLS_DIR": "", "STEP_NAME": "x", "PROGRESS_FILE": "p"})
    assert rendered == "value="


# ---------------------------------------------------------------------------
# Cross-group tests: verify block exists in other workflow groups
# ---------------------------------------------------------------------------


def test_delivery_planning_has_tool_instruction():
    """Verify TOOL_INSTRUCTION block is present in delivery_planning_v1 templates."""
    template = _read_template("30_delivery_planning_v1", "06_task.txt")
    rendered = render_prompt(template, _TEST_CONTEXT)
    assert "## Workflow Rules" in rendered


def test_delivery_scaffold_has_tool_instruction():
    """Verify TOOL_INSTRUCTION block is present in delivery_scaffold_v1 templates."""
    template = _read_template("10_execution_scaffold_v1", "01_project_analysis.txt")
    rendered = render_prompt(template, _TEST_CONTEXT)
    assert "## Workflow Rules" in rendered


def test_initiative_intake_has_tool_instruction():
    """Verify TOOL_INSTRUCTION block is present in initiative_intake_v1 templates."""
    template = _read_template("20_initiative_intake_v1", "01_pre_init.txt")
    rendered = render_prompt(template, _TEST_CONTEXT)
    assert "## Workflow Rules" in rendered


def test_image_csv_gen_v1_has_tool_instruction():
    """Verify TOOL_INSTRUCTION block is present in image_csv_gen_v1 templates."""
    template = _read_template("image_csv_gen_v1", "01_extract_desc.txt")
    rendered = render_prompt(template, _TEST_CONTEXT)
    assert "## Workflow Rules" in rendered


def test_image_csv_gen_v2_has_tool_instruction():
    """Verify TOOL_INSTRUCTION block is present in image_csv_gen_v2 templates."""
    template = _read_template("image_csv_gen_v2", "01_extract_desc.txt")
    rendered = render_prompt(template, _TEST_CONTEXT)
    assert "## Workflow Rules" in rendered


def test_documentation_sync_has_tool_instruction():
    """Verify TOOL_INSTRUCTION block is present in documentation_sync_v1 templates."""
    template = _read_template("40_documentation_sync_v1", "01_sync_docs.txt")
    rendered = render_prompt(template, _TEST_CONTEXT)
    assert "## Workflow Rules" in rendered


def test_initiative_intake_prompt_is_doc_first():
    """Verify initiative intake explicitly forbids code scanning and centers docs."""
    template = _read_template("20_initiative_intake_v1", "01_pre_init.txt")
    assert "do not scan code in this step" in template.lower()
    assert "documentation set as the primary source of truth" in template.lower()


def test_delivery_planning_prompt_is_doc_first():
    """Verify delivery planning explicitly forbids fresh code scans."""
    template = _read_template("30_delivery_planning_v1", "02_planner.txt")
    assert "do not perform a fresh code scan in this step" in template.lower()
    assert "documentation artifacts as the primary evidence base" in template.lower()


def test_task_execution_prompt_is_doc_first():
    """Verify task execution explicitly forbids fresh code scans."""
    template = _read_template("31_task_execution_v1", "08_impl_task.txt")
    assert "do not perform a new code scan in this step" in template.lower()
    assert "documentation set, approved plan, and task graph as the execution truth" in template.lower()


def test_task_execution_qwen_prompt_is_doc_first():
    """Verify the qwen task execution prompt matches the docs-first contract."""
    template = _read_template("31_task_execution_v1", "08_impl_task_qwen.txt")
    assert "do not perform a new code scan in this step" in template.lower()
    assert "documentation set, approved plan, and task graph as the execution truth" in template.lower()


