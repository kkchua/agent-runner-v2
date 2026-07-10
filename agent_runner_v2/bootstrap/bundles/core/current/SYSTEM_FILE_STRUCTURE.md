---
title: "System File Structure"
template_id: "SYS-03-SF"
status: "active"
change_id: "00DOC-20260710-15f76235"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
managed_by: workflow-generated
generated: "2026-07-10T11:57:31+08:00"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# System File Structure: agent-runner-v2

## Repository Structure

```
agent-runner-v2/                          # Project root
├── agent_runner_v2/                        # Main Python package (67 modules)
│   ├── __init__.py                         # Package entry
│   ├── run_agent.py                        # CLI entry point (2,338 lines)
│   ├── step_runner.py                      # Core step execution (2,582 lines)
│   ├── workflow_router.py                  # Post-step routing (787 lines)
│   ├── job_state.py                        # Job lifecycle management
│   ├── coder_adapters.py                   # Claude/Codex/Qwen invocation
│   ├── runtime_context.py                  # Active workflow/runtime context
│   ├── bundle_loader.py                    # Bootstrap seeding, workflow loading
│   ├── constants.py                        # Centralized path constants
│   ├── daemon.py                           # Workstation supervisor
│   ├── actions/                            # 26 deterministic runner actions
│   │   ├── init.py
│   │   ├── prepare_delivery_scaffold.py
│   │   ├── scan_repo_codebase.py
│   │   ├── validate_*.py                   # Document validation actions
│   │   ├── sync_*.py                       # Documentation sync actions
│   │   ├── generate_site.py
│   │   └── ...
│   ├── bootstrap/                          # Packaged workflow definitions
│   │   └── workflows/default/
│   │       ├── template_groups.py          # Workflow step definitions
│   │       ├── job_schema.json             # Job state schema
│   │       ├── llm_response_schema.json    # Meta.json schema
│   │       ├── model_mapping.json          # Model aliases
│   │       └── prompts/                    # LLM prompt templates
│   │           ├── 00_master_docs_bootstrap_v1/
│   │           ├── 10_execution_scaffold_v1/
│   │           ├── 20_initiative_intake_v1/
│   │           ├── 21_bug_fix_intake_v1/
│   │           ├── 30_delivery_planning_v1/
│   │           ├── 31_task_execution_v1/
│   │           ├── 40_documentation_sync_v1/
│   │           └── 41_audience_doc_v1/
│   └── tools/
│       └── agent_tools.py                  # Workflow utility tools
├── docs/                                   # Documentation governance
│   ├── delivery/                           # Delivery governance
│   │   ├── 01_initiatives/                # Initiative documents
│   │   ├── 02_plans/                        # Plan documents
│   │   ├── 03_tasks/                        # Task documents
│   │   └── 04_validation/                   # Validation documents
│   ├── codebase/                           # Codebase documentation
│   │   ├── 01_inventory/                    # Codebase inventory
│   │   ├── 02_modules/                      # 67 module docs
│   │   ├── 03_components/                   # Component docs
│   │   └── 04_changes/                      # Change impact docs
│   └── system/                             # System governance
│       └── 00_governance/bootstrap/         # Master system docs
├── tests/                                  # Test suite
│   ├── unit/                               # 45 pure unit tests
│   ├── integration/                        # Integration tests
│   └── conftest.py                         # Shared fixtures
├── scripts/                                # Utility scripts
│   └── ukbe-run-delivery.bat               # Batch wrapper
├── run-*.bat                               # Workflow launchers (26 files)
├── pyproject.toml                          # Package configuration
├── requirements.txt                        # Dependencies
├── README.md                               # Project readme
├── QWEN.md                                 # Qwen Code context
├── CODER_IMPLEMENTATION_SOP.md            # Coder SOP
└── .env.example                            # Environment template
```

## Top-Level Directories

### `agent_runner_v2/`

**Purpose**: Main Python package containing all runner logic

**Key Modules**:
- `run_agent.py` - CLI entry and orchestration
- `step_runner.py` - Core step execution contract
- `workflow_router.py` - Post-step routing logic
- `job_state.py` - Job lifecycle and persistence
- `constants.py` - Centralized artifact path constants

**Subpackages**:
- `actions/` - 26 deterministic runner actions
- `bootstrap/` - Packaged workflow definitions

