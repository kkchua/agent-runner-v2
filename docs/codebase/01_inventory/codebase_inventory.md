---
title: "Codebase Inventory - agent-runner-v2"
template_id: "CODEBASE-INV-v1"
status: "active"
generated: "2026-07-10T14:00:58+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "01_generate_codebase_baseline"
change_id: "00DOC-GEN-20260710-004"
---

# Codebase Inventory: agent-runner-v2

## 1. Inventory Scope

This inventory was generated from a repository scan at `2026-07-10T14:00:58+08:00`.

## 2. Python Source Modules

| File Path | Module Area | Documentation Mode | Status | Owner Doc Path | Last Verified By Change |
|---|---|---|---|---|---|
| agent_runner_v2/__init__.py | package | stub | current | docs/codebase/02_modules/agent-runner-v2-init.md | bootstrap/reconcile scan |
| agent_runner_v2/action_result.py | schema | summary | current | docs/codebase/02_modules/agent-runner-v2-action-result.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/__init__.py | actions | stub | current | docs/codebase/02_modules/agent-runner-v2-actions-init.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/archive_previous_version.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-archive-previous-version.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/assemble_video.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-assemble-video.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/copy_artifact.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-copy-artifact.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/documentation_validation_core.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-documentation-validation-core.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/execute_i2v.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-execute-i2v.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/execute_t2i.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-execute-t2i.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/execute_voiceover.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-execute-voiceover.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/finalize_bootstrap.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-finalize-bootstrap.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/generate_site.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-generate-site.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/generate_site_pdf.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-generate-site-pdf.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/prepare_delivery_scaffold.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-prepare-delivery-scaffold.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/promote_artifact.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-promote-artifact.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/promote_init.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-promote-init.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/publish_architecture_site.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-publish-architecture-site.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/scan_repo_codebase.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-scan-repo-codebase.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/submit_comfyui.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-submit-comfyui.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/sync_codebase_docs.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-sync-codebase-docs.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/sync_system_docs.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-sync-system-docs.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/validate_architecture_site.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-validate-architecture-site.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/validate_codebase_docs.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-validate-codebase-docs.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/validate_delivery_docs.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-validate-delivery-docs.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/validate_developer_site.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-validate-developer-site.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/validate_operator_site.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-validate-operator-site.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/validate_stakeholder_site.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-validate-stakeholder-site.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/validate_system_docs.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-validate-system-docs.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/validate_tester_site.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-validate-tester-site.md | bootstrap/reconcile scan |
| agent_runner_v2/actions/validate_user_site.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-validate-user-site.md | bootstrap/reconcile scan |
| agent_runner_v2/approve_commands.py | commands | summary | current | docs/codebase/02_modules/agent-runner-v2-approve-commands.md | bootstrap/reconcile scan |
| agent_runner_v2/architecture_site.py | support | summary | current | docs/codebase/02_modules/agent-runner-v2-architecture-site.md | bootstrap/reconcile scan |
| agent_runner_v2/artifact_paths.py | schema | summary | current | docs/codebase/02_modules/agent-runner-v2-artifact-paths.md | bootstrap/reconcile scan |
| agent_runner_v2/backend_client.py | backend | full | current | docs/codebase/02_modules/agent-runner-v2-backend-client.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/template_groups.py | bootstrap | full | current | docs/codebase/02_modules/agent-runner-v2-bootstrap-workflows-default-template-groups.md | bootstrap/reconcile scan |
| agent_runner_v2/bundle_loader.py | bootstrap | full | current | docs/codebase/02_modules/agent-runner-v2-bundle-loader.md | bootstrap/reconcile scan |
| agent_runner_v2/bundle_taxonomy.py | support | summary | current | docs/codebase/02_modules/agent-runner-v2-bundle-taxonomy.md | bootstrap/reconcile scan |
| agent_runner_v2/cleanup_generated_docs.py | support | summary | current | docs/codebase/02_modules/agent-runner-v2-cleanup-generated-docs.md | bootstrap/reconcile scan |
| agent_runner_v2/codebase_docs.py | support | summary | current | docs/codebase/02_modules/agent-runner-v2-codebase-docs.md | bootstrap/reconcile scan |
| agent_runner_v2/coder_adapters.py | coder | full | current | docs/codebase/02_modules/agent-runner-v2-coder-adapters.md | bootstrap/reconcile scan |
| agent_runner_v2/config/__init__.py | package | stub | current | docs/codebase/02_modules/agent-runner-v2-config-init.md | bootstrap/reconcile scan |
| agent_runner_v2/config/section_requirements.py | support | summary | current | docs/codebase/02_modules/agent-runner-v2-config-section-requirements.md | bootstrap/reconcile scan |
| agent_runner_v2/constants.py | support | summary | current | docs/codebase/02_modules/agent-runner-v2-constants.md | bootstrap/reconcile scan |
| agent_runner_v2/daemon.py | backend | full | current | docs/codebase/02_modules/agent-runner-v2-daemon.md | bootstrap/reconcile scan |
| agent_runner_v2/doc_paths.py | support | summary | current | docs/codebase/02_modules/agent-runner-v2-doc-paths.md | bootstrap/reconcile scan |
| agent_runner_v2/documentation_guardrails.py | support | summary | current | docs/codebase/02_modules/agent-runner-v2-documentation-guardrails.md | bootstrap/reconcile scan |
| agent_runner_v2/engine_commands.py | commands | summary | current | docs/codebase/02_modules/agent-runner-v2-engine-commands.md | bootstrap/reconcile scan |
| agent_runner_v2/exceptions.py | schema | summary | current | docs/codebase/02_modules/agent-runner-v2-exceptions.md | bootstrap/reconcile scan |
| agent_runner_v2/execution_request.py | state | summary | current | docs/codebase/02_modules/agent-runner-v2-execution-request.md | bootstrap/reconcile scan |
| agent_runner_v2/execution_result.py | state | summary | current | docs/codebase/02_modules/agent-runner-v2-execution-result.md | bootstrap/reconcile scan |
| agent_runner_v2/job_state.py | state | full | current | docs/codebase/02_modules/agent-runner-v2-job-state.md | bootstrap/reconcile scan |
| agent_runner_v2/model_config.py | coder | summary | current | docs/codebase/02_modules/agent-runner-v2-model-config.md | bootstrap/reconcile scan |
| agent_runner_v2/notification_manager.py | support | summary | current | docs/codebase/02_modules/agent-runner-v2-notification-manager.md | bootstrap/reconcile scan |
| agent_runner_v2/notifications.py | support | summary | current | docs/codebase/02_modules/agent-runner-v2-notifications.md | bootstrap/reconcile scan |
| agent_runner_v2/run_agent.py | core | full | current | docs/codebase/02_modules/agent-runner-v2-run-agent.md | bootstrap/reconcile scan |
| agent_runner_v2/runner_actions.py | schema | summary | current | docs/codebase/02_modules/agent-runner-v2-runner-actions.md | bootstrap/reconcile scan |
| agent_runner_v2/runner_logger.py | backend | full | current | docs/codebase/02_modules/agent-runner-v2-runner-logger.md | bootstrap/reconcile scan |
| agent_runner_v2/runtime_context.py | state | full | current | docs/codebase/02_modules/agent-runner-v2-runtime-context.md | bootstrap/reconcile scan |
| agent_runner_v2/site_styles.py | support | summary | current | docs/codebase/02_modules/agent-runner-v2-site-styles.md | bootstrap/reconcile scan |
| agent_runner_v2/step_runner.py | core | full | current | docs/codebase/02_modules/agent-runner-v2-step-runner.md | bootstrap/reconcile scan |
| agent_runner_v2/submit_commands.py | commands | summary | current | docs/codebase/02_modules/agent-runner-v2-submit-commands.md | bootstrap/reconcile scan |
| agent_runner_v2/submitter.py | commands | summary | current | docs/codebase/02_modules/agent-runner-v2-submitter.md | bootstrap/reconcile scan |
| agent_runner_v2/system_docs.py | support | summary | current | docs/codebase/02_modules/agent-runner-v2-system-docs.md | bootstrap/reconcile scan |
| agent_runner_v2/tools/agent_tools.py | tools | summary | current | docs/codebase/02_modules/agent-runner-v2-tools-agent-tools.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_packages/__init__.py | package | stub | current | docs/codebase/02_modules/agent-runner-v2-workflow-packages-init.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_packages/actions/__init__.py | package | stub | current | docs/codebase/02_modules/agent-runner-v2-workflow-packages-actions-init.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_packages/base.py | support | summary | current | docs/codebase/02_modules/agent-runner-v2-workflow-packages-base.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_packages/loader.py | support | summary | current | docs/codebase/02_modules/agent-runner-v2-workflow-packages-loader.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_packages/registry.py | support | summary | current | docs/codebase/02_modules/agent-runner-v2-workflow-packages-registry.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_router.py | core | full | current | docs/codebase/02_modules/agent-runner-v2-workflow-router.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_spec_commands.py | support | summary | current | docs/codebase/02_modules/agent-runner-v2-workflow-spec-commands.md | bootstrap/reconcile scan |
| agent_runner_v2/workflow_specs.py | support | summary | current | docs/codebase/02_modules/agent-runner-v2-workflow-specs.md | bootstrap/reconcile scan |

