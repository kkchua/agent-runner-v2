"""Context extensions for sdlc_00_codebase_scaffold_v1 workflow.

Combined workflow: codebase sync + SDLC delivery scaffold generation.
Merges artifact keys and context paths from both sdlc_00_codebase_v1
and sdlc_00_delivery_scaffold_v1.
"""
from __future__ import annotations

from pathlib import Path, PurePath
from typing import Any

from agent_runner_v2.constants import SDLC_DELIVERY_BASE
from agent_runner_v2.runtime_context import (
    JOBS_ROOT,
    get_governance_runtime_root,
    get_platform_runtime_root,
    get_workspace_root,
    resolve_repo_or_runtime_path,
)
from agent_runner_v2.workflow_packages.extensions_base import WorkflowExtensions


class Sdlc00CodebaseScaffoldExtensions(WorkflowExtensions):
    """Workflow extension hooks for sdlc_00_codebase_scaffold_v1."""

    workflow_name = "sdlc_00_codebase_scaffold_v1"

    def register_artifact_keys(
        self,
        *,
        job_id: str = "{job_id}",
        mode: str = "{mode}",
    ) -> dict[str, str]:
        """Return artifact key to relative-path mappings.

        Combines codebase sync staging (docs/repo/codebase/) and
        scaffold staging (docs/system/.../sdlc/).
        """
        # -- Codebase staging roots --
        cb_run_root = f"docs/repo/codebase/runs/{job_id}"
        cb_current_root = "docs/repo/codebase/current"
        cb_history_root = f"docs/repo/codebase/history/{job_id}"

        # -- Scaffold staging roots --
        scf_run_root = f"docs/system/00_governance/platform/agent_runner/sdlc/runs/{job_id}"
        scf_current_root = "docs/system/00_governance/platform/agent_runner/sdlc/current"
        scf_history_root = f"docs/system/00_governance/platform/agent_runner/sdlc/history/{job_id}"

        return {
            # =================================================================
            # Codebase Sync artifacts (staged under docs/repo/codebase/)
            # =================================================================
            "CODEBASE_CHANGE_IMPACT": f"{cb_run_root}/04_changes/{job_id}-reconcile.md",
            "CODEBASE_INVENTORY": f"{cb_run_root}/01_inventory/codebase_inventory.md",
            "SYNC_LOG": f"{cb_run_root}/sync_logs/SYNC-{job_id}.md",
            "REVIEW_FILE_SUGGESTED": f"{cb_run_root}/sync_logs/{job_id}-review.md",
            "VALIDATION_FILE": f"{cb_run_root}/04_changes/{job_id}-reconcile-validation.md",
            "CODEBASE_PUBLISH_MANIFEST": f"{cb_current_root}/codebase_manifest.json",
            "CODEBASE_PUBLISH_MANIFEST_HISTORY": f"{cb_history_root}/codebase_manifest.json",

            # =================================================================
            # SDLC Scaffold artifacts (staged under docs/system/.../sdlc/)
            # =================================================================
            # -- Master Templates (01_templates/) --
            "SDLC_TEMPLATE_REGISTRY": f"{scf_run_root}/01_templates/template_registry.md",
            "SDLC_WORKFLOW_SOP": f"{scf_run_root}/01_templates/WORKFLOW_SOP_v1.md",
            "SDLC_TEMPLATE_DRAFT_INIT": f"{scf_run_root}/01_templates/01_DRAFT_INIT_template.md",
            "SDLC_TEMPLATE_INIT": f"{scf_run_root}/01_templates/02_INIT_template.md",
            "SDLC_TEMPLATE_REQ": f"{scf_run_root}/01_templates/03_REQ_template.md",
            "SDLC_TEMPLATE_PLAN": f"{scf_run_root}/01_templates/04_PLAN_template.md",
            "SDLC_TEMPLATE_BACKLOG": f"{scf_run_root}/01_templates/05_BACKLOG_template.md",
            "SDLC_TEMPLATE_TASK": f"{scf_run_root}/01_templates/06_TASK_template.md",
            "SDLC_TEMPLATE_IMPL": f"{scf_run_root}/01_templates/07_IMPL_template.md",
            "SDLC_TEMPLATE_VALID": f"{scf_run_root}/01_templates/08_VALID_template.md",
            "SDLC_TEMPLATE_REV": f"{scf_run_root}/01_templates/09_REV_template.md",
            "SDLC_TEMPLATE_MEM": f"{scf_run_root}/01_templates/10_MEM_template.md",
            "SDLC_TEMPLATE_CLOSE": f"{scf_run_root}/01_templates/11_CLOSE_template.md",
            # -- Agent Contracts (02_agents/) --
            "SDLC_AGENTS_INDEX": f"{scf_run_root}/02_agents/AGENTS.md",
            "SDLC_AGENT_PLANNER": f"{scf_run_root}/02_agents/AGENT-planner.md",
            "SDLC_AGENT_TASK_DECOMPOSER": f"{scf_run_root}/02_agents/AGENT-task-decomposer.md",
            "SDLC_AGENT_IMPL_PLANNER": f"{scf_run_root}/02_agents/AGENT-implementation-planner.md",
            "SDLC_AGENT_EXECUTOR": f"{scf_run_root}/02_agents/AGENT-executor.md",
            "SDLC_AGENT_REVIEWER": f"{scf_run_root}/02_agents/AGENT-reviewer.md",
            "SDLC_AGENT_MEMORY_MANAGER": f"{scf_run_root}/02_agents/AGENT-memory-manager.md",
            "SDLC_DELIVERY_STATUS_RULES": f"{scf_run_root}/02_agents/DELIVERY_STATUS_RULES_v1.md",
            # -- Scaffold Review (reuses REVIEW_FILE_SUGGESTED from codebase phase) --
            # -- Scaffold Publish targets --
            "SDLC_CURRENT_ROOT": scf_current_root,
            "SDLC_HISTORY_ROOT": scf_history_root,
            "SDLC_SCAFFOLD_PUBLISH_MANIFEST": f"{scf_current_root}/sdlc_scaffold_manifest.json",
            "SDLC_SCAFFOLD_PUBLISH_MANIFEST_HISTORY": f"{scf_history_root}/sdlc_scaffold_manifest.json",
            # -- SDLC Delivery Artifact Keys (shared across all downstream workflows) --
            "DRAFT_INIT_FILE": f"{SDLC_DELIVERY_BASE}/00_draft_initiatives/DRAFT-INIT.md",
            "PRE_INIT_FILE": f"{SDLC_DELIVERY_BASE}/00_draft_initiatives/PRE-INIT.md",
            "INIT_FILE": f"{SDLC_DELIVERY_BASE}/00_initiatives/INIT.md",
            "REQ_FILE": f"{SDLC_DELIVERY_BASE}/10_requirements/REQ.md",
            "PLAN_FILE": f"{SDLC_DELIVERY_BASE}/20_plans/PLAN.md",
            "BACKLOG_FILE": f"{SDLC_DELIVERY_BASE}/30_backlogs/BACKLOG.md",
            "TASK_FILE": f"{SDLC_DELIVERY_BASE}/40_tasks/TASK.md",
            "WORK_ITEM": "",
            "IMPL_FILE": f"{SDLC_DELIVERY_BASE}/50_implementations/IMPL.md",
            "EXEC_FILE": f"{SDLC_DELIVERY_BASE}/60_executions/EXEC.md",
            "VAL_FILE": f"{SDLC_DELIVERY_BASE}/70_validations/VAL.md",
            "MEM_FILE": f"{SDLC_DELIVERY_BASE}/80_reviews/MEM.md",
            "CLOSE_FILE": f"{SDLC_DELIVERY_BASE}/80_reviews/CLOSE.md",
            "AUDIT_FILE_SUGGESTED": f"{SDLC_DELIVERY_BASE}/80_reviews/AUDIT.md",
            "CONTEXT_PACK_FILE": f"{SDLC_DELIVERY_BASE}/00_context_packs/CONTEXT.md",
        }

    def build_context_extensions(
        self,
        *,
        state: dict[str, Any],
        step: str,
        step_cfg: dict[str, Any],
        ctx: dict[str, str],
        project_root: Path | None = None,
    ) -> dict[str, str]:
        """Build context extensions for sdlc_00_codebase_scaffold_v1 workflow.

        Provides:
        - Layer 1 governance runtime root (global path)
        - Layer 2 platform runtime root (global path)
        - Codebase documentation roots (project-local)
        - SDLC scaffold roots (project-local)
        - Resolved artifact paths from register_artifact_keys()
        """
        del step_cfg, ctx
        result: dict[str, str] = {}

        # Layer 1 governance runtime root (global path)
        result["GOVERNANCE_RUNTIME_ROOT"] = str(get_governance_runtime_root())

        # Layer 2 platform runtime root (global path)
        result["PLATFORM_RUNTIME_ROOT"] = str(get_platform_runtime_root() / "agent_runner")

        # Resolve workspace and project root
        workspace_root = get_workspace_root()
        effective_root = Path(project_root or workspace_root or Path.cwd()).resolve()

        job_id = str(state.get("job_id") or "SDLC00CS").strip()

        # -- Codebase documentation roots (project-local) --
        result["CODEBASE_CURRENT_ROOT"] = str(
            effective_root / "docs" / "repo" / "codebase" / "current"
        )
        result["CODEBASE_HISTORY_ROOT"] = str(
            effective_root / "docs" / "repo" / "codebase" / "history" / job_id
        )

        # -- SDLC scaffold roots (project-local) --
        output_paths = self.register_artifact_keys(job_id=job_id)
        result["SDLC_CURRENT_ROOT"] = str(
            effective_root / output_paths["SDLC_CURRENT_ROOT"]
        )
        result["SDLC_HISTORY_ROOT"] = str(
            effective_root / output_paths["SDLC_HISTORY_ROOT"]
        )

        # -- SDLC reference paths --
        result["SDLC_L3_SPEC_PATH"] = str(
            effective_root / "masterplan" / "LAYER3_AI_DRIVEN_SDLC_SPECIFICATION.md"
        )
        result["SDLC_MASTER_TEMPLATE_ROOT"] = str(
            effective_root / "masterplan" / "delivery" / "00_templates"
        )
        result["SDLC_MASTER_AGENT_ROOT"] = str(
            effective_root / "masterplan" / "delivery" / "08_agents"
        )

        # -- Resolve artifact paths to absolute --
        for artifact_key, rel_path in output_paths.items():
            if not rel_path.endswith((".md", ".json")):
                continue
            resolved = resolve_repo_or_runtime_path(
                rel_path, project_root=effective_root, runtime_root=JOBS_ROOT
            )
            resolved_str = str(resolved)
            result[artifact_key] = resolved_str
            result[f"{artifact_key}_PATH"] = resolved_str
            pure = PurePath(resolved_str)
            result[f"{artifact_key}_METAJSON"] = str(
                pure.parent / f"{pure.stem}.meta.json"
            )

        return result

    def install_to_global(self, *, workspace_root, runner_home):
        """Copy SDLC scaffold to global runner home."""
        import shutil

        source = (
            Path(workspace_root)
            / "docs"
            / "system"
            / "00_governance"
            / "platform"
            / "agent_runner"
            / "sdlc"
            / "current"
        )
        dest = (
            Path(runner_home)
            / "bundles"
            / "core"
            / "current"
            / "platform"
            / "agent_runner"
            / "sdlc"
        )
        if not source.is_dir():
            return {"status": "SKIPPED", "reason": "SDLC scaffold not published yet"}
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(str(source), str(dest))
        count = sum(1 for _ in dest.rglob("*") if _.is_file())
        return {
            "status": "INSTALLED",
            "source": str(source),
            "destination": str(dest),
            "files_copied": count,
        }

    def sync_to_backend(self, *, workspace_root):
        """Sync via `ukbe-run-agent sync-workflows` CLI instead."""
        return {"status": "NO_OP"}
