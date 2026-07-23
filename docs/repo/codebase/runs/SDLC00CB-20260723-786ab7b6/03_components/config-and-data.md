---
title: "Component Documentation: config and data"
template_id: "CB-03"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
component_id: "config-and-data"
created: "2026-07-23T21:25:54+08:00"
owner: "sdlc_00_codebase_v1"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-20260723-786ab7b6 / 2026-07-23T21:25:54+08:00"
modules: [".env.example", "_test_payload.json", "agent_runner_v2/bootstrap/bundles/core/current/bootstrap_publish_manifest.json", "docs/repo/agent_runner/sdlc/delivery/00_initiatives/INIT-20260723-001_console-sdlc10-support.meta.json", "docs/repo/agent_runner/sdlc/delivery/10_requirements/REQ-20260723-001_console-sdlc10-support.meta.json", "docs/repo/agent_runner/sdlc/delivery/20_plans/PLAN-20260723-001_console-sdlc10-support.meta.json", "docs/repo/agent_runner/sdlc/delivery/30_backlogs/BACKLOG-20260723-001_console-sdlc10-support.meta.json", "docs/repo/agent_runner/sdlc/delivery/40_tasks/WI-20260723-001_console-sdlc10-support-01.meta.json", "docs/repo/agent_runner/sdlc/delivery/40_tasks/WI-20260723-001_console-sdlc10-support-02.meta.json", "docs/repo/agent_runner/sdlc/delivery/50_implementations/IMPL-20260723-001-001_console-sdlc10-support-01.meta.json", "docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/01_inventory/codebase_inventory.meta.json", "docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/01_inventory/codebase_inventory.meta.json", "docs/system/00_governance/bootstrap/workflows/00_bootstrap_lifecycle_admin_v1/workflow.toml", "docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/bundle_governance.toml", "docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/bundle_governance/prompt_contract.json", "docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/workflow.toml", "docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/bundle_governance.toml", "docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/bundle_governance/prompt_contract.json", "docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/workflow.toml", "docs/system/00_governance/bootstrap/workflows/_registry/coder_connections.json", "docs/system/00_governance/bootstrap/workflows/_registry/coder_roles.json", "docs/system/00_governance/bootstrap/workflows/_registry/coder_roles_opencode.json", "docs/system/00_governance/bootstrap/workflows/_registry/coder_roles_qwen.json", "docs/system/00_governance/bootstrap/workflows/_registry/role_policies.json", "docs/system/00_governance/bootstrap/workflows/sdlc_00_codebase_v1/bundle_governance.toml", "docs/system/00_governance/bootstrap/workflows/sdlc_00_codebase_v1/workflow.toml", "docs/system/00_governance/bootstrap/workflows/sdlc_00_delivery_scaffold_v1/workflow.toml", "docs/system/00_governance/bootstrap/workflows/sdlc_00_init_doc_v1/workflow.toml", "docs/system/00_governance/bootstrap/workflows/sdlc_10_requirement_v1/workflow.toml", "docs/system/00_governance/bootstrap/workflows/sdlc_20_planning_v1/workflow.toml", "docs/system/00_governance/bootstrap/workflows/sdlc_30_backlog_v1/workflow.toml", "docs/system/00_governance/bootstrap/workflows/sdlc_40_task_v1/workflow.toml", "docs/system/00_governance/bootstrap/workflows/sdlc_50_implementation_v1/workflow.toml", "docs/system/00_governance/bootstrap/workflows/sdlc_60_execution_v1/workflow.toml", "docs/system/00_governance/bootstrap/workflows/sdlc_70_validation_v1/workflow.toml", "docs/system/00_governance/bootstrap/workflows/sdlc_80_review_v1/workflow.toml", "docs/system/00_governance/foundation/current/governance_set_manifest.json", "docs/system/00_governance/foundation/history/01GF-20260719-0864b1f2/governance_set_manifest.json", "docs/system/00_governance/foundation/history/01GF-20260719-4e51c88b/governance_set_manifest.json", "docs/system/00_governance/foundation/history/01GF-20260719-61ae0105/governance_set_manifest.json", "docs/system/00_governance/foundation/history/01GF-20260719-96e730ab/governance_set_manifest.json", "docs/system/00_governance/foundation/history/01GF-20260719-c5e882c3/governance_set_manifest.json", "docs/system/00_governance/foundation/history/01GF-20260719-f15f153c/governance_set_manifest.json", "docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/01GF-20260719-0864b1f2-governance-foundation-audit.meta.json", "docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/01GF-20260719-0864b1f2-governance-foundation-review.meta.json", "docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/01GF-20260719-4e51c88b-governance-foundation-audit.meta.json", "docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/01GF-20260719-4e51c88b-governance-foundation-review.meta.json", "docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/01GF-20260719-61ae0105-governance-foundation-audit.meta.json", "docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/01GF-20260719-61ae0105-governance-foundation-review.meta.json", "docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/01GF-20260719-96e730ab-governance-foundation-audit.meta.json", "docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/01GF-20260719-96e730ab-governance-foundation-review.meta.json", "docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/01GF-20260719-c5e882c3-governance-foundation-audit.meta.json", "docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/01GF-20260719-c5e882c3-governance-foundation-review.meta.json", "docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/README.meta.json", "docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/01GF-20260719-f15f153c-governance-foundation-audit.meta.json", "docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/01GF-20260719-f15f153c-governance-foundation-review.meta.json", "docs/system/00_governance/platform/agent_runner/current/platform_set_manifest.json", "docs/system/00_governance/platform/agent_runner/history/02AR-20260721-2eaba4b3/platform_set_manifest.json", "docs/system/00_governance/platform/agent_runner/history/02PC-20260721-b092c705/platform_set_manifest.json", "docs/system/00_governance/platform/agent_runner/history/02PC-GEN-20260721-009/platform_set_manifest.json", "docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/02PC-20260721-b092c705-platform-core-audit.meta.json", "docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/02PC-20260721-b092c705-platform-core-review.meta.json", "docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/README.meta.json", "docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/02PC-GEN-20260721-009-platform-core-audit.meta.json", "docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/02PC-GEN-20260721-009-platform-core-review.meta.json", "docs/system/00_governance/platform/agent_runner/sdlc/current/sdlc_scaffold_manifest.json", "docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/sdlc_scaffold_manifest.json", "docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/template_registry.meta.json", "docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/AGENTS.meta.json", "docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/SDLC00SCF-20260722-914943f4-sdlc-scaffold-review.meta.json", "docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/template_registry.meta.json", "docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/AGENTS.meta.json", "docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/SDLC00SCF-20260722-cc2b347d-sdlc-scaffold-review.meta.json", "docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/template_registry.meta.json", "docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/AGENTS.meta.json", "masterplan/00_repo_master_docs_bootstrap_v1/workflow.toml", "masterplan/delivery/03_tasks/TASK-20260418-01_contract-build-api-trigger.meta.json", "masterplan/delivery/03_tasks/TASK-20260418-02_managed-generation-api-trigger.meta.json", "masterplan/delivery/03_tasks/TASK-20260418-03_generation-run-api-surface.meta.json", "masterplan/delivery/03_tasks/TASK-20260418-04_artifact-lifecycle-retrieval.meta.json", "masterplan/delivery/03_tasks/TASK-20260418-05_router-registration-documentation.meta.json", "masterplan/delivery/04_implementation_plans/IMPL-20260418-01_contract-build-api-trigger.meta.json", "masterplan/delivery/04_implementation_plans/IMPL-20260418-02_managed-generation-api-trigger.meta.json", "masterplan/delivery/04_implementation_plans/IMPL-20260418-03_generation-run-api-surface.meta.json", "masterplan/delivery/05_reviews/REV-260418-01_rtask_T-0418-01_contract-build-api-trigger.meta.json", "masterplan/delivery/05_reviews/REV-260418-02_rimpl_M-0418-01_contract-build-api-trigger.meta.json", "masterplan/delivery/05_reviews/REV-260418-03_rtask_T-0418-02_managed-generation-api-trigger.meta.json", "masterplan/delivery/05_reviews/REV-260418-04_rtask_T-0418-02_managed-generation-api-trigger.meta.json", "masterplan/delivery/05_reviews/REV-260418-05_rimpl_M-0418-02_managed-generation-api-trigger.meta.json", "masterplan/delivery/05_reviews/VALIDATION-260418-2-M-0418-01_contract-build-api-trigger.meta.json", "masterplan/delivery/05_reviews/VALIDATION-260418-2-M-0418-02_managed-generation-api-trigger.meta.json", "masterplan/delivery/05_reviews/VALIDATION-260418-3-M-0418-02_managed-generation-api-trigger.meta.json", "masterplan/delivery/05_reviews/VALIDATION-260418-M-0418-01_contract-build-api-trigger.meta.json", "masterplan/delivery/05_reviews/VALIDATION-260418-M-0418-02_managed-generation-api-trigger.meta.json", "masterplan/old legacy workflow/comfyui_config.json", "masterplan/old legacy workflow/job_schema.json", "masterplan/old legacy workflow/llm_response_schema.json", "masterplan/old legacy workflow/model_mapping.json", "masterplan/old legacy workflow/usage_schema.json", "opencode.json", "operator-console.example.json", "platform_context_manifest.json", "pyproject.toml", "workflows/00_bootstrap_lifecycle_admin_v1/workflow.toml", "workflows/01_governance_foundation_v1/bundle_governance.toml", "workflows/01_governance_foundation_v1/bundle_governance/prompt_contract.json", "workflows/01_governance_foundation_v1/workflow.toml", "workflows/02_agent_runner_platform_v1/bundle_governance.toml", "workflows/02_agent_runner_platform_v1/bundle_governance/prompt_contract.json", "workflows/02_agent_runner_platform_v1/workflow.toml", "workflows/_registry/coder_connections.json", "workflows/_registry/coder_roles.json", "workflows/_registry/coder_roles_opencode.json", "workflows/_registry/coder_roles_qwen.json", "workflows/_registry/role_policies.json", "workflows/sdlc_00_codebase_v1/bundle_governance.toml", "workflows/sdlc_00_codebase_v1/workflow.toml", "workflows/sdlc_00_delivery_scaffold_v1/workflow.toml", "workflows/sdlc_00_init_doc_v1/workflow.toml", "workflows/sdlc_10_requirement_v1/workflow.toml", "workflows/sdlc_20_planning_v1/workflow.toml", "workflows/sdlc_30_backlog_v1/workflow.toml", "workflows/sdlc_40_task_v1/workflow.toml", "workflows/sdlc_50_implementation_v1/workflow.toml", "workflows/sdlc_60_execution_v1/workflow.toml", "workflows/sdlc_70_validation_v1/workflow.toml", "workflows/sdlc_80_review_v1/workflow.toml"]
---

