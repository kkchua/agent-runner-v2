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

# Architecture site HTML filenames
FILENAME_ARCH_STAKEHOLDER_HTML = "stakeholders.html"
FILENAME_ARCH_DEVELOPER_HTML = "developers.html"
FILENAME_ARCH_FUNCTIONAL_HTML = "functional.html"
FILENAME_ARCH_RUNTIME_HTML = "runtime.html"
FILENAME_ARCH_COMPONENTS_HTML = "components.html"
FILENAME_ARCH_VALIDATION_MD = "validation.md"

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
ARTIFACT_KEY_REVIEW = "REVIEW_FILE"
ARTIFACT_KEY_VALIDATION = "VALIDATION_FILE"
ARTIFACT_KEY_CONTEXT_PACK = "CONTEXT_PACK_FILE"

# Image processing artifacts
ARTIFACT_KEY_IMAGE = "IMAGE_FILE"
ARTIFACT_KEY_IMAGE_FOLDER = "IMAGE_FOLDER"
ARTIFACT_KEY_IMAGE_DESC_FOLDER = "IMAGE_DESC_FOLDER"
ARTIFACT_KEY_IMAGE_CSV_JSON = "IMAGE_CSV_JSON"
ARTIFACT_KEY_IMAGE_CSV_CSV = "IMAGE_CSV_CSV"
ARTIFACT_KEY_IMAGE_CSV_SUBMIT_RESULT = "IMAGE_CSV_SUBMIT_RESULT"

# VideoExpress workflow artifacts
ARTIFACT_KEY_NARRATIVE = "NARRATIVE_FILE"
ARTIFACT_KEY_VIDEOWORKFLOW = "VIDEOWORKFLOW_FILE"
ARTIFACT_KEY_GENERATED_IMAGES = "GENERATED_IMAGES_FOLDER"
ARTIFACT_KEY_GENERATED_VIDEO_CLIPS = "GENERATED_VIDEO_CLIPS"
ARTIFACT_KEY_GENERATED_AUDIO = "GENERATED_AUDIO_FOLDER"
ARTIFACT_KEY_FINAL_VIDEO = "FINAL_VIDEO_FILE"

# TikTok pipeline artifacts
ARTIFACT_KEY_USER_INPUT = "USER_INPUT"
ARTIFACT_KEY_BRIEF_JSON = "BRIEF_JSON"
ARTIFACT_KEY_WORKFLOW_JSON = "WORKFLOW_JSON"
ARTIFACT_KEY_IMAGE_SUBMIT_RESULT = "IMAGE_SUBMIT_RESULT"
ARTIFACT_KEY_VIDEO_SUBMIT_RESULT = "VIDEO_SUBMIT_RESULT"
ARTIFACT_KEY_AUDIO_SUBMIT_RESULT = "AUDIO_SUBMIT_RESULT"
ARTIFACT_KEY_FINAL_VIDEO_TIKTOK = "FINAL_VIDEO"

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

# Bug fix artifacts
ARTIFACT_KEY_BUG_DRAFT = "BUG_DRAFT_FILE"
ARTIFACT_KEY_BUG_REPORT = "BUG_REPORT_FILE"
ARTIFACT_KEY_REPRO = "REPRO_FILE"
ARTIFACT_KEY_ROOT_CAUSE = "ROOT_CAUSE_FILE"
ARTIFACT_KEY_PATCH = "PATCH_FILE"

# Documentation site artifacts
ARTIFACT_KEY_ARCHITECTURE_SITE_INDEX = "ARCHITECTURE_SITE_INDEX"
ARTIFACT_KEY_ARCHITECTURE_SITE_MANIFEST = "ARCHITECTURE_SITE_MANIFEST"

