# Workflow Specification: Meta Content Renderer v1

## Overview

**Workflow name:** `meta_content_renderer_v1`
**Label:** Meta Content Renderer v1
**Job prefix:** `REND`
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

**Trigger:** User provides a meta content Markdown file and a config
specifying which formats to render.

**Outcome:** Rendered output files published to `docs/repo/rendered_docs/current/`
with full version history.

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
        """Render meta content Markdown to the target format.

        Args:
            meta_content: Raw Markdown content (including YAML frontmatter)
            metadata: Parsed frontmatter dict (title, audience, date, etc.)
            output_path: Directory to write the output file

        Returns:
            Path to the rendered output file
        """
        ...
```

### Renderer Registry

The `renderers/__init__.py` maintains a `RENDERER_REGISTRY` dict mapping
format names to renderer classes. The `discover_renderers()` function scans
the `renderers/` directory and auto-registers all `BaseRenderer` subclasses.

### Initial Renderer Set (4 plugins):

1. **html_renderer.py** -- Converts Markdown to self-contained HTML page
   with inline CSS. Should reuse the existing `agent_runner_v2/site_styles.py`
   framework (`page_shell()`, `card()`, `table()`, `section()`, `COMMON_CSS`).
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

## Inputs

**META_CONTENT_FILE** -- A meta content Rich Markdown file from
`docs/repo/meta_content/current/`. The user selects which audience's
meta content to render.

**RENDERER_CONFIG** -- Config file specifying rendering options:

```json
{
  "formats": ["html", "pdf"],
  "theme": "default",
  "include_toc": true,
  "slide_density": "medium"
}
```

- `formats` -- list of format names to render (must match registered renderers)
- `theme` -- visual theme for HTML/PDF output (maps to CSS variables)
- `include_toc` -- whether to generate table of contents
- `slide_density` -- for PPTX: "low" (1 slide per section), "medium"
  (key points), "high" (detailed)

## Outputs

### Output Root and Staging Pattern

Output follows the standard staging pattern under `docs/repo/rendered_docs/`:

```
docs/repo/rendered_docs/
├── current/                    <-- Published rendered outputs
│   ├── {slug}.html
│   ├── {slug}.pdf
│   ├── {slug}.docx
│   ├── {slug}.pptx
│   └── render_manifest.json    <-- Manifest of all published renders
├── runs/{job_id}/              <-- Staging area (per-job work)
│   ├── {slug}.html
│   ├── {slug}.pdf
│   ├── {slug}.docx
│   ├── {slug}.pptx
│   └── render_index.json       <-- Index of rendered outputs
├── history/{job_id}/           <-- Archived previous versions
└── backups/                    <-- Pre-publish safety snapshots
```

The `{slug}` is derived from the input meta content filename
(e.g., `META-DEV-20260806-001.md` -> slug `META-DEV-20260806-001`).

### Output Artifacts

| Artifact Key | Description |
|---|---|
| `RENDERED_HTML_FILE` | Self-contained HTML page with inline CSS |
| `RENDERED_PDF_FILE` | PDF document |
| `RENDERED_DOCX_FILE` | Word document |
| `RENDERED_PPTX_FILE` | PowerPoint presentation |
| `RENDER_INDEX` | JSON index of all rendered outputs (staging) |
| `RENDER_MANIFEST` | Published manifest in `current/` (publish target) |

Only formats listed in `config.json` are produced. Unselected formats
have no output artifact.

### Render Manifest

`render_manifest.json` tracks all published rendered outputs:

```json
{
  "workflow_id": "meta_content_renderer_v1",
  "change_or_run_id": "{job_id}",
  "source_meta_file": "developer/META-DEV-20260806-001.md",
  "source_audience": "developer",
  "rendered_formats": {
    "html": {
      "file": "META-DEV-20260806-001.html",
      "renderer_version": "1.0"
    },
    "pdf": {
      "file": "META-DEV-20260806-001.pdf",
      "renderer_version": "1.0"
    }
  },
  "published_timestamp": "2026-08-06T14:00:00+08:00",
  "supersedes": "previous-job-id-or-null",
  "active_set": true
}
```

## Publish Lifecycle

Follows the same pattern as `sdlc_00_codebase_v1`:

1. **Stage** -- Render selected formats into `runs/{job_id}/`
2. **Review** -- (Optional) Human reviews rendered outputs
3. **Backup** -- Copy `current/` to `backups/BACKUP-{timestamp}/`
4. **History** -- Move old `current/` to `history/{job_id}/`
5. **Publish** -- Copy `runs/{job_id}/` to `current/` with updated manifest

## Constraints

- This is an **action-only workflow** (no LLM steps). Rendering is
  deterministic format conversion.
- The renderer plugin interface must follow the existing `@action` decorator
  pattern from `workflow_packages/actions/__init__.py` for package-local
  actions.
- The HTML renderer should reuse `agent_runner_v2/site_styles.py` which
  provides `page_shell()`, `card()`, `table()`, `section()` helpers and
  `COMMON_CSS` -- a complete CSS framework with print/PDF styles.
- The `markdown` Python package is already a project dependency and should
  be used for Markdown-to-HTML conversion.
- Output paths follow the standard staging pattern (`current/`, `runs/`,
  `history/`, `backups/`).
- Artifact keys use `_FILE` suffix for document artifacts.
- The `renderers/` directory is part of the workflow package and must be
  deployed to the global runner home.
- The `{slug}` for output filenames is derived from the input meta content
  filename to maintain traceability.

## References

- Input source: `docs/repo/meta_content/current/` (from codebase_to_meta_v1)
- Similar workflow: `sdlc_00_codebase_v1` (same staging/publish pattern)
- HTML framework: `agent_runner_v2/site_styles.py` (reuse for HTML renderer)
- Action decorator: `agent_runner_v2/workflow_packages/actions/__init__.py`
- Markdown package: already in project dependencies
