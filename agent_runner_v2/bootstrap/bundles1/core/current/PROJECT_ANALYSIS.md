---
template_id: "SYS-00-PA"
title: "Project Analysis - agent-runner-v2"
status: "active"
generated: "2026-07-09T10:30:00+08:00"
workflow: "10_execution_scaffold_v1"
step: "01_project_analysis"
change_id: "10SCAFFOLD-20260708-8a4445fc"
managed_by: workflow-generated
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `project_analysis`
> This file is workflow-generated and protected from manual edits.

# Project Analysis: agent-runner-v2

## Repo Overview

`agent-runner-v2` is a standalone Python LLM workflow orchestration engine extracted from UKBE (UK Business Engine). It executes structured multi-step workflows across multiple AI models (Claude, Codex, Qwen, and aliased models) with review loops, retries, approval gates, and deterministic runner actions for code generation, documentation, and delivery workflows.

The system operates in three primary modes:

1. **Manual workflow execution** (`ukbe-run-agent run`) — Local development with full job state management
2. **Backend-connected execution** (`ukbe-run-agent worker`, `poll`, `execute-step`) — Distributed operation with backend API coordination
3. **Workstation supervision** (`ukbe-run-agent daemon`) — Persistent background operation with continuous polling

The backend serves as the source of truth for runs, step runs, artifacts, events, and approvals. The runner handles prompt rendering, coder/action execution, output validation via `meta.json` sidecars, and explicit failure routing through the workflow router.

### Key Architectural Principles (v2 Contract)

- **meta.json sidecar is the only structured result channel** — No markdown write-backs by the runner
- **No silent recovery paths** — Hard failures route explicitly through runner failure handling
- **Coder owns content analysis** — The runner does not parse LLM output for blocking issues
- **Centralized path constants** — All paths defined in `constants.py` with zero hardcoded strings in core modules

## Codebase Structure

### Package Layout

```
agent_runner_v2/
├── __init__.py                     # Package entry point
├── run_agent.py                    # CLI entry point and orchestration (2329 lines)
├── step_runner.py                  # Prompt rendering, sidecar validation, artifact checks (2437 lines)
├── workflow_router.py              # Post-step routing for approve/reject/failure cases (787 lines)
├── job_state.py                    # job.json lifecycle management (1806 lines)
├── coder_adapters.py               # Claude/Codex/Qwen invocation and polling
├── template_groups.py              # Package-local workflow definition mirror
├── bundle_loader.py                # Bootstrap seeding and workflow bundle loading
├── runtime_context.py              # Active workflow/runtime path context
├── constants.py                    # Centralized artifact path constants (677 lines)
├── actions/                        # Deterministic runner actions (29 action modules)
│   ├── finalize_bootstrap.py
│   ├── publish_architecture_site.py
│   ├── sync_codebase_docs.py
│   ├── sync_system_docs.py
│   ├── validate_*.py               # 8 validation actions
│   └── ... (21 more actions)
├── bootstrap/                      # Bootstrap workflow definitions
│   ├── bundles/core/current/       # Core bundle templates (18 files)
│   ├── themes/default/             # HTML theme templates
│   └── workflows/default/          # Default workflow prompts and schemas
├── config/                         # Configuration modules
└── tools/                          # Utility tools (agent_tools.py)
```

### Documentation Structure

```
docs/
├── codebase/                       # Codebase documentation
│   ├── 01_inventory/               # Module/component inventory (3 files + CODEBASE_INVENTORY.md)
│   ├── 02_modules/                 # Module documentation (67 files)
│   ├── 03_components/              # Component documentation (6 files)
│   └── 04_changes/                 # Change impact documents
├── delivery/                       # Delivery workflow outputs
│   ├── 00_standards/               # Delivery governance standards
│   ├── 01_initiatives/
│   ├── 02_plans/
│   ├── 03_tasks/
│   └── ...
├── site/                           # Generated architecture sites
│   ├── stakeholders/
│   ├── developers/
│   ├── operators/
│   ├── testers/
│   └── users/
└── system/                         # System documentation
    └── 00_governance/bootstrap/    # Master system docs (18 files)
```

### Test Structure

```
tests/
├── unit/                           # Pure unit tests (isolated logic, no filesystem)
│   ├── test_bundle_loader.py
│   ├── test_codebase_docs.py
│   ├── test_documentation_governance.py
│   ├── test_documentation_guardrails_cleanup.py
│   ├── test_run_agent_status.py
│   ├── test_runtime_context_paths.py
│   └── test_tool_instruction_block.py
├── integration/                    # Integration tests (real files, external systems, subprocesses)
│   ├── test_architecture_site.py
│   ├── test_backend_worker_mode.py
│   ├── test_daemon.py
│   ├── test_notification_e2e.py
│   ├── test_notification_integration.py
│   ├── test_notifications.py
│   ├── test_pushover.py
│   └── test_ukbe_runner_wrapper.py
└── conftest.py                     # Shared fixtures
```

### Scripts and Launchers

Repository root contains launcher batch files:
- `run-00_master_docs_bootstrap_v1.bat` through `run-55_user_docs_v1.bat` — Workflow launchers
- `ukbe-daemon.bat`, `ukbe-daemon-wsl.sh` — Daemon control scripts

