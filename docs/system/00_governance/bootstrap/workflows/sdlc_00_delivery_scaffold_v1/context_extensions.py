"""Context extensions for sdlc_00_delivery_scaffold_v1 workflow."""
from __future__ import annotations

from pathlib import Path, PurePath
from typing import Any

from agent_runner_v2.constants import SDLC_DELIVERY_BASE
from agent_runner_v2.runtime_context import get_governance_runtime_root, get_platform_runtime_root, JOBS_ROOT, resolve_repo_or_runtime_path
from agent_runner_v2.workflow_packages.extensions_base import WorkflowExtensions


class Sdlc00DeliveryScaffoldExtensions(WorkflowExtensions):
    """Workflow extension hooks for sdlc_00_delivery_scaffold_v1."""

    workflow_name = "sdlc_00_delivery_scaffold_v1"

    def register_artifact_keys(self, *, job_id: str = "{job_id}", mode: str = "{mode}") -> dict[str, str]:
        """Return artifact key to relative-path mappings.

        Paths follow the L2 platform staging pattern under sdlc/.
        """
        run_root = f"docs/system/00_governance/platform/agent_runner/sdlc/runs/{job_id}"
        current_root = "docs/system/00_governance/platform/agent_runner/sdlc/current"
        history_root = f"docs/system/00_governance/platform/agent_runner/sdlc/history/{job_id}"

        return {
            # -- Master Templates (01_templates/) --
            "SDLC_TEMPLATE_REGISTRY": f"{run_root}/01_templates/template_registry.md",
            "SDLC_WORKFLOW_SOP": f"{run_root}/01_templates/WORKFLOW_SOP_v1.md",
            "SDLC_TEMPLATE_DRAFT_INIT": f"{run_root}/01_templates/01_DRAFT_INIT_template.md",
            "SDLC_TEMPLATE_INIT": f"{run_root}/01_templates/02_INIT_template.md",
            "SDLC_TEMPLATE_REQ": f"{run_root}/01_templates/03_REQ_template.md",
            "SDLC_TEMPLATE_PLAN": f"{run_root}/01_templates/04_PLAN_template.md",
            "SDLC_TEMPLATE_BACKLOG": f"{run_root}/01_templates/05_BACKLOG_template.md",
            "SDLC_TEMPLATE_TASK": f"{run_root}/01_templates/06_TASK_template.md",
            "SDLC_TEMPLATE_IMPL": f"{run_root}/01_templates/07_IMPL_template.md",
            "SDLC_TEMPLATE_VALID": f"{run_root}/01_templates/08_VALID_template.md",
            "SDLC_TEMPLATE_REV": f"{run_root}/01_templates/09_REV_template.md",
            "SDLC_TEMPLATE_MEM": f"{run_root}/01_templates/10_MEM_template.md",
            "SDLC_TEMPLATE_CLOSE": f"{run_root}/01_templates/11_CLOSE_template.md",
            # -- Agent Contracts (02_agents/) --
            "SDLC_AGENTS_INDEX": f"{run_root}/02_agents/AGENTS.md",
            "SDLC_AGENT_PLANNER": f"{run_root}/02_agents/AGENT-planner.md",
            "SDLC_AGENT_TASK_DECOMPOSER": f"{run_root}/02_agents/AGENT-task-decomposer.md",
            "SDLC_AGENT_IMPL_PLANNER": f"{run_root}/02_agents/AGENT-implementation-planner.md",
            "SDLC_AGENT_EXECUTOR": f"{run_root}/02_agents/AGENT-executor.md",
            "SDLC_AGENT_REVIEWER": f"{run_root}/02_agents/AGENT-reviewer.md",
            "SDLC_AGENT_MEMORY_MANAGER": f"{run_root}/02_agents/AGENT-memory-manager.md",
            "SDLC_DELIVERY_STATUS_RULES": f"{run_root}/02_agents/DELIVERY_STATUS_RULES_v1.md",
            # -- Review --
            "REVIEW_FILE_SUGGESTED": f"{run_root}/{job_id}-sdlc-scaffold-review.md",
            # -- Publish targets --
            "SDLC_CURRENT_ROOT": current_root,
            "SDLC_HISTORY_ROOT": history_root,
            "SDLC_SCAFFOLD_PUBLISH_MANIFEST": f"{current_root}/sdlc_scaffold_manifest.json",
            "SDLC_SCAFFOLD_PUBLISH_MANIFEST_HISTORY": f"{history_root}/sdlc_scaffold_manifest.json",
            # -- SDLC Delivery Artifact Keys (shared across all downstream workflows) --
            # These keys are registered globally so create_job() accepts them as seed inputs.
            # Actual per-workflow path resolution happens in each workflow's context_extensions.py.
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
        """Build context extensions for sdlc_00_delivery_scaffold_v1."""
        del step_cfg, ctx
        job_id = str(state.get("job_id") or "SDLC00SCF").strip()
        root = Path(project_root or Path.cwd()).resolve()
        output_paths = self.register_artifact_keys(job_id=job_id, mode=str(state.get("mode") or "default"))

        extensions: dict[str, str] = {
            "GOVERNANCE_RUNTIME_ROOT": str(get_governance_runtime_root()),
            "PLATFORM_RUNTIME_ROOT": str(get_platform_runtime_root() / "agent_runner"),
            "SDLC_L3_SPEC_PATH": str(root / "masterplan" / "LAYER3_AI_DRIVEN_SDLC_SPECIFICATION.md"),
            "SDLC_MASTER_TEMPLATE_ROOT": str(root / "masterplan" / "delivery" / "00_templates"),
            "SDLC_MASTER_AGENT_ROOT": str(root / "masterplan" / "delivery" / "08_agents"),
            "SDLC_CURRENT_ROOT": str(root / output_paths["SDLC_CURRENT_ROOT"]),
            "SDLC_HISTORY_ROOT": str(root / output_paths["SDLC_HISTORY_ROOT"]),
        }

        for artifact_key, rel_path in output_paths.items():
            if not rel_path.endswith((".md", ".json")):
                continue
            resolved = resolve_repo_or_runtime_path(rel_path, project_root=root, runtime_root=JOBS_ROOT)
            resolved_str = str(resolved)
            extensions[artifact_key] = resolved_str
            extensions[f"{artifact_key}_PATH"] = resolved_str
            pure = PurePath(resolved_str)
            extensions[f"{artifact_key}_METAJSON"] = str(pure.parent / f"{pure.stem}.meta.json")

        return extensions

    def install_to_global(self, *, workspace_root, runner_home):
        """Copy SDLC scaffold to global runner home."""
        import shutil
        source = Path(workspace_root) / "docs" / "system" / "00_governance" / "platform" / "agent_runner" / "sdlc" / "current"
        dest = Path(runner_home) / "bundles" / "core" / "current" / "platform" / "agent_runner" / "sdlc"
        if not source.is_dir():
            return {"status": "SKIPPED", "reason": "SDLC scaffold not published yet"}
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(str(source), str(dest))
        count = sum(1 for _ in dest.rglob("*") if _.is_file())
        return {"status": "INSTALLED", "source": str(source), "destination": str(dest), "files_copied": count}

    def sync_to_backend(self, *, workspace_root):
        """Sync via `ukbe-run-agent sync-workflows` CLI instead."""
        return {"status": "NO_OP"}
