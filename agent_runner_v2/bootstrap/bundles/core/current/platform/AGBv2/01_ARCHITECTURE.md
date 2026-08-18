# AGBv2 Architecture

> **Purpose:** Explain the plugin architecture, separation of concerns, and implementation model  
> **Audience:** Workflow developers extending AGB or creating custom implementations

---

## Core Insight

AGBv2 uses a **plugin architecture** where domain logic is self-contained in implementation directories. The infrastructure (actions.py, prompts/) is copied from AGB itself, while domain-specific logic lives in `impls/{domain}/`.

```
workflows/{codename}/
├── workflow.toml              # Step sequence + default implementation
├── context_extensions.py      # Artifact resolution (generated)
├── actions.py                 # Infrastructure actions (copied from AGB)
├── prompts/                   # Infrastructure prompts (copied from AGB)
├── impls/                     # Domain plugins (generated)
│   └── {domain}/
│       ├── impl.yaml          # Implementation config
│       ├── actions/           # Domain-specific actions (optional)
│       └── prompts/           # Domain-specific prompts
└── README.md
```

---

## Separation of Concerns

| Layer | What | Who | Location |
|-------|------|-----|----------|
| **Infrastructure** | step_runner, routing, artifact system, daemon | Platform | Predefined |
| **AGB Infrastructure** | Generic actions (assemble, validate, promote), base prompts | AGB | Copied to output |
| **Domain Logic** | Domain-specific actions, domain-specific prompts | LLM | Generated in impls/ |
| **Structural Files** | workflow.toml, context_extensions.py | Assembler | Generated mechanically |

---

## Standard Implementation

**Purpose:** Produce complete executable workflow packages.

**Pipeline:** All steps execute normally.

**Output Structure:**
```
workflows/{codename}/
├── workflow.toml
├── context_extensions.py
├── actions.py                 ← From AGB infrastructure
├── prompts/                   ← From AGB infrastructure
├── impls/
│   └── {domain}/              ← Domain plugin
│       ├── impl.yaml
│       ├── actions/           ← Domain-specific actions
│       └── prompts/           ← Domain-specific prompts
└── README.md
```

**Key characteristic:** Infrastructure steps (copy_infrastructure, assemble_package, validate_structure, promote_package) execute normally.

---

## Plugin Structure

Each implementation in `impls/{domain}/` is a self-contained plugin:

```
impls/{domain}/
├── impl.yaml              # Implementation configuration
├── INPUT_ARTIFACTS.md     # Documentation: input artifacts
├── OUTPUT_ARTIFACTS.md    # Documentation: output artifacts
└── (optional)
    ├── actions/           # Domain-specific actions
    │   ├── __init__.py
    │   └── domain_action.py
    └── prompts/           # Domain-specific prompts
        └── {step}/
            └── {option}.txt
```

### impl.yaml Structure

```yaml
name: {domain}
description: "What this implementation does"
label: "Display Label"

# Step overrides (optional)
overrides:
  {step_name}:
    prompt: "path/to/prompt.txt"
    action: "action_name"

# Prompt slot definitions
prompt_slots:
  {step_name}:
    label: "Human-readable label"
    default: {option_name}
    options:
      - name: {option_name}
        file: "path/to/prompt.txt"
```

---

## Two-Tier Prompt Resolution

When a prompt slot specifies a `file` path, the runtime resolves it using a two-tier fallback:

1. **Impl-specific tier:** `workflow_root/impls/{active_impl}/{file}`
   - If this file exists, use it.

2. **Shared fallback tier:** `workflow_root/{file}`
   - Used when impl-specific file doesn't exist.

### Example

Given:
- Active implementation: `jimeng`
- Prompt slot file: `prompts/analyze_requirement/standard.txt`

Resolution:
1. Check: `impls/jimeng/prompts/analyze_requirement/standard.txt`
2. If not found: `prompts/analyze_requirement/standard.txt`

This allows implementations to override specific prompts while sharing a common pool.

---

## Override Pattern

The multi-implementation model uses an **override pattern**:

- **workflow.toml** = default implementation (all steps have `prompt=` or `action=`)
- **impls/{name}/impl.yaml** = partial overrides (only steps that differ)

### Resolution Algorithm

```python
def resolve_step(step_name, workflow_toml, selected_impl):
    config = workflow_toml.get_step(step_name)  # Default config
    if selected_impl and selected_impl != "default":
        impl_overrides = load_yaml(f"impls/{selected_impl}/impl.yaml")
        if step_name in impl_overrides.get("overrides", {}):
            config.update(impl_overrides["overrides"][step_name])
    return config
```

### Example Override

**workflow.toml (default):**
```toml
[[step]]
name = "analyze_requirement"
prompt = "prompts/analyze_requirement/standard.txt"
```

**impls/jimeng/impl.yaml (override):**
```yaml
overrides:
  analyze_requirement:
    prompt: "impls/jimeng/prompts/analyze/jimeng.txt"
```

