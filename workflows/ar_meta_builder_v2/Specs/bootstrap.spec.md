---
workflow_name: "ar_meta_builder_v2"
standard_name: "AMB_STANDARD"
standard_version: "v2.0.0"
standard_filename: "COMPOSITION_STANDARD.md"
output_type: "documented_versioned"
---

# AR Meta Builder v2 — Bootstrap Specification

## Purpose

Build a meta-workflow that transforms runtime specifications into complete, executable workflow packages for the agent-runner-v2 platform.

The meta-builder takes a runtime spec (describing a target workflow's domain, components, and composition requirements) and generates a full workflow package that can be immediately executed.

## Input

A runtime specification file (markdown with YAML frontmatter) containing:
- Target workflow identity (name, standard, version)
- Output delivery type (documented_versioned or direct)
- Domain description and natural phases
- Component types and their relationships
- Composition and output format requirements

## Output

A complete executable workflow package containing:
- Workflow definition (TOML format)
- Context extensions (Python)
- Custom actions (Python)
- Prompt templates (one per generation/review step)
- Documentation (README)
- Domain-specific composition standard
- Embedded builder specification (for recursive bootstrap)

### Version Naming
The generated workflow must include a **codename** (a distinctive, memorable name) that identifies this version. The output folder name follows the pattern: `{base_workflow_name}_{codename}` (e.g., `ar_meta_builder_einstein`).

The codename should be:
- Unique and distinctive
- Easy to remember and reference
- Appropriate for the workflow's character/approach

The workflow.toml `name` field must match the folder name exactly.

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
The generated workflow must be capable of bootstrapping the NEXT version of itself — given its own bootstrap spec as input, it should produce a functionally equivalent (but not necessarily identical) workflow package with a new codename. The output goes to a new folder, NEVER overwriting the source workflow.

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

The generated workflow package is successful if:
1. It can be immediately executed without manual modification
2. It produces valid, well-structured output for a given runtime spec
3. It maintains identity isolation (no meta-builder leakage)
4. It follows the three-layer composition pattern
5. It includes comprehensive validation at each phase
6. It has a unique codename and outputs to a new folder (not overwriting the source)
7. It can bootstrap the next version (recursive capability)

## What NOT to Specify

This bootstrap spec intentionally does NOT specify:
- Exact number of steps
- Exact step names
- Exact artifact key names
- Exact prompt content
- Exact routing logic
- Exact validation rules

These are implementation details that the LLM should determine based on the target domain and constraints.
