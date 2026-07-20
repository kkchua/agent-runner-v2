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
effective_version: "02PC-GEN-20260720-002"
---

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
    MetadataCheck,
    SectionCheck,
    FileExistenceCheck,
    ContentCheck,
)

plan = DocumentationValidationPlan(
    name="platform_core_validation",
    description="Validate the Layer 2 platform core constitution set",
    metadata_checks=[...],
    section_checks=[...],
    file_existence_checks=[...],
    content_checks=[...],
    cross_document_checks=[...],
)
```

### Validation Result

The plan executes all checks and produces a `ValidationResult` with:

- `passed`: Boolean indicating overall pass/fail.
- `failures`: List of individual check failures with details.
- `warnings`: List of non-fatal warnings.
- `summary`: Human-readable summary of findings.

## Section Checks

### `SectionCheck`

Section checks verify that required section headings exist in a document.

```python
SectionCheck(
    document="README.md",
    required_sections=["Document Map", "Platform Identity", "Layer 1 Inheritance"],
    description="README.md must contain the required platform index sections",
)
```

### `has_section()` Convention

Validation actions use the `has_section()` helper to verify section
presence:

```python
def has_section(content: str, heading: str) -> bool:
    """Check if a markdown heading exists in the document content."""
    import re
    pattern = rf"^#+\s+{re.escape(heading)}\s*$"
    return bool(re.search(pattern, content, re.MULTILINE))
```

### Required Sections Per Document

Each platform constitution document has a defined set of required section
headings. Validators check for these predefined sets per the document's
`template_id`.

| Document | Template ID | Required Sections |
|---|---|---|
| `README.md` | `SYS-02-IDX` | Document Map, Platform Identity, Layer 1 Inheritance |
| `RUNTIME_MODEL.md` | `SYS-02-RM` | Step Model, Execution Paths, Job Lifecycle, Coder Integration, Rejection And Retry |
| `BUNDLE_AUTHORING_CONTRACT.md` | `SYS-02-BAC` | Required Bundle Files, workflow.toml Format, Artifact Key Conventions, Bundle Governance Requirements, Metadata Compliance |
| `SHARED_SERVICES.md` | `SYS-02-SS` | Context Extensions, Artifact Resolution, Path Contracts, Meta Sidecar, Notification Integration, Backend Sync Protocol, Action Registration |
| `METADATA_CONTRACT.md` | `SYS-02-MC` | Platform doc_type Values, Platform authority Values, Additional Frontmatter Fields, Inheritance Rules, Scan Policy Expectations |
| `VALIDATION_CONTRACT.md` | `SYS-02-VC` | ValidationPlan Pattern, Section Checks, Frontmatter Enforcement, File Existence Checks, Bundle Validator Composition |

## Frontmatter Enforcement

### `MetadataCheck`

Metadata checks verify that required YAML frontmatter fields exist with
valid values.

```python
MetadataCheck(
    field="doc_type",
    allowed_values={"platform_standard", "system", "bundle_definition", "workflow_output"},
    description="doc_type must be a valid Layer 1 or Layer 2 value",
)
```

### Required Frontmatter Fields

All governed documents on this platform must carry these frontmatter
fields:

| Field | Required | Validation |
|---|---|---|
| `doc_type` | Yes | Must be a valid Layer 1 or Layer 2 value. |
| `authority` | Yes | Must be a valid Layer 1 or Layer 2 value. |
| `scan_policy` | Yes | Must be `include`, `conditional`, or `exclude`. |
| `scan_reason` | Yes | Must be non-empty. |
| `layer` | Yes | Must be `"layer1"`, `"layer2"`, or `"layer3"`. |
| `template_id` | Conditional | Required on permanent platform standards and bundle outputs with defined templates. |
| `lifecycle_status` | Yes | Must be `"draft"`, `"published"`, or `"superseded"`. |
| `effective_version` | Yes | Must be non-empty (typically a job ID). |

### `has_frontmatter_field()`

Validators use `has_frontmatter_field()` to check for field presence:

```python
def has_frontmatter_field(content: str, field: str) -> bool:
    """Check if a YAML frontmatter field exists in the document."""
    import re
    import yaml

    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return False
    try:
        frontmatter = yaml.safe_load(match.group(1))
        return field in (frontmatter or {})
    except yaml.YAMLError:
        return False