# Markdown source files (LLM-generated)
ARTIFACT_KEY_STAKEHOLDER_SITE_MARKDOWN = "STAKEHOLDER_SITE_MARKDOWN"
ARTIFACT_KEY_DEVELOPER_SITE_MARKDOWN = "DEVELOPER_SITE_MARKDOWN"
ARTIFACT_KEY_OPERATOR_SITE_MARKDOWN = "OPERATOR_SITE_MARKDOWN"
ARTIFACT_KEY_TESTER_SITE_MARKDOWN = "TESTER_SITE_MARKDOWN"
ARTIFACT_KEY_USER_SITE_MARKDOWN = "USER_SITE_MARKDOWN"

# HTML output files (generated from markdown)
ARTIFACT_KEY_STAKEHOLDER_SITE_INDEX = "STAKEHOLDER_SITE_INDEX"
ARTIFACT_KEY_DEVELOPER_SITE_INDEX = "DEVELOPER_SITE_INDEX"
ARTIFACT_KEY_OPERATOR_SITE_INDEX = "OPERATOR_SITE_INDEX"
ARTIFACT_KEY_TESTER_SITE_INDEX = "TESTER_SITE_INDEX"
ARTIFACT_KEY_USER_SITE_INDEX = "USER_SITE_INDEX"

# PDF output files (generated from HTML, if configured)
ARTIFACT_KEY_STAKEHOLDER_SITE_PDF = "STAKEHOLDER_SITE_PDF"
ARTIFACT_KEY_DEVELOPER_SITE_PDF = "DEVELOPER_SITE_PDF"
ARTIFACT_KEY_OPERATOR_SITE_PDF = "OPERATOR_SITE_PDF"
ARTIFACT_KEY_TESTER_SITE_PDF = "TESTER_SITE_PDF"
ARTIFACT_KEY_USER_SITE_PDF = "USER_SITE_PDF"

# Site manifest files
ARTIFACT_KEY_STAKEHOLDER_SITE_MANIFEST = "STAKEHOLDER_SITE_MANIFEST"
ARTIFACT_KEY_DEVELOPER_SITE_MANIFEST = "DEVELOPER_SITE_MANIFEST"
ARTIFACT_KEY_OPERATOR_SITE_MANIFEST = "OPERATOR_SITE_MANIFEST"
ARTIFACT_KEY_TESTER_SITE_MANIFEST = "TESTER_SITE_MANIFEST"
ARTIFACT_KEY_USER_SITE_MANIFEST = "USER_SITE_MANIFEST"

# ============================================================================
# Folder Key Constants
# ============================================================================
# These constants define base directory paths for different artifact categories.
# They are combined with artifact keys to construct full paths.
#
# Usage: artifact_path(ARTIFACT_KEY_PROJECT_ANALYSIS, FOLDER_KEY_SYSTEM_BOOTSTRAP)

# Base directory folders (correspond to doc_paths.py constants)
FOLDER_KEY_DOCS = "docs"
FOLDER_KEY_SYSTEM_DOC_ROOT = "docs/system/00_governance/bootstrap"
FOLDER_KEY_SYSTEM_TEMPLATE_ROOT = "docs/system/00_governance/bootstrap/templates"
FOLDER_KEY_SYSTEM_DELIVERY_TEMPLATE_ROOT = "docs/system/00_governance/bootstrap/templates/delivery"
FOLDER_KEY_SYSTEM_CODEBASE_TEMPLATE_ROOT = "docs/system/00_governance/bootstrap/templates/codebase"
FOLDER_KEY_CODEBASE_DOC_ROOT = "docs/codebase"
FOLDER_KEY_DELIVERY_DOC_ROOT = "docs/delivery"
FOLDER_KEY_DOCS_SITE_ROOT = "docs/site"
FOLDER_KEY_ARCHITECTURE_SITE_ROOT = "docs/site"  # Legacy alias
FOLDER_KEY_STAKEHOLDER_SITE_ROOT = "docs/site/stakeholders"
FOLDER_KEY_DEVELOPER_SITE_ROOT = "docs/site/developers"
FOLDER_KEY_OPERATOR_SITE_ROOT = "docs/site/operators"
FOLDER_KEY_TESTER_SITE_ROOT = "docs/site/testers"
FOLDER_KEY_USER_SITE_ROOT = "docs/site/users"

