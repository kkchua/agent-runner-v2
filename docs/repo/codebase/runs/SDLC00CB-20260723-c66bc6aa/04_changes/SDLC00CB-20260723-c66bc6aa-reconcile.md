---
title: "Change Impact: agent-runner-v2 codebase reconcile"
template_id: "CB-04"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
change_id: "SDLC00CB-20260723-c66bc6aa"
task_id: "sdlc_00_codebase_v1"
initiative_id: "codebase-doc-bootstrap"
created: "2026-07-23T20:12:07+08:00"
author: "sdlc_00_codebase_v1"
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
| `_test_payload.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/__init__.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/action_result.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/actions/__init__.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/actions/copy_artifact.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/actions/documentation_validation_core.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/actions/finalize_bootstrap.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/actions/promote_artifact.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/actions/promote_init.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/actions/scan_repo_codebase.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/actions/sdlc_shared_actions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/actions/step_completion.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/actions/sync_codebase_docs.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/actions/sync_system_docs.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/actions/validate_codebase_docs.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/actions/validate_system_docs.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/approve_commands.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/artifact_keys.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/artifact_paths.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/backend_client.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/backend_execution.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/00BOOT-20260719-5ceb9505-bootstrap-lifecycle-summary.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/00BOOT-20260720-5d679fd5-bootstrap-lifecycle-summary.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/00BOOT-20260720-818a452f-bootstrap-lifecycle-summary.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/00BOOT-20260720-f7113f08-bootstrap-lifecycle-summary.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/00BOOT-20260721-2af1fe38-bootstrap-lifecycle-summary.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/00BOOT-20260721-86fb57bb-bootstrap-lifecycle-summary.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/00BOOT-20260722-2dcbbdfe-bootstrap-lifecycle-summary.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/00BOOT-20260722-9877c2ee-bootstrap-lifecycle-summary.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/bundles/core/current/bootstrap_publish_manifest.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/00_bootstrap_lifecycle_admin_v1/actions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/00_bootstrap_lifecycle_admin_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
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
| `agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/output_paths.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/prompts/01_generate_governance_foundation_docs.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/prompts/02_review_governance_foundation_docs.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/prompts/03_refine_governance_foundation_docs.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/prompts/04_audit_governance_foundation_docs.txt` | modify | part of repository scan baseline | medium |
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
| `agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/output_paths.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/prompts/01_generate_platform_core_docs.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/prompts/02_review_platform_core_docs.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/prompts/03_refine_platform_core_docs.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/prompts/04_audit_platform_core_docs.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/_registry/coder_connections.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/_registry/coder_roles.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/_registry/coder_roles_opencode.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/_registry/coder_roles_qwen.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/_registry/role_policies.json` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_v1/actions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_v1/bundle_governance.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_v1/bundle_governance/core_governance.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_v1/bundle_governance/generated/AGENTS.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_v1/bundle_governance/generated/CLAUDE.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_v1/bundle_governance/generated/QWEN.md` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_v1/prompts/04_review_sync_log.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_v1/prompts/05_refine_codebase_docs.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_delivery_scaffold_v1/actions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_delivery_scaffold_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_delivery_scaffold_v1/install.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_delivery_scaffold_v1/prompts/01_generate_templates.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_delivery_scaffold_v1/prompts/02_generate_agent_contracts.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_delivery_scaffold_v1/prompts/03_review_scaffold.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_delivery_scaffold_v1/prompts/04_refine_scaffold.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_delivery_scaffold_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_init_doc_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_init_doc_v1/prompts/01_generate_initiative.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_init_doc_v1/prompts/02_technical_critique.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_init_doc_v1/prompts/03_review_initiative.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_init_doc_v1/prompts/04_refine_initiative.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_00_init_doc_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_10_requirement_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_10_requirement_v1/prompts/01_generate_requirements.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_10_requirement_v1/prompts/02_technical_critique.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_10_requirement_v1/prompts/03_review_requirements.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_10_requirement_v1/prompts/04_refine_requirements.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_10_requirement_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_20_planning_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_20_planning_v1/prompts/01_generate_plan.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_20_planning_v1/prompts/02_technical_critique.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_20_planning_v1/prompts/03_review_plan.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_20_planning_v1/prompts/04_refine_plan.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_20_planning_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_30_backlog_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_30_backlog_v1/prompts/01_generate_backlog.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_30_backlog_v1/prompts/02_technical_critique.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_30_backlog_v1/prompts/03_review_backlog.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_30_backlog_v1/prompts/04_refine_backlog.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_30_backlog_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_40_task_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_40_task_v1/prompts/01_generate_task.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_40_task_v1/prompts/02_technical_critique.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_40_task_v1/prompts/03_review_task.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_40_task_v1/prompts/04_refine_task.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_40_task_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_50_implementation_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_50_implementation_v1/prompts/01_generate_implementation.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_50_implementation_v1/prompts/02_technical_critique.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_50_implementation_v1/prompts/03_review_implementation.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_50_implementation_v1/prompts/04_refine_implementation.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_50_implementation_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_60_execution_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_60_execution_v1/prompts/01_execute_task.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_60_execution_v1/prompts/02_technical_critique.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_60_execution_v1/prompts/03_internal_review.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_60_execution_v1/prompts/04_refine_execution.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_60_execution_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_70_validation_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_70_validation_v1/prompts/01_generate_validation.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_70_validation_v1/prompts/02_technical_critique.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_70_validation_v1/prompts/03_review_validation.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_70_validation_v1/prompts/04_refine_validation.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_70_validation_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_80_review_v1/context_extensions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_80_review_v1/prompts/01_generate_review.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_80_review_v1/prompts/02_technical_critique.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_80_review_v1/prompts/03_review_all.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_80_review_v1/prompts/04_refine_documents.txt` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bootstrap/workflows/default/sdlc_80_review_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bundle_governance.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bundle_loader.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/bundle_taxonomy.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/cleanup_generated_docs.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/cli_runtime.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/codebase_docs.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/codebase_init_commands.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/coder_adapters.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/coder_registry.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/config/__init__.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/config/section_requirements.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/config_loader.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/console_commands.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/constants.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/constants_legacy_backup_20260717.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/daemon.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/daemon_runtime.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/doc_paths.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/documentation_guardrails.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/engine_commands.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/exceptions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/execution_core.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/execution_request.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/execution_result.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/execution_support.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/failure_runtime.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/job_state.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/manual_runtime.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/manual_runtime_deps.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/notification_manager.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/notifications.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/operator_console/__init__.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/operator_console/app.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/operator_console/app1.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/operator_console/config.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/operator_console/models.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/operator_console/services/__init__.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/operator_console/services/backend_service.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/operator_console/services/runner_service.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/path_catalog.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/path_primitives.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/recovery_runtime.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/routing_runtime.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/run_agent.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/runner_actions.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/runner_logger.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/runtime_context.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/runtime_utils.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/shared_runtime_deps.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/site_styles.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/state_defaults.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/step_execution_runtime.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/step_runner.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/stop_commands.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/submit_commands.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/submitter.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/sync_workflows.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/system_docs.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/task_runtime.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/tools/agent_tools.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/transition_runtime.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/workflow_bundle_validate_commands.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/workflow_bundle_validator.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/workflow_packages/__init__.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/workflow_packages/actions/__init__.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/workflow_packages/base.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/workflow_packages/extensions_base.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/workflow_packages/hooks.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/workflow_packages/loader.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/workflow_packages/registry.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/workflow_path_contracts.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/workflow_router.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/workflow_runtime.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/workflow_spec_commands.py` | modify | part of repository scan baseline | medium |
| `agent_runner_v2/workflow_specs.py` | modify | part of repository scan baseline | medium |
| `AGENT_RUNNER_V2_SPECIALIST.md` | modify | part of repository scan baseline | medium |
| `CLAUDE.md` | modify | part of repository scan baseline | medium |
| `CODER_IMPLEMENTATION_SOP.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/00_draft_initiatives/DRAFT-INIT-20260722-001_console-sdlc10-support.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/00_initiatives/INIT-20260723-001_console-sdlc10-support.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/00_initiatives/INIT-20260723-001_console-sdlc10-support.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/00_initiatives/INIT-20260723-002_console-sdlc10-support.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/10_requirements/REQ-20260723-001_console-sdlc10-support.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/10_requirements/REQ-20260723-001_console-sdlc10-support.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/20_plans/PLAN-20260723-001_console-sdlc10-support.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/20_plans/PLAN-20260723-001_console-sdlc10-support.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/30_backlogs/BACKLOG-20260723-001_console-sdlc10-support.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/30_backlogs/BACKLOG-20260723-001_console-sdlc10-support.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/40_tasks/WI-20260723-001_console-sdlc10-support-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/40_tasks/WI-20260723-001_console-sdlc10-support-01.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/40_tasks/WI-20260723-001_console-sdlc10-support-02.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/40_tasks/WI-20260723-001_console-sdlc10-support-02.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/50_implementations/IMPL-20260723-001-001_console-sdlc10-support-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/50_implementations/IMPL-20260723-001-001_console-sdlc10-support-01.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/60_executions/EXEC-20260723-001-001_console-sdlc10-support-01.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/console-sdlc10-support-01-REV-50-impl.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/console-sdlc10-support-CRITIQUE-00-init.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/console-sdlc10-support-REV-00-init.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/console-sdlc10-support-REV-10-req.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/console-sdlc10-support-REV-20-plan.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/console-sdlc10-support-REV-30-backlog.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/WI-20260723-001_console-sdlc10-support-01-REV-40-task.md` | modify | part of repository scan baseline | medium |
| `docs/repo/agent_runner/sdlc/delivery/80_reviews/WI-20260723-001_console-sdlc10-support-02-REV-40-task.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260723-193004/00_standards/CODEBASE_DOC_SOP.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260723-193004/00_standards/CODEBASE_DOC_STATUS_RULES.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260723-201201/00_standards/CODEBASE_DOC_SOP.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/backups/BACKUP-20260723-201201/00_standards/CODEBASE_DOC_STATUS_RULES.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/00_standards/CODEBASE_DOC_SOP.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/current/00_standards/CODEBASE_DOC_STATUS_RULES.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/01_inventory/codebase_inventory.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/01_inventory/codebase_inventory.meta.json` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-action-result.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-actions-copy-artifact.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-actions-documentation-validation-core.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-actions-finalize-bootstrap.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-actions-init.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-actions-promote-artifact.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-actions-promote-init.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-actions-scan-repo-codebase.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-actions-sdlc-shared-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-actions-step-completion.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-actions-sync-codebase-docs.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-actions-sync-system-docs.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-actions-validate-codebase-docs.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-actions-validate-system-docs.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-approve-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-artifact-keys.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-artifact-paths.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-backend-client.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-backend-execution.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-bootstrap-workflows-default-00-bootstrap-lifecycle-admin-v1-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-bootstrap-workflows-default-00-bootstrap-lifecycle-admin-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-bootstrap-workflows-default-01-governance-foundation-v1-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-bootstrap-workflows-default-01-governance-foundation-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-bootstrap-workflows-default-01-governance-foundation-v1-output-paths.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-bootstrap-workflows-default-02-agent-runner-platform-v1-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-bootstrap-workflows-default-02-agent-runner-platform-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-bootstrap-workflows-default-02-agent-runner-platform-v1-output-paths.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-codebase-v1-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-codebase-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-delivery-scaffold-v1-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-delivery-scaffold-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-delivery-scaffold-v1-install.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-init-doc-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-10-requirement-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-20-planning-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-30-backlog-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-40-task-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-50-implementation-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-60-execution-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-70-validation-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-80-review-v1-context-extensions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-bundle-governance.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-bundle-loader.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-bundle-taxonomy.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-cleanup-generated-docs.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-cli-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-codebase-docs.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-codebase-init-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-coder-adapters.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-coder-registry.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-config-init.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-config-loader.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-config-section-requirements.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-console-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-constants-legacy-backup-20260717.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-constants.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-daemon-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-daemon.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-doc-paths.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-documentation-guardrails.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-engine-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-exceptions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-execution-core.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-execution-request.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-execution-result.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-execution-support.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-failure-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-init.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-job-state.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-manual-runtime-deps.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-manual-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-notification-manager.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-notifications.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-operator-console-app.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-operator-console-app1.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-operator-console-config.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-operator-console-init.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-operator-console-models.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-operator-console-services-backend-service.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-operator-console-services-init.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-operator-console-services-runner-service.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-path-catalog.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-path-primitives.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-recovery-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-routing-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-run-agent.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-runner-actions.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-runner-logger.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-runtime-context.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-runtime-utils.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-shared-runtime-deps.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-site-styles.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-state-defaults.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-step-execution-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-step-runner.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-stop-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-submit-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-submitter.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-sync-workflows.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-system-docs.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-task-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-tools-agent-tools.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-transition-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-workflow-bundle-validate-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-workflow-bundle-validator.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-workflow-packages-actions-init.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-workflow-packages-base.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-workflow-packages-extensions-base.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-workflow-packages-hooks.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-workflow-packages-init.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-workflow-packages-loader.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-workflow-packages-registry.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-workflow-path-contracts.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-workflow-router.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-workflow-runtime.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-workflow-spec-commands.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/02_modules/agent-runner-v2-workflow-specs.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/03_components/actions-package.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/03_components/codebase-governance.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/03_components/config-and-data.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/03_components/scripts-suite.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/03_components/tests-suite.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/03_components/workflow-families.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/04_changes/SDLC00CB-20260723-945a0559-reconcile.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/sync_logs/SDLC00CB-20260723-945a0559-review.md` | modify | part of repository scan baseline | medium |
| `docs/repo/codebase/runs/SDLC00CB-20260723-945a0559/sync_logs/SYNC-SDLC00CB-20260723-945a0559.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/00BOOT-20260719-5ceb9505-bootstrap-lifecycle-summary.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/00BOOT-20260720-5d679fd5-bootstrap-lifecycle-summary.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/00BOOT-20260720-818a452f-bootstrap-lifecycle-summary.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/00BOOT-20260720-f7113f08-bootstrap-lifecycle-summary.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/00BOOT-20260721-2af1fe38-bootstrap-lifecycle-summary.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/00BOOT-20260721-86fb57bb-bootstrap-lifecycle-summary.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/00BOOT-20260722-2dcbbdfe-bootstrap-lifecycle-summary.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/00BOOT-20260722-9877c2ee-bootstrap-lifecycle-summary.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/00_bootstrap_lifecycle_admin_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/bundle_governance.toml` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/bundle_governance/action_policy.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/bundle_governance/core_governance.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/bundle_governance/generated/AGENTS.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/bundle_governance/generated/CLAUDE.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/bundle_governance/generated/QWEN.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/bundle_governance/prompt_contract.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/bundle_governance/prompt_layout.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/bundle_governance/prompt_sop.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/bundle_governance/review_audit_contract.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/bundle_governance.toml` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/bundle_governance/action_policy.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/bundle_governance/core_governance.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/bundle_governance/generated/AGENTS.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/bundle_governance/generated/CLAUDE.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/bundle_governance/generated/QWEN.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/bundle_governance/prompt_contract.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/bundle_governance/prompt_layout.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/bundle_governance/prompt_sop.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/bundle_governance/review_audit_contract.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/_registry/coder_connections.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/_registry/coder_roles.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/_registry/coder_roles_opencode.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/_registry/coder_roles_qwen.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/_registry/role_policies.json` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/sdlc_00_codebase_v1/bundle_governance.toml` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/sdlc_00_codebase_v1/bundle_governance/core_governance.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/sdlc_00_codebase_v1/bundle_governance/generated/AGENTS.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/sdlc_00_codebase_v1/bundle_governance/generated/CLAUDE.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/sdlc_00_codebase_v1/bundle_governance/generated/QWEN.md` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/sdlc_00_codebase_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/sdlc_00_delivery_scaffold_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/sdlc_00_init_doc_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/sdlc_10_requirement_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/sdlc_20_planning_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/sdlc_30_backlog_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/sdlc_40_task_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/sdlc_50_implementation_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/sdlc_60_execution_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/sdlc_70_validation_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `docs/system/00_governance/bootstrap/workflows/sdlc_80_review_v1/workflow.toml` | modify | part of repository scan baseline | medium |
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
| `masterplan/00_repo_master_docs_bootstrap_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/00_templates/01_initiative.template.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/00_templates/02_plan.template.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/00_templates/02b_task_graph.template.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/00_templates/03_task.template.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/00_templates/04_implementation_plan.template.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/00_templates/04_review.template.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/00_templates/05_agent.template.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/00_templates/05_validation.template.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/00_templates/06_memory.template.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/00_templates/_legacy/decision-template.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/00_templates/_legacy/execution-summary-template.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/00_templates/_legacy/initiative-template.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/00_templates/_legacy/outcome-template.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/00_templates/_legacy/plan-template.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/00_templates/_legacy/review-template.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/00_templates/_legacy/self-test-result-template.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/00_templates/_legacy/task-template.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/00_templates/_legacy/test-plan-template.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/00_templates/_legacy/test-result-template.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/00_templates/_legacy/test-result-<task>-codex.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/00_templates/template_registry.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/00_templates/WORKFLOW_SOP_v1.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/01_initiatives/INIT-20260418-04_managed-artifact-control-plane-exposure-v1.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/02_plans/artifacts/TASK-GRAPH-20260418-PLAN-20260418-02.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/02_plans/PLAN-20260418-02_managed-artifact-control-plane-exposure-v1.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/03_tasks/TASK-20260418-01_contract-build-api-trigger.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/03_tasks/TASK-20260418-01_contract-build-api-trigger.meta.json` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/03_tasks/TASK-20260418-02_managed-generation-api-trigger.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/03_tasks/TASK-20260418-02_managed-generation-api-trigger.meta.json` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/03_tasks/TASK-20260418-03_generation-run-api-surface.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/03_tasks/TASK-20260418-03_generation-run-api-surface.meta.json` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/03_tasks/TASK-20260418-04_artifact-lifecycle-retrieval.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/03_tasks/TASK-20260418-04_artifact-lifecycle-retrieval.meta.json` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/03_tasks/TASK-20260418-05_router-registration-documentation.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/03_tasks/TASK-20260418-05_router-registration-documentation.meta.json` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/04_implementation_plans/IMPL-20260418-01_contract-build-api-trigger.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/04_implementation_plans/IMPL-20260418-01_contract-build-api-trigger.meta.json` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/04_implementation_plans/IMPL-20260418-02_managed-generation-api-trigger.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/04_implementation_plans/IMPL-20260418-02_managed-generation-api-trigger.meta.json` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/04_implementation_plans/IMPL-20260418-03_generation-run-api-surface.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/04_implementation_plans/IMPL-20260418-03_generation-run-api-surface.meta.json` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/05_reviews/REV-260418-01_rtask_T-0418-01_contract-build-api-trigger.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/05_reviews/REV-260418-01_rtask_T-0418-01_contract-build-api-trigger.meta.json` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/05_reviews/REV-260418-02_rimpl_M-0418-01_contract-build-api-trigger.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/05_reviews/REV-260418-02_rimpl_M-0418-01_contract-build-api-trigger.meta.json` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/05_reviews/REV-260418-03_rtask_T-0418-02_managed-generation-api-trigger.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/05_reviews/REV-260418-03_rtask_T-0418-02_managed-generation-api-trigger.meta.json` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/05_reviews/REV-260418-04_rtask_T-0418-02_managed-generation-api-trigger.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/05_reviews/REV-260418-04_rtask_T-0418-02_managed-generation-api-trigger.meta.json` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/05_reviews/REV-260418-05_rimpl_M-0418-02_managed-generation-api-trigger.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/05_reviews/REV-260418-05_rimpl_M-0418-02_managed-generation-api-trigger.meta.json` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/05_reviews/VALIDATION-260418-2-M-0418-01_contract-build-api-trigger.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/05_reviews/VALIDATION-260418-2-M-0418-01_contract-build-api-trigger.meta.json` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/05_reviews/VALIDATION-260418-2-M-0418-02_managed-generation-api-trigger.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/05_reviews/VALIDATION-260418-2-M-0418-02_managed-generation-api-trigger.meta.json` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/05_reviews/VALIDATION-260418-3-M-0418-02_managed-generation-api-trigger.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/05_reviews/VALIDATION-260418-3-M-0418-02_managed-generation-api-trigger.meta.json` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/05_reviews/VALIDATION-260418-M-0418-01_contract-build-api-trigger.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/05_reviews/VALIDATION-260418-M-0418-01_contract-build-api-trigger.meta.json` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/05_reviews/VALIDATION-260418-M-0418-02_managed-generation-api-trigger.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/05_reviews/VALIDATION-260418-M-0418-02_managed-generation-api-trigger.meta.json` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/08_agents/AGENT-executor.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/08_agents/AGENT-implementation-planner.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/08_agents/AGENT-memory-manager.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/08_agents/AGENT-planner.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/08_agents/AGENT-reviewer.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/08_agents/AGENT-task-decomposer.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/08_agents/AGENTS.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/08_agents/DELIVERY_STATUS_RULES_v1.md` | modify | part of repository scan baseline | medium |
| `masterplan/delivery/README.md` | modify | part of repository scan baseline | medium |
| `masterplan/LAYER1_GOVERNANCE_SPECIFICATION.md` | modify | part of repository scan baseline | medium |
| `masterplan/LAYER2_PLATFORM_CORE_SPECIFICATION.md` | modify | part of repository scan baseline | medium |
| `masterplan/LAYER3_AI_DRIVEN_SDLC_IMPLEMENTATION_PLAN.md` | modify | part of repository scan baseline | medium |
| `masterplan/LAYER3_AI_DRIVEN_SDLC_SPECIFICATION.md` | modify | part of repository scan baseline | medium |
| `masterplan/LAYER_ARCHITECTURE_MASTERPLAN.md` | modify | part of repository scan baseline | medium |
| `masterplan/old legacy workflow/comfyui_config.json` | modify | part of repository scan baseline | medium |
| `masterplan/old legacy workflow/job_schema.json` | modify | part of repository scan baseline | medium |
| `masterplan/old legacy workflow/llm_response_schema.json` | modify | part of repository scan baseline | medium |
| `masterplan/old legacy workflow/model_mapping.json` | modify | part of repository scan baseline | medium |
| `masterplan/old legacy workflow/usage_schema.json` | modify | part of repository scan baseline | medium |
| `masterplan/README.md` | modify | part of repository scan baseline | medium |
| `masterplan/SDLC_00_CODEBASE_V1_PLAN.md` | modify | part of repository scan baseline | medium |
| `masterplan/SDLC_CONSOLE_APP_PLAN.md` | modify | part of repository scan baseline | medium |
| `masterplan/SDLC_TECHNICAL_CRITIQUE_PLAN.md` | modify | part of repository scan baseline | medium |
| `masterplan/SDLC_WORKFLOW_SCAFFOLD_PLAN.md` | modify | part of repository scan baseline | medium |
| `masterplan/WORKFLOW_EXTENSION_INTERFACE_PLAN.md` | modify | part of repository scan baseline | medium |
| `opencode.json` | modify | part of repository scan baseline | medium |
| `operator-console.example.json` | modify | part of repository scan baseline | medium |
| `platform_context_manifest.json` | modify | part of repository scan baseline | medium |
| `pyproject.toml` | modify | part of repository scan baseline | medium |
| `QWEN.md` | modify | part of repository scan baseline | medium |
| `README.md` | modify | part of repository scan baseline | medium |
| `run-00_bootstrap_lifecycle_admin_v1.bat` | modify | part of repository scan baseline | medium |
| `run-00_bootstrap_lifecycle_admin_v1.sh` | modify | part of repository scan baseline | medium |
| `run-01_governance_foundation_v1.bat` | modify | part of repository scan baseline | medium |
| `run-01_governance_foundation_v1.sh` | modify | part of repository scan baseline | medium |
| `run-02_agent_runner_platform_v1.bat` | modify | part of repository scan baseline | medium |
| `run-02_agent_runner_platform_v1.sh` | modify | part of repository scan baseline | medium |
| `run-approve-step.bat` | modify | part of repository scan baseline | medium |
| `run-approve-step.sh` | modify | part of repository scan baseline | medium |
| `run-bootstrap-publish.bat` | modify | part of repository scan baseline | medium |
| `run-bootstrap-publish.sh` | modify | part of repository scan baseline | medium |
| `run-cleanup-workflow.bat` | modify | part of repository scan baseline | medium |
| `run-cleanup-workflow.sh` | modify | part of repository scan baseline | medium |
| `run-console.bat` | modify | part of repository scan baseline | medium |
| `run-console.sh` | modify | part of repository scan baseline | medium |
| `run-daemon.bat` | modify | part of repository scan baseline | medium |
| `run-daemon.sh` | modify | part of repository scan baseline | medium |
| `run-init.bat` | modify | part of repository scan baseline | medium |
| `run-init.sh` | modify | part of repository scan baseline | medium |
| `run-reset-step.bat` | modify | part of repository scan baseline | medium |
| `run-reset-step.sh` | modify | part of repository scan baseline | medium |
| `run-sdlc_00_codebase_v1.bat` | modify | part of repository scan baseline | medium |
| `run-sdlc_00_codebase_v1.sh` | modify | part of repository scan baseline | medium |
| `run-sdlc_00_delivery_scaffold_v1.bat` | modify | part of repository scan baseline | medium |
| `run-sdlc_00_delivery_scaffold_v1.sh` | modify | part of repository scan baseline | medium |
| `run-sdlc_00_init_doc_v1.bat` | modify | part of repository scan baseline | medium |
| `run-sdlc_00_init_doc_v1.sh` | modify | part of repository scan baseline | medium |
| `run-sdlc_10_requirement_v1.bat` | modify | part of repository scan baseline | medium |
| `run-sdlc_10_requirement_v1.sh` | modify | part of repository scan baseline | medium |
| `run-sdlc_20_planning_v1.bat` | modify | part of repository scan baseline | medium |
| `run-sdlc_20_planning_v1.sh` | modify | part of repository scan baseline | medium |
| `run-sdlc_30_backlog_v1.bat` | modify | part of repository scan baseline | medium |
| `run-sdlc_30_backlog_v1.sh` | modify | part of repository scan baseline | medium |
| `run-sdlc_40_task_v1.bat` | modify | part of repository scan baseline | medium |
| `run-sdlc_40_task_v1.sh` | modify | part of repository scan baseline | medium |
| `run-sdlc_50_implementation_v1.bat` | modify | part of repository scan baseline | medium |
| `run-sdlc_50_implementation_v1.sh` | modify | part of repository scan baseline | medium |
| `run-sdlc_60_execution_v1.bat` | modify | part of repository scan baseline | medium |
| `run-sdlc_60_execution_v1.sh` | modify | part of repository scan baseline | medium |
| `run-sdlc_70_validation_v1.bat` | modify | part of repository scan baseline | medium |
| `run-sdlc_70_validation_v1.sh` | modify | part of repository scan baseline | medium |
| `run-sdlc_80_review_v1.bat` | modify | part of repository scan baseline | medium |
| `run-sdlc_80_review_v1.sh` | modify | part of repository scan baseline | medium |
| `submit-00_bootstrap_lifecycle_admin_v1.bat` | modify | part of repository scan baseline | medium |
| `submit-00_bootstrap_lifecycle_admin_v1.sh` | modify | part of repository scan baseline | medium |
| `submit-01_governance_foundation_v1.bat` | modify | part of repository scan baseline | medium |
| `submit-01_governance_foundation_v1.sh` | modify | part of repository scan baseline | medium |
| `submit-02_agent_runner_platform_v1.bat` | modify | part of repository scan baseline | medium |
| `submit-02_agent_runner_platform_v1.sh` | modify | part of repository scan baseline | medium |
| `submit-sdlc_00_codebase_v1.bat` | modify | part of repository scan baseline | medium |
| `submit-sdlc_00_codebase_v1.sh` | modify | part of repository scan baseline | medium |
| `submit-sdlc_00_init_doc_v1.bat` | modify | part of repository scan baseline | medium |
| `submit-sdlc_00_init_doc_v1.sh` | modify | part of repository scan baseline | medium |
| `submit-sdlc_10_requirement_v1.bat` | modify | part of repository scan baseline | medium |
| `submit-sdlc_10_requirement_v1.sh` | modify | part of repository scan baseline | medium |
| `submit-sdlc_20_planning_v1.bat` | modify | part of repository scan baseline | medium |
| `submit-sdlc_20_planning_v1.sh` | modify | part of repository scan baseline | medium |
| `submit-sdlc_30_backlog_v1.bat` | modify | part of repository scan baseline | medium |
| `submit-sdlc_30_backlog_v1.sh` | modify | part of repository scan baseline | medium |
| `submit-sdlc_40_task_v1.bat` | modify | part of repository scan baseline | medium |
| `submit-sdlc_40_task_v1.sh` | modify | part of repository scan baseline | medium |
| `submit-sdlc_50_implementation_v1.bat` | modify | part of repository scan baseline | medium |
| `submit-sdlc_50_implementation_v1.sh` | modify | part of repository scan baseline | medium |
| `submit-sdlc_60_execution_v1.bat` | modify | part of repository scan baseline | medium |
| `submit-sdlc_60_execution_v1.sh` | modify | part of repository scan baseline | medium |
| `submit-sdlc_70_validation_v1.bat` | modify | part of repository scan baseline | medium |
| `submit-sdlc_70_validation_v1.sh` | modify | part of repository scan baseline | medium |
| `submit-sdlc_80_review_v1.bat` | modify | part of repository scan baseline | medium |
| `submit-sdlc_80_review_v1.sh` | modify | part of repository scan baseline | medium |
| `sync-workflows-to-backend.bat` | modify | part of repository scan baseline | medium |
| `sync-workflows-to-backend.sh` | modify | part of repository scan baseline | medium |
| `tests/conftest.py` | modify | part of repository scan baseline | medium |
| `tests/integration/__init__.py` | modify | part of repository scan baseline | medium |
| `tests/integration/README.md` | modify | part of repository scan baseline | medium |
| `tests/integration/test_architecture_site.py` | modify | part of repository scan baseline | medium |
| `tests/integration/test_backend_worker_mode.py` | modify | part of repository scan baseline | medium |
| `tests/integration/test_daemon.py` | modify | part of repository scan baseline | medium |
| `tests/integration/test_notification_e2e.py` | modify | part of repository scan baseline | medium |
| `tests/integration/test_notification_integration.py` | modify | part of repository scan baseline | medium |
| `tests/integration/test_notifications.py` | modify | part of repository scan baseline | medium |
| `tests/integration/test_pushover.py` | modify | part of repository scan baseline | medium |
| `tests/integration/test_ukbe_runner_wrapper.py` | modify | part of repository scan baseline | medium |
| `tests/run_workflow_unit_tests.py` | modify | part of repository scan baseline | medium |
| `tests/unit/__init__.py` | modify | part of repository scan baseline | medium |
| `tests/unit/README.md` | modify | part of repository scan baseline | medium |
| `tests/unit/test_agent_tools.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_backend_execution.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_bundle_loader.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_codebase_docs.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_codebase_init_commands.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_coder_adapters_opencode.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_coder_adapters_sidecar_grace.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_constants_registry.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_context_extensions.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_daemon_runtime.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_daemon_worker_payload.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_documentation_governance.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_documentation_guardrails_cleanup.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_execution_core.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_failure_runtime.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_generated_doc_frontmatter_injection.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_job_state_review_completion.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_job_state_step_dirs.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_job_state_usage_summary.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_machine_contracts.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_manual_runtime.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_model_config_roles.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_notification_manager.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_operator_console_config.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_operator_console_services.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_plugin_workflow_support.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_promote_artifact.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_recovery_runtime.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_routing_runtime.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_run_agent_hook_surface.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_run_agent_legacy_cli.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_run_agent_status.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_runtime_context_paths.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_runtime_utils.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_sdlc_shared_actions.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_state_defaults.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_step_completion.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_step_runner_write_contract.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_stop_commands.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_submit_commands.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_sync_workflows.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_task_runtime.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_tool_instruction_block.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_transition_recovery_runtime.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_transition_runtime.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_workflow_bundle_validator.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_workflow_packages.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_workflow_registry.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_workflow_router_notifications.py` | modify | part of repository scan baseline | medium |
| `tests/unit/test_workflow_specs.py` | modify | part of repository scan baseline | medium |
| `tests/unit/workflows/00_bootstrap_lifecycle_admin_v1/test_actions.py` | modify | part of repository scan baseline | medium |
| `tests/unit/workflows/00_core_governance_bootstrap_v1/__init__.py` | modify | part of repository scan baseline | medium |
| `tests/unit/workflows/00_core_governance_bootstrap_v1/test_core_governance_validation_action.py` | modify | part of repository scan baseline | medium |
| `tests/unit/workflows/00_layer1_governance_bootstrap_v1/test_validation.py` | modify | part of repository scan baseline | medium |
| `tests/unit/workflows/00_master_docs_bootstrap_v2/__init__.py` | modify | part of repository scan baseline | medium |
| `tests/unit/workflows/00_master_docs_bootstrap_v2/test_execution_core.py` | modify | part of repository scan baseline | medium |
| `tests/unit/workflows/00_master_docs_bootstrap_v2/test_master_docs_validation_action.py` | modify | part of repository scan baseline | medium |
| `tests/unit/workflows/02_agent_runner_platform_v1/__init__.py` | modify | part of repository scan baseline | medium |
| `tests/unit/workflows/02_agent_runner_platform_v1/test_platform_core_actions.py` | modify | part of repository scan baseline | medium |
| `tests/unit/workflows/__init__.py` | modify | part of repository scan baseline | medium |
| `WORKFLOW_PLUGIN_INSTALLATION.md` | modify | part of repository scan baseline | medium |
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
| `workflows/02_agent_runner_platform_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/_registry/coder_connections.json` | modify | part of repository scan baseline | medium |
| `workflows/_registry/coder_roles.json` | modify | part of repository scan baseline | medium |
| `workflows/_registry/coder_roles_opencode.json` | modify | part of repository scan baseline | medium |
| `workflows/_registry/coder_roles_qwen.json` | modify | part of repository scan baseline | medium |
| `workflows/_registry/role_policies.json` | modify | part of repository scan baseline | medium |
| `workflows/DEVELOPER_GUIDE.md` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_00_codebase_v1/bundle_governance.toml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_00_codebase_v1/bundle_governance/core_governance.md` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_00_codebase_v1/bundle_governance/generated/AGENTS.md` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_00_codebase_v1/bundle_governance/generated/CLAUDE.md` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_00_codebase_v1/bundle_governance/generated/QWEN.md` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_00_codebase_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_00_delivery_scaffold_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_00_init_doc_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_10_requirement_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_20_planning_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_30_backlog_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_40_task_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_50_implementation_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_60_execution_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_70_validation_v1/workflow.toml` | modify | part of repository scan baseline | medium |
| `workflows/sdlc_80_review_v1/workflow.toml` | modify | part of repository scan baseline | medium |

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
| `codebase_inventory.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/01_inventory/codebase_inventory.md` | module/component/inventory | draft |
| `agent-runner-v2-init.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-init.md` | module/component/inventory | draft |
| `agent-runner-v2-action-result.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-action-result.md` | module/component/inventory | draft |
| `agent-runner-v2-actions-init.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-actions-init.md` | module/component/inventory | draft |
| `agent-runner-v2-actions-copy-artifact.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-actions-copy-artifact.md` | module/component/inventory | draft |
| `agent-runner-v2-actions-documentation-validation-core.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-actions-documentation-validation-core.md` | module/component/inventory | draft |
| `agent-runner-v2-actions-finalize-bootstrap.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-actions-finalize-bootstrap.md` | module/component/inventory | draft |
| `agent-runner-v2-actions-promote-artifact.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-actions-promote-artifact.md` | module/component/inventory | draft |
| `agent-runner-v2-actions-promote-init.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-actions-promote-init.md` | module/component/inventory | draft |
| `agent-runner-v2-actions-scan-repo-codebase.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-actions-scan-repo-codebase.md` | module/component/inventory | draft |
| `agent-runner-v2-actions-sdlc-shared-actions.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-actions-sdlc-shared-actions.md` | module/component/inventory | draft |
| `agent-runner-v2-actions-step-completion.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-actions-step-completion.md` | module/component/inventory | draft |
| `agent-runner-v2-actions-sync-codebase-docs.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-actions-sync-codebase-docs.md` | module/component/inventory | draft |
| `agent-runner-v2-actions-sync-system-docs.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-actions-sync-system-docs.md` | module/component/inventory | draft |
| `agent-runner-v2-actions-validate-codebase-docs.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-actions-validate-codebase-docs.md` | module/component/inventory | draft |
| `agent-runner-v2-actions-validate-system-docs.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-actions-validate-system-docs.md` | module/component/inventory | draft |
| `agent-runner-v2-approve-commands.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-approve-commands.md` | module/component/inventory | draft |
| `agent-runner-v2-artifact-keys.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-artifact-keys.md` | module/component/inventory | draft |
| `agent-runner-v2-artifact-paths.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-artifact-paths.md` | module/component/inventory | draft |
| `agent-runner-v2-backend-client.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-backend-client.md` | module/component/inventory | draft |
| `agent-runner-v2-backend-execution.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-backend-execution.md` | module/component/inventory | draft |
| `agent-runner-v2-bootstrap-workflows-default-00-bootstrap-lifecycle-admin-v1-actions.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-bootstrap-workflows-default-00-bootstrap-lifecycle-admin-v1-actions.md` | module/component/inventory | draft |
| `agent-runner-v2-bootstrap-workflows-default-00-bootstrap-lifecycle-admin-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-bootstrap-workflows-default-00-bootstrap-lifecycle-admin-v1-context-extensions.md` | module/component/inventory | draft |
| `agent-runner-v2-bootstrap-workflows-default-01-governance-foundation-v1-actions.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-bootstrap-workflows-default-01-governance-foundation-v1-actions.md` | module/component/inventory | draft |
| `agent-runner-v2-bootstrap-workflows-default-01-governance-foundation-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-bootstrap-workflows-default-01-governance-foundation-v1-context-extensions.md` | module/component/inventory | draft |
| `agent-runner-v2-bootstrap-workflows-default-01-governance-foundation-v1-output-paths.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-bootstrap-workflows-default-01-governance-foundation-v1-output-paths.md` | module/component/inventory | draft |
| `agent-runner-v2-bootstrap-workflows-default-02-agent-runner-platform-v1-actions.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-bootstrap-workflows-default-02-agent-runner-platform-v1-actions.md` | module/component/inventory | draft |
| `agent-runner-v2-bootstrap-workflows-default-02-agent-runner-platform-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-bootstrap-workflows-default-02-agent-runner-platform-v1-context-extensions.md` | module/component/inventory | draft |
| `agent-runner-v2-bootstrap-workflows-default-02-agent-runner-platform-v1-output-paths.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-bootstrap-workflows-default-02-agent-runner-platform-v1-output-paths.md` | module/component/inventory | draft |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-00-codebase-v1-actions.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-codebase-v1-actions.md` | module/component/inventory | draft |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-00-codebase-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-codebase-v1-context-extensions.md` | module/component/inventory | draft |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-00-delivery-scaffold-v1-actions.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-delivery-scaffold-v1-actions.md` | module/component/inventory | draft |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-00-delivery-scaffold-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-delivery-scaffold-v1-context-extensions.md` | module/component/inventory | draft |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-00-delivery-scaffold-v1-install.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-delivery-scaffold-v1-install.md` | module/component/inventory | draft |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-00-init-doc-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-init-doc-v1-context-extensions.md` | module/component/inventory | draft |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-10-requirement-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-10-requirement-v1-context-extensions.md` | module/component/inventory | draft |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-20-planning-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-20-planning-v1-context-extensions.md` | module/component/inventory | draft |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-30-backlog-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-30-backlog-v1-context-extensions.md` | module/component/inventory | draft |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-40-task-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-40-task-v1-context-extensions.md` | module/component/inventory | draft |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-50-implementation-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-50-implementation-v1-context-extensions.md` | module/component/inventory | draft |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-60-execution-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-60-execution-v1-context-extensions.md` | module/component/inventory | draft |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-70-validation-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-70-validation-v1-context-extensions.md` | module/component/inventory | draft |
| `agent-runner-v2-bootstrap-workflows-default-sdlc-80-review-v1-context-extensions.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-80-review-v1-context-extensions.md` | module/component/inventory | draft |
| `agent-runner-v2-bundle-governance.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-bundle-governance.md` | module/component/inventory | draft |
| `agent-runner-v2-bundle-loader.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-bundle-loader.md` | module/component/inventory | draft |
| `agent-runner-v2-bundle-taxonomy.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-bundle-taxonomy.md` | module/component/inventory | draft |
| `agent-runner-v2-cleanup-generated-docs.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-cleanup-generated-docs.md` | module/component/inventory | draft |
| `agent-runner-v2-cli-runtime.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-cli-runtime.md` | module/component/inventory | draft |
| `agent-runner-v2-codebase-docs.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-codebase-docs.md` | module/component/inventory | draft |
| `agent-runner-v2-codebase-init-commands.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-codebase-init-commands.md` | module/component/inventory | draft |
| `agent-runner-v2-coder-adapters.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-coder-adapters.md` | module/component/inventory | draft |
| `agent-runner-v2-coder-registry.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-coder-registry.md` | module/component/inventory | draft |
| `agent-runner-v2-config-init.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-config-init.md` | module/component/inventory | draft |
| `agent-runner-v2-config-section-requirements.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-config-section-requirements.md` | module/component/inventory | draft |
| `agent-runner-v2-config-loader.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-config-loader.md` | module/component/inventory | draft |
| `agent-runner-v2-console-commands.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-console-commands.md` | module/component/inventory | draft |
| `agent-runner-v2-constants.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-constants.md` | module/component/inventory | draft |
| `agent-runner-v2-constants-legacy-backup-20260717.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-constants-legacy-backup-20260717.md` | module/component/inventory | draft |
| `agent-runner-v2-daemon.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-daemon.md` | module/component/inventory | draft |
| `agent-runner-v2-daemon-runtime.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-daemon-runtime.md` | module/component/inventory | draft |
| `agent-runner-v2-doc-paths.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-doc-paths.md` | module/component/inventory | draft |
| `agent-runner-v2-documentation-guardrails.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-documentation-guardrails.md` | module/component/inventory | draft |
| `agent-runner-v2-engine-commands.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-engine-commands.md` | module/component/inventory | draft |
| `agent-runner-v2-exceptions.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-exceptions.md` | module/component/inventory | draft |
| `agent-runner-v2-execution-core.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-execution-core.md` | module/component/inventory | draft |
| `agent-runner-v2-execution-request.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-execution-request.md` | module/component/inventory | draft |
| `agent-runner-v2-execution-result.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-execution-result.md` | module/component/inventory | draft |
| `agent-runner-v2-execution-support.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-execution-support.md` | module/component/inventory | draft |
| `agent-runner-v2-failure-runtime.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-failure-runtime.md` | module/component/inventory | draft |
| `agent-runner-v2-job-state.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-job-state.md` | module/component/inventory | draft |
| `agent-runner-v2-manual-runtime.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-manual-runtime.md` | module/component/inventory | draft |
| `agent-runner-v2-manual-runtime-deps.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-manual-runtime-deps.md` | module/component/inventory | draft |
| `agent-runner-v2-notification-manager.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-notification-manager.md` | module/component/inventory | draft |
| `agent-runner-v2-notifications.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-notifications.md` | module/component/inventory | draft |
| `agent-runner-v2-operator-console-init.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-operator-console-init.md` | module/component/inventory | draft |
| `agent-runner-v2-operator-console-app.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-operator-console-app.md` | module/component/inventory | draft |
| `agent-runner-v2-operator-console-app1.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-operator-console-app1.md` | module/component/inventory | draft |
| `agent-runner-v2-operator-console-config.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-operator-console-config.md` | module/component/inventory | draft |
| `agent-runner-v2-operator-console-models.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-operator-console-models.md` | module/component/inventory | draft |
| `agent-runner-v2-operator-console-services-init.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-operator-console-services-init.md` | module/component/inventory | draft |
| `agent-runner-v2-operator-console-services-backend-service.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-operator-console-services-backend-service.md` | module/component/inventory | draft |
| `agent-runner-v2-operator-console-services-runner-service.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-operator-console-services-runner-service.md` | module/component/inventory | draft |
| `agent-runner-v2-path-catalog.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-path-catalog.md` | module/component/inventory | draft |
| `agent-runner-v2-path-primitives.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-path-primitives.md` | module/component/inventory | draft |
| `agent-runner-v2-recovery-runtime.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-recovery-runtime.md` | module/component/inventory | draft |
| `agent-runner-v2-routing-runtime.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-routing-runtime.md` | module/component/inventory | draft |
| `agent-runner-v2-run-agent.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-run-agent.md` | module/component/inventory | draft |
| `agent-runner-v2-runner-actions.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-runner-actions.md` | module/component/inventory | draft |
| `agent-runner-v2-runner-logger.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-runner-logger.md` | module/component/inventory | draft |
| `agent-runner-v2-runtime-context.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-runtime-context.md` | module/component/inventory | draft |
| `agent-runner-v2-runtime-utils.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-runtime-utils.md` | module/component/inventory | draft |
| `agent-runner-v2-shared-runtime-deps.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-shared-runtime-deps.md` | module/component/inventory | draft |
| `agent-runner-v2-site-styles.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-site-styles.md` | module/component/inventory | draft |
| `agent-runner-v2-state-defaults.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-state-defaults.md` | module/component/inventory | draft |
| `agent-runner-v2-step-execution-runtime.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-step-execution-runtime.md` | module/component/inventory | draft |
| `agent-runner-v2-step-runner.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-step-runner.md` | module/component/inventory | draft |
| `agent-runner-v2-stop-commands.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-stop-commands.md` | module/component/inventory | draft |
| `agent-runner-v2-submit-commands.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-submit-commands.md` | module/component/inventory | draft |
| `agent-runner-v2-submitter.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-submitter.md` | module/component/inventory | draft |
| `agent-runner-v2-sync-workflows.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-sync-workflows.md` | module/component/inventory | draft |
| `agent-runner-v2-system-docs.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-system-docs.md` | module/component/inventory | draft |
| `agent-runner-v2-task-runtime.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-task-runtime.md` | module/component/inventory | draft |
| `agent-runner-v2-tools-agent-tools.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-tools-agent-tools.md` | module/component/inventory | draft |
| `agent-runner-v2-transition-runtime.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-transition-runtime.md` | module/component/inventory | draft |
| `agent-runner-v2-workflow-bundle-validate-commands.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-workflow-bundle-validate-commands.md` | module/component/inventory | draft |
| `agent-runner-v2-workflow-bundle-validator.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-workflow-bundle-validator.md` | module/component/inventory | draft |
| `agent-runner-v2-workflow-packages-init.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-workflow-packages-init.md` | module/component/inventory | draft |
| `agent-runner-v2-workflow-packages-actions-init.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-workflow-packages-actions-init.md` | module/component/inventory | draft |
| `agent-runner-v2-workflow-packages-base.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-workflow-packages-base.md` | module/component/inventory | draft |
| `agent-runner-v2-workflow-packages-extensions-base.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-workflow-packages-extensions-base.md` | module/component/inventory | draft |
| `agent-runner-v2-workflow-packages-hooks.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-workflow-packages-hooks.md` | module/component/inventory | draft |
| `agent-runner-v2-workflow-packages-loader.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-workflow-packages-loader.md` | module/component/inventory | draft |
| `agent-runner-v2-workflow-packages-registry.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-workflow-packages-registry.md` | module/component/inventory | draft |
| `agent-runner-v2-workflow-path-contracts.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-workflow-path-contracts.md` | module/component/inventory | draft |
| `agent-runner-v2-workflow-router.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-workflow-router.md` | module/component/inventory | draft |
| `agent-runner-v2-workflow-runtime.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-workflow-runtime.md` | module/component/inventory | draft |
| `agent-runner-v2-workflow-spec-commands.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-workflow-spec-commands.md` | module/component/inventory | draft |
| `agent-runner-v2-workflow-specs.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-workflow-specs.md` | module/component/inventory | draft |
| `workflow-families.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/03_components/workflow-families.md` | module/component/inventory | draft |
| `actions-package.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/03_components/actions-package.md` | module/component/inventory | draft |
| `tests-suite.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/03_components/tests-suite.md` | module/component/inventory | draft |
| `scripts-suite.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/03_components/scripts-suite.md` | module/component/inventory | draft |
| `config-and-data.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/03_components/config-and-data.md` | module/component/inventory | draft |
| `codebase-governance.md` | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/03_components/codebase-governance.md` | module/component/inventory | draft |

