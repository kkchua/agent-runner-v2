#!/usr/bin/env python3
"""POC: Test todo tracking with Claude/Codex/Qwen CLI tools.

The Problem:
- We invoke CLI tools via subprocess with text prompts
- The prompt tells LLM to "create todo.md and update it"
- LLM ignores this or writes its own format

The Solution (from Ed Donner's notebook):
- Use function calling: define tools like create_todos(), mark_complete()
- The LLM natively calls these tools as it works
- We capture progress from the tool calls, not from files

But CLI tools don't support function calling natively!
So we need to test: Can we make CLI tools write structured progress?
"""
import json
import subprocess
import tempfile
import os
import time
from pathlib import Path

def test_claude_todo():
    """Test Claude CLI with todo tracking prompt."""
    print("=" * 60)
    print("TEST 1: Claude CLI with todo tracking")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a simple task
        task = """Create a file called 'hello.txt' in the current directory with content "Hello from Claude".
Then read it back and show me the contents."""
        
        # Approach A: Just tell it to create todo.md
        prompt_a = f"""You are a coding assistant. 

TASK: {task}

BEFORE you start, create a file called 'todos.md' with this exact format:
# Progress
- [ ] Create hello.txt
- [ ] Read hello.txt
- [ ] Show contents

Update todos.md as you complete each item. Mark completed items with [x].
"""
        
        print("\nApproach A: Prompt with todo instruction")
        print(f"Working directory: {tmpdir}")
        
        try:
            result = subprocess.run(
                ["claude", "--print", "--output-format", "text"],
                input=prompt_a,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=tmpdir,
            )
            
            print(f"Exit code: {result.returncode}")
            
            # Check for todos.md
            todos_path = Path(tmpdir) / "todos.md"
            if todos_path.exists():
                print("✅ todos.md was created!")
                print("Contents:")
                print(todos_path.read_text())
            else:
                print("❌ todos.md was NOT created")
            
            # Check for hello.txt
            hello_path = Path(tmpdir) / "hello.txt"
            if hello_path.exists():
                print("✅ hello.txt was created!")
            else:
                print("❌ hello.txt was NOT created")
                
        except subprocess.TimeoutExpired:
            print("⏱️  Timeout after 60s")
        except FileNotFoundError:
            print("⚠️  Claude CLI not found")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_codex_todo():
    """Test Codex CLI with todo tracking."""
    print("\n" + "=" * 60)
    print("TEST 2: Codex CLI with todo tracking")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        task = """Create a file called 'hello.txt' in the current directory with content "Hello from Codex".
Then read it back and show me the contents."""
        
        prompt = f"""You are a coding assistant. 

TASK: {task}

BEFORE you start, create a file called 'todos.md' with this exact format:
# Progress
- [ ] Create hello.txt
- [ ] Read hello.txt
- [ ] Show contents

Update todos.md as you complete each item. Mark completed items with [x].
"""
        
        print(f"\nWorking directory: {tmpdir}")
        
        try:
            result = subprocess.run(
                ["codex", "exec", "--json"],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=tmpdir,
            )
            
            print(f"Exit code: {result.returncode}")
            
            # Check for todos.md
            todos_path = Path(tmpdir) / "todos.md"
            if todos_path.exists():
                print("✅ todos.md was created!")
                print("Contents:")
                print(todos_path.read_text())
            else:
                print("❌ todos.md was NOT created")
            
            # Check for hello.txt
            hello_path = Path(tmpdir) / "hello.txt"
            if hello_path.exists():
                print("✅ hello.txt was created!")
            else:
                print("❌ hello.txt was NOT created")
                
        except subprocess.TimeoutExpired:
            print("⏱️  Timeout after 60s")
        except FileNotFoundError:
            print("⚠️  Codex CLI not found")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_qwen_todo():
    """Test Qwen CLI with todo tracking."""
    print("\n" + "=" * 60)
    print("TEST 3: Qwen CLI with todo tracking")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        task = """Create a file called 'hello.txt' in the current directory with content "Hello from Qwen".
Then read it back and show me the contents."""
        
        prompt = f"""You are a coding assistant. 

TASK: {task}

BEFORE you start, create a file called 'todos.md' with this exact format:
# Progress
- [ ] Create hello.txt
- [ ] Read hello.txt
- [ ] Show contents

Update todos.md as you complete each item. Mark completed items with [x].
"""
        
        print(f"\nWorking directory: {tmpdir}")
        
        try:
            result = subprocess.run(
                ["qwen", "--output-format", "json", "--approval-mode", "yolo"],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=tmpdir,
            )
            
            print(f"Exit code: {result.returncode}")
            
            # Check for todos.md
            todos_path = Path(tmpdir) / "todos.md"
            if todos_path.exists():
                print("✅ todos.md was created!")
                print("Contents:")
                print(todos_path.read_text())
            else:
                print("❌ todos.md was NOT created")
            
            # Check for hello.txt
            hello_path = Path(tmpdir) / "hello.txt"
            if hello_path.exists():
                print("✅ hello.txt was created!")
            else:
                print("❌ hello.txt was NOT created")
                
        except subprocess.TimeoutExpired:
            print("⏱️  Timeout after 60s")
        except FileNotFoundError:
            print("⚠️  Qwen CLI not found")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_structured_json_approach():
    """Test: Can we make CLI tools write structured JSON progress?"""
    print("\n" + "=" * 60)
    print("TEST 4: Structured JSON progress tracking")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        task = """Create a file called 'hello.txt' in the current directory with content "Hello".
Then read it back and show me the contents."""
        
        prompt = f"""You are a coding assistant. 

TASK: {task}

PROGRESS TRACKING (MANDATORY):
Before starting, create 'progress.jsonl' in the current directory with:
{{"event": "start", "todos": ["Create hello.txt", "Read hello.txt", "Show contents"]}}

After completing each step, APPEND a line to progress.jsonl:
{{"event": "complete", "index": 0, "result": "Created hello.txt"}}
{{"event": "complete", "index": 1, "result": "Read hello.txt"}}

Use APPEND mode. Each line is valid JSON.
"""
        
        print(f"\nWorking directory: {tmpdir}")
        
        try:
            result = subprocess.run(
                ["claude", "--print", "--output-format", "text"],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=tmpdir,
            )
            
            print(f"Exit code: {result.returncode}")
            
            # Check for progress.jsonl
            progress_path = Path(tmpdir) / "progress.jsonl"
            if progress_path.exists():
                print("✅ progress.jsonl was created!")
                print("Contents:")
                for line in progress_path.read_text().strip().splitlines():
                    print(f"  {line}")
            else:
                print("❌ progress.jsonl was NOT created")
            
            # Check for hello.txt
            hello_path = Path(tmpdir) / "hello.txt"
            if hello_path.exists():
                print("✅ hello.txt was created!")
            else:
                print("❌ hello.txt was NOT created")
                
        except subprocess.TimeoutExpired:
            print("⏱️  Timeout after 60s")
        except FileNotFoundError:
            print("⚠️  Claude CLI not found")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("POC: Todo Tracking with CLI Tools\n")
    print("Testing if CLI tools respect todo tracking instructions\n")
    
    test_claude_todo()
    test_codex_todo()
    test_qwen_todo()
    test_structured_json_approach()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""
The core issue: CLI tools (Claude, Codex, Qwen) are invoked with text
prompts, not function calling. The LLM can ignore todo instructions.

Solutions to explore:
1. Sidecar polling: Monitor files during execution
2. Structured JSON: Easier to parse than markdown
3. Post-processing: Extract progress from output
4. Hybrid: Combine approaches
""")