## Domain

`agent-runner-v2` operates in the **LLM workflow orchestration domain**, specifically targeting:

1. **AI-assisted software development** — Structured code generation with review loops and artifact validation
2. **Documentation governance** — Automated generation and maintenance of system/codebase/delivery documentation
3. **Delivery scaffold management** — SOP generation, template registries, agent contracts, status rules
4. **Multi-model orchestration** — Unified interface across Claude, Codex, Qwen, and aliased LLM providers
5. **Backend-coordinated distributed execution** — Worker pools polling backend APIs for work distribution

### Primary Stakeholders

| Stakeholder | Use Case | Artifact Focus |
|-------------|----------|----------------|
| **Software Engineers** | Code generation, bug fixes, refactoring | `IMPL_FILE`, `REVIEW_FILE`, `PATCH_FILE` |
| **Technical Writers** | Documentation generation and sync | `SYSTEM_CONTEXT`, `COMPONENT_ARCHITECTURE`, `CODEBASE_INVENTORY` |
| **DevOps/Platform Engineers** | Workflow automation, CI/CD integration | `DELIVERY_SOP`, `RUNBOOK`, `DAEMON_MODE_QUICKSTART` |
| **Product Managers** | Initiative intake, planning | `DRAFT_INIT_FILE`, `PLAN_FILE`, `TASK_GRAPH_FILE` |
| **Architects** | System overview, decision tracking | `BUSINESS_CAPABILITIES`, `FUNCTIONAL_SPEC`, `DECISION_LOG` |
| **Operators** | Runtime monitoring, notification management | `notifications.py`, `notification_manager.py`, Pushover config |

## Tech Stack

### Core Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.12.10 | Runtime language (minimum 3.11) |
| **setuptools** | >=68 | Package build and installation |
| **pytest** | >=8.2.0 | Testing framework |
| **pytest-cov** | >=5.0.0 | Test coverage reporting |

### External Integrations

| Integration | Interface | Purpose | Optional |
|-------------|-----------|---------|----------|
| **LLM Providers** | Subprocess invocation | Code generation and reasoning (Claude/Codex/Qwen) | No |
| **Backend API** | HTTP/WebSocket | Job distribution and status reporting | Yes |
| **Pushover** | HTTPS API | Push notifications for workflow events | Yes |
| **Git** | CLI subprocess | Version control and diff generation | No |
| **ComfyUI** | HTTP API | Image/video generation for content workflows | Yes |

### Build and Packaging

- **Build system**: setuptools with `pyproject.toml` configuration
- **Package data**: JSON schemas, markdown templates, workflow prompts bundled in package
- **Entry point**: `ukbe-run-agent` CLI command via `project.scripts`
- **Optional dependencies**: `dev` extras for testing (`pytest`, `pytest-cov`)

### Testing Infrastructure

- **Test framework**: pytest with markers for `unit` and `integration` separation
- **Test isolation**: Unit tests use pure logic; integration tests use real files/subprocesses
- **Temp directory policy**: `.pytest-temp` with `tmp_path_retention_policy = "none"`
- **Cache disabled**: `-p no:cacheprovider` to avoid Windows permission issues

## Complexity

### Codebase Scale

| Metric | Value |
|--------|-------|
| **Python modules** | 69 (47 in `agent_runner_v2/`, 29 in `actions/`) |
| **Lines of code** | ~15,000+ (core modules range 787-2437 lines each) |
| **Workflow families** | 22 defined in `template_groups.py` (2326 lines) |
| **Action modules** | 29 deterministic runner actions |
| **Test files** | 15 (7 unit, 8 integration) |
| **Documentation files** | 101 markdown files in `docs/` |
| **Constants** | 677 lines in `constants.py` with centralized path definitions |

### Architectural Complexity

**HIGH** — Multi-layered architecture with:

1. **CLI Layer** (`run_agent.py`) — Argument parsing, command dispatch, orchestration
2. **Execution Core** — Step runner, workflow router, job state manager, runtime context
3. **Coder Integration** — LLM adapters, model config, execution request/result schemas
4. **Action Layer** — 29 deterministic actions for documentation, validation, publishing
5. **Bootstrap Layer** — Bundle loader, template groups, workflow specs
6. **Support Components** — Constants, doc paths, guardrails, notifications, backend client

### Workflow Complexity

| Dimension | Count | Notes |
|-----------|-------|-------|
| **Workflow families** | 22 | From `00_master_docs_bootstrap_v1` to `55_user_docs_v1` |
| **Total steps** | ~150+ | Across all workflow families |
| **Artifact keys** | 100+ | Defined in `constants.py` and `template_groups.py` |
| **Agent roles** | 7 | Planner, Task Decomposer, Impl Planner, Executor, Reviewer, Memory Manager, plus generic |
| **Review/refine loops** | Multiple | Explicit in workflow definitions with max_rejects limits |

### Operational Complexity

**MODERATE-HIGH** — Requires understanding of:

- Runtime path resolution (absolute vs relative, workspace-root flags)
- Windows compatibility quirks (pathlib, tmp_path permissions)
- Subprocess working directory management for `.env` loading
- Backend API contract for distributed execution
- Notification configuration (Pushover credentials, context requirements)
- Job state schema migration (version 6 current)

## Recommended Workflow Scope

### Universal Baseline (All Repositories)

Every repository bootstrapped with `agent-runner-v2` should include:

1. **Core execution infrastructure**
   - CLI entry point, step runner, workflow router, job state manager
   - Centralized constants module for path management
   - Meta.json sidecar contract enforcement

2. **Documentation governance**
   - System documentation generation (`00_master_docs_bootstrap_v1`)
   - Codebase documentation scaffolding (`10_execution_scaffold_v1`)
   - Documentation sync capability (`40_documentation_sync_v1`)

3. **Delivery scaffold**
   - Project analysis, SOP generation, template registries
   - Agent contracts for planner, executor, reviewer roles
   - Status rules and validation templates

4. **Testing infrastructure**
   - Unit/integration test split with pytest
   - Isolated temp directories for Windows compatibility
   - Coverage reporting

### Repository-Specific Selection (agent-runner-v2)

This repository requires:

1. **Full workflow suite** — All 22 workflow families active due to self-hosting nature
2. **Architecture site publishing** — `50_architecture_site_v1` for stakeholder/developer/operator views
3. **Backend integration** — Worker mode, daemon supervisor, execute-step for distributed operation
4. **Content generation workflows** — T2I, I2V, voiceover, video assembly for multimedia pipelines
5. **Bug fix intake** — `21_bug_fix_intake_v1` with GitHub issue fetching capability

### Excluded Workflows (Not Applicable)

None — this repository exercises the full capability set as it is the reference implementation.

## Recommended Agent Roles

### Core Delivery Agents (7 Roles)

| Agent | Responsibility | Key Artifacts |
|-------|----------------|---------------|
| **Planner** | High-level planning, strategy decomposition | `PLAN_FILE`, `TASK_GRAPH_FILE` |
| **Task Decomposer** | Break plans into executable task contracts | `TASK_FILE` |
| **Implementation Planner** | Detailed implementation design | `IMPL_FILE` |
| **Executor** | Code generation and modification | Modified source files, `meta.json` |
| **Reviewer** | Code review, refinement suggestions | `REVIEW_FILE` |
| **Memory Manager** | Context preservation, knowledge retention | Memory entries, cross-references |
| **Generic Coder** | General-purpose code/doc generation | Any artifact based on prompt |

### Specialized Agents (Domain-Specific)

| Agent | Workflow Family | Purpose |
|-------|----------------|---------|
| **Initiative Analyst** | `20_initiative_intake_v1` | Draft initiative intake, pre-init refinement |
| **Bug Triage Specialist** | `21_bug_fix_intake_v1` | Bug report drafting, reproduction steps, root cause analysis |
| **Documentation Sync Agent** | `40_documentation_sync_v1` | Reconcile codebase drift, update stale docs |
| **Architecture Publisher** | `50_architecture_site_v1` | Generate HTML architecture views for multiple audiences |
| **Content Creator** | TikTok/Image/Video workflows | Generate images, videos, audio from narratives |

### Agent Role Boundaries

- **Planner** → defines what needs to be done (strategy)
- **Task Decomposer** → defines how to break it down (structure)
- **Impl Planner** → defines how to implement each task (design)
- **Executor** → performs the actual implementation (execution)
- **Reviewer** → validates quality and suggests improvements (quality)
- **Memory Manager** → preserves institutional knowledge (continuity)

## Codebase Documentation Scope

### Universal Baseline (All File Types)

The codebase documentation system covers:

1. **Module Documentation** (`docs/codebase/02_modules/`)
   - One markdown file per Python module
   - Covers purpose, key functions, collaborators, usage examples
   - Auto-generated via `scan_repo_codebase` action

2. **Component Documentation** (`docs/codebase/03_components/`)
   - Higher-level component views (packages, suites)
   - Cross-module relationships and integration points
   - Manual curation with workflow protection

3. **Inventory** (`docs/codebase/01_inventory/`)
   - `codebase_inventory.md` — Complete module/component listing
   - `INTEGRATION_MAP.md` — Inter-module dependencies
   - `FAILURE_MODES.md` — Known failure scenarios
   - `ARCHITECTURE_FLOW.md` — Data/control flow diagrams

4. **Change Impact** (`docs/codebase/04_changes/`)
   - Per-change documents tracking modifications outside normal workflow
   - Validation summaries, change logs, snapshots

### Repository-Specific Profile (agent-runner-v2)

This repository maintains:

- **67 module documentation files** — Comprehensive coverage of all major modules
- **6 component documentation files** — Actions package, workflow families, tests suite, scripts, config/data, codebase governance
- **4 inventory files** — Complete listing, integration map, failure modes, architecture flow
- **Dynamic change tracking** — Change impact documents generated per significant modification

### Documentation Maintenance Scope

