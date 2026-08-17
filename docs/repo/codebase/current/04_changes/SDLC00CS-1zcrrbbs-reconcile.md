---
title: "Change Impact: agent-runner-v2 codebase reconcile"
template_id: "CB-04"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
change_id: "SDLC00CS-1zcrrbbs"
task_id: "sdlc_00_codebase_scaffold_v1"
initiative_id: "codebase-doc-bootstrap"
created: "2026-08-17T21:19:17+08:00"
author: "sdlc_00_codebase_scaffold_v1"
---

# Change Impact: agent-runner-v2 codebase reconcile

## 1. Change Summary

### 1.1 Description

Repository scan bootstrap/reconcile generated or refreshed the codebase documentation baseline.

### 1.2 Rationale

Keep `/docs/repo/codebase/current` synchronized with the current repository state even when code changes occurred outside the normal workflow SOP.

## 2. Changed Files

### 2.1 Source Code Changes

| File | Change Type | Description | Impact |
|------|-------------|-------------|--------|
| `.env.example` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/__init__.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/action_result.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/actions/__init__.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/actions/archive_inputs.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/actions/copy_artifact.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/actions/documentation_validation_core.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/actions/finalize_bootstrap.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/actions/preset_config.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/actions/promote_artifact.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/actions/promote_init.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/actions/scan_repo_codebase.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/actions/sdlc_shared_actions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/actions/step_completion.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/actions/sync_codebase_docs.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/actions/sync_system_docs.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/actions/validate_codebase_docs.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/actions/validate_system_docs.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/api_key_pool.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/artifact_keys.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/artifact_paths.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/bootstrap_publish_manifest.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/foundation/BASE_COMPOSITION_STANDARD_v1.0.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/foundation/BUNDLE_TAXONOMY.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/foundation/DOCUMENT_AUTHORITY.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/foundation/GOVERNANCE_LIFECYCLE.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/foundation/governance_set_manifest.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/foundation/LAYER_MODEL.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/foundation/METADATA_STANDARD.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/foundation/README.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/current/BUNDLE_AUTHORING_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/current/METADATA_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/current/platform_set_manifest.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/current/README.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/current/RUNTIME_MODEL.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/current/SHARED_SERVICES.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/current/VALIDATION_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/history/02AR-20260721-2eaba4b3/BUNDLE_AUTHORING_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/history/02AR-20260721-2eaba4b3/METADATA_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/history/02AR-20260721-2eaba4b3/platform_set_manifest.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/history/02AR-20260721-2eaba4b3/README.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/history/02AR-20260721-2eaba4b3/RUNTIME_MODEL.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/history/02AR-20260721-2eaba4b3/SHARED_SERVICES.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/history/02AR-20260721-2eaba4b3/VALIDATION_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/history/02PC-20260721-b092c705/BUNDLE_AUTHORING_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/history/02PC-20260721-b092c705/METADATA_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/history/02PC-20260721-b092c705/platform_set_manifest.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/history/02PC-20260721-b092c705/README.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/history/02PC-20260721-b092c705/RUNTIME_MODEL.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/history/02PC-20260721-b092c705/SHARED_SERVICES.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/history/02PC-20260721-b092c705/VALIDATION_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/history/02PC-GEN-20260721-009/BUNDLE_AUTHORING_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/history/02PC-GEN-20260721-009/METADATA_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/history/02PC-GEN-20260721-009/platform_set_manifest.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/history/02PC-GEN-20260721-009/README.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/history/02PC-GEN-20260721-009/RUNTIME_MODEL.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/history/02PC-GEN-20260721-009/SHARED_SERVICES.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/history/02PC-GEN-20260721-009/VALIDATION_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/runs/02PC-20260721-b092c705/02PC-20260721-b092c705-platform-context-inventory.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/runs/02PC-20260721-b092c705/02PC-20260721-b092c705-platform-core-audit.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/runs/02PC-20260721-b092c705/02PC-20260721-b092c705-platform-core-audit.meta.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/runs/02PC-20260721-b092c705/02PC-20260721-b092c705-platform-core-review.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/runs/02PC-20260721-b092c705/02PC-20260721-b092c705-platform-core-review.meta.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/runs/02PC-20260721-b092c705/02PC-20260721-b092c705-platform-core-validation.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/runs/02PC-20260721-b092c705/BUNDLE_AUTHORING_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/runs/02PC-20260721-b092c705/METADATA_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/runs/02PC-20260721-b092c705/README.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/runs/02PC-20260721-b092c705/README.meta.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/runs/02PC-20260721-b092c705/RUNTIME_MODEL.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/runs/02PC-20260721-b092c705/SHARED_SERVICES.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/runs/02PC-20260721-b092c705/VALIDATION_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/runs/02PC-GEN-20260721-009/02PC-GEN-20260721-009-platform-context-inventory.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/runs/02PC-GEN-20260721-009/02PC-GEN-20260721-009-platform-core-audit.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/runs/02PC-GEN-20260721-009/02PC-GEN-20260721-009-platform-core-audit.meta.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/runs/02PC-GEN-20260721-009/02PC-GEN-20260721-009-platform-core-review.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/runs/02PC-GEN-20260721-009/02PC-GEN-20260721-009-platform-core-review.meta.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/runs/02PC-GEN-20260721-009/02PC-GEN-20260721-009-platform-core-validation.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/runs/02PC-GEN-20260721-009/BUNDLE_AUTHORING_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/runs/02PC-GEN-20260721-009/METADATA_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/runs/02PC-GEN-20260721-009/README.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/runs/02PC-GEN-20260721-009/RUNTIME_MODEL.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/runs/02PC-GEN-20260721-009/SHARED_SERVICES.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/runs/02PC-GEN-20260721-009/VALIDATION_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/current/01_templates/01_DRAFT_INIT_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/current/01_templates/02_INIT_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/current/01_templates/03_REQ_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/current/01_templates/04_PLAN_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/current/01_templates/05_BACKLOG_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/current/01_templates/06_TASK_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/current/01_templates/07_IMPL_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/current/01_templates/08_VALID_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/current/01_templates/09_REV_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/current/01_templates/10_MEM_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/current/01_templates/11_CLOSE_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/current/01_templates/template_registry.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/current/01_templates/WORKFLOW_SOP_v1.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/current/02_agents/AGENT-executor.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/current/02_agents/AGENT-implementation-planner.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/current/02_agents/AGENT-memory-manager.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/current/02_agents/AGENT-planner.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/current/02_agents/AGENT-reviewer.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/current/02_agents/AGENT-task-decomposer.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/current/02_agents/AGENTS.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/current/02_agents/DELIVERY_STATUS_RULES_v1.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/current/sdlc_scaffold_manifest.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/01_DRAFT_INIT_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/02_INIT_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/03_REQ_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/04_PLAN_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/05_BACKLOG_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/06_TASK_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/07_IMPL_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/08_VALID_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/09_REV_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/10_MEM_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/11_CLOSE_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/template_registry.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/WORKFLOW_SOP_v1.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-executor.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-implementation-planner.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-memory-manager.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-planner.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-reviewer.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-task-decomposer.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/02_agents/AGENTS.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/02_agents/DELIVERY_STATUS_RULES_v1.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/sdlc_scaffold_manifest.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/01_DRAFT_INIT_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/02_INIT_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/03_REQ_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/04_PLAN_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/05_BACKLOG_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/06_TASK_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/07_IMPL_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/08_VALID_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/09_REV_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/10_MEM_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/11_CLOSE_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/template_registry.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/WORKFLOW_SOP_v1.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-executor.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-implementation-planner.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-memory-manager.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-planner.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-reviewer.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-task-decomposer.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/02_agents/AGENTS.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/02_agents/DELIVERY_STATUS_RULES_v1.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/SDLC00SCF-20260722-3a011a52-sdlc-scaffold-review.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/01_DRAFT_INIT_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/02_INIT_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/03_REQ_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/04_PLAN_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/05_BACKLOG_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/06_TASK_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/07_IMPL_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/08_VALID_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/09_REV_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/10_MEM_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/11_CLOSE_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/template_registry.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/template_registry.meta.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/WORKFLOW_SOP_v1.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/AGENT-executor.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/AGENT-implementation-planner.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/AGENT-memory-manager.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/AGENT-planner.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/AGENT-reviewer.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/AGENT-task-decomposer.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/AGENTS.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/AGENTS.meta.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/DELIVERY_STATUS_RULES_v1.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/SDLC00SCF-20260722-914943f4-sdlc-scaffold-review.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/SDLC00SCF-20260722-914943f4-sdlc-scaffold-review.meta.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/01_DRAFT_INIT_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/02_INIT_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/03_REQ_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/04_PLAN_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/05_BACKLOG_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/06_TASK_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/07_IMPL_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/08_VALID_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/09_REV_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/10_MEM_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/11_CLOSE_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/template_registry.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/template_registry.meta.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/WORKFLOW_SOP_v1.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/AGENT-executor.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/AGENT-implementation-planner.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/AGENT-memory-manager.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/AGENT-planner.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/AGENT-reviewer.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/AGENT-task-decomposer.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/AGENTS.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/AGENTS.meta.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/DELIVERY_STATUS_RULES_v1.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/SDLC00SCF-20260722-cc2b347d-sdlc-scaffold-review.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/SDLC00SCF-20260722-cc2b347d-sdlc-scaffold-review.meta.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/01_DRAFT_INIT_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/02_INIT_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/03_REQ_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/04_PLAN_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/05_BACKLOG_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/06_TASK_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/07_IMPL_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/08_VALID_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/09_REV_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/10_MEM_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/11_CLOSE_template.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/template_registry.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/template_registry.meta.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/WORKFLOW_SOP_v1.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/AGENT-executor.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/AGENT-implementation-planner.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/AGENT-memory-manager.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/AGENT-planner.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/AGENT-reviewer.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/AGENT-task-decomposer.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/AGENTS.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/AGENTS.meta.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/DELIVERY_STATUS_RULES_v1.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/platform/agent_workflow_builder/current/standards/COMPOSITION_SYSTEM_STANDARD.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/00_bootstrap_lifecycle_admin_v1/actions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/00_bootstrap_lifecycle_admin_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/00_bootstrap_lifecycle_admin_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/00_bootstrap_lifecycle_admin_v1/README.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/00_bootstrap_lifecycle_admin_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/actions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/bundle_governance.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/bundle_governance/action_policy.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/bundle_governance/core_governance.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/bundle_governance/generated/AGENTS.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/bundle_governance/generated/CLAUDE.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/bundle_governance/generated/QWEN.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/bundle_governance/prompt_contract.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/bundle_governance/prompt_layout.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/bundle_governance/prompt_sop.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/bundle_governance/review_audit_contract.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/prompts/audit_governance_foundation_docs/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/prompts/generate_governance_foundation_docs/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/prompts/refine_governance_foundation_docs/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/prompts/review_governance_foundation_docs/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/README.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/actions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/bundle_governance.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/bundle_governance/action_policy.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/bundle_governance/core_governance.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/bundle_governance/generated/AGENTS.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/bundle_governance/generated/CLAUDE.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/bundle_governance/generated/QWEN.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/bundle_governance/prompt_contract.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/bundle_governance/prompt_layout.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/bundle_governance/prompt_sop.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/bundle_governance/review_audit_contract.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/prompts/audit_platform_core_docs/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/prompts/generate_platform_core_docs/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/prompts/refine_platform_core_docs/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/prompts/review_platform_core_docs/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/README.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/_registry/coder_connections.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/_registry/coder_roles.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/_registry/coder_roles_opencode.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/_registry/coder_roles_qwen.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/_registry/role_policies.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agentic_workflow_builder/actions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agentic_workflow_builder/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agentic_workflow_builder/impls/detailed/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agentic_workflow_builder/impls/detailed/prompts/04_implement_actions.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agentic_workflow_builder/impls/detailed/prompts/05_generate_prompts.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agentic_workflow_builder/impls/minimal/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agentic_workflow_builder/impls/minimal/prompts/04_implement_actions.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agentic_workflow_builder/impls/minimal/prompts/05_generate_prompts.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agentic_workflow_builder/prompts/02_analyze_workflow_structure.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agentic_workflow_builder/prompts/03_design_workflow_steps.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agentic_workflow_builder/prompts/04_implement_actions.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agentic_workflow_builder/prompts/05_generate_prompts.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agentic_workflow_builder/README.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agentic_workflow_builder/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agnes_gen_video_v1/.env.sample` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agnes_gen_video_v1/actions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agnes_gen_video_v1/config.json.sample` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agnes_gen_video_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agnes_gen_video_v1/impls/agnes_v2/actions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agnes_gen_video_v1/impls/agnes_v2/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agnes_gen_video_v1/impls/happyhorse_v1_1/actions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agnes_gen_video_v1/impls/happyhorse_v1_1/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agnes_gen_video_v1/README.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agnes_gen_video_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agnes_media_gen_v1/.env.sample` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agnes_media_gen_v1/actions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agnes_media_gen_v1/config.json.sample` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agnes_media_gen_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agnes_media_gen_v1/guardrails.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agnes_media_gen_v1/impls/agnes_media_v1/actions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agnes_media_gen_v1/impls/agnes_media_v1/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agnes_media_gen_v1/impls/agnes_media_v1/prompts/step_1_extract/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agnes_media_gen_v1/impls/agnes_media_v1/prompts/step_2_generate/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agnes_media_gen_v1/README.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/agnes_media_gen_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/actions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/impls/builder/bootstrap/builder_actions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/impls/builder/bootstrap/README.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/impls/builder/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/impls/builder/INPUT_ARTIFACTS.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/impls/builder/OUTPUT_ARTIFACTS.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/impls/builder/SPECIALIZED_STEPS.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/impls/generator/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/impls/generator/INPUT_ARTIFACTS.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/impls/generator/OUTPUT_ARTIFACTS.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/PLUGIN_ARCHITECTURE.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/prompts/analyze_requirement/builder/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/prompts/analyze_requirement/generator/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/prompts/challenge_plan/builder/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/prompts/challenge_plan/generator/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/prompts/critic_impl/builder/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/prompts/critic_impl/generator/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/prompts/gatekeep_package/builder/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/prompts/gatekeep_package/generator/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/prompts/implement_domain/builder/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/prompts/implement_domain/generator/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/prompts/plan_domain_logic/builder/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/prompts/plan_domain_logic/generator/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/prompts/review_package/builder/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/prompts/review_package/generator/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/README.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/artifact_generator_builder/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/codebase_intelligence/actions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/codebase_intelligence/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/codebase_intelligence/impls/executive_summary/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/codebase_intelligence/impls/executive_summary/prompts/analyze_health/executive_summary.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/codebase_intelligence/impls/executive_summary/prompts/analyze_security/executive_summary.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/codebase_intelligence/impls/executive_summary/prompts/generate_audience_meta/executive_summary.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/codebase_intelligence/impls/executive_summary/prompts/generate_findings_report/executive_summary.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/codebase_intelligence/impls/security_focused/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/codebase_intelligence/impls/security_focused/prompts/analyze_health/security_focused.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/codebase_intelligence/impls/security_focused/prompts/analyze_security/security_focused.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/codebase_intelligence/impls/security_focused/prompts/generate_audience_meta/security_focused.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/codebase_intelligence/impls/security_focused/prompts/generate_findings_report/security_focused.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/codebase_intelligence/impls/technical_deep_dive/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/codebase_intelligence/impls/technical_deep_dive/prompts/analyze_health/technical_deep_dive.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/codebase_intelligence/impls/technical_deep_dive/prompts/analyze_security/technical_deep_dive.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/codebase_intelligence/impls/technical_deep_dive/prompts/generate_audience_meta/technical_deep_dive.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/codebase_intelligence/impls/technical_deep_dive/prompts/generate_findings_report/technical_deep_dive.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/codebase_intelligence/prompts/analyze_health/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/codebase_intelligence/prompts/analyze_security/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/codebase_intelligence/prompts/generate_audience_meta/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/codebase_intelligence/prompts/generate_findings_report/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/codebase_intelligence/README.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/codebase_intelligence/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/.env.sample` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/actions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/api_actions/__init__.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/api_actions/render_image/__init__.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/api_actions/render_image/agnes_v1.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/api_actions/render_video/__init__.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/api_actions/render_video/agnes_v2.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/config.json.sample` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/impls/__init__.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/impls/agnes/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/impls/llm/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/prompts/__init__.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/prompts/extract_desc/__init__.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/prompts/extract_desc/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/prompts/extract_desc/standard_chinese.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/prompts/extract_desc/v1.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/prompts/generate_images/agnes_v1.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/prompts/generate_images/token_plan_image.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/prompts/generate_images/token_plan_wan27.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/prompts/generate_prompts/__init__.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/prompts/generate_prompts/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/prompts/generate_prompts/v1.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/prompts/generate_prompts/v2.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/prompts/generate_prompts/v2_chinese.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/prompts/generate_prompts/v3.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/prompts/generate_prompts/v4.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/prompts/generate_prompts/v5.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/prompts/generate_prompts/v6.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/prompts/generate_prompts/v7.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/prompts/generate_prompts/v8.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/prompts/generate_prompts/v9.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/prompts/generate_prompts/v9_chinese.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/prompts/generate_videos/agnes_v2.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/prompts/generate_videos/alibaba_token_plan.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/prompts/generate_videos/happyhorse-1.1-i2v.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/prompts/generate_videos/happyhorse-1.1-t2v.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/README.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/tests/__init__.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/tests/test_context.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/tests/test_prompt_slots.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/gen_media_content_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_scaffold_v1/actions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_scaffold_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_scaffold_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_scaffold_v1/prompts/generate_agent_contracts/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_scaffold_v1/prompts/generate_templates/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_scaffold_v1/prompts/refine_codebase_docs/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_scaffold_v1/prompts/refine_scaffold/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_scaffold_v1/prompts/review_scaffold/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_scaffold_v1/prompts/review_sync_log/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_scaffold_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_init_doc_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_init_doc_v1/DRAFT_INIT_AUTHORING_GUIDE.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_init_doc_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_init_doc_v1/prompts/address_critique/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_init_doc_v1/prompts/generate_initiative/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_init_doc_v1/prompts/refine_initiative/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_init_doc_v1/prompts/review_initiative/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_init_doc_v1/prompts/technical_critique/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_init_doc_v1/README.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_init_doc_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/actions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/prompts/backlog_address_critique/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/prompts/backlog_generate/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/prompts/backlog_refine/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/prompts/backlog_review/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/prompts/backlog_technical_critique/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/prompts/init_address_critique/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/prompts/init_generate/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/prompts/init_refine/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/prompts/init_review/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/prompts/init_technical_critique/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/prompts/plan_address_critique/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/prompts/plan_generate/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/prompts/plan_refine/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/prompts/plan_review/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/prompts/plan_technical_critique/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/prompts/req_address_critique/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/prompts/req_generate/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/prompts/req_refine/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/prompts/req_review/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/prompts/req_technical_critique/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/prompts/task_address_critique/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/prompts/task_generate/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/prompts/task_refine/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/prompts/task_review/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/prompts/task_technical_critique/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_requirement_planning_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_01_impl_exec_review_v1/actions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_01_impl_exec_review_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_01_impl_exec_review_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_01_impl_exec_review_v1/prompts/exec_address/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_01_impl_exec_review_v1/prompts/exec_challenge/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_01_impl_exec_review_v1/prompts/exec_execute/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_01_impl_exec_review_v1/prompts/exec_gatekeep/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_01_impl_exec_review_v1/prompts/exec_refine/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_01_impl_exec_review_v1/prompts/impl_address/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_01_impl_exec_review_v1/prompts/impl_challenge/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_01_impl_exec_review_v1/prompts/impl_gatekeep/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_01_impl_exec_review_v1/prompts/impl_generate/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_01_impl_exec_review_v1/prompts/impl_refine/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_01_impl_exec_review_v1/prompts/rev_address/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_01_impl_exec_review_v1/prompts/rev_critique/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_01_impl_exec_review_v1/prompts/rev_generate/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_01_impl_exec_review_v1/prompts/rev_refine/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_01_impl_exec_review_v1/prompts/rev_review/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_01_impl_exec_review_v1/prompts/val_address/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_01_impl_exec_review_v1/prompts/val_challenge/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_01_impl_exec_review_v1/prompts/val_gatekeep/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_01_impl_exec_review_v1/prompts/val_generate/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_01_impl_exec_review_v1/prompts/val_refine/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_01_impl_exec_review_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_10_requirement_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_10_requirement_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_10_requirement_v1/prompts/address_critique/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_10_requirement_v1/prompts/generate_requirements/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_10_requirement_v1/prompts/refine_requirements/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_10_requirement_v1/prompts/review_requirements/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_10_requirement_v1/prompts/technical_critique/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_10_requirement_v1/README.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_10_requirement_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_20_planning_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_20_planning_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_20_planning_v1/prompts/address_critique/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_20_planning_v1/prompts/generate_plan/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_20_planning_v1/prompts/refine_plan/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_20_planning_v1/prompts/review_plan/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_20_planning_v1/prompts/technical_critique/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_20_planning_v1/README.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_20_planning_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_30_backlog_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_30_backlog_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_30_backlog_v1/prompts/address_critique/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_30_backlog_v1/prompts/generate_backlog/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_30_backlog_v1/prompts/refine_backlog/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_30_backlog_v1/prompts/review_backlog/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_30_backlog_v1/prompts/technical_critique/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_30_backlog_v1/README.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_30_backlog_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_40_task_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_40_task_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_40_task_v1/prompts/address_critique/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_40_task_v1/prompts/generate_task/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_40_task_v1/prompts/refine_task/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_40_task_v1/prompts/review_task/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_40_task_v1/prompts/technical_critique/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_40_task_v1/README.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_40_task_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_50_implementation_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_50_implementation_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_50_implementation_v1/prompts/address_challenges/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_50_implementation_v1/prompts/challenge_implementation/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_50_implementation_v1/prompts/gatekeep_implementation/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_50_implementation_v1/prompts/generate_implementation/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_50_implementation_v1/prompts/refine_implementation/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_50_implementation_v1/README.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_50_implementation_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_60_execution_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_60_execution_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_60_execution_v1/prompts/address_challenges/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_60_execution_v1/prompts/challenge_execution/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_60_execution_v1/prompts/execute_task/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_60_execution_v1/prompts/gatekeep_execution/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_60_execution_v1/prompts/refine_execution/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_60_execution_v1/README.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_60_execution_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_70_validation_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_70_validation_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_70_validation_v1/prompts/address_challenges/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_70_validation_v1/prompts/challenge_validation/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_70_validation_v1/prompts/gatekeep_validation/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_70_validation_v1/prompts/generate_validation/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_70_validation_v1/prompts/refine_validation/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_70_validation_v1/README.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_70_validation_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_80_review_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_80_review_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_80_review_v1/prompts/address_critique/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_80_review_v1/prompts/generate_review/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_80_review_v1/prompts/refine_documents/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_80_review_v1/prompts/review_all/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_80_review_v1/prompts/technical_critique/standard.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_80_review_v1/README.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_80_review_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/text_summarizer_ayz/actions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/text_summarizer_ayz/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/text_summarizer_ayz/impls/key_points/actions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/text_summarizer_ayz/impls/key_points/impl.yaml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/text_summarizer_ayz/impls/key_points/prompts/03_transform_key_points.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/text_summarizer_ayz/prompts/02_analyze_structure.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/text_summarizer_ayz/prompts/03_transform_content.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/text_summarizer_ayz/README.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/text_summarizer_ayz/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bundle_governance.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bundle_loader.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bundle_taxonomy.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/cleanup_commands.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/cleanup_generated_docs.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/cli_runtime.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/codebase_docs.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/codebase_init_commands.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/coder_adapters.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/coder_registry.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/concurrent_api.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/config/__init__.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/config/section_requirements.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/config_loader.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/constants.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/daemon_v2.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/doc_paths.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/doc_text.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/documentation_guardrails.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/engine_commands.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/exceptions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/execution_core.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/execution_request.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/execution_result.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/execution_support.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/failure_runtime.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/hooks_protocols.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/job_state.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/list_runs_commands.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/manual_runtime.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/manual_runtime_deps.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/notification_manager.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/notifications.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/path_primitives.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/qwenpaw_client.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/recovery_runtime.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/reset_step_commands.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/run_agent.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/runner_actions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/runner_logger.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/runtime_context.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/runtime_hooks.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/runtime_utils.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/shared_runtime_deps.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/show_run_commands.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/single_instance.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/site_styles.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/state_defaults.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/status_commands.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/step_execution_runtime.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/step_runner.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/submit_commands.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/submitter.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/sync_workflows.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/system_docs.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/task_runtime.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/tools/agent_tools.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/v2/__init__.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/v2/backend_client.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/v2/backend_client_v1.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/v2/queue.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/v2/routing_runtime.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/v2/sync.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/v2/transition_runtime.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/v2/workflow_router.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/workflow_bundle_validate_commands.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/workflow_bundle_validator.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/workflow_package_validator.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/workflow_packages/__init__.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/workflow_packages/actions/__init__.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/workflow_packages/base.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/workflow_packages/extensions_base.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/workflow_packages/hooks.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/workflow_packages/loader.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/workflow_packages/registry.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/workflow_path_contracts.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/workflow_runtime.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/workflow_spec_commands.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/workflow_specs.py` | modify | part of repository scan baseline | medium |
| `AGENTS.md` | modify | part of repository scan baseline | medium |
| `config.json` | modify | part of repository scan baseline | medium |
| `docs/developer/AGENT_RUNNER_V2_SPECIALIST.md` | modify | part of repository scan baseline | medium |
| `docs/developer/ARCHITECTURAL_REFACTOR.md` | modify | part of repository scan baseline | medium |
| `docs/developer/CODER_IMPLEMENTATION_SOP.md` | modify | part of repository scan baseline | medium |
| `docs/developer/DOCSTRING_REVIEW_PLAN.md` | modify | part of repository scan baseline | medium |
| `docs/developer/DOCUMENTATION_CONSOLIDATION.md` | modify | part of repository scan baseline | medium |
| `docs/developer/JOB_DEFINITION_DICTIONARY.md` | modify | part of repository scan baseline | medium |
| `docs/developer/ROUTING_SIMPLIFICATION.md` | modify | part of repository scan baseline | medium |
| `docs/developer/WORKFLOW_REVISION_HISTORY_IMPLEMENTATION_PLAN.md` | modify | part of repository scan baseline | medium |
| `docs/developer/WORKFLOW_REVISION_HISTORY_SPEC.md` | modify | part of repository scan baseline | medium |
| `docs/QwenPaw/gen_media_content_v1/PLAN.md` | modify | part of repository scan baseline | medium |
| `docs/QwenPaw/gen_media_content_v1/REQUIREMENTS.md` | modify | part of repository scan baseline | medium |
| `docs/QwenPaw/gen_media_content_v1/TASKS_PHASE1.md` | modify | part of repository scan baseline | medium |
| `docs/QwenPaw/job-submission-reference.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/00_draft_initiatives/DRAFT-INIT-20260806-001_incremental-codebase-doc-update.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/00_initiatives/INIT-20260806-001_incremental-codebase-doc-update.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/00_initiatives/INIT-20260806-001_incremental-codebase-doc-update.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/10_requirements/REQ-20260806-001_incremental-codebase-doc-update.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/10_requirements/REQ-20260806-001_incremental-codebase-doc-update.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/20_plans/PLAN-20260806-001_incremental-codebase-doc-update.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/20_plans/PLAN-20260806-001_incremental-codebase-doc-update.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/30_backlogs/BACKLOG-20260806-001_incremental-codebase-doc-update.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/30_backlogs/BACKLOG-20260806-001_incremental-codebase-doc-update.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/40_tasks/TASK-20260814-001-01_gen-media-content-scaffolding.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/40_tasks/TASK-20260814-001-02_gen-media-content-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/40_tasks/TASK-20260815-001-03_gen-media-content-image-provider.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/40_tasks/TASK-20260815-001-04_gen-media-content-video-provider-agnes.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/40_tasks/TASK-20260815-001-05_gen-media-content-video-provider-happyhorse.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/40_tasks/TASK-20260815-001-06_gen-media-content-video-provider-none.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/40_tasks/TASK-20260815-001-07_gen-media-content-llm-prompts.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/40_tasks/TASK-20260815-001-08_gen-media-content-bcs-impls.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/40_tasks/TASK-20260815-001-09_gen-media-content-orchestrator-integration.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/50_implementations/IMPL-20260814-001-001_gen-media-content-scaffolding.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/50_implementations/IMPL-20260814-001-001_gen-media-content-scaffolding.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/50_implementations/IMPL-20260815-001-001_gen-media-content-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/50_implementations/IMPL-20260815-001-001_gen-media-content-actions.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/50_implementations/IMPL-20260815-001-002_gen-media-content-image-provider.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/50_implementations/IMPL-20260815-001-002_gen-media-content-image-provider.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/50_implementations/IMPL-20260815-001-003_gen-media-content-video-provider-agnes.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/50_implementations/IMPL-20260815-001-003_gen-media-content-video-provider-agnes.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/50_implementations/IMPL-20260815-001-004_gen-media-content-video-provider-agnes.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/50_implementations/IMPL-20260815-001-004_gen-media-content-video-provider-agnes.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/50_implementations/IMPL-20260815-001-004_gen-media-content-video-provider-happyhorse.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/50_implementations/IMPL-20260815-001-004_gen-media-content-video-provider-happyhorse.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/50_implementations/IMPL-20260815-001-005_gen-media-content-video-provider-none.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/50_implementations/IMPL-20260815-001-005_gen-media-content-video-provider-none.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/50_implementations/IMPL-20260815-001-006_gen-media-content-bcs-impls.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/50_implementations/IMPL-20260815-001-006_gen-media-content-bcs-impls.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/50_implementations/IMPL-20260815-001-006_gen-media-content-llm-prompts.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/50_implementations/IMPL-20260815-001-006_gen-media-content-llm-prompts.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/50_implementations/IMPL-20260815-001-007_gen-media-content-orchestrator-integration.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/50_implementations/IMPL-20260815-001-007_gen-media-content-orchestrator-integration.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/60_executions/EXEC-20260815-001-001_gen-media-content-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/60_executions/EXEC-20260815-001-001_gen-media-content-actions.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/60_executions/EXEC-20260815-001-002_gen-media-content-image-provider.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/60_executions/EXEC-20260815-001-002_gen-media-content-image-provider.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/60_executions/EXEC-20260815-001-003_gen-media-content-video-provider-agnes.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/60_executions/EXEC-20260815-001-003_gen-media-content-video-provider-agnes.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/60_executions/EXEC-20260815-001-003_gen-media-content-video-provider-happyhorse.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/60_executions/EXEC-20260815-001-003_gen-media-content-video-provider-happyhorse.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/60_executions/EXEC-20260815-001-004_gen-media-content-video-provider-none.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/60_executions/EXEC-20260815-001-004_gen-media-content-video-provider-none.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/60_executions/EXEC-20260815-001-005_gen-media-content-bcs-impls.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/60_executions/EXEC-20260815-001-005_gen-media-content-bcs-impls.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/60_executions/EXEC-20260815-001-005_gen-media-content-llm-prompts.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/60_executions/EXEC-20260815-001-005_gen-media-content-llm-prompts.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/60_executions/EXEC-20260815-001-006_gen-media-content-orchestrator-integration.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/70_validations/VAL-20260815-001_gen-media-content-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/70_validations/VAL-20260815-001_gen-media-content-actions.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/70_validations/VAL-20260815-002_gen-media-content-image-provider.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/70_validations/VAL-20260815-002_gen-media-content-image-provider.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/70_validations/VAL-20260815-003_gen-media-content-video-provider-happyhorse.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/70_validations/VAL-20260815-003_gen-media-content-video-provider-happyhorse.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/70_validations/VAL-20260815-004_gen-media-content-video-provider-agnes.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/70_validations/VAL-20260815-004_gen-media-content-video-provider-agnes.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/70_validations/VAL-20260815-005_gen-media-content-video-provider-none.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/70_validations/VAL-20260815-005_gen-media-content-video-provider-none.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/70_validations/VAL-20260815-006_gen-media-content-bcs-impls.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/70_validations/VAL-20260815-006_gen-media-content-bcs-impls.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/70_validations/VAL-20260815-006_gen-media-content-llm-prompts.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/70_validations/VAL-20260815-006_gen-media-content-llm-prompts.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/CLOSE-20260815-001_gen-media-content-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/CLOSE-20260815-002_gen-media-content-image-provider.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/CLOSE-20260815-003_gen-media-content-video-provider-happyhorse.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/CLOSE-20260815-004_gen-media-content-video-provider-agnes.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/CLOSE-20260815-005_gen-media-content-video-provider-none.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/CLOSE-20260815-006_gen-media-content-bcs-impls.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/CLOSE-20260815-006_gen-media-content-llm-prompts.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-actions-CHALLENGE-50-impl.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-actions-CHALLENGE-60-exec.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-actions-CHALLENGE-70-val.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-actions-CRITIQUE-80-rev.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-actions-GATEKEEP-50-impl.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-actions-GATEKEEP-60-exec.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-actions-GATEKEEP-70-val.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-actions-REVIEW-80-all.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-bcs-impls-CHALLENGE-50-impl.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-bcs-impls-CHALLENGE-60-exec.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-bcs-impls-CHALLENGE-70-val.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-bcs-impls-CRITIQUE-80-rev.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-bcs-impls-GATEKEEP-50-impl.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-bcs-impls-GATEKEEP-60-exec.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-bcs-impls-GATEKEEP-70-val.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-bcs-impls-REVIEW-80-all.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-image-provider-CHALLENGE-50-impl.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-image-provider-CHALLENGE-60-exec.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-image-provider-CHALLENGE-70-val.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-image-provider-CRITIQUE-80-rev.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-image-provider-GATEKEEP-50-impl.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-image-provider-GATEKEEP-60-exec.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-image-provider-GATEKEEP-70-val.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-image-provider-REVIEW-80-all.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-llm-prompts-CHALLENGE-50-impl.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-llm-prompts-CHALLENGE-60-exec.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-llm-prompts-CHALLENGE-70-val.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-llm-prompts-CRITIQUE-80-rev.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-llm-prompts-GATEKEEP-50-impl.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-llm-prompts-GATEKEEP-60-exec.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-llm-prompts-GATEKEEP-70-val.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-llm-prompts-REVIEW-80-all.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-orchestrator-integration-CHALLENGE-50-impl.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-orchestrator-integration-GATEKEEP-50-impl.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-scaffolding-CRITIQUE-50-impl.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-scaffolding-REV-50-impl.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-video-provider-agnes-CHALLENGE-50-impl.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-video-provider-agnes-CHALLENGE-60-exec.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-video-provider-agnes-CHALLENGE-70-val.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-video-provider-agnes-CRITIQUE-80-rev.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-video-provider-agnes-GATEKEEP-50-impl.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-video-provider-agnes-GATEKEEP-60-exec.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-video-provider-agnes-GATEKEEP-70-val.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-video-provider-agnes-REVIEW-80-all.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-video-provider-happyhorse-CHALLENGE-50-impl.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-video-provider-happyhorse-CHALLENGE-60-exec.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-video-provider-happyhorse-CHALLENGE-70-val.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-video-provider-happyhorse-CRITIQUE-80-rev.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-video-provider-happyhorse-GATEKEEP-50-impl.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-video-provider-happyhorse-GATEKEEP-60-exec.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-video-provider-happyhorse-GATEKEEP-70-val.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-video-provider-happyhorse-REVIEW-80-all.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-video-provider-none-CHALLENGE-50-impl.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-video-provider-none-CHALLENGE-60-exec.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-video-provider-none-CHALLENGE-70-val.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-video-provider-none-CRITIQUE-80-rev.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-video-provider-none-GATEKEEP-50-impl.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-video-provider-none-GATEKEEP-60-exec.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-video-provider-none-GATEKEEP-70-val.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/gen-media-content-video-provider-none-REVIEW-80-all.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/MEM-20260815-001_gen-media-content-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/MEM-20260815-002_gen-media-content-image-provider.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/MEM-20260815-003_gen-media-content-video-provider-happyhorse.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/MEM-20260815-004_gen-media-content-video-provider-agnes.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/MEM-20260815-005_gen-media-content-video-provider-none.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/MEM-20260815-006_gen-media-content-llm-prompts.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/MEM-20260815-007_gen-media-content-bcs-impls.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/REV-20260815-001_gen-media-content-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/REV-20260815-002_gen-media-content-image-provider.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/REV-20260815-003_gen-media-content-video-provider-happyhorse.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/REV-20260815-004_gen-media-content-video-provider-agnes.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/REV-20260815-005_gen-media-content-video-provider-none.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/REV-20260815-006_gen-media-content-llm-prompts.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/REV-20260815-007_gen-media-content-bcs-impls.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/AGB_V2_DESIGN.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/REQUIREMENT_DOC_AUTHORING_GUIDE.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-1p3xktl0/ARTIFACT_CONTRACT-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-1p3xktl0/GATEKEEP_ARTIFACTS-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-1p3xktl0/GATEKEEP_COMPOSITION_SPEC-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-1p3xktl0/GATEKEEP_PACKAGE-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-1p3xktl0/GATEKEEP_REQUIREMENT-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-1p3xktl0/GATEKEEP_RUNTIME_IMPL-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-1p3xktl0/GATEKEEP_STEPS-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-1p3xktl0/output/COMPOSITION_SPEC-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-1p3xktl0/output/COMPOSITION_STANDARD.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-1p3xktl0/output/default.impl.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-1p3xktl0/output/README.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-1p3xktl0/output/RUNTIME_IMPL-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-1p3xktl0/output/workflow.toml` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-1p3xktl0/REQUIREMENT_ANALYSIS-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-1p3xktl0/REVIEW_COMPOSITION_SPEC-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-1p3xktl0/REVIEW_PACKAGE-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-1p3xktl0/REVIEW_REQUIREMENT-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-1p3xktl0/REVIEW_RUNTIME_IMPL-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-1p3xktl0/STEP_SEQUENCE-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-43hev804/ARTIFACT_CONTRACT-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-43hev804/COMPOSITION_SPEC-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-43hev804/GATEKEEP_ARTIFACTS-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-43hev804/GATEKEEP_COMPOSITION_SPEC-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-43hev804/GATEKEEP_PACKAGE-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-43hev804/GATEKEEP_REQUIREMENT-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-43hev804/GATEKEEP_RUNTIME_IMPL-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-43hev804/GATEKEEP_STEPS-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-43hev804/output/COMPOSITION_STANDARD.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-43hev804/output/impls/default/default.impl.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-43hev804/output/README.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-43hev804/output/workflow.toml` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-43hev804/REQUIREMENT_ANALYSIS-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-43hev804/REVIEW_COMPOSITION_SPEC-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-43hev804/REVIEW_PACKAGE-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-43hev804/REVIEW_REQUIREMENT-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-43hev804/REVIEW_RUNTIME_IMPL-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-43hev804/RUNTIME_IMPL-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-43hev804/STEP_SEQUENCE-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-eeqbmreo/ARTIFACT_CONTRACT-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-eeqbmreo/GATEKEEP_ARTIFACTS-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-eeqbmreo/GATEKEEP_COMPOSITION_SPEC-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-eeqbmreo/GATEKEEP_PACKAGE-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-eeqbmreo/GATEKEEP_REQUIREMENT-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-eeqbmreo/GATEKEEP_RUNTIME_IMPL-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-eeqbmreo/GATEKEEP_STEPS-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-eeqbmreo/output/COMPOSITION_SPEC-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-eeqbmreo/output/README.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-eeqbmreo/output/RUNTIME_IMPL-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-eeqbmreo/output/workflow.toml` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-eeqbmreo/REQUIREMENT_ANALYSIS-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-eeqbmreo/REVIEW_COMPOSITION_SPEC-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-eeqbmreo/REVIEW_PACKAGE-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-eeqbmreo/REVIEW_REQUIREMENT-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-eeqbmreo/REVIEW_RUNTIME_IMPL-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-eeqbmreo/STEP_SEQUENCE-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-t0jk63sn/ARTIFACT_CONTRACT-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-t0jk63sn/GATEKEEP_ARTIFACTS-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-t0jk63sn/GATEKEEP_COMPOSITION_SPEC-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-t0jk63sn/GATEKEEP_PACKAGE-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-t0jk63sn/GATEKEEP_REQUIREMENT-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-t0jk63sn/GATEKEEP_RUNTIME_IMPL-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-t0jk63sn/GATEKEEP_STEPS-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-t0jk63sn/output/COMPOSITION_SPEC-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-t0jk63sn/output/README.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-t0jk63sn/output/RUNTIME_IMPL-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-t0jk63sn/output/workflow.toml` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-t0jk63sn/REQUIREMENT_ANALYSIS-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-t0jk63sn/REVIEW_COMPOSITION_SPEC-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-t0jk63sn/REVIEW_PACKAGE-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-t0jk63sn/REVIEW_REQUIREMENT-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-t0jk63sn/REVIEW_RUNTIME_IMPL-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-t0jk63sn/STEP_SEQUENCE-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-ub97gvkz/GATEKEEP_ARTIFACTS-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-ub97gvkz/GATEKEEP_COMPOSITION_SPEC-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-ub97gvkz/GATEKEEP_PACKAGE-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-ub97gvkz/GATEKEEP_REQUIREMENT-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-ub97gvkz/GATEKEEP_RUNTIME_IMPL-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-ub97gvkz/GATEKEEP_STEPS-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-ub97gvkz/output/ARTIFACT_CONTRACT-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-ub97gvkz/output/COMPOSITION_SPEC-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-ub97gvkz/output/COMPOSITION_STANDARD.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-ub97gvkz/output/default.impl.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-ub97gvkz/output/README.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-ub97gvkz/output/RUNTIME_IMPL-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-ub97gvkz/output/workflow.toml` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-ub97gvkz/REQUIREMENT_ANALYSIS-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-ub97gvkz/REVIEW_COMPOSITION_SPEC-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-ub97gvkz/REVIEW_PACKAGE-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-ub97gvkz/REVIEW_REQUIREMENT-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-ub97gvkz/REVIEW_RUNTIME_IMPL-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/runs/AGB-ub97gvkz/STEP_SEQUENCE-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/sop/AGB_SOP.md` | modify | part of repository scan baseline | medium |
| `docs/repo/artifact_generator_builder/templates/REQUIREMENT_DOC_TEMPLATE.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/00_standards/CODEBASE_DOC_SOP.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/00_standards/CODEBASE_DOC_STATUS_RULES.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/01_inventory/codebase_inventory.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-action-result.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-actions-copy-artifact.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-actions-documentation-validation-core.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-actions-finalize-bootstrap.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-actions-init.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-actions-promote-artifact.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-actions-promote-init.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-actions-scan-repo-codebase.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-actions-sdlc-shared-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-actions-step-completion.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-actions-sync-codebase-docs.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-actions-sync-system-docs.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-actions-validate-codebase-docs.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-actions-validate-system-docs.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-approve-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-artifact-keys.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-artifact-paths.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-backend-client.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-backend-execution.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-bootstrap-workflows-default-00-bootstrap-lifecycle-admin-v1-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-bootstrap-workflows-default-00-bootstrap-lifecycle-admin-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-bootstrap-workflows-default-01-governance-foundation-v1-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-bootstrap-workflows-default-01-governance-foundation-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-bootstrap-workflows-default-01-governance-foundation-v1-output-paths.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-bootstrap-workflows-default-02-agent-runner-platform-v1-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-bootstrap-workflows-default-02-agent-runner-platform-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-bootstrap-workflows-default-02-agent-runner-platform-v1-output-paths.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-codebase-v1-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-codebase-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-delivery-scaffold-v1-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-delivery-scaffold-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-delivery-scaffold-v1-install.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-init-doc-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-10-requirement-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-20-planning-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-30-backlog-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-40-task-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-50-implementation-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-60-execution-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-70-validation-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-80-review-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-bundle-governance.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-bundle-loader.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-bundle-taxonomy.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-cleanup-generated-docs.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-cli-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-codebase-docs.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-codebase-init-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-coder-adapters.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-coder-registry.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-config-init.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-config-loader.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-config-section-requirements.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-console-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-constants-legacy-backup-20260717.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-constants.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-daemon-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-daemon.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-doc-paths.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-doc-text.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-documentation-guardrails.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-engine-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-exceptions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-execution-core.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-execution-request.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-execution-result.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-execution-support.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-failure-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-init.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-job-state.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-manual-runtime-deps.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-manual-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-notification-manager.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-notifications.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-operator-console-app.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-operator-console-app1.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-operator-console-config.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-operator-console-init.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-operator-console-models.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-operator-console-services-backend-service.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-operator-console-services-init.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-operator-console-services-runner-service.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-path-catalog.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-path-primitives.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-recovery-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-routing-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-run-agent.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-runner-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-runner-logger.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-runtime-context.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-runtime-utils.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-shared-runtime-deps.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-site-styles.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-state-defaults.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-step-execution-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-step-runner.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-stop-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-submit-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-submitter.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-sync-workflows.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-system-docs.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-task-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-tools-agent-tools.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-transition-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-workflow-bundle-validate-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-workflow-bundle-validator.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-workflow-packages-actions-init.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-workflow-packages-base.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-workflow-packages-extensions-base.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-workflow-packages-hooks.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-workflow-packages-init.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-workflow-packages-loader.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-workflow-packages-registry.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-workflow-path-contracts.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-workflow-router.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-workflow-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-workflow-spec-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/02_modules/agent-runner-v2-workflow-specs.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/03_components/actions-package.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/03_components/codebase-governance.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/03_components/config-and-data.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/03_components/scripts-suite.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/03_components/tests-suite.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/03_components/workflow-families.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/04_changes/SDLC00CB-20260723-e1c86100-reconcile-validation.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/04_changes/SDLC00CB-20260723-e1c86100-reconcile.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260806-071222/codebase_manifest.json` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/00_standards/CODEBASE_DOC_SOP.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/00_standards/CODEBASE_DOC_STATUS_RULES.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/01_inventory/codebase_inventory.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-action-result.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-actions-archive-inputs.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-actions-copy-artifact.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-actions-documentation-validation-core.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-actions-finalize-bootstrap.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-actions-init.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-actions-promote-artifact.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-actions-promote-init.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-actions-scan-repo-codebase.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-actions-sdlc-shared-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-actions-step-completion.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-actions-sync-codebase-docs.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-actions-sync-system-docs.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-actions-validate-codebase-docs.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-actions-validate-system-docs.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-api-key-pool.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-approve-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-artifact-keys.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-artifact-paths.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-backend-client.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-backend-execution.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-00-bootstrap-lifecycle-admin-v1-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-00-bootstrap-lifecycle-admin-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-01-governance-foundation-v1-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-01-governance-foundation-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-01-governance-foundation-v1-output-paths.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-02-agent-runner-platform-v1-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-02-agent-runner-platform-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-02-agent-runner-platform-v1-output-paths.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-agnes-gen-video-v1-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-agnes-gen-video-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-agnes-media-gen-v1-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-agnes-media-gen-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-agnes-media-gen-v1-guardrails.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-codebase-v1-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-codebase-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-delivery-scaffold-v1-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-delivery-scaffold-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-delivery-scaffold-v1-install.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-init-doc-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-10-requirement-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-20-planning-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-30-backlog-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-40-task-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-50-implementation-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-60-execution-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-70-validation-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-80-review-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-workflow-builder-v1-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-workflow-builder-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bundle-governance.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bundle-loader.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-bundle-taxonomy.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-cleanup-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-cleanup-generated-docs.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-cli-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-codebase-docs.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-codebase-init-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-coder-adapters.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-coder-registry.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-concurrent-api.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-config-init.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-config-loader.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-config-section-requirements.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-console-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-constants-legacy-backup-20260717.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-constants.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-daemon-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-daemon-v2.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-daemon.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-doc-paths.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-doc-text.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-documentation-guardrails.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-engine-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-exceptions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-execution-core.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-execution-request.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-execution-result.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-execution-support.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-failure-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-hooks-protocols.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-init.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-job-state.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-list-runs-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-manual-runtime-deps.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-manual-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-notification-manager.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-notifications.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-operator-console-app.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-operator-console-app1.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-operator-console-config.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-operator-console-init.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-operator-console-models.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-operator-console-services-backend-service.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-operator-console-services-init.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-operator-console-services-runner-service.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-path-catalog.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-path-primitives.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-recovery-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-reset-step-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-routing-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-run-agent.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-runner-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-runner-logger.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-runtime-context.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-runtime-hooks.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-runtime-utils.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-shared-runtime-deps.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-show-run-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-single-instance.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-site-styles.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-state-defaults.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-status-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-step-execution-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-step-runner.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-stop-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-submit-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-submitter.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-sync-workflows.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-system-docs.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-task-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-tools-agent-tools.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-transition-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-v2-backend-client.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-v2-init.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-v2-queue.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-v2-sync.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-bundle-validate-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-bundle-validator.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-packages-actions-init.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-packages-base.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-packages-extensions-base.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-packages-hooks.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-packages-init.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-packages-loader.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-packages-registry.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-path-contracts.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-router.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-spec-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-specs.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/03_components/actions-package.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/03_components/codebase-governance.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/03_components/config-and-data.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/03_components/scripts-suite.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/03_components/tests-suite.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/03_components/workflow-families.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/04_changes/SDLC00CB-20260723-e1c86100-reconcile-validation.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/04_changes/SDLC00CB-20260723-e1c86100-reconcile.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/04_changes/SDLC00CB-bgmxg5vi-reconcile-validation.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/04_changes/SDLC00CB-bgmxg5vi-reconcile.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/codebase_manifest.json` | modify | part of repository scan baseline | medium |
| `docs/repo/refactor/AUDIT_TRAIL_20260729.md` | modify | part of repository scan baseline | medium |
| `docs/repo/refactor/DESIGN_circular_import_resolution.md` | modify | part of repository scan baseline | medium |
| `docs/repo/refactor/DESIGN_job_state_extraction.md` | modify | part of repository scan baseline | medium |
| `docs/repo/refactor/DESIGN_operator_console_extraction.md` | modify | part of repository scan baseline | medium |
| `docs/repo/refactor/DESIGN_step_runner_extraction.md` | modify | part of repository scan baseline | medium |
| `docs/repo/refactor/REFACTORING_SUMMARY.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/current/BUILDER_REQUIREMENTS.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/current/COMPOSITION_SYSTEM_STANDARD.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/current/sop/WORKFLOW_BUILDER_SOP.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/current/SPEC_AUTHORING_GUIDE.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/current/templates/COMPOSITION_SYSTEM_SPEC_TEMPLATE.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/current/templates/WORKFLOW_SPEC_TEMPLATE.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/PHASE1_V1_AS_COMPOSITION_SYSTEM.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/PHASE2_V2_DESIGN.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/AMB-ai99miop/COMPONENT_SCHEMA-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/AMB-ai99miop/COMPOSITION_FORMAT-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/AMB-ai99miop/COMPOSITION_STANDARD-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/AMB-ai99miop/GATEKEEP_COMPONENT_SCHEMA-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/AMB-ai99miop/GATEKEEP_COMPOSITION_FORMAT-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/AMB-ai99miop/GATEKEEP_COMPOSITION_STANDARD-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/AMB-ai99miop/GATEKEEP_OPERATIONAL_WORKFLOW-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/AMB-ai99miop/GATEKEEP_OUTPUT_FORMAT-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/AMB-ai99miop/GATEKEEP_PACKAGE-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/AMB-ai99miop/META_COMPOSITION_SPEC-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/AMB-ai99miop/OPERATIONAL_WORKFLOW-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/AMB-ai99miop/output/prompts_index.json` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/AMB-ai99miop/output/README.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/AMB-ai99miop/output/Standards/COMPOSITION_STANDARD.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/AMB-ai99miop/output/workflow.toml` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/AMB-ai99miop/OUTPUT_FORMAT-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/AMB-ai99miop/REVIEW-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/AMB-ai99miop/REVIEW_TEST_CRITERIA-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/AMB-ai99miop/TEST_CRITERIA-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/AMB-ai99miop/VALIDATION-20260809-001_deterministic.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/WBUILD3-scho512w/COMPONENT_SCHEMA-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/WBUILD3-scho512w/COMPOSITION_FORMAT-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/WBUILD3-scho512w/COMPOSITION_STANDARD-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/WBUILD3-scho512w/GATEKEEP_COMPONENT_SCHEMA-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/WBUILD3-scho512w/GATEKEEP_COMPOSITION_FORMAT-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/WBUILD3-scho512w/GATEKEEP_COMPOSITION_STANDARD-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/WBUILD3-scho512w/GATEKEEP_OPERATIONAL_WORKFLOW-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/WBUILD3-scho512w/GATEKEEP_OUTPUT_FORMAT-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/WBUILD3-scho512w/GATEKEEP_PACKAGE-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/WBUILD3-scho512w/META_COMPOSITION_SPEC-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/WBUILD3-scho512w/OPERATIONAL_WORKFLOW-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/WBUILD3-scho512w/output/prompts_index.json` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/WBUILD3-scho512w/output/README.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/WBUILD3-scho512w/output/Standards/COMPOSITION_STANDARD.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/WBUILD3-scho512w/output/workflow.toml` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/WBUILD3-scho512w/OUTPUT_FORMAT-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/WBUILD3-scho512w/REVIEW-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/WBUILD3-scho512w/REVIEW_TEST_CRITERIA-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/WBUILD3-scho512w/TEST_CRITERIA-001.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/runs/WBUILD3-scho512w/VALIDATION-20260809-001_deterministic.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/specs/Completed/agnes_media_gen_v1.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/specs/product_master_gen_v2.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/specs/prompt_quality_audit_v1.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/specs/security_audit_v1.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/specs/tdd_audit_v1.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/specs/update_codebase_docs_v1.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/specs/video_campaign_manuscript_v1.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/specs/video_campaign_manuscript_v2.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/specs/workflow_builder_v3.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/specs/workflow_builder_v4.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/standards/COMPOSITION_SYSTEM_STANDARD.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/standards/META_WORKFLOW_BUILDER_ARCHITECTURE.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/standards/WORKFLOW_BUILDER_COMPOSITION_SPEC.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/V4_BOOTSTRAP_SUMMARY.md` | modify | part of repository scan baseline | medium |
| `docs/repo/workflow_builder/WORKFLOW_BUILDER_V2_PLAN.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/current/BASE_COMPOSITION_STANDARD_v1.0.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/current/BUNDLE_TAXONOMY.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/current/DOCUMENT_AUTHORITY.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/current/GOVERNANCE_LIFECYCLE.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/current/governance_set_manifest.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/current/LAYER_MODEL.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/current/METADATA_STANDARD.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/current/README.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-0864b1f2/BUNDLE_TAXONOMY.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-0864b1f2/DOCUMENT_AUTHORITY.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-0864b1f2/GOVERNANCE_LIFECYCLE.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-0864b1f2/governance_set_manifest.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-0864b1f2/LAYER_MODEL.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-0864b1f2/METADATA_STANDARD.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-0864b1f2/README.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-4e51c88b/BUNDLE_TAXONOMY.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-4e51c88b/DOCUMENT_AUTHORITY.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-4e51c88b/GOVERNANCE_LIFECYCLE.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-4e51c88b/governance_set_manifest.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-4e51c88b/LAYER_MODEL.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-4e51c88b/METADATA_STANDARD.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-4e51c88b/README.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-61ae0105/BUNDLE_TAXONOMY.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-61ae0105/DOCUMENT_AUTHORITY.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-61ae0105/GOVERNANCE_LIFECYCLE.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-61ae0105/governance_set_manifest.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-61ae0105/LAYER_MODEL.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-61ae0105/METADATA_STANDARD.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-61ae0105/README.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-96e730ab/BUNDLE_TAXONOMY.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-96e730ab/DOCUMENT_AUTHORITY.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-96e730ab/GOVERNANCE_LIFECYCLE.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-96e730ab/governance_set_manifest.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-96e730ab/LAYER_MODEL.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-96e730ab/METADATA_STANDARD.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-96e730ab/README.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-c5e882c3/BUNDLE_TAXONOMY.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-c5e882c3/DOCUMENT_AUTHORITY.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-c5e882c3/GOVERNANCE_LIFECYCLE.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-c5e882c3/governance_set_manifest.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-c5e882c3/LAYER_MODEL.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-c5e882c3/METADATA_STANDARD.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-c5e882c3/README.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-f15f153c/BUNDLE_TAXONOMY.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-f15f153c/DOCUMENT_AUTHORITY.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-f15f153c/GOVERNANCE_LIFECYCLE.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-f15f153c/governance_set_manifest.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-f15f153c/LAYER_MODEL.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-f15f153c/METADATA_STANDARD.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/history/01GF-20260719-f15f153c/README.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/01GF-20260719-0864b1f2-governance-context-inventory.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/01GF-20260719-0864b1f2-governance-foundation-audit.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/01GF-20260719-0864b1f2-governance-foundation-audit.meta.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/01GF-20260719-0864b1f2-governance-foundation-review.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/01GF-20260719-0864b1f2-governance-foundation-review.meta.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/01GF-20260719-0864b1f2-governance-foundation-validation.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/BUNDLE_TAXONOMY.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/DOCUMENT_AUTHORITY.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/GOVERNANCE_LIFECYCLE.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/LAYER_MODEL.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/METADATA_STANDARD.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/README.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/01GF-20260719-4e51c88b-governance-context-inventory.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/01GF-20260719-4e51c88b-governance-foundation-audit.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/01GF-20260719-4e51c88b-governance-foundation-audit.meta.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/01GF-20260719-4e51c88b-governance-foundation-review.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/01GF-20260719-4e51c88b-governance-foundation-review.meta.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/01GF-20260719-4e51c88b-governance-foundation-validation.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/BUNDLE_TAXONOMY.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/DOCUMENT_AUTHORITY.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/GOVERNANCE_LIFECYCLE.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/LAYER_MODEL.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/METADATA_STANDARD.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/README.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/01GF-20260719-61ae0105-governance-context-inventory.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/01GF-20260719-61ae0105-governance-foundation-audit.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/01GF-20260719-61ae0105-governance-foundation-audit.meta.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/01GF-20260719-61ae0105-governance-foundation-review.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/01GF-20260719-61ae0105-governance-foundation-review.meta.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/01GF-20260719-61ae0105-governance-foundation-validation.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/BUNDLE_TAXONOMY.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/DOCUMENT_AUTHORITY.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/GOVERNANCE_LIFECYCLE.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/LAYER_MODEL.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/METADATA_STANDARD.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/README.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/01GF-20260719-96e730ab-governance-context-inventory.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/01GF-20260719-96e730ab-governance-foundation-audit.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/01GF-20260719-96e730ab-governance-foundation-audit.meta.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/01GF-20260719-96e730ab-governance-foundation-review.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/01GF-20260719-96e730ab-governance-foundation-review.meta.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/01GF-20260719-96e730ab-governance-foundation-validation.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/BUNDLE_TAXONOMY.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/DOCUMENT_AUTHORITY.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/GOVERNANCE_LIFECYCLE.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/LAYER_MODEL.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/METADATA_STANDARD.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/README.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/01GF-20260719-c5e882c3-governance-context-inventory.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/01GF-20260719-c5e882c3-governance-foundation-audit.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/01GF-20260719-c5e882c3-governance-foundation-audit.meta.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/01GF-20260719-c5e882c3-governance-foundation-review.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/01GF-20260719-c5e882c3-governance-foundation-review.meta.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/01GF-20260719-c5e882c3-governance-foundation-validation.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/BUNDLE_TAXONOMY.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/DOCUMENT_AUTHORITY.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/GOVERNANCE_LIFECYCLE.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/LAYER_MODEL.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/METADATA_STANDARD.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/README.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/README.meta.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/01GF-20260719-f15f153c-governance-context-inventory.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/01GF-20260719-f15f153c-governance-foundation-audit.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/01GF-20260719-f15f153c-governance-foundation-audit.meta.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/01GF-20260719-f15f153c-governance-foundation-review.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/01GF-20260719-f15f153c-governance-foundation-review.meta.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/01GF-20260719-f15f153c-governance-foundation-validation.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/BUNDLE_TAXONOMY.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/DOCUMENT_AUTHORITY.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/GOVERNANCE_LIFECYCLE.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/LAYER_MODEL.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/METADATA_STANDARD.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/README.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/current/BUNDLE_AUTHORING_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/current/METADATA_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/current/platform_set_manifest.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/current/README.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/current/RUNTIME_MODEL.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/current/SHARED_SERVICES.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/current/VALIDATION_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/history/02AR-20260721-2eaba4b3/BUNDLE_AUTHORING_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/history/02AR-20260721-2eaba4b3/METADATA_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/history/02AR-20260721-2eaba4b3/platform_set_manifest.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/history/02AR-20260721-2eaba4b3/README.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/history/02AR-20260721-2eaba4b3/RUNTIME_MODEL.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/history/02AR-20260721-2eaba4b3/SHARED_SERVICES.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/history/02AR-20260721-2eaba4b3/VALIDATION_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/history/02PC-20260721-b092c705/BUNDLE_AUTHORING_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/history/02PC-20260721-b092c705/METADATA_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/history/02PC-20260721-b092c705/platform_set_manifest.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/history/02PC-20260721-b092c705/README.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/history/02PC-20260721-b092c705/RUNTIME_MODEL.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/history/02PC-20260721-b092c705/SHARED_SERVICES.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/history/02PC-20260721-b092c705/VALIDATION_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/history/02PC-GEN-20260721-009/BUNDLE_AUTHORING_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/history/02PC-GEN-20260721-009/METADATA_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/history/02PC-GEN-20260721-009/platform_set_manifest.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/history/02PC-GEN-20260721-009/README.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/history/02PC-GEN-20260721-009/RUNTIME_MODEL.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/history/02PC-GEN-20260721-009/SHARED_SERVICES.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/history/02PC-GEN-20260721-009/VALIDATION_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/02PC-20260721-b092c705-platform-context-inventory.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/02PC-20260721-b092c705-platform-core-audit.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/02PC-20260721-b092c705-platform-core-audit.meta.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/02PC-20260721-b092c705-platform-core-review.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/02PC-20260721-b092c705-platform-core-review.meta.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/02PC-20260721-b092c705-platform-core-validation.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/BUNDLE_AUTHORING_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/METADATA_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/README.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/README.meta.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/RUNTIME_MODEL.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/SHARED_SERVICES.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/VALIDATION_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/02PC-GEN-20260721-009-platform-context-inventory.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/02PC-GEN-20260721-009-platform-core-audit.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/02PC-GEN-20260721-009-platform-core-audit.meta.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/02PC-GEN-20260721-009-platform-core-review.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/02PC-GEN-20260721-009-platform-core-review.meta.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/02PC-GEN-20260721-009-platform-core-validation.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/BUNDLE_AUTHORING_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/METADATA_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/README.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/RUNTIME_MODEL.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/SHARED_SERVICES.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/VALIDATION_CONTRACT.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/01_DRAFT_INIT_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/02_INIT_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/03_REQ_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/04_PLAN_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/05_BACKLOG_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/06_TASK_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/07_IMPL_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/08_VALID_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/09_REV_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/10_MEM_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/11_CLOSE_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/template_registry.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/WORKFLOW_SOP_v1.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/current/02_agents/AGENT-executor.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/current/02_agents/AGENT-implementation-planner.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/current/02_agents/AGENT-memory-manager.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/current/02_agents/AGENT-planner.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/current/02_agents/AGENT-reviewer.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/current/02_agents/AGENT-task-decomposer.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/current/02_agents/AGENTS.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/current/02_agents/DELIVERY_STATUS_RULES_v1.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/current/sdlc_scaffold_manifest.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/01_DRAFT_INIT_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/02_INIT_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/03_REQ_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/04_PLAN_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/05_BACKLOG_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/06_TASK_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/07_IMPL_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/08_VALID_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/09_REV_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/10_MEM_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/11_CLOSE_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/template_registry.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/WORKFLOW_SOP_v1.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-executor.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-implementation-planner.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-memory-manager.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-planner.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-reviewer.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-task-decomposer.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/02_agents/AGENTS.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/02_agents/DELIVERY_STATUS_RULES_v1.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/sdlc_scaffold_manifest.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/01_DRAFT_INIT_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/02_INIT_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/03_REQ_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/04_PLAN_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/05_BACKLOG_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/06_TASK_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/07_IMPL_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/08_VALID_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/09_REV_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/10_MEM_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/11_CLOSE_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/template_registry.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/WORKFLOW_SOP_v1.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-executor.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-implementation-planner.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-memory-manager.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-planner.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-reviewer.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-task-decomposer.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/02_agents/AGENTS.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/02_agents/DELIVERY_STATUS_RULES_v1.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/SDLC00SCF-20260722-3a011a52-sdlc-scaffold-review.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/01_DRAFT_INIT_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/02_INIT_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/03_REQ_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/04_PLAN_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/05_BACKLOG_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/06_TASK_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/07_IMPL_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/08_VALID_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/09_REV_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/10_MEM_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/11_CLOSE_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/template_registry.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/template_registry.meta.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/WORKFLOW_SOP_v1.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/AGENT-executor.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/AGENT-implementation-planner.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/AGENT-memory-manager.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/AGENT-planner.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/AGENT-reviewer.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/AGENT-task-decomposer.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/AGENTS.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/AGENTS.meta.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/DELIVERY_STATUS_RULES_v1.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/SDLC00SCF-20260722-914943f4-sdlc-scaffold-review.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/SDLC00SCF-20260722-914943f4-sdlc-scaffold-review.meta.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/01_DRAFT_INIT_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/02_INIT_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/03_REQ_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/04_PLAN_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/05_BACKLOG_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/06_TASK_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/07_IMPL_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/08_VALID_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/09_REV_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/10_MEM_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/11_CLOSE_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/template_registry.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/template_registry.meta.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/WORKFLOW_SOP_v1.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/AGENT-executor.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/AGENT-implementation-planner.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/AGENT-memory-manager.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/AGENT-planner.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/AGENT-reviewer.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/AGENT-task-decomposer.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/AGENTS.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/AGENTS.meta.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/DELIVERY_STATUS_RULES_v1.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/SDLC00SCF-20260722-cc2b347d-sdlc-scaffold-review.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/SDLC00SCF-20260722-cc2b347d-sdlc-scaffold-review.meta.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/01_DRAFT_INIT_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/02_INIT_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/03_REQ_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/04_PLAN_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/05_BACKLOG_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/06_TASK_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/07_IMPL_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/08_VALID_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/09_REV_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/10_MEM_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/11_CLOSE_template.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/template_registry.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/template_registry.meta.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/WORKFLOW_SOP_v1.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/AGENT-executor.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/AGENT-implementation-planner.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/AGENT-memory-manager.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/AGENT-planner.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/AGENT-reviewer.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/AGENT-task-decomposer.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/AGENTS.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/AGENTS.meta.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/DELIVERY_STATUS_RULES_v1.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/platform/agent_workflow_builder/current/standards/COMPOSITION_SYSTEM_STANDARD.md` | modify | part of repository scan baseline | medium |
| `docs/TEST_CASE_PLANNING_ROADMAP.md` | modify | part of repository scan baseline | medium |
| `pyproject.toml` | modify | part of repository scan baseline | medium |
| `README.md` | modify | part of repository scan baseline | medium |
| `run-bootstrap-publish.bat` | modify | part of repository scan baseline | medium |
| `run-bootstrap-publish.sh` | modify | part of repository scan baseline | medium |
| `run-cleanup-workflow.bat` | modify | part of repository scan baseline | medium |
| `run-cleanup-workflow.sh` | modify | part of repository scan baseline | medium |
| `run-cleanup.bat` | modify | part of repository scan baseline | medium |
| `run-daemon.bat` | modify | part of repository scan baseline | medium |
| `run-daemon.sh` | modify | part of repository scan baseline | medium |
| `run-init.bat` | modify | part of repository scan baseline | medium |
| `run-init.sh` | modify | part of repository scan baseline | medium |
| `scripts/run-00_bootstrap_lifecycle_admin_v1.bat` | modify | part of repository scan baseline | medium |
| `scripts/run-00_bootstrap_lifecycle_admin_v1.sh` | modify | part of repository scan baseline | medium |
| `scripts/run-01_governance_foundation_v1.bat` | modify | part of repository scan baseline | medium |
| `scripts/run-01_governance_foundation_v1.sh` | modify | part of repository scan baseline | medium |
| `scripts/run-02_agent_runner_platform_v1.bat` | modify | part of repository scan baseline | medium |
| `scripts/run-02_agent_runner_platform_v1.sh` | modify | part of repository scan baseline | medium |
| `scripts/run-approve-step.bat` | modify | part of repository scan baseline | medium |
| `scripts/run-approve-step.sh` | modify | part of repository scan baseline | medium |
| `scripts/run-console.bat` | modify | part of repository scan baseline | medium |
| `scripts/run-console.sh` | modify | part of repository scan baseline | medium |
| `scripts/run-reset-step.bat` | modify | part of repository scan baseline | medium |
| `scripts/run-reset-step.sh` | modify | part of repository scan baseline | medium |
| `scripts/run-sdlc_00_codebase_v1.bat` | modify | part of repository scan baseline | medium |
| `scripts/run-sdlc_00_codebase_v1.sh` | modify | part of repository scan baseline | medium |
| `scripts/run-sdlc_00_delivery_scaffold_v1.bat` | modify | part of repository scan baseline | medium |
| `scripts/run-sdlc_00_delivery_scaffold_v1.sh` | modify | part of repository scan baseline | medium |
| `scripts/run-sdlc_00_init_doc_v1.bat` | modify | part of repository scan baseline | medium |
| `scripts/run-sdlc_00_init_doc_v1.sh` | modify | part of repository scan baseline | medium |
| `scripts/run-sdlc_10_requirement_v1.bat` | modify | part of repository scan baseline | medium |
| `scripts/run-sdlc_10_requirement_v1.sh` | modify | part of repository scan baseline | medium |
| `scripts/run-sdlc_20_planning_v1.bat` | modify | part of repository scan baseline | medium |
| `scripts/run-sdlc_20_planning_v1.sh` | modify | part of repository scan baseline | medium |
| `scripts/run-sdlc_30_backlog_v1.bat` | modify | part of repository scan baseline | medium |
| `scripts/run-sdlc_30_backlog_v1.sh` | modify | part of repository scan baseline | medium |
| `scripts/run-sdlc_40_task_v1.bat` | modify | part of repository scan baseline | medium |
| `scripts/run-sdlc_40_task_v1.sh` | modify | part of repository scan baseline | medium |
| `scripts/run-sdlc_50_implementation_v1.bat` | modify | part of repository scan baseline | medium |
| `scripts/run-sdlc_50_implementation_v1.sh` | modify | part of repository scan baseline | medium |
| `scripts/run-sdlc_60_execution_v1.bat` | modify | part of repository scan baseline | medium |
| `scripts/run-sdlc_60_execution_v1.sh` | modify | part of repository scan baseline | medium |
| `scripts/run-sdlc_70_validation_v1.bat` | modify | part of repository scan baseline | medium |
| `scripts/run-sdlc_70_validation_v1.sh` | modify | part of repository scan baseline | medium |
| `scripts/run-sdlc_80_review_v1.bat` | modify | part of repository scan baseline | medium |
| `scripts/run-sdlc_80_review_v1.sh` | modify | part of repository scan baseline | medium |
| `scripts/submit-00_bootstrap_lifecycle_admin_v1.bat` | modify | part of repository scan baseline | medium |
| `scripts/submit-00_bootstrap_lifecycle_admin_v1.sh` | modify | part of repository scan baseline | medium |
| `scripts/submit-01_governance_foundation_v1.bat` | modify | part of repository scan baseline | medium |
| `scripts/submit-01_governance_foundation_v1.sh` | modify | part of repository scan baseline | medium |
| `scripts/submit-02_agent_runner_platform_v1.bat` | modify | part of repository scan baseline | medium |
| `scripts/submit-02_agent_runner_platform_v1.sh` | modify | part of repository scan baseline | medium |
| `scripts/submit-sdlc_00_codebase_v1.bat` | modify | part of repository scan baseline | medium |
| `scripts/submit-sdlc_00_codebase_v1.sh` | modify | part of repository scan baseline | medium |
| `scripts/submit-sdlc_00_init_doc_v1.bat` | modify | part of repository scan baseline | medium |
| `scripts/submit-sdlc_00_init_doc_v1.sh` | modify | part of repository scan baseline | medium |
| `scripts/submit-sdlc_10_requirement_v1.bat` | modify | part of repository scan baseline | medium |
| `scripts/submit-sdlc_10_requirement_v1.sh` | modify | part of repository scan baseline | medium |
| `scripts/submit-sdlc_20_planning_v1.bat` | modify | part of repository scan baseline | medium |
| `scripts/submit-sdlc_20_planning_v1.sh` | modify | part of repository scan baseline | medium |
| `scripts/submit-sdlc_30_backlog_v1.bat` | modify | part of repository scan baseline | medium |
| `scripts/submit-sdlc_30_backlog_v1.sh` | modify | part of repository scan baseline | medium |
| `scripts/submit-sdlc_40_task_v1.bat` | modify | part of repository scan baseline | medium |
| `scripts/submit-sdlc_40_task_v1.sh` | modify | part of repository scan baseline | medium |
| `scripts/submit-sdlc_50_implementation_v1.bat` | modify | part of repository scan baseline | medium |
| `scripts/submit-sdlc_50_implementation_v1.sh` | modify | part of repository scan baseline | medium |
| `scripts/submit-sdlc_50_implementation_v1_temp.bat` | modify | part of repository scan baseline | medium |
| `scripts/submit-sdlc_60_execution_v1.bat` | modify | part of repository scan baseline | medium |
| `scripts/submit-sdlc_60_execution_v1.sh` | modify | part of repository scan baseline | medium |
| `scripts/submit-sdlc_70_validation_v1.bat` | modify | part of repository scan baseline | medium |
| `scripts/submit-sdlc_70_validation_v1.sh` | modify | part of repository scan baseline | medium |
| `scripts/submit-sdlc_80_review_v1.bat` | modify | part of repository scan baseline | medium |
| `scripts/submit-sdlc_80_review_v1.sh` | modify | part of repository scan baseline | medium |
| `skills/opencode_runner/SKILL.md` | modify | part of repository scan baseline | medium |
| `sync-workflows-to-backend.bat` | modify | part of repository scan baseline | medium |
| `sync-workflows-to-backend.sh` | modify | part of repository scan baseline | medium |
| `tests/conftest.py` | modify | part of repository scan baseline | medium |
| `tests/integration/__init__.py` | modify | part of repository scan baseline | medium |
| `tests/integration/check_backend_runs.py` | modify | part of repository scan baseline | medium |
| `tests/integration/check_workflow_impls.py` | modify | part of repository scan baseline | medium |
| `tests/integration/README.md` | modify | part of repository scan baseline | medium |
| `tests/integration/submit_sdlc_50_job.py` | modify | part of repository scan baseline | medium |
| `tests/integration/test_architecture_site.py` | modify | part of repository scan baseline | medium |
| `tests/integration/test_backend_claim_response.py` | modify | part of repository scan baseline | medium |
| `tests/integration/test_backend_worker_mode.py` | modify | part of repository scan baseline | medium |
| `tests/integration/test_claim_existing_job.py` | modify | part of repository scan baseline | medium |
| `tests/integration/test_cli_backend_e2e.py` | modify | part of repository scan baseline | medium |
| `tests/integration/test_daemon_claim.py` | modify | part of repository scan baseline | medium |
| `tests/integration/test_notification_e2e.py` | modify | part of repository scan baseline | medium |
| `tests/integration/test_notification_integration.py` | modify | part of repository scan baseline | medium |
| `tests/integration/test_notifications.py` | modify | part of repository scan baseline | medium |
| `tests/integration/test_pushover.py` | modify | part of repository scan baseline | medium |
| `tests/integration/test_ukbe_runner_wrapper.py` | modify | part of repository scan baseline | medium |
| `tests/run_workflow_unit_tests.py` | modify | part of repository scan baseline | medium |
| `tests/unit/__init__.py` | modify | part of repository scan baseline | medium |
| `tests/unit/README.md` | modify | part of repository scan baseline | medium |
| `tests/unit/test_agb_assemble_package.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_agent_tools.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_api_key_pool.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_backend_client.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_bundle_loader.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_codebase_docs.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_codebase_init_commands.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_coder_adapters_opencode.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_coder_adapters_sidecar_grace.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_coder_registry.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_concurrent_api.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_config_loader.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_constants_registry.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_context_extensions.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_daemon_cli_construction.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_daemon_v2_backend_state.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_daemon_v2_child_outcome_action.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_daemon_v2_startup_validation.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_documentation_governance.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_documentation_guardrails_cleanup.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_dynamic_import_dataclass.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_execution_core.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_failure_runtime.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_generated_doc_frontmatter_injection.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_impl_name_propagation.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_impl_overrides.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_job_state_date_prefix.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_job_state_review_completion.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_job_state_step_dirs.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_job_state_usage_summary.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_list_runs_commands.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_machine_contracts.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_manual_runtime.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_model_config_roles.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_notification_manager.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_plugin_workflow_support.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_promote_artifact.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_prompt_selection_real.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_prompt_slot_resolution.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_recovery_runtime.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_reset_step_commands.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_routing_runtime.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_run_agent_hook_surface.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_run_agent_legacy_cli.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_run_agent_status.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_runtime_context_paths.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_runtime_hooks.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_runtime_utils.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_sdlc_shared_actions.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_show_run_commands.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_state_defaults.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_step_completion.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_step_runner_write_contract.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_submit_commands.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_sync_workflows.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_task_runtime.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_telegram_notifications.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_three_state_waiting.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_tool_instruction_block.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_transient_error_classification.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_transition_recovery_runtime.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_transition_runtime.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_v2_backend_client.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_v2_queue.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_v2_sync.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_workflow_bundle_validator.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_workflow_package_validator.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_workflow_packages.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_workflow_registry.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_workflow_router_notifications.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_workflow_specs.py` | modify | part of repository scan baseline | medium |
| `tests/unit/workflows/00_bootstrap_lifecycle_admin_v1/test_actions.py` | modify | part of repository scan baseline | medium |
| `tests/unit/workflows/02_agent_runner_platform_v1/__init__.py` | modify | part of repository scan baseline | medium |
| `tests/unit/workflows/02_agent_runner_platform_v1/test_platform_core_actions.py` | modify | part of repository scan baseline | medium |
| `tests/unit/workflows/__init__.py` | modify | part of repository scan baseline | medium |
| `tests/unit/workflows/text_summarizer_ayz/test_context_extensions.py` | modify | part of repository scan baseline | medium |
| `workflows/00_bootstrap_lifecycle_admin_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/00_bootstrap_lifecycle_admin_v1/README.md` | modify | part of repository scan baseline | medium |
| `workflows/00_bootstrap_lifecycle_admin_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/01_governance_foundation_v1/bundle_governance.toml` | modify | part of repository scan baseline | medium |
| `workflows/01_governance_foundation_v1/bundle_governance/action_policy.md` | modify | part of repository scan baseline | medium |
| `workflows/01_governance_foundation_v1/bundle_governance/core_governance.md` | modify | part of repository scan baseline | medium |
| `workflows/01_governance_foundation_v1/bundle_governance/generated/AGENTS.md` | modify | part of repository scan baseline | medium |
| `workflows/01_governance_foundation_v1/bundle_governance/generated/CLAUDE.md` | modify | part of repository scan baseline | medium |
| `workflows/01_governance_foundation_v1/bundle_governance/generated/QWEN.md` | modify | part of repository scan baseline | medium |
| `workflows/01_governance_foundation_v1/bundle_governance/prompt_contract.json` | modify | part of repository scan baseline | medium |
| `workflows/01_governance_foundation_v1/bundle_governance/prompt_layout.md` | modify | part of repository scan baseline | medium |
| `workflows/01_governance_foundation_v1/bundle_governance/prompt_sop.md` | modify | part of repository scan baseline | medium |
| `workflows/01_governance_foundation_v1/bundle_governance/review_audit_contract.md` | modify | part of repository scan baseline | medium |
| `workflows/01_governance_foundation_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/01_governance_foundation_v1/README.md` | modify | part of repository scan baseline | medium |
| `workflows/01_governance_foundation_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/02_agent_runner_platform_v1/bundle_governance.toml` | modify | part of repository scan baseline | medium |
| `workflows/02_agent_runner_platform_v1/bundle_governance/action_policy.md` | modify | part of repository scan baseline | medium |
| `workflows/02_agent_runner_platform_v1/bundle_governance/core_governance.md` | modify | part of repository scan baseline | medium |
| `workflows/02_agent_runner_platform_v1/bundle_governance/generated/AGENTS.md` | modify | part of repository scan baseline | medium |
| `workflows/02_agent_runner_platform_v1/bundle_governance/generated/CLAUDE.md` | modify | part of repository scan baseline | medium |
| `workflows/02_agent_runner_platform_v1/bundle_governance/generated/QWEN.md` | modify | part of repository scan baseline | medium |
| `workflows/02_agent_runner_platform_v1/bundle_governance/prompt_contract.json` | modify | part of repository scan baseline | medium |
| `workflows/02_agent_runner_platform_v1/bundle_governance/prompt_layout.md` | modify | part of repository scan baseline | medium |
| `workflows/02_agent_runner_platform_v1/bundle_governance/prompt_sop.md` | modify | part of repository scan baseline | medium |
| `workflows/02_agent_runner_platform_v1/bundle_governance/review_audit_contract.md` | modify | part of repository scan baseline | medium |
| `workflows/02_agent_runner_platform_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/02_agent_runner_platform_v1/README.md` | modify | part of repository scan baseline | medium |
| `workflows/02_agent_runner_platform_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/_registry/coder_connections.json` | modify | part of repository scan baseline | medium |
| `workflows/_registry/coder_roles.json` | modify | part of repository scan baseline | medium |
| `workflows/_registry/coder_roles_opencode.json` | modify | part of repository scan baseline | medium |
| `workflows/_registry/coder_roles_qwen.json` | modify | part of repository scan baseline | medium |
| `workflows/_registry/role_policies.json` | modify | part of repository scan baseline | medium |
| `workflows/agentic_workflow_builder/impls/detailed/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/agentic_workflow_builder/impls/minimal/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/agentic_workflow_builder/README.md` | modify | part of repository scan baseline | medium |
| `workflows/agentic_workflow_builder/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/agnes_gen_video_v1/impls/agnes_v2/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/agnes_gen_video_v1/impls/happyhorse_v1_1/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/agnes_gen_video_v1/README.md` | modify | part of repository scan baseline | medium |
| `workflows/agnes_gen_video_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/agnes_media_gen_v1/impls/agnes_media_v1/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/agnes_media_gen_v1/README.md` | modify | part of repository scan baseline | medium |
| `workflows/agnes_media_gen_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/artifact_generator_builder/impls/builder/bootstrap/README.md` | modify | part of repository scan baseline | medium |
| `workflows/artifact_generator_builder/impls/builder/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/artifact_generator_builder/impls/builder/INPUT_ARTIFACTS.md` | modify | part of repository scan baseline | medium |
| `workflows/artifact_generator_builder/impls/builder/OUTPUT_ARTIFACTS.md` | modify | part of repository scan baseline | medium |
| `workflows/artifact_generator_builder/impls/builder/SPECIALIZED_STEPS.md` | modify | part of repository scan baseline | medium |
| `workflows/artifact_generator_builder/impls/generator/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/artifact_generator_builder/impls/generator/INPUT_ARTIFACTS.md` | modify | part of repository scan baseline | medium |
| `workflows/artifact_generator_builder/impls/generator/OUTPUT_ARTIFACTS.md` | modify | part of repository scan baseline | medium |
| `workflows/artifact_generator_builder/PLUGIN_ARCHITECTURE.md` | modify | part of repository scan baseline | medium |
| `workflows/artifact_generator_builder/README.md` | modify | part of repository scan baseline | medium |
| `workflows/artifact_generator_builder/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/codebase_intelligence/impls/executive_summary/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/codebase_intelligence/impls/security_focused/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/codebase_intelligence/impls/technical_deep_dive/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/codebase_intelligence/README.md` | modify | part of repository scan baseline | medium |
| `workflows/codebase_intelligence/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/DEVELOPER_GUIDE.md` | modify | part of repository scan baseline | medium |
| `workflows/gen_media_content_v1/impls/agnes/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/gen_media_content_v1/impls/llm/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/gen_media_content_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/gen_media_content_v1/README.md` | modify | part of repository scan baseline | medium |
| `workflows/gen_media_content_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_00_codebase_scaffold_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_00_codebase_scaffold_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_00_init_doc_v1/DRAFT_INIT_AUTHORING_GUIDE.md` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_00_init_doc_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_00_init_doc_v1/README.md` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_00_init_doc_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_00_requirement_planning_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_00_requirement_planning_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_01_impl_exec_review_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_01_impl_exec_review_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_10_requirement_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_10_requirement_v1/README.md` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_10_requirement_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_20_planning_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_20_planning_v1/README.md` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_20_planning_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_30_backlog_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_30_backlog_v1/README.md` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_30_backlog_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_40_task_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_40_task_v1/README.md` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_40_task_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_50_implementation_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_50_implementation_v1/README.md` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_50_implementation_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_60_execution_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_60_execution_v1/README.md` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_60_execution_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_70_validation_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_70_validation_v1/README.md` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_70_validation_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_80_review_v1/impls/standard/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_80_review_v1/README.md` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_80_review_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/text_summarizer_ayz/impls/key_points/impl.yaml` | modify | part of repository scan baseline | medium |
| `workflows/text_summarizer_ayz/README.md` | modify | part of repository scan baseline | medium |
| `workflows/text_summarizer_ayz/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/UKBE_RUN_AGENT_ECOSYSTEM_GUIDE.md` | modify | part of repository scan baseline | medium |
| `workflows/WORKFLOW_CREATION_GUIDE.md` | modify | part of repository scan baseline | medium |
| `workflows/WORKFLOW_PLUGIN_INSTALLATION.md` | modify | part of repository scan baseline | medium |
| `workflows/WORKFLOW_STATUS.md` | modify | part of repository scan baseline | medium |

### 2.2 Configuration Changes

| File | Change Type | Description | Impact |
|------|-------------|-------------|--------|
| | | | |

### 2.3 Test Changes

| File | Change Type | Description |
|------|-------------|-------------|
| | | |

## 3. Updated Documentation

### 3.1 Documentation Created

| Document | Path | Type | Status |
|----------|------|------|--------|
| `agent-runner-v2-actions-preset-config.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-actions-preset-config.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-agentic-workflow-builder-actions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-agentic-workflow-builder-actions.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-agentic-workflow-builder-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-agentic-workflow-builder-context-extensions.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-agnes-gen-video-v1-impls-agnes-v2-actions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-agnes-gen-video-v1-impls-agnes-v2-actions.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-agnes-gen-video-v1-impls-happyhorse-v1-1-actions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-agnes-gen-video-v1-impls-happyhorse-v1-1-actions.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-agnes-media-gen-v1-impls-agnes-media-v1-actions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-agnes-media-gen-v1-impls-agnes-media-v1-actions.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-artifact-generator-builder-actions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-artifact-generator-builder-actions.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-artifact-generator-builder-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-artifact-generator-builder-context-extensions.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-artifact-generator-builder-impls-builder-bootstrap-builder-actions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-artifact-generator-builder-impls-builder-bootstrap-builder-actions.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-codebase-intelligence-actions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-codebase-intelligence-actions.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-codebase-intelligence-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-codebase-intelligence-context-extensions.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-actions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-actions.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-api-actions-init.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-api-actions-init.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-api-actions-render-image-agnes-v1.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-api-actions-render-image-agnes-v1.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-api-actions-render-image-init.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-api-actions-render-image-init.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-api-actions-render-video-agnes-v2.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-api-actions-render-video-agnes-v2.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-api-actions-render-video-init.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-api-actions-render-video-init.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-context-extensions.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-impls-init.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-impls-init.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-prompts-extract-desc-init.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-prompts-extract-desc-init.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-prompts-generate-prompts-init.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-prompts-generate-prompts-init.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-prompts-init.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-prompts-init.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-tests-init.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-tests-init.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-tests-test-context.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-tests-test-context.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-tests-test-prompt-slots.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-gen-media-content-v1-tests-test-prompt-slots.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-00-codebase-scaffold-v1-actions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-codebase-scaffold-v1-actions.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-00-codebase-scaffold-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-codebase-scaffold-v1-context-extensions.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-00-requirement-planning-v1-actions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-requirement-planning-v1-actions.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-00-requirement-planning-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-requirement-planning-v1-context-extensions.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-01-impl-exec-review-v1-actions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-01-impl-exec-review-v1-actions.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-01-impl-exec-review-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-01-impl-exec-review-v1-context-extensions.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-text-summarizer-ayz-actions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-text-summarizer-ayz-actions.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-text-summarizer-ayz-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-text-summarizer-ayz-context-extensions.md` | module | approved |
| `agent-runner-v2-bootstrap-workflows-default-text-summarizer-ayz-impls-key-points-actions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-text-summarizer-ayz-impls-key-points-actions.md` | module | approved |
| `agent-runner-v2-qwenpaw-client.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-qwenpaw-client.md` | module | approved |
| `agent-runner-v2-v2-backend-client-v1.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-v2-backend-client-v1.md` | module | approved |
| `agent-runner-v2-v2-routing-runtime.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-v2-routing-runtime.md` | module | approved |
| `agent-runner-v2-v2-transition-runtime.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-v2-transition-runtime.md` | module | approved |
| `agent-runner-v2-v2-workflow-router.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-v2-workflow-router.md` | module | approved |
| `agent-runner-v2-workflow-package-validator.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-workflow-package-validator.md` | module | approved |

### 3.2 Documentation Updated

| Document | Path | Section Updated | Reason |
|----------|------|-----------------|--------|
| `codebase_inventory.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/01_inventory/codebase_inventory.md` | inventory | repository scan baseline |
| `agent-runner-v2-action-result.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-action-result.md` | module doc | repository scan baseline |
| `agent-runner-v2-actions-archive-inputs.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-actions-archive-inputs.md` | module doc | repository scan baseline |
| `agent-runner-v2-actions-copy-artifact.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-actions-copy-artifact.md` | module doc | repository scan baseline |
| `agent-runner-v2-actions-documentation-validation-core.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-actions-documentation-validation-core.md` | module doc | repository scan baseline |
| `agent-runner-v2-actions-finalize-bootstrap.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-actions-finalize-bootstrap.md` | module doc | repository scan baseline |
| `agent-runner-v2-actions-init.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-actions-init.md` | module doc | repository scan baseline |
| `agent-runner-v2-actions-promote-artifact.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-actions-promote-artifact.md` | module doc | repository scan baseline |
| `agent-runner-v2-actions-promote-init.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-actions-promote-init.md` | module doc | repository scan baseline |
| `agent-runner-v2-actions-scan-repo-codebase.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-actions-scan-repo-codebase.md` | module doc | repository scan baseline |
| `agent-runner-v2-actions-sdlc-shared-actions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-actions-sdlc-shared-actions.md` | module doc | repository scan baseline |
| `agent-runner-v2-actions-step-completion.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-actions-step-completion.md` | module doc | repository scan baseline |
| `agent-runner-v2-actions-sync-codebase-docs.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-actions-sync-codebase-docs.md` | module doc | repository scan baseline |
| `agent-runner-v2-actions-sync-system-docs.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-actions-sync-system-docs.md` | module doc | repository scan baseline |
| `agent-runner-v2-actions-validate-codebase-docs.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-actions-validate-codebase-docs.md` | module doc | repository scan baseline |
| `agent-runner-v2-actions-validate-system-docs.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-actions-validate-system-docs.md` | module doc | repository scan baseline |
| `agent-runner-v2-api-key-pool.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-api-key-pool.md` | module doc | repository scan baseline |
| `agent-runner-v2-artifact-keys.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-artifact-keys.md` | module doc | repository scan baseline |
| `agent-runner-v2-artifact-paths.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-artifact-paths.md` | module doc | repository scan baseline |
| `agent-runner-v2-bootstrap-workflows-default-00-bootstrap-lifecycle-admin-v1-actions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-00-bootstrap-lifecycle-admin-v1-actions.md` | module doc | repository scan baseline |
| `agent-runner-v2-bootstrap-workflows-default-00-bootstrap-lifecycle-admin-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-00-bootstrap-lifecycle-admin-v1-context-extensions.md` | module doc | repository scan baseline |
| `agent-runner-v2-bootstrap-workflows-default-01-governance-foundation-v1-actions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-01-governance-foundation-v1-actions.md` | module doc | repository scan baseline |
| `agent-runner-v2-bootstrap-workflows-default-01-governance-foundation-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-01-governance-foundation-v1-context-extensions.md` | module doc | repository scan baseline |
| `agent-runner-v2-bootstrap-workflows-default-02-agent-runner-platform-v1-actions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-02-agent-runner-platform-v1-actions.md` | module doc | repository scan baseline |
| `agent-runner-v2-bootstrap-workflows-default-02-agent-runner-platform-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-02-agent-runner-platform-v1-context-extensions.md` | module doc | repository scan baseline |
| `agent-runner-v2-bootstrap-workflows-default-agnes-gen-video-v1-actions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-agnes-gen-video-v1-actions.md` | module doc | repository scan baseline |
| `agent-runner-v2-bootstrap-workflows-default-agnes-gen-video-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-agnes-gen-video-v1-context-extensions.md` | module doc | repository scan baseline |
| `agent-runner-v2-bootstrap-workflows-default-agnes-media-gen-v1-actions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-agnes-media-gen-v1-actions.md` | module doc | repository scan baseline |
| `agent-runner-v2-bootstrap-workflows-default-agnes-media-gen-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-agnes-media-gen-v1-context-extensions.md` | module doc | repository scan baseline |
| `agent-runner-v2-bootstrap-workflows-default-agnes-media-gen-v1-guardrails.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-agnes-media-gen-v1-guardrails.md` | module doc | repository scan baseline |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-00-init-doc-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-init-doc-v1-context-extensions.md` | module doc | repository scan baseline |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-10-requirement-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-10-requirement-v1-context-extensions.md` | module doc | repository scan baseline |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-20-planning-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-20-planning-v1-context-extensions.md` | module doc | repository scan baseline |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-30-backlog-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-30-backlog-v1-context-extensions.md` | module doc | repository scan baseline |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-40-task-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-40-task-v1-context-extensions.md` | module doc | repository scan baseline |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-50-implementation-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-50-implementation-v1-context-extensions.md` | module doc | repository scan baseline |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-60-execution-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-60-execution-v1-context-extensions.md` | module doc | repository scan baseline |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-70-validation-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-70-validation-v1-context-extensions.md` | module doc | repository scan baseline |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-80-review-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-80-review-v1-context-extensions.md` | module doc | repository scan baseline |
| `agent-runner-v2-bundle-governance.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bundle-governance.md` | module doc | repository scan baseline |
| `agent-runner-v2-bundle-loader.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bundle-loader.md` | module doc | repository scan baseline |
| `agent-runner-v2-bundle-taxonomy.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-bundle-taxonomy.md` | module doc | repository scan baseline |
| `agent-runner-v2-cleanup-commands.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-cleanup-commands.md` | module doc | repository scan baseline |
| `agent-runner-v2-cleanup-generated-docs.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-cleanup-generated-docs.md` | module doc | repository scan baseline |
| `agent-runner-v2-cli-runtime.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-cli-runtime.md` | module doc | repository scan baseline |
| `agent-runner-v2-codebase-docs.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-codebase-docs.md` | module doc | repository scan baseline |
| `agent-runner-v2-codebase-init-commands.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-codebase-init-commands.md` | module doc | repository scan baseline |
| `agent-runner-v2-coder-adapters.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-coder-adapters.md` | module doc | repository scan baseline |
| `agent-runner-v2-coder-registry.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-coder-registry.md` | module doc | repository scan baseline |
| `agent-runner-v2-concurrent-api.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-concurrent-api.md` | module doc | repository scan baseline |
| `agent-runner-v2-config-init.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-config-init.md` | module doc | repository scan baseline |
| `agent-runner-v2-config-loader.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-config-loader.md` | module doc | repository scan baseline |
| `agent-runner-v2-config-section-requirements.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-config-section-requirements.md` | module doc | repository scan baseline |
| `agent-runner-v2-constants.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-constants.md` | module doc | repository scan baseline |
| `agent-runner-v2-daemon-v2.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-daemon-v2.md` | module doc | repository scan baseline |
| `agent-runner-v2-doc-paths.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-doc-paths.md` | module doc | repository scan baseline |
| `agent-runner-v2-doc-text.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-doc-text.md` | module doc | repository scan baseline |
| `agent-runner-v2-documentation-guardrails.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-documentation-guardrails.md` | module doc | repository scan baseline |
| `agent-runner-v2-engine-commands.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-engine-commands.md` | module doc | repository scan baseline |
| `agent-runner-v2-exceptions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-exceptions.md` | module doc | repository scan baseline |
| `agent-runner-v2-execution-core.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-execution-core.md` | module doc | repository scan baseline |
| `agent-runner-v2-execution-request.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-execution-request.md` | module doc | repository scan baseline |
| `agent-runner-v2-execution-result.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-execution-result.md` | module doc | repository scan baseline |
| `agent-runner-v2-execution-support.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-execution-support.md` | module doc | repository scan baseline |
| `agent-runner-v2-failure-runtime.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-failure-runtime.md` | module doc | repository scan baseline |
| `agent-runner-v2-hooks-protocols.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-hooks-protocols.md` | module doc | repository scan baseline |
| `agent-runner-v2-init.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-init.md` | module doc | repository scan baseline |
| `agent-runner-v2-job-state.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-job-state.md` | module doc | repository scan baseline |
| `agent-runner-v2-list-runs-commands.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-list-runs-commands.md` | module doc | repository scan baseline |
| `agent-runner-v2-manual-runtime-deps.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-manual-runtime-deps.md` | module doc | repository scan baseline |
| `agent-runner-v2-manual-runtime.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-manual-runtime.md` | module doc | repository scan baseline |
| `agent-runner-v2-notification-manager.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-notification-manager.md` | module doc | repository scan baseline |
| `agent-runner-v2-notifications.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-notifications.md` | module doc | repository scan baseline |
| `agent-runner-v2-path-primitives.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-path-primitives.md` | module doc | repository scan baseline |
| `agent-runner-v2-recovery-runtime.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-recovery-runtime.md` | module doc | repository scan baseline |
| `agent-runner-v2-reset-step-commands.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-reset-step-commands.md` | module doc | repository scan baseline |
| `agent-runner-v2-run-agent.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-run-agent.md` | module doc | repository scan baseline |
| `agent-runner-v2-runner-actions.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-runner-actions.md` | module doc | repository scan baseline |
| `agent-runner-v2-runner-logger.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-runner-logger.md` | module doc | repository scan baseline |
| `agent-runner-v2-runtime-context.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-runtime-context.md` | module doc | repository scan baseline |
| `agent-runner-v2-runtime-hooks.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-runtime-hooks.md` | module doc | repository scan baseline |
| `agent-runner-v2-runtime-utils.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-runtime-utils.md` | module doc | repository scan baseline |
| `agent-runner-v2-shared-runtime-deps.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-shared-runtime-deps.md` | module doc | repository scan baseline |
| `agent-runner-v2-show-run-commands.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-show-run-commands.md` | module doc | repository scan baseline |
| `agent-runner-v2-single-instance.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-single-instance.md` | module doc | repository scan baseline |
| `agent-runner-v2-site-styles.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-site-styles.md` | module doc | repository scan baseline |
| `agent-runner-v2-state-defaults.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-state-defaults.md` | module doc | repository scan baseline |
| `agent-runner-v2-status-commands.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-status-commands.md` | module doc | repository scan baseline |
| `agent-runner-v2-step-execution-runtime.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-step-execution-runtime.md` | module doc | repository scan baseline |
| `agent-runner-v2-step-runner.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-step-runner.md` | module doc | repository scan baseline |
| `agent-runner-v2-submit-commands.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-submit-commands.md` | module doc | repository scan baseline |
| `agent-runner-v2-submitter.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-submitter.md` | module doc | repository scan baseline |
| `agent-runner-v2-sync-workflows.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-sync-workflows.md` | module doc | repository scan baseline |
| `agent-runner-v2-system-docs.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-system-docs.md` | module doc | repository scan baseline |
| `agent-runner-v2-task-runtime.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-task-runtime.md` | module doc | repository scan baseline |
| `agent-runner-v2-tools-agent-tools.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-tools-agent-tools.md` | module doc | repository scan baseline |
| `agent-runner-v2-v2-backend-client.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-v2-backend-client.md` | module doc | repository scan baseline |
| `agent-runner-v2-v2-init.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-v2-init.md` | module doc | repository scan baseline |
| `agent-runner-v2-v2-queue.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-v2-queue.md` | module doc | repository scan baseline |
| `agent-runner-v2-v2-sync.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-v2-sync.md` | module doc | repository scan baseline |
| `agent-runner-v2-workflow-bundle-validate-commands.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-workflow-bundle-validate-commands.md` | module doc | repository scan baseline |
| `agent-runner-v2-workflow-bundle-validator.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-workflow-bundle-validator.md` | module doc | repository scan baseline |
| `agent-runner-v2-workflow-packages-actions-init.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-workflow-packages-actions-init.md` | module doc | repository scan baseline |
| `agent-runner-v2-workflow-packages-base.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-workflow-packages-base.md` | module doc | repository scan baseline |
| `agent-runner-v2-workflow-packages-extensions-base.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-workflow-packages-extensions-base.md` | module doc | repository scan baseline |
| `agent-runner-v2-workflow-packages-hooks.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-workflow-packages-hooks.md` | module doc | repository scan baseline |
| `agent-runner-v2-workflow-packages-init.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-workflow-packages-init.md` | module doc | repository scan baseline |
| `agent-runner-v2-workflow-packages-loader.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-workflow-packages-loader.md` | module doc | repository scan baseline |
| `agent-runner-v2-workflow-packages-registry.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-workflow-packages-registry.md` | module doc | repository scan baseline |
| `agent-runner-v2-workflow-path-contracts.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-workflow-path-contracts.md` | module doc | repository scan baseline |
| `agent-runner-v2-workflow-runtime.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-workflow-runtime.md` | module doc | repository scan baseline |
| `agent-runner-v2-workflow-spec-commands.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-workflow-spec-commands.md` | module doc | repository scan baseline |
| `agent-runner-v2-workflow-specs.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-workflow-specs.md` | module doc | repository scan baseline |
| `actions-package.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/03_components/actions-package.md` | component doc | repository scan baseline |
| `codebase-governance.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/03_components/codebase-governance.md` | component doc | repository scan baseline |
| `config-and-data.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/03_components/config-and-data.md` | component doc | repository scan baseline |
| `scripts-suite.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/03_components/scripts-suite.md` | component doc | repository scan baseline |
| `tests-suite.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/03_components/tests-suite.md` | component doc | repository scan baseline |
| `workflow-families.md` | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/03_components/workflow-families.md` | component doc | repository scan baseline |

### 3.3 Inventory Updates

| Module | Previous Status | New Status | Owner Doc Path |
|--------|----------------|------------|----------------|
| `codebase_inventory.md` | undocumented | current | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/01_inventory/codebase_inventory.md` |
| `agent-runner-v2-init.md` | undocumented | current | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-init.md` |
| `agent-runner-v2-action-result.md` | undocumented | current | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-action-result.md` |
| `agent-runner-v2-actions-init.md` | undocumented | current | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-actions-init.md` |
| `agent-runner-v2-actions-archive-inputs.md` | undocumented | current | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-actions-archive-inputs.md` |
| `agent-runner-v2-actions-copy-artifact.md` | undocumented | current | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-actions-copy-artifact.md` |
| `agent-runner-v2-actions-documentation-validation-core.md` | undocumented | current | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-actions-documentation-validation-core.md` |
| `agent-runner-v2-actions-finalize-bootstrap.md` | undocumented | current | `docs/repo/codebase/runs/SDLC00CS-1zcrrbbs/02_modules/agent-runner-v2-actions-finalize-bootstrap.md` |