# Component Documentation: config and data

## 1. Component Overview

### 1.1 Purpose

Configuration and structured data files that define runtime and documentation behavior.

### 1.2 Scope

| Module | Role in Component |
|--------|-------------------|
| `.env.example` | configuration / structured data |
| `_test_payload.json` | configuration / structured data |
| `agent_runner_v2/bootstrap/bundles/core/current/bootstrap_publish_manifest.json` | configuration / structured data |
| `docs/repo/agent_runner/sdlc/delivery/00_initiatives/INIT-20260723-001_console-sdlc10-support.meta.json` | configuration / structured data |
| `docs/repo/agent_runner/sdlc/delivery/10_requirements/REQ-20260723-001_console-sdlc10-support.meta.json` | configuration / structured data |
| `docs/repo/agent_runner/sdlc/delivery/20_plans/PLAN-20260723-001_console-sdlc10-support.meta.json` | configuration / structured data |
| `docs/repo/agent_runner/sdlc/delivery/30_backlogs/BACKLOG-20260723-001_console-sdlc10-support.meta.json` | configuration / structured data |
| `docs/repo/agent_runner/sdlc/delivery/40_tasks/WI-20260723-001_console-sdlc10-support-01.meta.json` | configuration / structured data |
| `docs/repo/agent_runner/sdlc/delivery/40_tasks/WI-20260723-001_console-sdlc10-support-02.meta.json` | configuration / structured data |
| `docs/repo/agent_runner/sdlc/delivery/50_implementations/IMPL-20260723-001-001_console-sdlc10-support-01.meta.json` | configuration / structured data |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/01_inventory/codebase_inventory.meta.json` | configuration / structured data |
| `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/01_inventory/codebase_inventory.meta.json` | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/00_bootstrap_lifecycle_admin_v1/workflow.toml` | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/bundle_governance.toml` | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/bundle_governance/prompt_contract.json` | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/workflow.toml` | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/bundle_governance.toml` | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/bundle_governance/prompt_contract.json` | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/workflow.toml` | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/_registry/coder_connections.json` | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/_registry/coder_roles.json` | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/_registry/coder_roles_opencode.json` | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/_registry/coder_roles_qwen.json` | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/_registry/role_policies.json` | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/sdlc_00_codebase_v1/bundle_governance.toml` | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/sdlc_00_codebase_v1/workflow.toml` | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/sdlc_00_delivery_scaffold_v1/workflow.toml` | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/sdlc_00_init_doc_v1/workflow.toml` | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/sdlc_10_requirement_v1/workflow.toml` | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/sdlc_20_planning_v1/workflow.toml` | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/sdlc_30_backlog_v1/workflow.toml` | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/sdlc_40_task_v1/workflow.toml` | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/sdlc_50_implementation_v1/workflow.toml` | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/sdlc_60_execution_v1/workflow.toml` | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/sdlc_70_validation_v1/workflow.toml` | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/sdlc_80_review_v1/workflow.toml` | configuration / structured data |
| `docs/system/00_governance/foundation/current/governance_set_manifest.json` | configuration / structured data |
| `docs/system/00_governance/foundation/history/01GF-20260719-0864b1f2/governance_set_manifest.json` | configuration / structured data |
| `docs/system/00_governance/foundation/history/01GF-20260719-4e51c88b/governance_set_manifest.json` | configuration / structured data |
| `docs/system/00_governance/foundation/history/01GF-20260719-61ae0105/governance_set_manifest.json` | configuration / structured data |
| `docs/system/00_governance/foundation/history/01GF-20260719-96e730ab/governance_set_manifest.json` | configuration / structured data |
| `docs/system/00_governance/foundation/history/01GF-20260719-c5e882c3/governance_set_manifest.json` | configuration / structured data |
| `docs/system/00_governance/foundation/history/01GF-20260719-f15f153c/governance_set_manifest.json` | configuration / structured data |
| `docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/01GF-20260719-0864b1f2-governance-foundation-audit.meta.json` | configuration / structured data |
| `docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/01GF-20260719-0864b1f2-governance-foundation-review.meta.json` | configuration / structured data |
| `docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/01GF-20260719-4e51c88b-governance-foundation-audit.meta.json` | configuration / structured data |
| `docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/01GF-20260719-4e51c88b-governance-foundation-review.meta.json` | configuration / structured data |
| `docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/01GF-20260719-61ae0105-governance-foundation-audit.meta.json` | configuration / structured data |
| `docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/01GF-20260719-61ae0105-governance-foundation-review.meta.json` | configuration / structured data |
| `docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/01GF-20260719-96e730ab-governance-foundation-audit.meta.json` | configuration / structured data |
| `docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/01GF-20260719-96e730ab-governance-foundation-review.meta.json` | configuration / structured data |
| `docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/01GF-20260719-c5e882c3-governance-foundation-audit.meta.json` | configuration / structured data |
| `docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/01GF-20260719-c5e882c3-governance-foundation-review.meta.json` | configuration / structured data |
| `docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/README.meta.json` | configuration / structured data |
| `docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/01GF-20260719-f15f153c-governance-foundation-audit.meta.json` | configuration / structured data |
| `docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/01GF-20260719-f15f153c-governance-foundation-review.meta.json` | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/current/platform_set_manifest.json` | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/history/02AR-20260721-2eaba4b3/platform_set_manifest.json` | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/history/02PC-20260721-b092c705/platform_set_manifest.json` | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/history/02PC-GEN-20260721-009/platform_set_manifest.json` | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/02PC-20260721-b092c705-platform-core-audit.meta.json` | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/02PC-20260721-b092c705-platform-core-review.meta.json` | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/README.meta.json` | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/02PC-GEN-20260721-009-platform-core-audit.meta.json` | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/02PC-GEN-20260721-009-platform-core-review.meta.json` | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/sdlc/current/sdlc_scaffold_manifest.json` | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/sdlc_scaffold_manifest.json` | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/template_registry.meta.json` | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/AGENTS.meta.json` | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/SDLC00SCF-20260722-914943f4-sdlc-scaffold-review.meta.json` | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/template_registry.meta.json` | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/AGENTS.meta.json` | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/SDLC00SCF-20260722-cc2b347d-sdlc-scaffold-review.meta.json` | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/template_registry.meta.json` | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/AGENTS.meta.json` | configuration / structured data |
| `masterplan/00_repo_master_docs_bootstrap_v1/workflow.toml` | configuration / structured data |
| `masterplan/delivery/03_tasks/TASK-20260418-01_contract-build-api-trigger.meta.json` | configuration / structured data |
| `masterplan/delivery/03_tasks/TASK-20260418-02_managed-generation-api-trigger.meta.json` | configuration / structured data |
| `masterplan/delivery/03_tasks/TASK-20260418-03_generation-run-api-surface.meta.json` | configuration / structured data |
| `masterplan/delivery/03_tasks/TASK-20260418-04_artifact-lifecycle-retrieval.meta.json` | configuration / structured data |
| `masterplan/delivery/03_tasks/TASK-20260418-05_router-registration-documentation.meta.json` | configuration / structured data |
| `masterplan/delivery/04_implementation_plans/IMPL-20260418-01_contract-build-api-trigger.meta.json` | configuration / structured data |
| `masterplan/delivery/04_implementation_plans/IMPL-20260418-02_managed-generation-api-trigger.meta.json` | configuration / structured data |
| `masterplan/delivery/04_implementation_plans/IMPL-20260418-03_generation-run-api-surface.meta.json` | configuration / structured data |
| `masterplan/delivery/05_reviews/REV-260418-01_rtask_T-0418-01_contract-build-api-trigger.meta.json` | configuration / structured data |
| `masterplan/delivery/05_reviews/REV-260418-02_rimpl_M-0418-01_contract-build-api-trigger.meta.json` | configuration / structured data |
| `masterplan/delivery/05_reviews/REV-260418-03_rtask_T-0418-02_managed-generation-api-trigger.meta.json` | configuration / structured data |
| `masterplan/delivery/05_reviews/REV-260418-04_rtask_T-0418-02_managed-generation-api-trigger.meta.json` | configuration / structured data |
| `masterplan/delivery/05_reviews/REV-260418-05_rimpl_M-0418-02_managed-generation-api-trigger.meta.json` | configuration / structured data |
| `masterplan/delivery/05_reviews/VALIDATION-260418-2-M-0418-01_contract-build-api-trigger.meta.json` | configuration / structured data |
| `masterplan/delivery/05_reviews/VALIDATION-260418-2-M-0418-02_managed-generation-api-trigger.meta.json` | configuration / structured data |
| `masterplan/delivery/05_reviews/VALIDATION-260418-3-M-0418-02_managed-generation-api-trigger.meta.json` | configuration / structured data |
| `masterplan/delivery/05_reviews/VALIDATION-260418-M-0418-01_contract-build-api-trigger.meta.json` | configuration / structured data |
| `masterplan/delivery/05_reviews/VALIDATION-260418-M-0418-02_managed-generation-api-trigger.meta.json` | configuration / structured data |
| `masterplan/old legacy workflow/comfyui_config.json` | configuration / structured data |
| `masterplan/old legacy workflow/job_schema.json` | configuration / structured data |
| `masterplan/old legacy workflow/llm_response_schema.json` | configuration / structured data |
| `masterplan/old legacy workflow/model_mapping.json` | configuration / structured data |
| `masterplan/old legacy workflow/usage_schema.json` | configuration / structured data |
| `opencode.json` | configuration / structured data |
| `operator-console.example.json` | configuration / structured data |
| `platform_context_manifest.json` | configuration / structured data |
| `pyproject.toml` | configuration / structured data |
| `workflows/00_bootstrap_lifecycle_admin_v1/workflow.toml` | configuration / structured data |
| `workflows/01_governance_foundation_v1/bundle_governance.toml` | configuration / structured data |
| `workflows/01_governance_foundation_v1/bundle_governance/prompt_contract.json` | configuration / structured data |
| `workflows/01_governance_foundation_v1/workflow.toml` | configuration / structured data |
| `workflows/02_agent_runner_platform_v1/bundle_governance.toml` | configuration / structured data |
| `workflows/02_agent_runner_platform_v1/bundle_governance/prompt_contract.json` | configuration / structured data |
| `workflows/02_agent_runner_platform_v1/workflow.toml` | configuration / structured data |
| `workflows/_registry/coder_connections.json` | configuration / structured data |
| `workflows/_registry/coder_roles.json` | configuration / structured data |
| `workflows/_registry/coder_roles_opencode.json` | configuration / structured data |
| `workflows/_registry/coder_roles_qwen.json` | configuration / structured data |
| `workflows/_registry/role_policies.json` | configuration / structured data |
| `workflows/sdlc_00_codebase_v1/bundle_governance.toml` | configuration / structured data |
| `workflows/sdlc_00_codebase_v1/workflow.toml` | configuration / structured data |
| `workflows/sdlc_00_delivery_scaffold_v1/workflow.toml` | configuration / structured data |
| `workflows/sdlc_00_init_doc_v1/workflow.toml` | configuration / structured data |
| `workflows/sdlc_10_requirement_v1/workflow.toml` | configuration / structured data |
| `workflows/sdlc_20_planning_v1/workflow.toml` | configuration / structured data |
| `workflows/sdlc_30_backlog_v1/workflow.toml` | configuration / structured data |
| `workflows/sdlc_40_task_v1/workflow.toml` | configuration / structured data |
| `workflows/sdlc_50_implementation_v1/workflow.toml` | configuration / structured data |
| `workflows/sdlc_60_execution_v1/workflow.toml` | configuration / structured data |
| `workflows/sdlc_70_validation_v1/workflow.toml` | configuration / structured data |
| `workflows/sdlc_80_review_v1/workflow.toml` | configuration / structured data |

