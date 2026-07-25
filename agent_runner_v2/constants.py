"""Centralized artifact path constants and path generation for agent-runner-v2.

This module is the SINGLE SOURCE OF TRUTH for all documentation artifact
keys, folder locations, and path construction.

All scripts MUST reference these constants instead of hardcoding paths.
This ensures consistency, prevents case mismatches, and makes maintenance easier.

Usage:
    from agent_runner_v2.constants import artifact_path, ARTIFACT_KEY_PROJECT_ANALYSIS, FOLDER_KEY_SYSTEM_BOOTSTRAP
    
    # Get path for an artifact
    project_analysis_path = artifact_path(ARTIFACT_KEY_PROJECT_ANALYSIS, FOLDER_KEY_SYSTEM_BOOTSTRAP)
    # Returns: "docs/system/00_governance/bootstrap/PROJECT_ANALYSIS.md"
"""

from __future__ import annotations

from pathlib import Path, PurePosixPath

# ============================================================================
# File Extension Constants
# ============================================================================
# Single source of truth for file extensions used across the system.

EXT_MD = ".md"
EXT_JSON = ".json"
EXT_HTML = ".html"
EXT_PDF = ".pdf"

# ============================================================================
# Filename Pattern Constants
# ============================================================================
# Patterns for dynamically generated filenames (with job_id/mode placeholders)

FILENAME_CHANGE_LOG_PATTERN = "{job_id}-{mode}-change-log"
FILENAME_VALIDATION_PATTERN = "{job_id}-{mode}-validation"
FILENAME_BOOTSTRAP_SUMMARY_PATTERN = "{job_id}-bootstrap-summary"
FILENAME_SNAPSHOT_PATTERN = "{job_id}-{mode}-snapshot"
FILENAME_CODEBASE_INVENTORY = "CODEBASE_INVENTORY"

# Template filename constants (lowercase with numeric prefixes)
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

# Common site filenames
FILENAME_SITE_INDEX_HTML = "index.html"
FILENAME_SITE_MANIFEST_JSON = "manifest.json"
FILENAME_SITE_CONTENT_MD = "content.md"
FILENAME_SITE_INDEX_BASE = "index"  # Base name for index files (used with different extensions)
FILENAME_META_JSON = "meta.json"
FILENAME_SUBMISSION_RESULTS_JSON = "submission_results.json"
FILENAME_SUBMISSION_RESULTS_META_JSON = "submission_results.meta.json"

# ============================================================================
# Artifact Key Constants
# ============================================================================
# These constants define the canonical keys used throughout the workflow system.
# Each key represents an artifact that workflows produce or consume.
# 
# Usage: Always use these constants when referencing artifacts in code.
# Example: state["artifacts"][ARTIFACT_KEY_PROJECT_ANALYSIS] = path

# Core delivery workflow artifacts
ARTIFACT_KEY_DRAFT_INIT = "DRAFT_INIT_FILE"
ARTIFACT_KEY_PRE_INIT = "PRE_INIT_FILE"
ARTIFACT_KEY_INIT = "INIT_FILE"
ARTIFACT_KEY_PLAN = "PLAN_FILE"
ARTIFACT_KEY_TASK_GRAPH = "TASK_GRAPH_FILE"
ARTIFACT_KEY_TASK = "TASK_FILE"
ARTIFACT_KEY_IMPL = "IMPL_FILE"
ARTIFACT_KEY_REVIEW = "REVIEW_FILE_SUGGESTED"
ARTIFACT_KEY_AUDIT = "AUDIT_FILE_SUGGESTED"
ARTIFACT_KEY_VALIDATION = "VALIDATION_FILE"
ARTIFACT_KEY_CONTEXT_PACK = "CONTEXT_PACK_FILE"

# Project analysis and delivery scaffold artifacts
ARTIFACT_KEY_PROJECT_CONTEXT = "PROJECT_CONTEXT_FILE"
ARTIFACT_KEY_PROJECT_ANALYSIS = "PROJECT_ANALYSIS"
ARTIFACT_KEY_DELIVERY_SOP = "DELIVERY_SOP"
ARTIFACT_KEY_DELIVERY_STATUS_RULES = "DELIVERY_STATUS_RULES"
ARTIFACT_KEY_DELIVERY_TEMPLATE_REGISTRY = "DELIVERY_TEMPLATE_REGISTRY"
ARTIFACT_KEY_DELIVERY_INITIATIVE_TEMPLATE = "DELIVERY_INITIATIVE_TEMPLATE"
ARTIFACT_KEY_DELIVERY_PLAN_TEMPLATE = "DELIVERY_PLAN_TEMPLATE"
ARTIFACT_KEY_DELIVERY_TASK_GRAPH_TEMPLATE = "DELIVERY_TASK_GRAPH_TEMPLATE"
ARTIFACT_KEY_DELIVERY_TASK_TEMPLATE = "DELIVERY_TASK_TEMPLATE"
ARTIFACT_KEY_DELIVERY_IMPL_TEMPLATE = "DELIVERY_IMPL_TEMPLATE"
ARTIFACT_KEY_DELIVERY_REVIEW_TEMPLATE = "DELIVERY_REVIEW_TEMPLATE"
ARTIFACT_KEY_DELIVERY_VALIDATION_TEMPLATE = "DELIVERY_VALIDATION_TEMPLATE"
ARTIFACT_KEY_DELIVERY_MEMORY_TEMPLATE = "DELIVERY_MEMORY_TEMPLATE"
ARTIFACT_KEY_DELIVERY_AGENTS = "DELIVERY_AGENTS"
ARTIFACT_KEY_DELIVERY_AGENT_PLANNER = "DELIVERY_AGENT_PLANNER"
ARTIFACT_KEY_DELIVERY_AGENT_TASK_DECOMPOSER = "DELIVERY_AGENT_TASK_DECOMPOSER"
ARTIFACT_KEY_DELIVERY_AGENT_IMPL_PLANNER = "DELIVERY_AGENT_IMPL_PLANNER"
ARTIFACT_KEY_DELIVERY_AGENT_EXECUTOR = "DELIVERY_AGENT_EXECUTOR"
ARTIFACT_KEY_DELIVERY_AGENT_REVIEWER = "DELIVERY_AGENT_REVIEWER"
ARTIFACT_KEY_DELIVERY_AGENT_MEMORY_MANAGER = "DELIVERY_AGENT_MEMORY_MANAGER"

# System documentation artifacts (additional)
ARTIFACT_KEY_DOCUMENTATION_STANDARD = "DOCUMENTATION_STANDARD"

# Delivery documentation artifacts (additional)
ARTIFACT_KEY_WORKFLOW_SOP = "WORKFLOW_SOP_v1"
ARTIFACT_KEY_DELIVERY_FOLDER_MAP = "DELIVERY_FOLDER_MAP"

# Codebase documentation artifacts
ARTIFACT_KEY_CODEBASE_DOC_SOP = "CODEBASE_DOC_SOP_v1"
ARTIFACT_KEY_CODEBASE_DOC_STATUS_RULES = "CODEBASE_DOC_STATUS_RULES_v1"
ARTIFACT_KEY_EXISTING_REPO_WORKFLOW_SOP = "EXISTING_REPO_WORKFLOW_SOP"
ARTIFACT_KEY_CODEBASE_TEMPLATE_REGISTRY = "CODEBASE_TEMPLATE_REGISTRY"
ARTIFACT_KEY_CODEBASE_INVENTORY_TEMPLATE = "CODEBASE_INVENTORY_TEMPLATE"
ARTIFACT_KEY_CODEBASE_MODULE_TEMPLATE = "CODEBASE_MODULE_TEMPLATE"
ARTIFACT_KEY_CODEBASE_COMPONENT_TEMPLATE = "CODEBASE_COMPONENT_TEMPLATE"
ARTIFACT_KEY_CODEBASE_CHANGE_TEMPLATE = "CODEBASE_CHANGE_TEMPLATE"
ARTIFACT_KEY_CODEBASE_INVENTORY = "CODEBASE_INVENTORY"
ARTIFACT_KEY_CODEBASE_CHANGE_IMPACT = "CODEBASE_CHANGE_IMPACT"
ARTIFACT_KEY_CODEBASE_SCAN_SNAPSHOT = "CODEBASE_SCAN_SNAPSHOT"

# Understanding and architecture artifacts
ARTIFACT_KEY_INTEGRATION_MAP = "INTEGRATION_MAP"
ARTIFACT_KEY_FAILURE_MODES = "FAILURE_MODES"
ARTIFACT_KEY_ARCHITECTURE_FLOW = "ARCHITECTURE_FLOW"
ARTIFACT_KEY_DELIVERY_FOLDER_MAP = "DELIVERY_FOLDER_MAP"

