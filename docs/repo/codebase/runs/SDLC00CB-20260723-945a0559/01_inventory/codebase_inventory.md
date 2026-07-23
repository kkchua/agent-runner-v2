---
title: "Codebase Inventory - agent-runner-v2"
template_id: "CODEBASE-INV-v1"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
generated: "2026-07-23T19:30:10+08:00"
workflow: "sdlc_00_codebase_v1"
step: "sync_codebase_docs"
change_id: "SDLC00CB-20260723-945a0559"
---

# Codebase Inventory: agent-runner-v2

## 1. Inventory Scope

This inventory was generated from a repository scan at `2026-07-23T19:30:10+08:00`.

## 2. Python Source Modules

| File Path | Module Area | Documentation Mode | Status | Owner Doc Path | Last Verified By Change |
|---|---|---|---|---|---|
| agent_runner_v2/__init__.py | package | stub | current | docs/repo/codebase/current/02_modules/agent-runner-v2-init.md | bootstrap/reconcile scan |
| agent_runner_v2/action_result.py | schema | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-action-result.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/__init__.py | actions | stub | current | docs/repo/codebase/current/02_modules/agent-runner-v2-actions-init.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/copy_artifact.py | actions | full | current | docs/repo/codebase/current/02_modules/agent-runner-v2-actions-copy-artifact.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/documentation_validation_core.py | actions | full | current | docs/repo/codebase/current/02_modules/agent-runner-v2-actions-documentation-validation-core.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/finalize_bootstrap.py | actions | full | current | docs/repo/codebase/current/02_modules/agent-runner-v2-actions-finalize-bootstrap.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/promote_artifact.py | actions | full | current | docs/repo/codebase/current/02_modules/agent-runner-v2-actions-promote-artifact.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/promote_init.py | actions | full | current | docs/repo/codebase/current/02_modules/agent-runner-v2-actions-promote-init.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/scan_repo_codebase.py | actions | full | current | docs/repo/codebase/current/02_modules/agent-runner-v2-actions-scan-repo-codebase.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/sdlc_shared_actions.py | actions | full | current | docs/repo/codebase/current/02_modules/agent-runner-v2-actions-sdlc-shared-actions.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/step_completion.py | actions | full | current | docs/repo/codebase/current/02_modules/agent-runner-v2-actions-step-completion.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/sync_codebase_docs.py | actions | full | current | docs/repo/codebase/current/02_modules/agent-runner-v2-actions-sync-codebase-docs.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/sync_system_docs.py | actions | full | current | docs/repo/codebase/current/02_modules/agent-runner-v2-actions-sync-system-docs.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/validate_codebase_docs.py | actions | full | current | docs/repo/codebase/current/02_modules/agent-runner-v2-actions-validate-codebase-docs.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/validate_system_docs.py | actions | full | current | docs/repo/codebase/current/02_modules/agent-runner-v2-actions-validate-system-docs.md | bootstrap/reconcile scan |
| agent_runner_v2/approve_commands.py | commands | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-approve-commands.md | bootstrap/reconcile scan |
| agent_runner_v2/artifact_keys.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-artifact-keys.md | bootstrap/reconcile scan |
| agent_runner_v2/artifact_paths.py | schema | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-artifact-paths.md | bootstrap/reconcile scan |
| agent_runner_v2/backend_client.py | backend | full | current | docs/repo/codebase/current/02_modules/agent-runner-v2-backend-client.md | bootstrap/reconcile scan |
| agent_runner_v2/backend_execution.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-backend-execution.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_bootstrap_lifecycle_admin_v1/actions.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-00-bootstrap-lifecycle-admin-v1-actions.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_bootstrap_lifecycle_admin_v1/context_extensions.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-00-bootstrap-lifecycle-admin-v1-context-extensions.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/actions.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-01-governance-foundation-v1-actions.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/context_extensions.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-01-governance-foundation-v1-context-extensions.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/output_paths.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-01-governance-foundation-v1-output-paths.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/actions.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-02-agent-runner-platform-v1-actions.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/context_extensions.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-02-agent-runner-platform-v1-context-extensions.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/output_paths.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-02-agent-runner-platform-v1-output-paths.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_v1/actions.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-codebase-v1-actions.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_v1/context_extensions.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-codebase-v1-context-extensions.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_00_delivery_scaffold_v1/actions.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-delivery-scaffold-v1-actions.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_00_delivery_scaffold_v1/context_extensions.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-delivery-scaffold-v1-context-extensions.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_00_delivery_scaffold_v1/install.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-delivery-scaffold-v1-install.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_00_init_doc_v1/context_extensions.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-00-init-doc-v1-context-extensions.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_10_requirement_v1/context_extensions.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-10-requirement-v1-context-extensions.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_20_planning_v1/context_extensions.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-20-planning-v1-context-extensions.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_30_backlog_v1/context_extensions.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-30-backlog-v1-context-extensions.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_40_task_v1/context_extensions.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-40-task-v1-context-extensions.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_50_implementation_v1/context_extensions.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-50-implementation-v1-context-extensions.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_60_execution_v1/context_extensions.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-60-execution-v1-context-extensions.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_70_validation_v1/context_extensions.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-70-validation-v1-context-extensions.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_80_review_v1/context_extensions.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-bootstrap-workflows-default-sdlc-80-review-v1-context-extensions.md | bootstrap/reconcile scan |
| agent_runner_v2/bundle_governance.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-bundle-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bundle_loader.py | bootstrap | full | current | docs/repo/codebase/current/02_modules/agent-runner-v2-bundle-loader.md | bootstrap/reconcile scan |
| agent_runner_v2/bundle_taxonomy.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-bundle-taxonomy.md | bootstrap/reconcile scan |
| agent_runner_v2/cleanup_generated_docs.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-cleanup-generated-docs.md | bootstrap/reconcile scan |
| agent_runner_v2/cli_runtime.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-cli-runtime.md | bootstrap/reconcile scan |
| agent_runner_v2/codebase_docs.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-codebase-docs.md | bootstrap/reconcile scan |
| agent_runner_v2/codebase_init_commands.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-codebase-init-commands.md | bootstrap/reconcile scan |
| agent_runner_v2/coder_adapters.py | coder | full | current | docs/repo/codebase/current/02_modules/agent-runner-v2-coder-adapters.md | bootstrap/reconcile scan |
| agent_runner_v2/coder_registry.py | coder | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-coder-registry.md | bootstrap/reconcile scan |
| agent_runner_v2/config/__init__.py | package | stub | current | docs/repo/codebase/current/02_modules/agent-runner-v2-config-init.md | bootstrap/reconcile scan |
| agent_runner_v2/config/section_requirements.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-config-section-requirements.md | bootstrap/reconcile scan |
| agent_runner_v2/config_loader.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-config-loader.md | bootstrap/reconcile scan |
| agent_runner_v2/console_commands.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-console-commands.md | bootstrap/reconcile scan |
| agent_runner_v2/constants.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-constants.md | bootstrap/reconcile scan |
| agent_runner_v2/constants_legacy_backup_20260717.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-constants-legacy-backup-20260717.md | bootstrap/reconcile scan |
| agent_runner_v2/daemon.py | backend | full | current | docs/repo/codebase/current/02_modules/agent-runner-v2-daemon.md | bootstrap/reconcile scan |
| agent_runner_v2/daemon_runtime.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-daemon-runtime.md | bootstrap/reconcile scan |
| agent_runner_v2/doc_paths.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-doc-paths.md | bootstrap/reconcile scan |
| agent_runner_v2/documentation_guardrails.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-documentation-guardrails.md | bootstrap/reconcile scan |
| agent_runner_v2/engine_commands.py | commands | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-engine-commands.md | bootstrap/reconcile scan |
| agent_runner_v2/exceptions.py | schema | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-exceptions.md | bootstrap/reconcile scan |
| agent_runner_v2/execution_core.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-execution-core.md | bootstrap/reconcile scan |
| agent_runner_v2/execution_request.py | state | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-execution-request.md | bootstrap/reconcile scan |
| agent_runner_v2/execution_result.py | state | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-execution-result.md | bootstrap/reconcile scan |
| agent_runner_v2/execution_support.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-execution-support.md | bootstrap/reconcile scan |
| agent_runner_v2/failure_runtime.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-failure-runtime.md | bootstrap/reconcile scan |
| agent_runner_v2/job_state.py | state | full | current | docs/repo/codebase/current/02_modules/agent-runner-v2-job-state.md | bootstrap/reconcile scan |
| agent_runner_v2/manual_runtime.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-manual-runtime.md | bootstrap/reconcile scan |
| agent_runner_v2/manual_runtime_deps.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-manual-runtime-deps.md | bootstrap/reconcile scan |
| agent_runner_v2/notification_manager.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-notification-manager.md | bootstrap/reconcile scan |
| agent_runner_v2/notifications.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-notifications.md | bootstrap/reconcile scan |
| agent_runner_v2/operator_console/__init__.py | package | stub | current | docs/repo/codebase/current/02_modules/agent-runner-v2-operator-console-init.md | bootstrap/reconcile scan |
| agent_runner_v2/operator_console/app.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-operator-console-app.md | bootstrap/reconcile scan |
| agent_runner_v2/operator_console/app1.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-operator-console-app1.md | bootstrap/reconcile scan |
| agent_runner_v2/operator_console/config.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-operator-console-config.md | bootstrap/reconcile scan |
| agent_runner_v2/operator_console/models.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-operator-console-models.md | bootstrap/reconcile scan |
| agent_runner_v2/operator_console/services/__init__.py | package | stub | current | docs/repo/codebase/current/02_modules/agent-runner-v2-operator-console-services-init.md | bootstrap/reconcile scan |
| agent_runner_v2/operator_console/services/backend_service.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-operator-console-services-backend-service.md | bootstrap/reconcile scan |
| agent_runner_v2/operator_console/services/runner_service.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-operator-console-services-runner-service.md | bootstrap/reconcile scan |
| agent_runner_v2/path_catalog.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-path-catalog.md | bootstrap/reconcile scan |
| agent_runner_v2/path_primitives.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-path-primitives.md | bootstrap/reconcile scan |
| agent_runner_v2/recovery_runtime.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-recovery-runtime.md | bootstrap/reconcile scan |
| agent_runner_v2/routing_runtime.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-routing-runtime.md | bootstrap/reconcile scan |
| agent_runner_v2/run_agent.py | core | full | current | docs/repo/codebase/current/02_modules/agent-runner-v2-run-agent.md | bootstrap/reconcile scan |
| agent_runner_v2/runner_actions.py | schema | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-runner-actions.md | bootstrap/reconcile scan |
| agent_runner_v2/runner_logger.py | backend | full | current | docs/repo/codebase/current/02_modules/agent-runner-v2-runner-logger.md | bootstrap/reconcile scan |
| agent_runner_v2/runtime_context.py | state | full | current | docs/repo/codebase/current/02_modules/agent-runner-v2-runtime-context.md | bootstrap/reconcile scan |
| agent_runner_v2/runtime_utils.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-runtime-utils.md | bootstrap/reconcile scan |
| agent_runner_v2/shared_runtime_deps.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-shared-runtime-deps.md | bootstrap/reconcile scan |
| agent_runner_v2/site_styles.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-site-styles.md | bootstrap/reconcile scan |
| agent_runner_v2/state_defaults.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-state-defaults.md | bootstrap/reconcile scan |
| agent_runner_v2/step_execution_runtime.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-step-execution-runtime.md | bootstrap/reconcile scan |
| agent_runner_v2/step_runner.py | core | full | current | docs/repo/codebase/current/02_modules/agent-runner-v2-step-runner.md | bootstrap/reconcile scan |
| agent_runner_v2/stop_commands.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-stop-commands.md | bootstrap/reconcile scan |
| agent_runner_v2/submit_commands.py | commands | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-submit-commands.md | bootstrap/reconcile scan |
| agent_runner_v2/submitter.py | commands | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-submitter.md | bootstrap/reconcile scan |
| agent_runner_v2/sync_workflows.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-sync-workflows.md | bootstrap/reconcile scan |
| agent_runner_v2/system_docs.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-system-docs.md | bootstrap/reconcile scan |
| agent_runner_v2/task_runtime.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-task-runtime.md | bootstrap/reconcile scan |
| agent_runner_v2/tools/agent_tools.py | tools | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-tools-agent-tools.md | bootstrap/reconcile scan |
| agent_runner_v2/transition_runtime.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-transition-runtime.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_bundle_validate_commands.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-bundle-validate-commands.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_bundle_validator.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-bundle-validator.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_packages/__init__.py | package | stub | current | docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-packages-init.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_packages/actions/__init__.py | package | stub | current | docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-packages-actions-init.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_packages/base.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-packages-base.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_packages/extensions_base.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-packages-extensions-base.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_packages/hooks.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-packages-hooks.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_packages/loader.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-packages-loader.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_packages/registry.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-packages-registry.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_path_contracts.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-path-contracts.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_router.py | core | full | current | docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-router.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_runtime.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-runtime.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_spec_commands.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-spec-commands.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_specs.py | support | summary | current | docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-specs.md | bootstrap/reconcile scan |

