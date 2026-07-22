---
doc_type: "masterplan"
authority: "human-authored"
scan_policy: "exclude"
scan_reason: "design specification for Layer 3 AI-Driven SDLC workflows; exclude from operational scans"
---

# Layer 3 AI-Driven SDLC Specification

## Status

**Draft** -- This document defines the target specification for Layer 3 AI-Driven SDLC workflow bundles built on the `02_agent_runner_platform_v1` platform.

## Purpose

The Layer 3 AI-Driven SDLC workflows provide a complete software development lifecycle automation system that:

- Accepts initiatives/requirements as input
- Plans and designs solutions with human approval gates
- Generates detailed task specifications and implementation docs
- Executes tasks following implementation docs strictly
- Validates and reviews implementation quality
- Captures lessons learned and updates codebase

These workflows operationalize the AI-Driven SDLC methodology on the agent-runner-v2 platform, inheriting Layer 1 governance and Layer 2 platform contracts without redefining them.

## Design Objectives

The Layer 3 AI-Driven SDLC workflows must:

- Inherit Layer 1 governance and Layer 2 platform contracts from `~/.ukbe-runner/bundles/core/current/platform/`
- Provide end-to-end SDLC automation from initiative to deployment
- Include human approval gates at critical decision boundaries
- Generate immutable delivery documents for audit trail
- Support iterative refinement through review-refine loops
- Capture lessons learned and feed them back into future initiatives
- Be modular enough that individual phases can be used independently

## Workflow Family Overview

The AI-Driven SDLC consists of:
- **1 CLI command** for initial codebase setup
- **8 workflow bundles** organized by SDLC phase

### CLI Command (One-Time Setup)

| Command | Purpose |
|---------|---------|
| `ukbe-run-agent codebase-init` | Initial setup of `docs/repo/codebase/` structure |

This command is run once per repository to create the initial codebase documentation structure. It is not part of the SDLC workflow cycle.

### Workflow Bundles (SDLC Phases)

| # | Workflow | Phase | Purpose |
|---|----------|-------|---------|
| 00 | `sdlc_00_delivery_scaffold_v1` | Bootstrap | Generate master document templates and agent contracts for the SDLC delivery system |
| 00 | `sdlc_00_codebase_v1` | Maintenance | Periodic sync of repo code to codebase docs |
| 10 | `sdlc_10_requirement_v1` | Inception | Capture and structure requirements |
| 20 | `sdlc_20_planning_v1` | Inception | Design solution architecture and plan |
| 30 | `sdlc_30_backlog_v1` | Inception | Break down into backlog items |
| 40 | `sdlc_40_task_v1` | Construction | Generate task specifications |
| 50 | `sdlc_50_implementation_v1` | Construction | Generate implementation docs |
| 60 | `sdlc_60_execution_v1` | Construction | Execute tasks (with internal review/refine) |
| 70 | `sdlc_70_validation_v1` | Quality | System validation and regression tests |
| 80 | `sdlc_80_review_v1` | Finalization | Human review + initiative-specific codebase update + memory capture + close loop |

**Note:** `sdlc_00_codebase_v1` is a standalone sync workflow that can be run independently of the initiative flow. It is used to keep codebase docs in sync with the repository after manual changes or external updates.

## Workflow Implementation Reference

| Workflow | Input Artifacts | Output Artifacts | Promotion Pattern | Human Approval |
|----------|----------------|------------------|-------------------|----------------|
| `sdlc_00_delivery_scaffold_v1` | Master template designs (reference) | Templates (01_templates/), Agent contracts (02_agents/) | N/A (bootstrap scaffold) | Yes (after review) |
| `sdlc_00_codebase_v1` | Source code repository | Codebase docs, Sync log, Backup | N/A (no approval gates) | No (maintenance) |
| `sdlc_10_requirement_v1` | DRAFT_INIT_DOC, Codebase docs | INIT-DOC (approved) | Single artifact | Yes (after review) |
| `sdlc_20_planning_v1` | INIT-DOC (APPROVED), Codebase docs | REQ-DOC (approved) | Single artifact | Yes (after review) |
| `sdlc_30_backlog_v1` | REQ-DOC (APPROVED), Codebase docs | PLAN-DOC (approved) | Single artifact | Yes (after review) |
| `sdlc_40_task_v1` | PLAN-DOC (APPROVED), Codebase docs | BACKLOG-DOC (approved) | Single artifact | Yes (after review) |
| `sdlc_50_implementation_v1` | BACKLOG-DOC (APPROVED), Codebase docs | TASK-DOC (approved) | Single artifact | Yes (after review) |
| `sdlc_60_execution_v1` | TASK-DOC (APPROVED), Codebase docs | IMPL-DOC (approved) | Single artifact | Yes (after review) |
| `sdlc_70_validation_v1` | IMPL-DOC (APPROVED) | VALIDATE-DOC (approved), Code changes | Single artifact | Yes (after internal review) |
| `sdlc_80_review_v1` | VALIDATE-DOC (APPROVED), All delivery docs, Codebase docs | REV-DOC, MEM-DOC, CLOSE-DOC (approved) | Multi-artifact | Yes (after review of all docs) |

