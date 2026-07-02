---
title: "System File Structure: agent-runner-v2"
template_id: "SYS-03-SF"
status: "active"
managed_by: workflow-generated
created: "2026-07-02T20:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260702-005"
---

# System File Structure: agent-runner-v2

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

## 1. Repository Structure

```
D:\MyProjectSpace\01_Workflows\agent-runner-v2\
├── agent_runner_v2/                    # Main Python package
│   ├── __init__.py
│   ├── run_agent.py                    # CLI entry (2,141 lines)
│   ├── step_runner.py                  # Step execution (2,000 lines)
│   ├── workflow_router.py              # Post-step routing (774 lines)
│   ├── job_state.py                    # Job lifecycle (1,781 lines)
│   ├── coder_adapters.py               # LLM invocation (1,013 lines)
│   ├── daemon.py                       # Worker supervisor (420 lines)
│   ├── runtime_context.py              # Path/context (281 lines)
│   ├── bundle_loader.py                # Bundle loading (188 lines)
│   ├── backend_client.py               # Backend API (~200 lines)
│   ├── actions/                        # Deterministic actions
│   │   ├── __init__.py
│   │   ├── scan_repo_codebase.py
│   │   ├── sync_codebase_docs.py
│   │   ├── sync_system_docs.py
│   │   ├── validate_codebase_docs.py
│   │   ├── validate_delivery_docs.py
│   │   ├── validate_system_docs.py
│   │   ├── prepare_delivery_scaffold.py
│   │   ├── finalize_bootstrap.py
│   │   ├── promote_artifact.py
│   │   ├── promote_init.py
│   │   ├── copy_artifact.py
│   │   ├── submit_comfyui.py
│   │   ├── execute_t2i.py
│   │   ├── execute_i2v.py
│   │   ├── execute_voiceover.py
│   │   └── assemble_video.py
│   ├── bootstrap/                      # Bootstrap workflow assets
│   │   └── workflows/
│   │       └── default/
│   │           ├── template_groups.py  # Workflow definitions
│   │           ├── job_schema.json
│   │           ├── llm_response_schema.json
│   │           ├── model_mapping.json
│   │           ├── usage_schema.json
│   │           └── prompts/            # 100+ prompt templates
│   ├── tools/                          # Utility scripts
│   │   └── agent_tools.py
│   └── [schema, state, commands]       # Supporting modules
├── docs/                               # Documentation
│   ├── system/                         # System documentation
│   │   ├── 00_governance/              # Governance docs (this file)
│   │   └── [other folders]
│   └── codebase/                       # Codebase documentation
│       ├── 01_inventory/
│       ├── 02_modules/
│       ├── 03_components/
│       └── 04_changes/
├── scripts/                            # Shell scripts
│   ├── ukbe-runner.sh
│   ├── ukbe-daemon-wsl.sh
│   ├── approve-run.sh
│   └── examples/
├── tests/                              # Test suite
│   ├── conftest.py
│   └── test_*.py                       # 10 test modules
├── archive/                            # Legacy scripts
│   └── batch/
├── pyproject.toml                      # Package definition
├── README.md                           # Project README
├── QWEN.md                             # Qwen Code context
├── HOW_TO_GUIDE.md                     # User guide
├── WINDOWS_COMPATIBILITY.md            # Windows notes
├── .env.example                        # Environment template
├── .gitignore
└── [batch files]                       # Windows launchers
```

## 2. Directory Purposes

### 2.1 agent_runner_v2/

The main Python package containing all runtime code.

| Subdirectory | Purpose | File Count |
|--------------|---------|------------|
| `actions/` | Deterministic runner actions | 16 Python files |
| `bootstrap/` | Workflow bundle seed files | 4 JSON + 1 Python + prompts |
| `tools/` | Utility scripts for progress tracking | 1 Python file |

### 2.2 docs/

Comprehensive documentation organized by audience.

