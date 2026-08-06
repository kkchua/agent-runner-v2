# Workflow Specification: Codebase to Meta Content v1

## Overview

**Workflow name:** `codebase_to_meta_v1`
**Label:** Codebase to Meta Content v1
**Job prefix:** `META`
**Init step:** `scan_audiences`
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

## Workflow Type

**Mixed** -- Action steps for scanning and publishing, prompt-driven steps
for content generation and review.

## Input Artifacts

**No user-provided inputs.** All paths are hardcoded as context variables
in `context_extensions.py`:

| Context Variable | Hardcoded Path | Description |
|---|---|---|
| `CODEBASE_DOC_ROOT` | `{repo_root}/docs/repo/codebase/current/` | Source codebase documentation |
| `META_CONTENT_ROOT` | `{repo_root}/docs/repo/meta_content/` | Output staging/publish root |
| `AUDIENCE_DIR` | `{workflow_package}/audiences/` | Audience definition plugins |

## Output Artifacts

| Artifact Key | Filename Pattern | Description |
|---|---|---|
| `AUDIENCE_INVENTORY` | `AUDIENCE_INV-{date}-{seq}_{slug}.md` | Discovered audience definitions with metadata |
| `META_DEV_FILE` | `current/developer/META-DEV-{date}-{seq}.md` | Developer meta content |
| `META_ARCH_FILE` | `current/architect/META-ARCH-{date}-{seq}.md` | Architect meta content |
| `META_EXEC_FILE` | `current/executive/META-EXEC-{date}-{seq}.md` | Executive meta content |
| `META_INDEX` | `runs/{job_id}/meta_index.json` | JSON index of all generated meta files |
| `REVIEW_FILE_SUGGESTED` | `META-REV-{date}-{seq}_{slug}.md` | Quality review of all generated meta files |
| `META_MANIFEST` | `current/meta_manifest.json` | Published manifest (publish target) |

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

[Additional prompt guidance in the body]
```

**Frontmatter fields:**
- `audience_id` -- unique identifier, becomes the output subdirectory name
- `label` -- human-readable display name
- `tone` -- writing style guidance for the LLM
- `focus_areas` -- what to emphasize from the codebase docs
- `exclude` -- what to omit
- `section_structure` -- expected output sections

**Initial audience set (3 files):**

1. `developer.md` -- Implementation-focused: module APIs, dependencies,
   setup instructions, code patterns, extension points, testing guidance.

2. `architect.md` -- Design-focused: design decisions and rationale,
   pattern analysis, component relationships, dependency graphs,
   technical debt assessment, architectural constraints.

3. `executive.md` -- Business-focused: project overview, key metrics
   (module count, test coverage, workflow count), risk summary,
   progress status, cost/effort indicators.

## Meta Content File Format

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
- Prioritize factual accuracy -- no information invented beyond what
  codebase docs provide.

## Quality Requirements

- **Completeness** -- All codebase sections represented in each audience output
  (filtered by audience focus_areas/exclude).
- **Audience fidelity** -- Tone, focus, and section structure match the
  audience definition frontmatter.
- **Self-contained** -- Each meta file readable without reference to source docs.
- **Source attribution** -- Claims trace to specific codebase doc files.
- **No hallucination** -- No information invented beyond codebase docs.
- **YAML frontmatter** -- All required fields present with correct values.

## Builder Instructions

**Step architecture:** The builder shall propose the step sequence based on
the domain requirements above. Suggested phase decomposition (builder may adjust):

1. **Scan phase** -- Discover audience definitions, catalog codebase docs
2. **Generate phase** -- Produce meta content per audience (may be one step
   per audience or a single step iterating over all audiences)
3. **Review phase** -- Quality review against constraints above
4. **Refine phase** -- Fix issues (conditional)
5. **Publish phase** -- Backup, history, copy to current/ with manifest

**Action reuse:** Check if existing actions can be reused. A `scan_audiences`
action for audience discovery is likely needed. Publish actions (backup,
history, copy to current) may reuse patterns from `sdlc_00_codebase_v1`.

**Gatekeepers:** The builder should determine where QC gates add value. At
minimum, a quality gate after generation (before review) is recommended.

**install_to_global():** The `audiences/` directory must be deployed to the
global runner home. The workflow's `context_extensions.py` must implement
real `install_to_global()` logic to copy the audience files.

## Notes

- Source codebase docs: `docs/repo/codebase/current/`
- Codebase manifest: `docs/repo/codebase/current/codebase_manifest.json`
- Similar workflow: `sdlc_00_codebase_v1` (same staging/publish pattern)
- Existing HTML framework: `agent_runner_v2/site_styles.py` (for downstream renderer)
