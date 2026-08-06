# Workflow Specification: Meta Content Renderer v1

## Overview

**Workflow name:** `meta_content_renderer_v1`
**Label:** Meta Content Renderer v1
**Job prefix:** `REND`
**Init step:** `discover_renderers`
**Description:** Renders audience-specific meta content Markdown files into
selectable output formats (HTML, PDF, Word, PowerPoint) via a plugin-based
renderer registry.

## Purpose

The `codebase_to_meta_v1` workflow produces audience-specific Rich Markdown
meta content files published to `docs/repo/meta_content/current/`. These
files are human-readable but sometimes stakeholders need the content in
formal deliverable formats -- a web page, a PDF report, a Word document,
or a PowerPoint presentation.

This workflow takes a meta content Markdown file and renders it into one or
more output formats. The set of supported formats is **plugin-extensible** --
each format has a dedicated renderer plugin in the workflow's `renderers/`
directory. Adding a new format = adding a new renderer plugin file. No
workflow logic changes.

**Trigger:** User provides a meta content Markdown file path via config.

**Outcome:** Rendered output files published to `docs/repo/rendered_docs/current/`
with full version history.

## Workflow Type

**Action-only** -- All steps are deterministic format conversion. No LLM
invocations.

## Input Artifacts

**No user-provided required_inputs.** All paths are hardcoded as context
variables in `context_extensions.py`:

| Context Variable | Hardcoded Path | Description |
|---|---|---|
| `META_CONTENT_ROOT` | `{repo_root}/docs/repo/meta_content/current/` | Source meta content files |
| `RENDERED_DOCS_ROOT` | `{repo_root}/docs/repo/rendered_docs/` | Output staging/publish root |
| `RENDERER_CONFIG` | `{run_root}/config.json` | Rendering configuration |

### Render Config (config.json)

```json
{
  "source_file": "developer/META-DEV-20260806-001.md",
  "formats": ["html", "pdf"],
  "theme": "default",
  "include_toc": true,
  "slide_density": "medium"
}
```

- `source_file` -- path relative to `META_CONTENT_ROOT` identifying which
  audience's meta content to render
- `formats` -- list of format names to render (must match registered renderers)
- `theme` -- visual theme for HTML/PDF output (maps to CSS variables)
- `include_toc` -- whether to generate table of contents
- `slide_density` -- for PPTX: "low" (1 slide per section), "medium"
  (key points), "high" (detailed)

## Output Artifacts

| Artifact Key | Filename Pattern | Description |
|---|---|---|
| `RENDERED_HTML_FILE` | `current/{slug}.html` | Self-contained HTML page with inline CSS |
| `RENDERED_PDF_FILE` | `current/{slug}.pdf` | PDF document |
| `RENDERED_DOCX_FILE` | `current/{slug}.docx` | Word document |
| `RENDERED_PPTX_FILE` | `current/{slug}.pptx` | PowerPoint presentation |
| `RENDER_INDEX` | `runs/{job_id}/render_index.json` | JSON index of rendered outputs (staging) |
| `RENDER_MANIFEST` | `current/render_manifest.json` | Published manifest (publish target) |

Only formats listed in config.json are produced. Unselected formats have
no output artifact. The `{slug}` is derived from the input meta content
filename (e.g., `META-DEV-20260806-001`).

## Renderer Plugin System

Each output format is implemented as a renderer plugin in the workflow
package's `renderers/` directory:

```
workflows/meta_content_renderer_v1/
└── renderers/
    ├── __init__.py         <-- RENDERER_REGISTRY + discover_renderers()
    ├── base.py             <-- BaseRenderer ABC
    ├── html_renderer.py    <-- Markdown -> self-contained HTML
    ├── pdf_renderer.py     <-- HTML -> PDF
    ├── docx_renderer.py    <-- Markdown -> Word document
    └── pptx_renderer.py    <-- Markdown -> PowerPoint presentation
```

### BaseRenderer Interface

