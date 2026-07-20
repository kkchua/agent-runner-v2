---
template_id: SYS-02-AUD
version: "1.0"
doc_type: "audit_artifact"
authority: "workflow-generated"
scan_policy: "exclude"
scan_reason: "run-scoped audit evidence; excluded from operational scans"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02PC-GEN-20260720-005"
managed_by: workflow-generated
generated_at: "2026-07-20T16:55:00+08:00"
---

# Platform Core Audit -- agent-runner-v2 Layer 2 Constitution

## Decision

**APPROVED**

The staged Layer 2 platform core constitution set is approved for human
acceptance and publish. All six permanent documents are correctly scoped
to Layer 2, inherit Layer 1 governance without redefinition, carry valid
metadata, and maintain clear platform identity throughout. One fixable
factual accuracy finding was identified in SHARED_SERVICES.md (three
incorrect BackendClient method names) that should be corrected before or
during publish but does not constitute a conceptual runtime model
contradiction.

## Layer Boundary Audit

### Layer 1 Governance -- Not Redefined

All six documents inherit Layer 1 governance explicitly and correctly:

- **README.md** states: "This platform constitution inherits from the
  Layer 1 Governance Foundation without redefining it." It lists specific
  inherited elements: layer definitions, ownership boundaries, authority
  rules, metadata baseline, governance lifecycle model, and bundle
  taxonomy. It further states: "Where Layer 1 and Layer 2 appear to
  conflict, Layer 1 governs."

- **RUNTIME_MODEL.md** describes execution architecture (step model,
  daemon/CLI/manual modes, coder integration, rejection and retry) -- all
  Layer 2 platform concerns. No ecosystem governance is redefined.

- **BUNDLE_AUTHORING_CONTRACT.md** defines bundle requirements specific
  to agent-runner-v2. This is a platform contract, not an ecosystem rule.

- **SHARED_SERVICES.md** defines runtime services (context extensions,
  artifact resolution, sidecar contract, backend sync, action
  registration) -- all platform operational model.

- **METADATA_CONTRACT.md** explicitly states: "It does not redefine any
  Layer 1 baseline field or vocabulary. It extends where the platform
  requires more specific classification." The doc_type and authority
  values listed are a subset of Layer 1 vocabulary, not new definitions.

- **VALIDATION_CONTRACT.md** defines the platform validation pattern
  using the platform's own infrastructure (DocumentationValidationPlan,
  has_section, has_frontmatter_field). No Layer 1 governance content.

**Verdict: PASS** -- No Layer 1 governance redefinition or contradiction.

### Layer 3 Bundle-Specific Drift -- Absent

No document contains bundle-specific outputs or examples presented as
platform-wide rules:

- No concrete Layer 3 workflow bundle names appear as normative platform
  rules. The Known Workflow Bundles list in the context inventory is a
  temporary evidence artifact, not a permanent standard.
- Source code module references (runtime_context.py, step_runner.py,
  coder_adapters.py, etc.) are factual citations of the platform runtime,
  not bundle-specific content.
- BUNDLE_AUTHORING_CONTRACT.md defines generic requirements for ANY
  Layer 3 bundle, not a specific bundle's outputs or configuration.

**Verdict: PASS** -- No Layer 3 bundle-specific drift.

### Platform Identity -- Clear and Consistent

Every document declares:
- `platform: "agent-runner-v2"` in YAML frontmatter
- References to agent-runner-v2 as the owning platform in body text

README.md opens with a Platform Identity section stating: "agent-runner-v2
is a standalone, multi-step AI workflow runner."

**Verdict: PASS** -- Platform identity is clear throughout.

## Authority Audit

### No Promotion Authority Overclaim

- No Layer 2 document claims ecosystem-wide (Layer 1) authority.
- No document presents itself as Layer 1 governance.
- The README explicitly positions the set as "the authoritative Layer 2
  reference for the platform" -- scoped correctly.
- METADATA_CONTRACT.md correctly positions itself as extending (not
  replacing) the Layer 1 Metadata Standard.

