---
template_id: "CODEBASE-INV-TPL-v1"
title: "Codebase Inventory Template"
status: "active"
generated: "2026-07-09T10:35:00+08:00"
workflow: "10_execution_scaffold_v1"
step: "07_generate_templates"
change_id: "10SCAFFOLD-20260708-8a4445fc"
managed_by: workflow-generated
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Metadata

- **Template ID**: CODEBASE-INV-TPL-v1
- **Artifact Key**: `CODEBASE_INVENTORY_TEMPLATE`
- **Version**: 1.0
- **Owner**: Codebase Documentation Workflow
- **Purpose**: Defines template fields, entry template, status definitions, and file type coverage for systematic codebase inventory management

# Template Fields

## Required Fields

Every inventory entry must include the following fields:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| **Name** | String | Module or component name | `step_runner` |
| **Path** | String | File or directory path relative to project root | `agent_runner_v2/step_runner.py` |
| **Type** | String | Entry type: module/component/package | `module` |
| **Status** | String | Current documentation status (see Status Definitions) | `current` |
| **Owner-Doc Path** | String | Path to associated documentation file | `docs/codebase/02_modules/step_runner.md` |
| **Documentation Mode** | String | How documentation is maintained: auto_generated/manual_curation/hybrid | `auto_generated` |
| **Last Verified By Change** | String | Commit hash or change ID that last verified this entry | `d57a719` |
| **Last Verified Date** | Date | When this entry was last verified | `2026-07-09` |
| **Next Review Due** | Date | When this entry should be reviewed next | `2026-10-09` |
| **Profile Metadata** | Object | Optional: architecture profile information if applicable | See Profile Metadata section |

## Optional Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| **Description** | String | Brief description of module/component purpose | "Prompt rendering and sidecar validation" |
| **Dependencies** | Array | List of other modules/components this depends on | `["constants", "bundle_loader"]` |
| **Tags** | Array | Categorization tags for filtering | `["core", "execution", "validation"]` |
| **Complexity** | String | Relative complexity indicator | `LOW/MEDIUM/HIGH` |
| **Test Coverage** | String | Test coverage percentage or status | `85%` or `N/A` |

## Profile Metadata

When a module or component introduces or replaces a declared architecture standard, include profile metadata:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| **Current Profile** | String | Architecture standard currently in use | `DDD/EDA hybrid` |
| **Target Profile** | String | Architecture standard being adopted (if transitioning) | `event-driven microservices` |
| **Migration Mode** | String | How transition is occurring | `strangler_fig` or `not_applicable` |
| **Profile Introduction Date** | Date | When this profile was introduced | `2026-07-09` |
| **Profile Owner** | String | Who owns this architectural decision | `Architecture Team` |

# Entry Template

Use this template for each inventory entry:

## [Module/Component Name]

