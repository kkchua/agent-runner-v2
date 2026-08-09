---
doc_type: "composition_system_spec"
lifecycle_status: "draft"
domain: "meta_content_renderer"
domain_label: "Meta Content Renderer"
job_prefix: "REND"
workflow_pattern: "action_only"
self_bootstrap_capable: false
---

# Composition System Specification: Meta Content Renderer v1

> **Domain:** Meta content format rendering
> **Spec type:** Bootstrap spec (input to ar_meta_builder_v1)
> **Standard:** AR_META_BUILDER_STANDARD
> **Upstream producer:** codebase_to_meta_v1 (produces meta content files)

---

## 1. Domain Overview

**Domain name:** `meta_content_renderer`
**Label:** Meta Content Renderer v1
**Job prefix:** `REND`
**Workflow pattern:** `action_only` (all steps are deterministic format
conversion, no LLM invocations)
**Description:** Renders audience-specific meta content Markdown files
into selectable output formats (HTML, PDF, Word, PowerPoint) via a
plugin-based renderer registry.

### 1.1 Purpose

The `codebase_to_meta_v1` workflow produces audience-specific Rich
Markdown meta content files published to `docs/repo/meta_content/current/`.
These files are human-readable but sometimes stakeholders need the content
in formal deliverable formats -- a web page, a PDF report, a Word
document, or a PowerPoint presentation.

This composition system takes a meta content Markdown file and renders it
into one or more output formats. The set of supported formats is
**plugin-extensible** -- each format has a dedicated renderer plugin in
the workflow's `renderers/` directory. Adding a new format = adding a new
renderer plugin file. No workflow logic changes.

**Trigger:** User provides a render config (`config.json`) specifying
which meta content file to render and which formats to produce.

**Outcome:** Rendered output files published to
`docs/repo/rendered_docs/current/` with full version history.

### 1.2 Domain Context

The renderer sits downstream of codebase_to_meta_v1 in the content
production pipeline. It consumes meta content files and produces
formal deliverables.

```
codebase docs --> [codebase_to_meta_v1] --> meta content (per audience)
                                                  |
                                  [meta_content_renderer_v1]
                                                  |
                                    HTML / PDF / DOCX / PPTX
```

### 1.3 Context Variables

| Context Variable | Hardcoded Path | Description |
|---|---|---|
| `META_CONTENT_ROOT` | `{repo_root}/docs/repo/meta_content/current/` | Source meta content files |
| `RENDERED_DOCS_ROOT` | `{repo_root}/docs/repo/rendered_docs/` | Output staging/publish root |
| `RENDERER_CONFIG` | `{run_root}/config.json` | Rendering configuration |

### 1.4 Render Config (config.json)

