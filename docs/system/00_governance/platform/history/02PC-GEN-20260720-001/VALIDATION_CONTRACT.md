---
template_id: SYS-02-VC
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "permanent Layer 2 validation contract; defines the platform validation model shared across Layer 3 bundles"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "published"
effective_version: "02PC-GEN-20260720-001"
managed_by: workflow-generated
---

> Managed by workflow: `02_platform_core_foundation_v1` / step: `publish_platform_core_set`
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

1. **Metadata checks** - Frontmatter field presence and value validity.
2. **Section checks** - Required section headings present.
3. **File existence checks** - Required files present on disk.
4. **Content checks** - Forbidden content patterns absent.
5. **Cross-document checks** - Consistency across related documents.

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

- **Pass/fail status**: Overall plan outcome.
- **Per-document results**: Individual document check outcomes.
- **Findings**: Specific violations with document path, field or section,
  expected value, and actual value.
- **Summary statistics**: Total checks, passed, failed, skipped.

## Section Checks

### `has_section()`

Section checks verify that required section headings exist in a document.
The platform provides a `has_section()` helper that searches for Markdown
headings matching expected section names.

**Check approach:**

1. Parse the document for all Markdown headings (lines starting with `#`).
2. Match each expected section name against the parsed headings
   (case-insensitive, whitespace-normalized).
3. Report missing sections.

**Required sections are defined per template.** Each `template_id` maps
to a set of required section headings. For example:

| Template ID | Required Sections |
|---|---|
| `SYS-02-IDX` | Document Map, Platform Identity, Layer 1 Inheritance |
| `SYS-02-RM` | Step Model, Execution Paths, Job Lifecycle, Coder Integration, Rejection And Retry |
| `SYS-02-BAC` | Required Bundle Files, workflow.toml Format, Artifact Key Conventions, Bundle Governance Requirements, Metadata Compliance |
| `SYS-02-SS` | Context Extensions, Artifact Resolution, Path Contracts, Meta Sidecar, Notification Integration, Backend Sync Protocol, Action Registration |
| `SYS-02-MC` | Platform doc_type Values, Platform authority Values, Additional Frontmatter Fields, Inheritance Rules, Scan Policy Expectations |
| `SYS-02-VC` | ValidationPlan Pattern, Section Checks, Frontmatter Enforcement, File Existence Checks, Bundle Validator Composition |

### Section Check Rules

1. Section names are matched case-insensitively.
2. Leading/trailing whitespace is normalized before comparison.
3. Subsection headings (e.g., `### Subsection`) are not matched -
   only top-level headings (`#` or `##`) are checked.
4. A missing required section is a validation failure.
5. Extra sections beyond the required set are not an error.

## Frontmatter Enforcement

### `has_frontmatter_field()`

Frontmatter enforcement checks that YAML frontmatter fields exist and
have valid values. The platform validates frontmatter against:

1. **Layer 1 baseline** - Required fields and allowed vocabularies from
   `METADATA_STANDARD.md`.
2. **Layer 2 platform extensions** - Platform-specific fields from this
   platform's `METADATA_CONTRACT.md`.
3. **Template-specific requirements** - Required fields defined per
   `template_id`.

### Required Frontmatter by Document Class

**Permanent platform standards (`doc_type: "platform_standard"`):**

| Field | Required | Valid Values |
|---|---|---|
| `template_id` | Yes | Must match the document's assigned template ID. |
| `version` | Yes | Any non-empty string. |
| `doc_type` | Yes | `"platform_standard"` |
| `authority` | Yes | `"workflow-generated"` (draft) or `"platform-owned"` (published). |
| `scan_policy` | Yes | `"include"` for permanent standards. |
| `scan_reason` | Yes | Non-empty string. |
| `layer` | Yes | `"layer2"` |
| `platform` | Yes | `"agent-runner-v2"` |
| `lifecycle_status` | Yes | `"draft"` (staged) or `"published"` (active). |
| `effective_version` | Yes | The job ID that produced this version. |
| `managed_by` | Yes | `"workflow-generated"` |

