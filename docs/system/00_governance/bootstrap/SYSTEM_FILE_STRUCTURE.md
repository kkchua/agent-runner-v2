---
template_id: "SYS-03-SFS"
title: "System File Structure - agent-runner-v2"
status: "active"
change_id: "00DOC-GEN-20260710-004"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
managed_by: workflow-generated
generated: "2026-07-10T09:52:38+08:00"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# System File Structure: agent-runner-v2

## Repository Structure

```
agent-runner-v2/
├── agent_runner_v2/              # Main Python package (47 modules)
│   ├── __init__.py
│   ├── run_agent.py              # CLI entry point (2,308 lines)
│   ├── step_runner.py            # Core step execution (2,647 lines)
│   ├── workflow_router.py        # Post-step routing logic (787 lines)
│   ├── job_state.py              # Job.json lifecycle (1,806 lines)
│   ├── coder_adapters.py         # LLM invocation adapters
│   ├── template_groups.py        # Workflow definitions (2,453 lines)
│   ├── constants.py              # Centralized path constants (1,333 lines)
│   ├── bundle_loader.py          # Bootstrap seeding and bundle loading
│   ├── runtime_context.py        # Active workflow/runtime path context
│   ├── backend_client.py         # Backend API client
│   ├── daemon.py                 # Background job processor
│   ├── notifications.py          # Notification delivery
│   ├── notification_manager.py   # Notification orchestration
│   ├── artifact_paths.py         # Artifact path computation
│   ├── doc_paths.py              # Documentation path helpers
│   ├── exceptions.py             # Custom exceptions
│   ├── execution_request.py      # Execution request schema
│   ├── execution_result.py       # Execution result schema
│   ├── model_config.py           # Model resolution
│   ├── runner_logger.py          # Logging utilities
│   ├── runner_actions.py         # Action registry
│   ├── workflow_specs.py         # Workflow specifications
│   ├── workflow_spec_commands.py # Workflow CLI commands
│   ├── approve_commands.py       # Approval CLI commands
│   ├── submit_commands.py        # Submission CLI commands
│   ├── engine_commands.py        # Engine CLI commands
│   ├── submitter.py              # Submission handling
│   ├── documentation_guardrails.py # Document protection
│   ├── codebase_docs.py            # Codebase documentation
│   ├── system_docs.py              # System documentation
│   ├── cleanup_generated_docs.py   # Doc cleanup utility
│   ├── architecture_site.py        # Site generation
│   ├── site_styles.py              # Site styling
│   ├── bundle_taxonomy.py          # Bundle taxonomy
│   ├── config/                     # Configuration modules
│   │   ├── __init__.py
│   │   └── section_requirements.py
│   ├── tools/                      # Utility tools
│   │   └── agent_tools.py
│   ├── actions/                    # 29 deterministic runner actions
│   │   ├── __init__.py
│   │   ├── archive_previous_version.py
│   │   ├── assemble_video.py
│   │   ├── copy_artifact.py
│   │   ├── documentation_validation_core.py
│   │   ├── execute_i2v.py
│   │   ├── execute_t2i.py
│   │   ├── execute_voiceover.py
│   │   ├── finalize_bootstrap.py
│   │   ├── generate_site.py
│   │   ├── generate_site_pdf.py
│   │   ├── prepare_delivery_scaffold.py
│   │   ├── promote_artifact.py
│   │   ├── promote_init.py
│   │   ├── publish_architecture_site.py
│   │   ├── scan_repo_codebase.py
│   │   ├── submit_comfyui.py
│   │   ├── sync_codebase_docs.py
│   │   ├── sync_system_docs.py
│   │   ├── validate_architecture_site.py
│   │   ├── validate_codebase_docs.py
│   │   ├── validate_delivery_docs.py
│   │   ├── validate_developer_site.py
│   │   ├── validate_operator_site.py
│   │   ├── validate_stakeholder_site.py
│   │   ├── validate_system_docs.py
│   │   ├── validate_tester_site.py
│   │   └── validate_user_site.py
│   ├── bootstrap/                  # Packaged bootstrap source
│   │   ├── bundles/                  # Bundle templates
│   │   ├── themes/                   # Site themes
│   │   └── workflows/
│   │       └── default/
│   │           ├── template_groups.py    # Workflow definitions
│   │           ├── constants.py          # Path constants
│   │           ├── job_schema.json       # Job JSON schema
│   │           ├── llm_response_schema.json # LLM response schema
│   │           ├── model_mapping.json    # Model aliases
│   │           └── prompts/              # 290+ prompt templates
│   │               ├── 00_master_docs_bootstrap_v1/
│   │               ├── 10_execution_scaffold_v1/
│   │               ├── 20_initiative_intake_v1/
│   │               ├── 21_bug_fix_intake_v1/
│   │               ├── 30_delivery_planning_v1/
│   │               ├── 31_task_execution_v1/
│   │               ├── 40_documentation_sync_v1/
│   │               ├── 41_audience_doc_v1/
│   │               ├── 50_architecture_site_v1/
│   │               ├── 51_stakeholder_docs_v1/
│   │               ├── 52_developer_docs_v1/
│   │               ├── 53_operator_docs_v1/
│   │               ├── 54_tester_docs_v1/
│   │               ├── 55_user_docs_v1/
│   │               ├── image_csv_gen_v2/
│   │               ├── tiktok_video_pipeline_v1/
│   │               └── videoxpress_gen_v1/
│   └── templates/                  # Jinja2 templates
│
├── docs/                         # Documentation
│   ├── delivery/                 # Per-repo delivery artifacts
│   │   ├── 01_initiatives/
│   │   ├── 02_plans/
│   │   ├── 03_task_graphs/
│   │   ├── 04_tasks/
│   │   ├── 05_implementations/
│   │   ├── 06_reviews/
│   │   └── 08_agents/
│   ├── codebase/                 # Codebase documentation
│   │   ├── 01_inventory/         # Codebase inventory (auto-generated)
│   │   ├── 02_modules/           # Module documentation
│   │   ├── 03_components/        # Component documentation
│   │   └── 04_changes/           # Change impact documents
│   └── system/                   # System documentation
│       └── 00_governance/
│           └── bootstrap/        # Master system docs
│
├── tests/                        # Test suite
│   ├── unit/                     # Isolated logic tests (45 tests)
│   ├── integration/              # Real file/external system tests
│   └── conftest.py               # Shared fixtures
│
├── scripts/                      # Utility scripts
│   └── workflow_scaffold/        # Scaffold scripts
│
├── run-*.bat                     # 26 workflow launcher batch files
├── pyproject.toml                # Build configuration
├── requirements.txt              # Dependencies
├── README.md                     # Repository overview
├── QWEN.md                       # Project context
├── CLAUDE.md                     # Claude-specific context
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
└── MANIFEST.in                   # Package manifest
```

