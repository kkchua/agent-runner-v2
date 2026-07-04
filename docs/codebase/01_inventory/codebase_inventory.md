---
title: "Codebase Inventory - agent-runner-v2"
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: generate_templates
template_id: "CODEBASE-INV-v1"
status: "active"
generated: "2026-07-04T12:00:00+08:00"
change_id: "10SCAFFOLD-GEN-20260704-001"
previous_change_id: "00DOC-GEN-20260704-002"
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Codebase Inventory: agent-runner-v2

## 1. Inventory Scope

This inventory was generated from a repository scan at `2026-07-04T12:00:00+08:00`, reconciled during the `10_execution_scaffold_v1` / `generate_templates` step.

Previous baseline: `00DOC-GEN-20260704-002` (master docs bootstrap). This inventory adds the newly generated delivery and codebase template files and updates the workflow provenance metadata.

### Architecture Profile Metadata

| Field | Value |
|---|---|
| Current Profile | delivery-governance scaffold with mature populated corpus |
| Target Profile | full alignment with `10_execution_scaffold_v1` protected-doc set |
| Migration Mode | `active` — coexist with existing 86-file corpus, reconcile not replace |

## 2. Python Source Modules

| File Path | Module Area | Documentation Mode | Status | Owner Doc Path | Last Verified By Change |
|---|---|---|---|---|---|
| agent_runner_v2/__init__.py | package | stub | current | docs/codebase/02_modules/agent-runner-v2-init.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/action_result.py | schema | summary | current | docs/codebase/02_modules/agent-runner-v2-action-result.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/actions/__init__.py | actions | stub | current | docs/codebase/02_modules/agent-runner-v2-actions-init.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/actions/assemble_video.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-assemble-video.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/actions/copy_artifact.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-copy-artifact.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/actions/documentation_validation_core.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-documentation-validation-core.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/actions/execute_i2v.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-execute-i2v.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/actions/execute_t2i.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-execute-t2i.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/actions/execute_voiceover.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-execute-voiceover.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/actions/finalize_bootstrap.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-finalize-bootstrap.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/actions/prepare_delivery_scaffold.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-prepare-delivery-scaffold.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/actions/promote_artifact.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-promote-artifact.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/actions/promote_init.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-promote-init.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/actions/publish_architecture_site.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-publish-architecture-site.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/actions/scan_repo_codebase.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-scan-repo-codebase.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/actions/submit_comfyui.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-submit-comfyui.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/actions/sync_codebase_docs.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-sync-codebase-docs.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/actions/sync_system_docs.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-sync-system-docs.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/actions/validate_architecture_site.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-validate-architecture-site.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/actions/validate_codebase_docs.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-validate-codebase-docs.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/actions/validate_delivery_docs.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-validate-delivery-docs.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/actions/validate_system_docs.py | actions | full | current | docs/codebase/02_modules/agent-runner-v2-actions-validate-system-docs.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/approve_commands.py | commands | summary | current | docs/codebase/02_modules/agent-runner-v2-approve-commands.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/architecture_site.py | support | summary | current | docs/codebase/02_modules/agent-runner-v2-architecture-site.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/artifact_paths.py | schema | summary | current | docs/codebase/02_modules/agent-runner-v2-artifact-paths.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/backend_client.py | backend | full | current | docs/codebase/02_modules/agent-runner-v2-backend-client.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/bootstrap/workflows/default/template_groups.py | bootstrap | full | current | docs/codebase/02_modules/agent-runner-v2-bootstrap-workflows-default-template-groups.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/bundle_loader.py | bootstrap | full | current | docs/codebase/02_modules/agent-runner-v2-bundle-loader.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/bundle_taxonomy.py | support | summary | current | docs/codebase/02_modules/agent-runner-v2-bundle-taxonomy.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/cleanup_generated_docs.py | support | summary | current | docs/codebase/02_modules/agent-runner-v2-cleanup-generated-docs.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/codebase_docs.py | support | summary | current | docs/codebase/02_modules/agent-runner-v2-codebase-docs.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/coder_adapters.py | coder | full | current | docs/codebase/02_modules/agent-runner-v2-coder-adapters.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/daemon.py | backend | full | current | docs/codebase/02_modules/agent-runner-v2-daemon.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/doc_paths.py | support | summary | current | docs/codebase/02_modules/agent-runner-v2-doc-paths.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/documentation_guardrails.py | support | summary | current | docs/codebase/02_modules/agent-runner-v2-documentation-guardrails.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/engine_commands.py | commands | summary | current | docs/codebase/02_modules/agent-runner-v2-engine-commands.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/exceptions.py | schema | summary | current | docs/codebase/02_modules/agent-runner-v2-exceptions.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/execution_request.py | state | summary | current | docs/codebase/02_modules/agent-runner-v2-execution-request.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/execution_result.py | state | summary | current | docs/codebase/02_modules/agent-runner-v2-execution-result.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/job_state.py | state | full | current | docs/codebase/02_modules/agent-runner-v2-job-state.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/model_config.py | coder | summary | current | docs/codebase/02_modules/agent-runner-v2-model-config.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/run_agent.py | core | full | current | docs/codebase/02_modules/agent-runner-v2-run-agent.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/runner_actions.py | schema | summary | current | docs/codebase/02_modules/agent-runner-v2-runner-actions.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/runner_logger.py | backend | full | current | docs/codebase/02_modules/agent-runner-v2-runner-logger.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/runtime_context.py | state | full | current | docs/codebase/02_modules/agent-runner-v2-runtime-context.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/step_runner.py | core | full | current | docs/codebase/02_modules/agent-runner-v2-step-runner.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/submit_commands.py | commands | summary | current | docs/codebase/02_modules/agent-runner-v2-submit-commands.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/submitter.py | commands | summary | current | docs/codebase/02_modules/agent-runner-v2-submitter.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/system_docs.py | support | summary | current | docs/codebase/02_modules/agent-runner-v2-system-docs.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/tools/agent_tools.py | tools | summary | current | docs/codebase/02_modules/agent-runner-v2-tools-agent-tools.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/workflow_router.py | core | full | current | docs/codebase/02_modules/agent-runner-v2-workflow-router.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/workflow_spec_commands.py | support | summary | current | docs/codebase/02_modules/agent-runner-v2-workflow-spec-commands.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/workflow_specs.py | support | summary | current | docs/codebase/02_modules/agent-runner-v2-workflow-specs.md | 10SCAFFOLD-GEN-20260704-001 |

