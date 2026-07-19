from __future__ import annotations

"""Shared repository-relative documentation path contract.

This module re-exports all path-related constants and functions from constants.py
for backward compatibility with existing imports throughout the codebase.
"""

# Re-export active path primitives and path catalogs first.
from .path_primitives import (
    # Base folder key constants
    FOLDER_KEY_DOCS,
    FOLDER_KEY_SYSTEM_DOC_ROOT,
    FOLDER_KEY_SYSTEM_TEMPLATE_ROOT,
    FOLDER_KEY_SYSTEM_DELIVERY_TEMPLATE_ROOT,
    FOLDER_KEY_SYSTEM_CODEBASE_TEMPLATE_ROOT,
    FOLDER_KEY_CODEBASE_DOC_ROOT,
    FOLDER_KEY_DELIVERY_DOC_ROOT,
    FOLDER_KEY_DOCS_SITE_ROOT,
    FOLDER_KEY_ARCHITECTURE_SITE_ROOT,
    FOLDER_KEY_STAKEHOLDER_SITE_ROOT,
    FOLDER_KEY_DEVELOPER_SITE_ROOT,
    FOLDER_KEY_OPERATOR_SITE_ROOT,
    FOLDER_KEY_TESTER_SITE_ROOT,
    FOLDER_KEY_USER_SITE_ROOT,

    # Helper functions
    system_doc_rel,
    codebase_doc_rel,
    delivery_doc_rel,
    system_delivery_template_rel,
    system_codebase_template_rel,
    docs_site_rel,
    stakeholder_site_rel,
    developer_site_rel,
    operator_site_rel,
    tester_site_rel,
    user_site_rel,
    legacy_codebase_doc_rel,
    legacy_delivery_doc_rel,
    legacy_docs_site_rel,
    repo_doc_rel,
    docs_root_rel,
    system_template_rel,
    architecture_site_rel,
)
from .path_catalog import (

    # Path mapping functions
    known_artifact_paths,
    delivery_scaffold_docs,
    audience_site_artifacts,
    architecture_site_pages,
    stakeholder_site_pages,
    developer_site_pages,
    operator_site_pages,
    tester_site_pages,
    user_site_pages,
    legacy_artifact_paths,
)
