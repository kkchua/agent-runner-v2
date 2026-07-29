# Design Document: step_runner.py Extraction

**Status:** Draft  
**Created:** 2026-07-29  
**Scope:** Split step_runner.py (~3,490 lines, 84 functions) into focused modules

---

## Current State Analysis

### File Statistics
- **Lines:** ~3,490
- **Functions:** 84 (including private helpers)
- **Primary Responsibilities:**
  1. Step execution orchestration (`run_step`, `run_action`)
  2. Artifact validation (12 functions)
  3. Context building (15+ functions)
  4. Template validation (5+ functions)
  5. Path resolution (25+ functions)
  6. Prompt rendering (8+ functions)
  7. Backend artifact rules (5+ functions)
  8. Utility functions (14+ functions)

### Problems
- Violates Single Responsibility Principle
- Hard to navigate and understand
- Testing requires mocking too many dependencies
- Changes to one feature risk breaking others

---

## Proposed New Module Structure

```
agent_runner_v2/
├── step_runner.py              # Core orchestration (~500 lines)
├── artifact_validator.py       # Artifact validation logic
├── context_builder.py          # Context building and extensions
├── template_validator.py       # Template conformance checking
├── path_resolver.py            # Path resolution utilities
└── prompt_renderer.py          # Prompt rendering and checksums
```

---

## Module 1: artifact_validator.py

### Purpose
All artifact validation logic: existence checks, contract validation, BOM stripping

### Functions to Move (12 functions)

| Function | Line | Purpose |
|----------|------|---------|
| `_validate_artifact_files_exist` | 712 | Check artifact files exist on disk |
| `_strip_bom_from_artifacts` | 733 | Remove UTF-8 BOM from artifact files |
| `_validate_declared_produced_artifacts_exist` | 754 | Validate step's produces list exists |
| `_backfill_declared_produced_artifacts` | 798 | Backfill missing artifacts from context |
| `_validate_artifacts_in_produces_list` | 838 | Validate artifact against produces contract |
| `_normalize_artifact_contract_key` | 886 | Normalize artifact key names |
| `_declared_write_keys` | 905 | Get declared write keys from step config |
| `_step_requires_write_contract` | 932 | Check if step requires write contract |
| `_validate_step_write_contract_config` | 956 | Validate write contract configuration |
| `_resolve_contract_path_from_context` | 969 | Resolve contract path from context vars |
| `_resolve_allowed_write_paths` | 1001 | Resolve allowed write paths |
| `_verify_only_allowed_paths_changed` | 1043 | Verify file changes are in allowed paths |

### Interface Contract

```python
# artifact_validator.py

from dataclasses import dataclass
from pathlib import Path
from typing import Any

@dataclass
class ValidationResult:
    """Result of artifact validation."""
    valid: bool
    missing: list[str]
    errors: list[str]

def validate_required_artifacts(
    artifact_keys: list[str],
    job_dir: Path,
    state: dict[str, Any]
) -> ValidationResult:
    """Validate that all required artifacts exist."""
    ...

def validate_produced_artifacts(
    step_cfg: dict[str, Any],
    state: dict[str, Any],
    job_dir: Path
) -> ValidationResult:
    """Validate that declared produced artifacts exist."""
    ...

def validate_write_contract(
    step_cfg: dict[str, Any],
    step: str,
    ctx: dict[str, str]
) -> None:
    """Validate write contract configuration for a step."""
    ...

def strip_bom_from_path(path: Path) -> None:
    """Remove UTF-8 BOM from file if present."""
    ...
```

### Dependencies
- `pathlib.Path`
- `agent_runner_v2.exceptions.ArtifactMissingError`
- `agent_runner_v2.runtime_context`

---

## Module 2: context_builder.py

### Purpose
Build execution context: load extensions, apply hooks, resolve variables

### Functions to Move (15 functions)

| Function | Line | Purpose |
|----------|------|---------|
| `build_context` | 1989 | Main context building function |
| `_load_context_extensions_module` | 1958 | Load workflow context extensions |
| `_apply_workflow_package_context_hooks` | 1861 | Apply package context hooks |
| `_load_additional_sections` | 1845 | Load additional markdown sections |
| `_load_site_config` | 1689 | Load site configuration |
| `_load_site_theme` | 1755 | Load site theme configuration |
| `_build_layout_instructions` | 1823 | Build layout instructions |
| `_format_additional_sections` | 1726 | Format additional sections for prompt |
| `_set_backend_artifact_rule_aliases` | 1208 | Set backend artifact rule aliases |
| `_set_delivery_scaffold_aliases` | 1309 | Set delivery scaffold aliases |
| `_set_bug_fix_aliases` | 1370 | Set bug fix aliases |
| `_set_master_docs_aliases` | 1431 | Set master docs aliases |
| `_delivery_scaffold_output_path` | 1274 | Resolve delivery scaffold output path |
| `_canonicalize_master_bootstrap_artifacts` | 1064 | Canonicalize master bootstrap artifacts |
| `_task_source_traceability_metadata` | 3348 | Build task source traceability metadata |

### Interface Contract

