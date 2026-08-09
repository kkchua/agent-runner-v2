---
workflow_name: "ar_meta_builder_v2"
standard_name: "AMB_STANDARD"
standard_version: "v2.0.0"
standard_filename: "COMPOSITION_STANDARD.md"
output_type: "documented_versioned"
---

# AR Meta Builder v2 — Bootstrap Specification

## Purpose

Build a meta-workflow that transforms a bootstrap specification into a complete composition system for the agent-runner-v2 platform.

The meta-builder takes a bootstrap spec (describing a target workflow's domain, components, and composition requirements) and generates three deliverables: a master spec, a default runtime implementation, and a full executable workflow package.

## Input

A bootstrap specification file (`BOOTSTRAP_SPEC_FILE`, markdown with YAML frontmatter) containing:
- Target workflow identity (name, standard, version)
- Output delivery type (documented_versioned or direct)
- Domain description and natural phases
- Component types and their relationships
- Composition and output format requirements

## Output

Three deliverables that together form a complete composition system:

### 1. Master Spec
An enhanced composition system specification for the NEXT generation of the meta-builder:
- NOT a copy of the input bootstrap spec — it is a new, improved evolution
- Component schema and relationships
- Composition format and rules
- Output format and delivery contracts
- Validation and quality gates
- Includes the fixed promotion/backup/publish logic (propagates to next version)
- Named `{workflow_name}_{codename}.md` for development; future CLI promotes to `{workflow_name}_v{version}.md`

### 2. Default Runtime Implementation (`default.impl.md`)
A concrete, default implementation of the master spec:
- Specific component instances with values
- Example composition demonstrating the format
- Expected output examples
- Serves as both a test case and usage documentation

### 3. Workflow Package
A complete executable workflow package containing:
- Workflow definition (TOML format)
- Context extensions (Python)
- Custom actions (Python)
- Prompt templates (one per generation/review step)
- Documentation (README)
- Domain-specific composition standard

### Version Naming
All three deliverables share a **codename** (a distinctive, memorable name) that identifies this version. The output folder name follows the pattern: `{base_workflow_name}_{codename}` (e.g., `ar_meta_builder_einstein`).

The codename should be:
- Unique and distinctive
- Easy to remember and reference
- Appropriate for the workflow's character/approach

The workflow.toml `name` field must match the folder name exactly.

## Promotion, Backup and Publish

After a successful meta-builder run, the three deliverables are promoted to their target locations:

All documentation deliverables are self-contained under `docs/repo/{workflow_name}/`:

| Deliverable | Target Location |
|---|---|
| Master spec | `docs/repo/{workflow_name}/specs/` |
| Composition standard | `docs/repo/{workflow_name}/standards/` |
| Default runtime implementation | `docs/repo/{workflow_name}/impls/` |
| Workflow package | `workflows/{workflow_name}/` |

### Backup
Before promoting, backup any existing files at the target locations. The workflow package backup uses the existing backup mechanism (timestamped copy under `workflows/{slug}_bak_{timestamp}/`).

### Publish
After promotion, run `run-bootstrap-publish.bat` to package the updated workflow into the bootstrap bundle, then `run-init.bat` to install it to the global runner home.

## Constraints

### Identity Isolation
The meta-builder's own identity (ar_meta_builder_v2, AMB_STANDARD) must NEVER leak into generated output. The generated workflow uses the TARGET spec's identity exclusively.

### Three-Layer Architecture
Every generated workflow must follow the composition system pattern:
- Layer 1: Component definitions (what the building blocks are)
- Layer 2: Composition format (how they fit together)
- Layer 3: Resolved outputs (complete deliverables)

### Test-Driven Development
Each phase of the generated workflow must include:
- Generation step (creates the artifact)
- Review step (LLM validates quality)
- Validation step (deterministic checks)
- Gatekeeping step (final approval)

### Recursive Capability
The master spec IS the enhanced specification for the NEXT generation of the meta-builder. The recursive chain is:

```
bootstrap spec (input) → meta-builder run → master spec (enhanced, for next version)
                                                ↓
                                    next run uses master spec as BOOTSTRAP_SPEC_FILE input
```

The output goes to a new folder (`{workflow_name}_{codename}`), NEVER overwriting the source workflow. The codename differentiates development versions; a future CLI command promotes to official `{workflow_name}_v{version}`.

### Artifact Tracking
All generated artifacts must be:
- Declared in the workflow definition
- Tracked through context extensions
- Validated for existence after each step
- Named with clear, domain-appropriate keys

### Prompt Quality
Generated prompts must:
- Reference only declared input artifacts
- Include self-validation sections
- Specify forbidden content explicitly
- Use placeholder syntax correctly ({ARTIFACT_KEY})

## Knowledge Requirements

The meta-builder must understand:
- agent-runner-v2 workflow package structure
- Composition system standard (three-layer architecture)
- Test-driven workflow patterns
- Artifact key naming conventions
- Prompt engineering for LLM coders
- Recursive meta-system design

## Success Criteria

The meta-builder run is successful if:
1. A master spec is produced that fully defines the composition system
2. A default runtime implementation (`default.impl.md`) is produced that satisfies the master spec
3. The workflow package can be immediately executed without manual modification
4. The workflow produces valid, well-structured output for the default runtime implementation
5. It maintains identity isolation (no meta-builder leakage)
6. It follows the three-layer composition pattern
7. It includes comprehensive validation at each phase
8. All three deliverables share a unique codename and output to a new folder (not overwriting the source)
9. It can bootstrap the next version (recursive capability)

## What NOT to Specify

This bootstrap spec intentionally does NOT specify:
- Exact number of steps
- Exact step names
- Exact artifact key names
- Exact prompt content
- Exact routing logic
- Exact validation rules

These are implementation details that the LLM should determine based on the target domain and constraints.
