---
title: "Codebase Inventory - agent-runner-v2"
template_id: "CODEBASE-INV-v1"
status: "active"
generated: "2026-07-16T22:09:16+08:00"
workflow: "00_repo_master_docs_bootstrap_v1"
step: "01_generate_codebase_baseline"
change_id: "00RMD-20260716-5ee28fa5"
---

# Codebase Inventory: agent-runner-v2

## 1. Inventory Scope

This inventory was generated from a repository scan at `2026-07-16T22:09:16+08:00`.

## 2. Python Source Modules

| File Path | Module Area | Documentation Mode | Status | Owner Doc Path | Last Verified By Change |
|---|---|---|---|---|---|
| agent_runner_v2/__init__.py | package | stub | current | docs/repo/codebase/02_modules/agent-runner-v2-init.md | bootstrap/reconcile scan |
| agent_runner_v2/action_result.py | schema | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-action-result.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/__init__.py | actions | stub | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-init.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/archive_previous_version.py | actions | full | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-archive-previous-version.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/assemble_video.py | actions | full | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-assemble-video.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/copy_artifact.py | actions | full | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-copy-artifact.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/documentation_validation_core.py | actions | full | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-documentation-validation-core.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/execute_i2v.py | actions | full | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-execute-i2v.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/execute_t2i.py | actions | full | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-execute-t2i.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/execute_voiceover.py | actions | full | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-execute-voiceover.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/finalize_bootstrap.py | actions | full | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-finalize-bootstrap.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/generate_site.py | actions | full | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-generate-site.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/generate_site_pdf.py | actions | full | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-generate-site-pdf.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/prepare_delivery_scaffold.py | actions | full | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-prepare-delivery-scaffold.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/promote_artifact.py | actions | full | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-promote-artifact.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/promote_init.py | actions | full | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-promote-init.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/publish_architecture_site.py | actions | full | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-publish-architecture-site.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/scan_repo_codebase.py | actions | full | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-scan-repo-codebase.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/step_completion.py | actions | full | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-step-completion.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/submit_comfyui.py | actions | full | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-submit-comfyui.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/sync_codebase_docs.py | actions | full | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-sync-codebase-docs.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/sync_system_docs.py | actions | full | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-sync-system-docs.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/validate_architecture_site.py | actions | full | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-validate-architecture-site.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/validate_codebase_docs.py | actions | full | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-validate-codebase-docs.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/validate_delivery_docs.py | actions | full | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-validate-delivery-docs.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/validate_developer_site.py | actions | full | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-validate-developer-site.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/validate_operator_site.py | actions | full | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-validate-operator-site.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/validate_stakeholder_site.py | actions | full | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-validate-stakeholder-site.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/validate_system_docs.py | actions | full | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-validate-system-docs.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/validate_tester_site.py | actions | full | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-validate-tester-site.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/validate_user_site.py | actions | full | current | docs/repo/codebase/02_modules/agent-runner-v2-actions-validate-user-site.md | bootstrap/reconcile scan |
| agent_runner_v2/approve_commands.py | commands | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-approve-commands.md | bootstrap/reconcile scan |
| agent_runner_v2/architecture_site.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-architecture-site.md | bootstrap/reconcile scan |
| agent_runner_v2/artifact_paths.py | schema | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-artifact-paths.md | bootstrap/reconcile scan |
| agent_runner_v2/backend_client.py | backend | full | current | docs/repo/codebase/02_modules/agent-runner-v2-backend-client.md | bootstrap/reconcile scan |
| agent_runner_v2/backend_execution.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-backend-execution.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_bootstrap_lifecycle_admin_v1/actions.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-bootstrap-workflows-default-00-bootstrap-lifecycle-admin-v1-actions.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_bootstrap_lifecycle_admin_v1/context_extensions.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-bootstrap-workflows-default-00-bootstrap-lifecycle-admin-v1-context-extensions.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_layer1_governance_bootstrap_v1/actions.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-bootstrap-workflows-default-00-layer1-governance-bootstrap-v1-actions.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_layer1_governance_bootstrap_v1/context_extensions.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-bootstrap-workflows-default-00-layer1-governance-bootstrap-v1-context-extensions.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_repo_master_docs_bootstrap_v1/actions.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-bootstrap-workflows-default-00-repo-master-docs-bootstrap-v1-actions.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_repo_master_docs_bootstrap_v1/context_extensions.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-bootstrap-workflows-default-00-repo-master-docs-bootstrap-v1-context-extensions.md | bootstrap/reconcile scan |
| agent_runner_v2/bundle_governance.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-bundle-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bundle_loader.py | bootstrap | full | current | docs/repo/codebase/02_modules/agent-runner-v2-bundle-loader.md | bootstrap/reconcile scan |
| agent_runner_v2/bundle_taxonomy.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-bundle-taxonomy.md | bootstrap/reconcile scan |
| agent_runner_v2/cleanup_generated_docs.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-cleanup-generated-docs.md | bootstrap/reconcile scan |
| agent_runner_v2/cli_runtime.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-cli-runtime.md | bootstrap/reconcile scan |
| agent_runner_v2/codebase_docs.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-codebase-docs.md | bootstrap/reconcile scan |
| agent_runner_v2/coder_adapters.py | coder | full | current | docs/repo/codebase/02_modules/agent-runner-v2-coder-adapters.md | bootstrap/reconcile scan |
| agent_runner_v2/config/__init__.py | package | stub | current | docs/repo/codebase/02_modules/agent-runner-v2-config-init.md | bootstrap/reconcile scan |
| agent_runner_v2/config/section_requirements.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-config-section-requirements.md | bootstrap/reconcile scan |
| agent_runner_v2/config_loader.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-config-loader.md | bootstrap/reconcile scan |
| agent_runner_v2/constants.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-constants.md | bootstrap/reconcile scan |
| agent_runner_v2/daemon.py | backend | full | current | docs/repo/codebase/02_modules/agent-runner-v2-daemon.md | bootstrap/reconcile scan |
| agent_runner_v2/daemon_runtime.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-daemon-runtime.md | bootstrap/reconcile scan |
| agent_runner_v2/doc_paths.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-doc-paths.md | bootstrap/reconcile scan |
| agent_runner_v2/documentation_guardrails.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-documentation-guardrails.md | bootstrap/reconcile scan |
| agent_runner_v2/engine_commands.py | commands | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-engine-commands.md | bootstrap/reconcile scan |
| agent_runner_v2/exceptions.py | schema | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-exceptions.md | bootstrap/reconcile scan |
| agent_runner_v2/execution_core.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-execution-core.md | bootstrap/reconcile scan |
| agent_runner_v2/execution_request.py | state | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-execution-request.md | bootstrap/reconcile scan |
| agent_runner_v2/execution_result.py | state | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-execution-result.md | bootstrap/reconcile scan |
| agent_runner_v2/execution_support.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-execution-support.md | bootstrap/reconcile scan |
| agent_runner_v2/failure_runtime.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-failure-runtime.md | bootstrap/reconcile scan |
| agent_runner_v2/job_state.py | state | full | current | docs/repo/codebase/02_modules/agent-runner-v2-job-state.md | bootstrap/reconcile scan |
| agent_runner_v2/manual_runtime.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-manual-runtime.md | bootstrap/reconcile scan |
| agent_runner_v2/manual_runtime_deps.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-manual-runtime-deps.md | bootstrap/reconcile scan |
| agent_runner_v2/model_config.py | coder | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-model-config.md | bootstrap/reconcile scan |
| agent_runner_v2/notification_manager.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-notification-manager.md | bootstrap/reconcile scan |
| agent_runner_v2/notifications.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-notifications.md | bootstrap/reconcile scan |
| agent_runner_v2/recovery_runtime.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-recovery-runtime.md | bootstrap/reconcile scan |
| agent_runner_v2/routing_runtime.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-routing-runtime.md | bootstrap/reconcile scan |
| agent_runner_v2/run_agent.py | core | full | current | docs/repo/codebase/02_modules/agent-runner-v2-run-agent.md | bootstrap/reconcile scan |
| agent_runner_v2/runner_actions.py | schema | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-runner-actions.md | bootstrap/reconcile scan |
| agent_runner_v2/runner_logger.py | backend | full | current | docs/repo/codebase/02_modules/agent-runner-v2-runner-logger.md | bootstrap/reconcile scan |
| agent_runner_v2/runtime_context.py | state | full | current | docs/repo/codebase/02_modules/agent-runner-v2-runtime-context.md | bootstrap/reconcile scan |
| agent_runner_v2/runtime_utils.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-runtime-utils.md | bootstrap/reconcile scan |
| agent_runner_v2/shared_runtime_deps.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-shared-runtime-deps.md | bootstrap/reconcile scan |
| agent_runner_v2/site_styles.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-site-styles.md | bootstrap/reconcile scan |
| agent_runner_v2/state_defaults.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-state-defaults.md | bootstrap/reconcile scan |
| agent_runner_v2/step_execution_runtime.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-step-execution-runtime.md | bootstrap/reconcile scan |
| agent_runner_v2/step_runner.py | core | full | current | docs/repo/codebase/02_modules/agent-runner-v2-step-runner.md | bootstrap/reconcile scan |
| agent_runner_v2/submit_commands.py | commands | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-submit-commands.md | bootstrap/reconcile scan |
| agent_runner_v2/submitter.py | commands | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-submitter.md | bootstrap/reconcile scan |
| agent_runner_v2/sync_workflows.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-sync-workflows.md | bootstrap/reconcile scan |
| agent_runner_v2/system_docs.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-system-docs.md | bootstrap/reconcile scan |
| agent_runner_v2/task_runtime.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-task-runtime.md | bootstrap/reconcile scan |
| agent_runner_v2/tools/agent_tools.py | tools | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-tools-agent-tools.md | bootstrap/reconcile scan |
| agent_runner_v2/transition_runtime.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-transition-runtime.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_bundle_validate_commands.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-workflow-bundle-validate-commands.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_bundle_validator.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-workflow-bundle-validator.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_packages/__init__.py | package | stub | current | docs/repo/codebase/02_modules/agent-runner-v2-workflow-packages-init.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_packages/actions/__init__.py | package | stub | current | docs/repo/codebase/02_modules/agent-runner-v2-workflow-packages-actions-init.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_packages/base.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-workflow-packages-base.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_packages/loader.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-workflow-packages-loader.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_packages/registry.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-workflow-packages-registry.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_router.py | core | full | current | docs/repo/codebase/02_modules/agent-runner-v2-workflow-router.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_runtime.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-workflow-runtime.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_spec_commands.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-workflow-spec-commands.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_specs.py | support | summary | current | docs/repo/codebase/02_modules/agent-runner-v2-workflow-specs.md | bootstrap/reconcile scan |

