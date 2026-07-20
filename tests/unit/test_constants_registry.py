from __future__ import annotations

from agent_runner_v2.constants import (
    ARTIFACT_KEY_CODEBASE_INVENTORY,
    ARTIFACT_KEY_SYSTEM_DOCS_INDEX,
    ARTIFACT_KEY_SYSTEM_DOC_STANDARD,
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


def test_delivery_scaffold_dirs_include_template_roots():
    assert FOLDER_KEY_SYSTEM_DELIVERY_TEMPLATE_ROOT in DELIVERY_SCAFFOLD_DIRS
    assert FOLDER_KEY_SYSTEM_CODEBASE_TEMPLATE_ROOT in DELIVERY_SCAFFOLD_DIRS
