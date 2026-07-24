"""Context extensions for 01_governance_foundation_v1."""
from __future__ import annotations

from pathlib import Path, PurePath
from typing import Any

from agent_runner_v2.constants import ARTIFACT_KEY_AUDIT, ARTIFACT_KEY_REVIEW
from agent_runner_v2.runtime_context import JOBS_ROOT, get_workspace_root, resolve_repo_or_runtime_path
from agent_runner_v2.workflow_packages.extensions_base import WorkflowExtensions


class GovernanceFoundationExtensions(WorkflowExtensions):
    """Workflow extension hooks for 01_governance_foundation_v1."""

    workflow_name = "01_governance_foundation_v1"

    def register_artifact_keys(
        self, *, job_id: str = "{job_id}", mode: str = "{mode}",
    ) -> dict[str, str]:
        """Return artifact key to relative-path mappings."""
        run_root = f"docs/system/00_governance/foundation/runs/{job_id}"
        history_root = f"docs/system/00_governance/foundation/history/{job_id}"
        current_root = "docs/system/00_governance/foundation/current"
        return {
            "L1_FOUNDATION_INDEX": f"{run_root}/README.md",
            "L1_LAYER_MODEL": f"{run_root}/LAYER_MODEL.md",
            "L1_DOCUMENT_AUTHORITY": f"{run_root}/DOCUMENT_AUTHORITY.md",
            "L1_BUNDLE_TAXONOMY": f"{run_root}/BUNDLE_TAXONOMY.md",
            "L1_GOVERNANCE_LIFECYCLE": f"{run_root}/GOVERNANCE_LIFECYCLE.md",
            "L1_METADATA_STANDARD": f"{run_root}/METADATA_STANDARD.md",
            "GOVERNANCE_CONTEXT_INVENTORY": f"{run_root}/{job_id}-governance-context-inventory.md",
            "REVIEW_FILE_SUGGESTED": f"{run_root}/{job_id}-governance-foundation-review.md",
            "GOVERNANCE_FOUNDATION_VALIDATION": f"{run_root}/{job_id}-governance-foundation-validation.md",
            "AUDIT_FILE_SUGGESTED": f"{run_root}/{job_id}-governance-foundation-audit.md",
            "GOVERNANCE_PUBLISH_MANIFEST": f"{current_root}/governance_set_manifest.json",
            "GOVERNANCE_PUBLISH_MANIFEST_HISTORY": f"{history_root}/governance_set_manifest.json",
            "GOVERNANCE_CURRENT_ROOT": current_root,
            "GOVERNANCE_HISTORY_ROOT": history_root,
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
        """Build context extensions for 01_governance_foundation_v1."""
        del step_cfg, ctx
        job_id = str(state.get("job_id") or "00GF").strip()
        root = Path(project_root or get_workspace_root() or Path.cwd()).resolve()
        loop_ctx = state.get("loop_context") or {}
        loop_iteration = int(loop_ctx.get("loop_iteration", 0)) if loop_ctx.get("active") else 0
        iter_suffix = f"_iter{loop_iteration + 1}" if loop_iteration > 0 else ""
        output_paths = self.register_artifact_keys(job_id=job_id, mode=str(state.get("mode") or "default"))

        # Apply iteration suffix to loop-able artifacts
        if loop_iteration > 0:
            for key in ("REVIEW_FILE_SUGGESTED", "GOVERNANCE_FOUNDATION_VALIDATION", "AUDIT_FILE_SUGGESTED"):
                rel = output_paths[key]
                base, ext = rel.rsplit(".", 1)
                output_paths[key] = f"{base}{iter_suffix}.{ext}"

        extensions: dict[str, str] = {
            "MASTERPLAN_ARCHITECTURE_PATH": str(root / "masterplan" / "LAYER_ARCHITECTURE_MASTERPLAN.md"),
            "MASTERPLAN_WORKFLOW_SPEC_PATH": str(root / "masterplan" / "LAYER1_GOVERNANCE_SPECIFICATION.md"),
            "GOVERNANCE_ACTIVE_ROOT": str(root / "docs" / "system" / "00_governance" / "foundation" / "current"),
            "GOVERNANCE_HISTORY_ROOT": str(root / output_paths["GOVERNANCE_HISTORY_ROOT"]),
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
        """Copy L1 governance docs to global runner home."""
        import shutil
        source = workspace_root / "docs" / "system" / "00_governance" / "foundation" / "current"
        dest = Path(runner_home) / "bundles" / "core" / "current" / "foundation"
        if not source.is_dir():
            return {"status": "SKIPPED", "reason": "L1 governance not published yet"}
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(str(source), str(dest))
        count = sum(1 for _ in dest.rglob("*") if _.is_file())
        return {"status": "INSTALLED", "source": str(source), "destination": str(dest), "files_copied": count}

    def sync_to_backend(self, *, workspace_root):
        """Sync via `ukbe-run-agent sync-workflows` CLI instead."""
        return {"status": "NO_OP"}
