# AGB Plugin Architecture

## Overview

The Artifact Generator Builder (AGB) now supports a **plugin architecture** where each implementation is a self-contained domain knowledge package. This enables AGB to serve as a universal builder for both complete workflows and content generators.

## Architecture Principles

### Separation of Concerns

- **Infrastructure** (root level): `actions.py` + `prompts/` — copied from AGB itself
- **Domain Logic** (impls/{domain}/): Self-contained plugins with domain-specific actions + prompts
- **Workflow Definition**: `workflow.toml` as single source of truth for step sequence

### Plugin Structure

Each implementation in `impls/{domain}/` is a self-contained plugin:

```
impls/{domain}/
├── impl.yaml           # Implementation config with step overrides
├── actions/            # Domain-specific actions (optional)
│   ├── __init__.py
│   └── domain_action.py
└── prompts/            # Domain-specific prompts
    ├── analyze.txt
    └── implement.txt
```

## Two Implementation Types

### 1. Standard (Builder) Implementation

**Purpose**: Generates complete executable workflow packages

**Pipeline**:
1. Analyze requirement → Analysis JSON
2. **Copy infrastructure** → Copy AGB's `actions.py` + `prompts/` to output
3. Plan domain logic → Domain plan
4. Implement domain → Generate domain plugin in `impls/{domain}/`
5. Critic implementation → Review domain logic
6. Assemble package → Build `workflow.toml` + `context_extensions.py`
7. Review package → Quality review
8. Validate structure → Structural validation
9. Gatekeep package → Final approval
10. Promote package → Deploy to `workflows/{name}/`

**Output Structure**:
```
workflows/{name}/
├── workflow.toml              # Domain-specific steps
├── context_extensions.py      # Artifact resolution
├── actions.py                 # From AGB (infrastructure)
├── prompts/                   # From AGB (infrastructure)
├── impls/{domain}/            # Domain plugin (self-contained)
│   ├── impl.yaml
│   ├── actions/
│   └── prompts/
└── README.md
```

### 2. Generator Implementation

**Purpose**: Produces variable content artifacts (reports, media, documents)

**Key Difference**: Skips infrastructure steps using `noop` action

**Skipped Steps** (via impl.yaml overrides):
- `copy_infrastructure` → noop
- `assemble_package` → noop
- `validate_structure` → noop
- `promote_package` → noop

**Active Steps**:
1. Analyze requirement
2. ~~Copy infrastructure~~ (skipped)
3. Plan domain logic → Plan content generation
4. Implement domain → Generate content
5. Critic implementation → Review content
6. ~~Assemble package~~ (skipped)
7. Review package → Quality review
8. ~~Validate structure~~ (skipped)
9. Gatekeep package → Final approval
10. ~~Promote package~~ (skipped)

## Implementation Details

### noop Action

```python
@action("noop")
def noop_action(*, context, state, step_cfg, project_root):
    """No-operation action — returns success immediately."""
    return ActionResult(
        status="APPROVED",
        remark="Step skipped (no-op)",
        artifacts={},
    )
```

Used by generator impl to skip infrastructure steps without modifying the workflow.toml structure.

### copy_infrastructure Action

```python
@action("_copy_infrastructure")
def copy_infrastructure_action(*, context, state, step_cfg, project_root):
    """Copy AGB infrastructure (actions.py + prompts/) to output workflow."""
    # Copies from AGB's own directory to output directory
    # Ensures generated workflow has necessary infrastructure
```

Copies:
- `actions.py` — AGB's infrastructure actions
- `prompts/` — AGB's infrastructure prompts

### Step Overrides in impl.yaml

```yaml
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

The `overrides` section in `impl.yaml` allows implementations to replace step actions without modifying the workflow.toml. This maintains the fixed step sequence while enabling implementation-specific behavior.

## Creating a New Domain Plugin

To create a new domain plugin (e.g., JiMeng markdown parser):

1. **Create impl directory**: `impls/jimeng/`

2. **Create impl.yaml**:
```yaml
name: jimeng
description: "Parses JiMeng-style agent workflow markdown files"
label: "JiMeng Parser"

overrides:
  copy_infrastructure:
    action: "noop"  # Skip if generating content only

prompt_slots:
  analyze_requirement:
    label: "Analyze JiMeng Markdown"
    default: standard
    options:
      - name: standard
        file: "prompts/analyze_requirement/jimeng/standard.txt"
  # ... other prompt slots
```

3. **Create domain prompts**: `impls/jimeng/prompts/`
   - Teach LLM how to parse JiMeng markdown structure
   - Define domain-specific artifact patterns
   - Specify output format

4. **Create domain actions** (optional): `impls/jimeng/actions/`
   - Implement JiMeng-specific parsing logic
   - Handle domain-specific transformations

## Benefits

1. **Reusability**: Infrastructure logic (actions.py) is shared across all generated workflows
2. **Self-Containment**: Domain plugins are fully self-contained in `impls/{domain}/`
3. **Flexibility**: Same AGB pipeline can produce complete workflows or content artifacts
4. **Maintainability**: Clear separation between infrastructure and domain logic
5. **Extensibility**: New domain plugins can be added without modifying AGB core

## Migration Path

Existing workflows can be migrated to the plugin architecture:

1. **Identify infrastructure vs domain logic**:
   - Infrastructure: packing, assembling, promoting, publishing
   - Domain: domain-specific actions, prompts, transformations

2. **Move domain logic to impls/{domain}/**:
   - Create `impls/{domain}/actions/` for domain actions
   - Create `impls/{domain}/prompts/` for domain prompts

3. **Update impl.yaml**:
   - Add `overrides` section to skip infrastructure steps (if needed)
   - Add `prompt_slots` for domain-specific prompts

4. **Test with AGB**:
   - Run AGB with the new impl
   - Verify domain plugin is self-contained
   - Verify infrastructure is correctly copied (for builder impl)

## Example: JiMeng Plugin

See `impls/jimeng/` for a complete example of a domain plugin that parses JiMeng-style agent workflow markdown files.

**Key Features**:
- Parses markdown structure with sections, steps, and artifacts
- Generates domain-specific actions for markdown parsing
- Produces workflow.toml with JiMeng-specific step sequence
- Self-contained in `impls/jimeng/` directory

## Future Enhancements

1. **Plugin Registry**: Auto-discover available domain plugins
2. **Plugin Validation**: Validate plugin structure and completeness
3. **Plugin Composition**: Combine multiple domain plugins
4. **Plugin Marketplace**: Share domain plugins across projects
