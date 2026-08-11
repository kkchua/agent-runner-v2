---
codename: "text_summarizer_ayz"
generator_name: "Text Summarizer"
version: "1.0.0"
---

# Text Summarizer Generator

## Purpose

Build an artifact generator that takes a long text document and produces one of two possible outputs, depending on the selected implementation:

1. **Concise Summary** (impl: `summary`) — A prose summary at most 20% of the original word count, preserving the source language and logical structure (intro, main points, conclusion).
2. **Key Points List** (impl: `key_points`) — An ordered list of extracted key points from the source document, each with an importance score.

Both implementations share the same input. The operator selects which output to produce at invocation time.

## Input

A text document (.txt or .md or .pdf or .docx) containing long-form content to be summarized.

## Output

Depends on the selected implementation:

- **summary** — Condensed prose summary preserving logical structure (intro → main points → conclusion).
- **key_points** — Ordered list of extracted key points with importance scores.

## Transformation Requirements

**summary impl:**
- Remove redundancy while preserving core message
- Maintain logical flow (intro → main points → conclusion)
- Condense to at most 20% of original word count

**key_points impl:**
- Identify the most important sentences/paragraphs
- Extract and rank by importance
- Preserve original meaning without paraphrasing

## Constraints

- Must be in the same language as input
- Must not introduce new information not in the original

## Standard Reference

See BASE_COMPOSITION_STANDARD_v1.0.md for all structural decisions (artifact keys, implementation declarations, file structure).
