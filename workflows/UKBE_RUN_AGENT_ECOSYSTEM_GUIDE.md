# ukbe-run-agent CLI Ecosystem — Complete Guide

> **Audience:** Developers, operators, and integrators of the agent-runner-v2 system.
> **Scope:** Explains the CLI architecture, engine internals, and the two operational modes: **Development Mode** and **User Mode**.

---

## Table of Contents

1. [Overview](#1-overview)
2. [CLI Architecture — The `ukbe-run-agent` Command](#2-cli-architecture)
3. [Engine Deep Dive — How Workflows Execute](#3-engine-deep-dive)
4. [Configuration System](#4-configuration-system)
5. [Development Mode](#5-development-mode)
6. [User Mode](#6-user-mode)
7. [Lifecycle: Bootstrap → Init → Install → Sync → Run](#7-lifecycle)
8. [Operator Console](#8-operator-console)
9. [Daemon & Worker Mode (Backend Integration)](#9-daemon--worker-mode)
10. [Engine Version Management](#10-engine-version-management)
11. [Troubleshooting & FAQ](#11-troubleshooting--faq)

---

## 1. Overview

`ukbe-run-agent` is the CLI entry point for the **agent-runner-v2** system — a workflow engine that orchestrates multi-step LLM-driven processes. It manages the complete lifecycle of a "workflow run": loading configuration, resolving job state, preparing prompts, invoking a coder (LLM agent), validating outputs, and routing to the next step.

The system has two distinct operational modes:

| Aspect | Development Mode | User Mode |
|---|---|---|
| Repo location | Cloned locally (e.g. `D:/.../agent-runner-v2`) | Installed from GitHub as a pip package |
| Engine source | Live source tree (`SNAPSHOT` or `PYTHONPATH`) | Versioned install in `~/.ukbe-runner/engine/versions/` |
| Workflow configs | Local `workflows/` + global `~/.ukbe-runner/workflows/` | Global `~/.ukbe-runner/workflows/` only |
| Step spec source | `global` or `hybrid` (local specs authoritative) | `backend` (backend API specs authoritative) |
| Development cycle | Edit → `bootstrap-publish` → `init` → `sync` → test | No code changes — pure CLI usage |
| Worker label | `dev` | `live` |

---

## 2. CLI Architecture

### 2.1 Entry Point

Defined in `pyproject.toml`:

```toml
[project.scripts]
ukbe-run-agent = "agent_runner_v2.run_agent:main"
```

When installed, `pip install` creates a `ukbe-run-agent` executable that calls `agent_runner_v2.run_agent.main()`.

### 2.2 Command Reference

The CLI dispatches based on the **first positional argument**. If the first argument starts with `-` or is missing, it defaults to the `run` command.

| Command | Purpose | Mode |
|---|---|---|
| `run` (default) | Execute a workflow step from a job. | Both |
| `init` | Initialize the global runner home from a bootstrap snapshot. | Dev |
| `install` | Install and sync workflow packages to the global runner home. | Both |
| `bootstrap-publish` | Publish a bootstrap snapshot from the local repo. | Dev |
| `daemon` | Start a persistent worker daemon (polls backend for work). | Both |
| `worker` | One-shot backend-connected worker. | Both |
| `poll` | Single-shot backend poll (reads env vars). | Both |
| `submit` | Submit a workflow run to the backend API. | Both |
| `approve` | Approve a pending step. | Both |
| `stop` | Stop an active run. | Both |
| `console` | Launch the desktop operator console (Flet GUI). | Both |
| `engine` | Manage engine versions (install, snapshot, use, list). | Both |
| `workflow-spec` | Workflow spec operations. | Dev |
| `sync-workflow-spec` | Sync workflow definitions to the backend API. | Dev |
| `codebase-init` | Initialize codebase documentation. | Dev |

### 2.3 Command Dispatch Flow

```
main(argv)
  |
  +-- args = parse_args(argv)
  |
  +-- args.command == "init"       -> init_workspace() + hooks
  +-- args.command == "install"    -> install_all() / sync_all()
  +-- args.command == "engine"     -> engine_commands.main()
  +-- args.command == "bootstrap-publish" -> publish_bootstrap_bundle()
  +-- args.command == "daemon"     -> daemon.main()
  +-- args.command == "worker"     -> _worker_command()
  +-- args.command == "poll"       -> _worker_command(once=True)
  +-- args.command == "execute-step" -> (legacy, returns error)
  +-- args.command == "submit"     -> submit_commands.main()
  +-- args.command == "workflow-spec" / "sync-workflow-spec" -> workflow_spec_commands
  +-- args.command == "approve"    -> approve_commands.main()
  +-- args.command == "stop"       -> stop_commands.main()
  +-- args.command == "console"    -> console_commands.main()
  +-- args.command == "codebase-init" -> codebase_init_commands.main()
  |
  +-- args.command == "run" (default) -> full execution pipeline (see section 3)
```

---

## 3. Engine Deep Dive

### 3.1 Execution Pipeline (for `ukbe-run-agent run`)

```
main()  [run_agent.py]
  |
  +-- 1. Load project config
  |     load_project_config(workspace_root)
  |     -> reads ~/.ukbe-runner/config.json
  |
  +-- 2. Resolve workflow root
  |     resolve_workflow_root(workspace_root, workflow_name, config)
  |     -> finds workflow bundle in ~/.ukbe-runner/workflows/<name>/
  |
  +-- 3. Load workflow module
  |     load_workflow_module(workspace_root, workflow_name, config)
  |     -> builds TEMPLATE_GROUPS dict from workflow.toml packages
  |
  +-- 4. Set runtime context
  |     set_context(workspace_root, workflow_name, workflow_root, ...)
  |
  +-- 5. Load template group config
  |     _load_group(template_group) -> group_cfg dict
  |
  +-- 6. Register artifact keys
  |     register_all_artifact_keys() -> populates ARTIFACT_PATHS
  |
  +-- 7. Handle admin commands
  |     handle_admin_command() -> --approve, --stop, --show-job, etc.
  |
  +-- 8. Resolve manual run
  |     resolve_manual_run() -> state, step
  |     * Creates new job if no --job-id
  |     * Resumes existing job if --job-id provided
  |     * Auto-resumes matching active job if no --new-job
  |
  +-- 9. Prepare step execution
  |     prepare_step_execution() -> PreparedStepExecution
  |     * Validates required inputs
  |     * Checks preflight artifact status
  |     * Creates step directory
  |     * Builds context (artifact paths, variables)
  |     * Resolves and renders prompt template
  |     * Resolves coder (which LLM/provider to use)
  |
  +-- 10. Execute routed step
  |     execute_routed_step()
  |     |
  |     +-- invoke_prepared_step()
  |     |   |
  |     |   +-- Is action? -> run_action() [non-coder step]
  |     |   |
  |     |   +-- Is coder? -> run_step() [LLM step]
  |     |       +-- invoke_coder() -> spawns coder process
  |     |       +-- reads meta.json (coder output contract)
  |     |       +-- validates produced artifacts
  |     |       +-- enriches sidecar with usage data
  |     |
  |     +-- On failure -> route_after_failure()
  |     |   +-- Refine loop (retry with feedback)
  |     |   +-- Replan (re-route to earlier step)
  |     |   +-- Recovery budget exceeded -> mark as failed
  |     |
  |     +-- On success -> route_after_step()
  |         +-- Advance to next step
  |         +-- Set job status (IN_PROGRESS / WAITING_FOR_HUMAN_APPROVAL / COMPLETED)
  |         +-- Save job state to job.json
  |
  +-- 11. Output result JSON to stdout
```

### 3.2 Key Internal Modules

| Module | Responsibility |
|---|---|
| `run_agent.py` | CLI entry point, orchestration, exception handling |
| `step_runner.py` | Core step execution: coder invocation, meta.json contract, artifact validation |
| `step_execution_runtime.py` | Step preparation: context building, prompt rendering, coder resolution |
| `execution_core.py` | Generic execution orchestration with pluggable executors and routers |
| `workflow_router.py` | Post-step state routing (success, failure, refine, replan, recovery) |
| `workflow_runtime.py` | Template group loading, reference file validation |
| `job_state.py` | Job CRUD, state transitions, status management, schema migration |
| `coder_adapters.py` | Coder process invocation, output parsing, usage tracking |
| `coder_registry.py` | Coder role resolution, effective coder selection |
| `runtime_context.py` | Process-local path context (workspace, runner home, workflow root) |
| `config_loader.py` | Global runner config loader (`~/.ukbe-runner/config.json`) |
| `bundle_loader.py` | Bundle loading, workspace init, bootstrap publishing |
| `daemon.py` | Worker daemon supervisor (claims backend work, spawns children) |
| `daemon_runtime.py` | Worker request building, job sync mapping |
| `backend_client.py` | HTTP client for backend API interactions |
| `manual_runtime.py` | Manual (CLI) mode job resolution |
| `cli_runtime.py` | Admin command handling (approve/stop/override) |
| `workflow_packages/` | Pluggable workflow bundle system |
| `operator_console/` | Flet-based desktop GUI |

### 3.3 Job State Machine

A job progresses through these statuses:

```
NEW -> IN_PROGRESS -> WAITING_FOR_HUMAN_APPROVAL -> IN_PROGRESS -> ... -> COMPLETED
                      |                              |
                      +--> WAITING_FOR_HUMAN_INTERVENTION (rejected/blocked)
                      +--> FAILED (recovery budget exceeded)
```

Job state is persisted to `~/.ukbe-runner/jobs/<template_group>/<job_id>/job.json`.

### 3.4 Workflow Package System

Workflows are defined as **self-contained packages** under `workflows/<name>/`:

```
workflows/<name>/
+-- workflow.toml          # Manifest: defines steps, artifacts, routing, coder config
+-- prompts/               # Prompt templates for each step
|   +-- 01_analyze.md
|   +-- 02_design.md
+-- context_extensions.py  # Optional: WorkflowExtensions subclass for lifecycle hooks
+-- actions.py             # Optional: custom non-coder actions (decorated with @action)
+-- install.py             # Optional: custom install script
```

The `workflow.toml` is parsed by `workflow_packages/loader.py` into a `WorkflowBundle` dataclass, then adapted into a `TEMPLATE_GROUPS`-style dict for the runner.

---

## 4. Configuration System

### 4.1 Configuration Sources (in priority order)

1. **CLI arguments** — highest priority, e.g. `--workflow`, `--template-group`, `--coder`
2. **Environment variables** — e.g. `AGENT_RUNNER_BACKEND_URL`, `AGENT_RUNNER_WORKER_ID`, `AGENT_RUNNER_V2_SRC`, `WORKER_LABEL`, `STEP_SPEC_SOURCE`
3. **Global runner config** — `~/.ukbe-runner/config.json`
4. **Operator console config** — `~/.ukbe-runner/operator-console.json`

### 4.2 Global Runner Config (`~/.ukbe-runner/config.json`)

```json
{
  "backend_url": "http://127.0.0.1:8100",
  "worker_id": "my-worker-1",
  "worker_label": "live",
  "engine_version": "SNAPSHOT",
  "repo_root": "D:/MyProjectSpace/01_Workflows/agent-runner-v2",
  "step_spec_source": "backend",
  "default_workflow": "default",
  "bundle_profile": "core+workflow",
  "bundle_domain": "general"
}
```

### 4.3 Key Paths

| Path | Purpose |
|---|---|
| `~/.ukbe-runner/` | Global runner home |
| `~/.ukbe-runner/config.json` | Global runner config |
| `~/.ukbe-runner/operator-console.json` | Operator console config |
| `~/.ukbe-runner/jobs/` | Job state storage |
| `~/.ukbe-runner/logs/` | Log files (`daemon.log`, `worker.log`) |
| `~/.ukbe-runner/runtime/` | Runtime data |
| `~/.ukbe-runner/bundles/core/current/` | Core bootstrap bundles (governance, foundation) |
| `~/.ukbe-runner/workflows/` | Installed workflow packages |
| `~/.ukbe-runner/engine/versions/` | Versioned engine installs |
| `<repo>/workflows/` | Repo-local workflow bundles (dev mode) |
| `<repo>/docs/system/00_governance/bootstrap/` | Published bootstrap snapshot |

### 4.4 `step_spec_source` Explained

Controls where the step execution specification is sourced from:

| Value | Behavior |
|---|---|
| `backend` | Use the step spec from the backend API (production default) |
| `global` | Use the local workflow bundle spec (development) |
| `hybrid` | Merge backend spec with local overrides; local fills gaps |

---

## 5. Development Mode

### 5.1 When to Use Development Mode

You are in **Development Mode** when:
- The `agent-runner-v2` repository is cloned locally (e.g., `D:/MyProjectSpace/01_Workflows/agent-runner-v2`)
- You are actively developing workflows, modifying prompt templates, or changing runner code
- You want to test changes immediately without publishing a new version

### 5.2 How Development Mode Works

The engine determines it is in development mode by checking:

1. **`AGENT_RUNNER_V2_SRC`** environment variable — if set, overrides the engine source to the specified path
2. **`engine_version`** in config — if `"SNAPSHOT"` or absent, the system runs from the live source tree
3. **`repo_root`** in config — points to the local repo clone so the system can find `workflows/` and other resources

When running in SNAPSHOT mode, the daemon (`daemon.py`) resolves the engine path like this:

```python
def _resolve_engine_pythonpath(cfg, log):
    src = os.environ.get('AGENT_RUNNER_V2_SRC', '').strip()
    if src:
        return src  # Explicit override

    version = cfg.get('engine_version', '').strip()
    if not version or version == 'SNAPSHOT':
        repo_root = cfg.get('repo_root', '').strip()
        if repo_root:
            return repo_root  # Live repo tree
        return None  # Fall back to ambient PYTHONPATH
```

### 5.3 Development Workflow

The development cycle is:

```
1. Edit code / workflows / prompts
       |
       v
2. Run bootstrap-publish
   ukbe-run-agent bootstrap-publish
   -> Validates all workflow bundles under workflows/
   -> Copies them to docs/system/00_governance/bootstrap/workflows/
   -> Also copies to agent_runner_v2/bootstrap/bundles/core/current/
   -> Rebuilds agent_runner_v2/bootstrap/workflows/default/
   -> Generates governance docs
       |
       v
3. Run init
   ukbe-run-agent init
   -> Creates ~/.ukbe-runner/ directory structure
   -> Installs bootstrap bundles to global runner home
   -> Seeds workflow packages to ~/.ukbe-runner/workflows/
   -> Runs workflow package hooks (install, init, sync)
       |
       v
4. Run sync (if needed)
   ukbe-run-agent sync-workflow-spec
   -> Discovers all workflow.toml packages
   -> Validates each bundle
   -> POSTs definitions to backend API
       |
       v
5. Run a workflow
   ukbe-run-agent run --template-group <name> [options]
   -> Runs from the live source tree
   -> References workflow configs from ~/.ukbe-runner/workflows/
```

### 5.4 Key Characteristics of Development Mode

| Aspect | Behavior |
|---|---|
| **Engine source** | Live source tree (`SNAPSHOT` or `PYTHONPATH`) |
| **Workflow source** | `~/.ukbe-runner/workflows/<name>/` (after init copies from repo) |
| **Config source** | Global `~/.ukbe-runner/config.json` |
| **Code changes** | Take effect immediately on next `run` — no reinstall needed |
| **Workflow changes** | Need `bootstrap-publish` + `init` to propagate to global |
| **Config changes** | Need manual `init` or `sync` to propagate to backend |
| **Worker label** | Typically `dev` (separate queue from production) |
| **Step spec source** | `global` or `hybrid` |

### 5.5 Development Mode Setup Steps

**Step 1: Clone the repo**
```bash
git clone https://github.com/kkchua/agent-runner-v2.git
cd agent-runner-v2
```

**Step 2: Install in editable mode**
```bash
pip install -e .
```

**Step 3: Configure global runner home**
Create `~/.ukbe-runner/config.json`:
```json
{
  "backend_url": "http://127.0.0.1:8100",
  "worker_id": "dev-worker",
  "worker_label": "dev",
  "engine_version": "SNAPSHOT",
  "repo_root": "D:/MyProjectSpace/01_Workflows/agent-runner-v2",
  "step_spec_source": "global",
  "default_workflow": "default"
}
```

**Step 4: Publish bootstrap and init**
```bash
ukbe-run-agent bootstrap-publish
ukbe-run-agent init
```

**Step 5: Run a workflow**
```bash
ukbe-run-agent run --template-group sdlc_10_requirement_v1 --set INIT_FILE=path/to/init.md
```

### 5.6 Development Mode: File Change Impact Matrix

| What you change | What you need to do |
|---|---|
| `agent_runner_v2/*.py` (runner code) | Nothing — re-run the command (live source) |
| `workflows/<name>/workflow.toml` | `bootstrap-publish` + `init` |
| `workflows/<name>/prompts/*.md` | `bootstrap-publish` + `init` (if referenced from global) |
| `workflows/<name>/context_extensions.py` | Re-run the command (imported at runtime) |
| `~/.ukbe-runner/config.json` | Nothing — re-read on each run |
| Backend API config | `sync-workflow-spec` |

---

## 6. User Mode

### 6.1 When to Use User Mode

You are in **User Mode** when:
- The `agent-runner-v2` repository is **not** available locally
- You installed `ukbe-run-agent` from GitHub as a pip package
- You use the CLI to install the engine, initialize the global setup, and run workflows
- You interact with the system through the operator console or CLI commands

### 6.2 How User Mode Works

In User Mode, the engine is installed as a **versioned copy** in the global runner home:

```
~/.ukbe-runner/engine/versions/
+-- 0.4.0/
|   +-- agent_runner_v2/
|   |   +-- run_agent.py
|   |   +-- ...
|   +-- version.json
+-- 0.3.0/
    +-- ...
```

The active version is set in `~/.ukbe-runner/config.json`:

```json
{
  "engine_version": "0.4.0"
}
```

When the daemon needs to spawn a child process, it resolves the engine from `~/.ukbe-runner/engine/versions/<version>/` and prepends it to `PYTHONPATH`.

### 6.3 User Mode Setup Steps

**Step 1: Install the CLI tool**
```bash
pip install ukbe-run-agent
# Or from GitHub directly:
pip install git+https://github.com/kkchua/agent-runner-v2.git
```

**Step 2: Install the engine version**
```bash
ukbe-run-agent engine install 0.4.0
```

**Step 3: Set the active version**
```bash
ukbe-run-agent engine use 0.4.0
```

**Step 4: Initialize the global setup**
```bash
ukbe-run-agent init
```

**Step 5: Configure the operator console**
Create `~/.ukbe-runner/operator-console.json`:
```json
{
  "repos": [
    {
      "name": "my-project",
      "path": "D:/MyProjectSpace/my-project",
      "workflows": [
        {
          "name": "SDLC: Requirement Intake",
          "workflow_name": "sdlc_10_requirement_v1",
          "template_group": "sdlc_10_requirement_v1"
        }
      ]
    }
  ]
}
```

**Step 6: Launch the operator console**
```bash
ukbe-run-agent console
```

### 6.4 User Mode CLI Commands

**Run a workflow directly:**
```bash
ukbe-run-agent run --template-group sdlc_10_requirement_v1 --set INIT_FILE=requirements.md
```

**Submit a run to the backend:**
```bash
ukbe-run-agent submit --workflow-name sdlc_10_requirement_v1
```

**Start the daemon (backend worker):**
```bash
ukbe-run-agent daemon my-worker --worker-label live
```

**Approve a pending step:**
```bash
ukbe-run-agent approve --job-id <job-id> --step <step-name>
```

**Stop an active run:**
```bash
ukbe-run-agent stop --job-id <job-id>
```

### 6.5 Key Characteristics of User Mode

| Aspect | Behavior |
|---|---|
| **Engine source** | Versioned install in `~/.ukbe-runner/engine/versions/` |
| **Workflow source** | `~/.ukbe-runner/workflows/<name>/` (seeded during init) |
| **Config source** | Global `~/.ukbe-runner/config.json` |
| **Code changes** | Require a new engine version install |
| **Workflow changes** | Require a new package version + re-init |
| **Worker label** | Typically `live` (production queue) |
| **Step spec source** | `backend` (backend API is authoritative) |

---

## 7. Lifecycle: Bootstrap → Init → Install → Sync → Run

### 7.1 `bootstrap-publish` (Development Only)

**Purpose:** Snapshots the current state of the repo's workflow definitions into a publishable bootstrap bundle.

**What it does:**
1. Validates all workflow bundles under `workflows/` (runs `validate_workflow_bundle_dir()`)
2. Copies validated workflows to `docs/system/00_governance/bootstrap/workflows/`
3. Copies the core bundle to `agent_runner_v2/bootstrap/bundles/core/current/`
4. Rebuilds `agent_runner_v2/bootstrap/workflows/default/` from repo workflows
5. Generates governance documentation for each workflow bundle

**When to run:** After any change to workflow definitions, prompts, or configs.

### 7.2 `init`

**Purpose:** Initializes the global runner home from a bootstrap snapshot.

**What it does:**
1. Creates `~/.ukbe-runner/` directory structure (`jobs/`, `logs/`, `runtime/`, `bundles/`, `workflows/`)
2. Installs the bootstrap bundle to `~/.ukbe-runner/bundles/core/current/foundation/`
3. Installs platform bundles to `~/.ukbe-runner/bundles/core/current/platform/`
4. Runs `install.py` scripts from workflow packages
5. Seeds workflow packages to `~/.ukbe-runner/workflows/`
6. Runs `WorkflowExtensions.init()` hooks on all discovered packages
7. Runs `WorkflowExtensions.install_to_global()` hooks
8. Runs `WorkflowExtensions.sync_to_backend()` hooks
9. Writes a bundle manifest to the runner home
10. Saves the project config

**When to run:** Once per environment setup, or after `bootstrap-publish` in dev mode.

### 7.3 `install`

**Purpose:** Install and sync workflow packages without re-running the full init.

**What it does:**
1. Discovers all workflow packages
2. Runs `install_to_global()` on each package
3. Runs `sync_to_backend()` on each package

**When to run:** After adding a new workflow package, or to refresh an existing one.

### 7.4 `sync-workflow-spec`

**Purpose:** Sync workflow definitions to the backend API registry.

**What it does:**
1. Discovers all `workflow.toml` packages
2. Validates each bundle locally
3. Strips runtime-only `_workflow_bundle` references
4. POSTs each definition to `{backend_url}/api/admin/workflows/sync`
5. Reports sync summary

**When to run:** After workflow definition changes, to register them with the backend.

### 7.5 Lifecycle Diagram

```
Development Mode:
-----------------
  [Edit code/workflows]
       |
       v
  bootstrap-publish  ->  Validates + snapshots + generates docs
       |
       v
  init  ->  Creates ~/.ukbe-runner/ + installs bundles + seeds workflows
       |
       v
  sync-workflow-spec  ->  Registers definitions with backend API
       |
       v
  run  ->  Executes workflow from live source

User Mode:
----------
  [Install CLI via pip]
       |
       v
  engine install <version>  ->  Downloads versioned engine to ~/.ukbe-runner/engine/versions/
       |
       v
  engine use <version>  ->  Sets active version in config.json
       |
       v
  init  ->  Seeds workflows + installs bundles + runs hooks
       |
       v
  [Submit via console or CLI]  ->  Daemon polls, claims, runs
```

---

## 8. Operator Console — How User Mode Operates

### 8.1 What It Is

The operator console is a **Flet-based desktop GUI** application that provides a unified interface for managing workflow runs. It replaces per-workflow batch files with a visual interface. In **User Mode**, the console is the primary way operators interact with the system — they do not need to touch the terminal for daily operations.

### 8.2 Architecture in User Mode

```
+-----------------------------------------------------------------+
|  Operator Console (ukbe-run-agent console)                      |
|                                                                 |
|  +---------------------+    +--------------------------------+  |
|  |  Console Config      |    |  Global Runner Config         |  |
|  |  ~/.ukbe-runner/     |    |  ~/.ukbe-runner/config.json   |  |
|  |  operator-console.json|    |  (backend_url, worker_id,    |  |
|  |  (repos + workflows) |    |   worker_label)               |  |
|  +----------+----------+    +--------------+-----------------+  |
|             |                              |                    |
|             v                              v                    |
|  +-----------------------------------------------------------+ |
|  |  BackendRunService (BackendClient)                        | |
|  |  -> list_active_runs()  -> GET /api/runs                  | |
|  |  -> stop_run()          -> POST /api/runs/{id}/stop       | |
|  |  -> approve_run()       -> POST /api/runs/{id}/approve    | |
|  |  -> get_run_detail()    -> GET /api/runs/{id}             | |
|  |  -> reset_run_step()    -> POST /api/runs/{id}/reset      | |
|  +-----------------------------------------------------------+ |
|                                                                 |
|  +-----------------------------------------------------------+ |
|  |  RunnerActionService (in-process CLI invocation)           | |
|  |  -> submit_job()    -> submit_commands.main()             | |
|  |  -> approve_step()  -> run_agent.main(["run", ...])       | |
|  |  -> override_step() -> run_agent.main(["run", ...])       | |
|  |  -> init_workspace()-> run_agent.main(["init", ...])      | |
|  |                                                           | |
|  |  Executes CLI functions **in-process** (not subprocess)   | |
|  |  with stdout/stderr redirected to capture output.         | |
|  +-----------------------------------------------------------+ |
|                                                                 |
|  +-----------------------------------------------------------+ |
|  |  Workflow.toml Loader (via workflow_packages)              | |
|  |  -> Reads ~/.ukbe-runner/workflows/<name>/workflow.toml  | |
|  |  -> Discovers init_step required_inputs for UI fields    | |
|  +-----------------------------------------------------------+ |
+-----------------------------------------------------------------+
```

### 8.3 Startup Sequence (User Mode)

When the user runs `ukbe-run-agent console`, the following happens:

**Step 1 — Load global runner config**
```python
settings = load_global_settings()  # reads ~/.ukbe-runner/config.json
```
Must contain `backend_url` and `worker_id`, otherwise the console exits with an error.

**Step 2 — Load console config**
```python
console_config = load_console_config()  # reads ~/.ukbe-runner/operator-console.json
```
Must contain a `repos` array with at least one repo entry. Each entry must have a `name`, `path`, and `workflows` array. The `path` is the **filesystem path to the user's project repository** where the workflow will operate.

**Step 3 — Create services**
```python
backend_service = BackendRunService(BackendClient(settings.backend_url), worker_id=settings.worker_id)
runner_service = RunnerActionService(settings)
```
- `BackendRunService` — wraps `BackendClient` for backend API calls
- `RunnerActionService` — wraps CLI entry points for in-process execution

**Step 4 — Launch Flet GUI window**
```python
ft.app(target=app)
```
Opens a 980x760 desktop window with the full UI.

### 8.4 How Each Action Works in User Mode

#### 8.4.1 Submit

1. User selects a repo, workflow, fills in input fields, clicks **Run Action**
2. Console collects input artifact values from the dynamic UI fields
3. For each `*_FILE` key, it resolves the path using `resolve_input_path()`:
   - If it is an SDLC key (e.g. `INIT_FILE`, `REQ_FILE`), it looks in `<repo_path>/docs/repo/agent_runner/sdlc/delivery/<subdir>/`
   - If the value is an absolute path, it uses it as-is
   - Otherwise, it raises an error
4. `RunnerActionService.submit_job()` builds the argument list:
   ```
   ["--workflow-name", "sdlc_10_requirement_v1",
    "--backend-url", "http://...",
    "--worker-id", "my-worker",
    "--worker-label", "live",
    "--input", "INIT_FILE=path/to/init.md"]
   ```
5. `_invoke()` changes the working directory to `repo_path`, calls `submit_commands.main(argv)` **in-process**, captures stdout, and returns the output string
6. Backend receives the submission and queues the run

#### 8.4.2 Approve

1. Console fetches active runs from the backend via `BackendRunService.list_active_runs()`
2. User selects a run, clicks **Approve**, optionally provides feedback
3. Two things happen:
   - **Local approval**: `RunnerActionService.approve_step()` calls `run_agent.main(["run", "--template-group", "...", "--job-id", "...", "--approve-step", "..."])` in-process. This runs the local `ukbe-run-agent run --approve-step` command, which records the approval in the local `job.json` state.
   - **Backend approval**: `BackendRunService.approve_run()` sends `POST /api/runs/{id}/approve` to the backend API to update the workflow step run status.
4. Output from both calls is concatenated and displayed

#### 8.4.3 Reject

1. User selects an active run, provides feedback, clicks **Reject**
2. `BackendRunService.approve_run(reject=True, feedback="...")` sends `POST /api/runs/{id}/approve` with `action: "reject"`
3. No local runner invocation needed — rejection is handled through the backend
4. The backend triggers a refine/replan cycle on the workflow step

#### 8.4.4 Cancel

1. User selects an active run, provides a reason, clicks **Cancel**
2. `BackendRunService.stop_run(reason="...")` sends `POST /api/runs/{id}/stop`
3. Backend marks the run as stopped/cancelled
4. The daemon picks up the stop signal and terminates the child process

#### 8.4.5 Reset

1. User selects an active run, selects a target step from the Reset Target Step dropdown, clicks **Reset**
2. Two things happen:
   - **Local override**: `RunnerActionService.override_step()` calls `run_agent.main(["run", "--template-group", "...", "--job-id", "...", "--override-step", "step_name"])` in-process. This forces the local `job.json` to reset its `current_step` to the specified step.
   - **Backend reset**: `BackendRunService.reset_run_step()` sends `POST /api/runs/{id}/reset` to the backend to update the step run's current step.

### 8.5 Dynamic Input Field Generation

The console dynamically generates input fields based on the selected workflow's `workflow.toml`:

```
1. User selects workflow "SDLC: Requirement Intake"
2. Console resolves workflow path: ~/.ukbe-runner/workflows/sdlc_10_requirement_v1/
3. Console loads workflow.toml via load_workflow_package()
4. Reads bundle.init_step -> "01_requirement_intake"
5. Reads bundle.steps["01_requirement_intake"].required_inputs ->
   ["INIT_FILE", "PROJECT_ANALYSIS"]
6. For each required input:
   - If key ends with "_FILE": creates TextField + Browse button
     - Browse button opens file picker, rooted at SDLC delivery dir
     - e.g. INIT_FILE -> docs/repo/agent_runner/sdlc/delivery/00_initiatives/
   - If key is a scalar: creates plain TextField
7. Input fields are rendered in the dynamic_inputs_container panel
```

### 8.6 Active Runs Auto-Refresh

The console polls the backend every 5 seconds to refresh the Active Runs list:

```python
async def _auto_refresh_loop():
    while auto_refresh_cb.value:
        await asyncio.sleep(5)
        refresh_active_runs()  # calls BackendRunService.list_active_runs()
```

The auto-refresh is toggled via a checkbox. When disabled, the user can manually refresh via the **Refresh Active Runs** button.

### 8.7 In-Process CLI Invocation (Critical Detail)

The console does **not** spawn subprocesses. Instead, it calls the CLI entry points **in-process** with redirected stdout/stderr:

```python
def _invoke(self, *, repo_path, func, argv):
    workdir = Path(repo_path).resolve()
    stdout = io.StringIO()
    stderr = io.StringIO()

    with _pushd(workdir), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        exit_code = func(argv)  # Direct call to run_agent.main() or submit_commands.main()

    # Capture and return output
    return stdout.getvalue().strip()
```

This means:
- The console process IS the engine process — it runs the same Python code
- The engine version resolves from `~/.ukbe-runner/config.json` (same as any other CLI invocation)
- `engine_version: "SNAPSHOT"` -> runs from the live source tree if `repo_root` is configured
- `engine_version: "0.4.0"` -> runs from the versioned install in `~/.ukbe-runner/engine/versions/0.4.0/`
- The current working directory is temporarily changed to `repo_path` for the duration of the call

### 8.8 Prerequisites for User Mode Console

For the console to function in User Mode, these must be in place:

| Prerequisite | Location | Required For |
|---|---|---|
| Global runner config | `~/.ukbe-runner/config.json` | Backend URL + worker ID |
| Console config | `~/.ukbe-runner/operator-console.json` | Repo paths + workflow definitions |
| Workflow packages | `~/.ukbe-runner/workflows/<name>/` | Dynamic input field generation |
| Backend API | Reachable at `backend_url` | Submitting, listing, approving runs |
| flet package | `pip install agent-runner-v2[console]` | GUI rendering |

### 8.9 User Mode Console Workflow

A typical User Mode session:

```
1. ukbe-run-agent console
   -> Opens the Flet desktop window

2. Select repo -> "my-project"
   Workflow dropdown auto-populates from config

3. Select workflow -> "SDLC: Requirement Intake"
   Dynamic input fields appear (INIT_FILE, PROJECT_ANALYSIS)

4. Browse for INIT_FILE -> select requirements.md
   File picker opens at docs/repo/.../00_initiatives/

5. Action: "Submit" -> click "Run Action"
   Console calls submit_commands.main() in-process
   -> Backend queues the run
   -> Daemon picks it up, processes steps

6. Switch to "Active Runs" tab
   Auto-refresh shows runs in progress

7. When a step awaits human approval:
   Select the run -> Action: "Approve" -> click "Run Action"
   Console calls run_agent.main() + backend API
   -> Step approved, workflow continues
```


## 9. Daemon & Worker Mode

### 9.1 Architecture

```
Backend API
    |
    |  (poll for work)
    v
Daemon (persistent process)
    |
    |  (claim step)
    v
Child Process (ukbe-run-agent run)
    |
    |  (execute step, produce result)
    v
Backend API (report result)
```

### 9.2 Daemon Command

```bash
ukbe-run-agent daemon <worker-id> [options]
```

Options:
- `--backend-url` — Backend API URL (default: from config or `http://127.0.0.1:8100`)
- `--worker-label` — Queue label: `live` or `dev` (default: `live`)
- `--poll-seconds` — Polling interval in seconds (default: 5)
- `--once` — Claim and process one step, then exit
- `--engine-root` — Explicit engine version directory

### 9.3 How the Daemon Works

1. **Registration:** The daemon registers itself with the backend as an available worker
2. **Polling:** Every `poll-seconds` seconds, it polls the backend for available work
3. **Claiming:** When work is available, it claims a step run
4. **Spawning:** It spawns a child process: `ukbe-run-agent run --mode daemon --job-no <run_code> --template-group <group> --job <step>`
5. **Monitoring:** The daemon monitors the child process, writes logs, and emits heartbeats
6. **Reporting:** When the child finishes, the daemon reports the result back to the backend

### 9.4 Engine Resolution in Daemon Mode

The daemon resolves which engine version to use for child processes:

```python
def _resolve_engine_pythonpath(cfg, log):
    # 1. Check AGENT_RUNNER_V2_SRC env var
    # 2. Check engine_version in config
    #    - If SNAPSHOT: use repo_root from config
    #    - If versioned: use ~/.ukbe-runner/engine/versions/<version>/
    # 3. Fall back to ambient PYTHONPATH
```

---

## 10. Engine Version Management

### 10.1 Commands

| Command | Purpose |
|---|---|
| `ukbe-run-agent engine install <tag>` | Download and install engine from GitHub releases |
| `ukbe-run-agent engine install <tag> --local` | Install to repo-local `.ukbe-runner/engine/versions/` |
| `ukbe-run-agent engine install <tag> --from-path <dir>` | Copy from a local source directory |
| `ukbe-run-agent engine snapshot` | Snapshot current live source into a SNAPSHOT version |
| `ukbe-run-agent engine use <version>` | Set active version in `~/.ukbe-runner/config.json` |
| `ukbe-run-agent engine list` | List installed versions |
| `ukbe-run-agent engine current` | Show active version |

### 10.2 Version Storage

```
Global:
~/.ukbe-runner/engine/versions/
+-- 0.4.0/
|   +-- agent_runner_v2/   <- importable package
|   +-- version.json
+-- 0.3.0/
    +-- ...

Repo-local:
<repo>/.ukbe-runner/engine/versions/
+-- SNAPSHOT/
    +-- agent_runner_v2/
    +-- version.json
```

### 10.3 Development Mode: SNAPSHOT

When `engine_version` is `"SNAPSHOT"`:
- The system runs from the live source tree
- `repo_root` in config tells the system where the repo lives
- No `engine install` is needed — just run directly

### 10.4 User Mode: Versioned

When `engine_version` is a specific version (e.g., `"0.4.0"`):
- The system runs from `~/.ukbe-runner/engine/versions/0.4.0/`
- The engine is frozen — changes to the repo don't affect running workers
- To upgrade: `engine install <new-version>` then `engine use <new-version>`

---

## 11. Troubleshooting & FAQ

### 11.1 Common Issues

| Symptom | Cause | Solution |
|---|---|---|
| `No workflow packages found` | `init` not run or wrong workflow name | Run `ukbe-run-agent init` |
| `Engine version X not found` | Version not installed | `ukbe-run-agent engine install X` |
| `Backend request failed` | Backend URL incorrect or backend down | Check `~/.ukbe-runner/config.json` `backend_url` |
| `Missing required input artifact` | Seed artifacts not provided | Use `--set KEY=PATH` |
| `Preflight status not approved` | Artifact review status is not APPROVED | Use `--approve-step` or check the artifact's meta.json |
| `Cannot run step: missing required input` | Previous step didn't produce expected artifact | Check job.json for completed steps |
| `Unknown template group` | Workflow package not installed or name wrong | Check `ukbe-run-agent engine list` and `ukbe-run-agent init` |

### 11.2 FAQ

**Q: How do I switch between Development Mode and User Mode?**
A: Change `engine_version` in `~/.ukbe-runner/config.json`:
- `"SNAPSHOT"` for Development Mode (requires `repo_root`)
- `"0.4.0"` (or any version) for User Mode

**Q: How do I test a workflow change without affecting production?**
A: Use Development Mode with `worker_label: "dev"` and `step_spec_source: "global"`. This keeps your changes isolated from the `live` queue.

**Q: What happens if I run `ukbe-run-agent run` without a backend?**
A: The system works in standalone mode. It uses local job state (`~/.ukbe-runner/jobs/`) and doesn't contact the backend. You can approve/reject steps manually via `--approve-step`.

**Q: How do I reset a stuck job?**
A: Use `ukbe-run-agent run --override-step <step> --job-id <job-id>` to force a job to a specific step, or `--reapply-routing` to re-apply routing logic.

**Q: How do I see what is in a job?**
A: Use `ukbe-run-agent run --show-job --job-id <job-id>` to print the full job.json.

**Q: Can I run multiple daemons on the same machine?**
A: Yes, each daemon needs a unique `worker-id`. They can share the same `~/.ukbe-runner/` directory.

**Q: How do I update workflow definitions after they have been installed?**
A: In Dev Mode: `bootstrap-publish` -> `init`. In User Mode: create a new version of the workflow package, run `install`, then `sync-workflow-spec`.

---

## Appendix A: File Reference

| File | Purpose |
|---|---|
| `agent_runner_v2/run_agent.py` | CLI entry point, main orchestration |
| `agent_runner_v2/config_loader.py` | Global config loader |
| `agent_runner_v2/runtime_context.py` | Process-local path context |
| `agent_runner_v2/step_runner.py` | Core step execution logic |
| `agent_runner_v2/step_execution_runtime.py` | Step preparation |
| `agent_runner_v2/execution_core.py` | Execution orchestration |
| `agent_runner_v2/workflow_router.py` | Post-step routing |
| `agent_runner_v2/job_state.py` | Job lifecycle management |
| `agent_runner_v2/bundle_loader.py` | Bootstrap and init |
| `agent_runner_v2/daemon.py` | Worker daemon |
| `agent_runner_v2/engine_commands.py` | Engine version management |
| `agent_runner_v2/coder_adapters.py` | LLM coder invocation |
| `agent_runner_v2/backend_client.py` | Backend API client |
| `agent_runner_v2/workflow_packages/loader.py` | workflow.toml parser |
| `agent_runner_v2/workflow_packages/base.py` | WorkflowBundle dataclass |
| `agent_runner_v2/workflow_packages/extensions_base.py` | WorkflowExtensions base class |
| `agent_runner_v2/workflow_packages/hooks.py` | Lifecycle hook dispatcher |
| `agent_runner_v2/workflow_packages/registry.py` | Workflow package registry |
| `agent_runner_v2/operator_console/app.py` | Flet GUI application |
| `agent_runner_v2/operator_console/config.py` | Console config loader |
| `pyproject.toml` | Package config, entry point definition |
| `operator-console.example.json` | Example console configuration |

## Appendix B: Environment Variables

| Variable | Purpose | Default |
|---|---|---|
| `AGENT_RUNNER_BACKEND_URL` | Backend API URL | From config |
| `AGENT_RUNNER_WORKER_ID` | Worker identifier | From config |
| `AGENT_RUNNER_V2_SRC` | Engine source override (dev mode) | From config |
| `AGENT_RUNNER_CONSOLE_CONFIG` | Console config path override | `~/.ukbe-runner/operator-console.json` |
| `AGENT_RUNNER_WORKFLOW_RUN_ID` | Backend workflow run ID (daemon mode) | -- |
| `AGENT_RUNNER_WORKFLOW_STEP_RUN_ID` | Backend step run ID (daemon mode) | -- |
| `WORKER_LABEL` | Worker queue label | `live` |
| `STEP_SPEC_SOURCE` | Step spec source | `backend` |