# System documentation artifacts (bootstrap)
ARTIFACT_KEY_README = "README"  # Used by SYSTEM_DOCS_INDEX
ARTIFACT_KEY_SYSTEM_DOCS_INDEX = "SYSTEM_DOCS_INDEX"  # Maps to README.md
ARTIFACT_KEY_SYSTEM_DOCS_CHANGE_LOG = "SYSTEM_DOCS_CHANGE_LOG"
ARTIFACT_KEY_SYSTEM_DOCS_VALIDATION = "SYSTEM_DOCS_VALIDATION"
ARTIFACT_KEY_SYSTEM_DOC_STANDARD = "SYSTEM_DOC_STANDARD"
ARTIFACT_KEY_BUNDLE_TAXONOMY = "BUNDLE_TAXONOMY"
ARTIFACT_KEY_RUNTIME_GOVERNANCE = "RUNTIME_GOVERNANCE"
ARTIFACT_KEY_BUNDLE_MIGRATION_PLAN = "BUNDLE_MIGRATION_PLAN"
ARTIFACT_KEY_SYSTEM_OVERVIEW = "SYSTEM_OVERVIEW"
ARTIFACT_KEY_BUSINESS_CAPABILITIES = "BUSINESS_CAPABILITIES"
ARTIFACT_KEY_FUNCTIONAL_SPEC = "FUNCTIONAL_SPEC"
ARTIFACT_KEY_NON_FUNCTIONAL_REQUIREMENTS = "NON_FUNCTIONAL_REQUIREMENTS"
ARTIFACT_KEY_SYSTEM_CONTEXT = "SYSTEM_CONTEXT"
ARTIFACT_KEY_COMPONENT_ARCHITECTURE = "COMPONENT_ARCHITECTURE"
ARTIFACT_KEY_DECISION_LOG = "DECISION_LOG"
ARTIFACT_KEY_SYSTEM_FILE_STRUCTURE = "SYSTEM_FILE_STRUCTURE"
ARTIFACT_KEY_DEVELOPER_GUIDE = "DEVELOPER_GUIDE"
ARTIFACT_KEY_RUNBOOK = "RUNBOOK"
ARTIFACT_KEY_BOOTSTRAP_SUMMARY = "BOOTSTRAP_SUMMARY"
ARTIFACT_KEY_CODEBASE_SCAN_SNAPSHOT = "CODEBASE_SCAN_SNAPSHOT"

# ============================================================================
# Folder Key Constants
# ============================================================================
# These constants define base directory paths for different artifact categories.
# They are combined with artifact keys to construct full paths.
#
# Usage: artifact_path(ARTIFACT_KEY_PROJECT_ANALYSIS, FOLDER_KEY_SYSTEM_BOOTSTRAP)

# Base directory folders (correspond to doc_paths.py constants)
FOLDER_KEY_DOCS = "docs"
FOLDER_KEY_REPO_DOC_ROOT = "docs/repo"
FOLDER_KEY_SYSTEM_DOC_ROOT = "docs/system/00_governance/bootstrap"
FOLDER_KEY_SYSTEM_TEMPLATE_ROOT = "docs/system/00_governance/bootstrap/templates"
FOLDER_KEY_SYSTEM_DELIVERY_TEMPLATE_ROOT = "docs/system/00_governance/bootstrap/templates/delivery"
FOLDER_KEY_SYSTEM_CODEBASE_TEMPLATE_ROOT = "docs/system/00_governance/bootstrap/templates/codebase"
FOLDER_KEY_CODEBASE_DOC_ROOT = "docs/repo/codebase/current"
FOLDER_KEY_DELIVERY_DOC_ROOT = "docs/repo/delivery"
FOLDER_KEY_AUDIENCE_DOC_ROOT = "docs/repo/audience"
FOLDER_KEY_DOCS_SITE_ROOT = "docs/repo/site"
FOLDER_KEY_ARCHITECTURE_SITE_ROOT = "docs/repo/site"  # Legacy alias
FOLDER_KEY_STAKEHOLDER_SITE_ROOT = "docs/repo/site/stakeholders"
FOLDER_KEY_DEVELOPER_SITE_ROOT = "docs/repo/site/developers"
FOLDER_KEY_OPERATOR_SITE_ROOT = "docs/repo/site/operators"
FOLDER_KEY_TESTER_SITE_ROOT = "docs/repo/site/testers"
FOLDER_KEY_USER_SITE_ROOT = "docs/repo/site/users"

# Legacy repo-generated roots (read-only compatibility during migration)
FOLDER_KEY_LEGACY_CODEBASE_DOC_ROOT = "docs/codebase"
FOLDER_KEY_LEGACY_DELIVERY_DOC_ROOT = "docs/delivery"
FOLDER_KEY_LEGACY_DOCS_SITE_ROOT = "docs/site"

# Bootstrap folders (where 00_master_docs_bootstrap_v1 writes during development)
FOLDER_KEY_SYSTEM_BOOTSTRAP = "docs/system/00_governance/bootstrap"
FOLDER_KEY_CODEBASE_ANALYSIS = "docs/repo/codebase/current/00_analysis"
FOLDER_KEY_CODEBASE_STANDARDS = "docs/repo/codebase/current/00_standards"
FOLDER_KEY_CODEBASE_INVENTORY = "docs/repo/codebase/current/01_inventory"
FOLDER_KEY_CODEBASE_MODULES = "docs/repo/codebase/current/02_modules"
FOLDER_KEY_CODEBASE_COMPONENTS = "docs/repo/codebase/current/03_components"
FOLDER_KEY_CODEBASE_CHANGES = "docs/repo/codebase/current/04_changes"

# Repo governance folder (Layer 2 repo master docs)
FOLDER_KEY_REPO_GOVERNANCE = "docs/repo/governance"

# Delivery folders (where 10_execution_scaffold_v1 writes)
FOLDER_KEY_DELIVERY_DOC_ROOT = "docs/repo/delivery"
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

# Runtime global folders (after ukbe-run-agent init copies bootstrap to ~/.ukbe-runner)
# These will be resolved at runtime using the global runner home path
FOLDER_KEY_GLOBAL_BUNDLES = "~/.ukbe-runner/bundles/core/current"
FOLDER_KEY_GLOBAL_FOUNDATION = "~/.ukbe-runner/bundles/core/current/foundation"
FOLDER_KEY_GLOBAL_PLATFORM = "~/.ukbe-runner/bundles/core/current/platform"

# ============================================================================
# Path Generation Function
# ============================================================================

def artifact_path(artifact_key: str, folder_key: str, extension: str = EXT_MD) -> str:
    """Construct artifact path by combining folder base with artifact key and extension.
    
    Args:
        artifact_key: Artifact identifier (e.g., ARTIFACT_KEY_PROJECT_ANALYSIS)
        folder_key: Base directory path (e.g., FOLDER_KEY_SYSTEM_BOOTSTRAP)
        extension: File extension (default: EXT_MD)
        
    Returns:
        Repository-relative path like "docs/system/00_governance/bootstrap/PROJECT_ANALYSIS.md"
        
    Usage:
        path = artifact_path(ARTIFACT_KEY_PROJECT_ANALYSIS, FOLDER_KEY_SYSTEM_BOOTSTRAP)
        # Returns: "docs/system/00_governance/bootstrap/PROJECT_ANALYSIS.md"
        
        path = artifact_path(ARTIFACT_KEY_DELIVERY_AGENTS, FOLDER_KEY_DELIVERY_STANDARDS)
        # Returns: "docs/delivery/00_standards/DELIVERY_AGENTS.md"
    """
    return f"{folder_key}/{artifact_key}{extension}"


# ============================================================================
# Helper Functions
# ============================================================================

def placeholder(key: str) -> str:
    """Convert an artifact key to a prompt placeholder.
    
    Args:
        key: Artifact key (e.g., ARTIFACT_KEY_PROJECT_ANALYSIS)
        
    Returns:
        Placeholder string with braces (e.g., "{PROJECT_ANALYSIS}")
        
    Usage:
        placeholder(ARTIFACT_KEY_PROJECT_ANALYSIS)  # Returns "{PROJECT_ANALYSIS}"
    """
    return f"{{{key}}}"


def relpath(*parts: str) -> str:
    """Join path fragments into a repository-relative POSIX path."""
    return PurePosixPath(*parts).as_posix()


def file_in_folder(folder_key: str, filename: str) -> str:
    """Build a repository-relative path for a literal filename in a known folder."""
    return relpath(folder_key, filename)


def artifact_meta_path(artifact_rel: str) -> str:
    """Return the sidecar path for an artifact path."""
    path = PurePosixPath(str(artifact_rel))
    return str(path.parent / f"{path.stem}.meta.json")


# ============================================================================
# Pre-computed Artifact Path Constants
# ============================================================================
# These are computed from ARTIFACT_KEY + FOLDER_KEY using artifact_path().
# No hardcoded strings - all paths derived from constants.

