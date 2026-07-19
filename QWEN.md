# QWEN.md — agent-runner-v2

## Project Identity

**agent-runner-v2** (v0.3.0) is a standalone, multi-step AI workflow runner extracted from UKBE. It orchestrates LLM-powered ("coder") workflows defined in TOML manifests, supporting prompt-driven generation, action-based automation, human-in-the-loop approval, and daemon-based backend polling.

## Architecture

```
agent_runner_v2/
├── run_agent.py              # CLI entry point (ukbe-run-agent)
├── daemon.py                 # Backend-polling supervisor daemon
├── step_runner.py            # Core step execution (coder invoke → validate → sidecar)
├── workflow_router.py        # Post-step routing (approve/reject/refine/failure)
├── job_state.py              # On-disk job state management
├── bundle_loader.py          # Bootstrap bundle install, publish, workflow module loading
├── bundle_governance.py      # Bundle governance adapter generation
├── coder_adapters.py         # LLM/coder invocation abstraction
├── coder_registry.py         # Coder role → policy resolution
├── notification_manager.py   # Pushover + console notifications
├── documentation_guardrails.py # Cleanup + guardrail policies
│
├── workflow_packages/        # Plugin-based workflow package system
│   ├── base.py               #   StepConfig, WorkflowBundle, BundleGovernance dataclasses
│   ├── loader.py             #   TOML → WorkflowBundle → TEMPLATE_GROUPS dict adapter
│   └── registry.py           #   WorkflowRegistry discovery and lookup
│
├── actions/                  # 30 action modules (copy, validate, scan, publish, assemble, …)
│
├── constants.py              # Layered re-export: artifact_keys → path_primitives → path_catalog
├── artifact_keys.py          # Canonical artifact key literals (ARTIFACT_KEY_*)
├── path_primitives.py        # Stable filename/root constants, helper functions
├── doc_paths.py              # Re-exports all path constants from primitives + catalog
├── path_catalog.py           # known_artifact_paths(), legacy_artifact_paths(), site page maps
├── workflow_path_contracts.py # Workflow-owned output path contracts
│
├── bootstrap/
│   ├── bundles/core/current/ # Packaged bootstrap docs (installed via `init`)
│   └── workflows/default/    # 4 canonical bootstrap workflow packages:
│       ├── 00_bootstrap_lifecycle_admin_v1/
│       ├── 01_governance_foundation_v1/
│       ├── 00_layer1_governance_bootstrap_v1/
│       └── 00_repo_master_docs_bootstrap_v1/
│
├── operator_console/         # Flet-based desktop operator GUI
│   ├── app.py                #   Desktop console window (ukbe-run-agent console)
│   ├── config.py             #   Console config loader (repos + workflows)
│   ├── models.py             #   ConsoleConfig, GlobalSettings, ActiveRunSummary dataclasses
│   └── services/
│       ├── backend_service.py#   Backend API calls (list/stop/approve runs)
│       └── runner_service.py #   Local runner invocations (submit, approve, init, sync, …)
│
├── runtime_context.py        # PROJECT_ROOT, RUNNER_ROOT, JOBS_ROOT, ARTIFACT_ROOT
├── config_loader.py          # Runner config.json loading
├── execution_core.py         # execute_routed_step, invoke_prepared_step
├── execution_request.py      # ExecutionRequest dataclass
├── execution_result.py       # ExecutionResult, ExecutionFailure dataclasses
├── exceptions.py             # ArtifactMissingError, MetaJsonMissingError, PreflightBlockedError
├── workflow_specs.py         # Step execution spec resolution (global/backend/hybrid)
├── workflow_bundle_validator.py # Preflight validation for workflow bundles
└── sync_workflows.py         # Workflow bundle sync to backend
```

## Runtime Modes

| Mode | Entry point | Description |
|------|------------|-------------|
| **CLI** | `ukbe-run-agent run --template-group <name>` | Direct execution from a batch file or terminal |
| **Daemon** | `ukbe-run-agent daemon [worker-id]` | Polls backend for claims, spawns child subprocess per step |
| **Manual** | `ukbe-run-agent run --mode manual` | Human-in-the-loop with approval gating |

