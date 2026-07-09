---
template_id: "CODEBASE-CHG-v1"
title: "Codebase Change Template"
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

- **Template ID**: CODEBASE-CHG-v1
- **Artifact Key**: `CODEBASE_CHANGE_TEMPLATE`
- **Version**: 1.0
- **Owner**: Codebase Documentation Workflow
- **Purpose**: Tracks change summary, changed files, documentation updates, stale documentation removal, documentation freshness verification, cross-references, and notes for systematic change impact tracking

# Change Summary

**Change ID**: `[CHANGE-IMPACT-NNN]` or `[commit_hash]`

**Change Title**: [Brief descriptive title]

**Change Date**: [YYYY-MM-DD when change was made]

**Author**: [Name or role of person making the change]

**Change Type**: [feature/bugfix/refactor/documentation/infrastructure/configuration]

**Scope**: [S/M/L/XL — estimated scope of change]

**Summary**: [2-3 sentence description of what changed and why]

## Motivation

[Explain why this change was made]

**Problem**: [What problem or opportunity prompted this change]

**Solution**: [How this change addresses the problem]

**Alternatives Considered**: [Other approaches considered and why rejected]

## Impact Assessment

**Risk Level**: [LOW/MEDIUM/HIGH]

**Breaking Change**: [YES/NO — does this break existing functionality?]

**Migration Required**: [YES/NO — do users need to take action?]

**Affected Workflows**: [List workflows affected if any]

# Changed Files

## Source Code Changes

[List all source code files modified]

| File | Change Type | Lines Changed | Purpose |
|------|-------------|---------------|---------|
| `[path/to/file.py]` | new/modified/deleted | [+X/-Y] | [Why this file changed] |
| `[path/to/file.py]` | new/modified/deleted | [+X/-Y] | [Why this file changed] |

### Detailed Changes

[For significant changes, provide before/after comparisons]

#### Change in `[file.py]`

**Before**:
```python
# Original code
```

**After**:
```python
# Updated code
```

**Rationale**: [Why this change was made]

## Configuration Changes

[List configuration files modified]

| File | Change Type | Purpose | Migration Notes |
|------|-------------|---------|-----------------|
| `[path/to/config.json]` | modified | [What config controls] | [Any migration steps needed] |
| `.env.example` | modified | [What env var added/changed] | [Users must add to their .env] |

## Documentation Changes (Planned)

[List documentation that should be updated as a result of this change]

| Documentation | Artifact Key | Action Required | Priority | Owner |
|---------------|--------------|-----------------|----------|-------|
| [Doc name] | [ARTIFACT_KEY] | create/update/retire | HIGH/MED/LOW | [Role] |
| [Doc name] | [ARTIFACT_KEY] | create/update/retire | HIGH/MED/LOW | [Role] |

# Documentation Updates

## Documentation Created

[List documentation artifacts created as part of this change]

| Documentation | Artifact Key | Path | Purpose | Status |
|---------------|--------------|------|---------|--------|
| [Doc name] | [ARTIFACT_KEY] | `[docs/path/to/doc.md]` | [Why created] | current |
| [Doc name] | [ARTIFACT_KEY] | `[docs/path/to/doc.md]` | [Why created] | current |

## Documentation Updated

[List documentation artifacts updated as part of this change]

| Documentation | Artifact Key | What Changed | Reason | Verified By | Verified Date |
|---------------|--------------|--------------|--------|-------------|---------------|
| [Doc name] | [ARTIFACT_KEY] | [What was updated] | [Why updated] | [Name/Role] | [YYYY-MM-DD] |
| [Doc name] | [ARTIFACT_KEY] | [What was updated] | [Why updated] | [Name/Role] | [YYYY-MM-DD] |

### Update Details

[For significant documentation updates, provide details]

#### Update to `[Documentation Name]`

**Artifact Key**: `[ARTIFACT_KEY]`

**What Changed**: [Describe specific sections or content updated]

**Before**:
```markdown
# Old content
```

**After**:
```markdown
# New content
```

**Reason**: [Why this update was necessary]

**Verification Method**: [How accuracy was verified after update]

## Documentation Retired

[List documentation artifacts retired or superseded as part of this change]

| Documentation | Artifact Key | Reason for Retirement | Replacement | Superseded Date |
|---------------|--------------|----------------------|-------------|-----------------|
| [Doc name] | [ARTIFACT_KEY] | [Why retired] | [What replaces it, if anything] | [YYYY-MM-DD] |

# Stale Documentation Removal

## Identified Stale Documentation

[List documentation identified as stale due to this change]

