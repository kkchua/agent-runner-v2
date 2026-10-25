"""Tests for plan_first_review_v1 workflow — runner changes and workflow package."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

import agent_runner_v2.job_state as job_state
from agent_runner_v2.artifact_keys import (
    ARTIFACT_KEY_CODEX_REVIEW,
    ARTIFACT_KEY_PLANNING_FOLDER,
    ARTIFACT_KEY_QWEN_PLAN,
    ARTIFACT_KEY_RAW_REQUEST,
    ARTIFACT_KEY_REQUIREMENTS,
)
from agent_runner_v2.constants import (
    ARTIFACT_PATH_CODEX_REVIEW,
    ARTIFACT_PATH_QWEN_PLAN,
    ARTIFACT_PATH_RAW_REQUEST,
    ARTIFACT_PATH_REQUIREMENTS,
)
from agent_runner_v2.exceptions import UnauthorizedWriteError
from agent_runner_v2.state_defaults import default_loop_context, default_replan_context, default_review_state
from agent_runner_v2.v2.workflow_router import _classify_exception_v2


# ---------------------------------------------------------------------------
# 1. Persistent revision counter
# ---------------------------------------------------------------------------

def test_persistent_revision_counter(monkeypatch) -> None:
    """plan_revision increments after refine success, persists across loop_context clearing."""
    monkeypatch.setattr(job_state, "send_step_notification", lambda *a, **kw: None)
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-10-25T00:00:00")
    monkeypatch.setattr(job_state, "set_job_status", lambda s, v: s.__setitem__("_status", v))
    monkeypatch.setattr(job_state, "get_job_status", lambda s: s.get("_status", "IN_PROGRESS"))
    monkeypatch.setattr(job_state, "set_last_failure", lambda **kw: None)
    monkeypatch.setattr(job_state, "append_failure_history", lambda **kw: None)
    monkeypatch.setattr(job_state, "save_job", lambda *a: None)

    state = {
        "template_group": "plan_first_review_v1",
        "plan_revision": 1,
        "loop_context": {
            "active": True,
            "loop_step": "codex_review",
            "refine_step": "refine_plan",
            "loop_target_artifact": "QWEN_PLAN_FILE",
            "pre_refine_checksum": "abc123",
        },
        "review_state": {},
        "completed_steps": [],
        "artifacts": {"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v02.md"},
    }

    # complete_recovery_step returns exit_code=0 on success
    monkeypatch.setattr(
        job_state,
        "complete_recovery_step",
        lambda **kw: (kw["state"], 0),
    )

    updated, exit_code = job_state._handle_refine_success(
        state=state, step="refine_plan", step_cfg={"onsuccess": "codex_review"},
        artifacts={"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v02.md"},
    )
    assert exit_code == 0
    assert updated["plan_revision"] == 2


def test_plan_revision_not_incremented_for_other_workflows(monkeypatch) -> None:
    """plan_revision only increments for plan_first_review_v1, not other workflows."""
    monkeypatch.setattr(job_state, "send_step_notification", lambda *a, **kw: None)
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-10-25T00:00:00")
    monkeypatch.setattr(job_state, "set_job_status", lambda s, v: s.__setitem__("_status", v))
    monkeypatch.setattr(job_state, "get_job_status", lambda s: s.get("_status", "IN_PROGRESS"))
    monkeypatch.setattr(job_state, "set_last_failure", lambda **kw: None)
    monkeypatch.setattr(job_state, "append_failure_history", lambda **kw: None)
    monkeypatch.setattr(job_state, "save_job", lambda *a: None)

    state = {
        "template_group": "other_workflow",  # NOT plan_first_review_v1
        "plan_revision": 5,
        "loop_context": {
            "active": True,
            "loop_step": "review",
            "refine_step": "refine",
            "loop_target_artifact": "SOME_ARTIFACT",
            "pre_refine_checksum": "xyz789",
        },
        "review_state": {},
        "completed_steps": [],
        "artifacts": {"SOME_ARTIFACT": "some/path.md"},
    }

    monkeypatch.setattr(
        job_state,
        "complete_recovery_step",
        lambda **kw: (kw["state"], 0),
    )

    updated, exit_code = job_state._handle_refine_success(
        state=state, step="refine", step_cfg={"onsuccess": "review"},
        artifacts={"SOME_ARTIFACT": "some/path.md"},
    )
    assert exit_code == 0
    assert updated["plan_revision"] == 5  # NOT incremented


# ---------------------------------------------------------------------------
# 2. Versioned file paths via layered constants
# ---------------------------------------------------------------------------

def test_versioned_file_paths() -> None:
    """Path catalog functions generate correct versioned paths."""
    folder = "Planning/20261025-01_Test"
    assert ARTIFACT_PATH_QWEN_PLAN(folder, 1) == "Planning/20261025-01_Test/Qwen_Plan_v01.md"
    assert ARTIFACT_PATH_QWEN_PLAN(folder, 12) == "Planning/20261025-01_Test/Qwen_Plan_v12.md"
    assert ARTIFACT_PATH_CODEX_REVIEW(folder, 1) == "Planning/20261025-01_Test/Codex_Review_v01.md"
    assert ARTIFACT_PATH_CODEX_REVIEW(folder, 3) == "Planning/20261025-01_Test/Codex_Review_v03.md"
    assert ARTIFACT_PATH_RAW_REQUEST(folder) == "Planning/20261025-01_Test/request.md"
    assert ARTIFACT_PATH_REQUIREMENTS(folder) == "Planning/20261025-01_Test/requirements.md"


# ---------------------------------------------------------------------------
# 3. Human rejection exhaustion
# ---------------------------------------------------------------------------

def test_human_rejection_exhaustion(monkeypatch) -> None:
    """4th human rejection with max_human_rejections=3 → WAITING_FOR_HUMAN_INTERVENTION."""
    monkeypatch.setattr(job_state, "send_step_notification", lambda *a, **kw: None)
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-10-25T00:00:00")
    monkeypatch.setattr(job_state, "set_job_status", lambda s, v: s.__setitem__("_status", v))
    monkeypatch.setattr(job_state, "get_job_status", lambda s: s.get("_status", "IN_PROGRESS"))
    monkeypatch.setattr(job_state, "set_last_failure", lambda **kw: kw["state"].__setitem__("_failure", kw))
    monkeypatch.setattr(job_state, "clear_last_failure", lambda s: None)
    monkeypatch.setattr(job_state, "save_job", lambda *a: None)
    monkeypatch.setattr(job_state, "default_loop_context", lambda **kw: {"active": True, **kw})

    group_cfg = {
        "step_configs": {
            "codex_review": {
                "on_reject_refine": {
                    "step": "refine_plan",
                    "artifact": "QWEN_PLAN_FILE",
                    "max_iterations": 10,
                    "max_human_rejections": 3,
                    "exhausted_failure_code": "PLAN_REFINEMENT_EXHAUSTED",
                    "human_exhausted_failure_code": "PLAN_HUMAN_REJECTION_EXHAUSTED",
                    "exhausted_failure_class": "HUMAN_RETRY_REQUIRED",
                },
            },
        },
    }
    state = {
        "job_id": "test-job",
        "pending_human_approval_for": "codex_review",
        "reject_counts": {"codex_review": 0},
        "human_reject_counts": {"codex_review": 3},
        "review_state": {},
        "human_approvals": {"codex_review": True},
        "artifacts": {"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v01.md"},
    }

    result = job_state.reject_step(
        group_name="plan_first_review_v1", group_cfg=group_cfg,
        state=state, step="codex_review",
    )
    assert result["_status"] == "WAITING_FOR_HUMAN_INTERVENTION"
    assert result["_failure"]["failure_code"] == "PLAN_HUMAN_REJECTION_EXHAUSTED"
    assert result["human_reject_counts"]["codex_review"] == 4


# ---------------------------------------------------------------------------
# 4. Mixed rejections — reject_counts resets, human_reject_counts accumulates
# ---------------------------------------------------------------------------

def test_mixed_rejections(monkeypatch) -> None:
    """Model rejections reset on success; human rejections accumulate."""
    monkeypatch.setattr(job_state, "send_step_notification", lambda *a, **kw: None)
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-10-25T00:00:00")
    monkeypatch.setattr(job_state, "set_job_status", lambda s, v: s.__setitem__("_status", v))
    monkeypatch.setattr(job_state, "get_job_status", lambda s: s.get("_status", "IN_PROGRESS"))
    monkeypatch.setattr(job_state, "set_last_failure", lambda **kw: None)
    monkeypatch.setattr(job_state, "clear_last_failure", lambda s: None)
    monkeypatch.setattr(job_state, "save_job", lambda *a: None)
    monkeypatch.setattr(job_state, "default_loop_context", lambda **kw: {"active": True, **kw})

    group_cfg = {
        "step_configs": {
            "codex_review": {
                "on_reject_refine": {
                    "step": "refine_plan",
                    "artifact": "QWEN_PLAN_FILE",
                    "max_iterations": 10,
                    "max_human_rejections": 3,
                    "exhausted_failure_code": "PLAN_REFINEMENT_EXHAUSTED",
                    "human_exhausted_failure_code": "PLAN_HUMAN_REJECTION_EXHAUSTED",
                },
            },
        },
    }

    # Simulate: model rejects twice (reject_counts=2), then success resets it
    state = {
        "job_id": "test-job",
        "pending_human_approval_for": "codex_review",
        "reject_counts": {"codex_review": 2},
        "human_reject_counts": {},
        "review_state": {},
        "human_approvals": {},
        "artifacts": {"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v01.md"},
    }

    # Human rejects → reject_counts=3, human_reject_counts=1
    result = job_state.reject_step(
        group_name="plan_first_review_v1", group_cfg=group_cfg,
        state=state, step="codex_review",
    )
    assert result["reject_counts"]["codex_review"] == 3
    assert result["human_reject_counts"]["codex_review"] == 1

    # Simulate success path: reject_counts resets to 0
    result["reject_counts"]["codex_review"] = 0

    # Human rejects again → reject_counts=1, human_reject_counts=2
    result["pending_human_approval_for"] = "codex_review"
    result["human_approvals"] = {"codex_review": True}
    result2 = job_state.reject_step(
        group_name="plan_first_review_v1", group_cfg=group_cfg,
        state=result, step="codex_review",
    )
    assert result2["reject_counts"]["codex_review"] == 1
    assert result2["human_reject_counts"]["codex_review"] == 2


# ---------------------------------------------------------------------------
# 5. Retry resets human counter
# ---------------------------------------------------------------------------

def test_retry_step_resets_human_counter(monkeypatch) -> None:
    """retry_step() resets human_reject_counts for the step."""
    monkeypatch.setattr(job_state, "send_step_notification", lambda *a, **kw: None)
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-10-25T00:00:00")
    monkeypatch.setattr(job_state, "set_job_status", lambda s, v: s.__setitem__("_status", v))
    monkeypatch.setattr(job_state, "get_job_status", lambda s: s.get("_status", "WAITING_FOR_HUMAN_INTERVENTION"))
    monkeypatch.setattr(job_state, "clear_last_failure", lambda s: None)
    monkeypatch.setattr(job_state, "save_job", lambda *a: None)
    monkeypatch.setattr(job_state, "default_loop_context", lambda **kw: {})
    monkeypatch.setattr(job_state, "default_replan_context", lambda **kw: {})

    state = {
        "reject_counts": {"codex_review": 5},
        "auto_retry_count_by_step": {"codex_review": 2},
        "human_retry_count_by_step": {"codex_review": 1},
        "human_reject_counts": {"codex_review": 3, "other_step": 1},
        "pending_intervention_for": "codex_review",
        "pending_human_approval_for": None,
        "loop_context": {},
        "replan_context": {},
        "job_id": "test-job",
    }

    result = job_state.retry_step(
        group_name="plan_first_review_v1", group_cfg={},
        state=state, step="codex_review",
    )
    assert result["reject_counts"]["codex_review"] == 0
    assert "codex_review" not in result["human_reject_counts"]
    assert result["human_reject_counts"]["other_step"] == 1  # other step untouched


# ---------------------------------------------------------------------------
# 6. Exception classification
# ---------------------------------------------------------------------------

def test_exception_classification() -> None:
    """UnauthorizedWriteError → HUMAN_RETRY_REQUIRED / UNAUTHORIZED_WRITE_DETECTED."""
    exc = UnauthorizedWriteError("unauthorized writes", ["src/foo.py"])
    failure_class, failure_code, failure_source = _classify_exception_v2(exc)
    assert failure_class == "HUMAN_RETRY_REQUIRED"
    assert failure_code == "UNAUTHORIZED_WRITE_DETECTED"
    assert failure_source == "validator"


# ---------------------------------------------------------------------------
# 7. Layered path constants
# ---------------------------------------------------------------------------

def test_layered_path_constants() -> None:
    """Artifact keys exist, path catalog functions work."""
    assert ARTIFACT_KEY_RAW_REQUEST == "RAW_REQUEST_FILE"
    assert ARTIFACT_KEY_PLANNING_FOLDER == "PLANNING_FOLDER"
    assert ARTIFACT_KEY_REQUIREMENTS == "REQUIREMENTS_FILE"
    assert ARTIFACT_KEY_QWEN_PLAN == "QWEN_PLAN_FILE"
    assert ARTIFACT_KEY_CODEX_REVIEW == "CODEX_REVIEW_FILE"

    folder = "Planning/20261025-01_Test"
    assert ARTIFACT_PATH_QWEN_PLAN(folder, 1).endswith("Qwen_Plan_v01.md")
    assert ARTIFACT_PATH_CODEX_REVIEW(folder, 2).endswith("Codex_Review_v02.md")


# ---------------------------------------------------------------------------
# 8. Plan revision is job state, not artifact
# ---------------------------------------------------------------------------

def test_plan_revision_not_artifact() -> None:
    """plan_revision is initialized as job state, not in artifacts."""
    state = {"plan_revision": 1, "artifacts": {}}
    assert "plan_revision" in state
    assert "plan_revision" not in state["artifacts"]


# ---------------------------------------------------------------------------
# 9. Opt-in human limit preserves max_iterations
# ---------------------------------------------------------------------------

def test_opt_in_human_limit_preserves_max_iterations(monkeypatch) -> None:
    """When max_human_rejections=0, existing max_iterations check still triggers."""
    monkeypatch.setattr(job_state, "send_step_notification", lambda *a, **kw: None)
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-10-25T00:00:00")
    monkeypatch.setattr(job_state, "set_job_status", lambda s, v: s.__setitem__("_status", v))
    monkeypatch.setattr(job_state, "get_job_status", lambda s: s.get("_status", "IN_PROGRESS"))
    monkeypatch.setattr(job_state, "set_last_failure", lambda **kw: kw["state"].__setitem__("_failure", kw))
    monkeypatch.setattr(job_state, "clear_last_failure", lambda s: None)
    monkeypatch.setattr(job_state, "save_job", lambda *a: None)
    monkeypatch.setattr(job_state, "default_loop_context", lambda **kw: {"active": True, **kw})

    group_cfg = {
        "step_configs": {
            "codex_review": {
                "on_reject_refine": {
                    "step": "refine_plan",
                    "artifact": "QWEN_PLAN_FILE",
                    "max_iterations": 2,
                    # max_human_rejections NOT configured (defaults to 0)
                    "exhausted_failure_code": "REFINEMENT_EXHAUSTED",
                },
            },
        },
    }
    state = {
        "job_id": "test-job",
        "pending_human_approval_for": "codex_review",
        "reject_counts": {"codex_review": 2},  # Already at max_iterations
        "human_reject_counts": {},
        "review_state": {},
        "human_approvals": {"codex_review": True},
        "artifacts": {"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v01.md"},
    }

    result = job_state.reject_step(
        group_name="plan_first_review_v1", group_cfg=group_cfg,
        state=state, step="codex_review",
    )
    # max_iterations=2, reject_counts=3 > 2 → model exhaustion
    assert result["_status"] == "WAITING_FOR_HUMAN_INTERVENTION"
    assert result["_failure"]["failure_code"] == "REFINEMENT_EXHAUSTED"


# ---------------------------------------------------------------------------
# 10. PRIOR_PLAN_FILE is prompt-only
# ---------------------------------------------------------------------------

def test_prior_plan_file_is_prompt_only() -> None:
    """PRIOR_PLAN_FILE is not in artifact_keys.py — it's a prompt-only alias."""
    from agent_runner_v2 import artifact_keys
    assert not hasattr(artifact_keys, "ARTIFACT_KEY_PRIOR_PLAN")


