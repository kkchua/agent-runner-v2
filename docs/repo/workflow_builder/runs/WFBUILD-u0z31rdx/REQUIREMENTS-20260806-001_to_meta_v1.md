---
doc_type: "workflow_design"
lifecycle_status: "draft"
effective_version: "WFBUILD-u0z31rdx"
workflow_name: "codebase_to_meta_v1"
workflow_label: "Codebase to Meta Content v1"
job_prefix: "META"
spec_source: "codebase_to_meta_v1.md"
---

# Requirements: Codebase to Meta Content v1

## Overview

The codebase_to_meta_v1 workflow transforms the existing codebase documentation
(~155 files under docs/repo/codebase/current/) into audience-specific Rich
Markdown meta content files. Different stakeholders need different views of
the same codebase: developers need implementation details and APIs, architects
need design decisions and pattern analysis, and executives need high-level
status and risk summaries. The workflow dynamically discovers audience
definitions from a plugin-extensible audiences/ directory within the workflow
package, generates tailored content per audience using LLM-driven synthesis,
and publishes the results through a staged review-and-publish lifecycle
following the same pattern as sdlc_00_codebase_v1.

## Workflow Type

**Type: mixed**

**Justification:** The workflow combines deterministic action steps with
LLM-driven prompt steps. The action steps handle structural operations:
scanning the audiences/ directory to discover audience definitions, validating
generated meta content file structure, creating filesystem backups, and
publishing staged content to the current/ directory. The prompt steps handle
content synthesis: generating audience-tailored meta content from codebase
documentation, reviewing generated quality, and refining content based on
review feedback. Neither approach alone suffices -- pure prompt-driven cannot
handle filesystem operations or dynamic audience discovery; pure action-only
cannot perform the creative synthesis required to transform technical docs
into audience-specific narratives.

**Inferred pattern:** Gatekeeper QC Pipeline (Pattern 4 from
WORKFLOW_CREATION_GUIDE) adapted for audience-driven content generation.
The workflow follows the stage-review-refine-publish lifecycle with action
steps for structural operations and prompt steps for content generation
and quality control.

## Proposed Steps

### Step 1: scan_audiences

- **Name:** scan_audiences
- **Type:** action
- **Purpose:** Dynamically discover audience definition files from the
  workflow package's audiences/ directory. Parse each .md file's YAML
  frontmatter to extract audience_id, label, tone, focus_areas, exclude,
  and section_structure. Produce a JSON index of all discovered audiences
  for downstream steps to consume.
- **Inputs:** The audiences/ directory within the workflow package (resolved
  via context). No artifact inputs required -- reads directly from filesystem.
- **Outputs:** AUDIENCE_INDEX (JSON file mapping audience_id to parsed
  frontmatter metadata and body text path)
- **Routing:** onsuccess -> generate_meta

### Step 2: generate_meta

- **Name:** generate_meta
- **Type:** prompt
- **Purpose:** Read the codebase documentation (via CODEBASE_MANIFEST for
  inventory, then selectively reading docs from each section) and the
  audience index. For each audience, generate a Rich Markdown meta content
  file tailored to that audience's tone, focus_areas, exclude list, and
  section_structure. The prompt template must reference the AUDIENCE_INDEX
  so the LLM can iterate over discovered audiences dynamically.
- **Inputs:** AUDIENCE_INDEX, CODEBASE_MANIFEST, codebase docs directory
- **Outputs:** META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE (one Rich
  Markdown file per initial audience), META_INDEX (JSON index of all
  generated meta files with audience metadata)
- **Routing:** onsuccess -> review_meta

### Step 3: review_meta

- **Name:** review_meta
- **Type:** prompt
- **Purpose:** Review all generated meta content files for completeness,
  accuracy, audience-appropriateness, and structural compliance. The
  reviewer checks that each file follows its audience definition's
  section_structure, maintains the specified tone, covers focus_areas,
  and excludes the specified content. Produces a consolidated review
  document with feedback per audience.
- **Inputs:** META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE, META_INDEX,
  AUDIENCE_INDEX
- **Outputs:** REVIEW_FILE_SUGGESTED
- **Routing:** onsuccess -> validate_meta; on_reject_refine -> refine_meta;
  requires_human_approval_after = true
- **Coder role:** reviewer_standard

### Step 4: refine_meta

- **Name:** refine_meta
- **Type:** prompt
- **Purpose:** Refine generated meta content files based on review feedback.
  Reads the review document and applies corrections to the affected meta
  content files in place. Only modifies files that received feedback.