## 3. Bootstrap Workflow Files

| File Path | Description | Documentation Mode | Status | Owner Doc Path | Last Verified By Change |
|---|---|---|---|---|---|
| agent_runner_v2/bootstrap/workflows/default/00_bootstrap_lifecycle_admin_v1/workflow.toml | workflow asset | full | current | docs/repo/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_layer1_governance_bootstrap_v1/bundle_governance.toml | workflow asset | full | current | docs/repo/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_layer1_governance_bootstrap_v1/bundle_governance/core_governance.md | workflow asset | full | current | docs/repo/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_layer1_governance_bootstrap_v1/bundle_governance/generated/AGENTS.md | workflow asset | full | current | docs/repo/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_layer1_governance_bootstrap_v1/bundle_governance/generated/CLAUDE.md | workflow asset | full | current | docs/repo/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_layer1_governance_bootstrap_v1/bundle_governance/generated/QWEN.md | workflow asset | full | current | docs/repo/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_layer1_governance_bootstrap_v1/bundle_governance/prompt_contract.json | workflow asset | full | current | docs/repo/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_layer1_governance_bootstrap_v1/bundle_governance/prompt_layout.md | workflow asset | full | current | docs/repo/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_layer1_governance_bootstrap_v1/bundle_governance/prompt_sop.md | workflow asset | full | current | docs/repo/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_layer1_governance_bootstrap_v1/prompts/01_generate_layer1_governance_docs.txt | workflow asset | full | current | docs/repo/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_layer1_governance_bootstrap_v1/prompts/02_review_layer1_governance_docs.txt | workflow asset | full | current | docs/repo/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_layer1_governance_bootstrap_v1/prompts/03_refine_layer1_governance_docs.txt | workflow asset | full | current | docs/repo/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_layer1_governance_bootstrap_v1/prompts/04_audit_layer1_governance_accuracy.txt | workflow asset | full | current | docs/repo/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_layer1_governance_bootstrap_v1/workflow.toml | workflow asset | full | current | docs/repo/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_repo_master_docs_bootstrap_v1/prompts/02_generate_project_analysis.txt | workflow asset | full | current | docs/repo/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_repo_master_docs_bootstrap_v1/prompts/03_generate_system_overview_docs.txt | workflow asset | full | current | docs/repo/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_repo_master_docs_bootstrap_v1/prompts/04_generate_architecture_docs.txt | workflow asset | full | current | docs/repo/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_repo_master_docs_bootstrap_v1/prompts/04b_generate_integration_docs.txt | workflow asset | full | current | docs/repo/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_repo_master_docs_bootstrap_v1/prompts/04c_generate_failure_docs.txt | workflow asset | full | current | docs/repo/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_repo_master_docs_bootstrap_v1/prompts/04d_generate_architecture_flow_docs.txt | workflow asset | full | current | docs/repo/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_repo_master_docs_bootstrap_v1/prompts/05_review_master_system_docs.txt | workflow asset | full | current | docs/repo/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_repo_master_docs_bootstrap_v1/prompts/06_refine_master_system_docs.txt | workflow asset | full | current | docs/repo/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/00_repo_master_docs_bootstrap_v1/workflow.toml | workflow asset | full | current | docs/repo/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/_registry/coder_connections.json | workflow asset | full | current | docs/repo/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/_registry/coder_roles.json | workflow asset | full | current | docs/repo/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/_registry/role_policies.json | workflow asset | full | current | docs/repo/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |

