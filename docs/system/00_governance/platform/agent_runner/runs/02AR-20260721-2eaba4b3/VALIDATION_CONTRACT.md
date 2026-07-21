---
template_id: "SYS-02-VC"
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "permanent Layer 2 validation contract for agent-runner-v2"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02AR-20260721-2eaba4b3"
---

# agent-runner-v2 Validation Contract

This document defines the platform validation model shared across Layer 3 workflow bundles on agent-runner-v2.

## ValidationPlan Pattern

The platform provides a generic validation engine built on the `DocumentationValidationPlan` dataclass from `documentation_validation_core.py`.

### DocumentationValidationPlan

```python
@dataclass(frozen=True)
class DocumentationValidationPlan:
    required_folders: tuple[str, ...] = ()
    required_files: tuple[str, ...] = ()
    section_requirements: dict[str, tuple[str, ...]] = field(default_factory=dict)
    template_ids: dict[str, str] = field(default_factory=dict)
    extra_checkers: tuple[ValidationChecker, ...] = ()
```

The plan defines what the validator should check:

| Field | Type | Description |
|---|---|---|
| `required_folders` | `tuple[str, ...]` | Folder paths that must exist relative to the project root. |
| `required_files` | `tuple[str, ...]` | File paths that must exist relative to the project root. |
| `section_requirements` | `dict[str, tuple[str, ...]]` | Maps file paths to tuples of required section headings within each file. |
| `template_ids` | `dict[str, str]` | Maps file paths to expected `template_id` values in each file's frontmatter. |
| `extra_checkers` | `tuple[ValidationChecker, ...]` | Additional custom check functions to run beyond the standard checks. |

### Execution

The plan is executed by `validate_documentation_plan()`:

```python
def validate_documentation_plan(*, project_root: Path, plan: DocumentationValidationPlan) -> list[ValidationCheck]:
```

This function returns a list of `ValidationCheck` dictionaries, each containing:

- `check`: The check type (`"folder_structure"`, `"file_exists"`, `"file_section"`, `"template_id"`, or custom check names).
- `path`: The relative path being checked.
- `ok`: Boolean indicating whether the check passed.
- `detail`: Human-readable explanation of the result.
- Optional `section`, `field`, or `template_id` keys for specific check types.

### Bundle Composition

Layer 3 bundles compose the `DocumentationValidationPlan` for their own output validation:

1. Define required files matching the bundle's output artifact set.
2. Declare required section headings for each output file.
3. Map each output file to its expected `template_id`.
4. Add any bundle-specific extra checkers for custom validation logic.

The composition pattern is:

```python
from agent_runner_v2.actions.documentation_validation_core import (
    DocumentationValidationPlan,
    validate_documentation_plan,
)

plan = DocumentationValidationPlan(
    required_files=("docs/my_output/output.md", "docs/my_output/review.md"),
    section_requirements={
        "docs/my_output/output.md": ("Overview", "Analysis", "Recommendations"),
    },
    template_ids={
        "docs/my_output/output.md": "BUNDLE-01-OUT",
    },
)

checks = validate_documentation_plan(project_root=project_root, plan=plan)
```

## Section Checks

Section checks verify that generated documents contain the required section headings. The check is performed by the `has_section()` function:

```python
def has_section(content: str, section: str) -> bool:
```

This function performs a case-insensitive regex search for the given section name appearing as a Markdown heading (line starting with `#` characters). Section names are matched by text content, not by heading level -- `## Step Model` and `### Step Model` both match for section name `"Step Model"`.

### Section Check Behavior

- A section heading anywhere in the document (any level, any position) satisfies the check.
- The check is case-insensitive.
- Section names with special regex characters are escaped automatically.
- Missing sections are reported with the section name and file path for easy diagnosis.

### Required Sections per Platform Document

The platform itself uses the same validation pattern. Each permanent platform constitution document carries a `template_id` and required section headings:

| Document | template_id | Required Sections |
|---|---|---|
| `README.md` | `SYS-02-IDX` | Document Map, Platform Identity, Layer 1 Inheritance |
| `RUNTIME_MODEL.md` | `SYS-02-RM` | Step Model, Execution Paths, Job Lifecycle, Coder Integration, Rejection And Retry |
| `BUNDLE_AUTHORING_CONTRACT.md` | `SYS-02-BAC` | Required Bundle Files, workflow.toml Format, Artifact Key Conventions, Bundle Governance Requirements, Metadata Compliance |
| `SHARED_SERVICES.md` | `SYS-02-SS` | Context Extensions, Artifact Resolution, Path Contracts, Meta Sidecar, Notification Integration, Backend Sync Protocol, Action Registration |
| `METADATA_CONTRACT.md` | `SYS-02-MC` | Platform doc_type Values, Platform authority Values, Additional Frontmatter Fields, Inheritance Rules, Scan Policy Expectations |
| `VALIDATION_CONTRACT.md` | `SYS-02-VC` | ValidationPlan Pattern, Section Checks, Frontmatter Enforcement, File Existence Checks, Bundle Validator Composition |

## Frontmatter Enforcement

Frontmatter checks verify that generated documents carry the required YAML frontmatter fields. The check is performed by `has_frontmatter_field()`:

```python
def has_frontmatter_field(content: str, field: str) -> bool:
```

This function searches for the field name followed by a colon in the document's frontmatter block (between `---` delimiters at the start of the file).

### Platform Frontmatter Requirements

Every permanent agent-runner-v2 document must carry:

| Field | Required | Valid Values |
|---|---|---|
| `template_id` | Yes | Must match the document's expected `template_id` from the platform registry. |
| `version` | Yes | Semver or version identifier string. |
| `doc_type` | Yes | Must be a valid Layer 1 or Layer 2 `doc_type` value. Permanent platform docs use `"platform_standard"`. |
| `authority` | Yes | Must be a valid Layer 1 or Layer 2 `authority` value. |
| `scan_policy` | Yes | Must be `"include"`, `"exclude"`, or `"conditional"`. |
| `scan_reason` | Yes | Non-empty explanation of the scan policy. |
| `layer` | Yes | Must be `"layer2"` for platform documents, `"layer3"` for bundle documents. |
| `platform` | Yes | Must be `"agent-runner-v2"`. |
| `lifecycle_status` | Yes | Must be a valid lifecycle state. Staged docs use `"draft"`; published docs use `"published"`. |
| `effective_version` | Yes | The run or change identifier for this version. |

### Template ID Validation

The validator checks that each document's frontmatter contains the `template_id` field and that the expected value appears in the document content. This ensures the document self-identifies correctly and the template assignment matches.

## File Existence Checks

File existence checks verify that declared output files actually exist on disk. These are the most basic validation checks and are always performed first.

### Standard File Checks

The `check_file_exists()` function returns `(ok, detail)` for a given relative path:

```python
def check_file_exists(project_root: Path, rel_path: str) -> tuple[bool, str]:
```

The platform validation engine checks every file in `required_files` for existence. Files that do not exist are reported with their relative path and a "missing" detail message.

### Folder Structure Checks

The `check_folder_exists()` function performs the same check for directories:

```python
def check_folder_exists(project_root: Path, rel_path: str) -> tuple[bool, str]:
```

When a folder exists, the detail message includes the count of items within the folder.

### Artifact Existence Enforcement

Beyond the validation plan's file checks, the runner enforces artifact existence at runtime through `_validate_artifact_files_exist()` in `step_runner.py`. After reading the meta.json, the runner verifies that every artifact path claimed in the sidecar corresponds to a file that exists on disk. Missing artifacts cause the step to fail with `ArtifactMissingError`.

## Bundle Validator Composition

Layer 3 bundles build their own validation actions by composing the platform's validation primitives.

### Pattern for validate_* Actions

A typical bundle validation action follows this pattern:

1. **Instantiate a `DocumentationValidationPlan`** with the bundle's required files, section requirements, and template IDs.
2. **Call `validate_documentation_plan()`** to run the standard checks.
3. **Add bundle-specific extra checks** by appending to the check list or using `extra_checkers`.
4. **Produce a validation report** as a Markdown artifact listing passed and failed checks.
5. **Return `APPROVED`** if all checks pass, or `REJECTED` with a reject code if any check fails.

### Example Pattern

```python
@action("validate_my_bundle_outputs")
def validate_my_bundle_outputs(*, context, state, step_cfg, project_root):
    plan = DocumentationValidationPlan(
        required_files=("docs/my_output/analysis.md", "docs/my_output/summary.md"),
        section_requirements={
            "docs/my_output/analysis.md": ("Overview", "Findings", "Conclusions"),
            "docs/my_output/summary.md": ("Summary", "Next Steps"),
        },
        template_ids={
            "docs/my_output/analysis.md": "MYBUNDLE-01",
            "docs/my_output/summary.md": "MYBUNDLE-02",
        },
    )
    checks = validate_documentation_plan(project_root=project_root, plan=plan)

    # Bundle-specific extra checks
    checks.append(check_custom_rule(project_root))

    failed = [c for c in checks if not c["ok"]]
    if failed:
        # Write validation report artifact
        return ActionResult(
            status="REJECTED",
            remark=f"Validation failed: {len(failed)} checks.",
            artifacts={"VALIDATION_REPORT": "docs/my_output/validation.md"},
            reject_code="BUNDLE_VALIDATION_FAILED",
        )
    return ActionResult(
        status="APPROVED",
        remark="All validation checks passed.",
        artifacts={"VALIDATION_REPORT": "docs/my_output/validation.md"},
    )
```

### Distinction from Platform Validation

Bundle-level validation is separate from platform-level validation:

- **Platform validation** checks the platform constitution documents against platform rules (this document's own contract). It is owned by Layer 2.
- **Bundle validation** checks bundle-generated outputs against bundle-specific rules. It is owned by Layer 3 and composed from platform primitives.

Bundle validators must not:
- Claim to validate platform-wide standards.
- Redefine the meaning of platform validation check types.
- Produce validation artifacts that claim `platform-owned` authority.

Bundle validators should:
- Use the platform `DocumentationValidationPlan` and validation primitives.
- Produce validation artifacts with `doc_type: "validation_artifact"` and `authority: "workflow-generated"`.
- Store validation artifacts alongside bundle outputs, not in the platform governance directory.
