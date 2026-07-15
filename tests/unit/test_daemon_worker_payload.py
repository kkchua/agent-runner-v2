"""Test that daemon worker request payload validates against WorkerRequest schema."""
import pytest

from agent_runner_v2.execution_request import WorkerRequest


class TestDaemonWorkerPayloadValidation:
    """Verify _build_worker_request_payload produces valid WorkerRequest payloads."""

    def _sample_run(self) -> dict:
        return {
            "id": 123,
            "run_code": "TEST-001",
            "workflow_name": "default",
            "project_root": "/tmp/test-project",
            "workspace_path": "/tmp/test-project",
            "input_payload": {},
            "context_payload": {},
            "env_overrides": {},
        }

    def _sample_step_run(self) -> dict:
        return {
            "id": 456,
            "step_name": "project_analysis",
            "sequence_no": 1,
            "coder": None,
        }

    def _sample_spec(self) -> dict:
        return {
            "template_group": "delivery_scaffold_v1",
            "step_sequence_no": 1,
            "required_inputs": [],
            "optional_inputs": [],
            "produces": ["ARTIFACT_KEY_SOP"],
            "raw_config": {"action": "generate_sop"},
            "prompt_file": "delivery_scaffold_v1/prompts/01_generate_sop.txt",
            "action_name": "generate_sop",
        }

    def test_payload_has_all_required_worker_request_fields(self):
        """Payload from _build_worker_request_payload should have all required fields."""
        from agent_runner_v2.daemon_runtime import build_worker_request_payload
        import agent_runner_v2.shared_runtime_deps as hooks

        run = self._sample_run()
        step_run = self._sample_step_run()
        spec = self._sample_spec()

        payload = build_worker_request_payload(
            run=run,
            step_run=step_run,
            step_execution_spec=spec,
            backend_url="http://localhost:8100",
            step_spec_source="backend",
            hooks=hooks,
        )

        # Verify all WorkerRequest required fields are present
        required_fields = [
            "workflow_name",
            "template_group",
            "job_id",
            "step_name",
            "step_sequence_no",
            "workflow_run_id",
            "workflow_step_run_id",
            "project_root",
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
            "step_spec_source",
        ]

        for field in required_fields:
            assert field in payload, f"Missing required field: {field}"

        # Verify critical fields have correct types/values
        assert isinstance(payload["step_sequence_no"], int)
        assert payload["step_sequence_no"] == 1
        assert payload["backend_url"] == "http://localhost:8100"
        assert payload["job_id"] == "TEST-001"
        assert payload["step_name"] == "project_analysis"

    def test_payload_validates_against_worker_request_schema(self):
        """Payload should successfully parse via WorkerRequest.from_dict()."""
        from agent_runner_v2.daemon_runtime import build_worker_request_payload
        import agent_runner_v2.shared_runtime_deps as hooks

        run = self._sample_run()
        step_run = self._sample_step_run()
        spec = self._sample_spec()

        payload = build_worker_request_payload(
            run=run,
            step_run=step_run,
            step_execution_spec=spec,
            backend_url="http://localhost:8100",
            step_spec_source="backend",
            hooks=hooks,
        )

        # This should not raise ValueError
        request = WorkerRequest.from_dict(payload)

        # Verify parsed correctly
        assert request.workflow_name == "default"
        assert request.template_group == "delivery_scaffold_v1"
        assert request.job_id == "TEST-001"
        assert request.step_name == "project_analysis"
        assert request.step_sequence_no == 1
        assert request.backend_url == "http://localhost:8100"
        assert request.resolved_coder.get("provider_key") is None

    def test_step_sequence_no_computed_correctly_for_backend_mode(self):
        """Backend mode should preserve backend execution sequence for step dirs."""
        from agent_runner_v2.daemon_runtime import build_worker_request_payload
        import agent_runner_v2.shared_runtime_deps as hooks

        run = self._sample_run()
        step_run = self._sample_step_run()
        spec = self._sample_spec()

        # Test with spec providing step_sequence_no
        payload = build_worker_request_payload(
            run=run,
            step_run=step_run,
            step_execution_spec=spec,
            backend_url="http://localhost:8100",
            step_spec_source="backend",
            hooks=hooks,
        )
        assert payload["step_sequence_no"] == 1

        # Test with step_run providing sequence_no (spec doesn't have it)
        spec_no_seq = dict(spec)
        del spec_no_seq["step_sequence_no"]
        payload2 = build_worker_request_payload(
            run=run,
            step_run=step_run,
            step_execution_spec=spec_no_seq,
            backend_url="http://localhost:8100",
            step_spec_source="backend",
            hooks=hooks,
        )
        assert payload2["step_sequence_no"] == 1  # From step_run.sequence_no

    def test_backend_mode_preserves_backend_sequence_when_workflow_order_differs(self, monkeypatch):
        from agent_runner_v2.daemon_runtime import build_worker_request_payload
        import agent_runner_v2.shared_runtime_deps as hooks

        monkeypatch.setattr(
            hooks,
            "get_template_group_cfg",
            lambda **kwargs: {
                "steps": [
                    "generate_core_governance_docs",
                    "review_core_governance_docs",
                    "validate_core_governance_docs",
                    "audit_core_governance_accuracy",
                    "unused_hidden_slot",
                    "stepCompletion",
                ]
            },
        )

        run = {
            **self._sample_run(),
            "workflow_name": "00_core_governance_bootstrap_v1",
            "run_code": "00CORE-001",
        }
        step_run = {
            "id": 456,
            "step_name": "stepCompletion",
            "sequence_no": 5,
            "coder": None,
        }
        spec = {
            "template_group": "00_core_governance_bootstrap_v1",
            "step_order": 6,
            "step_sequence_no": 5,
            "required_inputs": [],
            "optional_inputs": [],
            "produces": [],
            "raw_config": {"action": "step_completion"},
            "action_name": "step_completion",
        }

        payload = build_worker_request_payload(
            run=run,
            step_run=step_run,
            step_execution_spec=spec,
            backend_url="http://localhost:8100",
            step_spec_source="backend",
            hooks=hooks,
        )

        assert payload["step_sequence_no"] == 5
        assert str(payload["state_overrides"]["backend_step_dir_rel"]).replace("\\", "/").endswith(
            "00_core_governance_bootstrap_v1/00CORE-001/05_stepCompletion"
        )

    def test_backend_url_present_at_top_level_and_in_env_overrides(self):
        """backend_url should be at top level (for WorkerRequest) AND in env_overrides (for subprocess)."""
        from agent_runner_v2.daemon_runtime import build_worker_request_payload
        import agent_runner_v2.shared_runtime_deps as hooks

        run = self._sample_run()
        step_run = self._sample_step_run()
        spec = self._sample_spec()

        payload = build_worker_request_payload(
            run=run,
            step_run=step_run,
            step_execution_spec=spec,
            backend_url="http://test-backend:9000",
            step_spec_source="backend",
            hooks=hooks,
        )

        # Top-level field for WorkerRequest validation
        assert payload["backend_url"] == "http://test-backend:9000"

        # Also in env_overrides for subprocess environment
        assert payload["env_overrides"]["BACKEND_URL"] == "http://test-backend:9000"
