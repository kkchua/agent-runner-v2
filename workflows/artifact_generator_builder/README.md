# Artifact Generator Builder v3

Build workflow packages from requirement documents. The LLM generates domain logic (actions + prompts), infrastructure is assembled mechanically.

## Core Insight

AGB is an artifact pipeline:

```
requirement.md  →  [AGB]  →  workflow_package/
```

The platform infrastructure (step runner, routing, artifact system) is predefined and stable. The LLM only generates the domain-specific content that plugs into it.

## Pipeline (10 steps)

| # | Step | Type | Purpose |
|---|------|------|---------|
| 1 | analyze_requirement | prompt | Read requirement doc, produce Analysis JSON |
| 2 | plan_domain_logic | prompt | Design what actions + prompts are needed |
| 3 | challenge_plan | prompt | Attack the plan (SDLC plan ↔ challenge) |
| 4 | implement_domain | prompt | Write actions.py + prompt files |
| 5 | critic_impl | prompt | Review code logic + prompt quality (SDLC implement ↔ critic) |
| 6 | assemble_package | action | Build workflow.toml + context_extensions.py + impl.yaml |
| 7 | review_package | prompt | Holistic review of assembled package |
| 8 | validate_structure | action | Deterministic structural validation |
| 9 | gatekeep_package | prompt | Final pass/fail gate |
| 10 | promote_package | action | Deploy to workflows/{codename}/ + generate README |

## What the LLM Generates

1. **actions.py** — domain-specific action functions
2. **prompts/*.txt** — domain-specific LLM instructions

## What is Assembled Mechanically

- **workflow.toml** — step sequence, routing, artifact bindings
- **context_extensions.py** — artifact key registration, path resolution
- **impl.yaml** — implementation override files
- **README.md** — generated during promote step

## Usage

### Input

Provide a requirement document (`REQUIREMENT_DOC`) specifying:

- **Input** — What content the generator accepts
- **Output** — What content the generator produces
- **Transformation requirements** — Business rules
- **Constraints** — Hard requirements

See `Specs/sample_requirement.md` for an example.

### Output

AGB produces a complete executable workflow package:

```
workflows/{codename}/
    workflow.toml
    context_extensions.py
    actions.py
    prompts/
    impls/{name}/        (alternative implementations)
    README.md
```

### Running

```bash
ukbe-run-agent run --template-group artifact_generator_builder
```

## Analysis JSON

The Analysis JSON is the contract between step 1 (analyze) and step 6 (assemble). It contains all information needed to mechanically construct structural files. See BASE_COMPOSITION_STANDARD v2.0 Section 8 for the schema.

## Multi-Implementation Support

Generated workflows support alternative implementations via the override pattern:
- `workflow.toml` = default implementation (all steps assigned)
- `impls/{name}/impl.yaml` = partial overrides (only steps that differ)

## Files

| File | Purpose |
|------|---------|
| `workflow.toml` | 10-step SDLC-scoped pipeline |
| `context_extensions.py` | Artifact key registration |
| `actions.py` | assemble_package, validate_structure, promote actions |
| `prompts/` | 7 prompt templates |
| `Specs/` | Requirement documents |

## Governance

BASE_COMPOSITION_STANDARD v2.0:
```
docs/system/00_governance/foundation/current/BASE_COMPOSITION_STANDARD_v1.0.md
```

## Version

- **Version**: 3.0.0
- **Job Prefix**: AGB
- **Platform**: agent-runner-v2
