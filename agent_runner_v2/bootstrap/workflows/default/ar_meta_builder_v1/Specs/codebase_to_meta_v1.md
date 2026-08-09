---
doc_type: "composition_system_spec"
lifecycle_status: "draft"
domain: "codebase_to_meta"
domain_label: "Codebase to Meta Content"
job_prefix: "META"
workflow_pattern: "mixed"
self_bootstrap_capable: false
---

# Composition System Specification: Codebase to Meta Content v1

> **Domain:** Codebase documentation transformation
> **Spec type:** Bootstrap spec (input to ar_meta_builder_v1)
> **Standard:** AR_META_BUILDER_STANDARD
> **Downstream consumers:** meta_content_renderer_v1 (renders meta content
> to HTML, PDF, DOCX, PPTX)

---

## 1. Domain Overview

**Domain name:** `codebase_to_meta`
**Label:** Codebase to Meta Content v1
**Job prefix:** `META`
**Workflow pattern:** `mixed` (action steps for scanning/publishing,
prompt-driven steps for content generation and review)
**Description:** Transforms codebase documentation into audience-specific
Rich Markdown meta content files via plugin-extensible audience definitions.

### 1.1 Purpose

The codebase documentation under `docs/repo/codebase/current/` contains
approximately 155 files of technical documentation (module docs, component
docs, standards, inventory, change records). This information is
comprehensive but written for a single audience -- developers who work on
the codebase.

Different stakeholders need different views of the same codebase:

- **Developers** need implementation details, APIs, dependencies, setup
  guides, code patterns, extension points, testing guidance.
- **Architects** need design decisions and rationale, pattern analysis,
  component relationships, dependency graphs, technical debt assessment.
- **Executives** need high-level project overview, key metrics (module
  count, test coverage, workflow count), risk summary, progress status.

This composition system scans the codebase docs and produces one Rich
Markdown meta content file per audience. The set of audiences is
**plugin-extensible** -- each audience is defined by a Markdown file with
YAML frontmatter in the workflow's `audiences/` directory. Adding a new
audience requires only dropping a new `.md` file into `audiences/`. No
workflow logic changes.

**Trigger:** User runs the workflow. No user-provided input artifacts --
all paths are resolved from the repo structure at runtime.

**Outcome:** A set of audience-specific meta content Markdown files
published to `docs/repo/meta_content/current/` with full version history.
Each file is self-contained and readable without reference to the source
codebase docs.

### 1.2 Domain Context

The meta content files serve as the bridge between raw codebase
documentation and downstream composition systems that need audience-tailored
views. The meta_content_renderer_v1 composition system consumes these files
to produce formal deliverable formats (HTML, PDF, DOCX, PPTX).

```
codebase docs --> [codebase_to_meta_v1] --> meta content (per audience)
                                                  |
                                  [meta_content_renderer_v1]
                                                  |
                                    HTML / PDF / DOCX / PPTX
```

### 1.3 Context Variables

All paths are hardcoded in `context_extensions.py`. No user-provided
input artifacts.

| Context Variable | Hardcoded Path | Description |
|---|---|---|
| `CODEBASE_DOC_ROOT` | `{repo_root}/docs/repo/codebase/current/` | Source codebase documentation |
| `META_CONTENT_ROOT` | `{repo_root}/docs/repo/meta_content/` | Output staging/publish root |
| `AUDIENCE_DIR` | `{workflow_package}/audiences/` | Audience definition plugins |

---

## 2. Component Schema (Layer 1)

This composition system uses 5 of the 8 universal component types to
define the codebase-to-meta workflow.

### 2.1 step_definition Components

The workflow has 5 steps across 5 phases.

| # | step_name | step_type | Phase | Purpose |
|---|---|---|---|---|
| 1 | `scan_audiences` | action | Scan | Discover audience definitions from `audiences/` directory |
| 2 | `generate_meta_content` | prompt | Generate | Produce one meta content file per discovered audience |
| 3 | `review_meta_content` | prompt | Review | Quality review of all generated meta files |
| 4 | `refine_meta_content` | prompt | Refine | Fix issues found in review (conditional) |
| 5 | `publish_meta_content` | action | Publish | Backup, history, copy to `current/` with manifest |

#### Step 1: scan_audiences (action)

Scans the `audiences/` directory for `.md` files. Parses YAML frontmatter
from each file to extract audience definitions. Produces an inventory
document listing all discovered audiences with their metadata.