### 3.2 Documentation Updated

| Document | Path | Section Updated | Reason |
|----------|------|-----------------|--------|

### 3.3 Inventory Updates

| Module | Previous Status | New Status | Owner Doc Path |
|--------|----------------|------------|----------------|
| `codebase_inventory.md` | undocumented | current | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/01_inventory/codebase_inventory.md` |
| `agent-runner-v2-init.md` | undocumented | current | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-init.md` |
| `agent-runner-v2-action-result.md` | undocumented | current | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-action-result.md` |
| `agent-runner-v2-actions-init.md` | undocumented | current | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-actions-init.md` |
| `agent-runner-v2-actions-copy-artifact.md` | undocumented | current | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-actions-copy-artifact.md` |
| `agent-runner-v2-actions-documentation-validation-core.md` | undocumented | current | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-actions-documentation-validation-core.md` |
| `agent-runner-v2-actions-finalize-bootstrap.md` | undocumented | current | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-actions-finalize-bootstrap.md` |
| `agent-runner-v2-actions-promote-artifact.md` | undocumented | current | `docs/repo/codebase/runs/SDLC00CB-20260723-c66bc6aa/02_modules/agent-runner-v2-actions-promote-artifact.md` |

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
| `sdlc_00_codebase_v1` | high | repository scan baseline |

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
