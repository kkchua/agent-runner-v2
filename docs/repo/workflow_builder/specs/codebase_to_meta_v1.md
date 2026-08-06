# Workflow Specification: Codebase to Meta Content v1

## Overview

**Workflow name:** `codebase_to_meta_v1`
**Label:** Codebase to Meta Content v1
**Job prefix:** `META`
**Description:** Transforms codebase documentation into audience-specific Rich
Markdown meta content files via plugin-extensible audience definitions.

## Purpose

The codebase documentation under `docs/repo/codebase/current/` contains ~155
files of technical documentation (module docs, component docs, standards,
inventory, change records). This information is comprehensive but written for
a single audience -- developers who work on the codebase.

Different stakeholders need different views of the same codebase:
- **Developers** need implementation details, APIs, dependencies, setup guides
- **Architects** need design decisions, patterns, component relationships, technical debt
- **Executives** need high-level status, key metrics, risk summary, progress

This workflow scans the codebase docs and produces one Rich Markdown meta
content file per audience. The set of audiences is **plugin-extensible** --
each audience is defined by a Markdown file with YAML frontmatter in the
workflow's `audiences/` directory. Adding a new audience = dropping a new
`.md` file into `audiences/`. No workflow logic changes.

**Trigger:** User runs the workflow (no user-provided inputs -- all paths
are resolved from the repo structure).

**Outcome:** A set of audience-specific meta content Markdown files published
to `docs/repo/meta_content/current/` with full version history.

## Audience Definition Plugin System

Each audience is defined by a Markdown file in the workflow package's
`audiences/` directory:

```
workflows/codebase_to_meta_v1/
└── audiences/
    ├── developer.md
    ├── architect.md
    └── executive.md
```

Each file is Rich Markdown with YAML frontmatter:

```yaml
---
audience_id: developer
label: Developer
tone: technical, hands-on, code-first
focus_areas:
  - module APIs and signatures
  - dependency relationships
  - setup and contribution guides
  - code patterns and conventions
  - extension points
exclude:
  - high-level business summaries
  - cost/effort estimates
section_structure:
  - overview
  - module_catalog
  - api_reference
  - dependency_map
  - developer_guide
---

# Audience Definition: Developer

Generate a meta content document targeted at software developers who will
work on or extend this codebase. Emphasize practical, hands-on information
that helps a new developer get productive quickly...

[Additional prompt guidance in the body]
```

**Frontmatter fields:**
- `audience_id` -- unique identifier, becomes the output subdirectory name
- `label` -- human-readable display name
- `tone` -- writing style guidance for the LLM
- `focus_areas` -- what to emphasize from the codebase docs
- `exclude` -- what to omit
- `section_structure` -- expected output sections

**Body:** Additional prompt guidance that provides context, examples, or
constraints for the LLM generation.

**Initial audience set (3 files):**

1. `developer.md` -- Implementation-focused: module APIs, dependencies,
   setup instructions, code patterns, extension points, testing guidance.

2. `architect.md` -- Design-focused: design decisions and rationale,
   pattern analysis, component relationships, dependency graphs,
   technical debt assessment, architectural constraints.

3. `executive.md` -- Business-focused: project overview, key metrics
   (module count, test coverage, workflow count), risk summary,
   progress status, cost/effort indicators.

## Inputs

**No user-provided inputs.** All paths are resolved by the workflow:

- **Codebase documentation root** -- `docs/repo/codebase/current/`
  Contains ~155 files across 5 sections:
  - `00_standards/` (2 files) -- documentation standards and status rules
  - `01_inventory/` (1 file) -- master inventory of all Python modules
  - `02_modules/` (141 files) -- one doc per Python module
  - `03_components/` (6 files) -- cross-cutting component docs
  - `04_changes/` (4 files) -- change impact and validation records
  - `codebase_manifest.json` -- artifact inventory with metadata

- **Audience definitions** -- `audiences/` directory in the workflow package

## Outputs

### Output Root and Staging Pattern

Output follows the standard staging pattern under `docs/repo/meta_content/`:

```
docs/repo/meta_content/
├── current/                    <-- Published active meta content
│   ├── developer/
│   │   └── META-DEV-{date}-{seq}.md
│   ├── architect/
│   │   └── META-ARCH-{date}-{seq}.md
│   ├── executive/
│   │   └── META-EXEC-{date}-{seq}.md
│   └── meta_manifest.json      <-- Manifest of all published meta files
├── runs/{job_id}/              <-- Staging area (per-job work)
│   ├── developer/
│   ├── architect/
│   ├── executive/
│   ├── meta_index.json
│   └── REV-{date}-{seq}.md     <-- Review document
├── history/{job_id}/           <-- Archived previous versions
└── backups/                    <-- Pre-publish safety snapshots
```

### Output Artifacts

| Artifact Key | Description |
|---|---|
| `META_DEV_FILE` | Developer meta content (Rich Markdown + YAML frontmatter) |
| `META_ARCH_FILE` | Architect meta content (Rich Markdown + YAML frontmatter) |
| `META_EXEC_FILE` | Executive meta content (Rich Markdown + YAML frontmatter) |
| `META_INDEX` | JSON index of all generated meta files with audience metadata |
| `REVIEW_FILE_SUGGESTED` | Review document covering all generated meta files |
| `META_MANIFEST` | Published manifest in `current/` (publish target) |

### Meta Content File Format

Each output meta content file is Rich Markdown with YAML frontmatter:

```yaml
---
title: "Agent Runner V2 -- Developer Guide"
audience: developer
audience_label: Developer
generated_date: "2026-08-06"
source_version: "SDLC00CB-bgmxg5vi"
section_count: 5
---
```

Followed by the audience-tailored content organized per the audience
definition's `section_structure`.

### Publish Manifest

`meta_manifest.json` tracks all published meta files:

```json
{
  "workflow_id": "codebase_to_meta_v1",
  "change_or_run_id": "{job_id}",
  "source_codebase_version": "SDLC00CB-bgmxg5vi",
  "audiences": {
    "developer": {
      "label": "Developer",
      "file": "developer/META-DEV-20260806-001.md",
      "generated_date": "2026-08-06"
    }
  },
  "published_timestamp": "2026-08-06T12:00:00+08:00",
  "supersedes": "previous-job-id-or-null",
  "active_set": true
}
```

## Publish Lifecycle

Follows the same pattern as `sdlc_00_codebase_v1`:

1. **Stage** -- Generate meta content files into `runs/{job_id}/`
2. **Review** -- Human reviews generated content for all audiences
3. **Refine** -- Fix issues from review (loop until approved)
4. **Backup** -- Copy `current/` to `backups/BACKUP-{timestamp}/`
5. **History** -- Move old `current/` to `history/{job_id}/`
6. **Publish** -- Copy `runs/{job_id}/` to `current/` with updated manifest

## Constraints

- Each meta content file must be self-contained (readable without reference
  to the source codebase docs).
- The workflow must dynamically discover audience definitions at startup by
  scanning the `audiences/` directory for `.md` files.
- Each audience definition's YAML frontmatter drives the generation: `tone`,
  `focus_areas`, `exclude`, `section_structure` guide the LLM; the body
  provides additional prompt guidance.
- The generate step reads `codebase_manifest.json` to understand the full
  doc inventory, then selectively reads docs from each section as guided
  by each audience's `focus_areas`.
- The `audiences/` directory is part of the workflow package and must be
  deployed to the global runner home via `install_to_global()`.
- Output paths follow the standard staging pattern (`current/`, `runs/`,
  `history/`, `backups/`).
- Artifact keys use `_FILE` suffix for document artifacts.
- The workflow should follow the standard prompt-driven pattern with
  review/refine loop and human approval gate.

## References

- Source codebase docs: `docs/repo/codebase/current/`
- Codebase manifest: `docs/repo/codebase/current/codebase_manifest.json`
- Similar workflow: `sdlc_00_codebase_v1` (same staging/publish pattern)
- Existing HTML framework: `agent_runner_v2/site_styles.py` (for downstream renderer)