**Verdict: PASS** -- No authority overclaim.

### Evidence Separation

- Context inventory: `doc_type: "validation_artifact"`,
  `scan_policy: "exclude"` -- correctly classified as temporary evidence.
- Review artifact: `doc_type: "review_artifact"`,
  `scan_policy: "exclude"` -- correctly classified.
- Validation artifact: `doc_type: "validation_artifact"`,
  `scan_policy: "exclude"` -- correctly classified.
- This audit artifact: `doc_type: "audit_artifact"`,
  `scan_policy: "exclude"` -- correctly classified.
- All six permanent documents: `doc_type: "platform_standard"`,
  `scan_policy: "include"` -- correctly classified.

**Verdict: PASS** -- Temporary evidence is not presented as permanent
standard.

### Lifecycle State

All six staged permanent documents use `lifecycle_status: "draft"`.
No document incorrectly claims `published` or `active` status while
still in the staged run directory. The publish step will transition
lifecycle status upon activation.

**Verdict: PASS** -- Lifecycle state is correct for staged documents.

## Metadata Audit

### Frontmatter Compliance

All six documents carry valid YAML frontmatter with consistent values:

| Field | Value | Compliant |
|---|---|---|
| doc_type | "platform_standard" | Yes -- valid Layer 1 value |
| authority | "workflow-generated" | Yes -- valid for staged docs |
| scan_policy | "include" | Yes -- correct for permanent docs |
| scan_reason | Non-empty, descriptive | Yes |
| layer | "layer2" | Yes -- correct layer |
| platform | "agent-runner-v2" | Yes -- consistent identity |
| lifecycle_status | "draft" | Yes -- correct for staged |
| template_id | SYS-02-XX pattern | Yes -- follows convention |
| version | "1.0" | Yes -- present on all |
| managed_by | "workflow-generated" | Yes -- present on all |
| effective_version | "02PC-GEN-20260720-005" | Yes -- run identifier |

### Metadata Inheritance

METADATA_CONTRACT.md correctly describes:
- Layer 1 baseline fields inherited without redefinition
- Platform extension fields (platform, template_id naming, managed_by)
- Inheritance direction: Layer 1 -> Layer 2 -> Layer 3
- Prohibition on lower layers redefining higher layer values
- Authority transition rule: workflow-generated -> platform-owned on
  publish

**Verdict: PASS** -- Metadata is compliant and inheritance is correct.

## Platform Identity Audit

### Cross-Document Consistency

- All six documents reference "agent-runner-v2" by name.
- All six documents declare `platform: "agent-runner-v2"` in frontmatter.
- The README.md document map correctly lists all six documents including
  itself (self-including -- six documents, not five plus an implicit
  index).
- The Layer 1 inheritance statement in README.md correctly references
  the Layer 1 governance set location.
- The relationship to Layer 3 is correctly described as downward
  dependency only.

### Source Code Verification

Key runtime model claims were verified against actual source code:

| Claim | Source Location | Verified |
|---|---|---|
| StepConfig dataclass | workflow_packages/base.py:45 | Yes |
| ActionResult dataclass | action_result.py:11 | Yes |
| DocumentationValidationPlan | actions/documentation_validation_core.py:18 | Yes |
| invoke_coder() | coder_adapters.py:544 | Yes |
| WorkflowRegistry | workflow_packages/registry.py:16 | Yes |
| BundleGovernance | workflow_packages/base.py:31 | Yes |
| BackendClient | backend_client.py:10 | Yes |
| @action() decorator | workflow_packages/actions/__init__.py:31 | Yes |
| execute_routed_step | execution_core.py:82 | Yes |
| invoke_prepared_step | execution_core.py:47 | Yes |
| ExecutionRequest | execution_request.py:10 | Yes |
| ExecutionResult | execution_result.py:16 | Yes |
| PROJECT_ROOT, RUNNER_ROOT, JOBS_ROOT, ARTIFACT_ROOT | runtime_context.py:355-360 | Yes |
| resolve_repo_or_runtime_path() | runtime_context.py:158 | Yes |
| write_meta_sidecar() | runtime_context.py:273 | Yes |
| known_artifact_paths() | constants.py:597 | Yes |
| artifact_path() | constants.py:224 | Yes |
| resolve_workflow_output_paths() | workflow_path_contracts.py:9 | Yes |
| render_prompt_governance_block() | bundle_governance.py:103 | Yes |
| load_workflow_package() | workflow_packages/loader.py:32 | Yes |
| daemon spawns child subprocesses | daemon.py:245 (_spawn_child) | Yes |
| has_section() | documentation_validation_core.py | Yes |
| has_frontmatter_field() | documentation_validation_core.py | Yes |
| check_file_exists() | documentation_validation_core.py | Yes |
| check_folder_exists() | documentation_validation_core.py | Yes |
| validate_documentation_plan() | documentation_validation_core.py | Yes |

