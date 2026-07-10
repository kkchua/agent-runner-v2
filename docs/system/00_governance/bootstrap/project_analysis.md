---
template_id: "SYS-00-PA"
title: "Project Analysis - agent-runner-v2"
status: "active"
change_id: "00DOC-GEN-20260710-004"
workflow: "00_master_docs_bootstrap_v1"
step: "02_generate_project_analysis"
managed_by: workflow-generated
generated: "2026-07-10T09:41:02+08:00"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `02_generate_project_analysis`
> This file is workflow-generated and protected from manual edits.

# Project Analysis: agent-runner-v2

## Repo Overview

`agent-runner-v2` is a standalone Python LLM workflow orchestration engine extracted from UKBE. It runs structured multi-step workflows across Claude, Codex, Qwen, and aliased models, with review loops, retries, approval gates, and deterministic runner actions.

The package provides a CLI entry point (`ukbe-run-agent`) supporting three primary usage modes:
- **Manual workflow execution** with `ukbe-run-agent run`
- **Backend-connected single-step execution** with `ukbe-run-agent worker`, `poll`, and `execute-step`
- **Workstation supervision** with `ukbe-run-agent daemon`

The backend is the source of truth for runs, step runs, artifacts, events, and approvals. The runner is responsible for prompt rendering, coder/action execution, output validation, and step result submission.

## Codebase Structure

### Package Layout

```
agent_runner_v2/              # Main Python package (47 modules)
├── __init__.py
├── run_agent.py              # CLI entry point (2,308 lines)
├── step_runner.py            # Core step execution contract (2,647 lines)
├── workflow_router.py        # Post-step routing logic
├── job_state.py              # Job.json lifecycle management
├── coder_adapters.py         # Claude/Codex/Qwen invocation
├── template_groups.py        # Workflow definitions (2,453 lines)
├── constants.py              # Centralized path constants (1,333 lines)
├── bundle_loader.py          # Bootstrap seeding and bundle loading
├── runtime_context.py        # Active workflow/runtime path context
├── actions/                  # 29 deterministic runner actions
│   ├── finalize_bootstrap.py
│   ├── prepare_delivery_scaffold.py
│   ├── sync_codebase_docs.py
│   ├── validate_*.py         # Multiple validation actions
│   └── ...
├── bootstrap/                # Packaged bootstrap source
│   └── workflows/default/    # Template groups and prompt templates
├── config/                   # Configuration modules
└── tools/                    # Utility tools
```

### Documentation Structure

```
docs/
├── delivery/                 # Per-repo delivery artifacts
│   ├── 01_initiatives/
│   ├── 02_plans/
│   ├── 03_task_graphs/
│   ├── 04_tasks/
│   ├── 05_implementations/
│   ├── 06_reviews/
│   └── 08_agents/
├── codebase/                 # Codebase documentation
│   ├── 01_inventory/         # Codebase inventory (auto-generated)
│   ├── 02_modules/           # Module documentation
│   ├── 03_components/        # Component documentation
│   └── 04_changes/           # Change impact documents
└── system/                   # System documentation
    └── 00_governance/bootstrap/  # Master system docs
```

### Tests Structure

```
tests/
├── unit/                     # Isolated logic tests
├── integration/              # Real file/external system tests
└── conftest.py               # Shared fixtures
```

### Workflow Launcher Entrypoints

34 batch files provide workflow launcher entrypoints:
- `run-00_master_docs_bootstrap_v1.bat`
- `run-10_execution_scaffold_v1.bat`
- `run-20_initiative_intake_v1.bat` through `run-21_bug_fix_intake_v1.bat`
- `run-30_delivery_planning_v1.bat` through `run-31_task_execution_v1.bat`
- `run-40_documentation_sync_v1.bat` through `run-55_user_docs_v1.bat`
- Test runners: `run-tests.bat`, `run-integration-tests.bat`, `run-all-tests.bat`

## Workflow and Runtime Model

### Core Execution Model

Each workflow step follows this sequence:

1. **Load workflow bundle** - Runtime loads from `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\`
2. **Render prompt** - Template substitution from `template_groups.py` definitions
3. **Invoke coder/action** - Either LLM coder (Claude/Codex/Qwen) or deterministic runner action
4. **Read meta.json sidecar** - The ONLY structured result channel (v2 contract)
5. **Validate artifacts** - Check existence and conformance to produces list
6. **Route to next step** - Based on APPROVE/REJECT/failure status

### Key v2 Contract Rules

- `meta.json` sidecar is the **only** communication channel
- No markdown write-backs by the runner
- No silent recovery paths
- Hard failures route explicitly through `route_after_failure()`
- Declarative document protection via `produces` lists

### Bootstrap vs Runtime Distinction

There are two distinct sources of truth:

1. **Packaged bootstrap source** (in repo)
   - `agent_runner_v2/bootstrap/workflows/default/`
   - Seeds the global runner home during `ukbe-run-agent init`

2. **Runtime workflow bundle** (during execution)
   - `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\`
   - Runtime loads from here, not directly from repo

### Workflow Families

The repository defines 21 workflow families with 290+ steps:

| Workflow | Steps | Purpose |
|----------|-------|---------|
| `00_master_docs_bootstrap_v1` | 13 | Bootstrap system documentation |
| `10_execution_scaffold_v1` | 13 | Scaffold delivery governance |
| `20_initiative_intake_v1` | 5 | Initiative capture and refinement |
| `21_bug_fix_intake_v1` | 7 | Bug triage and fix workflow |
| `30_delivery_planning_v1` | 10 | Plan and task graph generation |
| `31_task_execution_v1` | 12 | Implementation and validation |
| `40_documentation_sync_v1` | 5 | Doc reconciliation and validation |
| `50_architecture_site_v1` | 2 | HTML architecture site generation |
| `41_audience_doc_v1` | 4 | Audience-specific documentation |
| `51-55_*_docs_v1` | 1-4 | Stakeholder/developer/operator/tester/user docs |

## Operational Risks

### Runtime Sync Risk
Changes to bootstrap workflow files (`template_groups.py`, `constants.py`) must be synced to `%USERPROFILE%\.ukbe-runner\workflows\default\` before they take effect. Failure to sync causes placeholder substitution failures.

### Windows Pathlib Bug
Previous issues with `Path.relative_to()` on Windows have been fixed, but path handling remains a cross-platform concern.

### Test Permission Issues
pytest's `tmp_path` fixture creates directories that may have permission issues on Windows, requiring careful test design.

### Bootstrap-to-Runtime Bundle Drift
The repo bootstrap files only seed runtime bundles. Active development requires explicit sync commands to propagate changes.

### Sidecar Contract Enforcement
Strict v2 sidecar schema required; any deviation causes hard failures. Automated injection of sidecar instructions helps but doesn't eliminate risk.

### Documentation Protection Model
Declarative `produces` lists control write access. Misconfiguration can block legitimate artifact writes or allow unauthorized modifications.

## Architectural Observations

### Centralized Constants Architecture
`constants.py` (1,333 lines) serves as the single source of truth for:
- Artifact key constants (80+ keys)
- Folder key constants
- Path generation functions
- Section requirements dictionaries
- Reference file mappings

This eliminates hardcoded path strings throughout the codebase.

### Layered Constant System
```
FOLDER_KEY_*     → Base directory constants
ARTIFACT_KEY_*   → Artifact identifiers
ARTIFACT_PATH_*  → Pre-computed artifact paths
REFERENCE_FILES  → Complete artifact path dictionary
```

### Step Runner Contract
The `run_step()` function in `step_runner.py` enforces strict separation:
- Coder invocation → meta.json validation → artifact validation
- No fallback recovery functions
- Raises exceptions on failure for explicit routing

### Workflow Router
`route_after_step()` and `route_after_failure()` provide explicit routing:
- APPROVE → next step
- REJECT → refine/replan/human intervention
- Failure → failure handling with retry limits

### Review/Refine Loop Pattern
Common across workflows:
1. Generate artifact
2. Review step produces REVIEW_FILE_SUGGESTED
3. If rejected → refine step with `edit_mode: in_place`
4. Loop returns to review step
5. Max iterations enforced before human intervention

### Action vs Coder Steps
- **Coder steps**: Invoke LLM, expect meta.json sidecar
- **Action steps**: Deterministic Python functions in `actions/` package

## Architecture Posture

| Field | Value |
|-------|-------|
| `current_profile` | `provisional` |
| `target_profile` | `explicit` (delivery scaffold governance model) |
| `migration_mode` | `bootstrap-in-progress` |
| `repo_state` | `provisional` |
| `evidence_sources` | Codebase inventory scan, template_groups.py analysis, constants.py structure, QWEN.md context |

### Posture Assessment

The repository does not declare a clear architecture standard document, recording the posture as **provisional**. The codebase demonstrates explicit architecture through:

1. **Strong module separation**: Core (run_agent, step_runner), state (job_state, runtime_context), adapters (coder_adapters), actions (29 action modules)

2. **Centralized constants**: Single source of truth pattern with zero hardcoded path strings

3. **Contract-based step execution**: Strict v2 sidecar contract with validation layers

4. **Bootstrap/runtime separation**: Clear distinction between packaged source and runtime bundles

The intended target standard is the **delivery scaffold governance model** defined in the workflow families, with SOPs, templates, and agent contracts governing documentation lifecycle.

## Unresolved Documentation Gaps

The following gaps should be addressed by subsequent bootstrap steps:

1. **SYSTEM_OVERVIEW.md** - Comprehensive system overview document
2. **BUSINESS_CAPABILITIES.md** - Business capability mapping
3. **FUNCTIONAL_SPEC.md** - Detailed functional specification
4. **NON_FUNCTIONAL_REQUIREMENTS.md** - NFR documentation
5. **SYSTEM_CONTEXT.md** - System context and external interfaces
6. **COMPONENT_ARCHITECTURE.md** - Component-level architecture documentation
7. **DECISION_LOG.md** - Architecture decision records
8. **SYSTEM_FILE_STRUCTURE.md** - File organization rationale
9. **DEVELOPER_GUIDE.md** - Developer onboarding guide
10. **RUNBOOK.md** - Operational runbook
11. **INTEGRATION_MAP.md** - Integration points and contracts
12. **FAILURE_MODES.md** - Failure mode analysis
13. **ARCHITECTURE_FLOW.md** - Architecture flow documentation
14. **EXISTING_REPO_WORKFLOW_SOP.md** - Workflow SOP for existing repos
15. **Bundle taxonomy and migration plan** - Bundle structure and migration guidance

## Evidence Sources

This analysis was derived from:

- `docs/codebase/01_inventory/codebase_inventory.md` (395 lines, generated 2026-07-10)
- `docs/codebase/04_changes/00DOC-GEN-20260710-004-bootstrap.md` (577 lines)
- `docs/codebase/03_components/workflow-families.md` (component documentation)
- `README.md` (repository overview)
- `QWEN.md` (project context)
- `pyproject.toml` (build configuration)
- `agent_runner_v2/run_agent.py` (CLI entry point)
- `agent_runner_v2/step_runner.py` (step execution contract)
- `agent_runner_v2/template_groups.py` (workflow definitions)
- `agent_runner_v2/constants.py` (centralized constants)

---

*Generated by workflow `00_master_docs_bootstrap_v1` step `02_generate_project_analysis` on 2026-07-10T09:41:02+08:00*