| Subdirectory | Purpose | Audience |
|--------------|---------|----------|
| `system/00_governance/` | Governance and master docs | Maintainers |
| `system/` (other) | System overview, architecture | Developers |
| `codebase/01_inventory/` | Codebase inventory | Developers |
| `codebase/02_modules/` | Module documentation | Developers |
| `codebase/03_components/` | Component documentation | Developers |
| `codebase/04_changes/` | Change impact docs | Developers |

### 2.3 scripts/

Executable scripts for Unix/WSL environments.

| Script | Purpose |
|--------|---------|
| `ukbe-runner.sh` | Main runner script |
| `ukbe-daemon-wsl.sh` | WSL daemon launcher |
| `approve-run.sh` | Step approval helper |
| `examples/` | Example submission scripts |

### 2.4 tests/

Pytest test suite.

| Test Module | Coverage Area |
|-------------|---------------|
| `test_backend_worker_mode.py` | Backend integration |
| `test_bundle_loader.py` | Bundle loading |
| `test_codebase_docs.py` | Codebase documentation |
| `test_daemon.py` | Daemon supervisor |
| `test_documentation_governance.py` | Doc governance |
| `test_run_agent_status.py` | CLI status handling |
| `test_runtime_context_paths.py` | Path resolution |
| `test_tool_instruction_block.py` | Tool instructions |
| `test_ukbe_runner_wrapper.py` | Wrapper functionality |

## 3. Runtime File Structure

After `ukbe-run-agent init`, the runner home contains:

```
%USERPROFILE%\.ukbe-runner\
├── config.json                       # Global configuration
│
├── jobs/                             # Job state directory
│   └── <workflow-group>/             # e.g., "default", "delivery"
│       └── <job-id>/                 # UUID-based job ID
│           ├── job.json              # Job state (schema v6)
│           ├── <step-01>/            # Step directory
│           │   ├── meta.json         # Step result sidecar
│           │   ├── prompt.txt        # Rendered prompt
│           │   └── debug/            # Debug outputs
│           ├── <step-02>/
│           └── ...
│
├── workflows/                        # Runtime workflow bundles
│   └── default/                      # Active workflow
│       ├── template_groups.py        # Workflow definitions
│       ├── job_schema.json           # Validation schema
│       ├── llm_response_schema.json  # LLM response schema
│       ├── model_mapping.json        # Coder aliases
│       └── prompts/                  # Prompt templates
│           ├── 00_master_docs_bootstrap_v1/
│           ├── 10_execution_scaffold_v1/
│           ├── 20_initiative_intake_v1/
│           ├── 21_bug_fix_intake_v1/
│           ├── 30_delivery_planning_v1/
│           ├── 31_task_execution_v1/
│           ├── 40_documentation_sync_v1/
│           ├── image_csv_gen_v1/
│           ├── image_csv_gen_v2/
│           ├── tiktok_video_pipeline_v1/
│           └── videoxpress_gen_v1/
│
├── bundles/                          # Bundle taxonomy (future)
│   ├── core/
│   ├── domains/
│   └── workflows/
│
└── logs/                             # Execution logs
    └── ukbe-runner-<date>.log
```

## 4. Key File Relationships

### 4.1 Bootstrap to Runtime Flow

```
Package Bootstrap                    Runtime Home
agent_runner_v2/                     %USERPROFILE%\.ukbe-runner\
bootstrap/                               │
workflows/                               │
    default/                             │
        ├── template_groups.py ──────────► workflows/
        ├── *.json ───────────────────────► default/
        └── prompts/ ───────────────────► *.json
            └── **/*.txt ────────────────► prompts/
                                              └── **/
```

Triggered by: `ukbe-run-agent init`

### 4.2 Step Execution Flow

