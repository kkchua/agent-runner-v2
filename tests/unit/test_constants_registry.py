from __future__ import annotations

from agent_runner_v2.constants import (
    ARTIFACT_KEY_CODEBASE_INVENTORY,
    ARTIFACT_KEY_SYSTEM_DOCS_INDEX,
    ARTIFACT_KEY_SYSTEM_DOC_STANDARD,
    AUDIENCE_MARKDOWN_ARCHIVE_WORKFLOWS,
    AUDIENCE_SITE_WORKFLOWS,
    DELIVERY_SCAFFOLD_DIRS,
    FOLDER_KEY_SYSTEM_CODEBASE_TEMPLATE_ROOT,
    FOLDER_KEY_SYSTEM_DELIVERY_TEMPLATE_ROOT,
    prompt_literal_substitutions,
)


def test_prompt_literal_substitutions_include_aliased_system_docs():
    substitutions = prompt_literal_substitutions()

    assert substitutions["docs/system/00_governance/bootstrap/README.md"] == f"{{{ARTIFACT_KEY_SYSTEM_DOCS_INDEX}}}"
    assert substitutions["docs/system/00_governance/bootstrap/DOCUMENTATION_STANDARD.md"] == f"{{{ARTIFACT_KEY_SYSTEM_DOC_STANDARD}}}"
    assert substitutions["docs/codebase/01_inventory/CODEBASE_INVENTORY.md"] == f"{{{ARTIFACT_KEY_CODEBASE_INVENTORY}}}"
    assert substitutions["docs/repo/codebase/01_inventory/CODEBASE_INVENTORY.md"] == f"{{{ARTIFACT_KEY_CODEBASE_INVENTORY}}}"


def test_audience_workflow_registry_is_consistent():
    stakeholder_site = AUDIENCE_SITE_WORKFLOWS["51_stakeholder_docs_v1"]
    stakeholder_markdown = AUDIENCE_MARKDOWN_ARCHIVE_WORKFLOWS["41_stakeholder_doc_v1"]

    assert stakeholder_site["markdown_rel"] == "docs/repo/site/stakeholders/content.md"
    assert stakeholder_site["html_rel"] == "docs/repo/site/stakeholders/index.html"
    assert stakeholder_site["manifest_rel"] == "docs/repo/site/stakeholders/manifest.json"
    assert stakeholder_markdown["target_rel"] == stakeholder_site["markdown_rel"]
    assert stakeholder_markdown["archive_dir_rel"] == stakeholder_site["archive_dir_rel"]


def test_delivery_scaffold_dirs_include_template_roots():
    assert FOLDER_KEY_SYSTEM_DELIVERY_TEMPLATE_ROOT in DELIVERY_SCAFFOLD_DIRS
    assert FOLDER_KEY_SYSTEM_CODEBASE_TEMPLATE_ROOT in DELIVERY_SCAFFOLD_DIRS
