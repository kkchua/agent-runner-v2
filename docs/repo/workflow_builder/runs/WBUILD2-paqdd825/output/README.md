# Video Campaign Manuscript Composition System

## Overview

This workflow resolves declarative component compositions into self-contained
video campaign production manuscripts. It implements the three-layer
composition architecture:

- Layer 1 (Component Library): Standardized, reusable creative building blocks
  including hooks, scenes, voice styles, visual directions, audio moods, text
  styles, and transitions.

- Layer 2 (Composition Definitions): Declarative assembly instructions that
  reference components by ID, specify per-composition overrides, and bind
  placeholders to external data sources.

- Layer 3 (Resolved Outputs): Complete, self-contained production manuscripts
  with all references expanded, overrides applied, and placeholders filled.

The workflow follows a five-phase pattern: scan, plan, generate, review, and
refine. The scan and plan phases use deterministic actions for file discovery,
parsing, and validation. The generate, review, and refine phases use LLM-driven
prompts for creative assembly and quality assessment.

## Prerequisites

The following inputs must be available before running the workflow:

| Artifact Key | Description |
|---|---|
| COMPONENT_LIBRARY_DIR | Directory containing component markdown files organized by type subdirectories (hooks/, scenes/, voice_styles/, visual_directions/, audio_moods/, text_styles/, transitions/). Each .md file has YAML frontmatter with component properties. |
| COMPOSITIONS_DIR | Directory containing composition YAML files defining assembly instructions. Each YAML file specifies composition_id, target_metadata, data_sources, and component_bindings. |
| DATA_SOURCE_DIR | Directory containing placeholder resolution data files (product_master/, platform_config/, campaign_input/). Each YAML file provides field values for placeholder resolution. |
| COMPONENT_SCHEMA_FILE | Path to the component schema document defining types, properties, and validation rules for this domain. |
| OUTPUT_FORMAT_FILE | Path to the output format specification defining section structure, frontmatter fields, and formatting rules. |

## Usage

Run the workflow using the agent-runner CLI:

```bash
ukbe-run-agent run --template-group video_campaign_manuscript
```

Or via the daemon:

```bash
ukbe-run-agent daemon
```

The daemon will pick up jobs assigned to the video_campaign_manuscript
template group and execute all steps automatically.

## Step Reference

| # | Step Name | Type | Phase | Purpose |
|---|---|---|---|---|
| 1 | scan_components | action | Scan | Discover component files, parse YAML frontmatter, build inventory |
| 2 | validate_components | action | Scan | Validate components against schema rules |
| 3 | plan_compositions | action | Plan | Parse compositions, resolve references, validate overrides, inventory placeholders |
| 4 | generate_output | prompt | Generate | Expand references, merge overrides, resolve placeholders, assemble output |
| 5 | review_output | prompt | Review | Quality review against output format requirements |
| 6 | refine_output | prompt | Refine | Fix issues from review (conditional, on REJECTED verdict) |
| 7 | promote | action | Promotion | Deploy package to workflows/ directory |
| 8 | stepCompletion | action | Terminal | Mark workflow as successfully completed |

### Review-Refine Loop

Steps 5 and 6 form a review-refine loop with max_iterations = 2. If the review
finds issues (REJECTED verdict), the workflow routes to refine_output, which
fixes the issues and routes back to review_output. If the second review also
produces REJECTED, the workflow terminates with failure code
OUTPUT_REVIEW_EXHAUSTED and failure class HUMAN_RETRY_REQUIRED.

## Artifact Keys

### Input Artifacts

| Key | Description |
|---|---|
| COMPONENT_LIBRARY_DIR | Directory path containing component markdown files |
| COMPOSITIONS_DIR | Directory path containing composition YAML files |
| DATA_SOURCE_DIR | Directory path containing data source files |
| COMPONENT_SCHEMA_FILE | Path to the component schema document |
| OUTPUT_FORMAT_FILE | Path to the output format specification |

### Output Artifacts

| Key | Description | Produced By |
|---|---|---|
| COMPONENT_INVENTORY_FILE | YAML inventory of all discovered components | scan_components |
| VALIDATION_REPORT_FILE | YAML validation report with per-component results | validate_components |
| RESOLUTION_PLAN_FILE | YAML resolution plan with binding maps and placeholder inventory | plan_compositions |
| OUTPUT_FILE | Resolved production manuscript (markdown with YAML frontmatter) | generate_output, refine_output |
| REVIEW_FILE_SUGGESTED | Structured review report with findings and verdict | review_output |

## Architecture

### Three-Layer Composition Architecture

The workflow implements a clean separation of concerns through three layers:

Layer 1 (Component Library): Components are immutable reference material. Each
component has a unique component_id and encapsulates a distinct creative concern
(opening sequence, content segment, voice direction, visual treatment, audio
direction, text treatment, or scene transition). Components are stored as
markdown files with YAML frontmatter.

Layer 2 (Composition Definitions): Compositions are declarative assembly
instructions. They reference components by component_id (never inline content),
specify overrides for per-composition customization, and declare placeholder
bindings to external data sources. Compositions support singleton bindings
(one component per slot) and ordered list bindings (multiple components in
sequence).

Layer 3 (Resolved Outputs): Outputs are self-contained deliverables. All
component_id references are expanded to full content, overrides are merged
(override wins on conflict), placeholders are resolved from data sources, and
unresolved placeholders are flagged as {UNRESOLVED: field_name}. The output is
organized into domain-defined sections for downstream consumption.

### Five-Phase Workflow Pattern

The workflow follows the universal composition system pattern:

1. Scan Phase (Steps 1-2): Discover and validate the component library.
   Deterministic action steps for file I/O and schema validation.

2. Plan Phase (Step 3): Resolve compositions against the inventory.
   Deterministic action step for reference resolution and constraint checking.

3. Generate Phase (Step 4): Assemble fully resolved outputs.
   LLM-driven prompt step for creative formatting and coherence.

4. Review Phase (Step 5): Quality review of generated outputs.
   LLM-driven prompt step for semantic assessment against criteria.

5. Refine Phase (Step 6): Fix issues found during review.
   LLM-driven prompt step, conditional on review rejection.

### Domain Context

Short-form video campaign production for digital advertising and branded content
across platforms such as TikTok, Instagram Reels, and YouTube Shorts. The end
deliverable is a production manuscript that downstream workflows consume to
generate voiceover audio, visual assets, video edits, and platform-specific
adaptations.
