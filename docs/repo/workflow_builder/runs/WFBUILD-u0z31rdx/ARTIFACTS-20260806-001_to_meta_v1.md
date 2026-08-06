---
doc_type: "artifact_contract"
lifecycle_status: "draft"
effective_version: "{job_id}"
workflow_name: "codebase_to_meta_v1"
workflow_label: "Codebase to Meta Content v1"
---

# Artifact Contract: Codebase to Meta Content v1

## Artifact Key Summary

| Key | Path Pattern | Description | Required |
|---|---|---|---|
| CODEBASE_MANIFEST | docs/repo/codebase/current/codebase_manifest.json | Codebase manifest inventory file listing all tracked documentation artifacts. External input produced by sdlc_00_codebase_v1. | yes |
| AUDIENCE_INDEX | docs/repo/meta_content/runs/{job_id}/audience_index.json | JSON index of discovered audience definitions with parsed frontmatter metadata and body text paths. Produced by scan_audiences action. | yes |
| META_DEV_FILE | docs/repo/meta_content/runs/{job_id}/META-DEV-{date}-{seq}_{slug}.md | Developer meta content file. Rich Markdown with YAML frontmatter tailored for developer audience. | yes |
| META_ARCH_FILE | docs/repo/meta_content/runs/{job_id}/META-ARCH-{date}-{seq}_{slug}.md | Architect meta content file. Rich Markdown with YAML frontmatter tailored for architect audience. | yes |
| META_EXEC_FILE | docs/repo/meta_content/runs/{job_id}/META-EXEC-{date}-{seq}_{slug}.md | Executive meta content file. Rich Markdown with YAML frontmatter tailored for executive audience. | yes |
| META_INDEX | docs/repo/meta_content/runs/{job_id}/meta_index.json | JSON index of all generated meta files with audience metadata and file paths. | yes |
| REVIEW_FILE_SUGGESTED | docs/repo/meta_content/runs/{job_id}/{job_id}-review.md | Consolidated review document covering all generated meta files with per-audience feedback. | yes |
| VALIDATION_FILE | docs/repo/meta_content/runs/{job_id}/{job_id}-validation.md | Structural validation report for generated meta content files. | yes |
| META_BACKUP | docs/repo/meta_content/backups/BACKUP-{timestamp}/ | Path to backup directory created before publish. Skipped on first run when current/ does not exist. | no |
| META_MANIFEST | docs/repo/meta_content/current/meta_manifest.json | Published manifest in current/ tracking all published meta files, audience metadata, and supersedes chain. | yes |
| META_MANIFEST_HISTORY | docs/repo/meta_content/history/{job_id}/meta_manifest.json | Manifest copy archived in history/{job_id}/ for traceability. | yes |
| WORKFLOW_ACTIONS | workflows/codebase_to_meta_v1/actions.py | Python module with @action decorated functions for action-driven steps (scan_audiences, validate_meta, create_meta_backup, publish_meta). Conditional: required because the workflow has action-driven steps. | yes |

## Input Artifacts

### CODEBASE_MANIFEST

- Source: Produced externally by the sdlc_00_codebase_v1 workflow.
- Path: docs/repo/codebase/current/codebase_manifest.json
- Description: JSON manifest listing all tracked codebase documentation artifacts under docs/repo/codebase/current/. Contains inventory entries with section, type, path, and metadata for each of the 140+ tracked files.
- Consumed by: generate_meta step reads this to discover available source documentation. validate_meta step uses it to verify source_version references.

### AUDIENCE_INDEX

- Source: Produced internally by the scan_audiences action within this workflow.
- Path: docs/repo/meta_content/runs/{job_id}/audience_index.json
- Description: JSON index mapping each audience_id to its parsed YAML frontmatter fields (audience_id, label, tone, focus_areas, exclude, section_structure) and the absolute path to the audience definition .md file for body text access.
- Consumed by: generate_meta, review_meta, refine_meta, validate_meta, and publish_meta steps all consume this index.

## Output Artifacts

### AUDIENCE_INDEX

- Producer: scan_audiences action (action-driven)
- Path: docs/repo/meta_content/runs/{job_id}/audience_index.json
- Description: JSON index of discovered audience definitions. Maps each audience_id to an object containing: parsed frontmatter fields (6 fields), absolute path to the audience definition .md file, and audience body text. Variable count depending on number of .md files discovered in the audiences/ directory.
- Content: JSON structure: {audience_id: {audience_id, label, tone, focus_areas, exclude, section_structure, definition_path, body_text}}.

### META_DEV_FILE

- Producer: generate_meta step (prompt-driven)
- Path: docs/repo/meta_content/runs/{job_id}/META-DEV-{date}-{seq}_{slug}.md
- Description: Developer meta content file. Rich Markdown with YAML frontmatter containing 6 required fields (title, audience, audience_label, generated_date, source_version, section_count). Content tailored per the developer audience definition: tone, focus_areas, exclude list, and section_structure.
- Content: Self-contained developer guide synthesized from codebase documentation. Covers implementation details, API references, module documentation, and component architecture per developer focus areas.
- Edit mode: in_place (refine_meta step modifies in place).

