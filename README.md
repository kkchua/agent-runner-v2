# agent-runner-v2 Documentation Index

**Version:** v0.3.0 | **Last Updated:** 2026-07-27

This is the master index for agent-runner-v2 documentation. Use this page to find the right document for your task instead of reading everything.

---

## Quick Start

**New to the project?** Start here:
1. Read this README.md (you are here)
2. Read [QWEN.md](QWEN.md) for comprehensive project overview
3. Check [AGENT_RUNNER_V2_SPECIALIST.md](AGENT_RUNNER_V2_SPECIALIST.md) for navigation guidance

**Need to write code?** Go to [Coders](#for-coders) section below.

**Need to understand architecture?** Go to [Architecture & Design](#architecture--design) section.

**Need to understand job state?** Go to [Job State & Runtime](#job-state--runtime) section.

---

## Document Categories

### For Coders

| Document | Purpose | When to Read |
|----------|---------|--------------|
| [docs/developer/CODER_IMPLEMENTATION_SOP.md](docs/developer/CODER_IMPLEMENTATION_SOP.md) | **Execution discipline for coding tasks** — 8 mandatory rules | **Before writing/editing code** — mandatory reading |
| [QWEN.md](QWEN.md) | **Comprehensive project reference** — architecture, modules, conventions, commands | When you need to understand the codebase structure |
| [docs/developer/AGENT_RUNNER_V2_SPECIALIST.md](docs/developer/AGENT_RUNNER_V2_SPECIALIST.md) | **Agent navigation instructions** — how to find things without repo-wide scans | When you're lost or need to locate specific components |

**Key rules from CODER_IMPLEMENTATION_SOP.md:**
1. Re-read task inputs and referenced files before making changes
2. Verify current code behavior before assuming APIs/paths
3. Prefer extending shared modules over duplicate logic
4. Keep changes narrow, update closest relevant tests
5. When docs and code disagree, prefer active workflow files and current code
6. Verify intended files exist and tests pass before returning success
7. Use `.venv\Scripts\python` for Python/pytest commands
8. All code must include PEP 257 docstrings

**Pattern Compliance:** CODER_IMPLEMENTATION_SOP.md also defines mandatory patterns (v0.3.0+) for coder dispatch, config dataclasses, exception-based errors, and protocol-based hooks. See the "Pattern Compliance Rules" section.

---

### Architecture & Design

| Document | Purpose | When to Read |
|----------|---------|--------------|
| [QWEN.md](QWEN.md) | **Main architecture reference** — module layout, runtime modes, workflow packages, key concepts | For general architecture understanding |
| [docs/developer/ARCHITECTURAL_REFACTOR.md](docs/developer/ARCHITECTURAL_REFACTOR.md) | **Complete architectural refactor documentation** — root cause analysis, architecture violations, Phase 1-3 implementation, race conditions, results | When working on console, daemon, or CLI architecture. **Consolidates ARCHITECTURAL_REFACTOR_FINDINGS.md, ARCHITECTURAL_REFACTOR_SPEC.md, and DAEMON_RACE_CONDITIONS.md** |
| [masterplan/LAYER_ARCHITECTURE_MASTERPLAN.md](masterplan/LAYER_ARCHITECTURE_MASTERPLAN.md) | **Layer architecture** — L1/L2/L3 layer boundaries and responsibilities | For understanding the three-layer governance model |
| [masterplan/LAYER1_GOVERNANCE_SPECIFICATION.md](masterplan/LAYER1_GOVERNANCE_SPECIFICATION.md) | **Layer 1 spec** — Foundation governance rules | When working on governance bootstrap workflows |
| [masterplan/LAYER2_PLATFORM_CORE_SPECIFICATION.md](masterplan/LAYER2_PLATFORM_CORE_SPECIFICATION.md) | **Layer 2 spec** — Platform core constitution | When working on platform workflows (02_agent_runner_platform_v1) |
| [masterplan/LAYER3_AI_DRIVEN_SDLC_SPECIFICATION.md](masterplan/LAYER3_AI_DRIVEN_SDLC_SPECIFICATION.md) | **Layer 3 spec** — AI-driven SDLC workflows | When working on SDLC delivery workflows (sdlc_00 through sdlc_80) |

**Note:** The following documents have been consolidated into [docs/developer/ARCHITECTURAL_REFACTOR.md](docs/developer/ARCHITECTURAL_REFACTOR.md):
- `docs/archive/ARCHITECTURAL_REFACTOR_FINDINGS.md` — Superseded
- `docs/archive/ARCHITECTURAL_REFACTOR_SPEC.md` — Superseded
- `docs/archive/DAEMON_RACE_CONDITIONS.md` — Superseded

These files are kept for historical reference but should not be used as primary reference.

**Architecture principle (from docs/developer/ARCHITECTURAL_REFACTOR.md):**
```
Console (Control Panel) → CLI (brain) → Backend (database)
Daemon  (messenger)     → CLI (brain) → Backend (database)
```
- **Backend**: No logic. Database persistence only.
- **Console**: UI only. ALL operations through CLI. Zero direct backend calls.
- **Daemon**: Messenger. Claims work, spawns CLI, monitors liveness. No business logic.
- **CLI**: The brain. All logic, all backend API calls, all state transitions.

---

### Job State & Runtime

| Document | Purpose | When to Read |
|----------|---------|--------------|
| [docs/developer/JOB_DEFINITION_DICTIONARY.md](docs/developer/JOB_DEFINITION_DICTIONARY.md) | **Job state reference** — job.json fields, backend run/step_run fields, status values, transitions, mapping | When working with job state, status transitions, or backend sync |
| [docs/developer/ARCHITECTURAL_REFACTOR.md](docs/developer/ARCHITECTURAL_REFACTOR.md#race-conditions) | **Race condition fixes** — pre-execution backend sync, post-execution conflict check (see Race Conditions section) | When working on daemon-mode execution or result syncing |
| [QWEN.md](QWEN.md) | **Runtime modes** — CLI, Daemon, Manual mode descriptions | For understanding how jobs are executed |

**Key concepts from JOB_DEFINITION_DICTIONARY.md:**
- **job.json**: Local file at `~/.ukbe-runner/jobs/{template_group}/{job_id}/job.json`
- **Schema version**: 6 (v2 runner)
- **Non-terminal statuses**: IN_PROGRESS, WAITING_FOR_AUTO_RETRY, WAITING_FOR_HUMAN_APPROVAL, WAITING_FOR_HUMAN_INTERVENTION, WAITING_FOR_HUMAN_MAXRETRIED
- **Terminal statuses**: COMPLETED, FAILED, STOPPED
- **Backend mapping**: job_status → run_status (e.g., IN_PROGRESS → pending, COMPLETED → completed)

---

### Workflow Development

| Document | Purpose | When to Read |
|----------|---------|--------------|
| [QWEN.md](QWEN.md) | **Workflow package system** — workflow.toml structure, StepConfig, WorkflowBundle, BundleGovernance | When creating or modifying workflows |
| [masterplan/WORKFLOW_EXTENSION_INTERFACE_PLAN.md](masterplan/WORKFLOW_EXTENSION_INTERFACE_PLAN.md) | **WorkflowExtensions pattern** — how workflows hook into the runner | When implementing custom workflow logic |

**Workflow package structure:**
```
workflows/<name>/
├── workflow.toml         # Manifest: steps, artifacts, coder roles, routing
├── prompts/              # Prompt template .txt files
├── actions.py            # Custom action implementations
├── context_extensions.py # Workflow-specific context injection
├── output_paths.py       # Workflow-owned path contracts
└── bundle_governance/    # Generated AGENTS.md, CLAUDE.md, QWEN.md, prompt_contract.json
```

---

### SDLC Workflows

| Document | Purpose | When to Read |
|----------|---------|--------------|
| [masterplan/LAYER3_AI_DRIVEN_SDLC_SPECIFICATION.md](masterplan/LAYER3_AI_DRIVEN_SDLC_SPECIFICATION.md) | **SDLC workflow chain** — 9 workflows (sdlc_00 through sdlc_80) | When working on SDLC delivery workflows |
| [masterplan/SDLC_WORKFLOW_SCAFFOLD_PLAN.md](masterplan/SDLC_WORKFLOW_SCAFFOLD_PLAN.md) | **Scaffold workflow** — sdlc_00_delivery_scaffold_v1 | When working on delivery folder structure |
| [masterplan/SDLC_00_CODEBASE_V1_PLAN.md](masterplan/SDLC_00_CODEBASE_V1_PLAN.md) | **Codebase workflow** — codebase_inventory_v1 | When working on codebase documentation |
| [masterplan/SDLC_CONSOLE_APP_PLAN.md](masterplan/SDLC_CONSOLE_APP_PLAN.md) | **Console app** — operator console development | When working on the Flet-based GUI |

**SDLC workflow chain:**
```
sdlc_00_init_doc_v1      → DRAFT_INIT_FILE → INIT_FILE
sdlc_10_requirement_v1   → INIT_FILE → REQ_FILE
sdlc_20_planning_v1      → REQ_FILE → PLAN_FILE
sdlc_30_backlog_v1       → PLAN_FILE → BACKLOG_FILE
sdlc_40_task_v1          → BACKLOG_FILE → TASK_FILE
sdlc_50_implementation_v1 → TASK_FILE → IMPL_FILE
sdlc_60_execution_v1     → IMPL_FILE → EXEC_FILE
sdlc_70_validation_v1    → EXEC_FILE → VAL_FILE
sdlc_80_review_v1        → VAL_FILE → REV_FILE, MEM_FILE, CLOSE_FILE
```

---

### Tracking & Plans

| Document | Purpose | When to Read |
|----------|---------|--------------|
| [docs/developer/DOCSTRING_REVIEW_PLAN.md](docs/developer/DOCSTRING_REVIEW_PLAN.md) | **Docstring coverage tracking** — 95 files, 585 missing docstrings | When adding docstrings or tracking documentation coverage |
| [docs/developer/ARCHITECTURAL_REFACTOR.md](docs/developer/ARCHITECTURAL_REFACTOR.md) | **Refactor implementation plan** — Phase 1-3 with code examples and results | When implementing the CLI-only architecture (consolidates spec, findings, and race conditions) |

---

## Document Relationships

```
README.md (you are here)
  └─> QWEN.md (comprehensive reference)
       ├─> docs/developer/CODER_IMPLEMENTATION_SOP.md (coding rules)
       ├─> docs/developer/AGENT_RUNNER_V2_SPECIALIST.md (navigation)
       └─> docs/developer/JOB_DEFINITION_DICTIONARY.md (job state)

docs/developer/ARCHITECTURAL_REFACTOR.md (consolidated architecture refactor)
  ├─> Supersedes: docs/archive/ARCHITECTURAL_REFACTOR_FINDINGS.md
  ├─> Supersedes: docs/archive/ARCHITECTURAL_REFACTOR_SPEC.md
  └─> Supersedes: docs/archive/DAEMON_RACE_CONDITIONS.md

masterplan/
  ├─> LAYER_ARCHITECTURE_MASTERPLAN.md (layer boundaries)
  ├─> LAYER1_GOVERNANCE_SPECIFICATION.md (L1 rules)
  ├─> LAYER2_PLATFORM_CORE_SPECIFICATION.md (L2 platform)
  └─> LAYER3_AI_DRIVEN_SDLC_SPECIFICATION.md (L3 workflows)
```

---

## What's NOT Here

**Archived guidance:** Historical root guidance and superseded documents are in `docs/archive/`. Do not use archived docs as current reference.

**Developer documentation:** Active developer docs are in `docs/developer/` — see the tables above for specific documents.

**Batch scripts:** All run-*.bat, run-*.sh, submit-*.bat, submit-*.sh scripts are in `scripts/`.

**Generated governance docs:** Live under `docs/system/00_governance/` — these are generated by workflows, not manually maintained.

**Workflow-specific docs:** Each workflow has its own `bundle_governance/` folder with AGENTS.md, CLAUDE.md, QWEN.md — these are auto-generated from workflow.toml.

**Masterplan delivery artifacts:** `masterplan/delivery/` contains templates, initiatives, plans, tasks, reviews — these are SDLC workflow outputs, not reference documentation.

---

## Authority Order

When documents conflict, use this authority order:

1. **Active workflow files** under `workflows/<name>/`
2. **Current runner code** under `agent_runner_v2/`
3. **Generated governance docs** under `docs/system/00_governance/bootstrap/`
4. **Generated repo-local docs** under `docs/repo/*`
5. **This documentation** (README.md, QWEN.md, etc.)

Root markdown files are **not authoritative** for workflow design or documentation contracts. They are reference material only.

---

## Quick Reference

### Development Commands

```bash
# Install editable with dev dependencies
.venv\Scripts\python -m pip install -e ".[dev]"

# Run all unit tests
.venv\Scripts\python -m pytest tests/unit/ -v

# Run with coverage
.venv\Scripts\python -m pytest tests/unit/ --cov=agent_runner_v2 --cov-report=term-missing

# Run workflow-grouped tests
.venv\Scripts\python tests/run_workflow_unit_tests.py all
```

### Key Entry Points

| Task | Entry Point |
|------|-------------|
| CLI execution | `agent_runner_v2/run_agent.py` → `main()` |
| Daemon polling | `agent_runner_v2/daemon.py` → `_run_supervisor()` |
| Step execution | `agent_runner_v2/step_runner.py` → `run_step()` |
| Job state management | `agent_runner_v2/job_state.py` → `load_job()`, `save_job()` |
| Workflow routing | `agent_runner_v2/workflow_router.py` → `route_after_step()` |
| Backend sync | `agent_runner_v2/daemon_runtime.py` → `build_job_sync_payload()` |

### Key Directories

| Directory | Purpose |
|-----------|---------|
| `agent_runner_v2/` | Core runner code |
| `workflows/` | Workflow packages (plugin-based) |
| `tests/unit/` | Unit tests (pure logic, no filesystem) |
| `tests/integration/` | Integration tests (real files, subprocesses) |
| `docs/system/00_governance/` | Generated governance docs |
| `docs/repo/` | Generated repo-local docs |
| `docs/developer/` | Active developer documentation |
| `docs/archive/` | Superseded historical documents |
| `masterplan/` | Architecture specs and design docs |
| `scripts/` | Workflow-specific batch scripts (reference only) |
| `~/.ukbe-runner/` | Global runner home (config, bundles, jobs) |

### Batch Scripts

**Active scripts (in root):**
- `run-daemon.bat` / `run-daemon.sh` — Start the backend-connected daemon
- `run-console.bat` / `run-console.sh` — Launch the Flet-based operator console
- `run-init.bat` / `run-init.sh` — Install bootstrap bundle and seed workflows
- `run-cleanup-workflow.bat` / `run-cleanup-workflow.sh` — Clean up workflow runs
- `run-bootstrap-publish.bat` / `run-bootstrap-publish.sh` — Build packaged bootstrap bundle
- `sync-workflows-to-backend.bat` / `sync-workflows-to-backend.sh` — Sync workflow definitions to backend

**Workflow-specific scripts (in `scripts/`):**
- `run-*.bat` / `run-*.sh` — Individual workflow execution scripts
- `submit-*.bat` / `submit-*.sh` — Workflow submission scripts

**Note:** Workflow operations are typically done through the operator console (`run-console.bat`) rather than individual batch scripts.

---

## Maintenance

**Adding new documentation:**
1. Create the document in the appropriate location
2. Add it to this README.md index
3. Update QWEN.md if it's a major architectural change
4. Link from related documents

**Updating this index:**
- Keep the "When to Read" column actionable and specific
- Group documents by user intent, not by file location
- Remove documents that are archived or superseded
- Keep the "Authority Order" section current

---

## Contact & Support

- **Bug reports:** Use `/bug` command in Qwen Code
- **Architecture questions:** Refer to QWEN.md and masterplan specs
- **Coding questions:** Refer to CODER_IMPLEMENTATION_SOP.md
- **Navigation help:** Refer to AGENT_RUNNER_V2_SPECIALIST.md
