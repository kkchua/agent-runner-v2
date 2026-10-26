# JiMeng Agentic Workflow Builder

Builds executable agent-runner-v2 workflow packages from JiMeng/Dreamai-style agentic workflow markdown definitions.

**Version:** 1.0.0

## Pipeline Steps

| # | Step | Type | Detail |
|---|------|------|--------|
| 1 | parse_jimeng_markdown | action | parse_jimeng_markdown |
| 2 | analyze_workflow_architecture | prompt | {{ slot.analyze_workflow_architecture }} |
| 3 | generate_prompt_templates | prompt | {{ slot.generate_prompt_templates }} |
| 4 | assemble_workflow_package | action | assemble_workflow_package |
| 5 | copy_infrastructure | action | _copy_infrastructure |
| 6 | assemble_package | action | _assemble_package |
| 7 | validate_structure | action | _validate_structure |
| 8 | review_package | prompt | {{ slot.review_package }} |
| 9 | gatekeep_package | prompt | {{ slot.gatekeep_package }} |
| 10 | promote_package | action | _promote_workflow_package |
| 11 | step_completion | action | step_completion |

## Implementations

| Name | Description |
|------|-------------|
| standard | Default implementation for JiMeng Agentic Workflow Builder |

## Usage

```bash
ukbe-run-agent run --template-group jimeng_agentic_workflow_builder
```

## File Structure

```
jimeng_agentic_workflow_builder/
    workflow.toml              # Infrastructure + domain steps
    context_extensions.py      # Infrastructure + domain artifact keys
    actions.py                 # Infrastructure actions
    prompts/                   # Infrastructure prompts
    impls/standard/            # Domain logic (actions, prompts, impl.yaml)
    README.md
```