```python
class BaseRenderer:
    """Abstract base for output format renderers."""
    format_name: str        # "html", "pdf", "docx", "pptx"
    file_extension: str     # ".html", ".pdf", ".docx", ".pptx"
    mime_type: str          # "text/html", "application/pdf", etc.

    def render(self, meta_content: str, metadata: dict, output_path: Path) -> Path:
        """Render meta content Markdown to the target format."""
        ...
```

### Initial Renderer Set (4 plugins):

1. **html_renderer.py** -- Converts Markdown to self-contained HTML page
   with inline CSS. Reuses `agent_runner_v2/site_styles.py` framework
   (`page_shell()`, `card()`, `table()`, `section()`, `COMMON_CSS`).
   Supports table of contents generation, audience-themed color schemes.

2. **pdf_renderer.py** -- Converts rendered HTML to PDF document. Uses
   HTML-to-PDF conversion (e.g., weasyprint or similar). Inherits styling
   from the HTML renderer.

3. **docx_renderer.py** -- Converts Markdown to Word document using
   python-docx. Maps Markdown headings, paragraphs, tables, code blocks
   to Word styles.

4. **pptx_renderer.py** -- Converts Markdown to PowerPoint presentation
   using python-pptx. Maps top-level sections to slides, extracts key
   points as bullet lists, generates title slide from frontmatter metadata.

## Publish Lifecycle

Follows the same pattern as `sdlc_00_codebase_v1`:

1. **Stage** -- Render selected formats into `runs/{job_id}/`
2. **Backup** -- Copy `current/` to `backups/BACKUP-{timestamp}/`
3. **History** -- Move old `current/` to `history/{job_id}/`
4. **Publish** -- Copy `runs/{job_id}/` to `current/` with updated manifest

No review step -- rendering is deterministic format conversion. If a
render fails, the workflow reports the error and stops.

## Constraints

- The renderer plugin interface must follow the existing `@action` decorator
  pattern from `workflow_packages/actions/__init__.py` for package-local
  actions.
- The HTML renderer must reuse `agent_runner_v2/site_styles.py` which
  provides `page_shell()`, `card()`, `table()`, `section()` helpers and
  `COMMON_CSS` -- a complete CSS framework with print/PDF styles.
- The `markdown` Python package is already a project dependency and must
  be used for Markdown-to-HTML conversion.
- Output paths follow the standard staging pattern (`current/`, `runs/`,
  `history/`, `backups/`).
- The `renderers/` directory is part of the workflow package and must be
  deployed to the global runner home via `install_to_global()`.
- Output filenames use the same base stem as the input meta content file
  for traceability.

## Quality Requirements

- **Format fidelity** -- Rendered output preserves all content from the
  source Markdown (no data loss).
- **Styling consistency** -- HTML/PDF output uses site_styles.py framework.
- **Completeness** -- All formats requested in config.json are produced.
- **Manifest accuracy** -- render_manifest.json accurately reflects all
  published files.

## Builder Instructions

**Step architecture:** The builder shall propose the step sequence. This is
an action-only workflow (no LLM steps). Suggested phase decomposition
(builder may adjust):

1. **Discover phase** -- Scan renderers/ directory, validate config.json
   formats against registered renderers
2. **Render phase** -- Execute each requested renderer (may be one step per
   format or a single step iterating over formats)
3. **Publish phase** -- Backup, history, copy to current/ with manifest

**Action reuse:** Check if existing publish actions (backup, history, copy
to current) can be reused from other workflows.

**No gatekeepers needed** -- This is an action-only workflow with deterministic
output. Validation is handled by the renderer plugins themselves (fail fast
if format conversion fails).

**install_to_global():** The `renderers/` directory must be deployed to the
global runner home. The workflow's `context_extensions.py` must implement
real `install_to_global()` logic.

## Notes

- Input source: `docs/repo/meta_content/current/` (from codebase_to_meta_v1)
- Similar workflow: `sdlc_00_codebase_v1` (same staging/publish pattern)
- HTML framework: `agent_runner_v2/site_styles.py` (reuse for HTML renderer)
- Action decorator: `agent_runner_v2/workflow_packages/actions/__init__.py`
- Markdown package: already in project dependencies