# System documentation paths (bootstrap)
ARTIFACT_PATH_PROJECT_ANALYSIS = artifact_path(ARTIFACT_KEY_PROJECT_ANALYSIS, FOLDER_KEY_CODEBASE_ANALYSIS)
ARTIFACT_PATH_README = artifact_path(ARTIFACT_KEY_README, FOLDER_KEY_SYSTEM_BOOTSTRAP)
ARTIFACT_PATH_DOCUMENTATION_STANDARD = artifact_path(ARTIFACT_KEY_DOCUMENTATION_STANDARD, FOLDER_KEY_SYSTEM_BOOTSTRAP)
ARTIFACT_PATH_BUNDLE_TAXONOMY = artifact_path(ARTIFACT_KEY_BUNDLE_TAXONOMY, FOLDER_KEY_SYSTEM_BOOTSTRAP)
ARTIFACT_PATH_RUNTIME_GOVERNANCE = artifact_path(ARTIFACT_KEY_RUNTIME_GOVERNANCE, FOLDER_KEY_SYSTEM_BOOTSTRAP)
ARTIFACT_PATH_BUNDLE_MIGRATION_PLAN = artifact_path(ARTIFACT_KEY_BUNDLE_MIGRATION_PLAN, FOLDER_KEY_SYSTEM_BOOTSTRAP)
ARTIFACT_PATH_SYSTEM_OVERVIEW = artifact_path(ARTIFACT_KEY_SYSTEM_OVERVIEW, FOLDER_KEY_SYSTEM_BOOTSTRAP)
ARTIFACT_PATH_BUSINESS_CAPABILITIES = artifact_path(ARTIFACT_KEY_BUSINESS_CAPABILITIES, FOLDER_KEY_SYSTEM_BOOTSTRAP)
ARTIFACT_PATH_FUNCTIONAL_SPEC = artifact_path(ARTIFACT_KEY_FUNCTIONAL_SPEC, FOLDER_KEY_SYSTEM_BOOTSTRAP)
ARTIFACT_PATH_NON_FUNCTIONAL_REQUIREMENTS = artifact_path(ARTIFACT_KEY_NON_FUNCTIONAL_REQUIREMENTS, FOLDER_KEY_SYSTEM_BOOTSTRAP)
ARTIFACT_PATH_SYSTEM_CONTEXT = artifact_path(ARTIFACT_KEY_SYSTEM_CONTEXT, FOLDER_KEY_SYSTEM_BOOTSTRAP)
ARTIFACT_PATH_COMPONENT_ARCHITECTURE = artifact_path(ARTIFACT_KEY_COMPONENT_ARCHITECTURE, FOLDER_KEY_SYSTEM_BOOTSTRAP)
ARTIFACT_PATH_DECISION_LOG = artifact_path(ARTIFACT_KEY_DECISION_LOG, FOLDER_KEY_SYSTEM_BOOTSTRAP)
ARTIFACT_PATH_SYSTEM_FILE_STRUCTURE = artifact_path(ARTIFACT_KEY_SYSTEM_FILE_STRUCTURE, FOLDER_KEY_SYSTEM_BOOTSTRAP)
ARTIFACT_PATH_DEVELOPER_GUIDE = artifact_path(ARTIFACT_KEY_DEVELOPER_GUIDE, FOLDER_KEY_SYSTEM_BOOTSTRAP)
ARTIFACT_PATH_RUNBOOK = artifact_path(ARTIFACT_KEY_RUNBOOK, FOLDER_KEY_SYSTEM_BOOTSTRAP)
ARTIFACT_PATH_EXISTING_REPO_WORKFLOW_SOP = artifact_path(ARTIFACT_KEY_EXISTING_REPO_WORKFLOW_SOP, FOLDER_KEY_DELIVERY_STANDARDS)

# System governance paths (additional)
ARTIFACT_PATH_DELIVERY_STATUS_RULES = artifact_path(ARTIFACT_KEY_DELIVERY_STATUS_RULES, FOLDER_KEY_DELIVERY_STANDARDS)
ARTIFACT_PATH_WORKFLOW_SOP = artifact_path(ARTIFACT_KEY_WORKFLOW_SOP, FOLDER_KEY_DELIVERY_STANDARDS)

# Codebase documentation paths
ARTIFACT_PATH_CODEBASE_INVENTORY = artifact_path(FILENAME_CODEBASE_INVENTORY, FOLDER_KEY_CODEBASE_INVENTORY)
ARTIFACT_PATH_INTEGRATION_MAP = artifact_path(ARTIFACT_KEY_INTEGRATION_MAP, FOLDER_KEY_CODEBASE_INVENTORY)
ARTIFACT_PATH_FAILURE_MODES = artifact_path(ARTIFACT_KEY_FAILURE_MODES, FOLDER_KEY_CODEBASE_INVENTORY)
ARTIFACT_PATH_ARCHITECTURE_FLOW = artifact_path(ARTIFACT_KEY_ARCHITECTURE_FLOW, FOLDER_KEY_CODEBASE_INVENTORY)
ARTIFACT_PATH_CODEBASE_DOC_SOP = artifact_path(ARTIFACT_KEY_CODEBASE_DOC_SOP, FOLDER_KEY_CODEBASE_STANDARDS)
ARTIFACT_PATH_CODEBASE_DOC_STATUS_RULES = artifact_path(ARTIFACT_KEY_CODEBASE_DOC_STATUS_RULES, FOLDER_KEY_CODEBASE_STANDARDS)

# Delivery documentation paths
ARTIFACT_PATH_DELIVERY_AGENTS = artifact_path(ARTIFACT_KEY_DELIVERY_AGENTS, FOLDER_KEY_DELIVERY_AGENTS)
ARTIFACT_PATH_DELIVERY_AGENT_PLANNER = artifact_path(ARTIFACT_KEY_DELIVERY_AGENT_PLANNER, FOLDER_KEY_DELIVERY_AGENTS)
ARTIFACT_PATH_DELIVERY_AGENT_TASK_DECOMPOSER = artifact_path(ARTIFACT_KEY_DELIVERY_AGENT_TASK_DECOMPOSER, FOLDER_KEY_DELIVERY_AGENTS)
ARTIFACT_PATH_DELIVERY_AGENT_IMPL_PLANNER = artifact_path(ARTIFACT_KEY_DELIVERY_AGENT_IMPL_PLANNER, FOLDER_KEY_DELIVERY_AGENTS)
ARTIFACT_PATH_DELIVERY_AGENT_EXECUTOR = artifact_path(ARTIFACT_KEY_DELIVERY_AGENT_EXECUTOR, FOLDER_KEY_DELIVERY_AGENTS)
ARTIFACT_PATH_DELIVERY_AGENT_REVIEWER = artifact_path(ARTIFACT_KEY_DELIVERY_AGENT_REVIEWER, FOLDER_KEY_DELIVERY_AGENTS)
ARTIFACT_PATH_DELIVERY_AGENT_MEMORY_MANAGER = artifact_path(ARTIFACT_KEY_DELIVERY_AGENT_MEMORY_MANAGER, FOLDER_KEY_DELIVERY_AGENTS)
ARTIFACT_PATH_DELIVERY_FOLDER_MAP = artifact_path(ARTIFACT_KEY_DELIVERY_FOLDER_MAP, FOLDER_KEY_DELIVERY_DOC_ROOT, EXT_JSON)

# Template paths
ARTIFACT_PATH_DELIVERY_TEMPLATE_REGISTRY = f"{FOLDER_KEY_DELIVERY_TEMPLATES}/{FILENAME_DELIVERY_TEMPLATE_REGISTRY}{EXT_MD}"
ARTIFACT_PATH_DELIVERY_INITIATIVE_TEMPLATE = f"{FOLDER_KEY_DELIVERY_TEMPLATES}/{FILENAME_DELIVERY_INITIATIVE_TEMPLATE}{EXT_MD}"
ARTIFACT_PATH_DELIVERY_PLAN_TEMPLATE = f"{FOLDER_KEY_DELIVERY_TEMPLATES}/{FILENAME_DELIVERY_PLAN_TEMPLATE}{EXT_MD}"
ARTIFACT_PATH_DELIVERY_TASK_GRAPH_TEMPLATE = f"{FOLDER_KEY_DELIVERY_TEMPLATES}/{FILENAME_DELIVERY_TASK_GRAPH_TEMPLATE}{EXT_MD}"
ARTIFACT_PATH_DELIVERY_TASK_TEMPLATE = f"{FOLDER_KEY_DELIVERY_TEMPLATES}/{FILENAME_DELIVERY_TASK_TEMPLATE}{EXT_MD}"
ARTIFACT_PATH_DELIVERY_IMPL_TEMPLATE = f"{FOLDER_KEY_DELIVERY_TEMPLATES}/{FILENAME_DELIVERY_IMPL_TEMPLATE}{EXT_MD}"
ARTIFACT_PATH_DELIVERY_REVIEW_TEMPLATE = f"{FOLDER_KEY_DELIVERY_TEMPLATES}/{FILENAME_DELIVERY_REVIEW_TEMPLATE}{EXT_MD}"
ARTIFACT_PATH_DELIVERY_VALIDATION_TEMPLATE = f"{FOLDER_KEY_DELIVERY_TEMPLATES}/{FILENAME_DELIVERY_VALIDATION_TEMPLATE}{EXT_MD}"
ARTIFACT_PATH_DELIVERY_MEMORY_TEMPLATE = f"{FOLDER_KEY_DELIVERY_TEMPLATES}/{FILENAME_DELIVERY_MEMORY_TEMPLATE}{EXT_MD}"
ARTIFACT_PATH_CODEBASE_TEMPLATE_REGISTRY = f"{FOLDER_KEY_CODEBASE_TEMPLATES}/{FILENAME_CODEBASE_TEMPLATE_REGISTRY}{EXT_MD}"
ARTIFACT_PATH_CODEBASE_INVENTORY_TEMPLATE = f"{FOLDER_KEY_CODEBASE_TEMPLATES}/{FILENAME_CODEBASE_INVENTORY_TEMPLATE}{EXT_MD}"
ARTIFACT_PATH_CODEBASE_MODULE_TEMPLATE = f"{FOLDER_KEY_CODEBASE_TEMPLATES}/{FILENAME_CODEBASE_MODULE_TEMPLATE}{EXT_MD}"
ARTIFACT_PATH_CODEBASE_COMPONENT_TEMPLATE = f"{FOLDER_KEY_CODEBASE_TEMPLATES}/{FILENAME_CODEBASE_COMPONENT_TEMPLATE}{EXT_MD}"
ARTIFACT_PATH_CODEBASE_CHANGE_TEMPLATE = f"{FOLDER_KEY_CODEBASE_TEMPLATES}/{FILENAME_CODEBASE_CHANGE_TEMPLATE}{EXT_MD}"

