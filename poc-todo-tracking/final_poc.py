#!/usr/bin/env python3
"""POC: Function Calling vs CLI Prompts for Todo Tracking

Demonstrates the core difference:
- OpenAI API: Native function calling (LLM MUST call tools)
- CLI tools: Text prompts (LLM can ignore instructions)

Then shows a hybrid approach that works with CLI tools.
"""
import json
import subprocess
import tempfile
import time
import re
from pathlib import Path

# ============================================================================
# Part 1: OpenAI API with Native Function Calling
# ============================================================================

def part1_openai_function_calling():
    """Show how OpenAI API handles function calling natively."""
    print("=" * 70)
    print("PART 1: OpenAI API with Native Function Calling")
    print("=" * 70)
    
    try:
        from openai import OpenAI
    except ImportError:
        print("⚠️  openai not installed - skipping API test")
        print("   Install: pip install openai\n")
        return None
    
    api_key = __import__('os').environ.get("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY not set - skipping\n")
        return None
    
    client = OpenAI(api_key=api_key)
    
    # Todo state (managed by host)
    todos = []
    completed = []
    
    # Tool definitions (OpenAI format)
    tools = [
        {
            "type": "function",
            "function": {
                "name": "create_todos",
                "description": "Create a todo list. Call this FIRST.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "descriptions": {
                            "type": "array",
                            "items": {"type": "string"},
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
                "description": "Mark a todo as complete. Call after each step.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "index": {"type": "integer"},
                        "notes": {"type": "string"}
                    },
                    "required": ["index", "notes"]
                }
            }
        }
    ]
    
    def handle_tool(tool_name, args):
        if tool_name == "create_todos":
            descs = args["descriptions"]
            todos.extend(descs)
            completed.extend([False] * len(descs))
            print(f"[todo] 📋 Created {len(descs)} items:")
            for i, d in enumerate(descs, 1):
                print(f"     {i}. {d}")
            return f"Created {len(descs)} todos"
        elif tool_name == "mark_complete":
            idx = args["index"]
            notes = args["notes"]
            if 1 <= idx <= len(todos):
                completed[idx-1] = True
                print(f"[todo] ✅ #{idx}: {todos[idx-1]}")
                if notes:
                    print(f"     {notes}")
                return f"Marked #{idx} complete"
            return f"Invalid index {idx}"
        return f"Unknown tool: {tool_name}"
    
    task = """Create 3 files in /tmp/poc-todo/:
1. hello1.txt with "Hello 1"
2. hello2.txt with "Hello 2"  
3. hello3.txt with "Hello 3"
Then read them all and show contents.
"""
    
    messages = [
        {"role": "system", "content": (
            "You are a coding assistant. "
            "You MUST: 1) Call create_todos() FIRST with your plan. "
            "2) Do the work. "
            "3) Call mark_complete() after each step. "
            "4) Provide final summary."
        )},
        {"role": "user", "content": task}
    ]
    
    print(f"\nTask: {task.strip()}\n")
    
    try:
        for turn in range(10):
            resp = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=tools,
            )
            
            msg = resp.choices[0].message
            finish = resp.choices[0].finish_reason
            
            if finish == "tool_calls":
                for tc in msg.tool_calls:
                    args = json.loads(tc.function.arguments)
                    print(f"\n[tool_call] {tc.function.name}({json.dumps(args)})")
                    result = handle_tool(tc.function.name, args)
                    messages.append(msg)
                    messages.append({
                        "role": "tool",
                        "content": result,
                        "tool_call_id": tc.id,
                    })
            else:
                print(f"\n[final] {msg.content[:300]}")
                break
        
        # Verify files
        print(f"\n--- File Verification ---")
        for i in range(1, 4):
            f = Path(f"/tmp/poc-todo/hello{i}.txt")
            if f.exists():
                print(f"✅ hello{i}.txt: {f.read_text().strip()}")
            else:
                print(f"❌ hello{i}.txt missing")
        
        print(f"\n✅ Function Calling: {sum(completed)}/{len(todos)} todos tracked")
        return {"todos": len(todos), "completed": sum(completed)}
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


