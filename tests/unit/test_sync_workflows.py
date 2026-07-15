from __future__ import annotations

from agent_runner_v2 import sync_workflows
from agent_runner_v2.workflow_bundle_validator import ValidationFinding


class _Validation:
    def __init__(self, valid: bool, findings: tuple[ValidationFinding, ...] = ()) -> None:
        self.valid = valid
        self.findings = findings


def test_print_sync_summary_reports_split_counts(capsys) -> None:
    sync_workflows._print_sync_summary(
        synced=["ok_workflow"],
        validation_failed=["bad_local"],
        transport_failed=["bad_backend"],
    )

    captured = capsys.readouterr()
    assert "synced: 1" in captured.err
    assert "local_validation_failed: 1" in captured.err
    assert "backend_transport_failed: 1" in captured.err
    assert "validation_failed_workflows: bad_local" in captured.err
    assert "backend_failed_workflows: bad_backend" in captured.err


def test_print_validation_failure_renders_findings(capsys) -> None:
    validation = _Validation(
        valid=False,
        findings=(
            ValidationFinding(
                level="error",
                code="missing_prompt_file",
                message="Prompt file missing",
                path="X:/bundle/prompts/a.txt",
                step="step_a",
            ),
        ),
    )

    sync_workflows._print_validation_failure("demo_workflow", validation)

    captured = capsys.readouterr()
    assert "[demo_workflow] local validation failed:" in captured.err
    assert "[missing_prompt_file]" in captured.err
    assert "step=step_a" in captured.err