## 3. Bootstrap Workflow Files

| File Path | Description | Documentation Mode | Status | Owner Doc Path | Last Verified By Change |
|---|---|---|---|---|---|
| agent_runner_v2/bootstrap/workflows/default/00_bootstrap_lifecycle_admin_v1/workflow.toml | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/bundle_governance.toml | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/bundle_governance/action_policy.md | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/bundle_governance/core_governance.md | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/bundle_governance/generated/AGENTS.md | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/bundle_governance/generated/CLAUDE.md | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/bundle_governance/generated/QWEN.md | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/bundle_governance/prompt_contract.json | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/bundle_governance/prompt_layout.md | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/bundle_governance/prompt_sop.md | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/bundle_governance/review_audit_contract.md | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/prompts/01_generate_governance_foundation_docs.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/prompts/02_review_governance_foundation_docs.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/prompts/03_refine_governance_foundation_docs.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/prompts/04_audit_governance_foundation_docs.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/01_governance_foundation_v1/workflow.toml | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/bundle_governance.toml | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/bundle_governance/action_policy.md | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/bundle_governance/core_governance.md | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/bundle_governance/generated/AGENTS.md | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/bundle_governance/generated/CLAUDE.md | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/bundle_governance/generated/QWEN.md | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/bundle_governance/prompt_contract.json | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/bundle_governance/prompt_layout.md | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/bundle_governance/prompt_sop.md | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/bundle_governance/review_audit_contract.md | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/prompts/01_generate_platform_core_docs.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/prompts/02_review_platform_core_docs.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/prompts/03_refine_platform_core_docs.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/prompts/04_audit_platform_core_docs.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/02_agent_runner_platform_v1/workflow.toml | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/_registry/coder_connections.json | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/_registry/coder_roles.json | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/_registry/coder_roles_opencode.json | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/_registry/coder_roles_qwen.json | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/_registry/role_policies.json | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_v1/bundle_governance.toml | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_v1/bundle_governance/core_governance.md | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_v1/bundle_governance/generated/AGENTS.md | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_v1/bundle_governance/generated/CLAUDE.md | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_v1/bundle_governance/generated/QWEN.md | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_v1/prompts/04_review_sync_log.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_v1/prompts/05_refine_codebase_docs.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_00_codebase_v1/workflow.toml | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_00_delivery_scaffold_v1/prompts/01_generate_templates.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_00_delivery_scaffold_v1/prompts/02_generate_agent_contracts.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_00_delivery_scaffold_v1/prompts/03_review_scaffold.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_00_delivery_scaffold_v1/prompts/04_refine_scaffold.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_00_delivery_scaffold_v1/workflow.toml | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_00_init_doc_v1/prompts/01_generate_initiative.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_00_init_doc_v1/prompts/02_technical_critique.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_00_init_doc_v1/prompts/03_review_initiative.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_00_init_doc_v1/prompts/04_refine_initiative.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_00_init_doc_v1/workflow.toml | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_10_requirement_v1/prompts/01_generate_requirements.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_10_requirement_v1/prompts/02_technical_critique.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_10_requirement_v1/prompts/03_review_requirements.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_10_requirement_v1/prompts/04_refine_requirements.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_10_requirement_v1/workflow.toml | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_20_planning_v1/prompts/01_generate_plan.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_20_planning_v1/prompts/02_technical_critique.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_20_planning_v1/prompts/03_review_plan.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_20_planning_v1/prompts/04_refine_plan.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_20_planning_v1/workflow.toml | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_30_backlog_v1/prompts/01_generate_backlog.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_30_backlog_v1/prompts/02_technical_critique.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_30_backlog_v1/prompts/03_review_backlog.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_30_backlog_v1/prompts/04_refine_backlog.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_30_backlog_v1/workflow.toml | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_40_task_v1/prompts/01_generate_task.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_40_task_v1/prompts/02_technical_critique.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_40_task_v1/prompts/03_review_task.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_40_task_v1/prompts/04_refine_task.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_40_task_v1/workflow.toml | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_50_implementation_v1/prompts/01_generate_implementation.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_50_implementation_v1/prompts/02_technical_critique.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_50_implementation_v1/prompts/03_review_implementation.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_50_implementation_v1/prompts/04_refine_implementation.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_50_implementation_v1/workflow.toml | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_60_execution_v1/prompts/01_execute_task.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_60_execution_v1/prompts/02_technical_critique.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_60_execution_v1/prompts/03_internal_review.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_60_execution_v1/prompts/04_refine_execution.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_60_execution_v1/workflow.toml | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_70_validation_v1/prompts/01_generate_validation.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_70_validation_v1/prompts/02_technical_critique.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_70_validation_v1/prompts/03_review_validation.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_70_validation_v1/prompts/04_refine_validation.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_70_validation_v1/workflow.toml | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_80_review_v1/prompts/01_generate_review.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_80_review_v1/prompts/02_technical_critique.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_80_review_v1/prompts/03_review_all.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_80_review_v1/prompts/04_refine_documents.txt | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/sdlc_80_review_v1/workflow.toml | workflow asset | full | current | docs/repo/codebase/current/03_components/workflow-families.md | bootstrap/reconcile scan |