## 3. Bootstrap Workflow Files

| File Path | Description | Documentation Mode | Status | Owner Doc Path | Last Verified By Change |
|---|---|---|---|---|---|
| agent_runner_v2/bootstrap/workflows/default/job_schema.json | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/llm_response_schema.json | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/model_mapping.json | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/00_master_docs_bootstrap_v1/02_generate_project_analysis.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/00_master_docs_bootstrap_v1/03_generate_system_overview_docs.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/00_master_docs_bootstrap_v1/04_generate_architecture_docs.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/00_master_docs_bootstrap_v1/04b_generate_integration_docs.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/00_master_docs_bootstrap_v1/04c_generate_failure_docs.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/00_master_docs_bootstrap_v1/04d_generate_architecture_flow_docs.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/00_master_docs_bootstrap_v1/05_review_master_system_docs.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/00_master_docs_bootstrap_v1/06_refine_master_system_docs.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/10_execution_scaffold_v1/01_project_analysis.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/10_execution_scaffold_v1/02_generate_sop.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/10_execution_scaffold_v1/03_generate_templates.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/10_execution_scaffold_v1/03_review_sop.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/10_execution_scaffold_v1/04_generate_agents.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/10_execution_scaffold_v1/05_refine_sop.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/10_execution_scaffold_v1/05_replan_sop.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/10_execution_scaffold_v1/06_refine_templates.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/10_execution_scaffold_v1/06_review_templates.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/10_execution_scaffold_v1/07_refine_agents.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/10_execution_scaffold_v1/08_review_agents.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/20_initiative_intake_v1/01_pre_init.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/20_initiative_intake_v1/02_review_pre_init.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/20_initiative_intake_v1/03_refine_pre_init.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/21_bug_fix_intake_v1/01_triage_bug.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/21_bug_fix_intake_v1/02_reproduce_bug.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/21_bug_fix_intake_v1/03_isolate_root_cause.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/21_bug_fix_intake_v1/04_patch_bug.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/21_bug_fix_intake_v1/05_regression_validate.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/30_delivery_planning_v1/02_planner.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/30_delivery_planning_v1/03_refine_plan.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/30_delivery_planning_v1/03_replan_plan.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/30_delivery_planning_v1/03_review_planner.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/30_delivery_planning_v1/04_task_graph.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/30_delivery_planning_v1/05_refine_task_graph.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/30_delivery_planning_v1/05_replan_task_graph.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/30_delivery_planning_v1/05_review_task_graph.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/30_delivery_planning_v1/06_task.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/30_delivery_planning_v1/07_refine_task.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/30_delivery_planning_v1/07_review_task.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/31_task_execution_v1/08_impl_task.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/31_task_execution_v1/08_impl_task_qwen.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/31_task_execution_v1/09_refine_impl.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/31_task_execution_v1/09_review_impl_task.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/31_task_execution_v1/09_review_impl_task_qwen.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/31_task_execution_v1/10_executor.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/31_task_execution_v1/11_validate.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/31_task_execution_v1/11_validate_qwen.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/31_task_execution_v1/99_test.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/40_documentation_sync_v1/01_sync_docs.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/40_documentation_sync_v1/02_generate_integration_docs.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/40_documentation_sync_v1/02_review_docs.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/40_documentation_sync_v1/03_generate_failure_docs.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/40_documentation_sync_v1/03_refine_docs.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/40_documentation_sync_v1/04_generate_architecture_docs.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/40_documentation_sync_v1/04_validate_doc_sync.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/41_audience_doc_v1/01_generate_stakeholder_markdown.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/41_audience_doc_v1/02_review_developer_markdown.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/41_audience_doc_v1/02_review_markdown.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/41_audience_doc_v1/02_review_operator_markdown.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/41_audience_doc_v1/02_review_stakeholder_markdown.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/41_audience_doc_v1/02_review_tester_markdown.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/41_audience_doc_v1/02_review_user_markdown.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/41_audience_doc_v1/03_refine_developer_markdown.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/41_audience_doc_v1/03_refine_operator_markdown.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/41_audience_doc_v1/03_refine_stakeholder_markdown.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/41_audience_doc_v1/03_refine_tester_markdown.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/41_audience_doc_v1/03_refine_user_markdown.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/41_audience_doc_v1/04_generate_developer_markdown.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/41_audience_doc_v1/07_generate_operator_markdown.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/41_audience_doc_v1/10_generate_tester_markdown.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/41_audience_doc_v1/13_generate_user_markdown.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/51_stakeholder_docs_v1/04_generate_site.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/52_developer_docs_v1/01_generate_developer_site.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/52_developer_docs_v1/02_review_developer_site.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/52_developer_docs_v1/03_refine_developer_site.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/53_operator_docs_v1/01_generate_operator_site.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/53_operator_docs_v1/02_review_operator_site.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/53_operator_docs_v1/03_refine_operator_site.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/54_tester_docs_v1/01_generate_tester_site.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/54_tester_docs_v1/02_review_tester_site.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/54_tester_docs_v1/03_refine_tester_site.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/55_user_docs_v1/01_generate_user_site.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/55_user_docs_v1/02_review_user_site.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/55_user_docs_v1/03_refine_user_site.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/image_csv_gen_v1/01_extract_desc.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/image_csv_gen_v1/02_gen_prompts.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/image_csv_gen_v1/03_review_prompts.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/image_csv_gen_v1/04_refine_prompts.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/image_csv_gen_v1/05_submit_prompts.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/image_csv_gen_v2/01_extract_desc.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/image_csv_gen_v2/02_gen_prompts.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/image_csv_gen_v2/03_review_prompts.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/image_csv_gen_v2/04_refine_prompts.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/image_csv_gen_v2/05_submit_prompts.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/tiktok_video_pipeline_v1/01_extract_desc.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/tiktok_video_pipeline_v1/02_review_brief.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/tiktok_video_pipeline_v1/03_refine_brief.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/tiktok_video_pipeline_v1/04_gen_workflow.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/tiktok_video_pipeline_v1/05_review_workflow.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/tiktok_video_pipeline_v1/06_refine_workflow.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/tiktok_video_pipeline_v1/07_submit_images.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/tiktok_video_pipeline_v1/08_submit_videos.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/tiktok_video_pipeline_v1/09_submit_voiceover.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/tiktok_video_pipeline_v1/10_compose_final.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/videoxpress_gen_v1/01_extract_narrative.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/videoxpress_gen_v1/02_gen_videoxpress_workflow.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/videoxpress_gen_v1/03_review_workflow.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/videoxpress_gen_v1/04_refine_workflow.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/videoxpress_gen_v1/06_execute_t2i.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/videoxpress_gen_v1/07_execute_i2v.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/videoxpress_gen_v1/08_execute_voiceover.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/prompts/videoxpress_gen_v1/09_assemble_video.txt | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/workflows/default/usage_schema.json | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | bootstrap/reconcile scan |