# ============================================================================
# Part 2: CLI Tools with Text Prompts (Current Approach)
# ============================================================================

def part2_cli_text_prompts():
    """Show how CLI tools handle todo instructions in prompts."""
    print("\n" + "=" * 70)
    print("PART 2: CLI Tools with Text Prompts (Current Approach)")
    print("=" * 70)
    
    task = """Create 3 files in the current directory:
1. hello1.txt with "Hello 1"
2. hello2.txt with "Hello 2"
3. hello3.txt with "Hello 3"
Then read them all and show contents.
"""
    
    prompt = f"""You are a coding assistant.

TASK: {task}

MANDATORY: Before starting, create 'todos.md' with:
# Progress
- [ ] Create hello1.txt
- [ ] Create hello2.txt
- [ ] Create hello3.txt
- [ ] Read all files

Update todos.md after EACH step. Mark completed items with [x].
"""
    
    results = {}
    
    for name, cmd in [
        ("Claude", ["claude", "--print", "--output-format", "text"]),
        ("Codex", ["codex", "exec", "--json"]),
        ("Qwen", ["qwen", "--output-format", "json", "--approval-mode", "yolo"]),
    ]:
        print(f"\n--- Testing {name} ---")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                result = subprocess.run(
                    cmd,
                    input=prompt,
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=tmpdir,
                )
                
                todos_md = Path(tmpdir) / "todos.md"
                files_ok = all(Path(tmpdir, f"hello{i}.txt").exists() for i in range(1, 4))
                
                if todos_md.exists():
                    content = todos_md.read_text()
                    checked = content.count("[x]")
                    print(f"✅ todos.md created: {checked} items checked")
                    print(f"   Content preview: {content[:100]}...")
                else:
                    print(f"❌ todos.md NOT created")
                
                print(f"   Files created: {'✅' if files_ok else '❌'}")
                results[name] = {
                    "todos_md": todos_md.exists(),
                    "files": files_ok,
                    "exit_code": result.returncode,
                }
                
            except subprocess.TimeoutExpired:
                print(f"⏱️  Timeout")
                results[name] = {"timeout": True}
            except FileNotFoundError:
                print(f"⚠️  CLI not found")
                results[name] = {"not_found": True}
            except Exception as e:
                print(f"❌ Error: {e}")
                results[name] = {"error": str(e)}
    
    return results


# ============================================================================
# Part 3: Hybrid Approach - Structured Output + Post-Processing
# ============================================================================

def part3_hybrid_approach():
    """Show a hybrid approach that works better with CLI tools."""
    print("\n" + "=" * 70)
    print("PART 3: Hybrid Approach - Structured Output + Post-Processing")
    print("=" * 70)
    
    task = """Create 3 files in the current directory:
1. hello1.txt with "Hello 1"
2. hello2.txt with "Hello 2"
3. hello3.txt with "Hello 3"
Then read them all and show contents.
"""
    
    # Better prompt: Use JSONL format (easier to parse)
    prompt = f"""You are a coding assistant.

TASK: {task}

PROGRESS TRACKING (MANDATORY):
Before starting, create 'progress.jsonl' with:
{{"event": "start", "todos": ["Create hello1.txt", "Create hello2.txt", "Create hello3.txt", "Read all files"]}}

After EACH step, APPEND to progress.jsonl:
{{"event": "complete", "index": 0, "result": "Created hello1.txt"}}

Use APPEND mode. Each line is valid JSON.
"""
    
    print(f"\nTask: {task.strip()}\n")
    
    results = {}
    
    for name, cmd in [
        ("Claude", ["claude", "--print", "--output-format", "text"]),
        ("Qwen", ["qwen", "--output-format", "json", "--approval-mode", "yolo"]),
    ]:
        print(f"\n--- Testing {name} (JSONL) ---")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                result = subprocess.run(
                    cmd,
                    input=prompt,
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=tmpdir,
                )
                
                progress_file = Path(tmpdir) / "progress.jsonl"
                files_ok = all(Path(tmpdir, f"hello{i}.txt").exists() for i in range(1, 4))
                
                if progress_file.exists():
                    events = []
                    for line in progress_file.read_text().strip().splitlines():
                        try:
                            events.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
                    
                    print(f"✅ progress.jsonl: {len(events)} events")
                    for e in events:
                        if e.get("event") == "start":
                            print(f"   📋 Start: {len(e.get('todos', []))} todos")
                        elif e.get("event") == "complete":
                            print(f"   ✅ Complete: #{e.get('index')} - {e.get('result')}")
                else:
                    print(f"❌ progress.jsonl NOT created")
                
                print(f"   Files created: {'✅' if files_ok else '❌'}")
                results[name] = {
                    "jsonl": progress_file.exists(),
                    "files": files_ok,
                }
                
            except Exception as e:
                print(f"❌ Error: {e}")
                results[name] = {"error": str(e)}
    
    return results


