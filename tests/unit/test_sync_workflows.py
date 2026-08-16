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


class TestConvertToV2Format:
    def test_reconstructs_artifacts_from_flattened_fields(self):
        """Flattened required_inputs/produces are nested under artifacts."""
        group_dict = {
            "job_prefix": "TEST",
            "job_init_step": "generate",
            "default_max_rejects": 2,
            "steps": ["generate", "review"],
            "step_configs": {
                "generate": {
                    "required_inputs": ["DRAFT_INIT_FILE"],
                    "produces": ["INIT_FILE"],
                    "result_meta_key": "INIT_FILE",
                    "coder": {"role_policy": "architect_standard"},
                    "onsuccess": "review",
                    "prompt_file": "/abs/path/prompt.txt",
                },
                "review": {
                    "required_inputs": ["INIT_FILE"],
                    "produces": ["REVIEW_FILE"],
                    "onsuccess": "stepCompletion",
                },
            },
        }

        result = sync_workflows.convert_to_v2_format(group_dict)

        gen = result["steps"]["generate"]
        assert gen["artifacts"]["required_inputs"] == ["DRAFT_INIT_FILE"]
        assert gen["artifacts"]["produces"] == ["INIT_FILE"]
        assert gen["artifacts"]["result_meta_key"] == "INIT_FILE"
        assert gen["coder"] == {"role_policy": "architect_standard"}
        assert gen["onsuccess"] == "review"

    def test_preserves_all_step_fields(self):
        """Non-artifact fields are preserved as-is."""
        group_dict = {
            "job_prefix": "T",
            "job_init_step": "s1",
            "steps": ["s1"],
            "step_configs": {
                "s1": {
                    "onsuccess": "s2",
                    "requires_human_approval_after": True,
                    "on_reject_refine": {"step": "s1", "artifact": "X", "max_iterations": 2},
                    "action": "validate",
                },
                "s2": {},
            },
        }

        result = sync_workflows.convert_to_v2_format(group_dict)

        s1 = result["steps"]["s1"]
        assert s1["onsuccess"] == "s2"
        assert s1["requires_human_approval_after"] is True
        assert s1["on_reject_refine"]["max_iterations"] == 2
        assert s1["action"] == "validate"

    def test_no_artifacts_when_none_present(self):
        """Steps without artifact fields don't get an artifacts key."""
        group_dict = {
            "job_prefix": "T",
            "job_init_step": "s1",
            "steps": ["s1"],
            "step_configs": {
                "s1": {"onsuccess": "s2"},
                "s2": {},
            },
        }

        result = sync_workflows.convert_to_v2_format(group_dict)

        assert "artifacts" not in result["steps"]["s1"]

    def test_optional_and_immutable_inputs(self):
        """Optional and immutable inputs are also reconstructed."""
        group_dict = {
            "job_prefix": "T",
            "job_init_step": "s1",
            "steps": ["s1"],
            "step_configs": {
                "s1": {
                    "required_inputs": ["A"],
                    "optional_inputs": ["B"],
                    "immutable_inputs": ["C"],
                    "produces": ["D"],
                },
            },
        }

        result = sync_workflows.convert_to_v2_format(group_dict)

        arts = result["steps"]["s1"]["artifacts"]
        assert arts["required_inputs"] == ["A"]
        assert arts["optional_inputs"] == ["B"]
        assert arts["immutable_inputs"] == ["C"]
        assert arts["produces"] == ["D"]
