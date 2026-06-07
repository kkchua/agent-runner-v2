#!/usr/bin/env python3
"""POC 1: OpenAI API with native function calling for todo tracking.

This is the "gold standard" pattern from Ed Donner's agent loop.
The LLM calls create_todos() and mark_complete() as native function tools.
Progress is captured automatically from tool calls.
"""
import json
import os
import sys
from openai import OpenAI

# ---------------------------------------------------------------------------
# Todo state + functions (managed by the host, not the LLM)
# ---------------------------------------------------------------------------

todos: list[str] = []
completed: list[bool] = []

def get_todo_report() -> str:
    result = ""
    for i, todo in enumerate(todos):
        status = "DONE" if completed[i] else "TODO"
        result += f"Todo #{i + 1}: [{status}] {todo}\n"
    return result

def create_todos(descriptions: list[str]) -> str:
    todos.extend(descriptions)
    completed.extend([False] * len(descriptions))
    print(f"[todo] Created {len(descriptions)} todos:")
    for i, t in enumerate(descriptions, 1):
        print(f"  {i}. {t}")
    return get_todo_report()

def mark_complete(index: int, completion_notes: str = "") -> str:
    if 1 <= index <= len(todos):
        completed[index - 1] = True
        print(f"[todo] ✓ Todo #{index} completed: {todos[index-1]}")
        if completion_notes:
            print(f"  Notes: {completion_notes}")
        return get_todo_report()
    return f"Error: No todo at index {index}"

# ---------------------------------------------------------------------------
# Tool schemas (OpenAI function calling format)
# ---------------------------------------------------------------------------

TODO_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_todos",
            "description": "Create a todo list with descriptions. Call this FIRST to plan your work.",
            "parameters": {
                "type": "object",
                "properties": {
                    "descriptions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of todo item descriptions",
                    }
                },
                "required": ["descriptions"],
                "additionalProperties": False,
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mark_complete",
            "description": "Mark a todo as complete. Call this when you finish each item.",
            "parameters": {
                "type": "object",
                "properties": {
                    "index": {
                        "type": "integer",
                        "description": "1-based index of the todo to mark complete",
                    },
                    "completion_notes": {
                        "type": "string",
                        "description": "Brief notes about what was done",
                    }
                },
                "required": ["index", "completion_notes"],
                "additionalProperties": False,
            }
        }
    },
]

# ---------------------------------------------------------------------------
# Tool handler
# ---------------------------------------------------------------------------

HANDLERS = {
    "create_todos": create_todos,
    "mark_complete": mark_complete,
}

def handle_tool_calls(tool_calls: list) -> list[dict]:
    results = []
    for tc in tool_calls:
        name = tc.function.name
        args = json.loads(tc.function.arguments)
        handler = HANDLERS.get(name)
        if handler:
            content = str(handler(**args))
        else:
            content = f"Error: Unknown tool {name}"
        results.append({
            "role": "tool",
            "content": content,
            "tool_call_id": tc.id,
        })
    return results

# ---------------------------------------------------------------------------
# Agent loop
# ---------------------------------------------------------------------------

def run_agent_loop(client: OpenAI, model: str, task: str):
    messages = [
        {"role": "system", "content": (
            "You are a helpful assistant. "
            "You MUST follow this workflow:\n"
            "1. First, call create_todos() with a list of steps you plan to take\n"
            "2. Then do the work\n"
            "3. After each step, call mark_complete() with the index and notes\n"
            "4. Finally, provide a summary to the user\n"
            "Do NOT skip the todo steps. This is mandatory."
        )},
        {"role": "user", "content": task},
    ]

    max_turns = 20
    for turn in range(max_turns):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TODO_TOOLS,
        )
        message = response.choices[0].message
        finish = response.choices[0].finish_reason

        if finish == "tool_calls":
            messages.append(message)
            tool_results = handle_tool_calls(message.tool_calls)
            messages.extend(tool_results)
        else:
            messages.append(message)
            print(f"\n[final] {message.content}")
            break
    else:
        print(f"[warn] Reached max turns ({max_turns})")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    model = sys.argv[1] if len(sys.argv) > 1 else "gpt-4o"

    task = (
        "Create a Python file called 'hello_poc.py' that prints 'Hello from POC!'. "
        "Then verify it exists and show its contents. "
        "Finally, delete the file."
    )

    print(f"=== POC 1: OpenAI API (model={model}) ===\n")
    print(f"Task: {task}\n")
    run_agent_loop(client, model, task)
    print(f"\n=== Final todo state: {len(todos)} todos, {sum(completed)} completed ===")
