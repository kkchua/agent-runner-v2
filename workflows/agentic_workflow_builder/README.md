# Agentic Workflow Builder

Builds executable agent-runner-v2 workflows from JiMeng/Dreamai-style agentic workflow markdown definitions.

**Version:** 1.0.0

## Pipeline Steps

| # | Step | Type | Detail |
|---|------|------|--------|
| 1 | parse_jimeng_markdown | action | parse_jimeng_markdown |
| 2 | analyze_workflow_structure | prompt | prompts/02_analyze_workflow_structure.txt |
| 3 | design_workflow_steps | prompt | prompts/03_design_workflow_steps.txt |
| 4 | implement_actions | prompt | prompts/04_implement_actions.txt |
| 5 | generate_prompts | prompt | prompts/05_generate_prompts.txt |
| 6 | assemble_requirements | action | assemble_requirements |
| 7 | step_completion | action | step_completion |

## Implementations

| Name | Description |
|------|-------------|
| default | Default implementation (workflow.toml) |
| minimal | Condensed action implementations and streamlined prompts with minimal validation, suitable for simple JiMeng workflows with few phases and no complex conditional routing. |
| detailed | Comprehensive action implementations with full error handling and state management, detailed prompts preserving all quality criteria and self-check rules from the JiMeng source. |

## Usage

```bash
ukbe-run-agent run --template-group agentic_workflow_builder
```

## File Structure

```
agentic_workflow_builder/
    workflow.toml
    context_extensions.py
    actions.py
    prompts/
    impls/          (if alternative implementations exist)
    README.md
```