## 3. Bootstrap Workflow Files

| File Path | Description | Documentation Mode | Status | Owner Doc Path | Last Verified By Change |
|---|---|---|---|---|---|
| agent_runner_v2/bootstrap/workflows/default/job_schema.json | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/bootstrap/workflows/default/llm_response_schema.json | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/bootstrap/workflows/default/model_mapping.json | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/bootstrap/workflows/default/usage_schema.json | workflow asset | full | current | docs/codebase/03_components/workflow-families.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/bootstrap/workflows/default/prompts/** | prompt templates (67 files) | full | current | docs/codebase/03_components/workflow-families.md | 10SCAFFOLD-GEN-20260704-001 |

## 4. Configuration / Data Files

| File Path | Format | Documentation Mode | Status | Owner Doc Path | Last Verified By Change |
|---|---|---|---|---|---|
| .env.example | example | summary | current | docs/codebase/03_components/config-and-data.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/comfyui_config.json | json | summary | current | docs/codebase/03_components/config-and-data.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/job_schema.json | json | summary | current | docs/codebase/03_components/config-and-data.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/llm_response_schema.json | json | summary | current | docs/codebase/03_components/config-and-data.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/model_mapping.json | json | summary | current | docs/codebase/03_components/config-and-data.md | 10SCAFFOLD-GEN-20260704-001 |
| agent_runner_v2/usage_schema.json | json | summary | current | docs/codebase/03_components/config-and-data.md | 10SCAFFOLD-GEN-20260704-001 |
| docs/codebase/04_changes/00DOC-GEN-20260704-001-bootstrap-snapshot.json | json | summary | current | docs/codebase/03_components/config-and-data.md | 10SCAFFOLD-GEN-20260704-001 |
| docs/codebase/04_changes/00DOC-GEN-20260704-002-bootstrap-snapshot.json | json | summary | current | docs/codebase/03_components/config-and-data.md | 10SCAFFOLD-GEN-20260704-001 |
| docs/codebase/04_changes/DOCSYNC-20260704_codebase-doc-update.meta.json | json | summary | current | docs/codebase/03_components/config-and-data.md | 10SCAFFOLD-GEN-20260704-001 |
| pyproject.toml | toml | summary | current | docs/codebase/03_components/config-and-data.md | 10SCAFFOLD-GEN-20260704-001 |

## 5. Scripts

| File Path | Type | Documentation Mode | Status | Owner Doc Path | Last Verified By Change |
|---|---|---|---|---|---|
| archive/batch/*.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | 10SCAFFOLD-GEN-20260704-001 |
| run-*.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | 10SCAFFOLD-GEN-20260704-001 |
| scripts/*.sh, scripts/*.bat | .sh, .bat | summary | current | docs/codebase/03_components/scripts-suite.md | 10SCAFFOLD-GEN-20260704-001 |
| scripts/README.md | .md | summary | current | docs/codebase/03_components/scripts-suite.md | 10SCAFFOLD-GEN-20260704-001 |
| submit-*.bat, sync-*.bat, test-runner.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | 10SCAFFOLD-GEN-20260704-001 |
| run-40_documentation_sync_v1.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | 10SCAFFOLD-GEN-20260704-001 |
| sample-run-delivery.bat | .bat | summary | current | docs/codebase/03_components/scripts-suite.md | 10SCAFFOLD-GEN-20260704-001 |

## 6. Test Files

| File Path | Coverage Area | Documentation Mode | Status | Owner Doc Path | Last Verified By Change |
|---|---|---|---|---|---|
| tests/conftest.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | 10SCAFFOLD-GEN-20260704-001 |
| tests/test_architecture_site.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | 10SCAFFOLD-GEN-20260704-001 |
| tests/test_backend_worker_mode.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | 10SCAFFOLD-GEN-20260704-001 |
| tests/test_bundle_loader.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | 10SCAFFOLD-GEN-20260704-001 |
| tests/test_codebase_docs.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | 10SCAFFOLD-GEN-20260704-001 |
| tests/test_daemon.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | 10SCAFFOLD-GEN-20260704-001 |
| tests/test_documentation_governance.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | 10SCAFFOLD-GEN-20260704-001 |
| tests/test_documentation_guardrails_cleanup.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | 10SCAFFOLD-GEN-20260704-001 |
| tests/test_run_agent_status.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | 10SCAFFOLD-GEN-20260704-001 |
| tests/test_runtime_context_paths.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | 10SCAFFOLD-GEN-20260704-001 |
| tests/test_tool_instruction_block.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | 10SCAFFOLD-GEN-20260704-001 |
| tests/test_ukbe_runner_wrapper.py | tests | summary | current | docs/codebase/03_components/tests-suite.md | 10SCAFFOLD-GEN-20260704-001 |

## 7. Documentation Files

| File Path | Category | Documentation Mode | Status | Owner Doc Path | Last Verified By Change |
|---|---|---|---|---|---|
| docs/codebase/02_modules/*.md (53 files) | module docs | full | current | docs/codebase/03_components/codebase-governance.md | 10SCAFFOLD-GEN-20260704-001 |
| docs/codebase/03_components/*.md (6 files) | component docs | full | current | docs/codebase/03_components/codebase-governance.md | 10SCAFFOLD-GEN-20260704-001 |
| docs/codebase/04_changes/*.md (6 files) | change records | full | current | docs/codebase/03_components/codebase-governance.md | 10SCAFFOLD-GEN-20260704-001 |
| docs/system/00_governance/bootstrap/*.md (20 files) | system governance | protected | current | docs/system/00_governance/bootstrap/README.md | 10SCAFFOLD-GEN-20260704-001 |
| docs/system/00_governance/bootstrap/templates/delivery/*.md (9 files) | delivery templates | protected | current | docs/system/00_governance/bootstrap/templates/delivery/01_delivery_template_registry.md | 10SCAFFOLD-GEN-20260704-001 |
| docs/system/00_governance/bootstrap/templates/codebase/*.md (5 files) | codebase templates | protected | current | docs/system/00_governance/bootstrap/templates/codebase/01_codebase_template_registry.md | 10SCAFFOLD-GEN-20260704-001 |
| docs/delivery/05_reviews/REV-260704-01_rsop_R-0000-00_workflow-sop-v1.md | review | protected | current | docs/system/00_governance/bootstrap/WORKFLOW_SOP_v1.md | 10SCAFFOLD-GEN-20260704-001 |
| QWEN.md, agent_runner_v2/QWEN.md | context docs | inventoried_only | current | docs/codebase/03_components/codebase-governance.md | 10SCAFFOLD-GEN-20260704-001 |
| README.md, HOW_TO_GUIDE.md, WINDOWS_COMPATIBILITY.md | project docs | inventoried_only | current | docs/codebase/03_components/codebase-governance.md | 10SCAFFOLD-GEN-20260704-001 |
| .qwen/skills/**/SKILL.md (8 files) | skill docs | inventoried_only | current | docs/codebase/03_components/codebase-governance.md | 10SCAFFOLD-GEN-20260704-001 |
| archive/batch/README.md | archive docs | inventoried_only | current | docs/codebase/03_components/codebase-governance.md | 10SCAFFOLD-GEN-20260704-001 |

