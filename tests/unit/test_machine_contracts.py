"""Unit tests for machine-mode execution contracts.

Tests request parsing, validation, and result emission for daemon→run_agent.py communication.
"""
import json
import tempfile
from pathlib import Path
from typing import Any

import pytest

from agent_runner_v2.execution_request import WorkerRequest
from agent_runner_v2.execution_result import ExecutionFailure, ExecutionResult, MachineResult


class TestWorkerRequestValidation:
    """Test WorkerRequest.from_dict() validation."""

    def _valid_payload(self) -> dict[str, Any]:
        return {
            "workflow_name": "default",
            "template_group": "delivery_scaffold_v1",
            "job_id": "test-job-001",
            "step_name": "project_analysis",
            "step_sequence_no": 1,
            "workflow_run_id": 123,
            "workflow_step_run_id": 456,
            "project_root": "/tmp/test-project",
            "target_project_root": None,
            "input_artifacts": {},
            "context_payload": {},
            "env_overrides": {},
            "coder_override": None,
            "workflow_key_override": "",
            "backend_url": "http://localhost:8100",
            "state_overrides": {},
            "step_execution_spec": {},
            "resolved_coder": {
                "coder_alias": "claude",
                "coder_used": "claude-3-opus",
                "coder_role": "architect",
                "connection": "anthropic",
                "model_id": "claude-3-opus-20240229",
                "source": "role_policy",
            },
            "step_spec_source": "backend",
        }

    def test_valid_request_parses_successfully(self):
        """Valid payload should parse without errors."""
        payload = self._valid_payload()
        request = WorkerRequest.from_dict(payload)

        assert request.workflow_name == "default"
        assert request.template_group == "delivery_scaffold_v1"
        assert request.job_id == "test-job-001"
        assert request.step_name == "project_analysis"
        assert request.step_sequence_no == 1
        assert request.project_root == "/tmp/test-project"

    def test_missing_workflow_name_raises(self):
        """Missing workflow_name should raise ValueError."""
        payload = self._valid_payload()
        del payload["workflow_name"]

        with pytest.raises(ValueError, match="Workflow name is required"):
            WorkerRequest.from_dict(payload)

    def test_empty_workflow_name_raises(self):
        """Empty string workflow_name should raise ValueError."""
        payload = self._valid_payload()
        payload["workflow_name"] = ""

        with pytest.raises(ValueError, match="Workflow name is required"):
            WorkerRequest.from_dict(payload)

    def test_missing_template_group_raises(self):
        """Missing template_group should raise ValueError."""
        payload = self._valid_payload()
        del payload["template_group"]

        with pytest.raises(ValueError, match="Template group is required"):
            WorkerRequest.from_dict(payload)

    def test_missing_job_id_raises(self):
        """Missing job_id should raise ValueError."""
        payload = self._valid_payload()
        del payload["job_id"]

        with pytest.raises(ValueError, match="Job ID is required"):
            WorkerRequest.from_dict(payload)

    def test_missing_step_name_raises(self):
        """Missing step_name should raise ValueError."""
        payload = self._valid_payload()
        del payload["step_name"]

        with pytest.raises(ValueError, match="Step name is required"):
            WorkerRequest.from_dict(payload)

    def test_missing_step_sequence_no_raises(self):
        """Missing step_sequence_no should raise ValueError."""
        payload = self._valid_payload()
        del payload["step_sequence_no"]

        with pytest.raises(ValueError, match="Step sequence number is required"):
            WorkerRequest.from_dict(payload)

    def test_non_integer_step_sequence_no_raises(self):
        """Non-integer step_sequence_no should raise ValueError."""
        payload = self._valid_payload()
        payload["step_sequence_no"] = "not-a-number"

        with pytest.raises(ValueError, match="Step sequence number is required"):
            WorkerRequest.from_dict(payload)

    def test_missing_workflow_run_id_raises(self):
        """Missing workflow_run_id should raise ValueError."""
        payload = self._valid_payload()
        del payload["workflow_run_id"]

        with pytest.raises(ValueError, match="workflow_run_id is required"):
            WorkerRequest.from_dict(payload)

    def test_missing_workflow_step_run_id_raises(self):
        """Missing workflow_step_run_id should raise ValueError."""
        payload = self._valid_payload()
        del payload["workflow_step_run_id"]

        with pytest.raises(ValueError, match="workflow_step_run_id is required"):
            WorkerRequest.from_dict(payload)

    def test_missing_project_root_raises(self):
        """Missing project_root should raise ValueError."""
        payload = self._valid_payload()
        del payload["project_root"]

        with pytest.raises(ValueError, match="Project root is required"):
            WorkerRequest.from_dict(payload)

    def test_invalid_step_spec_source_raises(self):
        """Invalid step_spec_source should raise ValueError."""
        payload = self._valid_payload()
        payload["step_spec_source"] = "invalid"

        with pytest.raises(ValueError, match="step_spec_source must be global, backend, or hybrid"):
            WorkerRequest.from_dict(payload)

    def test_valid_step_spec_source_values(self):
        """All valid step_spec_source values should work."""
        payload = self._valid_payload()

        for value in ["global", "backend", "hybrid"]:
            payload["step_spec_source"] = value
            request = WorkerRequest.from_dict(payload)
            assert request.step_spec_source == value

    def test_optional_fields_default_correctly(self):
        """Optional fields should default to empty dicts/None."""
        payload = self._valid_payload()
        # Remove optional fields
        for key in [
            "target_project_root",
            "input_artifacts",
            "context_payload",
            "env_overrides",
            "coder_override",
            "workflow_key_override",
            "backend_url",
            "state_overrides",
            "step_execution_spec",
            "resolved_coder",
        ]:
            if key in payload:
                del payload[key]

        request = WorkerRequest.from_dict(payload)

        assert request.target_project_root is None
        assert request.input_artifacts == {}
        assert request.context_payload == {}
        assert request.env_overrides == {}
        assert request.coder_override is None
        assert request.workflow_key_override == ""
        assert request.backend_url == ""
        assert request.state_overrides == {}
        assert request.step_execution_spec == {}
        assert request.resolved_coder == {}

    def test_to_dict_roundtrip(self):
        """to_dict() should serialize all fields correctly."""
        payload = self._valid_payload()
        request = WorkerRequest.from_dict(payload)
        serialized = request.to_dict()

        assert serialized["workflow_name"] == request.workflow_name
        assert serialized["template_group"] == request.template_group
        assert serialized["job_id"] == request.job_id
        assert serialized["step_name"] == request.step_name
        assert serialized["step_sequence_no"] == request.step_sequence_no


