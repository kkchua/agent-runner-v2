---
codename: "text_summarizer_ayz"
generator_name: "Text Summarizer"
version: "1.0.0"
---

# Text Summarizer Generator

## Purpose

Build an artifact generator that takes a long text document and produces two outputs: a concise summary and an extracted key points list.

## Input

A text document (.txt or .md) containing long-form content to be summarized.

## Output Artifacts

1. **Condensed Summary** — A prose summary at most 20% of the original word count, preserving the source language and logical structure (intro, main points, conclusion).
2. **Key Points List** — An ordered list of extracted key points from the source document, each with an importance score.

## Transformation Requirements

1. **Extract key points** — Identify the most important sentences/paragraphs
2. **Remove redundancy** — Eliminate repetitive content
3. **Preserve meaning** — Summary must capture the core message
4. **Maintain structure** — Keep logical flow (intro → main points → conclusion)

## Constraints

- Summary must be at most 20% of original word count
- Must be in the same language as input
- Must not introduce new information not in the original