**Temporary evidence (`doc_type: "review_artifact"`, `"validation_artifact"`, `"audit_artifact"`):**

| Field | Required | Valid Values |
|---|---|---|
| `doc_type` | Yes | One of `review_artifact`, `validation_artifact`, `audit_artifact`. |
| `authority` | Yes | `"workflow-generated"` or `"derived"`. |
| `scan_policy` | Yes | `"conditional"` or `"exclude"`. |
| `scan_reason` | Yes | Non-empty string. |
| `layer` | Yes | `"layer2"` or `"layer3"`. |
| `platform` | Yes | `"agent-runner-v2"`. |

### Frontmatter Violation Classes

| Violation | Example | Severity |
|---|---|---|
| Missing required field | No `template_id` on a permanent document | Error |
| Invalid value | `doc_type: "masterplan"` on a platform standard | Error |
| Wrong authority claim | `authority: "human-authored"` on workflow-generated content | Error |
| Missing `scan_reason` when required | `scan_policy: "exclude"` with empty `scan_reason` | Error |
| Wrong layer declaration | `layer: "layer1"` on a platform standard | Error |
| Wrong platform | `platform: "comfyui"` on an agent-runner-v2 document | Error |

## File Existence Checks

### Required File Inventory

Validation must confirm that all required permanent documents exist on
disk. For the platform core constitution set, the required inventory is:

1. `README.md` (template `SYS-02-IDX`)
2. `RUNTIME_MODEL.md` (template `SYS-02-RM`)
3. `BUNDLE_AUTHORING_CONTRACT.md` (template `SYS-02-BAC`)
4. `SHARED_SERVICES.md` (template `SYS-02-SS`)
5. `METADATA_CONTRACT.md` (template `SYS-02-MC`)
6. `VALIDATION_CONTRACT.md` (template `SYS-02-VC`)

### File Check Rules

1. Every file in the required inventory must exist.
2. Every file must have a non-zero size (not empty).
3. Every file must have valid YAML frontmatter delimited by `---`.
4. Sidecar files (`.meta.json`) are excluded from required-inventory
   checks. They are validated separately.
5. Missing required files is a validation failure.

### Sidecar Validation

For each permanent document, the corresponding `meta.json` sidecar is
checked:

1. The sidecar file must exist for each produced artifact.
2. The sidecar must contain valid JSON matching the v2 schema.
3. The `coder_result.status` must be `"APPROVED"` for the step to have
   succeeded.
4. The `coder_result.artifacts` map must include entries for all produced
   artifact keys.

## Bundle Validator Composition

### Platform Validators

The platform provides reusable validators that Layer 3 bundles compose
into their own validation plans:

1. **`validate_frontmatter`** - Checks frontmatter field presence and
   value validity against Layer 1 baseline and Layer 2 platform
   extensions.
2. **`validate_sections`** - Checks required section headings against
   template definitions.
3. **`validate_file_existence`** - Checks that required files exist on
   disk.
4. **`validate_ascii_only`** - Checks that output files contain only
   ASCII characters.
5. **`validate_no_layer1_redefinition`** - Checks for content patterns
   that modify Layer 1 governance.
6. **`validate_no_layer3_drift`** - Checks for bundle-specific content
   presented as platform-wide rules.

### Bundle-Local Validators

Layer 3 bundles define their own validators in `actions.py` using the
`@action()` decorator. Bundle-local validators extend platform validators
with:

- Bundle-specific required documents
- Bundle-specific required sections
- Bundle-specific frontmatter requirements
- Bundle-specific forbidden content patterns

### Composition Pattern

