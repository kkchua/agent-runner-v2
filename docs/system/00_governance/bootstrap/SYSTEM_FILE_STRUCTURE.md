---
template_id: "SYS-03-SF"
title: "System File Structure"
status: "active"
generated: "2026-07-04T14:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260704-002"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# System File Structure

## Repository Structure

```
agent-runner-v2/
├── agent_runner_v2/              # Main package source
│   ├── __init__.py
│   ├── run_agent.py              # CLI entry point (core)
│   ├── step_runner.py            # Step execution (core)
│   ├── workflow_router.py        # Post-step routing (core)
│   ├── job_state.py              # Job lifecycle (state)
│   ├── coder_adapters.py         # LLM adapters (coder)
│   ├── model_config.py           # Model configuration (coder)
│   ├── runtime_context.py        # Runtime context (state)
│   ├── bundle_loader.py          # Bundle loading (bootstrap)
│   ├── backend_client.py         # Backend API client (backend)
│   ├── daemon.py                 # Daemon mode (backend)
│   ├── actions/                  # Deterministic actions (20 modules)
│   │   ├── __init__.py
│   │   ├── scan_repo_codebase.py
│   │   ├── sync_codebase_docs.py
│   │   ├── sync_system_docs.py
│   │   ├── validate_*.py
│   │   ├── prepare_delivery_scaffold.py
│   │   ├── finalize_bootstrap.py
│   │   ├── copy_artifact.py
│   │   ├── promote_*.py
│   │   ├── publish_architecture_site.py
│   │   ├── execute_*.py
│   │   ├── assemble_video.py
│   │   └── submit_comfyui.py
│   ├── bootstrap/                # Packaged workflow definitions
│   │   └── workflows/
│   │       └── default/
│   │           ├── template_groups.py      # 11 workflow families
│   │           ├── job_schema.json
│   │           ├── llm_response_schema.json
│   │           ├── model_mapping.json
│   │           ├── usage_schema.json
│   │           └── prompts/              # Per-step prompts
│   │               ├── 00_master_docs_bootstrap_v1/
│   │               ├── 10_execution_scaffold_v1/
│   │               ├── 20_initiative_intake_v1/
│   │               ├── 21_bug_fix_intake_v1/
│   │               ├── 30_delivery_planning_v1/
│   │               ├── 31_task_execution_v1/
│   │               ├── 40_documentation_sync_v1/
│   │               ├── 50_architecture_site_v1/
│   │               ├── image_csv_gen_v2/
│   │               ├── videoxpress_gen_v1/
│   │               └── tiktok_video_pipeline_v1/
│   └── tools/
│       └── agent_tools.py        # Progress tracking utilities
├── docs/                         # Documentation root
│   ├── codebase/                 # Codebase documentation
│   │   ├── 00_standards/         # SOP and status rules
│   │   ├── 01_inventory/         # codebase_inventory.md
│   │   ├── 02_modules/           # Per-module docs (56 files)
│   │   ├── 03_components/        # Component-level docs
│   │   └── 04_changes/           # Change impact documents
│   └── system/                   # System documentation
│       └── 00_governance/
│           └── bootstrap/        # Generated system docs
│               ├── README.md
│               ├── project_analysis.md
│               ├── DOCUMENTATION_STANDARD.md
│               ├── BUNDLE_TAXONOMY.md
│               ├── BUNDLE_MIGRATION_PLAN.md
│               ├── SYSTEM_OVERVIEW.md
│               ├── BUSINESS_CAPABILITIES.md
│               ├── FUNCTIONAL_SPEC.md
│               ├── NON_FUNCTIONAL_REQUIREMENTS.md
│               ├── SYSTEM_CONTEXT.md
│               ├── COMPONENT_ARCHITECTURE.md
│               ├── DECISION_LOG.md
│               ├── SYSTEM_FILE_STRUCTURE.md
│               ├── DEVELOPER_GUIDE.md
│               ├── RUNBOOK.md
│               └── EXISTING_REPO_WORKFLOW_SOP.md
├── tests/                        # Test suite
├── pyproject.toml                # Package configuration
├── README.md                     # Repository README
├── QWEN.md                       # Project context and conventions
├── HOW_TO_GUIDE.md             # Usage guide
├── *.bat                       # Batch launchers
└── .qwen/skills/               # Auto-skills
```

## Top-Level Directories

### `agent_runner_v2/` — Package Source

Contains all Python source code for the workflow runner.

**Why it exists**: Single package root for clean imports and distribution.

**Key subdirectories**:
- `actions/` — Deterministic runner actions (non-LLM operations)
- `bootstrap/workflows/default/` — Packaged workflow definitions and prompts
- `tools/` — Development utilities

### `docs/` — Documentation

Contains all project documentation, separated by audience.

**Why it exists**: Clear separation between codebase docs (for developers) and system docs (for stakeholders/operators).

**Subdirectories**:
- `codebase/` — Code-level documentation
  - `00_standards/` — Governance SOPs and status rules
  - `01_inventory/` — Module inventory
  - `02_modules/` — Per-module documentation
  - `03_components/` — Component documentation
  - `04_changes/` — Change impact tracking
- `system/00_governance/bootstrap/` — Generated system documentation

### `tests/` — Test Suite

Contains pytest-based test suite.

**Why it exists**: Standard Python testing location, referenced by `pyproject.toml`.

## Documentation Locations

| Document Type | Location | Purpose |
|---------------|----------|---------|
| **Module docs** | `docs/codebase/02_modules/*.md` | Per-module API and behavior |
| **Component docs** | `docs/codebase/03_components/*.md` | Component relationships |
| **Change impact** | `docs/codebase/04_changes/*.md` | Change tracking and impact |
| **System docs** | `docs/system/00_governance/bootstrap/*.md` | Platform-level documentation |
| **Inventory** | `docs/codebase/01_inventory/codebase_inventory.md` | Module registry |

## Runtime Locations

| Location | Path | Purpose |
|----------|------|---------|
| **Runner home** | `%USERPROFILE%\.ukbe-runner\` | Global runtime state |
| **Config** | `%USERPROFILE%\.ukbe-runner\config.json` | User configuration |
| **Jobs** | `%USERPROFILE%\.ukbe-runner\jobs\` | Job state directories |
| **Workflows** | `%USERPROFILE%\.ukbe-runner\workflows\` | Runtime workflow bundles |
| **Logs** | `%USERPROFILE%\.ukbe-runner\logs\` | Execution logs |

## File Relationships

### Core Execution Flow

```
run_agent.py
    ↓ imports
step_runner.py ←→ coder_adapters.py
    ↓ imports                   ↓ HTTP
workflow_router.py          LLM APIs
    ↓ imports
job_state.py
    ↓ imports
runtime_context.py ←→ bundle_loader.py
```

### Documentation Flow

```
scan_repo_codebase.py
    ↓ generates
codebase_inventory.md
    ↓ feeds into
PROJECT_ANALYSIS
    ↓ feeds into
System docs generation
```

## Key Files

| File | Purpose | Owner |
|------|---------|-------|
| `pyproject.toml` | Package config, entry points, dependencies | Source |
| `QWEN.md` | Project conventions and context | Manual |
| `README.md` | Repository overview | Manual |
| `template_groups.py` | Workflow definitions | Source |
| `job_schema.json` | Job state schema | Source |
| `llm_response_schema.json` | Expected LLM response format | Source |

---

*This file structure document explains the organization of agent-runner-v2. See DEVELOPER_GUIDE.md for development workflows and RUNBOOK.md for operational procedures.*
