"""Context extensions for 02_agent_runner_platform_v1."""
from __future__ import annotations

from pathlib import Path, PurePath
from typing import Any

from agent_runner_v2.constants import ARTIFACT_KEY_AUDIT, ARTIFACT_KEY_REVIEW
from agent_runner_v2.runtime_context import get_governance_runtime_root, get_platform_runtime_root, JOBS_ROOT, resolve_repo_or_runtime_path
from agent_runner_v2.workflow_packages.extensions_base import WorkflowExtensions


class AgentRunnerPlatformExtensions(WorkflowExtensions):
    """Workflow extension hooks for 02_agent_runner_platform_v1."""

    workflow_name = "02_agent_runner_platform_v1"

    def register_artifact_keys(
        self, *, job_id: str = "{job_id}", mode: str = "{mode}",
    ) -> dict[str, str]:
        """Return artifact key to relative-path mappings."""
        run_root = f"docs/system/00_governance/platform/agent_runner/runs/{job_id}"
        history_root = f"docs/system/00_governance/platform/agent_runner/history/{job_id}"
        current_root = "docs/system/00_governance/platform/agent_runner/current"
        return {
            "L2_PLATFORM_INDEX": f"{run_root}/README.md",
            "L2_RUNTIME_MODEL": f"{run_root}/RUNTIME_MODEL.md",
            "L2_BUNDLE_AUTHORING_CONTRACT": f"{run_root}/BUNDLE_AUTHORING_CONTRACT.md",
            "L2_SHARED_SERVICES": f"{run_root}/SHARED_SERVICES.md",
            "L2_METADATA_CONTRACT": f"{run_root}/METADATA_CONTRACT.md",
            "L2_VALIDATION_CONTRACT": f"{run_root}/VALIDATION_CONTRACT.md",
            "PLATFORM_CONTEXT_INVENTORY": f"{run_root}/{job_id}-platform-context-inventory.md",
            "REVIEW_FILE_SUGGESTED": f"{run_root}/{job_id}-platform-core-review.md",
            "PLATFORM_CORE_VALIDATION": f"{run_root}/{job_id}-platform-core-validation.md",
            "AUDIT_FILE_SUGGESTED": f"{run_root}/{job_id}-platform-core-audit.md",
            "PLATFORM_PUBLISH_MANIFEST": f"{current_root}/platform_set_manifest.json",
            "PLATFORM_PUBLISH_MANIFEST_HISTORY": f"{history_root}/platform_set_manifest.json",
            "PLATFORM_CURRENT_ROOT": current_root,
            "PLATFORM_HISTORY_ROOT": history_root,
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
        """Build context extensions for 02_agent_runner_platform_v1."""
        del step_cfg, ctx
        job_id = str(state.get("job_id") or "02AR").strip()
        root = Path(project_root or Path.cwd()).resolve()
        loop_ctx = state.get("loop_context") or {}
        loop_iteration = int(loop_ctx.get("loop_iteration", 0)) if loop_ctx.get("active") else 0
        iter_suffix = f"_iter{loop_iteration + 1}" if loop_iteration > 0 else ""
        output_paths = self.register_artifact_keys(job_id=job_id, mode=str(state.get("mode") or "default"))

        # Apply iteration suffix to loop-able artifacts
        if loop_iteration > 0:
            for key in ("REVIEW_FILE_SUGGESTED", "PLATFORM_CORE_VALIDATION", "AUDIT_FILE_SUGGESTED"):
                rel = output_paths[key]
                base, ext = rel.rsplit(".", 1)
                output_paths[key] = f"{base}{iter_suffix}.{ext}"

        extensions: dict[str, str] = {
            "MASTERPLAN_ARCHITECTURE_PATH": str(root / "masterplan" / "LAYER_ARCHITECTURE_MASTERPLAN.md"),
            "MASTERPLAN_PLATFORM_SPEC_PATH": str(root / "masterplan" / "LAYER2_PLATFORM_CORE_SPECIFICATION.md"),
            "GOVERNANCE_RUNTIME_ROOT": str(get_governance_runtime_root()),
            "PLATFORM_RUNTIME_ROOT": str(get_platform_runtime_root() / "agent_runner"),
            "PLATFORM_ACTIVE_ROOT": str(root / "docs" / "system" / "00_governance" / "platform" / "agent_runner" / "current"),
            "PLATFORM_HISTORY_ROOT": str(root / output_paths["PLATFORM_HISTORY_ROOT"]),
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

        extensions[ARTIFACT_KEY_REVIEW] = extensions["REVIEW_FILE_SUGGESTED"]
        extensions["REVIEW_FILE_PATH"] = extensions["REVIEW_FILE_SUGGESTED"]
        extensions["REVIEW_FILE_METAJSON"] = extensions["REVIEW_FILE_SUGGESTED_METAJSON"]

        extensions[ARTIFACT_KEY_AUDIT] = extensions["AUDIT_FILE_SUGGESTED"]
        extensions["AUDIT_FILE_PATH"] = extensions["AUDIT_FILE_SUGGESTED"]
        extensions["AUDIT_FILE_METAJSON"] = extensions["AUDIT_FILE_SUGGESTED_METAJSON"]

        return extensions

    def install_to_global(self, *, workspace_root, runner_home):
        """Copy L2 platform docs to global runner home."""
        import shutil
        source = workspace_root / "docs" / "system" / "00_governance" / "platform" / "agent_runner" / "current"
        dest = Path(runner_home) / "bundles" / "core" / "current" / "platform" / "agent_runner"
        if not source.is_dir():
            return {"status": "SKIPPED", "reason": "L2 platform docs not published yet"}
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(str(source), str(dest))
        count = sum(1 for _ in dest.rglob("*") if _.is_file())
        return {"status": "INSTALLED", "source": str(source), "destination": str(dest), "files_copied": count}

    def sync_to_backend(self, *, workspace_root):
        """Sync via `ukbe-run-agent sync-workflows` CLI instead."""
        return {"status": "NO_OP"}
