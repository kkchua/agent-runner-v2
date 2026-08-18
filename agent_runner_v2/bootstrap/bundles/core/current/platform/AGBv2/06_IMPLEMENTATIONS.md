# AGBv2 Implementations

> **Purpose:** Detailed documentation of the standard implementation
> **Audience:** Users creating workflow packages

---

## Overview

AGBv2 provides a single built-in implementation:

| Implementation | Use When | Output |
|----------------|----------|--------|
| **standard** (default) | Generating executable workflows | Complete workflow packages |

Select via `--impl-name standard` or operator console dropdown.

---

## Standard Implementation

**Name:** `standard`  
**Label:** Workflow Builder  
**Default:** Yes

### Purpose

Produces complete executable workflow packages with workflow.toml, actions.py, prompts/, etc.

### Pipeline

All 11 steps execute normally:

| Step | Action | Description |
|------|--------|-------------|
| 1. analyze_requirement | prompt | Parse requirement doc |
| 2. copy_infrastructure | action | Copy AGB infrastructure |
| 3. plan_domain_logic | prompt | Design domain actions + prompts |
| 4. challenge_plan | prompt | Attack the plan |
| 5. implement_domain | prompt | Write actions.py + prompts/ |
| 6. critic_impl | prompt | Review implementation |
| 7. assemble_package | action | Build structural files |
| 8. review_package | prompt | Holistic review |
| 9. validate_structure | action | Structural validation |
| 10. gatekeep_package | prompt | Final gate |
| 11. promote_package | action | Deploy to workflows/ |

### Output

```
workflows/{codename}/
├── workflow.toml              # Step sequence, routing, artifacts
├── context_extensions.py      # Artifact resolution
├── actions.py                 # Custom actions
├── prompts/                   # Prompt templates
│   └── *.txt
├── impls/                     # Alternative implementations (optional)
│   └── {name}/
│       ├── impl.yaml
│       ├── actions/
│       └── prompts/
└── README.md                  # Generated documentation
```

### Use Cases

- **Meta-workflows** — Workflows that generate other workflows
- **Reusable pipelines** — Standardized processing pipelines
- **Integration workflows** — Workflows integrating with external systems
- **Multi-step automation** — Complex multi-step processes

### When to Use

Use `standard` when you want:
- ✅ Complete executable workflow packages
- ✅ Reusable, shareable workflows
- ✅ Integration with agent-runner-v2 platform
- ✅ Multi-step automation with routing
- ❌ NOT just content generation

### Example

Requirement doc for a code review workflow:
```markdown
---
codename: "code_reviewer"
title: "Code Reviewer"
version: "1.0"
---

## Overview
Automated code review workflow for Python projects.

## Input Artifacts
- Source code files
- Coding standards document

## Output Artifacts
- Review report (markdown)
- Suggested fixes (patch format)

## Transformation Requirements
1. Parse code files
2. Analyze against standards
3. Generate review report
4. Create suggested fixes

## Constraints
- Support Python, JavaScript, TypeScript
- Do not modify original code
```

Result: Complete workflow package in `workflows/code_reviewer/`.

---

## Implementation Configuration

### standard/impl.yaml

```yaml
name: standard
description: "Produces executable workflow packages"
label: "Workflow Builder"

# No overrides — all steps execute normally

prompt_slots:
  analyze_requirement:
    label: "Analyze Requirement"
    default: standard
    options:
      - name: standard
        file: "prompts/analyze_requirement/standard.txt"
  # ... other slots
```

---

## Creating Custom Implementations

You can create custom implementations for specific domains:

### 1. Create Directory Structure

```
impls/my_domain/
├── impl.yaml
├── INPUT_ARTIFACTS.md
├── OUTPUT_ARTIFACTS.md
└── prompts/
    └── {step}/
        └── {option}.txt
```

### 2. Write impl.yaml

```yaml
name: my_domain
description: "Domain-specific implementation"
label: "My Domain"

overrides:
  # Override specific steps if needed
  analyze_requirement:
    prompt: "impls/my_domain/prompts/analyze/custom.txt"

prompt_slots:
  analyze_requirement:
    label: "Analyze My Domain"
    default: standard
    options:
      - name: standard
        file: "prompts/analyze_requirement/standard.txt"
      - name: advanced
        file: "impls/my_domain/prompts/analyze/advanced.txt"
```

### 3. Create Domain Prompts

Write specialized prompts at `impls/my_domain/prompts/{step}/{option}.txt`.

### 4. Update workflow.toml

Add implementation declaration:

```toml
[[workflow.implementation]]
name = "my_domain"
description = "Domain-specific implementation"
label = "My Domain"
```

### 5. Extend Mode

You can also use AGB's extend mode to add implementations to existing workflows:

```bash
ukbe-run-agent run --template-group artifact_generator_builder \
  --impl-name builder \
  --input-artifact REQUIREMENT_DOC=my_impl.md \
  --input-artifact EXISTING_WORKFLOW_DIR=workflows/existing_workflow/
```

---

## Implementation-Specific Guidance

Each implementation can provide guidance files:

| File | Purpose |
|------|---------|
| `INPUT_ARTIFACTS.md` | Describes expected input artifacts |
| `OUTPUT_ARTIFACTS.md` | Describes produced output artifacts |
| `SPECIALIZED_STEPS.md` | Describes domain-specific steps |

These are referenced in impl.yaml:

```yaml
guidance:
  input_artifacts: "impls/standard/INPUT_ARTIFACTS.md"
  output_artifacts: "impls/standard/OUTPUT_ARTIFACTS.md"
  specialized_steps: "impls/standard/SPECIALIZED_STEPS.md"
```

---

## See Also

- [01_ARCHITECTURE.md](./01_ARCHITECTURE.md) — Plugin architecture
- [README.md](./README.md) — Quick start
- Workflow source: `workflows/artifact_generator_builder/impls/`
