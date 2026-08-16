# Phase 1: Analyzing v1 as a Composition System

> **Status:** DRAFT
> **Created:** 2026-08-07
> **Purpose:** Break down v1's output into composition system components

---

## 1. v1's Output Structure

What does workflow_builder_v1 produce?

```
workflows/{workflow_name}/
├── workflow.toml              ← The manifest (step sequence, routing, artifacts)
├── context_extensions.py      ← Artifact key registration, context injection
├── actions.py                 ← Custom action implementations (if needed)
├── prompts/                   ← Prompt templates for LLM steps
│   ├── 01_step_name.txt
│   ├── 02_step_name.txt
│   └── ...
├── README.md                  ← User documentation
├── .env.sample                ← Environment variables (optional)
└── config.json.sample         ← Runtime config (optional)
```

## 2. Mapping to Composition System Metaphor

### 2.1 Components (The LEGO Bricks)

Each file/element in v1's output is a **component**:

| Component Type | File | Purpose | Properties |
|---|---|---|---|
| `workflow_manifest` | workflow.toml | Defines step sequence, routing, artifacts | name, version, job_prefix, steps[], routing |
| `context_extension` | context_extensions.py | Registers artifact keys, injects context | workflow_name, register_artifact_keys(), build_context_extensions() |
| `action_module` | actions.py | Custom action implementations | @action decorated functions, error handling |
| `prompt_template` | prompts/*.txt | LLM instructions for each step | objective, reference_inputs, output_instructions, self_critic |
| `documentation` | README.md | User guide | overview, prerequisites, usage, step_reference |
| `env_template` | .env.sample | Environment variable definitions | variable_name, description, placeholder |
| `config_template` | config.json.sample | Runtime configuration | settings, defaults |

### 2.2 Component Schema (The Brick Specification)

Each component type has a schema:

#### workflow_manifest Schema
```yaml
component_type: workflow_manifest
properties:
  name: string (required)           # Workflow name (lowercase_with_underscores)
  version: string (required)        # Semantic version
  label: string (required)          # Human-readable display name
  job_prefix: string (required)     # 4-char uppercase prefix
  description: string (required)    # What the workflow does
  init_step: string (required)      # First step name
  steps: array (required)           # Step definitions
  routing: object (required)        # onsuccess, on_reject_refine
```

#### context_extension Schema
```yaml
component_type: context_extension
properties:
  workflow_name: string (required)  # Must match workflow.toml name
  register_artifact_keys: function (required)  # Returns artifact key → path mapping
  build_context_extensions: function (required)  # Returns context variables
  install_to_global: function (required)  # Global installation logic
  sync_to_backend: function (required)  # Backend sync logic
```

#### action_module Schema
```yaml
component_type: action_module
properties:
  actions: array (required)         # List of @action decorated functions
  imports: array (required)         # Required imports
  error_handling: boolean (required)  # Whether actions have error handling
```

#### prompt_template Schema
```yaml
component_type: prompt_template
properties:
  step_name: string (required)      # Which step this prompt is for
  objective: string (required)      # What the LLM should do
  reference_inputs: array (required)  # What to read ({ARTIFACT_KEY} placeholders)
  output_instructions: string (required)  # Where to write, format
  self_critic: string (required)    # Challenge before completing
  forbidden_content: array (optional)  # What NOT to include
```

### 2.3 Composition Format (How Bricks Snap Together)

The **composition** is the workflow specification (the input to v1). It defines:
- Which components to generate (workflow_manifest, context_extension, etc.)
- How they fit together (step sequence, artifact flow)
- Overrides (domain-specific customizations)

```yaml
composition_id: "agnes_media_gen_v1"
name: "Agnes Media Generation v1"

component_bindings:
  workflow_manifest:
    name: "agnes_media_gen_v1"
    job_prefix: "AMGEN"
    steps:
      - name: "extract_descriptions"
        type: "prompt"
        produces: ["IMAGE_DESCRIPTIONS"]
      - name: "generate_prompts"
        type: "prompt"
        produces: ["PROMPT_VARIANTS"]
      - name: "generate_images"
        type: "action"
        action: "generate_images"
      # ...
  
  context_extension:
    workflow_name: "agnes_media_gen_v1"
    artifact_keys:
      IMAGE_DESCRIPTIONS: "step_01_imagedesc/index.json"
      PROMPT_VARIANTS: "step_02_promptvariant/index.json"
      # ...
  
  action_module:
    actions:
      - name: "generate_images"
        purpose: "Call Agnes Image API"
      - name: "generate_videos"
        purpose: "Call Agnes Video API"
  
  prompt_templates:
    - step: "extract_descriptions"
      objective: "Extract image descriptions via LLM vision"
    - step: "generate_prompts"
      objective: "Generate prompt variants for image/video generation"
  
  documentation:
    overview: "End-to-end media generation pipeline"
    prerequisites: ["Agnes API keys"]
```

### 2.4 Output Format (The Assembled Structure)

The **output** is the complete workflow package — all components resolved and assembled:

```markdown
---
composition_id: "agnes_media_gen_v1"
workflow_name: "agnes_media_gen_v1"
component_count: 7
generation_date: "2026-08-07"
---

# Agnes Media Generation v1

## Workflow Manifest (workflow.toml)
[Complete workflow.toml content]

## Context Extensions (context_extensions.py)
[Complete context_extensions.py content]

## Actions (actions.py)
[Complete actions.py content]

## Prompts (prompts/)
- 01_extract_descriptions.txt
- 02_generate_prompts.txt
- ...

## Documentation (README.md)
[Complete README.md content]
```

## 3. The Traditional Workflow Domain

Now we can define the **Traditional Workflow Domain** as a composition system:

### 3.1 Component Types

| Component Type | Description |
|---|---|
| `workflow_manifest` | The workflow.toml file |
| `context_extension` | The context_extensions.py file |
| `action_module` | The actions.py file (if needed) |
| `prompt_template` | Individual prompt files |
| `documentation` | The README.md file |
| `env_template` | The .env.sample file (optional) |
| `config_template` | The config.json.sample file (optional) |

### 3.2 Composition Rules

- Every workflow has a `workflow_manifest` and `context_extension`
- Every workflow has at least one `prompt_template` (for prompt-driven steps)
- Workflows with action steps have an `action_module`
- All workflows have `documentation`
- `env_template` and `config_template` are optional

### 3.3 Output Structure

The output is a complete workflow package directory with all components resolved and assembled.

## 4. What v2 Needs to Build

v2 needs to build **Traditional Workflow Composition Systems** — workflows that produce traditional workflow packages using the composition system approach.

**v2's Input:** A workflow specification (the composition)
**v2's Output:** A complete workflow package (the resolved composition)

**v2's Internal Workflow:**
1. Scan the workflow spec (composition)
2. Identify required components (manifest, context_extension, prompts, actions, docs)
3. Generate each component following its schema
4. Assemble into a complete workflow package
5. Review and refine

## 5. Next Steps

1. Define the component schemas in detail (validation rules, required fields)
2. Define the composition format for traditional workflows
3. Design v2's workflow to generate these components
4. Implement v2 and test with agnes_media_gen_v1 spec

---

**End of Analysis**
