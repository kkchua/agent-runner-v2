# Analysis JSON Schema

> **Purpose:** Reference for the Analysis JSON format — the domain-only contract between analyze_requirement (step 1) and downstream domain steps.
> **Design principle:** The Analysis JSON contains ONLY domain concerns. Infrastructure (workflow.toml, context_extensions.py, assembly, validation, promotion) is universal/standard and handled mechanically by the platform.

---

## Overview

The **Analysis JSON** is the sole intermediate artifact in the AGB domain pipeline. It contains all domain information needed to plan and implement the target workflow's domain logic:

- `identity` — workflow name, type, metadata
- `domain_steps` — what the target workflow DOES (action functions + prompt steps)
- `artifact_keys` — data flow between steps (inputs, intermediate, outputs)

The platform's infrastructure layer reads this JSON and mechanically produces:
- `workflow.toml` — step sequence, routing, artifact bindings
- `context_extensions.py` — artifact key registration and path resolution

The LLM working on domain logic never sees or references infrastructure files.

---

## Schema Definition

```json
{
  "identity": {
    "name": "string",
    "codename": "string",
    "job_prefix": "string",
    "version": "string",
    "label": "string",
    "description": "string",
    "type": "builder | generator",
    "subtype": "string (optional)"
  },
  "domain_steps": [
    {
      "name": "string",
      "type": "action | prompt",
      "action_name": "string (when type=action)",
      "prompt_file": "string (when type=prompt)",
      "role_policy": "string (when type=prompt)",
      "required_inputs": ["string"],
      "produces": ["string"]
    }
  ],
  "artifact_keys": {
    "inputs": [
      {"key": "string", "pattern": "string"}
    ],
    "intermediate": [
      {"key": "string", "pattern": "string"}
    ],
    "outputs": [
      {"key": "string", "pattern": "string"}
    ]
  }
}
```

---

## Field Reference

### identity

Workflow identity information.

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| `name` | string | YES | Workflow name | MUST match codename; lowercase_with_underscores |
| `codename` | string | YES | Unique identifier | MUST match name; read from requirement doc frontmatter |
| `job_prefix` | string | YES | Job ID prefix | 2-10 uppercase characters |
| `version` | string | YES | Semantic version | MAJOR.MINOR.PATCH format |
| `label` | string | YES | Display name | Human-readable |
| `description` | string | NO | One-line description | Brief summary |
| `type` | string | YES | AGB pipeline mode | `"builder"` or `"generator"` (default: `"generator"`) |
| `subtype` | string | NO | Domain specialization | e.g., "jimeng", "comfyui" |

**Type field:** Selects the AGB pipeline mode, NOT alternative implementations.
- `"builder"` — target workflow produces workflow packages (self-replicating)
- `"generator"` — target workflow produces variable artifacts (reports, media, documents)

The generated workflow always has a single "standard" implementation regardless of type.

**Example:**
```json
{
  "identity": {
    "name": "text_summarizer",
    "codename": "text_summarizer",
    "job_prefix": "TXTSUM",
    "version": "1.0.0",
    "label": "Text Summarizer",
    "description": "Transforms long text into condensed output",
    "type": "generator"
  }
}
```

---

### domain_steps

Array of domain step definitions. These describe what the target workflow DOES — not how it's built or deployed.

**Rules:**
- Domain steps must NOT include infrastructure actions (prefixed with `_`)
- Domain steps must NOT reference infrastructure artifact keys
- The assembler adds `onsuccess` chaining and terminal `step_completion` automatically

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | YES | Unique step identifier (snake_case) |
| `type` | string | YES | `"action"` or `"prompt"` |
| `action_name` | string | Conditional | Required when `type="action"` |
| `prompt_file` | string | Conditional | Required when `type="prompt"`. Filename only |
| `role_policy` | string | Conditional | Required when `type="prompt"` |
| `required_inputs` | array | NO | Artifact keys this step consumes |
| `produces` | array | NO | Artifact keys this step produces |

**Action Step Example:**
```json
{
  "name": "parse_input",
  "type": "action",
  "action_name": "parse_input_document",
  "required_inputs": ["SOURCE_DOCUMENT_FILE"],
  "produces": ["PARSED_DOCUMENT"]
}
```

**Prompt Step Example:**
```json
{
  "name": "analyze_structure",
  "type": "prompt",
  "prompt_file": "analyze_structure.txt",
  "role_policy": "architect_standard",
  "required_inputs": ["PARSED_DOCUMENT"],
  "produces": ["ANALYSIS_RESULT"]
}
```

---

### artifact_keys

Artifact key definitions. Split into three categories.