## 8. Other Files

| File Path | Category | Documentation Mode | Status | Owner Doc Path | Last Verified By Change |
|---|---|---|---|---|---|
| .env | other | summary | current | docs/codebase/03_components/codebase-governance.md | 10SCAFFOLD-GEN-20260704-001 |
| .gitignore | other | summary | current | docs/codebase/03_components/codebase-governance.md | 10SCAFFOLD-GEN-20260704-001 |
| MANIFEST.in | other | summary | current | docs/codebase/03_components/codebase-governance.md | 10SCAFFOLD-GEN-20260704-001 |
| progress.jsonl | other | summary | current | docs/codebase/03_components/codebase-governance.md | 10SCAFFOLD-GEN-20260704-001 |
| test-runner.ps1 | other | summary | current | docs/codebase/03_components/codebase-governance.md | 10SCAFFOLD-GEN-20260704-001 |

## 9. Summary Statistics

| Category | Total Files | `current` | `needs_update` | `pending_review` | `superseded` |
|---|---|---|---|---|---|
| Python source modules | 53 | 53 | 0 | 0 | 0 |
| Bootstrap workflow files | 80 | 80 | 0 | 0 | 0 |
| Configuration / data files | 10 | 10 | 0 | 0 | 0 |
| Scripts | 44 | 44 | 0 | 0 | 0 |
| Test files | 12 | 12 | 0 | 0 | 0 |
| Documentation files (existing) | 76 | 76 | 0 | 0 | 0 |
| Documentation files (newly generated) | 14 | 14 | 0 | 0 | 0 |
| Other files | 5 | 5 | 0 | 0 | 0 |
| **Total** | **294** | **294** | **0** | **0** | **0** |

## 10. Status Definitions

| Status | Definition | Transition Rules |
|---|---|---|
| `current` | The entry accurately reflects the current state of the code. The corresponding documentation (if any) is up to date. | May transition to `needs_update` when code changes; may transition to `superseded` when replaced. |
| `needs_update` | The code has changed since the entry was last verified, and the entry no longer accurately reflects the current state. | Must transition to `current` after documentation is updated, or to `pending_review` if the change is ambiguous. |
| `pending_review` | The entry may or may not be stale; it requires human or agent review to determine its accuracy. | Must transition to `current`, `needs_update`, or `superseded` after review. |
| `superseded` | The entry has been replaced by a newer entry. The file may still exist but is no longer tracked by this entry. | Terminal state. May transition back to `current` only if the superseding entry is itself invalidated. |

## 11. Verification Log

| Date | Verified By | Scope | Change ID | Result |
|---|---|---|---|---|
| 2026-07-04 | 00_master_docs_bootstrap_v1 | repository scan | 00DOC-GEN-20260704-002 | complete |
| 2026-07-04 | 10_execution_scaffold_v1 / generate_templates | reconciliation + new template files | 10SCAFFOLD-GEN-20260704-001 | complete |