```python
# context_builder.py

from typing import Any
from pathlib import Path

def build_context(
    *,
    state: dict[str, Any],
    step: str,
    step_cfg: dict[str, Any],
    job_dir: Path,
    templates_dir: Path | None = None,
) -> dict[str, str]:
    """Build execution context for a step.
    
    Args:
        state: Current job state
        step: Current step name
        step_cfg: Step configuration
        job_dir: Job directory path
        templates_dir: Optional templates directory
        
    Returns:
        Context dictionary for prompt rendering
    """
    ...

def load_context_extensions(
    workflow_module: Any,
    state: dict[str, Any]
) -> dict[str, Any]:
    """Load context extensions from workflow module."""
    ...

def apply_context_hooks(
    ctx: dict[str, str],
    state: dict[str, Any],
    step: str,
    step_cfg: dict[str, Any]
) -> dict[str, str]:
    """Apply workflow-specific context hooks."""
    ...

def resolve_artifact_aliases(
    ctx: dict[str, str],
    state: dict[str, Any],
    step: str,
    artifacts: dict[str, Any],
    produces: list[str]
) -> None:
    """Resolve artifact path aliases into context."""
    ...
```

### Dependencies
- `agent_runner_v2.runtime_context`
- `agent_runner_v2.constants`
- `agent_runner_v2.doc_paths`
- `agent_runner_v2.bundle_governance`

---

## Module 3: template_validator.py

### Purpose
Validate document templates: section requirements, metadata fields, conformance

### Functions to Move (5 functions)

| Function | Line | Purpose |
|----------|------|---------|
| `_validate_template_conformance` | 1515 | Main template conformance validation |
| `_has_section` | 1607 | Check if content has required section |
| `_has_metadata_field` | 1625 | Check if content has metadata field |
| `_extract_document_status` | 3381 | Extract document status from content |
| `_extract_metadata_value` | 3402 | Extract metadata value from content |

### Interface Contract

```python
# template_validator.py

from dataclasses import dataclass
from pathlib import Path
from typing import Any

@dataclass
class ConformanceResult:
    """Template conformance validation result."""
    conforms: bool
    missing_sections: list[str]
    missing_metadata: list[str]
    errors: list[str]

def validate_template_conformance(
    *,
    content: str,
    template_sections: list[str],
    required_metadata: list[str],
    allow_missing_sections: bool = False,
) -> ConformanceResult:
    """Validate document conforms to template requirements.
    
    Args:
        content: Document content to validate
        template_sections: Required section headings
        required_metadata: Required metadata fields
        allow_missing_sections: If True, warn instead of error
        
    Returns:
        Conformance validation result
    """
    ...

def has_section(content: str, section: str) -> bool:
    """Check if content contains a section heading."""
    ...

def has_metadata_field(content: str, field: str) -> bool:
    """Check if content has YAML metadata field."""
    ...

def extract_document_status(content: str) -> str | None:
    """Extract lifecycle_status from document content."""
    ...

def extract_metadata_value(content: str, key: str) -> str | None:
    """Extract metadata value from YAML frontmatter."""
    ...
```

### Dependencies
- `re` (regex)
- `yaml` (for frontmatter parsing)

---

## Module 4: path_resolver.py

### Purpose
Path resolution: artifact paths, review paths, validation paths, backend rules

### Functions to Move (25 functions)

| Function | Line | Purpose |
|----------|------|---------|
| `_resolve_meta_json_path` | 438 | Resolve meta.json path |
| `_backend_artifact_rules` | 1115 | Get backend artifact rules |
| `_normalize_backend_job_path` | 1131 | Normalize backend job path |
| `_resolve_backend_artifact_rule_path` | 1161 | Resolve backend artifact path |
| `_snapshot_allowed_write_roots` | 1028 | Snapshot allowed write roots |
| `_path_for_report` | 102 | Path formatting for reports |
| `_build_new_review_file_path` | 2857 | Build review file path |
| `_suggested_review_file_path` | 2922 | Suggested review file path |
| `_build_validation_file_path` | 2954 | Build validation file path |
| `_build_pre_init_file_path` | 3023 | Build pre-init file path |
| `_build_plan_file_path` | 3048 | Build plan file path |
| `_build_task_graph_file_path` | 3075 | Build task graph file path |
| `_build_impl_file_path` | 3094 | Build impl file path |
| `_build_codebase_change_impact_path` | 3123 | Build codebase change impact path |
| `_review_target_artifact_key` | 2726 | Get review target artifact key |
| `_review_filename_date_code` | 2747 | Generate review filename date code |
| `_review_step_code` | 2756 | Get review step code |
| `_normalize_review_slug` | 2787 | Normalize review slug |
| `_derive_review_slug_from_artifact_path` | 2805 | Derive review slug from path |
| `_build_review_target_identifier` | 2831 | Build review target identifier |
| `_hash_file` | 1059 | Hash file contents |
| `_resolve_progress_file_path` | 3305 | Resolve progress file path |
| `_build_file_fingerprint` | 3216 | Build file fingerprint |
| `_format_artifact_fingerprint_block` | 3240 | Format artifact fingerprint block |
| `_prompt_allowed_write_paths` | 3258 | Format allowed write paths for prompt |