Result for `jimeng` implementation:
- Step uses `impls/jimeng/prompts/analyze/jimeng.txt` instead of default.

---

## Prompt Slots

Each prompt-driven step uses a **slot** that can be filled by different implementations:

```toml
[[step]]
name = "analyze_requirement"
prompt = "{{ slot.analyze_requirement }}"  # Slot reference
```

At runtime, `{{ slot.analyze_requirement }}` resolves to the actual prompt file based on:
1. Active implementation's `prompt_slots` in impl.yaml
2. Selected option

### Slot Resolution

```yaml
# impl.yaml
prompt_slots:
  analyze_requirement:
    label: "Analyze Requirement"
    default: standard          # Default option
    options:
      - name: standard
        file: "prompts/analyze_requirement/standard.txt"
      - name: advanced
        file: "prompts/analyze_requirement/advanced.txt"
```

Runtime selection:
- If user selects `advanced` → uses `advanced.txt`
- If no selection → uses `standard.txt` (default)

---

## Creating a Custom Implementation

To create a new domain plugin (e.g., `my_domain`):

### 1. Create Directory Structure

```
impls/my_domain/
├── impl.yaml
├── actions/              # Optional
└── prompts/              # Optional
    └── {step}/
```

### 2. Write impl.yaml

```yaml
name: my_domain
description: "Domain-specific implementation for my use case"
label: "My Domain"

# Step overrides (if needed)
overrides:
  analyze_requirement:
    prompt: "impls/my_domain/prompts/analyze/custom.txt"

# Prompt slots
prompt_slots:
  analyze_requirement:
    label: "Analyze My Domain"
    default: standard
    options:
      - name: standard
        file: "prompts/analyze_requirement/my_domain/standard.txt"
```

### 3. Create Domain Prompts

Write prompts at `impls/my_domain/prompts/{step}/{option}.txt`.

### 4. (Optional) Create Domain Actions

Write actions at `impls/my_domain/actions/*.py`:

```python
from agent_runner_v2.workflow_packages.actions import action
from agent_runner_v2.action_result import ActionResult

@action("my_domain_action")
def my_domain_action(*, context, state, step_cfg, project_root):
    # Domain-specific logic
    return ActionResult(
        status="APPROVED",
        remark="Action completed",
        artifacts={}
    )
```

### 5. Update workflow.toml

Add implementation declaration:

```toml
[[workflow.implementation]]
name = "my_domain"
description = "Domain-specific implementation for my use case"
label = "My Domain"
```

---

## Extend Mode

AGBv2 supports **extend mode** — adding a new implementation to an existing generated workflow.

### How It Works

**Input:**
- `REQUIREMENT_DOC` — describes the NEW implementation
- `EXISTING_WORKFLOW_DIR` — path to existing workflow package

**Output:**
- Same workflow package with new `impls/{new_name}/` directory
- Updated `workflow.toml` with new `[[workflow.implementation]]` declaration
- Existing files remain unchanged

### Extend Mode Pipeline

| Step | Normal Mode | Extend Mode |
|------|-------------|-------------|
| analyze_requirement | Design full domain | Read existing workflow.toml, analyze ONLY new impl |
| plan_domain_logic | Plan all actions + prompts | Plan ONLY new impl overrides |
| implement_domain | Write actions.py + prompts/ | Write ONLY `impls/{new_name}/` files |
| assemble_package | Generate all files | Copy existing, add new impl declarations |
| promote_package | Promote to workflows/ | Merge into existing workflows/ |

### Usage

```bash
# Set EXISTING_WORKFLOW_DIR to trigger extend mode
ukbe-run-agent run --template-group artifact_generator_builder \
  --impl-name standard \
  --input-artifact REQUIREMENT_DOC=new_impl.md \
  --input-artifact EXISTING_WORKFLOW_DIR=workflows/existing_workflow/
```

---

## Self-Bootstrap

AGBv2 can build itself. The requirement document specifies:

- **Input:** Requirement documents
- **Output:** Workflow packages (per BCS_v2.0)

When AGB builds AGB, it produces a workflow that can also build workflows.

---

## Benefits

1. **Reusability:** Infrastructure logic is shared across all generated workflows
2. **Self-Containment:** Domain plugins are fully self-contained in `impls/{domain}/`
3. **Flexibility:** Same pipeline produces complete workflows for any domain
4. **Maintainability:** Clear separation between infrastructure and domain logic
5. **Extensibility:** New domain plugins without modifying AGB core

---

## See Also

- [BCS_v2.0.md](./BCS_v2.0.md) — Base Composition Standard
- [06_IMPLEMENTATIONS.md](./06_IMPLEMENTATIONS.md) — Implementation details
- [04_PROMPTS_REFERENCE.md](./04_PROMPTS_REFERENCE.md) — Prompt slots
- Workflow source: `workflows/artifact_generator_builder/`
