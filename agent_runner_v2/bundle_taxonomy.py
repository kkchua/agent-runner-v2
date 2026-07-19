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
    system_doc_rel("RUNTIME_GOVERNANCE.md"),
]

WORKFLOW_DOCS = [
    "agent_runner_v2/bootstrap/workflows/default/_registry/**",
    "agent_runner_v2/bootstrap/workflows/default/*/**",
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
