"""Context extensions for sdlc_01_impl_exec_review_v1 workflow.

Combined SDLC pipeline: implementation planning through execution,
validation, and review with adversarial challenge gates at each phase.
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

from agent_runner_v2.constants import SDLC_DELIVERY_BASE, extract_date_from_path, extract_slug_from_path, resolve_next_seq
from agent_runner_v2.runtime_context import get_governance_runtime_root, get_platform_runtime_root, get_workspace_root
from agent_runner_v2.workflow_packages.extensions_base import WorkflowExtensions


class Sdlc01ImplExecReviewExtensions(WorkflowExtensions):
    """Workflow extension hooks for sdlc_01_impl_exec_review_v1."""

    workflow_name = "sdlc_01_impl_exec_review_v1"

    # Step name prefix -> slug source artifact mapping
    _PHASE_SLUG_SOURCE = {
        "impl": "TASK_FILE",
        "exec": "IMPL_FILE",
        "val": "EXEC_FILE",
        "rev": "VAL_FILE",
    }

    # Phase-specific filename suffixes for shared artifact keys.
    # Each phase produces its own challenge/gatekeep/critique/review files
    # with distinct filenames to avoid collision within a single job.
    _PHASE_SUFFIX_MAP = {
        "impl": {
            "CHALLENGE_FILE_SUGGESTED": "-CHALLENGE-50-impl",
            "GATEKEEP_FILE_SUGGESTED": "-GATEKEEP-50-impl",
        },
        "exec": {
            "CHALLENGE_FILE_SUGGESTED": "-CHALLENGE-60-exec",
            "GATEKEEP_FILE_SUGGESTED": "-GATEKEEP-60-exec",
        },
        "val": {
            "CHALLENGE_FILE_SUGGESTED": "-CHALLENGE-70-val",
            "GATEKEEP_FILE_SUGGESTED": "-GATEKEEP-70-val",
        },
        "rev": {
            "CRITIQUE_FILE_SUGGESTED": "-CRITIQUE-80-rev",
            "REVIEW_FILE_SUGGESTED": "-REVIEW-80-all",
        },
    }

    # Input artifact -> subdirectory mapping for bare filename resolution
    _INPUT_DIRS = {
        "TASK_FILE": "40_tasks",
    }

    @staticmethod
    def _get_phase(step: str) -> str:
        """Determine phase from step name prefix."""
        for prefix in ("impl", "exec", "val", "rev"):
            if step.startswith(prefix + "_") or step == f"promote_{prefix}" or step == f"promote_{prefix}ation":
                return prefix
        # Handle promote_implementation, promote_execution, promote_validation, promote_all
        if step == "promote_implementation":
            return "impl"
        if step == "promote_execution":
            return "exec"
        if step == "promote_validation":
            return "val"
        if step == "promote_all":
            return "rev"
        return "unknown"

    def register_artifact_keys(
        self,
        *,
        job_id: str = "{job_id}",
        mode: str = "{mode}",
        date_str: str | None = None,
    ) -> dict[str, str]:
        """Return artifact key to relative-path mappings for OUTPUT artifacts.

        The date_str parameter propagates the original date from TASK_FILE
        through all phases, ensuring consistent naming across the chain.

        Note: Shared keys (CHALLENGE_FILE_SUGGESTED, GATEKEEP_FILE_SUGGESTED,
        CRITIQUE_FILE_SUGGESTED, REVIEW_FILE_SUGGESTED) use generic templates
        here. The actual phase-specific filenames are resolved in
        build_context_extensions() using _PHASE_SUFFIX_MAP.
        """
        if not date_str:
            date_str = dt.datetime.now().strftime("%Y%m%d")
        return {
            # Phase 1: Implementation outputs
            "IMPL_FILE": (
                f"{SDLC_DELIVERY_BASE}/50_implementations/"
                f"IMPL-{date_str}-001-{{seq}}_{{slug}}.md"
            ),
            # Phase 2: Execution outputs
            "EXEC_FILE": (
                f"{SDLC_DELIVERY_BASE}/60_executions/"
                f"EXEC-{date_str}-001-{{seq}}_{{slug}}.md"
            ),
            # Phase 3: Validation outputs
            "VAL_FILE": (
                f"{SDLC_DELIVERY_BASE}/70_validations/"
                f"VAL-{date_str}-{{seq}}_{{slug}}.md"
            ),
            # Phase 4: Review outputs
            "REV_FILE": (
                f"{SDLC_DELIVERY_BASE}/80_reviews/"
                f"REV-{date_str}-{{seq}}_{{slug}}.md"
            ),
            "MEM_FILE": (
                f"{SDLC_DELIVERY_BASE}/80_reviews/"
                f"MEM-{date_str}-{{seq}}_{{slug}}.md"
            ),
            "CLOSE_FILE": (
                f"{SDLC_DELIVERY_BASE}/80_reviews/"
                f"CLOSE-{date_str}-{{seq}}_{{slug}}.md"
            ),
            # Shared review artifacts (phase-specific suffixes applied at resolution time)
            "CHALLENGE_FILE_SUGGESTED": (
                f"{SDLC_DELIVERY_BASE}/80_reviews/"
                f"{{slug}}-CHALLENGE-{date_str}-{{seq}}.md"
            ),
            "GATEKEEP_FILE_SUGGESTED": (
                f"{SDLC_DELIVERY_BASE}/80_reviews/"
                f"{{slug}}-GATEKEEP-{date_str}-{{seq}}.md"
            ),
            "CRITIQUE_FILE_SUGGESTED": (
                f"{SDLC_DELIVERY_BASE}/80_reviews/"
                f"{{slug}}-CRITIQUE-{date_str}-{{seq}}.md"
            ),
            "REVIEW_FILE_SUGGESTED": (
                f"{SDLC_DELIVERY_BASE}/80_reviews/"
                f"{{slug}}-REV-{date_str}-{{seq}}.md"
            ),
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
        """Build context extensions for all 4 phases.

        Determines slug source based on current step's phase prefix.
        Applies phase-specific filename suffixes for shared artifact keys.
        """
        result: dict[str, str] = {}

        # Governance and platform roots
        result["GOVERNANCE_RUNTIME_ROOT"] = str(get_governance_runtime_root())
        result["PLATFORM_RUNTIME_ROOT"] = str(get_platform_runtime_root())

        effective_root = Path(project_root or get_workspace_root() or Path.cwd())
        job_id = str(state.get("job_id", "unknown"))
        artifacts = state.get("artifacts") or {}

        # Determine current phase
        phase = self._get_phase(step)

        # Extract slug from phase-specific source artifact
        slug = "unknown"
        slug_source_key = self._PHASE_SLUG_SOURCE.get(phase, "")
        if slug_source_key:
            slug = extract_slug_from_path(artifacts.get(slug_source_key, ""))

        # Resolve INPUT artifact: TASK_FILE (external input)
        task_value = artifacts.get("TASK_FILE", "")
        if task_value:
            task_path = Path(task_value)
            if task_path.is_absolute():
                result["TASK_FILE"] = str(task_path)
            else:
                # Bare filename — resolve to the tasks directory
                result["TASK_FILE"] = str(
                    effective_root / SDLC_DELIVERY_BASE / self._INPUT_DIRS["TASK_FILE"] / task_path.name
                )
            artifacts["TASK_FILE"] = result["TASK_FILE"]

        # Extract date from TASK_FILE to propagate through all phases
        date_str = extract_date_from_path(task_value)

        # Get phase-specific suffix overrides for this phase
        phase_suffixes = self._PHASE_SUFFIX_MAP.get(phase, {})

        # Resolve all artifact paths
        for key, rel_path in self.register_artifact_keys(job_id=job_id, date_str=date_str).items():
            # If artifact already has a value (produced by a previous step), preserve it
            # EXCEPT for shared keys that are overridden per-phase
            existing_value = artifacts.get(key)
            if existing_value and key not in phase_suffixes:
                result[key] = str(existing_value)
                continue

            # For shared keys with phase-specific suffixes, always re-resolve
            if key in phase_suffixes:
                suffix = phase_suffixes[key]
                resolved = f"{SDLC_DELIVERY_BASE}/80_reviews/{slug}{suffix}.md"
                result[key] = str(effective_root / resolved)
                continue

            resolved = rel_path.replace("{slug}", slug)
            if "{seq}" in resolved:
                path_dir, path_file = resolved.rsplit("/", 1)
                target_dir = effective_root / path_dir
                prefix = path_file.split("{seq}")[0]
                seq = resolve_next_seq(target_dir, prefix)
                resolved = resolved.replace("{seq}", seq)
            result[key] = str(effective_root / resolved)

        return result

    def install_to_global(self, *, workspace_root, runner_home):
        """This workflow has no global installation artifacts."""
        return {"status": "NO_OP"}

    def sync_to_backend(self, *, workspace_root):
        """Sync via `ukbe-run-agent sync-workflows` CLI instead."""
        return {"status": "NO_OP"}