**Error handling:**
- If `audiences/` directory is missing or contains no `.md` files, REJECT
  with reject_code `NO_AUDIENCES_FOUND`.
- If a file has invalid YAML frontmatter, log a warning and skip it.

**Returns:** APPROVED when at least one valid audience definition is found.

#### Step 2: generate_meta_content (prompt)

Reads the codebase documentation inventory from
`CODEBASE_DOC_ROOT/codebase_manifest.json`, then selectively reads docs
guided by each audience's `focus_areas` and `exclude` fields. Produces
one Rich Markdown meta content file per audience, following the audience
definition's `section_structure`, `tone`, and additional body guidance.

Each output file must be:
- Self-contained (readable without source docs)
- Audience-faithful (tone, focus, section structure match definition)
- Source-attributed (claims trace to specific codebase doc files)
- No hallucination (no information beyond what codebase docs provide)

#### Step 3: review_meta_content (prompt)

Reviews all generated meta content files against quality requirements.
Checks completeness, audience fidelity, source attribution, YAML
frontmatter correctness, and self-contained readability. Produces a
review document with per-audience assessments and an overall
APPROVED/REJECTED decision.

#### Step 4: refine_meta_content (prompt)

Receives the review document with specific issues to fix. Regenerates
the affected audience meta content files addressing all identified
issues. Preserves content that was not flagged.

#### Step 5: publish_meta_content (action)

Executes the publish lifecycle:

1. **Backup** -- Copy `current/` to `backups/BACKUP-{timestamp}/`
2. **History** -- Move old `current/` to `history/{job_id}/`
3. **Publish** -- Copy generated files to `current/` organized by
   audience subdirectory
4. **Manifest** -- Write `current/meta_manifest.json` listing all
   published files with metadata

**Returns:** APPROVED when all files are published and manifest is written.

### 2.2 role_policy Components

| step_name | policy_name | Rationale |
|---|---|---|
| `scan_audiences` | (action -- no role) | Deterministic directory scan |
| `generate_meta_content` | `architect_standard` | Content generation from structured source |
| `review_meta_content` | `reviewer_standard` | Quality review against constraints |
| `refine_meta_content` | `architect_standard` | Content regeneration addressing review |
| `publish_meta_content` | (action -- no role) | Deterministic file operations |

### 2.3 routing_pattern Components

| step_name | onsuccess | on_reject_refine |
|---|---|---|
| `scan_audiences` | `generate_meta_content` | -- |
| `generate_meta_content` | `review_meta_content` | -- |
| `review_meta_content` | `publish_meta_content` | refine_meta_content (max 2 iterations) |
| `refine_meta_content` | `review_meta_content` | -- |
| `publish_meta_content` | `step_completion` | -- |

**Exhaustion codes:**
- review_meta_content: `META_CONTENT_REVIEW_EXHAUSTED`,
  classification `HUMAN_RETRY_REQUIRED`

### 2.4 prompt_pattern Components

Applies to prompt-type steps (generate, review, refine).

| Pattern | Applied To | Content |
|---|---|---|
| `reference_inputs` | All 3 prompt steps | List input artifacts with `{PLACEHOLDER}` paths |
| `generation_tasks` | generate, refine | Specific content generation instructions per audience |
| `self_critic` | All 3 prompt steps | Challenge reasoning, verify audience alignment |
| `self_validation` | All 3 prompt steps | Check completeness, attribution, no hallucination |
| `forbidden_content` | generate, refine | No hallucination, no information beyond source docs |
| `output_instructions` | All 3 prompt steps | File path, YAML frontmatter format, ASCII-only |

### 2.5 artifact_contract Components

| Artifact Key | Filename Pattern | Produced By | Required |
|---|---|---|---|
| `AUDIENCE_INVENTORY_FILE` | `AUDIENCE_INV-{date}-{seq}_{slug}.md` | scan_audiences | Yes |
| `META_CONTENT_FILE` | `{audience_id}/META-{AUD}-{date}-{seq}.md` | generate_meta_content | Yes |
| `META_INDEX_FILE` | `meta_index.json` | generate_meta_content | Yes |
| `REVIEW_FILE_SUGGESTED` | `META-REV-{date}-{seq}_{slug}.md` | review_meta_content | Yes |
| `META_MANIFEST_FILE` | `meta_manifest.json` | publish_meta_content | Yes |

**Note:** `META_CONTENT_FILE` uses the `audience_id` from each audience
definition as the output subdirectory name and the `AUD` code in the
filename is derived from the audience_id (e.g., DEV, ARCH, EXEC). The
exact mapping is determined at runtime by the scan_audiences action.