## 4. Stale Documentation Removal

### 4.1 Stale Documents Identified

| Document | Path | Reason for Staleness | Action |
|----------|------|---------------------|--------|
| | | | |

### 4.2 Removal Log

| Document | Path | Removed By | Date | Reason |
|----------|------|-----------|------|--------|
| | | | | |

## 5. Impact Assessment

### 5.1 Affected Components

| Component | Impact | Documentation Status |
|-----------|--------|---------------------|
| codebase documentation baseline | high | current |

### 5.2 Affected Workflows

| Workflow | Impact | Notes |
|----------|--------|-------|
| `sdlc_00_codebase_scaffold_v1` | high | repository scan baseline |

### 5.3 Backward Compatibility

| Aspect | Compatible | Notes |
|--------|-----------|-------|
| API | yes | documentation only |
| Configuration | yes | no code changes |
| Sidecar contract | yes | action writes standard v2 meta.json |

## 6. Documentation Debt

| Item | Reason for Deferral | Owner | Due Date |
|------|-------------------|-------|----------|
| | | | |

## 7. Verification

| Check | Status | Notes |
|-------|--------|-------|
| All changed files listed | pass | repository scan summary |
| All updated docs listed | pass | generated docs |
| Stale docs identified and handled | pass | regenerated baseline |
| Inventory updated | pass | current scan |
