---
template_id: SYS-02-VC
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "permanent Layer 2 validation contract; defines platform validation model for all bundles"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02PC-20260720-86359b88"
managed_by: workflow-generated
---

> Managed by workflow: `02_platform_core_foundation_v1` / step: `generate_platform_core_docs`
> This file is workflow-generated and protected from manual edits.

# Validation Contract

## Purpose

This document defines the platform validation model for agent-runner-v2.
It describes the `DocumentationValidationPlan` pattern, section-check
conventions, frontmatter enforcement, file existence checks, and how
Layer 3 bundles compose platform validators.

The validation model is implemented in
`actions/documentation_validation_core.py` and is available to all
workflow bundles on this platform.

## ValidationPlan Pattern

The `DocumentationValidationPlan` is a dataclass that declaratively
describes what a validation step should check. It is the primary
abstraction for deterministic document validation on this platform.

### Structure

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
| `required_folders` | `tuple[str, ...]` | Relative paths of folders that must exist. |
| `required_files` | `tuple[str, ...]` | Relative paths of files that must exist. |
| `section_requirements` | `dict[str, tuple[str, ...]]` | Maps file relative paths to required section headings. |
| `template_ids` | `dict[str, str]` | Maps file relative paths to expected template_id values. |
| `extra_checkers` | `tuple[ValidationChecker, ...]` | Custom checker functions for bundle-specific validation. |

### Execution

The function `validate_documentation_plan()` in
`documentation_validation_core.py` executes a plan against a project
root:

1. For each entry in `required_folders`, verify the folder exists.
2. For each entry in `required_files`, verify the file exists.
3. For each entry in `section_requirements`, read the file and verify
   each required section heading is present.
4. For each entry in `template_ids`, read the file and verify the
   frontmatter `template_id` matches.
5. Run each `extra_checkers` function against the project root.

Each check produces a `ValidationCheck` result:

```python
{
    "check": "file_exists",     # check type
    "path": "docs/file.md",     # target path
    "ok": True,                 # pass/fail
    "detail": "exists (1234 bytes)"  # human-readable detail
}
```

### Composition

Validation plans are composable. A Layer 3 bundle can:

1. Start with a platform-provided base plan.
2. Add bundle-specific `required_files`, `section_requirements`, or
   `extra_checkers`.
3. Execute the combined plan in a single validation step.

This allows bundles to inherit platform-level validation while adding
their own constraints.

## Section Checks

The `has_section()` function in `documentation_validation_core.py`
checks whether a markdown file contains a specific section heading.

### Behavior

```python
def has_section(content: str, section: str) -> bool:
    pattern = re.compile(
        rf"^#+\s+.*{re.escape(section)}",
        re.MULTILINE | re.IGNORECASE
    )
    return bool(pattern.search(content))
```

The function:

- Matches any markdown heading level (`#`, `##`, `###`, etc.).
- Performs case-insensitive matching.
- Matches partial heading text (the section string need not be the
  complete heading).

### Convention

Section requirements in validation plans use the exact heading text
(expected to be found after the `#` markers). For example:

```python
section_requirements = {
    "docs/platform/README.md": (
        "Purpose",
        "Document Map",
        "Platform Identity",
    ),
}
```

This verifies that `README.md` contains headings matching "Purpose",
"Document Map", and "Platform Identity" at any heading level.

## Frontmatter Enforcement

The `has_frontmatter_field()` function in `documentation_validation_core.py`
checks whether a document's YAML frontmatter contains a specific field.

### Behavior

```python
def has_frontmatter_field(content: str, field: str) -> bool:
    pattern = re.compile(
        rf"^\s*-?\s*{re.escape(field)}\s*[:]",
        re.MULTILINE
    )
    return bool(pattern.search(content))
```

The function:

- Searches for the field name followed by a colon.
- Handles optional YAML list prefix (`-`).
- Operates on raw content (the caller reads the file).

### Platform Requirements

All permanent documents on this platform must include at minimum the
frontmatter fields defined in the Metadata Contract (`METADATA_CONTRACT.md`).
Validation steps should enforce these fields:

| Field | Required For |
|---|---|
| `template_id` | All permanent documents |
| `version` | All permanent documents |
| `doc_type` | All governed documents |
| `authority` | All governed documents |
| `scan_policy` | All governed documents |
| `scan_reason` | All governed documents |
| `layer` | All permanent documents |
| `platform` | All Layer 2 and Layer 3 permanent documents |
| `lifecycle_status` | All permanent documents |
| `effective_version` | Workflow-generated permanent documents |
| `managed_by` | Workflow-generated documents |

### Custom Checkers

Bundles may add custom frontmatter checkers via the `extra_checkers`
field:

```python
def check_custom_frontmatter(project_root: Path) -> list[ValidationCheck]:
    checks = []
    content = read_file(project_root, "docs/bundle/my_doc.md")
    if content is None:
        return [{"check": "custom", "path": "docs/bundle/my_doc.md",
                 "ok": False, "detail": "file missing"}]
    for field in ["custom_field_a", "custom_field_b"]:
        has = has_frontmatter_field(content, field)
        checks.append({
            "check": "frontmatter_field",
            "path": "docs/bundle/my_doc.md",
            "section": field,
            "ok": has,
            "detail": "found" if has else f"missing field `{field}`",
        })
    return checks
```

## File Existence Checks

The platform provides two file existence check functions in
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

### Usage in Plans

File and folder existence checks are declared in the validation plan:

```python
DocumentationValidationPlan(
    required_files=(
        "docs/system/00_governance/platform/current/README.md",
        "docs/system/00_governance/platform/current/RUNTIME_MODEL.md",
    ),
    required_folders=(
        "docs/system/00_governance/platform/current",
        "docs/system/00_governance/platform/runs",
    ),
)
```

## Bundle Validator Composition

Layer 3 bundles compose platform validators by combining platform-level
validation plans with bundle-specific checks.

### Pattern

1. The bundle defines its own `DocumentationValidationPlan` with
   bundle-specific requirements.
2. The bundle's validation action merges platform-level checks with
   bundle-level checks.
3. The combined plan is executed in a single validation step.

### Example

```python
def validate_bundle_output(context: dict) -> dict:
    project_root = Path(context["PROJECT_ROOT"])

    # Platform-level checks
    platform_plan = DocumentationValidationPlan(
        required_files=context.get("PLATFORM_REQUIRED_FILES", ()),
    )

    # Bundle-level checks
    bundle_plan = DocumentationValidationPlan(
        required_files=("docs/bundle/output.md",),
        section_requirements={
            "docs/bundle/output.md": ("Purpose", "Results"),
        },
        extra_checkers=(check_bundle_custom,),
    )

    # Execute both plans
    all_checks = []
    all_checks.extend(validate_documentation_plan(
        project_root=project_root, plan=platform_plan))
    all_checks.extend(validate_documentation_plan(
        project_root=project_root, plan=bundle_plan))

    passed = sum(1 for c in all_checks if c["ok"])
    total = len(all_checks)

    return {
        "status": "APPROVED" if passed == total else "REJECTED",
        "remark": f"Validation: {passed}/{total} checks passed.",
        "artifacts": {},
    }
```

### Distinction: Platform vs Bundle Checks

| Check Level | Scope | Examples |
|---|---|---|
| Platform-level | Applies to all bundles on this platform | Metadata field presence, scan_policy validity, layer field correctness |
| Bundle-level | Applies to a specific bundle | Bundle-specific artifact existence, bundle-specific section headings, custom business rules |

Platform-level checks are inherited by all bundles. Bundle-level checks
are additive and specific to the bundle's own outputs.

## Guidance for Writing validate_* Actions

Layer 3 bundles that need custom validation should follow these
guidelines when writing their `validate_*` action functions.

### Action Function Signature

```python
def validate_my_artifacts(context: dict) -> dict:
    """Validate bundle-specific artifacts."""
```

The function receives the step context dictionary and returns a result
dictionary compatible with the standard meta.json structure.

### Return Structure

```python
{
    "status": "APPROVED",      # or "REJECTED"
    "remark": "Summary.",
    "artifacts": {
        "VALIDATION_REPORT": "path/to/report.md"
    }
}
```

### Best Practices

1. **Use `DocumentationValidationPlan`** for declarative checks. Avoid
   reimplementing file existence or section matching logic.

2. **Use helper functions** from `documentation_validation_core.py`:
   `check_file_exists()`, `check_folder_exists()`, `has_section()`,
   `has_frontmatter_field()`, `read_file()`.

3. **Report all checks**, not just failures. The full check list
   provides audit traceability.

4. **Separate platform checks from bundle checks**. If the platform
   provides a base plan, extend it rather than replacing it.

5. **Return structured results**. Each check should produce a
   `ValidationCheck` dictionary with `check`, `path`, `ok`, and
   `detail` fields.

6. **Do not mutate documents** in a validation action. Validation is
   read-only. Corrections belong in a refine step.

7. **Handle missing files gracefully**. If a required file is missing,
   report it as a failed check rather than raising an exception.

### Workflow Integration

Validation actions are referenced in `workflow.toml`:

```toml
[[step]]
name = "validate_output"
action = "validate_my_artifacts"

[step.artifacts]
produces = ["VALIDATION_REPORT"]
required_inputs = ["MY_OUTPUT"]
```

The platform executes the validation action as a normal step and routes
based on the result (APPROVED continues, REJECTED triggers refine or
failure routing).
