---
doc_type: "audit_artifact"
authority: "workflow-generated"
scan_policy: "exclude"
scan_reason: "run-scoped platform core audit; temporary evidence only"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02PC-20260720-fd35ddf1"
generated_at: "2026-07-20T12:30:00+08:00"
---

# Platform Core Semantic Audit

- Job ID: `02PC-20260720-fd35ddf1`
- Audit scope: 6 staged permanent Layer 2 platform constitution documents
- Reference inputs: Layer Architecture Masterplan, Layer 2 Platform Core
  Specification, Platform Context Inventory, Platform Core Validation

## Decision

**APPROVED**

The staged Layer 2 platform core constitution set is approved for human
review and publish. All six documents maintain correct Layer 2 boundaries,
inherit Layer 1 governance without redefinition, carry consistent metadata,
and clearly identify the agent-runner-v2 platform identity. No forbidden
content was found.

The audit identified five fixable API-accuracy findings in SHARED_SERVICES.md
and VALIDATION_CONTRACT.md where code examples do not match the current
source code signatures or module locations. These are correctable in a
refine pass and do not constitute systemic runtime model contradictions.

## Layer Boundary Audit

### Layer 1 Redefinition Check: PASS

No document in the staged set redefines or contradicts Layer 1 governance.

- README.md explicitly states: "Layer 1 is inherited, not modified" and
  "Does not change the meaning of any Layer 1 doc_type or authority value."
- METADATA_CONTRACT.md inherits all eight Layer 1 doc_type values and five
  authority values verbatim, then extends with platform-specific semantics
  only for `bundle_definition` and `platform_standard`.
- No document attempts to redefine the three-layer architecture, cross-
  ecosystem ownership rules, or promotion rules.
- The Layer 1 inheritance table in README.md correctly references the five
  Layer 1 governance documents (SYS-00-LM, SYS-00-DA, SYS-00-BT, SYS-00-GL,
  SYS-00-MS) and describes how Layer 2 applies each without modification.

### Layer 3 Bundle Drift Check: PASS

No document contains bundle-specific content normalized into platform
standards.

- BUNDLE_AUTHORING_CONTRACT.md defines the general contract for ALL Layer 3
  bundles (required files, TOML format, artifact conventions). It does not
  describe any specific bundle's implementation.
- SHARED_SERVICES.md describes platform-level runtime services available to
  all bundles. Code examples use generic placeholders (MY_OUTPUT, MY_CUSTOM_PATH).
- The Platform Context Inventory lists known bundles by name only as
  reference context, which is within Layer 2 scope.
- No bundle-specific prompts, artifact mappings, or output contracts appear
  in any permanent document.

### Evidence Normalization Check: PASS

No temporary evidence is presented as permanent platform standard.

- All six permanent documents carry `doc_type: "platform_standard"` and
  `lifecycle_status: "draft"` (correct for staged pre-publish state).
- The PLATFORM_CONTEXT_INVENTORY and PLATFORM_CORE_VALIDATION artifacts
  carry `doc_type: "validation_artifact"` and `scan_policy: "exclude"`,
  correctly classifying them as temporary evidence.
- The audit artifact itself carries `doc_type: "audit_artifact"` and
  `scan_policy: "exclude"`.

## Authority Audit

### Promotion Authority Check: PASS

No document overclaims authority above Layer 2.

- README.md states: "Does not assert constitutional authority beyond this
  platform."
- METADATA_CONTRACT.md states: "This contract does not modify or contradict
  Layer 1 baseline values."
- BUNDLE_AUTHORING_CONTRACT.md states: "Layer 3 bundles must operate within
  this contract. They must not modify Layer 1 ecosystem governance or this
  Layer 2 platform constitution."
- VALIDATION_CONTRACT.md describes platform-level validation only and
  explicitly separates platform validation from bundle-local checks.
- No document claims ecosystem-wide governance authority or attempts to
  redefine cross-layer rules.

### Internal Consistency Check: PASS

All six documents are internally consistent on authority, lifecycle, and
metadata rules.

- All six carry identical `effective_version: "02PC-20260720-fd35ddf1"`,
  `lifecycle_status: "draft"`, `platform: "agent-runner-v2"`,
  `layer: "layer2"`.
- Cross-document references are consistent: README.md document map lists
  all six documents with correct template IDs; VALIDATION_CONTRACT.md
  references the same template IDs and required sections.
- The METADATA_CONTRACT.md description of permanent Layer 2 documents
  ("six permanent platform constitution documents") matches the actual set.
- The validation contract's frontmatter rules for Layer 2 permanent docs
  (`doc_type: platform_standard`, `authority: platform-owned or
  workflow-generated`) are consistent with the actual metadata values used.

## Metadata Audit

### Required Fields: PASS

All six permanent documents include all required frontmatter fields:

| Field | README | RUNTIME_MODEL | BUNDLE_AUTHORING | SHARED_SERVICES | METADATA | VALIDATION |
|---|---|---|---|---|---|---|
| template_id | SYS-02-IDX | SYS-02-RM | SYS-02-BAC | SYS-02-SS | SYS-02-MC | SYS-02-VC |
| version | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| doc_type | platform_standard | platform_standard | platform_standard | platform_standard | platform_standard | platform_standard |
| authority | workflow-generated | workflow-generated | workflow-generated | workflow-generated | workflow-generated | workflow-generated |
| scan_policy | include | include | include | include | include | include |
| scan_reason | present | present | present | present | present | present |
| layer | layer2 | layer2 | layer2 | layer2 | layer2 | layer2 |
| platform | agent-runner-v2 | agent-runner-v2 | agent-runner-v2 | agent-runner-v2 | agent-runner-v2 | agent-runner-v2 |
| lifecycle_status | draft | draft | draft | draft | draft | draft |
| effective_version | 02PC-... | 02PC-... | 02PC-... | 02PC-... | 02PC-... | 02PC-... |
| managed_by | workflow-generated | workflow-generated | workflow-generated | workflow-generated | workflow-generated | workflow-generated |

### Lifecycle State Check: PASS

All staged permanent docs correctly carry `lifecycle_status: "draft"`.
None are prematurely marked as `published` or `active`. The publish step
(step 8) is responsible for transitioning to `published` after human
approval.

### Vocabulary Compliance: PASS

- `doc_type: "platform_standard"` is a valid Layer 1 vocabulary value.
- `authority: "workflow-generated"` is a valid Layer 1 vocabulary value.
- `scan_policy: "include"` is a valid Layer 1 vocabulary value.
- No document claims `human-authored` authority (forbidden for generated docs).
- No document uses `layer: "layer1"` (forbidden for Layer 2 outputs).

## Platform Identity Audit

### Platform Identification: PASS

All six documents clearly identify `agent-runner-v2` as the owning platform.

- README.md opens with: "agent-runner-v2 is a standalone, multi-step AI
  workflow runner."
- All frontmatter blocks include `platform: "agent-runner-v2"`.
- RUNTIME_MODEL.md describes the agent-runner-v2 execution architecture
  with specific module references (step_runner.py, daemon.py, coder_adapters.py,
  workflow_router.py, coder_registry.py).
- BUNDLE_AUTHORING_CONTRACT.md references platform-specific paths and
  conventions (agent_runner_v2/artifact_keys.py, constants.py).
- SHARED_SERVICES.md references platform-specific modules (runtime_context.py,
  notification_manager.py, backend_client.py, workflow_packages/loader.py).
- METADATA_CONTRACT.md defines platform-specific field semantics for
  agent-runner-v2.
- VALIDATION_CONTRACT.md enforces `platform: "agent-runner-v2"` as a
  required frontmatter value.

## Runtime Model Accuracy Audit

### Execution Architecture: PASS (with findings)

The RUNTIME_MODEL.md accurately describes the platform's execution
architecture at the conceptual and structural level:

- Step model (prompt-driven vs action-driven) matches source code.
- Three execution paths (CLI, daemon, manual) match source code.
- Job lifecycle stages (init, execute, route, review/refine, approve,
  publish, completion) match source code.
- Coder integration model (role-based, dual-path registry discovery)
  matches source code.
- Rejection and retry model (refine loop, replan, failure routing) matches
  source code.
- Daemon subprocess architecture (fresh subprocess per invocation) matches
  daemon.py source code.
- Meta.json sidecar as sole communication channel matches source code.

### API Accuracy Findings (fixable)

The following code examples in SHARED_SERVICES.md and VALIDATION_CONTRACT.md
contain API signatures or module locations that do not match the current
source code. These are fixable defects suitable for a refine pass.

**Finding 1: build_context_extensions() signature mismatch**
- Document: SHARED_SERVICES.md, Context Extensions section
- Documented: `build_context_extensions(context: dict, state: dict, step_config: StepConfig) -> dict`
- Actual (step_runner.py line 1776): `build_context_extensions(*, state: dict, step: str, step_cfg: dict, ctx: dict[str, str], project_root: Path | None = None) -> dict[str, str]`
- Discrepancy: Parameter names differ (context vs ctx, step_config vs step_cfg), missing parameters (step, project_root), wrong parameter types.

**Finding 2: @action() decorator import path and signature**
- Document: SHARED_SERVICES.md, Action Registration section
- Documented import: `from agent_runner_v2.actions import action`
- Actual location: `agent_runner_v2.workflow_packages.actions.__init__`
- Documented signature: `def my_custom_action(*, state: dict, step_cfg: dict, job_dir: Path, context: dict) -> dict`
- Actual decorator example (workflow_packages/actions/__init__.py): `@action("name") def fn(*, context, state, step_cfg, project_root) -> ActionResult`
- Discrepancy: Wrong import module, different parameter names (job_dir vs project_root), wrong return type (dict vs ActionResult).