### META_ARCH_FILE

- Producer: generate_meta step (prompt-driven)
- Path: docs/repo/meta_content/runs/{job_id}/META-ARCH-{date}-{seq}_{slug}.md
- Description: Architect meta content file. Rich Markdown with YAML frontmatter. Content tailored per the architect audience definition.
- Content: Self-contained architecture narrative covering design decisions, pattern analysis, integration maps, and system context per architect focus areas.
- Edit mode: in_place (refine_meta step modifies in place).

### META_EXEC_FILE

- Producer: generate_meta step (prompt-driven)
- Path: docs/repo/meta_content/runs/{job_id}/META-EXEC-{date}-{seq}_{slug}.md
- Description: Executive meta content file. Rich Markdown with YAML frontmatter. Content tailored per the executive audience definition.
- Content: Self-contained executive summary covering high-level status, risk summaries, and strategic capabilities per executive focus areas. Excludes implementation details per exclude list.
- Edit mode: in_place (refine_meta step modifies in place).

### META_INDEX

- Producer: generate_meta step (prompt-driven)
- Path: docs/repo/meta_content/runs/{job_id}/meta_index.json
- Description: JSON index of all generated meta files. Maps each audience_id to its output file path, generated_date, audience_label, and section_count. Enables downstream steps to iterate over all generated files without hardcoded references.
- Content: Structure per audience entry: {audience_id: {file, generated_date, audience_label, section_count}}.

### REVIEW_FILE_SUGGESTED

- Producer: review_meta step (prompt-driven)
- Path: docs/repo/meta_content/runs/{job_id}/{job_id}-review.md
- Description: Consolidated review document covering all generated meta files. Contains per-audience feedback sections evaluating completeness, accuracy, audience-appropriateness, and structural compliance.
- Content: One review section per audience, each assessing the corresponding meta content file against its audience definition constraints.

### VALIDATION_FILE

- Producer: validate_meta action (action-driven)
- Path: docs/repo/meta_content/runs/{job_id}/{job_id}-validation.md
- Description: Structural validation report for generated meta content files. Lists each file with pass/fail status per structural check (frontmatter fields, audience ID match, section headings, UTF-8 encoding).
- Content: Validation report table with file name, check name, and pass/fail result.

### META_BACKUP

- Producer: create_meta_backup action (action-driven)
- Path: docs/repo/meta_content/backups/BACKUP-{timestamp}/
- Description: Path to backup directory created before publish. Contains timestamped backup of previous current/ contents. Format: BACKUP-{YYYYMMDD-HHMMSS}/. Skipped on first run when current/ does not yet exist.
- Content: Complete copy of the previous docs/repo/meta_content/current/ directory tree.
- Note: Optional artifact. The action returns APPROVED with no backup on first run.

### META_MANIFEST

- Producer: publish_meta action (action-driven)
- Path: docs/repo/meta_content/current/meta_manifest.json
- Description: Published manifest in current/ tracking all published meta files. Contains 7 top-level fields: workflow_id, change_or_run_id, source_codebase_version, audiences, published_timestamp, supersedes, active_set.
- Content: JSON manifest with supersedes chain tracking the lineage of published content sets.

### META_MANIFEST_HISTORY

- Producer: publish_meta action (action-driven)
- Path: docs/repo/meta_content/history/{job_id}/meta_manifest.json
- Description: Manifest copy archived in history/{job_id}/ for traceability. Identical content to META_MANIFEST but stored in the historical archive directory.
- Content: Same JSON structure as META_MANIFEST, stored for audit trail.

### WORKFLOW_ACTIONS

- Producer: generate_package step (external workflow creation step)
- Path: workflows/codebase_to_meta_v1/actions.py
- Description: Python module with @action decorated functions implementing the 4 action-driven steps: scan_audiences, validate_meta, create_meta_backup, publish_meta. Required because the workflow type is "mixed" with action-driven steps.
- Content: Module containing scan_audiences(), validate_meta(), create_meta_backup(), and publish_meta() functions using the @action decorator from agent_runner_v2.workflow_packages.actions.

## Shared Artifacts

The following framework-level artifact keys are used by this workflow. These keys are defined globally and shared across multiple workflows.

| Key | Purpose in This Workflow |
|---|---|
| REVIEW_FILE_SUGGESTED | Review output from review_meta step. Standard review artifact key used across all SDLC workflows with review/refine loops. Defined in artifact_keys.py as ARTIFACT_KEY_REVIEW. |
| VALIDATION_FILE | Validation report from validate_meta action step. Standard validation artifact key used across all SDLC workflows with validation checkpoints. Defined in artifact_keys.py as ARTIFACT_KEY_VALIDATION. |