```json
{
  "source_file": "developer/META-DEV-20260808-001.md",
  "formats": ["html", "pdf"],
  "theme": "default",
  "include_toc": true,
  "slide_density": "medium"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `source_file` | string | Yes | Path relative to `META_CONTENT_ROOT` identifying which audience's meta content to render |
| `formats` | array | Yes | List of format names to render (must match registered renderers) |
| `theme` | string | No | Visual theme for HTML/PDF output (maps to CSS variables). Default: "default" |
| `include_toc` | boolean | No | Whether to generate table of contents. Default: true |
| `slide_density` | string | No | For PPTX: "low" (1 slide/section), "medium" (key points), "high" (detailed). Default: "medium" |

---

## 2. Component Schema (Layer 1)

This composition system uses 4 of the 8 universal component types to
define the meta content renderer workflow.

### 2.1 step_definition Components

The workflow has 3 steps across 3 phases.

| # | step_name | step_type | Phase | Purpose |
|---|---|---|---|---|
| 1 | `discover_renderers` | action | Discover | Scan renderers/ directory, validate config against registered renderers |
| 2 | `render_formats` | action | Render | Execute each requested renderer plugin |
| 3 | `publish_rendered` | action | Publish | Backup, history, copy to `current/` with manifest |

#### Step 1: discover_renderers (action)

Scans the `renderers/` directory for renderer plugin files. Builds a
renderer registry mapping format names to renderer implementations.
Validates the config.json `formats` list against registered renderers.
Validates the `source_file` exists under `META_CONTENT_ROOT`.

**Error handling:**
- If `renderers/` directory is missing or contains no valid renderers,
  REJECT with reject_code `NO_RENDERERS_FOUND`.
- If config.json requests a format not in the registry, REJECT with
  reject_code `UNKNOWN_FORMAT` listing available formats.
- If `source_file` does not exist under `META_CONTENT_ROOT`, REJECT
  with reject_code `SOURCE_NOT_FOUND`.
- If config.json is missing or invalid JSON, REJECT with reject_code
  `INVALID_CONFIG`.

**Returns:** APPROVED when at least one renderer is registered and all
requested formats are available.

#### Step 2: render_formats (action)

Reads the source meta content Markdown file. Executes each requested
renderer plugin in sequence. Each renderer produces one output file
in its target format.

**Error handling:**
- If a renderer plugin raises `MISSING_DEPENDENCY`, report the required
  pip package and REJECT the workflow.
- If a renderer fails mid-conversion, REJECT with reject_code
  `RENDER_FAILED` -- do not write partial output.
- If source file is empty or unreadable, REJECT with reject_code
  `INVALID_SOURCE`.

**Returns:** APPROVED when all requested formats are rendered successfully.

#### Step 3: publish_rendered (action)

Executes the publish lifecycle:

1. **Backup** -- Copy `current/` to `backups/BACKUP-{timestamp}/`
2. **History** -- Move old `current/` to `history/{job_id}/`
3. **Publish** -- Copy rendered files to `current/`
4. **Manifest** -- Write `current/render_manifest.json` listing all
   published files with format, source, theme, and timestamp.

**Returns:** APPROVED when all files are published and manifest written.

### 2.2 role_policy Components

All steps are action-type -- no role policies needed.

| step_name | policy_name | Rationale |
|---|---|---|
| `discover_renderers` | (action -- no role) | Deterministic directory scan + validation |
| `render_formats` | (action -- no role) | Deterministic format conversion |
| `publish_rendered` | (action -- no role) | Deterministic file operations |

### 2.3 routing_pattern Components

| step_name | onsuccess | on_reject_refine |
|---|---|---|
| `discover_renderers` | `render_formats` | -- |
| `render_formats` | `publish_rendered` | -- |
| `publish_rendered` | `step_completion` | -- |

No review/refine loops -- rendering is deterministic. If a step fails,
the workflow stops and reports the error.

### 2.4 artifact_contract Components

| Artifact Key | Filename Pattern | Produced By | Required |
|---|---|---|---|
| `RENDERER_INVENTORY_FILE` | `RENDERER_INV-{date}-{seq}_{slug}.md` | discover_renderers | Yes |
| `RENDERED_HTML_FILE` | `{slug}.html` | render_formats | Conditional |
| `RENDERED_PDF_FILE` | `{slug}.pdf` | render_formats | Conditional |
| `RENDERED_DOCX_FILE` | `{slug}.docx` | render_formats | Conditional |
| `RENDERED_PPTX_FILE` | `{slug}.pptx` | render_formats | Conditional |
| `RENDER_INDEX_FILE` | `render_index.json` | render_formats | Yes |
| `RENDER_MANIFEST_FILE` | `render_manifest.json` | publish_rendered | Yes |

**Note:** `RENDERED_*_FILE` artifacts are conditional -- only produced
when the corresponding format is listed in config.json `formats`. The
`{slug}` is derived from the input meta content filename (e.g.,
`META-DEV-20260808-001` becomes the base stem for all rendered outputs).

### 2.5 Renderer Plugin Format

Each renderer is a Python file in the `renderers/` directory implementing
the `BaseRenderer` interface:

```python
class BaseRenderer:
    """Abstract base for output format renderers."""
    format_name: str        # "html", "pdf", "docx", "pptx"
    file_extension: str     # ".html", ".pdf", ".docx", ".pptx"
    mime_type: str          # "text/html", "application/pdf", etc.

    def render(self, meta_content: str, metadata: dict,
               config: dict, output_path: Path) -> Path:
        """Render meta content Markdown to the target format."""
        ...