# Bootstrap folders (where 00_master_docs_bootstrap_v1 writes during development)
FOLDER_KEY_SYSTEM_BOOTSTRAP = "docs/system/00_governance/bootstrap"
FOLDER_KEY_CODEBASE_INVENTORY = "docs/codebase/01_inventory"
FOLDER_KEY_CODEBASE_CHANGES = "docs/codebase/04_changes"
FOLDER_KEY_CODEBASE_MODULES = "docs/codebase/02_modules"
FOLDER_KEY_CODEBASE_COMPONENTS = "docs/codebase/03_components"
FOLDER_KEY_CODEBASE_STANDARDS = "docs/codebase/00_standards"

# Delivery folders (where 10_execution_scaffold_v1 writes)
FOLDER_KEY_DELIVERY_DOC_ROOT = "docs/delivery"
FOLDER_KEY_DELIVERY_STANDARDS = "docs/delivery/00_standards"
FOLDER_KEY_DELIVERY_INITIATIVES = "docs/delivery/01_initiatives"
FOLDER_KEY_DELIVERY_PLANS = "docs/delivery/02_plans"
FOLDER_KEY_DELIVERY_TASKS = "docs/delivery/03_tasks"
FOLDER_KEY_DELIVERY_IMPLEMENTATIONS = "docs/delivery/04_implementation_plans"
FOLDER_KEY_DELIVERY_REVIEWS = "docs/delivery/05_reviews"
FOLDER_KEY_DELIVERY_VALIDATIONS = "docs/delivery/06_validations"
FOLDER_KEY_DELIVERY_MEMORY = "docs/delivery/07_memory"
FOLDER_KEY_DELIVERY_AGENTS = "docs/delivery/08_agents"
FOLDER_KEY_DELIVERY_TEMPLATES = "docs/system/00_governance/bootstrap/templates/delivery"
FOLDER_KEY_CODEBASE_TEMPLATES = "docs/system/00_governance/bootstrap/templates/codebase"

# Runtime global folders (after ukbe-run-agent init copies bootstrap to ~/.ukbe-runner)
# These will be resolved at runtime using the global runner home path
FOLDER_KEY_GLOBAL_BUNDLES = "~/.ukbe-runner/bundles/core/current"

# Architecture site folders
FOLDER_KEY_DOCS_SITE = "docs/site"
FOLDER_KEY_STAKEHOLDER_SITE = "docs/site/stakeholders"
FOLDER_KEY_DEVELOPER_SITE = "docs/site/developers"
FOLDER_KEY_OPERATOR_SITE = "docs/site/operators"
FOLDER_KEY_TESTER_SITE = "docs/site/testers"
FOLDER_KEY_USER_SITE = "docs/site/users"

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


# ============================================================================
# Pre-computed Artifact Path Constants
# ============================================================================
# These are computed from ARTIFACT_KEY + FOLDER_KEY using artifact_path().
# No hardcoded strings - all paths derived from constants.

# System documentation paths (bootstrap)
ARTIFACT_PATH_PROJECT_ANALYSIS = artifact_path(ARTIFACT_KEY_PROJECT_ANALYSIS, FOLDER_KEY_SYSTEM_BOOTSTRAP)
ARTIFACT_PATH_README = artifact_path(ARTIFACT_KEY_README, FOLDER_KEY_SYSTEM_BOOTSTRAP)
ARTIFACT_PATH_DOCUMENTATION_STANDARD = artifact_path(ARTIFACT_KEY_DOCUMENTATION_STANDARD, FOLDER_KEY_SYSTEM_BOOTSTRAP)
ARTIFACT_PATH_BUNDLE_TAXONOMY = artifact_path(ARTIFACT_KEY_BUNDLE_TAXONOMY, FOLDER_KEY_SYSTEM_BOOTSTRAP)
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
ARTIFACT_PATH_EXISTING_REPO_WORKFLOW_SOP = artifact_path(ARTIFACT_KEY_EXISTING_REPO_WORKFLOW_SOP, FOLDER_KEY_SYSTEM_BOOTSTRAP)