## 4. Configuration / Data Files

| File Path | Format | Documentation Mode | Status | Owner Doc Path | Last Verified By Change |
|---|---|---|---|---|---|
| .env.example | example | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| _test_payload.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/bootstrap_publish_manifest.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/repo/agent_runner/sdlc/delivery/00_initiatives/INIT-20260723-001_console-sdlc10-support.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/repo/agent_runner/sdlc/delivery/10_requirements/REQ-20260723-001_console-sdlc10-support.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/repo/agent_runner/sdlc/delivery/20_plans/PLAN-20260723-001_console-sdlc10-support.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/repo/agent_runner/sdlc/delivery/30_backlogs/BACKLOG-20260723-001_console-sdlc10-support.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/repo/agent_runner/sdlc/delivery/40_tasks/WI-20260723-001_console-sdlc10-support-01.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/repo/agent_runner/sdlc/delivery/40_tasks/WI-20260723-001_console-sdlc10-support-02.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/repo/agent_runner/sdlc/delivery/50_implementations/IMPL-20260723-001-001_console-sdlc10-support-01.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/00_bootstrap_lifecycle_admin_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/bundle_governance.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/bundle_governance/prompt_contract.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/bundle_governance.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/bundle_governance/prompt_contract.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/_registry/coder_connections.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/_registry/coder_roles.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/_registry/coder_roles_opencode.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/_registry/coder_roles_qwen.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/_registry/role_policies.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_00_codebase_v1/bundle_governance.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_00_codebase_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_00_delivery_scaffold_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_00_init_doc_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_10_requirement_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_20_planning_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_30_backlog_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_40_task_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_50_implementation_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_60_execution_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_70_validation_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_80_review_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/current/governance_set_manifest.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-0864b1f2/governance_set_manifest.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-4e51c88b/governance_set_manifest.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-61ae0105/governance_set_manifest.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-96e730ab/governance_set_manifest.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-c5e882c3/governance_set_manifest.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-f15f153c/governance_set_manifest.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/01GF-20260719-0864b1f2-governance-foundation-audit.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/01GF-20260719-0864b1f2-governance-foundation-review.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/01GF-20260719-4e51c88b-governance-foundation-audit.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/01GF-20260719-4e51c88b-governance-foundation-review.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/01GF-20260719-61ae0105-governance-foundation-audit.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/01GF-20260719-61ae0105-governance-foundation-review.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/01GF-20260719-96e730ab-governance-foundation-audit.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/01GF-20260719-96e730ab-governance-foundation-review.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/01GF-20260719-c5e882c3-governance-foundation-audit.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/01GF-20260719-c5e882c3-governance-foundation-review.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/README.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/01GF-20260719-f15f153c-governance-foundation-audit.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/01GF-20260719-f15f153c-governance-foundation-review.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/current/platform_set_manifest.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/history/02AR-20260721-2eaba4b3/platform_set_manifest.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/history/02PC-20260721-b092c705/platform_set_manifest.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/history/02PC-GEN-20260721-009/platform_set_manifest.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/02PC-20260721-b092c705-platform-core-audit.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/02PC-20260721-b092c705-platform-core-review.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/README.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/02PC-GEN-20260721-009-platform-core-audit.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/02PC-GEN-20260721-009-platform-core-review.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/current/sdlc_scaffold_manifest.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/sdlc_scaffold_manifest.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/template_registry.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/AGENTS.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/SDLC00SCF-20260722-914943f4-sdlc-scaffold-review.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/template_registry.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/AGENTS.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/SDLC00SCF-20260722-cc2b347d-sdlc-scaffold-review.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/template_registry.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/AGENTS.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| masterplan/00_repo_master_docs_bootstrap_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| masterplan/delivery/03_tasks/TASK-20260418-01_contract-build-api-trigger.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| masterplan/delivery/03_tasks/TASK-20260418-02_managed-generation-api-trigger.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| masterplan/delivery/03_tasks/TASK-20260418-03_generation-run-api-surface.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| masterplan/delivery/03_tasks/TASK-20260418-04_artifact-lifecycle-retrieval.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| masterplan/delivery/03_tasks/TASK-20260418-05_router-registration-documentation.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| masterplan/delivery/04_implementation_plans/IMPL-20260418-01_contract-build-api-trigger.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| masterplan/delivery/04_implementation_plans/IMPL-20260418-02_managed-generation-api-trigger.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| masterplan/delivery/04_implementation_plans/IMPL-20260418-03_generation-run-api-surface.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| masterplan/delivery/05_reviews/REV-260418-01_rtask_T-0418-01_contract-build-api-trigger.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| masterplan/delivery/05_reviews/REV-260418-02_rimpl_M-0418-01_contract-build-api-trigger.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| masterplan/delivery/05_reviews/REV-260418-03_rtask_T-0418-02_managed-generation-api-trigger.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| masterplan/delivery/05_reviews/REV-260418-04_rtask_T-0418-02_managed-generation-api-trigger.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| masterplan/delivery/05_reviews/REV-260418-05_rimpl_M-0418-02_managed-generation-api-trigger.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| masterplan/delivery/05_reviews/VALIDATION-260418-2-M-0418-01_contract-build-api-trigger.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| masterplan/delivery/05_reviews/VALIDATION-260418-2-M-0418-02_managed-generation-api-trigger.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| masterplan/delivery/05_reviews/VALIDATION-260418-3-M-0418-02_managed-generation-api-trigger.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| masterplan/delivery/05_reviews/VALIDATION-260418-M-0418-01_contract-build-api-trigger.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| masterplan/delivery/05_reviews/VALIDATION-260418-M-0418-02_managed-generation-api-trigger.meta.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/comfyui_config.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/job_schema.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/llm_response_schema.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/model_mapping.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/usage_schema.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| opencode.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| operator-console.example.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| platform_context_manifest.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| pyproject.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/00_bootstrap_lifecycle_admin_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/01_governance_foundation_v1/bundle_governance.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/01_governance_foundation_v1/bundle_governance/prompt_contract.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/01_governance_foundation_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/02_agent_runner_platform_v1/bundle_governance.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/02_agent_runner_platform_v1/bundle_governance/prompt_contract.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/02_agent_runner_platform_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/_registry/coder_connections.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/_registry/coder_roles.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/_registry/coder_roles_opencode.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/_registry/coder_roles_qwen.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/_registry/role_policies.json | json | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/sdlc_00_codebase_v1/bundle_governance.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/sdlc_00_codebase_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/sdlc_00_delivery_scaffold_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/sdlc_00_init_doc_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/sdlc_10_requirement_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/sdlc_20_planning_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/sdlc_30_backlog_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/sdlc_40_task_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/sdlc_50_implementation_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/sdlc_60_execution_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/sdlc_70_validation_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/sdlc_80_review_v1/workflow.toml | toml | summary | current | docs/repo/codebase/current/03_components/config-and-data.md | bootstrap/reconcile scan |