```python
from agent_runner_v2.actions.documentation_validation_core import (
    DocumentationValidationPlan,
    validate_frontmatter,
    validate_sections,
    validate_file_existence,
)

@action(name="validate_my_bundle")
def validate_my_bundle(context, state, step_config):
    plan = DocumentationValidationPlan(plan_id="my_bundle_validation")

    # Compose platform validators
    plan.add_check(validate_frontmatter(my_docs, my_requirements))
    plan.add_check(validate_sections(my_docs, my_template_map))
    plan.add_check(validate_file_existence(my_required_files))

    # Add bundle-specific checks
    plan.add_check(my_custom_content_check())

    result = plan.execute()
    return {
        "status": "APPROVED" if result.passed else "REJECTED",
        "remark": result.summary,
        "artifacts": {"VALIDATION_REPORT": str(result.report_path)},
    }
```

### Validation Scope

| Scope | Owned By | Examples |
|---|---|---|
| Layer 1 baseline checks | Platform | Frontmatter field presence, `doc_type`/`authority` vocabulary, scan-policy rules. |
| Layer 2 platform checks | Platform | `platform` field, `template_id` format, platform-specific frontmatter requirements. |
| Layer 3 bundle checks | Bundle | Bundle-specific document inventory, bundle-specific sections, bundle-specific content rules. |

Layer 3 bundles must not modify platform-level validation rules. They
compose platform validators and add bundle-specific checks.

## Guidance for Writing `validate_*` Actions

### When to Write a Validator

Write a `validate_*` action when:

- A workflow produces permanent documents that must meet structural
  requirements.
- Documents carry frontmatter that must be verified before publication.
- Required section headings must be confirmed present.
- Content must be checked for forbidden patterns (Layer 1 redefinition,
  Layer 3 drift, operational content).

Do not write a validator when:

- The check is a one-off review task better performed by a review prompt.
- The check requires semantic judgment that cannot be expressed
  deterministically.
- The check duplicates an existing platform validator.

### Validator Design Principles

1. **Deterministic**: The same input always produces the same result.
   Validation is not review - it checks structure, not quality.
2. **Composable**: Bundle validators compose platform validators. Do not
   reimplement platform checks.
3. **Fail-early**: Report the first violation clearly. Do not accumulate
   hundreds of findings before reporting.
4. **Actionable**: Every finding must cite the document path, the specific
   field or section, the expected value, and the actual value.
5. **Separate from review**: Validation checks structure and metadata.
   Review checks content quality and scope. Do not combine them into
   one step.

### Validator Output Contract

A `validate_*` action must return:

```python
{
    "status": "APPROVED",           # or "REJECTED"
    "remark": "N/N checks passed",  # Summary
    "artifacts": {
        "VALIDATION_REPORT": "path/to/validation-report.md",
    },
}
```

The validation report artifact must:

- List each check performed with pass/fail status.
- For each failure, cite the document, the field or section, the expected
  value, and the actual value.
- Include a summary with total checks, passed, failed, and skipped counts.
- Use ASCII only.

### Rejection Codes

Validators should use these rejection codes for routing decisions:

| Rejection Code | Meaning | Typical Route |
|---|---|---|
| `MISSING_DOCUMENT` | A required file is missing from the inventory. | `fail` |
| `MISSING_SECTION` | A required section heading is absent. | `refine` |
| `METADATA_NONCOMPLIANCE` | Frontmatter field missing or value invalid. | `refine` |
| `LAYER1_REDEFINITION` | Content modifies Layer 1 governance. | `fail` |
| `LAYER3_DRIFT` | Bundle-specific content presented as platform-wide. | `fail` |
| `NON_ASCII_CONTENT` | Output contains non-ASCII characters. | `refine` |
| `WRONG_DOCUMENT_INVENTORY` | The document set does not match the required set. | `fail` |
| `EVIDENCE_AS_STANDARD` | Temporary evidence classified as permanent standard. | `fail` |

### Validation in the Workflow Lifecycle

Validation runs after generation and refinement, before audit:

```
generate --> review --> refine --> validate --> audit --> human_approval --> publish
                                    ^             |
                                    |   (reject)  |
                                    +-------------+
```

If validation finds fixable defects (missing sections, metadata issues),
the workflow routes to refine. If validation finds unfixable defects
(wrong layer, drift), the workflow fails.
