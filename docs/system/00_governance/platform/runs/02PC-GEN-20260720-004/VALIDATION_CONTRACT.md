---
template_id: SYS-02-VC
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "permanent Layer 2 validation contract; defines platform validation model for Layer 3 bundles"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02PC-GEN-20260720-004"
managed_by: workflow-generated
---

# Validation Contract

## Purpose

This document defines the platform validation model for agent-runner-v2.
It describes the `DocumentationValidationPlan` pattern, section-check
conventions, frontmatter enforcement, file existence checks, and how
Layer 3 bundles compose platform validators.

The validation model is implemented in
`actions/documentation_validation_core.py` and consumed by validation
actions across the platform.

## ValidationPlan Pattern

### `DocumentationValidationPlan`

Defined in `actions/documentation_validation_core.py` as a frozen
dataclass. A validation plan declares what to check:

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

| Field | Type | Description |
|---|---|---|
| `required_folders` | `tuple[str, ...]` | Relative paths of folders that must exist. |
| `required_files` | `tuple[str, ...]` | Relative paths of files that must exist. |
| `section_requirements` | `dict[str, tuple[str, ...]]` | Maps file relative paths to required section headings. |
| `template_ids` | `dict[str, str]` | Maps file relative paths to expected template_id values. |
| `extra_checkers` | `tuple[ValidationChecker, ...]` | Custom checker functions for platform-specific or bundle-specific validations. |

### Execution

The `validate_documentation_plan()` function executes a plan:

1. For each folder in `required_folders`, check that the directory
   exists and report item count
2. For each file in `required_files`, check that the file exists and
   report file size
3. For each entry in `section_requirements`, read the file and check
   that each required section heading is present
4. For each entry in `template_ids`, read the file and verify the
   template_id appears in the frontmatter
5. For each checker in `extra_checkers`, invoke it with the project
   root and collect additional checks

### Result Format

Each check produces a `ValidationCheck` dict:

```python
{
    "check": "<check_type>",    # folder_structure, file_exists, file_section, template_id, custom
    "path": "<relative_path>",
    "ok": True | False,
    "detail": "<human-readable detail>"
}
```

The full result is a list of `ValidationCheck` dicts. Callers determine
pass/fail by checking whether all entries have `ok: true`.

## Section Checks

### `has_section()`

Defined in `actions/documentation_validation_core.py`. This function
checks whether a markdown file contains a section heading matching the
given text:

```python
def has_section(content: str, section: str) -> bool:
    pattern = re.compile(rf"^#+\s+.*{re.escape(section)}", re.MULTILINE | re.IGNORECASE)
    return bool(pattern.search(content))
```

### Convention

- Section matching is case-insensitive
- The match uses a regex that looks for markdown heading syntax
  (`#`, `##`, etc.) followed by the section text
- The section text is matched as a substring within the heading --
  `has_section(content, "Step Model")` matches `## Step Model` and
  `## The Step Model Architecture`

### Section Requirements Per Template

Each template_id defines required section headings. The platform
enforces these through the `section_requirements` field of the
validation plan. For the Layer 2 platform constitution set:

| Template ID | Required Sections |
|---|---|
| `SYS-02-IDX` | Document Map, Platform Identity, Layer 1 Inheritance |
| `SYS-02-RM` | Step Model, Execution Paths, Job Lifecycle, Coder Integration, Rejection And Retry |
| `SYS-02-BAC` | Required Bundle Files, workflow.toml Format, Artifact Key Conventions, Bundle Governance Requirements, Metadata Compliance |
| `SYS-02-SS` | Context Extensions, Artifact Resolution, Path Contracts, Meta Sidecar, Notification Integration, Backend Sync Protocol, Action Registration |
| `SYS-02-MC` | Platform doc_type Values, Platform authority Values, Additional Frontmatter Fields, Inheritance Rules, Scan Policy Expectations |
| `SYS-02-VC` | ValidationPlan Pattern, Section Checks, Frontmatter Enforcement, File Existence Checks, Bundle Validator Composition |

## Frontmatter Enforcement

### `has_frontmatter_field()`

Defined in `actions/documentation_validation_core.py`. This function
checks whether a markdown file contains a YAML frontmatter field:

```python
def has_frontmatter_field(content: str, field: str) -> bool:
    pattern = re.compile(rf"^\s*-?\s*{re.escape(field)}\s*[:]", re.MULTILINE)
    return bool(pattern.search(content))
```

### Required Frontmatter Fields

All permanent platform documents must include at minimum:

| Field | Required | Notes |
|---|---|---|
| `template_id` | Yes | Must match the document's template definition. |
| `version` | Yes | Document version string. |
| `doc_type` | Yes | From the allowed vocabulary. |
| `authority` | Yes | From the allowed vocabulary. |
| `scan_policy` | Yes | From the allowed vocabulary. |
| `scan_reason` | Yes | Non-empty when scan_policy is `exclude` or `conditional`. |
| `layer` | Yes | `"layer1"`, `"layer2"`, or `"layer3"`. |
| `platform` | Yes (Layer 2/3) | `"agent-runner-v2"`. |
| `lifecycle_status` | Yes | Current lifecycle state. |
| `effective_version` | Conditional | Required for workflow-generated permanent documents. |
| `managed_by` | Conditional | Required for workflow-generated documents. |

