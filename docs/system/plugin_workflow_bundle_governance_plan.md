# Plugin Workflow Bundle Governance Plan

## Purpose

This document defines the target governance model for plugin workflow bundles
in the `agent-runner` ecosystem.

The current workflow design is still implicitly shaped around a single
workflow at a time. That is too narrow for real operating bundles such as a
software development lifecycle bundle, where multiple workflows form one
coherent operating system.

This plan defines how such multi-workflow bundles should be governed.

## Problem Statement

The current design has a gap between:

- ecosystem-level governance
- individual workflow execution

What is missing is an explicit governance model for a plugin bundle that
contains multiple workflows with shared purpose, sequencing, handoff rules,
artifact boundaries, and operational guardrails.

Example:

An SDLC bundle may include:

- `10_execution_scaffold_v2`
- `20_initiative_intake_v1`
- `21_bug_fix_intake_v1`
- `30_delivery_planning_v1`
- `31_task_execution_v1`
- `40_documentation_sync_v1`

These should not be treated as isolated workflows with no bundle-level
control model. They form a coordinated plugin bundle and should be governed
as one bundle.

## Core Decision

A plugin workflow bundle may contain one or many workflows.

The governance model must explicitly support both:

- a single-workflow bundle
- a multi-workflow bundle

The bundle, not just the workflow, must become a first-class governance
object.

## Governance Layer Placement

The clean responsibility split is:

### Layer 1: Ecosystem Governance

Owns the universal rules for what a plugin workflow bundle is.

Layer 1 should define:

- required bundle control files
- bundle ownership model
- publish/install/runtime boundaries
- bundle-level artifact guardrails
- sequencing and dependency contract shape
- registry and role-policy expectations

Layer 1 should not hardcode a specific SDLC workflow inventory.

### Layer 2: Bundle-Local Governance

Owns the SOP and operating model of a specific plugin bundle.

For example, the SDLC bundle should define:

- exact workflow sequence
- workflow entrypoints
- allowed branches in the lifecycle
- handoff contract between workflows
- owned artifact families
- review/refine/approval control points

### Layer 3: Repo-Local Outputs

Owns generated outputs for a specific repository or run.

Repo-local outputs remain downstream and must not become bundle governance.

## Bundle As First-Class Runtime Object

The runtime model should recognize these first-class objects:

- ecosystem governance
- plugin bundle
- workflow
- job/run
- artifact set

A workflow should not be interpreted without its bundle context when the
workflow belongs to a coordinated operating bundle.

## Target Bundle Responsibilities

A plugin workflow bundle should own:

- bundle identity
- bundle purpose
- workflow inventory
- workflow sequence and dependency rules
- shared role-policy expectations
- shared artifact ownership boundaries
- bundle-local SOP and guardrails
- publish/install structure
- validation rules for bundle consistency

A plugin workflow bundle should not own:

- ecosystem-wide governance authority
- provider authentication logic
- repo-derived outputs outside its runtime scope

## Proposed Bundle File Structure

Recommended structure:

```text
workflows/
  _registry/
    coder_connections.json
    coder_roles.json
    role_policies.json

  sdlc_bundle/
    bundle.toml
    bundle_governance/
      BUNDLE_OVERVIEW.md
      WORKFLOW_SEQUENCE.md
      WORKFLOW_SOP.md
      ARTIFACT_OWNERSHIP.md
      OPERATING_GUARDRAILS.md

    10_execution_scaffold_v2/
      workflow.toml
      prompts/
      bundle_governance/

    20_initiative_intake_v1/
      workflow.toml
      prompts/
      bundle_governance/

    21_bug_fix_intake_v1/
      workflow.toml
      prompts/
      bundle_governance/

    30_delivery_planning_v1/
      workflow.toml
      prompts/
      bundle_governance/

    31_task_execution_v1/
      workflow.toml
      prompts/
      bundle_governance/

    40_documentation_sync_v1/
      workflow.toml
      prompts/
      bundle_governance/
```

This is only a target pattern, but the key idea is that the bundle has its
own control plane above the individual workflows.

## Required Bundle Control Files

Every plugin bundle should define a small, explicit control surface.

### `bundle.toml`

Owns:

- bundle id
- bundle name
- bundle purpose
- workflow membership
- canonical workflow ordering
- entry workflows
- optional branching rules
- bundle-local validation configuration

### `BUNDLE_OVERVIEW.md`

Owns:

- what the bundle is for
- who uses it
- high-level lifecycle covered by the bundle
- relationship to ecosystem governance