## 4. Configuration / Data Files

| File Path | Format | Documentation Mode | Status | Owner Doc Path | Last Verified By Change |
|---|---|---|---|---|---|
| .env.example | example | summary | current | docs/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/00DOC-20260710-15f76235-bootstrap-validation.meta.json | json | summary | current | docs/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/00DOC-20260710-15f76235-bootstrap-validation.meta.meta.json | json | summary | current | docs/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| agent_runner_v2/comfyui_config.json | json | summary | current | docs/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| agent_runner_v2/job_schema.json | json | summary | current | docs/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| agent_runner_v2/llm_response_schema.json | json | summary | current | docs/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| agent_runner_v2/model_mapping.json | json | summary | current | docs/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| agent_runner_v2/usage_schema.json | json | summary | current | docs/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/codebase/04_changes/00DOC-GEN-20260710-001-bootstrap-snapshot.json | json | summary | current | docs/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/codebase/04_changes/00DOC-GEN-20260710-002-bootstrap-snapshot.json | json | summary | current | docs/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/codebase/04_changes/00DOC-GEN-20260710-003-bootstrap-snapshot.json | json | summary | current | docs/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| docs/codebase/04_changes/00DOC-GEN-20260710-004-bootstrap-snapshot.json | json | summary | current | docs/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| pyproject.toml | toml | summary | current | docs/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |
| workflows/00_master_docs_bootstrap_v2/workflow.toml | toml | summary | current | docs/codebase/03_components/config-and-data.md | bootstrap/reconcile scan |