## 2. Architecture

### 2.1 Component Diagram

Generated from repository scan baseline.

### 2.2 Data Flow

Repository files are scanned, normalized into inventory rows, and rendered into codebase documentation artifacts.

### 2.3 External Interfaces

| Interface | Direction | Protocol | Description |
|-----------|-----------|----------|-------------|
| `.env.example` | outbound | markdown | configuration / structured data |
| `_test_payload.json` | outbound | markdown | configuration / structured data |
| `agent_runner_v2/bootstrap/bundles/core/current/bootstrap_publish_manifest.json` | outbound | markdown | configuration / structured data |
| `docs/repo/agent_runner/sdlc/delivery/00_initiatives/INIT-20260723-001_console-sdlc10-support.meta.json` | outbound | markdown | configuration / structured data |
| `docs/repo/agent_runner/sdlc/delivery/10_requirements/REQ-20260723-001_console-sdlc10-support.meta.json` | outbound | markdown | configuration / structured data |
| `docs/repo/agent_runner/sdlc/delivery/20_plans/PLAN-20260723-001_console-sdlc10-support.meta.json` | outbound | markdown | configuration / structured data |
| `docs/repo/agent_runner/sdlc/delivery/30_backlogs/BACKLOG-20260723-001_console-sdlc10-support.meta.json` | outbound | markdown | configuration / structured data |
| `docs/repo/agent_runner/sdlc/delivery/40_tasks/WI-20260723-001_console-sdlc10-support-01.meta.json` | outbound | markdown | configuration / structured data |
| `docs/repo/agent_runner/sdlc/delivery/40_tasks/WI-20260723-001_console-sdlc10-support-02.meta.json` | outbound | markdown | configuration / structured data |
| `docs/repo/agent_runner/sdlc/delivery/50_implementations/IMPL-20260723-001-001_console-sdlc10-support-01.meta.json` | outbound | markdown | configuration / structured data |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/01_inventory/codebase_inventory.meta.json` | outbound | markdown | configuration / structured data |
| `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/01_inventory/codebase_inventory.meta.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/00_bootstrap_lifecycle_admin_v1/workflow.toml` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/bundle_governance.toml` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/bundle_governance/prompt_contract.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/workflow.toml` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/bundle_governance.toml` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/bundle_governance/prompt_contract.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/workflow.toml` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/_registry/coder_connections.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/_registry/coder_roles.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/_registry/coder_roles_opencode.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/_registry/coder_roles_qwen.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/_registry/role_policies.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/sdlc_00_codebase_v1/bundle_governance.toml` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/sdlc_00_codebase_v1/workflow.toml` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/sdlc_00_delivery_scaffold_v1/workflow.toml` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/sdlc_00_init_doc_v1/workflow.toml` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/sdlc_10_requirement_v1/workflow.toml` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/sdlc_20_planning_v1/workflow.toml` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/sdlc_30_backlog_v1/workflow.toml` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/sdlc_40_task_v1/workflow.toml` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/sdlc_50_implementation_v1/workflow.toml` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/sdlc_60_execution_v1/workflow.toml` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/sdlc_70_validation_v1/workflow.toml` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/bootstrap/workflows/sdlc_80_review_v1/workflow.toml` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/foundation/current/governance_set_manifest.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/foundation/history/01GF-20260719-0864b1f2/governance_set_manifest.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/foundation/history/01GF-20260719-4e51c88b/governance_set_manifest.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/foundation/history/01GF-20260719-61ae0105/governance_set_manifest.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/foundation/history/01GF-20260719-96e730ab/governance_set_manifest.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/foundation/history/01GF-20260719-c5e882c3/governance_set_manifest.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/foundation/history/01GF-20260719-f15f153c/governance_set_manifest.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/01GF-20260719-0864b1f2-governance-foundation-audit.meta.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/01GF-20260719-0864b1f2-governance-foundation-review.meta.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/01GF-20260719-4e51c88b-governance-foundation-audit.meta.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/01GF-20260719-4e51c88b-governance-foundation-review.meta.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/01GF-20260719-61ae0105-governance-foundation-audit.meta.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/01GF-20260719-61ae0105-governance-foundation-review.meta.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/01GF-20260719-96e730ab-governance-foundation-audit.meta.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/01GF-20260719-96e730ab-governance-foundation-review.meta.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/01GF-20260719-c5e882c3-governance-foundation-audit.meta.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/01GF-20260719-c5e882c3-governance-foundation-review.meta.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/README.meta.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/01GF-20260719-f15f153c-governance-foundation-audit.meta.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/01GF-20260719-f15f153c-governance-foundation-review.meta.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/current/platform_set_manifest.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/history/02AR-20260721-2eaba4b3/platform_set_manifest.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/history/02PC-20260721-b092c705/platform_set_manifest.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/history/02PC-GEN-20260721-009/platform_set_manifest.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/02PC-20260721-b092c705-platform-core-audit.meta.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/02PC-20260721-b092c705-platform-core-review.meta.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/README.meta.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/02PC-GEN-20260721-009-platform-core-audit.meta.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/02PC-GEN-20260721-009-platform-core-review.meta.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/sdlc/current/sdlc_scaffold_manifest.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/sdlc_scaffold_manifest.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/template_registry.meta.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/AGENTS.meta.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/SDLC00SCF-20260722-914943f4-sdlc-scaffold-review.meta.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/template_registry.meta.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/AGENTS.meta.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/SDLC00SCF-20260722-cc2b347d-sdlc-scaffold-review.meta.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/template_registry.meta.json` | outbound | markdown | configuration / structured data |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/AGENTS.meta.json` | outbound | markdown | configuration / structured data |
| `masterplan/00_repo_master_docs_bootstrap_v1/workflow.toml` | outbound | markdown | configuration / structured data |
| `masterplan/delivery/03_tasks/TASK-20260418-01_contract-build-api-trigger.meta.json` | outbound | markdown | configuration / structured data |
| `masterplan/delivery/03_tasks/TASK-20260418-02_managed-generation-api-trigger.meta.json` | outbound | markdown | configuration / structured data |
| `masterplan/delivery/03_tasks/TASK-20260418-03_generation-run-api-surface.meta.json` | outbound | markdown | configuration / structured data |
| `masterplan/delivery/03_tasks/TASK-20260418-04_artifact-lifecycle-retrieval.meta.json` | outbound | markdown | configuration / structured data |
| `masterplan/delivery/03_tasks/TASK-20260418-05_router-registration-documentation.meta.json` | outbound | markdown | configuration / structured data |
| `masterplan/delivery/04_implementation_plans/IMPL-20260418-01_contract-build-api-trigger.meta.json` | outbound | markdown | configuration / structured data |
| `masterplan/delivery/04_implementation_plans/IMPL-20260418-02_managed-generation-api-trigger.meta.json` | outbound | markdown | configuration / structured data |
| `masterplan/delivery/04_implementation_plans/IMPL-20260418-03_generation-run-api-surface.meta.json` | outbound | markdown | configuration / structured data |
| `masterplan/delivery/05_reviews/REV-260418-01_rtask_T-0418-01_contract-build-api-trigger.meta.json` | outbound | markdown | configuration / structured data |
| `masterplan/delivery/05_reviews/REV-260418-02_rimpl_M-0418-01_contract-build-api-trigger.meta.json` | outbound | markdown | configuration / structured data |
| `masterplan/delivery/05_reviews/REV-260418-03_rtask_T-0418-02_managed-generation-api-trigger.meta.json` | outbound | markdown | configuration / structured data |
| `masterplan/delivery/05_reviews/REV-260418-04_rtask_T-0418-02_managed-generation-api-trigger.meta.json` | outbound | markdown | configuration / structured data |
| `masterplan/delivery/05_reviews/REV-260418-05_rimpl_M-0418-02_managed-generation-api-trigger.meta.json` | outbound | markdown | configuration / structured data |
| `masterplan/delivery/05_reviews/VALIDATION-260418-2-M-0418-01_contract-build-api-trigger.meta.json` | outbound | markdown | configuration / structured data |
| `masterplan/delivery/05_reviews/VALIDATION-260418-2-M-0418-02_managed-generation-api-trigger.meta.json` | outbound | markdown | configuration / structured data |
| `masterplan/delivery/05_reviews/VALIDATION-260418-3-M-0418-02_managed-generation-api-trigger.meta.json` | outbound | markdown | configuration / structured data |
| `masterplan/delivery/05_reviews/VALIDATION-260418-M-0418-01_contract-build-api-trigger.meta.json` | outbound | markdown | configuration / structured data |
| `masterplan/delivery/05_reviews/VALIDATION-260418-M-0418-02_managed-generation-api-trigger.meta.json` | outbound | markdown | configuration / structured data |
| `masterplan/old legacy workflow/comfyui_config.json` | outbound | markdown | configuration / structured data |
| `masterplan/old legacy workflow/job_schema.json` | outbound | markdown | configuration / structured data |
| `masterplan/old legacy workflow/llm_response_schema.json` | outbound | markdown | configuration / structured data |
| `masterplan/old legacy workflow/model_mapping.json` | outbound | markdown | configuration / structured data |
| `masterplan/old legacy workflow/usage_schema.json` | outbound | markdown | configuration / structured data |
| `opencode.json` | outbound | markdown | configuration / structured data |
| `operator-console.example.json` | outbound | markdown | configuration / structured data |
| `platform_context_manifest.json` | outbound | markdown | configuration / structured data |
| `pyproject.toml` | outbound | markdown | configuration / structured data |
| `workflows/00_bootstrap_lifecycle_admin_v1/workflow.toml` | outbound | markdown | configuration / structured data |
| `workflows/01_governance_foundation_v1/bundle_governance.toml` | outbound | markdown | configuration / structured data |
| `workflows/01_governance_foundation_v1/bundle_governance/prompt_contract.json` | outbound | markdown | configuration / structured data |
| `workflows/01_governance_foundation_v1/workflow.toml` | outbound | markdown | configuration / structured data |
| `workflows/02_agent_runner_platform_v1/bundle_governance.toml` | outbound | markdown | configuration / structured data |
| `workflows/02_agent_runner_platform_v1/bundle_governance/prompt_contract.json` | outbound | markdown | configuration / structured data |
| `workflows/02_agent_runner_platform_v1/workflow.toml` | outbound | markdown | configuration / structured data |
| `workflows/_registry/coder_connections.json` | outbound | markdown | configuration / structured data |
| `workflows/_registry/coder_roles.json` | outbound | markdown | configuration / structured data |
| `workflows/_registry/coder_roles_opencode.json` | outbound | markdown | configuration / structured data |
| `workflows/_registry/coder_roles_qwen.json` | outbound | markdown | configuration / structured data |
| `workflows/_registry/role_policies.json` | outbound | markdown | configuration / structured data |
| `workflows/sdlc_00_codebase_v1/bundle_governance.toml` | outbound | markdown | configuration / structured data |
| `workflows/sdlc_00_codebase_v1/workflow.toml` | outbound | markdown | configuration / structured data |
| `workflows/sdlc_00_delivery_scaffold_v1/workflow.toml` | outbound | markdown | configuration / structured data |
| `workflows/sdlc_00_init_doc_v1/workflow.toml` | outbound | markdown | configuration / structured data |
| `workflows/sdlc_10_requirement_v1/workflow.toml` | outbound | markdown | configuration / structured data |
| `workflows/sdlc_20_planning_v1/workflow.toml` | outbound | markdown | configuration / structured data |
| `workflows/sdlc_30_backlog_v1/workflow.toml` | outbound | markdown | configuration / structured data |
| `workflows/sdlc_40_task_v1/workflow.toml` | outbound | markdown | configuration / structured data |
| `workflows/sdlc_50_implementation_v1/workflow.toml` | outbound | markdown | configuration / structured data |
| `workflows/sdlc_60_execution_v1/workflow.toml` | outbound | markdown | configuration / structured data |
| `workflows/sdlc_70_validation_v1/workflow.toml` | outbound | markdown | configuration / structured data |
| `workflows/sdlc_80_review_v1/workflow.toml` | outbound | markdown | configuration / structured data |

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
| 2026-07-23 | Initial baseline generated from repository scan | 127 modules/files | sdlc_00_codebase_v1 |
