from __future__ import annotations

from agent_runner_v2.operator_console.models import GlobalSettings, WorkflowEntry
from agent_runner_v2.operator_console.services.backend_service import BackendRunService
from agent_runner_v2.operator_console.services.runner_service import RunnerActionService


class _FakeBackendClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    def list_runs(self, **kwargs):
        self.calls.append(("list_runs", kwargs))
        return {
            "runs": [
                {
                    "id": "run-1",
                    "run_code": "RUN-1",
                    "workflow_name": "01_governance_foundation_v1",
                    "status": "IN_PROGRESS",
                    "current_step": "review_docs",
                    "updated_at": "2026-07-18T00:00:00Z",
                }
            ]
        }

    def stop_run(self, **kwargs):
        self.calls.append(("stop_run", kwargs))
        return {"status": "ok"}

    def approve_run(self, **kwargs):
        self.calls.append(("approve_run", kwargs))
        return {"status": "ok"}


def test_backend_run_service_lists_active_runs() -> None:
    client = _FakeBackendClient()
    service = BackendRunService(client, worker_id="worker-1")  # type: ignore[arg-type]

    runs = service.list_active_runs(
        repo_path="D:/MyProjectSpace/01_Workflows/agent-runner-v2",
        workflow_name="01_governance_foundation_v1",
    )

    assert len(runs) == 1
    assert runs[0].run_id == "run-1"
    assert runs[0].current_step == "review_docs"
    assert client.calls[0] == (
        "list_runs",
        {
            "repo_path": "D:/MyProjectSpace/01_Workflows/agent-runner-v2",
            "workflow_name": "01_governance_foundation_v1",
            "status_group": "non_terminal",
            "worker_id": "worker-1",
        },
    )


def test_runner_action_service_submit_passes_global_settings(monkeypatch, tmp_path) -> None:
    captured: dict[str, object] = {}
    repo_path = tmp_path / "repo"
    repo_path.mkdir()

    def fake_submit_main(argv):
        captured["argv"] = list(argv or [])
        return 0

    monkeypatch.setattr("agent_runner_v2.operator_console.services.runner_service.submit_commands.main", fake_submit_main)

    service = RunnerActionService(
        GlobalSettings(
            backend_url="http://127.0.0.1:8100",
            worker_id="worker-1",
            worker_label="live",
        )
    )
    result = service.submit_job(
        repo_path=str(repo_path),
        workflow=WorkflowEntry(name="SDLC Requirement", workflow_name="sdlc_10_requirement_v1"),
        input_artifacts={"INIT_FILE": "D:/repo/docs/repo/agent_runner/sdlc/delivery/00_initiatives/INIT-001.md"},
    )

    assert result == "ok"
    assert captured["argv"] == [
        "--workflow-name",
        "sdlc_10_requirement_v1",
        "--backend-url",
        "http://127.0.0.1:8100",
        "--worker-id",
        "worker-1",
        "--worker-label",
        "live",
        "--input",
        "INIT_FILE=D:/repo/docs/repo/agent_runner/sdlc/delivery/00_initiatives/INIT-001.md",
    ]


def test_runner_action_service_approve_step_invokes_run_agent(monkeypatch, tmp_path) -> None:
    captured: dict[str, object] = {}
    repo_path = tmp_path / "repo"
    repo_path.mkdir()

    def fake_run_agent_main(argv):
        captured["argv"] = list(argv or [])
        return 0

    monkeypatch.setattr("agent_runner_v2.operator_console.services.runner_service.run_agent.main", fake_run_agent_main)

    service = RunnerActionService(
        GlobalSettings(
            backend_url="http://127.0.0.1:8100",
            worker_id="worker-1",
            worker_label="live",
        )
    )
    result = service.approve_step(
        repo_path=str(repo_path),
        template_group="01_governance_foundation_v1",
        job_id="00GF-20260719-5246749d",
        step_name="audit_governance_foundation_docs",
    )

    assert result == "ok"
    assert captured["argv"] == [
        "run",
        "--template-group",
        "01_governance_foundation_v1",
        "--job-id",
        "00GF-20260719-5246749d",
        "--approve-step",
        "audit_governance_foundation_docs",
    ]


def test_runner_action_service_override_step_invokes_run_agent(monkeypatch, tmp_path) -> None:
    captured: dict[str, object] = {}
    repo_path = tmp_path / "repo"
    repo_path.mkdir()

    def fake_run_agent_main(argv):
        captured["argv"] = list(argv or [])
        return 0

    monkeypatch.setattr("agent_runner_v2.operator_console.services.runner_service.run_agent.main", fake_run_agent_main)

    service = RunnerActionService(
        GlobalSettings(
            backend_url="http://127.0.0.1:8100",
            worker_id="worker-1",
            worker_label="live",
        )
    )
    result = service.override_step(
        repo_path=str(repo_path),
        template_group="01_governance_foundation_v1",
        job_id="00GF-20260719-5246749d",
        step_name="publish_governance_foundation_set",
    )

    assert result == "ok"
    assert captured["argv"] == [
        "run",
        "--template-group",
        "01_governance_foundation_v1",
        "--job-id",
        "00GF-20260719-5246749d",
        "--override-step",
        "publish_governance_foundation_set",
    ]
