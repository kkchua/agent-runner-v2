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
│   ├── REVIEW-{date}-{seq}_{slug}.md
│   ├── workflow.toml                         ← Generated manifest
│   ├── context_extensions.py                 ← Generated extensions
│   ├── README.md                             ← Generated user guide
│   ├── .env.sample                           ← Generated env template (conditional)
│   ├── config.json.sample                    ← Generated config template (conditional)
│   └── prompts/                              ← Generated prompt templates
│       ├── 01_step_name.txt
│       └── ...
└── history/{job_id}/                         ← Archived after completion
```

## Naming Conventions

### Input Specs

- Location: `docs/repo/workflow_builder/specs/`
- Format: `{slug}.md` where slug uses `lowercase_with_underscores`
- Example: `agnes_media_gen_v1.md`, `notification_pipeline.md`
- The slug becomes the workflow package name (directory, workflow.toml
  name, context_extensions.py workflow_name)

### Per-Run Artifacts

- Location: `docs/repo/workflow_builder/runs/{job_id}/`
- Prefix pattern: `{TYPE}-{YYYYMMDD}-{3-digit-seq}_{slug}.md`
- Types: REQUIREMENTS, ARTIFACTS, STEPS, PROMPTS, VALIDATION, REVIEW
- Sequence numbers auto-increment via `resolve_next_seq()`

### Generated Workflow Package

- Location: `workflows/{slug}/`
- The slug is derived from the input spec filename (e.g.,
  `specs/agnes-media-gen-v1.md` → slug `agnes-media-gen-v1`)
- The slug must match:
  - `name` field in `workflow.toml`
  - `workflow_name` attribute in `context_extensions.py`
  - Directory name

## Supplementary Files

The generate_package step produces supplementary files alongside the
required workflow.toml and context_extensions.py:

### README.md (always generated)

A user guide for the generated workflow package. Must include:

- **Overview** — what the workflow does, its purpose and scope
- **Prerequisites** — required setup, dependencies, API access
- **Installation** — how to deploy the workflow package
- **Configuration** — environment variables (.env) and config.json settings
- **Usage** — how to run the workflow (batch file, operator console, daemon)
- **Step Reference** — table of steps with name, type, role, and purpose
- **Artifact Keys** — table of all artifact keys with descriptions

### .env.sample (conditional)

Generated only when the workflow needs environment variables such as
API keys, credentials, or external service configuration. Format:

```
# Description of what this variable does
WORKFLOW_API_KEY=your_api_key_here
```

### config.json.sample (conditional)

Generated only when the workflow needs runtime configuration beyond
what .env provides. Must be valid JSON with sensible defaults and
inline comments where possible.

## Promotion

After the review_package step approves the generated package, the
promote_package step copies the deployable files to the repo workflows
directory:

```
Source:  docs/repo/workflow_builder/runs/{job_id}/
Target:  workflows/{workflow_name}/
```

### Files copied during promotion

| File | Condition |
|------|-----------|
| `workflow.toml` | Always |
| `context_extensions.py` | Always |
| `actions.py` | If exists |
| `prompts/` | If exists |
| `README.md` | Always |
| `.env.sample` | If exists |
| `config.json.sample` | If exists |

### Files NOT copied

Design docs (REQUIREMENTS, ARTIFACTS, STEPS, PROMPTS index, VALIDATION,
REVIEW), meta.json sidecars, and validation reports stay in the run
directory for the audit trail.

### Backup behavior

If the target directory already exists, it is backed up as
`workflows/{workflow_name}_bak_{timestamp}/` before copying.

### Post-promotion

After promotion, the user should:
1. Run `ukbe-run-agent sync-workflows {workflow_name}` to sync to backend
2. Run bootstrap-publish if the workflow should be included in the
   packaged bootstrap bundle

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
