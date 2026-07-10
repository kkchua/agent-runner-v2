---
template_id: "SYS-03-SF"
title: "System File Structure - agent-runner-v2"
status: "active"
managed_by: workflow-generated
generated: "2026-07-10T19:56:49+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "04_generate_architecture_docs"
change_id: "00DOC-20260710-0098bf53"
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# System File Structure: agent-runner-v2

## Repository Structure

```
D:\MyProjectSpace\01_Workflows\agent-runner-v2\
├── agent_runner_v2/              # Main Python package
│   ├── __init__.py
│   ├── run_agent.py              # CLI entry point
│   ├── step_runner.py            # Step execution
│   ├── workflow_router.py        # Post-step routing
│   ├── job_state.py              # Job state management
│   ├── runtime_context.py        # Runtime context
│   ├── bundle_loader.py          # Bundle loading
│   ├── coder_adapters.py         # LLM invocation
│   ├── constants.py              # Centralized constants
│   ├── actions/                  # 30+ runner actions
│   │   ├── scan_repo_codebase.py
│   │   ├── sync_codebase_docs.py
│   │   ├── validate_delivery_docs.py
│   │   ├── generate_site.py
│   │   └── ... (26 more)
│   ├── bootstrap/                # Bootstrap source
│   │   ├── workflows/default/    # Default workflow bundle
│   │   ├── bundles/core/current/ # Master system docs bundle
│   │   └── themes/default/       # HTML site themes
│   ├── config/                   # Configuration
│   │   └── section_requirements.py
│   ├── tools/                    # Tool utilities
│   │   └── agent_tools.py
│   └── workflow_packages/        # Plugin system
│       ├── base.py
│       ├── loader.py
│       └── registry.py
├── docs/                         # Documentation
│   ├── system/                   # System docs (generated)
│   │   └── 00_governance/bootstrap/
│   ├── codebase/                 # Codebase docs
│   │   ├── 01_inventory/
│   │   ├── 02_modules/           # 73 module docs
│   │   ├── 03_components/
│   │   └── 04_changes/
│   └── delivery/                 # Delivery artifacts
├── workflows/                    # Plugin workflow packages
│   └── 00_master_docs_bootstrap_v2/
│       ├── workflow.toml
│       └── prompts/
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests (45)
│   ├── integration/              # Integration tests
│   └── conftest.py
├── scripts/                      # Shell scripts
│   ├── ukbe-run-agent.sh
│   └── ukbe-run-delivery.bat
├── run-*.bat                     # 26 batch files
├── pyproject.toml                # Package config
├── requirements.txt              # Dependencies
└── README.md
```

## Top-Level Directories

### agent_runner_v2/

**Purpose**: Main Python package containing all runtime code.

**Key Files**:
- `run_agent.py` - CLI entry point and orchestration
- `step_runner.py` - Core step execution contract
- `workflow_router.py` - Post-step routing logic
- `job_state.py` - Job state persistence
- `constants.py` - Centralized artifact paths and keys

**Subdirectories**:
- `actions/` - Deterministic runner actions (30+)
- `bootstrap/` - Seeding data for global runner home
- `config/` - Configuration and section requirements
- `tools/` - Tool utilities (agent_tools.py)
- `workflow_packages/` - Plugin system modules

### docs/

**Purpose**: All documentation artifacts.

**Subdirectories**:
- `system/` - Generated system documentation
- `codebase/` - Codebase documentation from scanning
- `delivery/` - Delivery artifacts from workflows

### workflows/

**Purpose**: Plugin workflow packages (new system).

**Structure**: Each subdirectory is a self-contained workflow with `workflow.toml` and `prompts/`.

### tests/

**Purpose**: Test suite.

**Subdirectories**:
- `unit/` - Pure logic tests (45 passing)
- `integration/` - Integration tests with real files

### scripts/

**Purpose**: Shell scripts for execution.

**Files**:
- `ukbe-run-agent.sh` - Unix launcher
- `ukbe-run-delivery.bat` - Windows launcher

## Documentation Locations

| Doc Type | Location | Purpose |
|----------|----------|---------|
| **System Docs** | `docs/system/00_governance/bootstrap/` | Master system documentation |
| **Codebase Inventory** | `docs/codebase/01_inventory/` | Repository scan results |
| **Module Docs** | `docs/codebase/02_modules/` | 73 module documentation files |
| **Component Docs** | `docs/codebase/03_components/` | Component architecture |
| **Change Impact** | `docs/codebase/04_changes/` | Change impact documents |
| **Delivery Artifacts** | `docs/delivery/` | Workflow-generated delivery docs |

## Runtime Locations

| Resource | Location | Purpose |
|----------|----------|---------|
| **Runner Home** | `~/.ukbe-runner/` | Global runtime directory |
| **Workflow Bundles** | `~/.ukbe-runner/workflows/` | Runtime workflow definitions |
| **Job State** | `~/.ukbe-runner/jobs/<job_id>/` | Per-job state |
| **Logs** | `~/.ukbe-runner/logs/` | Execution logs |
| **Config** | `~/.ukbe-runner/config.json` | Global configuration |

## Why These Folders Exist

### agent_runner_v2/actions/

Contains 30+ deterministic runner actions that execute without LLM involvement. Each action is a Python module that performs a specific task (scanning, syncing, validation, etc.).

### agent_runner_v2/bootstrap/

Seeds the global runner home at initialization. The `workflows/default/` directory contains default workflow bundles. The `bundles/core/current/` directory contains master system docs.

### agent_runner_v2/workflow_packages/

Implements the plugin-based workflow system. The adapter pattern converts workflow.toml bundles to the same dict format as legacy TEMPLATE_GROUPS.

### docs/system/

Generated system documentation set. Protected from manual edits by documentation guardrails. Synchronized via `40_documentation_sync_v1` workflow.

### docs/codebase/

Codebase documentation generated by repository scanning. Module documentation auto-generated from source. Component documentation aggregates related modules.

### workflows/

Self-contained workflow packages for the plugin system. Each package has its own manifest, prompts, and optional hooks.

## File Relationships

```
run_agent.py
├── Imports from: job_state.py, step_runner.py, workflow_router.py
├── Uses: runtime_context.py for paths
└── Loads: bundle_loader.py for workflows

step_runner.py
├── Imports from: coder_adapters.py, exceptions.py
├── Uses: constants.py for paths
└── Writes: meta.json sidecars

constants.py
├── Defines: All artifact keys, folder keys, section requirements
└── Used by: step_runner.py, documentation_guardrails.py
```

---

*Last updated: 2026-07-10T19:56:49+08:00 via workflow `00_master_docs_bootstrap_v2`*