**Legend:**
- **Single artifact:** Changes frontmatter status from `draft` to `approved` on the same file
- **Two-file:** Creates new approved file from draft file, preserves both for audit trail
- **Multi-artifact:** Promotes multiple artifacts together after human approval
- **N/A:** Workflow operates outside approval-gate model (maintenance only)

## Dependency Chain

### Scaffold Prerequisite (One-Time Bootstrap)
```
sdlc_00_delivery_scaffold_v1 (runs once to generate templates + agent contracts)
    v
Produces universal scaffolding at:
  ~/.ukbe-runner/bundles/core/current/platform/agent_runner/sdlc/
    00_governance/   -- SDLC governance baseline
    01_templates/    -- Master document templates
    02_agents/       -- Agent contract definitions
```

### Initiative Flow (Approval-Gated)
```
Layer 1: 01_governance_foundation_v1
    v (inherits governance)
Layer 2: 02_agent_runner_platform_v1
    v (inherits platform contract)
Layer 3: AI-Driven SDLC workflows
    v
    sdlc_00_delivery_scaffold_v1 (prerequisite -- generates templates + agents)
        v (APPROVED)
    sdlc_10_requirement_v1 (DRAFT_INIT -> INIT-DOC)
        v (APPROVED)
    sdlc_20_planning_v1 (INIT-DOC -> REQ-DOC)
        v (APPROVED)
    sdlc_30_backlog_v1 (REQ-DOC -> PLAN-DOC)
        v (APPROVED)
    sdlc_40_task_v1 (PLAN-DOC -> BACKLOG-DOC)
        v (APPROVED)
    sdlc_50_implementation_v1 (BACKLOG-DOC -> TASK-DOC)
        v (APPROVED)
    sdlc_60_execution_v1 (TASK-DOC -> IMPL-DOC)
        v (APPROVED)
    sdlc_70_validation_v1 (IMPL-DOC -> VALIDATE-DOC)
        v (APPROVED)
    sdlc_80_review_v1 (VALIDATE-DOC -> REV + MEM + CLOSE)
```

### Maintenance Workflow (Standalone)
```
sdlc_00_codebase_v1 (runs independently, not part of initiative flow)
    v
Updates docs/repo/codebase/ (no approval gates)
```

**Prerequisite for Initiative Flow:** Codebase docs must exist at `docs/repo/codebase/` before starting sdlc_10. This can be satisfied by:
- **Initial setup:** Run `ukbe-run-agent codebase-init` (one-time CLI command)
- **Ongoing sync:** Run `sdlc_00_codebase_v1` workflow (periodic maintenance)

The initiative flow does not check whether sdlc_00 has been run; it only checks that codebase docs exist. sdlc_00 is a maintenance workflow that keeps codebase docs synchronized with the repository, not a gate in the initiative flow.

## Approval Gate Model

### Standard Model (Initiative Workflows)

Each workflow in the initiative flow (sdlc_10 through sdlc_80):
1. Checks that previous workflow's output has `lifecycle_status: "approved"` in frontmatter
2. Produces output with `lifecycle_status: "draft"`
3. Goes through internal review -> refine loops
4. Reaches `lifecycle_status: "approved"` via human approval
5. Next workflow can then start

**Lifecycle States:**
```
draft -> changes_requested -> draft (refine loop) -> approved
```

Note: "Waiting for human approval" is a transient state within the review step, not a separate lifecycle status.

### Maintenance Workflow Exception

**sdlc_00_codebase_v1** is a maintenance workflow that operates outside the approval-gate model:
- Does not require human approval
- Does not produce approved artifacts
- Runs independently of initiative flow
- Purpose is synchronization, not delivery

