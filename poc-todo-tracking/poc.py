#!/usr/bin/env python3
"""POC: Todo tracking for LLM agents

The Problem:
- When we invoke Claude/Codex/Qwen via CLI, we pass a text prompt
- The prompt tells the LLM to "create a todo.md and update it"
- But the LLM ignores this or writes its own format

The Solution (OpenAI API pattern):
- Use function calling: define tools like create_todos(), mark_complete()
- The LLM natively calls these tools as it works
- We capture progress from the tool calls, not from files

This POC demonstrates both approaches side by side.
"""
import json
import subprocess
import tempfile
import os
import time
from pathlib import Path

# ============================================================================
# APPROACH 1: OpenAI API with function calling (the "right" way)
# ============================================================================

def approach_openai_api():
    """Demonstrate OpenAI API function calling for todo tracking."""
    
    print("=" * 60)
    print("APPROACH 1: OpenAI API with Function Calling")
    print("=" * 60)
    
    # This is the pattern from Ed Donner's notebook:
    # 1. Define tools as JSON schemas
    # 2. Pass tools to the API
    # 3. LLM calls tools natively
    # 4. We handle the tool calls and feed results back
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "create_todos",
                "description": "Create a todo list with descriptions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "descriptions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of todo item descriptions"
                        }
                    },
                    "required": ["descriptions"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "mark_complete",
                "description": "Mark a todo as complete",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "index": {
                            "type": "integer",
                            "description": "1-based index of todo to mark complete"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Notes about completion"
                        }
                    },
                    "required": ["index", "notes"]
                }
            }
        }
    ]
    
    print("\nTools defined:")
    for tool in tools:
        fn = tool["function"]
        print(f"  - {fn['name']}: {fn['description']}")
    
    print("\nHow it works:")
    print("  1. Define tools as JSON schemas")
    print("  2. Pass to OpenAI API with messages")
    print("  3. LLM responds with tool_calls")
    print("  4. Execute tool calls locally")
    print("  5. Feed results back to LLM")
    print("  6. Repeat until LLM returns text (not tool_calls)")
    
    print("\n✅ PROS:")
    print("  - Native function calling - LLM MUST use tools")
    print("  - Structured data - no parsing needed")
    print("  - Real-time progress tracking")
    print("  - Works with OpenAI models (GPT-4, GPT-3.5)")
    
    print("\n❌ CONS:")
    print("  - Only works with OpenAI API")
    print("  - Claude/Codex/Qwen CLI don't support this")
    print("  - Requires API key + HTTP calls")
    
    return tools


# ============================================================================
# APPROACH 2: CLI tools with text prompts (current approach)
# ============================================================================

def approach_cli_prompts():
    """Demonstrate CLI tool approach with text prompts."""
    
    print("\n" + "=" * 60)
    print("APPROACH 2: CLI Tools with Text Prompts")
    print("=" * 60)
    
    prompt = """You are a coding assistant. Your task:

1. Create a file called 'hello.py' that prints "Hello World"
2. Verify the file exists
3. Show the file contents
4. Delete the file

IMPORTANT: Before you start, create a file called 'todos.md' with this format:
# Todo List
- [ ] Create hello.py
- [ ] Verify file exists
- [ ] Show contents
- [ ] Delete file

Update todos.md as you complete each item. Mark completed items with [x].
"""
    
    print("\nPrompt sent to CLI tool:")
    print(prompt)
    
    print("\n❌ PROBLEMS:")
    print("  1. LLM may ignore the todo instruction entirely")
    print("  2. LLM may create todos.md but never update it")
    print("  3. LLM may use different format than expected")
    print("  4. No way to verify progress in real-time")
    print("  5. Parsing markdown is fragile")
    
    print("\n✅ WORKAROUNDS:")
    print("  - Make prompt instructions stronger/more explicit")
    print("  - Use sidecar files that LLM must update")
    print("  - Poll for file changes during execution")
    print("  - Post-process output to extract progress")


