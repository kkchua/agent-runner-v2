from __future__ import annotations

"""Shared repository-relative documentation path contract."""

from pathlib import PurePosixPath


SYSTEM_DOC_ROOT = PurePosixPath("docs/system/00_governance/bootstrap")
DOCS_ROOT = PurePosixPath("docs")
SYSTEM_TEMPLATE_ROOT = SYSTEM_DOC_ROOT / "templates"
SYSTEM_DELIVERY_TEMPLATE_ROOT = SYSTEM_TEMPLATE_ROOT / "delivery"
SYSTEM_CODEBASE_TEMPLATE_ROOT = SYSTEM_TEMPLATE_ROOT / "codebase"
CODEBASE_DOC_ROOT = PurePosixPath("docs/codebase")
DELIVERY_DOC_ROOT = PurePosixPath("docs/delivery")
ARCHITECTURE_SITE_ROOT = PurePosixPath("docs/site/architecture")


def _rel(*parts: str) -> str:
    return PurePosixPath(*parts).as_posix()


def repo_doc_rel(*parts: str) -> str:
    return _rel("docs", *parts)


def docs_root_rel(*parts: str) -> str:
    return _rel(*(DOCS_ROOT.parts + parts))


def system_doc_rel(*parts: str) -> str:
    return _rel(*(SYSTEM_DOC_ROOT.parts + parts))


def system_template_rel(*parts: str) -> str:
    return _rel(*(SYSTEM_TEMPLATE_ROOT.parts + parts))


def system_delivery_template_rel(*parts: str) -> str:
    return _rel(*(SYSTEM_DELIVERY_TEMPLATE_ROOT.parts + parts))


def system_codebase_template_rel(*parts: str) -> str:
    return _rel(*(SYSTEM_CODEBASE_TEMPLATE_ROOT.parts + parts))


def codebase_doc_rel(*parts: str) -> str:
    return _rel(*(CODEBASE_DOC_ROOT.parts + parts))


def delivery_doc_rel(*parts: str) -> str:
    return _rel(*(DELIVERY_DOC_ROOT.parts + parts))


def architecture_site_rel(*parts: str) -> str:
    return _rel(*(ARCHITECTURE_SITE_ROOT.parts + parts))


def master_bootstrap_docs(*, job_id: str, mode: str) -> dict[str, str]:
    return {
        "PROJECT_ANALYSIS": system_doc_rel("project_analysis.md"),
        "SYSTEM_DOCS_INDEX": system_doc_rel("README.md"),
        "SYSTEM_DOCS_CHANGE_LOG": system_doc_rel(f"{job_id}-{mode}-change-log.md"),
        "SYSTEM_DOCS_VALIDATION": system_doc_rel(f"{job_id}-{mode}-validation.md"),
        "SYSTEM_DOC_STANDARD": system_doc_rel("DOCUMENTATION_STANDARD.md"),
        "BUNDLE_TAXONOMY": system_doc_rel("BUNDLE_TAXONOMY.md"),
        "BUNDLE_MIGRATION_PLAN": system_doc_rel("BUNDLE_MIGRATION_PLAN.md"),
        "SYSTEM_OVERVIEW": system_doc_rel("SYSTEM_OVERVIEW.md"),
        "BUSINESS_CAPABILITIES": system_doc_rel("BUSINESS_CAPABILITIES.md"),
        "FUNCTIONAL_SPEC": system_doc_rel("FUNCTIONAL_SPEC.md"),
        "NON_FUNCTIONAL_REQUIREMENTS": system_doc_rel("NON_FUNCTIONAL_REQUIREMENTS.md"),
        "SYSTEM_CONTEXT": system_doc_rel("SYSTEM_CONTEXT.md"),
        "COMPONENT_ARCHITECTURE": system_doc_rel("COMPONENT_ARCHITECTURE.md"),
        "DECISION_LOG": system_doc_rel("DECISION_LOG.md"),
        "SYSTEM_FILE_STRUCTURE": system_doc_rel("SYSTEM_FILE_STRUCTURE.md"),
        "DEVELOPER_GUIDE": system_doc_rel("DEVELOPER_GUIDE.md"),
        "RUNBOOK": system_doc_rel("RUNBOOK.md"),
        "EXISTING_REPO_WORKFLOW_SOP": system_doc_rel("EXISTING_REPO_WORKFLOW_SOP.md"),
        "BOOTSTRAP_SUMMARY": system_doc_rel(f"{job_id}-bootstrap-summary.md"),
    }


