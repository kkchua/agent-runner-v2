from __future__ import annotations

"""Shared path primitives and stable filename/root literals."""

from pathlib import PurePosixPath

# File extensions
EXT_MD = ".md"
EXT_JSON = ".json"
EXT_HTML = ".html"
EXT_PDF = ".pdf"

# Dynamic filename patterns
FILENAME_CHANGE_LOG_PATTERN = "{job_id}-{mode}-change-log"
FILENAME_VALIDATION_PATTERN = "{job_id}-{mode}-validation"
FILENAME_BOOTSTRAP_SUMMARY_PATTERN = "{job_id}-bootstrap-summary"
FILENAME_SNAPSHOT_PATTERN = "{job_id}-{mode}-snapshot"

# Stable filenames
FILENAME_CODEBASE_INVENTORY = "CODEBASE_INVENTORY"
FILENAME_DELIVERY_TEMPLATE_REGISTRY = "01_delivery_template_registry"
FILENAME_DELIVERY_INITIATIVE_TEMPLATE = "02_delivery_initiative_template"
FILENAME_DELIVERY_PLAN_TEMPLATE = "03_delivery_plan_template"
FILENAME_DELIVERY_TASK_GRAPH_TEMPLATE = "04_delivery_task_graph_template"
FILENAME_DELIVERY_TASK_TEMPLATE = "05_delivery_task_template"
FILENAME_DELIVERY_IMPL_TEMPLATE = "06_delivery_impl_template"
FILENAME_DELIVERY_REVIEW_TEMPLATE = "07_delivery_review_template"
FILENAME_DELIVERY_VALIDATION_TEMPLATE = "08_delivery_validation_template"
FILENAME_DELIVERY_MEMORY_TEMPLATE = "09_delivery_memory_template"
FILENAME_CODEBASE_TEMPLATE_REGISTRY = "01_codebase_template_registry"
FILENAME_CODEBASE_INVENTORY_TEMPLATE = "02_codebase_inventory_template"
FILENAME_CODEBASE_MODULE_TEMPLATE = "03_codebase_module_template"
FILENAME_CODEBASE_COMPONENT_TEMPLATE = "04_codebase_component_template"
FILENAME_CODEBASE_CHANGE_TEMPLATE = "05_codebase_change_template"
FILENAME_SITE_INDEX_HTML = "index.html"
FILENAME_SITE_MANIFEST_JSON = "manifest.json"
FILENAME_SITE_CONTENT_MD = "content.md"
FILENAME_SITE_INDEX_BASE = "index"
FILENAME_META_JSON = "meta.json"
FILENAME_SUBMISSION_RESULTS_JSON = "submission_results.json"
FILENAME_SUBMISSION_RESULTS_META_JSON = "submission_results.meta.json"
FILENAME_BUG_REPORT = "BUG_REPORT"
FILENAME_BUG_REPRODUCTION = "BUG_REPRODUCTION"
FILENAME_ROOT_CAUSE = "ROOT_CAUSE"
FILENAME_PATCH = "PATCH"
FILENAME_ARCH_STAKEHOLDER_HTML = "stakeholders.html"
FILENAME_ARCH_DEVELOPER_HTML = "developers.html"
FILENAME_ARCH_FUNCTIONAL_HTML = "functional.html"
FILENAME_ARCH_RUNTIME_HTML = "runtime.html"
FILENAME_ARCH_COMPONENTS_HTML = "components.html"
FILENAME_ARCH_VALIDATION_MD = "validation.md"

