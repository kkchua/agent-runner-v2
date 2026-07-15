# Workflow Onboarding Runtime Streamline Plan

## Problem

Adding a new workflow should require only workflow-package changes. Today it still
requires touching central runner code in multiple places, which creates repeated
runtime regressions.

Recent failures in `00_layer1_governance_bootstrap_v1` exposed the pattern:

- central alias logic in `agent_runner_v2/step_runner.py` had to be updated for
  the new workflow name
- prompt/runtime path behavior depended on runner-side special cases instead of
  workflow-owned context configuration
- step preparation signatures changed in multiple layers and manual/backend
  call sites drifted out of sync
- review/audit artifact-key contracts were duplicated across prompts and
  workflow config, allowing mismatches

This is not a one-off bug. It is an onboarding design problem.

## Root Causes

### 1. Central workflow-name branching

`step_runner.py` still contains workflow-specific branches such as:

- `_set_master_docs_aliases()`
- hardcoded checks for `00_core_governance_bootstrap_v1`
- hardcoded checks for `00_layer1_governance_bootstrap_v1`
- review/audit special handling tied to exact workflow names

This means every new workflow family risks requiring edits in shared runtime.

### 2. Context assembly is not package-owned enough

The repo already has the better pattern:

- `workflows/00_master_docs_bootstrap_v2/context_extensions.py`

That file explicitly states it replaces old `_set_master_docs_aliases()`
behavior. But the shared runner still owns part of the same concern.

Result:

- some workflows use package-local context extension
- some workflows depend on shared alias injection
- onboarding rules are inconsistent

### 3. Artifact contract is duplicated across too many surfaces

For one step, artifact ownership is currently spread across:

- `workflow.toml`
- prompt JSON schema text
- `bundle_governance.toml`
- runner path alias rules
- validation rules

Because these are not fully derived from one source, mismatches occur:

- `REVIEW_FILE` vs `REVIEW_FILE_SUGGESTED`
- repo-relative vs absolute-path prompt values
- produced artifact exists but contract path cannot resolve

### 4. Manual and backend execution still have too many wrappers

The execution path currently flows through multiple thin wrappers:

- `run_agent.py`
- `shared_runtime_deps.py`
- `step_execution_runtime.py`
- `backend_execution.py`

Signature changes like `project_root` can drift across those layers.

## Target Design

### Principle 1: New workflow onboarding must be package-local by default

A new workflow should be able to onboard with:

- `workflow.toml`
- prompts
- optional `actions.py`
- optional `context_extensions.py`
- required `bundle_governance.toml` when the workflow writes governed artifacts

Shared runtime should not need workflow-name conditionals for normal onboarding.

### Principle 2: Shared runtime should be artifact-class aware, not workflow-name aware

Instead of:

- `if template_group == "..."`

prefer:

- behavior derived from declared artifact registry
- behavior derived from workflow package metadata
- behavior derived from declared context extension hooks

### Principle 3: Workflow package owns prompt path substitution

Absolute path injection for special artifact families should be provided by:

- workflow-local `context_extensions.py`

not by central `step_runner.py` branches.

### Principle 4: One execution preparation function, one signature, one caller contract

`prepare_step_execution()` should remain the single authority.

All callers should pass one execution input object or one stable signature.
Avoid thin wrapper drift.

## Required Refactor

### Phase 1. Remove central master-doc alias branching

Replace `_set_master_docs_aliases()` usage with workflow-owned context
extensions for all master-doc style workflows:

- `00_master_docs_bootstrap_v2`
- `00_core_governance_bootstrap_v1` if kept for reference execution
- `00_layer1_governance_bootstrap_v1`

Action:

- create `workflows/00_layer1_governance_bootstrap_v1/context_extensions.py`
- move all absolute-path alias generation for:
  - `SYSTEM_DOCS_INDEX`
  - `SYSTEM_DOC_STANDARD`
  - `BUNDLE_TAXONOMY`
  - `RUNTIME_GOVERNANCE`
  - `REVIEW_FILE_SUGGESTED`
  - `SYSTEM_DOCS_VALIDATION`
- make those values resolve from `project_root`

After migration:

- delete `_set_master_docs_aliases()` from `step_runner.py`
- remove workflow-name checks tied to master-doc path aliases

### Phase 2. Make bundle governance mandatory for governed-output workflows

Any workflow that declares stable artifact outputs should provide:

- `bundle_governance.toml`

Validation should fail at package-load time if:

- a workflow has `produces` entries
- and those keys are not declared in bundle governance

This already partially exists in `workflow_bundle_validator.py`; it should be
enforced as part of onboarding acceptance.

### Phase 3. Derive prompt-side artifact keys from workflow spec

Review/audit prompts should not hand-maintain artifact key names.

Target:

- generate the sidecar artifact-key schema section from step config
- or inject a normalized artifact contract block during prompt rendering

This avoids:

- `REVIEW_FILE` vs `REVIEW_FILE_SUGGESTED`
- stale copied JSON examples

### Phase 4. Collapse wrapper signature drift

Replace ad hoc wrapper forwarding with one typed execution request object for
manual and backend step preparation.

At minimum:

- manual mode and backend mode must call the same preparation helper through a
  single stable adapter
- shared wrappers should stop re-declaring parallel keyword signatures when
  possible

### Phase 5. Add onboarding regression tests

The missing protection is not syntax checking. It is onboarding regression.

Required automated tests:

1. workflow package load test
   - validates `workflow.toml`
   - validates `bundle_governance.toml`
   - validates prompt references to declared artifact keys

2. prompt context build test
   - for `00_layer1_governance_bootstrap_v1`
   - confirms system-doc artifact context values are absolute repo-root paths

3. prepare-step parity test
   - manual path and backend path produce equivalent `PreparedStepExecution`
   - same prompt path
   - same artifact context
   - same `meta.json` target

4. reject-loop contract test
   - review step returns `REVIEW_FILE_SUGGESTED`
   - valid model `REJECTED` routes to refine
   - contract mismatch does not consume reject budget

5. pre-run signature drift test
   - smoke test calling all execution wrappers into `prepare_step_execution()`
   - catches missing forwarded arguments such as `project_root`

## Immediate Recommendation

Do not keep extending `step_runner.py` with workflow-specific onboarding logic.

For the current migration:

1. introduce `context_extensions.py` for `00_layer1_governance_bootstrap_v1`
2. migrate master-doc path aliasing into that file
3. delete the shared `_set_master_docs_aliases()` path once parity is proven
4. add onboarding regression tests before migrating the next workflow

## Success Criteria

The design is acceptable only when a new workflow can be introduced without any
shared-runner changes unless it adds a genuinely new execution capability.

Concretely:

- adding a new workflow must not require editing `step_runner.py`
- adding a new workflow must not require editing `run_agent.py`
- adding a new workflow must not require editing `backend_execution.py`
- artifact path shape and artifact key naming must be package-derived
- manual and backend execution must share one tested preparation contract