## 5. Scripts

| File Path | Type | Documentation Mode | Status | Owner Doc Path | Last Verified By Change |
|---|---|---|---|---|---|
| run-00_bootstrap_lifecycle_admin_v1.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-00_bootstrap_lifecycle_admin_v1.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-01_governance_foundation_v1.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-01_governance_foundation_v1.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-02_agent_runner_platform_v1.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-02_agent_runner_platform_v1.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-approve-step.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-approve-step.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-bootstrap-publish.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-bootstrap-publish.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-cleanup-workflow.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-cleanup-workflow.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-console.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-console.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-daemon.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-daemon.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-init.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-init.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-reset-step.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-reset-step.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-sdlc_00_codebase_v1.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-sdlc_00_codebase_v1.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-sdlc_00_delivery_scaffold_v1.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-sdlc_00_delivery_scaffold_v1.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-sdlc_00_init_doc_v1.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-sdlc_00_init_doc_v1.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-sdlc_10_requirement_v1.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-sdlc_10_requirement_v1.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-sdlc_20_planning_v1.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-sdlc_20_planning_v1.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-sdlc_30_backlog_v1.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-sdlc_30_backlog_v1.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-sdlc_40_task_v1.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-sdlc_40_task_v1.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-sdlc_50_implementation_v1.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-sdlc_50_implementation_v1.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-sdlc_60_execution_v1.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-sdlc_60_execution_v1.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-sdlc_70_validation_v1.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-sdlc_70_validation_v1.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-sdlc_80_review_v1.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-sdlc_80_review_v1.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-00_bootstrap_lifecycle_admin_v1.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-00_bootstrap_lifecycle_admin_v1.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-01_governance_foundation_v1.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-01_governance_foundation_v1.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-02_agent_runner_platform_v1.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-02_agent_runner_platform_v1.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-sdlc_00_codebase_v1.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-sdlc_00_codebase_v1.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-sdlc_00_init_doc_v1.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-sdlc_00_init_doc_v1.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-sdlc_10_requirement_v1.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-sdlc_10_requirement_v1.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-sdlc_20_planning_v1.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-sdlc_20_planning_v1.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-sdlc_30_backlog_v1.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-sdlc_30_backlog_v1.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-sdlc_40_task_v1.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-sdlc_40_task_v1.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-sdlc_50_implementation_v1.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-sdlc_50_implementation_v1.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-sdlc_60_execution_v1.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-sdlc_60_execution_v1.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-sdlc_70_validation_v1.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-sdlc_70_validation_v1.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-sdlc_80_review_v1.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-sdlc_80_review_v1.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| sync-workflows-to-backend.bat | .bat | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |
| sync-workflows-to-backend.sh | .sh | summary | current | docs/repo/codebase/current/03_components/scripts-suite.md | bootstrap/reconcile scan |

## 6. Test Files

| File Path | Coverage Area | Documentation Mode | Status | Owner Doc Path | Last Verified By Change |
|---|---|---|---|---|---|
| tests/conftest.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/integration/__init__.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/integration/test_architecture_site.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/integration/test_backend_worker_mode.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/integration/test_daemon.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/integration/test_notification_e2e.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/integration/test_notification_integration.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/integration/test_notifications.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/integration/test_pushover.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/integration/test_ukbe_runner_wrapper.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/run_workflow_unit_tests.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/__init__.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_agent_tools.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_backend_execution.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_bundle_loader.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_codebase_docs.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_codebase_init_commands.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_coder_adapters_opencode.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_coder_adapters_sidecar_grace.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_constants_registry.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_context_extensions.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_daemon_runtime.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_daemon_worker_payload.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_documentation_governance.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_documentation_guardrails_cleanup.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_execution_core.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_failure_runtime.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_generated_doc_frontmatter_injection.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_job_state_review_completion.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_job_state_step_dirs.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_job_state_usage_summary.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_machine_contracts.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_manual_runtime.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_model_config_roles.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_notification_manager.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_operator_console_config.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_operator_console_services.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_plugin_workflow_support.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_promote_artifact.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_recovery_runtime.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_routing_runtime.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_run_agent_hook_surface.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_run_agent_legacy_cli.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_run_agent_status.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_runtime_context_paths.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_runtime_utils.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_sdlc_shared_actions.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_state_defaults.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_step_completion.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_step_runner_write_contract.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_stop_commands.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_submit_commands.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_sync_workflows.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_task_runtime.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_tool_instruction_block.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_transition_recovery_runtime.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_transition_runtime.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_workflow_bundle_validator.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_workflow_packages.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_workflow_registry.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_workflow_router_notifications.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_workflow_specs.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/workflows/00_bootstrap_lifecycle_admin_v1/test_actions.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/workflows/00_core_governance_bootstrap_v1/__init__.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/workflows/00_core_governance_bootstrap_v1/test_core_governance_validation_action.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/workflows/00_layer1_governance_bootstrap_v1/test_validation.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/workflows/00_master_docs_bootstrap_v2/__init__.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/workflows/00_master_docs_bootstrap_v2/test_execution_core.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/workflows/00_master_docs_bootstrap_v2/test_master_docs_validation_action.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/workflows/02_agent_runner_platform_v1/__init__.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/workflows/02_agent_runner_platform_v1/test_platform_core_actions.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/workflows/__init__.py | tests | summary | current | docs/repo/codebase/current/03_components/tests-suite.md | bootstrap/reconcile scan |

## 7. Documentation Files

