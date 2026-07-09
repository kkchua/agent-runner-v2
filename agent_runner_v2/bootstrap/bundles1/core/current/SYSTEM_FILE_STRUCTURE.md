---
template_id: "SYS-03-SF"
title: "System File Structure - agent-runner-v2"
status: "active"
generated: "2026-07-08T23:26:47+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-20260708-78fb419e"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# System File Structure: agent-runner-v2

## Repository Structure

```
agent-runner-v2/
├── agent_runner_v2/              # Main Python package
│   ├── __init__.py                 # Package init
│   ├── run_agent.py                # CLI entry point (2329 lines)
│   ├── step_runner.py              # Core step execution (2437 lines)
│   ├── workflow_router.py          # Post-step routing (787 lines)
│   ├── job_state.py                # Job.json lifecycle (1806 lines)
│   ├── runtime_context.py          # Process-local context (301 lines)
│   ├── coder_adapters.py           # LLM invocation
│   ├── constants.py                # Centralized path constants (677 lines)
│   ├── doc_paths.py                # Path resolution helpers
│   ├── artifact_paths.py           # Artifact path computation
│   ├── workflow_specs.py           # Workflow specification loading
│   ├── template_groups.py          # Template group definitions
│   ├── bundle_loader.py            # Bootstrap seeding
│   ├── documentation_guardrails.py # Validation rules
│   ├── notifications.py              # Notification utilities
│   ├── notification_manager.py     # Notification orchestration
│   ├── backend_client.py           # Backend API client
│   ├── runner_logger.py            # Structured logging
│   ├── daemon.py                   # Workstation supervisor
│   ├── action_result.py            # Action result schemas
│   ├── artifact_paths.py           # Artifact path computation
│   ├── approve_commands.py         # Approval CLI commands
│   ├── architecture_site.py        # HTML site generation
│   ├── bundle_taxonomy.py          # Bundle taxonomy
│   ├── cleanup_generated_docs.py   # Doc cleanup utilities
│   ├── codebase_docs.py            # Codebase doc utilities
│   ├── config/                     # Configuration modules
│   │   ├── __init__.py
│   │   └── section_requirements.py
│   ├── actions/                    # 25+ deterministic runner actions
│   │   ├── __init__.py
│   │   ├── archive_previous_version.py
│   │   ├── assemble_video.py
│   │   ├── copy_artifact.py
│   │   ├── documentation_validation_core.py
│   │   ├── execute_i2v.py
│   │   ├── execute_t2i.py
│   │   ├── execute_voiceover.py
│   │   ├── finalize_bootstrap.py
│   │   ├── generate_site.py
│   │   ├── generate_site_pdf.py
│   │   ├── prepare_delivery_scaffold.py
│   │   ├── promote_artifact.py
│   │   ├── promote_init.py
│   │   ├── publish_architecture_site.py
│   │   ├── scan_repo_codebase.py
│   │   ├── submit_comfyui.py
│   │   ├── sync_codebase_docs.py
│   │   ├── sync_system_docs.py
│   │   ├── validate_architecture_site.py
│   │   ├── validate_codebase_docs.py
│   │   ├── validate_delivery_docs.py
│   │   ├── validate_developer_site.py
│   │   ├── validate_operator_site.py
│   │   ├── validate_stakeholder_site.py
│   │   ├── validate_system_docs.py
│   │   ├── validate_tester_site.py
│   │   └── validate_user_site.py
│   ├── bootstrap/                  # Packaged bootstrap content
│   │   ├── workflows/default/      # Workflow definitions
│   │   │   ├── template_groups.py  # 19 workflow families
│   │   │   ├── job_schema.json     # Job schema
│   │   │   ├── llm_response_schema.json
│   │   │   ├── model_mapping.json  # Model aliases
│   │   │   └── prompts/            # Step prompts (100+ files)
│   │   │       ├── 00_master_docs_bootstrap_v1/
│   │   │       ├── 10_execution_scaffold_v1/
│   │   │       ├── 20_initiative_intake_v1/
│   │   │       ├── 21_bug_fix_intake_v1/
│   │   │       ├── 30_delivery_planning_v1/
│   │   │       ├── 31_task_execution_v1/
│   │   │       ├── 40_documentation_sync_v1/
│   │   │       ├── 41_audience_doc_v1/
│   │   │       ├── 50_architecture_site_v1/
│   │   │       └── ... (other workflows)
│   │   ├── bundles/core/current/   # Master documentation bundle
│   │   │   ├── README.md
│   │   │   ├── PROJECT_ANALYSIS.md
│   │   │   ├── DOCUMENTATION_STANDARD.md
│   │   │   ├── SYSTEM_OVERVIEW.md
│   │   │   ├── BUSINESS_CAPABILITIES.md
│   │   │   ├── FUNCTIONAL_SPEC.md
│   │   │   ├── NON_FUNCTIONAL_REQUIREMENTS.md
│   │   │   ├── SYSTEM_CONTEXT.md
│   │   │   ├── COMPONENT_ARCHITECTURE.md
│   │   │   ├── DECISION_LOG.md
│   │   │   ├── SYSTEM_FILE_STRUCTURE.md
│   │   │   ├── DEVELOPER_GUIDE.md
│   │   │   ├── RUNBOOK.md
│   │   │   ├── EXISTING_REPO_WORKFLOW_SOP.md
│   │   │   ├── BUNDLE_TAXONOMY.md
│   │   │   ├── BUNDLE_MIGRATION_PLAN.md
│   │   │   └── templates/
│   │   └── themes/default/         # HTML site themes
│   │       └── layout.html
│   └── tools/                      # Utility tools
│       └── agent_tools.py          # Agent tool utilities
├── docs/                           # Documentation output
│   ├── system/00_governance/bootstrap/  # Generated system docs
│   │   ├── README.md
│   │   ├── PROJECT_ANALYSIS.md
│   │   └── ... (this document set)
│   ├── codebase/
│   │   ├── 01_inventory/           # Codebase inventory
│   │   │   └── codebase_inventory.md
│   │   ├── 02_modules/             # Per-module docs (67 files)
│   │   ├── 03_components/          # Component docs (6 files)
│   │   └── 04_changes/             # Change impact docs
│   └── delivery/                   # Delivery artifacts
│       ├── 01_initiatives/
│       ├── 02_plans/
│       ├── 03_task_graphs/
│       ├── 04_tasks/
│       ├── 05_implementations/
│       ├── 06_reviews/
│       └── 07_validations/
├── tests/                          # Test suite
│   ├── unit/                       # Pure unit tests
│   ├── integration/                # Integration tests
│   └── conftest.py
├── scripts/                        # Helper scripts
│   └── ukbe-run-delivery.bat       # Core delivery runner
├── run-*.bat                       # 26 workflow launcher batch files
├── pyproject.toml                  # Package configuration
├── requirements.txt                # Dependencies
├── README.md                       # Usage documentation
├── QWEN.md                         # Qwen Code context
├── CLAUDE.md                       # Claude context
├── HOW_TO_GUIDE.md                 # User guide
└── .env.example                    # Environment template
```