DELIVERY_SCAFFOLD_DIRS = [
    FOLDER_KEY_SYSTEM_DELIVERY_TEMPLATE_ROOT,
    FOLDER_KEY_SYSTEM_CODEBASE_TEMPLATE_ROOT,
]

RUN_AGENT_REQUIRED_DOC_DIRS = [
    *DELIVERY_SCAFFOLD_DIRS,
    FOLDER_KEY_CODEBASE_STANDARDS,
    relpath(FOLDER_KEY_DOCS, "system", "00_governance"),
    FOLDER_KEY_SYSTEM_BOOTSTRAP,
    FOLDER_KEY_SYSTEM_TEMPLATE_ROOT,
]

# ============================================================================
# Reference Files Constant
# ============================================================================
# Centralized reference files mapping used by workflow validation and prompt rendering.
# Keys use clean ARTIFACT_KEY names (no _MD suffix).
# Values use pre-computed ARTIFACT_PATH_* constants - zero hardcoded strings.

# ============================================================================
# Reference Files Constant
# ============================================================================
# Centralized reference files mapping used by workflow validation and prompt rendering.
# Keys use clean artifact names (no ARTIFACT_KEY_ prefix).
# Values use pre-computed ARTIFACT_PATH_* constants - zero hardcoded strings.

REFERENCE_FILES = {
    # Project analysis
    "PROJECT_ANALYSIS": ARTIFACT_PATH_PROJECT_ANALYSIS,
    # Agent contracts
    "DELIVERY_AGENTS": ARTIFACT_PATH_DELIVERY_AGENTS,
    "DELIVERY_AGENT_PLANNER": ARTIFACT_PATH_DELIVERY_AGENT_PLANNER,
    "DELIVERY_AGENT_TASK_DECOMPOSER": ARTIFACT_PATH_DELIVERY_AGENT_TASK_DECOMPOSER,
    "DELIVERY_AGENT_IMPL_PLANNER": ARTIFACT_PATH_DELIVERY_AGENT_IMPL_PLANNER,
    "DELIVERY_AGENT_EXECUTOR": ARTIFACT_PATH_DELIVERY_AGENT_EXECUTOR,
    "DELIVERY_AGENT_REVIEWER": ARTIFACT_PATH_DELIVERY_AGENT_REVIEWER,
    "DELIVERY_AGENT_MEMORY_MANAGER": ARTIFACT_PATH_DELIVERY_AGENT_MEMORY_MANAGER,
    # Delivery governance
    "DELIVERY_STATUS_RULES": ARTIFACT_PATH_DELIVERY_STATUS_RULES,
    "WORKFLOW_SOP": ARTIFACT_PATH_WORKFLOW_SOP,
    "DELIVERY_SOP": ARTIFACT_PATH_WORKFLOW_SOP,  # Alias to same path
    # Codebase standards
    "CODEBASE_DOC_SOP": ARTIFACT_PATH_CODEBASE_DOC_SOP,
    "CODEBASE_DOC_SOP_v1": ARTIFACT_PATH_CODEBASE_DOC_SOP,  # Alias for artifact key
    "CODEBASE_DOC_STATUS_RULES": ARTIFACT_PATH_CODEBASE_DOC_STATUS_RULES,
    "CODEBASE_DOC_STATUS_RULES_v1": ARTIFACT_PATH_CODEBASE_DOC_STATUS_RULES,  # Alias for artifact key
    "CODEBASE_INVENTORY": ARTIFACT_PATH_CODEBASE_INVENTORY,
    # System docs
    "DOCUMENTATION_STANDARD": ARTIFACT_PATH_DOCUMENTATION_STANDARD,
    "SYSTEM_OVERVIEW": ARTIFACT_PATH_SYSTEM_OVERVIEW,
    "SYSTEM_FILE_STRUCTURE": ARTIFACT_PATH_SYSTEM_FILE_STRUCTURE,
    "DEVELOPER_GUIDE": ARTIFACT_PATH_DEVELOPER_GUIDE,
    "RUNBOOK": ARTIFACT_PATH_RUNBOOK,
    "EXISTING_REPO_WORKFLOW_SOP": ARTIFACT_PATH_EXISTING_REPO_WORKFLOW_SOP,
    # Templates
    "DELIVERY_TEMPLATE_REGISTRY": ARTIFACT_PATH_DELIVERY_TEMPLATE_REGISTRY,
    "DELIVERY_INITIATIVE_TEMPLATE": ARTIFACT_PATH_DELIVERY_INITIATIVE_TEMPLATE,
    "DELIVERY_PLAN_TEMPLATE": ARTIFACT_PATH_DELIVERY_PLAN_TEMPLATE,
    "DELIVERY_TASK_GRAPH_TEMPLATE": ARTIFACT_PATH_DELIVERY_TASK_GRAPH_TEMPLATE,
    "DELIVERY_TASK_TEMPLATE": ARTIFACT_PATH_DELIVERY_TASK_TEMPLATE,
    "DELIVERY_IMPL_TEMPLATE": ARTIFACT_PATH_DELIVERY_IMPL_TEMPLATE,
    "DELIVERY_REVIEW_TEMPLATE": ARTIFACT_PATH_DELIVERY_REVIEW_TEMPLATE,
    "DELIVERY_VALIDATION_TEMPLATE": ARTIFACT_PATH_DELIVERY_VALIDATION_TEMPLATE,
    "DELIVERY_MEMORY_TEMPLATE": ARTIFACT_PATH_DELIVERY_MEMORY_TEMPLATE,
    "CODEBASE_TEMPLATE_REGISTRY": ARTIFACT_PATH_CODEBASE_TEMPLATE_REGISTRY,
    "CODEBASE_INVENTORY_TEMPLATE": ARTIFACT_PATH_CODEBASE_INVENTORY_TEMPLATE,
    "CODEBASE_MODULE_TEMPLATE": ARTIFACT_PATH_CODEBASE_MODULE_TEMPLATE,
    "CODEBASE_COMPONENT_TEMPLATE": ARTIFACT_PATH_CODEBASE_COMPONENT_TEMPLATE,
    "CODEBASE_CHANGE_TEMPLATE": ARTIFACT_PATH_CODEBASE_CHANGE_TEMPLATE,
    # Folder map
    "DELIVERY_FOLDER_MAP": ARTIFACT_PATH_DELIVERY_FOLDER_MAP,
    # Integration and architecture flow
    "INTEGRATION_MAP": ARTIFACT_PATH_INTEGRATION_MAP,
    "FAILURE_MODES": ARTIFACT_PATH_FAILURE_MODES,
    "ARCHITECTURE_FLOW": ARTIFACT_PATH_ARCHITECTURE_FLOW,
}


# ============================================================================
# Folder Root Constants (for prompt templates - NOT in REFERENCE_FILES)
# ============================================================================
# These are directory paths used in prompts for scanning, not artifact files.
# They are resolved at runtime by the prompt rendering system.
FOLDER_ROOT_CONSTANTS = {
    "DELIVERY_DOC_ROOT": FOLDER_KEY_DELIVERY_DOC_ROOT,
    "SYSTEM_DOC_ROOT": FOLDER_KEY_SYSTEM_DOC_ROOT,
    "CODEBASE_DOC_ROOT": FOLDER_KEY_CODEBASE_DOC_ROOT,
    "SYSTEM_TEMPLATE_ROOT": FOLDER_KEY_SYSTEM_TEMPLATE_ROOT,
}