## Top-Level Directories

### agent_runner_v2/

**Purpose**: Main Python package containing all runtime code.

**Why this structure**:
- Clear package boundary for imports
- Mirrors runtime module structure
- Enables `pip install` distribution
- Separates code from configuration and docs

**Key files**:
- `run_agent.py` - CLI entry point
- `step_runner.py` - Core execution engine
- `constants.py` - Single source of truth for paths

### docs/

**Purpose**: All documentation artifacts.

**Three subdirectories**:

| Directory | Purpose | Generated |
|-----------|---------|-----------|
| `delivery/` | Initiative artifacts (plans, tasks, reviews) | Workflow-generated |
| `codebase/` | Repository documentation | Auto-generated + manual |
| `system/` | Master system documentation | Workflow-generated |

**Why three doc types**:
- **Delivery**: Tracks work in progress (ephemeral)
- **Codebase**: Describes code (regenerated on changes)
- **System**: Describes architecture (versioned, reviewed)

### tests/

**Purpose**: Test suite with clear separation.

**Structure**:
- `unit/` - Pure logic tests, no file I/O (45 tests, 100% pass)
- `integration/` - Tests with real files, external systems

**Why split**: Unit tests must run fast and reliably; integration tests verify real behavior.

### agent_runner_v2/bootstrap/

**Purpose**: Packaged bootstrap source that seeds runtime.