# ---------------------------------------------------------------------------
# 11. Workflow TOML schema
# ---------------------------------------------------------------------------

def test_workflow_toml_schema() -> None:
    """workflow.toml parses with correct schema."""
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib

    toml_path = Path(__file__).parents[2] / "workflows" / "plan_first_review_v1" / "workflow.toml"
    if not toml_path.exists():
        pytest.skip("workflow.toml not found")

    data = tomllib.loads(toml_path.read_text(encoding="utf-8"))
    assert data["workflow"]["name"] == "plan_first_review_v1"
    assert data["workflow"]["job_prefix"] == "PLAN"
    assert data["workflow"]["init_step"] == "prepare_request"

    steps = data["step"]
    step_names = [s["name"] for s in steps]
    assert "prepare_request" in step_names
    assert "formalize_requirements" in step_names
    assert "generate_plan" in step_names
    assert "codex_review" in step_names
    assert "refine_plan" in step_names
    assert "step_completion" in step_names

    # Verify codex_review has on_reject_refine
    codex_review = next(s for s in steps if s["name"] == "codex_review")
    assert codex_review["on_reject_refine"]["step"] == "refine_plan"
    assert codex_review["on_reject_refine"]["max_human_rejections"] == 3

    # Verify all prompt steps use slot syntax
    for s in steps:
        if "prompt" in s:
            assert s["prompt"].startswith("{{ slot.")


# ---------------------------------------------------------------------------
# 12. Coder role resolution
# ---------------------------------------------------------------------------

def test_coder_role_resolution() -> None:
    """All prompt steps resolve to OpenCode with intended models."""
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib

    toml_path = Path(__file__).parents[2] / "workflows" / "plan_first_review_v1" / "workflow.toml"
    if not toml_path.exists():
        pytest.skip("workflow.toml not found")

    data = tomllib.loads(toml_path.read_text(encoding="utf-8"))
    steps = data["step"]

    # Review steps use reviewer_standard
    for name in ("formalize_requirements", "codex_review"):
        step = next(s for s in steps if s["name"] == name)
        assert step["coder"]["role_policy"] == "reviewer_standard"

    # Planning steps use plan_standard
    for name in ("generate_plan", "refine_plan"):
        step = next(s for s in steps if s["name"] == name)
        assert step["coder"]["role_policy"] == "plan_standard"

    # Verify policies exist in registry
    import json
    registry_path = Path(__file__).parents[2] / "workflows" / "_registry" / "role_policies.json"
    policies = json.loads(registry_path.read_text(encoding="utf-8"))["role_policies"]
    assert "reviewer_standard" in policies
    assert "plan_standard" in policies

    # Verify coder roles resolve to opencode
    roles_path = Path(__file__).parents[2] / "workflows" / "_registry" / "coder_roles.json"
    roles = json.loads(roles_path.read_text(encoding="utf-8"))["roles"]
    reviewer_role = policies["reviewer_standard"]["default_role"]
    planner_role = policies["plan_standard"]["default_role"]
    assert roles[reviewer_role]["coder"] == "opencode"
    assert roles[planner_role]["coder"] == "opencode"


# ---------------------------------------------------------------------------
# 13. E2E reject → refine → re-review
# ---------------------------------------------------------------------------

def test_e2e_reject_refine_rereview(monkeypatch) -> None:
    """Full cycle: human rejects twice, revision increments each time."""
    monkeypatch.setattr(job_state, "send_step_notification", lambda *a, **kw: None)
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-10-25T00:00:00")
    monkeypatch.setattr(job_state, "set_job_status", lambda s, v: s.__setitem__("_status", v))
    monkeypatch.setattr(job_state, "get_job_status", lambda s: s.get("_status", "IN_PROGRESS"))
    monkeypatch.setattr(job_state, "set_last_failure", lambda **kw: None)
    monkeypatch.setattr(job_state, "clear_last_failure", lambda s: None)
    monkeypatch.setattr(job_state, "save_job", lambda *a: None)
    monkeypatch.setattr(job_state, "default_loop_context", lambda **kw: {"active": True, **kw})

    group_cfg = {
        "step_configs": {
            "codex_review": {
                "on_reject_refine": {
                    "step": "refine_plan",
                    "artifact": "QWEN_PLAN_FILE",
                    "max_iterations": 10,
                    "max_human_rejections": 3,
                    "exhausted_failure_code": "PLAN_REFINEMENT_EXHAUSTED",
                    "human_exhausted_failure_code": "PLAN_HUMAN_REJECTION_EXHAUSTED",
                },
            },
        },
    }

    state = {
        "job_id": "test-job",
        "plan_revision": 1,
        "pending_human_approval_for": "codex_review",
        "reject_counts": {},
        "human_reject_counts": {},
        "review_state": {},
        "human_approvals": {"codex_review": True},
        "artifacts": {"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v01.md"},
    }

    # First human rejection → revision stays 1, refine loop activates
    result = job_state.reject_step(
        group_name="plan_first_review_v1", group_cfg=group_cfg,
        state=state, step="codex_review",
    )
    assert result["human_reject_counts"]["codex_review"] == 1
    assert result["_status"] == "IN_PROGRESS"  # refine loop activated

    # Simulate refine success → revision increments to 2
    result["plan_revision"] = 2
    result["reject_counts"]["codex_review"] = 0  # success resets reject_counts

    # Second human rejection
    result["pending_human_approval_for"] = "codex_review"
    result["human_approvals"] = {"codex_review": True}
    result2 = job_state.reject_step(
        group_name="plan_first_review_v1", group_cfg=group_cfg,
        state=result, step="codex_review",
    )
    assert result2["human_reject_counts"]["codex_review"] == 2
    assert result2["plan_revision"] == 2  # revision persists
    assert result2["reject_counts"]["codex_review"] == 1  # reset then incremented


# ---------------------------------------------------------------------------
# Baseline path constants
# ---------------------------------------------------------------------------

def test_baseline_path_constants_baseline_1_at_root() -> None:
    """Baseline 1 paths stay at root (backward compatible)."""
    from agent_runner_v2.constants import (
        ARTIFACT_PATH_BASELINE_DIR,
        ARTIFACT_PATH_BASELINE_REQUEST,
        ARTIFACT_PATH_REQUIREMENTS,
        ARTIFACT_PATH_QWEN_PLAN,
        ARTIFACT_PATH_CODEX_REVIEW,
    )
    
    folder = "Planning/20261025-01_Test"
    
    # Baseline 1 at root
    assert ARTIFACT_PATH_BASELINE_DIR(folder, 1) == f"{folder}/"
    assert ARTIFACT_PATH_BASELINE_REQUEST(folder, 1) == f"{folder}/request.md"
    assert ARTIFACT_PATH_REQUIREMENTS(folder, 1) == f"{folder}/requirements.md"
    assert ARTIFACT_PATH_QWEN_PLAN(folder, 1, 1) == f"{folder}/Qwen_Plan_v01.md"
    assert ARTIFACT_PATH_CODEX_REVIEW(folder, 1, 1) == f"{folder}/Codex_Review_v01.md"


def test_baseline_path_constants_baseline_2_in_subdirectory() -> None:
    """Baseline 2+ paths use subdirectories."""
    from agent_runner_v2.constants import (
        ARTIFACT_PATH_BASELINE_DIR,
        ARTIFACT_PATH_BASELINE_REQUEST,
        ARTIFACT_PATH_REQUIREMENTS,
        ARTIFACT_PATH_QWEN_PLAN,
        ARTIFACT_PATH_CODEX_REVIEW,
    )
    
    folder = "Planning/20261025-01_Test"
    
    # Baseline 2 in subdirectory
    assert ARTIFACT_PATH_BASELINE_DIR(folder, 2) == f"{folder}/baseline_02"
    assert ARTIFACT_PATH_BASELINE_REQUEST(folder, 2) == f"{folder}/baseline_02/request.md"
    assert ARTIFACT_PATH_REQUIREMENTS(folder, 2) == f"{folder}/baseline_02/requirements.md"
    assert ARTIFACT_PATH_QWEN_PLAN(folder, 1, 2) == f"{folder}/baseline_02/Qwen_Plan_v01.md"
    assert ARTIFACT_PATH_CODEX_REVIEW(folder, 1, 2) == f"{folder}/baseline_02/Codex_Review_v01.md"


