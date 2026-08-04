from __future__ import annotations

import errno
import os
from pathlib import Path

from agent_runner_v2 import job_state


def test_make_step_dir_keeps_base_name_when_unused(monkeypatch, tmp_path: Path) -> None:
    jobs_root = tmp_path / ".ukbe-runner" / "jobs"
    monkeypatch.setattr(job_state, "JOBS_ROOT", jobs_root)
    monkeypatch.delenv("AGENT_RUNNER_JOB_DIR", raising=False)

    result = job_state.make_step_dir(
        {"steps": ["review_docs"]},
        {"template_group": "demo", "job_id": "DEMO-20260804-001"},
        "review_docs",
    )

    assert result == jobs_root / "20260804" / "demo" / "DEMO-20260804-001" / "01_review_docs"


def test_make_step_dir_appends_run_suffix_when_folder_exists(monkeypatch, tmp_path: Path) -> None:
    jobs_root = tmp_path / ".ukbe-runner" / "jobs"
    monkeypatch.setattr(job_state, "JOBS_ROOT", jobs_root)
    monkeypatch.delenv("AGENT_RUNNER_JOB_DIR", raising=False)
    base_dir = jobs_root / "20260804" / "demo" / "DEMO-20260804-001" / "01_review_docs"
    base_dir.mkdir(parents=True, exist_ok=True)
    (jobs_root / "20260804" / "demo" / "DEMO-20260804-001" / "01_review_docs_run2").mkdir(parents=True, exist_ok=True)

    result = job_state.make_step_dir(
        {"steps": ["review_docs"]},
        {"template_group": "demo", "job_id": "DEMO-20260804-001"},
        "review_docs",
    )

    assert result == jobs_root / "20260804" / "demo" / "DEMO-20260804-001" / "02_review_docs"


def test_make_step_dir_appends_run_suffix_for_loop_iteration_collisions(monkeypatch, tmp_path: Path) -> None:
    jobs_root = tmp_path / ".ukbe-runner" / "jobs"
    monkeypatch.setattr(job_state, "JOBS_ROOT", jobs_root)
    monkeypatch.delenv("AGENT_RUNNER_JOB_DIR", raising=False)
    iter_dir = jobs_root / "20260804" / "demo" / "DEMO-20260804-001" / "06_refine_docs_iter1"
    iter_dir.mkdir(parents=True, exist_ok=True)

    result = job_state.make_step_dir(
        {"steps": ["refine_docs"]},
        {
            "template_group": "demo",
            "job_id": "DEMO-20260804-001",
            "backend_step_sequence": 6,
            "loop_context": {
                "active": True,
                "loop_step": "review_docs",
                "refine_step": "refine_docs",
                "loop_iteration": 1,
            },
        },
        "refine_docs",
    )

    assert result == jobs_root / "20260804" / "demo" / "DEMO-20260804-001" / "07_refine_docs_iter1"


def test_create_step_dir_skips_existing_locked_directory(monkeypatch, tmp_path: Path) -> None:
    jobs_root = tmp_path / ".ukbe-runner" / "jobs"
    monkeypatch.setattr(job_state, "JOBS_ROOT", jobs_root)
    monkeypatch.delenv("AGENT_RUNNER_JOB_DIR", raising=False)
    monkeypatch.setattr(job_state.time, "sleep", lambda _: None)

    base_dir = jobs_root / "20260804" / "demo" / "DEMO-20260804-001" / "01_review_docs"
    base_dir.mkdir(parents=True, exist_ok=True)

    original_mkdir = Path.mkdir

    def fake_mkdir(self: Path, parents: bool = False, exist_ok: bool = False) -> None:
        if self == base_dir:
            raise PermissionError(errno.EACCES, "Access denied", str(self))
        return original_mkdir(self, parents=parents, exist_ok=exist_ok)

    monkeypatch.setattr(Path, "mkdir", fake_mkdir)

    result = job_state.create_step_dir(
        {"steps": ["review_docs"]},
        {"template_group": "demo", "job_id": "DEMO-20260804-001"},
        "review_docs",
    )

    assert result == jobs_root / "20260804" / "demo" / "DEMO-20260804-001" / "02_review_docs"
    assert result.exists()


def test_next_step_sequence_uses_highest_existing_prefix_not_folder_count(monkeypatch, tmp_path: Path) -> None:
    jobs_root = tmp_path / ".ukbe-runner" / "jobs"
    monkeypatch.setattr(job_state, "JOBS_ROOT", jobs_root)
    monkeypatch.delenv("AGENT_RUNNER_JOB_DIR", raising=False)
    job_root = jobs_root / "20260804" / "demo" / "DEMO-20260804-001"
    for name in ["01_generate_docs", "02_review_docs", "04_validate_docs"]:
        (job_root / name).mkdir(parents=True, exist_ok=True)

    result = job_state.make_step_dir(
        {"steps": ["refine_docs"]},
        {"template_group": "demo", "job_id": "DEMO-20260804-001"},
        "refine_docs",
    )

    assert result == jobs_root / "20260804" / "demo" / "DEMO-20260804-001" / "05_refine_docs"


def test_save_json_retries_permission_error(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(job_state.time, "sleep", lambda _: None)
    path = tmp_path / "job.json"
    original_replace = job_state.os.replace
    attempts = {"count": 0}

    def fake_replace(src: str, dst: str) -> None:
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise PermissionError(errno.EACCES, "Access denied", dst)
        return original_replace(src, dst)

    monkeypatch.setattr(job_state.os, "replace", fake_replace)

    job_state.save_json(path, {"status": "ok"})

    assert attempts["count"] == 3
    assert path.read_text(encoding="utf-8").strip().startswith("{")