# System governance paths (additional)
ARTIFACT_PATH_DELIVERY_STATUS_RULES = artifact_path(ARTIFACT_KEY_DELIVERY_STATUS_RULES, FOLDER_KEY_SYSTEM_BOOTSTRAP)
ARTIFACT_PATH_WORKFLOW_SOP = artifact_path(ARTIFACT_KEY_WORKFLOW_SOP, FOLDER_KEY_SYSTEM_BOOTSTRAP)

# Codebase documentation paths
ARTIFACT_PATH_CODEBASE_INVENTORY = artifact_path(FILENAME_CODEBASE_INVENTORY, FOLDER_KEY_CODEBASE_INVENTORY)
ARTIFACT_PATH_INTEGRATION_MAP = artifact_path(ARTIFACT_KEY_INTEGRATION_MAP, FOLDER_KEY_CODEBASE_INVENTORY)
ARTIFACT_PATH_FAILURE_MODES = artifact_path(ARTIFACT_KEY_FAILURE_MODES, FOLDER_KEY_CODEBASE_INVENTORY)
ARTIFACT_PATH_ARCHITECTURE_FLOW = artifact_path(ARTIFACT_KEY_ARCHITECTURE_FLOW, FOLDER_KEY_CODEBASE_INVENTORY)
ARTIFACT_PATH_CODEBASE_DOC_SOP = artifact_path(ARTIFACT_KEY_CODEBASE_DOC_SOP, FOLDER_KEY_CODEBASE_STANDARDS)
ARTIFACT_PATH_CODEBASE_DOC_STATUS_RULES = artifact_path(ARTIFACT_KEY_CODEBASE_DOC_STATUS_RULES, FOLDER_KEY_CODEBASE_STANDARDS)

# Delivery documentation paths
ARTIFACT_PATH_DELIVERY_AGENTS = artifact_path(ARTIFACT_KEY_DELIVERY_AGENTS, FOLDER_KEY_SYSTEM_BOOTSTRAP)
ARTIFACT_PATH_DELIVERY_AGENT_PLANNER = artifact_path(ARTIFACT_KEY_DELIVERY_AGENT_PLANNER, FOLDER_KEY_SYSTEM_BOOTSTRAP)
ARTIFACT_PATH_DELIVERY_AGENT_TASK_DECOMPOSER = artifact_path(ARTIFACT_KEY_DELIVERY_AGENT_TASK_DECOMPOSER, FOLDER_KEY_SYSTEM_BOOTSTRAP)
ARTIFACT_PATH_DELIVERY_AGENT_IMPL_PLANNER = artifact_path(ARTIFACT_KEY_DELIVERY_AGENT_IMPL_PLANNER, FOLDER_KEY_SYSTEM_BOOTSTRAP)
ARTIFACT_PATH_DELIVERY_AGENT_EXECUTOR = artifact_path(ARTIFACT_KEY_DELIVERY_AGENT_EXECUTOR, FOLDER_KEY_SYSTEM_BOOTSTRAP)
ARTIFACT_PATH_DELIVERY_AGENT_REVIEWER = artifact_path(ARTIFACT_KEY_DELIVERY_AGENT_REVIEWER, FOLDER_KEY_SYSTEM_BOOTSTRAP)
ARTIFACT_PATH_DELIVERY_AGENT_MEMORY_MANAGER = artifact_path(ARTIFACT_KEY_DELIVERY_AGENT_MEMORY_MANAGER, FOLDER_KEY_SYSTEM_BOOTSTRAP)
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