## 5. Scripts

| File Path | Type | Documentation Mode | Status | Owner Doc Path | Last Verified By Change |
|---|---|---|---|---|---|
| archive/batch/run-bug_fix_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| archive/batch/run-codebase_bootstrap_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| archive/batch/run-codebase_reconcile_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| archive/batch/run-codebase_rescan_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| archive/batch/run-codebase_sync_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| archive/batch/run-documentation_bootstrap_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| archive/batch/run-documentation_validation_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| archive/batch/run-system_docs_bootstrap_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| archive/batch/submit-bug_fix_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| archive/batch/submit-codebase_bootstrap_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| archive/batch/submit-codebase_reconcile_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| archive/batch/submit-codebase_rescan_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| archive/batch/submit-codebase_sync_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| archive/batch/submit-documentation_bootstrap_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| archive/batch/submit-documentation_validation_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-00_master_docs_bootstrap_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-00_master_docs_bootstrap_v2.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-10_execution_scaffold_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-20_initiative_intake_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-21_bug_fix_intake_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-30_delivery_planning_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-31_task_execution_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-40_documentation_sync_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-41_developer_doc_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-41_operator_doc_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-41_stakeholder_doc_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-41_tester_doc_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-41_user_doc_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-50_architecture_site_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-51_stakeholder_docs_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-52_developer_docs_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-53_operator_docs_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-54_tester_docs_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-55_user_docs_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-all-tests.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-approve-step.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-bootstrap-publish.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-cleanup-generated-docs.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-daemon.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-integration-tests.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-reset-step.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| run-tests.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| sample-run-delivery.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| scripts/approve-run.sh | .sh | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| scripts/examples/approve-run.sh | .sh | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| scripts/examples/submit-delivery-planning.sh | .sh | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| scripts/examples/submit-delivery-scaffold.sh | .sh | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| scripts/examples/submit-image-csv-gen-v1.sh | .sh | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| scripts/examples/submit-image-csv-gen-v2.sh | .sh | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| scripts/examples/submit-initiative-intake.sh | .sh | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| scripts/examples/submit-task-execution.sh | .sh | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| scripts/README.md | .md | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| scripts/submit-delivery-planning.sh | .sh | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| scripts/submit-delivery-scaffold.sh | .sh | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| scripts/submit-initiative-intake.sh | .sh | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| scripts/ukbe-daemon-wsl.sh | .sh | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| scripts/ukbe-daemon.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| scripts/ukbe-run-delivery.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| scripts/ukbe-runner.sh | .sh | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-00_master_docs_bootstrap_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-10_execution_scaffold_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-40_documentation_sync_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| submit-41_audience_doc_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| sync-10_execution_scaffold_v1-workflow-spec.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| sync-workflows-to-backend.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |
| test-runner.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | bootstrap/reconcile scan |