### Validation Rules

Frontmatter validation enforces:

1. All required fields are present
2. `doc_type` belongs to the allowed vocabulary (Layer 1 baseline +
   Layer 2 extensions)
3. `authority` belongs to the allowed vocabulary
4. `scan_policy` belongs to the allowed vocabulary
5. `scan_reason` is non-empty when `scan_policy` is `exclude` or
   `conditional`
6. Generated documents do not claim `human-authored` authority
7. `template_id` matches the expected value for the document
8. `layer` matches the document's actual layer
9. `platform` is `"agent-runner-v2"` for all Layer 2 and Layer 3
   permanent documents

## File Existence Checks

### `check_file_exists()`

Defined in `actions/documentation_validation_core.py`:

```python
def check_file_exists(project_root: Path, rel_path: str) -> tuple[bool, str]:
    full = project_root / rel_path
    if full.exists() and full.is_file():
        return True, f"exists ({full.stat().st_size} bytes)"
    return False, f"missing at {rel_path}"
```

### `check_folder_exists()`

Also defined in `actions/documentation_validation_core.py`:

```python
def check_folder_exists(project_root: Path, rel_path: str) -> tuple[bool, str]:
    full = project_root / rel_path
    if full.exists() and full.is_dir():
        count = len(list(full.iterdir()))
        return True, f"exists ({count} items)"
    return False, f"missing at {rel_path}"
```

### File Existence Validation

File existence checks verify:

1. All required permanent documents exist at their expected paths
2. Required directory structures exist (e.g., `prompts/`,
   `bundle_governance/`)
3. Required input artifacts exist before a step runs
4. Output artifacts exist after a step completes

### Path Resolution

File paths in validation plans are relative to the project root. The
`validate_documentation_plan()` function receives the project root and
resolves all paths against it. For runtime validation, the project root
is `PROJECT_ROOT` from `runtime_context.py`.

## Bundle Validator Composition

### Platform-Level vs Bundle-Level

The validation model has two layers:

**Platform-level validation** enforces rules that apply to all bundles
on agent-runner-v2:

- metadata compliance (Layer 1 baseline + Layer 2 extensions)
- required bundle files (`workflow.toml` exists)
- artifact key conventions
- scan policy rules

**Bundle-level validation** enforces rules specific to a single bundle:

- bundle-specific artifact existence
- bundle-specific section requirements
- bundle-specific frontmatter values
- custom validation logic via `extra_checkers`

### Composition Pattern

Layer 3 bundles compose validators by:

1. Starting with the platform validation plan (or building one that
   includes platform-level checks)
2. Adding bundle-specific `required_files`, `section_requirements`,
   and `template_ids`
3. Adding bundle-specific `extra_checkers` for custom logic

### `extra_checkers` Pattern

The `extra_checkers` field accepts `ValidationChecker` functions:

```python
ValidationChecker = Callable[[Path], list[ValidationCheck]]
```

Each checker receives the project root and returns a list of
`ValidationCheck` dicts. This allows bundles to add arbitrary custom
validation logic while using the same result format.

### Workflow Bundle Validator

`workflow_bundle_validator.py` provides preflight validation for
workflow bundles. It checks:

- `workflow.toml` exists and is parseable
- Required fields are present in the manifest
- Step names are unique
- Prompt files referenced by steps exist
- Artifact keys are valid

## Guidance for Writing `validate_*` Actions

### Action Signature

Validation actions follow the standard action signature:

```python
@action("validate_my_bundle")
def validate_my_bundle(*, context, state, step_cfg, project_root):
    plan = DocumentationValidationPlan(
        required_files=(...),
        section_requirements={...},
        template_ids={...},
        extra_checkers=(...),
    )
    checks = validate_documentation_plan(
        project_root=project_root,
        plan=plan,
    )
    # Determine pass/fail from checks
    ...
    return ActionResult(status="APPROVED" | "REJECTED", ...)
```

### Best Practices

1. **Declare all checks in the plan** -- use `required_files`,
   `section_requirements`, and `template_ids` for structural checks.
   Reserve `extra_checkers` for logic that cannot be expressed as
   simple existence or section checks.

2. **Use deterministic checks** -- validation actions must produce the
   same result given the same input. No randomness, no time-dependent
   behavior, no external system calls.

3. **Report all findings** -- do not short-circuit on first failure.
   Collect all checks and report the full result so the review step
   can see all defects at once.

4. **Separate platform and bundle checks** -- if a validation action
   checks both platform-level and bundle-level rules, document which
   checks belong to which level.

5. **Return structured results** -- the `ActionResult` should include
   the validation report path as an artifact so downstream steps
   (review, audit) can reference it.

6. **Use `check_file_exists()` and `check_folder_exists()`** -- these
   helpers provide consistent detail messages and avoid duplicating
   path resolution logic.
