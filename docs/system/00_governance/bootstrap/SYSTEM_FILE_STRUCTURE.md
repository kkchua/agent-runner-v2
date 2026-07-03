---
template_id: "SYS-03-SF"
title: "System File Structure - agent-runner-v2"
status: "active"
generated: "2026-07-04T10:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260704-001"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# System File Structure: agent-runner-v2

## Repository Structure

```
D:\MyProjectSpace\01_Workflows\agent-runner-v2\
├───.env.example                    # Environment variable template
├───.gitignore                      # Git ignore patterns
├───HOW_TO_GUIDE.md                 # Delivery scaffold workflow guide
├───MANIFEST.in                     # Package manifest for distribution
├───pyproject.toml                  # Python project configuration
├───QWEN.md                         # Qwen Code context for this repo
├───README.md                       # Repository quick start guide
│
├───agent_runner_v2/                # Core Python package (40+ modules)
│   ├───__init__.py                 # Package initialization
│   ├───run_agent.py                # CLI entry point (~2100 lines)
│   ├───step_runner.py              # Step execution engine (~2000 lines)
│   ├───workflow_router.py          # Post-step routing (~774 lines)
│   ├───job_state.py                # Job lifecycle management (~1781 lines)
│   ├───coder_adapters.py           # LLM provider adapters (~1013 lines)
│   ├───runtime_context.py         # Process-local runtime context (~281 lines)
│   ├───bundle_loader.py            # Workflow bundle loading (~188 lines)
│   ├───backend_client.py          # Backend HTTP API client
│   ├───daemon.py                   # Workstation supervisor
│   ├───documentation_guardrails.py # Generated doc protection
│   ├───*.py                        # Additional core modules
│   │
│   ├───actions/                    # Deterministic runner actions (18 modules)
│   │   ├───__init__.py             # Action registry
│   │   ├───scan_repo_codebase.py   # Repository structure analysis
│   │   ├───sync_codebase_docs.py   # Codebase doc synchronization
│   │   ├───sync_system_docs.py     # System doc synchronization
│   │   ├───validate_*.py           # Validation actions (5 modules)
│   │   ├───execute_*.py            # Media generation actions (3 modules)
│   │   └───...                     # Additional action modules
│   │
│   ├───bootstrap/                   # Packaged workflow definitions
│   │   └───workflows/default/
│   │       ├───template_groups.py  # Workflow definitions (~3000 lines)
│   │       ├───*.json              # JSON schemas (job, LLM response, usage)
│   │       └───prompts/            # Prompt templates (10 workflow families)
│   │           ├───00_master_docs_bootstrap_v1/
│   │           ├───10_execution_scaffold_v1/
│   │           ├───20_initiative_intake_v1/
│   │           ├───21_bug_fix_intake_v1/
│   │           ├───30_delivery_planning_v1/
│   │           ├───31_task_execution_v1/
│   │           ├───40_documentation_sync_v1/
│   │           ├───image_csv_gen_v2/
│   │           ├───videoxpress_gen_v1/
│   │           └───tiktok_video_pipeline_v1/
│   │
│   └───tools/                      # Utility tooling
│       └───agent_tools.py          # Agent helper functions
│
├───archive/                        # Deprecated/legacy files
│   └───batch/                      # Legacy batch scripts (archived)
│
├───docs/                           # Documentation
│   ├───codebase/                   # Codebase documentation
│   │   ├───01_inventory/           # Codebase inventory
│   │   ├───02_modules/             # Per-module documentation (49 files)
│   │   ├───03_components/          # Component documentation (6 files)
│   │   └───04_changes/             # Change impact documents
│   │
│   ├───operations/                 # Operational manuals
│   │   ├───DAEMON_MODE_QUICKSTART.md
│   │   └───EXISTING_REPO_WORKFLOW_SOP.md
│   │
│   ├───system/                     # System documentation
│   │   └───00_governance/bootstrap/ # Master system docs
│   │       ├───README.md           # Documentation index
│   │       ├───project_analysis.md # Project analysis
│   │       ├───DOCUMENTATION_STANDARD.md
│   │       ├───BUNDLE_TAXONOMY.md
│   │       ├───BUNDLE_MIGRATION_PLAN.md
│   │       ├───SYSTEM_OVERVIEW.md
│   │       ├───BUSINESS_CAPABILITIES.md
│   │       ├───FUNCTIONAL_SPEC.md
│   │       ├───NON_FUNCTIONAL_REQUIREMENTS.md
│   │       ├───SYSTEM_CONTEXT.md   # This file
│   │       ├───COMPONENT_ARCHITECTURE.md
│   │       ├───DECISION_LOG.md
│   │       ├───SYSTEM_FILE_STRUCTURE.md
│   │       ├───DEVELOPER_GUIDE.md
│   │       ├───RUNBOOK.md
│   │       ├───EXISTING_REPO_WORKFLOW_SOP.md
│   │       └───*-bootstrap-change-log.md
│   │
│   └───delivery/                   # Delivery scaffold (if generated)
│
├───scripts/                        # Launcher scripts
│   ├───ukbe-daemon.bat             # Daemon mode launcher
│   └───ukbe-run-delivery.bat       # Workflow execution launcher
│
├───tests/                          # Test suite (pytest-based)
│
├───run-*.bat                       # Workflow execution batch files
├───submit-*.bat                    # Workflow submission batch files
└───sync-*.bat                      # Workflow sync batch files
```

## Top-Level Directories

### `agent_runner_v2/` — Core Package

**Purpose:** Contains all Python code for the workflow runner.