| Documentation | Artifact Key | Why Stale | Action Taken | Date |
|---------------|--------------|-----------|--------------|------|
| [Doc name] | [ARTIFACT_KEY] | [Why it became stale] | updated/marked_needs_update/supersede/removed | [YYYY-MM-DD] |
| [Doc name] | [ARTIFACT_KEY] | [Why it became stale] | updated/marked_needs_update/supersede/removed | [YYYY-MM-DD] |

## Action Details

[For each stale documentation item, describe action taken]

### Stale Doc: `[Documentation Name]`

**Artifact Key**: `[ARTIFACT_KEY]`

**Staleness Reason**: [Why documentation became stale]

**Action Taken**: [updated/marked_needs_update/supersede/removed]

**Details**: 
- If **updated**: Describe what was updated
- If **marked_needs_update**: Note when update is planned
- If **superseded**: Link to replacement documentation
- If **removed**: Explain why removal is appropriate

**Verification**: [How we verified the action was appropriate]

## Proactive Stale Detection

[Describe any proactive measures taken to detect other potentially stale documentation]

**Scan Performed**: [YES/NO — did we scan for other stale docs?]

**Scan Method**: [How we scanned: manual review, automated tool, grep, etc.]

**Additional Stale Docs Found**: [N — how many additional stale docs were found?]

**Action Plan**: [What will be done about additional stale docs]

# Documentation Freshness Verification

## Freshness Verification Checklist

Use this checklist to verify documentation remains fresh after this change:

- [ ] All changed modules have updated documentation
- [ ] Module documentation examples match current implementation
- [ ] API signatures in documentation match function definitions
- [ ] Dependency lists reflect current imports
- [ ] Component documentation reflects module changes
- [ ] Codebase inventory updated with status changes
- [ ] System documentation updated if architectural changes made
- [ ] All referenced artifact keys resolve correctly

## Verification Methods

[Describe methods used to verify documentation freshness]

### Method 1: [Method Name]

**Description**: [How this verification method works]

**Scope**: [What documentation this verifies]

**Results**: [What this verification found]

**Limitations**: [What this method cannot verify]

### Method 2: [Method Name]

**Description**: [How this verification method works]

**Scope**: [What documentation this verifies]

**Results**: [What this verification found]

**Limitations**: [What this method cannot verify]

## Freshness Metrics

[Quantify documentation freshness where possible]

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Modules with current docs | [N out of M] | [Target %] | PASS/FAIL |
| Examples matching code | [N out of M] | [Target %] | PASS/FAIL |
| Artifact keys resolving | [N out of M] | 100% | PASS/FAIL |
| Inventory accuracy | [XX%] | [Target %] | PASS/FAIL |

## Next Freshness Review

**Scheduled Date**: [YYYY-MM-DD when next freshness review is due]

**Review Scope**: [What will be reviewed]

**Review Method**: [How freshness will be verified]

**Owner**: [Who is responsible for next review]

# Cross-References

## Related Changes

[List related changes in the repository]

| Change ID | Link | Relationship | Shared Impact |
|-----------|------|--------------|---------------|
| [Change ID] | [Link to change impact doc] | [How related] | [What impacts overlap] |
| [Change ID] | [Link to change impact doc] | [How related] | [What impacts overlap] |

## Related Initiatives

[List initiatives related to this change]

| Initiative | Link | Relationship |
|------------|------|--------------|
| [Initiative name] | [Link to initiative doc] | [How related] |

## Related Plans

[List plans related to this change]

| Plan | Link | Relationship |
|------|------|--------------|
| [Plan name] | [Link to plan doc] | [How related] |

## Related Tasks

[List tasks that implemented or validated this change]

| Task | Task ID | Relationship |
|------|---------|--------------|
| [Task name] | T-NNN | [How related] |

## Related Decisions

[List architectural or strategic decisions related to this change]

| Decision | Link | Relationship |
|----------|------|--------------|
| [Decision description] | [Link to decision log] | [How related] |

## Git References

[Provide git references for traceability]

**Commit Hash**: `[full_commit_hash]`

**Pull Request**: #[PR number] (if applicable)

**Branch**: `[branch_name]` (if still available)

**Diff Link**: [Link to diff if hosted somewhere accessible]

# Notes

- [Additional context about the change not captured elsewhere]
- [Assumptions made during implementation]
- [Constraints that shaped the change]
- [Open questions for future investigation]
- [Acknowledgments for contributors]
- [Link to discussions, meeting notes, or informal decisions not formally documented]
- [Temporary workarounds implemented with plans for future cleanup]
- [Special considerations for Windows compatibility if applicable]
- [Rollback plan if change needs to be reverted]