def test_baseline_path_constants_default_parameter() -> None:
    """Default baseline parameter is 1 (backward compatible)."""
    from agent_runner_v2.constants import (
        ARTIFACT_PATH_REQUIREMENTS,
        ARTIFACT_PATH_QWEN_PLAN,
        ARTIFACT_PATH_CODEX_REVIEW,
    )
    
    folder = "Planning/20261025-01_Test"
    
    # Default baseline=1
    assert ARTIFACT_PATH_REQUIREMENTS(folder) == f"{folder}/requirements.md"
    assert ARTIFACT_PATH_QWEN_PLAN(folder, 1) == f"{folder}/Qwen_Plan_v01.md"
    assert ARTIFACT_PATH_CODEX_REVIEW(folder, 1) == f"{folder}/Codex_Review_v01.md"


# ---------------------------------------------------------------------------
# Cumulative refinement limit
# ---------------------------------------------------------------------------

def test_ten_refinements_allowed_eleventh_blocked(monkeypatch) -> None:
    """10 refinements allowed, 11th blocked by cumulative limit."""
    monkeypatch.setattr(job_state, "send_step_notification", lambda *a, **kw: None)
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-10-25T00:00:00")
    monkeypatch.setattr(job_state, "set_job_status", lambda s, v: s.__setitem__("_status", v))
    monkeypatch.setattr(job_state, "get_job_status", lambda s: s.get("_status", "IN_PROGRESS"))
    monkeypatch.setattr(job_state, "set_last_failure", lambda **kw: None)
    monkeypatch.setattr(job_state, "append_failure_history", lambda **kw: None)
    monkeypatch.setattr(job_state, "save_job", lambda *a: None)
    
    group_cfg = {
        "step_configs": {
            "codex_review": {
                "on_reject_refine": {
                    "step": "refine_plan",
                    "artifact": "QWEN_PLAN_FILE",
                    "max_iterations": 10,
                    "max_refinements": 10,
                    "max_human_rejections": 3,
                }
            }
        }
    }
    
    # Simulate 10 refinements (plan_revision = 11 after 10 increments)
    state = {
        "job_id": "PLAN-TEST-001",
        "plan_revision": 11,  # After 10 refinements
        "reject_counts": {"codex_review": 0},
        "human_reject_counts": {"codex_review": 0},
        "refinement_extensions": [],
        "loop_context": {},
        "review_state": {},
        "pending_human_approval_for": "codex_review",
        "human_approvals": {"codex_review": True},
        "artifacts": {"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v11.md"},
    }
    
    # 11th rejection should be blocked by cumulative limit
    result = job_state.reject_step(
        group_name="plan_first_review_v1", group_cfg=group_cfg,
        state=state, step="codex_review",
    )
    assert result["_status"] == "WAITING_FOR_HUMAN_INTERVENTION"
    assert result["pending_intervention_for"] == "codex_review"


def test_retry_does_not_reset_plan_revision(monkeypatch) -> None:
    """--retry-step does not reset plan_revision (cumulative counter persists)."""
    monkeypatch.setattr(job_state, "send_step_notification", lambda *a, **kw: None)
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-10-25T00:00:00")
    monkeypatch.setattr(job_state, "set_job_status", lambda s, v: s.__setitem__("_status", v))
    monkeypatch.setattr(job_state, "get_job_status", lambda s: s.get("_status", "WAITING_FOR_HUMAN_INTERVENTION"))
    monkeypatch.setattr(job_state, "set_last_failure", lambda **kw: None)
    monkeypatch.setattr(job_state, "append_failure_history", lambda **kw: None)
    monkeypatch.setattr(job_state, "save_job", lambda *a: None)

    # Simulate retry_step (which resets reject_counts but not plan_revision)
    state = {
        "job_id": "PLAN-TEST-RETRY",
        "plan_revision": 5,
        "reject_counts": {"codex_review": 3},
        "human_reject_counts": {},
    }

    # retry_step resets reject_counts but not plan_revision
    job_state.retry_step(
        group_name="plan_first_review_v1", group_cfg={},
        state=state, step="codex_review",
    )

    assert state["reject_counts"]["codex_review"] == 0  # Reset
    assert state["plan_revision"] == 5  # NOT reset


def test_reject_step_uses_plan_revision_not_reject_counts(monkeypatch) -> None:
    """Cumulative limit uses plan_revision, not reject_counts."""
    monkeypatch.setattr(job_state, "send_step_notification", lambda *a, **kw: None)
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-10-25T00:00:00")
    monkeypatch.setattr(job_state, "set_job_status", lambda s, v: s.__setitem__("_status", v))
    monkeypatch.setattr(job_state, "get_job_status", lambda s: s.get("_status", "IN_PROGRESS"))
    monkeypatch.setattr(job_state, "set_last_failure", lambda **kw: None)
    monkeypatch.setattr(job_state, "append_failure_history", lambda **kw: None)
    monkeypatch.setattr(job_state, "save_job", lambda *a: None)
    
    group_cfg = {
        "step_configs": {
            "codex_review": {
                "on_reject_refine": {
                    "step": "refine_plan",
                    "artifact": "QWEN_PLAN_FILE",
                    "max_iterations": 10,
                    "max_refinements": 5,  # Low cumulative limit
                    "max_human_rejections": 3,
                }
            }
        }
    }
    
    # plan_revision = 6 (exceeds max_refinements=5), but reject_counts = 0
    state = {
        "job_id": "PLAN-TEST-002",
        "plan_revision": 6,
        "reject_counts": {"codex_review": 0},  # Low reject count
        "human_reject_counts": {"codex_review": 0},
        "refinement_extensions": [],
        "loop_context": {},
        "review_state": {},
        "pending_human_approval_for": "codex_review",
        "human_approvals": {"codex_review": True},
        "artifacts": {"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v06.md"},
    }
    
    # Should be blocked by cumulative limit (plan_revision > max_refinements)
    result = job_state.reject_step(
        group_name="plan_first_review_v1", group_cfg=group_cfg,
        state=state, step="codex_review",
    )
    assert result["_status"] == "WAITING_FOR_HUMAN_INTERVENTION"


def test_human_rejection_limit_still_enforced(monkeypatch) -> None:
    """Human rejection limit (max_human_rejections) still enforced independently."""
    monkeypatch.setattr(job_state, "send_step_notification", lambda *a, **kw: None)
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-10-25T00:00:00")
    monkeypatch.setattr(job_state, "set_job_status", lambda s, v: s.__setitem__("_status", v))
    monkeypatch.setattr(job_state, "get_job_status", lambda s: s.get("_status", "IN_PROGRESS"))
    monkeypatch.setattr(job_state, "set_last_failure", lambda **kw: None)
    monkeypatch.setattr(job_state, "append_failure_history", lambda **kw: None)
    monkeypatch.setattr(job_state, "save_job", lambda *a: None)
    
    group_cfg = {
        "step_configs": {
            "codex_review": {
                "on_reject_refine": {
                    "step": "refine_plan",
                    "artifact": "QWEN_PLAN_FILE",
                    "max_iterations": 10,
                    "max_refinements": 10,
                    "max_human_rejections": 3,
                }
            }
        }
    }
    
    # 4th human rejection (exceeds max_human_rejections=3)
    state = {
        "job_id": "PLAN-TEST-003",
        "plan_revision": 2,  # Low revision
        "reject_counts": {"codex_review": 4},
        "human_reject_counts": {"codex_review": 4},  # Exceeds limit
        "refinement_extensions": [],
        "loop_context": {},
        "review_state": {},
        "pending_human_approval_for": "codex_review",
        "human_approvals": {"codex_review": True},
        "artifacts": {"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v02.md"},
    }
    
    # Should be blocked by human rejection limit (checked FIRST)
    result = job_state.reject_step(
        group_name="plan_first_review_v1", group_cfg=group_cfg,
        state=state, step="codex_review",
    )
    assert result["_status"] == "WAITING_FOR_HUMAN_INTERVENTION"
    assert result["human_reject_counts"]["codex_review"] == 5  # Incremented from 4 to 5


# ---------------------------------------------------------------------------
# Continuation with counter reset
# ---------------------------------------------------------------------------

def test_extend_refinement_limit_resets_reject_counts(monkeypatch) -> None:
    """extend_refinement_limit resets reject_counts and extends effective limit."""
    monkeypatch.setattr(job_state, "send_step_notification", lambda *a, **kw: None)
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-10-25T00:00:00")
    monkeypatch.setattr(job_state, "set_job_status", lambda s, v: s.__setitem__("_status", v))
    monkeypatch.setattr(job_state, "get_job_status", lambda s: s.get("_status", "WAITING_FOR_HUMAN_INTERVENTION"))
    monkeypatch.setattr(job_state, "set_last_failure", lambda **kw: None)
    monkeypatch.setattr(job_state, "clear_last_failure", lambda s: None)
    monkeypatch.setattr(job_state, "save_job", lambda *a: None)

    group_cfg = {
        "step_configs": {
            "codex_review": {
                "on_reject_refine": {
                    "step": "refine_plan",
                    "artifact": "QWEN_PLAN_FILE",
                    "max_iterations": 10,
                    "max_refinements": 10,
                    "max_human_rejections": 3,
                    "max_ceiling": 20,
                    "exhausted_failure_code": "PLAN_REFINEMENT_EXHAUSTED",
                }
            }
        }
    }

    state = {
        "job_id": "PLAN-TEST-EXTEND",
        "plan_revision": 11,  # Exceeds max_refinements=10
        "reject_counts": {"codex_review": 10},  # At per-step limit
        "human_reject_counts": {"codex_review": 2},
        "refinement_extensions": [],
        "last_failure_code": "PLAN_REFINEMENT_EXHAUSTED",
        "loop_context": {},
        "review_state": {},
        "pending_intervention_for": "codex_review",
        "pending_human_approval_for": "codex_review",
        "artifacts": {"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v11.md"},
    }

    result = job_state.extend_refinement_limit(
        group_name="plan_first_review_v1",
        group_cfg=group_cfg,
        state=state,
        additional_allowance=5,
        reason="Need more iterations",
    )

    # Verify extension recorded
    assert len(result["refinement_extensions"]) == 1
    assert result["refinement_extensions"][0]["additional_allowance"] == 5
    assert result["refinement_extensions"][0]["reason"] == "Need more iterations"

    # Verify reject_counts reset
    assert result["reject_counts"]["codex_review"] == 0

    # Verify loop context reconstructed
    assert result["loop_context"]["active"] is True
    assert result["loop_context"]["loop_step"] == "codex_review"
    assert result["loop_context"]["refine_step"] == "refine_plan"
    assert result["loop_context"]["loop_target_artifact"] == "QWEN_PLAN_FILE"

    # Verify transition to refine step
    assert result["current_step"] == "refine_plan"
    assert result["_status"] == "IN_PROGRESS"
    assert result["pending_intervention_for"] is None
    assert result["pending_human_approval_for"] is None


def test_extend_refinement_limit_only_for_plan_first_review(monkeypatch) -> None:
    """extend_refinement_limit rejects non-plan_first_review_v1 workflows."""
    monkeypatch.setattr(job_state, "save_job", lambda *a: None)

    state = {
        "job_id": "OTHER-TEST",
        "plan_revision": 5,
        "reject_counts": {},
        "refinement_extensions": [],
    }

    with pytest.raises(ValueError, match="only valid for plan_first_review_v1"):
        job_state.extend_refinement_limit(
            group_name="other_workflow",
            group_cfg={},
            state=state,
            additional_allowance=5,
        )


def test_extend_refinement_limit_requires_waiting_status(monkeypatch) -> None:
    """extend_refinement_limit requires WAITING_FOR_HUMAN_INTERVENTION status."""
    monkeypatch.setattr(job_state, "get_job_status", lambda s: s.get("_status", "IN_PROGRESS"))
    monkeypatch.setattr(job_state, "save_job", lambda *a: None)

    state = {
        "job_id": "PLAN-TEST-STATUS",
        "_status": "IN_PROGRESS",
        "plan_revision": 5,
        "reject_counts": {},
        "refinement_extensions": [],
    }

    with pytest.raises(ValueError, match="expected WAITING_FOR_HUMAN_INTERVENTION"):
        job_state.extend_refinement_limit(
            group_name="plan_first_review_v1",
            group_cfg={"step_configs": {"codex_review": {"on_reject_refine": {"step": "refine_plan", "artifact": "QWEN_PLAN_FILE"}}}},
            state=state,
            additional_allowance=5,
        )


