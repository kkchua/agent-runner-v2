---
template_id: "SYS-00-SOP"
title: "Delivery Standard Operating Procedure v1"
Status: draft
version: "1.0"
generated: "2026-07-09T10:30:00+08:00"
workflow: "10_execution_scaffold_v1"
step: "generate_sop"
change_id: "10SCAFFOLD-20260708-8a4445fc"
managed_by: workflow-generated
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_sop`
> This file is workflow-generated and protected from manual edits.

# Delivery Standard Operating Procedure v1

## Purpose

This SOP defines the standard operating procedure for executing delivery workflows within agent-runner-v2. It governs the complete lifecycle from initiative intake through implementation, review, validation, and architecture site publishing. The SOP ensures consistent execution across all workflow families while maintaining documentation governance and traceability.

## Core Principle

**Document-first, artifact-driven execution.** Every delivery workflow must produce structured artifacts (markdown documents, meta.json sidecars) that serve as the authoritative record of decisions, plans, tasks, implementations, reviews, and validations. No code or documentation change occurs without a corresponding delivery artifact.

## Authority Precedence

When conflicts arise between sources, apply this precedence order:

1. **Runtime workflow bundle** (`%USERPROFILE%\.ukbe-runner\workflows\<workflow>\`) — Runtime source of truth
2. **Bootstrap packaged source** (`agent_runner_v2/bootstrap/workflows/default/`) — Seeds runtime bundles during `ukbe-run-agent init`
3. **Centralized constants** (`agent_runner_v2/constants.py`) — Single source of truth for artifact paths
4. **Generated artifacts** — Workflow outputs in `docs/delivery/` and `docs/codebase/`
5. **Manual edits** — Prohibited on workflow-generated documents; use source prompts instead

## Workflow State Machine

The delivery lifecycle follows explicit state transitions. Each arrow represents a valid transition enforced by the workflow router.

### Primary Lifecycle (Initiative Intake)

```
draft → active → planned → executing → completed
```

### Task Graph Lifecycle (Delivery Planning)

```
draft → active → task_graph_ready → task_graph_validated → executing → completed
```

### Implementation Lifecycle (Task Execution)

```
draft → active → implementing → reviewing → validating → completed
```

### Documentation Sync Lifecycle

```
draft → active → reconciling → validated → completed
```

### Architecture Site Lifecycle

```
draft → active → generating → publishing → completed
```

### Failure Transitions (All Workflows)

Any active state may transition to:
- `failed` → Explicit failure routing through runner failure handling
- `rejected` → Review loop rejection triggers refine cycle
- `awaiting_approval` → Human-in-the-loop approval gate

### Retry Transitions

- `rejecting → drafting` → Refine cycle restarts with max_rejects counter
- `failed → retrying` → Automated retry with backoff (if configured)

## Agent Roles

Seven core delivery agents execute the workflow phases. Each agent has distinct responsibilities and artifact ownership.

### Planner

**Responsibility:** High-level planning and strategy decomposition  
**Key Artifacts:** `PLAN_FILE`, `TASK_GRAPH_FILE`  
**Workflow Phases:** `30_delivery_planning_v1`  
**Boundaries:** Defines what needs to be done; does not implement or review

### Task Decomposer

**Responsibility:** Break plans into executable task contracts  
**Key Artifacts:** `TASK_FILE`  
**Workflow Phases:** `30_delivery_planning_v1`  
**Boundaries:** Converts strategic plans into atomic task units; does not execute tasks

### Implementation Planner

**Responsibility:** Detailed implementation design per task  
**Key Artifacts:** `IMPL_FILE`  
**Workflow Phases:** `31_task_execution_v1`  
**Boundaries:** Designs how to implement each task; does not write production code

### Executor

**Responsibility:** Code generation and modification  
**Key Artifacts:** Modified source files, `meta.json` sidecar  
**Workflow Phases:** `31_task_execution_v1`  
**Boundaries:** Performs actual implementation; writes code/docs; produces meta.json

### Reviewer

**Responsibility:** Code review and refinement suggestions  
**Key Artifacts:** `REVIEW_FILE`  
**Workflow Phases:** `31_task_execution_v1` (review loop)  
**Boundaries:** Validates quality; suggests improvements; does not modify code directly

### Memory Manager

**Responsibility:** Context preservation and knowledge retention  
**Key Artifacts:** Memory entries, cross-references  
**Workflow Phases:** All phases (continuous)  
**Boundaries:** Captures institutional knowledge; maintains continuity across sessions

### Generic Coder

**Responsibility:** General-purpose code/documentation generation  
**Key Artifacts:** Any artifact based on prompt  
**Workflow Phases:** Fallback role when specialized agents unavailable  
**Boundaries:** Follows prompt instructions; no domain-specific expertise assumed

## Workflow Phases

### Phase 1: Initiative Intake (`20_initiative_intake_v1`)

**Purpose:** Capture requirement and documentation scope  
**Inputs:** `DRAFT_INIT_FILE` (user-provided or skill-assisted)  
**Outputs:** `PRE_INIT_FILE`, `INIT_FILE`  
**Agent:** Initiative Analyst  
**Review Loop:** Yes (max_rejects = 2)  
**Documentation Scope:** Identifies affected modules, stale-guidance risk, acceptance criteria

### Phase 2: Delivery Planning (`30_delivery_planning_v1`)

**Purpose:** Convert documentation scope into plan/task obligations  
**Inputs:** `INIT_FILE`  
**Outputs:** `PLAN_FILE`, `TASK_GRAPH_FILE`, `TASK_FILE`  
**Agents:** Planner → Task Decomposer  
**Review Loop:** Yes (plan review, task graph validation)  
**Documentation Obligations:** Maps plan items to documentation updates required

### Phase 3: Task Execution (`31_task_execution_v1`)

**Purpose:** Execute code and documentation updates together  
**Inputs:** `TASK_FILE`  
**Outputs:** `IMPL_FILE`, modified source files, `REVIEW_FILE`, `VALIDATION_FILE`  
**Agents:** Implementation Planner → Executor → Reviewer  
**Review Loop:** Yes (implementation review with max_rejects = 3)  
**Documentation Updates:** Executes documentation changes as part of task completion

### Phase 4: Documentation Sync (`40_documentation_sync_v1`)

**Purpose:** Reconcile codebase inventory and stale guidance after drift  
**Inputs:** Current repository state, existing documentation  
**Outputs:** Updated module docs, component docs, inventory, change impacts  
**Agent:** Documentation Sync Agent  
**Review Loop:** No (automated reconciliation with validation)  
**Trigger:** Code changes outside normal workflow, periodic maintenance

### Phase 5: Architecture Site Publishing (`50_architecture_site_v1`)

**Purpose:** Publish browsable HTML architecture views for stakeholders  
**Inputs:** System documentation set, codebase inventory  
**Outputs:** Generated HTML site in `docs/site/`  
**Agent:** Architecture Publisher  
**Review Loop:** No (publishing is deterministic)  
**Audiences:** Stakeholders, developers, operators, testers, users

## Standard Rules

### Artifact Production Rules

1. **Meta.json sidecar mandatory** — Every coder/runner step must produce a `meta.json` sidecar at the step output path
2. **No markdown write-backs** — The runner does not parse LLM output for blocking issues; coder owns content analysis
3. **Deterministic artifact paths** — All artifacts written to pre-computed paths from `constants.py`; zero hardcoded strings
4. **Protected document guardrails** — Workflow-generated documents cannot be manually edited; use source prompts instead

### Review Loop Rules

1. **Max rejects enforcement** — Each workflow defines max_rejects threshold; exceeded thresholds route to failure
2. **Explicit rejection reasons** — Reviewer must provide specific findings; vague rejections rejected
3. **Refine context preserved** — Previous attempt artifacts available to coder during refine cycle

### Approval Gate Rules

1. **Human-in-the-loop required** — Critical artifacts (plans, task graphs, implementations) require explicit approval
2. **Approval recorded** — Approver identity and timestamp captured in job state
3. **Rejection triggers refine** — Approved artifacts proceed; rejected artifacts trigger refine cycle

### Failure Handling Rules

1. **No silent recovery** — Hard failures route explicitly through runner failure handling
2. **Failure code assigned** — Each failure receives a standardized code (e.g., `PLANNING_ATTEMPT_BUDGET_EXCEEDED`)
3. **Failure context preserved** — Failed artifacts retained for debugging; not deleted

### Documentation Governance Rules

1. **Document-first principle** — No code change without corresponding documentation artifact
2. **Change impact tracking** — Significant changes require change impact documents
3. **Inventory reconciliation** — Module/component inventory updated after structural changes
4. **Stale guidance flagging** — Documentation sync identifies and flags outdated guidance

## Folder Structure

### Delivery Output Folders

```
docs/delivery/
├── 00_standards/           # Delivery governance standards (SOPs, status rules, templates)
├── 01_initiatives/         # Initiative intake documents (DRAFT_INIT, PRE_INIT, INIT)
├── 02_plans/               # Delivery plans (strategic and tactical)
├── 03_tasks/               # Task contracts (decomposed task definitions)
├── 04_implementation_plans/ # Implementation designs (detailed specs)
├── 05_reviews/             # Review artifacts (findings, refinements)
├── 06_validations/         # Validation results (quality gate outcomes)
├── 07_memory/              # Institutional knowledge (lessons learned, decisions)
└── 08_agents/              # Agent definitions (role specifications, contracts)
```

### Codebase Documentation Folders

```
docs/codebase/
├── 00_standards/           # Codebase documentation SOPs and status rules
├── 01_inventory/           # Module/component inventory (auto-generated)
├── 02_modules/             # Individual module documentation (auto-generated)
├── 03_components/          # Component-level documentation (manually curated)
└── 04_changes/             # Change impact documents (per-change tracking)
```

### System Documentation Folders

```
docs/system/
└── 00_governance/bootstrap/ # Master system docs (README, SYSTEM_CONTEXT, COMPONENT_ARCHITECTURE, etc.)
```

### Architecture Site Folders

```
docs/site/
├── stakeholders/           # Stakeholder-facing HTML views
├── developers/             # Developer-focused HTML views
├── operators/              # Operator runbooks and monitoring views
├── testers/                # Tester-oriented quality and validation views
└── users/                  # End-user functional guides
```

## Validation

### Pre-Execution Validation

Before each workflow step executes:

1. **Input artifact exists** — Required input files present on disk
2. **Prompt template resolves** — Placeholder substitution succeeds using `constants.py`
3. **Job state valid** — Current job.json schema version matches CURRENT_SCHEMA_VERSION
4. **Runtime context initialized** — Workflow bundle loaded from global runner home

### Post-Execution Validation

After each workflow step completes:

1. **Meta.json sidecar present** — Step output directory contains valid meta.json
2. **Artifact paths match schema** — Produced artifacts match expected keys from workflow definition
3. **Protected docs unchanged** — `_assert_protected_docs_unchanged()` passes for generated documents
4. **Status reported** — Coder result status is APPROVED or REJECTED with remark

### Workflow Completion Validation

When workflow reaches `completed` state:

1. **All required artifacts produced** — Expected artifact keys all have corresponding files on disk
2. **Final meta.json valid** — Last step's meta.json has schema_version "v2" and coder_result.status
3. **Job state terminal** — Job.json status is "completed", "failed", or "cancelled"
4. **Notification sent** — If notifications enabled, completion notification delivered

### Documentation Sync Validation

After `40_documentation_sync_v1`:

1. **Inventory accurate** — Module count matches actual Python files
2. **Module docs current** — All modules have up-to-date documentation
3. **Stale guidance flagged** — Outdated sections marked with staleness warnings
4. **Change impacts recorded** — Modifications tracked in change impact documents

### Architecture Site Validation

After `50_architecture_site_v1`:

1. **HTML generated** — All audience folders contain index.html
2. **Links valid** — Internal hyperlinks resolve correctly
3. **Content current** — Site reflects latest system documentation
4. **Theme applied** — CSS/styles consistent with selected theme

---

*Generated by workflow: 10_execution_scaffold_v1 | Step: generate_sop | Change: 10SCAFFOLD-20260708-8a4445fc*