**Verdict: PASS with finding** -- Platform identity is clear and
consistent. Runtime model architecture is accurately described. One
factual accuracy finding exists (see Cited Evidence below).

## Cited Evidence

### Finding F1: Incorrect BackendClient Method Names (Fixable)

**Document**: SHARED_SERVICES.md, section "BackendClient"

**Offending text**:

    The `BackendClient` dataclass provides the API interface:

    - `submit_run()`: submits a new workflow run to the backend.
    - `claim_step()`: claims a pending step for execution (used by daemon).
    - `report_result()`: reports step completion and artifact paths.
    - `send_heartbeat()`: emits liveness heartbeats for active runs.
    - `approve_step()`: records human approval decisions.
    - `stop_run()`: cancels an active run.

**Actual source code** (backend_client.py):

| Documented Name | Actual Name | Line |
|---|---|---|
| `submit_run()` | `submit_run()` | 40 |
| `claim_step()` | `claim_step()` | 170 |
| `report_result()` | `complete_step_run()` | 173 |
| `send_heartbeat()` | `heartbeat()` | 132 |
| `approve_step()` | `approve_run()` | 85 |
| `stop_run()` | `stop_run()` | 115 |

Three of six method names are incorrect: `report_result()` should be
`complete_step_run()`, `send_heartbeat()` should be `heartbeat()`, and
`approve_step()` should be `approve_run()`.

**Severity**: Fixable. The conceptual description of the backend sync
protocol is accurate (the platform does provide step completion,
heartbeat, and approval services). The method names are factual
references that can be corrected without changing the architectural
model. This does not constitute a conceptual runtime model contradiction
because the execution architecture, service descriptions, and sync
protocol flow are all correct.

**Routing**: Refine -- correct the three method names before or during
publish.

### No Other Findings

All other audit checks passed without exception:

1. No Layer 1 governance redefinition or contradiction.
2. No bundle-specific content normalized into platform standards.
3. Platform identity (agent-runner-v2) clear in every document.
4. No temporary evidence normalized into permanent standards.
5. No promotion authority overclaim above Layer 2.
6. No internal conflicts on authority, lifecycle, or metadata rules.
7. All staged permanent docs correctly use lifecycle_status: "draft".
8. Runtime model architecture accurately reflects source code structure.
9. Document map is self-including (six documents, not five).
10. Metadata inheritance rules are correctly described.

## Publish Recommendation

**APPROVED for human acceptance and publish**, with one recommended
correction:

1. **Before publish** (preferred): Correct the three BackendClient method
   names in SHARED_SERVICES.md to match the actual source code
   (`complete_step_run()`, `heartbeat()`, `approve_run()`).

2. **During publish** (acceptable): If the human approver accepts the
   finding, the method names can be corrected as part of the publish
   transition.

The staged set is structurally complete, properly scoped to Layer 2,
metadata-compliant, and architecturally accurate. The single finding is
a factual naming error in one section of one document -- it does not
affect the validity of the platform constitution as a whole.
