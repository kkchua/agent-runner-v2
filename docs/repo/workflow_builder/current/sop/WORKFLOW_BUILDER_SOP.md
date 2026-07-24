# Workflow Builder SOP

> Standard Operating Procedure for the workflow builder system.
> Governs document storage, naming conventions, and audit trail.

## Storage Structure

```
docs/repo/workflow_builder/
├── current/
│   ├── sop/
│   │   └── WORKFLOW_BUILDER_SOP.md          ← This document
│   ├── templates/
│   │   └── WORKFLOW_SPEC_TEMPLATE.md        ← Template for user input specs
│   └── registry/
│       └── workflow_registry.md             ← Index of all generated workflows
├── specs/                                    ← User-provided input specs (permanent)
│   └── {slug}.md
├── runs/{job_id}/                            ← Per-run working documents
│   ├── REQUIREMENTS-{date}-{seq}_{slug}.md
│   ├── ARTIFACTS-{date}-{seq}_{slug}.md
│   ├── STEPS-{date}-{seq}_{slug}.md
│   ├── PROMPTS-{date}-{seq}_{slug}.md
│   ├── VALIDATION-{date}-{seq}_{slug}.md
│   └── REVIEW-{date}-{seq}_{slug}.md
└── history/{job_id}/                         ← Archived after completion
```

## Naming Conventions

### Input Specs

- Location: `docs/repo/workflow_builder/specs/`
- Format: `{slug}.md` where slug is a short descriptive name
- Example: `image-csv-gen-v3.md`, `notification-pipeline.md`

### Per-Run Artifacts

- Location: `docs/repo/workflow_builder/runs/{job_id}/`
- Prefix pattern: `{TYPE}-{YYYYMMDD}-{3-digit-seq}_{slug}.md`
- Types: REQUIREMENTS, ARTIFACTS, STEPS, PROMPTS, VALIDATION, REVIEW
- Sequence numbers auto-increment via `resolve_next_seq()`

### Generated Workflow Package

- Location: `workflows/{workflow_name}/`
- The workflow name must match:
  - `name` field in `workflow.toml`
  - `workflow_name` attribute in `context_extensions.py`
  - Directory name

## Document Lifecycle

1. **Draft** — User creates spec in `specs/`
2. **In Progress** — Builder creates run artifacts in `runs/{job_id}/`
3. **Completed** — Run artifacts moved to `history/{job_id}/`
4. **Registered** — Generated workflow added to `registry/workflow_registry.md`

## Audit Trail

Every workflow builder run produces:
- REQUIREMENTS doc — what the workflow should do
- ARTIFACTS doc — artifact key definitions and paths
- STEPS doc — step sequence, routing, role policies
- VALIDATION report — structural validation results
- REVIEW doc — quality review with approval/rejection

These documents form the audit trail for why the workflow was built
the way it was. They must be preserved in `history/` after completion.

## Per-Workflow Install Hooks

Every generated workflow must include in its `context_extensions.py`:

```python
def install_to_global(self, *, workspace_root, runner_home):
    """Install workflow files to global runner home, or NO_OP."""
    return {"status": "NO_OP"}

def sync_to_backend(self, *, workspace_root):
    """Sync workflow definition to backend, or NO_OP."""
    return {"status": "NO_OP"}
```

Workflows that produce global artifacts (templates, governance docs)
should implement real install logic. All others return NO_OP.
