# Artifact Generator Builder v2 (AGBv2)

> **Purpose:** Transform requirement documents into executable workflow packages  
> **Status:** v3.0.0 (stable)  
> **Base Standard:** [BCS_v2.0.md](./BCS_v2.0.md)

---

## What is AGBv2?

AGBv2 is a **meta-workflow** that reads a requirement document describing what artifact generator to build, and produces a complete, executable workflow package.

```
input/requirement.md  →  [AGBv2]  →  workflows/{codename}/
```

The generated workflow is ready to run immediately — no additional coding required.

---

## Quick Start

### 1. Prepare Your Workspace

Create a workspace folder with `input/` and `output/` subfolders:

```
D:\MyProjectSpace\01_Workflows\artifact-generator-builder-v2/
├── input/          ← Place requirement.md here
└── output/         ← AGBv2 writes results here
```

### 2. Write a Requirement Document

Create `input/requirement.md` following the [Requirement Doc Guide](./03_REQUIREMENT_DOC_GUIDE.md):

```yaml
---
codename: "my_generator"
title: "My Generator"
version: "1.0"
---

## Overview
What problem does this generator solve?

## Input Artifacts
What content does it accept?

## Output Artifacts
What does it produce?

## Transformation Requirements
How does input become output?

## Constraints
Hard requirements (formats, sizes, limits).
```

See [templates/REQUIREMENT_DOC_TEMPLATE.md](./templates/REQUIREMENT_DOC_TEMPLATE.md) for a blank template.

### 3. Run AGBv2

Via CLI:
```bash
ukbe-run-agent run --template-group artifact_generator_builder
```

Via Operator Console:
- Select workflow: `artifact_generator_builder`
- Select implementation: `standard`
- Submit job

### 4. Collect Output

Find your generated workflow in:
- `output/{job_id}/` — All intermediate artifacts
- `workflows/{codename}/` — Final promoted workflow package

---

## Implementation

AGBv2 uses a single `standard` implementation that produces complete executable workflow packages.

| Implementation | Output |
|----------------|--------|
| **standard** (default) | Complete workflow package with workflow.toml, actions.py, prompts/ |

Select via `--impl-name standard` (default).

See [06_IMPLEMENTATIONS.md](./06_IMPLEMENTATIONS.md) for details on creating custom implementations.

---

## The Pipeline (11 Steps)

AGBv2 follows an SDLC-scoped pipeline with quality gates:

```
1.  analyze_requirement      → Understand the domain
2.  copy_infrastructure      → Copy AGB infrastructure (actions.py + prompts/)
3.  plan_domain_logic        → Design actions + prompts needed
4.  challenge_plan           → Attack the plan (find gaps)
    ↕ refine loop (max 2)
5.  implement_domain           → Write actions.py + prompt files
6.  critic_impl              → Review code + prompt quality
    ↕ refine loop (max 2)
7.  assemble_package         → Build workflow.toml + context_extensions.py
8.  review_package           → Holistic quality review
9.  validate_structure       → Deterministic structural validation
10. gatekeep_package          → Final pass/fail gate
11. promote_package           → Deploy to workflows/{codename}/
```

See [07_SDLC_PIPELINE.md](./07_SDLC_PIPELINE.md) for step-by-step details.

---

## Key Concepts

### Analysis JSON

The contract between step 1 (analyze) and step 7 (assemble). Contains all information needed to mechanically construct structural files. See [02_ANALYSIS_JSON_SCHEMA.md](./02_ANALYSIS_JSON_SCHEMA.md).

### Two-Tier Prompt Resolution

Prompts resolve in two tiers:
1. **Impl-specific:** `impls/{name}/prompts/{step}/{option}.txt`
2. **Shared fallback:** `prompts/{step}/{option}.txt`

See [01_ARCHITECTURE.md](./01_ARCHITECTURE.md#two-tier-prompt-resolution).

### Override Pattern

Multi-implementation model:
- `workflow.toml` = default implementation (all steps assigned)
- `impls/{name}/impl.yaml` = partial overrides (only steps that differ)

---

## Documentation Index

| Document | Purpose |
|----------|---------|
| [BCS_v2.0.md](./BCS_v2.0.md) | Base Composition Standard — workflow package contract |
| [01_ARCHITECTURE.md](./01_ARCHITECTURE.md) | Plugin architecture, implementations, two-tier resolution |
| [02_ANALYSIS_JSON_SCHEMA.md](./02_ANALYSIS_JSON_SCHEMA.md) | Complete Analysis JSON schema reference |
| [03_REQUIREMENT_DOC_GUIDE.md](./03_REQUIREMENT_DOC_GUIDE.md) | How to write requirement documents |
| [04_PROMPTS_REFERENCE.md](./04_PROMPTS_REFERENCE.md) | All prompt slots and their purpose |
| [05_ACTIONS_REFERENCE.md](./05_ACTIONS_REFERENCE.md) | Action reference (assemble, validate, promote) |
| [06_IMPLEMENTATIONS.md](./06_IMPLEMENTATIONS.md) | Implementation details and custom implementation guide |
| [07_SDLC_PIPELINE.md](./07_SDLC_PIPELINE.md) | Step-by-step pipeline walkthrough |
| [ARTIFACT_USAGE_REFERENCE.md](./ARTIFACT_USAGE_REFERENCE.md) | Artifact key usage tracking (producers, consumers, data flow) |
| [templates/REQUIREMENT_DOC_TEMPLATE.md](./templates/REQUIREMENT_DOC_TEMPLATE.md) | Blank requirement doc template |

---

## Artifacts Reference

### Input Artifacts

| Key | Description | Required |
|-----|-------------|----------|
| `REQUIREMENT_DOC` | Path to requirement.md | YES |
| `EXISTING_WORKFLOW_DIR` | Path to existing workflow (for extend mode) | NO |

### Output Artifacts

| Key | Description |
|-----|-------------|
| `ANALYSIS_JSON_FILE` | Structured analysis of requirement doc |
| `DOMAIN_PLAN_FILE` | Design plan for actions + prompts |
| `PLAN_CHALLENGE_FILE` | Critique of the plan |
| `WORKFLOW_ACTIONS_FILE` | Generated actions.py |
| `WORKFLOW_PROMPTS_DIR` | Generated prompt files |
| `WORKFLOW_REQUIREMENTS_FILE` | Generated requirements.txt |
| `IMPL_CRITIQUE_FILE` | Review of implementation |
| `WORKFLOW_MANIFEST_FILE` | Generated workflow.toml |
| `WORKFLOW_EXTENSIONS_FILE` | Generated context_extensions.py |
| `IMPL_OVERRIDE_FILES` | Implementation override files |
| `PACKAGE_REVIEW_FILE` | Holistic package review |
| `VALIDATION_FINDINGS_FILE` | Structural validation results |
| `GATEKEEP_PACKAGE_FILE` | Final gatekeeper decision |
| `WORKFLOW_PACKAGE_DIR` | Final promoted workflow directory |

---

## Version Information

- **Version:** 3.0.0
- **Job Prefix:** AGB
- **Platform:** agent-runner-v2
- **Base Standard:** BCS_v2.0

---

## See Also

- [BCS_v2.0.md](./BCS_v2.0.md) — Base Composition Standard (workflow package contract)
- Workflow source: `workflows/artifact_generator_builder/`