# Architecture site paths
ARTIFACT_PATH_ARCHITECTURE_SITE_INDEX = f"{FOLDER_KEY_DOCS_SITE}/{FILENAME_SITE_INDEX_HTML}"
ARTIFACT_PATH_STAKEHOLDER_SITE_INDEX = f"{FOLDER_KEY_STAKEHOLDER_SITE}/{FILENAME_SITE_INDEX_HTML}"
ARTIFACT_PATH_DEVELOPER_SITE_INDEX = f"{FOLDER_KEY_DEVELOPER_SITE}/{FILENAME_SITE_INDEX_HTML}"
ARTIFACT_PATH_OPERATOR_SITE_INDEX = f"{FOLDER_KEY_OPERATOR_SITE}/{FILENAME_SITE_INDEX_HTML}"
ARTIFACT_PATH_TESTER_SITE_INDEX = f"{FOLDER_KEY_TESTER_SITE}/{FILENAME_SITE_INDEX_HTML}"
ARTIFACT_PATH_USER_SITE_INDEX = f"{FOLDER_KEY_USER_SITE}/{FILENAME_SITE_INDEX_HTML}"
ARTIFACT_PATH_STAKEHOLDER_SITE_MARKDOWN = f"{FOLDER_KEY_STAKEHOLDER_SITE}/{FILENAME_SITE_CONTENT_MD}"
ARTIFACT_PATH_DEVELOPER_SITE_MARKDOWN = f"{FOLDER_KEY_DEVELOPER_SITE}/{FILENAME_SITE_CONTENT_MD}"
ARTIFACT_PATH_OPERATOR_SITE_MARKDOWN = f"{FOLDER_KEY_OPERATOR_SITE}/{FILENAME_SITE_CONTENT_MD}"
ARTIFACT_PATH_TESTER_SITE_MARKDOWN = f"{FOLDER_KEY_TESTER_SITE}/{FILENAME_SITE_CONTENT_MD}"
ARTIFACT_PATH_USER_SITE_MARKDOWN = f"{FOLDER_KEY_USER_SITE}/{FILENAME_SITE_CONTENT_MD}"


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
    "CODEBASE_DOC_STATUS_RULES": ARTIFACT_PATH_CODEBASE_DOC_STATUS_RULES,
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
        ARTIFACT_KEY_PROJECT_ANALYSIS: artifact_path(ARTIFACT_KEY_PROJECT_ANALYSIS, FOLDER_KEY_SYSTEM_BOOTSTRAP),
        ARTIFACT_KEY_SYSTEM_DOCS_INDEX: artifact_path(ARTIFACT_KEY_README, FOLDER_KEY_SYSTEM_BOOTSTRAP),
        ARTIFACT_KEY_SYSTEM_DOCS_CHANGE_LOG: f"{FOLDER_KEY_SYSTEM_BOOTSTRAP}/{FILENAME_CHANGE_LOG_PATTERN.format(job_id=job_id, mode=mode)}{EXT_MD}",
        ARTIFACT_KEY_SYSTEM_DOCS_VALIDATION: f"{FOLDER_KEY_SYSTEM_BOOTSTRAP}/{FILENAME_VALIDATION_PATTERN.format(job_id=job_id, mode=mode)}{EXT_MD}",
        ARTIFACT_KEY_SYSTEM_DOC_STANDARD: artifact_path(ARTIFACT_KEY_DOCUMENTATION_STANDARD, FOLDER_KEY_SYSTEM_BOOTSTRAP),
        ARTIFACT_KEY_BUNDLE_TAXONOMY: artifact_path(ARTIFACT_KEY_BUNDLE_TAXONOMY, FOLDER_KEY_SYSTEM_BOOTSTRAP),
        ARTIFACT_KEY_BUNDLE_MIGRATION_PLAN: artifact_path(ARTIFACT_KEY_BUNDLE_MIGRATION_PLAN, FOLDER_KEY_SYSTEM_BOOTSTRAP),
        ARTIFACT_KEY_SYSTEM_OVERVIEW: artifact_path(ARTIFACT_KEY_SYSTEM_OVERVIEW, FOLDER_KEY_SYSTEM_BOOTSTRAP),
        ARTIFACT_KEY_BUSINESS_CAPABILITIES: artifact_path(ARTIFACT_KEY_BUSINESS_CAPABILITIES, FOLDER_KEY_SYSTEM_BOOTSTRAP),
        ARTIFACT_KEY_FUNCTIONAL_SPEC: artifact_path(ARTIFACT_KEY_FUNCTIONAL_SPEC, FOLDER_KEY_SYSTEM_BOOTSTRAP),
        ARTIFACT_KEY_NON_FUNCTIONAL_REQUIREMENTS: artifact_path(ARTIFACT_KEY_NON_FUNCTIONAL_REQUIREMENTS, FOLDER_KEY_SYSTEM_BOOTSTRAP),
        ARTIFACT_KEY_SYSTEM_CONTEXT: artifact_path(ARTIFACT_KEY_SYSTEM_CONTEXT, FOLDER_KEY_SYSTEM_BOOTSTRAP),
        ARTIFACT_KEY_COMPONENT_ARCHITECTURE: artifact_path(ARTIFACT_KEY_COMPONENT_ARCHITECTURE, FOLDER_KEY_SYSTEM_BOOTSTRAP),
        ARTIFACT_KEY_DECISION_LOG: artifact_path(ARTIFACT_KEY_DECISION_LOG, FOLDER_KEY_SYSTEM_BOOTSTRAP),
        ARTIFACT_KEY_SYSTEM_FILE_STRUCTURE: artifact_path(ARTIFACT_KEY_SYSTEM_FILE_STRUCTURE, FOLDER_KEY_SYSTEM_BOOTSTRAP),
        ARTIFACT_KEY_DEVELOPER_GUIDE: artifact_path(ARTIFACT_KEY_DEVELOPER_GUIDE, FOLDER_KEY_SYSTEM_BOOTSTRAP),
        ARTIFACT_KEY_RUNBOOK: artifact_path(ARTIFACT_KEY_RUNBOOK, FOLDER_KEY_SYSTEM_BOOTSTRAP),
        ARTIFACT_KEY_EXISTING_REPO_WORKFLOW_SOP: artifact_path(ARTIFACT_KEY_EXISTING_REPO_WORKFLOW_SOP, FOLDER_KEY_SYSTEM_BOOTSTRAP),
        ARTIFACT_KEY_BOOTSTRAP_SUMMARY: f"{FOLDER_KEY_SYSTEM_BOOTSTRAP}/{FILENAME_BOOTSTRAP_SUMMARY_PATTERN.format(job_id=job_id)}{EXT_MD}",
        ARTIFACT_KEY_CODEBASE_SCAN_SNAPSHOT: f"{FOLDER_KEY_CODEBASE_CHANGES}/{FILENAME_SNAPSHOT_PATTERN.format(job_id=job_id, mode=mode)}{EXT_JSON}",
    }