# ============================================================================
# Output Path Mappings
# ============================================================================
# Maps artifact keys to output file paths for different workflow families.
# Used by step_runner to determine where artifacts should be written.

def get_master_docs_output_paths(job_id: str = "{job_id}", mode: str = "{mode}") -> dict[str, str]:
    """Generate output path mappings for master bootstrap workflow.

    Uses artifact_path() function with FOLDER_KEY and ARTIFACT_KEY constants for consistency.

    Args:
        job_id: Job identifier (can contain {job_id} placeholder for template)
        mode: Workflow mode (can contain {mode} placeholder for template)

    Returns:
        Dict mapping artifact keys to repo-relative output paths
    """
    # Note: Some paths use f-strings with FILENAME_*_PATTERN constants because
    # the filenames contain dynamic placeholders (job_id, mode) that vary per execution.
    # These cannot use artifact_path() directly but still use FOLDER_KEY constants for base paths.
    return {
        # Governance docs (Layer 2) → docs/repo/governance/
        ARTIFACT_KEY_PROJECT_ANALYSIS: artifact_path(ARTIFACT_KEY_PROJECT_ANALYSIS, FOLDER_KEY_REPO_GOVERNANCE),
        ARTIFACT_KEY_SYSTEM_DOCS_INDEX: artifact_path(ARTIFACT_KEY_README, FOLDER_KEY_REPO_GOVERNANCE),
        ARTIFACT_KEY_SYSTEM_DOCS_CHANGE_LOG: f"{FOLDER_KEY_REPO_GOVERNANCE}/{FILENAME_CHANGE_LOG_PATTERN.format(job_id=job_id, mode=mode)}{EXT_MD}",
        ARTIFACT_KEY_SYSTEM_DOCS_VALIDATION: f"{FOLDER_KEY_REPO_GOVERNANCE}/{FILENAME_VALIDATION_PATTERN.format(job_id=job_id, mode=mode)}{EXT_MD}",
        ARTIFACT_KEY_SYSTEM_DOC_STANDARD: repo_governance_rel("REPO_DOCUMENTATION_STANDARD.md"),
        ARTIFACT_KEY_DECISION_LOG: artifact_path(ARTIFACT_KEY_DECISION_LOG, FOLDER_KEY_REPO_GOVERNANCE),
        ARTIFACT_KEY_DEVELOPER_GUIDE: artifact_path(ARTIFACT_KEY_DEVELOPER_GUIDE, FOLDER_KEY_REPO_GOVERNANCE),
        ARTIFACT_KEY_BOOTSTRAP_SUMMARY: f"{FOLDER_KEY_REPO_GOVERNANCE}/{FILENAME_BOOTSTRAP_SUMMARY_PATTERN.format(job_id=job_id)}{EXT_MD}",
        # Codebase inventory stays in docs/repo/codebase/
        ARTIFACT_KEY_CODEBASE_SCAN_SNAPSHOT: f"{FOLDER_KEY_CODEBASE_CHANGES}/{FILENAME_SNAPSHOT_PATTERN.format(job_id=job_id, mode=mode)}{EXT_JSON}",
    }


# ============================================================================
# Path Helper Functions (from doc_paths.py)
# ============================================================================
# These functions construct paths dynamically using base folder constants.

def _rel(*parts: str) -> str:
    """Convert path parts to POSIX-style string."""
    return PurePosixPath(*parts).as_posix()


def system_doc_rel(*parts: str) -> str:
    """Get path relative to SYSTEM_DOC_ROOT."""
    return _rel(*(PurePosixPath(FOLDER_KEY_SYSTEM_DOC_ROOT).parts + parts))


def codebase_doc_rel(*parts: str) -> str:
    """Get path relative to CODEBASE_DOC_ROOT."""
    return _rel(*(PurePosixPath(FOLDER_KEY_CODEBASE_DOC_ROOT).parts + parts))


def repo_governance_rel(*parts: str) -> str:
    """Get path relative to REPO_GOVERNANCE (Layer 2 repo master docs)."""
    return _rel(*(PurePosixPath(FOLDER_KEY_REPO_GOVERNANCE).parts + parts))


def delivery_doc_rel(*parts: str) -> str:
    """Get path relative to DELIVERY_DOC_ROOT."""
    return _rel(*(PurePosixPath(FOLDER_KEY_DELIVERY_DOC_ROOT).parts + parts))


def system_delivery_template_rel(*parts: str) -> str:
    """Get path relative to SYSTEM_DELIVERY_TEMPLATE_ROOT."""
    return _rel(*(PurePosixPath(FOLDER_KEY_SYSTEM_DELIVERY_TEMPLATE_ROOT).parts + parts))


def system_codebase_template_rel(*parts: str) -> str:
    """Get path relative to SYSTEM_CODEBASE_TEMPLATE_ROOT."""
    return _rel(*(PurePosixPath(FOLDER_KEY_SYSTEM_CODEBASE_TEMPLATE_ROOT).parts + parts))


def legacy_codebase_doc_rel(*parts: str) -> str:
    """Get path relative to the legacy CODEBASE_DOC_ROOT."""
    return _rel(*(PurePosixPath(FOLDER_KEY_LEGACY_CODEBASE_DOC_ROOT).parts + parts))


def legacy_delivery_doc_rel(*parts: str) -> str:
    """Get path relative to the legacy DELIVERY_DOC_ROOT."""
    return _rel(*(PurePosixPath(FOLDER_KEY_LEGACY_DELIVERY_DOC_ROOT).parts + parts))


def repo_doc_rel(*parts: str) -> str:
    """Get path relative to DOCS_ROOT (docs/ folder)."""
    return _rel(*(PurePosixPath(FOLDER_KEY_DOCS).parts + parts))


def docs_root_rel(*parts: str) -> str:
    """Get path relative to DOCS_ROOT (docs/ folder) - alias for repo_doc_rel."""
    return repo_doc_rel(*parts)


def system_template_rel(*parts: str) -> str:
    """Get path relative to SYSTEM_TEMPLATE_ROOT."""
    return _rel(*(PurePosixPath(FOLDER_KEY_SYSTEM_TEMPLATE_ROOT).parts + parts))


# ============================================================================
# Path Mapping Functions (from doc_paths.py)
# ============================================================================
# These functions return dictionaries mapping artifact keys to their paths.

def delivery_scaffold_docs() -> dict[str, str]:
    """Get all delivery scaffold documentation paths using centralized constants."""
    return {
        ARTIFACT_KEY_PROJECT_ANALYSIS: ARTIFACT_PATH_PROJECT_ANALYSIS,
        ARTIFACT_KEY_DELIVERY_SOP: ARTIFACT_PATH_WORKFLOW_SOP,
        ARTIFACT_KEY_DELIVERY_STATUS_RULES: ARTIFACT_PATH_DELIVERY_STATUS_RULES,
        ARTIFACT_KEY_DELIVERY_VALIDATION_TEMPLATE: ARTIFACT_PATH_DELIVERY_VALIDATION_TEMPLATE,
        ARTIFACT_KEY_DELIVERY_TEMPLATE_REGISTRY: ARTIFACT_PATH_DELIVERY_TEMPLATE_REGISTRY,
        ARTIFACT_KEY_DELIVERY_INITIATIVE_TEMPLATE: ARTIFACT_PATH_DELIVERY_INITIATIVE_TEMPLATE,
        ARTIFACT_KEY_DELIVERY_PLAN_TEMPLATE: ARTIFACT_PATH_DELIVERY_PLAN_TEMPLATE,
        ARTIFACT_KEY_DELIVERY_TASK_GRAPH_TEMPLATE: ARTIFACT_PATH_DELIVERY_TASK_GRAPH_TEMPLATE,
        ARTIFACT_KEY_DELIVERY_TASK_TEMPLATE: ARTIFACT_PATH_DELIVERY_TASK_TEMPLATE,
        ARTIFACT_KEY_DELIVERY_IMPL_TEMPLATE: ARTIFACT_PATH_DELIVERY_IMPL_TEMPLATE,
        ARTIFACT_KEY_DELIVERY_REVIEW_TEMPLATE: ARTIFACT_PATH_DELIVERY_REVIEW_TEMPLATE,
        ARTIFACT_KEY_DELIVERY_MEMORY_TEMPLATE: ARTIFACT_PATH_DELIVERY_MEMORY_TEMPLATE,
        ARTIFACT_KEY_DELIVERY_AGENTS: ARTIFACT_PATH_DELIVERY_AGENTS,
        ARTIFACT_KEY_DELIVERY_AGENT_PLANNER: ARTIFACT_PATH_DELIVERY_AGENT_PLANNER,
        ARTIFACT_KEY_DELIVERY_AGENT_TASK_DECOMPOSER: ARTIFACT_PATH_DELIVERY_AGENT_TASK_DECOMPOSER,
        ARTIFACT_KEY_DELIVERY_AGENT_IMPL_PLANNER: ARTIFACT_PATH_DELIVERY_AGENT_IMPL_PLANNER,
        ARTIFACT_KEY_DELIVERY_AGENT_EXECUTOR: ARTIFACT_PATH_DELIVERY_AGENT_EXECUTOR,
        ARTIFACT_KEY_DELIVERY_AGENT_REVIEWER: ARTIFACT_PATH_DELIVERY_AGENT_REVIEWER,
        ARTIFACT_KEY_DELIVERY_AGENT_MEMORY_MANAGER: ARTIFACT_PATH_DELIVERY_AGENT_MEMORY_MANAGER,
        ARTIFACT_KEY_CODEBASE_DOC_SOP: ARTIFACT_PATH_CODEBASE_DOC_SOP,
        ARTIFACT_KEY_CODEBASE_DOC_STATUS_RULES: ARTIFACT_PATH_CODEBASE_DOC_STATUS_RULES,
        ARTIFACT_KEY_CODEBASE_TEMPLATE_REGISTRY: ARTIFACT_PATH_CODEBASE_TEMPLATE_REGISTRY,
        ARTIFACT_KEY_CODEBASE_INVENTORY_TEMPLATE: ARTIFACT_PATH_CODEBASE_INVENTORY_TEMPLATE,
        ARTIFACT_KEY_CODEBASE_MODULE_TEMPLATE: ARTIFACT_PATH_CODEBASE_MODULE_TEMPLATE,
        ARTIFACT_KEY_CODEBASE_COMPONENT_TEMPLATE: ARTIFACT_PATH_CODEBASE_COMPONENT_TEMPLATE,
        ARTIFACT_KEY_CODEBASE_CHANGE_TEMPLATE: ARTIFACT_PATH_CODEBASE_CHANGE_TEMPLATE,
        ARTIFACT_KEY_CODEBASE_INVENTORY: ARTIFACT_PATH_CODEBASE_INVENTORY,
        ARTIFACT_KEY_DELIVERY_FOLDER_MAP: ARTIFACT_PATH_DELIVERY_FOLDER_MAP,
        ARTIFACT_KEY_EXISTING_REPO_WORKFLOW_SOP: ARTIFACT_PATH_EXISTING_REPO_WORKFLOW_SOP,
    }