## Top-Level Directories

| Directory | Purpose | Key Contents |
|-----------|---------|--------------|
| `agent_runner_v2/` | Main package | 67 Python modules, bootstrap content, actions |
| `docs/` | Generated documentation | System docs, codebase docs, delivery artifacts |
| `tests/` | Test suite | Unit and integration tests |
| `scripts/` | Helper scripts | `ukbe-run-delivery.bat` |
| `run-*.bat` | Workflow launchers | 26 batch files for workflow invocation |

## Documentation Locations

| Type | Location | Generated By |
|------|----------|--------------|
| **System Documentation** | `docs/system/00_governance/bootstrap/` | 00_master_docs_bootstrap_v1 |
| **Codebase Inventory** | `docs/codebase/01_inventory/` | scan_repo_codebase action |
| **Module Documentation** | `docs/codebase/02_modules/` | 67 module docs |
| **Component Documentation** | `docs/codebase/03_components/` | 6 component docs |
| **Change Impact** | `docs/codebase/04_changes/` | Documentation sync |
| **Delivery Artifacts** | `docs/delivery/` | Delivery workflows |

## Runtime Locations (Global)

| Location | Path | Purpose |
|----------|------|---------|
| **Runner Home** | `%USERPROFILE%\.ukbe-runner\` | Global state and config |
| **Config** | `%USERPROFILE%\.ukbe-runner\config.json` | User configuration |
| **Workflows** | `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\` | Runtime workflow bundles |
| **Jobs** | `%USERPROFILE%\.ukbe-runner\jobs\<workflow>\<job_id>\` | Job state and sidecars |
| **Logs** | `%USERPROFILE%\.ukbe-runner\logs\` | Execution logs |

---

*Generated by workflow: 00_master_docs_bootstrap_v1 | Step: 04_generate_architecture_docs | Change: 00DOC-20260708-78fb419e*