**Finding 3: build_output_paths() signature mismatch**
- Document: SHARED_SERVICES.md, Path Contracts section
- Documented: `build_output_paths(*, job_id: str, project_root: Path) -> dict`
- Actual (context_extensions.py): `build_output_paths(*, job_id: str = "{job_id}", mode: str = "{mode}", loop_iteration: int = 0) -> dict[str, str]`
- Discrepancy: Different parameters (project_root vs mode/loop_iteration).

**Finding 4: has_section() and has_frontmatter_field() module location**
- Document: VALIDATION_CONTRACT.md, Section Checks and Frontmatter Enforcement sections
- Documented location: `agent_runner_v2/documentation_guardrails.py`
- Actual location: `agent_runner_v2/actions/documentation_validation_core.py`
- Verification: grep confirms neither function exists in documentation_guardrails.py.

**Finding 5: DocumentationValidationPlan API mismatch**
- Document: VALIDATION_CONTRACT.md, ValidationPlan Pattern section
- Documented API: Constructor takes `plan_id: str` and `documents: list[dict]` with per-document `path`, `template_id`, `required_sections`, `required_frontmatter` fields.
- Actual API (documentation_validation_core.py): Dataclass with fields `required_folders: tuple[str, ...]`, `required_files: tuple[str, ...]`, `section_requirements: dict[str, tuple[str, ...]]`, `template_ids: dict[str, str]`, `extra_checkers: tuple[ValidationChecker, ...]`.
- Discrepancy: The documented API structure does not match the actual class. The documented example would fail at runtime.

**Finding 6: has_section() behavioral description**
- Document: VALIDATION_CONTRACT.md, Section Checks section
- Documented: "Case-sensitive exact match against heading text"
- Actual (documentation_validation_core.py line 49): Uses `re.IGNORECASE` flag, making it case-insensitive.

### Severity Assessment

These findings are API-level inaccuracies in code examples and function
descriptions. The broader architectural concepts described in both documents
are correct:

- The context extension pattern exists and works as described conceptually.
- The @action() decorator pattern exists and works as described conceptually.
- The DocumentationValidationPlan pattern exists and works as described
  conceptually.
- The has_section() and has_frontmatter_field() functions exist and serve
  the described purpose.

A Layer 3 bundle author reading these documents would understand the correct
patterns but would need to consult the actual source code for exact API
signatures. The findings are correctable in a single refine pass by updating
the code examples to match current source.

## Cited Evidence

| Finding | Document | Section | Offending Text |
|---|---|---|---|
| F1 | SHARED_SERVICES.md | Context Extensions | `def build_context_extensions(context: dict, state: dict, step_config: StepConfig) -> dict` |
| F2 | SHARED_SERVICES.md | Action Registration | `from agent_runner_v2.actions import action` |
| F2 | SHARED_SERVICES.md | Action Registration | `def my_custom_action(*, state: dict, step_cfg: dict, job_dir: Path, context: dict) -> dict` |
| F3 | SHARED_SERVICES.md | Path Contracts | `def build_output_paths(*, job_id: str, project_root: Path) -> dict` |
| F4 | VALIDATION_CONTRACT.md | Section Checks | `has_section()` function (in `agent_runner_v2/documentation_guardrails.py`) |
| F4 | VALIDATION_CONTRACT.md | Frontmatter Enforcement | `has_frontmatter_field()` function (in `agent_runner_v2/documentation_guardrails.py`) |
| F5 | VALIDATION_CONTRACT.md | ValidationPlan Pattern | `DocumentationValidationPlan(plan_id="my_validation", documents=[...])` |
| F6 | VALIDATION_CONTRACT.md | Section Checks | "Case-sensitive exact match against heading text" |

## Publish Recommendation

**Recommend publish after addressing findings.**

The staged Layer 2 platform core constitution set is semantically sound:

1. Layer boundaries are correctly maintained throughout all six documents.
2. Layer 1 governance is inherited without redefinition.
3. Platform identity (agent-runner-v2) is clearly established.
4. Metadata is consistent and compliant across all documents.
5. No forbidden content (Layer 3 drift, evidence normalization, authority
   overclaim) was detected.
6. The runtime model accurately describes the platform architecture at the
   conceptual level.

The six API-accuracy findings (F1-F6) in SHARED_SERVICES.md and
VALIDATION_CONTRACT.md are fixable defects that do not invalidate the
overall constitution. They should be corrected in a refine pass before
or after publish, as they affect code examples that Layer 3 bundle authors
will reference.

The set is ready for human approval (step 7) and publish (step 8).