def delivery_scaffold_docs() -> dict[str, str]:
    return {
        "PROJECT_ANALYSIS": system_doc_rel("project_analysis.md"),
        "DELIVERY_SOP": system_doc_rel("WORKFLOW_SOP_v1.md"),
        "DELIVERY_STATUS_RULES": system_doc_rel("DELIVERY_STATUS_RULES_v1.md"),
        "DELIVERY_VALIDATION_TEMPLATE": system_delivery_template_rel("08_delivery_validation_template.md"),
        "DELIVERY_TEMPLATE_REGISTRY": system_delivery_template_rel("01_delivery_template_registry.md"),
        "DELIVERY_INITIATIVE_TEMPLATE": system_delivery_template_rel("02_delivery_initiative_template.md"),
        "DELIVERY_PLAN_TEMPLATE": system_delivery_template_rel("03_delivery_plan_template.md"),
        "DELIVERY_TASK_GRAPH_TEMPLATE": system_delivery_template_rel("04_delivery_task_graph_template.md"),
        "DELIVERY_TASK_TEMPLATE": system_delivery_template_rel("05_delivery_task_template.md"),
        "DELIVERY_IMPL_TEMPLATE": system_delivery_template_rel("06_delivery_impl_template.md"),
        "DELIVERY_REVIEW_TEMPLATE": system_delivery_template_rel("07_delivery_review_template.md"),
        "DELIVERY_MEMORY_TEMPLATE": system_delivery_template_rel("09_delivery_memory_template.md"),
        "DELIVERY_AGENTS_MD": delivery_doc_rel("00_standards/DELIVERY_AGENTS_MD.md"),
        "DELIVERY_AGENT_PLANNER": delivery_doc_rel("00_standards/DELIVERY_AGENT_PLANNER.md"),
        "DELIVERY_AGENT_TASK_DECOMPOSER": delivery_doc_rel("00_standards/DELIVERY_AGENT_TASK_DECOMPOSER.md"),
        "DELIVERY_AGENT_IMPL_PLANNER": delivery_doc_rel("00_standards/DELIVERY_AGENT_IMPL_PLANNER.md"),
        "DELIVERY_AGENT_EXECUTOR": delivery_doc_rel("00_standards/DELIVERY_AGENT_EXECUTOR.md"),
        "DELIVERY_AGENT_REVIEWER": delivery_doc_rel("00_standards/DELIVERY_AGENT_REVIEWER.md"),
        "DELIVERY_AGENT_MEMORY_MANAGER": delivery_doc_rel("00_standards/DELIVERY_AGENT_MEMORY_MANAGER.md"),
        "CODEBASE_DOC_SOP": codebase_doc_rel("00_standards/CODEBASE_DOC_SOP_v1.md"),
        "CODEBASE_DOC_STATUS_RULES": codebase_doc_rel("00_standards/CODEBASE_DOC_STATUS_RULES_v1.md"),
        "CODEBASE_TEMPLATE_REGISTRY": system_codebase_template_rel("01_codebase_template_registry.md"),
        "CODEBASE_INVENTORY_TEMPLATE": system_codebase_template_rel("02_codebase_inventory_template.md"),
        "CODEBASE_MODULE_TEMPLATE": system_codebase_template_rel("03_codebase_module_template.md"),
        "CODEBASE_COMPONENT_TEMPLATE": system_codebase_template_rel("04_codebase_component_template.md"),
        "CODEBASE_CHANGE_TEMPLATE": system_codebase_template_rel("05_codebase_change_template.md"),
        "CODEBASE_INVENTORY": codebase_doc_rel("01_inventory/codebase_inventory.md"),
        "DELIVERY_FOLDER_MAP": delivery_doc_rel("DELIVERY_FOLDER_MAP.json"),
        "EXISTING_REPO_WORKFLOW_SOP": system_doc_rel("EXISTING_REPO_WORKFLOW_SOP.md"),
    }


