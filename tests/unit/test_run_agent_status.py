from __future__ import annotations

import json

from agent_runner_v2 import manual_runtime_deps, shared_runtime_deps
from agent_runner_v2 import run_agent as run_agent_module


def test_step_progress_label_formats_index_and_total():
    group_cfg = {"steps": ["project_analysis", "generate_sop", "review_sop"]}

    assert run_agent_module._step_progress_label(group_cfg, "generate_sop") == "step 2 of 3"
    assert run_agent_module._step_progress_label(group_cfg, None) == "step ? of ?"


def test_format_job_status_summary_includes_progress_and_counts():
    state = {
        "job_id": "JOB-123",
        "template_group": "delivery_scaffold_v1",
        "job_status": "IN_PROGRESS",
        "current_step": "generate_sop",
        "completed_steps": ["project_analysis"],
        "reject_counts": {"generate_sop": 1},
    }
    group_cfg = {"steps": ["project_analysis", "generate_sop", "review_sop"]}

    summary = run_agent_module._format_job_status_summary(state, group_cfg)

    assert "Progress:      step 2 of 3" in summary
    assert "Completed:     1 of 3" in summary
    assert "  generate_sop: 1" in summary


def test_main_returns_success_for_completed_matching_seed(monkeypatch, tmp_path, capsys):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    group_cfg = {
        "steps": ["project_analysis", "generate_sop"],
        "step_configs": {},
        "job_init_step": "project_analysis",
        "job_init_inputs": [],
        "default_max_rejects": 2,
    }
    completed_state = {
        "job_id": "SCAFFOLD-GEN-001",
        "template_group": "delivery_scaffold_v1",
        "job_status": "COMPLETED",
        "status": "COMPLETED",
        "current_step": None,
        "completed_steps": ["project_analysis", "generate_sop"],
        "reject_counts": {},
        "artifacts": {},
        "seed_artifact_type": "TARGET_PROJECT_ROOT",
        "seed_artifact_path": str(workspace).replace("\\", "/"),
    }

    monkeypatch.setattr(run_agent_module, "load_project_config", lambda root: {})
    monkeypatch.setattr(run_agent_module, "_resolve_workflow_bundle_root", lambda *args, **kwargs: workspace)
    monkeypatch.setattr(run_agent_module, "load_workflow_module", lambda *args, **kwargs: None)
    monkeypatch.setattr(run_agent_module, "_load_group", lambda template_group, **kwargs: group_cfg)
    monkeypatch.setattr(run_agent_module, "_validate_static_reference_files", lambda *args, **kwargs: None)
    monkeypatch.setattr(run_agent_module, "set_context", lambda **kwargs: None)
    monkeypatch.setattr(run_agent_module, "set_workflow_module", lambda module: None)
    monkeypatch.setattr(manual_runtime_deps, "find_matching_active_job", lambda **kwargs: "")
    monkeypatch.setattr(manual_runtime_deps, "find_matching_completed_job", lambda **kwargs: "SCAFFOLD-GEN-001")
    monkeypatch.setattr(
        manual_runtime_deps,
        "infer_seed_identity",
        lambda template_group, seed_artifacts: ("TARGET_PROJECT_ROOT", str(workspace).replace("\\", "/")),
    )
    monkeypatch.setattr(manual_runtime_deps, "load_job", lambda *args, **kwargs: completed_state)
    monkeypatch.setattr(manual_runtime_deps, "ensure_backward_compatible_state", lambda state: state)
    monkeypatch.setattr(manual_runtime_deps, "migrate_job_state", lambda state: state)
    monkeypatch.setattr(manual_runtime_deps, "reconcile_job_state", lambda state, group_cfg: state)
    monkeypatch.setattr(shared_runtime_deps, "load_project_config", lambda root: {})
    monkeypatch.setattr(shared_runtime_deps, "load_workflow_module", lambda *args, **kwargs: None)
    monkeypatch.setattr(shared_runtime_deps, "_load_group", lambda template_group, **kwargs: group_cfg)
    monkeypatch.setattr(shared_runtime_deps, "_validate_static_reference_files", lambda *args, **kwargs: None)

    rc = run_agent_module.main(
        [
            "run",
            "--project-root",
            str(workspace),
            "--template-group",
            "delivery_scaffold_v1",
            "--target-project-root",
            str(workspace),
        ]
    )

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "APPROVED"
    assert payload["job_status"] == "COMPLETED"
    assert payload["progress"] == "step ? of ?"
    assert "already completed" in payload["remark"]