This exception applies only to maintenance workflows. All initiative workflows (sdlc_10 through sdlc_80) follow the standard approval model.

**Implementation:**
```yaml
preflight_status_check:
  artifact: "INPUT_ARTIFACT_KEY"
  required_status: "approved"

produced_document_status:
  artifact: "OUTPUT_ARTIFACT_KEY"
  required_status: "draft"
```

**Promotion Patterns:**

After review and human approval, workflows use one of these promotion patterns:

1. **Single Artifact Promotion** (most workflows):
   ```yaml
   promote_artifact:
     promotes: "OUTPUT_ARTIFACT_KEY"
   ```
   Changes frontmatter status from `draft` to `approved` on the same file.

2. **Two-File Promotion** (sdlc_10 only):
   ```yaml
   promote_to_requirement:
     source: "PRE_REQ_FILE"
     creates: "REQ_FILE"
     status: "approved"
   ```
   Creates a new approved file (REQ) from the draft file (PRE-REQ). Both files are preserved for audit trail.

3. **Multi-Artifact Promotion** (sdlc_80 only):
   ```yaml
   promote_all:
     promotes: ["REV_FILE", "MEM_FILE", "CLOSE_FILE"]
   ```
   Promotes multiple artifacts together after all have been reviewed and human approval has been granted.

## Delivery Folder Structure

All delivery documents are stored under `docs/repo/agent_runner/sdlc/delivery/` with the following structure:

```
docs/repo/agent_runner/sdlc/
+-- delivery/
|   +-- draft_initiatives/                # User-authored draft initiative files
|   |   +-- DRAFT-INIT-{date}-{seq}_{slug}.md
|   |
|   +-- initiatives/                      # Approved initiative documents (from sdlc_10)
|   |   +-- INIT-{date}-{seq}_{slug}.md
|   |
|   +-- requirements/                     # Approved requirement documents (from sdlc_20)
|   |   +-- REQ-{date}-{seq}_{slug}.md
|   |
|   +-- plans/                            # Approved plans (from sdlc_30)
|   |   +-- PLAN-{date}-{seq}_{slug}.md
|   |
|   +-- backlogs/                         # Approved backlogs (from sdlc_40)
|   |   +-- BACKLOG-{date}-{seq}_{slug}.md
|   |
|   +-- tasks/                            # Approved task specs (from sdlc_50)
|   |   +-- TASK-{date}-{seq}-{task}_{slug}.md
|   |
|   +-- implementations/                  # Approved implementation docs (from sdlc_60)
|   |   +-- IMPL-{date}-{seq}-{task}_{slug}.md
|   |
|   +-- validations/                      # Approved validation reports (from sdlc_70)
|   |   +-- VALID-{date}-{seq}_{slug}.md
|   |
|   +-- reviews/                          # Approved reviews + memory + closure (from sdlc_80)
|       +-- REV-{date}-{seq}_{slug}.md
|       +-- MEM-{date}-{seq}_{slug}.md
|       +-- CLOSE-{date}-{seq}_{slug}.md
|
+-- 00_governance/                        # SDLC governance baseline (universal)
|   +-- README.md
|   +-- SDLC_SOP.md
|   +-- SDLC_STATUS_RULES.md
|
+-- 01_templates/                         # Master document templates (universal)
|   +-- template_registry.md
|   +-- WORKFLOW_SOP_v1.md
|   +-- 01_DRAFT_INIT_template.md
|   +-- 02_INIT_template.md
|   +-- 03_REQ_template.md
|   +-- 04_PLAN_template.md
|   +-- 05_BACKLOG_template.md
|   +-- 06_TASK_template.md
|   +-- 07_IMPL_template.md
|   +-- 08_VALID_template.md
|   +-- 09_REV_template.md
|   +-- 10_MEM_template.md
|   +-- 11_CLOSE_template.md
|
+-- 02_agents/                            # Agent contract definitions (universal)
|   +-- AGENTS.md
|   +-- AGENT-planner.md
|   +-- AGENT-task-decomposer.md
|   +-- AGENT-implementation-planner.md
|   +-- AGENT-executor.md
|   +-- AGENT-reviewer.md
|   +-- AGENT-memory-manager.md
|   +-- DELIVERY_STATUS_RULES_v1.md
|
+-- archive/                              # Closed/archived initiatives
```