# ============================================================================
# Path Helper Functions (from doc_paths.py)
# ============================================================================
# These functions construct paths dynamically using base folder constants.

from pathlib import PurePosixPath

def _rel(*parts: str) -> str:
    """Convert path parts to POSIX-style string."""
    return PurePosixPath(*parts).as_posix()


def system_doc_rel(*parts: str) -> str:
    """Get path relative to SYSTEM_DOC_ROOT."""
    return _rel(*(PurePosixPath(FOLDER_KEY_SYSTEM_DOC_ROOT).parts + parts))


def codebase_doc_rel(*parts: str) -> str:
    """Get path relative to CODEBASE_DOC_ROOT."""
    return _rel(*(PurePosixPath(FOLDER_KEY_CODEBASE_DOC_ROOT).parts + parts))


def delivery_doc_rel(*parts: str) -> str:
    """Get path relative to DELIVERY_DOC_ROOT."""
    return _rel(*(PurePosixPath(FOLDER_KEY_DELIVERY_DOC_ROOT).parts + parts))


def system_delivery_template_rel(*parts: str) -> str:
    """Get path relative to SYSTEM_DELIVERY_TEMPLATE_ROOT."""
    return _rel(*(PurePosixPath(FOLDER_KEY_SYSTEM_DELIVERY_TEMPLATE_ROOT).parts + parts))