class TestWorkerRequestFromFile:
    """Test WorkerRequest.from_file() loading."""

    def test_load_from_valid_json_file(self):
        """Should load and validate from JSON file."""
        payload = {
            "workflow_name": "default",
            "template_group": "test_group",
            "job_id": "job-123",
            "step_name": "test_step",
            "step_sequence_no": 1,
            "workflow_run_id": 1,
            "workflow_step_run_id": 2,
            "project_root": "/tmp/test",
            "input_artifacts": {},
            "context_payload": {},
            "env_overrides": {},
            "coder_override": None,
            "workflow_key_override": "",
            "backend_url": "",
            "state_overrides": {},
            "step_execution_spec": {},
            "resolved_coder": {},
            "step_spec_source": "backend",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(payload, f)
            temp_path = f.name

        try:
            request = WorkerRequest.from_file(temp_path)
            assert request.workflow_name == "default"
            assert request.step_name == "test_step"
        finally:
            Path(temp_path).unlink()

    def test_load_from_nonexistent_file_raises(self):
        """Missing file should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Request file not found"):
            WorkerRequest.from_file("/nonexistent/path/request.json")

    def test_load_from_invalid_json_raises(self):
        """Invalid JSON should raise ValueError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json }")
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Invalid JSON"):
                WorkerRequest.from_file(temp_path)
        finally:
            Path(temp_path).unlink()