def codebase_docs(*, job_id: str, mode: str) -> dict[str, str]:
    return {
        "CODEBASE_INVENTORY": codebase_doc_rel("01_inventory/codebase_inventory.md"),
        "CODEBASE_CHANGE_IMPACT": codebase_doc_rel("04_changes", f"{job_id}-{mode}.md"),
        "CODEBASE_SCAN_SNAPSHOT": codebase_doc_rel("04_changes", f"{job_id}-{mode}-snapshot.json"),
    }


def architecture_site_pages() -> dict[str, str]:
    return {
        architecture_site_rel("index.html"): "Architecture Overview",
        architecture_site_rel("stakeholders.html"): "Stakeholder View",
        architecture_site_rel("developers.html"): "Developer View",
        architecture_site_rel("functional.html"): "Functional View",
        architecture_site_rel("runtime.html"): "Runtime View",
        architecture_site_rel("components.html"): "Component View",
        architecture_site_rel("manifest.json"): "Manifest",
        architecture_site_rel("validation.md"): "Validation",
    }


def prompt_literal_aliases() -> dict[str, str]:
    """Map literal repo-relative paths to prompt placeholders."""
    aliases = {
        str(DOCS_ROOT): "{DOCS_ROOT}",
        str(SYSTEM_DOC_ROOT): "{SYSTEM_DOC_ROOT}",
        str(SYSTEM_TEMPLATE_ROOT): "{SYSTEM_TEMPLATE_ROOT}",
        str(SYSTEM_DELIVERY_TEMPLATE_ROOT): "{SYSTEM_DELIVERY_TEMPLATE_ROOT}",
        str(SYSTEM_CODEBASE_TEMPLATE_ROOT): "{SYSTEM_CODEBASE_TEMPLATE_ROOT}",
        str(CODEBASE_DOC_ROOT): "{CODEBASE_DOC_ROOT}",
        str(DELIVERY_DOC_ROOT): "{DELIVERY_DOC_ROOT}",
        str(ARCHITECTURE_SITE_ROOT): "{ARCHITECTURE_SITE_ROOT}",
    }
    aliases.update(
        {
            system_doc_rel("project_analysis.md"): "{PROJECT_ANALYSIS}",
            system_doc_rel("README.md"): "{SYSTEM_DOCS_INDEX}",
            system_doc_rel("DOCUMENTATION_STANDARD.md"): "{SYSTEM_DOC_STANDARD}",
            system_doc_rel("BUNDLE_TAXONOMY.md"): "{BUNDLE_TAXONOMY}",
            system_doc_rel("BUNDLE_MIGRATION_PLAN.md"): "{BUNDLE_MIGRATION_PLAN}",
            system_doc_rel("SYSTEM_OVERVIEW.md"): "{SYSTEM_OVERVIEW}",
            system_doc_rel("BUSINESS_CAPABILITIES.md"): "{BUSINESS_CAPABILITIES}",
            system_doc_rel("FUNCTIONAL_SPEC.md"): "{FUNCTIONAL_SPEC}",
            system_doc_rel("NON_FUNCTIONAL_REQUIREMENTS.md"): "{NON_FUNCTIONAL_REQUIREMENTS}",
            system_doc_rel("SYSTEM_CONTEXT.md"): "{SYSTEM_CONTEXT}",
            system_doc_rel("COMPONENT_ARCHITECTURE.md"): "{COMPONENT_ARCHITECTURE}",
            system_doc_rel("DECISION_LOG.md"): "{DECISION_LOG}",
            system_doc_rel("SYSTEM_FILE_STRUCTURE.md"): "{SYSTEM_FILE_STRUCTURE}",
            system_doc_rel("DEVELOPER_GUIDE.md"): "{DEVELOPER_GUIDE}",
            system_doc_rel("RUNBOOK.md"): "{RUNBOOK}",
            system_doc_rel("EXISTING_REPO_WORKFLOW_SOP.md"): "{EXISTING_REPO_WORKFLOW_SOP}",
            codebase_doc_rel("01_inventory/codebase_inventory.md"): "{CODEBASE_INVENTORY}",
            codebase_doc_rel("00_standards/CODEBASE_DOC_SOP_v1.md"): "{CODEBASE_DOC_SOP}",
            codebase_doc_rel("00_standards/CODEBASE_DOC_STATUS_RULES_v1.md"): "{CODEBASE_DOC_STATUS_RULES}",
            delivery_doc_rel("00_standards/DELIVERY_AGENTS_MD.md"): "{DELIVERY_AGENTS_MD}",
            delivery_doc_rel("00_standards/DELIVERY_AGENT_PLANNER.md"): "{DELIVERY_AGENT_PLANNER}",
            delivery_doc_rel("00_standards/DELIVERY_AGENT_TASK_DECOMPOSER.md"): "{DELIVERY_AGENT_TASK_DECOMPOSER}",
            delivery_doc_rel("00_standards/DELIVERY_AGENT_IMPL_PLANNER.md"): "{DELIVERY_AGENT_IMPL_PLANNER}",
            delivery_doc_rel("00_standards/DELIVERY_AGENT_EXECUTOR.md"): "{DELIVERY_AGENT_EXECUTOR}",
            delivery_doc_rel("00_standards/DELIVERY_AGENT_REVIEWER.md"): "{DELIVERY_AGENT_REVIEWER}",
            delivery_doc_rel("00_standards/DELIVERY_AGENT_MEMORY_MANAGER.md"): "{DELIVERY_AGENT_MEMORY_MANAGER}",
            delivery_doc_rel("DELIVERY_FOLDER_MAP.json"): "{DELIVERY_FOLDER_MAP}",
            system_delivery_template_rel("01_delivery_template_registry.md"): "{DELIVERY_TEMPLATE_REGISTRY}",
            system_delivery_template_rel("02_delivery_initiative_template.md"): "{DELIVERY_INITIATIVE_TEMPLATE}",
            system_delivery_template_rel("03_delivery_plan_template.md"): "{DELIVERY_PLAN_TEMPLATE}",
            system_delivery_template_rel("04_delivery_task_graph_template.md"): "{DELIVERY_TASK_GRAPH_TEMPLATE}",
            system_delivery_template_rel("05_delivery_task_template.md"): "{DELIVERY_TASK_TEMPLATE}",
            system_delivery_template_rel("06_delivery_impl_template.md"): "{DELIVERY_IMPL_TEMPLATE}",
            system_delivery_template_rel("07_delivery_review_template.md"): "{DELIVERY_REVIEW_TEMPLATE}",
            system_delivery_template_rel("08_delivery_validation_template.md"): "{DELIVERY_VALIDATION_TEMPLATE}",
            system_delivery_template_rel("09_delivery_memory_template.md"): "{DELIVERY_MEMORY_TEMPLATE}",
            system_codebase_template_rel("01_codebase_template_registry.md"): "{CODEBASE_TEMPLATE_REGISTRY}",
            system_codebase_template_rel("02_codebase_inventory_template.md"): "{CODEBASE_INVENTORY_TEMPLATE}",
            system_codebase_template_rel("03_codebase_module_template.md"): "{CODEBASE_MODULE_TEMPLATE}",
            system_codebase_template_rel("04_codebase_component_template.md"): "{CODEBASE_COMPONENT_TEMPLATE}",
            system_codebase_template_rel("05_codebase_change_template.md"): "{CODEBASE_CHANGE_TEMPLATE}",
            architecture_site_rel("index.html"): "{ARCHITECTURE_SITE_INDEX}",
            architecture_site_rel("stakeholders.html"): "{ARCHITECTURE_SITE_STAKEHOLDERS}",
            architecture_site_rel("developers.html"): "{ARCHITECTURE_SITE_DEVELOPERS}",
            architecture_site_rel("functional.html"): "{ARCHITECTURE_SITE_FUNCTIONAL}",
            architecture_site_rel("runtime.html"): "{ARCHITECTURE_SITE_RUNTIME}",
            architecture_site_rel("components.html"): "{ARCHITECTURE_SITE_COMPONENTS}",
            architecture_site_rel("manifest.json"): "{ARCHITECTURE_SITE_MANIFEST}",
            architecture_site_rel("validation.md"): "{ARCHITECTURE_SITE_VALIDATION}",
            docs_root_rel("engineering"): "{DOCS_ROOT}/engineering",
            docs_root_rel("operations"): "{DOCS_ROOT}/operations",
        }
    )
    return aliases