### 2.6 Audience Definition Plugin Format

Each audience is defined by a Markdown file in the `audiences/` directory
with YAML frontmatter:

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

| Field | Type | Required | Description |
|---|---|---|---|
| `audience_id` | string | Yes | Unique identifier, becomes output subdirectory name |
| `label` | string | Yes | Human-readable display name |
| `tone` | string | Yes | Writing style guidance for the LLM |
| `focus_areas` | array | Yes | What to emphasize from codebase docs |
| `exclude` | array | No | What to omit from output |
| `section_structure` | array | Yes | Expected output section order |

**Initial audience set (3 files):**

1. `developer.md` -- Implementation-focused: module APIs, dependencies,
   setup instructions, code patterns, extension points, testing guidance.

2. `architect.md` -- Design-focused: design decisions and rationale,
   pattern analysis, component relationships, dependency graphs,
   technical debt assessment, architectural constraints.

3. `executive.md` -- Business-focused: project overview, key metrics
   (module count, test coverage, workflow count), risk summary,
   progress status, cost/effort indicators.

### 2.7 Validation Rules

| Rule | Severity | Description |
|---|---|---|
| Audiences directory exists | CRITICAL | `audiences/` must exist with at least one `.md` file |
| Frontmatter validity | CRITICAL | Each audience `.md` must have valid YAML frontmatter with all required fields |
| Unique audience_id | CRITICAL | No two audience definitions may share the same audience_id |
| Codebase manifest exists | CRITICAL | `CODEBASE_DOC_ROOT/codebase_manifest.json` must exist |
| Self-contained output | HIGH | Each meta content file must be readable without source docs |
| Source attribution | HIGH | Every factual claim must trace to a specific codebase doc file |
| No hallucination | CRITICAL | No information invented beyond what codebase docs provide |
| Audience fidelity | HIGH | Tone, focus, and section structure must match audience definition |
| YAML frontmatter on output | HIGH | Each meta file must have required frontmatter fields |

---

## 3. Composition Format (Layer 2)

### 3.1 Composition Structure

The "composition" in this domain is the combination of codebase
documentation with audience definitions. The workflow reads all codebase
docs and filters/transforms them per audience.

| Field | Type | Required | Description |
|---|---|---|---|
| `CODEBASE_DOC_ROOT` | directory | Yes | Source codebase documentation (~155 files) |
| `audiences/` | directory | Yes | Audience definition plugin files |

### 3.2 Binding Rules

| Binding | Source | Cardinality | Required? | Description |
|---|---|---|---|---|
| `codebase_docs` | codebase documentation files | Ordered set | Yes | All `.md` files under `CODEBASE_DOC_ROOT` |
| `codebase_manifest` | `codebase_manifest.json` | Singleton | Yes | Full doc inventory with metadata |
| `audience_defs` | audience plugin `.md` files | Unordered set | Yes | All audience definitions from `audiences/` |

### 3.3 Override Mechanism

Per-audience customization is achieved through the audience definition
frontmatter fields:

- `tone` overrides the default writing style
- `focus_areas` overrides which codebase sections to emphasize
- `exclude` overrides which content to omit
- `section_structure` overrides the output section order

These are not component-level overrides in the traditional sense -- they
are audience-specific configuration that drives the LLM's content
generation behavior.

### 3.4 Placeholder Resolution

| Priority | Data Source | Fields Provided |
|---|---|---|
| 1 (highest) | Runtime context | `CODEBASE_DOC_ROOT`, `META_CONTENT_ROOT`, `AUDIENCE_DIR` |
| 2 | Audience definition | `audience_id`, `label`, `tone`, `focus_areas`, `section_structure` |
| 3 | Codebase manifest | `doc_inventory`, `section_list`, `total_doc_count` |
| 4 (lowest) | Job runtime | `job_id`, `seq`, `workspace_root` |

### 3.5 Example Composition

```
Input:
  CODEBASE_DOC_ROOT/
  |-- codebase_manifest.json
  |-- standards/
  |   |-- CODING_STANDARD.md
  |   +-- DOCUMENTATION_STANDARD.md
  |-- modules/
  |   |-- agent_runner_v2.md
  |   |-- step_runner.md
  |   +-- ...
  +-- inventory/
      +-- CODEBASE_INVENTORY.md

  audiences/
  |-- developer.md
  |-- architect.md
  +-- executive.md

Output:
  docs/repo/meta_content/current/
  |-- developer/
  |   +-- META-DEV-20260808-001.md
  |-- architect/
  |   +-- META-ARCH-20260808-001.md
  |-- executive/
  |   +-- META-EXEC-20260808-001.md
  +-- meta_manifest.json
```

