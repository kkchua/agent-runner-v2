---
template_id: SYS-02-VC
version: "1.0"
doc_type: "platform_standard"
authority: "platform-owned"
scan_policy: "include"
scan_reason: "permanent Layer 2 validation contract; defines the platform validation model shared across Layer 3 bundles on agent-runner-v2"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "published"
effective_version: "02PC-GEN-20260721-009"
managed_by: workflow-generated
---

> Managed by workflow: `02_platform_core_foundation_v1` / step: `publish_platform_core_set`
> This file is workflow-generated and protected from manual edits.
> This file is workflow-generated and subject to review, validation, audit, and human approval before publication.

# Validation Contract

## Purpose

This document defines the platform validation model for agent-runner-v2.
It describes the `DocumentationValidationPlan` pattern, section-check
conventions, frontmatter enforcement, file existence checks, and how
Layer 3 bundles compose platform-level validators with bundle-local
checks.

## ValidationPlan Pattern

The platform provides a `DocumentationValidationPlan` class in
`agent_runner_v2.actions.documentation_validation_core`. This class
defines a reusable pattern for writing deterministic validation actions.

### Core Pattern

A `DocumentationValidationPlan` is a collection of named checks that
can be composed into a validation report. Each check:

1. Has a unique name.
2. Produces a pass/fail outcome.
3. Emits a diagnostic message on failure.
4. Can be grouped by category (structure, metadata, content, etc.).

### Validation Report

The validation plan produces a structured report containing:

- Overall pass/fail status
- Per-check results with diagnostic messages
- Summary statistics (total checks, passed, failed)

### Bundle Composition

Layer 3 bundles create their own validation plans by:

1. Instantiating the platform's `DocumentationValidationPlan`.
2. Adding bundle-specific checks (required files, required sections,
   artifact existence).
3. Adding inherited platform checks (frontmatter compliance, layer
   boundaries, forbidden content).
4. Running the plan and reporting results.

The platform validation module in
`agent_runner_v2.actions.documentation_validation_core` provides the
base class and helper functions. Bundle-specific validators extend or
instantiate this class.

## Section Checks

Section checks verify that a document contains required section
headings. The platform provides a `has_section()` helper.

### `has_section()` Convention

A section check verifies that a markdown document includes a specific
section heading:

```
## Section Heading Name
```

### Usage Pattern

```python
plan.add_check(
    name="required_section_runtime_model",
    category="structure",
    check=lambda: has_section(doc_content, "Step Model"),
    on_fail="RUNTIME_MODEL.md is missing required section: Step Model"
)
```

### Required Section Checks per Document

The platform constitution's `template_id` values encode required
section headings. For any document carrying a `template_id`, the
validator should cross-reference the template definition to verify
all required sections are present.

| Template ID | Document | Required Sections |
|---|---|---|
| `SYS-02-IDX` | `README.md` | Document Map, Platform Identity, Layer 1 Inheritance |
| `SYS-02-RM` | `RUNTIME_MODEL.md` | Step Model, Execution Paths, Job Lifecycle, Coder Integration, Rejection And Retry |
| `SYS-02-BAC` | `BUNDLE_AUTHORING_CONTRACT.md` | Required Bundle Files, workflow.toml Format, Artifact Key Conventions, Bundle Governance Requirements, Metadata Compliance |
| `SYS-02-SS` | `SHARED_SERVICES.md` | Context Extensions, Artifact Resolution, Path Contracts, Meta Sidecar, Notification Integration, Backend Sync Protocol, Action Registration |
| `SYS-02-MC` | `METADATA_CONTRACT.md` | Platform doc_type Values, Platform authority Values, Additional Frontmatter Fields, Inheritance Rules, Scan Policy Expectations |
| `SYS-02-VC` | `VALIDATION_CONTRACT.md` | ValidationPlan Pattern, Section Checks, Frontmatter Enforcement, File Existence Checks, Bundle Validator Composition |

Layer 3 bundles define their own `template_id` values and associated
required section lists in their bundle governance.

## Frontmatter Enforcement

Frontmatter checks verify that YAML frontmatter in markdown documents
meets the metadata contract. The platform provides a
`has_frontmatter_field()` helper.

### `has_frontmatter_field()` Convention

Checks that a document's frontmatter includes a specific field with a
valid value:

```python
plan.add_check(
    name="frontmatter_has_template_id",
    category="metadata",
    check=lambda: has_frontmatter_field(doc_content, "template_id"),
    on_fail="Document is missing required frontmatter field: template_id"
)
```

### Required Frontmatter Fields

Every permanent document on agent-runner-v2 must carry these frontmatter
fields:

| Field | Validation Rule |
|---|---|
| `template_id` | Must be present and non-empty. |
| `version` | Must be present and non-empty. |
| `doc_type` | Must be a recognized value from the Layer 1 baseline or platform extension. |
| `authority` | Must be a recognized value from the Layer 1 baseline or platform extension. |
| `scan_policy` | Must be `include`, `exclude`, or `conditional`. |
| `scan_reason` | Must be non-empty when `scan_policy` is `exclude` or `conditional`. |
| `layer` | Must be `layer1`, `layer2`, or `layer3`. |
| `platform` | Required for Layer 2 and Layer 3 docs. Must be `"agent-runner-v2"`. |
| `lifecycle_status` | Must be a recognized lifecycle status. |

### Value Validation

Beyond presence, validators should check:

- `authority: "human-authored"` must not appear on workflow-generated
  documents.
- `authority: "platform-owned"` must not appear on Layer 3 documents.
- `doc_type: "platform_standard"` must not appear on Layer 3 documents.
- `layer` must be consistent with the document's declared authority
  and doc_type.
- `managed_by` must be present on workflow-generated documents.

## File Existence Checks

### Required File Inventory

Validation must confirm that all declared artifact files exist on disk.
The platform's `_validate_artifact_files_exist()` and
`_validate_declared_produced_artifacts_exist()` functions in
`step_runner.py` perform this verification automatically for every step.

For Layer 3 bundle validators, the check pattern is:

```python
for artifact_key, relative_path in expected_artifacts.items():
    full_path = project_root / relative_path
    if not full_path.exists():
        plan.fail(f"Missing artifact: {artifact_key} -> {relative_path}")
```

### Directory Structure Checks

Validators should also verify that the expected directory structure
exists:

```
docs/system/00_governance/platform/
  runs/<job_id>/          -- staged artifacts present
  current/                -- has platform_set_manifest.json (if published)
```

### Canonical Path Usage

All validation file-existence checks must use canonical repo-relative
paths. Example (not schematic):

```
docs/system/00_governance/platform/current/README.md
docs/system/00_governance/platform/current/RUNTIME_MODEL.md
docs/system/00_governance/platform/current/BUNDLE_AUTHORING_CONTRACT.md
docs/system/00_governance/platform/current/SHARED_SERVICES.md
docs/system/00_governance/platform/current/METADATA_CONTRACT.md
docs/system/00_governance/platform/current/VALIDATION_CONTRACT.md
```

## Bundle Validator Composition

### How Layer 3 Bundles Use Platform Validators

Layer 3 bundles compose validation in a `validate_*` action function:

```python
from agent_runner_v2.actions.documentation_validation_core import (
    DocumentationValidationPlan,
)

@action("validate_my_output")
def validate_my_output(*, context, state, step_cfg, project_root):
    plan = DocumentationValidationPlan(name="my_bundle_validation")

    # 1. Inherited platform checks
    for check in platform_frontmatter_checks(context, project_root):
        plan.add_check(**check)

    # 2. Bundle-specific structure checks
    for doc_key in ["MY_OUTPUT", "MY_REPORT"]:
        doc_path = context.get(doc_key)
        if not doc_path:
            plan.fail(f"Missing context variable: {doc_key}")
            continue
        plan.add_check(
            name=f"file_exists_{doc_key}",
            category="existence",
            check=lambda p=Path(project_root) / doc_path: p.exists(),
            on_fail=f"File does not exist: {doc_key}"
        )

    # 3. Bundle-specific section checks
    for section in ["Purpose", "Design", "Implementation"]:
        plan.add_section_check(doc_key="MY_OUTPUT", section=section)

    # 4. Run and report
    plan.run()
    return plan.to_action_result()
```

### Separation of Concerns

- **Platform-level validation** -- Enforces Layer 2 metadata contract,
  frontmatter compliance, and platform-specific rules. Provided by the
  platform's validation module.

- **Bundle-level validation** -- Enforces bundle-specific structure,
  required sections, content rules, and artifact inventory. Defined in
  the bundle's own `validate_*` actions.

Bundles must not redefine platform-level validation logic. Instead,
they inherit platform checks and add bundle-specific checks on top.

### Guidance for Writing `validate_*` Actions

1. **Use the platform plan** -- Instantiate
   `DocumentationValidationPlan` from the platform module. Do not
   implement custom reporting logic.

2. **Inherit platform checks** -- Call the platform's frontmatter and
   structure check helpers first. These enforce Layer 1 and Layer 2
   compliance.

3. **Add bundle checks after** -- Bundle-specific checks should run
   after platform checks so that fundamental compliance issues are
   reported before bundle-specific structure issues.

4. **Return an ActionResult** -- The `to_action_result()` method
   converts the plan into a standard `ActionResult`. Set
   `status = "APPROVED"` only if all checks pass.

5. **Be deterministic** -- Validation checks must be deterministic.
   Do not use LLM-based checks in validation. Use LLM-based review
   for semantic quality; use validation for structural compliance.

6. **Report all failures** -- Do not short-circuit on the first
   failure. Run all checks and report a complete set of diagnostics.

7. **Use canonical paths** -- All file references in validation
   reports must use full repo-relative paths (e.g.,
   `docs/system/00_governance/platform/current/README.md`), not
   shortened or schematic paths.