| Category | Location | Description |
|----------|----------|-------------|
| `inputs` | `input/{filename}` | Provided by operator console as workflow input |
| `intermediate` | `output/{job_id}/{filename}` | Produced by one step, consumed by another |
| `outputs` | `output/{job_id}/{filename}` | Final deliverable artifacts |

Each entry:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `key` | string | YES | Artifact key name |
| `pattern` | string | YES | Filename or template (`{seq}` for sequence) |

**Key Naming Conventions:**
- Input files: `_FILE` suffix (e.g., `SOURCE_DOCUMENT_FILE`)
- Input directories: `_DIR` suffix (e.g., `INPUT_FOLDER_DIR`)
- Output/intermediate: descriptive name (e.g., `PARSED_DOCUMENT`, `SUMMARY_FILE`)

**Example:**
```json
{
  "artifact_keys": {
    "inputs": [
      {"key": "SOURCE_DOCUMENT_FILE", "pattern": "source.md"}
    ],
    "intermediate": [
      {"key": "PARSED_DOCUMENT", "pattern": "PARSED_DOCUMENT.json"},
      {"key": "ANALYSIS_RESULT", "pattern": "ANALYSIS_RESULT.json"}
    ],
    "outputs": [
      {"key": "SUMMARY_FILE", "pattern": "SUMMARY_FILE.md"}
    ]
  }
}
```

---

## Complete Example

```json
{
  "identity": {
    "name": "text_summarizer",
    "codename": "text_summarizer",
    "job_prefix": "TXTSUM",
    "version": "1.0.0",
    "label": "Text Summarizer",
    "description": "Transforms long text into condensed output",
    "type": "generator"
  },
  "domain_steps": [
    {
      "name": "parse_input",
      "type": "action",
      "action_name": "parse_input_document",
      "required_inputs": ["SOURCE_DOCUMENT_FILE"],
      "produces": ["PARSED_DOCUMENT"]
    },
    {
      "name": "analyze_structure",
      "type": "prompt",
      "prompt_file": "analyze_structure.txt",
      "role_policy": "architect_standard",
      "required_inputs": ["PARSED_DOCUMENT"],
      "produces": ["ANALYSIS_RESULT"]
    },
    {
      "name": "transform_content",
      "type": "prompt",
      "prompt_file": "transform_content.txt",
      "role_policy": "architect_standard",
      "required_inputs": ["ANALYSIS_RESULT"],
      "produces": ["TRANSFORMED_CONTENT"]
    },
    {
      "name": "render_output",
      "type": "action",
      "action_name": "render_prose_output",
      "required_inputs": ["TRANSFORMED_CONTENT", "PARSED_DOCUMENT"],
      "produces": ["SUMMARY_FILE"]
    }
  ],
  "artifact_keys": {
    "inputs": [
      {"key": "SOURCE_DOCUMENT_FILE", "pattern": "source.md"}
    ],
    "intermediate": [
      {"key": "PARSED_DOCUMENT", "pattern": "PARSED_DOCUMENT.json"},
      {"key": "ANALYSIS_RESULT", "pattern": "ANALYSIS_RESULT.json"},
      {"key": "TRANSFORMED_CONTENT", "pattern": "TRANSFORMED_CONTENT.md"}
    ],
    "outputs": [
      {"key": "SUMMARY_FILE", "pattern": "SUMMARY_FILE.md"}
    ]
  }
}
```

---

## What is NOT in the Analysis JSON

The following are **infrastructure concerns** — handled mechanically by the platform:

- `workflow.toml` structure (assembled from domain_steps)
- `context_extensions.py` (generated from artifact_keys)
- `implementations` array (always single "standard" implementation)
- `extend_mode` (removed — impl override pattern IS the extension mechanism)
- Infrastructure step definitions (_assemble_package, _validate_structure, _promote_package)
- Infrastructure artifact keys (WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, etc.)

---

## Validation Rules

1. **identity.name** MUST match **identity.codename**
2. **identity.job_prefix** MUST be 2-10 uppercase characters
3. **identity.type** MUST be `"builder"` or `"generator"`
4. **domain_steps[].name** MUST be unique within the array
5. **domain_steps[].type** MUST be `"action"` or `"prompt"`
6. **Prompt steps** MUST have `role_policy`
7. **Action steps** MUST have `action_name`
8. **artifact_keys.inputs[].key** SHOULD end with `_FILE` or `_DIR`
9. **Data flow** MUST be valid: each step's required_inputs produced by prior steps or workflow inputs
10. **No infrastructure steps** — steps with `_` prefix are domain violations

---

## See Also

- [BCS_v2.0.md](./BCS_v2.0.md) — Base Composition Standard
- [01_ARCHITECTURE.md](./01_ARCHITECTURE.md) — Architecture overview
- [ARTIFACT_USAGE_REFERENCE.md](./ARTIFACT_USAGE_REFERENCE.md) — Artifact key mapping