- **Path**: `[relative/path/to/file_or_directory]`
- **Type**: `[module/component/package]`
- **Status**: `[current/needs_update/pending_review/superseded]`
- **Owner-Doc Path**: `[docs/codebase/XX_type/name.md]`
- **Documentation Mode**: `[auto_generated/manual_curation/hybrid]`
- **Last Verified By Change**: `[commit_hash_or_change_id]`
- **Last Verified Date**: `[YYYY-MM-DD]`
- **Next Review Due**: `[YYYY-MM-DD]`
- **Description**: [Brief description of purpose]
- **Dependencies**: [`[dep1]`, `[dep2]`]
- **Tags**: [`[tag1]`, `[tag2]`]`
- **Complexity**: `[LOW/MEDIUM/HIGH]`
- **Test Coverage**: `[XX% or N/A]`

### Profile Metadata (if applicable)

- **Current Profile**: `[architecture_standard]`
- **Target Profile**: `[target_architecture_standard]`
- **Migration Mode**: `[migration_approach]`
- **Profile Introduction Date**: `[YYYY-MM-DD]`
- **Profile Owner**: `[owner_name_or_role]`

---

[Repeat for all entries...]

# Status Definitions

## current

**Definition**: Documentation is up-to-date with code and has been recently verified.

**Criteria**:
- Documentation reflects current code state accurately
- Last verified within review frequency window (e.g., 90 days for core modules)
- No known discrepancies between code and documentation
- Examples in documentation match actual implementation

**Actions Required**: None — entry is healthy.

**Review Frequency**: 
- Core modules: Every 90 days
- Supporting modules: Every 180 days
- Utility modules: Every 365 days

## needs_update

**Definition**: Documentation is known to be stale and requires updates.

**Criteria**:
- Code has changed but documentation has not been updated
- Known discrepancies exist between code and documentation
- Examples in documentation no longer match implementation
- API signatures have changed but docs still show old signatures

**Actions Required**:
1. Update documentation to reflect current code state
2. Verify all examples match actual implementation
3. Update last_verified_by_change and last_verified_date
4. Set status to pending_review after updates complete

**Review Frequency**: Immediate — should be addressed in next documentation sync workflow.

## pending_review

**Definition**: Documentation has been updated but not yet verified for accuracy.

**Criteria**:
- Documentation updates have been made but not reviewed
- Changes made by developer who is not primary owner
- Automated documentation generation awaiting human verification
- Awaiting reviewer approval before marking as current

**Actions Required**:
1. Assign reviewer (module owner or designated reviewer)
2. Reviewer verifies documentation against code
3. If accurate, set status to current and update last_verified_date
4. If inaccurate, set status to needs_update with specific issues noted

**Review Frequency**: Within 7 days of entering pending_review status.

## superseded

**Definition**: Documentation or code has been replaced by something else.

**Criteria**:
- Module has been deprecated and replaced by another module
- Documentation has been consolidated into a different document
- Functionality moved to a different location
- Legacy documentation kept for reference only

**Actions Required**:
1. Identify replacement module/documentation
2. Add cross-reference to replacement in notes
3. Preserve entry for historical reference but mark clearly as superseded
4. Consider archival if no longer needed for reference

**Review Frequency**: One-time action — verify replacement is adequate, then archive if appropriate.

# File Type Coverage

The inventory system covers all source file types in the repository:

## Python Files (.py)

**Coverage**: All `.py` files in `agent_runner_v2/` package

**Documentation Approach**:
- Individual modules → Module documentation in `docs/codebase/02_modules/`
- Package-level views → Component documentation in `docs/codebase/03_components/`

**Inventory Entry Requirements**:
- Must have corresponding module documentation file
- Must track test coverage where applicable
- Must identify dependencies on other modules

## Markdown Files (.md)

**Coverage**: All documentation files in `docs/` directory

**Documentation Approach**:
- System documentation → Tracked in system doc inventory
- Codebase documentation → Tracked in codebase inventory
- Delivery artifacts → Tracked in delivery inventory

**Inventory Entry Requirements**:
- Must identify owner and review schedule
- Must track status (current/needs_update/pending_review/superseded)
- Must link to related documents where applicable

## Configuration Files (.json, .toml, .ini, .cfg)

**Coverage**: Configuration files affecting runtime behavior

**Documentation Approach**:
- Documented within relevant module or system documentation
- Critical configuration files may have dedicated documentation

**Inventory Entry Requirements**:
- Must identify which modules consume this configuration
- Must document configuration schema if complex
- Must track default values and valid ranges

## Batch/Shell Scripts (.bat, .sh)

**Coverage**: Launcher scripts in repository root

**Documentation Approach**:
- Documented in developer guide or runbook
- Complex scripts may have dedicated module documentation

**Inventory Entry Requirements**:
- Must document script purpose and usage
- Must identify environment prerequisites
- Must track dependencies on Python packages or external tools

## Template Files (.txt, .j2, etc.)

**Coverage**: Prompt templates and workflow templates in `bootstrap/`

**Documentation Approach**:
- Documented within workflow documentation
- Template structure documented in developer guide

**Inventory Entry Requirements**:
- Must identify which workflow uses this template
- Must document template variables and placeholders
- Must track template versioning if applicable

## Data Files (.json, .yaml, .yml)

**Coverage**: Data files used by workflows or tests

**Documentation Approach**:
- Documented within relevant workflow or test documentation
- Schema documentation for structured data files

**Inventory Entry Requirements**:
- Must document data file purpose and format
- Must identify which workflows or tests consume this data
- Must track data file versioning if applicable

## Other File Types

Any other file types significant to repository operation should be inventoried with appropriate documentation approach and entry requirements defined based on file purpose and usage.