```

**Initial renderer set (4 plugins):**

1. **html_renderer.py** -- Markdown to self-contained HTML with inline
   CSS. Reuses `agent_runner_v2/site_styles.py` framework
   (`page_shell()`, `card()`, `table()`, `section()`, `COMMON_CSS`).
   Supports table of contents generation, audience-themed color schemes.
   **Dependency:** `markdown` package (already in project dependencies).

2. **pdf_renderer.py** -- HTML to PDF conversion. Inherits styling from
   the HTML renderer pipeline.
   **Dependency:** `weasyprint` or similar HTML-to-PDF engine.
   **Timeout:** 120 seconds. No partial output on failure.

3. **docx_renderer.py** -- Markdown to Word document. Maps headings,
   paragraphs, tables, code blocks to Word styles.
   **Dependency:** `python-docx`.
   **Graceful degradation:** Unsupported elements (embedded videos, SVG)
   rendered as static image placeholder -- does not fail.

4. **pptx_renderer.py** -- Markdown to PowerPoint presentation. Maps
   top-level sections to slides, extracts key points as bullet lists,
   generates title slide from frontmatter metadata.
   **Dependency:** `python-pptx`.
   **Constraint:** Max 200 slides. If exceeded, REJECT with suggestion
   to use `slide_density: "low"`.

### 2.6 Validation Rules

| Rule | Severity | Description |
|---|---|---|
| Renderers directory exists | CRITICAL | `renderers/` must exist with at least one valid renderer |
| Config validity | CRITICAL | config.json must be valid JSON with required fields |
| Format availability | CRITICAL | All requested formats must have registered renderers |
| Source file exists | CRITICAL | source_file must exist under META_CONTENT_ROOT |
| Format fidelity | HIGH | Rendered output preserves all content from source Markdown |
| Output naming | HIGH | Output filenames use same base stem as input meta content file |
| No partial output | CRITICAL | If rendering fails, do not write partial output files |
| Manifest accuracy | HIGH | render_manifest.json accurately reflects all published files |

---

## 3. Composition Format (Layer 2)

### 3.1 Composition Structure

The "composition" is the combination of a source meta content file with
requested output formats.

| Field | Type | Required | Description |
|---|---|---|---|
| `META_CONTENT_ROOT` | directory | Yes | Source meta content files |
| `renderers/` | directory | Yes | Renderer plugin implementations |
| `config.json` | file | Yes | Render configuration |

### 3.2 Binding Rules

| Binding | Source | Cardinality | Required? | Description |
|---|---|---|---|---|
| `source_meta_content` | meta content Markdown file | Singleton | Yes | The audience-specific meta content to render |
| `renderer_plugins` | renderer `.py` files | Unordered set | Yes | All registered renderer implementations |
| `render_config` | config.json | Singleton | Yes | Which formats to produce, theme, options |

### 3.3 Override Mechanism

Per-render customization via config.json fields:

- `theme` overrides the default visual theme for HTML/PDF output
- `include_toc` overrides table of contents generation
- `slide_density` overrides PowerPoint slide granularity

### 3.4 Placeholder Resolution

| Priority | Data Source | Fields Provided |
|---|---|---|
| 1 (highest) | Render config | `source_file`, `formats`, `theme`, `include_toc`, `slide_density` |
| 2 | Runtime context | `META_CONTENT_ROOT`, `RENDERED_DOCS_ROOT`, `RENDERER_CONFIG` |
| 3 | Source metadata | `audience`, `audience_label`, `generated_date`, `source_version` (from meta content YAML frontmatter) |
| 4 (lowest) | Job runtime | `job_id`, `seq`, `workspace_root` |

### 3.5 Example Composition

```
Input:
  config.json:
    source_file: "developer/META-DEV-20260808-001.md"
    formats: ["html", "pdf", "pptx"]
    theme: "default"
    include_toc: true
    slide_density: "medium"

  META_CONTENT_ROOT/
  |-- developer/
  |   +-- META-DEV-20260808-001.md    <-- source to render
  |-- architect/
  |   +-- META-ARCH-20260808-001.md
  +-- executive/
      +-- META-EXEC-20260808-001.md

Output:
  docs/repo/rendered_docs/current/
  |-- META-DEV-20260808-001.html
  |-- META-DEV-20260808-001.pdf
  |-- META-DEV-20260808-001.pptx
  +-- render_manifest.json
