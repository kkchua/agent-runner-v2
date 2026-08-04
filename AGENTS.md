# AGENTS.md — agent-runner-v2

## Coding Rules

- Do not add new dependencies unless required.
- Prefer explicit code over magic.
- All new endpoints must have tests.
- Do not commit secrets.
- Use type hints.
- Keep functions small and testable.
- All path constants must use the layered system in `constants.py` — no hardcoded path strings in production code.
- Workflow prompt placeholders must use `{ARTIFACT_KEY_*}` keys from `artifact_keys.py`, resolved via `known_artifact_paths()`.
- The `meta.json` sidecar is the sole coder-to-runner communication channel. No stdout parsing, no pre-invocation sidecar writes.
- All development happens on the `dev` branch. `master` is the stable release branch — never commit directly to it.

## Definition of Done

A task is not complete until:

- The requested change is implemented.
- Relevant tests are added or updated.
- Tests pass: `.venv\Scripts\python -m pytest tests/unit/ -v`
- If setup, commands, architecture, environment variables, dependencies, or workflows changed, update:
  - AGENTS.md
  - README.md if human-facing behavior changed
- If a new convention is introduced, document it here.

## Quick Start for Agents

First time working on this repo? Do this in order:

1. **Read [README.md](README.md)** — master documentation index, architecture overview, entry points.
2. **Read [docs/developer/CODER_IMPLEMENTATION_SOP.md](docs/developer/CODER_IMPLEMENTATION_SOP.md)** — 8 mandatory execution rules and pattern compliance (read before writing code).
3. **Set up environment** (see [Environment Setup](#environment-setup) below).
4. **Run tests** to confirm baseline: `.venv\Scripts\python -m pytest tests/unit/ -v`
5. **Read the [Project Reference](#project-reference) section** of this file for system context.

## Do NOT

- **Do not edit bootstrap copies.** Files under `agent_runner_v2/bootstrap/` and `docs/system/00_governance/bootstrap/` are packaged snapshots. Edit the repo-local source under `workflows/` instead.
- **Do not edit generated governance docs.** Files under `bundle_governance/generated/` are auto-generated from `workflow.toml`. Edit the workflow manifest, not the output.
- **Do not touch `daemon.py`.** It is the V1 daemon, deprecated. All daemon work goes in `daemon_v2.py`.
- **Do not touch `operator_console/`.** It is the legacy Flet console, deprecated. The React console lives in the `operator-console-v2` repo.
- **Do not add error handling for impossible cases.** Only validate at system boundaries (user input, external APIs, file I/O).
- **Do not add broad `try/except` or silent `None` returns.** Use explicit exceptions (`ConfigurationError`, `NotFoundError`). See `exceptions.py`.
- **Do not use `if/elif` chains for dispatch.** Use the registry pattern (`CODER_REGISTRY` in `coder_adapters.py`).
- **Do not use long parameter lists.** Use dataclass config objects (e.g., `SupervisorConfig` in `daemon_v2.py`).
- **Do not hardcode path strings.** Use the layered constant system: `artifact_keys.py` → `path_primitives.py` → `path_catalog.py`, re-exported by `constants.py`.

## Environment Setup

```bash
# Create virtual environment (first time only)
python -m venv .venv

# Install editable with dev dependencies
.venv\Scripts\python -m pip install -e ".[dev]"

# Copy .env.example to .env and fill in credentials
copy .env.example .env

# Initialize global runner home (~/.ukbe-runner/)
.venv\Scripts\python -m agent_runner_v2.run_agent init
```

**Key paths:**
- `.venv\Scripts\python` — always use this for Python/pytest (not system Python)
- `~/.ukbe-runner/config.json` — runner engine config (backend URL, worker ID, engine version)
- `~/.ukbe-runner/jobs/` — job state directories

## Change Log

- 2026-08-04: Initial agent instructions added.

---

## Project Reference

Minimal context for understanding the system. See README.md for full details.

### Three-Repo Platform

| Repo | Role |
|------|------|
| **agent-runner-v2** (this repo) | Daemon + CLI execution engine (Python 3.12+) |
| **agent-runner-backend-v2** | State machine + persistence (FastAPI, PostgreSQL, port 8200) |
| **operator-console-v2** | Web-based operator UI (React 19, Vite, TypeScript) |

### Runtime Modes

| Mode | Entry point | Description |
|------|------------|-------------|
| **CLI** | `ukbe-run-agent run --template-group <name>` | Direct execution from batch file or terminal |
| **Daemon** | `ukbe-run-agent daemon [worker-id]` | Polls backend for claims, spawns child subprocess per step |
| **Worker** | `ukbe-run-agent worker --backend-url URL --worker-id ID` | Backend-connected worker mode |
| **Manual** | `ukbe-run-agent run --mode manual` | Human-in-the-loop with approval gating |

The daemon spawns a fresh subprocess per workflow invocation, so code changes are picked up without restarting. Only `daemon_v2.py` changes require a daemon restart.

### Workflow Package System

Each workflow is a self-contained directory with a `workflow.toml` manifest:

```
workflows/<name>/
├── workflow.toml         # Manifest: steps, artifacts, coder roles, routing
├── prompts/              # Prompt template .txt files
├── actions.py            # Custom action implementations
├── context_extensions.py # Workflow-specific context injection
├── output_paths.py       # Workflow-owned path contracts
└── bundle_governance/    # Generated governance docs (do not edit)
```

**Steps** are either prompt-driven (`.txt` template → LLM coder) or action-driven (Python function). After execution, the coder writes a `meta.json` sidecar — the sole communication channel.

**Artifacts** are named outputs tracked through workflow state. Canonical keys in `artifact_keys.py`, paths resolved via `known_artifact_paths()` in `constants.py`.

**Routing:** `onsuccess` → next step, `on_reject_refine` → refinement loop, `on_exhaust_replan` → replan, or failure routing via `route_after_failure()`.

### Key Source Modules

| Module | Purpose |
|--------|---------|
| `run_agent.py` | CLI entry point (`ukbe-run-agent`) — all subcommands |
| `daemon_v2.py` | V2 daemon — self-contained worker loop |
| `step_runner.py` | Core step execution (coder invoke → validate → sidecar) |
| `coder_adapters.py` | LLM/coder invocation via `CODER_REGISTRY` dispatch |
| `coder_registry.py` | Coder role → policy resolution |
| `workflow_packages/` | Plugin-based workflow package system |
| `constants.py` | Layered path constant re-exports |
| `v2/backend_client.py` | HTTP client for state-machine backend |
| `v2/sync.py` | Outcome sync to backend |
| `actions/` | 30+ action modules (copy, validate, scan, publish, …) |
