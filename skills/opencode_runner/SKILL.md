# Opencode Runner

Use this skill when you need to run opencode CLI commands as a background task.
This encapsulates the knowledge of how to invoke opencode with the correct
agent-runner-v2 syntax so you don't need to repeat it every time.

## CLI Syntax

```bash
cd /d "{workspace_root}" && echo "{prompt_text}" | opencode run --model 00-bailian/qwen3.7-plus --agent arv_coder --auto
```

## Parameters

| Parameter     | Description                                          | Example                                            |
|---------------|------------------------------------------------------|----------------------------------------------------|
| `workspace_root` | The directory to `cd` into before running opencode  | `D:\MyProjectSpace\01_Workflows\agent-runner-v2`   |
| `doc_path`    | Path to the task/impl doc opencode should read       | `docs/QwenPaw/gen_media_content_v1/tasks/TASKS_PHASE1.md` |
| `prompt_text` | Instruction to pass to opencode                      | "Read {doc_path} and follow all instructions"      |

## Common Prompt Patterns

### Read doc and execute
```
Read the file at {doc_path} and follow ALL instructions in it. Do NOT modify any files outside of the specified scope. When done, list all files you created or modified.
```

### Read doc and report only (no changes)
```
Read the file at {doc_path} and tell me what it asks you to do. Do NOT create or modify any files.
```

## Execution Flow

1. Receive `workspace_root`, `doc_path`, `prompt_text`
2. Construct the CLI command
3. Execute via `execute_shell_command` with appropriate timeout (300s for simple tasks, 600s for complex)
4. Report results: files created/modified, any errors, exit code

## Error Handling

- If opencode fails, report the error output
- If timeout, kill the process (`taskkill /F /IM opencode.exe /IM node.exe`)
- If governance blocks, report the denial reason

## Important Notes

- `arv_coder` agent has bash/write/edit permissions pre-configured
- The `--auto` flag auto-approves permissions (dangerous, use carefully)
- opencode runs under the arv_coder agent profile which already knows BCS, TDD, and workflow conventions
- All file paths in prompts should be relative to `workspace_root`