def known_artifact_paths() -> dict[str, str]:
    """Map artifact keys to their known repository-relative paths.

    This is used for auto-discovery of artifacts that exist on disk
    but are not yet in the job state (e.g., from previous workflow runs).
    """
    paths = {}
    # Master bootstrap docs (use get_master_docs_output_paths)
    paths.update(get_master_docs_output_paths())

    # Delivery scaffold docs
    paths.update(delivery_scaffold_docs())

    # Understanding docs (use ARTIFACT_PATH constants)
    paths[ARTIFACT_KEY_INTEGRATION_MAP] = ARTIFACT_PATH_INTEGRATION_MAP
    paths[ARTIFACT_KEY_FAILURE_MODES] = ARTIFACT_PATH_FAILURE_MODES
    paths[ARTIFACT_KEY_ARCHITECTURE_FLOW] = ARTIFACT_PATH_ARCHITECTURE_FLOW
    return paths


def all_artifact_keys() -> list[str]:
    """Return all canonical artifact key literals declared in this module."""
    keys: list[str] = []
    seen: set[str] = set()
    for name, value in globals().items():
        if not name.startswith("ARTIFACT_KEY_"):
            continue
        if not isinstance(value, str) or not value:
            continue
        if value in seen:
            continue
        seen.add(value)
        keys.append(value)
    return keys


def legacy_artifact_paths() -> dict[str, list[str]]:
    """Map artifact keys to legacy repository-relative paths."""
    return {
        ARTIFACT_KEY_PROJECT_ANALYSIS: [relpath("docs/system/00_governance/bootstrap", f"{ARTIFACT_KEY_PROJECT_ANALYSIS}{EXT_MD}")],
        ARTIFACT_KEY_DELIVERY_SOP: [relpath("docs/system/00_governance/bootstrap", f"{ARTIFACT_KEY_WORKFLOW_SOP}{EXT_MD}")],
        ARTIFACT_KEY_DELIVERY_STATUS_RULES: [relpath("docs/system/00_governance/bootstrap", f"{ARTIFACT_KEY_DELIVERY_STATUS_RULES}{EXT_MD}")],
        ARTIFACT_KEY_EXISTING_REPO_WORKFLOW_SOP: [relpath("docs/system/00_governance/bootstrap", f"{ARTIFACT_KEY_EXISTING_REPO_WORKFLOW_SOP}{EXT_MD}")],
        ARTIFACT_KEY_CODEBASE_DOC_SOP: [legacy_codebase_doc_rel("00_standards", f"{ARTIFACT_KEY_CODEBASE_DOC_SOP}{EXT_MD}")],
        ARTIFACT_KEY_CODEBASE_DOC_STATUS_RULES: [legacy_codebase_doc_rel("00_standards", f"{ARTIFACT_KEY_CODEBASE_DOC_STATUS_RULES}{EXT_MD}")],
        ARTIFACT_KEY_CODEBASE_INVENTORY: [legacy_codebase_doc_rel("01_inventory", f"{FILENAME_CODEBASE_INVENTORY}{EXT_MD}")],
        ARTIFACT_KEY_INTEGRATION_MAP: [legacy_codebase_doc_rel("01_inventory", f"{ARTIFACT_KEY_INTEGRATION_MAP}{EXT_MD}")],
        ARTIFACT_KEY_FAILURE_MODES: [legacy_codebase_doc_rel("01_inventory", f"{ARTIFACT_KEY_FAILURE_MODES}{EXT_MD}")],
        ARTIFACT_KEY_ARCHITECTURE_FLOW: [legacy_codebase_doc_rel("01_inventory", f"{ARTIFACT_KEY_ARCHITECTURE_FLOW}{EXT_MD}")],
        ARTIFACT_KEY_DELIVERY_AGENTS: [legacy_delivery_doc_rel("08_agents", f"{ARTIFACT_KEY_DELIVERY_AGENTS}{EXT_MD}")],
        ARTIFACT_KEY_DELIVERY_AGENT_PLANNER: [legacy_delivery_doc_rel("08_agents", f"{ARTIFACT_KEY_DELIVERY_AGENT_PLANNER}{EXT_MD}")],
        ARTIFACT_KEY_DELIVERY_AGENT_TASK_DECOMPOSER: [legacy_delivery_doc_rel("08_agents", f"{ARTIFACT_KEY_DELIVERY_AGENT_TASK_DECOMPOSER}{EXT_MD}")],
        ARTIFACT_KEY_DELIVERY_AGENT_IMPL_PLANNER: [legacy_delivery_doc_rel("08_agents", f"{ARTIFACT_KEY_DELIVERY_AGENT_IMPL_PLANNER}{EXT_MD}")],
        ARTIFACT_KEY_DELIVERY_AGENT_EXECUTOR: [legacy_delivery_doc_rel("08_agents", f"{ARTIFACT_KEY_DELIVERY_AGENT_EXECUTOR}{EXT_MD}")],
        ARTIFACT_KEY_DELIVERY_AGENT_REVIEWER: [legacy_delivery_doc_rel("08_agents", f"{ARTIFACT_KEY_DELIVERY_AGENT_REVIEWER}{EXT_MD}")],
        ARTIFACT_KEY_DELIVERY_AGENT_MEMORY_MANAGER: [legacy_delivery_doc_rel("08_agents", f"{ARTIFACT_KEY_DELIVERY_AGENT_MEMORY_MANAGER}{EXT_MD}")],
    }


PROMPT_LITERAL_ALIASES: dict[str, str] = {
    ARTIFACT_PATH_README: ARTIFACT_KEY_SYSTEM_DOCS_INDEX,
    ARTIFACT_PATH_DOCUMENTATION_STANDARD: ARTIFACT_KEY_SYSTEM_DOC_STANDARD,
}


def prompt_literal_substitutions() -> dict[str, str]:
    """Map known literal file paths to canonical prompt placeholders."""
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