def system_codebase_template_rel(*parts: str) -> str:
    """Get path relative to SYSTEM_CODEBASE_TEMPLATE_ROOT."""
    return _rel(*(PurePosixPath(FOLDER_KEY_SYSTEM_CODEBASE_TEMPLATE_ROOT).parts + parts))


def docs_site_rel(*parts: str) -> str:
    """Get path relative to DOCS_SITE_ROOT."""
    return _rel(*(PurePosixPath(FOLDER_KEY_DOCS_SITE_ROOT).parts + parts))


def stakeholder_site_rel(*parts: str) -> str:
    """Get path relative to STAKEHOLDER_SITE_ROOT."""
    return _rel(*(PurePosixPath(FOLDER_KEY_STAKEHOLDER_SITE_ROOT).parts + parts))


def developer_site_rel(*parts: str) -> str:
    """Get path relative to DEVELOPER_SITE_ROOT."""
    return _rel(*(PurePosixPath(FOLDER_KEY_DEVELOPER_SITE_ROOT).parts + parts))


def operator_site_rel(*parts: str) -> str:
    """Get path relative to OPERATOR_SITE_ROOT."""
    return _rel(*(PurePosixPath(FOLDER_KEY_OPERATOR_SITE_ROOT).parts + parts))


def tester_site_rel(*parts: str) -> str:
    """Get path relative to TESTER_SITE_ROOT."""
    return _rel(*(PurePosixPath(FOLDER_KEY_TESTER_SITE_ROOT).parts + parts))


def user_site_rel(*parts: str) -> str:
    """Get path relative to USER_SITE_ROOT."""
    return _rel(*(PurePosixPath(FOLDER_KEY_USER_SITE_ROOT).parts + parts))


def repo_doc_rel(*parts: str) -> str:
    """Get path relative to DOCS_ROOT (docs/ folder)."""
    return _rel(*(PurePosixPath(FOLDER_KEY_DOCS).parts + parts))


def docs_root_rel(*parts: str) -> str:
    """Get path relative to DOCS_ROOT (docs/ folder) - alias for repo_doc_rel."""
    return repo_doc_rel(*parts)


def system_template_rel(*parts: str) -> str:
    """Get path relative to SYSTEM_TEMPLATE_ROOT."""
    return _rel(*(PurePosixPath(FOLDER_KEY_SYSTEM_TEMPLATE_ROOT).parts + parts))


def architecture_site_rel(*parts: str) -> str:
    """Get path relative to ARCHITECTURE_SITE_ROOT (legacy alias for DOCS_SITE_ROOT)."""
    return docs_site_rel(*parts)


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


