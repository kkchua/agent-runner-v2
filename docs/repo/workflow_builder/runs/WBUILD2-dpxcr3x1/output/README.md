# Video Campaign Manuscript Composition System

## Overview

This workflow implements the three-layer composition architecture for short-form video campaign manuscripts. It takes a component library (Layer 1) of reusable creative building blocks and declarative composition definitions (Layer 2) as input, then produces fully resolved video production manuscripts (Layer 3) as output.

The end-to-end transformation:

1. **Scan**: Component markdown files are discovered, parsed, classified by type, and validated against the domain schema.
2. **Plan**: Composition YAML files are resolved against the component inventory. Overrides are validated, binding constraints checked, and placeholders inventoried.
3. **Generate**: Component references are expanded to full content, overrides applied, placeholders resolved from data sources, and the complete manuscript assembled.
4. **Review**: The generated manuscript is quality-reviewed for dangling references, unresolved placeholders, schema conformance, section completeness, and cross-section consistency.
5. **Refine**: Issues found during review are fixed and the manuscript is re-reviewed (up to 2 iterations).

The domain context is short-form video campaign production (15-90 seconds) for platforms including TikTok, Instagram Reels, and YouTube Shorts.

## Prerequisites

Before running this workflow, prepare the following inputs:

| Input | Description |
|---|---|
| Component Library Directory | A directory containing component markdown files organized by type subdirectories: hooks/, scenes/, voice_styles/, visual_directions/, audio_moods/, text_styles/, transitions/. Each file has YAML frontmatter with component properties. |
| Compositions Directory | A directory containing composition YAML files defining how components are assembled. Each composition references components by ID with optional overrides. |
| Data Source Directory | A directory containing Product Master, Campaign Input, and Platform Config data files for placeholder resolution. |
| Component Schema File | The component schema definition (7 types, common properties, type-specific properties, validation rules). Deployed as schema/component_schema.md in the workflow package. |
| Composition Format File | The composition format definition (binding rules, override mechanism, placeholder resolution rules). Deployed as schema/composition_format_spec.md in the workflow package. |
| Output Format File | The output format definition (section structure, resolution rules, quality requirements). Deployed as schema/output_format_spec.md in the workflow package. |

## Usage

Run the workflow using the agent-runner CLI:

```
ukbe-run-agent run --template-group video_campaign_manuscript
```

The workflow requires the following inputs to be provided at invocation time:
- COMPONENT_LIBRARY_DIR: path to the component library
- COMPOSITIONS_DIR: path to the compositions directory
- DATA_SOURCE_DIR: path to the data source directory

The schema files (COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE) are embedded in the workflow package and resolved automatically.

## Step Reference

| Seq | Step Name | Type | Phase | Purpose |
|---|---|---|---|---|
| 1 | scan_components | action | Scan | Discover and validate all components in the library |
| 2 | plan_compositions | action | Plan | Resolve compositions against inventory, validate bindings, inventory placeholders |
| 3 | generate_output | prompt | Generate | Expand components, apply overrides, resolve placeholders, assemble manuscripts |
| 4 | review_output | prompt | Review | Quality review of generated manuscripts against format requirements |
| 5 | refine_output | prompt | Refine | Fix issues found in review (conditional, max 2 iterations) |
| 6 | step_completion | action | Terminal | Mark workflow as successfully completed |

### Routing

- scan_components -> plan_compositions -> generate_output -> review_output -> step_completion
- review_output -> (on reject) -> refine_output -> review_output (loop, max 2 iterations)
- If review-refine loop exhausts 2 iterations without APPROVED verdict, workflow fails with HUMAN_RETRY_REQUIRED.

## Artifact Keys