SIDECAR_INSTRUCTION_TEMPLATE = """

===========================================================
CRITICAL: RESULT REPORTING REQUIREMENT (AUTOMATED INJECTION)
===========================================================

After completing your work, you MUST report results via meta.json sidecar.

**Sidecar path**: `{META_JSON_PATH}`

**Required steps**:
1. Write your artifact file(s) to disk using write_file tool
2. Verify each artifact file exists on disk
3. Create the meta.json sidecar using write_file tool with this EXACT structure:
   {{
     "schema_version": "v2",
     "coder_result": {{
       "status": "APPROVED" or "REJECTED",
       "remark": "Brief summary of what you accomplished",
       "artifacts": {{
         {ARTIFACT_ENTRIES}
       }},
       "recorded_at": "{CURRENT_TIMESTAMP}",
       "usage": {{
         "input_tokens": <number>,
         "output_tokens": <number>,
         "total_tokens": <number>
       }}
     }}
   }}
4. Verify meta.json exists on disk before finishing

**Status decision rule**:
- Return APPROVED only if ALL required artifacts exist on disk AND meta.json is written
- Return REJECTED if any artifact is missing or cannot be created

**Output format rule**:
- Return ONLY valid JSON matching this structure:
  {{
    "status": "APPROVED" or "REJECTED",
    "remark": "<summary>",
    "artifacts": {{
      {ARTIFACT_ENTRIES}
    }},
    "usage": {{
      "input_tokens": <number>,
      "output_tokens": <number>,
      "total_tokens": <number>
    }}
  }}
- Do NOT return markdown, explanations, or conversational text
- The runner reads results ONLY from meta.json and your JSON output
- If a path is absolute on Windows, use forward slashes in JSON strings
  Example: `D:/repo/docs/system/file.md`

**Valid example**:
{{
  "status": "APPROVED",
  "remark": "Wrote the required artifact and meta.json successfully.",
  "artifacts": {{
    {ARTIFACT_ENTRIES}
  }},
  "usage": {{
    "input_tokens": 1234,
    "output_tokens": 567,
    "total_tokens": 1801
  }}
}}

**Verification requirement**:
- You MUST verify files exist on disk before returning APPROVED
- Use exact artifact paths provided in context variables above

This requirement is MANDATORY - failure to follow these steps will cause workflow failure.
===========================================================
"""


ASCII_ONLY_INSTRUCTION = """

## Output Encoding Rule

All generated documents MUST use ASCII characters only.
- Use plain hyphens (-) for dashes. Do NOT use em-dashes or en-dashes.
- Use straight quotes (" and ') for quotations. Do NOT use curly quotes.
- Do NOT use any other Unicode characters (bullets, arrows, ellipsis, etc.).
- If your editor or model produces non-ASCII characters, replace them before writing.
- NEVER call sanitization tools on JSON files (meta.json, .meta.json, etc.) — only on .md documentation files if needed.
"""


SECTION_HEADING_RULE = r"""

## Section Heading Rule

Section headings (lines starting with #) MUST use plain text only.
- Do NOT add backticks, bold, italics, or other inline formatting to section headings.
- Section headings must match required names exactly as specified.
- Correct: `## Platform doc_type Values`
- Wrong: `## Platform \`doc_type\` Values` or `## **Platform doc_type Values**`
"""


GOVERNANCE_PATH_REFERENCE_RULE = """

## Governance Path Reference Rule

When referencing governance or platform documents in output, use filenames
only (e.g., METADATA_STANDARD.md, METADATA_CONTRACT.md). Do NOT include
resolved filesystem paths or repo-local directory paths.
"""


CODER_SOP_INSTRUCTION_TEMPLATE = """

===========================================================================
MANDATORY CODER SOP
===========================================================================
Before implementing any logic, read and follow:
{CODER_IMPLEMENTATION_SOP_PATH}

Minimum required behavior:
- Re-read the current source-of-truth files from disk before making decisions
- Inspect existing code paths before assuming runtime behavior
- Refactor duplicated execution logic toward one shared helper or transition path
- Do not add new parallel logic for workflow completion, failure, notifications, or artifacts
- Add or update tests proving all affected execution modes follow the same behavior

This SOP is repository-wide and applies to all coder backends for this step.
===========================================================================
"""


TOOL_INSTRUCTION_TEMPLATE = """

## Workflow Rules

You MUST use the tools below for EVERY step. Do NOT skip them. Do NOT answer directly without calling them first.

CRITICAL: Do NOT ask any clarifying questions. Do NOT ask for more info. Execute immediately using the tools.

Your step ID is: {STEP_NAME}

### create_todos(step_id, todos)
Call FIRST. Break the task into concrete steps, one record per todo.
Usage: {PYTHON_CMD} -c "import os; os.environ['PROGRESS_FILE']={PROGRESS_FILE_PY}; from agent_tools import create_todos; create_todos({STEP_NAME_PY}, ['Step 1', 'Step 2'])"

### mark_process(step_id, index, notes='')
Call immediately BEFORE starting each todo item. This inserts a `processing` status record.
Usage: {PYTHON_CMD} -c "import os; os.environ['PROGRESS_FILE']={PROGRESS_FILE_PY}; from agent_tools import mark_process; mark_process({STEP_NAME_PY}, 1, notes='Started')"

### mark_complete(step_id, index, notes='')
Call immediately AFTER finishing each todo item. This inserts a `completed` status record. 1-based index.
Usage: {PYTHON_CMD} -c "import os; os.environ['PROGRESS_FILE']={PROGRESS_FILE_PY}; from agent_tools import mark_complete; mark_complete({STEP_NAME_PY}, 1, notes='Done')"

## Mandatory Sequence
1. create_todos(step_id) - list all your steps first
2. Before starting todo item `i`, call mark_process(step_id, i)
3. Execute todo item `i`
4. After finishing todo item `i`, call mark_complete(step_id, i)
5. You MUST complete the full `pending -> processing -> completed` record sequence for every todo item before returning your final result

Example for a 3-step task:
  create_todos('{STEP_NAME}', ['Read input file', 'Generate output', 'Write result'])
  mark_process('{STEP_NAME}', 1, notes='Started reading input')
  mark_complete('{STEP_NAME}', 1, notes='File read successfully')
  mark_process('{STEP_NAME}', 2, notes='Started generating output')
  mark_complete('{STEP_NAME}', 2, notes='Output generated')
  mark_process('{STEP_NAME}', 3, notes='Started writing result')
  mark_complete('{STEP_NAME}', 3, notes='Result written to disk')

Actually call the functions with real arguments - do NOT just describe your answer."""


# ============================================================================
# Section Requirements
# ============================================================================
# Centralized section requirements for all generated documents.
# Keys use ARTIFACT_PATH constants for direct lookup during validation.

# System documentation section requirements
SYSTEM_DOC_SECTION_REQUIREMENTS: dict[str, list[str]] = {
    ARTIFACT_PATH_PROJECT_ANALYSIS: [
        "Repo Overview",
        "Codebase Structure",
        "Domain",
        "Tech Stack",
        "Complexity",
        "Recommended Workflow Scope",
        "Recommended Agent Roles",
        "Codebase Documentation Scope",
        "Documentation Freshness Risks",
        "Project-Specific SOP Considerations",
        "Operational Risks",
        "Architectural Observations",
        "Architecture Posture",
        "Discovered Files",
    ],
    ARTIFACT_PATH_DOCUMENTATION_STANDARD: [
        "Purpose",
        "Audience Model",
        "Document Set",
        "Update Triggers",
        "Validation",
        "Architecture Baseline",
        "Repo-Selected Profile",
        "Migration Mode",
        "Conditional Standards",
    ],
    ARTIFACT_PATH_README: [
        "System Documentation Index",
        "Audience Views",
        "Document Map",
    ],
    ARTIFACT_PATH_SYSTEM_OVERVIEW: [
        "Purpose",
        "Scope",
        "Primary Flows",
        "Key Risks",
        "Architecture Profile",
    ],
    ARTIFACT_PATH_BUSINESS_CAPABILITIES: [
        "Business Capabilities",
    ],
    ARTIFACT_PATH_FUNCTIONAL_SPEC: [
        "Functional Requirements",
    ],
    ARTIFACT_PATH_NON_FUNCTIONAL_REQUIREMENTS: [
        "Non-Functional Requirements",
    ],
    ARTIFACT_PATH_SYSTEM_CONTEXT: [
        "System Context",
    ],
    ARTIFACT_PATH_COMPONENT_ARCHITECTURE: [
        "Component Architecture",
    ],
    ARTIFACT_PATH_DECISION_LOG: [
        "Decision Log",
    ],
    ARTIFACT_PATH_SYSTEM_FILE_STRUCTURE: [
        "Repository Structure",
        "Top-Level Directories",
        "Documentation Locations",
    ],
    ARTIFACT_PATH_DEVELOPER_GUIDE: [
        "Development Workflow",
        "Key Commands",
        "Documentation Responsibilities",
        "Architecture Posture",
    ],
    ARTIFACT_PATH_RUNBOOK: [
        "Operations Scope",
        "Routine Procedures",
        "Failure Handling",
    ],
    ARTIFACT_PATH_EXISTING_REPO_WORKFLOW_SOP: [
        "Purpose",
        "First-Time Setup",
        "Normal Governed Delivery",
        "Drift Reconciliation",
        "Governance Refresh",
        "Batch Files",
        "Notes",
    ],
}

# Codebase documentation section requirements
CODEBASE_DOC_SECTION_REQUIREMENTS: dict[str, list[str]] = {
    ARTIFACT_PATH_CODEBASE_INVENTORY: [
        "Module Inventory",
    ],
}