| File Path | Category | Documentation Mode | Status | Owner Doc Path | Last Verified By Change |
|---|---|---|---|---|---|
| agent_runner_v2/bootstrap/bundles/core/current/00BOOT-20260719-5ceb9505-bootstrap-lifecycle-summary.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/00BOOT-20260720-5d679fd5-bootstrap-lifecycle-summary.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/00BOOT-20260720-818a452f-bootstrap-lifecycle-summary.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/00BOOT-20260720-f7113f08-bootstrap-lifecycle-summary.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/00BOOT-20260721-2af1fe38-bootstrap-lifecycle-summary.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/00BOOT-20260721-86fb57bb-bootstrap-lifecycle-summary.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/00BOOT-20260722-2dcbbdfe-bootstrap-lifecycle-summary.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/00BOOT-20260722-9877c2ee-bootstrap-lifecycle-summary.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| AGENT_RUNNER_V2_SPECIALIST.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| CLAUDE.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| CODER_IMPLEMENTATION_SOP.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/repo/agent_runner/sdlc/delivery/00_draft_initiatives/DRAFT-INIT-20260722-001_console-sdlc10-support.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/repo/agent_runner/sdlc/delivery/00_initiatives/INIT-20260723-001_console-sdlc10-support.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/repo/agent_runner/sdlc/delivery/10_requirements/REQ-20260723-001_console-sdlc10-support.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/repo/agent_runner/sdlc/delivery/20_plans/PLAN-20260723-001_console-sdlc10-support.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/repo/agent_runner/sdlc/delivery/30_backlogs/BACKLOG-20260723-001_console-sdlc10-support.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/repo/agent_runner/sdlc/delivery/40_tasks/WI-20260723-001_console-sdlc10-support-01.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/repo/agent_runner/sdlc/delivery/40_tasks/WI-20260723-001_console-sdlc10-support-02.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/repo/agent_runner/sdlc/delivery/50_implementations/IMPL-20260723-001-001_console-sdlc10-support-01.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/repo/agent_runner/sdlc/delivery/60_executions/EXEC-20260723-001-001_console-sdlc10-support-01.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/repo/agent_runner/sdlc/delivery/80_reviews/console-sdlc10-support-01-REV-50-impl.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/repo/agent_runner/sdlc/delivery/80_reviews/console-sdlc10-support-REV-00-init.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/repo/agent_runner/sdlc/delivery/80_reviews/console-sdlc10-support-REV-10-req.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/repo/agent_runner/sdlc/delivery/80_reviews/console-sdlc10-support-REV-20-plan.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/repo/agent_runner/sdlc/delivery/80_reviews/console-sdlc10-support-REV-30-backlog.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/repo/agent_runner/sdlc/delivery/80_reviews/WI-20260723-001_console-sdlc10-support-01-REV-40-task.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/repo/agent_runner/sdlc/delivery/80_reviews/WI-20260723-001_console-sdlc10-support-02-REV-40-task.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/repo/codebase/backups/BACKUP-20260723-193004/00_standards/CODEBASE_DOC_SOP.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/repo/codebase/backups/BACKUP-20260723-193004/00_standards/CODEBASE_DOC_STATUS_RULES.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/repo/codebase/current/00_standards/CODEBASE_DOC_SOP.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/repo/codebase/current/00_standards/CODEBASE_DOC_STATUS_RULES.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/00BOOT-20260719-5ceb9505-bootstrap-lifecycle-summary.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/00BOOT-20260720-5d679fd5-bootstrap-lifecycle-summary.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/00BOOT-20260720-818a452f-bootstrap-lifecycle-summary.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/00BOOT-20260720-f7113f08-bootstrap-lifecycle-summary.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/00BOOT-20260721-2af1fe38-bootstrap-lifecycle-summary.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/00BOOT-20260721-86fb57bb-bootstrap-lifecycle-summary.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/00BOOT-20260722-2dcbbdfe-bootstrap-lifecycle-summary.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/00BOOT-20260722-9877c2ee-bootstrap-lifecycle-summary.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/bundle_governance/action_policy.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/bundle_governance/core_governance.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/bundle_governance/generated/AGENTS.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/bundle_governance/generated/CLAUDE.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/bundle_governance/generated/QWEN.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/bundle_governance/prompt_layout.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/bundle_governance/prompt_sop.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/bundle_governance/review_audit_contract.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/bundle_governance/action_policy.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/bundle_governance/core_governance.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/bundle_governance/generated/AGENTS.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/bundle_governance/generated/CLAUDE.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/bundle_governance/generated/QWEN.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/bundle_governance/prompt_layout.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/bundle_governance/prompt_sop.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/bundle_governance/review_audit_contract.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_00_codebase_v1/bundle_governance/core_governance.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_00_codebase_v1/bundle_governance/generated/AGENTS.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_00_codebase_v1/bundle_governance/generated/CLAUDE.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_00_codebase_v1/bundle_governance/generated/QWEN.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/current/BUNDLE_TAXONOMY.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/current/DOCUMENT_AUTHORITY.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/current/GOVERNANCE_LIFECYCLE.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/current/LAYER_MODEL.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/current/METADATA_STANDARD.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/current/README.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-0864b1f2/BUNDLE_TAXONOMY.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-0864b1f2/DOCUMENT_AUTHORITY.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-0864b1f2/GOVERNANCE_LIFECYCLE.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-0864b1f2/LAYER_MODEL.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-0864b1f2/METADATA_STANDARD.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-0864b1f2/README.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-4e51c88b/BUNDLE_TAXONOMY.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-4e51c88b/DOCUMENT_AUTHORITY.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-4e51c88b/GOVERNANCE_LIFECYCLE.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-4e51c88b/LAYER_MODEL.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-4e51c88b/METADATA_STANDARD.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-4e51c88b/README.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-61ae0105/BUNDLE_TAXONOMY.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-61ae0105/DOCUMENT_AUTHORITY.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-61ae0105/GOVERNANCE_LIFECYCLE.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-61ae0105/LAYER_MODEL.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-61ae0105/METADATA_STANDARD.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-61ae0105/README.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-96e730ab/BUNDLE_TAXONOMY.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-96e730ab/DOCUMENT_AUTHORITY.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-96e730ab/GOVERNANCE_LIFECYCLE.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-96e730ab/LAYER_MODEL.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-96e730ab/METADATA_STANDARD.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-96e730ab/README.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-c5e882c3/BUNDLE_TAXONOMY.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-c5e882c3/DOCUMENT_AUTHORITY.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-c5e882c3/GOVERNANCE_LIFECYCLE.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-c5e882c3/LAYER_MODEL.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-c5e882c3/METADATA_STANDARD.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-c5e882c3/README.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-f15f153c/BUNDLE_TAXONOMY.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-f15f153c/DOCUMENT_AUTHORITY.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-f15f153c/GOVERNANCE_LIFECYCLE.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-f15f153c/LAYER_MODEL.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-f15f153c/METADATA_STANDARD.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/history/01GF-20260719-f15f153c/README.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/01GF-20260719-0864b1f2-governance-context-inventory.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/01GF-20260719-0864b1f2-governance-foundation-audit.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/01GF-20260719-0864b1f2-governance-foundation-review.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/01GF-20260719-0864b1f2-governance-foundation-validation.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/BUNDLE_TAXONOMY.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/DOCUMENT_AUTHORITY.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/GOVERNANCE_LIFECYCLE.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/LAYER_MODEL.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/METADATA_STANDARD.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-0864b1f2/README.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/01GF-20260719-4e51c88b-governance-context-inventory.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/01GF-20260719-4e51c88b-governance-foundation-audit.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/01GF-20260719-4e51c88b-governance-foundation-review.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/01GF-20260719-4e51c88b-governance-foundation-validation.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/BUNDLE_TAXONOMY.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/DOCUMENT_AUTHORITY.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/GOVERNANCE_LIFECYCLE.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/LAYER_MODEL.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/METADATA_STANDARD.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/README.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/01GF-20260719-61ae0105-governance-context-inventory.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/01GF-20260719-61ae0105-governance-foundation-audit.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/01GF-20260719-61ae0105-governance-foundation-review.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/01GF-20260719-61ae0105-governance-foundation-validation.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/BUNDLE_TAXONOMY.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/DOCUMENT_AUTHORITY.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/GOVERNANCE_LIFECYCLE.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/LAYER_MODEL.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/METADATA_STANDARD.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-61ae0105/README.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/01GF-20260719-96e730ab-governance-context-inventory.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/01GF-20260719-96e730ab-governance-foundation-audit.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/01GF-20260719-96e730ab-governance-foundation-review.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/01GF-20260719-96e730ab-governance-foundation-validation.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/BUNDLE_TAXONOMY.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/DOCUMENT_AUTHORITY.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/GOVERNANCE_LIFECYCLE.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/LAYER_MODEL.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/METADATA_STANDARD.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-96e730ab/README.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/01GF-20260719-c5e882c3-governance-context-inventory.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/01GF-20260719-c5e882c3-governance-foundation-audit.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/01GF-20260719-c5e882c3-governance-foundation-review.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/01GF-20260719-c5e882c3-governance-foundation-validation.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/BUNDLE_TAXONOMY.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/DOCUMENT_AUTHORITY.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/GOVERNANCE_LIFECYCLE.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/LAYER_MODEL.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/METADATA_STANDARD.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-c5e882c3/README.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/01GF-20260719-f15f153c-governance-context-inventory.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/01GF-20260719-f15f153c-governance-foundation-audit.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/01GF-20260719-f15f153c-governance-foundation-review.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/01GF-20260719-f15f153c-governance-foundation-validation.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/BUNDLE_TAXONOMY.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/DOCUMENT_AUTHORITY.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/GOVERNANCE_LIFECYCLE.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/LAYER_MODEL.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/METADATA_STANDARD.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/foundation/runs/01GF-20260719-f15f153c/README.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/current/BUNDLE_AUTHORING_CONTRACT.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/current/METADATA_CONTRACT.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/current/README.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/current/RUNTIME_MODEL.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/current/SHARED_SERVICES.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/current/VALIDATION_CONTRACT.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/history/02AR-20260721-2eaba4b3/BUNDLE_AUTHORING_CONTRACT.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/history/02AR-20260721-2eaba4b3/METADATA_CONTRACT.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/history/02AR-20260721-2eaba4b3/README.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/history/02AR-20260721-2eaba4b3/RUNTIME_MODEL.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/history/02AR-20260721-2eaba4b3/SHARED_SERVICES.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/history/02AR-20260721-2eaba4b3/VALIDATION_CONTRACT.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/history/02PC-20260721-b092c705/BUNDLE_AUTHORING_CONTRACT.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/history/02PC-20260721-b092c705/METADATA_CONTRACT.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/history/02PC-20260721-b092c705/README.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/history/02PC-20260721-b092c705/RUNTIME_MODEL.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/history/02PC-20260721-b092c705/SHARED_SERVICES.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/history/02PC-20260721-b092c705/VALIDATION_CONTRACT.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/history/02PC-GEN-20260721-009/BUNDLE_AUTHORING_CONTRACT.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/history/02PC-GEN-20260721-009/METADATA_CONTRACT.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/history/02PC-GEN-20260721-009/README.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/history/02PC-GEN-20260721-009/RUNTIME_MODEL.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/history/02PC-GEN-20260721-009/SHARED_SERVICES.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/history/02PC-GEN-20260721-009/VALIDATION_CONTRACT.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/02PC-20260721-b092c705-platform-context-inventory.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/02PC-20260721-b092c705-platform-core-audit.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/02PC-20260721-b092c705-platform-core-review.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/02PC-20260721-b092c705-platform-core-validation.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/BUNDLE_AUTHORING_CONTRACT.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/METADATA_CONTRACT.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/README.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/RUNTIME_MODEL.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/SHARED_SERVICES.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/runs/02PC-20260721-b092c705/VALIDATION_CONTRACT.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/02PC-GEN-20260721-009-platform-context-inventory.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/02PC-GEN-20260721-009-platform-core-audit.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/02PC-GEN-20260721-009-platform-core-review.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/02PC-GEN-20260721-009-platform-core-validation.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/BUNDLE_AUTHORING_CONTRACT.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/METADATA_CONTRACT.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/README.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/RUNTIME_MODEL.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/SHARED_SERVICES.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/runs/02PC-GEN-20260721-009/VALIDATION_CONTRACT.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/01_DRAFT_INIT_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/02_INIT_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/03_REQ_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/04_PLAN_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/05_BACKLOG_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/06_TASK_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/07_IMPL_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/08_VALID_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/09_REV_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/10_MEM_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/11_CLOSE_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/template_registry.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/current/01_templates/WORKFLOW_SOP_v1.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/current/02_agents/AGENT-executor.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/current/02_agents/AGENT-implementation-planner.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/current/02_agents/AGENT-memory-manager.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/current/02_agents/AGENT-planner.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/current/02_agents/AGENT-reviewer.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/current/02_agents/AGENT-task-decomposer.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/current/02_agents/AGENTS.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/current/02_agents/DELIVERY_STATUS_RULES_v1.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/01_DRAFT_INIT_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/02_INIT_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/03_REQ_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/04_PLAN_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/05_BACKLOG_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/06_TASK_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/07_IMPL_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/08_VALID_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/09_REV_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/10_MEM_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/11_CLOSE_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/template_registry.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/01_templates/WORKFLOW_SOP_v1.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-executor.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-implementation-planner.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-memory-manager.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-planner.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-reviewer.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-task-decomposer.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/02_agents/AGENTS.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/history/SDLC00SCF-20260722-3a011a52/02_agents/DELIVERY_STATUS_RULES_v1.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/01_DRAFT_INIT_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/02_INIT_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/03_REQ_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/04_PLAN_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/05_BACKLOG_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/06_TASK_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/07_IMPL_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/08_VALID_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/09_REV_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/10_MEM_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/11_CLOSE_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/template_registry.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/01_templates/WORKFLOW_SOP_v1.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-executor.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-implementation-planner.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-memory-manager.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-planner.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-reviewer.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/02_agents/AGENT-task-decomposer.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/02_agents/AGENTS.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/02_agents/DELIVERY_STATUS_RULES_v1.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-3a011a52/SDLC00SCF-20260722-3a011a52-sdlc-scaffold-review.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/01_DRAFT_INIT_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/02_INIT_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/03_REQ_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/04_PLAN_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/05_BACKLOG_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/06_TASK_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/07_IMPL_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/08_VALID_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/09_REV_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/10_MEM_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/11_CLOSE_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/template_registry.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/01_templates/WORKFLOW_SOP_v1.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/AGENT-executor.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/AGENT-implementation-planner.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/AGENT-memory-manager.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/AGENT-planner.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/AGENT-reviewer.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/AGENT-task-decomposer.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/AGENTS.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/02_agents/DELIVERY_STATUS_RULES_v1.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-914943f4/SDLC00SCF-20260722-914943f4-sdlc-scaffold-review.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/01_DRAFT_INIT_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/02_INIT_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/03_REQ_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/04_PLAN_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/05_BACKLOG_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/06_TASK_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/07_IMPL_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/08_VALID_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/09_REV_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/10_MEM_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/11_CLOSE_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/template_registry.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/01_templates/WORKFLOW_SOP_v1.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/AGENT-executor.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/AGENT-implementation-planner.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/AGENT-memory-manager.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/AGENT-planner.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/AGENT-reviewer.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/AGENT-task-decomposer.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/AGENTS.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/02_agents/DELIVERY_STATUS_RULES_v1.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-cc2b347d/SDLC00SCF-20260722-cc2b347d-sdlc-scaffold-review.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/01_DRAFT_INIT_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/02_INIT_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/03_REQ_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/04_PLAN_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/05_BACKLOG_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/06_TASK_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/07_IMPL_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/08_VALID_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/09_REV_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/10_MEM_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/11_CLOSE_template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/template_registry.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/01_templates/WORKFLOW_SOP_v1.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/AGENT-executor.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/AGENT-implementation-planner.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/AGENT-memory-manager.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/AGENT-planner.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/AGENT-reviewer.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/AGENT-task-decomposer.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/AGENTS.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/platform/agent_runner/sdlc/runs/SDLC00SCF-20260722-f831acb7/02_agents/DELIVERY_STATUS_RULES_v1.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/00_templates/01_initiative.template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/00_templates/02_plan.template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/00_templates/02b_task_graph.template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/00_templates/03_task.template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/00_templates/04_implementation_plan.template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/00_templates/04_review.template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/00_templates/05_agent.template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/00_templates/05_validation.template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/00_templates/06_memory.template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/00_templates/_legacy/decision-template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/00_templates/_legacy/execution-summary-template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/00_templates/_legacy/initiative-template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/00_templates/_legacy/outcome-template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/00_templates/_legacy/plan-template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/00_templates/_legacy/review-template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/00_templates/_legacy/self-test-result-template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/00_templates/_legacy/task-template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/00_templates/_legacy/test-plan-template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/00_templates/_legacy/test-result-template.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/00_templates/_legacy/test-result-<task>-codex.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/00_templates/template_registry.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/00_templates/WORKFLOW_SOP_v1.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/01_initiatives/INIT-20260418-04_managed-artifact-control-plane-exposure-v1.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/02_plans/artifacts/TASK-GRAPH-20260418-PLAN-20260418-02.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/02_plans/PLAN-20260418-02_managed-artifact-control-plane-exposure-v1.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/03_tasks/TASK-20260418-01_contract-build-api-trigger.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/03_tasks/TASK-20260418-02_managed-generation-api-trigger.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/03_tasks/TASK-20260418-03_generation-run-api-surface.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/03_tasks/TASK-20260418-04_artifact-lifecycle-retrieval.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/03_tasks/TASK-20260418-05_router-registration-documentation.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/04_implementation_plans/IMPL-20260418-01_contract-build-api-trigger.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/04_implementation_plans/IMPL-20260418-02_managed-generation-api-trigger.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/04_implementation_plans/IMPL-20260418-03_generation-run-api-surface.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/05_reviews/REV-260418-01_rtask_T-0418-01_contract-build-api-trigger.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/05_reviews/REV-260418-02_rimpl_M-0418-01_contract-build-api-trigger.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/05_reviews/REV-260418-03_rtask_T-0418-02_managed-generation-api-trigger.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/05_reviews/REV-260418-04_rtask_T-0418-02_managed-generation-api-trigger.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/05_reviews/REV-260418-05_rimpl_M-0418-02_managed-generation-api-trigger.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/05_reviews/VALIDATION-260418-2-M-0418-01_contract-build-api-trigger.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/05_reviews/VALIDATION-260418-2-M-0418-02_managed-generation-api-trigger.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/05_reviews/VALIDATION-260418-3-M-0418-02_managed-generation-api-trigger.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/05_reviews/VALIDATION-260418-M-0418-01_contract-build-api-trigger.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/05_reviews/VALIDATION-260418-M-0418-02_managed-generation-api-trigger.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/08_agents/AGENT-executor.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/08_agents/AGENT-implementation-planner.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/08_agents/AGENT-memory-manager.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/08_agents/AGENT-planner.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/08_agents/AGENT-reviewer.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/08_agents/AGENT-task-decomposer.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/08_agents/AGENTS.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/08_agents/DELIVERY_STATUS_RULES_v1.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/delivery/README.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/LAYER1_GOVERNANCE_SPECIFICATION.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/LAYER2_PLATFORM_CORE_SPECIFICATION.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/LAYER3_AI_DRIVEN_SDLC_IMPLEMENTATION_PLAN.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/LAYER3_AI_DRIVEN_SDLC_SPECIFICATION.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/LAYER_ARCHITECTURE_MASTERPLAN.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/README.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/SDLC_00_CODEBASE_V1_PLAN.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/SDLC_CONSOLE_APP_PLAN.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/SDLC_TECHNICAL_CRITIQUE_PLAN.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/SDLC_WORKFLOW_SCAFFOLD_PLAN.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/WORKFLOW_EXTENSION_INTERFACE_PLAN.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| QWEN.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| README.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| tests/integration/README.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| tests/unit/README.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| WORKFLOW_PLUGIN_INSTALLATION.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/01_governance_foundation_v1/bundle_governance/action_policy.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/01_governance_foundation_v1/bundle_governance/core_governance.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/01_governance_foundation_v1/bundle_governance/generated/AGENTS.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/01_governance_foundation_v1/bundle_governance/generated/CLAUDE.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/01_governance_foundation_v1/bundle_governance/generated/QWEN.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/01_governance_foundation_v1/bundle_governance/prompt_layout.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/01_governance_foundation_v1/bundle_governance/prompt_sop.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/01_governance_foundation_v1/bundle_governance/review_audit_contract.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/02_agent_runner_platform_v1/bundle_governance/action_policy.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/02_agent_runner_platform_v1/bundle_governance/core_governance.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/02_agent_runner_platform_v1/bundle_governance/generated/AGENTS.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/02_agent_runner_platform_v1/bundle_governance/generated/CLAUDE.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/02_agent_runner_platform_v1/bundle_governance/generated/QWEN.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/02_agent_runner_platform_v1/bundle_governance/prompt_layout.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/02_agent_runner_platform_v1/bundle_governance/prompt_sop.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/02_agent_runner_platform_v1/bundle_governance/review_audit_contract.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/DEVELOPER_GUIDE.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_00_codebase_v1/bundle_governance/core_governance.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_00_codebase_v1/bundle_governance/generated/AGENTS.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_00_codebase_v1/bundle_governance/generated/CLAUDE.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_00_codebase_v1/bundle_governance/generated/QWEN.md | docs | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |

