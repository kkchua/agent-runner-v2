"""Unit tests for operator console runner_service (CLI-only architecture)."""
from __future__ import annotations

from agent_runner_v2.operator_console.models import GlobalSettings, WorkflowEntry
from agent_runner_v2.operator_console.services.runner_service import RunnerActionService


def test_runner_action_service_submit_passes_settings(monkeypatch, tmp_path) -> None:
    """submit_job builds correct CLI argv from global settings."""
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
    # CLI reads backend_url from config.json — no --backend-url in argv
    assert captured["argv"] == [
        "--workflow-name",
        "sdlc_10_requirement_v1",
        "--worker-id",
        "worker-1",
        "--worker-label",
        "live",
        "--input",
        "INIT_FILE=D:/repo/docs/repo/agent_runner/sdlc/delivery/00_initiatives/INIT-001.md",
    ]


def test_runner_action_service_approve_step_invokes_run_agent(monkeypatch, tmp_path) -> None:
    """approve_step builds correct CLI argv."""
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
    """override_step builds correct CLI argv."""
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


def test_runner_service_list_active_runs_parses_json(monkeypatch) -> None:
    """list_active_runs_for_worker parses CLI JSON output into ActiveRunSummary."""
    import json

    def fake_list_runs_main(argv):
        print(json.dumps({
            "runs": [
                {
                    "id": "run-uuid-1",
                    "run_code": "JOB-001",
                    "workflow_name": "agnes_media_gen_v1",
                    "run_status": "pending",
                    "current_step": "generate_prompts",
                    "updated_at": "2026-07-27T10:00:00",
                    "worker_id": "worker-01",
                    "project_root": "/tmp/repo",
                }
            ]
        }))
        return 0

    monkeypatch.setattr(
        "agent_runner_v2.operator_console.services.runner_service.list_runs_commands.main",
        fake_list_runs_main,
    )

    service = RunnerActionService(
        GlobalSettings(
            backend_url="http://127.0.0.1:8100",
            worker_id="worker-1",
            worker_label="live",
        )
    )
    runs = service.list_active_runs_for_worker(worker_id="worker-01")

    assert len(runs) == 1
    assert runs[0].run_id == "run-uuid-1"
    assert runs[0].run_code == "JOB-001"
    assert runs[0].workflow_name == "agnes_media_gen_v1"
    assert runs[0].status == "pending"
    assert runs[0].current_step == "generate_prompts"


def test_runner_service_stop_run(monkeypatch) -> None:
    """stop_run builds correct CLI argv."""
    captured: dict[str, object] = {}

    def fake_stop_main(argv):
        captured["argv"] = list(argv or [])
        print('{"status": "ok"}')
        return 0

    monkeypatch.setattr(
        "agent_runner_v2.operator_console.services.runner_service.stop_commands.main",
        fake_stop_main,
    )

    service = RunnerActionService(
        GlobalSettings(
            backend_url="http://127.0.0.1:8100",
            worker_id="worker-1",
            worker_label="live",
        )
    )
    result = service.stop_run(run_id="run-uuid-1", reason="Cancelled by operator")

    assert '"status": "ok"' in result
    assert captured["argv"] == ["run-uuid-1", "--reason", "Cancelled by operator"]


def test_runner_service_approve(monkeypatch) -> None:
    """approve builds correct CLI argv with --resume flag."""
    captured: dict[str, object] = {}

    def fake_approve_main(argv):
        captured["argv"] = list(argv or [])
        print('{"status": "ok"}')
        return 0

    monkeypatch.setattr(
        "agent_runner_v2.operator_console.services.runner_service.approve_commands.main",
        fake_approve_main,
    )

    service = RunnerActionService(
        GlobalSettings(
            backend_url="http://127.0.0.1:8100",
            worker_id="worker-1",
            worker_label="live",
        )
    )
    result = service.approve(run_id="run-uuid-1", resume=True)

    assert '"status": "ok"' in result
    assert captured["argv"] == ["run-uuid-1", "--resume"]