# Delivery template section requirements (detailed)
DELIVERY_TEMPLATE_SECTION_REQUIREMENTS: dict[str, list[str]] = {
    ARTIFACT_PATH_DELIVERY_TEMPLATE_REGISTRY: [
        "Metadata",
        "Registry Overview",
        "Template Families",
        "Usage Rules",
        "Cross-References",
    ],
    ARTIFACT_PATH_DELIVERY_INITIATIVE_TEMPLATE: [
        "Metadata",
        "Initiative Description",
        "Scope",
        "Documentation Scope",
        "Dependencies",
        "Acceptance Criteria",
        "Notes",
    ],
    ARTIFACT_PATH_DELIVERY_PLAN_TEMPLATE: [
        "Metadata",
        "Plan Objective",
        "Strategy Overview",
        "Scope Mapping",
        "Task Breakdown",
        "Documentation Strategy",
        "Risks",
        "Deliverables",
        "Acceptance Criteria",
        "Notes",
    ],
    ARTIFACT_PATH_DELIVERY_TASK_GRAPH_TEMPLATE: [
        "Metadata",
        "Task Graph Objective",
        "Task Graph",
        "Execution Flow",
        "Documentation Workstream",
        "Success Criteria",
        "Notes",
    ],
    ARTIFACT_PATH_DELIVERY_TASK_TEMPLATE: [
        "Metadata",
        "Objective",
        "Inputs",
        "Outputs",
        "Execution Steps",
        "Validation Criteria",
        "Documentation Impact",
        "Dependencies",
        "Notes",
    ],
    ARTIFACT_PATH_DELIVERY_IMPL_TEMPLATE: [
        "Metadata",
        "Implementation Objective",
        "Changes Overview",
        "Implementation Steps",
        "Documentation Update Plan",
        "Risk Assessment",
        "Validation Criteria",
        "Notes",
    ],
    ARTIFACT_PATH_DELIVERY_REVIEW_TEMPLATE: [
        "Metadata",
        "Review Scope",
        "Findings",
        "Documentation Compliance",
        "Verdict",
        "Notes",
    ],
    ARTIFACT_PATH_DELIVERY_VALIDATION_TEMPLATE: [
        "Metadata",
        "Validation Scope",
        "Code Validation",
        "Documentation Synchronization Validation",
        "Validation Issues",
        "Validation Summary",
        "Verdict",
        "Approval",
        "Notes",
    ],
    ARTIFACT_PATH_DELIVERY_MEMORY_TEMPLATE: [
        "Metadata",
        "Context",
        "Lessons Learned",
        "Reusable Patterns",
        "Anti-Patterns",
        "Documentation Notes",
        "Related Memories",
        "Notes",
    ],
}

# Codebase template section requirements
CODEBASE_TEMPLATE_SECTION_REQUIREMENTS: dict[str, list[str]] = {
    ARTIFACT_PATH_CODEBASE_TEMPLATE_REGISTRY: [
        "Template Registry",
    ],
    ARTIFACT_PATH_CODEBASE_INVENTORY_TEMPLATE: [
        "Inventory Template",
    ],
    ARTIFACT_PATH_CODEBASE_MODULE_TEMPLATE: [
        "Module Template",
    ],
    ARTIFACT_PATH_CODEBASE_COMPONENT_TEMPLATE: [
        "Component Template",
    ],
    ARTIFACT_PATH_CODEBASE_CHANGE_TEMPLATE: [
        "Change Template",
    ],
}

# SOP and status rules section requirements (list constants)
DELIVERY_SOP_REQUIRED_SECTIONS = [
    "Purpose",
    "Core Principle",
    "Authority Precedence",
    "Workflow State Machine",
    "Agent Roles",
    "Workflow Phases",
    "Standard Rules",
    "Folder Structure",
    "Validation",
]

DELIVERY_STATUS_RULES_REQUIRED_SECTIONS = [
    "Core Principles",
    "Global Workflow Discipline",
    "Lifecycle Rules",
    "Authority Model",
    "Approval Gates",
    "Forbidden Transitions",
    "Document-First",
    "Traceability",
]

CODEBASE_SOP_REQUIRED_SECTIONS = [
    "Purpose",
    "Coverage Model",
    "Documentation Modes",
    "Freshness Rules",
    "Stale Content Policy",
    "Workflow Integration",
    "File-Type Rules",
    "Validation",
]

CODEBASE_STATUS_RULES_REQUIRED_SECTIONS = [
    "Core Principles",
    "Inventory Status Model",
    "Document Status Model",
    "Supersession Rules",
    "Update Triggers",
    "Traceability",
    "Removal Rules",
]

# SOP and status rules section requirements (combined dictionary)
SOP_AND_STATUS_RULES_REQUIREMENTS: dict[str, list[str]] = {
    ARTIFACT_PATH_WORKFLOW_SOP: DELIVERY_SOP_REQUIRED_SECTIONS,
    ARTIFACT_PATH_DELIVERY_STATUS_RULES: DELIVERY_STATUS_RULES_REQUIRED_SECTIONS,
    ARTIFACT_PATH_CODEBASE_DOC_SOP: CODEBASE_SOP_REQUIRED_SECTIONS,
    ARTIFACT_PATH_CODEBASE_DOC_STATUS_RULES: CODEBASE_STATUS_RULES_REQUIRED_SECTIONS,
}


# ============================================================================
# Shared SDLC Constants
# ============================================================================
# Common base paths used across all SDLC workflow packages.
# Workflows reference these instead of hardcoding path strings.

SDLC_DELIVERY_BASE = "docs/repo/agent_runner/sdlc/delivery"


# ============================================================================
# Global Artifact Path Registry
# ============================================================================
# Runtime-populated dict that maps artifact keys to repo-relative paths.
# Populated by workflow_packages/hooks.py when workflows register their
# artifact keys via WorkflowExtensions.register_artifact_keys().
#
# This is the single lookup table for artifact path resolution at runtime.

ARTIFACT_PATHS: dict[str, str] = {}


def register_artifact_paths(paths: dict[str, str]) -> None:
    """Merge workflow-contributed paths into the global registry.

    Called by the scanner (workflow_packages/hooks.py) when a workflow's
    ``register_artifact_keys()`` hook returns path mappings.

    Parameters:
        paths: Dict mapping artifact key strings to repo-relative
            path templates.
    """
    ARTIFACT_PATHS.update(paths)


def get_artifact_path(key: str, default: str = "") -> str:
    """Look up an artifact path from the global registry.

    Parameters:
        key: Artifact key (e.g. ``"INIT_FILE"``).
        default: Value to return when the key is not registered.

    Returns:
        The repo-relative path template, or *default* if not found.
    """
    return ARTIFACT_PATHS.get(key, default)


# ============================================================================
# SDLC Sequence Number Resolution
# ============================================================================

def resolve_next_seq(directory: Path, prefix: str) -> str:
    """Scan *directory* for ``.md`` files starting with *prefix*.

    Extracts the sequence number from the segment immediately before the
    ``_slug`` part of each filename and returns the next available number
    as a zero-padded 3-digit string.

    Examples::

        # BACKLOG-20260723-001_console-sdlc10-support.md  → seq 001
        # BACKLOG-20260723-002_console-sdlc10-support.md  → seq 002
        resolve_next_seq(dir, "BACKLOG-20260723-") → "003"

        # IMPL-20260723-001-003_console-sdlc10-support.md → seq 003
        resolve_next_seq(dir, "IMPL-20260723-") → "004"

    Parameters:
        directory: Target directory to scan.
        prefix: Filename prefix including the date (e.g. ``"BACKLOG-20260723-"``).

    Returns:
        Next 3-digit zero-padded sequence number (``"001"`` when no
        matching files exist).
    """
    import re
    max_seq = 0
    if directory.is_dir():
        for f in directory.iterdir():
            if f.suffix != ".md":
                continue
            if not f.name.startswith(prefix):
                continue
            # Find the segment containing '_' and extract digits before it
            stem = f.stem
            parts = stem.split("-")
            for part in reversed(parts):
                if "_" in part:
                    num_str = part.split("_")[0]
                    if num_str.isdigit():
                        max_seq = max(max_seq, int(num_str))
                    break
    return str(max_seq + 1).zfill(3)


# ============================================================================
# SDLC Slug Extraction
# ============================================================================

def extract_slug_from_path(file_path: str) -> str:
    """Extract the slug from an SDLC artifact filename.

    Pattern: ``{TYPE}-{date}-{seq}_{slug}.md`` → returns ``{slug}``.
    Falls back to the filename stem (e.g. ``"my-workflow-spec"``),
    then to ``"unknown"`` if the path is empty.

    Examples::

        extract_slug_from_path(".../INIT-20260722-001_console-sdlc10-support.md")
        → "console-sdlc10-support"

        extract_slug_from_path(".../specs/agnes-media-gen-v1.md")
        → "agnes-media-gen-v1"

        extract_slug_from_path("")
        → "unknown"

    Parameters:
        file_path: Path or filename string to extract the slug from.

    Returns:
        The slug substring after the last ``_``, the filename stem, or ``"unknown"``.
    """
    import re
    if not file_path:
        return "unknown"
    filename = Path(file_path).stem
    if not filename:
        return "unknown"
    match = re.search(r"_(.+)$", filename)
    if match:
        return match.group(1)
    return filename
