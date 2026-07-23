---
template_id: "SYS-00-CDS"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "permanent codebase documentation standard"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "approved"
generated_at: "2026-07-21T21:16:49"
managed_by: "cli-command"
---

# Codebase Documentation Standard

## Purpose

This document defines the standard for codebase documentation within the
repository. It establishes conventions for documenting modules, components,
and changes.

## Documentation Structure

Codebase documentation follows a staging pattern under `docs/repo/codebase/`:

- `current/` -- Published stable version (active docs)
  - `00_standards/` - Documentation standards and rules
  - `01_inventory/` - Codebase inventory
  - `02_modules/` - Module-level documentation
  - `03_components/` - Component-level documentation
  - `04_changes/` - Change impact documentation
- `runs/<job_id>/` -- Staging area for in-progress sync operations
- `history/<job_id>/` -- Archived previous versions
- `backups/` -- Pre-sync safety snapshots

## Documentation Rules

### File Naming

- Use lowercase with underscores: `module_name.md`
- Match the Python module name when documenting a module
- Use descriptive names for component documentation

### Frontmatter Requirements

All codebase documentation must include YAML frontmatter with:

- `template_id`: Unique identifier for the document type
- `version`: Document version
- `doc_type`: "system" for codebase docs
- `authority`: "workflow-generated" or "human-authored"
- `scan_policy`: "include" for permanent docs
- `lifecycle_status`: "approved" for active docs

### Content Requirements

- ASCII-only content (no Unicode characters)
- Plain text section headings (no backticks or formatting)
- Clear purpose statement at the beginning
- Structured sections with consistent headings

## Update Triggers

Codebase documentation should be updated when:

1. New modules or components are added
2. Significant architectural changes occur
3. Module interfaces change
4. Component responsibilities shift

## Maintenance

Use `sdlc_00_codebase_v1` workflow for periodic synchronization of codebase
documentation with the actual repository state.