| Document Type | Update Frequency | Trigger | Owner |
|---------------|------------------|---------|-------|
| Module docs | On module changes | Code modification | Developer + sync workflow |
| Component docs | On structural changes | New packages, major refactors | Architect |
| Inventory | Periodic | `scan_repo_codebase` action | Automation |
| Change impacts | Per change | Manual or automated detection | Developer |
| System docs | Major releases | `00_master_docs_bootstrap_v1` | Technical writer |

## Documentation Freshness Risks

### High-Risk Areas

1. **Code Changes Outside Workflow SOP**
   - **Risk**: Direct edits to source files without running documentation sync workflows
   - **Impact**: Module docs become stale, inventory outdated
   - **Mitigation**: Enforce `40_documentation_sync_v1` after any code modification; use change impact documents for emergency fixes

2. **Workflow Definition Drift**
   - **Risk**: Updates to `template_groups.py` not reflected in runtime bundles
   - **Impact**: Runtime behavior diverges from bootstrap source
   - **Mitigation**: Always run `ukbe-run-agent init` after modifying bootstrap workflows; verify runtime bundle matches

3. **Constants Module Evolution**
   - **Risk**: New artifact keys added to `constants.py` but not propagated to prompts/templates
   - **Impact**: Placeholder resolution failures at runtime
   - **Mitigation**: Validate all prompt templates reference valid artifact keys; use centralized `placeholder()` function

4. **Backend API Contract Changes**
   - **Risk**: Backend API evolves without updating worker/poll/daemon modes
   - **Impact**: Backend-connected execution fails silently or with cryptic errors
   - **Mitigation**: Document backend API contract explicitly; add integration tests for backend communication

5. **Test Suite Divergence**
   - **Risk**: Unit tests accidentally gain filesystem dependencies; integration tests lack proper isolation
   - **Impact**: False positives/negatives in test results
   - **Mitigation**: Enforce strict unit/integration separation; review test file imports for filesystem operations

### Medium-Risk Areas

6. **Notification Configuration Drift**
   - **Risk**: Pushover credentials expire or change without updating `.env`
   - **Impact**: Silent notification failures during critical workflow events
   - **Mitigation**: Add notification health check to daemon startup; document credential rotation procedure

7. **Windows Compatibility Regressions**
   - **Risk**: New code introduces pathlib assumptions that fail on Windows
   - **Impact**: Path resolution failures, permission errors
   - **Mitigation**: Always use `_safe_relative_to()` helper; run tests on Windows periodically

8. **Job State Schema Evolution**
   - **Risk**: New fields added to `job.json` without schema version bump or migration logic
   - **Impact**: Old jobs fail to load, new jobs incompatible with old runners
   - **Mitigation**: Bump `CURRENT_SCHEMA_VERSION` on any schema change; implement migration in `job_state.py`

### Low-Risk Areas (Currently Managed)

9. **Prompt Template Updates**
   - **Current state**: Prompts use artifact key placeholders, resolved at runtime
   - **Risk level**: Low due to centralized constant system
   - **Monitoring**: Validate placeholder resolution during step execution

10. **Generated Document Protection**
    - **Current state**: Workflow-generated documents have protection banners and guardrails
    - **Risk level**: Low due to `_assert_protected_docs_unchanged()` validation
    - **Monitoring**: Reject manual edits to protected documents

## Project-Specific SOP Considerations

### Delivery SOP Requirements

This repository's delivery standard operating procedures must account for:

1. **Self-Hosting Nature**
   - The repository generates its own documentation using its own workflows
   - SOP must distinguish between bootstrap (development) and runtime (global) contexts
   - Changes to bootstrap sources require re-initialization of global runner home

2. **Multi-Mode Operation**
   - SOP must cover manual, backend-connected, and daemon modes
   - Each mode has different failure modes and recovery procedures
   - Daemon mode requires special attention to subprocess lifecycle and `.env` loading

3. **Artifact Volume**
   - 100+ artifact keys across 22 workflow families
   - SOP must provide clear artifact naming conventions and folder organization
   - Cross-workflow artifact dependencies must be documented (e.g., `PROJECT_ANALYSIS` feeds into delivery scaffold)

4. **Review Loop Enforcement**
   - Multiple workflows include explicit review/refine cycles
   - SOP must define max_rejects thresholds and escalation procedures
   - Human-in-the-loop approval gates for critical artifacts

### Codebase Documentation SOP Requirements

1. **Scan-Based Generation**
   - Module docs auto-generated via `scan_repo_codebase` action
   - SOP must define scan frequency and trigger conditions
   - Manual curation allowed for component docs but not module docs

2. **Change Impact Tracking**
   - Every significant code change requires a change impact document
   - SOP must define "significant" criteria (API changes, architectural shifts, bug fixes)
   - Change impacts feed into documentation sync workflows

3. **Inventory Maintenance**
   - `codebase_inventory.md` must stay synchronized with actual module count
   - SOP must include periodic inventory reconciliation
   - Stale module references must be cleaned up proactively

### Operational SOP Requirements

1. **Initialization Procedure**
   - `ukbe-run-agent init` seeds global runner home
   - SOP must verify config.json, workflow bundles, job directories created correctly
   - Post-init validation should confirm runtime paths resolve correctly