def audience_site_artifacts() -> dict[str, str]:
    """Map artifact keys to their paths for all audience sites."""
    return {
        ARTIFACT_KEY_ARCHITECTURE_SITE_INDEX: docs_site_rel(FILENAME_SITE_INDEX_HTML),
        ARTIFACT_KEY_ARCHITECTURE_SITE_MANIFEST: docs_site_rel(FILENAME_SITE_MANIFEST_JSON),
        # Markdown source files (LLM-generated)
        ARTIFACT_KEY_STAKEHOLDER_SITE_MARKDOWN: stakeholder_site_rel(FILENAME_SITE_CONTENT_MD),
        ARTIFACT_KEY_DEVELOPER_SITE_MARKDOWN: developer_site_rel(FILENAME_SITE_CONTENT_MD),
        ARTIFACT_KEY_OPERATOR_SITE_MARKDOWN: operator_site_rel(FILENAME_SITE_CONTENT_MD),
        ARTIFACT_KEY_TESTER_SITE_MARKDOWN: tester_site_rel(FILENAME_SITE_CONTENT_MD),
        ARTIFACT_KEY_USER_SITE_MARKDOWN: user_site_rel(FILENAME_SITE_CONTENT_MD),
        # HTML output files (generated from markdown)
        ARTIFACT_KEY_STAKEHOLDER_SITE_INDEX: stakeholder_site_rel(FILENAME_SITE_INDEX_HTML),
        ARTIFACT_KEY_DEVELOPER_SITE_INDEX: developer_site_rel(FILENAME_SITE_INDEX_HTML),
        ARTIFACT_KEY_OPERATOR_SITE_INDEX: operator_site_rel(FILENAME_SITE_INDEX_HTML),
        ARTIFACT_KEY_TESTER_SITE_INDEX: tester_site_rel(FILENAME_SITE_INDEX_HTML),
        ARTIFACT_KEY_USER_SITE_INDEX: user_site_rel(FILENAME_SITE_INDEX_HTML),
        # PDF output files (generated from HTML, if configured)
        ARTIFACT_KEY_STAKEHOLDER_SITE_PDF: stakeholder_site_rel(f"{FILENAME_SITE_INDEX_BASE}{EXT_PDF}"),
        ARTIFACT_KEY_DEVELOPER_SITE_PDF: developer_site_rel(f"{FILENAME_SITE_INDEX_BASE}{EXT_PDF}"),
        ARTIFACT_KEY_OPERATOR_SITE_PDF: operator_site_rel(f"{FILENAME_SITE_INDEX_BASE}{EXT_PDF}"),
        ARTIFACT_KEY_TESTER_SITE_PDF: tester_site_rel(f"{FILENAME_SITE_INDEX_BASE}{EXT_PDF}"),
        ARTIFACT_KEY_USER_SITE_PDF: user_site_rel(f"{FILENAME_SITE_INDEX_BASE}{EXT_PDF}"),
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

    # Audience site artifacts
    paths.update(audience_site_artifacts())
    return paths


def architecture_site_pages() -> dict[str, str]:
    """Master index site pages (50_architecture_site_v1)."""
    return {
        docs_site_rel(FILENAME_SITE_INDEX_HTML): "Documentation Hub",
        docs_site_rel(FILENAME_SITE_MANIFEST_JSON): "Manifest",
    }


def stakeholder_site_pages() -> dict[str, str]:
    """Stakeholder documentation site pages (51_stakeholder_docs_v1)."""
    return {
        stakeholder_site_rel(FILENAME_SITE_INDEX_HTML): "Stakeholder Documentation",
        stakeholder_site_rel(FILENAME_SITE_MANIFEST_JSON): "Manifest",
    }


def developer_site_pages() -> dict[str, str]:
    """Developer documentation site pages (52_developer_docs_v1)."""
    return {
        developer_site_rel(FILENAME_SITE_INDEX_HTML): "Developer Documentation",
        developer_site_rel(FILENAME_SITE_MANIFEST_JSON): "Manifest",
    }


def operator_site_pages() -> dict[str, str]:
    """Operator documentation site pages (53_operator_docs_v1)."""
    return {
        operator_site_rel(FILENAME_SITE_INDEX_HTML): "Operator Documentation",
        operator_site_rel(FILENAME_SITE_MANIFEST_JSON): "Manifest",
    }


def tester_site_pages() -> dict[str, str]:
    """Tester documentation site pages (54_tester_docs_v1)."""
    return {
        tester_site_rel(FILENAME_SITE_INDEX_HTML): "Tester Documentation",
        tester_site_rel(FILENAME_SITE_MANIFEST_JSON): "Manifest",
    }


def user_site_pages() -> dict[str, str]:
    """User documentation site pages (55_user_docs_v1)."""
    return {
        user_site_rel(FILENAME_SITE_INDEX_HTML): "User Documentation",
        user_site_rel(FILENAME_SITE_MANIFEST_JSON): "Manifest",
    }


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