---

## 4. Output Format (Layer 3)

### 4.1 Output Structure

Each meta content file is Rich Markdown with YAML frontmatter:

```yaml
---
title: "Agent Runner V2 -- Developer Guide"
audience: developer
audience_label: "Developer"
generated_date: "2026-08-08"
source_version: "{codebase_version}"
section_count: 5
---
```

Followed by audience-tailored content organized per the audience
definition's `section_structure`.

### 4.2 Resolution Rules

| Rule | Description |
|---|---|
| RR-META-001 | Each audience definition produces exactly one meta content file |
| RR-META-002 | Output filename uses audience_id prefix: `META-{AUD}-{date}-{seq}.md` |
| RR-META-003 | Output subdirectory matches audience_id |
| RR-META-004 | Section order follows audience definition's `section_structure` |
| RR-META-005 | Tone follows audience definition's `tone` field |
| RR-META-006 | Excluded topics from `exclude` field must not appear in output |
| RR-META-007 | Source attribution via inline references to codebase doc filenames |

### 4.3 Quality Requirements

| Rule | Requirement | Severity |
|---|---|---|
| QR-META-001 | **Completeness** -- All codebase sections represented in each audience output (filtered by focus_areas/exclude) | CRITICAL |
| QR-META-002 | **Audience fidelity** -- Tone, focus, and section structure match audience definition frontmatter | CRITICAL |
| QR-META-003 | **Self-contained** -- Each meta file readable without reference to source docs | HIGH |
| QR-META-004 | **Source attribution** -- Claims trace to specific codebase doc files | HIGH |
| QR-META-005 | **No hallucination** -- No information invented beyond codebase docs | CRITICAL |
| QR-META-006 | **YAML frontmatter** -- All required fields present with correct values | HIGH |
| QR-META-007 | **ASCII-only** -- No em-dashes, no curly quotes in generated content | HIGH |

### 4.4 Meta Content File Format (Example)

```markdown
---
title: "Agent Runner V2 -- Developer Guide"
audience: developer
audience_label: "Developer"
generated_date: "2026-08-08"
source_version: "SDLC00CB-bgmxg5vi"
section_count: 5
---

# Agent Runner V2 -- Developer Guide

## Overview

The agent-runner-v2 is a Python 3.12+ daemon and CLI execution engine...

## Module Catalog

### agent_runner_v2.run_agent
Entry point for the `ukbe-run-agent` CLI...

### agent_runner_v2.step_runner
Core step execution engine...

## API Reference

[Detailed function signatures, parameters, return types]

## Dependency Map

[Module dependency relationships]

## Developer Guide

[Setup, contribution, testing instructions]
```

---

## 5. Operational Requirements

### 5.1 Workflow Phases

| Phase | Purpose | Step(s) |
|---|---|---|
| **Scan** | Discover audience definitions from `audiences/` directory | scan_audiences |
| **Generate** | Produce one meta content file per discovered audience | generate_meta_content |
| **Review** | Quality review against constraints | review_meta_content |
| **Refine** | Fix issues from review (conditional, max 2 iterations) | refine_meta_content |
| **Publish** | Backup, history, copy to `current/` with manifest | publish_meta_content |

### 5.2 Input Artifacts

**No user-provided inputs.** All paths are resolved from the repo
structure at runtime via context variables.

### 5.3 Output Artifacts

| Artifact Key | Description |
|---|---|
| `AUDIENCE_INVENTORY_FILE` | Discovered audience definitions with metadata |
| `META_CONTENT_FILE` | One Rich Markdown meta content file per audience |
| `META_INDEX_FILE` | JSON index of all generated meta files |
| `REVIEW_FILE_SUGGESTED` | Quality review of all generated meta files |
| `META_MANIFEST_FILE` | Published manifest in `current/` |

### 5.4 Action Steps

Two custom action steps are needed:

#### scan_audiences

Recursively scan `AUDIENCE_DIR` for `.md` files. Parse YAML frontmatter
from each file. Build an audience inventory with audience_id, label,
tone, focus_areas, exclude, section_structure, and file path.

Write the inventory to `AUDIENCE_INVENTORY_FILE`.