The daemon spawns a fresh subprocess for each workflow invocation (identical to manual batch files), so **code changes are picked up automatically** without restarting the daemon itself. Only `daemon.py` changes require a daemon restart.

## Workflow Package System

Each workflow is a self-contained directory with a `workflow.toml` manifest:

```
workflows/<name>/
├── workflow.toml         # Manifest: steps, artifacts, coder roles, routing
├── prompts/              # Prompt template .txt files
├── actions.py            # Custom action implementations
├── context_extensions.py # Workflow-specific context injection
├── output_paths.py       # Workflow-owned path contracts
└── bundle_governance/    # Generated AGENTS.md, CLAUDE.md, QWEN.md, prompt_contract.json
```

### workflow.toml structure

- **`[workflow]`** — name, version, label, job_prefix, visibility, default_max_rejects, init step
- **`[[step]]`** — name, prompt (or action), onsuccess routing, requires_human_approval_after, enable_notifications
- **`[step.artifacts]`** — produces, required_inputs, optional_inputs, result_meta_key, target_artifact, edit_mode
- **`[step.coder]`** — role_policy, must_differ, allowed roles
- **`[step.on_reject_refine]`** — refine step, artifact, max_iterations, exhausted failure code
- **`[step.on_exhaust_replan]`** — replan step and artifact

### Key dataclasses (from `workflow_packages/base.py`)
- `StepConfig` — validated step configuration
- `WorkflowBundle` — full bundle: name, version, steps, init step, governance
- `BundleGovernance` — governance contract with adapter targets, extensions, artifact registry

## Key Concepts

### Artifacts
Named outputs tracked through workflow state. Canonical keys are defined in `artifact_keys.py` (e.g., `REVIEW_FILE_SUGGESTED`, `DELIVERY_AGENTS`, `CODEBASE_INVENTORY`). Artifact paths are resolved via `known_artifact_paths()` in constants.py.

### Steps
Each step is either:
- **Prompt-driven** — a `.txt` template rendered with context, sent to a coder (LLM)
- **Action-driven** — a Python function in `actions/` or the workflow's `actions.py`

After execution, the coder writes a `meta.json` sidecar — the sole communication channel (no stdout parsing).

### Routing
Post-step routing: `onsuccess` → next step, `on_reject_refine` → refinement loop, `on_exhaust_replan` → replan, or failure routing via `route_after_failure()`.

### Coder Roles
Role policies (e.g., `architect_standard`, `reviewer_standard`, `refine_standard`, `validation_standard`) map to coder configurations resolved by `coder_registry.py`.

## Directory Layout (Runtime)

```
<project_root>/
├── agent_runner_v2/           # Source package
├── tests/
│   ├── unit/                  # Pure logic tests (no filesystem deps)
│   ├── integration/           # Real files, subprocesses, external systems
│   └── conftest.py            # Shared fixtures
├── docs/
│   ├── repo/                  # Generated repo-local docs
│   │   ├── codebase/
│   │   ├── delivery/
│   │   ├── audience/
│   │   ├── site/
│   │   └── governance/
│   └── system/00_governance/bootstrap/  # Generated master governance docs
├── workflows/                 # Project-local workflow packages (plugin-based)
├── run-*.bat                  # Convenience batch files
├── pyproject.toml
├── requirements.txt
├── .env.example
└── operator-console.example.json

~\.ukbe-runner\                # Global runner home
├── config.json                # Runner configuration (backend URL, worker ID, engine)
├── bundles/core/current/      # Installed bootstrap bundle
├── workflows/default/         # Seeded workflow bundle
└── jobs/                      # Job state directories
```

## Development Commands

Always use `.venv\Scripts\python` (Windows) for Python and pytest commands in this repository.

