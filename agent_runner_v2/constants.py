"""Compatibility surface for shared constants and path contracts.

Active shared primitives now live in:
- ``artifact_keys.py`` for semantic artifact IDs
- ``path_primitives.py`` for roots, filenames, and path helpers

Legacy precomputed paths and compatibility mappings are loaded from the
preserved backup module until remaining callers are migrated.
"""

from __future__ import annotations

from .constants_legacy_backup_20260717 import *  # noqa: F401,F403
from .artifact_keys import *  # noqa: F401,F403
from .path_primitives import *  # noqa: F401,F403
from .workflow_path_contracts import resolve_workflow_output_paths


def get_master_docs_output_paths(job_id: str = "{job_id}", mode: str = "{mode}") -> dict[str, str]:
    """Compatibility wrapper for the repo-master-doc workflow contract."""
    return resolve_workflow_output_paths(
        template_group="00_repo_master_docs_bootstrap_v1",
        job_id=job_id,
        mode=mode,
    )


def known_artifact_paths() -> dict[str, str]:
    """Map artifact keys to active known repository-relative paths."""
    paths: dict[str, str] = {}
    paths.update(get_master_docs_output_paths())
    paths.update(delivery_scaffold_docs())
    paths[ARTIFACT_KEY_INTEGRATION_MAP] = ARTIFACT_PATH_INTEGRATION_MAP
    paths[ARTIFACT_KEY_FAILURE_MODES] = ARTIFACT_PATH_FAILURE_MODES
    paths[ARTIFACT_KEY_ARCHITECTURE_FLOW] = ARTIFACT_PATH_ARCHITECTURE_FLOW
    paths.update(audience_site_artifacts())
    return paths


def prompt_literal_substitutions() -> dict[str, str]:
    """Map literal file paths to canonical prompt placeholders."""
    substitutions = {
        literal_path: placeholder(alias_key)
        for literal_path, alias_key in PROMPT_LITERAL_ALIASES.items()
    }
    substitutions.update(
        {
            literal_path: placeholder(artifact_key)
            for artifact_key, literal_path in known_artifact_paths().items()
        }
    )
    substitutions.update(
        {
            legacy_path: placeholder(artifact_key)
            for artifact_key, legacy_paths in legacy_artifact_paths().items()
            for legacy_path in legacy_paths
        }
    )
    return substitutions
