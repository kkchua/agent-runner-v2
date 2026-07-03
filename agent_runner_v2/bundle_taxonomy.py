from __future__ import annotations

"""Canonical bundle taxonomy for agent-runner-v2."""

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


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
    "docs/system/00_governance/bootstrap/README.md",
    "docs/system/00_governance/bootstrap/DOCUMENTATION_STANDARD.md",
    "docs/system/00_governance/bootstrap/BUNDLE_TAXONOMY.md",
    "docs/system/00_governance/bootstrap/BUNDLE_MIGRATION_PLAN.md",
    "docs/system/00_governance/bootstrap/SYSTEM_OVERVIEW.md",
    "docs/system/00_governance/bootstrap/BUSINESS_CAPABILITIES.md",
    "docs/system/00_governance/bootstrap/FUNCTIONAL_SPEC.md",
    "docs/system/00_governance/bootstrap/NON_FUNCTIONAL_REQUIREMENTS.md",
    "docs/system/00_governance/bootstrap/SYSTEM_CONTEXT.md",
    "docs/system/00_governance/bootstrap/COMPONENT_ARCHITECTURE.md",
    "docs/system/00_governance/bootstrap/DECISION_LOG.md",
    "docs/system/00_governance/bootstrap/SYSTEM_FILE_STRUCTURE.md",
    "docs/system/00_governance/bootstrap/DEVELOPER_GUIDE.md",
    "docs/system/00_governance/bootstrap/RUNBOOK.md",
    "docs/system/00_governance/bootstrap/EXISTING_REPO_WORKFLOW_SOP.md",
]

WORKFLOW_DOCS = [
    "agent_runner_v2/bootstrap/workflows/default/template_groups.py",
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
