# Text Summarizer (text_summarizer_ayz)

## Overview

Text Summarizer is an artifact generator that transforms long-form text
documents into condensed outputs. It follows the Pattern 2 (Input
Transformation) three-layer pipeline architecture.

| Property | Value |
|---|---|
| Codename | text_summarizer_ayz |
| Version | 1.0.0 |
| Pattern | Pattern2_Input_Transformation |
| Platform | agent-runner-v2 |
| Layer | layer3 |

## Implementations

Two output implementations are supported. The operator selects which
to produce at invocation time.

### summary (default)

Produces a condensed prose summary preserving the logical structure
of the original document. Output contains three blocks: intro, main
points, and conclusion. Word count is at most 20% of the original.

### key_points

Produces an ordered list of extracted key points from the source
document, each annotated with an importance score. Points are ranked
from most to least important. Original wording is preserved verbatim.

## Input

| Artifact | Format | Required | Description |
|---|---|---|---|
| INPUT_FILE | .txt or .md | Yes | Source text document to transform |

The input must be a plain text or markdown document containing
long-form content. No specific internal structure is required.

## Output

| Implementation | Artifact | Format | Description |
|---|---|---|---|
| summary | OUTPUT_SUMMARY | .txt | Condensed prose summary |
| key_points | OUTPUT_KEY_POINTS | .txt | Ordered list with scores |

## Pipeline Architecture

```
Layer 1: Input Parsing
  Step 1: parse_input (action)
    Validates input, extracts document structure.
    Output: PARSED_DOCUMENT

Layer 2: Transformation
  Step 2: analyze_structure (prompt)
    Region classification (TR-S1) and redundancy detection (TR-S2).
    Output: ANALYZED_STRUCTURE

  Step 3: score_importance (prompt)
    Importance scoring for each segment (TR-S3).
    Output: SCORED_SEGMENTS

  Step 4: identify_core_message (prompt)
    Core thesis identification (TR-S4) and profile assembly (TR-S5).
    Output: ANALYSIS_RESULT

Layer 3: Output Rendering
  Step 5: render_output (action)
    Renders final output. Default: render_summary. Override: render_key_points.
    Output: OUTPUT_DOCUMENT

  Step 6: validate_output (action)
    Validates output against quality rules. Default: validate_summary.
    Override: validate_key_points.
    Output: OUTPUT_SUMMARY or OUTPUT_KEY_POINTS

Terminal:
  Step 7: step_completion (action)
    Finalizes job and writes meta.json sidecar.
```

## File Structure

```
text_summarizer_ayz/
    workflow.toml                 # Step sequence + default implementation
    context_extensions.py         # Artifact key registration
    actions.py                    # Shared action functions
    prompts/                      # Prompt templates (Layer 2 steps)
        02_analyze_structure.txt
        03_score_importance.txt
        04_identify_core_message.txt
    standards/
        COMPOSITION_STANDARD.md   # Step contracts and invariants
    impls/
        key_points/               # Alternative implementation
            impl.yaml             # Overrides for render_output, validate_output
    Specs/
        simple_text_summarizer.md # Original requirement document
    README.md                     # This file
```

## Quality Constraints

| Rule | Scope | Check |
|---|---|---|
| OV-001 | summary | Compression ratio <= 20% |
| OV-002 | both | Source language preserved |
| OV-003 | both | No new information introduced |
| OV-004 | both | Core message retained |
| OV-005 | summary | Logical flow preserved |
| OV-006 | key_points | Points ordered by importance |
| OV-007 | key_points | Original wording preserved |
| OV-008 | key_points | Scores valid in [0.0, 1.0] |
| OV-009 | both | Single coherent document |

## Invocation

```bash
# Default implementation (summary)
ukbe-run-agent run --template-group text_summarizer_ayz

# Key points implementation
ukbe-run-agent run --template-group text_summarizer_ayz --impl key_points
```

## Extension Points

| ID | Protocol | Steps | Description |
|---|---|---|---|
| EP-001 | InputParser | parse_input | Parse input into structured form |
| EP-002 | TransformationEngine | analyze_structure, score_importance, identify_core_message | Transform Layer 1 to Layer 2 |
| EP-003 | OutputRenderer | render_output | Render final output from analysis |
| EP-004 | ValidationStrategy | validate_output | Validate output against quality rules |
