# 00 Master Docs Bootstrap v2 Migration Plan

## Summary

This document tracks the completion of the partial migration for
`00_master_docs_bootstrap_v2`.

Recommendation:

- do **not** recreate the workflow from scratch
- complete the migration by modifying the existing package in place

Reason:

- the workflow package structure is already migrated enough to preserve
  directly
- the remaining gaps are concentrated in coder routing and control-plane
  wiring, not in the workflow's artifact model or package-local runtime hooks

This workflow should be the next migration target after
`00_core_governance_bootstrap_v1`.

Dependency order:

1. `00_core_governance_bootstrap_v1`
2. `00_master_docs_bootstrap_v2`
3. `10_execution_scaffold_v2`

This order matches the intended governance stack:

- Layer 1: ecosystem governance
- Layer 2: repo master-doc structure
- Layer 3: SDLC / execution scaffold

## Current Status Review

### What Is Already Migrated

The workflow already has real package-local migration work and should be
treated as an in-progress migrated workflow, not as untouched legacy state.

Already migrated:

- `workflow.toml` exists as a package manifest
- package-local `actions.py` exists
- package-local `context_extensions.py` exists
- the workflow uses artifact-driven step definitions rather than old
  template-group-only wiring
- most steps already use role-based coder fields:
  - `default_role`
  - `allowed_roles`
- validation and finalization are already package-local actions:
  - `validate_system_docs`
  - `finalize_bootstrap`

### What Is Still Legacy

The workflow is not fully migrated because it still carries legacy routing
assumptions.

Remaining legacy elements:

- `workflows/00_master_docs_bootstrap_v2/coder_roles.json` is still alias-based
  instead of semantic-role-to-connection routing
- step `04d_generate_architecture_flow_docs` still uses legacy coder config:
  - `default = "qwen-architect"`
  - `allowed = ["claude", "codex", "qwen-architect"]`
- role resolution still depends on old alias-era names such as:
  - `qwen-architect`
  - `qwen-reviewer`
  - `claude-architect`
  - `codex-architect`
  - `deepseek-developer`
- the workflow has not yet been normalized onto the shared runtime control
  plane under `workflows/_registry`

### Scope Identity

This workflow is a repo master-doc bootstrap workflow, not a Layer 1
governance workflow and not an SDLC scaffold workflow.

Its effective purpose is:

- scan a target repository
- generate the repository's master system documentation set
- review and refine that document set
- validate the generated system-doc baseline
- finalize the repository bootstrap summary

Its main output family includes:

- `PROJECT_ANALYSIS`
- `SYSTEM_DOCS_INDEX`
- `SYSTEM_DOC_STANDARD`
- `BUNDLE_TAXONOMY`
- `SYSTEM_OVERVIEW`
- `BUSINESS_CAPABILITIES`
- `FUNCTIONAL_SPEC`
- `NON_FUNCTIONAL_REQUIREMENTS`
- `SYSTEM_CONTEXT`
- `COMPONENT_ARCHITECTURE`
- `DECISION_LOG`
- `SYSTEM_FILE_STRUCTURE`
- `DEVELOPER_GUIDE`
- `RUNBOOK`
- `INTEGRATION_MAP`
- `FAILURE_MODES`
- `ARCHITECTURE_FLOW`
- `SYSTEM_DOCS_VALIDATION`
- `BOOTSTRAP_SUMMARY`

## Recommendation

Modify the current workflow in place.

Do not recreate it from scratch.

### Why In-Place Repair Is Better

- the package-local action split is already done
- the context-extension hook is already done
- the workflow artifact graph is already explicit and stable
- the step ordering and review/refine loops are already encoded in the package
- the remaining work is mostly routing cleanup, registry alignment, and a
  small amount of workflow TOML normalization

### Why Full Recreation Is Worse

- it would duplicate already-migrated package behavior
- it would increase churn in prompts, actions, and validation paths without
  solving a fundamentally different problem
- it would make it harder to compare against the current working package
  behavior
- it would likely reintroduce avoidable drift in artifact naming and step
  semantics