# Stable roots
FOLDER_KEY_DOCS = "docs"
FOLDER_KEY_REPO_DOC_ROOT = "docs/repo"
FOLDER_KEY_SYSTEM_DOC_ROOT = "docs/system/00_governance/bootstrap"
FOLDER_KEY_SYSTEM_TEMPLATE_ROOT = "docs/system/00_governance/bootstrap/templates"
FOLDER_KEY_SYSTEM_DELIVERY_TEMPLATE_ROOT = "docs/system/00_governance/bootstrap/templates/delivery"
FOLDER_KEY_SYSTEM_CODEBASE_TEMPLATE_ROOT = "docs/system/00_governance/bootstrap/templates/codebase"
FOLDER_KEY_CODEBASE_DOC_ROOT = "docs/repo/codebase"
FOLDER_KEY_DELIVERY_DOC_ROOT = "docs/repo/delivery"
FOLDER_KEY_AUDIENCE_DOC_ROOT = "docs/repo/audience"
FOLDER_KEY_DOCS_SITE_ROOT = "docs/repo/site"
FOLDER_KEY_ARCHITECTURE_SITE_ROOT = "docs/repo/site"
FOLDER_KEY_STAKEHOLDER_SITE_ROOT = "docs/repo/site/stakeholders"
FOLDER_KEY_DEVELOPER_SITE_ROOT = "docs/repo/site/developers"
FOLDER_KEY_OPERATOR_SITE_ROOT = "docs/repo/site/operators"
FOLDER_KEY_TESTER_SITE_ROOT = "docs/repo/site/testers"
FOLDER_KEY_USER_SITE_ROOT = "docs/repo/site/users"
FOLDER_KEY_LEGACY_CODEBASE_DOC_ROOT = "docs/codebase"
FOLDER_KEY_LEGACY_DELIVERY_DOC_ROOT = "docs/delivery"
FOLDER_KEY_LEGACY_DOCS_SITE_ROOT = "docs/site"
FOLDER_KEY_SYSTEM_BOOTSTRAP = "docs/system/00_governance/bootstrap"
FOLDER_KEY_CODEBASE_ANALYSIS = "docs/repo/codebase/00_analysis"
FOLDER_KEY_CODEBASE_STANDARDS = "docs/repo/codebase/00_standards"
FOLDER_KEY_CODEBASE_INVENTORY = "docs/repo/codebase/01_inventory"
FOLDER_KEY_CODEBASE_MODULES = "docs/repo/codebase/02_modules"
FOLDER_KEY_CODEBASE_COMPONENTS = "docs/repo/codebase/03_components"
FOLDER_KEY_CODEBASE_CHANGES = "docs/repo/codebase/04_changes"
FOLDER_KEY_REPO_GOVERNANCE = "docs/repo/governance"
FOLDER_KEY_DELIVERY_STANDARDS = "docs/repo/delivery/00_standards"
FOLDER_KEY_DELIVERY_INITIATIVES = "docs/repo/delivery/01_initiatives"
FOLDER_KEY_DELIVERY_PLANS = "docs/repo/delivery/02_plans"
FOLDER_KEY_DELIVERY_TASKS = "docs/repo/delivery/03_tasks"
FOLDER_KEY_DELIVERY_IMPLEMENTATIONS = "docs/repo/delivery/04_implementation_plans"
FOLDER_KEY_DELIVERY_REVIEWS = "docs/repo/delivery/05_reviews"
FOLDER_KEY_DELIVERY_VALIDATIONS = "docs/repo/delivery/06_validations"
FOLDER_KEY_DELIVERY_MEMORY = "docs/repo/delivery/07_memory"
FOLDER_KEY_DELIVERY_AGENTS = "docs/repo/delivery/08_agents"
FOLDER_KEY_DELIVERY_TEMPLATES = "docs/system/00_governance/bootstrap/templates/delivery"
FOLDER_KEY_CODEBASE_TEMPLATES = "docs/system/00_governance/bootstrap/templates/codebase"
FOLDER_KEY_SDLC_DOC_ROOT = "docs/repo/sdlc"
FOLDER_KEY_SDLC_GOVERNANCE = "docs/repo/sdlc/00_governance"
FOLDER_KEY_SDLC_REQUIREMENTS = "docs/repo/sdlc/01_requirements"
FOLDER_KEY_SDLC_PLANNING = "docs/repo/sdlc/02_planning"
FOLDER_KEY_SDLC_BACKLOG = "docs/repo/sdlc/03_backlog"
FOLDER_KEY_SDLC_TASKS = "docs/repo/sdlc/04_tasks"
FOLDER_KEY_SDLC_IMPLEMENTATION = "docs/repo/sdlc/05_implementation"
FOLDER_KEY_SDLC_REVIEW = "docs/repo/sdlc/06_review"
FOLDER_KEY_SDLC_EXECUTION = "docs/repo/sdlc/07_execution"
FOLDER_KEY_SDLC_VALIDATION = "docs/repo/sdlc/08_validation"
FOLDER_KEY_SDLC_MEMORY = "docs/repo/sdlc/09_memory"
FOLDER_KEY_SDLC_ARCHIVE = "docs/repo/sdlc/10_archive"
FOLDER_KEY_GLOBAL_BUNDLES = "~/.ukbe-runner/bundles/core/current"
FOLDER_KEY_DOCS_SITE = "docs/repo/site"
FOLDER_KEY_STAKEHOLDER_SITE = "docs/repo/site/stakeholders"
FOLDER_KEY_DEVELOPER_SITE = "docs/repo/site/developers"
FOLDER_KEY_OPERATOR_SITE = "docs/repo/site/operators"
FOLDER_KEY_TESTER_SITE = "docs/repo/site/testers"
FOLDER_KEY_USER_SITE = "docs/repo/site/users"