```
Workflow Definition                    Job State                      Step Result
(template_groups.py)                                                    (meta.json)
       │                                     │                              │
       │  1. Load workflow                   │                              │
       ▼                                     │                              │
┌──────────────┐                            │                              │
│  workflow    │─────────────────────────────►                              │
│   module     │                            │                              │
└──────────────┘                            │                              │
       │                                     │                              │
       │  2. Create job                      │                              │
       ▼                                     ▼                              │
┌──────────────┐                      ┌───────────┐                         │
│   run_       │─────────────────────►│  job.json │                         │
│  agent.py    │                      │  (CREATED)│                         │
└──────────────┘                      └───────────┘                         │
       │                                     │                              │
       │  3. Execute step                    │                              │
       ▼                                     ▼                              ▼
┌──────────────┐                      ┌───────────┐                  ┌───────────┐
│  step_       │─────────────────────►│  <step>/  │─────────────────►│  meta.json│
│ runner.py    │  4. Update state     │           │  5. Validate     │ (APPROVED)│
└──────────────│◄─────────────────────│           │◄─────────────────└───────────┘
       │       6. Route               │           │
       ▼                              └───────────┘
┌──────────────┐                            │
│  workflow_   │────────────────────────────►│
│  router.py   │  7. Next step / done       │
└──────────────┘                            │
```

### 4.3 Documentation Generation Flow

```
Codebase Scan                           Module Docs                     Component Docs
(agent_runner_v2/)                      (02_modules/)                   (03_components/)
       │                                       │                                │
       ▼                                       │                                │
┌──────────────┐                               │                                │
│ actions/     │───────────────────────────────►                               │
│ scan_repo_   │  Generate module docs         │                                │
│ codebase.py  │                               │                                │
└──────────────┘                               ▼                                │
                                         ┌───────────┐                         │
                                         │ agent-    │                         │
                                         │ runner-*  │────────────────────────►│
                                         │ .md       │  Aggregate into         │
                                         └───────────┘  component docs         ▼
                                                                              ┌───────────┐
                                                                              │ actions-  │
                                                                              │ package   │
                                                                              │ .md       │
                                                                              └───────────┘
```

## 5. File Size and Complexity

### 5.1 Largest Files

| File | Lines | Complexity | Purpose |
|------|-------|------------|---------|
| `run_agent.py` | 2,141 | High | CLI entry, orchestration |
| `step_runner.py` | 2,000 | High | Step execution contract |
| `job_state.py` | 1,781 | High | Job state machine |
| `coder_adapters.py` | 1,013 | Medium | LLM invocation |
| `workflow_router.py` | 774 | Medium | Routing logic |
| `daemon.py` | 420 | Medium | Worker supervisor |

### 5.2 Module Organization

```
Core Modules (>1000 lines):
├── run_agent.py
├── step_runner.py
└── job_state.py

Coder/Backend (~1000 lines):
├── coder_adapters.py

Routing/Support (300-800 lines):
├── workflow_router.py
├── daemon.py
├── runtime_context.py
├── backend_client.py
└── bundle_loader.py

Actions (~100-200 lines each):
├── actions/*.py (16 files)

Supporting (<300 lines each):
├── *.py (schema, state, commands, etc.)
```

## 6. Naming Conventions

### 6.1 Python Files

| Pattern | Example | Purpose |
|---------|---------|---------|
| `run_*.py` | `run_agent.py` | Entry points |
| `*_runner.py` | `step_runner.py` | Execution engines |
| `*_router.py` | `workflow_router.py` | Routing logic |
| `*_state.py` | `job_state.py` | State management |
| `*_adapters.py` | `coder_adapters.py` | External interfaces |
| `*_client.py` | `backend_client.py` | API clients |
| `*_commands.py` | `approve_commands.py` | CLI commands |
| `action_*.py` | `action_result.py` | Action schemas |
| `*_tools.py` | `agent_tools.py` | Utilities |

### 6.2 Documentation Files

| Pattern | Example | Purpose |
|---------|---------|---------|
| `*.md` | `README.md` | Markdown docs |
| `*-change-log.md` | `00DOC-*-change-log.md` | Change logs |
| `*-snapshot.json` | `00DOC-*-snapshot.json` | Snapshots |

### 6.3 Step Directories

| Pattern | Example | Purpose |
|---------|---------|---------|
| `<step_name>/` | `02_generate_project_analysis/` | Step output |
| `meta.json` | `meta.json` | Sidecar result |

---

*Generated by workflow `00_master_docs_bootstrap_v1` step `04_generate_architecture_docs`*
