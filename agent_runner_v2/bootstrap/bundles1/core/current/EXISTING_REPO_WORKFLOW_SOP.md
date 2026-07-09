---
template_id: "SYS-00-ERW"
title: "Existing Repository Workflow Standard Operating Procedure"
status: "active"
version: "1.0"
generated: "2026-07-09T10:30:00+08:00"
workflow: "10_execution_scaffold_v1"
step: "generate_sop"
change_id: "10SCAFFOLD-20260708-8a4445fc"
managed_by: workflow-generated
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_sop`
> This file is workflow-generated and protected from manual edits.

# Existing Repository Workflow Standard Operating Procedure

## Purpose

This SOP defines the exact onboarding and reconciliation sequence for applying agent-runner-v2 governance to a pre-existing repository. It provides operators with a clear, repeatable procedure for:

1. **First-time setup** — Bootstrapping an existing repository with delivery scaffold and documentation governance
2. **Normal governed delivery** — Executing standard initiative-to-completion workflows
3. **Drift reconciliation** — Recovering synchronization when code changes occur outside workflow SOP
4. **Governance refresh** — Periodic maintenance of system documentation and architecture site

This SOP applies to any repository being brought under agent-runner-v2 governance, including the agent-runner-v2 repository itself (self-hosting).

## First-Time Setup

When onboarding an existing repository to agent-runner-v2 governance, execute these steps in order:

### Step 1: Initialize Runner Home

```bash
ukbe-run-agent init
```

**Purpose:** Seeds global runner home under `%USERPROFILE%\.ukbe-runner`  
**Creates:**
- `%USERPROFILE%\.ukbe-runner\config.json` — Runtime configuration
- `%USERPROFILE%\.ukbe-runner\jobs\` — Job state directory
- `%USERPROFILE%\.ukbe-runner\workflows\example\` — Example workflow bundle
- `%USERPROFILE%\.ukbe-runner\logs\` — Execution logs

**Validation:**
- Verify `config.json` exists and contains valid JSON
- Verify all directories created
- Verify workflow bundles seeded from bootstrap source

### Step 2: Bootstrap Master System Documentation

```bash
ukbe-run-agent run 00_master_docs_bootstrap_v1 --project-root <repo_path>
```

**Purpose:** Generates complete master system documentation set from repository analysis  
**Outputs:**
- `docs/system/00_governance/bootstrap/SYSTEM_CONTEXT.md`
- `docs/system/00_governance/bootstrap/COMPONENT_ARCHITECTURE.md`
- `docs/system/00_governance/bootstrap/FUNCTIONAL_SPEC.md`
- `docs/system/00_governance/bootstrap/NON_FUNCTIONAL_REQUIREMENTS.md`
- `docs/system/00_governance/bootstrap/DEVELOPER_GUIDE.md`
- `docs/system/00_governance/bootstrap/RUNBOOK.md`
- `docs/system/00_governance/bootstrap/DECISION_LOG.md`
- `docs/system/00_governance/bootstrap/SYSTEM_FILE_STRUCTURE.md`
- `docs/system/00_governance/bootstrap/SYSTEM_OVERVIEW.md`
- `docs/system/00_governance/bootstrap/BUSINESS_CAPABILITIES.md`
- `docs/system/00_governance/bootstrap/DOCUMENTATION_STANDARD.md`
- `docs/system/00_governance/bootstrap/README.md`
- Plus bundle taxonomy, migration plan, and existing repo workflow SOP (this document)

**Agent:** Generic Coder (bootstrap mode)  
**Duration:** 5-15 minutes depending on repository size  
**Validation:**
- All 18 master documents generated in `docs/system/00_governance/bootstrap/`
- Documents contain repository-specific content (not boilerplate)
- Meta.json sidecars present for each generation step

### Step 3: Execute Delivery Scaffold

```bash
ukbe-run-agent run 10_execution_scaffold_v1 --project-root <repo_path>
```

**Purpose:** Generates delivery governance infrastructure (SOPs, templates, agents, status rules)  
**Workflow Steps:**
1. `project_analysis` — Auto-discovers project context, analyzes structure and tech stack
2. `generate_sop` — Generates delivery SOP, delivery status rules, codebase doc SOP, codebase doc status rules, existing repo workflow SOP
3. `generate_templates` — Generates 9 delivery templates and 6 codebase documentation templates
4. `generate_agents` — Generates 7 agent contract files (AGENTS.md + 6 individual AGENT-*.md)
5. `finalize_scaffold` — Validates scaffold completeness, creates folder structure

**Outputs:**
- `docs/system/00_governance/bootstrap/WORKFLOW_SOP_v1.md` — Delivery standard operating procedure
- `docs/system/00_governance/bootstrap/DELIVERY_STATUS_RULES.md` — Delivery status transition rules
- `docs/codebase/00_standards/CODEBASE_DOC_SOP_v1.md` — Codebase documentation SOP
- `docs/codebase/00_standards/CODEBASE_DOC_STATUS_RULES_v1.md` — Codebase doc status rules
- `docs/system/00_governance/bootstrap/EXISTING_REPO_WORKFLOW_SOP.md` — This document
- Delivery templates in `docs/delivery/00_standards/templates/delivery/`
- Codebase templates in `docs/system/00_governance/bootstrap/templates/codebase/`
- Agent contracts in `docs/delivery/08_agents/`
- Folder map and inventory templates

**Agents:** Project Analyst → SOP Architect → Template Generator → Agent Contract Writer  
**Duration:** 15-30 minutes  
**Validation:**
- All five SOP/status rule documents generated
- All 15 templates generated (9 delivery + 6 codebase)
- All 7 agent contracts generated
- Folder structure created (`docs/delivery/`, `docs/codebase/`)
- Meta.json sidecar at job path confirms APPROVED status

### Step 4: Scan Repository Codebase

```bash
ukbe-run-agent run 40_documentation_sync_v1 --project-root <repo_path>
```

**Purpose:** Generates initial codebase documentation inventory and module docs  
**Workflow Steps:**
1. `scan_repo_codebase` — Walks repository tree, extracts module information
2. `generate_module_docs` — Creates markdown per Python module
3. `update_inventory` — Generates codebase inventory with accurate counts
4. `flag_stale_guidance` — Identifies any outdated sections (none on first run)
5. `record_change_impacts` — Documents initial baseline as change impact

**Outputs:**
- `docs/codebase/01_inventory/codebase_inventory.md` — Complete module/component listing
- `docs/codebase/01_inventory/INTEGRATION_MAP.md` — Inter-module dependencies
- `docs/codebase/01_inventory/FAILURE_MODES.md` — Known failure scenarios (initial baseline)
- `docs/codebase/01_inventory/ARCHITECTURE_FLOW.md` — Data/control flow diagrams
- `docs/codebase/02_modules/*.md` — One module doc per Python file (67+ files for agent-runner-v2)
- `docs/codebase/03_components/*.md` — Component-level documentation (6 files)
- `docs/codebase/04_changes/00DOC-<date>-<hash>-baseline.md` — Baseline change impact document

**Agent:** Documentation Sync Agent  
**Duration:** 10-20 minutes depending on repository size  
**Validation:**
- Module doc count matches actual `.py` file count (excluding exclusions)
- Inventory accurately lists all modules and components
- Component docs cover major packages (actions, workflows, tests, scripts, config, governance)
- Change impact baseline document created

### Step 5: Publish Architecture Site (Optional)

```bash
ukbe-run-agent run 50_architecture_site_v1 --project-root <repo_path>
```

**Purpose:** Generates browsable HTML architecture views for multiple audiences  
**Workflow Steps:**
1. `read_system_docs` — Loads current system documentation set
2. `read_codebase_docs` — Loads codebase inventory and module docs
3. `generate_html` — Renders markdown to HTML with theme styling
4. `create_audience_views` — Generates stakeholder, developer, operator, tester, user views
5. `validate_links` — Verifies internal hyperlinks resolve correctly
6. `publish_site` — Writes HTML to `docs/site/`

**Outputs:**
- `docs/site/stakeholders/index.html` — Stakeholder-facing overview
- `docs/site/developers/index.html` — Developer-focused technical docs
- `docs/site/operators/index.html` — Operator runbooks and monitoring
- `docs/site/testers/index.html` — Tester-oriented quality and validation
- `docs/site/users/index.html` — End-user functional guides
- CSS/theme files in `docs/site/assets/`

**Agent:** Architecture Publisher  
**Duration:** 5-10 minutes  
**Validation:**
- All audience folders contain `index.html`
- Internal links resolve correctly
- Site reflects latest system and codebase documentation
- Theme styling applied consistently

### First-Time Setup Completion Checklist

After completing all five steps, verify:

- [ ] Runner home initialized (`%USERPROFILE%\.ukbe-runner\` exists with config, jobs, workflows, logs)
- [ ] Master system docs generated (18 files in `docs/system/00_governance/bootstrap/`)
- [ ] Delivery scaffold complete (5 SOP/status rule docs, 15 templates, 7 agent contracts)
- [ ] Codebase documentation generated (67+ module docs, 6 component docs, 4 inventory files)
- [ ] Architecture site published (optional; 5 audience views in `docs/site/`)
- [ ] All meta.json sidecars show APPROVED status
- [ ] No validation failures in execution logs

## Normal Governed Delivery

Once repository is onboarded, normal delivery follows this sequence:

### Phase 1: Initiative Intake

```bash
ukbe-run-agent run 20_initiative_intake_v1 --project-root <repo_path> --draft-init <path_to_draft>
```

**Purpose:** Capture requirement and documentation scope for new initiative  
**Input:** `DRAFT_INIT_FILE` (user-provided or created via draft-initiative-pre-initskill)  
**Outputs:**
- `docs/delivery/01_initiatives/PRE_INIT_<date>_<slug>.md`
- `docs/delivery/01_initiatives/INIT_<date>_<slug>.md`

**Agent:** Initiative Analyst  
**Review Loop:** Yes (max_rejects = 2)  
**Documentation Scope:** Identifies affected modules, stale-guidance risk, acceptance criteria

**When to Use:**
- New feature development
- Major refactoring initiatives
- Bug fix triage (use `21_bug_fix_intake_v1` for bugs)
- Documentation improvement projects

### Phase 2: Delivery Planning

```bash
ukbe-run-agent run 30_delivery_planning_v1 --project-root <repo_path> --init-file <path_to_init_doc>
```

**Purpose:** Convert documentation scope into plan/task obligations  
**Input:** `INIT_FILE` from Phase 1  
**Outputs:**
- `docs/delivery/02_plans/PLAN_<date>_<slug>.md`
- `docs/delivery/03_tasks/TASK_GRAPH_<date>_<slug>.md`
- `docs/delivery/03_tasks/TASK_<date>_<slug>_*.md` (one per task)

**Agents:** Planner → Task Decomposer  
**Review Loop:** Yes (plan review, task graph validation)  
**Documentation Obligations:** Maps plan items to required documentation updates

**When to Use:**
- After initiative approved
- Before any implementation work begins
- When initiative scope needs decomposition into executable tasks

### Phase 3: Task Execution

```bash
ukbe-run-agent run 31_task_execution_v1 --project-root <repo_path> --task-file <path_to_task_doc>
```

**Purpose:** Execute code and documentation updates together  
**Input:** `TASK_FILE` from Phase 2  
**Outputs:**
- Modified source files (code changes)
- `docs/delivery/04_implementation_plans/IMPL_<date>_<slug>.md`
- `docs/delivery/05_reviews/REVIEW_<date>_<slug>.md`
- `docs/delivery/06_validations/VALIDATION_<date>_<slug>.md`
- Updated module/component docs (if task includes doc updates)

**Agents:** Implementation Planner → Executor → Reviewer  
**Review Loop:** Yes (implementation review with max_rejects = 3)  
**Documentation Updates:** Executes documentation changes as part of task completion

**When to Use:**
- For each task in task graph
- When implementation work ready to begin
- When code and docs must be updated together

### Phase 4: Documentation Sync (As Needed)

```bash
ukbe-run-agent run 40_documentation_sync_v1 --project-root <repo_path>
```

**Purpose:** Reconcile codebase inventory and stale guidance after drift  
**Trigger:**
- Code changes made outside workflow SOP (emergency fixes, hotfixes)
- Periodic maintenance (recommended weekly)
- After structural changes (package reorganization, new modules)

**Outputs:**
- Updated module docs in `docs/codebase/02_modules/`
- Updated inventory in `docs/codebase/01_inventory/`
- Change impact docs in `docs/codebase/04_changes/`
- Staleness flags on outdated sections

**Agent:** Documentation Sync Agent  
**Review Loop:** No (automated reconciliation with validation)

**When to Use:**
- After emergency fixes bypassing normal workflow
- Weekly maintenance window
- After adding/removing modules or packages
- When staleness flags detected

### Phase 5: Architecture Site Publishing (Optional)

```bash
ukbe-run-agent run 50_architecture_site_v1 --project-root <repo_path>
```

**Purpose:** Publish updated browsable HTML architecture views  
**Trigger:**
- System documentation updated via `00_master_docs_bootstrap_v1`
- Significant architectural changes
- Quarterly refresh schedule

**Outputs:**
- Updated HTML site in `docs/site/`

**Agent:** Architecture Publisher  
**Review Loop:** No (publishing is deterministic)

**When to Use:**
- After major system doc updates
- Quarterly maintenance schedule
- Before stakeholder reviews

### Normal Delivery Completion Criteria

A delivery cycle is complete when:

1. All tasks in task graph executed and validated
2. All documentation updates applied and verified
3. Change impact documents created for significant changes
4. Inventory reconciled if structural changes occurred
5. Architecture site refreshed (if applicable)
6. Final validation passed with APPROVED status

## Drift Reconciliation

When code changes occur outside normal workflow SOP, use drift reconciliation:

### Drift Detection

Drift occurs when:

1. **Direct code edits** — Developer modifies source files without running `31_task_execution_v1`
2. **Emergency fixes** — Hotfixes applied without initiative/planning phases
3. **Structural changes** — Packages/modules added/removed without documentation sync
4. **Configuration updates** — Config files modified without corresponding plan item
5. **Dependency changes** — New dependencies added without documentation update

### Drift Severity Classification

| Severity | Indicators | Response Required |
|----------|-----------|-------------------|
| **Critical** | API-breaking changes, removed modules, deleted packages | Immediate `40_documentation_sync_v1` + change impact docs |
| **High** | New modules added, function signature changes, dependency updates | `40_documentation_sync_v1` within 1 week |
| **Medium** | Minor code refactoring, comment updates, internal logic changes | `40_documentation_sync_v1` within 2 weeks |
| **Low** | Whitespace, formatting, variable renaming | Next periodic sync (monthly) |

### Drift Reconciliation Procedure

#### Step 1: Assess Drift Scope

```bash
git diff HEAD~<n> --name-only
```

Identify changed files and classify by severity using drift severity table above.

#### Step 2: Create Change Impact Documents

For each significant change (critical/high severity):

1. Create change impact doc in `docs/codebase/04_changes/`
2. Document what changed, why, and impact
3. List affected module docs requiring updates
4. Flag whether `40_documentation_sync_v1` should be triggered

**Naming:** `00DOC-<date>-<hash>-<description>.md`

#### Step 3: Execute Documentation Sync

```bash
ukbe-run-agent run 40_documentation_sync_v1 --project-root <repo_path>
```

**Purpose:** Reconcile current code against active documentation and flag stale guidance  
**Process:**
1. Scans repository for all Python modules
2. Compares existing docs against current code
3. Updates module docs to match current state
4. Updates inventory with accurate counts
5. Flags stale guidance sections
6. Generates change impacts for significant updates

**Outputs:**
- Updated module docs matching current code
- Updated inventory with accurate module/component counts
- Change impact docs for significant updates
- Staleness flags on outdated sections

#### Step 4: Refresh System Docs (If Needed)

If drift affected system architecture, operations, or developer guidance:

```bash
ukbe-run-agent run 00_master_docs_bootstrap_v1 --project-root <repo_path>
```

**Purpose:** Regenerate master system documentation to reflect current repository state  
**Trigger:**
- Architectural changes (new components, removed subsystems)
- Operations guidance outdated (runbook, developer guide)
- Functional spec no longer matches implementation
- Security boundaries changed

**Outputs:**
- Updated system docs in `docs/system/00_governance/bootstrap/`

#### Step 5: Validate Reconciliation

After sync completes:

1. Verify module doc count matches actual `.py` file count
2. Confirm inventory accurately lists all modules and components
3. Check that staleness flags resolved
4. Validate change impact docs created for significant changes
5. Ensure meta.json sidecars show APPROVED status

### Drift Reconciliation Completion Criteria

Drift reconciliation is complete when:

- [ ] All changed files identified and classified by severity
- [ ] Change impact docs created for critical/high severity changes
- [ ] `40_documentation_sync_v1` executed successfully
- [ ] Module docs match current code (no staleness flags)
- [ ] Inventory accurate (module/component counts match disk)
- [ ] System docs refreshed if architecture/operations affected
- [ ] All meta.json sidecars show APPROVED status

## Governance Refresh

Periodic governance refresh maintains documentation health:

### Monthly Refresh Checklist

Execute monthly:

1. **Staleness check** — Run `40_documentation_sync_v1` to identify stale docs
   ```bash
   ukbe-run-agent run 40_documentation_sync_v1 --project-root <repo_path>
   ```

2. **Inventory reconciliation** — Verify module/component counts match disk
   - Included in `40_documentation_sync_v1` scan
   - Manual verification: count `.py` files vs inventory listing

3. **Failure mode review** — Update `FAILURE_MODES.md` with recent incidents
   - Review bug reports, test failures, incident logs from past month
   - Add new failure patterns via task execution or change impact doc

4. **Change impact cleanup** — Archive change impacts >90 days old
   - Move old change impacts to `docs/codebase/04_changes/archive/`
   - Update archive frontmatter with archival metadata

### Quarterly Refresh Checklist

Execute quarterly:

1. **Integration map validation** — Verify dependency arrows still accurate
   - Manual review of `INTEGRATION_MAP.md`
   - Update via task execution if dependencies changed

2. **Architecture flow update** — Refresh flow diagrams if architecture evolved
   - Review `ARCHITECTURE_FLOW.md` against current architecture
   - Update via task execution if flows changed

3. **Component doc review** — Validate component docs reflect current structure
   - Review all 6 component docs in `docs/codebase/03_components/`
   - Update via task execution if structural drift detected

4. **Architecture site refresh** — Republish HTML site with latest docs
   ```bash
   ukbe-run-agent run 50_architecture_site_v1 --project-root <repo_path>
   ```

### Annual Refresh Checklist

Execute annually:

1. **Master system doc regeneration** — Full bootstrap refresh
   ```bash
   ukbe-run-agent run 00_master_docs_bootstrap_v1 --project-root <repo_path>
   ```

2. **Delivery scaffold refresh** — Regenerate SOPs, templates, agents
   ```bash
   ukbe-run-agent run 10_execution_scaffold_v1 --project-root <repo_path>
   ```

3. **Archive cleanup** — Review archives >2 years old for permanent deletion
   - Check `docs/codebase/04_changes/archive/`
   - Delete archives with no active references (requires architect approval)

4. **Workflow bundle update** — Re-initialize runner home with latest bootstrap
   ```bash
   ukbe-run-agent init
   ```

## Batch Files

Repository root contains launcher batch files for common workflows:

### Delivery Workflows

| Batch File | Target Workflow | Purpose |
|------------|----------------|---------|
| `run-20_initiative_intake_v1.bat` | `20_initiative_intake_v1` | Initiative intake and pre-init refinement |
| `run-21_bug_fix_intake_v1.bat` | `21_bug_fix_intake_v1` | Bug fix triage and report drafting |
| `run-30_delivery_planning_v1.bat` | `30_delivery_planning_v1` | Delivery planning and task decomposition |
| `run-31_task_execution_v1.bat` | `31_task_execution_v1` | Task execution with review loops |

### Documentation Workflows

| Batch File | Target Workflow | Purpose |
|------------|----------------|---------|
| `run-00_master_docs_bootstrap_v1.bat` | `00_master_docs_bootstrap_v1` | Generate master system documentation |
| `run-10_execution_scaffold_v1.bat` | `10_execution_scaffold_v1` | Delivery scaffold setup |
| `run-40_documentation_sync_v1.bat` | `40_documentation_sync_v1` | Documentation sync and reconciliation |
| `run-50_architecture_site_v1.bat` | `50_architecture_site_v1` | Architecture site publishing |

### Audience-Specific Documentation

| Batch File | Target Workflow | Purpose |
|------------|----------------|---------|
| `run-41_developer_doc_v1.bat` | `41_audience_doc_v1` | Developer-focused documentation |
| `run-41_operator_doc_v1.bat` | `41_audience_doc_v1` | Operator-focused documentation |
| `run-51_stakeholder_docs_v1.bat` | `51_stakeholder_docs_v1` | Stakeholder-focused documentation |
| `run-55_user_docs_v1.bat` | `55_user_docs_v1` | End-user documentation |

### Batch File Usage

Batch files activate `.venv` and invoke `ukbe-run-agent` with appropriate arguments:

```batch
@echo off
call .venv\Scripts\activate.bat
ukbe-run-agent run <workflow_name> --project-root "%~dp0" %*
```

**Usage:**
```bash
run-20_initiative_intake_v1.bat --draft-init docs/delivery/01_initiatives/draft/DRAFT_INIT_20260709_example.md
```

### Daemon Mode (Background Operation)

For continuous background operation:

```bash
ukbe-daemon.bat start    # Start daemon supervisor
ukbe-daemon.bat stop     # Stop daemon supervisor
ukbe-daemon.bat status   # Check daemon status
```

Daemon spawns fresh subprocesses per step; does not restart for code changes. Subprocess working directory set explicitly for `.env` loading.

## Notes

### Universal Ecosystem Baseline

Every repository bootstrapped with agent-runner-v2 receives this universal baseline:

1. **Core execution infrastructure** — CLI entry point, step runner, workflow router, job state manager, centralized constants
2. **Documentation governance** — System doc generation, codebase scaffolding, documentation sync capability
3. **Delivery scaffold** — Project analysis, SOP generation, template registries, agent contracts, status rules
4. **Testing infrastructure** — Unit/integration test split with pytest, isolated temp directories, coverage reporting

### Repo-Selected Profile

The universal baseline is refined by repository-specific profile selection:

| Profile Attribute | agent-runner-v2 Value | Rationale |
|-------------------|----------------------|-----------|
| **current_profile** | `explicit-v2-workflow-runner` | Clear v2 contract with meta.json sidecars, explicit failure routing, centralized constants |
| **target_profile** | `universal-bootstrap-engine` | Standalone workflow engine that can bootstrap any repository with consistent documentation and delivery patterns |
| **migration_mode** | `provisional` | Established patterns exist but universal abstraction still evolving; self-hosting creates circular dependencies |
| **repo_state** | `explicit` | Clear architecture with centralized constants, defined workflow families, established conventions, comprehensive documentation |

### Migration Mode

Repositories may operate in different migration modes:

| Mode | Description | Use Case |
|------|-------------|----------|
| **provisional** | Established patterns exist but evolving | agent-runner-v2 itself; balancing stability with innovation |
| **greenfield** | No existing patterns; fresh start | New repositories with no legacy documentation |
| **brownfield** | Existing docs need migration | Repositories with outdated/inconsistent documentation |
| **hybrid** | Mix of greenfield and brownfield areas | Large repositories with varied documentation maturity |

Migration mode affects:
- How aggressively stale docs are flagged
- Whether existing docs are preserved or regenerated
- Timeline for achieving full governance compliance

### Conditional Standards

Architecture standards are conditional profile choices rather than universal defaults:

| Standard | Conditional Application | Default for agent-runner-v2 |
|----------|------------------------|----------------------------|
| **DDD (Domain-Driven Design)** | Applied when domain complexity warrants bounded contexts | Not applied (workflow orchestration doesn't require DDD) |
| **EDA (Event-Driven Architecture)** | Applied when async event processing is primary pattern | Partially applied (daemon mode uses polling, not pure EDA) |
| **Clean Architecture** | Applied when separation of concerns critical across layers | Applied (clear layering: CLI → execution core → actions) |
| **Microservices** | Applied when independent deployment/scaling needed | Not applied (monolithic package with modular structure) |
| **Plugin Architecture** | Applied when extensibility via third-party plugins required | Applied (action layer supports pluggable extensions) |

Standards are selected based on:
- Repository domain complexity
- Deployment architecture requirements
- Team structure and ownership model
- Evolution timeline and maintenance strategy

### Deprecated Patterns

The following patterns are deprecated and must not appear in current workflows:

- **`07_master_prompts`** — Deprecated prompt organization; replaced by centralized artifact key placeholders in prompts
- **Hardcoded paths in prompts** — Replaced by `{ARTIFACT_KEY}` placeholders resolved at runtime
- **Markdown write-backs by runner** — Replaced by meta.json sidecar as only structured result channel
- **Silent recovery paths** — Replaced by explicit failure routing through runner failure handling

### Self-Hosting Considerations

When applying this SOP to agent-runner-v2 itself (self-hosting):

1. **Circular dependency awareness** — Repository generates its own documentation using its own workflows
2. **Bootstrap vs runtime distinction** — Changes to bootstrap sources require re-initialization of global runner home
3. **Reference implementation responsibility** — agent-runner-v2 exercises full capability set as reference implementation
4. **Backward compatibility** — Changes must not break existing workflow executions on other repositories

### Operational Reminders

1. **Runtime path resolution** — Workflow paths in `config.json` must use absolute paths or be omitted to avoid workspace-relative resolution failures
2. **Subprocess working directory** — Daemon subprocess needs correct CWD for `.env` loading and artifact path resolution
3. **Meta.json mandatory** — Every coder/runner step must produce meta.json sidecar; workflow fails without it
4. **Protected documents** — Workflow-generated documents cannot be manually edited; update source prompts instead
5. **Notification credentials** — Pushover notifications require API credentials in `.env`; test delivery periodically

---

*Generated by workflow: 10_execution_scaffold_v1 | Step: generate_sop | Change: 10SCAFFOLD-20260708-8a4445fc*
