---
codename: "example_content_transformer"
generator_name: "Example Content Transformer"
version: "1.0.0"
---

# Example: Content Transformer Generator

## Purpose

Build an artifact generator that transforms a folder of markdown documents into a styled HTML report with accompanying static assets.

## Input

- A folder containing `.md` files to transform
- A YAML configuration file with styling preferences (colors, fonts, layout)

## Output Artifacts

1. **Styled HTML Report** — A single consolidated HTML report with styling applied, table of contents auto-generated from headings, and all markdown content converted to HTML.
2. **Static Assets** — CSS stylesheets, embedded images, and other static resources referenced by the HTML report.

## Transformation Requirements

1. **Parse markdown** — Convert markdown syntax to HTML
2. **Apply styling** — Use style config for colors, fonts, layout
3. **Consolidate** — Merge multiple markdown files into single report
4. **Generate TOC** — Auto-generate table of contents from headings
5. **Embed assets** — Inline CSS and base64-encode images

## Constraints

- Must handle UTF-8 content
- Must preserve code block syntax highlighting
- Must generate responsive HTML (mobile-friendly)
- Output must be self-contained (no external dependencies)

## Standard Reference

See BASE_COMPOSITION_STANDARD_v1.0.md for all structural decisions (artifact keys, output variants, implementation declarations, file structure).
