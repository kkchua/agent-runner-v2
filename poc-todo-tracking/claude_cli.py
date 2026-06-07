#!/usr/bin/env python3
"""POC 2: Claude Code CLI — can we pass tool definitions?

Claude Code CLI supports `--print` mode with JSON output.
Question: Does it support tool/function definitions that we can pass via CLI?

Test approach:
1. Try passing tool schemas via --allowed-tools or similar
2. If not, try the "write todo.md" approach and see if Claude follows it
3. Compare results with OpenAI API approach
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

TASK = (
    "Create a Python file called 'hello_poc.py' in the current directory that prints 'Hello from POC!'. "
    "Then verify it exists and show its contents. "
    "Finally, delete the file."
)

def test_claude_with_todo_instruction():
    """Test: Can Claude follow 'create todos first' instruction in prompt?"""
    
    prompt = f"""You are a helpful assistant. Follow this workflow EXACTLY:

Step 1 - Create your todo list FIRST:
Create a file called `todos.jsonl` in the current directory. Write ONE JSON line:
{{"tool": "create_todos", "args": {{"descriptions": ["Step 1 description", "Step 2 description", ...]}}}}

Step 2 - Do the work, one step at a time.

Step 3 - After completing each step, append to todos.jsonl:
{{"tool": "mark_complete", "args": {{"index": 1, "completion_notes": "What was done"}}}}

Step 4 - When all done, provide a summary.

MANDATORY: You MUST create todos.jsonl with create_todos BEFORE doing any work.
MANDATORY: You MUST mark each item complete as you finish it.

Task: {TASK}
"""
    
    print("=== Claude CLI: Todo via prompt instruction ===")
    print(f"Prompt length: {len(prompt)} chars\n")
    
    result = subprocess.run(
        ["claude", "--print", "--output-format", "json"],
        input=prompt,
        capture_output=True,
        text=True,
        timeout=120,
        cwd="/tmp/poc-claude",
        env={**os.environ, "CLAUDE_FORCE_COLOR": "1"},
    )
    
    # Check if todos.jsonl was created
    todos_path = Path("/tmp/poc-claude/todos.jsonl")
    if todos_path.exists():
        print("✅ todos.jsonl created!")
        for line in todos_path.read_text().strip().splitlines():
            print(f"  {line}")
    else:
        print("❌ todos.jsonl NOT created")
    
    # Check if hello_poc.py was created
    hello_path = Path("/tmp/poc-claude/hello_poc.py")
    if hello_path.exists():
        print("✅ hello_poc.py created!")
    else:
        print("❌ hello_poc.py NOT created")
    
    print(f"\nExit code: {result.returncode}")
    return result

def test_claude_with_tool_schema():
    """Test: Can we pass tool schemas to Claude CLI?"""
    
    # Claude doesn't have native --tools flag, but let's check if we can
    # use the --allowed-tools or pass tools via the prompt in a structured way
    
    print("\n=== Claude CLI: Tool schema attempt ===")
    
    result = subprocess.run(
        ["claude", "--help"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    
    has_tools = "--tools" in result.stdout or "--allowed-tools" in result.stdout
    print(f"Has --tools flag: {has_tools}")
    print(f"Has --allowed-tools: {'--allowed-tools' in result.stdout}")
    
    # Show relevant flags
    for line in result.stdout.splitlines():
        if "tool" in line.lower() or "allowed" in line.lower():
            print(f"  {line.strip()}")
    
    return has_tools

if __name__ == "__main__":
    os.makedirs("/tmp/poc-claude", exist_ok=True)
    
    print("=== POC 2: Claude Code CLI ===\n")
    
    # Check CLI capabilities
    test_claude_with_tool_schema()
    
    # Run the todo test
    test_claude_with_todo_instruction()