- **Inputs:** META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE, META_INDEX,
  AUDIENCE_INDEX, REVIEW_FILE_SUGGESTED
- **Outputs:** META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE, META_INDEX
  (updated in place)
- **Routing:** onsuccess -> review_meta
- **Coder role:** architect_standard
- **Edit mode:** in_place (target_artifact = all meta files)

### Step 5: validate_meta

- **Name:** validate_meta
- **Type:** action
- **Purpose:** Structurally validate all generated meta content files.
  Check that each file has valid YAML frontmatter with required fields
  (title, audience, audience_label, generated_date, source_version,
  section_count). Verify that audience IDs match the AUDIENCE_INDEX.
  Verify that section_structure from each audience definition is reflected
  in the output. Check file encoding is UTF-8 and ASCII-only content
  where required.
- **Inputs:** META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE, META_INDEX,
  AUDIENCE_INDEX
- **Outputs:** VALIDATION_FILE (validation report)
- **Routing:** onsuccess -> create_meta_backup

### Step 6: create_meta_backup

- **Name:** create_meta_backup
- **Type:** action
- **Purpose:** Create a backup of the current docs/repo/meta_content/current/
  directory before publishing new content. Copies to
  docs/repo/meta_content/backups/BACKUP-{timestamp}/. Handles first-run
  gracefully when current/ does not yet exist.
- **Inputs:** None (filesystem operation only)
- **Outputs:** META_BACKUP (path to backup directory)
- **Routing:** onsuccess -> publish_meta

### Step 7: publish_meta

- **Name:** publish_meta
- **Type:** action
- **Purpose:** Publish staged meta content from runs/{job_id}/ to
  docs/repo/meta_content/current/. Archives the previous current/ contents
  to history/{job_id}/. Copies each audience subdirectory from the staging
  area to current/. Writes meta_manifest.json to both current/ and
  history/{job_id}/ tracking all published files, audience metadata,
  source version, and supersedes chain.
- **Inputs:** META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE, META_INDEX,
  AUDIENCE_INDEX
- **Outputs:** META_MANIFEST (published manifest in current/),
  META_MANIFEST_HISTORY (manifest copy in history/)
- **Routing:** onsuccess -> step_completion

### Step 8: step_completion

- **Name:** step_completion
- **Type:** action
- **Purpose:** Standard terminal step. Marks the workflow as completed.
- **Inputs:** None
- **Outputs:** None
- **Routing:** terminal

## Custom Actions

| action_name | purpose | inputs | outputs | logic_description |
|---|---|---|---|---|
| scan_audiences | Discover and index audience definition files from the workflow package audiences/ directory | Workflow package audiences/ directory path (from context: AUDIENCES_ROOT) | AUDIENCE_INDEX (JSON file) | Scan audiences/ for .md files. For each file, parse YAML frontmatter (audience_id, label, tone, focus_areas, exclude, section_structure) and read the body text. Write a JSON index mapping each audience_id to its parsed metadata and the absolute path to the definition file body. Return APPROVED with the index path. |
| validate_meta | Structurally validate generated meta content files | META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE, META_INDEX, AUDIENCE_INDEX | VALIDATION_FILE (validation report) | For each meta content file: (1) verify valid YAML frontmatter with required fields (title, audience, audience_label, generated_date, source_version, section_count), (2) verify audience field matches an entry in AUDIENCE_INDEX, (3) verify section headings match the audience definition's section_structure, (4) verify file is valid UTF-8 Markdown. Write a validation report listing each file and pass/fail status per check. Return APPROVED if all files pass, REJECTED if any file fails structural checks. |
| create_meta_backup | Backup current/ meta content before publishing | None (filesystem operation) | META_BACKUP (backup directory path) | Check if docs/repo/meta_content/current/ exists. If not (first run), return APPROVED with no backup. If yes, generate timestamped backup directory name (BACKUP-{YYYYMMDD-HHMMSS}) under docs/repo/meta_content/backups/. Copy current/ tree to backup directory using shutil.copytree. Return APPROVED with backup path. |
| publish_meta | Publish staged meta content to current/ directory | META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE, META_INDEX, AUDIENCE_INDEX | META_MANIFEST, META_MANIFEST_HISTORY | Two-phase publish: (1) Archive existing docs/repo/meta_content/current/ to docs/repo/meta_content/history/{job_id}/ -- copy each audience subdirectory and any existing manifest. (2) Copy staged audience subdirectories from runs/{job_id}/ to current/. Write meta_manifest.json to both current/ and history/ containing: workflow_id, change_or_run_id (job_id), source_codebase_version, audiences map (audience_id to label, file path, generated_date), published_timestamp, supersedes (previous job_id from old manifest or null), active_set flag. |