2. **Daemon Lifecycle Management**
   - Daemon spawns fresh subprocesses per step; does not restart for code changes
   - SOP must cover daemon start/stop, log monitoring, child process tracking
   - Failure recovery must preserve job state for retry

3. **Notification Management**
   - Pushover notifications require API credentials in `.env`
   - SOP must cover credential setup, rotation, and troubleshooting
   - Notification context must include workflow_name, template_group, timestamps

## Operational Risks

### Critical Risks

1. **Runtime Path Resolution Failures**
   - **Description**: Workflow paths in `config.json` must use absolute paths or be omitted to avoid workspace-relative resolution failures
   - **Evidence**: Memory from `workflow-config-path-resolution.md`; Windows-specific pathlib issues
   - **Impact**: Workflow execution fails immediately; jobs cannot initialize
   - **Mitigation**: Use `--project-root` flag for repo-local workflows; omit `workflows` map from config.json for standard setups; always use `_safe_relative_to()` helper

2. **Subprocess Working Directory Mismatch**
   - **Description**: Daemon subprocess needs correct CWD for `.env` loading and artifact path resolution
   - **Evidence**: Fixed in codebase per `daemon-subprocess-cwd-fix.md` memory
   - **Impact**: Credentials not loaded; artifacts written to wrong locations
   - **Mitigation**: Subprocesses set working directory explicitly before execution; verify `.env` presence in project root

3. **Backend API Contract Ambiguity**
   - **Description**: No explicit documentation of backend HTTP API endpoints expected by worker mode
   - **Evidence**: Identified gap in existing PROJECT_ANALYSIS.md
   - **Impact**: Backend integration fails with unclear error messages; debugging difficult
   - **Mitigation**: Document backend API contract in developer guide; add integration tests for backend communication; log full request/response cycles

### High Risks

4. **Documentation Drift from Code Changes**
   - **Description**: Code changes outside normal workflow SOP cause documentation staleness
   - **Evidence**: Change impact documents in `docs/codebase/04_changes/`; memory from `fix-prompts-not-generated-docs.md`
   - **Impact**: Module docs outdated; inventory incorrect; onboarding difficulty increases
   - **Mitigation**: Enforce `40_documentation_sync_v1` after code modifications; use change impact documents for emergency fixes; periodic inventory reconciliation

5. **Test Suite Contamination**
   - **Description**: Unit tests accidentally gain filesystem dependencies; integration tests lack proper isolation
   - **Evidence**: Memory from `unit-test-pure-logic.md`; pytest tmp_path permission issues on Windows
   - **Impact**: False test results; CI/CD flakiness; misleading coverage reports
   - **Mitigation**: Strict unit/integration separation enforced in test structure; review test imports for filesystem operations; use isolated temp directories

6. **Job State Schema Incompatibility**
   - **Description**: New fields added to `job.json` without schema version bump or migration logic
   - **Evidence**: Current schema version 6; migration logic exists in `job_state.py`
   - **Impact**: Old jobs fail to load; new jobs incompatible with old runners
   - **Mitigation**: Bump `CURRENT_SCHEMA_VERSION` on any schema change; implement forward/backward migration; document schema evolution policy

### Medium Risks

7. **Notification Credential Expiration**
   - **Description**: Pushover credentials expire or change without updating `.env`
   - **Evidence**: Pushover configuration present but not fully documented
   - **Impact**: Silent notification failures during critical workflow events
   - **Mitigation**: Add notification health check to daemon startup; document credential rotation procedure; test notification delivery periodically

8. **Constants Module Drift**
   - **Description**: New artifact keys added to `constants.py` but not propagated to prompts/templates
   - **Evidence**: Centralized constant system in place; 677 lines of definitions
   - **Impact**: Placeholder resolution failures at runtime; confusing error messages
   - **Mitigation**: Validate all prompt templates reference valid artifact keys; use centralized `placeholder()` function; add linting for undefined placeholders

9. **Windows Compatibility Regressions**
   - **Description**: New code introduces pathlib assumptions that fail on Windows
   - **Evidence**: Fixed `Path.relative_to()` failures per `pathlib-windows-bug-fix.md` memory
   - **Impact**: Path resolution failures; permission errors; test failures
   - **Mitigation**: Always use `_safe_relative_to()` helper; run tests on Windows periodically; document Windows-specific considerations

### Low Risks

10. **Prompt Template Synchronization**
    - **Description**: Bootstrap prompts updated but runtime bundles not re-initialized
    - **Evidence**: Two distinct sources (packaged bootstrap vs runtime bundle)
    - **Impact**: Runtime behavior uses stale prompts; changes not reflected
    - **Mitigation**: Always run `ukbe-run-agent init` after modifying bootstrap workflows; document bootstrap-to-runtime synchronization procedure

11. **Generated Document Manual Edits**
    - **Description**: Users manually edit workflow-generated documents despite protection banners
    - **Evidence**: Protected document guardrails in place; memory from `fix-prompts-not-generated-docs.md`
    - **Impact**: Manual edits overwritten on next workflow run; user frustration
    - **Mitigation**: Enforce `_assert_protected_docs_unchanged()` validation; educate users to update source prompts instead; provide clear guidance in HOW_TO_GUIDE.md