## 6. Test Files

| File Path | Coverage Area | Documentation Mode | Status | Owner Doc Path | Last Verified By Change |
|---|---|---|---|---|---|
| tests/conftest.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/integration/__init__.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/integration/test_architecture_site.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/integration/test_backend_worker_mode.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/integration/test_daemon.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/integration/test_notification_e2e.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/integration/test_notification_integration.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/integration/test_notifications.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/integration/test_pushover.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/integration/test_ukbe_runner_wrapper.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/__init__.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_agent_tools.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_bundle_loader.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_codebase_docs.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_coder_adapters_sidecar_grace.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_constants_registry.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_context_extensions.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_documentation_governance.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_documentation_guardrails_cleanup.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_run_agent_status.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_runtime_context_paths.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_step_runner_write_contract.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_tool_instruction_block.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_workflow_packages.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |
| tests/unit/test_workflow_registry.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | bootstrap/reconcile scan |

## 7. Documentation Files

| File Path | Category | Documentation Mode | Status | Owner Doc Path | Last Verified By Change |
|---|---|---|---|---|---|
| agent_runner_v2/bootstrap/bundles/core/current/00DOC-20260710-15f76235-bootstrap-change-log.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/00DOC-20260710-15f76235-bootstrap-summary.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/00DOC-20260710-15f76235-bootstrap-validation.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/BUNDLE_MIGRATION_PLAN.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/BUNDLE_TAXONOMY.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/BUSINESS_CAPABILITIES.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/COMPONENT_ARCHITECTURE.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/DECISION_LOG.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/DEVELOPER_GUIDE.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/DOCUMENTATION_STANDARD.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/EXISTING_REPO_WORKFLOW_SOP.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/FUNCTIONAL_SPEC.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/NON_FUNCTIONAL_REQUIREMENTS.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/project_analysis.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/README.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/RUNBOOK.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/SYSTEM_CONTEXT.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/SYSTEM_FILE_STRUCTURE.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/bundles/core/current/SYSTEM_OVERVIEW.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/themes/default/layout.html | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/image_csv_generation.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/QWEN.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| archive/batch/README.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| CLAUDE.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| CODER_IMPLEMENTATION_SOP.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| HOW_TO_GUIDE.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| PUSHOVER_NOTIFICATIONS.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| QWEN.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| README.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| tests/integration/README.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| tests/unit/README.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| TODO_LIST.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| UNIT_TEST_FIXES.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| UNIT_TEST_RESULTS.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| WINDOWS_COMPATIBILITY.md | docs | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |

## 8. Other Files

| File Path | Category | Documentation Mode | Status | Owner Doc Path | Last Verified By Change |
|---|---|---|---|---|---|
| .gitignore | other | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| agent_runner_v2/bootstrap/themes/default/theme.css | other | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| archive/_gen_stakeholder_html.py | other | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| count_workflows.py | other | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| MANIFEST.in | other | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| requirements.txt | other | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| test-runner.ps1 | other | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| test_script.py | other | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_master_docs_bootstrap_v2/actions.py | other | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_master_docs_bootstrap_v2/context_extensions.py | other | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_master_docs_bootstrap_v2/prompts/02_generate_project_analysis.txt | other | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_master_docs_bootstrap_v2/prompts/03_generate_system_overview_docs.txt | other | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_master_docs_bootstrap_v2/prompts/04_generate_architecture_docs.txt | other | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_master_docs_bootstrap_v2/prompts/04b_generate_integration_docs.txt | other | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_master_docs_bootstrap_v2/prompts/04c_generate_failure_docs.txt | other | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_master_docs_bootstrap_v2/prompts/04d_generate_architecture_flow_docs.txt | other | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_master_docs_bootstrap_v2/prompts/05_review_master_system_docs.txt | other | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |
| workflows/00_master_docs_bootstrap_v2/prompts/06_refine_master_system_docs.txt | other | summary | current | docs/codebase/03_components/codebase-governance.md | bootstrap/reconcile scan |

## 9. Summary Statistics

| Category | Total Files | Current | Needs Update | Pending Review | Superseded |
|---|---|---|---|---|---|
| configuration/data files | 14 | 14 | 0 | 0 | 0 |
| other files | 18 | 18 | 0 | 0 | 0 |
| python modules | 72 | 72 | 0 | 0 | 0 |
| documentation files | 35 | 35 | 0 | 0 | 0 |
| bootstrap workflow files | 115 | 115 | 0 | 0 | 0 |
| scripts | 66 | 66 | 0 | 0 | 0 |
| test files | 25 | 25 | 0 | 0 | 0 |

## 10. Status Legend

- `current`: documentation is up to date and matches the source
- `needs_update`: source changed and documentation is stale
- `pending_review`: documentation exists but has not been verified
- `superseded`: documentation is obsolete or replaced

## 11. Verification Log

| Date | Verified By | Scope | Result |
|---|---|---|---|
| 2026-07-10 | 00_master_docs_bootstrap_v2 | repository scan | complete |

