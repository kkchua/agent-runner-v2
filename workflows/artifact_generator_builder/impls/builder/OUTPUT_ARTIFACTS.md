# Builder Output Artifacts (Fixed)

All builder-type workflows produce these fixed output artifacts — a complete, executable agent-runner-v2 workflow package.

## Output Artifact Table

| Artifact Key | Filename Pattern | Description |
|---|---|---|
| `WORKFLOW_TOML` | `workflow.toml` | Step definitions, routing (onsuccess chains), identity, implementation declarations |
| `ACTIONS_PY` | `actions.py` | Python @action functions for deterministic steps |
| `CONTEXT_EXTENSIONS_PY` | `context_extensions.py` | Artifact key registration, runtime context builder (extends WorkflowExtensions) |
| `PROMPTS_DIR` | `prompts/*.txt` | LLM prompt templates for prompt-driven steps |
| `IMPLS_DIR` | `impls/*/` | Alternative implementation overrides (impl.yaml, prompts/, actions.py) |
| `README_MD` | `README.md` | Human-readable workflow documentation with pipeline table |
| `REQUIREMENTS_TXT` | `requirements.txt` | Python dependencies for the generated workflow |

## Output Directory Structure

```
{output_dir}/{job_id}/
├── workflow.toml
├── actions.py
├── context_extensions.py
├── README.md
├── requirements.txt
├── prompts/
│   ├── 02_<step_name>.txt
│   ├── 03_<step_name>.txt
│   └── ...
└── impls/
    ├── <impl_name_1>/
    │   ├── impl.yaml
    │   ├── actions.py (optional)
    │   └── prompts/
    │       └── ...
    └── <impl_name_2>/
        └── ...
```

## Quality Gate Artifacts

The builder also produces these quality gate artifacts during generation:

| Artifact Key | Filename Pattern | Description |
|---|---|---|
| `ANALYSIS_JSON` | `ANALYSIS_JSON-001.json` | Structured analysis of the input requirement |
| `DOMAIN_PLAN` | `DOMAIN_PLAN-001.md` | Detailed implementation plan with action/prompt step plans |
| `PLAN_CHALLENGE` | `PLAN_CHALLENGE-001.md` | Adversarial analysis finding potential failures |
| `IMPL_CRITIQUE` | `IMPL_CRITIQUE-001.md` | Code-level review of generated actions.py |
| `PACKAGE_REVIEW` | `PACKAGE_REVIEW-001.md` | Structural consistency check |
| `VALIDATION_FINDINGS` | `VALIDATION_FINDINGS-001.md` | Deterministic validation results |
| `GATEKEEP_PACKAGE` | `GATEKEEP_PACKAGE-001.md` | Final approve/reject verdict |

## Constraints

- All generated workflow packages must be executable via `ukbe-run-agent run --template-group <name>`
- Generated actions.py must follow the @action decorator pattern with keyword-only args
- Generated context_extensions.py must extend WorkflowExtensions base class
- Generated prompts must include artifact placeholders and validation checklists
- Generated implementations must have impl.yaml declaring override mappings