**Why separate**: Runtime loads from `%USERPROFILE%\.ukbe-runner`, not directly from repo. Bootstrap seeds the initial runtime state.

**Sync requirement**: Changes to bootstrap files require explicit sync to runtime.

## File Organization Rationale

### Why constants.py is Centralized

All documentation paths use constants from `constants.py`:

```python
# Before (scattered):
path = "docs/system/00_governance/bootstrap/PROJECT_ANALYSIS.md"

# After (centralized):
from agent_runner_v2.constants import artifact_path, ARTIFACT_KEY_PROJECT_ANALYSIS
path = artifact_path(ARTIFACT_KEY_PROJECT_ANALYSIS, FOLDER_KEY_SYSTEM_BOOTSTRAP)
```

**Benefits**:
- Single source of truth
- No case mismatches
- Easy path refactoring
- Type safety

### Why Runtime Context Exists

`runtime_context.py` provides process-local context:

```python
CTX = RuntimeContext(
    workspace_root=Path.cwd().resolve(),
    runner_home=GLOBAL_RUNNER_HOME,
    workflow_name="default",
    workflow_module=None,
    delivery_root=None,
)
```

**Benefits**:
- Thread-safe context storage
- Lazy path resolution
- Testable isolation

### Why Batch Files for Workflows

26 batch files provide simple entry points:

```batch
run-00_master_docs_bootstrap_v1.bat
run-10_execution_scaffold_v1.bat
run-20_initiative_intake_v1.bat
...
```

**Benefits**:
- Simple double-click execution
- Consistent activation: `.venv\Scripts\activate`
- Clear workflow discovery

### Why Meta.json Sidecars

Every step produces a sidecar file:

```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED",
    "remark": "Task completed",
    "artifacts": {...},
    "recorded_at": "2026-07-10T09:52:38+08:00"
  }
}
```

**Benefits**:
- Structured communication
- Versioned schema
- Validatable
- No stdout parsing

## Documentation Locations

### Workflow-Generated Documents

| Document | Location | Owner |
|----------|----------|-------|
| PROJECT_ANALYSIS.md | `docs/system/00_governance/bootstrap/` | 00_master_docs_bootstrap_v1 |
| SYSTEM_OVERVIEW.md | `docs/system/00_governance/bootstrap/` | 00_master_docs_bootstrap_v1 |
| COMPONENT_ARCHITECTURE.md | `docs/system/00_governance/bootstrap/` | 00_master_docs_bootstrap_v1 |
| codebase_inventory.md | `docs/codebase/01_inventory/` | 40_documentation_sync_v1 |
| Delivery artifacts | `docs/delivery/*/` | Various workflows |

### Protected Documents

Documents with `managed_by: workflow-generated` in frontmatter are protected from manual edits. Changes must be made via workflow prompts.

## Configuration Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Package metadata, dependencies, pytest config |
| `requirements.txt` | Runtime dependencies |
| `.env.example` | Environment variable template |
| `.env` | Local credentials (git-ignored) |

## Runtime Files

| Location | Purpose |
|----------|---------|
| `%USERPROFILE%\.ukbe-runner\config.json` | Runner configuration |
| `%USERPROFILE%\.ukbe-runner\jobs\` | Job state persistence |
| `%USERPROFILE%\.ukbe-runner\workflows\` | Runtime workflow bundles |
| `%USERPROFILE%\.ukbe-runner\logs\` | Execution logs |

## Version Control Strategy

| What | Where | Git |
|------|-------|-----|
| Source code | `agent_runner_v2/` | Tracked |
| System docs | `docs/system/` | Tracked |
| Codebase docs | `docs/codebase/` | Tracked |
| Delivery docs | `docs/delivery/` | Tracked |
| Job state | `%USERPROFILE%\.ukbe-runner\jobs\` | Ignored |
| Runtime bundles | `%USERPROFILE%\.ukbe-runner\workflows\` | Ignored |
| Logs | `%USERPROFILE%\.ukbe-runner\logs\` | Ignored |

---

*Generated by workflow `00_master_docs_bootstrap_v1` step `04_generate_architecture_docs` on 2026-07-10T09:52:38+08:00*
