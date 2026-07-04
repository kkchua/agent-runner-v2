---
title: "Component Documentation: codebase governance"
template_id: "CB-03"
status: "active"
component_id: "codebase-governance"
created: "2026-07-04T13:29:07+08:00"
owner: "40_documentation_sync_v1"
last_verified_by_change: "40_documentation_sync_v1 / 40DOCSYNC-GEN-20260704-001 / 2026-07-04T13:29:07+08:00"
modules: [".qwen/skills/auto-skill-agent-system-review/SKILL.md", ".qwen/skills/auto-skill-generate-agents/SKILL.md", ".qwen/skills/auto-skill-generate-architecture-docs/SKILL.md", ".qwen/skills/auto-skill-generate-master-system-docs/SKILL.md", ".qwen/skills/auto-skill-generate-sop/SKILL.md", ".qwen/skills/auto-skill-generate-templates/SKILL.md", ".qwen/skills/auto-skill-project-analysis/SKILL.md", ".qwen/skills/auto-skill-review-master-system-docs/SKILL.md", "agent_runner_v2/bootstrap/bundles/core/current/00DOC-GEN-20260704-002-bootstrap-change-log.md", "agent_runner_v2/bootstrap/bundles/core/current/00DOC-GEN-20260704-002-bootstrap-summary.md", "agent_runner_v2/bootstrap/bundles/core/current/00DOC-GEN-20260704-002-bootstrap-validation.md", "agent_runner_v2/bootstrap/bundles/core/current/BUNDLE_MIGRATION_PLAN.md", "agent_runner_v2/bootstrap/bundles/core/current/BUNDLE_TAXONOMY.md", "agent_runner_v2/bootstrap/bundles/core/current/BUSINESS_CAPABILITIES.md", "agent_runner_v2/bootstrap/bundles/core/current/COMPONENT_ARCHITECTURE.md", "agent_runner_v2/bootstrap/bundles/core/current/DECISION_LOG.md", "agent_runner_v2/bootstrap/bundles/core/current/DELIVERY_STATUS_RULES_v1.md", "agent_runner_v2/bootstrap/bundles/core/current/DEVELOPER_GUIDE.md", "agent_runner_v2/bootstrap/bundles/core/current/DOCUMENTATION_STANDARD.md", "agent_runner_v2/bootstrap/bundles/core/current/EXISTING_REPO_WORKFLOW_SOP.md", "agent_runner_v2/bootstrap/bundles/core/current/FUNCTIONAL_SPEC.md", "agent_runner_v2/bootstrap/bundles/core/current/NON_FUNCTIONAL_REQUIREMENTS.md", "agent_runner_v2/bootstrap/bundles/core/current/project_analysis.md", "agent_runner_v2/bootstrap/bundles/core/current/README.md", "agent_runner_v2/bootstrap/bundles/core/current/RUNBOOK.md", "agent_runner_v2/bootstrap/bundles/core/current/SYSTEM_CONTEXT.md", "agent_runner_v2/bootstrap/bundles/core/current/SYSTEM_FILE_STRUCTURE.md", "agent_runner_v2/bootstrap/bundles/core/current/SYSTEM_OVERVIEW.md", "agent_runner_v2/bootstrap/bundles/core/current/templates/codebase/01_codebase_template_registry.md", "agent_runner_v2/bootstrap/bundles/core/current/templates/codebase/02_codebase_inventory_template.md", "agent_runner_v2/bootstrap/bundles/core/current/templates/codebase/03_codebase_module_template.md", "agent_runner_v2/bootstrap/bundles/core/current/templates/codebase/04_codebase_component_template.md", "agent_runner_v2/bootstrap/bundles/core/current/templates/codebase/05_codebase_change_template.md", "agent_runner_v2/bootstrap/bundles/core/current/templates/delivery/01_delivery_template_registry.md", "agent_runner_v2/bootstrap/bundles/core/current/templates/delivery/02_delivery_initiative_template.md", "agent_runner_v2/bootstrap/bundles/core/current/templates/delivery/03_delivery_plan_template.md", "agent_runner_v2/bootstrap/bundles/core/current/templates/delivery/04_delivery_task_graph_template.md", "agent_runner_v2/bootstrap/bundles/core/current/templates/delivery/05_delivery_task_template.md", "agent_runner_v2/bootstrap/bundles/core/current/templates/delivery/06_delivery_impl_template.md", "agent_runner_v2/bootstrap/bundles/core/current/templates/delivery/07_delivery_review_template.md", "agent_runner_v2/bootstrap/bundles/core/current/templates/delivery/08_delivery_validation_template.md", "agent_runner_v2/bootstrap/bundles/core/current/templates/delivery/09_delivery_memory_template.md", "agent_runner_v2/bootstrap/bundles/core/current/WORKFLOW_SOP_v1.md", "agent_runner_v2/image_csv_generation.md", "agent_runner_v2/QWEN.md", "archive/batch/README.md", "docs/codebase/00_standards/CODEBASE_DOC_SOP_v1.md", "docs/codebase/00_standards/CODEBASE_DOC_STATUS_RULES_v1.md", "docs/codebase/01_inventory/01_PROJECT_ANALYSIS.md", "docs/codebase/01_inventory/codebase_inventory.md", "docs/delivery/00_standards/DELIVERY_AGENT_EXECUTOR.md", "docs/delivery/00_standards/DELIVERY_AGENT_IMPL_PLANNER.md", "docs/delivery/00_standards/DELIVERY_AGENT_MEMORY_MANAGER.md", "docs/delivery/00_standards/DELIVERY_AGENT_PLANNER.md", "docs/delivery/00_standards/DELIVERY_AGENT_REVIEWER.md", "docs/delivery/00_standards/DELIVERY_AGENT_TASK_DECOMPOSER.md", "docs/delivery/00_standards/DELIVERY_AGENTS_MD.md", "docs/delivery/05_reviews/REV-260704-01_rsop_R-0000-00_workflow-sop-v1.md", "docs/delivery/05_reviews/REV-260704-02_rtmpl_R-0000-00_01-delivery-template-registry.md", "docs/delivery/05_reviews/REV-260704-03_ragent_R-0000-00_delivery-agents-md.md", "docs/system/00_governance/bootstrap/00DOC-GEN-20260704-002-bootstrap-change-log.md", "docs/system/00_governance/bootstrap/00DOC-GEN-20260704-002-bootstrap-summary.md", "docs/system/00_governance/bootstrap/00DOC-GEN-20260704-002-bootstrap-validation.md", "docs/system/00_governance/bootstrap/BUNDLE_MIGRATION_PLAN.md", "docs/system/00_governance/bootstrap/BUNDLE_TAXONOMY.md", "docs/system/00_governance/bootstrap/BUSINESS_CAPABILITIES.md", "docs/system/00_governance/bootstrap/COMPONENT_ARCHITECTURE.md", "docs/system/00_governance/bootstrap/DECISION_LOG.md", "docs/system/00_governance/bootstrap/DELIVERY_STATUS_RULES_v1.md", "docs/system/00_governance/bootstrap/DEVELOPER_GUIDE.md", "docs/system/00_governance/bootstrap/DOCUMENTATION_STANDARD.md", "docs/system/00_governance/bootstrap/EXISTING_REPO_WORKFLOW_SOP.md", "docs/system/00_governance/bootstrap/FUNCTIONAL_SPEC.md", "docs/system/00_governance/bootstrap/NON_FUNCTIONAL_REQUIREMENTS.md", "docs/system/00_governance/bootstrap/project_analysis.md", "docs/system/00_governance/bootstrap/README.md", "docs/system/00_governance/bootstrap/RUNBOOK.md", "docs/system/00_governance/bootstrap/SYSTEM_CONTEXT.md", "docs/system/00_governance/bootstrap/SYSTEM_FILE_STRUCTURE.md", "docs/system/00_governance/bootstrap/SYSTEM_OVERVIEW.md", "docs/system/00_governance/bootstrap/templates/codebase/01_codebase_template_registry.md", "docs/system/00_governance/bootstrap/templates/codebase/02_codebase_inventory_template.md", "docs/system/00_governance/bootstrap/templates/codebase/03_codebase_module_template.md", "docs/system/00_governance/bootstrap/templates/codebase/04_codebase_component_template.md", "docs/system/00_governance/bootstrap/templates/codebase/05_codebase_change_template.md", "docs/system/00_governance/bootstrap/templates/delivery/01_delivery_template_registry.md", "docs/system/00_governance/bootstrap/templates/delivery/02_delivery_initiative_template.md", "docs/system/00_governance/bootstrap/templates/delivery/03_delivery_plan_template.md", "docs/system/00_governance/bootstrap/templates/delivery/04_delivery_task_graph_template.md", "docs/system/00_governance/bootstrap/templates/delivery/05_delivery_task_template.md", "docs/system/00_governance/bootstrap/templates/delivery/06_delivery_impl_template.md", "docs/system/00_governance/bootstrap/templates/delivery/07_delivery_review_template.md", "docs/system/00_governance/bootstrap/templates/delivery/08_delivery_validation_template.md", "docs/system/00_governance/bootstrap/templates/delivery/09_delivery_memory_template.md", "docs/system/00_governance/bootstrap/WORKFLOW_SOP_v1.md", "HOW_TO_GUIDE.md", "QWEN.md", "README.md", "WINDOWS_COMPATIBILITY.md"]
---

