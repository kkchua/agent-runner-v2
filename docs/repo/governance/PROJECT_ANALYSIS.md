---
template_id: "SYS-00-PA"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-16T22:09:21+08:00"
workflow: "00_repo_master_docs_bootstrap_v1"
step: "02_generate_project_analysis"
change_id: "00RMD-20260716-5ee28fa5"
---

# Project Analysis: agent-runner-v2

## Repo Overview

`agent-runner-v2` is a standalone workflow runner extracted from UKBE (UK Build Engine). It orchestrates AI-Driven SDLC workflows with human approval gates, managing the full lifecycle of software development artifacts from requirements through validation.

The runner executes declarative workflow bundles defined in TOML manifests, invoking LLM coders for generative steps and deterministic Python actions for validation and file operations. It supports multiple execution modes: CLI-based manual execution, daemon-based backend worker mode, and a hybrid daemon-manual unification path.

Key capabilities:
- **Workflow orchestration**: Step-by-step execution with routing logic (approve/reject/replan)
- **Coder abstraction**: Pluggable LLM backend integration with sidecar metadata contracts
- **Action library**: Deterministic Python functions for file operations, validation, and site generation
- **Bootstrap governance**: Layer 1 ecosystem governance and Layer 2 repo master docs generation
- **Dual deployment**: Global runner home and local project runtime paths

## Codebase Structure

```
agent-runner-v2/
├── agent_runner_v2/           # Main package (70 modules)
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
├── scripts/                    # Batch scripts for workflow execution
└── *.bat                       # Root-level launcher scripts (13 files)
```

**Module areas**:
- `core`: `run_agent.py`, `step_runner.py`, `workflow_router.py`
- `coder`: `coder_adapters.py`, `model_config.py`
- `backend`: `daemon.py`, `backend_client.py`, `runner_logger.py`
- `actions`: 29 deterministic action modules
- `support`: Runtime utilities, context builders, notifications

**Workflow bundles** (bootstrap families):
- `00_bootstrap_lifecycle_admin_v1`: Bootstrap lifecycle management (5 steps)
- `00_layer1_governance_bootstrap_v1`: Layer 1 governance generation (6 steps)
- `00_repo_master_docs_bootstrap_v1`: Repo master docs bootstrap (14 steps)

## Workflow and Runtime Model

### Execution Model

The runner follows a step-by-step execution model:

1. **Workflow loading**: TOML manifest → `WorkflowBundle` dataclass
2. **Step execution**: Coder (LLM) or Action (Python) based on step type
3. **Routing**: Post-step routing based on result (approve/reject/replan)
4. **State management**: Job state persisted to `.ukbe-runner/jobs/<job_id>/`
5. **Notifications**: Optional Pushover notifications on step completion

### Coder/Action Split

- **Coder steps**: Invoke external LLM processes (OpenCode, Claude, etc.)
  - Prompt templates rendered with context placeholders
  - Sidecar `meta.json` contract for result reporting
  - Timeout handling and process management via `coder_adapters.py`

- **Action steps**: Deterministic Python functions
  - Registered via `@action()` decorator
  - Direct filesystem and validation operations
  - No external process dependencies

### Sidecar Contract

Each step produces a `meta.json` sidecar file containing:
- `coder_result`: Status (APPROVED/REJECTED), artifacts, remark
- `runner_data`: Invocation metadata, timestamps, checksums
- `usage`: Token counts and model information

### Workflow Bundle Architecture

The plugin-based workflow package system (`workflow_packages/`) provides:
- `WorkflowBundle`: Canonical validated workflow definition
- `StepConfig`: Per-step configuration with artifact contracts
- `BundleGovernance`: Optional governance extension for generated artifacts
- `context_extensions.py`: Workflow-specific context hooks

