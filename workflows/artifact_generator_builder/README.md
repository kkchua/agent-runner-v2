# Artifact Generator Builder v3

Build workflow packages from requirement documents. The LLM generates domain logic (actions + prompts), infrastructure is assembled mechanically.

## Core Insight

AGB is an artifact pipeline:

```
requirement.md  →  [AGB]  →  workflow_package/
```

The platform infrastructure (step runner, routing, artifact system) is predefined and stable. The LLM only generates the domain-specific content that plugs into it.

## Pipeline (12 steps)

### Domain Phase (LLM's world)

| # | Step | Type | Purpose |
|---|------|------|---------|
| 1 | analyze_requirement | prompt | Read requirement doc, produce Analysis JSON |
| 2 | generate_domain_map | action | Generate artifact key mapping from Analysis JSON |
| 3 | plan_domain_logic | prompt | Design what actions + prompts are needed |
| 4 | challenge_plan | prompt | Attack the plan (SDLC plan ↔ challenge) |
| 5 | implement_domain | prompt | Write actions.py + prompt files |
| 6 | critic_impl | prompt | Review code logic + prompt quality (SDLC implement ↔ critic) |

### Infrastructure Phase (platform's world)

| # | Step | Type | Purpose |
|---|------|------|---------|
| 7 | copy_infrastructure | action | Copy AGB infrastructure files to target_workflow/ |
| 8 | assemble_package | action | Build workflow.toml + context_extensions.py |
| 9 | validate_structure | action | Deterministic structural validation |
| 10 | review_package | prompt | Holistic review of assembled package |
| 11 | gatekeep_package | prompt | Final pass/fail gate |
| 12 | promote_package | action | Deploy to workflows/{codename}/ + generate README |

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

Provide a requirement document (`REQUIREMENT_DOC`) in `input/`:

- **Input** — What content the generator accepts
- **Output** — What content the generator produces
- **Transformation requirements** — Business rules
- **Constraints** — Hard requirements

See `input/sample_requirement.md` for an example.

### Output

AGB produces a complete executable workflow package:

```
workflows/{codename}/
    workflow.toml              # Infrastructure (assembled)
    context_extensions.py      # Infrastructure (generated)
    actions.py                 # Infrastructure (copied from AGB)
    prompts/                   # Infrastructure (copied from AGB)
    impls/standard/
        actions.py             # Domain (LLM-generated)
        requirements.txt       # Domain (LLM-generated)
        prompts/               # Domain (LLM-generated)
        impl.yaml              # Domain (LLM-generated)
    README.md                  # Generated during promote step
```

### Running

```bash
ukbe-run-agent run --template-group artifact_generator_builder
```

## Analysis JSON

The Analysis JSON is the contract between step 1 (analyze) and step 6 (assemble). It contains all information needed to mechanically construct structural files. See BASE_COMPOSITION_STANDARD v2.0 Section 8 for the schema.

## Multi-Implementation Support

AGB itself uses implementation name `"standard"` (see workflow.toml).

Generated target workflows also use implementation name `"standard"`:
- `workflow.toml` = default implementation (all steps assigned)
- `impls/standard/impl.yaml` = domain-specific overrides (actions, prompts, requirements.txt)

## Files

| File | Purpose |
|------|---------|
| `workflow.toml` | 12-step pipeline (6 domain + 6 infrastructure) |
| `context_extensions.py` | Two-dict artifact resolution (INPUT_ARTIFACTS + OUTPUT_ARTIFACTS) |
| `actions.py` | Domain + infrastructure action implementations |
| `prompts/` | 7 prompt templates (all at root, no subdirs) |
| `input/` | Requirement documents |

## Governance

BASE_COMPOSITION_STANDARD v2.0:
```
docs/system/00_governance/foundation/current/BASE_COMPOSITION_STANDARD_v1.0.md
```

## Version

- **Version**: 3.1.0
- **Job Prefix**: AGB
- **Platform**: agent-runner-v2