**Error handling:**
- If `AUDIENCE_DIR` does not exist or contains no `.md` files, return
  REJECTED with reject_code `NO_AUDIENCES_FOUND`.
- If a file has invalid YAML frontmatter, log a warning and skip it.
- If two files define the same `audience_id`, return REJECTED with
  reject_code `DUPLICATE_AUDIENCE_ID`.

**Returns:** APPROVED when at least one valid audience is found.

#### publish_meta_content

Execute the publish lifecycle:

1. If `current/` exists and contains files:
   a. Copy `current/` to `backups/BACKUP-{timestamp}/`
   b. Move `current/` to `history/{job_id}/`
2. For each audience meta content file:
   a. Copy to `current/{audience_id}/`
3. Write `current/meta_manifest.json` listing all published files with
   audience_id, filename, generated_date, source_version.

**Returns:** APPROVED when all files are published and manifest written.

### 5.5 Domain-Specific Requirements

- The `audiences/` directory is part of the workflow package and must be
  deployed to the global runner home at install time via
  `install_to_global()`.
- The publish lifecycle follows the same staging pattern as
  `sdlc_00_codebase_v1` (stage -> review -> refine -> backup -> history
  -> publish).
- Output paths follow the standard staging pattern (`current/`, `runs/`,
  `history/`, `backups/`).
- The generate step reads `codebase_manifest.json` to understand the full
  doc inventory, then selectively reads docs from each section as guided
  by each audience's `focus_areas`.
- Each meta content file must be self-contained (readable without
  reference to the source codebase docs).

### 5.6 Package File Inventory

The generated workflow package must include:

| File/Directory | Description |
|---|---|
| `workflow.toml` | Workflow manifest with 5 steps |
| `context_extensions.py` | Artifact key registration with hardcoded paths |
| `actions.py` | scan_audiences and publish_meta_content implementations |
| `prompts/` | Prompt templates for generate, review, refine steps |
| `audiences/` | Audience definition plugin files (3 initial) |
| `audiences/developer.md` | Developer audience definition |
| `audiences/architect.md` | Architect audience definition |
| `audiences/executive.md` | Executive audience definition |
| `Specs/` | Directory for workflow specifications |
| `Specs/codebase_to_meta_v1.md` | Runtime spec -- defines what meta content this workflow produces |
| `README.md` | Human documentation |

### 5.7 Default Runtime Spec

The builder must generate a spec into `Specs/codebase_to_meta_v1.md`
that the generated workflow reads at runtime to know WHAT to produce.
This is a different document at a different level:

| Spec | Level | Purpose |
|---|---|---|
| Bootstrap spec (this document) | Meta level | Input to AMB v1 -- tells the builder how to build the workflow |
| Runtime spec (`Specs/codebase_to_meta_v1.md`) | Runtime level | Read by the generated workflow -- tells it what meta content to produce |

The runtime spec defines the meta content production contract:

- **Output format** -- YAML frontmatter schema, section structure rules,
  Markdown formatting conventions
- **Per-audience section templates** -- what sections each audience type
  expects (developer: module_catalog, api_reference, dependency_map;
  architect: design_decisions, pattern_analysis, tech_debt; executive:
  metrics, risk_summary, progress)
- **Content extraction rules** -- how to map codebase doc sections to
  meta content sections per audience
- **Quality criteria** -- completeness, audience fidelity, source
  attribution, no hallucination rules that the review step checks
- **Audience plugin contract** -- required frontmatter fields for
  audience definitions (audience_id, label, tone, focus_areas, exclude,
  section_structure)

The `generate_meta_content` prompt step must reference this spec as an
input: `{Specs/codebase_to_meta_v1.md}`. The `review_meta_content` step
also reads it to validate output against the defined criteria.

This spec also serves as the reference contract for downstream
composition systems (e.g., `meta_content_renderer_v1`) that need to
understand the meta content format and audience structure.

---

## 6. References

- **Downstream consumer:** `meta_content_renderer_v1` (renders meta
  content to HTML, PDF, DOCX, PPTX)
- **Similar workflow:** `sdlc_00_codebase_v1` (same staging/publish
  pattern)
- **Source data:** `docs/repo/codebase/current/` (~155 codebase doc files)
- **Codebase manifest:** `docs/repo/codebase/current/codebase_manifest.json`
- **Existing HTML framework:** `agent_runner_v2/site_styles.py` (for
  downstream renderer)

---

**End of Specification**