## Migration Target State

`00_master_docs_bootstrap_v2` should finish in the same migration model as
`00_core_governance_bootstrap_v1`, adapted for repo master-doc outputs.

Target state:

- workflow is loaded purely as a workflow package
- coder routing is resolved via the shared registry in `workflows/_registry`
- no step uses legacy alias-based `default` / `allowed` coder config
- semantic roles resolve through registry-backed connections and models
- package-local actions remain authoritative
- package-local context extensions remain authoritative
- runtime uses the installed global workflow copy only
- no dependency remains on legacy flat alias mapping for this workflow

## Required Changes

### 1. Finish Step-Level TOML Migration

Normalize the remaining legacy coder config in `workflow.toml`.

Required change:

- replace the legacy coder block on `04d_generate_architecture_flow_docs`
  with role-based fields

Use the same role-based shape as the rest of the workflow:

- `default_role`
- `allowed_roles`

Prefer alignment with the surrounding architecture-generation steps unless
there is an explicit product reason for this one step to diverge.

### 2. Replace Workflow-Local Alias Roles

Rewrite `workflows/00_master_docs_bootstrap_v2/coder_roles.json` so it no
longer stores alias names.

Replace entries of the form:

- `"alias": "qwen-architect"`

with registry-native role definitions of the form:

- `coder`
- `connection`
- `model_id`
- `role_type`

Use the shared registry model already established in `workflows/_registry`.

### 3. Align Workflow Roles With Shared Registry Intent

The workflow-local role file must agree with the current shared registry and
the intended provider split.

At minimum:

- architect roles must resolve through explicit `connection + model_id`
- reviewer roles must resolve through explicit `connection + model_id`
- codex roles must remain standalone and must not define `connection`

The workflow-local role names should remain stable:

- `architect_primary`
- `architect_secondary`
- `architect_tertiary`
- `reviewer_primary`
- `reviewer_secondary`
- `reviewer_tertiary`
- `developer_primary`
- `developer_secondary`

### 4. Remove Alias-Era Dependency From This Workflow

This workflow should stop depending on alias-era names such as
`qwen-architect` and `qwen-reviewer`.

For this workflow specifically:

- no step should reference alias-style coder names
- no workflow-local role should wrap an alias name
- resolution should go directly through semantic role -> connection -> model

### 5. Keep Existing Package-Local Actions

Do not rewrite or relocate package-local actions unless a concrete defect is
found.

Keep:

- `validate_system_docs`
- `finalize_bootstrap`

The current migration should build on them, not replace them.

### 6. Keep Existing Context Extension Model

Do not recreate the path-alias behavior elsewhere.

Keep `context_extensions.py` as the workflow-owned place that injects
master-doc artifact paths into prompt context.

Only adjust it if migration uncovers a concrete runtime parity bug.

### 7. Publish / Install Verification

This workflow should not be considered migrated until the full publish chain
is verified:

1. repo source under `workflows/00_master_docs_bootstrap_v2/`
2. packaged bootstrap mirror under
   `agent_runner_v2/bootstrap/workflows/default/00_master_docs_bootstrap_v2/`
3. installed global runtime copy under
   `%USERPROFILE%/.ukbe-runner/workflows/default/00_master_docs_bootstrap_v2/`

The same applies to the shared registry files under `workflows/_registry`.

## Acceptance Criteria

The migration is complete when all of the following are true:

- `00_master_docs_bootstrap_v2/workflow.toml` contains no legacy alias-style
  `default` / `allowed` coder blocks
- `00_master_docs_bootstrap_v2/coder_roles.json` contains no alias fields
- workflow role resolution uses explicit `coder + connection + model_id`
- the workflow runs against the installed global workflow copy and resolves
  the intended providers from the shared registry
- package-local actions execute successfully through the migrated path
- package-local context extensions still resolve canonical artifact paths
- review/refine loops still return to the correct steps
- validation and finalization still emit deterministic output artifacts

## Suggested Execution Order