def relpath(*parts: str) -> str:
    return PurePosixPath(*parts).as_posix()


def artifact_path(artifact_key: str, folder_key: str, extension: str = EXT_MD) -> str:
    return f"{folder_key}/{artifact_key}{extension}"


def placeholder(key: str) -> str:
    return f"{{{key}}}"


def file_in_folder(folder_key: str, filename: str) -> str:
    return relpath(folder_key, filename)


def artifact_meta_path(artifact_rel: str) -> str:
    path = PurePosixPath(str(artifact_rel))
    return str(path.parent / f"{path.stem}.meta.json")


def _rel(*parts: str) -> str:
    return PurePosixPath(*parts).as_posix()


def system_doc_rel(*parts: str) -> str:
    return _rel(*(PurePosixPath(FOLDER_KEY_SYSTEM_DOC_ROOT).parts + parts))


def codebase_doc_rel(*parts: str) -> str:
    return _rel(*(PurePosixPath(FOLDER_KEY_CODEBASE_DOC_ROOT).parts + parts))


def repo_governance_rel(*parts: str) -> str:
    return _rel(*(PurePosixPath(FOLDER_KEY_REPO_GOVERNANCE).parts + parts))


def delivery_doc_rel(*parts: str) -> str:
    return _rel(*(PurePosixPath(FOLDER_KEY_DELIVERY_DOC_ROOT).parts + parts))


def system_delivery_template_rel(*parts: str) -> str:
    return _rel(*(PurePosixPath(FOLDER_KEY_SYSTEM_DELIVERY_TEMPLATE_ROOT).parts + parts))


def system_codebase_template_rel(*parts: str) -> str:
    return _rel(*(PurePosixPath(FOLDER_KEY_SYSTEM_CODEBASE_TEMPLATE_ROOT).parts + parts))


def docs_site_rel(*parts: str) -> str:
    return _rel(*(PurePosixPath(FOLDER_KEY_DOCS_SITE_ROOT).parts + parts))


def stakeholder_site_rel(*parts: str) -> str:
    return _rel(*(PurePosixPath(FOLDER_KEY_STAKEHOLDER_SITE_ROOT).parts + parts))


def developer_site_rel(*parts: str) -> str:
    return _rel(*(PurePosixPath(FOLDER_KEY_DEVELOPER_SITE_ROOT).parts + parts))


def operator_site_rel(*parts: str) -> str:
    return _rel(*(PurePosixPath(FOLDER_KEY_OPERATOR_SITE_ROOT).parts + parts))


def tester_site_rel(*parts: str) -> str:
    return _rel(*(PurePosixPath(FOLDER_KEY_TESTER_SITE_ROOT).parts + parts))


def user_site_rel(*parts: str) -> str:
    return _rel(*(PurePosixPath(FOLDER_KEY_USER_SITE_ROOT).parts + parts))


def legacy_codebase_doc_rel(*parts: str) -> str:
    return _rel(*(PurePosixPath(FOLDER_KEY_LEGACY_CODEBASE_DOC_ROOT).parts + parts))


def legacy_delivery_doc_rel(*parts: str) -> str:
    return _rel(*(PurePosixPath(FOLDER_KEY_LEGACY_DELIVERY_DOC_ROOT).parts + parts))


def legacy_docs_site_rel(*parts: str) -> str:
    return _rel(*(PurePosixPath(FOLDER_KEY_LEGACY_DOCS_SITE_ROOT).parts + parts))


def repo_doc_rel(*parts: str) -> str:
    return _rel(*(PurePosixPath(FOLDER_KEY_DOCS).parts + parts))


def docs_root_rel(*parts: str) -> str:
    return repo_doc_rel(*parts)


def system_template_rel(*parts: str) -> str:
    return _rel(*(PurePosixPath(FOLDER_KEY_SYSTEM_TEMPLATE_ROOT).parts + parts))


def architecture_site_rel(*parts: str) -> str:
    return docs_site_rel(*parts)