## 8. Other Files

| File Path | Category | Documentation Mode | Status | Owner Doc Path | Last Verified By Change |
|---|---|---|---|---|---|
| .gitignore | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| _check_ascii.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| _check_chars.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/00_bootstrap_lifecycle_admin_v1/actions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/00_bootstrap_lifecycle_admin_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/actions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/output_paths.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/prompts/01_generate_governance_foundation_docs.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/prompts/02_review_governance_foundation_docs.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/prompts/03_refine_governance_foundation_docs.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/01_governance_foundation_v1/prompts/04_audit_governance_foundation_docs.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/actions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/output_paths.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/prompts/01_generate_platform_core_docs.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/prompts/02_review_platform_core_docs.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/prompts/03_refine_platform_core_docs.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/02_agent_runner_platform_v1/prompts/04_audit_platform_core_docs.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_00_codebase_v1/actions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_00_codebase_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_00_codebase_v1/prompts/04_review_sync_log.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_00_codebase_v1/prompts/05_refine_codebase_docs.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_00_delivery_scaffold_v1/actions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_00_delivery_scaffold_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_00_delivery_scaffold_v1/install.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_00_delivery_scaffold_v1/prompts/01_generate_templates.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_00_delivery_scaffold_v1/prompts/02_generate_agent_contracts.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_00_delivery_scaffold_v1/prompts/03_review_scaffold.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_00_delivery_scaffold_v1/prompts/04_refine_scaffold.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_00_init_doc_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_00_init_doc_v1/prompts/01_generate_initiative.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_00_init_doc_v1/prompts/02_technical_critique.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_00_init_doc_v1/prompts/03_review_initiative.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_00_init_doc_v1/prompts/04_refine_initiative.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_10_requirement_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_10_requirement_v1/prompts/01_generate_requirements.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_10_requirement_v1/prompts/02_technical_critique.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_10_requirement_v1/prompts/03_review_requirements.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_10_requirement_v1/prompts/04_refine_requirements.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_20_planning_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_20_planning_v1/prompts/01_generate_plan.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_20_planning_v1/prompts/02_technical_critique.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_20_planning_v1/prompts/03_review_plan.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_20_planning_v1/prompts/04_refine_plan.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_30_backlog_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_30_backlog_v1/prompts/01_generate_backlog.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_30_backlog_v1/prompts/02_technical_critique.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_30_backlog_v1/prompts/03_review_backlog.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_30_backlog_v1/prompts/04_refine_backlog.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_40_task_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_40_task_v1/prompts/01_generate_task.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_40_task_v1/prompts/02_technical_critique.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_40_task_v1/prompts/03_review_task.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_40_task_v1/prompts/04_refine_task.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_50_implementation_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_50_implementation_v1/prompts/01_generate_implementation.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_50_implementation_v1/prompts/02_technical_critique.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_50_implementation_v1/prompts/03_review_implementation.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_50_implementation_v1/prompts/04_refine_implementation.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_60_execution_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_60_execution_v1/prompts/01_execute_task.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_60_execution_v1/prompts/02_technical_critique.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_60_execution_v1/prompts/03_internal_review.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_60_execution_v1/prompts/04_refine_execution.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_70_validation_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_70_validation_v1/prompts/01_generate_validation.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_70_validation_v1/prompts/02_technical_critique.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_70_validation_v1/prompts/03_review_validation.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_70_validation_v1/prompts/04_refine_validation.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_80_review_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_80_review_v1/prompts/01_generate_review.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_80_review_v1/prompts/02_technical_critique.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_80_review_v1/prompts/03_review_all.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/workflows/sdlc_80_review_v1/prompts/04_refine_documents.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| MANIFEST.in | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/00_repo_master_docs_bootstrap_v1/actions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/00_repo_master_docs_bootstrap_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/00_repo_master_docs_bootstrap_v1/output_paths.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/00_repo_master_docs_bootstrap_v1/prompts/02_generate_project_analysis.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/00_repo_master_docs_bootstrap_v1/prompts/03_generate_system_overview_docs.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/00_repo_master_docs_bootstrap_v1/prompts/04_generate_architecture_docs.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/00_repo_master_docs_bootstrap_v1/prompts/04b_generate_integration_docs.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/00_repo_master_docs_bootstrap_v1/prompts/04c_generate_failure_docs.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/00_repo_master_docs_bootstrap_v1/prompts/04d_generate_architecture_flow_docs.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/00_repo_master_docs_bootstrap_v1/prompts/05_review_master_system_docs.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/00_repo_master_docs_bootstrap_v1/prompts/06_refine_master_system_docs.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/_layer3_archive/architecture_site.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/_layer3_archive/archive_previous_version.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/_layer3_archive/assemble_video.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/_layer3_archive/execute_i2v.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/_layer3_archive/execute_t2i.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/_layer3_archive/execute_voiceover.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/_layer3_archive/generate_site.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/_layer3_archive/generate_site_pdf.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/_layer3_archive/prepare_delivery_scaffold.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/_layer3_archive/publish_architecture_site.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/_layer3_archive/submit_comfyui.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/_layer3_archive/validate_architecture_site.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/_layer3_archive/validate_delivery_docs.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/_layer3_archive/validate_developer_site.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/_layer3_archive/validate_operator_site.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/_layer3_archive/validate_stakeholder_site.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/_layer3_archive/validate_tester_site.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/_layer3_archive/validate_user_site.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/delivery_planning_v1/02_planner.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/delivery_planning_v1/03_refine_plan.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/delivery_planning_v1/03_replan_plan.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/delivery_planning_v1/03_review_planner.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/delivery_planning_v1/04_task_graph.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/delivery_planning_v1/05_refine_task_graph.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/delivery_planning_v1/05_replan_task_graph.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/delivery_planning_v1/05_review_task_graph.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/delivery_planning_v1/06_task.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/delivery_planning_v1/07_refine_task.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/delivery_planning_v1/07_review_task.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/delivery_scaffold_v1/01_project_analysis.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/delivery_scaffold_v1/02_generate_sop.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/delivery_scaffold_v1/03_generate_templates.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/delivery_scaffold_v1/03_review_sop.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/delivery_scaffold_v1/04_generate_agents.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/delivery_scaffold_v1/05_refine_sop.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/delivery_scaffold_v1/05_replan_sop.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/delivery_scaffold_v1/06_refine_templates.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/delivery_scaffold_v1/06_review_templates.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/delivery_scaffold_v1/07_refine_agents.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/delivery_scaffold_v1/08_review_agents.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/initiative_intake_v1/01_pre_init.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/initiative_intake_v1/02_review_pre_init.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/initiative_intake_v1/03_refine_pre_init.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/task_execution_v1/08_impl_task.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/task_execution_v1/08_impl_task_qwen.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/task_execution_v1/09_refine_impl.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/task_execution_v1/09_review_impl_task.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/task_execution_v1/09_review_impl_task_qwen.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/task_execution_v1/10_executor.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/task_execution_v1/11_validate.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/task_execution_v1/11_validate_qwen.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/prompts/task_execution_v1/99_test.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| masterplan/old legacy workflow/template_groups.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| requirements.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| sample_dropdown_app.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_bootstrap_lifecycle_admin_v1/actions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_bootstrap_lifecycle_admin_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/01_governance_foundation_v1/actions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/01_governance_foundation_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/01_governance_foundation_v1/output_paths.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/01_governance_foundation_v1/prompts/01_generate_governance_foundation_docs.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/01_governance_foundation_v1/prompts/02_review_governance_foundation_docs.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/01_governance_foundation_v1/prompts/03_refine_governance_foundation_docs.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/01_governance_foundation_v1/prompts/04_audit_governance_foundation_docs.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/02_agent_runner_platform_v1/actions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/02_agent_runner_platform_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/02_agent_runner_platform_v1/output_paths.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/02_agent_runner_platform_v1/prompts/01_generate_platform_core_docs.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/02_agent_runner_platform_v1/prompts/02_review_platform_core_docs.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/02_agent_runner_platform_v1/prompts/03_refine_platform_core_docs.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/02_agent_runner_platform_v1/prompts/04_audit_platform_core_docs.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_00_codebase_v1/actions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_00_codebase_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_00_codebase_v1/prompts/04_review_sync_log.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_00_codebase_v1/prompts/05_refine_codebase_docs.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_00_delivery_scaffold_v1/actions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_00_delivery_scaffold_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_00_delivery_scaffold_v1/install.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_00_delivery_scaffold_v1/prompts/01_generate_templates.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_00_delivery_scaffold_v1/prompts/02_generate_agent_contracts.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_00_delivery_scaffold_v1/prompts/03_review_scaffold.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_00_delivery_scaffold_v1/prompts/04_refine_scaffold.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_00_init_doc_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_00_init_doc_v1/prompts/01_generate_initiative.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_00_init_doc_v1/prompts/02_technical_critique.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_00_init_doc_v1/prompts/03_review_initiative.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_00_init_doc_v1/prompts/04_refine_initiative.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_10_requirement_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_10_requirement_v1/prompts/01_generate_requirements.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_10_requirement_v1/prompts/02_technical_critique.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_10_requirement_v1/prompts/03_review_requirements.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_10_requirement_v1/prompts/04_refine_requirements.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_20_planning_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_20_planning_v1/prompts/01_generate_plan.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_20_planning_v1/prompts/02_technical_critique.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_20_planning_v1/prompts/03_review_plan.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_20_planning_v1/prompts/04_refine_plan.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_30_backlog_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_30_backlog_v1/prompts/01_generate_backlog.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_30_backlog_v1/prompts/02_technical_critique.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_30_backlog_v1/prompts/03_review_backlog.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_30_backlog_v1/prompts/04_refine_backlog.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_40_task_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_40_task_v1/prompts/01_generate_task.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_40_task_v1/prompts/02_technical_critique.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_40_task_v1/prompts/03_review_task.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_40_task_v1/prompts/04_refine_task.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_50_implementation_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_50_implementation_v1/prompts/01_generate_implementation.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_50_implementation_v1/prompts/02_technical_critique.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_50_implementation_v1/prompts/03_review_implementation.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_50_implementation_v1/prompts/04_refine_implementation.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_60_execution_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_60_execution_v1/prompts/01_execute_task.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_60_execution_v1/prompts/02_technical_critique.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_60_execution_v1/prompts/03_internal_review.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_60_execution_v1/prompts/04_refine_execution.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_70_validation_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_70_validation_v1/prompts/01_generate_validation.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_70_validation_v1/prompts/02_technical_critique.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_70_validation_v1/prompts/03_review_validation.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_70_validation_v1/prompts/04_refine_validation.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_80_review_v1/context_extensions.py | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_80_review_v1/prompts/01_generate_review.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_80_review_v1/prompts/02_technical_critique.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_80_review_v1/prompts/03_review_all.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/sdlc_80_review_v1/prompts/04_refine_documents.txt | other | summary | current | docs/repo/codebase/current/03_components/codebase-governance.md | bootstrap/reconcile scan |

## 9. Summary Statistics

| Category | Total Files | Current | Needs Update | Pending Review | Superseded |
|---|---|---|---|---|---|
| configuration/data files | 125 | 125 | 0 | 0 | 0 |
| other files | 214 | 214 | 0 | 0 | 0 |
| python modules | 117 | 117 | 0 | 0 | 0 |
| documentation files | 423 | 423 | 0 | 0 | 0 |
| bootstrap workflow files | 94 | 94 | 0 | 0 | 0 |
| scripts | 70 | 70 | 0 | 0 | 0 |
| test files | 72 | 72 | 0 | 0 | 0 |

## 10. Status Legend

- `current`: documentation is up to date and matches the source
- `needs_update`: source changed and documentation is stale
- `pending_review`: documentation exists but has not been verified
- `superseded`: documentation is obsolete or replaced

## 11. Verification Log

| Date | Verified By | Scope | Result |
|---|---|---|---|
| 2026-07-23 | sdlc_00_codebase_v1 | repository scan | complete |

