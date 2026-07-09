---
template_id: "SYS-03-SFS"
managed_by: workflow-generated
generated: "2026-07-09T21:26:23+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260709-002"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# System File Structure

## Repository Structure

```
agent-runner-v2/
├── agent_runner_v2/              # Main Python package
│   ├── __init__.py
│   ├── actions/                  # 29 deterministic runner actions
│   │   ├── __init__.py
│   │   ├── validate_delivery_docs.py
│   │   ├── sync_system_docs.py
│   │   ├── generate_site.py
│   │   └── ... (26 more)
│   ├── bootstrap/                # Package-local workflow seeds
│   │   ├── workflows/default/    # Default workflow definitions
│   │   │   ├── template_groups.py
│   │   │   ├── prompts/          # Prompt templates per workflow
│   │   │   ├── job_schema.json
│   │   │   └── model_mapping.json
│   │   ├── bundles/core/current/ # Core bootstrap bundle docs
│   │   └── themes/default/       # HTML themes for architecture site
│   ├── config/                   # Configuration utilities
│   │   ├── __init__.py
│   │   └── section_requirements.py
│   ├── tools/                    # Standalone tool scripts
│   │   └── agent_tools.py
│   ├── run_agent.py              # CLI entry point (~2,300 lines)
│   ├── step_runner.py            # Step execution (~2,400 lines)
│   ├── workflow_router.py        # Post-step routing (~800 lines)
│   ├── job_state.py              # Job lifecycle (~1,800 lines)
│   ├── coder_adapters.py         # Coder invocation (~1,000 lines)
│   ├── constants.py              # Path constants (~1,000 lines)
│   ├── runtime_context.py        # Runtime context
│   ├── bundle_loader.py          # Bundle loading
│   ├── daemon.py                 # Worker daemon (~466 lines)
│   ├── backend_client.py         # Backend HTTP client
│   ├── documentation_guardrails.py
│   └── ... (20+ more modules)
├── docs/                         # Documentation
│   ├── system/                   # System-level documentation
│   │   └── 00_governance/
│   │       └── bootstrap/        # Bootstrap bundle (workflow-generated)
│   ├── codebase/                 # Codebase documentation
│   │   ├── 01_inventory/         # Codebase inventory
│   │   ├── 02_modules/           # Module documentation (67 files)
│   │   ├── 03_components/        # Component documentation (6 files)
│   │   └── 04_changes/           # Change impact documents
│   └── operations/               # Operational guides
├── tests/                        # Test suite
│   ├── unit/                     # Pure logic tests (45 tests)
│   └── integration/              # Integration tests
├── scripts/                      # Utility scripts
├── *.bat                         # 34 Windows batch launchers
├── pyproject.toml                # Package configuration
├── requirements.txt              # Dependencies
└── README.md                     # Package readme
```

## Top-Level Directories

### `agent_runner_v2/` — Core Package

**Purpose**: Contains all runtime Python code.

**Key Subdirectories**:
| Subdirectory | Purpose | File Count |
|--------------|---------|------------|
| `actions/` | Deterministic runner actions | 29 files |
| `bootstrap/` | Workflow seeds and bundle templates | ~200 files |
| `config/` | Configuration utilities | 2 files |
| `tools/` | Standalone tool scripts | 1 file |

**Key Files**:
- `run_agent.py` — CLI entry and orchestration
- `step_runner.py` — Core step execution
- `workflow_router.py` — Routing logic
- `job_state.py` — State management
- `constants.py` — Path constants (single source of truth)

### `docs/` — Documentation

**Purpose**: All project documentation.

**Subdirectories**:
| Subdirectory | Purpose | Content |
|--------------|---------|---------|
| `system/00_governance/bootstrap/` | System docs (workflow-generated) | Master docs bundle |
| `codebase/01_inventory/` | Codebase inventory | `codebase_inventory.md` |
| `codebase/02_modules/` | Module docs | 67 module files |
| `codebase/03_components/` | Component docs | 6 component files |
| `codebase/04_changes/` | Change impact docs | Latest change impact |
| `operations/` | Operational guides | Daemon quickstart, SOPs |

### `tests/` — Test Suite

**Purpose**: Test coverage for the codebase.

**Structure**:
- `unit/` — Pure logic tests (isolated, no filesystem dependencies)
- `integration/` — Integration tests (real files, external systems)
- `conftest.py` — Shared pytest fixtures

**Current Status**: 45 unit tests passing (100%).

### Batch Files (Root)

**Purpose**: Windows-native workflow launchers.

**Naming Pattern**:
- `run-*.bat` — Execute workflows locally
- `submit-*.bat` — Submit jobs to backend
- `sync-*.bat` — Sync workflows to backend

**Examples**:
- `run-00_master_docs_bootstrap_v1.bat` — Bootstrap documentation
- `run-20_initiative_intake_v1.bat` — Initiative intake workflow
- `run-daemon.bat` — Start daemon mode

## Documentation Locations

### System Documentation

| Document | Path | Purpose |
|----------|------|---------|
| README.md | `docs/system/00_governance/bootstrap/` | Documentation index |
| PROJECT_ANALYSIS.md | `docs/system/00_governance/bootstrap/` | Repo analysis |
| SYSTEM_OVERVIEW.md | `docs/system/00_governance/bootstrap/` | Platform overview |
| FUNCTIONAL_SPEC.md | `docs/system/00_governance/bootstrap/` | System behaviors |
| COMPONENT_ARCHITECTURE.md | `docs/system/00_governance/bootstrap/` | Architecture |
| DEVELOPER_GUIDE.md | `docs/system/00_governance/bootstrap/` | Developer guide |
| RUNBOOK.md | `docs/system/00_governance/bootstrap/` | Operations guide |

### Codebase Documentation

| Document | Path | Purpose |
|----------|------|---------|
| codebase_inventory.md | `docs/codebase/01_inventory/` | Module/component registry |
| workflow-families.md | `docs/codebase/03_components/` | Workflow definitions |
| actions-package.md | `docs/codebase/03_components/` | Actions overview |
| 67 module docs | `docs/codebase/02_modules/` | Per-module documentation |

### Bootstrap Bundle

The bootstrap bundle at `agent_runner_v2/bootstrap/bundles/core/current/` contains:
- Master system documentation (mirror of `docs/system/`)
- Workflow templates (delivery, codebase)
- SOPs and agent contracts

This bundle is copied to `~/.ukbe-runner/` on `ukbe-run-agent init`.

## Runtime Locations

### Global Runner Home

Location: `%USERPROFILE%\.ukbe-runner\`

| Subdirectory | Purpose |
|--------------|---------|
| `config.json` | Runtime configuration |
| `jobs/` | Job execution state |
| `workflows/` | Active workflow bundles |
| `logs/` | Execution logs |
| `engine/` | Engine versions (if versioned) |

### Job Execution Directories

Structure:
```
~/.ukbe-runner/jobs/<workflow>/<job_id>/
├── job.json                    # Job state
├── 01_<step_name>/             # Step working directory
│   ├── prompt.txt              # Rendered prompt
│   ├── meta.json               # Step result sidecar
│   └── <artifacts...>          # Generated artifacts
├── 02_<step_name>/
│   └── ...
└── ...
```

---

*Generated by workflow: 00_master_docs_bootstrap_v1 / step: 04_generate_architecture_docs*