## Naming Convention

| Doc Type | Prefix | Format | Example |
|----------|--------|--------|---------|
| Draft Initiative | `DRAFT-INIT` | `DRAFT-INIT-{YYYYMMDD}-{NN}_{slug}.md` | `DRAFT-INIT-20260721-001_add-auth-feature.md` |
| Initiative | `INIT` | `INIT-{YYYYMMDD}-{NN}_{slug}.md` | `INIT-20260721-001_add-auth-feature.md` |
| Requirement | `REQ` | `REQ-{YYYYMMDD}-{NN}_{slug}.md` | `REQ-20260721-001_add-auth-feature.md` |
| Plan | `PLAN` | `PLAN-{YYYYMMDD}-{NN}_{slug}.md` | `PLAN-20260721-001_add-auth-feature.md` |
| Backlog | `BACKLOG` | `BACKLOG-{YYYYMMDD}-{NN}_{slug}.md` | `BACKLOG-20260721-001_add-auth-feature.md` |
| Task | `TASK` | `TASK-{YYYYMMDD}-{NN}-{TT}_{slug}.md` | `TASK-20260721-001-001_add-auth-feature.md` |
| Implementation | `IMPL` | `IMPL-{YYYYMMDD}-{NN}-{TT}_{slug}.md` | `IMPL-20260721-001-001_add-auth-feature.md` |
| Validation | `VALID` | `VALID-{YYYYMMDD}-{NN}_{slug}.md` | `VALID-20260721-001_add-auth-feature.md` |
| Review | `REV` | `REV-{YYYYMMDD}-{NN}_{slug}.md` | `REV-20260721-001_add-auth-feature.md` |
| Memory | `MEM` | `MEM-{YYYYMMDD}-{NN}_{slug}.md` | `MEM-20260721-001_add-auth-feature.md` |
| Close | `CLOSE` | `CLOSE-{YYYYMMDD}-{NN}_{slug}.md` | `CLOSE-20260721-001_add-auth-feature.md` |

**Key Points:**
- **Slug**: Short description of what the initiative is about (e.g., `add-auth-feature`, `fix-payment-bug`)
- **Same slug across all docs**: All docs for the same initiative share the same slug for easy tracing
- **Unique filenames**: Date + sequence + slug ensures global uniqueness
- **Task numbering**: `{NN}-{TT}` where `{NN}` is initiative sequence and `{TT}` is task number within initiative

## Document Audit Trail

### Delivery Documents (Immutable)
Once a delivery document has `lifecycle_status: "approved"` in its frontmatter:
- **Cannot be modified** by any workflow
- Provides **immutable audit trail**
- Any changes require a **new initiative** or formal amendment process
- Traceability from draft_init -> initiative -> requirement -> plan -> backlog -> task -> impl -> validation -> review

### Codebase Documents (Versioned)
Codebase documents (`docs/repo/codebase/`) are living documentation that can be updated:
- **Not immutable** - updated by sdlc_00 (periodic sync) and sdlc_80 (initiative-specific changes)
- **Audit trail via sync logs** - each sdlc_00 run produces `SYNC-{date}-{seq}.md` documenting changes
- **Git versioning** - all changes committed to git with descriptive messages
- **Optional backups** - sdlc_00 can create `backups/BACKUP-{date}/` before sync for rollback
- **Review before commit** - sync log reviewed for errors before changes are committed

## CLI Command: codebase-init

**Command:** `ukbe-run-agent codebase-init`

**Purpose:** One-time initial setup of `docs/repo/codebase/` structure for a repository.

**When to Run:**
- First time setting up SDLC workflows for a repository
- After migrating to a new repository
- If codebase docs are deleted or corrupted

**What It Does:**
- Creates `docs/repo/codebase/` directory structure
- Generates initial codebase inventory
- Generates initial module documentation
- Generates initial component documentation
- Generates initial project analysis

**Note:** This is a CLI command, not a workflow. It does not go through the approval gate model. After initial setup, use `sdlc_00_codebase_v1` workflow for periodic sync.

## Workflow Specifications

### sdlc_00_delivery_scaffold_v1

**Purpose:** Generate master document templates and agent contracts for the SDLC delivery system. This is a one-time bootstrap workflow that produces universal scaffolding shared across all repositories.

