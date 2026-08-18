# Actions Reference

> **Purpose:** Documentation of all actions in the AGBv2 pipeline  
> **Audience:** Developers debugging action failures or extending AGB

---

## Overview

AGBv2 uses **4 action-driven steps** (steps 2, 7, 9, 11):

| Step | Action | Purpose |
|------|--------|---------|
| 2 | `_copy_infrastructure` | Copy AGB infrastructure to output |
| 7 | `_assemble_package` | Build workflow.toml + context_extensions.py |
| 9 | `_validate_structure` | Deterministic structural validation |
| 11 | `_promote_workflow_package` | Deploy to workflows/{codename}/ |

Plus one special action:

| Action | Purpose |
|--------|---------|
| `noop` | Skip step (used by generator implementation) |

---

## Action Interface Contract

All actions MUST follow this contract:

```python
from agent_runner_v2.workflow_packages.actions import action
from agent_runner_v2.action_result import ActionResult

@action("action_name")
def action_name(*, context, state, step_cfg, project_root):
    """Docstring describing what this action does."""
    # ... implementation ...
    return ActionResult(
        status="APPROVED",           # "APPROVED" or "REJECTED"
        remark="Brief description",  # Human-readable summary
        artifacts={                  # artifact_key → path
            "OUTPUT_KEY": "/path/to/output"
        },
        reject_code=None,            # Machine-readable failure code
    )
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `context` | `dict[str, str]` | Resolved artifact paths and context variables |
| `state` | `dict[str, Any]` | Job state including `state["artifacts"]` |
| `step_cfg` | `dict[str, Any]` | Step configuration from workflow.toml |
| `project_root` | `Path` | Absolute path to project root |

### Return Value

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | string | YES | `"APPROVED"` or `"REJECTED"` |
| `remark` | string | YES | Human-readable summary |
| `artifacts` | dict | YES | Mapping of artifact_key → absolute path |
| `reject_code` | string | NO | Machine-readable code when REJECTED |

---

## Action: _copy_infrastructure

**Step:** 2 — Copy Infrastructure  
**Purpose:** Copy AGB infrastructure (actions.py + prompts/) to output directory

### Behavior

1. Reads codename from requirement doc frontmatter
2. Determines output directory from `WORKFLOW_ACTIONS_FILE` artifact
3. Copies AGB's `actions.py` to output
4. Copies AGB's `prompts/` directory to output

### Inputs

| Artifact | Description | Required |
|----------|-------------|----------|
| `REQUIREMENT_DOC` | To extract codename | YES |
| `ANALYSIS_JSON_FILE` | Contains codename fallback | YES |

### Outputs

| Artifact | Description |
|----------|-------------|
| `WORKFLOW_ACTIONS_FILE` | Path to copied actions.py |
| `WORKFLOW_PROMPTS_DIR` | Path to copied prompts/ directory |
| `WORKFLOW_EXTENSIONS_FILE` | Generated context_extensions.py (placeholder) |

### Error Conditions

| Condition | reject_code | Description |
|-----------|-------------|-------------|
| Missing requirement doc | `MISSING_REQUIREMENT_DOC` | REQUIREMENT_DOC not in state |
| Missing analysis JSON | `MISSING_ANALYSIS_JSON` | ANALYSIS_JSON_FILE not in state |
| Source not found | `SOURCE_NOT_FOUND` | AGB actions.py not found |

### Notes

- This action is skipped (noop) in generator implementation
- The copied infrastructure serves as the base for domain-specific extensions
- context_extensions.py is created as a placeholder; step 7 overwrites it

---

## Action: _assemble_package

**Step:** 7 — Assemble Package  
**Purpose:** Mechanically build workflow.toml, context_extensions.py, and impl.yaml files

### Behavior

1. Reads Analysis JSON from `ANALYSIS_JSON_FILE`
2. Validates JSON structure
3. Filters out infrastructure steps (prefixed with `_`)
4. Generates workflow.toml with step chaining
5. Generates context_extensions.py with two-dict pattern
6. Generates impls/{name}/impl.yaml for each implementation
7. Handles extend mode if `extend_mode: true`

### Extend Mode

If `extend_mode: true` in Analysis JSON:
1. Reads existing workflow from `EXISTING_WORKFLOW_DIR`
2. Copies existing files (actions.py, prompts/, context_extensions.py)
3. Appends new implementation declarations to workflow.toml
4. Generates impl.yaml ONLY for new implementations

### Inputs

| Artifact | Description | Required |
|----------|-------------|----------|
| `ANALYSIS_JSON_FILE` | Analysis JSON | YES |
| `WORKFLOW_ACTIONS_FILE` | Path to actions.py | YES |
| `WORKFLOW_PROMPTS_DIR` | Path to prompts/ | NO |
| `EXISTING_WORKFLOW_DIR` | For extend mode | NO |

### Outputs

| Artifact | Description |
|----------|-------------|
| `WORKFLOW_MANIFEST_FILE` | Generated workflow.toml |
| `WORKFLOW_EXTENSIONS_FILE` | Generated context_extensions.py |
| `IMPL_OVERRIDE_FILES` | Generated impls/ directory |

### Generated Files

**workflow.toml:**
- `[workflow]` section from `identity`
- `[[step]]` sections from `domain_steps` with `onsuccess` chaining
- `[[workflow.implementation]]` sections from `implementations`
- Terminal `step_completion` step

**context_extensions.py:**
- `INPUT_ARTIFACTS` dict from `artifact_keys.inputs`
- `OUTPUT_ARTIFACTS` dict from `artifact_keys.intermediate` + `artifact_keys.outputs`
- `register_artifact_keys()` for backward compatibility
- `build_context_extensions()` using resolvers

**impls/{name}/impl.yaml:**
- `name`, `description`, `label` from implementation entry
- `overrides` section from implementation entry

### Error Conditions

| Condition | reject_code | Description |
|-----------|-------------|-------------|
| Missing Analysis JSON | `MISSING_ANALYSIS_JSON` | File not found in state |
| Parse error | `PARSE_ERROR` | Invalid JSON |
| Invalid analysis | `INVALID_ANALYSIS` | Missing identity or domain_steps |
| Missing role_policy | `MISSING_ROLE_POLICY` | Prompt step missing role_policy |
| No domain steps | `NO_DOMAIN_STEPS` | All steps were infrastructure |

### Notes

- This action is skipped (noop) in generator implementation
- Infrastructure steps are filtered with a warning log
- The assembler adds `onsuccess` chaining automatically
- Sequence numbers (`{seq}`) are handled at runtime, not assembly

---

## Action: _validate_structure

**Step:** 9 — Validate Structure  
**Purpose:** Deterministic structural validation of the assembled package

### Behavior

1. Validates file existence (workflow.toml, context_extensions.py, actions.py)
2. Validates TOML syntax in workflow.toml
3. Validates Python syntax in actions.py
4. Checks artifact key consistency
5. Verifies step references exist

### Validation Checks

| Check | Description |
|-------|-------------|
| File existence | All declared files exist |
| TOML syntax | workflow.toml is valid TOML |
| Python syntax | actions.py is valid Python |
| Artifact keys | All keys in steps are declared in context_extensions |
| Step references | All `onsuccess` targets exist |
| Implementation dirs | All `[[workflow.implementation]]` have matching `impls/{name}/` |

### Inputs

| Artifact | Description | Required |
|----------|-------------|----------|
| `WORKFLOW_MANIFEST_FILE` | workflow.toml path | YES |
| `WORKFLOW_ACTIONS_FILE` | actions.py path | YES |
| `WORKFLOW_EXTENSIONS_FILE` | context_extensions.py path | YES |

### Outputs

| Artifact | Description |
|----------|-------------|
| `VALIDATION_FINDINGS_FILE` | Validation results |

### Output Format

```json
{
  "valid": true,
  "checks": {
    "workflow_manifest": {"passed": true},
    "context_extensions": {"passed": true},
    "actions_module": {"passed": true},
    "artifact_keys": {"passed": true},
    "step_references": {"passed": true},
    "implementations": {"passed": true}
  },
  "errors": [],
  "warnings": []
}
```

### Error Conditions

| Condition | reject_code | Description |
|-----------|-------------|-------------|
| Missing manifest | `MISSING_MANIFEST` | workflow.toml not found |
| Missing actions | `MISSING_ACTIONS` | actions.py not found |
| Missing extensions | `MISSING_EXTENSIONS` | context_extensions.py not found |
| Validation failed | `VALIDATION_FAILED` | One or more checks failed |

### Notes

- This action is skipped (noop) in generator implementation
- Validation focuses on structure, not domain logic
- Failures route to human intervention

---

## Action: _promote_workflow_package

**Step:** 11 — Promote Package  
**Purpose:** Deploy the workflow package to `workflows/{codename}/`

### Behavior

1. Reads codename from workflow.toml
2. Determines source directory (where workflow.toml is)
3. Determines target directory (`workflows/{codename}/`)
4. Backs up existing target (if exists)
5. Copies all files to target
6. Generates README.md if not present

### Extend Mode

If `EXISTING_WORKFLOW_DIR` is provided:
1. If target doesn't exist, copies from existing first
2. Updates workflow.toml with merged version
3. Merges new impls/ into existing impls/
4. Does NOT overwrite existing actions.py, prompts/, context_extensions.py

### Files Copied

**Always:**
- workflow.toml
- context_extensions.py
- README.md

**Conditional:**
- actions.py (if exists)
- .env.sample (if exists)
- config.json.sample (if exists)

**Directories:**
- prompts/
- impls/ (if exists)

### Backup

If target exists:
```
workflows/{codename}_bak_{timestamp}/
```

### README.md Generation

If README.md doesn't exist, generates from workflow.toml metadata:
- Workflow name and description
- Step reference table
- Artifact contract

### Inputs

| Artifact | Description | Required |
|----------|-------------|----------|
| `WORKFLOW_MANIFEST_FILE` | workflow.toml path | YES |
| `WORKFLOW_ACTIONS_FILE` | actions.py path | YES |
| `WORKFLOW_EXTENSIONS_FILE` | context_extensions.py path | YES |
| `WORKFLOW_PROMPTS_DIR` | prompts/ path | YES |
| `EXISTING_WORKFLOW_DIR` | For extend mode | NO |

### Outputs

| Artifact | Description |
|----------|-------------|
| `WORKFLOW_PACKAGE_DIR` | Path to promoted workflow |

### Error Conditions

| Condition | reject_code | Description |
|-----------|-------------|-------------|
| Missing manifest | `MISSING_MANIFEST` | workflow.toml not in state |
| Source not found | `SOURCE_DIR_NOT_FOUND` | workflow.toml parent not a directory |
| Missing codename | `MISSING_CODENAME` | No name in workflow.toml |
| Existing not found | `EXISTING_WORKFLOW_NOT_FOUND` | Extend mode: EXISTING_WORKFLOW_DIR doesn't exist |

### Notes

- This action is skipped (noop) in generator implementation
- Extend mode merges rather than overwrites
- Backups preserve existing work
- README generation is automatic

---

## Action: noop

**Purpose:** No-operation action for skipping steps

### Behavior

Returns success immediately without doing anything.

```python
@action("noop")
def noop_action(*, context, state, step_cfg, project_root):
    return ActionResult(
        status="APPROVED",
        remark="Step skipped (no-op)",
        artifacts={},
    )
```

### Usage

Generator implementation uses `noop` to skip infrastructure steps:

```yaml
# impls/generator/impl.yaml
overrides:
  copy_infrastructure:
    action: "noop"
  assemble_package:
    action: "noop"
  validate_structure:
    action: "noop"
  promote_package:
    action: "noop"
```

### When to Use

- Skipping steps in generator implementation
- Placeholder for future functionality
- Conditional step execution

---

## Dispatch Priority

Actions are resolved in this order:

1. **Package-local actions.py** — highest priority
2. **Implementation-specific actions** — `impls/{name}/actions/*.py`
3. **Global ACTION_REGISTRY** — platform built-in actions

This allows workflows to override global actions and implementations to override workflow defaults.

---

## See Also

- [01_ARCHITECTURE.md](./01_ARCHITECTURE.md) — Plugin architecture
- [07_SDLC_PIPELINE.md](./07_SDLC_PIPELINE.md) — Pipeline walkthrough
- Workflow source: `workflows/artifact_generator_builder/actions.py`
