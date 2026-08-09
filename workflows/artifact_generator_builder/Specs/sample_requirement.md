---
generator_name: "example_content_transformer"
input_type: "markdown_documents"
output_type: "html_report"
version: "1.0.0"
---

# Example: Content Transformer Generator

## Purpose

Build an artifact generator that transforms markdown documents into styled HTML reports.

## Input Artifacts

| Key | Type | Description |
|-----|------|-------------|
| `MARKDOWN_FILES` | directory | Folder containing `.md` files to transform |
| `STYLE_CONFIG` | file | YAML config with styling preferences |

## Output Artifacts

| Key | Type | Description |
|-----|------|-------------|
| `HTML_REPORT` | file | Single consolidated HTML report with styling |
| `ASSETS_DIR` | directory | CSS, images, and other static assets |

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

## Extension Points

Future runtime implementations could produce:
- PDF output (via HTML → PDF conversion)
- EPUB output (for e-reader format)
- Slide deck (markdown → presentation)