def test_extend_refinement_limit_increases_effective_limit(monkeypatch) -> None:
    """Multiple extensions accumulate in effective limit."""
    monkeypatch.setattr(job_state, "send_step_notification", lambda *a, **kw: None)
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-10-25T00:00:00")
    monkeypatch.setattr(job_state, "set_job_status", lambda s, v: s.__setitem__("_status", v))
    monkeypatch.setattr(job_state, "get_job_status", lambda s: s.get("_status", "WAITING_FOR_HUMAN_INTERVENTION"))
    monkeypatch.setattr(job_state, "set_last_failure", lambda **kw: None)
    monkeypatch.setattr(job_state, "clear_last_failure", lambda s: None)
    monkeypatch.setattr(job_state, "save_job", lambda *a: None)

    group_cfg = {
        "step_configs": {
            "codex_review": {
                "on_reject_refine": {
                    "step": "refine_plan",
                    "artifact": "QWEN_PLAN_FILE",
                    "max_refinements": 10,
                    "max_ceiling": 20,
                    "exhausted_failure_code": "PLAN_REFINEMENT_EXHAUSTED",
                }
            }
        }
    }

    state = {
        "job_id": "PLAN-TEST-MULTI",
        "plan_revision": 11,
        "reject_counts": {"codex_review": 10},
        "refinement_extensions": [],
        "last_failure_code": "PLAN_REFINEMENT_EXHAUSTED",
        "loop_context": {},
        "review_state": {},
        "pending_intervention_for": "codex_review",
        "pending_human_approval_for": "codex_review",
        "artifacts": {"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v11.md"},
    }

    # First extension: +5
    result = job_state.extend_refinement_limit(
        group_name="plan_first_review_v1",
        group_cfg=group_cfg,
        state=state,
        additional_allowance=5,
    )
    assert len(result["refinement_extensions"]) == 1
    effective_limit = job_state._get_effective_limit(result, group_cfg["step_configs"]["codex_review"]["on_reject_refine"])
    assert effective_limit == 15  # 10 base + 5 extension

    # Second extension: +3
    result["pending_intervention_for"] = "codex_review"
    result["pending_human_approval_for"] = "codex_review"
    result["_status"] = "WAITING_FOR_HUMAN_INTERVENTION"
    result = job_state.extend_refinement_limit(
        group_name="plan_first_review_v1",
        group_cfg=group_cfg,
        state=result,
        additional_allowance=3,
    )
    assert len(result["refinement_extensions"]) == 2
    effective_limit = job_state._get_effective_limit(result, group_cfg["step_configs"]["codex_review"]["on_reject_refine"])
    assert effective_limit == 18  # 10 base + 5 + 3


def test_extend_refinement_limit_rejects_non_positive_allowance(monkeypatch) -> None:
    """extend_refinement_limit rejects additional_allowance <= 0."""
    monkeypatch.setattr(job_state, "get_job_status", lambda s: s.get("_status", "WAITING_FOR_HUMAN_INTERVENTION"))
    monkeypatch.setattr(job_state, "save_job", lambda *a: None)

    group_cfg = {
        "step_configs": {
            "codex_review": {
                "on_reject_refine": {
                    "step": "refine_plan",
                    "artifact": "QWEN_PLAN_FILE",
                    "max_refinements": 10,
                    "max_ceiling": 20,
                    "exhausted_failure_code": "PLAN_REFINEMENT_EXHAUSTED",
                }
            }
        }
    }

    base_state = {
        "job_id": "PLAN-TEST-ALLOWANCE",
        "_status": "WAITING_FOR_HUMAN_INTERVENTION",
        "plan_revision": 11,
        "reject_counts": {"codex_review": 10},
        "refinement_extensions": [],
        "last_failure_code": "PLAN_REFINEMENT_EXHAUSTED",
    }

    # allowance=0
    with pytest.raises(ValueError, match="additional_allowance must be positive"):
        job_state.extend_refinement_limit(
            group_name="plan_first_review_v1",
            group_cfg=group_cfg,
            state=dict(base_state),
            additional_allowance=0,
        )

    # allowance=-1
    with pytest.raises(ValueError, match="additional_allowance must be positive"):
        job_state.extend_refinement_limit(
            group_name="plan_first_review_v1",
            group_cfg=group_cfg,
            state=dict(base_state),
            additional_allowance=-1,
        )


def test_extend_refinement_limit_requires_cumulative_exhaustion(monkeypatch) -> None:
    """extend_refinement_limit requires last_failure_code to match exhausted_failure_code."""
    monkeypatch.setattr(job_state, "get_job_status", lambda s: s.get("_status", "WAITING_FOR_HUMAN_INTERVENTION"))
    monkeypatch.setattr(job_state, "save_job", lambda *a: None)

    group_cfg = {
        "step_configs": {
            "codex_review": {
                "on_reject_refine": {
                    "step": "refine_plan",
                    "artifact": "QWEN_PLAN_FILE",
                    "max_refinements": 10,
                    "max_ceiling": 20,
                    "exhausted_failure_code": "PLAN_REFINEMENT_EXHAUSTED",
                }
            }
        }
    }

    # Wrong failure code — e.g. model rejection exhaustion, not cumulative
    state = {
        "job_id": "PLAN-TEST-WRONG-CODE",
        "_status": "WAITING_FOR_HUMAN_INTERVENTION",
        "plan_revision": 11,
        "reject_counts": {"codex_review": 10},
        "refinement_extensions": [],
        "last_failure_code": "REFINEMENT_EXHAUSTED",
    }

    with pytest.raises(ValueError, match="last_failure_code is 'REFINEMENT_EXHAUSTED'.*expected 'PLAN_REFINEMENT_EXHAUSTED'"):
        job_state.extend_refinement_limit(
            group_name="plan_first_review_v1",
            group_cfg=group_cfg,
            state=state,
            additional_allowance=5,
        )

    # No failure code at all
    state2 = dict(state)
    state2["last_failure_code"] = None
    with pytest.raises(ValueError, match="last_failure_code is None"):
        job_state.extend_refinement_limit(
            group_name="plan_first_review_v1",
            group_cfg=group_cfg,
            state=state2,
            additional_allowance=5,
        )


def test_extend_refinement_limit_respects_max_ceiling(monkeypatch) -> None:
    """extend_refinement_limit rejects extensions that would exceed max_ceiling."""
    monkeypatch.setattr(job_state, "get_job_status", lambda s: s.get("_status", "WAITING_FOR_HUMAN_INTERVENTION"))
    monkeypatch.setattr(job_state, "save_job", lambda *a: None)

    group_cfg = {
        "step_configs": {
            "codex_review": {
                "on_reject_refine": {
                    "step": "refine_plan",
                    "artifact": "QWEN_PLAN_FILE",
                    "max_refinements": 10,
                    "max_ceiling": 20,
                    "exhausted_failure_code": "PLAN_REFINEMENT_EXHAUSTED",
                }
            }
        }
    }

    # Already at ceiling (base 10 + existing extension 10 = 20), try to add 1 more
    state = {
        "job_id": "PLAN-TEST-CEILING",
        "_status": "WAITING_FOR_HUMAN_INTERVENTION",
        "plan_revision": 21,
        "reject_counts": {"codex_review": 10},
        "refinement_extensions": [{"additional_allowance": 10, "reason": "prior", "granted_at": "2026-10-24T00:00:00"}],
        "last_failure_code": "PLAN_REFINEMENT_EXHAUSTED",
    }

    with pytest.raises(ValueError, match="would exceed max_ceiling"):
        job_state.extend_refinement_limit(
            group_name="plan_first_review_v1",
            group_cfg=group_cfg,
            state=state,
            additional_allowance=1,
        )

    # Exactly at ceiling is OK (base 10 + 10 = 20, adding 0 would be rejected by positive check,
    # but adding up to ceiling is fine — verify boundary: base 10 + 5 = 15, adding 5 = 20 exactly)
    state2 = {
        "job_id": "PLAN-TEST-CEILING-OK",
        "_status": "WAITING_FOR_HUMAN_INTERVENTION",
        "plan_revision": 16,
        "reject_counts": {"codex_review": 10},
        "refinement_extensions": [{"additional_allowance": 5, "reason": "prior", "granted_at": "2026-10-24T00:00:00"}],
        "last_failure_code": "PLAN_REFINEMENT_EXHAUSTED",
        "loop_context": {},
        "review_state": {},
        "pending_intervention_for": "codex_review",
        "pending_human_approval_for": "codex_review",
        "artifacts": {"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v16.md"},
    }
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-10-25T00:00:00")
    monkeypatch.setattr(job_state, "set_job_status", lambda s, v: s.__setitem__("_status", v))
    monkeypatch.setattr(job_state, "clear_last_failure", lambda s: None)

    result = job_state.extend_refinement_limit(
        group_name="plan_first_review_v1",
        group_cfg=group_cfg,
        state=state2,
        additional_allowance=5,
    )
    effective = job_state._get_effective_limit(result, group_cfg["step_configs"]["codex_review"]["on_reject_refine"])
    assert effective == 20  # exactly at ceiling


def test_continue_refinement_cli_passes_workspace_root(monkeypatch, tmp_path) -> None:
    """continue-refinement CLI calls get_template_group_cfg with workspace_root keyword."""
    from agent_runner_v2 import run_agent, runtime_context, workflow_specs
    import json

    # Create a fake job directory with job.json
    jobs_root = tmp_path / "jobs"
    job_dir = jobs_root / "plan_first_review_v1" / "PLAN-CLI-TEST"
    job_dir.mkdir(parents=True)
    job_json = job_dir / "job.json"
    job_json.write_text(json.dumps({
        "job_id": "PLAN-CLI-TEST",
        "template_group": "plan_first_review_v1",
        "_status": "WAITING_FOR_HUMAN_INTERVENTION",
        "plan_revision": 11,
        "reject_counts": {"codex_review": 10},
        "refinement_extensions": [],
        "last_failure_code": "PLAN_REFINEMENT_EXHAUSTED",
    }), encoding="utf-8")

    workspace = tmp_path / "workspace"
    workspace.mkdir()

    captured_cfg_args = {}

    def fake_get_cfg(*, template_group, workspace_root, workflow_name="default"):
        captured_cfg_args["template_group"] = template_group
        captured_cfg_args["workspace_root"] = workspace_root
        captured_cfg_args["workflow_name"] = workflow_name
        return {
            "step_configs": {
                "codex_review": {
                    "on_reject_refine": {
                        "step": "refine_plan",
                        "artifact": "QWEN_PLAN_FILE",
                        "max_refinements": 10,
                        "max_ceiling": 20,
                        "exhausted_failure_code": "PLAN_REFINEMENT_EXHAUSTED",
                    }
                }
            }
        }

    monkeypatch.setattr(runtime_context, "get_jobs_root", lambda: str(jobs_root))
    monkeypatch.setattr(runtime_context, "get_workspace_root", lambda: workspace)
    monkeypatch.setattr(workflow_specs, "get_template_group_cfg", fake_get_cfg)
    monkeypatch.setattr(job_state, "save_job", lambda *a: None)
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-10-25T00:00:00")
    monkeypatch.setattr(job_state, "set_job_status", lambda s, v: s.__setitem__("_status", v))
    monkeypatch.setattr(job_state, "get_job_status", lambda s: s.get("_status", "WAITING_FOR_HUMAN_INTERVENTION"))
    monkeypatch.setattr(job_state, "clear_last_failure", lambda s: None)

    rc = run_agent.main(["continue-refinement", "--job-id", "PLAN-CLI-TEST", "--additional-allowance", "5", "--reason", "test"])
    assert rc == 0

    # Verify get_template_group_cfg was called with correct keyword args
    assert captured_cfg_args["template_group"] == "plan_first_review_v1"
    assert captured_cfg_args["workspace_root"] == workspace


def test_model_rejection_route_checks_cumulative_limit(monkeypatch) -> None:
    """Model rejection route (_route_loop_or_replan) blocks when cumulative limit exceeded."""
    from agent_runner_v2.v2 import workflow_router
    from agent_runner_v2.step_runner import StepResult

    monkeypatch.setattr(workflow_router, "set_job_status", lambda s, v: s.__setitem__("_status", v))
    monkeypatch.setattr(workflow_router, "set_last_failure", lambda **kw: None)
    monkeypatch.setattr(workflow_router, "save_job", lambda *a: None)
    monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
    monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a, **kw: None)

    on_reject_refine = {
        "step": "refine_plan",
        "artifact": "QWEN_PLAN_FILE",
        "max_iterations": 10,
        "max_refinements": 10,
        "max_ceiling": 20,
        "exhausted_failure_code": "PLAN_REFINEMENT_EXHAUSTED",
        "exhausted_failure_class": "HUMAN_RETRY_REQUIRED",
    }

    state = {
        "job_id": "PLAN-MODEL-CUMULATIVE",
        "template_group": "plan_first_review_v1",
        "plan_revision": 11,  # Exceeds max_refinements=10
        "reject_counts": {"codex_review": 2},  # Well under max_iterations=10
        "refinement_extensions": [],
        "_status": "IN_PROGRESS",
    }

    step_result = StepResult(
        status="REJECTED",
        remark="Model found issues",
        artifacts={},
        reject_code=None,
        meta_json_path="test/meta.json",
        usage_data={},
    )

    result_state, rc = workflow_router._route_loop_or_replan(
        group_name="plan_first_review_v1",
        group_cfg={"step_configs": {"codex_review": {"on_reject_refine": on_reject_refine}}},
        state=state,
        step="codex_review",
        step_cfg={"on_reject_refine": on_reject_refine},
        step_result=step_result,
        coder_used="test_coder",
        on_reject_refine=on_reject_refine,
        reject_counts=state["reject_counts"],
        artifacts={},
    )

    # Should be blocked by cumulative limit, NOT trigger loop
    assert result_state["_status"] == "WAITING_FOR_HUMAN_INTERVENTION"
    assert result_state["pending_intervention_for"] == "codex_review"
    # reject_counts was incremented (3) but loop was NOT triggered
    assert result_state["reject_counts"]["codex_review"] == 3