## 4. Configuration / Data Files

| File Path | Format | Documentation Mode | Status | Owner Doc Path | Last Verified By Change |
|---|---|---|---|---|---|
| .env.example | example | summary | current | docs/repo/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/bootstrap_publish_manifest.json | json | summary | current | docs/repo/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| agent_runner_v2/comfyui_config.json | json | summary | current | docs/repo/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| agent_runner_v2/job_schema.json | json | summary | current | docs/repo/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| agent_runner_v2/llm_response_schema.json | json | summary | current | docs/repo/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| agent_runner_v2/model_mapping.json | json | summary | current | docs/repo/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| agent_runner_v2/usage_schema.json | json | summary | current | docs/repo/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/repo/codebase/04_changes/00RMD-20260716-5ee28fa5-bootstrap-snapshot.json | json | summary | current | docs/repo/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/00L1-20260716-e4c16ad4-layer1-governance-audit.meta.json | json | summary | current | docs/repo/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/00L1-20260716-e4c16ad4-layer1-governance-review.meta.json | json | summary | current | docs/repo/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| pyproject.toml | toml | summary | current | docs/repo/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/00_bootstrap_lifecycle_admin_v1/workflow.toml | toml | summary | current | docs/repo/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/00_layer1_governance_bootstrap_v1/bundle_governance.toml | toml | summary | current | docs/repo/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/00_layer1_governance_bootstrap_v1/bundle_governance/prompt_contract.json | json | summary | current | docs/repo/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/00_layer1_governance_bootstrap_v1/workflow.toml | toml | summary | current | docs/repo/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/00_repo_master_docs_bootstrap_v1/workflow.toml | toml | summary | current | docs/repo/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/_registry/coder_connections.json | json | summary | current | docs/repo/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/_registry/coder_roles.json | json | summary | current | docs/repo/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/_registry/role_policies.json | json | summary | current | docs/repo/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |

## 5. Scripts

| File Path | Type | Documentation Mode | Status | Owner Doc Path | Last Verified By Change |
|---|---|---|---|---|---|
| run-00_bootstrap_lifecycle_admin_v1.bat | .bat | summary | current | docs/repo/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-00_layer1_governance_bootstrap_v1.bat | .bat | summary | current | docs/repo/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-00_repo_master_docs_bootstrap_v1.bat | .bat | summary | current | docs/repo/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-approve-step.bat | .bat | summary | current | docs/repo/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-bootstrap-publish.bat | .bat | summary | current | docs/repo/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-cleanup-workflow.bat | .bat | summary | current | docs/repo/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-daemon.bat | .bat | summary | current | docs/repo/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-init.bat | .bat | summary | current | docs/repo/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-reset-step.bat | .bat | summary | current | docs/repo/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-00_bootstrap_lifecycle_admin_v1.bat | .bat | summary | current | docs/repo/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-00_layer1_governance_bootstrap_v1.bat | .bat | summary | current | docs/repo/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-00_repo_master_docs_bootstrap_v1.bat | .bat | summary | current | docs/repo/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| sync-workflows-to-backend.bat | .bat | summary | current | docs/repo/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |

## 6. Test Files

| File Path | Coverage Area | Documentation Mode | Status | Owner Doc Path | Last Verified By Change |
|---|---|---|---|---|---|
| tests/conftest.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/integration/__init__.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/integration/test_architecture_site.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/integration/test_backend_worker_mode.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/integration/test_daemon.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/integration/test_notification_e2e.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/integration/test_notification_integration.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/integration/test_notifications.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/integration/test_pushover.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/integration/test_ukbe_runner_wrapper.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/run_workflow_unit_tests.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/__init__.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_agent_tools.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_backend_execution.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_bundle_loader.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_codebase_docs.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_coder_adapters_opencode.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_coder_adapters_sidecar_grace.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_constants_registry.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_context_extensions.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_daemon_runtime.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_daemon_worker_payload.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_documentation_governance.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_documentation_guardrails_cleanup.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_execution_core.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_failure_runtime.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_generated_doc_frontmatter_injection.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_job_state_review_completion.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_job_state_step_dirs.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_job_state_usage_summary.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_machine_contracts.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_manual_runtime.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_model_config_roles.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_notification_manager.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_plugin_workflow_support.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_recovery_runtime.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_routing_runtime.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_run_agent_hook_surface.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_run_agent_legacy_cli.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_run_agent_status.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_runtime_context_paths.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_runtime_utils.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_state_defaults.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_step_completion.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_step_runner_write_contract.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_submit_commands.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_sync_workflows.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_task_runtime.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_tool_instruction_block.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_transition_recovery_runtime.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_transition_runtime.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_workflow_bundle_validator.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_workflow_packages.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_workflow_registry.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_workflow_router_notifications.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_workflow_specs.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/workflows/00_bootstrap_lifecycle_admin_v1/test_actions.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/workflows/00_core_governance_bootstrap_v1/__init__.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/workflows/00_core_governance_bootstrap_v1/test_core_governance_validation_action.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/workflows/00_layer1_governance_bootstrap_v1/test_validation.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/workflows/00_master_docs_bootstrap_v2/__init__.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/workflows/00_master_docs_bootstrap_v2/test_execution_core.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/workflows/00_master_docs_bootstrap_v2/test_master_docs_validation_action.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/workflows/__init__.py | tests | summary | current | docs/repo/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |

## 7. Documentation Files

| File Path | Category | Documentation Mode | Status | Owner Doc Path | Last Verified By Change |
|---|---|---|---|---|---|
| agent_runner_v2/bootstrap/bundles/core/current/00L1-20260716-e4c16ad4-layer1-governance-audit.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/00L1-20260716-e4c16ad4-layer1-governance-review.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/00L1-20260716-e4c16ad4-layer1-governance-validation.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/BUNDLE_TAXONOMY.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/DOCUMENTATION_STANDARD.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/README.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/RUNTIME_GOVERNANCE.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/themes/default/layout.html | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/image_csv_generation.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/QWEN.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| CLAUDE.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| CODER_IMPLEMENTATION_SOP.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/00L1-20260716-e4c16ad4-bootstrap-validation.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/00L1-20260716-e4c16ad4-layer1-governance-audit.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/00L1-20260716-e4c16ad4-layer1-governance-review.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/00L1-20260716-e4c16ad4-layer1-governance-validation.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/BUNDLE_TAXONOMY.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/DOCUMENTATION_STANDARD.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/README.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/00_governance/bootstrap/RUNTIME_GOVERNANCE.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/01_layer2_repo_master_docs_solution_proposal.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/02_ai_driven_sdlc_structure_proposal.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/03_ai_driven_sdlc_migration_plan.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/04_ai_driven_sdlc_docs_reframe_plan.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/backend_execution_refactor_plan.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/core_governance_doc_model_refactor_plan.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/daemon_job_state_sync_plan.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/daemon_manual_execution_unification_plan.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/layer1_governance_bootstrap_v1_draft.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/master_docs_bootstrap_v2_migration_plan.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/model_registry_role_policy_refactor_plan.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/plugin_workflow_bundle_governance_plan.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/workflow_bundle_validation_and_backend_sync_refactor_plan.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| docs/system/workflow_onboarding_runtime_streamline_plan.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| QWEN.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| README.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| tests/integration/README.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| tests/unit/README.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_layer1_governance_bootstrap_v1/bundle_governance/core_governance.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_layer1_governance_bootstrap_v1/bundle_governance/generated/AGENTS.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_layer1_governance_bootstrap_v1/bundle_governance/generated/CLAUDE.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_layer1_governance_bootstrap_v1/bundle_governance/generated/QWEN.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_layer1_governance_bootstrap_v1/bundle_governance/prompt_layout.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_layer1_governance_bootstrap_v1/bundle_governance/prompt_sop.md | docs | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |

## 8. Other Files

| File Path | Category | Documentation Mode | Status | Owner Doc Path | Last Verified By Change |
|---|---|---|---|---|---|
| .gitignore | other | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/themes/default/theme.css | other | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| Create | other | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| MANIFEST.in | other | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| requirements.txt | other | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_bootstrap_lifecycle_admin_v1/actions.py | other | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_bootstrap_lifecycle_admin_v1/context_extensions.py | other | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_layer1_governance_bootstrap_v1/actions.py | other | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_layer1_governance_bootstrap_v1/context_extensions.py | other | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_layer1_governance_bootstrap_v1/prompts/01_generate_layer1_governance_docs.txt | other | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_layer1_governance_bootstrap_v1/prompts/02_review_layer1_governance_docs.txt | other | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_layer1_governance_bootstrap_v1/prompts/03_refine_layer1_governance_docs.txt | other | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_layer1_governance_bootstrap_v1/prompts/04_audit_layer1_governance_accuracy.txt | other | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_repo_master_docs_bootstrap_v1/actions.py | other | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_repo_master_docs_bootstrap_v1/context_extensions.py | other | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_repo_master_docs_bootstrap_v1/prompts/02_generate_project_analysis.txt | other | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_repo_master_docs_bootstrap_v1/prompts/03_generate_system_overview_docs.txt | other | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_repo_master_docs_bootstrap_v1/prompts/04_generate_architecture_docs.txt | other | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_repo_master_docs_bootstrap_v1/prompts/04b_generate_integration_docs.txt | other | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_repo_master_docs_bootstrap_v1/prompts/04c_generate_failure_docs.txt | other | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_repo_master_docs_bootstrap_v1/prompts/04d_generate_architecture_flow_docs.txt | other | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_repo_master_docs_bootstrap_v1/prompts/05_review_master_system_docs.txt | other | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_repo_master_docs_bootstrap_v1/prompts/06_refine_master_system_docs.txt | other | summary | current | docs/repo/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |

## 9. Summary Statistics

| Category | Total Files | Current | Needs Update | Pending Review | Superseded |
|---|---|---|---|---|---|
| configuration/data files | 19 | 19 | 0 | 0 | 0 |
| other files | 23 | 23 | 0 | 0 | 0 |
| python modules | 100 | 100 | 0 | 0 | 0 |
| documentation files | 44 | 44 | 0 | 0 | 0 |
| bootstrap workflow files | 26 | 26 | 0 | 0 | 0 |
| scripts | 13 | 13 | 0 | 0 | 0 |
| test files | 64 | 64 | 0 | 0 | 0 |

## 10. Status Legend

- `current`: documentation is up to date and matches the source
- `needs_update`: source changed and documentation is stale
- `pending_review`: documentation exists but has not been verified
- `superseded`: documentation is obsolete or replaced

## 11. Verification Log

| Date | Verified By | Scope | Result |
|---|---|---|---|
| 2026-07-16 | 00_repo_master_docs_bootstrap_v1 | repository scan | complete |

