---
template_id: "SYS-03-SF"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-16T22:22:07+08:00"
workflow: "00_repo_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00RMD-20260716-5ee28fa5"
---

# System File Structure: agent-runner-v2

## Repository Structure

```
agent-runner-v2/
├── .agents/                    # Agent-specific configuration (git-ignored)
├── .claude/                    # Claude-specific configuration (git-ignored)
├── .qwen/                      # Qwen-specific configuration (git-ignored)
├── .tmp/                       # Temporary files (git-ignored)
├── .venv/                      # Python virtual environment (git-ignored)
├── agent_runner_v2/            # Main package (70 modules)
│   ├── actions/                # Deterministic action modules (29 files)
│   ├── bootstrap/              # Bootstrap workflow bundles
│   │   ├── bundles/core/       # Published governance artifacts
│   │   └── workflows/default/  # Layer 1 bootstrap workflows (3 families)
│   ├── config/                 # Section requirements configuration
│   ├── tools/                  # Progress tracking agent tools
│   └── workflow_packages/      # Plugin-based workflow package system
├── docs/
│   ├── repo/                   # Repo-level documentation
│   │   ├── codebase/           # Codebase inventory and module docs
│   │   ├── governance/         # Repo governance (this file)
│   │   └── sdlc/               # AI-Driven SDLC artifacts (planned)
│   └── system/                 # System-level governance and plans
├── tests/
│   ├── unit/                   # Pure unit tests (45+ tests, isolated logic)
│   └── integration/            # Integration tests (real files, external systems)
├── workflows/                  # Runtime workflow packages (deployed)
│   ├── _registry/              # Workflow registry
│   ├── 00_bootstrap_lifecycle_admin_v1/
│   ├── 00_layer1_governance_bootstrap_v1/
│   └── 00_repo_master_docs_bootstrap_v1/
├── .env.example                # Example environment configuration
├── .gitignore                  # Git ignore patterns
├── CLAUDE.md                   # Claude agent instructions
├── CODER_IMPLEMENTATION_SOP.md # Implementation SOP for coders
├── MANIFEST.in                 # Python package manifest
├── pyproject.toml              # Project configuration
├── QWEN.md                     # Qwen agent instructions
├── README.md                   # Project readme
├── requirements.txt            # Python dependencies
└── *.bat                       # Root-level launcher scripts (13 files)
```

## Top-Level Directories

| Directory | Purpose | Contents |
|-----------|---------|----------|
| `agent_runner_v2/` | Main Python package | Core modules, actions, bootstrap, workflow packages |
| `docs/` | All documentation | Repo docs, system docs, governance |
| `tests/` | Test suite | Unit tests, integration tests |
| `workflows/` | Runtime workflow packages | Deployed workflow bundles |
| `.agents/` | Agent-specific config | Per-agent settings (git-ignored) |
| `.claude/` | Claude-specific config | Claude integration (git-ignored) |
| `.qwen/` | Qwen-specific config | Qwen integration (git-ignored) |
| `.tmp/` | Temporary files | Scratch files (git-ignored) |
| `.venv/` | Python virtual env | Development environment (git-ignored) |

## Documentation Locations

### Layer 1: Ecosystem Governance

| Path | Purpose |
|------|---------|
| `docs/system/00_governance/bootstrap/` | Layer 1 governance artifacts |
| `docs/system/00_governance/bootstrap/DOCUMENTATION_STANDARD.md` | Documentation authority |
| `docs/system/00_governance/bootstrap/BUNDLE_TAXONOMY.md` | Bundle classes and ownership |
| `docs/system/00_governance/bootstrap/RUNTIME_GOVERNANCE.md` | Runtime governance rules |

### Layer 2: Repo Master Docs

| Path | Purpose |
|------|---------|
| `docs/repo/governance/` | Repo master documentation (this directory) |
| `docs/repo/governance/README.md` | System docs index |
| `docs/repo/governance/PROJECT_ANALYSIS.md` | Approved project analysis (read-only) |
| `docs/repo/governance/SYSTEM_CONTEXT.md` | System context |
| `docs/repo/governance/COMPONENT_ARCHITECTURE.md` | Component architecture |
| `docs/repo/governance/DECISION_LOG.md` | Decision log |
| `docs/repo/governance/SYSTEM_FILE_STRUCTURE.md` | File structure (this document) |
| `docs/repo/governance/DEVELOPER_GUIDE.md` | Developer guide |
| `docs/repo/governance/RUNBOOK.md` | Operations runbook |
| `docs/repo/governance/EXISTING_REPO_WORKFLOW_SOP.md` | Workflow SOP |

### Layer 3: Codebase Docs

| Path | Purpose |
|------|---------|
| `docs/repo/codebase/01_inventory/` | Codebase inventory |
| `docs/repo/codebase/02_modules/` | Module documentation (100+ files) |
| `docs/repo/codebase/03_components/` | Component documentation |
| `docs/repo/codebase/04_changes/` | Change impact assessments |

