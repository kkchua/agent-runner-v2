# POC: Todo Tracking for LLM Coders

## The Problem

When we ask an LLM to "write a todo.md file and update it as you work", it:
- Ignores the instruction
- Writes a custom format we can't parse
- Never updates it mid-task

## The Solution (from Ed Donner's OpenAI agent loop)

Use **function calling** — the LLM natively calls `create_todos()` and `mark_complete()` as tools. Progress is captured from tool calls, not from files.

## This POC

1. **openai_api.py** — Direct OpenAI API with function calling (the "gold standard" pattern)
2. **claude_cli.py** — Claude Code CLI (does it support tool definitions?)
3. **codex_cli.py** — Codex CLI (does it support tool definitions?)
4. **qwen_cli.py** — Qwen CLI (does it support tool definitions?)

Each POC runs the same task: "Plan and execute a simple file operation" and tracks todo progress.