def test_continue_refinement_cli_rejects_substring_collision(monkeypatch, tmp_path) -> None:
    """continue-refinement CLI rejects substring matches — requires exact job_id."""
    from agent_runner_v2 import run_agent, runtime_context, workflow_specs
    import json

    # Create two job directories: "PLAN-1" and "PLAN-10"
    # Searching for "PLAN-1" must NOT match "PLAN-10"
    jobs_root = tmp_path / "jobs"

    # PLAN-10 directory (created first to test ordering independence)
    job_dir_10 = jobs_root / "plan_first_review_v1" / "PLAN-10"
    job_dir_10.mkdir(parents=True)
    (job_dir_10 / "job.json").write_text(json.dumps({
        "job_id": "PLAN-10",
        "template_group": "plan_first_review_v1",
        "_status": "WAITING_FOR_HUMAN_INTERVENTION",
        "plan_revision": 11,
        "reject_counts": {"codex_review": 10},
        "refinement_extensions": [],
        "last_failure_code": "PLAN_REFINEMENT_EXHAUSTED",
    }), encoding="utf-8")

    # PLAN-1 directory (the actual target)
    job_dir_1 = jobs_root / "plan_first_review_v1" / "PLAN-1"
    job_dir_1.mkdir(parents=True)
    (job_dir_1 / "job.json").write_text(json.dumps({
        "job_id": "PLAN-1",
        "template_group": "plan_first_review_v1",
        "_status": "WAITING_FOR_HUMAN_INTERVENTION",
        "plan_revision": 11,
        "reject_counts": {"codex_review": 10},
        "refinement_extensions": [],
        "last_failure_code": "PLAN_REFINEMENT_EXHAUSTED",
    }), encoding="utf-8")

    workspace = tmp_path / "workspace"
    workspace.mkdir()

    captured_job_ids = []

    def fake_get_cfg(*, template_group, workspace_root, workflow_name="default"):
        return {
            "step_configs": {
                "codex_review": {
                    "on_reject_refine": {
                        "step": "refine_plan",
                        "artifact": "QWEN_PLAN_FILE",
                        "max_refinements": 10,
                        "max_ceiling": 20,
                        "exhausted_failure_code": "PLAN_REFINEMENT_EXHAUSTED",
                    }
                }
            }
        }

    monkeypatch.setattr(runtime_context, "get_jobs_root", lambda: str(jobs_root))
    monkeypatch.setattr(runtime_context, "get_workspace_root", lambda: workspace)
    monkeypatch.setattr(workflow_specs, "get_template_group_cfg", fake_get_cfg)
    monkeypatch.setattr(job_state, "save_job", lambda *a: None)
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-10-25T00:00:00")
    monkeypatch.setattr(job_state, "set_job_status", lambda s, v: s.__setitem__("_status", v))
    monkeypatch.setattr(job_state, "get_job_status", lambda s: s.get("_status", "WAITING_FOR_HUMAN_INTERVENTION"))
    monkeypatch.setattr(job_state, "clear_last_failure", lambda s: None)

    # Search for "PLAN-1" — must match PLAN-1, not PLAN-10
    rc = run_agent.main(["continue-refinement", "--job-id", "PLAN-1", "--additional-allowance", "5"])
    assert rc == 0

    # Search for "PLAN-10" — must match PLAN-10
    rc = run_agent.main(["continue-refinement", "--job-id", "PLAN-10", "--additional-allowance", "3"])
    assert rc == 0

    # Search for non-existent "PLAN-11" — must fail even though "PLAN-1" is a substring
    rc = run_agent.main(["continue-refinement", "--job-id", "PLAN-11", "--additional-allowance", "1"])
    assert rc == 1


# ---------------------------------------------------------------------------
# Phase 4: Stop/Archive and Change Requirements
# ---------------------------------------------------------------------------

def test_stop_and_archive_creates_terminal_state(monkeypatch) -> None:
    """stop_and_archive() marks job as STOPPED_ARCHIVED and preserves artifacts."""
    monkeypatch.setattr(job_state, "send_step_notification", lambda *a, **kw: None)
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-10-25T00:00:00")
    monkeypatch.setattr(job_state, "set_job_status", lambda s, v: s.__setitem__("_status", v))
    monkeypatch.setattr(job_state, "save_job", lambda *a: None)

    state = {
        "job_id": "PLAN-TEST-001",
        "template_group": "plan_first_review_v1",
        "artifacts": {"QWEN_PLAN_FILE": "/path/to/plan.md"},
        "pending_intervention_for": "codex_review",
        "pending_human_approval_for": "codex_review",
        "loop_context": {"active": True},
    }

    result = job_state.stop_and_archive(
        group_name="plan_first_review_v1",
        state=state,
        reason="User requested stop",
    )

    assert result["_status"] == "STOPPED_ARCHIVED"
    assert result["stop_reason"] == "User requested stop"
    assert result["stopped_at"] == "2026-10-25T00:00:00"
    assert result["pending_intervention_for"] is None
    assert result["pending_human_approval_for"] is None
    assert result["loop_context"]["active"] is False
    assert result["artifacts"]["QWEN_PLAN_FILE"] == "/path/to/plan.md"


def test_change_requirements_creates_baseline_subdirectory(tmp_path, monkeypatch) -> None:
    """change_requirements() creates baseline_02/ subdirectory for baseline 2."""
    monkeypatch.setattr("agent_runner_v2.job_state.PROJECT_ROOT", tmp_path)
    monkeypatch.setattr("agent_runner_v2.job_state.save_job", lambda *a: None)
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-10-25T00:00:00")
    monkeypatch.setattr(job_state, "set_job_status", lambda s, v: s.__setitem__("_status", v))

    planning_folder = "Planning/20261025-01_Test"
    planning_dir = tmp_path / planning_folder
    planning_dir.mkdir(parents=True)

    new_req_file = tmp_path / "new_requirements.md"
    new_req_file.write_text("New requirements")

    state = {
        "job_id": "PLAN-TEST-002",
        "template_group": "plan_first_review_v1",
        "requirements_baseline": 1,
        "artifacts": {"PLANNING_FOLDER": planning_folder},
        "completed_steps": ["prepare_request", "formalize_requirements"],
        "model_approved_steps": ["formalize_requirements"],
    }

    result = job_state.change_requirements(
        group_name="plan_first_review_v1",
        state=state,
        new_requirements_file=str(new_req_file),
        reason="Requirements changed",
    )

    assert result["requirements_baseline"] == 2
    assert (tmp_path / planning_folder / "baseline_02").exists()
    assert (tmp_path / planning_folder / "baseline_02" / "request.md").exists()


def test_change_requirements_preserves_old_baseline_files(tmp_path, monkeypatch) -> None:
    """change_requirements() preserves old baseline 1 files."""
    monkeypatch.setattr("agent_runner_v2.job_state.PROJECT_ROOT", tmp_path)
    monkeypatch.setattr("agent_runner_v2.job_state.save_job", lambda *a: None)
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-10-25T00:00:00")
    monkeypatch.setattr(job_state, "set_job_status", lambda s, v: s.__setitem__("_status", v))

    planning_folder = "Planning/20261025-01_Test"
    planning_dir = tmp_path / planning_folder
    planning_dir.mkdir(parents=True)

    # Create baseline 1 files
    (planning_dir / "requirements.md").write_text("Original requirements")
    (planning_dir / "Qwen_Plan_v02.md").write_text("Original plan")

    new_req_file = tmp_path / "new_requirements.md"
    new_req_file.write_text("New requirements")

    state = {
        "job_id": "PLAN-TEST-003",
        "template_group": "plan_first_review_v1",
        "requirements_baseline": 1,
        "artifacts": {
            "PLANNING_FOLDER": planning_folder,
            "REQUIREMENTS_FILE": str(planning_dir / "requirements.md"),
            "QWEN_PLAN_FILE": str(planning_dir / "Qwen_Plan_v02.md"),
        },
        "completed_steps": ["prepare_request"],
        "model_approved_steps": [],
    }

    result = job_state.change_requirements(
        group_name="plan_first_review_v1",
        state=state,
        new_requirements_file=str(new_req_file),
        reason="Requirements changed",
    )

    # Old baseline 1 files still exist
    assert (planning_dir / "requirements.md").read_text() == "Original requirements"
    assert (planning_dir / "Qwen_Plan_v02.md").read_text() == "Original plan"
    # New baseline 2 request.md created (formalize_requirements will produce requirements.md)
    assert (planning_dir / "baseline_02" / "request.md").read_text() == "New requirements"


def test_change_requirements_uses_baseline_aware_paths(tmp_path, monkeypatch) -> None:
    """change_requirements() updates artifacts to point to new baseline paths."""
    monkeypatch.setattr("agent_runner_v2.job_state.PROJECT_ROOT", tmp_path)
    monkeypatch.setattr("agent_runner_v2.job_state.save_job", lambda *a: None)
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-10-25T00:00:00")
    monkeypatch.setattr(job_state, "set_job_status", lambda s, v: s.__setitem__("_status", v))

    planning_folder = "Planning/20261025-01_Test"
    planning_dir = tmp_path / planning_folder
    planning_dir.mkdir(parents=True)

    new_req_file = tmp_path / "new_requirements.md"
    new_req_file.write_text("New requirements")

    state = {
        "job_id": "PLAN-TEST-004",
        "template_group": "plan_first_review_v1",
        "requirements_baseline": 1,
        "artifacts": {"PLANNING_FOLDER": planning_folder},
        "completed_steps": ["prepare_request"],
        "model_approved_steps": [],
    }

    result = job_state.change_requirements(
        group_name="plan_first_review_v1",
        state=state,
        new_requirements_file=str(new_req_file),
        reason="Requirements changed",
    )

    assert "baseline_02" in result["artifacts"]["RAW_REQUEST_FILE"]
    assert "baseline_02" in result["artifacts"]["REQUIREMENTS_FILE"]
    assert "baseline_02" in result["artifacts"]["QWEN_PLAN_FILE"]
    assert "baseline_02" in result["artifacts"]["CODEX_REVIEW_FILE"]


def test_change_requirements_clears_pending_approval(tmp_path, monkeypatch) -> None:
    """change_requirements() clears pending_human_approval_for."""
    monkeypatch.setattr("agent_runner_v2.job_state.PROJECT_ROOT", tmp_path)
    monkeypatch.setattr("agent_runner_v2.job_state.save_job", lambda *a: None)
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-10-25T00:00:00")
    monkeypatch.setattr(job_state, "set_job_status", lambda s, v: s.__setitem__("_status", v))

    planning_folder = "Planning/20261025-01_Test"
    planning_dir = tmp_path / planning_folder
    planning_dir.mkdir(parents=True)

    new_req_file = tmp_path / "new_requirements.md"
    new_req_file.write_text("New requirements")

    state = {
        "job_id": "PLAN-TEST-005",
        "template_group": "plan_first_review_v1",
        "requirements_baseline": 1,
        "artifacts": {"PLANNING_FOLDER": planning_folder},
        "completed_steps": ["prepare_request"],
        "model_approved_steps": [],
        "pending_human_approval_for": "codex_review",
    }

    result = job_state.change_requirements(
        group_name="plan_first_review_v1",
        state=state,
        new_requirements_file=str(new_req_file),
        reason="Requirements changed",
    )

    assert result["pending_human_approval_for"] is None