# ============================================================================
# APPROACH 3: Hybrid - CLI tools with structured output
# ============================================================================

def approach_hybrid():
    """Demonstrate hybrid approach: CLI tools write structured JSON."""
    
    print("\n" + "=" * 60)
    print("APPROACH 3: Hybrid - CLI with Structured JSON Output")
    print("=" * 60)
    
    prompt = """You are a coding assistant. Your task:

1. Create a file called 'hello.py' that prints "Hello World"
2. Verify the file exists
3. Show the file contents
4. Delete the file

PROGRESS TRACKING (MANDATORY):
Before starting, create 'progress.jsonl' with:
{"event": "start", "todos": ["Create hello.py", "Verify file", "Show contents", "Delete file"]}

After each step, append a line:
{"event": "complete", "index": 0, "result": "Created hello.py with print statement"}

Final line when done:
{"event": "done", "success": true}

Use APPEND mode for progress.jsonl. Each line is valid JSON.
"""
    
    print("\nPrompt with structured JSON tracking:")
    print(prompt)
    
    print("\n✅ ADVANTAGES:")
    print("  - Works with any CLI tool (Claude, Codex, Qwen)")
    print("  - JSON is easier to parse than markdown")
    print("  - Can poll progress.jsonl in real-time")
    print("  - Structured data for DB/storage")
    
    print("\n❌ STILL FRAGILE:")
    print("  - LLM may still ignore instructions")
    print("  - JSON format may vary")
    print("  - No enforcement mechanism")


# ============================================================================
# LIVE TEST: Run actual CLI tool
# ============================================================================

def live_test_claude():
    """Actually run Claude CLI with todo prompt and see what happens."""
    
    print("\n" + "=" * 60)
    print("LIVE TEST: Claude CLI with Todo Prompt")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        prompt = """Create a file called 'test.txt' in the current directory with content "Hello from Claude".
Then read it back and show me the contents.

BEFORE you start, create 'todos.md' with:
# Progress
- [ ] Create test.txt
- [ ] Read test.txt
- [ ] Show contents

Update it as you work.
"""
        
        print(f"\nWorking directory: {tmpdir}")
        print("Running Claude CLI...\n")
        
        try:
            result = subprocess.run(
                ["claude", "--print", "--output-format", "text"],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=tmpdir,
            )
            
            print("Exit code:", result.returncode)
            print("Output length:", len(result.stdout))
            
            # Check for todos.md
            todos_path = Path(tmpdir) / "todos.md"
            if todos_path.exists():
                print("\n✅ todos.md was created!")
                print("Contents:")
                print(todos_path.read_text())
            else:
                print("\n❌ todos.md was NOT created")
            
            # Check for test.txt
            test_path = Path(tmpdir) / "test.txt"
            if test_path.exists():
                print("✅ test.txt was created!")
                print("Contents:", test_path.read_text())
            else:
                print("❌ test.txt was NOT created")
                
        except subprocess.TimeoutExpired:
            print("⏱️  Timeout after 60s")
        except FileNotFoundError:
            print("⚠️  Claude CLI not found in PATH")
        except Exception as e:
            print(f"❌ Error: {e}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("POC: Todo Tracking for LLM Agents")
    print("Testing different approaches to track LLM progress\n")
    
    # Show all approaches
    tools = approach_openai_api()
    approach_cli_prompts()
    approach_hybrid()
    
    # Live test
    live_test_claude()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""
The core issue: CLI tools (Claude, Codex, Qwen) are invoked with text
prompts, not function calling. The LLM can ignore todo instructions.

Solutions:
1. OpenAI API: Native function calling (best, but OpenAI only)
2. Structured JSON prompts: Better parsing, still fragile
3. Sidecar polling: Monitor files during execution
4. Hybrid: Combine structured output with post-processing

For agent-runner-v2, we should:
- Use structured JSON output in prompts
- Poll for progress files during execution
- Post-process to extract todo state
- Fall back to OpenAI API when available
""")