```

### Value Validation

Beyond presence, validators check that values belong to allowed sets:

- `doc_type` must match a Layer 1 baseline or Layer 2 extension value.
- `authority` must match a Layer 1 baseline or Layer 2 extension value.
- `scan_policy` must be one of `include`, `conditional`, `exclude`.
- `layer` must be `layer2` for platform standards.
- `platform` must be `"agent-runner-v2"` for platform-owned documents.
- `lifecycle_status` must be `"draft"` for staged outputs.

## File Existence Checks

### `FileExistenceCheck`

File existence checks verify that required files exist on disk.

```python
FileExistenceCheck(
    expected_files=[
        "README.md",
        "RUNTIME_MODEL.md",
        "BUNDLE_AUTHORING_CONTRACT.md",
        "SHARED_SERVICES.md",
        "METADATA_CONTRACT.md",
        "VALIDATION_CONTRACT.md",
    ],
    description="All six permanent platform constitution files must exist",
)
```

### Directory Structure Checks

Beyond individual files, validators may check directory structure:

- The output directory contains exactly the expected document set.
- No unexpected files are present (excluding evidence artifacts with
  `scan_policy: "conditional"` or `"exclude"`).
- Sidecar files (`.meta.json`) are excluded from file-existence
  validation against the permanent set.

### Skip Sidecar Files

`.meta.json` sidecar files are excluded from artifact existence
validation. The validator checks for content files only; sidecars are
runtime infrastructure, not governed artifacts.

## Bundle Validator Composition

### Platform-to-Bundle Hierarchy

Validation follows a composition hierarchy:

1. **Platform validators** (in `agent_runner_v2/actions/`) define checks
   applicable to all Layer 3 bundles:
   - Metadata compliance checks
   - File existence checks for common patterns
   - ASCII-only output checks
   - Frontmatter field presence checks

2. **Bundle validators** (in the bundle's `actions.py`) add
   bundle-specific checks:
   - Required artifact inventory for this bundle
   - Bundle-specific section requirements
   - Bundle-specific content rules
   - Bundle-local path contracts

### Composing Validators

A Layer 3 bundle's `validate_*` action should compose platform validators
with bundle-specific checks:

```python
from agent_runner_v2.actions import run_validation_plan

def validate_my_bundle(state, context, env):
    plan = build_platform_validation_plan()  # inherited
    plan.add_bundle_checks(build_my_bundle_checks())  # bundle-specific
    result = run_validation_plan(plan)
    # Write meta.json with result
```

### Distinction: Platform vs Bundle Checks

| Check Type | Owned By | Examples |
|---|---|---|
| Platform-level | Platform core | Frontmatter field presence, `doc_type` value validity, `layer` field check, ASCII-only output, scan policy compliance |
| Bundle-level | Layer 3 bundle | Required bundle artifact inventory, bundle-specific sections, bundle-specific content rules, output path contract compliance |

## Guidance for Writing `validate_*` Actions

### Principles

1. **Deterministic**: Validation actions must be deterministic. Same inputs
   must produce the same results. No LLM calls, no network dependency.

2. **Explicit failures**: Every failure must cite the specific document,
   field, or section that failed, with the expected and actual values.

3. **Metadata first**: Check frontmatter compliance before content checks.
   A document with missing metadata cannot be properly classified for
   further checks.

4. **Separate evidence from standards**: Validation artifacts are evidence.
   They carry `scan_policy: "conditional"` or `"exclude"` and must not be
   treated as permanent platform standards.

5. **Fail fast on structure**: If required files are missing or required
   sections are absent, report immediately. Do not attempt content checks
   on structurally invalid documents.

6. **Bundle-local checks are additive**: Platform validators run first.
   Bundle checks add constraints but never relax platform requirements.

### Action Structure

A `validate_*` action typically follows this pattern:

```python
@action(name="validate_my_outputs")
def validate_my_outputs(state, context, env):
    failures = []
    warnings = []

    # 1. Check file existence
    for file_path in REQUIRED_FILES:
        if not Path(file_path).exists():
            failures.append(f"Required file missing: {file_path}")

    # 2. Check metadata compliance
    for file_path in REQUIRED_FILES:
        content = Path(file_path).read_text(encoding="utf-8")
        for field in REQUIRED_FIELDS:
            if not has_frontmatter_field(content, field):
                failures.append(f"{file_path}: missing frontmatter field '{field}'")

    # 3. Check required sections
    for file_path, sections in REQUIRED_SECTIONS.items():
        content = Path(file_path).read_text(encoding="utf-8")
        for section in sections:
            if not has_section(content, section):
                failures.append(f"{file_path}: missing section '{section}'")

    # 4. Check forbidden content
    for file_path, patterns in FORBIDDEN_PATTERNS.items():
        content = Path(file_path).read_text(encoding="utf-8")
        for pattern in patterns:
            if re.search(pattern, content):
                failures.append(f"{file_path}: forbidden pattern '{pattern}' found")

    # 5. Write result
    status = "APPROVED" if not failures else "REJECTED"
    remark = "Validation passed" if not failures else f"Validation failed: {len(failures)} issues"
    write_meta_sidecar(
        meta_path,
        status=status,
        remark=remark,
        artifacts={"VALIDATION_REPORT": str(report_path)},
    )
```

### Validation Scope Rules

- Validate only files this workflow owns. Do not scan unrelated
  directories.
- Validate against the declared artifact registry in
  `bundle_governance.toml`.
- Distinguish between fatal failures (must fix) and warnings (should
  review).
- Report every failure individually, not as a single aggregated message.