## Input Artifacts

| artifact_key | description | required_or_optional |
|---|---|---|
| AUDIENCE_INDEX | JSON index of discovered audience definitions (produced by scan_audiences action within this workflow) | required (produced internally) |
| CODEBASE_MANIFEST | The codebase_manifest.json file from docs/repo/codebase/current/ listing all 140+ tracked documentation artifacts | required |

**Note:** The codebase documentation files themselves (under
docs/repo/codebase/current/) are not tracked as named artifacts but are
accessed via the CODEBASE_CURRENT_ROOT context variable. The generate step
reads the CODEBASE_MANIFEST for inventory, then selectively reads individual
documentation files as guided by each audience's focus_areas.

**Note:** No user-provided inputs. All paths are resolved from repo structure
by the workflow's context_extensions.py.

## Output Artifacts

| artifact_key | description | required_or_optional |
|---|---|---|
| AUDIENCE_INDEX | JSON index of discovered audience definitions with parsed frontmatter metadata | required |
| META_DEV_FILE | Developer meta content file -- Rich Markdown with YAML frontmatter tailored for developers | required |
| META_ARCH_FILE | Architect meta content file -- Rich Markdown with YAML frontmatter tailored for architects | required |
| META_EXEC_FILE | Executive meta content file -- Rich Markdown with YAML frontmatter tailored for executives | required |
| META_INDEX | JSON index of all generated meta files with audience metadata and file paths | required |
| REVIEW_FILE_SUGGESTED | Consolidated review document covering all generated meta files with per-audience feedback | required |
| VALIDATION_FILE | Structural validation report for generated meta content files | required |
| META_BACKUP | Path to backup directory created before publish | optional (skipped on first run) |
| META_MANIFEST | Published manifest in current/ tracking all published meta files | required |
| META_MANIFEST_HISTORY | Manifest copy in history/{job_id}/ for archival | required |

## Constraints

### Governance Constraints

- Layer 1 (governance) and Layer 2 (platform constitution) documents are
  read-only authority. This workflow must not redefine or contradict them.
- The workflow operates at Layer 3 (application workflow layer).
- Governance runtime root must be accessible via GOVERNANCE_RUNTIME_ROOT
  context variable for prompt steps.
- Platform runtime root must be accessible via PLATFORM_RUNTIME_ROOT
  context variable for prompt steps.

### Naming Constraints

- All artifact keys use UPPER_SNAKE_CASE with _FILE suffix for document
  artifacts (per repository convention).
- The workflow package directory name must be codebase_to_meta_v1
  (matching the spec slug).
- The workflow_name attribute in context_extensions.py must match the
  directory name exactly.
- Output files follow the naming pattern from the spec:
  META-DEV-{date}-{seq}.md, META-ARCH-{date}-{seq}.md,
  META-EXEC-{date}-{seq}.md.
- Sequence numbers use resolve_next_seq() for auto-incrementing.

### Structural Constraints

- Each meta content file must be self-contained (readable without reference
  to the source codebase docs).
- The workflow must dynamically discover audience definitions at startup
  by scanning the audiences/ directory for .md files.
- Each audience definition's YAML frontmatter drives the generation:
  tone, focus_areas, exclude, section_structure guide the LLM; the body
  provides additional prompt guidance.
- The audiences/ directory is part of the workflow package and must be
  deployed to the global runner home via install_to_global().
- Output paths follow the standard staging pattern: current/, runs/,
  history/, backups/.
- The workflow must include a review/refine loop with human approval gate
  (requires_human_approval_after on the review step).
- The refine step must use edit_mode = "in_place" with target_artifact.

### Dependency Constraints

- The codebase documentation under docs/repo/codebase/current/ must exist
  and contain the codebase_manifest.json before this workflow runs.
- The workflow depends on the sdlc_00_codebase_v1 workflow having run at
  least once to populate the codebase docs.
- The shared action create_backup from sdlc_shared_actions.py provides
  the backup pattern reference; a workflow-specific create_meta_backup
  action should follow the same approach but target meta_content paths.
- The shared action step_completion is used as the terminal step.

### Audience Extensibility Constraint

- The initial audience set is 3 files: developer.md, architect.md,
  executive.md.
- Adding a new audience requires: (1) dropping a new .md file into the
  audiences/ directory, (2) adding corresponding META_{ID}_FILE artifact
  key in context_extensions.py, (3) the generate prompt already handles
  all audiences via the AUDIENCE_INDEX.