12. **Performance Tuning Gaps**
    - **Description**: No documentation on optimizing coder timeout settings or parallel execution
    - **Evidence**: Identified gap in existing analysis
    - **Impact**: Suboptimal performance; timeouts on large artifacts; missed parallelization opportunities
    - **Mitigation**: Document performance tuning parameters; provide recommended defaults; add monitoring for execution duration

## Architectural Observations

### 1. Centralized Constants Pattern (Strength)

- All artifact paths consolidated in `constants.py` with layered constant system
- `FOLDER_KEY_*`, `ARTIFACT_KEY_*`, `ARTIFACT_PATH_*` constants provide single source of truth
- Zero hardcoded strings in path construction across core modules (`step_runner.py`, `documentation_guardrails.py`)
- Pre-computed path constants eliminate formatting complexity at injection time
- **Impact**: Reduces maintenance burden; prevents path mismatches; enables easy path swaps

### 2. Prompt Injection with Placeholders (Strength)

- Templates use `{ARTIFACT_KEY}` placeholders instead of hardcoded paths
- Placeholders resolved at runtime via centralized `placeholder()` function
- Supports swapping between bootstrap (dev) and runtime (global) contexts seamlessly
- **Impact**: Decouples prompt design from deployment context; enables multi-environment support

### 3. Job State Management with Schema Migration (Strength)

- `job.json` is the source of truth for workflow execution state
- Schema version 6 (CURRENT_SCHEMA_VERSION) with runner_version="v2"
- Comprehensive retry history, failure tracking, usage summary
- Loop context and replan context for refinement workflows
- Forward/backward migration support for schema evolution
- **Impact**: Enables long-running workflows; supports retry/refine patterns; preserves execution history

### 4. Notification System with Context Requirements (Moderate)

- Pushover notifications for step and workflow events
- Context requires `workflow_name`, `template_group`, timestamps
- Step-level notifications require `enable_notifications: True` in step config
- Notification manager supports pluggable backends
- **Gap**: Credential management and health checks not fully documented
- **Impact**: Provides operational visibility; aids debugging; requires credential maintenance

### 5. Backend Integration with Graceful Degradation (Strength)

- Worker mode polls backend for work via HTTP API
- `execute-step` command for backend-driven single-step execution
- Daemon falls back to local mode when backend unavailable
- Artifact rules system for backend path resolution
- **Gap**: Backend API contract not explicitly documented
- **Impact**: Enables distributed execution; maintains functionality when backend down

### 6. Protected Document Guardrails (Strength)

- Workflow-generated documents are protected from manual edits
- `_assert_protected_docs_unchanged()` validates no external modifications
- `generated_doc_manifest` tracks workflow outputs
- Protection banner clearly marks generated files
- **Impact**: Prevents documentation drift; enforces workflow discipline; reduces manual maintenance

### 7. Action Layer Extensibility (Strength)

- 29 deterministic runner actions in `actions/` package
- Clear pattern for adding new actions (implement function, register in `__init__.py`)
- Actions handle documentation sync, validation, publishing, content generation
- **Impact**: Easy to extend system capabilities; promotes code reuse; maintains consistency

### 8. Multi-Model Coder Adapter Pattern (Strength)

- Unified interface for Claude, Codex, Qwen via adapter pattern in `coder_adapters.py`
- Model config and alias mapping in `model_config.py`
- Subprocess-based invocation isolates model-specific quirks
- **Impact**: Model-agnostic workflow definitions; easy to add new providers; fallback strategies possible

### 9. Workflow Bundle/Runtime Distinction (Complexity)

