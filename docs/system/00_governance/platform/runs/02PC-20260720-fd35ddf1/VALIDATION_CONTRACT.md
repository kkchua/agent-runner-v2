---
template_id: SYS-02-VC
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "permanent Layer 2 validation contract; defines the platform validation model shared across Layer 3 bundles"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02PC-20260720-fd35ddf1"
managed_by: workflow-generated
---

> Managed by workflow: `02_platform_core_foundation_v1` / step: `generate_platform_core_docs`
> This file is workflow-generated and protected from manual edits.

# Validation Contract

## Overview

This document defines the platform validation model for agent-runner-v2.
It establishes the `DocumentationValidationPlan` pattern, section-check
conventions, frontmatter enforcement rules, file existence checks, bundle
validator composition, and guidance for writing validation actions in
Layer 3 workflows.

The validation model is shared across all Layer 3 bundles. Each bundle
composes platform-level validators with bundle-specific checks to produce
a complete validation plan.

## ValidationPlan Pattern

### `DocumentationValidationPlan`

The platform provides a `DocumentationValidationPlan` class (in
`agent_runner_v2/actions/documentation_validation_core.py`) that defines
a structured validation plan for governed documents.

A validation plan consists of:

1. **Metadata checks** : Frontmatter field presence and value validity.
2. **Section checks** : Required section headings present in the document
   body.
3. **File existence checks** : Required files present on disk.
4. **Content checks** : Forbidden content patterns absent.
5. **Cross-document checks** : Consistency across related documents.

### Plan Structure

```python
from agent_runner_v2.actions.documentation_validation_core import (
    DocumentationValidationPlan,
)

plan = DocumentationValidationPlan(
    plan_id="my_validation",
    documents=[
        {
            "path": Path("path/to/doc.md"),
            "template_id": "SYS-02-RM",
            "required_sections": ["Step Model", "Execution Paths", "Job Lifecycle"],
            "required_frontmatter": {
                "template_id": "SYS-02-RM",
                "doc_type": "platform_standard",
                "layer": "layer2",
                "platform": "agent-runner-v2",
            },
        },
    ],
)
```

### Plan Execution

A validation plan returns a result with:

- **Pass/fail status** : Overall plan outcome. Fails if any document has
  unresolved violations.
- **Per-document results** : Individual document check outcomes with
  specific violations.
- **Findings** : Specific violations with document path, field or section,
  expected value, and actual value.

### Plan Composition

Layer 3 bundles compose platform validators by:

1. Importing the platform's `DocumentationValidationPlan`.
2. Defining bundle-specific document entries with required sections and
   frontmatter.
3. Adding bundle-specific content checks and cross-document consistency
   rules.
4. Executing the plan through a `validate_*` action.

## Section Checks

### `has_section()`

The platform provides a `has_section()` function (in
`agent_runner_v2/documentation_guardrails.py`) that checks whether a
document contains a required section heading.

**Signature:**

```python
def has_section(content: str, heading: str) -> bool:
    """Return True if the document contains the given markdown heading."""
```

**Heading matching:**

- Matches markdown headings of any level (`#`, `##`, `###`, etc.)
- Case-sensitive exact match against heading text
- Does not match substrings or partial heading text

### Section Check Conventions

When defining required sections for a document:

1. **Use the exact heading text** as it appears in the document
   specification. Example: `"Step Model"`, not `"step model"` or
   `"Step model"`.
2. **List only top-level requirements** : the validator checks for
   existence, not for content quality.
3. **Keep section lists stable** : changing required sections is a
   governance change that should be reviewed.

### Section Check Usage

```python
from agent_runner_v2.documentation_guardrails import has_section

content = read_document("path/to/doc.md")
if not has_section(content, "Step Model"):
    report_violation("Missing required section: Step Model")
```

### Required Sections Per Document Type

When defining a `DocumentationValidationPlan`, required sections are
specified per document entry. The platform constitution documents have
these required sections (see individual document specifications for the
full list):

| Template ID | Required Sections (abbreviated) |
|---|---|
| `SYS-02-IDX` | Document Map, Platform Identity, Layer 1 Inheritance |
| `SYS-02-RM` | Step Model, Execution Paths, Job Lifecycle, Coder Integration, Rejection And Retry |
| `SYS-02-BAC` | Required Bundle Files, workflow.toml Format, Artifact Key Conventions, Bundle Governance Requirements, Metadata Compliance |
| `SYS-02-SS` | Context Extensions, Artifact Resolution, Path Contracts, Meta Sidecar, Notification Integration, Backend Sync Protocol, Action Registration |
| `SYS-02-MC` | Platform doc_type Values, Platform authority Values, Additional Frontmatter Fields, Inheritance Rules, Scan Policy Expectations |
| `SYS-02-VC` | ValidationPlan Pattern, Section Checks, Frontmatter Enforcement, File Existence Checks, Bundle Validator Composition |

## Frontmatter Enforcement

### `has_frontmatter_field()`

The platform provides a `has_frontmatter_field()` function (in
`agent_runner_v2/documentation_guardrails.py`) that checks whether a
document's YAML frontmatter contains a required field with a valid value.

**Signature:**

```python
def has_frontmatter_field(
    frontmatter: dict,
    field: str,
    expected_value: str | None = None,
) -> bool:
    """Return True if the frontmatter has the field with the expected value."""
```

**Parameters:**

- `frontmatter` : Parsed YAML frontmatter dictionary.
- `field` : Field name to check.
- `expected_value` : Optional expected value for the field.

**Example:**