```

---

## 4. Output Format (Layer 3)

### 4.1 Output Structure

Rendered files use the same base stem as the input meta content file.
Output filenames: `{slug}.{extension}` where `{slug}` is derived from
the source filename.

| Format | Extension | MIME Type | Description |
|---|---|---|---|
| HTML | `.html` | `text/html` | Self-contained HTML page with inline CSS |
| PDF | `.pdf` | `application/pdf` | PDF document |
| Word | `.docx` | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | Word document |
| PowerPoint | `.pptx` | `application/vnd.openxmlformats-officedocument.presentationml.presentation` | PowerPoint presentation |

### 4.2 Resolution Rules

| Rule | Description |
|---|---|
| RR-REND-001 | Each requested format produces exactly one output file |
| RR-REND-002 | Output filename uses same base stem as input meta content file |
| RR-REND-003 | HTML output must be self-contained (inline CSS, no external references) |
| RR-REND-004 | PDF output inherits HTML styling pipeline |
| RR-REND-005 | PPTX slide count respects `slide_density` config |
| RR-REND-006 | Unrequested formats produce no output file |
| RR-REND-007 | All output files go to staging dir first, then published to `current/` |

### 4.3 Quality Requirements

| Rule | Requirement | Severity |
|---|---|---|
| QR-REND-001 | **Format fidelity** -- Rendered output preserves all content from source Markdown (no data loss) | CRITICAL |
| QR-REND-002 | **Styling consistency** -- HTML/PDF output uses site_styles.py framework | HIGH |
| QR-REND-003 | **Completeness** -- All formats requested in config.json are produced | CRITICAL |
| QR-REND-004 | **Manifest accuracy** -- render_manifest.json accurately reflects all published files | HIGH |
| QR-REND-005 | **No partial output** -- Failed renders produce no output file | CRITICAL |
| QR-REND-006 | **Traceability** -- Output filenames link back to source meta content file | HIGH |

---

## 5. Operational Requirements

### 5.1 Workflow Phases

| Phase | Purpose | Step(s) |
|---|---|---|
| **Discover** | Scan renderers/ directory, validate config against registered renderers | discover_renderers |
| **Render** | Execute each requested renderer plugin | render_formats |
| **Publish** | Backup, history, copy to `current/` with manifest | publish_rendered |

### 5.2 Input Artifacts

| Artifact Key | Description | Required? |
|---|---|---|
| `RENDERER_CONFIG` | config.json specifying source file, formats, and options | Yes |

The source meta content file is identified by `config.json` `source_file`
field (relative path under `META_CONTENT_ROOT`).

### 5.3 Output Artifacts

| Artifact Key | Description |
|---|---|
| `RENDERER_INVENTORY_FILE` | Discovered renderer plugins with metadata |
| `RENDERED_HTML_FILE` | Rendered HTML (conditional on config) |
| `RENDERED_PDF_FILE` | Rendered PDF (conditional on config) |
| `RENDERED_DOCX_FILE` | Rendered Word (conditional on config) |
| `RENDERED_PPTX_FILE` | Rendered PowerPoint (conditional on config) |
| `RENDER_INDEX_FILE` | JSON index of rendered outputs (staging) |
| `RENDER_MANIFEST_FILE` | Published manifest in `current/` |

### 5.4 Action Steps

Three custom action steps are needed:

#### discover_renderers

Scan `renderers/` directory for `.py` files (excluding `__init__.py` and
`base.py`). Import each module and verify it implements `BaseRenderer`.
Build a registry: `{format_name: renderer_instance}`. Validate
config.json formats against registry. Validate source_file exists.

**Error handling:**
- No renderers found: REJECT `NO_RENDERERS_FOUND`
- Unknown format in config: REJECT `UNKNOWN_FORMAT` with available formats
- Source file missing: REJECT `SOURCE_NOT_FOUND`
- Invalid config: REJECT `INVALID_CONFIG`

**Returns:** APPROVED when registry is built and all validations pass.

#### render_formats

Read source meta content file. Parse YAML frontmatter for metadata
(audience, title, generated_date). For each requested format, invoke
the corresponding renderer's `render()` method. Write output to staging
directory `runs/{job_id}/`.

**Error handling:**
- Missing dependency: REJECT `MISSING_DEPENDENCY` with pip package name
- Render failure: REJECT `RENDER_FAILED` -- delete any partial output
- Invalid source: REJECT `INVALID_SOURCE`
- Too many slides (PPTX): REJECT `TOO_MANY_SLIDES`

**Returns:** APPROVED when all requested formats rendered successfully.

#### publish_rendered

Same publish lifecycle as codebase_to_meta_v1:

1. If `current/` exists and contains files:
   a. Copy `current/` to `backups/BACKUP-{timestamp}/`
   b. Move `current/` to `history/{job_id}/`
2. Copy rendered files to `current/`
3. Write `current/render_manifest.json`

**Returns:** APPROVED when all files published and manifest written.

### 5.5 Domain-Specific Requirements

- The `renderers/` directory is part of the workflow package and must be
  deployed to the global runner home at install time via
  `install_to_global()`.
- The HTML renderer must reuse `agent_runner_v2/site_styles.py` which
  provides `page_shell()`, `card()`, `table()`, `section()` helpers and
  `COMMON_CSS`.
- The `markdown` Python package is already a project dependency.
- Output paths follow the standard staging pattern (`current/`, `runs/`,
  `history/`, `backups/`).
- Output filenames use the same base stem as the input meta content file
  for traceability.
- No review/refine loop needed -- rendering is deterministic. If a render
  fails, the workflow reports the error and stops.

### 5.6 Package File Inventory

The generated workflow package must include:

| File/Directory | Description |
|---|---|
| `workflow.toml` | Workflow manifest with 3 steps |
| `context_extensions.py` | Artifact key registration with hardcoded paths |
| `actions.py` | discover_renderers, render_formats, publish_rendered implementations |
| `renderers/` | Renderer plugin directory |
| `renderers/__init__.py` | RENDERER_REGISTRY + discover_renderers() |
| `renderers/base.py` | BaseRenderer ABC |
| `renderers/html_renderer.py` | Markdown to HTML renderer |
| `renderers/pdf_renderer.py` | HTML to PDF renderer |
| `renderers/docx_renderer.py` | Markdown to Word renderer |
| `renderers/pptx_renderer.py` | Markdown to PowerPoint renderer |
| `Specs/` | Directory for workflow specifications |
| `Specs/meta_content_renderer_v1.md` | Runtime spec -- defines rendering contracts and format rules |
| `README.md` | Human documentation |

### 5.7 Default Runtime Spec

The builder must generate a spec into `Specs/meta_content_renderer_v1.md`
that the generated workflow reads at runtime to know WHAT to render and
HOW. This is a different document at a different level:

| Spec | Level | Purpose |
|---|---|---|
| Bootstrap spec (this document) | Meta level | Input to AMB v1 -- tells the builder how to build the workflow |
| Runtime spec (`Specs/meta_content_renderer_v1.md`) | Runtime level | Read by the generated workflow -- defines rendering contracts, format rules, and quality criteria |

The runtime spec defines the rendering production contract:

- **Renderer plugin contract** -- BaseRenderer interface, required
  attributes (format_name, file_extension, mime_type), render() method
  signature
- **Format-specific rules** -- per-format quality requirements (HTML
  self-contained, PDF no partial output, DOCX graceful degradation,
  PPTX slide density mapping)
- **Output naming rules** -- how to derive output filenames from source
- **Quality criteria** -- format fidelity, styling consistency,
  completeness, manifest accuracy
- **Config schema** -- required and optional config.json fields with
  validation rules

The `render_formats` prompt step must reference this spec as an input.

---

## 6. References

- **Upstream producer:** `codebase_to_meta_v1` (produces meta content
  files that this workflow renders)
- **Similar workflow:** `sdlc_00_codebase_v1` (same staging/publish
  pattern)
- **HTML framework:** `agent_runner_v2/site_styles.py` (reuse for HTML
  renderer)
- **Action decorator:** `agent_runner_v2/workflow_packages/actions/__init__.py`
- **Markdown package:** already in project dependencies
- **Input source:** `docs/repo/meta_content/current/`

---

**End of Specification**