- Packaged bootstrap source in repo: `agent_runner_v2/bootstrap/workflows/default/`
- Runtime workflow bundle: `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\`
- Runtime prompts/templates loaded from global runner home, not directly from repo tree
- Repo bootstrap files only seed runtime bundles during `ukbe-run-agent init`
- **Impact**: Clear separation of concerns; requires synchronization awareness; adds initialization step

### 10. Test Structure Discipline (Strength)

- Strict unit/integration separation with pytest markers
- Unit tests focus on pure logic without filesystem dependencies
- Integration tests handle real files, external systems, subprocesses
- Temp directory policy avoids Windows permission issues
- **Impact**: Fast unit test feedback; reliable integration validation; cross-platform compatibility

## Architecture Posture

| Attribute | Value | Rationale |
|-----------|-------|-----------|
| **current_profile** | `explicit-v2-workflow-runner` | Clear v2 contract with meta.json sidecars, explicit failure routing, centralized constants |
| **target_profile** | `universal-bootstrap-engine` | A standalone workflow engine that can bootstrap any repository with consistent documentation and delivery patterns |
| **migration_mode** | `provisional` | The repo has established patterns but the universal abstraction is still evolving; self-hosting creates circular dependencies |
| **repo_state** | `explicit` | Clear architecture with centralized constants, defined workflow families, established conventions, comprehensive documentation |

### Evidence Sources

1. **Codebase Inventory** (`docs/codebase/01_inventory/codebase_inventory.md`): 69 Python modules, 6 component documentation files
2. **Change Impact Document** (`00DOC-20260708-78fb419e-bootstrap.md`): Comprehensive repository scan showing current state
3. **Module Documentation** (`docs/codebase/02_modules/`): 67 module docs covering all major components
4. **Workflow Families** (`docs/codebase/03_components/workflow-families.md`): 22 workflow families with step counts
5. **Constants Module** (`agent_runner_v2/constants.py`): 677 lines of centralized path constants
6. **Template Groups** (`agent_runner_v2/bootstrap/workflows/default/template_groups.py`): 2326 lines of workflow definitions
7. **System Architecture Docs** (`docs/system/00_governance/bootstrap/`): 18 master system documents

### Unresolved Documentation Gaps

1. **Backend API Contract**: No explicit documentation of the backend HTTP API endpoints expected by the worker mode (endpoints, request/response schemas, authentication)

2. **Action Development Guide**: No documented guide for adding new deterministic runner actions to the `actions/` package (naming conventions, registration process, testing requirements)

3. **Workflow Bundle Customization**: Limited documentation on creating custom workflow bundles beyond the bootstrap seeding (directory structure, template syntax, validation procedures)

4. **Notification Configuration Reference**: Pushover configuration is present but not fully documented in system docs (credential format, context requirements, troubleshooting)

5. **Architecture Site Themes**: Theme customization documentation exists in code (`site_styles.py`, `bootstrap/themes/`) but not in user-facing docs

6. **Migration from v1**: No explicit migration guide for users coming from agent-runner-v1 (breaking changes, feature mapping, upgrade procedure)

7. **Performance Tuning Guide**: No documentation on optimizing coder timeout settings, parallel execution limits, or artifact size thresholds

8. **Error Code Reference**: Failure codes like `PLANNING_ATTEMPT_BUDGET_EXCEEDED` exist but lack comprehensive reference with remediation guidance

9. **Testing Philosophy**: While test structure exists, there's no documented testing philosophy, contribution guidelines, or test writing best practices

10. **Cross-Platform Considerations**: Windows-specific fixes exist (pathlib, tmp_path) but aren't summarized in operational docs; macOS/Linux differences not documented

## Discovered Files

### AI Coder Context Files

| File | Location | Purpose |
|------|----------|---------|
| `QWEN.md` | Project root | Qwen Code assistant instructions (this file's predecessor) |
| `CLAUDE.md` | Project root | Claude-specific context and guidelines |
| `agent_runner_v2/QWEN.md` | Package subdirectory | Package-local Qwen context |

### Project Metadata Files

| File | Location | Purpose |
|------|----------|---------|
| `README.md` | Project root | Project overview, install instructions, CLI modes |
| `pyproject.toml` | Project root | Build configuration, dependencies, entry points |
| `requirements.txt` | Project root | Dependency list (if present) |
| `.env.example` | Project root | Environment variable template |
| `.gitignore` | Project root | Git ignore patterns |

### Architecture/Design Documentation

| Category | Location | File Count |
|----------|----------|------------|
| **System Governance** | `docs/system/00_governance/bootstrap/` | 18 files |
| **Codebase Modules** | `docs/codebase/02_modules/` | 67 files |
| **Codebase Components** | `docs/codebase/03_components/` | 6 files |
| **Codebase Inventory** | `docs/codebase/01_inventory/` | 4 files |
| **Change Impacts** | `docs/codebase/04_changes/` | Dynamic |

Key architecture documents:
- `SYSTEM_CONTEXT.md` — System boundaries, external integrations, security boundaries
- `COMPONENT_ARCHITECTURE.md` — Component groups, dependencies, design patterns
- `DEVELOPER_GUIDE.md` — Development workflow, testing, contribution guidelines
- `RUNBOOK.md` — Operational procedures, troubleshooting, maintenance tasks
- `FUNCTIONAL_SPEC.md` — Functional requirements, workflow specifications
- `NON_FUNCTIONAL_REQUIREMENTS.md` — Performance, reliability, security requirements

### Existing Delivery Documentation

| Directory | Purpose | Notable Contents |
|-----------|---------|------------------|
| `docs/delivery/00_standards/` | Delivery governance standards | Agent contracts, SOPs, status rules |
| `docs/delivery/01_initiatives/` | Initiative intake documents | Draft and approved initiatives |
| `docs/delivery/02_plans/` | Delivery plans | Strategic and tactical plans |
| `docs/delivery/03_tasks/` | Task contracts | Decomposed task definitions |
| `docs/delivery/04_implementation_plans/` | Implementation designs | Detailed implementation specs |
| `docs/delivery/05_reviews/` | Review artifacts | Code review findings, refinements |
| `docs/delivery/06_validations/` | Validation results | Quality gate outcomes |
| `docs/delivery/07_memory/` | Institutional knowledge | Lessons learned, decisions |
| `docs/delivery/08_agents/` | Agent definitions | Role specifications, contracts |

### Existing Codebase Documentation

| Directory | Purpose | Maintenance Strategy |
|-----------|---------|---------------------|
| `docs/codebase/01_inventory/` | Module/component inventory | Auto-generated via scan |
| `docs/codebase/02_modules/` | Individual module docs | Auto-generated, protected |
| `docs/codebase/03_components/` | Component-level docs | Manually curated, protected |
| `docs/codebase/04_changes/` | Change impact tracking | Per-change documents |
| `docs/codebase/00_standards/` | Codebase documentation SOPs | Workflow-generated |

### Bootstrap Workflow Definitions

| File | Location | Purpose |
|------|----------|---------|
| `template_groups.py` | `agent_runner_v2/bootstrap/workflows/default/` | Workflow family definitions (2326 lines) |
| `job_schema.json` | `agent_runner_v2/bootstrap/workflows/default/` | Job state JSON schema |
| `llm_response_schema.json` | `agent_runner_v2/bootstrap/workflows/default/` | LLM response validation schema |
| `model_mapping.json` | `agent_runner_v2/bootstrap/workflows/default/` | Model alias resolution |
| `usage_schema.json` | `agent_runner_v2/bootstrap/workflows/default/` | Usage tracking schema |
| `prompts/*/` | `agent_runner_v2/bootstrap/workflows/default/prompts/` | Prompt templates per workflow |

### Core Bundle Templates

Located in `agent_runner_v2/bootstrap/bundles/core/current/`:

| Document | Purpose |
|----------|---------|
| `README.md` | Bundle overview |
| `BUNDLE_TAXONOMY.md` | Bundle classification system |
| `BUNDLE_MIGRATION_PLAN.md` | Migration strategy for bundle evolution |
| `BUSINESS_CAPABILITIES.md` | Business capability model |
| `COMPONENT_ARCHITECTURE.md` | Component architecture view |
| `DECISION_LOG.md` | Architectural decisions record |
| `DEVELOPER_GUIDE.md` | Developer onboarding guide |
| `DOCUMENTATION_STANDARD.md` | Documentation quality standards |
| `EXISTING_REPO_WORKFLOW_SOP.md` | Standard operating procedure |
| `FUNCTIONAL_SPEC.md` | Functional specifications |
| `NON_FUNCTIONAL_REQUIREMENTS.md` | Non-functional requirements |
| `RUNBOOK.md` | Operational runbook |
| `SYSTEM_CONTEXT.md` | System context diagram |
| `SYSTEM_FILE_STRUCTURE.md` | File organization rationale |
| `SYSTEM_OVERVIEW.md` | High-level system overview |

### Test Files

| Test Type | Location | File Count | Coverage Area |
|-----------|----------|------------|---------------|
| **Unit Tests** | `tests/unit/` | 7 files | Pure logic, isolated components |
| **Integration Tests** | `tests/integration/` | 8 files | Real files, external systems, subprocesses |
| **Shared Fixtures** | `tests/conftest.py` | 1 file | Common test utilities |

Unit test coverage:
- Bundle loader functionality
- Codebase documentation generation
- Documentation governance validation
- Documentation guardrails cleanup
- Run agent status reporting
- Runtime context path resolution
- Tool instruction block processing

Integration test coverage:
- Architecture site generation and publishing
- Backend worker mode communication
- Daemon supervisor lifecycle
- Notification end-to-end flows
- Pushover integration
- UKBE runner wrapper execution

### Launcher Scripts

| Script | Purpose | Workflow Target |
|--------|---------|----------------|
| `run-00_master_docs_bootstrap_v1.bat` | Generate master system documentation | `00_master_docs_bootstrap_v1` |
| `run-10_execution_scaffold_v1.bat` | Delivery scaffold setup | `10_execution_scaffold_v1` |
| `run-20_initiative_intake_v1.bat` | Initiative intake | `20_initiative_intake_v1` |
| `run-21_bug_fix_intake_v1.bat` | Bug fix triage | `21_bug_fix_intake_v1` |
| `run-30_delivery_planning_v1.bat` | Delivery planning | `30_delivery_planning_v1` |
| `run-31_task_execution_v1.bat` | Task execution | `31_task_execution_v1` |
| `run-40_documentation_sync_v1.bat` | Documentation sync | `40_documentation_sync_v1` |
| `run-41_developer_doc_v1.bat` | Developer documentation | `41_audience_doc_v1` |
| `run-41_operator_doc_v1.bat` | Operator documentation | `41_audience_doc_v1` |
| `run-50_architecture_site_v1.bat` | Architecture site publishing | `50_architecture_site_v1` |
| Additional launchers | Various audience docs and content workflows | Various |

### Configuration and Support Files

| File | Purpose |
|------|---------|
| `HOW_TO_GUIDE.md` | Delivery scaffold workflow guide |
| `PUSHOVER_NOTIFICATIONS.md` | Pushover notification configuration |
| `WINDOWS_COMPATIBILITY.md` | Windows-specific considerations |
| `TODO_LIST.md` | Current work items |
| `UNIT_TEST_RESULTS.md` | Recent test execution results |
| `count_workflows.py` | Utility script for workflow counting |
| `MANIFEST.in` | Package manifest for distribution |

---

*Analysis completed by workflow: 10_execution_scaffold_v1 | Step: project_analysis | Change: 10SCAFFOLD-20260708-8a4445fc*