### Interface Contract

```python
# path_resolver.py

from pathlib import Path
from typing import Any

def resolve_meta_json_path(
    job_dir: Path,
    step: str,
    result_meta_key: str | None = None
) -> Path:
    """Resolve meta.json path for a step."""
    ...

def resolve_artifact_path(
    artifact_key: str,
    state: dict[str, Any],
    step: str
) -> Path | None:
    """Resolve artifact path from key."""
    ...

def build_review_file_path(
    *,
    state: dict[str, Any],
    step: str,
    step_cfg: dict[str, Any]
) -> Path:
    """Build path for review file."""
    ...

def build_validation_file_path(
    *,
    state: dict[str, Any],
    step: str,
    step_cfg: dict[str, Any]
) -> Path:
    """Build path for validation file."""
    ...

def hash_file(path: Path) -> str:
    """Compute MD5 hash of file contents."""
    ...
```

---

## Module 5: prompt_renderer.py

### Purpose
Prompt rendering, template substitution, checksums

### Functions to Move (8 functions)

| Function | Line | Purpose |
|----------|------|---------|
| `render_prompt` | 2432 | Main prompt rendering function |
| `_rewrite_prompt_literals` | 2540 | Rewrite prompt literal placeholders |
| `_stringify_prompt_value` | 2558 | Stringify context value for prompt |
| `_normalize_prompt_context_paths` | 2574 | Normalize paths in context |
| `_prompt_safe_path_value` | 2595 | Make path safe for prompt inclusion |
| `_looks_like_prompt_path` | 2613 | Check if value looks like a path |
| `_python_string_literal` | 2652 | Escape value for Python string literal |
| `prompt_checksum` | 2664 | Compute prompt checksum |

### Interface Contract

```python
# prompt_renderer.py

def render_prompt(
    template_text: str,
    context: dict[str, str],
    step_cfg: dict | None = None
) -> str:
    """Render prompt template with context variables.
    
    Args:
        template_text: Raw template text with {placeholders}
        context: Dictionary of replacement values
        step_cfg: Optional step configuration for literal rewriting
        
    Returns:
        Rendered prompt text
    """
    ...

def prompt_checksum(prompt_text: str) -> str:
    """Compute SHA256 checksum of prompt text."""
    ...

def stringify_for_prompt(value: Any) -> str:
    """Convert value to string safe for prompt inclusion."""
    ...

def rewrite_literal_placeholders(template: str) -> str:
    """Rewrite {{PLACEHOLDER}} to {PLACEHOLDER} for literal output."""
    ...
```

---

## Remaining in step_runner.py

### Core Orchestration Functions (Keep)

| Function | Line | Purpose |
|----------|------|---------|
| `run_step` | 129 | Main step execution entry point |
| `run_action` | 337 | Action execution entry point |
| `_resolve_meta_json_path` | May move, or keep wrapper |
| `_read_and_validate_meta_json` | 486 | Read and validate meta.json |
| `enrich_sidecar` | 1640 | Enrich meta.json sidecar |

### Private Helpers (Keep or Inline)

- `_coerce_int`, `_coerce_float`, `_coerce_direct_result_to_meta`
- `_repair_or_validate_meta_json`
- `_save_debug_failure`, `_write_raw_events_jsonl`

---

## Migration Plan

### Phase 2A: Create New Modules (No Breaking Changes)

1. Create `artifact_validator.py` with extracted functions
2. Create `context_builder.py` with extracted functions
3. Create `template_validator.py` with extracted functions
4. Create `path_resolver.py` with extracted functions
5. Create `prompt_renderer.py` with extracted functions

### Phase 2B: Update step_runner.py Imports

```python
# New imports in step_runner.py
from .artifact_validator import (
    validate_required_artifacts,
    validate_produced_artifacts,
    validate_write_contract,
)
from .context_builder import build_context
from .template_validator import validate_template_conformance
from .path_resolver import resolve_meta_json_path, resolve_artifact_path
from .prompt_renderer import render_prompt, prompt_checksum
```

### Phase 2C: Deprecate and Remove

1. Mark old functions as deprecated with warnings
2. After 2 releases, remove deprecated function bodies
3. Keep only re-exports for backward compatibility

---

## Dependencies Graph

```
step_runner.py
├── artifact_validator.py (uses: exceptions, runtime_context)
├── context_builder.py (uses: runtime_context, constants, doc_paths, bundle_governance)
├── template_validator.py (uses: re)
├── path_resolver.py (uses: runtime_context, constants, hashlib)
├── prompt_renderer.py (uses: constants, hashlib)
└── Other internal: _coerce*, _repair*, _save*, enrich_sidecar
```

---

## Testing Strategy

1. **Unit tests for each new module** - Test in isolation
2. **Integration tests** - Verify step_runner still works
3. **Backward compatibility tests** - Ensure existing workflows work

---

## Success Criteria

- [ ] Each new module < 600 lines
- [ ] step_runner.py < 800 lines
- [ ] All existing tests pass
- [ ] New unit tests for extracted modules
- [ ] No regressions in workflow execution