# ============================================================================
# Part 4: Agent Loop Pattern (Ed Donner Style)
# ============================================================================

def part4_agent_loop():
    """Show the agent loop pattern that enables function calling with CLI tools."""
    print("\n" + "=" * 70)
    print("PART 4: Agent Loop Pattern (Ed Donner Style)")
    print("=" * 70)
    
    print("""
The Pattern:
1. Define tools as JSON schemas (create_todos, mark_complete)
2. Pass tools to LLM via prompt
3. LLM outputs tool calls in structured format
4. Extract tool calls from output
5. Execute tool calls locally (update state)
6. Feed results back to LLM
7. Repeat until LLM provides final answer

This mirrors the OpenAI API function calling pattern but works with CLI tools.

Example flow:
  User: "Create 3 files"
  LLM: "```tool_call\\n{\"tool\": \"create_todos\", \"args\": {...}}\\n```"
  Host: Extracts tool call, executes create_todos()
  Host: "Tool result: Created 3 todos"
  LLM: "```tool_call\\n{\"tool\": \"mark_complete\", \"args\": {...}}\\n```"
  Host: Extracts tool call, executes mark_complete()
  Host: "Tool result: Marked #1 complete"
  ...
  LLM: "Done! All files created."

Benefits:
✅ Progress tracked in real-time
✅ Structured data (not parsing markdown)
✅ Can validate tool calls before proceeding
✅ Works with any CLI tool

Challenges:
❌ LLM may not follow tool call format
❌ Regex extraction is fragile
❌ No enforcement mechanism (unlike native function calling)
""")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("POC: Function Calling vs CLI Prompts for Todo Tracking\n")
    print("Testing 4 approaches to track LLM progress:\n")
    print("1. OpenAI API with native function calling")
    print("2. CLI tools with text prompts (current approach)")
    print("3. Hybrid: Structured JSONL output")
    print("4. Agent loop pattern (Ed Donner style)\n")
    
    # Run all parts
    api_result = part1_openai_function_calling()
    cli_results = part2_cli_text_prompts()
    hybrid_results = part3_hybrid_approach()
    part4_agent_loop()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"""
Approach          | Progress Tracking | Reliability | Works With
------------------|-------------------|-------------|----------
OpenAI API        | ✅ Native         | ✅ High     | OpenAI only
CLI Text Prompts  | ❌ Ignored        | ❌ Low      | All CLI tools
Hybrid JSONL      | ⚠️ Partial        | ⚠️ Medium   | Qwen, some Claude
Agent Loop        | ✅ Structured     | ⚠️ Medium   | All CLI tools

Recommendation for agent-runner-v2:
1. Use OpenAI API directly when possible (best)
2. For CLI tools, use hybrid JSONL + agent loop
3. Define clear tool schemas in prompts
4. Validate tool call output before proceeding
5. Fall back to sidecar polling if tools not called
""")
