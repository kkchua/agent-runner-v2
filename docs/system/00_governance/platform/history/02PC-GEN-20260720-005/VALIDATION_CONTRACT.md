---
template_id: SYS-02-VC
version: "1.0"
doc_type: "platform_standard"
authority: "platform-owned"
scan_policy: "include"
scan_reason: "permanent Layer 2 validation contract; defines the platform validation model"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "published"
effective_version: "02PC-GEN-20260720-005"
managed_by: workflow-generated
---

> Managed by workflow: `02_platform_core_foundation_v1` / step: `publish_platform_core_set`
> This file is workflow-generated and protected from manual edits.

# Validation Contract

## Purpose

This document defines the platform validation model for agent-runner-v2.
It describes the `DocumentationValidationPlan` pattern, section-check
conventions, frontmatter enforcement, file existence checks, and how
Layer 3 bundles compose platform validators. It also provides guidance
for writing `validate_*` actions in Layer 3 workflows.

This contract ensures that validation across the platform is consistent,
deterministic, and composable.

## ValidationPlan Pattern

The platform provides a structured validation plan pattern through the
`DocumentationValidationPlan` dataclass in
`actions/documentation_validation_core.py`.

### Dataclass Definition

```python
@dataclass(frozen=True)
class DocumentationValidationPlan:
    required_folders: tuple[str, ...] = ()
    required_files: tuple[str, ...] = ()
    section_requirements: dict[str, tuple[str, ...]] = field(default_factory=dict)
    template_ids: dict[str, str] = field(default_factory=dict)
    extra_checkers: tuple[ValidationChecker, ...] = ()
```

### Fields

| Field | Type | Purpose |
|---|---|---|
| `required_folders` | Tuple of relative paths | Folders that must exist in the project. |
| `required_files` | Tuple of relative paths | Files that must exist in the project. |
| `section_requirements` | Dict mapping file paths to required section headings | Each key is a relative file path; each value is a tuple of section heading substrings that must appear as markdown headings in that file. |
| `template_ids` | Dict mapping file paths to expected template IDs | Each key is a relative file path; each value is the expected `template_id` value in that file's frontmatter. |
| `extra_checkers` | Tuple of callable checkers | Custom validation functions that receive the project root and return a list of `ValidationCheck` dictionaries. |

### Execution

The `validate_documentation_plan()` function in
`documentation_validation_core.py` executes a plan and returns a list of
`ValidationCheck` dictionaries. Each check contains:

- `check`: the check type (e.g., `folder_structure`, `file_exists`,
  `file_section`, `template_id`).
- `path`: the file or folder path being checked.
- `ok`: boolean indicating pass or fail.
- `detail`: human-readable detail about the result.
- `section`: (for section checks) the section heading being verified.
- `template_id`: (for template checks) the expected template identifier.

### Composition

Validation plans are composable. A Layer 3 bundle can:

1. Define its own `DocumentationValidationPlan` for bundle-local checks.
2. Reference platform-level validators for cross-cutting concerns.
3. Add custom `extra_checkers` for bundle-specific validation logic.
4. Combine multiple plans by merging their check results.

## Section Checks

The platform provides a section-check helper through the `has_section()`
function in `documentation_validation_core.py`.

### Pattern

```python
def has_section(content: str, section: str) -> bool:
    pattern = re.compile(
        rf"^#+\s+.*{re.escape(section)}",
        re.MULTILINE | re.IGNORECASE,
    )
    return bool(pattern.search(content))
```

### Rules

- Section checks match markdown headings at any level (`#` through
  `######`).
- Matching is case-insensitive.
- The section parameter is a substring match against the heading text.
- A heading containing the section substring is considered a match.

### Usage in Validation Plans

Section requirements are declared in the `section_requirements` field of
`DocumentationValidationPlan`. The key is the relative file path, and the
value is a tuple of required section heading substrings.

Example:

```python
DocumentationValidationPlan(
    section_requirements={
        "docs/system/00_governance/platform/current/README.md": (
            "Document Map",
            "Platform Identity",
            "Layer 1 Inheritance",
        ),
    },
)
```

## Frontmatter Enforcement

The platform provides frontmatter field checking through the
`has_frontmatter_field()` function in `documentation_validation_core.py`.

### Pattern

```python
def has_frontmatter_field(content: str, field: str) -> bool:
    pattern = re.compile(
        rf"^\s*-?\s*{re.escape(field)}\s*[:]",
        re.MULTILINE,
    )
    return bool(pattern.search(content))
```

### Rules

- Frontmatter field checks look for YAML key-value patterns in the
  document's frontmatter block.
- The field parameter matches the key name before the colon separator.
- This function checks for field presence, not value validity. Value
  validation requires additional custom checkers.

### Required Frontmatter Fields

Based on the Metadata Contract (`METADATA_CONTRACT.md`), permanent
documents on this platform must include at least:

- `template_id`
- `version`
- `doc_type`
- `authority`
- `scan_policy`
- `scan_reason`
- `layer`
- `platform`
- `lifecycle_status`
- `effective_version`

### Validation Approach

Validators should check frontmatter fields in two passes:

1. **Presence check**: verify all required fields exist using
   `has_frontmatter_field()`.
2. **Value check**: verify field values belong to allowed vocabularies
   (custom checker logic).

## File Existence Checks

The platform provides file and folder existence helpers through
`check_file_exists()` and `check_folder_exists()` in
`documentation_validation_core.py`.

### File Check

```python
def check_file_exists(project_root: Path, rel_path: str) -> tuple[bool, str]:
    full = project_root / rel_path
    if full.exists() and full.is_file():
        return True, f"exists ({full.stat().st_size} bytes)"
    return False, f"missing at {rel_path}"
```

### Folder Check

```python
def check_folder_exists(project_root: Path, rel_path: str) -> tuple[bool, str]:
    full = project_root / rel_path
    if full.exists() and full.is_dir():
        count = len(list(full.iterdir()))
        return True, f"exists ({count} items)"
    return False, f"missing at {rel_path}"
```

### Usage in Validation Plans

File and folder requirements are declared in the `required_files` and
`required_folders` fields of `DocumentationValidationPlan`. Paths are
relative to the project root.

## Bundle Validator Composition

Layer 3 bundles compose validators by combining platform-level validation
with bundle-local checks.

### Platform-Level Validators

The platform provides shared validation infrastructure:

- `DocumentationValidationPlan` for structured check definitions.
- `validate_documentation_plan()` for plan execution.
- `has_section()`, `has_frontmatter_field()`, `check_file_exists()`,
  `check_folder_exists()` for individual checks.

### Bundle-Local Validators

Each Layer 3 bundle may define its own validation logic in:

- The bundle's `actions.py` module using the `@action()` decorator to
  register `validate_*` action functions.
- Custom `ValidationChecker` callables passed via the `extra_checkers`
  field of `DocumentationValidationPlan`.

### Composition Pattern

A Layer 3 bundle's validation step should:

1. Define a `DocumentationValidationPlan` with bundle-specific
   `required_files`, `required_folders`, `section_requirements`, and
   `template_ids`.
2. Add custom `extra_checkers` for bundle-specific rules (e.g., artifact
   key compliance, prompt template structure).
3. Execute the plan using `validate_documentation_plan()`.
4. Report results as a validation artifact.

### Workflow Bundle Validation

The `workflow_bundle_validator.py` module provides preflight validation
for workflow bundles themselves (not their outputs). It checks:

- Manifest structure and required fields.
- Step name uniqueness and ordering.
- Artifact key references.
- Coder configuration validity.
- Governance package completeness.

This validator is used during bundle loading to catch configuration
errors before execution begins.

## Guidance for Writing validate_* Actions

Layer 3 bundles that need custom validation steps should follow these
guidelines.

### Action Registration

Register validation actions using the `@action()` decorator:

```python
from agent_runner_v2.workflow_packages.actions import action
from agent_runner_v2.action_result import ActionResult

@action("validate_my_bundle_outputs")
def validate_my_bundle_outputs(*, context, state, step_cfg, project_root):
    # ... validation logic ...
    return ActionResult(
        status="APPROVED" if all_ok else "REJECTED",
        remark="Validation summary",
        artifacts={"VALIDATION_REPORT": report_path},
    )
```

### Validation Logic Structure

A `validate_*` action should:

1. **Load the validation plan**: construct a
   `DocumentationValidationPlan` with the bundle's requirements.
2. **Execute the plan**: call `validate_documentation_plan()` with the
   project root.
3. **Evaluate results**: check all `ValidationCheck` entries for
   failures.
4. **Write a report**: generate a validation report artifact with
   detailed findings.
5. **Return result**: return `ActionResult` with `APPROVED` if all
   checks pass, `REJECTED` otherwise.

### Determinism Rules

- Validation actions must be deterministic: given the same inputs, they
  must produce the same outputs.
- Validation actions must not depend on external state (network, time,
  random values).
- Validation actions must not mutate the artifacts they validate.
- Validation actions must report all findings, not just the first
  failure.

### Report Structure

Validation reports should include:

- Total check count and pass/fail counts.
- Per-check detail: check type, path, section, pass/fail, detail message.
- Overall verdict: approved or rejected.
- Any recommendations for fixing failures.

### Separation of Concerns

- Platform-level validation (metadata compliance, required sections)
  belongs in shared validators.
- Bundle-level validation (bundle-specific artifact structure, prompt
  content rules) belongs in bundle-local validators.
- Validation actions must not perform review or audit functions. They
  check deterministic rules, not semantic quality.