### `WORKFLOW_SEQUENCE.md`

Owns:

- canonical workflow order
- allowed alternate paths
- workflow prerequisites
- workflow handoff expectations

This is where an SDLC bundle should describe how:

- initiative intake
- bug-fix intake
- planning
- execution
- documentation sync

fit together.

### `WORKFLOW_SOP.md`

Owns:

- operator procedure
- entry conditions
- exit conditions
- human approval points
- refine/review loops
- expected workflow state transitions

### `ARTIFACT_OWNERSHIP.md`

Owns:

- which workflow may create which artifact family
- which workflow may mutate which artifacts
- handoff artifacts
- bundle-level ownership boundaries

### `OPERATING_GUARDRAILS.md`

Owns:

- forbidden writes
- sequence violations
- invalid direct workflow jumps
- role misuse boundaries
- retry/escalation rules
- validation gates before progression

## Bundle Guardrails

The bundle governance model should enforce these guardrails.

### Sequence Guardrails

- workflows must run only in allowed order
- branching workflows must define explicit entry conditions
- downstream workflows must reject missing prerequisites

### Artifact Guardrails

- each artifact family must have a clear owning workflow
- downstream workflows may read many artifacts but must mutate only approved
  owned artifacts
- bundle-level packaging must not blur ownership boundaries

### Control Guardrails

- workflow prompts must not silently expand bundle scope
- a workflow may not assume authority over another workflow's owned artifacts
- bundle-local SOP must override ad hoc workflow behavior

### Runtime Guardrails

- manual mode and daemon mode must enforce the same bundle rules
- validation must happen before execution transitions to the next workflow
- bundle-local control files must be available at publish/install/runtime

## Relationship To `_registry`

The bundle governance model should work with the shared `_registry`, not
replace it.

Recommended split:

- `workflows/_registry/` owns shared runtime registries
- bundle control files own bundle sequencing, SOP, and ownership
- workflow files own step execution logic inside bundle constraints

This keeps:

- role and coder routing centralized
- bundle operating rules bundle-local
- step behavior workflow-local

## SDLC Bundle Example

A future SDLC plugin bundle should be modeled as one coordinated bundle with
multiple workflows.

Illustrative lifecycle:

1. `10_execution_scaffold_v2`
2. `20_initiative_intake_v1` or `21_bug_fix_intake_v1`
3. `30_delivery_planning_v1`
4. `31_task_execution_v1`
5. `40_documentation_sync_v1`

Bundle governance should define:

- when initiative intake is used
- when bug-fix intake is used
- whether both may feed planning
- what artifacts planning must produce before execution starts
- what documentation sync may update after execution completes

These rules belong at bundle level, not repeated ad hoc in each workflow.

## Ecosystem Governance Implications

Layer 1 governance should be updated so it explicitly recognizes:

- a bundle may contain multiple workflows
- a workflow may belong to a lifecycle-oriented plugin bundle
- bundle-local SOP is required for multi-workflow bundles
- bundle-local sequencing and artifact-ownership rules are authoritative
  inside the bundle

This should be reflected in:

- `BUNDLE_TAXONOMY.md`
- `RUNTIME_GOVERNANCE.md`

not by embedding specific repo workflow inventories, but by defining the
general contract.

## Validation Requirements

Bundle governance validation should check at least:

1. every workflow belongs to a declared bundle
2. bundle membership in `bundle.toml` matches actual workflow folders
3. workflow sequencing references only declared workflows
4. declared entry workflows exist
5. artifact ownership rules do not overlap without explicit handoff semantics
6. workflow prompts do not claim bundle authority outside declared scope
7. publish/install packaging includes required bundle control files

## Acceptance Criteria

This design is complete when:

1. plugin workflow bundles are treated as first-class governance objects
2. the ecosystem governance model supports multi-workflow bundles cleanly
3. each concrete bundle can carry its own SOP and guardrails
4. SDLC-style bundles can express lifecycle sequencing explicitly
5. bundle-level artifact ownership is clearer than per-workflow ad hoc rules
6. manual and daemon execution can both enforce the same bundle-level rules

## Recommended Next Steps

1. approve the bundle-governance model
2. update the core governance refactor so Layer 1 recognizes multi-workflow
   plugin bundles
3. define the initial `bundle.toml` schema
4. define the minimum required bundle governance docs
5. design the first concrete multi-workflow bundle, likely the SDLC bundle
6. migrate individual workflows into that bundle model one by one