- The scan_audiences action and generate_meta prompt are designed to
  handle any number of audiences without step definition changes.

## Context Variables

The following context variables must be provided by context_extensions.py
via build_context_extensions(). These are variable names and descriptions
only; resolved file paths are handled by the define_artifacts step.

| variable_name | description |
|---|---|
| AUDIENCES_ROOT | Root directory of the workflow package's audiences/ subdirectory containing audience definition .md files. Used by scan_audiences action for dynamic discovery. |
| CODEBASE_CURRENT_ROOT | Root directory of the codebase documentation tree (docs/repo/codebase/current/). Contains 00_standards/, 01_inventory/, 02_modules/, 03_components/, 04_changes/ subdirectories and codebase_manifest.json. Used by generate_meta step to read source documentation. |
| CODEBASE_MANIFEST | Absolute path to the codebase_manifest.json artifact inventory file within CODEBASE_CURRENT_ROOT. Lists all tracked documentation artifacts with metadata. |
| GOVERNANCE_RUNTIME_ROOT | Layer 1 governance runtime root (global path). Resolved via get_governance_runtime_root(). Provides read-only access to governance documents for prompt steps. |
| PLATFORM_RUNTIME_ROOT | Layer 2 platform constitution runtime root (global path). Resolved via get_platform_runtime_root(). Provides read-only access to platform documents for prompt steps. |
| META_CONTENT_ROOT | Base output directory for meta content (docs/repo/meta_content/). Contains current/, runs/{job_id}/, history/{job_id}/, and backups/ subdirectories. Used by create_meta_backup and publish_meta actions. |

## Data Schemas

This section summarizes the key data structures defined by the spec. Full
schemas are in the source specification; this section provides field counts
and purposes for downstream implementation reference.

### Audience Definition YAML Frontmatter

Each audience .md file in audiences/ has YAML frontmatter with 6 fields:

| field | type | purpose |
|---|---|---|
| audience_id | string | Unique identifier; becomes the output subdirectory name |
| label | string | Human-readable display name |
| tone | string | Writing style guidance for the LLM |
| focus_areas | list[string] | Topics to emphasize from codebase docs |
| exclude | list[string] | Topics to omit from output |
| section_structure | list[string] | Expected output section headings |

The Markdown body of the file provides additional prompt guidance beyond
what the frontmatter fields capture.

### AUDIENCE_INDEX JSON

Produced by scan_audiences action. Maps each audience_id to an object
containing:

- Parsed frontmatter fields (6 fields as above)
- Absolute path to the audience definition .md file (for body text access)
- Count: variable (depends on number of .md files discovered)

### Meta Content File YAML Frontmatter

Each generated meta content file has YAML frontmatter with 6 fields:

| field | type | purpose |
|---|---|---|
| title | string | Document title (e.g., "Agent Runner V2 -- Developer Guide") |
| audience | string | Audience identifier (matches audience_id) |
| audience_label | string | Display name (matches label) |
| generated_date | string | ISO date of generation (e.g., "2026-08-06") |
| source_version | string | Codebase version identifier (e.g., "SDLC00CB-bgmxg5vi") |
| section_count | integer | Number of content sections in the file |

Followed by audience-tailored content organized per the audience
definition's section_structure.

### Publish Manifest JSON (meta_manifest.json)

Written to both current/ and history/{job_id}/ during publish. Contains
7 top-level fields:

| field | type | purpose |
|---|---|---|
| workflow_id | string | Workflow identifier ("codebase_to_meta_v1") |
| change_or_run_id | string | Job ID of the publishing run |
| source_codebase_version | string | Version of source codebase docs used |
| audiences | object | Map of audience_id to {label, file, generated_date} |
| published_timestamp | string | ISO 8601 timestamp of publication |
| supersedes | string/null | Previous job_id being replaced, or null |
| active_set | boolean | Whether this is the active published set |

## Implementation Notes

This section lists reusable scripts, existing patterns, and reference
implementations identified in the specification that should inform the
workflow implementation.

### Reusable Shared Actions

| action | source module | usage |
|---|---|---|
| step_completion | sdlc_shared_actions.py | Terminal step -- marks workflow as completed. Used directly; no custom implementation needed. |
| create_backup | sdlc_shared_actions.py | Reference pattern for backup logic. The workflow requires a custom create_meta_backup action targeting meta_content paths, but should follow the same approach (timestamped directory, shutil.copytree). |

### Reference Workflow Pattern