**Output Model (L2 Platform Pattern):**
- Staging: `docs/system/00_governance/platform/agent_runner/sdlc/runs/<job_id>/`
- Publish: `docs/system/00_governance/platform/agent_runner/sdlc/current/`
- Global: `~/.ukbe-runner/bundles/core/current/platform/agent_runner/sdlc/` (via `ukbe-run-agent init`)

**Inputs:**
- Master template designs (reference only — from `masterplan/delivery/00_templates/`)
- Agent contract designs (reference only — from `masterplan/delivery/08_agents/`)

**Outputs:**
- `00_governance/` — SDLC governance baseline (README.md, SDLC_SOP.md, SDLC_STATUS_RULES.md)
- `01_templates/` — Master document templates (template_registry.md, WORKFLOW_SOP_v1.md, 11 template files):
  - `01_DRAFT_INIT_template.md`, `02_INIT_template.md`, `03_REQ_template.md`
  - `04_PLAN_template.md`, `05_BACKLOG_template.md`, `06_TASK_template.md`
  - `07_IMPL_template.md`, `08_VALID_template.md`
  - `09_REV_template.md`, `10_MEM_template.md`, `11_CLOSE_template.md`
- `02_agents/` — Agent contract definitions (AGENTS.md, 6 agent contracts, DELIVERY_STATUS_RULES_v1.md)

**Steps:**
1. `generate_templates` (prompt) — Generate all 01_templates/ files
2. `generate_agent_contracts` (prompt) — Generate all 02_agents/ files
3. `review_scaffold` (prompt) — Review templates + agent contracts for consistency
4. `refine_scaffold` (prompt) — Refine based on review (if needed)
5. `stepCompletion` (action) — Finalize

**Human Approval:** Required after review step

**Note:** Once this workflow has run and the scaffold is published, the masterplan reference files (`masterplan/delivery/00_templates/` and `masterplan/delivery/08_agents/`) can be removed. The generated templates and agent contracts in the global path become the authoritative source.

---

### sdlc_00_codebase_v1

**Purpose:** Periodic full sync of repository code to codebase documentation

**Note:** Initial setup of `docs/repo/codebase/` is done via CLI command `ukbe-run-agent codebase-init`. This workflow is for ongoing maintenance sync.

**Audit Trail:**
- Produces sync log documenting all changes made during sync
- Git tracks version history automatically (all changes committed)
- Optional backup created before sync for rollback capability
- Review step catches errors before commit

**Inputs:**
- Source code repository
- Existing codebase documentation (must exist from initial setup)

**Outputs:**
- Updated codebase inventory
- Updated module documentation
- Updated component documentation
- Updated project analysis
- **Sync log** documenting what changed (SYNC-{date}-{seq}.md)
- **Backup** of previous codebase docs (optional, BACKUP-{date}/)

**Steps:**
1. `create_backup` (action) - Backup current codebase docs to `backups/BACKUP-{date}/` (optional)
2. `scan_codebase` (action) - Scan entire repository structure
3. `sync_codebase_docs` (prompt) - Sync all codebase docs to match current repo state
4. `generate_sync_log` (action) - Generate sync report documenting all changes
5. `review_sync_log` (prompt) - Review sync log for errors or unexpected changes
6. `refine_codebase_docs` (prompt) - Refine based on review (if needed)
7. `validate_codebase_docs` (action) - Validate documentation structure
8. `commit_changes` (action) - Commit all changes to git with message: `sync: codebase update {date}`
9. `stepCompletion` (action) - Finalize

**Human Approval:** Not required (maintenance operation), but review step catches issues before commit

**Artifact Paths:**
- `docs/repo/codebase/01_inventory/codebase_inventory.md`
- `docs/repo/codebase/02_modules/*.md`
- `docs/repo/codebase/03_components/*.md`
- `docs/repo/codebase/sync_logs/SYNC-{date}-{seq}.md`
- `docs/repo/codebase/backups/BACKUP-{date}/` (optional)

---

### sdlc_10_requirement_v1

**Purpose:** Generate an approved initiative document from a user-authored draft

**Inputs:**
- User draft initiative (DRAFT_INIT_DOC from `draft_initiatives/`)
- Codebase context (from docs/repo/codebase/)

**Outputs:**
- INIT-DOC document (approved, in `initiatives/`)

**Template:** `02_INIT_template.md`