```bash
# Install editable with dev dependencies
.venv\Scripts\python -m pip install -e ".[dev]"

# Run all unit tests
.venv\Scripts\python -m pytest tests/unit/ -v

# Run unit tests with marker
.venv\Scripts\python -m pytest tests/unit/ -v -m unit

# Run integration tests
.venv\Scripts\python -m pytest tests/integration/ -v -m integration

# Run with coverage
.venv\Scripts\python -m pytest tests/unit/ --cov=agent_runner_v2 --cov-report=term-missing

# Run workflow-grouped tests
.venv\Scripts\python tests/run_workflow_unit_tests.py all

# Lint (no project-wide linter configured — rely on pytest)
```

## Key Conventions

1. **Layered constants** — All path constants flow: `artifact_keys.py` (keys) → `path_primitives.py` (roots/helpers) → `path_catalog.py` (computed mappings). `constants.py` re-exports everything. No hardcoded path strings in production code.

2. **Artifact placeholder resolution** — Workflow prompt templates use `{ARTIFACT_KEY_*}` placeholders matching keys from `artifact_keys.py`. Resolution uses `ARTIFACT_KEYS` + `known_artifact_paths()`, not the deprecated `REFERENCE_FILES` dict.

3. **Pure unit tests** — Unit tests test logic in isolation without filesystem dependencies. Use mocks for external systems. Filesystem-dependent tests go in `tests/integration/`.

4. **Daemon subprocess architecture** — The daemon spawns `python -m agent_runner_v2.run_agent run ...` per workflow. Code changes are picked up without restarting the daemon. Only `daemon.py` changes require daemon restart.

5. **Batch file conventions** — All `run-*.bat` activate `.venv` first, then invoke `ukbe-run-agent`. Use `ukbe-run-agent init` after `run-bootstrap-publish.bat` to seed the global runner home.

6. **meta.json sidecar** — The sole communication channel between coder and runner. No stdout JSON parsing, no pre-invocation sidecar writes, no disk recovery functions.

7. **Workflow-owned path contracts** — `workflow_path_contracts.py` defines output path mappings for each workflow. Bootstrap workflows use `resolve_workflow_output_paths()`.

8. **Runtime context** — `PROJECT_ROOT`, `RUNNER_ROOT`, `JOBS_ROOT`, `ARTIFACT_ROOT` are resolved at import time from `runtime_context.py`. Use `set_context()` to override in tests.

## Operator Console

A Flet-based desktop GUI (`ukbe-run-agent console`) for monitoring and managing workflow runs without a terminal.

**Launch:** `ukbe-run-agent console` (requires `pip install -e ".[console]"` for the `flet` dependency)

**Actions:**
| Action | Description |
|--------|-------------|
| submit job | Submit a new workflow job to the backend |
| approval | Approve (or reject) a run awaiting human decision |
| cancel job | Stop an active run on the backend |
| reset step | Override a job's current step to a different step |
| bootstrap | Run bootstrap-publish for the selected repo |
| init | Run init to seed workflow bundles into global runner home |
| sync | Sync workflow definitions to the backend |

**Configuration:**
- `~/.ukbe-runner/config.json` — provides `backend_url`, `worker_id`, `worker_label` (required for backend operations)
- `~/.ukbe-runner/operator-console.json` — lists `repos` (name + path) and `workflows` (name + workflow_name) to populate dropdowns

**Services:**
- `BackendRunService` — wraps `BackendClient` for listing active runs, stopping runs, approving/rejecting, fetching run detail
- `RunnerActionService` — invokes local runner CLIs (`run_agent.main`, `submit_commands.main`, `sync_workflows.main`) in subprocess via `_invoke()` with working-directory switching

## Config & Environment

- **`.env`** — ComfyUI credentials, TTS provider/keys, video assembly settings, Pushover tokens
- **`~/.ukbe-runner/config.json`** — Runner engine config (version, backend URL, worker ID, step spec source)
- **`operator-console.example.json`** — Operator console configuration template
- **`pyproject.toml`** — Package metadata, pytest configuration, setuptools package data