## Naming Rationale

### Key Naming Choices

- META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE: Per-audience output keys using the convention META_{AUDIENCE_ID}_FILE. Each initial audience (dev, arch, exec) gets a dedicated key for explicit traceability and individual in-place editing during the refine loop. The _FILE suffix follows the repository convention for document artifacts.

- META_INDEX: JSON index artifact naming follows the convention of INDEX suffix for registry/catalog artifacts (similar to AUDIENCE_INDEX). The index enables dynamic iteration over generated files without hardcoded per-audience references.

- AUDIENCE_INDEX: JSON index produced by scan_audiences. Named to clearly indicate it is an index of audience definitions. Produced internally within the workflow but listed as both input and output because downstream steps depend on it.

- CODEBASE_MANIFEST: References the codebase_manifest.json from the sdlc_00_codebase_v1 workflow output. Key name uses the MANIFEST suffix to indicate it is a registry/inventory document. This is a new key specific to this workflow's input contract, pointing to the same underlying file as CODEBASE_PUBLISH_MANIFEST in the codebase workflow.

- META_BACKUP: Directory path artifact. No _FILE suffix because it points to a directory, not a document. Follows the convention of naming backup artifacts by their purpose (similar to CODEBASE_BACKUP pattern from the reference workflow).

- META_MANIFEST and META_MANIFEST_HISTORY: Paired publish/history manifest keys. Follow the convention from sdlc_00_codebase_v1 which uses CODEBASE_PUBLISH_MANIFEST and CODEBASE_PUBLISH_MANIFEST_HISTORY. The META_ prefix distinguishes these from the codebase workflow's manifests while maintaining the same semantic relationship.

- REVIEW_FILE_SUGGESTED: Reuses the existing shared key. The _SUGGESTED suffix indicates the review is a suggestion pending human approval, consistent with the review/refine loop pattern.

- VALIDATION_FILE: Reuses the existing shared key. Standard validation report artifact across all SDLC workflows.

- WORKFLOW_ACTIONS: Standard key for the workflow package's actions.py module. Required for mixed-type workflows with action-driven steps.

### Path Pattern Choices

- Base output root: docs/repo/meta_content/ follows the same domain-based output root convention as sdlc_00_codebase_v1 which uses docs/repo/codebase/. The root reflects the content domain (meta content) rather than the workflow name.

- Staging directory: docs/repo/meta_content/runs/{job_id}/ is the staging area where generated content is written before publish. Follows the standard runs/{job_id}/ pattern.

- Filename prefix: META-DEV-, META-ARCH-, META-EXEC- prefixes match the artifact key names for consistency. The {date} component uses YYYYMMDD format. The {seq} component uses 3-digit zero-padded auto-incrementing sequence numbers via resolve_next_seq().

- Slug component: The {slug} is derived from the input specification filename using _extract_slug_from_path(). This enables traceability from output files back to the input that triggered their generation.

- Publish targets: docs/repo/meta_content/current/ and docs/repo/meta_content/history/{job_id}/ follow the standard publish lifecycle directories (current/, history/, backups/) matching the reference workflow pattern.

## Self-Validation Results

1. Coverage Check: PASS -- All 10 output artifacts from REQUIREMENTS-20260806-001_to_meta_v1.md have path patterns defined (AUDIENCE_INDEX, META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE, META_INDEX, REVIEW_FILE_SUGGESTED, VALIDATION_FILE, META_BACKUP, META_MANIFEST, META_MANIFEST_HISTORY). Plus WORKFLOW_ACTIONS for the action-driven steps. Plus CODEBASE_MANIFEST for the external input.

2. WORKFLOW_ACTIONS Check: PASS -- The requirements declare 4 action-driven steps (scan_audiences, validate_meta, create_meta_backup, publish_meta). WORKFLOW_ACTIONS is included in the contract.

3. Placeholder Validity Check: PASS -- {job_id} used in staging, history, and review paths. {date} used in meta content filenames. {seq} used in meta content filenames. {slug} used in meta content filenames. {timestamp} used in backup directory name. All paths are relative (no absolute paths). Forward slashes used throughout.

4. Path Consistency Check: PASS -- Paths follow the sdlc_00_codebase_v1 reference pattern: runs/{job_id}/ for staging, current/ for publish target, history/{job_id}/ for archive, backups/ for backup. Filename prefixes match artifact key names.

5. Collision Check: PASS -- No collisions with existing artifact keys in artifact_keys.py. REVIEW_FILE_SUGGESTED and VALIDATION_FILE are intentionally reused as shared framework keys. All other keys (CODEBASE_MANIFEST, AUDIENCE_INDEX, META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE, META_INDEX, META_BACKUP, META_MANIFEST, META_MANIFEST_HISTORY, WORKFLOW_ACTIONS) are new to this workflow and do not collide with existing definitions.