```python
frontmatter = parse_frontmatter("path/to/doc.md")
if not has_frontmatter_field(frontmatter, "doc_type", "platform_standard"):
    report_violation("doc_type must be platform_standard")
```

### Required Frontmatter Fields

The platform enforces these frontmatter fields on permanent documents:

| Field | Check Type | Description |
|---|---|---|
| `template_id` | Presence + exact match | Must match the expected template ID for the document. |
| `version` | Presence | Must be present and non-empty. |
| `doc_type` | Presence + value in allowed set | Must be a valid `doc_type` value. |
| `authority` | Presence + value in allowed set | Must be a valid `authority` value. |
| `scan_policy` | Presence + value in allowed set | Must be `include`, `exclude`, or `conditional`. |
| `scan_reason` | Presence + non-empty | Required when `scan_policy` is `exclude` or `conditional`. |
| `layer` | Presence + exact match | Must match the owning layer (`layer1`, `layer2`, `layer3`). |
| `platform` | Presence + exact match | Must be `agent-runner-v2` for documents on this platform. |
| `lifecycle_status` | Presence | Must be present (`draft` or `published`). |
| `effective_version` | Conditional presence | Required for workflow-generated permanent documents. |
| `managed_by` | Conditional presence | Required for workflow-generated documents. |

### Allowed Value Enforcement

The validator checks that `doc_type`, `authority`, `scan_policy`, and
`layer` values belong to the allowed vocabulary (Layer 1 baseline plus
Layer 2 platform extensions).

### Frontmatter by Document Class

| Document Class | Required `doc_type` | Required `authority` | Required `layer` |
|---|---|---|---|
| Layer 2 constitution (permanent) | `platform_standard` | `platform-owned` or `workflow-generated` | `layer2` |
| Layer 2 evidence (temporary) | `review_artifact`, `validation_artifact`, or `audit_artifact` | `workflow-generated` or `derived` | `layer2` |
| Layer 3 permanent output | `workflow_output` or `bundle_definition` | `bundle-owned` or `workflow-generated` | `layer3` |
| Layer 3 evidence | `review_artifact`, `validation_artifact`, or `audit_artifact` | `workflow-generated` or `derived` | `layer3` |

## File Existence Checks

### File Inventory Validation

The validator checks that required files exist on disk at their expected
paths. The file inventory is defined per document in the
`DocumentationValidationPlan`.

**Check types:**

- **Single file existence** : A specific file must exist at an exact path.
- **Directory existence** : A directory must exist with at least one
  matching file.
- **Directory non-empty** : A directory must contain at least one file.

### Path Convention

All file paths in validation plans must use absolute paths. The validator
does not resolve relative paths. The workflow bundle's context extensions
or output path contracts should provide absolute paths to the validator.

### File Set Validation

For governed document sets (e.g., the six-document platform constitution),
the validator checks that the complete set of required files exists. A
missing document in the set is a failing validation.

## Bundle Validator Composition

### Composing Platform Validators

Layer 3 bundles compose platform validators by:

1. **Importing platform validation primitives** : `DocumentationValidationPlan`,
   `has_section()`, `has_frontmatter_field()`.
2. **Defining bundle-specific documents** : Adding entries for each
   document the bundle produces.
3. **Adding bundle-specific checks** : Content rules, cross-document
   consistency, forbidden patterns.
4. **Wrapping in a validate action** : Registering the validation plan
   execution as a `@action(name="validate_*")`.

### Validation Action Pattern

```python
# In actions.py of the workflow bundle

from agent_runner_v2.actions.documentation_validation_core import (
    DocumentationValidationPlan,
)
from agent_runner_v2.actions import action

@action(name="validate_my_outputs")
def validate_my_outputs(*, state, step_cfg, job_dir, context):
    plan = DocumentationValidationPlan(
        plan_id="my_bundle_validation",
        documents=[
            {
                "path": Path(context["MY_OUTPUT_PATH"]),
                "required_sections": ["Required Section 1", "Required Section 2"],
                "required_frontmatter": {
                    "doc_type": "workflow_output",
                    "layer": "layer3",
                    "platform": "agent-runner-v2",
                },
            },
        ],
    )
    result = plan.execute()
    return {
        "status": "APPROVED" if result.passed else "REJECTED",
        "remark": result.summary(),
        "artifacts": {},
    }
```

### Platform vs Bundle Validation

| Aspect | Platform Validation | Bundle Validation |
|---|---|---|
| Scope | All documents on the platform | Bundle-owned documents only |
| Rules | Layer 1 + Layer 2 metadata compliance, ASCII-only, platform identity | Bundle-specific sections, content rules, cross-document consistency |
| Execution | Platform core workflow (`validate` step) | Bundle workflow (`validate_*` action) |
| Failure | Blocks platform constitution publication | Blocks bundle output publication |

### Validation Guidance

When writing bundle validators:

1. **Do not revalidate Layer 1 compliance** : Platform validators handle
   metadata vocabulary and structural compliance. Bundle validators check
   bundle-specific requirements.
2. **Use platform primitives** : Always use `has_section()` and
   `has_frontmatter_field()` from the platform rather than implementing
   custom checks.
3. **Keep validators deterministic** : Validation must produce the same
   result for the same inputs. No LLM calls in validators.
4. **Report specific violations** : Include the document path, the field
   or section, the expected value, and the actual value for every
   violation.
5. **Separate validation from review** : Validators check machine-checkable
   rules (metadata, sections, file existence). Reviewers check semantic
   quality, scope, and correctness.
