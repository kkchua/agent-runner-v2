---
name: todo-tracking-for-workflow
description: Procedure for creating and managing todos using the create_todos and mark_complete functions in workflow steps
source: auto-skill
extracted_at: '2026-06-05T09:25:30.097Z'
---

# Todo Tracking for Workflow Steps

## When to use
This skill applies when executing any workflow step that requires progress tracking using the create_todos and mark_complete functions. This is particularly important for the delivery_scaffold_v1 workflow and other multi-step processes.

## Required tracking sequence

### Step 1: Create todos at the beginning of the task
Call the create_todos function immediately after starting the workflow step using the shell command:
```
python3 -c "from agent_runner_v2.agent_tools import create_todos; create_todos('JOB_ID', ['Step 1 description', 'Step 2 description', ...])"
```

Where JOB_ID is the specific job identifier provided by the runner (e.g., SCAFFOLD-GEN-20260605-007) and the list contains all the major steps of the task.

**Note**: The create_todos and mark_complete functions are not available as direct tools in the tool registry, but must be called via shell commands as shown.

### Step 2: Execute each step and mark complete
After completing each step, call the mark_complete function using the shell command:
```
python3 -c "from agent_runner_v2.agent_tools import mark_complete; mark_complete('JOB_ID', STEP_NUMBER, notes='Specific notes about what was done for this step')"
```

Where STEP_NUMBER is the 1-based index of the step being marked complete, and notes should be unique for each step describing what was accomplished.

### Step 3: Maintain unique notes
Each call to mark_complete must have UNIQUE notes describing what you did for that specific step. This prevents confusion and provides clear audit trail.

## Best practices for todo creation

Create concrete, actionable steps that can be individually completed:
- "Scan project root for AI context files"
- "Read discovered files"
- "Analyze project domain and tech stack"
- "Assess complexity and workflow scope"
- "Write output files"
- "Verify all files exist"

Avoid vague or overlapping step descriptions.

## Important considerations

- Call create_todos function FIRST before starting the main work
- Call mark_complete function after EACH step with unique notes
- Make sure the job ID matches exactly what was provided by the runner
- Use 1-based indexing for step numbers in mark_complete
- Each mark_complete call must have meaningful, different notes
- Don't skip steps - mark each one as complete in sequence
- Actually execute the functions with real arguments - don't just describe the process