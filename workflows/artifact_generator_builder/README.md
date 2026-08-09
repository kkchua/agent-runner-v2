# Artifact Generator Builder

Build artifact generators that transform input content into output artifacts following a consistent, mandatory pattern:

```
Input → Composition Spec → Runtime Implementation → Output
```

## Overview

The Artifact Generator Builder (AGB) is a meta-workflow that creates other workflows (artifact generators). Each generated generator follows the same universal pattern, ensuring consistency across all generators.

**Key Concepts:**

- **Composition Spec** — Defines transformation rules, meta schema, and structure
- **Runtime Implementation** — Concrete executor that follows the composition spec
- **Mandatory Pattern** — ALL generators follow input → spec → impl → output

## Usage

### Input

Provide a requirement document (`REQUIREMENT_DOC`) specifying:

- **Input artifacts** — What content the generator will accept
- **Output artifacts** — What content the generator will produce
- **Transformation requirements** — How to convert input to output
- **Constraints** — Hard requirements for the generator

See `Specs/sample_requirement.md` for an example.

### Output

AGB produces a complete executable workflow package:

| File | Description |
|------|-------------|
| `workflow.toml` | Workflow definition with steps and routing |
| `context_extensions.py` | Artifact key registration and path resolution |
| `actions.py` | Custom action implementations |
| `prompts/*.txt` | Prompt templates for each step |
| `README.md` | Documentation for the generated workflow |

### Running

```bash
# Using the CLI
ukbe-run-agent run --template-group artifact_generator_builder

# Or via daemon
# Submit a job with the requirement document path
```

## Workflow Phases

AGB follows a 7-phase process with built-in validation:

### Phase 1: Analyze Requirement
- **Generate** → Understand input/output specifications
- **Review** → Check completeness and accuracy
- **Gatekeep** → Approve for next phase

### Phase 2: Design Composition Spec
- **Generate** → Define transformation rules and meta schema
- **Review** → Verify spec compliance and feasibility
- **Gatekeep** → Approve for implementation design

### Phase 3: Design Runtime Implementation
- **Generate** → Design the executor that follows the spec
- **Review** → Verify implementation correctness
- **Gatekeep** → Approve for artifact definition

### Phase 4: Define Artifacts
- **Generate** → Specify all artifact keys and paths
- **Gatekeep** → Validate artifact contract

### Phase 5: Design Steps
- **Generate** → Define workflow steps and routing
- **Gatekeep** → Validate step sequence

### Phase 6: Generate Package
- **Generate** → Produce workflow files (toml, py, prompts)
- **Review** → Check package completeness and identity isolation
- **Gatekeep** → Approve for promotion

### Phase 7: Promote Package
- **Action** → Backup existing workflow and copy new one to target location

## Self-Bootstrap

AGB can build itself! The self-bootstrap requirement specifies:

- **Input**: Requirement documents
- **Output**: Artifact generators (workflow packages)

This creates a recursive chain where AGB can produce improved versions of itself.

## Extension Points

Generated generators can support multiple output types:

1. **Default runtime implementation** — Produced by AGB
2. **Additional runtime implementations** — Can be added later without modifying the generator

Users select which runtime implementation to use when running the generator.

## Design Principles

1. **Mandatory Pattern** — All generators follow input → spec → impl → output
2. **Consistency** — Universal interface across all generators
3. **Extensibility** — Add new output types without code changes
4. **Validation** — Self-critic, review, and gatekeep at each phase
5. **Identity Isolation** — Generated workflows use target identity, not builder's

## Files

| File | Purpose |
|------|---------|
| `workflow.toml` | 7-phase workflow definition |
| `context_extensions.py` | Artifact key registration |
| `actions.py` | Promotion action |
| `prompts/` | 18 prompt templates (generate, review, refine, gatekeep) |
| `Specs/sample_requirement.md` | Example requirement document |

## Governance

The composition system standard is located at:
```
docs/system/00_governance/foundation/current/COMPOSITION_SYSTEM_STANDARD.md
```

At runtime, it's accessed via:
```python
{GOVERNANCE_RUNTIME_ROOT}/COMPOSITION_SYSTEM_STANDARD.md
```

## Version

- **Version**: 1.0.0
- **Job Prefix**: AGB
- **Platform**: agent-runner-v2