1. Convert `workflows/00_master_docs_bootstrap_v2/coder_roles.json` to the
   registry-native role format
2. Replace the remaining legacy coder block in `workflow.toml`
3. Verify that workflow package loading resolves the intended role data
4. Publish bootstrap again
5. Install / sync to the global runtime copy
6. Run manual local regression for `00_master_docs_bootstrap_v2`
7. Run daemon / backend mode regression only after manual parity is confirmed

## Tracking Notes

Current migration assessment:

- package migration: substantially complete
- routing migration: incomplete
- registry migration: incomplete
- runtime publish/install verification: required

Final recommendation:

- proceed by modifying the current workflow in place
- do not recreate the workflow from scratch

## Layer 2 Target Capability Model

The target role of `00_master_docs_bootstrap_v2` is to establish the repo
master-doc and operating structure for `agent-runner-v2`.

That Layer 2 structure should be broad enough to support multiple plugin
workflow families under one coherent repository model.

### Intended Layering

- Layer 1: ecosystem governance
- Layer 2: repo master-doc and operating structure
- Layer 3: plugin workflow families

### Plugin Workflow Families Layer 2 Must Support

The Layer 2 repo-doc model should explicitly support at least these workflow
families:

1. SDLC workflows
2. Documentation Generator workflows
3. Runtime Operations workflows
4. Quality / Compliance workflows
5. Migration / Refactor workflows
6. Scaffolding / Bootstrap workflows
7. Integration / External System workflows
8. Knowledge / Analysis workflows
9. Release / Packaging workflows
10. Incident / Recovery workflows

### Family Descriptions

#### 1. SDLC Workflows

Examples:

- initiative intake
- delivery planning
- task execution
- review / validation
- documentation sync
- architecture communication
- delivery memory and audit

#### 2. Documentation Generator Workflows

Examples:

- repo/system master docs
- governance docs
- architecture views
- audience-facing documentation
- change logs
- validation reports

#### 3. Runtime Operations Workflows

Examples:

- daemon diagnostics
- worker/runtime checks
- registry sync verification
- bundle install verification
- runtime state reconciliation

#### 4. Quality / Compliance Workflows

Examples:

- deterministic validation
- policy audit
- documentation contract checks
- artifact completeness review
- governance conformance review

#### 5. Migration / Refactor Workflows

Examples:

- workflow migration
- bundle migration
- repository contract upgrades
- legacy cleanup
- compatibility verification

#### 6. Scaffolding / Bootstrap Workflows

Examples:

- repo bootstrap
- workflow package bootstrap
- plugin starter generation
- environment initialization

#### 7. Integration / External System Workflows

Examples:

- backend sync
- external tool submission
- import / export pipelines
- connector verification

#### 8. Knowledge / Analysis Workflows

Examples:

- codebase scan
- impact analysis
- dependency mapping
- failure mode discovery
- architecture analysis

#### 9. Release / Packaging Workflows

Examples:

- bundle publish
- workflow package validation
- release manifest generation
- deployment preparation

#### 10. Incident / Recovery Workflows

Examples:

- drift recovery
- failed-run recovery
- state repair
- rollback preparation
- post-incident documentation refresh

### Implication For 00 Master Docs Bootstrap v2

`00_master_docs_bootstrap_v2` should not be treated as a narrow document
writer only.

It should establish the Layer 2 repository structure that lets all of the
workflow families above plug into a consistent repo-level operating model.

That means the workflow should generate repo-level system and operating docs
that answer questions such as:

- what this repository is
- how it is structured
- how it runs
- how workflow families fit together
- where runtime state lives
- how operators and developers navigate the system
- how plugin workflow bundles integrate into the repository model

### Layer 2 Scope Boundary

Layer 2 should own repo-level structure and operating understanding.

Layer 2 should not own:

- Layer 1 ecosystem authority
- universal governance contracts
- plugin-bundle-local SOP details for every bundle
- run-local or job-local generated output state

Those belong respectively to:

- Layer 1 ecosystem governance
- Layer 3 bundle-local workflow governance
- repo-local run outputs