- **sdlc_00_codebase_v1** -- The spec explicitly states this workflow
  follows the same staging/publish pattern. Its context_extensions.py
  provides the reference implementation for:
  - Layer 1/Layer 2 governance root resolution via
    get_governance_runtime_root() and get_platform_runtime_root()
  - Standard staging directory structure (current/, runs/, history/)
  - Artifact path registration with resolve_repo_or_runtime_path()
  - Sequence auto-increment with resolve_next_seq()
  - Workspace root resolution with fallback chain

### Required Utility Imports

The following imports from agent_runner_v2.constants and
agent_runner_v2.runtime_context are needed based on the pattern:

- `resolve_next_seq` -- for auto-incrementing sequence numbers in output
  filenames (META-DEV-{date}-{seq}.md, etc.)
- `SDLC_DELIVERY_BASE` -- base constant for delivery artifact paths
- `get_governance_runtime_root` -- resolves Layer 1 governance path
- `get_platform_runtime_root` -- resolves Layer 2 platform path
- `get_workspace_root` -- resolves project workspace root
- `resolve_repo_or_runtime_path` -- resolves relative paths to absolute

### install_to_global() Requirement

The spec states: "The audiences/ directory is part of the workflow package
and must be deployed to the global runner home via install_to_global()."
The context_extensions.py must implement install_to_global() to copy the
audiences/ directory (containing developer.md, architect.md, executive.md)
to the global runner home so the scan_audiences action can discover them
when running from the bootstrap copy.

## Resolved Questions

All questions from the initial requirements pass have been resolved from
the source specification:

1. **Q: Are there any ambiguities in the spec that block implementation?**
   **Resolved:** No. The specification provides sufficient detail for all
   workflow elements: audience definition format, input/output artifact
   contracts, staging/publish lifecycle, and constraints. The spec's
   "Audience Definition Plugin System," "Outputs," "Publish Lifecycle,"
   and "Constraints" sections collectively cover all implementation needs.

2. **Q: Is the workflow type classification correct?**
   **Resolved:** Yes. The spec describes both action steps (scan, validate,
   backup, publish) and prompt steps (generate, review, refine). The mixed
   type classification is confirmed. The spec section "Constraints" states
   "The workflow should follow the standard prompt-driven pattern with
   review/refine loop and human approval gate," and the "Inputs" section
   confirms dynamic audience discovery via filesystem scanning.

3. **Q: Are all artifact keys traceable to the spec?**
   **Resolved:** Yes. META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE,
   META_INDEX, REVIEW_FILE_SUGGESTED, and META_MANIFEST are explicitly
   listed in the spec's "Output Artifacts" table. CODEBASE_MANIFEST is
   the spec's "codebase_manifest.json." AUDIENCE_INDEX, VALIDATION_FILE,
   META_BACKUP, and META_MANIFEST_HISTORY are structurally necessary
   artifacts derived from spec constraints (dynamic discovery, structural
   validation, backup before publish, manifest archival to history/).

4. **Q: Does the step sequence cover the full publish lifecycle?**
   **Resolved:** Yes. The spec's "Publish Lifecycle" section lists 6 phases:
   Stage, Review, Refine, Backup, History, Publish. The proposed steps
   cover all 6: generate_meta (Stage), review_meta (Review), refine_meta
   (Refine), create_meta_backup (Backup), publish_meta (History + Publish).
   scan_audiences and validate_meta are additional quality/infrastructure
   steps implied by the spec's constraints on dynamic discovery and
   structural compliance.

5. **Q: What context variables are needed?**
   **Resolved:** The Context Variables section now documents all 6 required
   variables: AUDIENCES_ROOT, CODEBASE_CURRENT_ROOT, CODEBASE_MANIFEST,
   GOVERNANCE_RUNTIME_ROOT, PLATFORM_RUNTIME_ROOT, META_CONTENT_ROOT.
   These are derived from the spec's Inputs section, Output Root structure,
   and Constraints section.

6. **Q: What data schemas must be implemented?**
   **Resolved:** The Data Schemas section now documents 4 key structures:
   Audience Definition YAML frontmatter (6 fields), AUDIENCE_INDEX JSON,
   Meta Content File YAML frontmatter (6 fields), and Publish Manifest JSON
   (7 top-level fields). All schemas are derived directly from the spec's
   "Audience Definition Plugin System," "Meta Content File Format," and
   "Publish Manifest" sections.

## Design Decisions Required

All questions resolved. No design decisions required.

The specification is deterministic on all implementation aspects. The
workflow type, step sequence, action specifications, input/output artifacts,
context variables, data schemas, and constraints are all derivable from the
spec and verified against the actual codebase structure and existing
workflow patterns (sdlc_00_codebase_v1).