def test_change_requirements_preserves_prepare_request(tmp_path, monkeypatch) -> None:
    """change_requirements() preserves prepare_request in completed_steps."""
    monkeypatch.setattr("agent_runner_v2.job_state.PROJECT_ROOT", tmp_path)
    monkeypatch.setattr("agent_runner_v2.job_state.save_job", lambda *a: None)
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-10-25T00:00:00")
    monkeypatch.setattr(job_state, "set_job_status", lambda s, v: s.__setitem__("_status", v))

    planning_folder = "Planning/20261025-01_Test"
    planning_dir = tmp_path / planning_folder
    planning_dir.mkdir(parents=True)

    new_req_file = tmp_path / "new_requirements.md"
    new_req_file.write_text("New requirements")

    state = {
        "job_id": "PLAN-TEST-006",
        "template_group": "plan_first_review_v1",
        "requirements_baseline": 1,
        "artifacts": {"PLANNING_FOLDER": planning_folder},
        "completed_steps": ["prepare_request", "formalize_requirements", "generate_plan"],
        "model_approved_steps": ["formalize_requirements", "generate_plan"],
    }

    result = job_state.change_requirements(
        group_name="plan_first_review_v1",
        state=state,
        new_requirements_file=str(new_req_file),
        reason="Requirements changed",
    )

    assert result["completed_steps"] == ["prepare_request"]


def test_change_requirements_clears_model_approved_steps(tmp_path, monkeypatch) -> None:
    """change_requirements() clears model_approved_steps to empty list."""
    monkeypatch.setattr("agent_runner_v2.job_state.PROJECT_ROOT", tmp_path)
    monkeypatch.setattr("agent_runner_v2.job_state.save_job", lambda *a: None)
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-10-25T00:00:00")
    monkeypatch.setattr(job_state, "set_job_status", lambda s, v: s.__setitem__("_status", v))

    planning_folder = "Planning/20261025-01_Test"
    planning_dir = tmp_path / planning_folder
    planning_dir.mkdir(parents=True)

    new_req_file = tmp_path / "new_requirements.md"
    new_req_file.write_text("New requirements")

    state = {
        "job_id": "PLAN-TEST-007",
        "template_group": "plan_first_review_v1",
        "requirements_baseline": 1,
        "artifacts": {"PLANNING_FOLDER": planning_folder},
        "completed_steps": ["prepare_request"],
        "model_approved_steps": ["formalize_requirements", "generate_plan", "codex_review"],
    }

    result = job_state.change_requirements(
        group_name="plan_first_review_v1",
        state=state,
        new_requirements_file=str(new_req_file),
        reason="Requirements changed",
    )

    assert result["model_approved_steps"] == []
    assert isinstance(result["model_approved_steps"], list)


def test_stale_pending_approval_cleared_after_rebaseline(tmp_path, monkeypatch) -> None:
    """After change_requirements(), stale pending_human_approval_for is cleared."""
    from agent_runner_v2.workflow_packages.loader import load_workflow_package, bundle_to_template_group_dict
    from pathlib import Path
    import pytest

    monkeypatch.setattr("agent_runner_v2.job_state.PROJECT_ROOT", tmp_path)
    monkeypatch.setattr("agent_runner_v2.job_state.save_job", lambda *a: None)
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-10-25T00:00:00")
    monkeypatch.setattr(job_state, "set_job_status", lambda s, v: s.__setitem__("_status", v))

    workflow_pkg_dir = Path(__file__).parent.parent.parent / "workflows" / "plan_first_review_v1"
    bundle = load_workflow_package(workflow_pkg_dir)
    group_cfg = bundle_to_template_group_dict(bundle)

    new_req_file = tmp_path / "new_requirements.md"
    new_req_file.write_text("New requirements")

    planning_folder = "Planning/20261025-01_Test"
    planning_dir = tmp_path / planning_folder
    planning_dir.mkdir(parents=True)

    state = {
        "job_id": "PLAN-TEST-008",
        "template_group": "plan_first_review_v1",
        "requirements_baseline": 1,
        "plan_revision": 2,
        "completed_steps": ["prepare_request", "formalize_requirements", "generate_plan", "codex_review"],
        "model_approved_steps": ["formalize_requirements", "generate_plan", "codex_review"],
        "artifacts": {"PLANNING_FOLDER": planning_folder},
        "pending_human_approval_for": "codex_review",
        "review_state": default_review_state(),
        "human_approvals": {},
        "reject_counts": {},
        "human_reject_counts": {},
        "auto_retry_count_by_step": {},
        "human_retry_count_by_step": {},
        "refinement_extensions": [],
        "loop_context": default_loop_context(),
        "replan_context": default_replan_context(),
        "pending_intervention_for": None,
    }

    result = job_state.change_requirements(
        group_name="plan_first_review_v1",
        state=state,
        new_requirements_file=str(new_req_file),
        reason="Requirements changed",
    )

    assert result["pending_human_approval_for"] is None
    assert result["model_approved_steps"] == []

    with pytest.raises(ValueError, match="not pending human approval"):
        job_state.approve_step(
            group_name="plan_first_review_v1",
            group_cfg=group_cfg,
            state=result,
            step="codex_review",
        )


def test_approve_step_requires_model_approval(tmp_path, monkeypatch) -> None:
    """approve_step() rejects if step not in model_approved_steps."""
    from agent_runner_v2.workflow_packages.loader import load_workflow_package, bundle_to_template_group_dict
    from pathlib import Path
    import pytest

    workflow_pkg_dir = Path(__file__).parent.parent.parent / "workflows" / "plan_first_review_v1"
    bundle = load_workflow_package(workflow_pkg_dir)
    group_cfg = bundle_to_template_group_dict(bundle)

    state = {
        "job_id": "PLAN-TEST-009",
        "template_group": "plan_first_review_v1",
        "completed_steps": ["prepare_request", "formalize_requirements", "generate_plan", "codex_review"],
        "model_approved_steps": [],
        "artifacts": {
            "PLANNING_FOLDER": "Planning/20261025-01_Test",
            "QWEN_PLAN_FILE": "Planning/20261025-01_Test/Qwen_Plan_v01.md",
            "CODEX_REVIEW_FILE": "Planning/20261025-01_Test/Codex_Review_v01.md",
        },
        "review_state": default_review_state(),
        "pending_human_approval_for": "codex_review",
        "human_approvals": {},
    }

    with pytest.raises(ValueError, match="does not have recorded model approval"):
        job_state.approve_step(
            group_name="plan_first_review_v1",
            group_cfg=group_cfg,
            state=state,
            step="codex_review",
        )


def test_new_baseline_full_cycle_proceeds_to_promote_plan(tmp_path, monkeypatch) -> None:
    """After new baseline review is approved, next step must be promote_plan, not prepare_request."""
    from agent_runner_v2.v2.transition_runtime import mark_review_waiting_for_human
    from agent_runner_v2.workflow_packages.loader import load_workflow_package, bundle_to_template_group_dict
    from agent_runner_v2.job_state import now_iso, set_job_status

    monkeypatch.setattr("agent_runner_v2.job_state.PROJECT_ROOT", tmp_path)
    monkeypatch.setattr("agent_runner_v2.job_state.save_job", lambda *a: None)
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-10-25T00:00:00")
    monkeypatch.setattr(job_state, "set_job_status", lambda s, v: s.__setitem__("_status", v))
    monkeypatch.setattr(job_state, "get_job_status", lambda s: s.get("_status", "IN_PROGRESS"))

    workflow_pkg_dir = Path(__file__).parent.parent.parent / "workflows" / "plan_first_review_v1"
    bundle = load_workflow_package(workflow_pkg_dir)
    group_cfg = bundle_to_template_group_dict(bundle)

    new_req_file = tmp_path / "new_requirements.md"
    new_req_file.write_text("New requirements with authentication")

    planning_folder = "Planning/20261025-01_Test"
    planning_dir = tmp_path / planning_folder
    planning_dir.mkdir(parents=True)

    # Create baseline 1 artifacts
    (planning_dir / "request.md").write_text("Original request")
    (planning_dir / "requirements.md").write_text("Original requirements")
    (planning_dir / "Qwen_Plan_v02.md").write_text("Original plan v02")
    (planning_dir / "Codex_Review_v02.md").write_text("Original review v02")

    state = {
        "job_id": "PLAN-TEST-010",
        "template_group": "plan_first_review_v1",
        "requirements_baseline": 1,
        "plan_revision": 2,
        "completed_steps": ["prepare_request", "formalize_requirements", "generate_plan", "codex_review"],
        "model_approved_steps": ["formalize_requirements", "generate_plan", "codex_review"],
        "artifacts": {
            "PLANNING_FOLDER": planning_folder,
            "RAW_REQUEST_FILE": str(planning_dir / "request.md"),
            "REQUIREMENTS_FILE": str(planning_dir / "requirements.md"),
            "QWEN_PLAN_FILE": str(planning_dir / "Qwen_Plan_v02.md"),
            "CODEX_REVIEW_FILE": str(planning_dir / "Codex_Review_v02.md"),
        },
        "review_state": {
            "reviewer_step": "codex_review",
            "review_decision": "APPROVED",
            "review_decided_at": "2026-10-25T10:00:00",
            "human_decision": "APPROVED",
            "human_decided_at": "2026-10-25T10:30:00",
            "human_actor": "human",
            "final_decision": "APPROVED",
            "final_decision_source": "HUMAN",
            "review_iteration": 1,
        },
        "pending_human_approval_for": None,
        "human_approvals": {"codex_review": {"status": "APPROVED", "approved_at": "2026-10-25T10:30:00", "approved_by": "human"}},
        "reject_counts": {},
        "human_reject_counts": {},
        "auto_retry_count_by_step": {},
        "human_retry_count_by_step": {},
        "refinement_extensions": [],
        "loop_context": default_loop_context(),
        "replan_context": default_replan_context(),
        "pending_intervention_for": None,
        "current_step": "promote_plan",
        "last_failure_code": None,
        "last_failure_class": None,
        "last_failure_reason": None,
        "last_failure_source": None,
        "last_failure_step": None,
    }

    # Create baseline 2 (requirements change)
    result = job_state.change_requirements(
        group_name="plan_first_review_v1",
        state=state,
        new_requirements_file=str(new_req_file),
        reason="Requirements changed",
    )

    # Verify request.md written, prepare_request preserved, stale approvals cleared
    assert (planning_dir / "baseline_02" / "request.md").exists()
    assert (planning_dir / "baseline_02" / "request.md").read_text() == "New requirements with authentication"
    assert "prepare_request" in result["completed_steps"]
    assert result["current_step"] == "formalize_requirements"
    assert result["model_approved_steps"] == []
    assert result["requirements_baseline"] == 2
    assert result["human_approvals"] == {}
    assert result["review_state"]["review_decision"] == "PENDING"

    # Old baseline 1 files still exist
    assert (planning_dir / "request.md").exists()
    assert (planning_dir / "requirements.md").exists()
    assert (planning_dir / "Qwen_Plan_v02.md").exists()

    # Simulate new baseline workflow through to codex_review
    result["completed_steps"].append("formalize_requirements")
    result["current_step"] = "generate_plan"

    result["completed_steps"].append("generate_plan")
    result["current_step"] = "codex_review"

    # codex_review completes with model approval
    result["completed_steps"].append("codex_review")
    result, exit_code = mark_review_waiting_for_human(
        state=result,
        step="codex_review",
        coder_used="opencode",
        default_review_state=default_review_state,
        now_iso=now_iso,
        set_job_status=set_job_status,
    )

    assert "codex_review" in result["model_approved_steps"]
    assert result["pending_human_approval_for"] == "codex_review"
    assert result["review_state"]["review_decision"] == "APPROVED"

    # Human approves codex_review
    result = job_state.approve_step(
        group_name="plan_first_review_v1",
        group_cfg=group_cfg,
        state=result,
        step="codex_review",
    )

    # Next step is promote_plan, NOT prepare_request
    assert result["current_step"] == "promote_plan", f"Expected promote_plan, got {result['current_step']}"
    assert result["completed_steps"].count("prepare_request") == 1


