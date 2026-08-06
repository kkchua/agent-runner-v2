# codebase_to_meta_v1

Codebase to Meta Content v1

## Overview

The codebase_to_meta_v1 workflow transforms the existing codebase
documentation (~155 files under docs/repo/codebase/current/) into
audience-specific Rich Markdown meta content files. Different stakeholders
need different views of the same codebase:

- Developers need implementation details and APIs
- Architects need design decisions and pattern analysis
- Executives need high-level status and risk summaries

The workflow dynamically discovers audience definitions from a
plugin-extensible audiences/ directory, generates tailored content per
audience using LLM-driven synthesis, and publishes the results through
a staged review-and-publish lifecycle.

## Workflow Type

**Mixed** -- combines deterministic action steps with LLM-driven prompt
steps.

## Step Reference

| # | Step Name | Type | Role Policy | Routing |
|---|-----------|------|-------------|---------|
| 1 | scan_audiences | action | -- | onsuccess -> generate_meta |
| 2 | generate_meta | prompt | architect_standard | onsuccess -> review_meta |
| 3 | review_meta | prompt | reviewer_standard | onsuccess -> validate_meta; on_reject_refine -> refine_meta |
| 4 | refine_meta | prompt | architect_standard | onsuccess -> review_meta (loop) |
| 5 | validate_meta | action | -- | onsuccess -> create_meta_backup |
| 6 | create_meta_backup | action | -- | onsuccess -> publish_meta |
| 7 | publish_meta | action | -- | onsuccess -> stepCompletion |
| 8 | stepCompletion | action | -- | terminal |

## Review Loop

The review_meta / refine_meta pair forms a refinement loop:

1. review_meta evaluates all generated meta content files
2. If issues found, on_reject_refine routes to refine_meta
3. refine_meta applies corrections in place
4. refine_meta routes back to review_meta for re-evaluation
5. Maximum 2 iterations before REFINE_EXHAUSTED failure
6. review_meta has requires_human_approval_after = true

## Artifact Keys

| Key | Description |
|-----|-------------|
| CODEBASE_MANIFEST | Codebase manifest inventory (external input) |
| AUDIENCE_INDEX | JSON index of discovered audience definitions |
| META_DEV_FILE | Developer meta content file |
| META_ARCH_FILE | Architect meta content file |
| META_EXEC_FILE | Executive meta content file |
| META_INDEX | JSON index of all generated meta files |
| REVIEW_FILE_SUGGESTED | Consolidated review document |
| VALIDATION_FILE | Structural validation report |
| META_BACKUP | Backup directory path (optional) |
| META_MANIFEST | Published manifest in current/ |
| META_MANIFEST_HISTORY | Manifest copy in history/ |

## Custom Actions

| Action | Purpose |
|--------|---------|
| scan_audiences | Discover and index audience definitions from audiences/ |
| validate_meta | Structural validation of generated meta content files |
| create_meta_backup | Backup current/ before publishing |
| publish_meta | Publish staged content to current/ and history/ |

## Context Variables

| Variable | Description |
|----------|-------------|
| AUDIENCES_ROOT | Root of workflow package audiences/ directory |
| CODEBASE_CURRENT_ROOT | Root of codebase documentation tree |
| CODEBASE_MANIFEST | Path to codebase_manifest.json |
| GOVERNANCE_RUNTIME_ROOT | Layer 1 governance runtime root |
| PLATFORM_RUNTIME_ROOT | Layer 2 platform constitution runtime root |
| META_CONTENT_ROOT | Base output directory for meta content |

## Directory Structure

```
workflows/codebase_to_meta_v1/
  workflow.toml          Step definitions, routing, artifact bindings
  context_extensions.py  WorkflowExtensions interface implementation
  actions.py             Custom action implementations
  README.md              This file
  audiences/             Audience definition files (.md)
    developer.md         Developer audience definition
    architect.md         Architect audience definition
    executive.md         Executive audience definition
  prompts/               Prompt templates
    02_generate_meta.txt Generate meta content per audience
    03_review_meta.txt   Review generated meta content
    04_refine_meta.txt   Refine meta content based on review
```

## Output Lifecycle

The workflow follows a staged publish lifecycle:

1. **Stage**: generate_meta produces meta files to runs/{job_id}/
2. **Review**: review_meta evaluates quality and compliance
3. **Refine**: refine_meta applies corrections (loop with review)
4. **Validate**: validate_meta performs structural checks
5. **Backup**: create_meta_backup archives current/ before publish
6. **Publish**: publish_meta copies to current/ and archives to history/

## Audience Extensibility

To add a new audience:

1. Create a new .md file in the audiences/ directory with YAML frontmatter
2. Add a corresponding META_{ID}_FILE artifact key in context_extensions.py
3. The generate_meta prompt handles all audiences via AUDIENCE_INDEX

No changes to step definitions are needed. The scan_audiences action
dynamically discovers all .md files in the audiences/ directory.

## Installation

```bash
# Install to global runner home (copies audiences/ directory)
ukbe-run-agent install codebase_to_meta_v1

# Or install all workflows
ukbe-run-agent install
```

## Running

```bash
# Run from batch file or terminal
ukbe-run-agent run --template-group codebase_to_meta_v1 --new-job
```