### `docs/`

**Purpose**: Documentation governance under three taxonomies

**Structure**:
- `delivery/` - Initiative, plan, task, validation documents
- `codebase/` - Module docs, component docs, inventory, changes
- `system/` - Master system documentation

**Governance**:
- All docs workflow-generated with protection banners
- Declarative `produces` lists control mutations
- Validation against section requirements

### `tests/`

**Purpose**: Split test suite

**Structure**:
- `unit/` - Pure logic tests (45 tests, no filesystem)
- `integration/` - Real files and external systems
- `conftest.py` - Shared pytest fixtures

**Markers**:
- `unit` - Fast, isolated, no I/O
- `integration` - Slow, filesystem, network

### `scripts/`

**Purpose**: Utility scripts

**Contents**:
- `ukbe-run-delivery.bat` - Common batch wrapper

## Runtime Locations

### Runner Home (`~/.ukbe-runner/`)

```
~/.ukbe-runner/
├── config.json                             # Global configuration
├── engine/
│   └── config.json                         # Engine/daemon config
├── jobs/                                   # Job state storage
│   └── <workflow>/
│       └── <job_id>/
│           ├── job.json                    # Job state
│           ├── 01_<step>/                  # Step working dirs
│           │   ├── meta.json               # Step result sidecar
│           │   └── <artifacts>
│           └── ...
├── workflows/                              # Runtime workflow bundles
│   └── default/
│       ├── template_groups.py              # (copied from bootstrap)
│       └── prompts/                        # (copied from bootstrap)
└── logs/                                   # Execution logs
```

**Key Files**:
- `~/.ukbe-runner/config.json` - User configuration
- `~/.ukbe-runner/engine/config.json` - Daemon configuration
- `~/.ukbe-runner/jobs/<wf>/<job>/job.json` - Job state
- `~/.ukbe-runner/jobs/<wf>/<job>/<step>/meta.json` - Step results

## Documentation Locations

### System Docs (`docs/system/00_governance/bootstrap/`)

| Document | Purpose |
|----------|---------|
| `PROJECT_ANALYSIS.md` | Repository analysis |
| `README.md` | Documentation index |
| `DOCUMENTATION_STANDARD.md` | Governance rules |
| `BUNDLE_TAXONOMY.md` | Bundle structure |
| `BUNDLE_MIGRATION_PLAN.md` | Migration strategy |
| `SYSTEM_OVERVIEW.md` | Platform overview |
| `BUSINESS_CAPABILITIES.md` | Capabilities |
| `FUNCTIONAL_SPEC.md` | Functional spec |
| `NON_FUNCTIONAL_REQUIREMENTS.md` | Quality attributes |
| `SYSTEM_CONTEXT.md` | System context |
| `COMPONENT_ARCHITECTURE.md` | Component architecture |
| `DECISION_LOG.md` | Decision log |
| `SYSTEM_FILE_STRUCTURE.md` | File structure |
| `DEVELOPER_GUIDE.md` | Developer guide |
| `RUNBOOK.md` | Operations runbook |
| `EXISTING_REPO_WORKFLOW_SOP.md` | Workflow SOP |

### Codebase Docs (`docs/codebase/`)

| Directory | Contents |
|-----------|----------|
| `01_inventory/` | `codebase_inventory.md` |
| `02_modules/` | 67 module documentation files |
| `03_components/` | Component documentation |
| `04_changes/` | Change impact documents |

## Relationships

### Bootstrap to Runtime

1. **Packaged bootstrap** (`agent_runner_v2/bootstrap/`) ships with repo
2. **`init` command** seeds runtime bundles to `~/.ukbe-runner/workflows/`
3. **Runtime execution** loads from runner home, not repo
4. **Sync required** after bootstrap changes

### Code to Docs

1. **Code changes** trigger `40_documentation_sync_v1` workflow
2. **Codebase scan** updates `codebase_inventory.md`
3. **Module docs** refreshed from source analysis
4. **Validation** ensures docs match code

### Job State Flow

1. **Create job** → `job.json` in `~/.ukbe-runner/jobs/<wf>/<job>/`
2. **Run step** → Working dir `<step>/` created
3. **Write artifacts** → Files in working dir
4. **Write meta.json** → Sidecar for routing
5. **Route** → Next step or completion