**Steps:**
1. `generate_initiative` (prompt) - Generate structured initiative document from draft
2. `review_initiative` (prompt) - Review initiative document
3. `refine_initiative` (prompt) - Refine based on review (if needed)
4. `promote_initiative` (action) - Promote to approved
5. `stepCompletion` (action) - Finalize

**Human Approval:** Required after review step

**Artifact Paths:**
- `docs/repo/agent_runner/sdlc/delivery/draft_initiatives/DRAFT-INIT-{date}-{seq}_{slug}.md` (input, user-authored)
- `docs/repo/agent_runner/sdlc/delivery/initiatives/INIT-{date}-{seq}_{slug}.md` (approved output)

---

### sdlc_20_planning_v1

**Purpose:** Generate an approved requirement document from an approved initiative

**Inputs:**
- INIT-DOC (APPROVED from sdlc_10)
- Codebase context (from docs/repo/codebase/)

**Outputs:**
- REQ-DOC document (approved)

**Template:** `03_REQ_template.md`

**Steps:**
1. `generate_requirement` (prompt) - Generate requirement document from initiative
2. `review_requirement` (prompt) - Review requirement
3. `refine_requirement` (prompt) - Refine based on review (if needed)
4. `promote_requirement` (action) - Promote to approved
5. `stepCompletion` (action) - Finalize

**Human Approval:** Required after review step

**Artifact Paths:**
- `docs/repo/agent_runner/sdlc/delivery/requirements/REQ-{date}-{seq}_{slug}.md`

---

### sdlc_30_backlog_v1

**Purpose:** Generate a plan document from an approved requirement

**Inputs:**
- REQ-DOC (APPROVED from sdlc_20)
- Codebase context (from docs/repo/codebase/)

**Outputs:**
- PLAN-DOC document (approved)

**Template:** `04_PLAN_template.md`

**Steps:**
1. `generate_plan` (prompt) - Generate plan document from requirement
2. `review_plan` (prompt) - Review plan
3. `refine_plan` (prompt) - Refine based on review (if needed)
4. `promote_plan` (action) - Promote to approved
5. `stepCompletion` (action) - Finalize

**Human Approval:** Required after review step

**Artifact Paths:**
- `docs/repo/agent_runner/sdlc/delivery/plans/PLAN-{date}-{seq}_{slug}.md`

---

### sdlc_40_task_v1

**Purpose:** Generate a backlog document from an approved plan

**Inputs:**
- PLAN-DOC (APPROVED from sdlc_30)
- Codebase context (from docs/repo/codebase/)

**Outputs:**
- BACKLOG-DOC document (approved)

**Template:** `05_BACKLOG_template.md`

**Steps:**
1. `generate_backlog` (prompt) - Generate backlog from plan
2. `review_backlog` (prompt) - Review backlog
3. `refine_backlog` (prompt) - Refine based on review (if needed)
4. `promote_backlog` (action) - Promote to approved
5. `stepCompletion` (action) - Finalize

**Human Approval:** Required after review step

**Artifact Paths:**
- `docs/repo/agent_runner/sdlc/delivery/backlogs/BACKLOG-{date}-{seq}_{slug}.md`

---

### sdlc_50_implementation_v1

**Purpose:** Generate task specifications from an approved backlog

**Inputs:**
- BACKLOG-DOC (APPROVED from sdlc_40)
- Codebase context (from docs/repo/codebase/)

**Outputs:**
- TASK-DOC document (approved)

**Template:** `06_TASK_template.md`

**Steps:**
1. `generate_task` (prompt) - Generate task spec from backlog
2. `review_task` (prompt) - Review task spec
3. `refine_task` (prompt) - Refine based on review (if needed)
4. `promote_task` (action) - Promote to approved
5. `stepCompletion` (action) - Finalize

**Human Approval:** Required after review step

**Artifact Paths:**
- `docs/repo/agent_runner/sdlc/delivery/tasks/TASK-{date}-{seq}-{TT}_{slug}.md`

---

### sdlc_60_execution_v1

**Purpose:** Generate implementation docs from approved task specs

**Inputs:**
- TASK-DOC (APPROVED from sdlc_50)
- Codebase context (from docs/repo/codebase/)

**Outputs:**
- IMPL-DOC document (approved)

**Template:** `07_IMPL_template.md`

**Steps:**
1. `generate_implementation` (prompt) - Generate implementation doc from task
2. `review_implementation` (prompt) - Review implementation doc
3. `refine_implementation` (prompt) - Refine based on review (if needed)
4. `promote_implementation` (action) - Promote to approved
5. `stepCompletion` (action) - Finalize