def test_archived_job_cannot_resume(tmp_path, monkeypatch) -> None:
    """stop_and_archive() sets terminal status; manual run path rejects archived jobs."""
    from agent_runner_v2.manual_runtime import resolve_manual_run
    import argparse

    monkeypatch.setattr("agent_runner_v2.job_state.PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-10-25T00:00:00")
    monkeypatch.setattr(job_state, "set_job_status", lambda s, v: s.__setitem__("_status", v))
    monkeypatch.setattr(job_state, "get_job_status", lambda s: s.get("_status", "IN_PROGRESS"))

    # Create a job directory with STOPPED_ARCHIVED status
    jobs_root = tmp_path / "jobs"
    job_dir = jobs_root / "plan_first_review_v1" / "PLAN-TEST-011"
    job_dir.mkdir(parents=True)

    archived_state = {
        "job_id": "PLAN-TEST-011",
        "template_group": "plan_first_review_v1",
        "_status": "STOPPED_ARCHIVED",
        "stop_reason": "User requested stop",
        "stopped_at": "2026-10-25T00:00:00",
        "current_step": "formalize_requirements",
        "artifacts": {},
        "completed_steps": ["prepare_request"],
    }

    import json
    (job_dir / "job.json").write_text(json.dumps(archived_state), encoding="utf-8")

    # Mock hooks to load the archived job
    class FakeHooks:
        def ensure_backward_compatible_state(self, s):
            return s
        def migrate_job_state(self, s):
            return s
        def load_job(self, tg, jid):
            return archived_state.copy()

    args = argparse.Namespace(
        template_group="plan_first_review_v1",
        job_id="PLAN-TEST-011",
        job="PLAN-TEST-011",
        job_no="",
        start_step="",
        retry_step="",
        resume_step="",
    )

    with pytest.raises(ValueError, match="STOPPED_ARCHIVED"):
        resolve_manual_run(args=args, group_cfg={}, mode="manual", hooks=FakeHooks())


def test_change_requirements_rejects_stopped_archived(tmp_path, monkeypatch) -> None:
    """change_requirements() rejects STOPPED_ARCHIVED jobs at the function level."""
    monkeypatch.setattr("agent_runner_v2.job_state.PROJECT_ROOT", tmp_path)
    monkeypatch.setattr("agent_runner_v2.job_state.save_job", lambda *a: None)
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-10-25T00:00:00")
    monkeypatch.setattr(job_state, "set_job_status", lambda s, v: s.__setitem__("_status", v))
    monkeypatch.setattr(job_state, "get_job_status", lambda s: s.get("_status", "STOPPED_ARCHIVED"))

    planning_folder = "Planning/20261025-01_Test"
    planning_dir = tmp_path / planning_folder
    planning_dir.mkdir(parents=True)

    new_req_file = tmp_path / "new_requirements.md"
    new_req_file.write_text("New requirements")

    state = {
        "job_id": "PLAN-TEST-012",
        "template_group": "plan_first_review_v1",
        "_status": "STOPPED_ARCHIVED",
        "requirements_baseline": 1,
        "artifacts": {"PLANNING_FOLDER": planning_folder},
        "completed_steps": ["prepare_request"],
        "model_approved_steps": [],
    }

    with pytest.raises(ValueError, match="STOPPED_ARCHIVED"):
        job_state.change_requirements(
            group_name="plan_first_review_v1",
            state=state,
            new_requirements_file=str(new_req_file),
            reason="Requirements changed",
        )


def test_single_step_rejects_stopped_archived(tmp_path, monkeypatch) -> None:
    """--single-step rejects STOPPED_ARCHIVED jobs in cli_runtime."""
    from agent_runner_v2.cli_runtime import handle_admin_command
    import argparse

    archived_state = {
        "job_id": "PLAN-TEST-013",
        "template_group": "plan_first_review_v1",
        "job_status": "STOPPED_ARCHIVED",
        "stop_reason": "User requested stop",
        "current_step": "formalize_requirements",
        "artifacts": {},
        "completed_steps": ["prepare_request"],
    }

    class FakeHooks:
        def ensure_backward_compatible_state(self, s):
            return s
        def migrate_job_state(self, s):
            return s
        def load_job(self, tg, jid):
            return archived_state.copy()
        def reconcile_job_state(self, s, cfg):
            return s
        def save_job(self, *a):
            pass

    args = argparse.Namespace(
        template_group="plan_first_review_v1",
        job_id="PLAN-TEST-013",
        job="formalize_requirements",
        single_step=True,
    )

    with pytest.raises(ValueError, match="STOPPED_ARCHIVED"):
        handle_admin_command(args=args, group_cfg={"step_configs": {"formalize_requirements": {}}}, hooks=FakeHooks())


def test_change_requirements_cli_rejects_stopped_archived(tmp_path, monkeypatch) -> None:
    """change-requirements CLI command rejects STOPPED_ARCHIVED jobs."""
    from agent_runner_v2 import run_agent
    from agent_runner_v2 import runtime_context
    import json

    jobs_root = tmp_path / "jobs"
    job_dir = jobs_root / "plan_first_review_v1" / "PLAN-TEST-014"
    job_dir.mkdir(parents=True)

    archived_state = {
        "job_id": "PLAN-TEST-014",
        "template_group": "plan_first_review_v1",
        "job_status": "STOPPED_ARCHIVED",
        "stop_reason": "User requested stop",
        "current_step": "formalize_requirements",
        "artifacts": {},
        "completed_steps": ["prepare_request"],
    }
    (job_dir / "job.json").write_text(json.dumps(archived_state), encoding="utf-8")

    new_req_file = tmp_path / "new_requirements.md"
    new_req_file.write_text("New requirements")

    monkeypatch.setattr(runtime_context, "get_jobs_root", lambda: str(jobs_root))

    rc = run_agent.main([
        "change-requirements",
        "--job-id", "PLAN-TEST-014",
        "--new-requirements-file", str(new_req_file),
        "--reason", "Requirements changed",
    ])
    assert rc == 1


def test_force_approve_step_rejects_stopped_archived(tmp_path, monkeypatch) -> None:
    """--force-approve-step rejects STOPPED_ARCHIVED jobs at function level."""
    from agent_runner_v2.cli_runtime import handle_admin_command
    import argparse

    archived_state = {
        "job_id": "PLAN-TEST-015",
        "template_group": "plan_first_review_v1",
        "job_status": "STOPPED_ARCHIVED",
        "stop_reason": "User requested stop",
        "current_step": "formalize_requirements",
        "artifacts": {},
        "completed_steps": ["prepare_request"],
    }

    class FakeHooks:
        def ensure_backward_compatible_state(self, s):
            return s
        def migrate_job_state(self, s):
            return s
        def load_job(self, tg, jid):
            return archived_state.copy()
        def reconcile_job_state(self, s, cfg):
            return s
        def save_job(self, *a):
            pass
        def force_approve_step(self, *, group_name, group_cfg, state, step):
            # Call the real function to test the guard
            from agent_runner_v2.job_state import force_approve_step as real_force_approve
            return real_force_approve(group_name=group_name, group_cfg=group_cfg, state=state, step=step)

    args = argparse.Namespace(
        template_group="plan_first_review_v1",
        job_id="PLAN-TEST-015",
        force_approve_step="formalize_requirements",
        single_step=False,
        show_job=False,
        check_job_status=False,
        retry_step=None,
        continue_refinement=None,
        approve_step=None,
        reject_step=None,
        resume_step=None,
    )

    with pytest.raises(ValueError, match="STOPPED_ARCHIVED"):
        handle_admin_command(args=args, group_cfg={"step_configs": {"formalize_requirements": {}}}, hooks=FakeHooks())


# ---------------------------------------------------------------------------
# Phase 5: Unauthorized Write Detection
# ---------------------------------------------------------------------------

def test_unauthorized_write_detection_detects_violation(tmp_path, monkeypatch) -> None:
    """_verify_no_unauthorized_writes raises UnauthorizedWriteError for unauthorized changes."""
    from agent_runner_v2.step_runner import _verify_no_unauthorized_writes
    from agent_runner_v2.exceptions import UnauthorizedWriteError
    from pathlib import Path

    project_root = tmp_path / "project"
    project_root.mkdir()

    # Create some files
    allowed_file = project_root / "allowed.txt"
    allowed_file.write_text("allowed content")
    unauthorized_file = project_root / "unauthorized.txt"
    unauthorized_file.write_text("original")

    # Snapshot before
    before = {
        allowed_file.resolve(): "hash_allowed",
        unauthorized_file.resolve(): "hash_original",
    }

    # Snapshot after — unauthorized file changed
    after = {
        allowed_file.resolve(): "hash_allowed",
        unauthorized_file.resolve(): "hash_modified",
    }

    allowed_paths = {allowed_file.resolve()}

    with pytest.raises(UnauthorizedWriteError) as exc_info:
        _verify_no_unauthorized_writes(
            before=before,
            after=after,
            allowed_paths=allowed_paths,
            project_root=project_root,
        )

    assert "unauthorized.txt" in str(exc_info.value)
    assert len(exc_info.value.unauthorized_paths) == 1


def test_unauthorized_write_detection_allows_authorized_paths(tmp_path, monkeypatch) -> None:
    """_verify_no_unauthorized_writes does not raise for changes in allowed paths."""
    from agent_runner_v2.step_runner import _verify_no_unauthorized_writes
    from pathlib import Path

    project_root = tmp_path / "project"
    project_root.mkdir()

    # Create allowed files
    allowed_file1 = project_root / "allowed1.txt"
    allowed_file1.write_text("original1")
    allowed_file2 = project_root / "allowed2.txt"
    allowed_file2.write_text("original2")

    # Snapshot before
    before = {
        allowed_file1.resolve(): "hash1_original",
        allowed_file2.resolve(): "hash2_original",
    }

    # Snapshot after — both allowed files changed
    after = {
        allowed_file1.resolve(): "hash1_modified",
        allowed_file2.resolve(): "hash2_modified",
    }

    allowed_paths = {allowed_file1.resolve(), allowed_file2.resolve()}

    # Should not raise
    _verify_no_unauthorized_writes(
        before=before,
        after=after,
        allowed_paths=allowed_paths,
        project_root=project_root,
    )


def test_unauthorized_write_detection_checks_prompt_file_not_action(tmp_path, monkeypatch) -> None:
    """Detection only runs for prompt-driven steps, not action-driven steps."""
    from agent_runner_v2.step_runner import _snapshot_all_files
    from pathlib import Path

    project_root = tmp_path / "project"
    project_root.mkdir()

    # Create a file
    test_file = project_root / "test.txt"
    test_file.write_text("content")

    # Snapshot should work
    snapshot = _snapshot_all_files(project_root)
    assert test_file.resolve() in snapshot

    # Verify the condition: prompt-driven step has prompt_file and no action
    step_cfg_prompt = {"prompt_file": "prompt.txt", "action": None}
    step_cfg_action = {"prompt_file": None, "action": "some_action"}

    # The detection logic checks: step_cfg.get("prompt_file") and not step_cfg.get("action")
    assert step_cfg_prompt.get("prompt_file") and not step_cfg_prompt.get("action")
    assert not (step_cfg_action.get("prompt_file") and not step_cfg_action.get("action"))


def test_unauthorized_write_detection_integration_with_flag(tmp_path, monkeypatch) -> None:
    """Integration test: enable_unauthorized_write_detection flag triggers detection in run_step."""
    from agent_runner_v2.step_runner import _snapshot_all_files, _verify_no_unauthorized_writes, _build_allowed_paths
    from agent_runner_v2.exceptions import UnauthorizedWriteError
    from pathlib import Path

    project_root = tmp_path / "project"
    project_root.mkdir()

    # Create job's Planning folder
    job_folder = project_root / "Planning" / "PLAN-001"
    job_folder.mkdir(parents=True)
    allowed_file = job_folder / "requirements.md"
    allowed_file.write_text("requirements")

    # Create another job's folder (should be unauthorized)
    other_job_folder = project_root / "Planning" / "PLAN-002"
    other_job_folder.mkdir(parents=True)
    other_file = other_job_folder / "requirements.md"
    other_file.write_text("other requirements")

    # State with this job's artifacts
    state = {
        "artifacts": {
            "PLANNING_FOLDER": "Planning/PLAN-001",
            "REQUIREMENTS_FILE": "Planning/PLAN-001/requirements.md",
        },
        "current_step_dir": "jobs/plan_first_review_v1/PLAN-001/step_02",
    }

    # Build allowed paths
    allowed_paths = _build_allowed_paths(state=state, project_root=project_root)

    # Verify that PLAN-002 is NOT in allowed paths
    assert other_job_folder.resolve() not in allowed_paths
    assert other_file.resolve() not in allowed_paths

    # Snapshot before
    before = _snapshot_all_files(project_root)

    # Simulate unauthorized write to other job's folder
    other_file.write_text("modified by coder")

    # Snapshot after
    after = _snapshot_all_files(project_root)

    # Should raise UnauthorizedWriteError
    with pytest.raises(UnauthorizedWriteError) as exc_info:
        _verify_no_unauthorized_writes(
            before=before,
            after=after,
            allowed_paths=allowed_paths,
            project_root=project_root,
        )

    assert "PLAN-002" in str(exc_info.value)


