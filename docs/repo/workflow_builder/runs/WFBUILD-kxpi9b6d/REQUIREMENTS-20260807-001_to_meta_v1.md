---
doc_type: "workflow_design"
lifecycle_status: "draft"
effective_version: "WFBUILD-kxpi9b6d"
workflow_name: "codebase_to_meta_v1"
workflow_label: "Codebase to Meta Content v1"
job_prefix: "META"
spec_source: "docs/repo/workflow_builder/specs/codebase_to_meta_v1.md"
---

# Workflow Requirements: Codebase to Meta Content v1

## Overview

This workflow transforms codebase documentation (~155 files under docs/repo/codebase/current/) into audience-specific Rich Markdown meta content files. It dynamically discovers audience definitions from a plugin directory (audiences/*.md), uses LLM generation to produce tailored content per audience, and follows a staging/review/refine/publish lifecycle. The output is a set of self-contained meta content documents organized by audience under docs/repo/meta_content/current/, with full version history and backup support. The audience set is extensible by dropping new .md files into the workflow package's audiences/ directory.

## Workflow Type

**Inferred Type:** Mixed (prompt-driven + action-driven)

**Justification:**

The workflow combines two categories of operations:

1. **Prompt-driven steps (LLM reasoning):** The core content generation requires LLM judgment to read ~155 codebase documentation files and synthesize audience-tailored Rich Markdown content. The review and refine steps also require LLM reasoning to evaluate generated content quality and suggest improvements. These steps cannot be implemented as deterministic Python code.

2. **Action-driven steps (deterministic operations):** Audience discovery (scanning a directory for .md files and parsing YAML frontmatter), meta index construction (assembling a JSON index from generated files), and the publish lifecycle (backup, archive, copy, manifest writing) are all deterministic file-system operations that should be implemented as Python actions for reliability and speed.

The mixed type is appropriate because the spec explicitly requires both dynamic audience discovery (action) and LLM-driven content synthesis (prompt), plus a deterministic publish lifecycle (action).

## Proposed Steps

### Step 1: scan_audiences

| Field | Value |
|-------|-------|
| Step Name | scan_audiences |
| Step Type | action |
| Purpose | Dynamically discover audience definitions from the workflow package's audiences/ directory. Parse YAML frontmatter from each .md file to extract audience_id, label, tone, focus_areas, exclude, and section_structure. Produce a structured audience index JSON that downstream prompt steps consume to know which audiences to generate for. |
| Inputs | audiences/ directory (within workflow package path) |
| Outputs | AUDIENCE_INDEX |
| Routing | onsuccess -> generate_meta |

### Step 2: generate_meta

| Field | Value |
|-------|-------|
| Step Name | generate_meta |
| Step Type | prompt |
| Purpose | Read all audience definitions (via AUDIENCE_INDEX) and selectively read codebase documentation files (guided by codebase_manifest.json and each audience's focus_areas). For each audience, generate a self-contained Rich Markdown meta content file following the audience's section_structure and tone guidance. Each meta content file must be readable without reference to source docs. |
| Inputs | AUDIENCE_INDEX, CODEBASE_MANIFEST |
| Outputs | META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE |
| Coder Role | architect_standard |
| Routing | onsuccess -> build_meta_index |

### Step 3: build_meta_index

| Field | Value |
|-------|-------|
| Step Name | build_meta_index |
| Step Type | action |
| Purpose | After meta content generation, assemble a JSON index (META_INDEX) cataloging all generated meta files. The index includes audience metadata (audience_id, label), generated file references, generation date, and source version. This index enables downstream review and publishing steps to locate and validate generated content. |
| Inputs | META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE |
| Outputs | META_INDEX |
| Routing | onsuccess -> generate_review |

### Step 4: generate_review

| Field | Value |
|-------|-------|
| Step Name | generate_review |
| Step Type | prompt |
| Purpose | Generate a review document that evaluates all generated meta content files. Check for completeness (all audience sections covered), accuracy (content traces to source docs), consistency (no contradictions across audience views), and self-contained readability. Produce actionable review suggestions per audience file. |
| Inputs | META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE, META_INDEX |
| Outputs | REVIEW_FILE_SUGGESTED |
| Coder Role | reviewer_standard |
| Routing | onsuccess -> review_meta |

### Step 5: review_meta

| Field | Value |
|-------|-------|
| Step Name | review_meta |
| Step Type | prompt |
| Purpose | Human review gate. Present all generated meta content files and the review document for human approval. The reviewer evaluates quality, accuracy, and completeness. Approve to proceed to publish, or reject to trigger refinement. |
| Inputs | META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE, META_INDEX, REVIEW_FILE_SUGGESTED |
| Outputs | REVIEW_FILE_SUGGESTED (in-place, updated with decision) |
| Coder Role | reviewer_standard |
| Routing | onsuccess -> create_meta_backup; on_reject_refine -> refine_meta; requires_human_approval_after = true |

### Step 6: refine_meta

| Field | Value |
|-------|-------|
| Step Name | refine_meta |
| Step Type | prompt |
| Purpose | Refine meta content files based on review feedback. Read the review document's suggestions and edit each meta content file in-place to address identified issues. Routes back to review_meta for re-evaluation. |
| Inputs | META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE, REVIEW_FILE_SUGGESTED |
| Outputs | META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE (edited in-place) |
| Coder Role | refine_standard |
| Routing | onsuccess -> review_meta |
| Edit Mode | in_place |
| Target Artifacts | META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE |

### Step 7: create_meta_backup

| Field | Value |
|-------|-------|
| Step Name | create_meta_backup |
| Step Type | action |
| Purpose | Before publishing new content, create a safety backup of the existing docs/repo/meta_content/current/ directory. Copy to backups/BACKUP-{timestamp}/. If current/ does not exist (first run), this step succeeds with NO_OP status. |
| Inputs | (implicit: docs/repo/meta_content/current/ if it exists) |
| Outputs | META_BACKUP |
| Routing | onsuccess -> publish_meta |

### Step 8: publish_meta

| Field | Value |
|-------|-------|
| Step Name | publish_meta |
| Step Type | action |
| Purpose | Execute the two-phase publish lifecycle: (1) Archive existing current/ to history/{job_id}/ if it exists. (2) Copy staged content from runs/{job_id}/ to current/ and write meta_manifest.json with workflow metadata, audience file references, timestamps, and supersedes tracking. |
| Inputs | META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE, META_INDEX |
| Outputs | META_MANIFEST |
| Routing | onsuccess -> promote_meta |

### Step 9: promote_meta

| Field | Value |
|-------|-------|
| Step Name | promote_meta |
| Step Type | action |
| Purpose | Update the Status field in the YAML frontmatter of all generated meta content files to "Approved". This marks the artifacts as finalized in the audit trail. |
| Inputs | META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE |
| Outputs | META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE (status updated in-place) |
| Action | promote_all |
| Promotes | META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE |
| Routing | onsuccess -> stepCompletion |

### Step 10: stepCompletion

| Field | Value |
|-------|-------|
| Step Name | stepCompletion |
| Step Type | action |
| Purpose | Terminal step. Signals workflow completion. |
| Inputs | (none) |
| Outputs | (none) |
| Action | step_completion |
| Routing | terminal |

## Custom Actions

| action_name | purpose | inputs | outputs | logic_description |
|-------------|---------|--------|---------|-------------------|
| scan_audiences | Discover and parse audience definition files from the workflow package audiences/ directory | workflow_package_path (context: path to workflow package root), AUDIENCE_INDEX (output path) | AUDIENCE_INDEX (JSON file) | 1. Glob audiences/*.md in workflow package directory. 2. For each .md file, parse YAML frontmatter to extract audience_id, label, tone, focus_areas, exclude, section_structure. 3. Validate each definition has required frontmatter fields (audience_id, label, tone, focus_areas, section_structure). 4. Write audience_index.json with list of audience definitions and their metadata. Return APPROVED with AUDIENCE_INDEX path. |
| build_meta_index | Assemble a JSON index of all generated meta content files | META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE (paths from state artifacts), META_INDEX (output path) | META_INDEX (JSON file) | 1. For each generated meta file, read YAML frontmatter to extract title, audience, audience_label, generated_date, source_version, section_count. 2. Build JSON object with workflow_id, job_id, list of audience entries (each with audience_id, label, file reference, metadata). 3. Write meta_index.json to staging area. Return APPROVED with META_INDEX path. |
| publish_meta | Execute two-phase publish: archive old current/ to history/, then copy staged content to current/ with manifest | META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE, META_INDEX (from state), META_MANIFEST (output path), job_id (from state) | META_MANIFEST (JSON file in current/) | 1. If docs/repo/meta_content/current/ exists, copy to docs/repo/meta_content/history/{job_id}/. 2. Create docs/repo/meta_content/current/ if not exists. 3. For each audience subdirectory in runs/{job_id}/, copy meta content files to current/{audience_id}/. 4. Write meta_manifest.json to current/ with workflow_id, job_id, audience file references, published_timestamp, supersedes (previous job_id or null), active_set: true. 5. Copy meta_index.json to current/. Return APPROVED with META_MANIFEST path. |

## Input Artifacts

| Artifact Key | Description | Required/Optional |
|--------------|-------------|-------------------|
| CODEBASE_MANIFEST | The codebase manifest file (codebase_manifest.json) from docs/repo/codebase/current/. Contains artifact inventory with metadata for all ~155 codebase documentation files. The generate_meta step reads this to understand the full doc inventory and selectively reads docs from each section. | Required |
| AUDIENCE_DEFINITIONS_DIR | The audiences/ directory within the workflow package. Contains .md files with YAML frontmatter defining each audience (audience_id, label, tone, focus_areas, exclude, section_structure) and prompt guidance in the body. Scanned dynamically by the scan_audiences action. | Required |

## Output Artifacts

| Artifact Key | Description | Required/Optional |
|--------------|-------------|-------------------|
| AUDIENCE_INDEX | JSON index of discovered audience definitions. Contains parsed frontmatter metadata for each audience (audience_id, label, tone, focus_areas, exclude, section_structure) plus the path to the audience definition .md file. Consumed by generate_meta to know which audiences to produce content for. | Required |
| META_DEV_FILE | Developer meta content file. Rich Markdown with YAML frontmatter (title, audience, audience_label, generated_date, source_version, section_count). Contains implementation-focused content: module APIs, dependencies, setup instructions, code patterns, extension points, testing guidance. Self-contained. | Required |
| META_ARCH_FILE | Architect meta content file. Rich Markdown with YAML frontmatter. Contains design-focused content: design decisions and rationale, pattern analysis, component relationships, dependency graphs, technical debt assessment, architectural constraints. Self-contained. | Required |
| META_EXEC_FILE | Executive meta content file. Rich Markdown with YAML frontmatter. Contains business-focused content: project overview, key metrics (module count, test coverage, workflow count), risk summary, progress status, cost/effort indicators. Self-contained. | Required |
| META_INDEX | JSON index of all generated meta files. Contains workflow_id, job_id, list of audience entries with audience_id, label, file path, and frontmatter metadata. Used by review and publish steps to locate generated content. | Required |
| REVIEW_FILE_SUGGESTED | Review document evaluating all generated meta content files. Contains per-audience assessment of completeness, accuracy, consistency, and readability. Includes actionable suggestions for refinement. Updated in-place during review step with approval/rejection decision. | Required |
| META_MANIFEST | Published manifest in current/ directory. JSON file tracking all published meta files with workflow_id, job_id, audience file references, published_timestamp, supersedes, active_set. Written by publish_meta action. | Required |
| META_BACKUP | Backup record indicating the backup location and timestamp. Written by create_meta_backup action. Contains backup_path, timestamp, and list of backed-up files. | Optional (NO_OP on first run if current/ does not exist) |

## Constraints

### Governance Constraints
- Layer 1 (governance) and Layer 2 (platform constitution) are read-only. This workflow operates in Layer 3 and must not redefine or extend governance standards.
- All generated documents must comply with governance standards declared in Layer 1/Layer 2 inputs.
- YAML frontmatter is mandatory on all generated documents. Missing frontmatter is a critical defect.

### Naming Constraints
- Workflow name: codebase_to_meta_v1 (must match directory name and context_extensions.py workflow_name).
- Job prefix: META.
- Artifact keys use UPPER_SNAKE_CASE with _FILE suffix for document artifacts.
- Audience definition files: lowercase .md files in audiences/ directory (developer.md, architect.md, executive.md).
- Output subdirectory names match audience_id from frontmatter (developer/, architect/, executive/).
- Meta content filenames follow pattern: META-{CODE}-{date}-{seq}.md (e.g., META-DEV-20260807-001.md).

### Dependency Constraints
- The audiences/ directory is part of the workflow package and must be deployed to the global runner home via install_to_global() in context_extensions.py.
- Codebase documentation must exist at docs/repo/codebase/current/ (produced by sdlc_00_codebase_v1 workflow).
- The codebase_manifest.json must be present and contain a valid artifact_inventory.
- Output paths follow the standard staging pattern: current/, runs/{job_id}/, history/{job_id}/, backups/.

### Behavioral Constraints
- Each meta content file must be self-contained (readable without reference to source codebase docs).
- The workflow must dynamically discover audience definitions at startup by scanning audiences/ for .md files.
- Each audience definition's YAML frontmatter drives the generation (tone, focus_areas, exclude, section_structure guide the LLM; the body provides additional prompt guidance).
- The generate step reads codebase_manifest.json to understand the full doc inventory, then selectively reads docs from each section as guided by each audience's focus_areas.
- The workflow follows the standard prompt-driven pattern with review/refine loop and human approval gate.
- Max refine iterations: 2 (matching sdlc_00_codebase_v1 pattern).
- ASCII-only output for all generated files.

## Open Questions

1. None. The specification provides sufficient detail to design the workflow. The audience plugin system, artifact keys, publish lifecycle, and content format are all defined. The three initial audience definitions (developer, architect, executive) are specified with their focus areas and section structures.