**Human Approval:** Required after review step

**Artifact Paths:**
- `docs/repo/agent_runner/sdlc/delivery/implementations/IMPL-{date}-{seq}-{TT}_{slug}.md`

---

### sdlc_70_validation_v1

**Purpose:** Execute tasks and validate following implementation docs

**Inputs:**
- IMPL-DOC (APPROVED from sdlc_60)

**Outputs:**
- VALIDATE-DOC document (approved)
- Actual code changes in source repository

**Template:** `08_VALID_template.md`

**Steps:**
1. `execute_task` (prompt) - Execute task following IMPL-DOC
2. `internal_review` (prompt) - Review if execution followed IMPL-DOC
3. `refine_execution` (prompt) - Re-execute based on review (if needed)
4. `promote_execution` (action) - Promote to approved
5. `stepCompletion` (action) - Finalize

**Human Approval:** Required after internal review passes

**Artifact Paths:**
- `docs/repo/agent_runner/sdlc/delivery/validations/VALID-{date}-{seq}_{slug}.md`
- Actual code changes in source repository

---

### sdlc_80_review_v1

**Purpose:** Final review, memory capture, and initiative closure

**Inputs:**
- VALIDATE-DOC (APPROVED from sdlc_70)
- All previous delivery documents
- Codebase context (from docs/repo/codebase/)

**Outputs:**
- REV-DOC document (approved, final review)
- MEM-DOC document (approved, lessons learned)
- CLOSE-DOC document (approved, initiative closure)

**Templates:** `09_REV_template.md`, `10_MEM_template.md`, `11_CLOSE_template.md`

**Steps:**
1. `generate_review` (prompt) - Generate REV, MEM, and CLOSE documents
2. `review_all` (prompt) - Human review of all documents
3. `refine_documents` (prompt) - Refine based on review feedback (if rejected)
   - **Loop returns to:** Step 2 (review_all) if any document was refined
4. `promote_all` (action) - Promote REV, MEM, CLOSE to approved
5. `stepCompletion` (action) - Finalize

**Human Approval:** Required after step 2. If refinement occurs at step 3, workflow loops back to step 2.

**Artifact Paths:**
- `docs/repo/agent_runner/sdlc/delivery/reviews/REV-{date}-{seq}_{slug}.md`
- `docs/repo/agent_runner/sdlc/delivery/reviews/MEM-{date}-{seq}_{slug}.md`
- `docs/repo/agent_runner/sdlc/delivery/reviews/CLOSE-{date}-{seq}_{slug}.md`

---

## Cross-Cutting Concerns

### Layer 2 References

All SDLC workflows must reference Layer 2 guardrails and SOP from:
`~/.ukbe-runner/bundles/core/current/platform/`

Key references:
- `BUNDLE_AUTHORING_CONTRACT.md` - Bundle contract requirements
- `SHARED_SERVICES.md` - Available runtime services
- `VALIDATION_CONTRACT.md` - Validation patterns
- `METADATA_CONTRACT.md` - Metadata requirements
- `RUNTIME_MODEL.md` - Execution model

### Error Handling

Each workflow must handle:
- Validation failures (refine loops with max iterations)
- Review rejections (refine based on feedback)
- Human intervention requests (pause for human input)
- Coder failures (retry with different coder or escalate)

### Notification Model

Each workflow supports:
- Step completion notifications (optional per-step)
- Workflow completion notifications (always on)
- Human approval request notifications
- Failure/escalation notifications

### Coder Integration

Each prompt-driven step must:
- Specify role policy (architect_standard, reviewer_standard, etc.)
- Support multiple coder backends (opencode, qwen, claude, codex)
- Handle coder-specific quirks via adapters
- Write meta.json sidecar for result communication

### Metadata Compliance

All generated artifacts must:
- Include YAML frontmatter with required fields
- Use correct doc_type, authority, layer, platform values
- Follow ASCII-only encoding rule
- Use plain text section headings (no backticks/formatting)

### Code Documentation Standards

All generated code must:
- Include docstrings for all modules, classes, and functions
- Use Python standard docstring format (triple quotes)
- Document purpose, parameters, return values, and exceptions
- Follow PEP 257 docstring conventions
- Be ASCII-only (no Unicode characters in docstrings)

