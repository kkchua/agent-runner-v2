from __future__ import annotations

"""Canonical bundle taxonomy for agent-runner-v2."""

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from .doc_paths import system_doc_rel


CORE_BUNDLE_NAME = "core"
DEFAULT_DOMAIN_BUNDLE = "general"
DEFAULT_BUNDLE_PROFILE = "core+workflow"

DOMAIN_BUNDLE_NAMES = [
    "frontend",
    "backend",
    "content",
    "data",
    "platform",
]


CORE_DOCS = [
    system_doc_rel("README.md"),
    system_doc_rel("DOCUMENTATION_STANDARD.md"),
    system_doc_rel("BUNDLE_TAXONOMY.md"),
    system_doc_rel("BUNDLE_MIGRATION_PLAN.md"),
    system_doc_rel("SYSTEM_OVERVIEW.md"),
    system_doc_rel("BUSINESS_CAPABILITIES.md"),
    system_doc_rel("FUNCTIONAL_SPEC.md"),
    system_doc_rel("NON_FUNCTIONAL_REQUIREMENTS.md"),
    system_doc_rel("SYSTEM_CONTEXT.md"),
    system_doc_rel("COMPONENT_ARCHITECTURE.md"),
    system_doc_rel("DECISION_LOG.md"),
    system_doc_rel("SYSTEM_FILE_STRUCTURE.md"),
    system_doc_rel("DEVELOPER_GUIDE.md"),
    system_doc_rel("RUNBOOK.md"),
    system_doc_rel("EXISTING_REPO_WORKFLOW_SOP.md"),
]

WORKFLOW_DOCS = [
    "agent_runner_v2/bootstrap/workflows/default/template_groups.py",
    "agent_runner_v2/bootstrap/workflows/default/coder_roles.json",
    "agent_runner_v2/bootstrap/workflows/default/prompts/**",
    "agent_runner_v2/bootstrap/workflows/default/job_schema.json",
    "agent_runner_v2/bootstrap/workflows/default/llm_response_schema.json",
    "agent_runner_v2/bootstrap/workflows/default/model_mapping.json",
    "agent_runner_v2/bootstrap/workflows/default/usage_schema.json",
]

DOMAIN_DOCS = {
    "frontend": [
        "docs/system/04_domain/frontend/**",
    ],
    "backend": [
        "docs/system/04_domain/backend/**",
    ],
    "content": [
        "docs/system/04_domain/content/**",
    ],
    "data": [
        "docs/system/04_domain/data/**",
    ],
    "platform": [
        "docs/system/04_domain/platform/**",
    ],
}


@dataclass(frozen=True)
class BundleSelection:
    profile: str = DEFAULT_BUNDLE_PROFILE
    domain: str = DEFAULT_DOMAIN_BUNDLE
    workflow_name: str = "default"
    core_bundle: str = CORE_BUNDLE_NAME
    domain_bundle: str = DEFAULT_DOMAIN_BUNDLE

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def bundle_manifest(*, workflow_name: str, domain: str = DEFAULT_DOMAIN_BUNDLE, profile: str = DEFAULT_BUNDLE_PROFILE) -> dict[str, Any]:
    selection = BundleSelection(profile=profile, domain=domain, workflow_name=workflow_name, domain_bundle=domain)
    return {
        "schema_version": "v1",
        "selection": selection.to_dict(),
        "taxonomy": {
            "core_bundle_docs": CORE_DOCS,
            "domain_bundle_names": list(DOMAIN_BUNDLE_NAMES),
            "workflow_bundle_docs": list(WORKFLOW_DOCS),
            "domain_docs": dict(DOMAIN_DOCS),
        },
    }


def bundle_manifest_path(runner_home: Path) -> Path:
    return runner_home / "bundles" / "bundle-set.json"