# Component Documentation: codebase governance

## 1. Component Overview

### 1.1 Purpose

The codebase documentation standards, templates, inventory, and validation rules that govern `/docs/codebase`.

### 1.2 Scope

| Module | Role in Component |
|--------|-------------------|
| `.qwen/skills/auto-skill-agent-system-review/SKILL.md` | documentation artifact |
| `.qwen/skills/auto-skill-generate-agents/SKILL.md` | documentation artifact |
| `.qwen/skills/auto-skill-generate-architecture-docs/SKILL.md` | documentation artifact |
| `.qwen/skills/auto-skill-generate-master-system-docs/SKILL.md` | documentation artifact |
| `.qwen/skills/auto-skill-generate-sop/SKILL.md` | documentation artifact |
| `.qwen/skills/auto-skill-generate-templates/SKILL.md` | documentation artifact |
| `.qwen/skills/auto-skill-project-analysis/SKILL.md` | documentation artifact |
| `.qwen/skills/auto-skill-review-master-system-docs/SKILL.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/00DOC-GEN-20260704-002-bootstrap-change-log.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/00DOC-GEN-20260704-002-bootstrap-summary.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/00DOC-GEN-20260704-002-bootstrap-validation.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/BUNDLE_MIGRATION_PLAN.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/BUNDLE_TAXONOMY.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/BUSINESS_CAPABILITIES.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/COMPONENT_ARCHITECTURE.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/DECISION_LOG.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/DELIVERY_STATUS_RULES_v1.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/DEVELOPER_GUIDE.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/DOCUMENTATION_STANDARD.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/EXISTING_REPO_WORKFLOW_SOP.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/FUNCTIONAL_SPEC.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/NON_FUNCTIONAL_REQUIREMENTS.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/project_analysis.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/README.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/RUNBOOK.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/SYSTEM_CONTEXT.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/SYSTEM_FILE_STRUCTURE.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/SYSTEM_OVERVIEW.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/templates/codebase/01_codebase_template_registry.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/templates/codebase/02_codebase_inventory_template.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/templates/codebase/03_codebase_module_template.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/templates/codebase/04_codebase_component_template.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/templates/codebase/05_codebase_change_template.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/templates/delivery/01_delivery_template_registry.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/templates/delivery/02_delivery_initiative_template.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/templates/delivery/03_delivery_plan_template.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/templates/delivery/04_delivery_task_graph_template.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/templates/delivery/05_delivery_task_template.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/templates/delivery/06_delivery_impl_template.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/templates/delivery/07_delivery_review_template.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/templates/delivery/08_delivery_validation_template.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/templates/delivery/09_delivery_memory_template.md` | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/WORKFLOW_SOP_v1.md` | documentation artifact |
| `agent_runner_v2/image_csv_generation.md` | documentation artifact |
| `agent_runner_v2/QWEN.md` | documentation artifact |
| `archive/batch/README.md` | documentation artifact |
| `docs/codebase/00_standards/CODEBASE_DOC_SOP_v1.md` | documentation artifact |
| `docs/codebase/00_standards/CODEBASE_DOC_STATUS_RULES_v1.md` | documentation artifact |
| `docs/codebase/01_inventory/01_PROJECT_ANALYSIS.md` | documentation artifact |
| `docs/codebase/01_inventory/codebase_inventory.md` | documentation artifact |
| `docs/delivery/00_standards/DELIVERY_AGENT_EXECUTOR.md` | documentation artifact |
| `docs/delivery/00_standards/DELIVERY_AGENT_IMPL_PLANNER.md` | documentation artifact |
| `docs/delivery/00_standards/DELIVERY_AGENT_MEMORY_MANAGER.md` | documentation artifact |
| `docs/delivery/00_standards/DELIVERY_AGENT_PLANNER.md` | documentation artifact |
| `docs/delivery/00_standards/DELIVERY_AGENT_REVIEWER.md` | documentation artifact |
| `docs/delivery/00_standards/DELIVERY_AGENT_TASK_DECOMPOSER.md` | documentation artifact |
| `docs/delivery/00_standards/DELIVERY_AGENTS_MD.md` | documentation artifact |
| `docs/delivery/05_reviews/REV-260704-01_rsop_R-0000-00_workflow-sop-v1.md` | documentation artifact |
| `docs/delivery/05_reviews/REV-260704-02_rtmpl_R-0000-00_01-delivery-template-registry.md` | documentation artifact |
| `docs/delivery/05_reviews/REV-260704-03_ragent_R-0000-00_delivery-agents-md.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/00DOC-GEN-20260704-002-bootstrap-change-log.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/00DOC-GEN-20260704-002-bootstrap-summary.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/00DOC-GEN-20260704-002-bootstrap-validation.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/BUNDLE_MIGRATION_PLAN.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/BUNDLE_TAXONOMY.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/BUSINESS_CAPABILITIES.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/COMPONENT_ARCHITECTURE.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/DECISION_LOG.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/DELIVERY_STATUS_RULES_v1.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/DEVELOPER_GUIDE.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/DOCUMENTATION_STANDARD.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/EXISTING_REPO_WORKFLOW_SOP.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/FUNCTIONAL_SPEC.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/NON_FUNCTIONAL_REQUIREMENTS.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/project_analysis.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/README.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/RUNBOOK.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/SYSTEM_CONTEXT.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/SYSTEM_FILE_STRUCTURE.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/SYSTEM_OVERVIEW.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/templates/codebase/01_codebase_template_registry.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/templates/codebase/02_codebase_inventory_template.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/templates/codebase/03_codebase_module_template.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/templates/codebase/04_codebase_component_template.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/templates/codebase/05_codebase_change_template.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/templates/delivery/01_delivery_template_registry.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/templates/delivery/02_delivery_initiative_template.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/templates/delivery/03_delivery_plan_template.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/templates/delivery/04_delivery_task_graph_template.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/templates/delivery/05_delivery_task_template.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/templates/delivery/06_delivery_impl_template.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/templates/delivery/07_delivery_review_template.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/templates/delivery/08_delivery_validation_template.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/templates/delivery/09_delivery_memory_template.md` | documentation artifact |
| `docs/system/00_governance/bootstrap/WORKFLOW_SOP_v1.md` | documentation artifact |
| `HOW_TO_GUIDE.md` | documentation artifact |
| `QWEN.md` | documentation artifact |
| `README.md` | documentation artifact |
| `WINDOWS_COMPATIBILITY.md` | documentation artifact |

## 2. Architecture

### 2.1 Component Diagram

Generated from repository scan baseline.

### 2.2 Data Flow

Repository files are scanned, normalized into inventory rows, and rendered into codebase documentation artifacts.

### 2.3 External Interfaces

| Interface | Direction | Protocol | Description |
|-----------|-----------|----------|-------------|
| `.qwen/skills/auto-skill-agent-system-review/SKILL.md` | outbound | markdown | documentation artifact |
| `.qwen/skills/auto-skill-generate-agents/SKILL.md` | outbound | markdown | documentation artifact |
| `.qwen/skills/auto-skill-generate-architecture-docs/SKILL.md` | outbound | markdown | documentation artifact |
| `.qwen/skills/auto-skill-generate-master-system-docs/SKILL.md` | outbound | markdown | documentation artifact |
| `.qwen/skills/auto-skill-generate-sop/SKILL.md` | outbound | markdown | documentation artifact |
| `.qwen/skills/auto-skill-generate-templates/SKILL.md` | outbound | markdown | documentation artifact |
| `.qwen/skills/auto-skill-project-analysis/SKILL.md` | outbound | markdown | documentation artifact |
| `.qwen/skills/auto-skill-review-master-system-docs/SKILL.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/00DOC-GEN-20260704-002-bootstrap-change-log.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/00DOC-GEN-20260704-002-bootstrap-summary.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/00DOC-GEN-20260704-002-bootstrap-validation.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/BUNDLE_MIGRATION_PLAN.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/BUNDLE_TAXONOMY.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/BUSINESS_CAPABILITIES.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/COMPONENT_ARCHITECTURE.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/DECISION_LOG.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/DELIVERY_STATUS_RULES_v1.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/DEVELOPER_GUIDE.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/DOCUMENTATION_STANDARD.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/EXISTING_REPO_WORKFLOW_SOP.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/FUNCTIONAL_SPEC.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/NON_FUNCTIONAL_REQUIREMENTS.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/project_analysis.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/README.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/RUNBOOK.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/SYSTEM_CONTEXT.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/SYSTEM_FILE_STRUCTURE.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/SYSTEM_OVERVIEW.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/templates/codebase/01_codebase_template_registry.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/templates/codebase/02_codebase_inventory_template.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/templates/codebase/03_codebase_module_template.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/templates/codebase/04_codebase_component_template.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/templates/codebase/05_codebase_change_template.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/templates/delivery/01_delivery_template_registry.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/templates/delivery/02_delivery_initiative_template.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/templates/delivery/03_delivery_plan_template.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/templates/delivery/04_delivery_task_graph_template.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/templates/delivery/05_delivery_task_template.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/templates/delivery/06_delivery_impl_template.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/templates/delivery/07_delivery_review_template.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/templates/delivery/08_delivery_validation_template.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/templates/delivery/09_delivery_memory_template.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/bootstrap/bundles/core/current/WORKFLOW_SOP_v1.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/image_csv_generation.md` | outbound | markdown | documentation artifact |
| `agent_runner_v2/QWEN.md` | outbound | markdown | documentation artifact |
| `archive/batch/README.md` | outbound | markdown | documentation artifact |
| `docs/codebase/00_standards/CODEBASE_DOC_SOP_v1.md` | outbound | markdown | documentation artifact |
| `docs/codebase/00_standards/CODEBASE_DOC_STATUS_RULES_v1.md` | outbound | markdown | documentation artifact |
| `docs/codebase/01_inventory/01_PROJECT_ANALYSIS.md` | outbound | markdown | documentation artifact |
| `docs/codebase/01_inventory/codebase_inventory.md` | outbound | markdown | documentation artifact |
| `docs/delivery/00_standards/DELIVERY_AGENT_EXECUTOR.md` | outbound | markdown | documentation artifact |
| `docs/delivery/00_standards/DELIVERY_AGENT_IMPL_PLANNER.md` | outbound | markdown | documentation artifact |
| `docs/delivery/00_standards/DELIVERY_AGENT_MEMORY_MANAGER.md` | outbound | markdown | documentation artifact |
| `docs/delivery/00_standards/DELIVERY_AGENT_PLANNER.md` | outbound | markdown | documentation artifact |
| `docs/delivery/00_standards/DELIVERY_AGENT_REVIEWER.md` | outbound | markdown | documentation artifact |
| `docs/delivery/00_standards/DELIVERY_AGENT_TASK_DECOMPOSER.md` | outbound | markdown | documentation artifact |
| `docs/delivery/00_standards/DELIVERY_AGENTS_MD.md` | outbound | markdown | documentation artifact |
| `docs/delivery/05_reviews/REV-260704-01_rsop_R-0000-00_workflow-sop-v1.md` | outbound | markdown | documentation artifact |
| `docs/delivery/05_reviews/REV-260704-02_rtmpl_R-0000-00_01-delivery-template-registry.md` | outbound | markdown | documentation artifact |
| `docs/delivery/05_reviews/REV-260704-03_ragent_R-0000-00_delivery-agents-md.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/00DOC-GEN-20260704-002-bootstrap-change-log.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/00DOC-GEN-20260704-002-bootstrap-summary.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/00DOC-GEN-20260704-002-bootstrap-validation.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/BUNDLE_MIGRATION_PLAN.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/BUNDLE_TAXONOMY.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/BUSINESS_CAPABILITIES.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/COMPONENT_ARCHITECTURE.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/DECISION_LOG.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/DELIVERY_STATUS_RULES_v1.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/DEVELOPER_GUIDE.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/DOCUMENTATION_STANDARD.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/EXISTING_REPO_WORKFLOW_SOP.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/FUNCTIONAL_SPEC.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/NON_FUNCTIONAL_REQUIREMENTS.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/project_analysis.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/README.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/RUNBOOK.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/SYSTEM_CONTEXT.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/SYSTEM_FILE_STRUCTURE.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/SYSTEM_OVERVIEW.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/templates/codebase/01_codebase_template_registry.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/templates/codebase/02_codebase_inventory_template.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/templates/codebase/03_codebase_module_template.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/templates/codebase/04_codebase_component_template.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/templates/codebase/05_codebase_change_template.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/templates/delivery/01_delivery_template_registry.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/templates/delivery/02_delivery_initiative_template.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/templates/delivery/03_delivery_plan_template.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/templates/delivery/04_delivery_task_graph_template.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/templates/delivery/05_delivery_task_template.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/templates/delivery/06_delivery_impl_template.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/templates/delivery/07_delivery_review_template.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/templates/delivery/08_delivery_validation_template.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/templates/delivery/09_delivery_memory_template.md` | outbound | markdown | documentation artifact |
| `docs/system/00_governance/bootstrap/WORKFLOW_SOP_v1.md` | outbound | markdown | documentation artifact |
| `HOW_TO_GUIDE.md` | outbound | markdown | documentation artifact |
| `QWEN.md` | outbound | markdown | documentation artifact |
| `README.md` | outbound | markdown | documentation artifact |
| `WINDOWS_COMPATIBILITY.md` | outbound | markdown | documentation artifact |

## 3. Behavior

### 3.1 Lifecycle

Created during codebase bootstrap or reconcile runs and refreshed when repository structure changes.

### 3.2 State Management

State is represented by the generated inventory and per-module/component documents.

### 3.3 Error Propagation

Documentation drift is treated as a validation failure and reraised to the workflow runner.

## 4. Configuration

| Parameter | Source | Default | Description |
|-----------|--------|---------|-------------|
| | | | |

## 5. Constraints

| Constraint | Rationale | Enforcement |
|------------|-----------|-------------|
| Zero mutation of source code | Documentation bootstrap must not alter code | Workflow writes docs only |

## 6. Testing

### 6.1 Integration Tests

| Test | Coverage |
|------|----------|
| | |

### 6.2 Known Gaps

Auto-generated baseline; extend with component-specific checks as needed.

## 7. Change Log

| Date | Change | Modules Affected | Verified By |
|------|--------|-----------------|-------------|
| 2026-07-04 | Initial baseline generated from repository scan | 99 modules/files | 40_documentation_sync_v1 |