### Layer 4+: SDLC Artifacts (Planned)

| Path | Purpose |
|------|---------|
| `docs/repo/sdlc/00_governance/` | SDLC governance baseline |
| `docs/repo/sdlc/01_requirements/` | Requirements artifacts |
| `docs/repo/sdlc/02_planning/` | Planning artifacts |
| `docs/repo/sdlc/03_backlog/` | Backlog management |
| `docs/repo/sdlc/04_tasks/` | Task breakdowns |
| `docs/repo/sdlc/05_implementation/` | Implementation records |
| `docs/repo/sdlc/06_review/` | Review records |
| `docs/repo/sdlc/07_execution/` | Execution logs |
| `docs/repo/sdlc/08_validation/` | Validation results |
| `docs/repo/sdlc/09_memory/` | Workflow memory |
| `docs/repo/sdlc/10_archive/` | Archived artifacts |

## Root-Level Launcher Files

### Active Commands

| File | Purpose | Status |
|------|---------|--------|
| `run-init.bat` | Initialize new job | Active |
| `run-00_layer1_governance_bootstrap_v1.bat` | Run Layer 1 governance bootstrap | Active |
| `run-00_repo_master_docs_bootstrap_v1.bat` | Run repo master docs bootstrap | Active |
| `run-00_bootstrap_lifecycle_admin_v1.bat` | Run bootstrap lifecycle admin | Active |
| `run-bootstrap-publish.bat` | Publish bootstrap bundles | Active |
| `run-daemon.bat` | Start daemon worker | Active |
| `run-approve-step.bat` | Approve current step | Active |
| `run-reset-step.bat` | Reset step for retry | Active |
| `run-cleanup-workflow.bat` | Cleanup workflow artifacts | Active |
| `submit-00_bootstrap_lifecycle_admin_v1.bat` | Submit bootstrap lifecycle job | Active |
| `submit-00_layer1_governance_bootstrap_v1.bat` | Submit Layer 1 governance job | Active |
| `submit-00_repo_master_docs_bootstrap_v1.bat` | Submit master docs job | Active |
| `sync-workflows-to-backend.bat` | Sync workflow packages to backend | Active |

### Archived Commands

**None**. All legacy workflow launchers have been removed from the repository. The `archive/` directory does not exist in the current tree.

### Notes on Archived Workflows

Legacy SDLC workflows (`10_execution_scaffold_v2`, `20_initiative_intake_v1`, `30_delivery_planning_v1`, `31_task_execution_v1`, `40_documentation_sync_v1`, `50_architecture_site_v1`) are **not currently present** in the repository. These workflows are pending restoration as part of the AI-Driven SDLC migration plan documented in `docs/system/03_ai_driven_sdlc_migration_plan.md`.

## Package Structure

### `agent_runner_v2/` Package

| Subdirectory | Purpose | Module Count |
|--------------|---------|--------------|
| `actions/` | Deterministic action modules | 29 |
| `bootstrap/` | Bootstrap workflow bundles | 3 families |
| `config/` | Section requirements | 2 |
| `tools/` | Progress tracking | 1 |
| `workflow_packages/` | Plugin system | 5 |

### `tests/` Package

| Subdirectory | Purpose | Test Count |
|--------------|---------|------------|
| `unit/` | Pure unit tests (isolated logic) | 45+ |
| `integration/` | Integration tests (real files) | 10+ |

## Runtime State Locations

| Path | Purpose | Lifecycle |
|------|---------|-----------|
| `.ukbe-runner/jobs/<job_id>/` | Job state directory | Per-job |
| `.ukbe-runner/jobs/<job_id>/<step_id>/` | Step working directory | Per-step |
| `.ukbe-runner/jobs/<job_id>/<step_id>/meta.json` | Step result sidecar | Per-step |
| `%USERPROFILE%\.ukbe-runner\workflows\` | Global workflow packages | Persistent |
| `%USERPROFILE%\.ukbe-runner\config.json` | Global configuration | Persistent |

## Configuration Files

| File | Purpose | Location |
|------|---------|----------|
| `config.json` | Workflow paths, coder config | Project root or global |
| `.env` | Secrets (Pushover, API keys) | Project root |
| `workflow.toml` | Workflow manifest | Per-workflow package |
| `coder_connections.json` | Coder process config | Bootstrap registry |
| `role_policies.json` | Coder role policies | Bootstrap registry |

## File Naming Conventions

| Pattern | Purpose | Example |
|---------|---------|---------|
| `run-<workflow>.bat` | Run workflow launcher | `run-00_layer1_governance_bootstrap_v1.bat` |
| `submit-<workflow>.bat` | Submit workflow job | `submit-00_layer1_governance_bootstrap_v1.bat` |
| `test_<module>.py` | Unit test file | `test_job_state.py` |
| `*.meta.json` | Sidecar metadata | `layer1-governance-review.meta.json` |
| `*-bootstrap-change-log.md` | Bootstrap change log | `00RMD-20260716-5ee28fa5-bootstrap-change-log.md` |