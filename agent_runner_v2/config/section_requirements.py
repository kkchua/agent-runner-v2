"""Central section requirements for all generated documents.

Single source of truth for document section requirements.
Both prompts and validation code reference this module.
"""

from pathlib import Path

# System documentation section requirements (all UPPERCASE filenames)
SYSTEM_DOC_SECTIONS: dict[str, list[str]] = {
    "PROJECT_ANALYSIS.md": [
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
    "DOCUMENTATION_STANDARD.md": [
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
    "README.md": [
        "System Documentation Index",
        "Audience Views",
        "Document Map",
    ],
    "SYSTEM_OVERVIEW.md": [
        "Purpose",
        "Scope",
        "Primary Flows",
        "Key Risks",
        "Architecture Profile",
    ],
    "BUSINESS_CAPABILITIES.md": [
        "Business Capabilities",
    ],
    "FUNCTIONAL_SPEC.md": [
        "Functional Requirements",
    ],
    "NON_FUNCTIONAL_REQUIREMENTS.md": [
        "Non-Functional Requirements",
    ],
    "SYSTEM_CONTEXT.md": [
        "System Context",
    ],
    "COMPONENT_ARCHITECTURE.md": [
        "Component Architecture",
    ],
    "DECISION_LOG.md": [
        "Decision Log",
    ],
    "SYSTEM_FILE_STRUCTURE.md": [
        "Repository Structure",
        "Top-Level Directories",
        "Documentation Locations",
    ],
    "DEVELOPER_GUIDE.md": [
        "Development Workflow",
        "Key Commands",
        "Documentation Responsibilities",
        "Architecture Posture",
    ],
    "RUNBOOK.md": [
        "Operations Scope",
        "Routine Procedures",
        "Failure Handling",
    ],
    "EXISTING_REPO_WORKFLOW_SOP.md": [
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
CODEBASE_DOC_SECTIONS: dict[str, list[str]] = {
    "INTEGRATION_MAP.md": [
        "Module Dependency Graph",
        "Dependency Matrix",
        "Data Flow Diagrams",
        "Integration Points",
        "Module Areas",
    ],
    "FAILURE_MODES.md": [
        "Failure Modes",
    ],
    "ARCHITECTURE_FLOW.md": [
        "Architecture Flow",
    ],
    "codebase_inventory.md": [
        "Module Inventory",
    ],
}

# Delivery template section requirements
DELIVERY_TEMPLATE_SECTIONS: dict[str, list[str]] = {
    "WORKFLOW_SOP_v1.md": [
        "Purpose",
        "Audience",
        "Workflow Steps",
        "Responsibilities",
        "Validation",
    ],
    "DELIVERY_STATUS_RULES_v1.md": [
        "Status Definitions",
        "Transition Rules",
        "Validation Criteria",
    ],
}

# Codebase template section requirements
CODEBASE_TEMPLATE_SECTION_REQUIREMENTS: dict[str, list[str]] = {
    "01_delivery_template_registry.md": [
        "Template Registry",
    ],
    "02_initiative_template.md": [
        "Initiative Template",
    ],
    "03_plan_template.md": [
        "Plan Template",
    ],
    "04_task_graph_template.md": [
        "Task Graph Template",
    ],
    "05_task_template.md": [
        "Task Template",
    ],
    "06_impl_template.md": [
        "Implementation Template",
    ],
    "07_review_template.md": [
        "Review Template",
    ],
    "08_validation_template.md": [
        "Validation Template",
    ],
    "09_memory_template.md": [
        "Memory Template",
    ],
}

# Codebase doc SOP sections
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

# Delivery template section requirements (detailed)
DELIVERY_TEMPLATE_SECTION_REQUIREMENTS: dict[str, list[str]] = {
    "01_delivery_template_registry.md": [
        "Metadata",
        "Registry Overview",
        "Template Families",
        "Usage Rules",
        "Cross-References",
    ],
    "02_delivery_initiative_template.md": [
        "Metadata",
        "Initiative Description",
        "Scope",
        "Documentation Scope",
        "Dependencies",
        "Acceptance Criteria",
        "Notes",
    ],
    "03_delivery_plan_template.md": [
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
    "04_delivery_task_graph_template.md": [
        "Metadata",
        "Task Graph Objective",
        "Task Graph",
        "Execution Flow",
        "Documentation Workstream",
        "Success Criteria",
        "Notes",
    ],
    "05_delivery_task_template.md": [
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
    "06_delivery_impl_template.md": [
        "Metadata",
        "Implementation Objective",
        "Changes Overview",
        "Implementation Steps",
        "Documentation Update Plan",
        "Risk Assessment",
        "Validation Criteria",
        "Notes",
    ],
    "07_delivery_review_template.md": [
        "Metadata",
        "Review Scope",
        "Findings",
        "Documentation Compliance",
        "Verdict",
        "Notes",
    ],
    "08_delivery_validation_template.md": [
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
    "09_delivery_memory_template.md": [
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

# Delivery governance SOP sections
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


def get_required_sections(doc_path: str) -> list[str]:
    """Get required sections for a document by path or name.
    
    Args:
        doc_path: Full path or just filename (e.g., "PROJECT_ANALYSIS.md")
    
    Returns:
        List of required section headings
    
    Raises:
        ValueError: If document has no defined section requirements
    """
    doc_name = Path(doc_path).name
    
    # Check system docs
    if doc_name in SYSTEM_DOC_SECTIONS:
        return SYSTEM_DOC_SECTIONS[doc_name]
    
    # Check codebase docs
    if doc_name in CODEBASE_DOC_SECTIONS:
        return CODEBASE_DOC_SECTIONS[doc_name]
    
    raise ValueError(
        f"No section requirements defined for {doc_name}. "
        f"Add it to agent_runner_v2/config/section_requirements.py"
    )


def list_all_documented_files() -> list[str]:
    """List all documents with defined section requirements."""
    return sorted(set(SYSTEM_DOC_SECTIONS.keys()) | set(CODEBASE_DOC_SECTIONS.keys()))