Dual-path discovery: Global `%USERPROFILE%\.ukbe-runner\workflows\` first, local `agent_runner_v2/bootstrap/workflows/default/` fallback.

## Operational Risks

| Risk | Impact | Mitigation Status |
|------|--------|-------------------|
| Layer 2 bootstrap incomplete | Blocks SDLC workflow-family work | Requires restoration of `00_master_docs_bootstrap_v2` from archive |
| Plugin migration incomplete | Legacy `TEMPLATE_GROUPS` still referenced | Active migration on `feat/plugin-workflow-system` branch |
| Delivery-era artifact keys | Runtime not aligned to SDLC structure | Migration plan documented, constants update pending |
| Daemon subprocess CWD | `.env` loading failures if CWD wrong | Fixed in recent commits (v0.3.0) |
| Windows path handling | `Path.relative_to()` edge cases | Fixed with fallback logic in `run_agent.py` |
| Notification credentials | Missing Pushover tokens cause silent failures | Credential resolution documented in memory |
| Test infrastructure drift | Unit tests using `tmp_path` moved to integration | 45 pure unit tests passing, integration tests stabilized |

## Architectural Observations

### Design Patterns

1. **Adapter pattern**: Plugin system converts `WorkflowBundle` → legacy dict format, preserving execution pipeline compatibility
2. **Sidecar contract**: Meta.json decouples coder output from runner state management
3. **Layer dependency chain**: Layer 1 (governance) → Layer 2 (master docs) → Layer 3+ (SDLC workflows)
4. **Dual-path deployment**: Global runner home for stable workflows, local project for development

### Constraints

- **Zero mutation of source code**: Bootstrap workflows must not alter code, only docs
- **Absolute paths in context**: All placeholder paths must be absolute for Windows compatibility
- **Artifact key normalization**: Auto-corrects common LLM mistakes (e.g., `_METAJSON` suffix)
- **Declarative doc protection**: Allow-list model for document deletion safety

### Technical Debt

- Legacy `TEMPLATE_GROUPS` dict in `template_groups.py` (2453 lines) being replaced by plugin packages
- Delivery-era artifact keys (`DRAFT_INIT_FILE`, etc.) need migration to SDLC semantics
- Multiple runtime entrypoints (`run_agent.py`, `daemon.py`) being unified

## Architecture Posture

| Attribute | Value | Evidence |
|-----------|-------|----------|
| `current_profile` | transitional | Migrating from monolithic `TEMPLATE_GROUPS` to plugin-based workflow packages |
| `target_profile` | plugin-based workflow bundles | `workflow_packages/` directory with `base.py`, `loader.py`, `registry.py` |
| `migration_mode` | active | Branch `feat/plugin-workflow-system`, version 0.3.0, recent refactor commits |
| `repo_state` | explicit | Has `CODER_IMPLEMENTATION_SOP.md`, governance docs under `docs/system/00_governance/` |
| `evidence_sources` | codebase inventory, module docs, migration plan, GUIDE docs | `docs/repo/codebase/01_inventory/`, `docs/system/03_ai_driven_sdlc_migration_plan.md` |

**Migration trajectory**:
- From: Monolithic `TEMPLATE_GROUPS` dict with hardcoded workflow definitions
- To: Self-contained plugin workflow packages with declarative TOML manifests
- Status: Bootstrap workflows migrated, legacy SDLC workflows pending

**Layer dependency status**:
- Layer 1: ✅ `00_layer1_governance_bootstrap_v1` operational
- Layer 2: ⚠️ `00_master_docs_bootstrap_v2` in archive, needs restoration
- Layer 3+: ❌ Blocked until Layer 2 complete

## Unresolved Documentation Gaps

| Gap | Required Resolution | Blocking Step |
|-----|---------------------|---------------|
| Layer 2 bootstrap workflow missing from live workflows | Restore `00_master_docs_bootstrap_v2` from archive as `00_master_docs_bootstrap_v1` | All SDLC workflow-family work |
| SDLC governance baseline not generated | Run restored master-docs bootstrap to create `docs/repo/sdlc/00_governance/` | SDLC workflow onboarding |
| Artifact key migration plan not executed | Update `constants.py` with SDLC folder keys and artifact paths | SDLC workflow execution |
| Legacy delivery scaffold compatibility | Document read-only alias from `docs/repo/delivery/` to `docs/repo/sdlc/` | Migration cut-over |
| Workflow package developer guide completeness | Validate GUIDE docs against actual migration patterns | Future workflow migrations |
| Architecture site documentation | Generate architecture site from current codebase state | Stakeholder visibility |