| Artifact Key | Description | Produced By |
|---|---|---|
| COMPONENT_LIBRARY_DIR | Directory containing component markdown files organized by type subdirectory | User at invocation |
| COMPOSITIONS_DIR | Directory containing composition YAML files defining how components are assembled | User at invocation |
| DATA_SOURCE_DIR | Directory containing data source files for placeholder resolution | User at invocation |
| COMPONENT_SCHEMA_FILE | Component schema definition (7 types, properties, validation rules) | Workflow package (schema/component_schema.md) |
| COMPOSITION_FORMAT_FILE | Composition format definition (binding rules, override mechanism) | Workflow package (schema/composition_format_spec.md) |
| OUTPUT_FORMAT_FILE | Output format definition (section structure, resolution rules, quality requirements) | Workflow package (schema/output_format_spec.md) |
| COMPONENT_INVENTORY_FILE | Catalog of all discovered components with type classification and validation status | scan_components (Step 1) |
| VALIDATION_REPORT_FILE | Detailed validation results per component with rule IDs and error messages | scan_components (Step 1) |
| RESOLUTION_PLAN_FILE | Per-composition: resolved references, overrides, placeholder inventory, binding validation | plan_compositions (Step 2) |
| OUTPUT_FILE | The assembled video campaign manuscript with all components expanded and placeholders resolved | generate_output (Step 3), refine_output (Step 5) |
| REVIEW_FILE_SUGGESTED | Quality review document with APPROVED/REJECTED verdict and specific findings | review_output (Step 4) |

## Architecture

This workflow implements the three-layer composition architecture defined in COMPOSITION_SYSTEM_STANDARD.md:

### Layer 1: Component Library

The component library defines the reusable building blocks. Each component encapsulates a distinct creative concern -- an opening hook, a content scene, voice direction, visual treatment, audio mood, text overlay styling, or scene transition. Components are stored as markdown files with YAML frontmatter and organized into type-specific subdirectories.

The schema defines exactly 7 component types:
1. **hook** -- Opening sequence that captures attention (singleton, required)
2. **scene** -- Content segment with narrative purpose (ordered list 3-8, required)
3. **voice_style** -- Voiceover delivery direction (singleton, required)
4. **visual_direction** -- Visual treatment and aesthetic (singleton, required)
5. **audio_mood** -- Background music and audio direction (singleton, required)
6. **text_style** -- On-screen text treatment (singleton, optional)
7. **transition** -- Scene transition effect (ordered list N-1 for N scenes, required)

### Layer 2: Composition Definitions

Compositions are declarative YAML documents that specify how components are assembled. They reference components by component_id (never copying content) and optionally override specific properties. Placeholders in override values are resolved from external data sources at generation time.

Key features:
- Reference pattern: Components referenced by ID, not duplicated
- Override mechanism: Per-composition customization with schema conformance
- Placeholder resolution: {field_name} tokens resolved from Product Master, Campaign Input, Platform Config
- Binding rules: 7 binding slots (6 required, 1 optional) with cardinality constraints

### Layer 3: Resolved Output

The resolved output is a complete, self-contained video production manuscript. All component references are expanded, all overrides applied, all placeholders resolved. The output is consumed by downstream workflows (voiceover generation, visual asset creation, video editing, platform adaptation).

Output structure:
- YAML frontmatter with metadata
- Opening (Hook), Voice Direction, Visual Treatment, Scene-by-Scene Breakdown, Audio Direction, Text Overlay (conditional), Production Notes

### Mixed Workflow Type

The workflow uses both action steps and prompt-driven steps:
- **Action steps** (scan_components, plan_compositions): Deterministic operations -- file I/O, YAML parsing, schema validation, reference resolution. These are implemented as Python functions in actions.py.
- **Prompt steps** (generate_output, review_output, refine_output): Judgment operations -- manuscript assembly, quality review, issue correction. These use LLM-based coders with prompt templates.

## File Inventory

| File | Purpose |
|---|---|
| workflow.toml | Workflow manifest defining all 6 steps, routing, artifact declarations, and coder roles |
| context_extensions.py | Artifact key registration and context injection module |
| actions.py | Python implementations for scan_components and plan_compositions actions |
| prompts/03_generate_output.txt | Prompt template for manuscript generation |
| prompts/04_review_output.txt | Prompt template for quality review |
| prompts/05_refine_output.txt | Prompt template for issue refinement |
| prompts_index.json | Index of all prompt files with step mapping |
| README.md | This file -- user guide |
