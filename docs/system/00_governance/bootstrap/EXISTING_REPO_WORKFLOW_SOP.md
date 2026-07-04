---
title: Existing Repository Workflow SOP
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: generate_sop
created: 2026-07-04
version: 1
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_sop`
> This file is workflow-generated and protected from manual edits.

# Existing Repository Workflow SOP

## Purpose

This SOP provides operators with the exact onboarding and reconciliation sequence for bringing a pre-existing repository under governed delivery. It applies when a repository already has an established codebase, existing documentation, and possibly prior governance conventions.

This SOP is NOT for greenfield repositories — those follow the standard `10_execution_scaffold_v1` flow directly. This SOP addresses the specific challenges of migration mode: coexisting with existing artifacts, reconciling existing documentation, and establishing governance without destroying prior work.

### Universal Ecosystem Baseline

Every governed repository — including this existing repository — MUST satisfy the **universal ecosystem baseline**. The universal baseline applies regardless of architecture profile or migration mode:

1. **Inventory Coverage**: Every source module, configuration file, and script MUST be represented in the codebase inventory or module documentation.
2. **Freshness Contract**: Documentation MUST be updated in the same delivery cycle as the code it describes.
3. **Status Tracking**: Every codebase document carries a status (`active`, `stale`, `superseded`, `archived`) governed by `CODEBASE_DOC_STATUS_RULES_v1.md`.
4. **Workflow Integration**: Codebase documentation is a deliverable in every task graph — `20_initiative_intake_v1` captures scope, `30_delivery_planning_v1` converts it into obligations, `31_task_execution_v1` executes and validates updates.
5. **Reconciliation**: `40_documentation_sync_v1` reconciles current code against active documentation and flags stale guidance.
6. **Architecture Communication**: `50_architecture_site_v1` publishes browsable HTML views after repository posture and docs are synchronized.
7. **Protection**: Workflow-generated documents are protected from manual edits via frontmatter and banner.
8. **No Deprecated Artifacts**: `07_master_prompts` is deprecated and MUST NOT appear in any governed repository.

### Repo-Selected Profile

Architecture profiles (DDD, EDA, microservices, event-sourced, CQRS, etc.) are **conditional profile choices** — they are NOT universal defaults. A repository adopts an architecture profile only when its architecture posture warrants it.

- The universal baseline applies first.
- Profile refinements layer on top of the baseline.
- A repository may adopt zero, one, or multiple architecture profiles.
- Profile adoption is documented in the project analysis and reflected in module documentation structure.

### Migration Mode

This repository operates in **migration mode** — it has a mature, populated governance corpus that the scaffold must coexist with, not overwrite. The sequence below is designed to respect existing artifacts while bringing the repository into alignment with the universal ecosystem baseline.

When repo standard is unclear, fall back to the universal baseline and use `40_documentation_sync_v1` to identify gaps and inconsistencies. Adopt the universal baseline incrementally and document adopted conventions for future reference.

### Conditional Standards

The following standards are conditional — they apply only when the repository's architecture profile warrants them:

| Standard | Condition | Notes |
|---|---|---|
| DDD (Domain-Driven Design) | Repository adopts bounded contexts, aggregates, domain events | Module docs may reflect domain boundaries |
| EDA (Event-Driven Architecture) | Repository uses event contracts and message flows | Event contracts warrant dedicated documentation |
| CQRS | Repository separates command and query models | Command/query separation documented per module |
| Event Sourcing | Repository uses event logs as primary store | Event schema documentation required |
| Microservices | Repository is decomposed into independent services | Service boundary documentation required |

These are NOT universal requirements. The universal baseline does not require any of these. They are refinements that specific architecture profiles may introduce.

## First-Time Setup

The first-time setup sequence establishes the governance foundation for an existing repository. It MUST be run before any governed delivery begins.

### First-Time Setup Sequence

```
00_master_docs_bootstrap_v1 → 10_execution_scaffold_v1
```

### Step 1: Run `00_master_docs_bootstrap_v1`

**Purpose**: Generate master system documentation and codebase baseline.

**Produces**:
- `docs/codebase/01_inventory/01_PROJECT_ANALYSIS.md` — comprehensive analysis
- System overview documents (SYSTEM_OVERVIEW, FUNCTIONAL_SPEC, SYSTEM_CONTEXT, COMPONENT_ARCHITECTURE, etc.)
- Initial codebase inventory

### Step 2: Run `10_execution_scaffold_v1`

**Purpose**: Generate the complete governance scaffold — SOPs, status rules, templates, agent contracts, folder map, and this existing-repo workflow SOP.

**Produces**:
- `docs/system/00_governance/bootstrap/WORKFLOW_SOP_v1.md` — delivery SOP
- `docs/system/00_governance/bootstrap/DELIVERY_STATUS_RULES_v1.md` — delivery status rules
- `docs/codebase/00_standards/CODEBASE_DOC_SOP_v1.md` — codebase documentation SOP
- `docs/codebase/00_standards/CODEBASE_DOC_STATUS_RULES_v1.md` — codebase documentation status rules
- `docs/system/00_governance/bootstrap/EXISTING_REPO_WORKFLOW_SOP.md` — this document
- Delivery template registry and templates
- Codebase template registry and templates
- Agent role contracts
- Folder map

### First-Time Setup Validation

After first-time setup:
1. Review generated artifacts for conflicts with existing conventions
2. Resolve any conflicts (the scaffold should coexist, not overwrite)
3. Validate that `docs/codebase/` and `docs/system/` trees are populated correctly
4. Confirm no `07_master_prompts` artifacts are present

## Normal Governed Delivery

Once first-time setup is complete, all subsequent deliveries follow the standard governed delivery sequence.

### Governed Delivery Sequence

```
20_initiative_intake_v1 → 30_delivery_planning_v1 → 31_task_execution_v1
```

### Step 1: Initiative Intake (`20_initiative_intake_v1`)

**Purpose**: Capture the initiative scope, including documentation scope and stale-guidance risk assessment.

**Key Migration Consideration**: For existing repositories, the initiative intake MUST account for existing documentation that may need updating. The stale-guidance risk assessment is critical — existing docs may already be partially stale.

**Produces**: Approved initiative document with documentation scope and stale-guidance risk captured.

### Step 2: Delivery Planning (`30_delivery_planning_v1`)

**Purpose**: Convert documentation scope into plan and task obligations. Generate delivery plan and task graph.

**Key Migration Consideration**: The plan must include tasks for reconciling existing documentation that will be affected by the initiative.

**Produces**: Approved delivery plan and validated task graph.

### Step 3: Task Execution (`31_task_execution_v1`)

**Purpose**: Execute tasks — implement code changes and update codebase documentation as part of task completion.

**Key Migration Consideration**: When updating existing module docs, respect the existing documentation style and conventions where they don't conflict with the universal baseline.

**Produces**: Completed tasks with updated code and documentation.

## Drift Reconciliation

When documentation drift is detected — or suspected — the drift reconciliation workflow is triggered.

### Drift Detection Triggers

- `validate_codebase_docs` reports stale documentation
- `scan_repo_codebase` finds undocumented modules
- An operator observes that system behavior or operations guidance is stale
- After a delivery that touched many modules
- Periodically (recommended: quarterly)

### Drift Reconciliation Workflow

**Workflow**: `40_documentation_sync_v1`

`40_documentation_sync_v1` is the **repo-wide reconciliation workflow**. It:

1. Scans the entire codebase documentation corpus
2. Compares documentation against current code state
3. Flags stale guidance — documents that no longer match code behavior
4. Generates a reconciliation report
5. Identifies which documents need repair, supersession, or archival

### Stale Guidance Response

When `40_documentation_sync_v1` identifies stale guidance:

1. **Assess severity**: Is the stale guidance actively misleading, or merely outdated?
2. **Repair or supersede**: Update the document to match current code, or supersede it if fundamentally outdated
3. **Refresh system docs**: When system behavior or operations guidance is stale, refresh the affected system documentation
4. **Record the reconciliation**: Create a change record in `docs/codebase/04_changes/`

### Drift Recovery Flow

```
40_documentation_sync_v1 → (if stale guidance found) → targeted repair tasks → validate_codebase_docs
```

## Architecture Communication

After the repository posture and documentation are synchronized, the architecture communication workflow publishes browsable views.

### Architecture Communication Workflow

**Workflow**: `50_architecture_site_v1`

`50_architecture_site_v1` is the **next-phase architecture communication workflow**. It:

1. Publishes browsable HTML architecture views
2. Generates views for different audiences:
   - **Stakeholders**: High-level architecture, business context, system boundaries
   - **Developers**: Module structure, API contracts, dependency graphs
   - **Operators**: Deployment topology, configuration, monitoring, runbooks
   - **Functional consumers**: Integration points, API documentation, usage guides
3. Uses Pandoc + Mermaid pipeline for rendering
4. Outputs to `docs/system/02_architecture_site/`

### When to Run

`50_architecture_site_v1` runs:
- After first-time setup is complete
- After drift reconciliation has synchronized docs
- Periodically (recommended: monthly or after significant deliveries)
- When requested by stakeholders

### Prerequisites

- Documentation must be synchronized (run `40_documentation_sync_v1` first)
- No stale guidance in published documents
- Architecture site pipeline (Pandoc + Mermaid) must be functional

### Governance Refresh Chain

```
40_documentation_sync_v1 → 50_architecture_site_v1
```

## Governance Refresh

When the governance scaffold itself needs updating — for example, when new workflow families are added or the SOP structure evolves — a governance refresh is performed.

### Governance Refresh Sequence

1. **Re-run `10_execution_scaffold_v1`** — regenerates protected documents
2. **Review changes** — compare regenerated documents with prior versions
3. **Resolve conflicts** — if existing conventions conflict with updated scaffold, resolve explicitly
4. **Validate** — confirm all protected documents are correctly regenerated
5. **Update this SOP** — if the existing-repo workflow sequence changes

### Full Refresh Chain

For a complete governance refresh:

```
00_master_docs_bootstrap_v1 → 10_execution_scaffold_v1 → 40_documentation_sync_v1 → 50_architecture_site_v1
```

### Governance Refresh vs. Drift Reconciliation

- **Governance refresh** updates the governance framework itself (SOPs, templates, agent contracts)
- **Drift reconciliation** updates the codebase documentation to match current code
- They are independent but complementary — a governance refresh may reveal drift that needs reconciliation

## Batch Files

### Bootstrap Batch Files

| Batch File | Purpose |
|---|---|
| `run-00_master_docs_bootstrap_v1.bat` | Run bootstrap locally |
| `submit-00_master_docs_bootstrap_v1.bat` | Submit to backend |
| `run-10_execution_scaffold_v1.bat` | Run scaffold locally |
| `submit-10_execution_scaffold_v1.bat` | Submit scaffold to backend |

### Operational Batch Files

| Batch File | Purpose |
|---|---|
| `run-20_initiative_intake_v1.bat` | Run initiative intake locally |
| `submit-20_initiative_intake_v1.bat` | Submit initiative to backend |
| `run-30_delivery_planning_v1.bat` | Run delivery planning locally |
| `submit-30_delivery_planning_v1.bat` | Submit planning to backend |
| `run-31_task_execution_v1.bat` | Run task execution locally |
| `submit-31_task_execution_v1.bat` | Submit execution to backend |
| `run-40_documentation_sync_v1.bat` | Run documentation sync locally |
| `submit-40_documentation_sync_v1.bat` | Submit sync to backend |
| `run-50_architecture_site_v1.bat` | Publish architecture site |
| `run-daemon.bat` | Start daemon mode |
| `run-approve-step.bat` | Force approve a step |
| `run-reset-step.bat` | Reset step for retry |
| `run-cleanup-generated-docs.bat` | Clean generated docs |

## Notes

### Migration Mode Considerations

1. **Coexistence, not replacement**: The scaffold coexists with existing documentation. It does not overwrite or delete existing artifacts unless they are directly superseded by workflow-generated replacements.

2. **Respect existing conventions**: Where existing documentation conventions don't conflict with the universal baseline, respect them. The scaffold adapts to the repository, not the other way around.

3. **Incremental adoption**: Not all governance features need to be adopted at once. Prioritize:
   - SOPs and status rules (foundational)
   - Delivery workflow (immediate governance)
   - Codebase documentation coverage (ongoing)
   - Architecture site (communication)

4. **Dual source of truth**: Be aware of the dual source-of-truth model — packaged bootstrap (`agent_runner_v2/bootstrap/workflows/default/`) vs. runtime bundle (`%USERPROFILE%\.ukbe-runner\workflows\...`). Never hand-edit the runtime bundle.

5. **Windows-first**: Paths and scripts assume Windows. The SOP does not assume POSIX tools unless explicitly wrapped.

6. **Zero runtime deps**: The runner is intentionally dependency-free. Adding dependencies requires explicit review.

7. **Protected documents**: Workflow-generated documents carry `managed_by: workflow-generated` and are protected from manual edits. Respect this protection.

8. **`07_master_prompts` is deprecated**: This artifact MUST NOT appear in any governed repository. If found during reconciliation, flag it for removal.

### Architecture Profile Notes

- **DDD (Domain-Driven Design)**: If the repository adopts DDD, the module documentation structure may be refined to reflect bounded contexts, aggregates, and domain events. This is a profile choice, not a universal requirement.
- **EDA (Event-Driven Architecture)**: If the repository adopts EDA, event contracts and message flows may warrant dedicated documentation sections. This is a profile choice.
- **Other profiles**: Microservices, CQRS, event-sourced, and similar architectures each have conditional documentation refinements. The universal baseline applies first; profile refinements layer on top.

### Workflow Dependencies

| Workflow | Requires | Produces |
|---|---|---|
| `10_execution_scaffold_v1` | `PROJECT_ANALYSIS` from `00_master_docs_bootstrap_v1` | Delivery scaffold |
| `20_initiative_intake_v1` | User directive or ticket | Approved initiative |
| `30_delivery_planning_v1` | `INIT_FILE` from `20_initiative_intake_v1` | Plan, task graph |
| `31_task_execution_v1` | `TASK_FILE` from `30_delivery_planning_v1` | Implementation |
| `40_documentation_sync_v1` | Current codebase state | Updated docs |
| `50_architecture_site_v1` | Synchronized system docs | HTML site |