class TestMachineResultSchema:
    """Test MachineResult dataclass and serialization."""

    def _create_minimal_result(self) -> MachineResult:
        return MachineResult(
            status="completed",
            outcome="success",
            step_name="project_analysis",
            workflow_name="default",
            template_group="delivery_scaffold_v1",
            job_id="test-job-001",
            step_dir="/tmp/jobs/delivery_scaffold_v1/test-job-001/01_project_analysis",
            meta_json_path="/tmp/jobs/.../meta.json",
            job_json_path="/tmp/jobs/delivery_scaffold_v1/test-job-001/job.json",
            progress_jsonl_path=None,
            artifacts={"ARTIFACT_KEY_SOP": "docs/SOP.md"},
            review=None,
            usage={"prompt_tokens": 100, "completion_tokens": 200},
            return_code=0,
            error_class=None,
            error_message=None,
            failure=None,
            diagnostics={},
        )

    def test_minimal_result_serializes_correctly(self):
        """Basic result should serialize to dict with all required fields."""
        result = self._create_minimal_result()
        data = result.to_dict()

        # Check all required fields present
        assert data["status"] == "completed"
        assert data["outcome"] == "success"
        assert data["step_name"] == "project_analysis"
        assert data["workflow_name"] == "default"
        assert data["template_group"] == "delivery_scaffold_v1"
        assert data["job_id"] == "test-job-001"
        assert data["step_dir"] != ""
        assert data["job_json_path"] != ""
        assert data["artifacts"] == {"ARTIFACT_KEY_SOP": "docs/SOP.md"}
        assert data["return_code"] == 0
        assert data["failure"] is None

    def test_failed_result_with_error_info(self):
        """Failed result should include error details."""
        failure = ExecutionFailure(
            failure_class="RUNTIME_ERROR",
            failure_code="ACTION_FAILED",
            failure_reason="Action script exited with code 1",
            failure_source="runner",
        )
        result = MachineResult(
            status="failed",
            outcome="action_failed",
            step_name="generate_templates",
            workflow_name="default",
            template_group="delivery_scaffold_v1",
            job_id="test-job-002",
            step_dir="/tmp/jobs/...",
            meta_json_path=None,
            job_json_path="/tmp/jobs/.../job.json",
            progress_jsonl_path=None,
            artifacts={},
            review=None,
            usage={},
            return_code=1,
            error_class="RUNTIME_ERROR",
            error_message="Action script exited with code 1",
            failure=failure,
            diagnostics={},
        )

        data = result.to_dict()
        assert data["status"] == "failed"
        assert data["error_class"] == "RUNTIME_ERROR"
        assert data["error_message"] == "Action script exited with code 1"
        assert data["failure"]["failure_class"] == "RUNTIME_ERROR"
        assert data["failure"]["failure_code"] == "ACTION_FAILED"

    def test_from_execution_result_conversion(self):
        """MachineResult.from_execution_result() should convert correctly."""
        exec_result = ExecutionResult(
            status="completed",
            outcome="success",
            step_name="test_step",
            coder_used="claude-3-opus",
            remark="Step completed successfully",
            artifacts={"KEY": "path/to/artifact.md"},
            meta_json_path="/tmp/meta.json",
            review=None,
            usage={"tokens": 300},
            failure=None,
            diagnostics={"test": "diag"},
        )

        machine_result = MachineResult.from_execution_result(
            result=exec_result,
            workflow_name="test_workflow",
            template_group="test_group",
            job_id="job-123",
            step_dir="/tmp/step_dir",
            job_json_path="/tmp/job.json",
            return_code=0,
        )

        assert machine_result.status == "completed"
        assert machine_result.workflow_name == "test_workflow"
        assert machine_result.template_group == "test_group"
        assert machine_result.job_id == "job-123"
        assert machine_result.step_dir == "/tmp/step_dir"
        assert machine_result.meta_json_path == "/tmp/meta.json"
        assert machine_result.job_json_path == "/tmp/job.json"
        assert machine_result.artifacts == {"KEY": "path/to/artifact.md"}
        assert machine_result.coder_used == "claude-3-opus"
        assert machine_result.remark == "Step completed successfully"
        assert machine_result.return_code == 0

    def test_progress_path_can_be_set(self):
        """progress_jsonl_path should be settable after construction."""
        result = self._create_minimal_result()
        assert result.progress_jsonl_path is None

        result.progress_jsonl_path = "/tmp/progress.jsonl"
        assert result.progress_jsonl_path == "/tmp/progress.jsonl"

    def test_diagnostics_defaults_to_empty_dict(self):
        """diagnostics field should default to empty dict."""
        result = self._create_minimal_result()
        assert result.diagnostics == {}

        # Verify it serializes correctly
        data = result.to_dict()
        assert "diagnostics" in data
        assert isinstance(data["diagnostics"], dict)


class TestContractRoundTrip:
    """Test request → execution → result round-trip."""

    def test_request_to_result_flow(self):
        """Simulate the full flow: request JSON → parse → execute → result."""
        # Create request
        request_payload = {
            "workflow_name": "default",
            "template_group": "test_workflow",
            "job_id": "round-trip-job",
            "step_name": "test_step",
            "step_sequence_no": 1,
            "workflow_run_id": 999,
            "workflow_step_run_id": 888,
            "project_root": "/tmp/test",
            "input_artifacts": {},
            "context_payload": {},
            "env_overrides": {},
            "coder_override": None,
            "workflow_key_override": "",
            "backend_url": "http://localhost:8100",
            "state_overrides": {},
            "step_execution_spec": {},
            "resolved_coder": {},
            "step_spec_source": "backend",
        }

        # Parse request
        request = WorkerRequest.from_dict(request_payload)
        assert request.job_id == "round-trip-job"

        # Simulate execution result
        exec_result = ExecutionResult(
            status="completed",
            outcome="success",
            step_name=request.step_name,
            coder_used="test-coder",
            artifacts={},
            usage={},
        )

        # Convert to machine result
        machine_result = MachineResult.from_execution_result(
            result=exec_result,
            workflow_name=request.workflow_name,
            template_group=request.template_group,
            job_id=request.job_id,
            step_dir="/tmp/step",
            job_json_path="/tmp/job.json",
            return_code=0,
        )

        # Verify consistency
        assert machine_result.workflow_name == request.workflow_name
        assert machine_result.template_group == request.template_group
        assert machine_result.job_id == request.job_id
        assert machine_result.step_name == request.step_name

        # Serialize result
        result_data = machine_result.to_dict()
        assert result_data["status"] == "completed"
        assert result_data["job_id"] == "round-trip-job"