**Example:**
```python
def my_function(param1: str, param2: int) -> bool:
    """Brief description of what the function does.
    
    Args:
        param1: Description of param1.
        param2: Description of param2.
    
    Returns:
        Description of return value.
    
    Raises:
        ValueError: When param1 is invalid.
    """
    pass
```

## Migration Path

The legacy `00_repo_master_docs_bootstrap_v1` workflow provides a reference implementation for:
- Codebase scanning and inventory generation
- Documentation validation patterns
- Review-refine loops
- Bootstrap finalization

Key patterns to preserve:
- `scan_repo_codebase` action -> becomes shared service
- `validate_system_docs` action -> pattern in VALIDATION_CONTRACT
- Review-refine loop structure -> standard pattern for all workflows
- ASCII-only validation -> universal rule (already implemented)

## Template-to-Workflow Mapping

| Template | Produces | SDLC Workflow |
|---|---|---|
| `01_DRAFT_INIT_template.md` | DRAFT-INIT-DOC | (user-authored, input to sdlc_10) |
| `02_INIT_template.md` | INIT-DOC | sdlc_10 |
| `03_REQ_template.md` | REQ-DOC | sdlc_20 |
| `04_PLAN_template.md` | PLAN-DOC | sdlc_30 |
| `05_BACKLOG_template.md` | BACKLOG-DOC | sdlc_40 |
| `06_TASK_template.md` | TASK-DOC | sdlc_50 |
| `07_IMPL_template.md` | IMPL-DOC | sdlc_60 |
| `08_VALID_template.md` | VALIDATE-DOC | sdlc_70 |
| `09_REV_template.md` | REV-DOC | sdlc_80 |
| `10_MEM_template.md` | MEM-DOC | sdlc_80 |
| `11_CLOSE_template.md` | CLOSE-DOC | sdlc_80 |

## Agent-to-Workflow Mapping

| Agent Contract | SDLC Workflow | Role |
|---|---|---|
| (user input) | sdlc_10 | Initiative author |
| AGENT-planner.md | sdlc_20 | Solution architect |
| AGENT-task-decomposer.md | sdlc_30 | Backlog decomposer |
| AGENT-task-decomposer.md | sdlc_40 | Task specifier |
| AGENT-implementation-planner.md | sdlc_50 | Implementation planner |
| AGENT-executor.md | sdlc_60 | Code executor |
| AGENT-reviewer.md | sdlc_70 | Validator |
| AGENT-reviewer.md + AGENT-memory-manager.md | sdlc_80 | Reviewer + memory capture |

## Implementation Sequence

1. **Phase 0:** Create `sdlc_00_delivery_scaffold_v1` (bootstrap templates + agents)
2. **Phase 1:** Create `sdlc_00_codebase_v1` (foundation)
3. **Phase 2:** Create `sdlc_10_requirement_v1` (inception start)
4. **Phase 3:** Create `sdlc_20_planning_v1` and `sdlc_30_backlog_v1` (inception complete)
5. **Phase 4:** Create `sdlc_40_task_v1` and `sdlc_50_implementation_v1` (construction planning)
6. **Phase 5:** Create `sdlc_60_execution_v1` (construction execution)
7. **Phase 6:** Create `sdlc_70_validation_v1` (quality gates)
8. **Phase 7:** Create `sdlc_80_review_v1` (finalization)

## Success Criteria

The AI-Driven SDLC workflows are successful when:

1. **End-to-end automation:** Can take an initiative from requirements to deployment
2. **Human-in-the-loop:** Approval gates work correctly at critical boundaries
3. **Immutable audit trail:** Delivery documents cannot be modified after approval
4. **Quality assurance:** Validation catches issues before deployment
5. **Learning loop:** Lessons learned feed back into future initiatives
6. **Platform compliance:** All workflows follow Layer 2 platform contract
7. **Governance compliance:** All workflows follow Layer 1 governance rules

## References

- Layer Architecture Masterplan: `masterplan/LAYER_ARCHITECTURE_MASTERPLAN.md`
- Layer 1 Governance Specification: `masterplan/LAYER1_GOVERNANCE_SPECIFICATION.md`
- Layer 2 Platform Core Specification: `masterplan/LAYER2_PLATFORM_CORE_SPECIFICATION.md`
- Legacy workflow reference: `masterplan/00_repo_master_docs_bootstrap_v1/`
- Legacy workflow prompts: `masterplan/old legacy workflow/`