**Key Files:**
| File | Responsibility |
|------|----------------|
| `run_agent.py` | CLI entry point, command dispatch, orchestration |
| `step_runner.py` | Prompt rendering, coder invocation, validation |
| `workflow_router.py` | Post-step routing, state transitions |
| `job_state.py` | Job lifecycle, persistence, migration |
| `coder_adapters.py` | LLM provider abstraction |
| `runtime_context.py` | Process-local context management |
| `bundle_loader.py` | Workflow bundle loading |

### `agent_runner_v2/actions/` — Deterministic Actions

**Purpose:** Non-coder steps implemented as deterministic Python functions.

**Categories:**
| Category | Files |
|----------|-------|
| Documentation | `sync_codebase_docs.py`, `sync_system_docs.py`, `validate_*.py` |
| Scanning | `scan_repo_codebase.py` |
| Media Generation | `execute_t2i.py`, `execute_i2v.py`, `execute_voiceover.py`, `assemble_video.py` |
| Scaffold | `prepare_delivery_scaffold.py`, `finalize_bootstrap.py` |

### `agent_runner_v2/bootstrap/` — Packaged Workflows

**Purpose:** Seeds runtime workflow bundles during `init`.

**Key Files:**
| File | Purpose |
|------|---------|
| `template_groups.py` | Workflow family definitions (10 families, 73+ steps) |
| `job_schema.json` | Job state JSON schema |
| `llm_response_schema.json` | LLM response validation schema |
| `model_mapping.json` | LLM provider configuration |
| `prompts/*/` | Per-workflow prompt templates |

### `docs/codebase/` — Codebase Documentation

**Purpose:** Documentation generated from and about the codebase.

**Structure:**
| Subdirectory | Content |
|--------------|---------|
| `01_inventory/` | `codebase_inventory.md` — module registry |
| `02_modules/` | Per-module documentation (49 files) |
| `03_components/` | Component documentation (6 files) |
| `04_changes/` | Change impact documents |

### `docs/system/` — System Documentation

**Purpose:** Master system documentation for the platform.

**Structure:**
| File | Purpose |
|------|---------|
| `00_governance/bootstrap/` | Core system docs (this bootstrap set) |
| `00_governance/bootstrap/README.md` | Documentation index |
| Various `.md` files | System overview, architecture, guides |

### `scripts/` — Launcher Scripts

**Purpose:** Helper scripts for workflow execution.

| File | Purpose |
|------|---------|
| `ukbe-run-delivery.bat` | Main workflow execution script |
| `ukbe-daemon.bat` | Daemon mode launcher |

### `archive/` — Legacy Files

**Purpose:** Deprecated batch scripts and legacy code.

**Note:** Contents are preserved for reference but not actively used.

## Documentation Locations

### System Documentation

| Document | Location | Owner |
|----------|----------|-------|
| Documentation Standard | `docs/system/00_governance/bootstrap/DOCUMENTATION_STANDARD.md` | Bootstrap workflow |
| Bundle Taxonomy | `docs/system/00_governance/bootstrap/BUNDLE_TAXONOMY.md` | Bootstrap workflow |
| System Overview | `docs/system/00_governance/bootstrap/SYSTEM_OVERVIEW.md` | Bootstrap workflow |
| Component Architecture | `docs/system/00_governance/bootstrap/COMPONENT_ARCHITECTURE.md` | Bootstrap workflow |
| Developer Guide | `docs/system/00_governance/bootstrap/DEVELOPER_GUIDE.md` | Bootstrap workflow |
| Runbook | `docs/system/00_governance/bootstrap/RUNBOOK.md` | Bootstrap workflow |

### Codebase Documentation

| Document | Location | Owner |
|----------|----------|-------|
| Codebase Inventory | `docs/codebase/01_inventory/codebase_inventory.md` | Bootstrap/reconcile |
| Module Docs | `docs/codebase/02_modules/*.md` | Bootstrap/reconcile |
| Component Docs | `docs/codebase/03_components/*.md` | Bootstrap/reconcile |
| Change Impact | `docs/codebase/04_changes/*.md` | Bootstrap/reconcile |

### Operational Documentation

| Document | Location | Owner |
|----------|----------|-------|
| Daemon Quickstart | `docs/operations/DAEMON_MODE_QUICKSTART.md` | Manual |
| Workflow SOP | `docs/operations/EXISTING_REPO_WORKFLOW_SOP.md` | Manual/Scaffold |

## Runtime Locations

### Global Runner Home

| Path | Purpose |
|------|---------|
| `%USERPROFILE%\.ukbe-runner\config.json` | User configuration |
| `%USERPROFILE%\.ukbe-runner\jobs\` | Job state persistence |
| `%USERPROFILE%\.ukbe-runner\workflows\` | Runtime workflow bundles |
| `%USERPROFILE%\.ukbe-runner\logs\` | Execution logs |

### Job State Structure

```
%USERPROFILE%\.ukbe-runner\jobs\
└───<template_group>\                # e.g., 00_master_docs_bootstrap_v1
    └───<job_id>\                    # e.g., 00DOC-GEN-20260703-007
        ├───job.json                 # Job state
        ├───<step_id>\               # Per-step directories
        │   └───meta.json            # Step result sidecar
        └───logs\                    # Execution logs
```

---

*Generated: 2026-07-04T10:00:00+08:00*
*Workflow: 00_master_docs_bootstrap_v1 / Step: 04_generate_architecture_docs*
*Change ID: 00DOC-GEN-20260704-001*