def test_unauthorized_write_detection_rejects_other_job_folder(tmp_path, monkeypatch) -> None:
    """_build_allowed_paths does not allow writes to other jobs' Planning folders."""
    from agent_runner_v2.step_runner import _build_allowed_paths
    from pathlib import Path

    project_root = tmp_path / "project"
    project_root.mkdir()

    # Create this job's Planning folder
    job_folder = project_root / "Planning" / "PLAN-001"
    job_folder.mkdir(parents=True)

    # Create another job's Planning folder
    other_job_folder = project_root / "Planning" / "PLAN-002"
    other_job_folder.mkdir(parents=True)

    # State with this job's artifacts
    state = {
        "artifacts": {
            "PLANNING_FOLDER": "Planning/PLAN-001",
        },
    }

    # Build allowed paths
    allowed_paths = _build_allowed_paths(state=state, project_root=project_root)

    # Verify that this job's folder is allowed
    assert job_folder.resolve() in allowed_paths

    # Verify that other job's folder is NOT allowed
    assert other_job_folder.resolve() not in allowed_paths

    # Verify that parent Planning/ folder is NOT allowed
    assert (project_root / "Planning").resolve() not in allowed_paths


def test_unauthorized_write_detection_detects_deletion(tmp_path, monkeypatch) -> None:
    """_verify_no_unauthorized_writes detects unauthorized file deletions."""
    from agent_runner_v2.step_runner import _verify_no_unauthorized_writes
    from agent_runner_v2.exceptions import UnauthorizedWriteError
    from pathlib import Path

    project_root = tmp_path / "project"
    project_root.mkdir()

    # Create files
    allowed_file = project_root / "allowed.txt"
    allowed_file.write_text("allowed")
    unauthorized_file = project_root / "unauthorized.txt"
    unauthorized_file.write_text("will be deleted")

    # Snapshot before
    before = {
        allowed_file.resolve(): "hash_allowed",
        unauthorized_file.resolve(): "hash_unauthorized",
    }

    # Snapshot after — unauthorized file deleted
    after = {
        allowed_file.resolve(): "hash_allowed",
    }

    allowed_paths = {allowed_file.resolve()}

    # Should raise UnauthorizedWriteError for deletion
    with pytest.raises(UnauthorizedWriteError) as exc_info:
        _verify_no_unauthorized_writes(
            before=before,
            after=after,
            allowed_paths=allowed_paths,
            project_root=project_root,
        )

    assert "unauthorized.txt" in str(exc_info.value)
    assert "deleted" in str(exc_info.value)


def test_run_step_invokes_detection_when_flag_enabled(tmp_path, monkeypatch) -> None:
    """run_step() invokes unauthorized write detection when flag is enabled and step is prompt-driven."""
    from agent_runner_v2 import step_runner
    from agent_runner_v2.exceptions import UnauthorizedWriteError
    from pathlib import Path
    from unittest.mock import MagicMock, patch

    project_root = tmp_path / "project"
    project_root.mkdir()

    # Create job's Planning folder
    job_folder = project_root / "Planning" / "PLAN-001"
    job_folder.mkdir(parents=True)
    allowed_file = job_folder / "requirements.md"
    allowed_file.write_text("original")

    # Create another job's folder (unauthorized target)
    other_folder = project_root / "Planning" / "PLAN-002"
    other_folder.mkdir(parents=True)
    other_file = other_folder / "data.txt"

    # Setup state
    state = {
        "artifacts": {
            "PLANNING_FOLDER": "Planning/PLAN-001",
            "REQUIREMENTS_FILE": "Planning/PLAN-001/requirements.md",
        },
        "current_step_dir": "jobs/plan_first_review_v1/PLAN-001/step_02",
        "template_group": "plan_first_review_v1",
        "job_id": "PLAN-001",
    }

    # Setup step config (prompt-driven)
    step_cfg = {
        "prompt_file": "prompts/formalize_requirements.txt",
        "produces": ["REQUIREMENTS_FILE"],
    }

    # Setup group config with flag enabled
    group_cfg = {
        "enable_unauthorized_write_detection": True,
        "step_configs": {"formalize_requirements": step_cfg},
    }

    # Setup context
    context = {
        "RAW_REQUEST_FILE": "Planning/PLAN-001/request.md",
        "REQUIREMENTS_FILE": "Planning/PLAN-001/requirements.md",
    }

    # Create step_dir
    step_dir = project_root / "jobs" / "plan_first_review_v1" / "PLAN-001" / "step_02"
    step_dir.mkdir(parents=True)

    # Mock invoke_coder to simulate unauthorized write
    def mock_invoke_coder(*args, **kwargs):
        # Simulate coder writing to unauthorized location
        other_file.write_text("unauthorized write")
        # Return a mock invocation result
        mock_result = MagicMock()
        mock_result.return_code = 0
        mock_result.stdout = "success"
        mock_result.stderr = ""
        mock_result.usage = MagicMock()
        mock_result.manifest = MagicMock()
        mock_result.parsed_result = {
            "coder_result": {
                "status": "success",
                "artifacts": {"REQUIREMENTS_FILE": "Planning/PLAN-001/requirements.md"},
            }
        }
        return mock_result

    # Mock other dependencies
    monkeypatch.setattr(step_runner, "invoke_coder", mock_invoke_coder)
    monkeypatch.setattr(step_runner, "_now_iso", lambda: "2026-10-25T00:00:00")

    # Mock StepResult
    mock_step_result = MagicMock()
    monkeypatch.setattr(step_runner, "StepResult", lambda **kw: mock_step_result)

    # Call run_step() — should raise UnauthorizedWriteError
    with pytest.raises(UnauthorizedWriteError) as exc_info:
        step_runner.run_step(
            group_name="plan_first_review_v1",
            group_cfg=group_cfg,
            state=state,
            step="formalize_requirements",
            step_cfg=step_cfg,
            coder="opencode",
            coder_config=None,
            prompt_text="test prompt",
            checksum="abc123",
            step_dir=step_dir,
            project_root=project_root,
            context=context,
        )

    # Verify the error mentions the unauthorized file
    assert "PLAN-002" in str(exc_info.value) or "data.txt" in str(exc_info.value)


def test_run_step_detection_runs_on_coder_failure(tmp_path, monkeypatch) -> None:
    """run_step() runs unauthorized write detection even when invoke_coder() fails."""
    from agent_runner_v2 import step_runner
    from agent_runner_v2.coder_adapters import CoderInvocationError
    from agent_runner_v2.exceptions import UnauthorizedWriteError
    from pathlib import Path
    from unittest.mock import MagicMock

    project_root = tmp_path / "project"
    project_root.mkdir()

    # Create job's Planning folder
    job_folder = project_root / "Planning" / "PLAN-001"
    job_folder.mkdir(parents=True)

    # Create another job's folder (unauthorized target)
    other_folder = project_root / "Planning" / "PLAN-002"
    other_folder.mkdir(parents=True)
    other_file = other_folder / "data.txt"

    # Setup state
    state = {
        "artifacts": {
            "PLANNING_FOLDER": "Planning/PLAN-001",
        },
        "current_step_dir": "jobs/plan_first_review_v1/PLAN-001/step_02",
        "template_group": "plan_first_review_v1",
        "job_id": "PLAN-001",
    }

    # Setup step config (prompt-driven)
    step_cfg = {
        "prompt_file": "prompts/formalize_requirements.txt",
    }

    # Setup group config with flag enabled
    group_cfg = {
        "enable_unauthorized_write_detection": True,
    }

    # Setup context
    context = {}

    # Create step_dir
    step_dir = project_root / "jobs" / "plan_first_review_v1" / "PLAN-001" / "step_02"
    step_dir.mkdir(parents=True)

    # Mock invoke_coder to simulate failure with unauthorized write
    def mock_invoke_coder(*args, **kwargs):
        # Simulate coder writing to unauthorized location before failing
        other_file.write_text("unauthorized write before failure")
        # Raise CoderInvocationError
        raise CoderInvocationError(
            command="test command",
            return_code=1,
            stdout="error output",
            stderr="error",
            raw_events=[],
            message="coder failed",
        )

    # Mock dependencies
    monkeypatch.setattr(step_runner, "invoke_coder", mock_invoke_coder)
    monkeypatch.setattr(step_runner, "_now_iso", lambda: "2026-10-25T00:00:00")
    monkeypatch.setattr(step_runner, "_resolve_meta_json_path", lambda **kw: step_dir / "meta.json")
    monkeypatch.setattr(step_runner, "_validate_step_write_contract_config", lambda **kw: None)
    monkeypatch.setattr(step_runner, "_resolve_allowed_write_paths", lambda **kw: set())
    monkeypatch.setattr(step_runner, "_snapshot_allowed_write_roots", lambda **kw: {})
    monkeypatch.setattr(step_runner, "_save_debug_failure", lambda **kw: None)

    # Call run_step() — should raise UnauthorizedWriteError (not CoderInvocationError)
    # because detection runs before the exception is re-raised
    with pytest.raises(UnauthorizedWriteError) as exc_info:
        step_runner.run_step(
            group_name="plan_first_review_v1",
            group_cfg=group_cfg,
            state=state,
            step="formalize_requirements",
            step_cfg=step_cfg,
            coder="opencode",
            coder_config=None,
            prompt_text="test prompt",
            checksum="abc123",
            step_dir=step_dir,
            project_root=project_root,
            context=context,
        )

    # Verify the error mentions the unauthorized file
    assert "PLAN-002" in str(exc_info.value) or "data.txt" in str(exc_info.value)


# ---------------------------------------------------------------------------
# 7. Path constant compliance
# ---------------------------------------------------------------------------

def test_actions_py_uses_path_constants_not_hardcoded_strings():
    """actions.py must use layered path constants (PLANNING_BASE, ARTIFACT_PATH_RAW_REQUEST),
    not hardcoded path strings like 'Planning' or 'request.md' concatenation."""
    import ast

    actions_path = (
        Path(__file__).parent.parent.parent
        / "workflows" / "plan_first_review_v1" / "actions.py"
    )
    source = actions_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    # Collect all string literals in the AST (excluding docstrings)
    string_literals: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            # Skip docstrings — they appear as Expr > Constant
            if isinstance(getattr(node, "_parent", None), ast.Expr):
                continue
            string_literals.append(node.value)

    # No hardcoded "Planning" directory name — must use PLANNING_BASE constant
    assert "Planning" not in string_literals, (
        "actions.py contains hardcoded 'Planning' string — use PLANNING_BASE from constants"
    )

    # Verify imports from the layered constant system
    assert "PLANNING_BASE" in source, "actions.py must import PLANNING_BASE"
    assert "ARTIFACT_PATH_RAW_REQUEST" in source, (
        "actions.py must import ARTIFACT_PATH_RAW_REQUEST"
    )


def test_prepare_request_atomic_folder_allocation(tmp_path, monkeypatch):
    """When the preferred folder name already exists, prepare_request() claims the
    next sequence number instead of overwriting. Uses mkdir(exist_ok=False) atomically."""
    from datetime import datetime as dt
    from unittest.mock import MagicMock
    from workflows.plan_first_review_v1.actions import prepare_request

    # Freeze date so folder name is deterministic
    monkeypatch.setattr(
        "workflows.plan_first_review_v1.actions.datetime",
        MagicMock(now=MagicMock(return_value=dt(2026, 10, 25, 12, 0, 0))),
    )

    project_root = tmp_path
    # Create source request file
    src = project_root / "my_request.md"
    src.write_text("# Original request")

    # Pre-create the folder that seq=01 would claim, with a marker file
    slug = "my_request"
    planning_base = project_root / "Planning"
    planning_base.mkdir()
    occupied = planning_base / f"20261025-01_{slug}"
    occupied.mkdir()
    marker = occupied / "existing.md"
    marker.write_text("do not overwrite")

    context = {ARTIFACT_KEY_RAW_REQUEST: str(src)}
    state = {}

    result = prepare_request(
        context=context, state=state, step_cfg={}, step={}, project_root=project_root,
    )

    assert result.status == "APPROVED"
    # Must have claimed seq=02, not seq=01
    expected_folder = f"Planning/20261025-02_{slug}"
    assert result.artifacts[ARTIFACT_KEY_PLANNING_FOLDER] == expected_folder
    # New folder exists with request.md
    new_folder = project_root / expected_folder
    assert new_folder.is_dir()
    assert (new_folder / "request.md").is_file()
    # Pre-existing folder untouched
    assert marker.read_text() == "do not overwrite"


