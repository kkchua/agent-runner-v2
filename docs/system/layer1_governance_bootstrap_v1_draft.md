# 00 Layer1 Governance Bootstrap v1 Draft

## Summary

This document defines the replacement workflow concept for Layer 1 ecosystem
governance generation.

Proposed new workflow name:

- `00_layer1_governance_bootstrap_v1`

Reason for creating a new workflow instead of rewriting
`00_core_governance_bootstrap_v1` in place:

- the current workflow is still shaped by legacy repository-specific
  assumptions
- it hardcodes concrete workflow-era ideas that no longer belong in Layer 1
- it is useful to preserve the current workflow as a historical reference
  during the transition
- the replacement should be treated as a clean Layer 1 contract, not as an
  incremental patch to an old migration-era design

The old workflow should remain available as reference only:

- `00_core_governance_bootstrap_v1`

The new workflow should become the authoritative Layer 1 generator for the
ecosystem.

## Core Objective

`00_layer1_governance_bootstrap_v1` should generate the universal Layer 1
governance docs for an ecosystem.

It must not depend on:

- concrete workflow names
- repository-specific plugin bundle names
- repository-specific SDLC inventory
- repo-local artifact names
- repo-specific prompt-contract placeholders
- historical migration assumptions from old bootstrap workflows

It should be reusable for:

- `agent-runner-v2`
- other workflow-based ecosystems
- ecosystems that use different Layer 2 and Layer 3 workflow families

## Governance Scope

The workflow owns only the permanent Layer 1 governance set.

It should generate exactly these four docs:

1. `README.md`
2. `DOCUMENTATION_STANDARD.md`
3. `BUNDLE_TAXONOMY.md`
4. `RUNTIME_GOVERNANCE.md`

These docs should live under:

- `docs/system/00_governance/bootstrap/`

### Layering Model

The generated Layer 1 docs should define this governance split:

- Layer 1: ecosystem governance
- Layer 2: repo or bundle master-doc and operating structure
- Layer 3: plugin workflow families and repo-local outputs

Layer 1 must define the universal contract for:

- governance authority
- documentation structure rules
- bundle class model
- ownership boundaries
- runtime publish/install/control-plane model
- validation gates

Layer 1 must not define:

- the specific workflow inventory of a repository
- the exact canonical SDLC scaffold workflow for a repository
- the exact plugin bundle inventory of a repository
- repo-local generated artifact sets
- provider authentication flows
- step-specific workflow business logic

## Workflow-Owned Outputs

### 1. `README.md`

Purpose:

- canonical overview of the ecosystem documentation and governance model

Must define:

- Layer 1 / Layer 2 / Layer 3 model
- authority boundaries
- audience framing
- canonical map of the four Layer 1 docs

Must not define:

- a repository's concrete workflow inventory
- a concrete scaffold workflow name
- plugin bundle membership for a specific repository

### 2. `DOCUMENTATION_STANDARD.md`

Purpose:

- canonical documentation contract for Layer 1 docs

Must define:

- required frontmatter
- required sections
- wording constraints
- update triggers
- deterministic validation rules

Must not define:

- repository-specific artifact examples
- repository-specific output names
- repository-specific filename examples
- concrete plugin workflow names

### 3. `BUNDLE_TAXONOMY.md`

Purpose:

- canonical bundle class and ownership model

Must define:

- core governance bundles
- plugin workflow bundles
- ownership boundaries
- packaging scope boundaries
- artifact authority boundaries
- the fact that a plugin bundle may contain one workflow or many workflows

Must not define:

- a repository's active workflow inventory
- a special exception for a named workflow
- repo-local runtime output inventory

### 4. `RUNTIME_GOVERNANCE.md`

Purpose:

- canonical steady-state runtime operating model

Must define:

- runtime scope boundaries
- publish/install/runtime boundaries
- `_registry` responsibilities
- role / connection / model resolution responsibilities
- plugin bundle runtime control expectations
- validation gates before publish, install, submit, and execute
- artifact ownership enforcement
- manual / daemon execution parity expectations

Must not define:

- repository-specific workflow chains
- concrete scaffold workflow identifiers
- provider authentication behavior
- migration history

## Non-Goals

The new workflow must not be used to generate:

- repo master docs
- repo-level system analysis
- codebase inventory
- SDLC SOP details
- workflow-bundle-local SOP
- plugin bundle workflow sequence for a specific repository
- audience docs
- delivery docs
- incident output docs

Those belong downstream to Layer 2 or Layer 3 workflows.

## Required Prompt Contract

The new workflow prompts should enforce these constraints.

### Generation Step

The generation prompt must:

- describe Layer 1 as universal ecosystem governance
- forbid concrete workflow inventory
- forbid concrete scaffold workflow names
- forbid repo-derived artifact names
- forbid repo-specific output filenames
- require generic support for plugin workflow bundles
- require generic support for single-workflow and multi-workflow bundles

The prompt should allow only generic concrete references such as:

- the current workflow's own name in frontmatter
- canonical directory locations that are part of the Layer 1 contract

### Review Step

The reviewer must approve only if:

- all four Layer 1 docs stay generic
- no repository-specific workflow inventory appears
- no concrete scaffold workflow is named as a universal requirement
- no repo-local artifact family is described as Layer 1 ownership
- plugin bundle support is generic and reusable
- Layer 1 / Layer 2 / Layer 3 boundaries are explicit and coherent

### Refine Step

The refine step must be validation-driven.

It must:

- read the latest review file
- read the latest deterministic validation file when present
- resolve every reported blocking issue directly
- preserve generic Layer 1 scope
- avoid introducing repository-specific names while fixing issues

### Audit Step

The final semantic audit should verify:

- factual correctness against the generic governance model
- no hidden repository-specific coupling
- no stale migration-era identifiers
- no contradiction between docs

## Required Validation Model

The new validator should be rewritten to enforce generic Layer 1 rules only.

### Keep These Validation Categories

- required files exist
- required sections exist
- template ids are correct
- frontmatter contract is correct
- stale forbidden literals are absent
- repo-derived artifact names are absent from Layer 1 docs where forbidden
- plugin bundle support is present generically
- runtime governance is steady-state rather than migration-oriented

### Remove These Validation Categories

The new validator must not require:

- `10_execution_scaffold_v2`
- `00_master_docs_bootstrap_v2`
- `20_initiative_intake_v1`
- any concrete workflow inventory
- any repository-specific scaffold/bundle naming

### Replace With Generic Rules

Replace repository-specific checks with generic checks such as:

- Layer 1 may define that a repository or bundle ecosystem must have a
  canonical scaffold or operating bundle, but must not name the concrete
  implementation
- Layer 1 may define that plugin bundles may contain one or many workflows
- Layer 1 may define that Layer 2 or bundle-local docs name the exact
  workflow inventory
- Layer 1 must not classify repo-local outputs as ecosystem governance

## Proposed Workflow Structure

The new workflow should keep the same high-level step pattern because the
pattern itself is sound.

Suggested steps:

1. `generate_layer1_governance_docs`
2. `review_layer1_governance_docs`
3. `refine_layer1_governance_docs`
4. `validate_layer1_governance_docs`
5. `audit_layer1_governance_accuracy`
6. `stepCompletion`

### Suggested Artifacts

- `SYSTEM_DOCS_INDEX`
- `SYSTEM_DOC_STANDARD`
- `BUNDLE_TAXONOMY`
- `RUNTIME_GOVERNANCE`
- `SYSTEM_DOCS_VALIDATION`
- `REVIEW_FILE_SUGGESTED`

This preserves the existing Layer 1 output model without carrying forward the
legacy prompt assumptions.

## Migration Strategy

### Keep Old Workflow

Keep:

- `00_core_governance_bootstrap_v1`

Role:

- legacy reference workflow
- historical comparison point
- not the long-term Layer 1 target

### Create New Workflow

Create:

- `workflows/00_layer1_governance_bootstrap_v1/`

Suggested initial contents:

- `workflow.toml`
- `prompts/01_generate_layer1_governance_docs.txt`
- `prompts/02_review_layer1_governance_docs.txt`
- `prompts/03_refine_layer1_governance_docs.txt`
- `prompts/04_audit_layer1_governance_accuracy.txt`
- `actions.py`
- `coder_roles.json`
- any bundle governance files only if needed for package-local ownership

### Implementation Approach

Use the current `00_core_governance_bootstrap_v1` only as a structural
starting point.

Reuse:

- step pattern
- output set
- review / refine / validate / audit loop structure

Do not reuse unchanged:

- repository-specific prompt constraints
- repository-specific validator checks
- workflow-name-specific governance assertions
- migration-era stale-reference assumptions

## Acceptance Criteria

The new workflow is ready when:

- it generates the four Layer 1 docs successfully
- no prompt requires concrete repository workflow names
- no validator requires concrete repository workflow names
- no review or audit logic requires concrete repository workflow names
- the docs define a generic plugin-bundle governance contract
- the docs define Layer 1 / Layer 2 / Layer 3 responsibilities clearly
- the workflow can be reused for another ecosystem without changing its Layer 1
  conceptual model

## Final Recommendation

Proceed by creating a new workflow:

- `00_layer1_governance_bootstrap_v1`

Keep the current workflow:

- `00_core_governance_bootstrap_v1`

as legacy reference only.
